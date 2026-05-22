# Skill Manager

Interactive tool for managing installed agent skills with a beautiful `fzf`-powered interface.

## ✨ Features

- 🎯 **Interactive selection** with fuzzy search
- 📦 **Multi-select** with TAB key
- 🔍 **Real-time filtering** as you type
- 🌍 **Scope selection** - choose global, local, or both
- 🏷️ **Location tags** - see where each skill is installed ([copilot], [local], etc.)
- ✅ **Safe uninstallation** with confirmation
- 🎨 **Cross-platform** (macOS, Linux, WSL)

## 🚀 Quick Start

### 1. Install fzf (if not already installed)

```bash
# macOS
brew install fzf

# Ubuntu/Debian/WSL
sudo apt update && sudo apt install fzf

# Fedora
sudo dnf install fzf
```

### 2. Run the interactive uninstaller

```bash
cd skill-manager
chmod +x scripts/uninstall-interactive.sh
./scripts/uninstall-interactive.sh
```

## 📖 How to Use

### Uninstall Skills Interactively

1. Run `./scripts/uninstall-interactive.sh`
2. **Choose scope:**
   - `1) Global only` - Skills in `~/.{copilot,claude,cursor,agents}/skills`
   - `2) Local only` - Skills in `.agents/skills` (current project)
   - `3) Both` - All locations
3. A list of installed skills appears with location tags
4. Navigate with ⬆️⬇️ arrow keys
5. Type to filter instantly
6. Press `TAB` to select (or unselect)
7. Press `ENTER` to uninstall selected skills
8. Press `ESC` or `Ctrl+C` to cancel

### Example Session

```
$ ./scripts/uninstall-interactive.sh

ℹ️ Found 2 skill location(s):
  - /Users/you/.copilot/skills
  - .agents/skills

ℹ️ Choose skill scope:

  1) Global only  (~/.*/skills)
  2) Local only   (.agents/skills)
  3) Both         (all locations)

Select [1-3]: 3

ℹ️ Using scope: both (2 location(s))

┌─────────────────────────────────────────┐
│  Select skills to uninstall (TAB=select)│
└─────────────────────────────────────────┘

  [copilot] graph-it-live
> [copilot] dead-code-hunter [✓]
  [local] obsidian-commander [✓]
  [local] onboarding-express

2/4 selected

⚠️ Proceed with uninstallation? [y/N] y

  Removing dead-code-hunter from ~/.copilot/skills... ✓
  Removing obsidian-commander from .agents/skills... ✓

✅ Successfully uninstalled 2 skill(s)
```

## 🎯 Supported Platforms

The script automatically detects your agent platform:

| Platform | Skill Directory |
|----------|----------------|
| **VS Code / GitHub Copilot** | `~/.copilot/skills/` |
| **Claude Code** | `~/.claude/skills/` |
| **Cursor** | `~/.cursor/skills/` |
| **Generic Agent Framework** | `~/.agents/skills/` |
| **Project-Local** | `.agents/skills/` |

**Detection Priority:**
1. Custom `SKILLS_DIR` environment variable (highest priority)
2. `~/.copilot/skills/` (global)
3. `~/.claude/skills/` (global)
4. `~/.cursor/skills/` (global)
5. `~/.agents/skills/` (global)
6. `.agents/skills/` (project-local, lowest priority)

**Note:** If you have multiple skill directories, the first one found is used. To target a specific directory, use `SKILLS_DIR`:

```bash
# Target project-local skills
SKILLS_DIR=.agents/skills ./scripts/uninstall-interactive.sh

# Target global agent skills
SKILLS_DIR=~/.agents/skills ./scripts/uninstall-interactive.sh
```

## 🛠️ Advanced Usage

### Select Scope Non-Interactively

```bash
# Global skills only
./scripts/uninstall-interactive.sh --scope global

# Local skills only
./scripts/uninstall-interactive.sh --scope local

# All locations
./scripts/uninstall-interactive.sh --scope both
```

### Custom Skill Directory

Override the default directory (bypasses scope selection):

```bash
export SKILLS_DIR="/path/to/custom/skills"
./scripts/uninstall-interactive.sh

# Or inline
./scripts/uninstall-interactive.sh --dir /path/to/custom/skills
```

### List All Installed Skills

```bash
# Auto-detect platform and list
./scripts/uninstall-interactive.sh --list

# Or manually
ls -1 ~/.copilot/skills/
```

### Uninstall Without fzf (Manual)

If you prefer not to use fzf:

```bash
# VS Code / GitHub Copilot
rm -rf ~/.copilot/skills/<skill-name>

# Claude Code
rm -rf ~/.claude/skills/<skill-name>

# Cursor
rm -rf ~/.cursor/skills/<skill-name>

# Generic Agent Framework
rm -rf ~/.agents/skills/<skill-name>

# Project-Local
rm -rf .agents/skills/<skill-name>
```

## 🔧 Troubleshooting

### "fzf: command not found"

Install fzf first (see Quick Start section above).

### "No skills found"

Possible causes:
- No skills installed yet
- Wrong platform detected (set `SKILLS_DIR` manually)
- Skills installed in non-standard location

Check your skill directory:

```bash
echo $SKILLS_DIR
ls -la ~/.copilot/skills/
```

### "Permission denied"

Make the script executable:

```bash
chmod +x scripts/uninstall-interactive.sh
```

Or run with bash:

```bash
bash scripts/uninstall-interactive.sh
```

## 🎨 Customization

### Change fzf Appearance

The script uses default fzf settings. Customize via environment variables:

```bash
export FZF_DEFAULT_OPTS="--height 40% --border --preview 'echo {}'"
./scripts/uninstall-interactive.sh
```

See [fzf documentation](https://github.com/junegunn/fzf) for more options.

## 📦 Installation with npx skills

```bash
# Install this skill
npx skills add magic5644/skills/skill-manager

# Then use it
cd ~/.copilot/skills/skill-manager
./scripts/uninstall-interactive.sh
```

## 🤝 Contributing

Found a bug or have a suggestion? Open an issue or submit a PR!

## 📄 License

Same as parent repository.

## 🔗 Related Skills

- [graph-it-live](../graph-it-live/) — Dependency analysis and architecture
- [dead-code-hunter](../dead-code-hunter/) — Find and remove unused code
- [obsidian-commander](../obsidian-commander/) — Manage Obsidian vaults
