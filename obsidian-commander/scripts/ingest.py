#!/usr/bin/env python3
"""Ingest external content into an Obsidian vault."""

import argparse
import pathlib
import re
import sys
from datetime import datetime

import yaml

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    from markdownify import markdownify as md
    HAS_MARKDOWNIFY = True
except ImportError:
    HAS_MARKDOWNIFY = False


def sanitize_filename(name):
    """Create a safe filename from a string."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:200]  # Limit length


def create_frontmatter(title, tags=None, source=None, extra=None):
    """Generate frontmatter dict for an ingested note."""
    fm = {
        "title": title,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "tags": tags or ["inbox", "ingested"],
    }
    if source:
        fm["source"] = source
    if extra:
        fm.update(extra)
    return fm


def html_to_markdown(html_content):
    """Convert HTML to Obsidian-flavored markdown."""
    if HAS_MARKDOWNIFY:
        return md(html_content, heading_style="ATX", bullets="-")
    if HAS_BS4:
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator="\n\n")
    # Fallback: strip tags
    return re.sub(r"<[^>]+>", "", html_content)


def ingest_file(source_path, vault_path, folder="Inbox", mode="note", tags=None):
    """Ingest a single file into the vault."""
    vault = pathlib.Path(vault_path).resolve()
    source = pathlib.Path(source_path).resolve()

    if not source.exists():
        print(f"Error: Source file not found: {source}")
        return None

    content = source.read_text(encoding="utf-8", errors="ignore")
    title = source.stem

    # Convert if needed
    if source.suffix.lower() in (".html", ".htm"):
        content = html_to_markdown(content)
    elif source.suffix.lower() == ".txt":
        pass  # Keep as-is
    elif source.suffix.lower() == ".csv":
        content = csv_to_markdown_table(content)
    elif source.suffix.lower() == ".json":
        content = json_to_markdown(content)

    fm = create_frontmatter(title, tags=tags, source=str(source))
    fm_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)

    safe_name = sanitize_filename(title)
    target_dir = vault / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{safe_name}.md"

    if target_path.exists():
        # Append counter
        counter = 1
        while target_path.exists():
            target_path = target_dir / f"{safe_name} ({counter}).md"
            counter += 1

    full_content = f"---\n{fm_str}---\n\n# {title}\n\n{content}\n"
    target_path.write_text(full_content, encoding="utf-8")
    rel = target_path.relative_to(vault)
    print(f"  Ingested: {source.name} → {rel}")
    return str(rel)


def csv_to_markdown_table(csv_content):
    """Convert CSV content to a markdown table."""
    import csv
    import io
    reader = csv.reader(io.StringIO(csv_content))
    rows = list(reader)
    if not rows:
        return csv_content

    # Header
    header = "| " + " | ".join(rows[0]) + " |"
    separator = "| " + " | ".join(["---"] * len(rows[0])) + " |"
    body = "\n".join("| " + " | ".join(row) + " |" for row in rows[1:])
    return f"{header}\n{separator}\n{body}"


def json_to_markdown(json_content):
    """Convert JSON to readable markdown."""
    import json as json_mod
    try:
        data = json_mod.loads(json_content)
        return f"```json\n{json_mod.dumps(data, indent=2, ensure_ascii=False)}\n```"
    except json_mod.JSONDecodeError:
        return json_content


def ingest_directory(source_dir, vault_path, folder="Inbox", extensions=None, tags=None):
    """Ingest all matching files from a directory."""
    source = pathlib.Path(source_dir).resolve()
    if not source.is_dir():
        print(f"Error: {source} is not a directory")
        sys.exit(1)

    exts = set(extensions) if extensions else {".md", ".txt", ".html", ".htm", ".csv", ".json"}
    count = 0

    for f in sorted(source.rglob("*")):
        if f.is_file() and f.suffix.lower() in exts:
            ingest_file(str(f), vault_path, folder=folder, tags=tags)
            count += 1

    print(f"\nIngested {count} files into {folder}/")


def append_to_daily(vault_path, content):
    """Append content to today's daily note (file-based, no CLI needed)."""
    vault = pathlib.Path(vault_path).resolve()
    today = datetime.now().strftime("%Y-%m-%d")

    # Try common daily note paths
    daily_paths = [
        vault / "Daily Notes" / f"{today}.md",
        vault / "daily" / f"{today}.md",
        vault / f"{today}.md",
    ]

    daily_path = None
    for p in daily_paths:
        if p.exists():
            daily_path = p
            break

    if daily_path is None:
        # Create in Daily Notes/
        daily_dir = vault / "Daily Notes"
        daily_dir.mkdir(parents=True, exist_ok=True)
        daily_path = daily_dir / f"{today}.md"
        fm = {"tags": ["daily"], "created": today}
        fm_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True)
        daily_path.write_text(f"---\n{fm_str}---\n\n# {today}\n\n", encoding="utf-8")

    # Append
    existing = daily_path.read_text(encoding="utf-8", errors="ignore")
    daily_path.write_text(existing + "\n" + content + "\n", encoding="utf-8")
    print(f"  Appended to: {daily_path.relative_to(vault)}")


def main():
    parser = argparse.ArgumentParser(description="Ingest content into Obsidian vault")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")

    sub = parser.add_subparsers(dest="command", required=True)

    # File ingestion
    f = sub.add_parser("file", help="Ingest a single file")
    f.add_argument("--source", required=True, help="Source file path")
    f.add_argument("--folder", default="Inbox", help="Target folder in vault")
    f.add_argument("--tags", help="Comma-separated tags")

    # Directory ingestion
    d = sub.add_parser("dir", help="Ingest all files from a directory")
    d.add_argument("--source", required=True, help="Source directory")
    d.add_argument("--folder", default="Inbox", help="Target folder in vault")
    d.add_argument("--ext", help="File extensions to include (comma-separated, e.g. .md,.txt)")
    d.add_argument("--tags", help="Comma-separated tags")

    # Append to daily
    a = sub.add_parser("daily", help="Append content to daily note")
    a.add_argument("--content", required=True, help="Content to append")

    args = parser.parse_args()

    if args.command == "file":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
        ingest_file(args.source, args.vault, folder=args.folder, tags=tags)
    elif args.command == "dir":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
        exts = [e.strip() for e in args.ext.split(",")] if args.ext else None
        ingest_directory(args.source, args.vault, folder=args.folder, extensions=exts, tags=tags)
    elif args.command == "daily":
        append_to_daily(args.vault, args.content)


if __name__ == "__main__":
    main()
