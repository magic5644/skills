#!/usr/bin/env python3
"""Install obsidian-commander skill to target IDE/CLI skill directories."""

import argparse
import os
import pathlib
import shutil
import sys

SKILL_NAME = "obsidian-commander"

TARGETS = {
    "copilot": {
        "label": "VS Code / GitHub Copilot",
        "path": pathlib.Path.home() / ".copilot" / "skills" / SKILL_NAME,
    },
    "claude": {
        "label": "Claude Code / Claude CLI",
        "path": pathlib.Path.home() / ".claude" / "skills" / SKILL_NAME,
    },
    "agents": {
        "label": "Generic Agents (Cursor, etc.)",
        "path": pathlib.Path.home() / ".agents" / "skills" / SKILL_NAME,
    },
    "project": {
        "label": "Current project (.github/skills/)",
        "path": None,  # Determined at runtime
    },
}

FILES_TO_COPY = [
    "SKILL.md",
    "requirements.txt",
    "references/obsidian-cli.md",
    "references/obsidian-markdown.md",
    "scripts/semantic_search.py",
    "scripts/create_note.py",
    "scripts/link_audit.py",
    "scripts/bulk_properties.py",
    "scripts/vault_cleanup.py",
    "scripts/vault_health.py",
    "scripts/scaffold_vault.py",
    "scripts/ingest.py",
]


def install(target_key, source_dir, project_dir=None):
    """Install skill files to target location."""
    source = pathlib.Path(source_dir).resolve()

    if target_key == "project":
        if project_dir:
            dest = pathlib.Path(project_dir).resolve() / ".github" / "skills" / SKILL_NAME
        else:
            dest = pathlib.Path.cwd() / ".github" / "skills" / SKILL_NAME
    elif target_key == "all":
        for key in ["copilot", "claude", "agents"]:
            install(key, source_dir)
        return
    else:
        dest = TARGETS[target_key]["path"]

    label = TARGETS.get(target_key, {}).get("label", target_key)
    print(f"Installing to {label}: {dest}")

    dest.mkdir(parents=True, exist_ok=True)

    for rel_path in FILES_TO_COPY:
        src_file = source / rel_path
        dst_file = dest / rel_path
        if src_file.exists():
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            print(f"  Copied: {rel_path}")
        else:
            print(f"  Skipped (not found): {rel_path}")

    print(f"Done! Skill installed at: {dest}\n")


def main():
    parser = argparse.ArgumentParser(description="Install obsidian-commander skill")
    parser.add_argument("--target", required=True,
                        choices=list(TARGETS.keys()) + ["all"],
                        help="Installation target")
    parser.add_argument("--source", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        help="Source directory (default: skill root)")
    parser.add_argument("--project-dir", help="Project directory (for --target project)")
    args = parser.parse_args()

    install(args.target, args.source, project_dir=args.project_dir)


if __name__ == "__main__":
    main()
