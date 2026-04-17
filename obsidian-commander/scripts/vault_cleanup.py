#!/usr/bin/env python3
"""Vault cleanup: remove empty notes, fix broken links, clean orphaned attachments."""

import argparse
import json
import pathlib
import re
import sys
import yaml


ATTACHMENT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
                         ".mp3", ".mp4", ".webm", ".wav", ".ogg",
                         ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}


def parse_frontmatter(content):
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            try:
                return yaml.safe_load(content[3:end]) or {}
            except yaml.YAMLError:
                pass
    return {}


def body_after_frontmatter(content):
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].strip()
    return content.strip()


def extract_all_references(content):
    """Extract all file references (wikilinks, embeds, md links)."""
    refs = set()
    # Wikilinks and embeds: [[file]] or ![[file]]
    for m in re.finditer(r"!?\[\[([^\]|#]+)", content):
        refs.add(m.group(1).strip())
    # Markdown links: [text](file.ext)
    for m in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", content):
        link = m.group(2).split("#")[0].strip()
        if not link.startswith("http"):
            refs.add(link)
    return refs


def find_empty_notes(notes):
    """Find notes with no meaningful content beyond frontmatter."""
    empty = []
    for path, content in notes.items():
        body = body_after_frontmatter(content)
        # Remove headings that match the filename
        clean = re.sub(r"^#\s+.*$", "", body, flags=re.MULTILINE).strip()
        if len(clean) < 5:
            empty.append(path)
    return empty


def find_orphaned_attachments(vault_path, notes):
    """Find attachment files not referenced by any note."""
    vault = pathlib.Path(vault_path)
    all_refs = set()
    for content in notes.values():
        all_refs.update(extract_all_references(content))

    # Normalize refs (just filenames for comparison)
    ref_names = set()
    for ref in all_refs:
        ref_names.add(pathlib.Path(ref).name)
        ref_names.add(ref)

    orphaned = []
    for f in vault.rglob("*"):
        if f.is_file() and f.suffix.lower() in ATTACHMENT_EXTENSIONS:
            rel = str(f.relative_to(vault)).replace("\\", "/")
            if f.name not in ref_names and rel not in ref_names:
                orphaned.append(rel)
    return orphaned


def find_duplicate_tags(notes):
    """Find tags that differ only in casing."""
    tag_variants = {}
    for content in notes.values():
        fm = parse_frontmatter(content)
        tags = fm.get("tags", [])
        if isinstance(tags, list):
            for tag in tags:
                lower = tag.lower()
                tag_variants.setdefault(lower, set()).add(tag)

    return {k: list(v) for k, v in tag_variants.items() if len(v) > 1}


def cleanup_report(vault_path):
    """Generate a cleanup report."""
    vault = pathlib.Path(vault_path).resolve()
    if not (vault / ".obsidian").exists():
        print(f"Error: {vault} is not a valid Obsidian vault")
        sys.exit(1)

    notes = {}
    for f in vault.rglob("*.md"):
        rel = str(f.relative_to(vault)).replace("\\", "/")
        if rel.startswith(".obsidian"):
            continue
        notes[rel] = f.read_text(encoding="utf-8", errors="ignore")

    empty = find_empty_notes(notes)
    orphaned_attachments = find_orphaned_attachments(vault_path, notes)
    dup_tags = find_duplicate_tags(notes)

    # Notes missing frontmatter
    no_fm = [rel for rel, c in notes.items() if not parse_frontmatter(c)]

    report = {
        "empty_notes": empty,
        "orphaned_attachments": orphaned_attachments,
        "duplicate_tags": dup_tags,
        "notes_without_frontmatter": no_fm,
    }

    print("=" * 50)
    print("       VAULT CLEANUP REPORT")
    print("=" * 50)
    print(f"  Empty notes:               {len(empty)}")
    print(f"  Orphaned attachments:      {len(orphaned_attachments)}")
    print(f"  Duplicate tag variants:    {len(dup_tags)}")
    print(f"  Notes without frontmatter: {len(no_fm)}")
    print("=" * 50)

    if empty:
        print(f"\nEmpty notes ({len(empty)}):")
        for e in empty[:20]:
            print(f"  {e}")

    if orphaned_attachments:
        print(f"\nOrphaned attachments ({len(orphaned_attachments)}):")
        for a in orphaned_attachments[:20]:
            print(f"  {a}")

    if dup_tags:
        print(f"\nDuplicate tag variants:")
        for tag, variants in dup_tags.items():
            print(f"  {tag}: {variants}")

    if no_fm:
        print(f"\nNotes without frontmatter ({len(no_fm)}):")
        for n in no_fm[:20]:
            print(f"  {n}")

    return report


def apply_fixes(vault_path, fix_empty=True, fix_orphans=False, fix_frontmatter=True):
    """Apply cleanup fixes."""
    vault = pathlib.Path(vault_path).resolve()

    notes = {}
    for f in vault.rglob("*.md"):
        rel = str(f.relative_to(vault)).replace("\\", "/")
        if rel.startswith(".obsidian"):
            continue
        notes[rel] = f.read_text(encoding="utf-8", errors="ignore")

    fixed = 0

    # Add missing frontmatter
    if fix_frontmatter:
        for rel, content in notes.items():
            if not parse_frontmatter(content):
                from datetime import datetime
                fm = {"created": datetime.now().strftime("%Y-%m-%d"), "tags": []}
                fm_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True)
                new_content = f"---\n{fm_str}---\n\n{content}"
                (vault / rel).write_text(new_content, encoding="utf-8")
                print(f"  Added frontmatter: {rel}")
                fixed += 1

    # Delete empty notes
    if fix_empty:
        empty = find_empty_notes(notes)
        for e in empty:
            target = vault / e
            if target.exists():
                target.unlink()
                print(f"  Deleted empty note: {e}")
                fixed += 1

    # Delete orphaned attachments (opt-in only, destructive)
    if fix_orphans:
        orphaned = find_orphaned_attachments(vault_path, notes)
        for a in orphaned:
            target = vault / a
            if target.exists():
                target.unlink()
                print(f"  Deleted orphaned attachment: {a}")
                fixed += 1

    print(f"\nApplied {fixed} fixes.")


def main():
    parser = argparse.ArgumentParser(description="Obsidian vault cleanup")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")
    parser.add_argument("--action", required=True, choices=["report", "fix"],
                        help="report = dry run, fix = apply changes")
    parser.add_argument("--fix-orphans", action="store_true",
                        help="Also delete orphaned attachments (destructive)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if args.action == "report":
        report = cleanup_report(args.vault)
        if args.format == "json":
            print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.action == "fix":
        print("Applying fixes...")
        apply_fixes(args.vault, fix_orphans=args.fix_orphans)


if __name__ == "__main__":
    main()
