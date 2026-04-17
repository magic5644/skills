#!/usr/bin/env python3
"""Audit and map links in an Obsidian vault."""

import argparse
import json
import pathlib
import re
import sys
import yaml


def parse_frontmatter(content):
    """Extract frontmatter dict from markdown content."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            try:
                return yaml.safe_load(content[3:end]) or {}
            except yaml.YAMLError:
                pass
    return {}


def extract_wikilinks(content):
    """Extract all [[wikilinks]] from content, excluding embeds and code blocks."""
    # Remove code blocks
    clean = re.sub(r"```[\s\S]*?```", "", content)
    clean = re.sub(r"`[^`]+`", "", clean)
    # Remove comments
    clean = re.sub(r"%%[\s\S]*?%%", "", clean)

    links = []
    # Match [[link]] and [[link|alias]] but not ![[embed]]
    for match in re.finditer(r"(?<!!)\[\[([^\]|#]+)(?:#[^\]|]*)?\|?[^\]]*\]\]", clean):
        link_target = match.group(1).strip()
        if link_target:
            links.append(link_target)
    return links


def extract_md_links(content):
    """Extract markdown-style [text](link.md) links."""
    clean = re.sub(r"```[\s\S]*?```", "", content)
    clean = re.sub(r"`[^`]+`", "", clean)

    links = []
    for match in re.finditer(r"\[([^\]]*)\]\(([^)]+\.md(?:#[^)]*)?)\)", clean):
        link_path = match.group(2).split("#")[0].strip()
        if link_path and not link_path.startswith("http"):
            links.append(link_path)
    return links


def extract_tags_from_content(content):
    """Extract inline #tags from content."""
    clean = re.sub(r"```[\s\S]*?```", "", content)
    clean = re.sub(r"`[^`]+`", "", clean)
    clean = re.sub(r"%%[\s\S]*?%%", "", clean)
    return re.findall(r"(?<!\w)#([a-zA-Z_\-/][\w\-/]*)", clean)


def resolve_link(link_name, all_files, vault_path):
    """Resolve a wikilink name to a file path."""
    # Exact match
    for f in all_files:
        if f.stem == link_name:
            return str(f.relative_to(vault_path))
    # Case-insensitive match
    lower = link_name.lower()
    for f in all_files:
        if f.stem.lower() == lower:
            return str(f.relative_to(vault_path))
    # Path match
    for f in all_files:
        rel = str(f.relative_to(vault_path))
        if rel.replace("\\", "/").endswith(link_name + ".md"):
            return rel
    return None


def audit_vault(vault_path, format_output="text"):
    """Run full link audit on the vault."""
    vault = pathlib.Path(vault_path).resolve()
    if not (vault / ".obsidian").exists():
        print(f"Error: {vault} is not a valid Obsidian vault")
        sys.exit(1)

    all_files = sorted([
        f for f in vault.rglob("*.md")
        if not str(f.relative_to(vault)).startswith(".obsidian")
    ])

    notes = {}
    for f in all_files:
        rel = str(f.relative_to(vault)).replace("\\", "/")
        content = f.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(content)
        wikilinks = extract_wikilinks(content)
        md_links = extract_md_links(content)
        fm_tags = fm.get("tags", []) if isinstance(fm.get("tags"), list) else []
        inline_tags = extract_tags_from_content(content)

        notes[rel] = {
            "stem": f.stem,
            "outgoing_wiki": wikilinks,
            "outgoing_md": md_links,
            "tags": list(set(fm_tags + inline_tags)),
            "has_frontmatter": bool(fm),
            "frontmatter": fm,
        }

    # Resolve links and compute stats
    total_links = 0
    resolved_count = 0
    unresolved = {}
    backlinks = {rel: [] for rel in notes}
    orphans = []
    deadends = []

    for rel, note in notes.items():
        outgoing_resolved = []
        for link in note["outgoing_wiki"]:
            total_links += 1
            target = resolve_link(link, all_files, vault)
            if target:
                resolved_count += 1
                outgoing_resolved.append(target)
                if target in backlinks:
                    backlinks[target].append(rel)
            else:
                unresolved.setdefault(link, []).append(rel)

        for link in note["outgoing_md"]:
            total_links += 1
            target_path = vault / link
            if target_path.exists():
                resolved_count += 1
                target_rel = str(target_path.relative_to(vault)).replace("\\", "/")
                if target_rel in backlinks:
                    backlinks[target_rel].append(rel)
            else:
                unresolved.setdefault(link, []).append(rel)

        note["outgoing_resolved"] = outgoing_resolved
        if not note["outgoing_wiki"] and not note["outgoing_md"]:
            deadends.append(rel)

    for rel in notes:
        if not backlinks[rel]:
            orphans.append(rel)

    # Collect all tags
    all_tags = {}
    for note in notes.values():
        for tag in note["tags"]:
            all_tags[tag] = all_tags.get(tag, 0) + 1

    report = {
        "total_notes": len(notes),
        "total_links": total_links,
        "resolved_links": resolved_count,
        "unresolved_count": len(unresolved),
        "unresolved": unresolved,
        "orphan_count": len(orphans),
        "orphans": orphans,
        "deadend_count": len(deadends),
        "deadends": deadends,
        "total_tags": len(all_tags),
        "tags": dict(sorted(all_tags.items(), key=lambda x: -x[1])),
        "notes_without_frontmatter": [
            rel for rel, n in notes.items() if not n["has_frontmatter"]
        ],
    }

    if format_output == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        pct = (resolved_count / total_links * 100) if total_links > 0 else 100
        print("=" * 50)
        print("       VAULT LINK HEALTH REPORT")
        print("=" * 50)
        print(f"  Total notes:          {report['total_notes']}")
        print(f"  Total links:          {report['total_links']}")
        print(f"  Resolved:             {report['resolved_links']} ({pct:.1f}%)")
        print(f"  Unresolved:           {report['unresolved_count']}")
        print(f"  Orphan notes:         {report['orphan_count']}")
        print(f"  Dead-end notes:       {report['deadend_count']}")
        print(f"  Unique tags:          {report['total_tags']}")
        print(f"  No frontmatter:       {len(report['notes_without_frontmatter'])}")
        print("=" * 50)

        if unresolved:
            print(f"\nUnresolved links ({len(unresolved)}):")
            for link, sources in sorted(unresolved.items()):
                print(f"  [[{link}]] — referenced from: {', '.join(sources[:3])}")

        if orphans and len(orphans) <= 20:
            print(f"\nOrphan notes ({len(orphans)}):")
            for o in orphans[:20]:
                print(f"  {o}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Audit links in an Obsidian vault")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format")
    args = parser.parse_args()
    audit_vault(args.vault, format_output=args.format)


if __name__ == "__main__":
    main()
