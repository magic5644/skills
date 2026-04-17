#!/usr/bin/env python3
"""Create notes in an Obsidian vault with frontmatter, templates, and auto-linking."""

import argparse
import pathlib
import re
import yaml
from datetime import datetime


VAULT_TEMPLATES = {
    "default": {
        "frontmatter": {"tags": [], "aliases": [], "created": "{{date}}"},
        "body": "# {{title}}\n\n"
    },
    "daily": {
        "frontmatter": {"tags": ["daily"], "created": "{{date}}"},
        "body": "# {{date}}\n\n## Tasks\n\n- [ ] \n\n## Notes\n\n"
    },
    "meeting": {
        "frontmatter": {"tags": ["meeting"], "created": "{{date}}", "attendees": [], "status": "draft"},
        "body": "# Meeting: {{title}}\n\n**Date:** {{date}}\n**Attendees:**\n\n## Agenda\n\n1. \n\n## Notes\n\n## Action Items\n\n- [ ] \n"
    },
    "project": {
        "frontmatter": {"tags": ["project"], "created": "{{date}}", "status": "active", "priority": "medium"},
        "body": "# {{title}}\n\n## Overview\n\n## Goals\n\n- \n\n## Tasks\n\n- [ ] \n\n## Resources\n\n## Notes\n\n"
    },
    "zettel": {
        "frontmatter": {"tags": [], "created": "{{date}}", "aliases": []},
        "body": "# {{title}}\n\n\n\n---\n## References\n\n## Related\n\n"
    },
    "literature": {
        "frontmatter": {"tags": ["literature-note"], "created": "{{date}}", "author": "", "source": "", "year": ""},
        "body": "# {{title}}\n\n## Summary\n\n## Key Points\n\n- \n\n## Quotes\n\n> \n\n## My Thoughts\n\n## Related\n\n"
    }
}


def resolve_variables(text, variables):
    """Replace {{var}} placeholders with values."""
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def create_note(vault_path, name, template="default", folder=None, content=None,
                tags=None, properties=None, link_to=None):
    """Create a new note in the vault."""
    vault = pathlib.Path(vault_path).resolve()
    if not (vault / ".obsidian").exists():
        print(f"Error: {vault} is not a valid Obsidian vault (no .obsidian folder)")
        return None

    now = datetime.now()
    variables = {
        "title": name,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "datetime": now.isoformat(),
        "timestamp": str(int(now.timestamp())),
    }

    # Determine file path
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
    if folder:
        target_dir = vault / folder
    else:
        target_dir = vault
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / f"{safe_name}.md"

    if file_path.exists():
        print(f"Warning: {file_path.relative_to(vault)} already exists. Skipping.")
        return None

    # Build content from template
    tmpl = VAULT_TEMPLATES.get(template, VAULT_TEMPLATES["default"])
    fm = dict(tmpl["frontmatter"])
    body = tmpl["body"]

    # Apply variables to frontmatter values
    for key, value in fm.items():
        if isinstance(value, str):
            fm[key] = resolve_variables(value, variables)

    # Override with custom properties
    if tags:
        fm["tags"] = tags if isinstance(tags, list) else [t.strip().lstrip("#") for t in tags.split(",")]

    if properties:
        for prop in properties:
            k, v = prop.split("=", 1)
            fm[k.strip()] = v.strip()

    # Build body
    body = resolve_variables(body, variables)
    if content:
        body += content + "\n"

    # Add links
    if link_to:
        links = link_to if isinstance(link_to, list) else [l.strip() for l in link_to.split(",")]
        body += "\n## Related\n\n"
        for link in links:
            body += f"- [[{link}]]\n"

    # Write file
    fm_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    full_content = f"---\n{fm_str}---\n\n{body}"
    file_path.write_text(full_content, encoding="utf-8")

    rel = file_path.relative_to(vault)
    print(f"Created: {rel}")
    return str(rel)


def main():
    parser = argparse.ArgumentParser(description="Create notes in an Obsidian vault")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")
    parser.add_argument("--name", required=True, help="Note name/title")
    parser.add_argument("--template", default="default",
                        choices=list(VAULT_TEMPLATES.keys()),
                        help="Note template")
    parser.add_argument("--folder", help="Target folder within vault")
    parser.add_argument("--content", help="Additional content to add")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--property", action="append", dest="properties",
                        help="Property as key=value (can repeat)")
    parser.add_argument("--link-to", help="Comma-separated note names to link to")
    parser.add_argument("--list-templates", action="store_true", help="List available templates")
    args = parser.parse_args()

    if args.list_templates:
        for name, tmpl in VAULT_TEMPLATES.items():
            tags = tmpl["frontmatter"].get("tags", [])
            print(f"  {name:15s} — tags: {tags}")
        return

    create_note(
        vault_path=args.vault,
        name=args.name,
        template=args.template,
        folder=args.folder,
        content=args.content,
        tags=args.tags,
        properties=args.properties,
        link_to=args.link_to
    )


if __name__ == "__main__":
    main()
