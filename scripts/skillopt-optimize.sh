#!/usr/bin/env bash
# Optimize one or every skill document in this repository with SkillOpt.
#
#   scripts/skillopt-optimize.sh --list
#   scripts/skillopt-optimize.sh pr-review
#   scripts/skillopt-optimize.sh pr-review graph-it-live --adopt
#   scripts/skillopt-optimize.sh --all --epochs 2
#   scripts/skillopt-optimize.sh pr-review --dry-run          # 2 items, 1 epoch, cheap smoke run
#   scripts/skillopt-optimize.sh --all -- --cfg-options optimizer.learning_rate=2
#
# Options:
#   --all                 optimize every skill that has a config
#   --list                list optimizable skills and exit
#   --adopt               overwrite <skill>/SKILL.md when the held-out test score improves
#   --dry-run             tiny run (1 epoch, 2 items/split) to validate wiring and credentials
#   --preset NAME         run through an installed agent CLI instead of a raw API:
#                           copilot      GitHub Copilot CLI for both roles (no API key)
#                           claude-code  Claude Code CLI as the target agent
#                                        (+ ANTHROPIC_API_KEY for the optimizer role)
#                           claude-code-copilot  Claude Code CLI target, Copilot CLI optimizer
#                           codex        Codex CLI for both roles (no API key)
#   --model NAME          model passed to the agent CLI of the preset
#   --epochs N            override train.num_epochs
#   --backend NAME        set both optimizer and target backend (openai_chat, claude_chat,
#                         qwen_chat, minimax_chat, copilot_chat, openai_compatible, ...)
#   --target-backend NAME / --optimizer-backend NAME
#   --target MODEL / --optimizer MODEL
#   --out DIR             output root (default optimization/outputs)
#   --                    everything after this is passed straight to SkillOpt
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PY="$REPO_ROOT/.skillopt/venv/bin/python"
CONFIG_DIR="$REPO_ROOT/optimization/configs"
OUT_ROOT="$REPO_ROOT/optimization/outputs"

SKILLS=()
ADOPT=0
DRY_RUN=0
CFG_OPTS=()
PASSTHROUGH=()

list_skills() {
  find "$CONFIG_DIR" -maxdepth 1 -name '*.yaml' -exec basename {} .yaml \; | sort
}

while [ $# -gt 0 ]; do
  case "$1" in
    --list) list_skills; exit 0 ;;
    --all) while IFS= read -r s; do SKILLS+=("$s"); done < <(list_skills) ;;
    --adopt) ADOPT=1 ;;
    --dry-run) DRY_RUN=1 ;;
    --preset)
      case "$2" in
        copilot)
          CFG_OPTS+=("model.optimizer_backend=copilot_chat" "model.target_backend=copilot_exec" "env.workers=2") ;;
        claude-code)
          CFG_OPTS+=("model.optimizer_backend=claude_chat" "model.target_backend=claude_code_exec" "env.workers=2") ;;
        claude-code-copilot)
          CFG_OPTS+=("model.optimizer_backend=copilot_chat" "model.target_backend=claude_code_exec" "env.workers=2") ;;
        codex)
          CFG_OPTS+=("model.optimizer_backend=codex_exec" "model.target_backend=codex_exec" "env.workers=2") ;;
        *) echo "Unknown preset: $2 (copilot | claude-code | claude-code-copilot | codex)" >&2; exit 2 ;;
      esac
      shift ;;
    --model) CFG_OPTS+=("model.target=$2"); shift ;;
    --epochs) CFG_OPTS+=("train.num_epochs=$2"); shift ;;
    --backend) CFG_OPTS+=("model.optimizer_backend=$2" "model.target_backend=$2"); shift ;;
    --target-backend) CFG_OPTS+=("model.target_backend=$2"); shift ;;
    --optimizer-backend) CFG_OPTS+=("model.optimizer_backend=$2"); shift ;;
    --target) CFG_OPTS+=("model.target=$2"); shift ;;
    --optimizer) CFG_OPTS+=("model.optimizer=$2"); shift ;;
    --out) OUT_ROOT="$2"; shift ;;
    --) shift; PASSTHROUGH=("$@"); break ;;
    -h|--help) sed -n '2,25p' "$0"; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; exit 2 ;;
    *) SKILLS+=("$1") ;;
  esac
  shift
done

if [ ! -x "$VENV_PY" ]; then
  echo "SkillOpt is not installed. Run scripts/skillopt-bootstrap.sh first." >&2
  exit 1
fi

if [ ${#SKILLS[@]} -eq 0 ]; then
  echo "No skill selected. Use --all, or name one or more of:" >&2
  list_skills >&2
  exit 2
fi

if [ "$DRY_RUN" -eq 1 ]; then
  CFG_OPTS+=("train.num_epochs=1" "env.limit=2" "evaluation.eval_test=true")
fi

# SkillOpt resolves relative paths (skill_init, split_dir) against the cwd.
cd "$REPO_ROOT"
set -a; [ -f "$REPO_ROOT/.env" ] && . "$REPO_ROOT/.env"; set +a

STAMP="$(date +%Y%m%d-%H%M%S)"
FAILED=()

for skill in "${SKILLS[@]}"; do
  config="$CONFIG_DIR/$skill.yaml"
  if [ ! -f "$config" ]; then
    echo "No config for skill '$skill' ($config)" >&2
    FAILED+=("$skill")
    continue
  fi

  run_dir="$OUT_ROOT/$skill/$STAMP"
  mkdir -p "$run_dir"
  echo
  echo "=============================================================="
  echo "  Optimizing $skill  ->  $run_dir"
  echo "=============================================================="

  cmd=("$VENV_PY" optimization/run.py train --config "$config" --out_root "$run_dir")
  if [ ${#CFG_OPTS[@]} -gt 0 ]; then
    cmd+=(--cfg-options "${CFG_OPTS[@]}")
  fi
  cmd+=("${PASSTHROUGH[@]+"${PASSTHROUGH[@]}"}")

  if ! "${cmd[@]}"; then
    echo "!! Optimization failed for $skill" >&2
    FAILED+=("$skill")
    continue
  fi

  "$VENV_PY" optimization/adopt.py \
    --skill "$skill" \
    --run-dir "$run_dir" \
    $([ "$ADOPT" -eq 1 ] && echo --apply || echo --report-only)
done

echo
if [ ${#FAILED[@]} -gt 0 ]; then
  echo "Failed: ${FAILED[*]}" >&2
  exit 1
fi
echo "All runs completed. Reports under $OUT_ROOT"
