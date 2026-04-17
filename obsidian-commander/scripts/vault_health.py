#!/usr/bin/env python3
"""Comprehensive vault health check for Obsidian."""

import argparse
import json
import pathlib
import re
import sys
from collections import Counter
from datetime import datetime

import yaml


def parse_frontmatter(content):
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            try:
                return yaml.safe_load(content[3:end]) or {}
            except yaml.YAMLError:
                pass
    return {}


def count_words(text):
    """Count words in text, excluding frontmatter."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:]
    return len(text.split())


def health_check(vault_path, format_output="text"):
    """Run comprehensive vault health check."""
    vault = pathlib.Path(vault_path).resolve()
    if not (vault / ".obsidian").exists():
        print(f"Error: {vault} is not a valid Obsidian vault")
        sys.exit(1)

    notes = {}
    attachments = []
    total_size = 0
    tag_counter = Counter()
    property_counter = Counter()
    notes_with_fm = 0
    notes_without_fm = 0
    word_counts = []
    creation_dates = []
    modification_dates = []
    link_count = 0
    embed_count = 0

    attachment_exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
                       ".mp3", ".mp4", ".pdf", ".doc", ".docx"}

    for f in vault.rglob("*"):
        if f.is_dir():
            continue
        rel = str(f.relative_to(vault)).replace("\\", "/")
        if rel.startswith(".obsidian"):
            continue

        total_size += f.stat().st_size
        mod_time = datetime.fromtimestamp(f.stat().st_mtime)
        modification_dates.append((rel, mod_time))

        if f.suffix == ".md":
            content = f.read_text(encoding="utf-8", errors="ignore")
            fm = parse_frontmatter(content)
            notes[rel] = {"fm": fm, "size": f.stat().st_size}

            if fm:
                notes_with_fm += 1
                tags = fm.get("tags", [])
                if isinstance(tags, list):
                    for t in tags:
                        tag_counter[t] += 1
                for key in fm:
                    property_counter[key] += 1
                if "created" in fm:
                    try:
                        creation_dates.append((rel, str(fm["created"])))
                    except (ValueError, TypeError):
                        pass
            else:
                notes_without_fm += 1

            words = count_words(content)
            word_counts.append((rel, words))

            # Count links and embeds
            link_count += len(re.findall(r"(?<!!)\[\[[^\]]+\]\]", content))
            embed_count += len(re.findall(r"!\[\[[^\]]+\]\]", content))

        elif f.suffix.lower() in attachment_exts:
            attachments.append(rel)

    # Compute stats
    total_words = sum(w for _, w in word_counts)
    avg_words = total_words // len(word_counts) if word_counts else 0
    largest_notes = sorted(word_counts, key=lambda x: -x[1])[:10]
    smallest_notes = sorted(word_counts, key=lambda x: x[1])[:10]

    # Stale notes (not modified in 90+ days)
    now = datetime.now()
    stale = [(rel, d) for rel, d in modification_dates
             if (now - d).days > 90 and rel.endswith(".md")]
    recent = [(rel, d) for rel, d in modification_dates
              if (now - d).days <= 7 and rel.endswith(".md")]

    # Top tags
    top_tags = tag_counter.most_common(20)

    # Top properties
    top_props = property_counter.most_common(20)

    report = {
        "total_notes": len(notes),
        "total_attachments": len(attachments),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "total_words": total_words,
        "avg_words_per_note": avg_words,
        "notes_with_frontmatter": notes_with_fm,
        "notes_without_frontmatter": notes_without_fm,
        "total_links": link_count,
        "total_embeds": embed_count,
        "unique_tags": len(tag_counter),
        "top_tags": dict(top_tags),
        "unique_properties": len(property_counter),
        "top_properties": dict(top_props),
        "stale_notes_90d": len(stale),
        "recently_modified_7d": len(recent),
        "largest_notes": [(n, w) for n, w in largest_notes],
    }

    if format_output == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    else:
        print("=" * 55)
        print("         OBSIDIAN VAULT HEALTH CHECK")
        print("=" * 55)
        print(f"  Vault:                  {vault.name}")
        print(f"  Total size:             {report['total_size_mb']} MB")
        print(f"  Notes:                  {report['total_notes']}")
        print(f"  Attachments:            {report['total_attachments']}")
        print(f"  Total words:            {report['total_words']:,}")
        print(f"  Avg words/note:         {report['avg_words_per_note']}")
        print("-" * 55)
        print(f"  With frontmatter:       {report['notes_with_frontmatter']}")
        print(f"  Without frontmatter:    {report['notes_without_frontmatter']}")
        print(f"  Internal links:         {report['total_links']}")
        print(f"  Embeds:                 {report['total_embeds']}")
        print(f"  Unique tags:            {report['unique_tags']}")
        print(f"  Unique properties:      {report['unique_properties']}")
        print("-" * 55)
        print(f"  Recently modified (7d): {report['recently_modified_7d']}")
        print(f"  Stale (>90d):           {report['stale_notes_90d']}")
        print("=" * 55)

        if top_tags:
            print("\nTop Tags:")
            for tag, count in top_tags:
                print(f"  #{tag}: {count}")

        if largest_notes:
            print("\nLargest Notes (by words):")
            for note, words in largest_notes[:5]:
                print(f"  {note}: {words:,} words")

    return report


def main():
    parser = argparse.ArgumentParser(description="Obsidian vault health check")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()
    health_check(args.vault, format_output=args.format)


if __name__ == "__main__":
    main()
