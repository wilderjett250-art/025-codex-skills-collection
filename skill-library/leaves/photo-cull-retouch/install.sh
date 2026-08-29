#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="photo-cull-retouch"
SKILLS_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
TARGET="$SKILLS_DIR/$SKILL_NAME"
PYTHON_BIN="${PYTHON:-python3}"

INSTALL_OPTIONAL=0
FORCE=0

for arg in "$@"; do
  case "$arg" in
    --with-optional-engines) INSTALL_OPTIONAL=1 ;;
    --force) FORCE=1 ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Usage: $0 [--with-optional-engines] [--force]" >&2
      exit 2
      ;;
  esac
done

mkdir -p "$SKILLS_DIR"

if [[ -e "$TARGET" || -L "$TARGET" ]]; then
  if [[ "$FORCE" != "1" ]]; then
    echo "Skill already exists at $TARGET"
    echo "Re-run with --force to replace it."
    exit 1
  fi
  rm -rf "$TARGET"
fi

"$PYTHON_BIN" -m venv "$SCRIPT_DIR/.venv"
"$SCRIPT_DIR/.venv/bin/python" -m pip install --upgrade pip
"$SCRIPT_DIR/.venv/bin/python" -m pip install -r "$SCRIPT_DIR/requirements.txt"

ln -s "$SCRIPT_DIR" "$TARGET"

if [[ "$INSTALL_OPTIONAL" == "1" ]]; then
  "$SCRIPT_DIR/setup_local_engines.sh" --with-shuttersift
fi

echo "Installed $SKILL_NAME at $TARGET"
echo "Run: $SCRIPT_DIR/run.sh /path/to/image-folder"
