"""Rubric-based LLM judge for agent-skill responses.

The judge runs on the *optimizer* backend (a different, stronger model than the
target in most setups) and returns one verdict per rubric criterion, plus one
verdict per anti-pattern. Scores:

* ``soft``  = weighted criterion pass rate, penalised by triggered anti-patterns
* ``hard``  = 1 when ``soft >= hard_threshold`` and no anti-pattern triggered
"""

from __future__ import annotations

import json
import re

from skillopt.model import chat_optimizer

JUDGE_SYSTEM = """You grade the response of a coding agent that was given a skill document as its system prompt.

You receive: the user task, optional repository context, a rubric (criteria the
response must satisfy), and optional anti-patterns (behaviours the response must
avoid). Grade ONLY the response text against those criteria. Do not reward
verbosity, politeness, or restating the task.

Rules:
- A criterion passes only if the response actually does it, concretely.
- Naming a command/flag/file counts only if it is used correctly for the task.
- An anti-pattern triggers if the response exhibits it even partially.
- Be strict and consistent; identical responses must get identical grades.

Return ONLY a JSON object, no prose, no code fences:
{
  "criteria": [{"index": 0, "pass": true, "why": "<=20 words"}],
  "anti_patterns": [{"index": 0, "triggered": false, "why": "<=20 words"}],
  "summary": "<=30 words on the single biggest weakness"
}"""


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            text = text[start : end + 1]
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _render_list(header: str, values: list[str]) -> str:
    if not values:
        return ""
    lines = "\n".join(f"[{i}] {v}" for i, v in enumerate(values))
    return f"{header}\n{lines}\n\n"


def judge_response(
    *,
    item: dict,
    response: str,
    max_completion_tokens: int = 2048,
    hard_threshold: float = 0.8,
) -> dict:
    """Grade one response. Never raises: judge failures score 0 with a reason."""
    rubric: list[str] = item.get("rubric") or []
    anti: list[str] = item.get("anti_patterns") or []

    if not (response or "").strip():
        return {
            "hard": 0,
            "soft": 0.0,
            "criteria_passed": 0,
            "criteria_total": len(rubric),
            "anti_patterns_triggered": [],
            "fail_reason": "empty response from target",
        }

    user = (
        f"# Task given to the agent\n{item.get('question', '')}\n\n"
        + (f"# Repository context\n{item['context']}\n\n" if item.get("context") else "")
        + _render_list("# Rubric criteria", rubric)
        + _render_list("# Anti-patterns", anti)
        + (f"# Reference notes (what a strong answer contains)\n{item['ground_truth']}\n\n" if item.get("ground_truth") else "")
        + f"# Agent response\n{response}"
    )

    try:
        raw, _usage = chat_optimizer(
            system=JUDGE_SYSTEM,
            user=user,
            max_completion_tokens=max_completion_tokens,
        )
    except Exception as exc:  # noqa: BLE001 - a judge outage must not kill the run
        return {
            "hard": 0,
            "soft": 0.0,
            "criteria_passed": 0,
            "criteria_total": len(rubric),
            "anti_patterns_triggered": [],
            "fail_reason": f"judge call failed: {exc}",
        }

    payload = _extract_json(raw)
    if not payload:
        return {
            "hard": 0,
            "soft": 0.0,
            "criteria_passed": 0,
            "criteria_total": len(rubric),
            "anti_patterns_triggered": [],
            "fail_reason": "judge returned unparsable output",
        }

    verdicts = {
        int(v.get("index", -1)): bool(v.get("pass"))
        for v in payload.get("criteria", [])
        if isinstance(v, dict)
    }
    passed = [i for i in range(len(rubric)) if verdicts.get(i, False)]
    failed = [rubric[i] for i in range(len(rubric)) if not verdicts.get(i, False)]

    triggered = [
        anti[int(v["index"])]
        for v in payload.get("anti_patterns", [])
        if isinstance(v, dict)
        and bool(v.get("triggered"))
        and isinstance(v.get("index"), int)
        and 0 <= int(v["index"]) < len(anti)
    ]

    base = len(passed) / len(rubric) if rubric else 0.0
    soft = max(0.0, base - 0.25 * len(triggered))
    hard = int(soft >= hard_threshold and not triggered)

    reason_bits = []
    if failed:
        reason_bits.append("missed: " + "; ".join(failed[:3]))
    if triggered:
        reason_bits.append("anti-pattern: " + "; ".join(triggered[:2]))
    summary = str(payload.get("summary") or "").strip()
    if summary:
        reason_bits.append(summary)

    return {
        "hard": hard,
        "soft": round(soft, 4),
        "criteria_passed": len(passed),
        "criteria_total": len(rubric),
        "failed_criteria": failed,
        "anti_patterns_triggered": triggered,
        "fail_reason": " | ".join(reason_bits) if hard == 0 else "",
    }
