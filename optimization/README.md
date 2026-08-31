# Skill Optimization with Microsoft SkillOpt

This directory turns every `SKILL.md` in this repository into a **trainable document**.
It wires [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) to a custom benchmark
environment (`agentskill`) that scores a skill document against realistic user requests using
an LLM judge and a per-item rubric, then lets SkillOpt propose bounded edits that are kept
only when a held-out validation score improves.

Two loops are available:

| Loop | Command | What it uses | Cadence |
|---|---|---|---|
| **Offline optimization** | `scripts/skillopt-optimize.sh` | the curated datasets in `optimization/datasets/` | on demand, before a release |
| **Daily consolidation (Sleep)** | `scripts/skillopt-sleep.sh` | your own local agent transcripts (Claude Code, Codex, Copilot, Cursor, Pi, OpenCode) | nightly cron |

---

## 1. Install

```bash
scripts/skillopt-bootstrap.sh
```

This clones SkillOpt into `.skillopt/SkillOpt`, creates `.skillopt/venv`, installs the package,
and copies SkillOpt's `.env.example` to `.env` if you don't have one. Both are git-ignored.

Then fill `.env` with credentials for the backend you intend to use. SkillOpt separates two roles:

- **target** — the model that plays the agent reading the skill document
- **optimizer** — the stronger model that reflects on failures, writes edits, and judges rubrics

Supported backends: `openai_chat`, `claude_chat`, `qwen_chat`, `minimax_chat`, `copilot_chat`,
`openai_compatible`, plus exec targets (`codex_exec`, `claude_code_exec`, `cursor_exec`, `copilot_exec`).
The `agentskill` environment calls `chat_target` / `chat_optimizer`, so use a **chat** backend for both
roles; exec targets would need a dedicated harness.

Verify the wiring before spending tokens:

```bash
.skillopt/venv/bin/python optimization/selftest.py        # offline, stubs both models and the agent CLI
scripts/skillopt-optimize.sh pr-review --dry-run --backend claude_chat   # 1 epoch, 2 items, real calls
```

---

## 2. Optimize

```bash
scripts/skillopt-optimize.sh --list                      # which skills are optimizable
scripts/skillopt-optimize.sh pr-review                   # one skill
scripts/skillopt-optimize.sh --all                       # every skill, sequentially
scripts/skillopt-optimize.sh --all --epochs 2 --adopt    # and write back the winners
scripts/skillopt-optimize.sh graph-it-live -- --cfg-options optimizer.learning_rate=2
```

Each run writes to `optimization/outputs/<skill>/<timestamp>/`:

| File | Contents |
|---|---|
| `best_skill.md` | the optimized skill document |
| `summary.json` | baseline vs optimized scores, accepted/rejected edits, token usage |
| `predictions/<item-id>/conversation.json` | the rollout used for reflection |
| `predictions/<item-id>/verdict.json` | rubric verdict per item |

`optimization/adopt.py` runs after every optimization and prints the report. **Adoption is gated**:
`--adopt` writes `best_skill.md` over `<skill>/SKILL.md` only when the held-out *test* hard score
strictly improved, and always keeps a `SKILL.md.bak-<stamp>` next to it. Without `--adopt`, nothing
in the repository is touched.

Score a document without training it:

```bash
scripts/skillopt-eval.sh pr-review --split valid_unseen
scripts/skillopt-eval.sh --all --split valid_unseen        # baseline the whole repo
scripts/skillopt-eval.sh pr-review --skill optimization/outputs/pr-review/<stamp>/best_skill.md
```

---

## 3. Running through your Claude Code / Copilot / Codex session

The `agentskill` environment supports two execution modes.

| Mode | Target backend | What the target sees | Credentials |
|---|---|---|---|
| **chat** (default) | `openai_chat`, `claude_chat`, `copilot_chat`, `openai_compatible`, ... | skill document as the system prompt | provider API key (except `copilot_chat`, which uses the Copilot CLI login) |
| **exec** | `claude_code_exec`, `copilot_exec`, `codex_exec`, `cursor_exec` | the skill installed as a real skill file in an isolated workspace, driven by the actual agent CLI | the CLI's own authentication — no API key |

