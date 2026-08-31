#!/usr/bin/env python3
"""Validate the evaluation datasets without installing SkillOpt.

Checks, per skill: the three splits exist, every item carries the required
fields, ids are unique across splits, rubric criteria are non-empty strings,
and at least one negative-trigger item guards against over-firing.

    python3 optimization/validate_datasets.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATASETS = REPO_ROOT / "optimization" / "datasets"
CONFIGS = REPO_ROOT / "optimization" / "configs"
SPLITS = ("train", "val", "test")
REQUIRED = ("id", "task_type", "prompt", "rubric")
MIN_ITEMS_PER_SKILL = 10


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    seen_ids: dict[str, str] = {}
    total = 0
    negatives = 0

    skill_doc = REPO_ROOT / skill_dir.name / "SKILL.md"
    if not skill_doc.is_file():
        errors.append(f"{skill_dir.name}: no SKILL.md at {skill_doc}")
    if not (CONFIGS / f"{skill_dir.name}.yaml").is_file():
        errors.append(f"{skill_dir.name}: no config in optimization/configs/")

    for split in SPLITS:
        path = skill_dir / split / "items.json"
        if not path.is_file():
            errors.append(f"{skill_dir.name}/{split}: missing items.json")
            continue
        try:
            items = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{skill_dir.name}/{split}: invalid JSON ({exc})")
            continue
        if not isinstance(items, list) or not items:
            errors.append(f"{skill_dir.name}/{split}: expected a non-empty JSON array")
            continue

        total += len(items)
        for item in items:
            where = f"{skill_dir.name}/{split}/{item.get('id', '?')}"
            for key in REQUIRED:
                if not item.get(key):
                    errors.append(f"{where}: missing or empty '{key}'")
            rubric = item.get("rubric") or []
            if not isinstance(rubric, list) or len(rubric) < 3:
                errors.append(f"{where}: rubric needs at least 3 criteria")
            elif any(not isinstance(c, str) or not c.strip() for c in rubric):
                errors.append(f"{where}: rubric criteria must be non-empty strings")
            if not isinstance(item.get("anti_patterns", []), list):
                errors.append(f"{where}: anti_patterns must be a list")
            item_id = str(item.get("id", ""))
            if item_id in seen_ids:
                errors.append(f"{where}: duplicate id, already in {seen_ids[item_id]}")
            seen_ids[item_id] = f"{skill_dir.name}/{split}"
            if item.get("should_trigger") is False:
                negatives += 1

    if total < MIN_ITEMS_PER_SKILL:
        errors.append(
            f"{skill_dir.name}: only {total} items, expected at least {MIN_ITEMS_PER_SKILL}"
        )
    if negatives == 0:
        errors.append(
            f"{skill_dir.name}: no negative-trigger item (should_trigger: false) — "
            "over-triggering would go unmeasured"
        )
    return errors


def main() -> int:
    skill_dirs = sorted(p for p in DATASETS.iterdir() if p.is_dir())
    if not skill_dirs:
        print(f"No datasets found under {DATASETS}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        counts = []
        for split in SPLITS:
            path = skill_dir / split / "items.json"
            n = len(json.loads(path.read_text(encoding="utf-8"))) if path.is_file() else 0
            counts.append(f"{split}={n}")
        status = "FAIL" if errors else "ok"
        print(f"[{status:>4}] {skill_dir.name:<22} {' '.join(counts)}")
        all_errors.extend(errors)

    if all_errors:
        print("\nProblems found:", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("\nAll datasets valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
