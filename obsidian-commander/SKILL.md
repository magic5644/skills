---
name: obsidian-commander
description: 'Manage Obsidian vaults from any IDE or CLI. Use when: creating notes, searching vault, managing tags, updating properties/frontmatter, mapping links, cleaning orphans, organizing folders, building semantic index, ingesting content, bulk editing, vault health check, daily notes, templates, obsidian vault, obsidian search, obsidian links, obsidian tags, obsidian properties, obsidian cleanup, obsidian organize.'
argument-hint: 'What do you want to do in your Obsidian vault?'
---

# Obsidian Commander

Full-featured Obsidian vault management from any code editor or CLI.
Supports **VS Code (GitHub Copilot)**, **Claude Code**, **Cursor**, **Copilot CLI**, **Claude CLI**, and any agent-compatible IDE.

## When to Use

- Create, read, update, delete notes in a vault
- Search vault content (text, semantic, tags, properties)
- Manage frontmatter/properties (add, edit, remove, bulk update)
- Map and audit links (backlinks, orphans, unresolved, dead-ends)
- Clean up vault (remove orphans, fix broken links, deduplicate)
- Organize vault structure (move notes, create folders, apply templates)
- Build and query a semantic search index
- Ingest external content into the vault
- Generate vault health reports
- Manage daily notes, tasks, bookmarks, templates
- Control Obsidian app via CLI (requires Obsidian 1.12.7+)

## Quick Decision: CLI vs File-Based

| Approach | When | How |
|----------|------|-----|
| **Obsidian CLI** (`obsidian` command) | Obsidian app is running, need live interaction | See [CLI Reference](./references/obsidian-cli.md) |
| **File-based scripts** | Headless, CI/CD, batch operations, no Obsidian running | See [Scripts](./scripts/) |
| **Direct file editing** | Simple note creation/editing | Read/write `.md` files directly |

## Vault Detection

Before any operation, locate the vault:

1. Check if current working directory contains `.obsidian/` folder
2. If not, ask user for vault path
3. Validate: vault must contain `.obsidian/` directory

```
vault_path = find_ancestor_with(".obsidian") or ask_user("Vault path?")
```

## Core Procedures

### 1. Create a Note

```bash
# Via Obsidian CLI (if running)
obsidian create name="My Note" content="# My Note\n\nContent here"

# Via file system
# Create file at <vault>/path/Note.md with frontmatter
```

**Template for new note:**
```markdown
---
created: {{date}}
tags: []
aliases: []
---

# {{title}}

{{content}}
```

Use [create_note.py](./scripts/create_note.py) for advanced creation with templates and auto-linking.

### 2. Search the Vault

**Text search** (Obsidian CLI):
```bash
obsidian search query="meeting notes"
obsidian search:context query="TODO" path="Projects/"
```

**Semantic search** (AI-powered, works offline):
```bash
python scripts/semantic_search.py --vault /path/to/vault --action build   # Index
python scripts/semantic_search.py --vault /path/to/vault --action ask --query "concept"
```

**Property search** (find notes by metadata):
```bash
python scripts/search_properties.py --vault /path/to/vault --property status --value "draft"
```

**Search operators reference** (for Obsidian CLI):
| Operator | Example | Description |
|----------|---------|-------------|
| `file:` | `file:recipe` | Match filename |
| `path:` | `path:"Daily notes"` | Match file path |
| `tag:` | `tag:#work` | Match tag |
| `content:` | `content:"hello"` | Match content |
| `line:` | `line:(todo important)` | Match within same line |
| `section:` | `section:(dog cat)` | Match within same section |
| `task:` | `task:call` | Match in tasks |
| `task-todo:` | `task-todo:buy` | Match uncompleted tasks |
| `[property:value]` | `[status:draft]` | Match property value |

### 3. Manage Properties / Frontmatter

**Read properties:**
```bash
obsidian properties active                    # Current file
obsidian property:read name=tags file=MyNote  # Specific property
```

**Set properties:**
```bash
obsidian property:set name=status value=published file=MyNote
obsidian property:set name=tags value="[project,active]" type=list
```

**Bulk update** (use script for batch operations):
```bash
python scripts/bulk_properties.py --vault . --filter "tag:#draft" --set "status=review"
python scripts/bulk_properties.py --vault . --folder "Archive/" --set "archived=true" --type checkbox
```

