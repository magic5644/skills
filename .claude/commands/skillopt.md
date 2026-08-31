---
description: Run the SkillOpt optimization loop on this repository's skills from inside a Claude Code session
argument-hint: '[skill-name | --all] [--adopt] [--dry-run] [--preset claude-code|copilot|codex]'
allowed-tools: Bash(scripts/skillopt-*.sh:*), Bash(.skillopt/venv/bin/python:*), Read, Grep, Glob
---

Run and interpret a SkillOpt run for this repository. Arguments: `$ARGUMENTS`

## Procedure

1. **Check the toolchain.** If `.skillopt/venv/bin/python` is missing, run
   `scripts/skillopt-bootstrap.sh` first and say so.

2. **Pick the execution mode.**
   - No arguments, or a skill name only: use the repo default (chat backends, needs API
     credentials in `.env`).
   - `--preset claude-code`: the target agent is the Claude Code CLI itself, so the skill is
     exercised the way it is actually deployed. The optimizer role still needs
     `ANTHROPIC_API_KEY`; use `--preset claude-code-copilot` to drive the optimizer through the
     Copilot CLI instead, or `--preset copilot` / `--preset codex` for a fully CLI-driven run.
   - Verify credentials cheaply before a long run:
     `.skillopt/venv/bin/python optimization/selftest.py` (offline, no provider calls).

3. **Run it.**
   ```bash
   scripts/skillopt-optimize.sh <skill|--all> [--preset NAME] [--dry-run] [--epochs N]
   ```
   Never pass `--adopt` unless the user asked for it explicitly. Runs are long; report progress
   rather than re-running.

4. **Report the outcome** from `optimization/outputs/<skill>/<stamp>/summary.json`:
   baseline vs optimized test score, accepted/rejected edit counts, and the token cost.

5. **Show what changed.** Diff `best_skill.md` against the live `<skill>/SKILL.md` and summarise
   the edits by intent (trigger wording, command correctness, procedure, output contract, safety).
   Call out any edit that weakens the frontmatter `description` triggers — including the
   French ones — or that contradicts a documented CLI flag.

6. **Adoption is the user's call.** Adoption is gated on a strict held-out gain and always keeps a
   `SKILL.md.bak-<stamp>`. If the user wants it applied, re-run with `--adopt`, then show
   `git diff` and let them commit.

## Diagnosing a weak run

- Many rejected edits: the gate is doing its job; the val split (4 items) may be too small to
  resolve the gain. Add dataset items rather than loosening the gate.
- Every item fails the same criterion: usually a dataset problem (criterion not observable in the
  response text), not a skill problem.
- Negative-trigger items failing: the skill is over-firing; the fix belongs in the frontmatter
  `description`, not in the body.

Reference: `optimization/README.md`.
