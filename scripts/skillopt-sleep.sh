#!/usr/bin/env bash
# Daily improvement loop: harvest local agent transcripts (Claude Code, Codex,
# GitHub Copilot in VS Code, Copilot CLI, Cursor, Pi, OpenCode), mine recurring
# tasks, replay them, and stage validation-gated edits to the skills in this repo.
#
#   scripts/skillopt-sleep.sh --install-config       # write ~/.skillopt-sleep/config.json
#   scripts/skillopt-sleep.sh harvest                # read transcripts only, stage nothing
#   scripts/skillopt-sleep.sh dry-run                # full cycle, report only
#   scripts/skillopt-sleep.sh run                    # full cycle, proposals staged for review
#   scripts/skillopt-sleep.sh status                 # state + latest staged proposal
#   scripts/skillopt-sleep.sh adopt --skill pr-review
#   scripts/skillopt-sleep.sh nightly                # what the cron job runs (all sources, dry safe)
#   scripts/skillopt-sleep.sh --install-cron         # install the nightly cron entry
#
# Options:
#   --sources "claude codex copilot cursor"   sources to sweep (default: auto-detected)
#   --backend NAME                            replay/optimizer backend (claude, codex, copilot,
#                                             cursor, pi, opencode, azure_openai, handoff, mock)
#   --lookback N                              hours of history to scan (default 24; 0 = all)
#
# Data boundary: harvesting is local and read-only. Any backend other than `mock`
# sends truncated transcript excerpts to that provider. Review harvested tasks
# before running a real backend on sensitive projects.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SLEEP_BIN="$REPO_ROOT/.skillopt/venv/bin/skillopt-sleep"
STATE_DIR="${SKILLOPT_SLEEP_HOME:-$HOME/.skillopt-sleep}"
LOG_DIR="$REPO_ROOT/optimization/outputs/sleep"

BACKEND="${SKILLOPT_SLEEP_BACKEND:-claude}"
LOOKBACK=24
SOURCES=()
ACTION=""
EXTRA=()

detect_sources() {
  local found=()
  [ -d "$HOME/.claude/projects" ] && found+=(claude)
  [ -d "$HOME/.codex" ] && found+=(codex)
  [ -d "$HOME/.cursor" ] && found+=(cursor)
  [ -d "$HOME/Library/Application Support/Code/User/workspaceStorage" ] && found+=(copilot)
  [ -d "$HOME/.config/Code/User/workspaceStorage" ] && found+=(copilot)
  [ -d "$HOME/.pi/agent/sessions" ] && found+=(pi)
  printf '%s\n' "${found[@]+"${found[@]}"}" | awk '!seen[$0]++'
}

install_config() {
  mkdir -p "$STATE_DIR"
  local target="$STATE_DIR/config.json"
  if [ -f "$target" ]; then
    cp "$target" "$target.bak-$(date +%Y%m%d-%H%M%S)"
    echo "Existing config backed up."
  fi
  sed "s#<REPO>#$REPO_ROOT#g" "$REPO_ROOT/optimization/sleep/config.json" \
    | grep -v '"_comment"' > "$target"
  echo "Wrote $target"
  echo "skill_roots points at $REPO_ROOT, so every <skill>/SKILL.md here is a fan-out target."
}

install_cron() {
  local entry="30 3 * * * cd $REPO_ROOT && scripts/skillopt-sleep.sh nightly >> $LOG_DIR/cron.log 2>&1"
  mkdir -p "$LOG_DIR"
  if crontab -l 2>/dev/null | grep -Fq "skillopt-sleep.sh nightly"; then
    echo "Nightly entry already installed:"
    crontab -l | grep "skillopt-sleep.sh nightly"
    return 0
  fi
  (crontab -l 2>/dev/null || true; echo "$entry") | crontab -
  echo "Installed nightly cron entry (03:30 local time):"
  echo "  $entry"
  echo "Remove it later with: crontab -e"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --install-config) install_config; exit 0 ;;
    --install-cron) install_cron; exit 0 ;;
    --sources) read -r -a SOURCES <<< "$2"; shift ;;
    --backend) BACKEND="$2"; shift ;;
    --lookback) LOOKBACK="$2"; shift ;;
    -h|--help) sed -n '2,26p' "$0"; exit 0 ;;
    harvest|dry-run|run|status|adopt|schedule|unschedule|nightly) ACTION="$1" ;;
    *) EXTRA+=("$1") ;;
  esac
  shift
done

if [ ! -x "$SLEEP_BIN" ]; then
  echo "skillopt-sleep not installed. Run scripts/skillopt-bootstrap.sh first." >&2
  exit 1
fi

[ -z "$ACTION" ] && { echo "No action given. Try: dry-run | run | harvest | status | adopt | nightly" >&2; exit 2; }

mkdir -p "$LOG_DIR"
cd "$REPO_ROOT"
set -a; [ -f "$REPO_ROOT/.env" ] && . "$REPO_ROOT/.env"; set +a

# status / adopt are state-level actions: no source sweep.
if [ "$ACTION" = "status" ] || [ "$ACTION" = "adopt" ] || [ "$ACTION" = "schedule" ] || [ "$ACTION" = "unschedule" ]; then
  exec "$SLEEP_BIN" "$ACTION" --project "$REPO_ROOT" ${EXTRA[@]+"${EXTRA[@]}"}
fi

RUN_ACTION="$ACTION"
[ "$ACTION" = "nightly" ] && RUN_ACTION="run"

if [ ${#SOURCES[@]} -eq 0 ]; then
  while IFS= read -r s; do [ -n "$s" ] && SOURCES+=("$s"); done < <(detect_sources)
fi
if [ ${#SOURCES[@]} -eq 0 ]; then
  echo "No local agent transcript directory found. Nothing to harvest." >&2
  exit 0
fi

if [ ! -f "$STATE_DIR/config.json" ]; then
  echo "Warning: $STATE_DIR/config.json is missing, so multi-skill fan-out, the"
  echo "         no-regression gate and the house rules for this repo are not active."
  echo "         Run: scripts/skillopt-sleep.sh --install-config"
  echo
fi

echo "Sources: ${SOURCES[*]}   backend: $BACKEND   lookback: ${LOOKBACK}h"

STAMP="$(date +%Y%m%d-%H%M%S)"
STATUS=0
for source in "${SOURCES[@]}"; do
  log="$LOG_DIR/$STAMP-$source-$RUN_ACTION.log"
  echo
  echo "==> $RUN_ACTION from $source (log: $log)"
  if ! "$SLEEP_BIN" "$RUN_ACTION" \
      --project "$REPO_ROOT" \
      --source "$source" \
      --backend "$BACKEND" \
      --lookback-hours "$LOOKBACK" \
      --skill-root "$REPO_ROOT" \
      --progress \
      ${EXTRA[@]+"${EXTRA[@]}"} 2>&1 | tee "$log"; then
    echo "!! sleep cycle failed for source $source" >&2
    STATUS=1
  fi
done

echo
echo "Done. Review staged proposals with:"
echo "  scripts/skillopt-sleep.sh status"
echo "  scripts/skillopt-sleep.sh adopt --skill <name>     # or --all-skills"
exit "$STATUS"
