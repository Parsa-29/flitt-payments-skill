#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="flitt-payments"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

install_to() {
  local dest
  dest="$(mkdir -p "$1" && cd "$1" && pwd)"
  local files=("${@:2}")

  # Skip if we would be installing into our own source directory
  if [[ "$dest" == "$SCRIPT_DIR" ]]; then
    echo "  -> $dest (already in place, skipping)"
    return
  fi

  if [[ -d "$dest" ]]; then
    echo "Existing installation found at $dest — updating."
    rm -rf "$dest"
  fi
  mkdir -p "$dest"
  for f in "${files[@]}"; do
    [[ -e "$SCRIPT_DIR/$f" ]] && cp -r "$SCRIPT_DIR/$f" "$dest/"
  done
  echo "  -> $dest"
}

echo "Installing $SKILL_NAME skill..."

install_to "$HOME/.claude/skills/$SKILL_NAME" SKILL.md references scripts
install_to "$HOME/.cursor/skills/$SKILL_NAME" SKILL.md references scripts
install_to "$HOME/.codex/skills/$SKILL_NAME"  SKILL.md references scripts agents

echo "Done. Restart Claude Code / Cursor / Codex to activate."
