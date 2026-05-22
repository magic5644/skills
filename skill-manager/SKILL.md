---
name: skill-manager
description: |
  Interactive skill management for installed agent skills. Use this skill when the user wants to
  uninstall, remove, or manage their installed skills without typing names manually. Provides
  an interactive fzf-based interface for selecting and removing skills. Trigger for: "uninstall skills",
  "remove skills", "delete skills", "manage my skills", "clean up skills", "show installed skills",
  "désinstaller skills", "supprimer skills", "gérer mes skills".
argument-hint: 'Do you want to list or uninstall installed skills?'
context: fork
---

# Skill Manager

Interactive management tool for installed agent skills using `fzf` fuzzy finder.
Provides a visual selection interface to uninstall multiple skills at once.

## Prerequisites

- **fzf** installed (fuzzy finder for terminal)

```bash
# macOS
brew install fzf

# Ubuntu/Debian/WSL
sudo apt update && sudo apt install fzf

# Fedora
sudo dnf install fzf
```

## When to Use

- Remove skills interactively without typing names
- Bulk uninstall multiple skills at once
- List all installed skills
- Clean up skill directory before reinstalling
- Check which skills are currently installed

---

## Quick Actions

### Uninstall Skills Interactively

Use the interactive script to select and remove skills:

```bash
# From the skill-manager directory
./scripts/uninstall-interactive.sh
```

**How it works:**
1. Detects all installed skill locations
2. Prompts for scope: global, local, or both
3. Lists skills with location tags (e.g., `[copilot] skill-name`)
4. Opens fzf interactive selector
5. Navigate with arrow keys, filter by typing
6. Select multiple with `TAB`
7. Confirm with `ENTER` to uninstall

**Scope Options:**
- **Global**: Only `~/.copilot/skills/`, `~/.claude/skills/`, `~/.cursor/skills/`, `~/.agents/skills/`
- **Local**: Only `.agents/skills/` (project-local)
- **Both**: All locations (default)

**Skip scope prompt:**
```bash
# Uninstall global skills only
./scripts/uninstall-interactive.sh --scope global

# Uninstall local skills only
./scripts/uninstall-interactive.sh --scope local

# Uninstall from all locations
./scripts/uninstall-interactive.sh --scope both
```

### List Installed Skills

```bash
# VS Code / GitHub Copilot
ls -1 ~/.copilot/skills/

# Claude Code
ls -1 ~/.claude/skills/

# Cursor
ls -1 ~/.cursor/skills/

# Generic Agent Framework
ls -1 ~/.agents/skills/

# Project-Local
ls -1 .agents/skills/
```

---

## Agent Instructions

When the user wants to uninstall or manage skills:

1. **Detect multiple skill locations**: Check if user has both global and project-local skills
2. **Ask about scope** if not clear from context:
   - Global: Remove from `~/.{copilot,claude,cursor,agents}/skills`
   - Local: Remove from `.agents/skills` (project-specific)
   - Both: Remove from all locations
3. **Check if fzf is installed**: `command -v fzf`
4. **If fzf missing**: Guide user to install it first
5. **Run the interactive uninstaller**:
   - With scope: `./scripts/uninstall-interactive.sh --scope <global|local|both>`
   - Interactive: `./scripts/uninstall-interactive.sh` (prompts for scope)
6. **Confirm success**: List remaining skills after uninstallation

### Platform-Specific Directories

| Platform | Skill Directory |
|----------|----------------|
| VS Code / GitHub Copilot | `~/.copilot/skills/` |
| Claude Code | `~/.claude/skills/` |
| Cursor | `~/.cursor/skills/` |
| Generic Agent Framework | `~/.agents/skills/` |
| Project-Local | `.agents/skills/` |

**Detection Priority:**
1. Custom `SKILLS_DIR` environment variable
2. `~/.copilot/skills/` → `~/.claude/skills/` → `~/.cursor/skills/` → `~/.agents/skills/` → `.agents/skills/`

**Multiple Directories:** If user has both global and project-local skills, set `SKILLS_DIR` to target specific directory:
- Project-local: `SKILLS_DIR=.agents/skills ./scripts/uninstall-interactive.sh`
- Global agent: `SKILLS_DIR=~/.agents/skills ./scripts/uninstall-interactive.sh`

### Error Handling

- **fzf not found**: Provide installation instructions for user's OS
- **No skills installed**: Inform user and exit gracefully
- **Permission denied**: Check write permissions on skill directory
- **Canceled selection**: Exit without changes

---

## Advanced Usage

### Custom Skill Directory

Set a custom directory before running:

```bash
export SKILLS_DIR="/path/to/custom/skills"
./scripts/uninstall-interactive.sh
```

### Non-Interactive Uninstall

To remove a specific skill without the interactive interface:

```bash
# VS Code / GitHub Copilot
rm -rf ~/.copilot/skills/<skill-name>

# Claude Code
rm -rf ~/.claude/skills/<skill-name>
```

---

## Safety Features

- **Preview before deletion**: Shows selected skills before removal
- **Confirmation required**: Press ENTER to confirm
- **Cancel anytime**: ESC or Ctrl+C to abort
- **No hidden deletions**: All actions are visible and logged

## Troubleshooting

### fzf doesn't open

Check if fzf is in PATH:

```bash
which fzf
# Should output: /usr/local/bin/fzf or similar
```

### Script not executable

Make it executable:

```bash
chmod +x skill-manager/scripts/uninstall-interactive.sh
```

### Skills directory not found

Verify your agent's skill directory exists:

```bash
# Create if missing
mkdir -p ~/.copilot/skills/
```

---

## Related Skills

- **skill-manager** (this skill) — Interactive skill management
- **graph-it-live** — Dependency analysis and architecture
- **dead-code-hunter** — Find and remove unused code
