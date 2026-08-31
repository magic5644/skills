---
mode: agent
description: Run the SkillOpt optimization loop on this repository's skills from GitHub Copilot Chat
tools: ['codebase', 'search', 'runCommands', 'terminalLastCommand']
---

# Optimize a skill with SkillOpt

Ask which skill to optimize if the user did not name one (`dead-code-hunter`, `graph-it-live`,
`obsidian-commander`, `onboarding-express`, `pr-review`, `skill-manager`, or all of them).

## Procedure

1. If `.skillopt/venv/bin/python` does not exist, run `scripts/skillopt-bootstrap.sh`.

2. Validate the wiring without spending tokens:

   ```bash
   .skillopt/venv/bin/python optimization/selftest.py
   ```

3. Run the optimization through the GitHub Copilot CLI, which uses your Copilot subscription
   rather than a provider API key:

   ```bash
   scripts/skillopt-optimize.sh <skill> --preset copilot
   ```

   Add `--dry-run` first (1 epoch, 2 items per split) when the setup has never run on this
   machine. Use `--preset claude-code-copilot` to exercise the skill inside the Claude Code CLI
   while keeping the Copilot CLI as the optimizer.

4. Report from `optimization/outputs/<skill>/<stamp>/summary.json`: baseline vs optimized
   held-out score, accepted and rejected edits, wall time, token usage.

5. Diff the produced `best_skill.md` against the live `<skill>/SKILL.md` and summarise the edits.
   Flag anything that weakens the frontmatter `description` triggers or contradicts a documented
   CLI flag.

6. Do **not** pass `--adopt` unless the user explicitly asks. Adoption requires a strict held-out
   improvement and writes a `SKILL.md.bak-<stamp>` backup; the user reviews `git diff` and commits.

Reference: `optimization/README.md`.
