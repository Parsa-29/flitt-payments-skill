#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="flitt-payments"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILES=("SKILL.md" "references" "scripts")

install_to() {
  local dest="$1"
  if [[ -d "$dest" ]]; then
    echo "Existing installation found at $dest — updating."
    rm -rf "$dest"
  fi
  mkdir -p "$dest"
  for f in "${FILES[@]}"; do
    cp -r "$SCRIPT_DIR/$f" "$dest/"
  done
  echo "  -> $dest"
}

echo "Installing $SKILL_NAME skill..."

install_to "$HOME/.claude/skills/$SKILL_NAME"
install_to "$HOME/.cursor/skills/$SKILL_NAME"

echo "Done. Restart Claude Code / Cursor to activate."
