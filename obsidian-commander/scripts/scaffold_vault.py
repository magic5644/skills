#!/usr/bin/env python3
"""Scaffold vault folder structures from predefined templates."""

import argparse
import pathlib
import sys

TEMPLATES = {
    "zettelkasten": {
        "description": "Zettelkasten method: fleeting, literature, permanent notes + MOCs",
        "folders": [
            "0-Inbox",
            "1-Fleeting",
            "2-Literature",
            "3-Permanent",
            "4-MOC",
            "Templates",
            "Attachments",
        ],
        "notes": {
            "0-Inbox/README.md": "---\ntags: [meta]\n---\n# Inbox\n\nCapture fleeting thoughts and ideas here.\nProcess regularly into permanent notes.\n",
            "4-MOC/Home.md": "---\ntags: [moc]\naliases: [home, index]\n---\n# Home\n\nWelcome to your Zettelkasten.\n\n## Maps of Content\n\n- [[Topics MOC]]\n\n## Recent\n\n",
            "4-MOC/Topics MOC.md": "---\ntags: [moc]\n---\n# Topics\n\nOrganize your main topics here.\n\n## Areas\n\n- \n",
            "Templates/Zettel.md": "---\ntags: []\ncreated: {{date}}\n---\n# {{title}}\n\n\n\n---\n## References\n\n## Related\n\n",
            "Templates/Literature Note.md": "---\ntags: [literature-note]\ncreated: {{date}}\nauthor: \nsource: \n---\n# {{title}}\n\n## Summary\n\n## Key Points\n\n- \n\n## Quotes\n\n> \n\n## My Thoughts\n\n",
        }
    },
    "para": {
        "description": "PARA method: Projects, Areas, Resources, Archive",
        "folders": [
            "Projects",
            "Areas",
            "Resources",
            "Archive",
            "Templates",
            "Attachments",
            "Daily Notes",
        ],
        "notes": {
            "Projects/README.md": "---\ntags: [meta]\n---\n# Projects\n\nShort-term efforts with a clear goal and deadline.\n\n## Active Projects\n\n- \n",
            "Areas/README.md": "---\ntags: [meta]\n---\n# Areas\n\nLong-term responsibilities with standards to maintain.\n\n## My Areas\n\n- \n",
            "Resources/README.md": "---\ntags: [meta]\n---\n# Resources\n\nTopics or themes of ongoing interest.\n\n## Topics\n\n- \n",
            "Archive/README.md": "---\ntags: [meta]\n---\n# Archive\n\nInactive items from the other categories.\n",
            "Templates/Project.md": "---\ntags: [project]\ncreated: {{date}}\nstatus: active\npriority: medium\ndeadline: \n---\n# {{title}}\n\n## Overview\n\n## Goals\n\n- \n\n## Tasks\n\n- [ ] \n\n## Notes\n\n",
            "Templates/Meeting.md": "---\ntags: [meeting]\ncreated: {{date}}\nattendees: []\n---\n# Meeting: {{title}}\n\n**Date:** {{date}}\n**Attendees:**\n\n## Agenda\n\n1. \n\n## Notes\n\n## Action Items\n\n- [ ] \n",
        }
    },
    "gtd": {
        "description": "Getting Things Done: Inbox, Next Actions, Projects, Someday/Maybe, Reference",
        "folders": [
            "Inbox",
            "Next Actions",
            "Projects",
            "Waiting For",
            "Someday Maybe",
            "Reference",
            "Templates",
            "Attachments",
            "Daily Notes",
        ],
        "notes": {
            "Inbox/README.md": "---\ntags: [meta]\n---\n# Inbox\n\nCapture everything here. Process daily.\n\n## Unprocessed\n\n- \n",
            "Next Actions/README.md": "---\ntags: [meta]\n---\n# Next Actions\n\nConcrete next steps organized by context.\n\n## @Computer\n\n- [ ] \n\n## @Phone\n\n- [ ] \n\n## @Errands\n\n- [ ] \n",
            "Projects/README.md": "---\ntags: [meta]\n---\n# Projects\n\nMulti-step outcomes.\n\n## Active\n\n- \n",
        }
    },
    "journal": {
        "description": "Journal/diary: daily notes, reflections, goals",
        "folders": [
            "Daily Notes",
            "Weekly Reviews",
            "Monthly Reviews",
            "Goals",
            "Gratitude",
            "Templates",
            "Attachments",
        ],
        "notes": {
            "Templates/Daily.md": "---\ntags: [daily]\ncreated: {{date}}\nmood: \n---\n# {{date}}\n\n## Morning\n\n### Gratitude\n\n1. \n2. \n3. \n\n### Today's Focus\n\n- [ ] \n\n## Notes\n\n## Evening Reflection\n\n",
            "Templates/Weekly Review.md": "---\ntags: [weekly-review]\ncreated: {{date}}\n---\n# Week of {{date}}\n\n## Wins\n\n- \n\n## Challenges\n\n- \n\n## Lessons\n\n- \n\n## Next Week Goals\n\n- [ ] \n",
            "Goals/README.md": "---\ntags: [meta]\n---\n# Goals\n\n## This Year\n\n- \n\n## This Quarter\n\n- \n\n## This Month\n\n- \n",
        }
    },
    "research": {
        "description": "Academic/research: papers, experiments, literature review",
        "folders": [
            "Papers",
            "Literature Review",
            "Experiments",
            "Data",
            "Figures",
            "Drafts",
            "Templates",
            "Attachments",
        ],
        "notes": {
            "Templates/Paper Note.md": "---\ntags: [paper]\ncreated: {{date}}\nauthor: \nyear: \njournal: \ndoi: \n---\n# {{title}}\n\n## Abstract\n\n## Key Findings\n\n- \n\n## Methods\n\n## My Notes\n\n## Related Papers\n\n",
            "Templates/Experiment.md": "---\ntags: [experiment]\ncreated: {{date}}\nstatus: planned\nhypothesis: \n---\n# {{title}}\n\n## Hypothesis\n\n## Method\n\n## Results\n\n## Conclusions\n\n",
            "Literature Review/README.md": "---\ntags: [meta]\n---\n# Literature Review\n\n## Topics\n\n- \n\n## Papers to Read\n\n- [ ] \n",
        }
    }
}


