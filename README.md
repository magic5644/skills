# Skills

A collection of AI agent skills for VS Code (GitHub Copilot), Claude Code, Cursor, and any agent-compatible IDE.

Each subfolder contains a self-contained skill with a `SKILL.md` file that agents load automatically when a matching request is detected.

## Available Skills

| Skill | Description |
| ----- | ----------- |
| [obsidian-commander](./obsidian-commander/) | Manage Obsidian vaults from any IDE or CLI |
| [graph-it-live](./graph-it-live/) | Analyze code dependencies, call graphs, and architecture |
| [onboarding-express](./onboarding-express/) | Guided architectural tour for new developers using Graph-It-Live |
| [dead-code-hunter](./dead-code-hunter/) | Scan the dependency graph for orphan symbols and propose safe deletions |

## Installation

### Option 1 — Install a single skill with `npx skills`

```bash
npx skills add magic5644/skills/<skill-name>
```

Replace `<skill-name>` with any folder name listed above. Examples:

```bash
npx skills add magic5644/skills/obsidian-commander
npx skills add magic5644/skills/graph-it-live
```

### Option 2 — Clone the repository

```bash
git clone https://github.com/magic5644/skills.git
```

Then copy the skill folder you need to your agent's skill directory:

**VS Code / GitHub Copilot:**

```bash
cp -r skills/<skill-name> ~/.copilot/skills/<skill-name>
```

**Claude Code:**

```bash
cp -r skills/<skill-name> ~/.claude/skills/<skill-name>
```

**Generic agents:**

```bash
cp -r skills/<skill-name> ~/.agents/skills/<skill-name>
```

**As a project skill** (scoped to a single repo):

```bash
cp -r skills/<skill-name> .github/skills/<skill-name>
```

### Option 3 — Install as a VS Code personal skill (Windows)

```powershell
Copy-Item -Recurse skills\<skill-name> "$env:USERPROFILE\.copilot\skills\<skill-name>"
```

## License

[MIT](./LICENSE)
