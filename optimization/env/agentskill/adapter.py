"""Environment adapter for the ``agentskill`` benchmark.

Optimises a single agent skill document (``SKILL.md``) against a rubric-scored
dataset of realistic user requests for that skill.
"""

from __future__ import annotations

from pathlib import Path

from skillopt.datasets.base import BatchSpec
from skillopt.envs.base import EnvAdapter

from .dataloader import AgentSkillLoader
from .rollout import run_batch

_PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def _local_prompt(name: str) -> str | None:
    """Load an env-specific prompt shipped next to this adapter.

    ``skillopt.prompts.load_prompt`` only resolves prompts inside the installed
    ``skillopt/envs/<env>/prompts`` tree, which an out-of-tree env cannot use.
    """
    path = _PROMPT_DIR / f"{name}.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return None


class AgentSkillAdapter(EnvAdapter):
    """Rubric-judged evaluation of an agent skill document."""

    def __init__(
        self,
        split_dir: str = "",
        data_path: str = "",
        split_mode: str = "split_dir",
        split_ratio: str = "5:3:2",
        split_seed: int = 42,
        split_output_dir: str = "",
        workers: int = 4,
        analyst_workers: int = 4,
        failure_only: bool = False,
        minibatch_size: int = 4,
        edit_budget: int = 3,
        seed: int = 42,
        limit: int = 0,
        max_completion_tokens: int = 4096,
        hard_threshold: float = 0.8,
        target_model: str = "",
        exec_timeout: int = 300,
    ) -> None:
        self.workers = int(workers)
        self.analyst_workers = int(analyst_workers)
        self.failure_only = bool(failure_only)
        self.minibatch_size = int(minibatch_size)
        self.edit_budget = int(edit_budget)
        self.max_completion_tokens = int(max_completion_tokens)
        self.hard_threshold = float(hard_threshold)
        # Only used by exec backends (claude_code_exec, copilot_exec, ...).
        self.target_model = str(target_model or "")
        self.exec_timeout = int(exec_timeout)
        self.dataloader = AgentSkillLoader(
            split_dir=split_dir,
            data_path=data_path,
            split_mode=split_mode,
            split_ratio=split_ratio,
            split_seed=split_seed,
            split_output_dir=split_output_dir,
            seed=seed,
            limit=limit,
        )

    # ── Lifecycle ──────────────────────────────────────────────────────

    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.dataloader.setup(cfg)

    def get_dataloader(self):
        return self.dataloader

    # ── Batch → env manager ────────────────────────────────────────────

    def build_env_from_batch(self, batch: BatchSpec, **kwargs):
        return list(batch.payload or [])

    def build_train_env(self, batch_size: int, seed: int, **kwargs):
        batch = self.dataloader.build_train_batch(batch_size=batch_size, seed=seed, **kwargs)
        return self.build_env_from_batch(batch, **kwargs)

    def build_eval_env(self, env_num: int, split: str, seed: int, **kwargs):
        batch = self.dataloader.build_eval_batch(env_num=env_num, split=split, seed=seed, **kwargs)
        return self.build_env_from_batch(batch, **kwargs)

    # ── Rollout ────────────────────────────────────────────────────────

    def rollout(self, env_manager, skill_content: str, out_dir: str, **kwargs) -> list[dict]:
        items: list[dict] = list(env_manager or [])
        if not items:
            return []
        return run_batch(
            items=items,
            skill_content=skill_content,
            out_root=out_dir,
            workers=self.workers,
            max_completion_tokens=self.max_completion_tokens,
            hard_threshold=self.hard_threshold,
            target_model=self.target_model,
            exec_timeout=self.exec_timeout,
        )

    # ── Reflection prompts ─────────────────────────────────────────────

    def get_error_minibatch_prompt(self) -> str | None:
        return _local_prompt("analyst_error") or super().get_error_minibatch_prompt()

    def get_success_minibatch_prompt(self) -> str | None:
        return _local_prompt("analyst_success") or super().get_success_minibatch_prompt()

    # ── Stratification ─────────────────────────────────────────────────

    def get_task_types(self) -> list[str]:
        seen: list[str] = []
        all_items = (
            self.dataloader.train_items
            + self.dataloader.val_items
            + self.dataloader.test_items
        )
        for item in all_items:
            task_type = str(item.get("task_type") or "general")
            if task_type not in seen:
                seen.append(task_type)
        return seen or ["general"]
