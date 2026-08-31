# Skills

A collection of AI agent skills for VS Code (GitHub Copilot), Claude Code, Cursor, and any agent-compatible IDE.

Each subfolder contains a self-contained skill with a `SKILL.md` file that agents load automatically when a matching request is detected.

## Available Skills

| Skill | Description |
| ----- | ----------- |
| [skill-manager](./skill-manager/) | Interactive skill management - uninstall skills with fzf fuzzy finder |
| [obsidian-commander](./obsidian-commander/) | Manage Obsidian vaults from any IDE or CLI |
| [graph-it-live](./graph-it-live/) | Analyze code dependencies, call graphs, and architecture |
| [graph-it-refactor](./graph-it-refactor/) | Safe two-phase refactoring with Graph-It-Live impact mapping before edits |
| [onboarding-express](./onboarding-express/) | Guided architectural tour for new developers using Graph-It-Live |
| [dead-code-hunter](./dead-code-hunter/) | Scan the dependency graph for orphan symbols and propose safe deletions |
| [pr-review](./pr-review/) | Review Git diffs with Graph-It-Live risk, impact, and GitHub Actions evidence |

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

## Skill Optimization (SkillOpt)

Every skill in this repository is optimizable with [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt):
each `SKILL.md` is treated as a trainable document, scored against a rubric dataset, and improved
through bounded edits that are kept only when a held-out validation score improves.

```bash
scripts/skillopt-bootstrap.sh                  # install the toolchain into .skillopt/
scripts/skillopt-optimize.sh --list            # optimizable skills
scripts/skillopt-optimize.sh pr-review         # optimize one skill
scripts/skillopt-optimize.sh --all --adopt     # optimize all, write back only real gains
scripts/skillopt-sleep.sh --install-cron       # nightly learning from local agent transcripts
```

No provider API key? Run the loop through an agent CLI you already pay for — the skill is then
installed in a throwaway workspace and exercised by the real agent:

```bash
scripts/skillopt-optimize.sh pr-review --preset copilot              # GitHub Copilot CLI
scripts/skillopt-optimize.sh pr-review --preset claude-code-copilot  # Claude Code target
```

From inside a session: `/skillopt` in Claude Code (`.claude/commands/skillopt.md`) or in
GitHub Copilot Chat (`.github/prompts/skillopt.prompt.md`).

The nightly loop harvests local Claude Code, Codex, GitHub Copilot, Cursor, Pi and OpenCode
sessions, mines the tasks you actually repeat, and stages validation-gated skill edits for review.

See [optimization/README.md](./optimization/README.md) for datasets, configuration, scoring, and
the data-boundary notes.

## License

[MIT](./LICENSE)
