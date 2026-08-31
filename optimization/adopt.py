#!/usr/bin/env python3
"""Report a SkillOpt run and, on request, adopt the optimized skill document.

A run is adopted only when the held-out **test** hard score improved over the
baseline. Anything else is reported and left staged in the run directory, so a
regression can never silently overwrite a skill.

Usage::

    python optimization/adopt.py --skill pr-review --run-dir optimization/outputs/pr-review/<stamp> [--apply]
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Report / adopt a SkillOpt run")
    parser.add_argument("--skill", required=True, help="skill folder name, e.g. pr-review")
    parser.add_argument("--run-dir", required=True, help="SkillOpt --out_root of the run")
    parser.add_argument("--apply", action="store_true", help="write the optimized skill in place")
    parser.add_argument("--report-only", action="store_true", help="never write (default)")
    parser.add_argument(
        "--min-delta",
        type=float,
        default=0.0,
        help="minimum test hard-score gain required to adopt (default: any strict gain)",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    summary_path = run_dir / "summary.json"
    best_skill = run_dir / "best_skill.md"
    target = REPO_ROOT / args.skill / "SKILL.md"

    if not summary_path.is_file():
        print(f"[{args.skill}] no summary.json in {run_dir} — nothing to report")
        return 1

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    baseline = summary.get("baseline_test_hard")
    final = summary.get("final_test_hard")
    if final is None:
        final = summary.get("test_hard")
    delta = None if (final is None or baseline is None) else final - baseline

    print(f"\n[{args.skill}] run report")
    print(f"  steps={summary.get('total_steps')} accepted={summary.get('total_accepts')} "
          f"rejected={summary.get('total_rejects')} skipped={summary.get('total_skips')}")
    print(f"  best validation score : {_fmt(summary.get('best_score'))}")
    print(f"  test hard  baseline   : {_fmt(baseline)}")
    print(f"  test hard  optimized  : {_fmt(final)}")
    print(f"  test hard  delta      : {_fmt(delta)}")
    print(f"  candidate document    : {best_skill}")

    if not best_skill.is_file():
        print(f"[{args.skill}] no best_skill.md produced — nothing to adopt")
        return 1

    if delta is None or delta <= args.min_delta:
        print(f"[{args.skill}] NOT adopted: no held-out improvement. "
              f"Review the candidate manually if you disagree.")
        return 0

    if not args.apply or args.report_only:
        print(f"[{args.skill}] improvement found. Re-run with --adopt to apply, or copy:\n"
              f"  cp {best_skill} {target}")
        return 0

    backup = target.with_suffix(
        f".md.bak-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    )
    shutil.copy2(target, backup)
    shutil.copy2(best_skill, target)
    print(f"[{args.skill}] ADOPTED. Previous version saved at {backup.name}")
    print("  Review the diff before committing: git diff -- "
          f"{target.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
