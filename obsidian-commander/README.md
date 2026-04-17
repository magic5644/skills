# Obsidian Commander

**Manage your Obsidian vault from any AI agent-compatible IDE or CLI.**

Obsidian Commander is a comprehensive **AI skill** that lets you manage all features of an Obsidian vault — note creation, semantic search, frontmatter management, link auditing, cleanup, organization, content ingestion — directly from your code editor or a terminal.

---

## Table of Contents

- [Obsidian Commander](#obsidian-commander)
  - [Table of Contents](#table-of-contents)
  - [Supported Environments](#supported-environments)
  - [Prerequisites](#prerequisites)
    - [Required](#required)
    - [Optional](#optional)
    - [Python Dependencies](#python-dependencies)
  - [Installation](#installation)
    - [Automatic Installation (all IDEs)](#automatic-installation-all-ides)
    - [Manual Installation per IDE](#manual-installation-per-ide)
    - [Installation as a Project Skill](#installation-as-a-project-skill)
  - [Project Structure](#project-structure)
  - [Usage Guide](#usage-guide)
    - [1. Create Notes](#1-create-notes)
      - [Via the AI Agent](#via-the-ai-agent)
      - [Via Command Line](#via-command-line)
      - [Via Obsidian CLI (if Obsidian is open)](#via-obsidian-cli-if-obsidian-is-open)
    - [2. Search the Vault](#2-search-the-vault)
      - [Text Search (Obsidian CLI)](#text-search-obsidian-cli)
      - [Property Search (script)](#property-search-script)
      - [AI Semantic Search](#ai-semantic-search)
    - [3. Manage Frontmatter (Properties)](#3-manage-frontmatter-properties)
      - [Reading](#reading)
      - [Single Edit (Obsidian CLI)](#single-edit-obsidian-cli)
      - [Bulk Edit (script)](#bulk-edit-script)
    - [4. Audit and Map Links](#4-audit-and-map-links)
      - [Quick Commands (Obsidian CLI)](#quick-commands-obsidian-cli)
      - [Full Audit (script)](#full-audit-script)
    - [5. Clean Up the Vault](#5-clean-up-the-vault)
      - [Step 1: Generate a Report (dry-run)](#step-1-generate-a-report-dry-run)
      - [Step 2: Apply Fixes](#step-2-apply-fixes)
    - [6. Organize Vault Structure](#6-organize-vault-structure)
      - [Create a Structure from a Template](#create-a-structure-from-a-template)
      - [Move and Rename (Obsidian CLI)](#move-and-rename-obsidian-cli)
    - [7. Ingest External Content](#7-ingest-external-content)
      - [Single File](#single-file)
      - [Entire Folder](#entire-folder)
      - [Append to Today's Note](#append-to-todays-note)
    - [8. Semantic Search (AI)](#8-semantic-search-ai)
      - [Build the Index](#build-the-index)
      - [Update the Index](#update-the-index)
      - [Search](#search)
      - [Choose a Different Model](#choose-a-different-model)
    - [9. Vault Health Report](#9-vault-health-report)
    - [10. Daily Notes and Tasks](#10-daily-notes-and-tasks)
      - [Via Obsidian CLI](#via-obsidian-cli)
      - [Via Script (without Obsidian)](#via-script-without-obsidian)
    - [11. Plugins and Themes (via CLI)](#11-plugins-and-themes-via-cli)
  - [Using with AI Agents](#using-with-ai-agents)
    - [VS Code / GitHub Copilot](#vs-code--github-copilot)
    - [Claude Code / Claude CLI](#claude-code--claude-cli)
    - [Cursor](#cursor)
    - [Copilot CLI](#copilot-cli)
  - [Script Reference](#script-reference)
  - [Obsidian CLI](#obsidian-cli)
  - [FAQ](#faq)
    - [The skill doesn't trigger automatically](#the-skill-doesnt-trigger-automatically)
    - [Error "Not a valid Obsidian vault"](#error-not-a-valid-obsidian-vault)
    - [Semantic search is slow](#semantic-search-is-slow)
    - [How to use with a vault on a NAS / cloud?](#how-to-use-with-a-vault-on-a-nas--cloud)
    - [`obsidian` commands don't work](#obsidian-commands-dont-work)
  - [License](#license)

---

## Supported Environments

| Environment | Type | Skill Path |
| --- | --- | --- |
| **VS Code + GitHub Copilot** | IDE | `~/.copilot/skills/obsidian-commander/` |
| **Claude Code** | CLI | `~/.claude/skills/obsidian-commander/` |
| **Claude CLI** | CLI | `~/.claude/skills/obsidian-commander/` |
| **Cursor** | IDE | `~/.agents/skills/obsidian-commander/` |
| **Copilot CLI** | CLI | `~/.copilot/skills/obsidian-commander/` |
| **Other compatible agents** | IDE/CLI | `~/.agents/skills/obsidian-commander/` |
| **Specific project** | Workspace | `.github/skills/obsidian-commander/` |

---

## Prerequisites

### Required

- **Python 3.9+** (for vault management scripts)
- **An Obsidian vault** (folder containing `.obsidian/`)

### Optional

- **Obsidian 1.12.7+** with CLI enabled (for real-time `obsidian` commands)
- **GPU** (speeds up semantic indexing, but not required — works on CPU)

### Python Dependencies

```
sentence-transformers    # AI model for semantic search
faiss-cpu                # Fast vector index
numpy                    # Numerical computing
pyyaml                   # YAML/frontmatter parsing
tqdm                     # Progress bars
beautifulsoup4           # HTML parsing (for ingestion)
markdownify              # HTML to Markdown conversion
```

---

## Installation

### Automatic Installation (all IDEs)

The installer copies the skill to all compatible locations in a single command.

**Windows (PowerShell):**

```powershell
cd c:\github\obsidian-commander

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install the skill in all IDEs
python scripts\install_skill.py --target all
```

**macOS / Linux:**

```bash
cd ~/github/obsidian-commander

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install the skill in all IDEs
python scripts/install_skill.py --target all
```

Or use the shell script:

```bash
bash install.sh
```

### Manual Installation per IDE

If you prefer to install for a single environment only:

```bash
# VS Code / GitHub Copilot only
python scripts/install_skill.py --target copilot

# Claude Code / Claude CLI only
python scripts/install_skill.py --target claude

# Cursor / other agents
python scripts/install_skill.py --target agents
```

### Installation as a Project Skill

To make the skill available only in a specific project (shareable via Git):

```bash
python scripts/install_skill.py --target project --project-dir /path/to/your/project
```

This creates the `.github/skills/obsidian-commander/` folder in the target project.

---

## Project Structure

```
obsidian-commander/
├── SKILL.md                        # Required: metadata + instructions (read by AI agent)
├── README.md                       # This file
│
├── references/                     # Reference documentation (loaded on demand)
│   ├── obsidian-cli.md             #   Obsidian CLI commands (40+ commands)
│   └── obsidian-markdown.md        #   Obsidian syntax (frontmatter, links, tags)
│
└── scripts/                        # Executable Python scripts
    ├── bulk_properties.py          #   Bulk frontmatter management
    ├── create_note.py              #   Note creation with templates
    ├── ingest.py                   #   External content ingestion
    ├── install_skill.py            #   Cross-IDE installer
    ├── link_audit.py               #   Comprehensive link audit
    ├── scaffold_vault.py           #   Structure creation (PARA, Zettelkasten...)
    ├── semantic_search.py          #   AI semantic search (FAISS)
    ├── vault_cleanup.py            #   Vault cleanup
    └── vault_health.py             #   Health report
```

---

## Usage Guide

Each script can be used in **two ways**:

1. **Via the AI agent**: ask in natural language in your IDE's chat
2. **Via command line**: run the Python scripts directly

### 1. Create Notes

#### Via the AI Agent

Simply say:

> "Create a Meeting note in my Obsidian vault in the Projects folder"

> "Create a zettel-type note about the concept of Machine Learning"

#### Via Command Line

```bash
# Simple note
python scripts/create_note.py --vault /path/to/vault --name "My Note"

# Note with template and tags
python scripts/create_note.py --vault . --name "Sprint 42 Meeting" --template meeting --tags "meeting,sprint" --folder "Projects/Sprints"

# Note with content and links
python scripts/create_note.py --vault . --name "AI Concept" --template zettel --content "Generative AI is transforming..." --link-to "Machine Learning,Deep Learning"

# List available templates
python scripts/create_note.py --vault . --name x --list-templates
```

**Available templates:**

| Template | Description | Default Tags |
| --- | --- | --- |
| `default` | Standard note with minimal frontmatter | `[]` |
| `daily` | Daily note | `[daily]` |
| `meeting` | Meeting notes (agenda, notes, actions) | `[meeting]` |
| `project` | Project card (overview, goals, tasks) | `[project]` |
| `zettel` | Zettelkasten note (references, links) | `[]` |
| `literature` | Literature note (summary, quotes, thoughts) | `[literature-note]` |

#### Via Obsidian CLI (if Obsidian is open)

```bash
obsidian create name="My Note" content="# My Note\n\nContent here" open
obsidian create name="Sprint Review" template=Meeting
```

---

### 2. Search the Vault

#### Text Search (Obsidian CLI)

```bash
# Simple search
obsidian search query="microservices architecture"

# Search with context (shows lines around the match)
obsidian search:context query="TODO" path="Projects/"

# Search by tag
obsidian search query="tag:#urgent"

# Search by property
obsidian search query="[status:draft]"
```

#### Property Search (script)

```bash
# Find all notes with status=draft
python scripts/bulk_properties.py search --vault . --property status --value draft

# Find notes without frontmatter
python scripts/bulk_properties.py search --vault . --property tags

# JSON output
python scripts/bulk_properties.py search --vault . --property status --value active --format json
```

#### AI Semantic Search

See [dedicated section](#8-semantic-search-ai).

---

### 3. Manage Frontmatter (Properties)

Frontmatter is the YAML block at the top of each Obsidian note:

```yaml
---
title: My Note
tags:
  - project
  - active
created: 2024-01-15
status: draft
---
```

#### Reading

```bash
# Via Obsidian CLI
obsidian properties active                         # Properties of the active file
obsidian property:read name=tags file="My Note"    # Read a specific property

# Via script
python scripts/bulk_properties.py search --vault . --property status
```

#### Single Edit (Obsidian CLI)

```bash
obsidian property:set name=status value=published file="My Note"
obsidian property:set name=tags value="[project,completed]" type=list
obsidian property:remove name=draft file="My Note"
```

#### Bulk Edit (script)

```bash
# Set all notes tagged #draft to status=review
python scripts/bulk_properties.py update --vault . --filter "tag:#draft" --set "status=review"

# Add archived=true to all files in the Archive/ folder
python scripts/bulk_properties.py update --vault . --folder "Archive/" --set "archived=true"

# Rename a property across the entire vault
python scripts/bulk_properties.py update --vault . --rename "date:created"

# Remove a property from all notes
python scripts/bulk_properties.py update --vault . --remove "obsolete_field"

# Dry-run mode (preview without modifying)
python scripts/bulk_properties.py update --vault . --filter "tag:#draft" --set "status=review" --dry-run
```

**Available filters:**

| Filter | Example | Description |
| --- | --- | --- |
| `tag:#xxx` | `tag:#draft` | Notes having this tag |
| `path:xxx` | `path:Projects/` | Notes in this folder |
| `property:key=val` | `property:status=draft` | Property with this value |
| `missing:key` | `missing:created` | Notes missing this property |
| Free text | `"TODO"` | Content containing this text |

---

### 4. Audit and Map Links

#### Quick Commands (Obsidian CLI)

```bash
obsidian links file="My Note"       # Outgoing links
obsidian backlinks file="My Note"   # Incoming links
obsidian unresolved                 # Broken links in the entire vault
obsidian orphans                    # Notes with no incoming links
obsidian deadends                   # Notes with no outgoing links
```

#### Full Audit (script)

```bash
# Text report
python scripts/link_audit.py --vault /path/to/vault

# JSON report (for automated processing)
python scripts/link_audit.py --vault . --format json
```

**Sample output:**

```
==================================================
       VAULT LINK HEALTH REPORT
==================================================
  Total notes:          342
  Total links:          1,205
  Resolved:             1,180 (97.9%)
  Unresolved:           25
  Orphan notes:         18
  Dead-end notes:       45
  Unique tags:          89
  No frontmatter:       12
==================================================

Unresolved links (25):
  [[API Reference]] — referenced from: Projects/Backend.md, Notes/Architecture.md
  [[Config Guide]] — referenced from: Setup/Install.md

Orphan notes (18):
  Archive/old-idea.md
  Notes/random-thought.md
```

---

### 5. Clean Up the Vault

#### Step 1: Generate a Report (dry-run)

```bash
python scripts/vault_cleanup.py --vault . --action report
```

**Output:**

```
==================================================
       VAULT CLEANUP REPORT
==================================================
  Empty notes:               8
  Orphaned attachments:      15
  Duplicate tag variants:    3
  Notes without frontmatter: 12
==================================================

Empty notes (8):
  Notes/untitled.md
  Inbox/empty-idea.md
  ...

Orphaned attachments (15):
  Attachments/old-screenshot.png
  Attachments/diagram-v1.svg
  ...

Duplicate tag variants:
  project: ['project', 'Project']
  meeting: ['meeting', 'Meeting']
```

#### Step 2: Apply Fixes

```bash
# Standard fixes (adds missing frontmatter, removes empty notes)
python scripts/vault_cleanup.py --vault . --action fix

# With orphaned attachment removal (destructive!)
python scripts/vault_cleanup.py --vault . --action fix --fix-orphans
```

> **Warning:** `--fix-orphans` deletes files. Always run `--action report` first and review the list.

---

### 6. Organize Vault Structure

#### Create a Structure from a Template

```bash
# View available templates
python scripts/scaffold_vault.py --vault . --template zettelkasten --list

# Apply a template
python scripts/scaffold_vault.py --vault . --template para
```

**Organization templates:**

| Template | Folders Created | Philosophy |
| --- | --- | --- |
| `zettelkasten` | Inbox, Fleeting, Literature, Permanent, MOC | Interconnected atomic notes |
| `para` | Projects, Areas, Resources, Archive | Tiago Forte's PARA method |
| `gtd` | Inbox, Next Actions, Projects, Waiting For, Someday Maybe | Getting Things Done |
| `journal` | Daily Notes, Weekly Reviews, Monthly Reviews, Goals | Personal journal |
| `research` | Papers, Literature Review, Experiments, Data, Drafts | Academic research |

Each template also creates a `Templates/` folder with matching note templates.

#### Move and Rename (Obsidian CLI)

```bash
obsidian move file="Old Note" to="Archive/2024/"
obsidian rename file="Old Name" name="New Name"
```

---

### 7. Ingest External Content

Import external files into your vault.

#### Single File

```bash
# Import a Markdown file
python scripts/ingest.py --vault . file --source ~/Documents/notes.md

# Import an HTML file (converted to Markdown)
python scripts/ingest.py --vault . file --source ~/Downloads/article.html --folder "Inbox" --tags "web,article"

# Import a CSV (converted to Markdown table)
python scripts/ingest.py --vault . file --source data.csv --folder "Data"
```

#### Entire Folder

```bash
# Import all .md and .txt files from a folder
python scripts/ingest.py --vault . dir --source ~/old-notes/

# Import only .html files
python scripts/ingest.py --vault . dir --source ~/web-clips/ --ext ".html,.htm" --tags "web-clip"
```

#### Append to Today's Note

```bash
python scripts/ingest.py --vault . daily --content "- [ ] Idea to explore: autonomous agents"
```

**Supported formats:** `.md`, `.txt`, `.html`, `.htm`, `.csv`, `.json`

---

### 8. Semantic Search (AI)

Semantic search uses an AI model (sentence-transformers) to find notes by **meaning** rather than exact keywords.

#### Build the Index

**First use** (indexes all notes):

```bash
python scripts/semantic_search.py --vault /path/to/vault --action build
```

Duration: ~1-2 minutes for 500 notes on CPU. The index is stored in `.obsidian/ai_index/`.

#### Update the Index

After adding/modifying notes:

```bash
python scripts/semantic_search.py --vault . --action update
```

#### Search

```bash
# Text search
python scripts/semantic_search.py --vault . --action ask --query "how to manage team conflicts"

# More results
python scripts/semantic_search.py --vault . --action ask --query "machine learning" --top 20

# JSON output
python scripts/semantic_search.py --vault . --action ask --query "productivity" --format json
```

**Sample output:**

```
Top 5 results for: "how to manage team conflicts"

  1. [[Nonviolent Communication]] (Notes/NVC.md) — score: 0.823
  2. [[Conflict Management]] (Projects/Management/Conflicts.md) — score: 0.791
  3. [[Constructive Feedback]] (Areas/Leadership/Feedback.md) — score: 0.756
  4. [[Sprint 12 Retrospective]] (Projects/Sprints/Retro-12.md) — score: 0.698
  5. [[One on One Template]] (Templates/1on1.md) — score: 0.654
```

#### Choose a Different Model

```bash
# Lighter model (faster, less accurate)
python scripts/semantic_search.py --vault . --action build --model all-MiniLM-L6-v2

# Multilingual model (default, recommended for non-English content)
python scripts/semantic_search.py --vault . --action build --model paraphrase-multilingual-MiniLM-L12-v2
```

---

### 9. Vault Health Report

```bash
# Text report
python scripts/vault_health.py --vault /path/to/vault

# JSON report
python scripts/vault_health.py --vault . --format json
```

**Sample output:**

```
=======================================================
         OBSIDIAN VAULT HEALTH CHECK
=======================================================
  Vault:                  my-vault
  Total size:             45.2 MB
  Notes:                  342
  Attachments:            128
  Total words:            185,430
  Avg words/note:         542
-------------------------------------------------------
  With frontmatter:       330
  Without frontmatter:    12
  Internal links:         1,205
  Embeds:                 89
  Unique tags:            67
  Unique properties:      15
-------------------------------------------------------
  Recently modified (7d): 23
  Stale (>90d):           45
=======================================================

Top Tags:
  #project: 89
  #meeting: 67
  #idea: 45
  #daily: 342
  #draft: 23

Largest Notes (by words):
  Projects/Architecture.md: 12,450 words
  Resources/API-Guide.md: 8,230 words
```

---

### 10. Daily Notes and Tasks

#### Via Obsidian CLI

```bash
# Open today's note
obsidian daily

# Read the content
obsidian daily:read

# Add a task
obsidian daily:append content="- [ ] Call the client"

# Add text at the top of the note
obsidian daily:prepend content="## Goal for Today\n\nFinalize the proposal."

# List incomplete tasks in the vault
obsidian tasks todo

# List tasks from the daily note
obsidian tasks daily

# Toggle a task
obsidian task ref="Daily Notes/2026-04-17.md:5" toggle
```

#### Via Script (without Obsidian)

```bash
python scripts/ingest.py --vault . daily --content "- [ ] New important task"
```

---

### 11. Plugins and Themes (via CLI)

Requires Obsidian to be open with CLI enabled.

```bash
# List installed plugins
obsidian plugins

# Install and enable a plugin
obsidian plugin:install id=dataview enable

# Disable a plugin
obsidian plugin:disable id=daily-notes

# Reload a plugin (development)
obsidian plugin:reload id=my-plugin

# Manage themes
obsidian themes
obsidian theme:set name="Minimal"
obsidian theme:install name="Catppuccin" enable

# Manage CSS snippets
obsidian snippets
obsidian snippet:enable name="custom-headers"
```

---

## Using with AI Agents

The skill is designed to be **automatically invoked** by the AI agent when you ask questions related to Obsidian. Here's how to use it in each environment.

### VS Code / GitHub Copilot

1. Install the skill: `python scripts/install_skill.py --target copilot`
2. Open Copilot chat (`Ctrl+Shift+I`)
3. Type `/obsidian-commander` or ask your question directly:

**Example prompts:**

```
Create a "Client Meeting" note with the meeting template in my vault ~/Documents/notes
Semantically search for "hexagonal architecture" in my vault
Run a link audit on my vault
Clean up empty notes and show me the report first
Scaffold my vault with the PARA method
Show me my vault's health
Which notes don't have frontmatter?
Add the #review tag to all notes in the Draft/ folder
```

### Claude Code / Claude CLI

1. Install: `python scripts/install_skill.py --target claude`
2. Use in CLI:

```bash
claude "Create a zettel note about the concept of Domain-Driven Design in my vault ~/vault"
claude "Run a full link audit on my vault ~/notes"
```

### Cursor

1. Install: `python scripts/install_skill.py --target agents`
2. Use Cursor chat with the same prompts as for Copilot.

### Copilot CLI

```bash
gh copilot suggest "Find orphan notes in my Obsidian vault"
```

---

## Script Reference

| Script | Description | Quick Command |
| --- | --- | --- |
| `semantic_search.py` | AI semantic search | `--action build\|update\|ask` |
| `create_note.py` | Create notes with templates | `--name "X" --template meeting` |
| `link_audit.py` | Comprehensive link audit | `--vault .` |
| `bulk_properties.py` | Bulk frontmatter management | `update --set "k=v"` or `search --property k` |
| `vault_cleanup.py` | Vault cleanup | `--action report\|fix` |
| `vault_health.py` | Health report | `--vault . --format text\|json` |
| `scaffold_vault.py` | Create vault structure | `--template para\|zettelkasten\|gtd` |
| `ingest.py` | Import external content | `file --source X` or `dir --source X` |
| `install_skill.py` | Install the skill | `--target all\|copilot\|claude\|agents` |

All scripts accept `--help` for full documentation:

```bash
python scripts/semantic_search.py --help
python scripts/create_note.py --help
```

---

## Obsidian CLI

The skill integrates with the **official Obsidian CLI** (1.12.7+). See the [full reference](references/obsidian-cli.md) for all 40+ available commands.

**Enable the CLI:**

1. Obsidian → Settings → General → Enable "Command line interface"
2. Restart the terminal

**Most useful commands:**

```bash
obsidian vault                    # Vault info
obsidian files                    # List files
obsidian search query="X"        # Search
obsidian create name="X"         # Create
obsidian read file=X              # Read
obsidian daily                    # Today's note
obsidian tasks todo               # Pending tasks
obsidian tags counts              # Tags with counts
obsidian backlinks file=X         # Incoming links
obsidian eval code="..."          # Execute JS
```

---

## FAQ

### The skill doesn't trigger automatically

Check that `SKILL.md` is in the correct folder:

```bash
# Check installation
ls ~/.copilot/skills/obsidian-commander/SKILL.md    # Copilot
ls ~/.claude/skills/obsidian-commander/SKILL.md     # Claude
ls ~/.agents/skills/obsidian-commander/SKILL.md     # Agents
```

The `description` field in SKILL.md contains trigger keywords. If the agent doesn't load it, try `/obsidian-commander` explicitly.

### Error "Not a valid Obsidian vault"

The script looks for an `.obsidian/` folder at the specified path. Make sure:

- The path points to the **root** of the vault (not a subfolder)
- The vault has been opened at least once in Obsidian

### Semantic search is slow

- The first `build` downloads the model (~500 MB). Subsequent runs are fast.
- Use `--action update` instead of `build` for incremental updates.
- On a vault with 1000+ notes, expect 2-3 minutes for a full build on CPU.

### How to use with a vault on a NAS / cloud?

Simply point to the mounted path:

```bash
python scripts/vault_health.py --vault /mnt/nas/my-vault
python scripts/semantic_search.py --vault "D:\OneDrive\Obsidian\my-vault" --action build
```

### `obsidian` commands don't work

The Obsidian CLI requires:

1. Obsidian **1.12.7+** installed
2. CLI enabled in Settings → General
3. The Obsidian application **must be running**
4. The terminal **restarted** after activation

If the CLI is not available, all Python scripts work standalone without Obsidian.

---

## License

MIT — Free to use, modify, and redistribute.