Exec mode is deployment-faithful: the document is written verbatim into
`<workspace>/.agents/skills/skillopt-target/SKILL.md`, frontmatter included, and the agent decides
on its own whether the skill applies. That makes the `description` triggers part of what is being
measured. Rollouts are read-only (`allow_file_edits=False`) inside a throwaway workspace.

Presets wire both roles for you:

```bash
scripts/skillopt-optimize.sh pr-review --preset copilot                 # Copilot CLI, no API key
scripts/skillopt-optimize.sh pr-review --preset codex                   # Codex CLI, no API key
scripts/skillopt-optimize.sh pr-review --preset claude-code --model sonnet
scripts/skillopt-optimize.sh pr-review --preset claude-code-copilot     # Claude target, Copilot optimizer
scripts/skillopt-eval.sh pr-review --preset copilot --split valid_unseen
```

| Preset | Optimizer role | Target role | Needs an API key? |
|---|---|---|---|
| `copilot` | `copilot_chat` | `copilot_exec` | no — GitHub Copilot subscription |
| `codex` | `codex_exec` | `codex_exec` | no — ChatGPT/Codex login |
| `claude-code` | `claude_chat` | `claude_code_exec` | yes, `ANTHROPIC_API_KEY` for the optimizer only |
| `claude-code-copilot` | `copilot_chat` | `claude_code_exec` | no |

**Why the optimizer role is the constraint.** SkillOpt's reflection, edit and merge stages call
`chat_optimizer`, which accepts only chat backends plus `codex_exec`. The Claude Code CLI is not
one of them, so a Claude-only setup still needs an API key for the optimizer — or pair the Claude
Code target with the Copilot or Codex CLI as optimizer.

Presets drop `env.workers` to 2, since each exec rollout spawns a CLI process; `env.exec_timeout`
(default 300s) bounds each call. A 6-item epoch through an agent CLI takes minutes, not seconds.

### From inside a session

- **Claude Code**: `/skillopt <skill> [--preset claude-code] [--dry-run]` — see
  `.claude/commands/skillopt.md`. It runs the scripts, reads `summary.json`, diffs the candidate
  against the live document, and never adopts unless you ask.
- **GitHub Copilot Chat (VS Code)**: `/skillopt` — see `.github/prompts/skillopt.prompt.md`.
- **Copilot CLI / Claude CLI / any agent**: the shell scripts are the interface; nothing else is
  required.

---

## 4. Daily improvement from real sessions (SkillOpt-Sleep)

Sleep harvests your **local** agent transcripts, mines the tasks you actually repeat, replays them,
and stages validation-gated edits to the skills in this repo.

```bash
scripts/skillopt-sleep.sh --install-config    # ~/.skillopt-sleep/config.json from the template here
scripts/skillopt-sleep.sh harvest             # read transcripts only, stage nothing
scripts/skillopt-sleep.sh dry-run             # full cycle, report only
scripts/skillopt-sleep.sh run                 # full cycle, proposals staged for review
scripts/skillopt-sleep.sh status              # state + latest staged proposal
scripts/skillopt-sleep.sh adopt --skill pr-review
scripts/skillopt-sleep.sh --install-cron      # nightly at 03:30, logs to optimization/outputs/sleep/
```

Sources are auto-detected from what exists on the machine (`~/.claude/projects`, `~/.codex`,
`~/.cursor`, VS Code `workspaceStorage` for Copilot Chat, `~/.pi/agent/sessions`); override with
`--sources "claude codex"`. The script sweeps one source per cycle and stages each proposal separately.

`skill_roots` points at the repository root, so every `<skill>/SKILL.md` here is a fan-out target
and each proposal is adopted independently. `auto_adopt` is **false** — proposals always wait for
your review.

> **Data boundary.** Harvesting is local and read-only. Any backend other than `mock` sends truncated
> transcript excerpts to that provider for mining, replay, judging and reflection. `redact_secrets`
> is enabled as defense in depth, not as a guarantee. Inspect harvested tasks before running a real
> backend on sensitive projects, and treat the per-night `evidence.jsonl` as sensitive local data.

---

## 5. The datasets

