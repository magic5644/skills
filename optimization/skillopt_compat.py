"""Compatibility patches applied to the vendored SkillOpt checkout.

**Why this exists.** ``skillopt.config`` flattens the structured YAML format by
mapping dotted keys to flat ones, including ``env.name -> env``. Two helpers
then delete the flat alias from a layer:

* ``_resolve_layer_format_duplicates(cfg)`` pops ``cfg["env"]``
* ``_drop_base_keys_overridden_by_layer(base, override)`` pops ``base["env"]``

Because the flat alias for ``env.name`` is literally ``"env"``, both helpers
delete the whole structured ``env:`` section instead of a scalar alias. The
result is that ``env.name``, ``env.split_dir``, ``env.skill_init`` and every
env-specific key silently disappear from the merged config, and the trainer
falls back to its default environment.

The patch below preserves the ``env`` mapping across both helpers while leaving
their scalar-alias behaviour untouched. It is idempotent and applies only to the
checkout this repo drives.

Re-check on every SkillOpt upgrade: if upstream fixes the aliasing, this becomes
a no-op that can be deleted.
"""

from __future__ import annotations

_PATCH_FLAG = "_skills_repo_env_section_patch"


def _merge_preserved(preserved: dict, current) -> dict:
    """Layer-local values win over the preserved copy."""
    merged = dict(preserved)
    if isinstance(current, dict):
        merged.update(current)
    return merged


def apply_config_patches() -> None:
    """Keep structured ``env:`` sections alive through config merging."""
    import skillopt.config as config

    if getattr(config, _PATCH_FLAG, False):
        return

    original_resolve = config._resolve_layer_format_duplicates
    original_drop = config._drop_base_keys_overridden_by_layer

    def resolve_layer_format_duplicates(cfg: dict) -> None:
        preserved = cfg.get("env")
        preserved = dict(preserved) if isinstance(preserved, dict) else None
        original_resolve(cfg)
        if preserved is not None:
            cfg["env"] = _merge_preserved(preserved, cfg.get("env"))

    def drop_base_keys_overridden_by_layer(base: dict, override: dict) -> None:
        preserved = base.get("env")
        preserved = dict(preserved) if isinstance(preserved, dict) else None
        original_drop(base, override)
        if preserved is not None:
            base["env"] = _merge_preserved(preserved, base.get("env"))

    config._resolve_layer_format_duplicates = resolve_layer_format_duplicates
    config._drop_base_keys_overridden_by_layer = drop_base_keys_overridden_by_layer
    setattr(config, _PATCH_FLAG, True)
