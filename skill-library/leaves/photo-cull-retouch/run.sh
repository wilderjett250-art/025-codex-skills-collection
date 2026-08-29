#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_PY="$SCRIPT_DIR/.venv/bin/python"

if [[ -x "${CODEX_PHOTO_PYTHON:-}" ]]; then
  PYTHON="${CODEX_PHOTO_PYTHON}"
elif [[ -x "$LOCAL_PY" ]]; then
  PYTHON="$LOCAL_PY"
else
  PYTHON="${PYTHON:-python3}"
fi

"$PYTHON" "$SCRIPT_DIR/scripts/photo_cull_retouch.py" "$@"
