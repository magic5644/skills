#!/usr/bin/env bash
# Score a skill document against its dataset without optimizing it.
#
#   scripts/skillopt-eval.sh pr-review                       # current SKILL.md, all splits
#   scripts/skillopt-eval.sh pr-review --split valid_unseen  # held-out test split only
#   scripts/skillopt-eval.sh pr-review --skill optimization/outputs/pr-review/<stamp>/best_skill.md
#   scripts/skillopt-eval.sh --all --split valid_unseen      # baseline every skill
#
#   scripts/skillopt-eval.sh pr-review --preset claude-code --model sonnet
#
# Splits: train | valid_seen (val) | valid_unseen (test) | all (default)
# Presets: copilot | claude-code | claude-code-copilot | codex (see skillopt-optimize.sh)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PY="$REPO_ROOT/.skillopt/venv/bin/python"
CONFIG_DIR="$REPO_ROOT/optimization/configs"
OUT_ROOT="$REPO_ROOT/optimization/outputs"

SKILLS=()
SKILL_FILE=""
SPLIT="all"
PASSTHROUGH=()
CFG_OPTS=()

list_skills() {
  find "$CONFIG_DIR" -maxdepth 1 -name '*.yaml' -exec basename {} .yaml \; | sort
}

while [ $# -gt 0 ]; do
  case "$1" in
    --all) while IFS= read -r s; do SKILLS+=("$s"); done < <(list_skills) ;;
    --skill) SKILL_FILE="$2"; shift ;;
    --split) SPLIT="$2"; shift ;;
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
    --) shift; PASSTHROUGH=("$@"); break ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; exit 2 ;;
    *) SKILLS+=("$1") ;;
  esac
  shift
done

[ -x "$VENV_PY" ] || { echo "Run scripts/skillopt-bootstrap.sh first." >&2; exit 1; }
[ ${#SKILLS[@]} -gt 0 ] || { echo "Name a skill or use --all:" >&2; list_skills >&2; exit 2; }
if [ -n "$SKILL_FILE" ] && [ ${#SKILLS[@]} -gt 1 ]; then
  echo "--skill applies to a single skill only." >&2
  exit 2
fi

cd "$REPO_ROOT"
set -a; [ -f "$REPO_ROOT/.env" ] && . "$REPO_ROOT/.env"; set +a

STAMP="$(date +%Y%m%d-%H%M%S)"
for skill in "${SKILLS[@]}"; do
  config="$CONFIG_DIR/$skill.yaml"
  [ -f "$config" ] || { echo "No config for '$skill'" >&2; exit 1; }
  doc="${SKILL_FILE:-$REPO_ROOT/$skill/SKILL.md}"
  run_dir="$OUT_ROOT/$skill/eval-$STAMP"
  mkdir -p "$run_dir"

  echo
  echo "==> Evaluating $skill ($SPLIT) from $doc"
  cmd=("$VENV_PY" optimization/run.py eval
       --config "$config" --skill "$doc" --split "$SPLIT" --out_root "$run_dir")
  if [ ${#CFG_OPTS[@]} -gt 0 ]; then
    cmd+=(--cfg-options "${CFG_OPTS[@]}")
  fi
  cmd+=("${PASSTHROUGH[@]+"${PASSTHROUGH[@]}"}")
  "${cmd[@]}"
done
