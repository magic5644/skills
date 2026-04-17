#!/usr/bin/env python3
"""Bulk property (frontmatter) management for Obsidian vaults."""

import argparse
import pathlib
import re
import sys
import yaml


def parse_note(content):
    """Parse a note into frontmatter dict and body string."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            try:
                fm = yaml.safe_load(content[3:end]) or {}
                body = content[end + 3:]
                return fm, body
            except yaml.YAMLError:
                pass
    return {}, content


def serialize_note(fm, body):
    """Serialize frontmatter and body back to a note string."""
    if fm:
        fm_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return f"---\n{fm_str}---{body}"
    return body


def matches_filter(note_path, content, fm, filter_str, vault_path):
    """Check if a note matches the given filter."""
    if not filter_str:
        return True

    rel = str(note_path.relative_to(vault_path)).replace("\\", "/")

    if filter_str.startswith("tag:#"):
        tag = filter_str[5:]
        tags = fm.get("tags", [])
        if isinstance(tags, list):
            return tag in tags
        return False

    if filter_str.startswith("path:"):
        path_prefix = filter_str[5:].strip('"').strip("'")
        return rel.startswith(path_prefix)

    if filter_str.startswith("property:"):
        prop_query = filter_str[9:]
        if "=" in prop_query:
            key, val = prop_query.split("=", 1)
            return str(fm.get(key.strip(), "")) == val.strip()
        return prop_query.strip() in fm

    if filter_str.startswith("missing:"):
        prop_name = filter_str[8:].strip()
        return prop_name not in fm

    # Default: search in content
    return filter_str.lower() in content.lower()


def bulk_update(vault_path, filter_str=None, folder=None, set_props=None,
                remove_props=None, rename_props=None, dry_run=False, format_output="text"):
    """Bulk update properties across vault notes."""
    vault = pathlib.Path(vault_path).resolve()
    if not (vault / ".obsidian").exists():
        print(f"Error: {vault} is not a valid Obsidian vault")
        sys.exit(1)

    search_dir = vault / folder if folder else vault
    notes = sorted([
        f for f in search_dir.rglob("*.md")
        if not str(f.relative_to(vault)).startswith(".obsidian")
    ])

    matched = []
    for note_path in notes:
        content = note_path.read_text(encoding="utf-8", errors="ignore")
        fm, body = parse_note(content)
        if matches_filter(note_path, content, fm, filter_str, vault):
            matched.append((note_path, fm, body))

    if not matched:
        print("No matching notes found.")
        return

    action_label = "Would update" if dry_run else "Updated"
    updated_count = 0

    for note_path, fm, body in matched:
        rel = str(note_path.relative_to(vault)).replace("\\", "/")
        changed = False

        # Set properties
        if set_props:
            for prop in set_props:
                key, value = prop.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Type inference
                if value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                elif value.startswith("[") and value.endswith("]"):
                    value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass

                if fm.get(key) != value:
                    fm[key] = value
                    changed = True

        # Remove properties
        if remove_props:
            for prop in remove_props:
                if prop in fm:
                    del fm[prop]
                    changed = True

        # Rename properties
        if rename_props:
            for rename in rename_props:
                old_name, new_name = rename.split(":", 1)
                if old_name in fm:
                    fm[new_name] = fm.pop(old_name)
                    changed = True

        if changed:
            updated_count += 1
            if dry_run:
                print(f"  [DRY RUN] {action_label}: {rel}")
            else:
                new_content = serialize_note(fm, body)
                note_path.write_text(new_content, encoding="utf-8")
                print(f"  {action_label}: {rel}")

    print(f"\n{action_label} {updated_count}/{len(matched)} matching notes.")


def search_properties(vault_path, property_name=None, value=None, format_output="text"):
    """Search notes by property values."""
    vault = pathlib.Path(vault_path).resolve()
    notes = sorted([
        f for f in vault.rglob("*.md")
        if not str(f.relative_to(vault)).startswith(".obsidian")
    ])

    results = []
    for note_path in notes:
        content = note_path.read_text(encoding="utf-8", errors="ignore")
        fm, _ = parse_note(content)
        if not fm:
            continue

        if property_name:
            if property_name not in fm:
                continue
            if value is not None:
                prop_val = fm[property_name]
                if isinstance(prop_val, list):
                    if value not in prop_val:
                        continue
                elif str(prop_val).lower() != value.lower():
                    continue

        rel = str(note_path.relative_to(vault)).replace("\\", "/")
        results.append({"path": rel, "properties": fm})

    if format_output == "json":
        import json
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
    else:
        for r in results:
            props = ", ".join(f"{k}={v}" for k, v in r["properties"].items() if k != "tags")
            print(f"  {r['path']}")
            if property_name:
                print(f"    {property_name}: {r['properties'].get(property_name)}")

    print(f"\n{len(results)} notes found.")
    return results


def main():
    parser = argparse.ArgumentParser(description="Bulk property management for Obsidian")
    sub = parser.add_subparsers(dest="command", required=True)

    # Update command
    up = sub.add_parser("update", help="Bulk update properties")
    up.add_argument("--vault", required=True, help="Vault path")
    up.add_argument("--filter", help="Filter: tag:#x, path:folder/, property:key=val, missing:key")
    up.add_argument("--folder", help="Limit to folder")
    up.add_argument("--set", action="append", dest="set_props", help="Set property: key=value")
    up.add_argument("--remove", action="append", dest="remove_props", help="Remove property")
    up.add_argument("--rename", action="append", dest="rename_props", help="Rename: old:new")
    up.add_argument("--dry-run", action="store_true", help="Preview without changes")

    # Search command
    sr = sub.add_parser("search", help="Search by properties")
    sr.add_argument("--vault", required=True, help="Vault path")
    sr.add_argument("--property", help="Property name to search")
    sr.add_argument("--value", help="Property value to match")
    sr.add_argument("--format", choices=["text", "json"], default="text")

    args = parser.parse_args()

    if args.command == "update":
        bulk_update(
            vault_path=args.vault,
            filter_str=args.filter,
            folder=args.folder,
            set_props=args.set_props,
            remove_props=args.remove_props,
            rename_props=args.rename_props,
            dry_run=args.dry_run,
        )
    elif args.command == "search":
        search_properties(
            vault_path=args.vault,
            property_name=args.property,
            value=args.value,
            format_output=args.format,
        )


if __name__ == "__main__":
    main()