**Property types:** `text`, `list`, `number`, `checkbox`, `date`, `datetime`

**YAML frontmatter format:**
```yaml
---
title: My Note
tags:
  - project
  - active
created: 2024-01-15
status: draft
aliases:
  - "my-note"
cssclasses:
  - wide-page
---
```

### 4. Map and Audit Links

**List links:**
```bash
obsidian links file=MyNote          # Outgoing links
obsidian backlinks file=MyNote      # Incoming links
obsidian unresolved                 # Broken links in vault
obsidian orphans                    # Notes with no incoming links
obsidian deadends                   # Notes with no outgoing links
```

**Full link audit** (comprehensive report):
```bash
python scripts/link_audit.py --vault /path/to/vault
```

Output:
```
=== Vault Link Health Report ===
Total notes: 342
Total links: 1,205
Resolved: 1,180 (97.9%)
Unresolved: 25
Orphan notes: 18
Dead-end notes: 45
Bidirectional links: 380
```

**Link formats in Obsidian:**
- Wikilinks: `[[Note Name]]`, `[[Note Name|Display Text]]`, `[[Note#Heading]]`, `[[Note#^block-id]]`
- Markdown: `[Display](Note.md)`, `[Display](Note.md#Heading)`
- Embeds: `![[Note]]`, `![[image.png]]`

### 5. Clean Up Vault

```bash
python scripts/vault_cleanup.py --vault /path/to/vault --action report  # Dry run
python scripts/vault_cleanup.py --vault /path/to/vault --action fix     # Apply fixes
```

**Cleanup operations:**
- Remove empty notes (no content beyond frontmatter)
- Fix broken internal links
- Remove duplicate notes
- Standardize frontmatter (ensure required fields)
- Clean orphaned attachments (images/files not linked anywhere)
- Normalize tag casing
- Remove stale TODO items

### 6. Organize Vault Structure

**Move and rename:**
```bash
obsidian move file=OldNote to="Archive/2024/"
obsidian rename file=OldName name="New Name"
```

**Batch organize:**
```bash
python scripts/organize_vault.py --vault . --strategy by-tag      # Group by primary tag
python scripts/organize_vault.py --vault . --strategy by-date     # Group by creation date
python scripts/organize_vault.py --vault . --strategy by-moc      # Group around Maps of Content
```

**Create folder structure from template:**
```bash
python scripts/scaffold_vault.py --vault . --template zettelkasten
python scripts/scaffold_vault.py --vault . --template para
python scripts/scaffold_vault.py --vault . --template gtd
```

Available templates: `zettelkasten`, `para` (Projects/Areas/Resources/Archive), `gtd`, `journal`, `research`, `custom`

### 7. Ingest External Content

```bash
python scripts/ingest.py --vault . --source /path/to/files --format markdown
python scripts/ingest.py --vault . --source /path/to/files --format html --convert
python scripts/ingest.py --vault . --source clipboard --as daily-append
python scripts/ingest.py --vault . --url "https://example.com/article" --as note
```

**Supported source formats:** Markdown, HTML, plain text, PDF (text extraction), CSV, JSON
**Ingestion modes:**
- `note`: Create a new note per file
- `append`: Append to an existing note
- `daily-append`: Append to today's daily note
- `split`: Split large documents into linked notes

### 8. Build Semantic Search Index

Uses sentence-transformers and FAISS for AI-powered semantic search:

```bash
# Build/rebuild index
python scripts/semantic_search.py --vault /path/to/vault --action build

# Query
python scripts/semantic_search.py --vault /path/to/vault --action ask --query "machine learning concepts" --top 10

# Incremental update (only new/modified notes)
python scripts/semantic_search.py --vault /path/to/vault --action update
```

**Requirements:** `pip install -r requirements.txt` (sentence-transformers, faiss-cpu, numpy, pyyaml, tqdm)

### 9. Daily Notes & Tasks

```bash
# Daily notes
obsidian daily                                          # Open today's daily note
obsidian daily:append content="- [ ] Buy groceries"     # Add task
obsidian daily:read                                     # Read content

# Tasks
obsidian tasks todo                                     # List incomplete tasks
obsidian tasks daily                                    # Tasks from daily note
obsidian task ref="Recipe.md:8" toggle                  # Toggle task
```