def scaffold(vault_path, template_name, force=False):
    """Create vault folder structure from template."""
    vault = pathlib.Path(vault_path).resolve()

    if template_name not in TEMPLATES:
        print(f"Unknown template: {template_name}")
        print(f"Available: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)

    tmpl = TEMPLATES[template_name]
    print(f"Scaffolding vault with '{template_name}' template")
    print(f"  {tmpl['description']}")
    print()

    # Create .obsidian if it doesn't exist (minimal vault init)
    obsidian_dir = vault / ".obsidian"
    if not obsidian_dir.exists():
        obsidian_dir.mkdir(parents=True, exist_ok=True)
        (obsidian_dir / "app.json").write_text("{}", encoding="utf-8")
        print(f"  Created vault config: .obsidian/")

    # Create folders
    for folder in tmpl["folders"]:
        folder_path = vault / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created folder: {folder}/")

    # Create template notes
    for rel_path, content in tmpl["notes"].items():
        file_path = vault / rel_path
        if file_path.exists() and not force:
            print(f"  Skipped (exists): {rel_path}")
            continue
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        print(f"  Created note: {rel_path}")

    print(f"\nDone! Vault scaffolded at: {vault}")


def main():
    parser = argparse.ArgumentParser(description="Scaffold Obsidian vault structure")
    parser.add_argument("--vault", required=True, help="Path to vault (created if needed)")
    parser.add_argument("--template", required=True, choices=list(TEMPLATES.keys()),
                        help="Organization template to use")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--list", action="store_true", help="List available templates")
    args = parser.parse_args()

    if args.list:
        for name, tmpl in TEMPLATES.items():
            print(f"  {name:15s} — {tmpl['description']}")
            print(f"  {'':15s}   Folders: {', '.join(tmpl['folders'])}")
            print()
        return

    scaffold(args.vault, args.template, force=args.force)


if __name__ == "__main__":
    main()