`optimization/datasets/<skill>/{train,val,test}/items.json` — 14 items per skill (6 / 4 / 4),
covering the skill's main task types, its documented failure modes, a non-English trigger, and at
least one **negative-trigger** item where the skill is loaded but must not fire.

```jsonc
{
  "id": "pr-train-02",                 // unique across all splits
  "task_type": "partial-analysis",     // used for stratified sampling
  "prompt": "…the user request…",
  "context": "…repo state the agent can rely on…",
  "rubric": ["…criterion the response must satisfy…"],
  "anti_patterns": ["…behaviour that must not appear…"],
  "gold_notes": "…what a strong answer contains…",
  "should_trigger": true               // false = the skill must stay quiet
}
```

Scoring (`optimization/env/agentskill/judge.py`):

- `soft` = fraction of rubric criteria passed, minus `0.25` per triggered anti-pattern
- `hard` = 1 when `soft >= hard_threshold` (default `0.8`) **and** no anti-pattern triggered

Validate the datasets any time (no SkillOpt install required — this also runs in CI):

```bash
python3 optimization/validate_datasets.py
```

**Adding items.** Keep rubric criteria observable in the response text ("uses `--targetPath`",
not "understands reverse lookup"), keep ids unique, and add a matching negative-trigger item when
you add a new task type. More items make the gate less noisy; the split sizes in the configs
(`train.batch_size`) should match the train split.

---

## 6. Layout

```
optimization/
├── run.py                  # registers the out-of-tree env, delegates to SkillOpt train/eval
├── adopt.py                # run report + gated write-back to <skill>/SKILL.md
├── skillopt_compat.py      # keeps structured `env:` sections alive through SkillOpt config merging
├── selftest.py             # offline end-to-end check with stubbed model calls
├── validate_datasets.py    # stdlib-only dataset schema check (CI)
├── configs/
│   ├── _base_/agentskill.yaml   # shared training knobs, inherits SkillOpt's default.yaml
│   └── <skill>.yaml             # skill_init + split_dir per skill
├── datasets/<skill>/{train,val,test}/items.json
├── env/agentskill/
│   ├── adapter.py          # EnvAdapter: splits, rollouts, reflection prompts, task types
│   ├── dataloader.py       # SplitDataLoader over items.json
│   ├── rollout.py          # skill doc as system prompt -> target model -> judge
│   ├── judge.py            # rubric LLM judge on the optimizer backend
│   └── prompts/            # skill-document-specific reflection prompts
└── sleep/config.json       # template for ~/.skillopt-sleep/config.json
```

SkillOpt resolves environments through a registry hardcoded in its own `scripts/train.py`.
`run.py` imports that module and injects `agentskill` into the registry before delegating,
which keeps the SkillOpt checkout unpatched and updatable.

`run.py` also applies `skillopt_compat.apply_config_patches()`. In SkillOpt's config loader the
flat alias of `env.name` is literally `env`, so the de-duplication helpers delete the whole
structured `env:` section during `_base_` merging — `env.name`, `env.split_dir` and
`env.skill_init` never reach the trainer, which then falls back to its default environment.
The patch preserves the mapping and is idempotent; re-check it after each SkillOpt upgrade and
delete it once upstream fixes the aliasing.

## 7. Tuning knobs

Set in `optimization/configs/_base_/agentskill.yaml` or overridden per run with `--cfg-options`:

| Key | Default | Effect |
|---|---|---|
| `optimizer.learning_rate` | `3` | max edits per step (textual learning rate) |
| `optimizer.lr_scheduler` | `cosine` | edit budget decay across epochs |
| `optimizer.skill_update_mode` | `patch` | bounded edits instead of full rewrites |
| `evaluation.use_gate` | `true` | keep an edit only if held-out validation improves |
| `env.hard_threshold` | `0.8` | rubric pass rate needed for a success |
| `env.exec_timeout` | `300` | seconds per agent-CLI call (exec backends only) |
| `gradient.failure_only` | `false` | also learn from successful rollouts |
| `train.num_epochs` | `4` | passes over the train split |

## References

- SkillOpt: <https://github.com/microsoft/SkillOpt> (MIT)
- Paper: *SkillOpt: Executive strategy for self-evolving agent skills*, arXiv:2605.23904