### 10. Templates

```bash
obsidian templates                                      # List templates
obsidian template:read name=Meeting resolve             # Preview with variables
obsidian create name="Standup 2024-01-15" template=Meeting
```

### 11. Vault Health Check

```bash
python scripts/vault_health.py --vault /path/to/vault
```

**Report includes:**
- Total notes, attachments, tags, properties
- Link health (resolved %, orphans, dead-ends, unresolved)
- Frontmatter consistency (missing required fields)
- Tag distribution and potential duplicates
- Large files and potential splits
- Recently modified vs stale notes
- Naming convention violations

### 12. Manage Plugins & Themes (via CLI)

```bash
obsidian plugins                                        # List installed
obsidian plugin:install id=dataview enable               # Install + enable
obsidian plugin:reload id=my-plugin                      # Reload (dev)
obsidian themes                                          # List themes
obsidian theme:set name="Minimal"                        # Set theme
```

## Obsidian Data Model Reference

**Vault structure:**
```
my-vault/
├── .obsidian/                 # Config folder (hidden)
│   ├── app.json               # App settings
│   ├── appearance.json        # Theme settings
│   ├── community-plugins.json # Installed plugins list
│   ├── core-plugins.json      # Core plugin toggles
│   ├── hotkeys.json           # Custom hotkeys
│   ├── plugins/               # Plugin data & settings
│   ├── themes/                # Installed themes
│   ├── snippets/              # CSS snippets
│   └── workspace.json         # Layout (exclude from git)
├── Notes/                     # Your notes (any structure)
├── Templates/                 # Template files
├── Attachments/               # Images, PDFs, etc.
└── Daily Notes/               # Daily notes folder
```

**Frontmatter (YAML between `---` markers):**
- Default properties: `tags` (list), `aliases` (list), `cssclasses` (list)
- Custom properties: any key-value pairs
- Types: text, list, number, checkbox, date, datetime

**Link syntax:**
| Format | Example |
|--------|---------|
| Wikilink | `[[Note]]` |
| With alias | `[[Note\|Display]]` |
| To heading | `[[Note#Heading]]` |
| To block | `[[Note#^block-id]]` |
| Embed | `![[Note]]` or `![[image.png]]` |
| Markdown | `[text](Note.md)` |

**Tags:** `#tag`, `#nested/tag`, in frontmatter as `tags: [a, b]`

## Installation

### As a personal skill (all your projects)

**VS Code / GitHub Copilot:**
```bash
mkdir -p ~/.copilot/skills/obsidian-commander
cp -r . ~/.copilot/skills/obsidian-commander/
```

**Claude Code:**
```bash
mkdir -p ~/.claude/skills/obsidian-commander
cp -r . ~/.claude/skills/obsidian-commander/
```

**Generic agents:**
```bash
mkdir -p ~/.agents/skills/obsidian-commander
cp -r . ~/.agents/skills/obsidian-commander/
```

### As a project skill

```bash
# In your vault or project root
mkdir -p .github/skills/obsidian-commander
cp -r . .github/skills/obsidian-commander/
```

### Install Python dependencies (for scripts)

```bash
pip install sentence-transformers faiss-cpu numpy pyyaml tqdm beautifulsoup4 markdownify
```

## Workflow Examples

**"I want to capture a quick idea"**
```bash
obsidian create name="Idea - Quantum Computing" content="# Quantum Computing\n\n- Potential for ML acceleration\n- Read more about Shor's algorithm" open
obsidian property:set name=tags value="[idea,quantum,research]" type=list
```

**"Show me everything related to Project X"**
```bash
obsidian search query="Project X"
obsidian search:context query="tag:#project-x"
python scripts/semantic_search.py --vault . --action ask --query "Project X goals and deliverables"
```

**"Clean up my vault"**
```bash
python scripts/vault_health.py --vault .
python scripts/vault_cleanup.py --vault . --action report
python scripts/vault_cleanup.py --vault . --action fix
```

**"Reorganize by PARA method"**
```bash
python scripts/scaffold_vault.py --vault . --template para
python scripts/organize_vault.py --vault . --strategy by-tag --mapping "project:Projects,area:Areas,resource:Resources,archive:Archive"
```
