#!/usr/bin/env python3
"""Entry point that runs SkillOpt training / evaluation with this repo's env.

SkillOpt resolves environments through a hardcoded registry inside its own
``scripts/train.py`` and ``scripts/eval_only.py``. Rather than fork SkillOpt,
this wrapper imports those modules and registers the out-of-tree ``agentskill``
adapter into their registries before delegating to their ``main()``.

Usage::

    python optimization/run.py train --config optimization/configs/pr-review.yaml [skillopt args...]
    python optimization/run.py eval  --config optimization/configs/pr-review.yaml --skill pr-review/SKILL.md
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLOPT_ROOT = Path(os.environ.get("SKILLOPT_ROOT", REPO_ROOT / ".skillopt" / "SkillOpt"))

ENV_NAME = "agentskill"


def _bootstrap_sys_path() -> None:
    """Put the SkillOpt checkout first, then this repo (for ``optimization.*``)."""
    if not (SKILLOPT_ROOT / "scripts" / "train.py").is_file():
        sys.exit(
            f"SkillOpt checkout not found at {SKILLOPT_ROOT}.\n"
            "Run scripts/skillopt-bootstrap.sh first, or set SKILLOPT_ROOT."
        )
    for path in (str(SKILLOPT_ROOT), str(REPO_ROOT)):
        if path in sys.path:
            sys.path.remove(path)
    sys.path.insert(0, str(REPO_ROOT))
    sys.path.insert(0, str(SKILLOPT_ROOT))


def _register(module) -> None:
    from optimization.env.agentskill import AgentSkillAdapter

    module._ENV_REGISTRY[ENV_NAME] = AgentSkillAdapter


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in {"train", "eval"}:
        sys.exit(f"usage: {sys.argv[0]} <train|eval> [skillopt arguments...]")

    action, sys.argv = sys.argv[1], [sys.argv[0], *sys.argv[2:]]
    _bootstrap_sys_path()

    from optimization.skillopt_compat import apply_config_patches

    apply_config_patches()

    if action == "train":
        from scripts import train as runner
    else:
        from scripts import eval_only as runner

    # The registry is populated lazily by SkillOpt; make sure ours survives.
    runner._register_builtins()
    _register(runner)
    runner.main()


if __name__ == "__main__":
    main()
