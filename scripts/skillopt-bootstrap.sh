#!/usr/bin/env bash
# Install the SkillOpt toolchain used to optimize the skills in this repo.
#
#   scripts/skillopt-bootstrap.sh              # install / update
#   SKILLOPT_REF=v0.2.0 scripts/skillopt-bootstrap.sh
#
# Everything lands under .skillopt/ (git-ignored):
#   .skillopt/SkillOpt   pinned source checkout of microsoft/SkillOpt
#   .skillopt/venv       virtualenv with skillopt + its dependencies
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLOPT_DIR="$REPO_ROOT/.skillopt"
SRC_DIR="$SKILLOPT_DIR/SkillOpt"
VENV_DIR="$SKILLOPT_DIR/venv"
SKILLOPT_REPO="${SKILLOPT_REPO:-https://github.com/microsoft/SkillOpt.git}"
SKILLOPT_REF="${SKILLOPT_REF:-main}"   # main carries the Sleep features we use
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "$SKILLOPT_DIR"

if [ -d "$SRC_DIR/.git" ]; then
  echo "==> Updating SkillOpt checkout ($SKILLOPT_REF)"
  git -C "$SRC_DIR" fetch --depth 1 origin "$SKILLOPT_REF"
  git -C "$SRC_DIR" checkout --detach FETCH_HEAD
else
  echo "==> Cloning SkillOpt ($SKILLOPT_REF)"
  git clone --depth 1 --branch "$SKILLOPT_REF" "$SKILLOPT_REPO" "$SRC_DIR" 2>/dev/null \
    || git clone --depth 1 "$SKILLOPT_REPO" "$SRC_DIR"
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating virtualenv at $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "==> Installing SkillOpt into the virtualenv"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -e "$SRC_DIR"

if [ ! -f "$REPO_ROOT/.env" ] && [ -f "$SRC_DIR/.env.example" ]; then
  cp "$SRC_DIR/.env.example" "$REPO_ROOT/.env"
  echo "==> Wrote .env from SkillOpt's .env.example — fill in your provider credentials"
fi

echo
echo "SkillOpt ready."
echo "  source:  $SRC_DIR ($(git -C "$SRC_DIR" rev-parse --short HEAD))"
echo "  venv:    $VENV_DIR"
echo
echo "Next:"
echo "  scripts/skillopt-optimize.sh --list"
echo "  scripts/skillopt-optimize.sh pr-review --dry-run"
