"""Rollout helper for the ``agentskill`` benchmark.

Two execution modes, selected by the configured target backend:

* **chat backends** (``openai_chat``, ``claude_chat``, ``copilot_chat``, ...) —
  the skill document is the system prompt and the task is the user message.
* **exec backends** (``claude_code_exec``, ``copilot_exec``, ``codex_exec``,
  ``cursor_exec``) — the skill document is installed as a real skill inside an
  isolated workspace (``.agents/skills/skillopt-target/SKILL.md``) and the task
  is handed to the actual agent CLI. This is the deployment-faithful mode: the
  frontmatter description has to make the agent pick the skill up on its own.

Either way the conversation is persisted at
``<out_dir>/predictions/<id>/conversation.json``, which is where the shared
``EnvAdapter.reflect()`` looks for trajectories.
"""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from skillopt.model import chat_target
from skillopt.model.backend_config import get_target_backend, is_target_chat_backend
from skillopt.model.codex_harness import prepare_workspace, run_target_exec

from .judge import judge_response

HARNESS_PREAMBLE = """You are a coding agent working inside a user's repository from a terminal.
The skill document below was loaded into your context because the user's request matched it.
Answer the user's request by applying that skill: state the concrete commands you run, the
files you inspect, and the conclusions you draw. Do not ask clarifying questions unless the
request is genuinely ambiguous. Be concise and concrete.

--- SKILL DOCUMENT ---
"""


EXEC_PROMPT = """Read `task.md` in this workspace and answer the user request it contains.

A skill document is installed at `.agents/skills/skillopt-target/SKILL.md`. Decide for
yourself whether it applies to this request; use it when it does, ignore it when it does
not. Do not modify any file. Answer in the request's own language, stating the concrete
commands you would run and the conclusions you would draw."""


def _build_user_prompt(item: dict) -> str:
    parts = [f"User request: {item.get('question', '')}"]
    if item.get("context"):
        parts.append(f"\nRepository context:\n{item['context']}")
    return "\n".join(parts)


def _run_chat_target(
    item: dict, skill_content: str, *, max_completion_tokens: int
) -> tuple[str, str, str, str]:
    """Return ``(prediction, error, system, user)`` for a chat backend."""
    system = HARNESS_PREAMBLE + skill_content
    user = _build_user_prompt(item)
    try:
        prediction, _usage = chat_target(
            system=system,
            user=user,
            max_completion_tokens=max_completion_tokens,
        )
    except Exception as exc:  # noqa: BLE001 - one bad episode must not kill the batch
        return "", f"target call failed: {exc}", system, user
    return prediction, "", system, user


def _run_exec_target(
    item: dict,
    skill_content: str,
    *,
    task_dir: Path,
    model: str,
    timeout: int,
) -> tuple[str, str, str, str]:
    """Run the task through an agent CLI with the skill installed in a workspace."""
    user = _build_user_prompt(item)
    work_dir = task_dir / "exec_workspace"
    try:
        # The document is written verbatim, frontmatter included: the trigger
        # description is part of what we are optimizing.
        prepare_workspace(
            work_dir=str(work_dir),
            skill_md=skill_content,
            task_text=user,
        )
        prediction, raw = run_target_exec(
            work_dir=str(work_dir),
            prompt=EXEC_PROMPT,
            model=model,
            timeout=timeout,
            allow_file_edits=False,
        )
    except Exception as exc:  # noqa: BLE001 - one bad episode must not kill the batch
        return "", f"{get_target_backend()} call failed: {exc}", EXEC_PROMPT, user
    return (prediction or raw), "", EXEC_PROMPT, user


def _rollout_one(
    item: dict,
    skill_content: str,
    *,
    prediction_dir: Path,
    max_completion_tokens: int,
    hard_threshold: float,
    target_model: str = "",
    exec_timeout: int = 300,
) -> dict:
    task_dir = prediction_dir / str(item["id"])
    task_dir.mkdir(parents=True, exist_ok=True)

    if is_target_chat_backend():
        prediction, target_error, system, user = _run_chat_target(
            item, skill_content, max_completion_tokens=max_completion_tokens
        )
    else:
        prediction, target_error, system, user = _run_exec_target(
            item,
            skill_content,
            task_dir=task_dir,
            model=target_model,
            timeout=exec_timeout,
        )

    verdict = judge_response(
        item=item,
        response=prediction,
        hard_threshold=hard_threshold,
    )
    if target_error:
        verdict["fail_reason"] = target_error

    conversation = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
        {"role": "assistant", "content": prediction},
    ]
    (task_dir / "conversation.json").write_text(
        json.dumps(conversation, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (task_dir / "verdict.json").write_text(
        json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return {
        "id": str(item["id"]),
        "hard": verdict["hard"],
        "soft": verdict["soft"],
        "predicted_answer": prediction,
        "task_description": item.get("question", ""),
        "question": item.get("question", ""),
        "context": item.get("context", ""),
        "task_type": item.get("task_type", "general"),
        "rubric": item.get("rubric", []),
        "failed_criteria": verdict.get("failed_criteria", []),
        "anti_patterns_triggered": verdict.get("anti_patterns_triggered", []),
        "criteria_passed": verdict.get("criteria_passed", 0),
        "criteria_total": verdict.get("criteria_total", 0),
        "fail_reason": verdict.get("fail_reason", ""),
        "target_system_prompt": system,
        "target_user_prompt": user,
        "n_turns": 1,
    }


def run_batch(
    *,
    items: list[dict],
    skill_content: str,
    out_root: str,
    workers: int = 4,
    max_completion_tokens: int = 4096,
    hard_threshold: float = 0.8,
    target_model: str = "",
    exec_timeout: int = 300,
) -> list[dict]:
    """Run every item in ``items`` under ``skill_content`` and score the replies."""
    os.makedirs(out_root, exist_ok=True)
    prediction_dir = Path(out_root, "predictions")
    prediction_dir.mkdir(parents=True, exist_ok=True)

    def _run(item: dict) -> dict:
        return _rollout_one(
            item,
            skill_content,
            prediction_dir=prediction_dir,
            max_completion_tokens=max_completion_tokens,
            hard_threshold=hard_threshold,
            target_model=target_model,
            exec_timeout=exec_timeout,
        )

    if workers > 1 and len(items) > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_run, items))
    else:
        results = [_run(item) for item in items]

    Path(out_root, "rollouts.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return results
