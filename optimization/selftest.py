#!/usr/bin/env python3
"""Offline self-test of the agentskill environment — no provider calls.

Stubs the target and judge model calls, then exercises config loading, the
adapter, a full batch rollout, and the rubric scoring path for every skill.

    .skillopt/venv/bin/python optimization/selftest.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLOPT_ROOT = Path(os.environ.get("SKILLOPT_ROOT", REPO_ROOT / ".skillopt" / "SkillOpt"))
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SKILLOPT_ROOT))

from optimization.skillopt_compat import apply_config_patches  # noqa: E402

apply_config_patches()

from skillopt.config import flatten_config, load_config  # noqa: E402

from optimization.env.agentskill import adapter as adapter_mod  # noqa: E402
from optimization.env.agentskill import judge as judge_mod  # noqa: E402
from optimization.env.agentskill import rollout as rollout_mod  # noqa: E402


def _stub_target(*, system: str, user: str, **_kwargs) -> tuple[str, dict]:
    assert system and user, "rollout must send a system and a user message"
    return ("Stubbed agent response.", {"prompt_tokens": 0, "completion_tokens": 0})


def _stub_optimizer(*, system: str, user: str, **_kwargs) -> tuple[str, dict]:
    # Pass the first two criteria, fail the rest, trigger no anti-pattern.
    verdicts = [{"index": i, "pass": i < 2, "why": "stub"} for i in range(12)]
    payload = {
        "criteria": verdicts,
        "anti_patterns": [{"index": 0, "triggered": False, "why": "stub"}],
        "summary": "stub verdict",
    }
    return (json.dumps(payload), {"prompt_tokens": 0, "completion_tokens": 0})


def _stub_exec(*, work_dir: str, prompt: str, model: str, timeout: int, **_kwargs):
    installed = Path(work_dir, ".agents", "skills", "skillopt-target", "SKILL.md")
    assert installed.is_file(), "exec rollout must install the skill in the workspace"
    assert Path(work_dir, "task.md").is_file(), "exec rollout must write task.md"
    assert installed.read_text(encoding="utf-8").startswith("---"), (
        "the skill document must reach the agent verbatim, frontmatter included"
    )
    return ("Stubbed agent CLI response.", "raw-transcript")


rollout_mod.chat_target = _stub_target
rollout_mod.run_target_exec = _stub_exec
judge_mod.chat_optimizer = _stub_optimizer


def main() -> int:
    configs = sorted((REPO_ROOT / "optimization" / "configs").glob("*.yaml"))
    if not configs:
        print("No skill configs found", file=sys.stderr)
        return 1

    failures = 0
    for config_path in configs:
        skill = config_path.stem
        flat = flatten_config(load_config(str(config_path)))

        assert flat.get("env") == "agentskill", f"{skill}: env name not resolved"
        skill_doc = REPO_ROOT / flat["skill_init"]
        if not skill_doc.is_file():
            print(f"[FAIL] {skill}: skill_init points at a missing file ({skill_doc})")
            failures += 1
            continue

        env = adapter_mod.AgentSkillAdapter(
            split_dir=str(REPO_ROOT / flat["split_dir"]),
            split_mode="split_dir",
            workers=1,
            hard_threshold=float(flat.get("hard_threshold", 0.8)),
        )
        env.setup(flat)

        items = env.build_eval_env(env_num=0, split="valid_seen", seed=42)
        with tempfile.TemporaryDirectory() as tmp:
            results = env.rollout(items, skill_doc.read_text(encoding="utf-8"), tmp)
            conversations = list(Path(tmp, "predictions").glob("*/conversation.json"))

        ok = (
            len(results) == len(items)
            and len(conversations) == len(items)
            and all("hard" in r and "soft" in r for r in results)
            and all(0.0 <= r["soft"] <= 1.0 for r in results)
        )
        status = "ok" if ok else "FAIL"
        failures += 0 if ok else 1
        soft = sum(r["soft"] for r in results) / max(len(results), 1)
        print(
            f"[{status:>4}] {skill:<22} items={len(items)} "
            f"trajectories={len(conversations)} mean_soft={soft:.3f} "
            f"task_types={len(env.get_task_types())}"
        )

    failures += _check_exec_mode()

    if failures:
        print(f"\n{failures} check(s) failed the offline self-test", file=sys.stderr)
        return 1
    print("\nOffline self-test passed for every skill (chat and exec modes).")
    return 0


def _check_exec_mode() -> int:
    """Exercise the agent-CLI path (claude_code_exec) with a stubbed CLI."""
    from skillopt.model import backend_config

    previous = backend_config.get_target_backend()
    backend_config.set_target_backend("claude_code_exec")
    try:
        skill_doc = REPO_ROOT / "pr-review" / "SKILL.md"
        env = adapter_mod.AgentSkillAdapter(
            split_dir=str(REPO_ROOT / "optimization" / "datasets" / "pr-review"),
            split_mode="split_dir",
            workers=1,
            target_model="sonnet",
            exec_timeout=60,
        )
        env.setup({})
        items = env.build_eval_env(env_num=0, split="valid_seen", seed=42)[:1]
        with tempfile.TemporaryDirectory() as tmp:
            results = env.rollout(items, skill_doc.read_text(encoding="utf-8"), tmp)
            workspace = list(Path(tmp, "predictions").glob("*/exec_workspace/.agents/skills/*/SKILL.md"))
        # A low rubric score is expected from the stub; only a transport error is a failure.
        ok = (
            len(results) == 1
            and len(workspace) == 1
            and "call failed" not in results[0]["fail_reason"]
        )
        print(f"[{'ok' if ok else 'FAIL':>4}] exec mode (claude_code_exec)  "
              f"workspace={'built' if workspace else 'missing'} "
              f"soft={results[0]['soft'] if results else 'n/a'}")
        return 0 if ok else 1
    except Exception as exc:  # noqa: BLE001 - report instead of crashing the suite
        print(f"[FAIL] exec mode (claude_code_exec): {exc}")
        return 1
    finally:
        backend_config.set_target_backend(previous)


if __name__ == "__main__":
    raise SystemExit(main())
