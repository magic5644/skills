"""Data loader for the ``agentskill`` benchmark.

Loads rubric-scored agent-skill tasks from a pre-split directory layout::

    skillopt/datasets/<skill-name>/
        train/items.json
        valid_seen/items.json
        valid_unseen/items.json

Each entry is normalised into the dict shape the rollout and judge expect.
"""

from __future__ import annotations

import json
from pathlib import Path

from skillopt.datasets.base import SplitDataLoader


def _normalize_item(raw: dict) -> dict:
    """Normalise one dataset entry.

    Required keys in the raw entry: ``id``, ``prompt``, ``rubric``.
    Everything else is optional and defaults to an empty value.
    """
    rubric = raw.get("rubric") or []
    if not isinstance(rubric, list):
        raise ValueError(f"item {raw.get('id')!r}: 'rubric' must be a list")
    return {
        "id": str(raw.get("id") or ""),
        "task_type": str(raw.get("task_type") or "general"),
        "question": str(raw.get("prompt") or raw.get("question") or ""),
        "context": str(raw.get("context") or ""),
        "rubric": [str(c) for c in rubric],
        "anti_patterns": [str(c) for c in (raw.get("anti_patterns") or [])],
        "ground_truth": str(raw.get("gold_notes") or raw.get("ground_truth") or ""),
        "should_trigger": bool(raw.get("should_trigger", True)),
    }


class AgentSkillLoader(SplitDataLoader):
    """Load agent-skill evaluation items from ``*.json`` / ``*.jsonl`` files."""

    def load_split_items(self, split_path: str) -> list[dict]:
        path = Path(split_path)
        rows: list[dict] = []

        for json_file in sorted(path.glob("*.json")):
            with json_file.open(encoding="utf-8") as f:
                payload = json.load(f)
            if not isinstance(payload, list):
                raise ValueError(f"Expected a JSON array at top level of {json_file}")
            rows.extend(payload)

        for jsonl_file in sorted(path.glob("*.jsonl")):
            with jsonl_file.open(encoding="utf-8") as f:
                rows.extend(json.loads(line) for line in f if line.strip())

        if not rows:
            raise FileNotFoundError(f"No .json or .jsonl item file found in {split_path}")

        items = [_normalize_item(row) for row in rows]
        seen: set[str] = set()
        for item in items:
            if not item["id"]:
                raise ValueError(f"An item in {split_path} is missing 'id'")
            if item["id"] in seen:
                raise ValueError(f"Duplicate item id {item['id']!r} in {split_path}")
            seen.add(item["id"])
        return items

    def load_raw_items(self, data_path: str) -> list[dict]:
        """Support ``split_mode='ratio'`` over a single flat directory or file."""
        path = Path(data_path)
        if path.is_file():
            with path.open(encoding="utf-8") as f:
                payload = json.load(f)
            return [_normalize_item(row) for row in payload]
        return self.load_split_items(str(path))
