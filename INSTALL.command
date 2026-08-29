#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
bash "$SCRIPT_DIR/scripts/install.sh" "$@"
echo
read -r -p "Press Enter to close..." _
