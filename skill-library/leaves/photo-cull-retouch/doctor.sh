#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_TARGET="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}/photo-cull-retouch"

if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
  PYTHON="$SCRIPT_DIR/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

echo "photo-cull-retouch doctor"
echo "skill dir: $SCRIPT_DIR"
echo "python: $PYTHON"

"$PYTHON" - <<'PY'
import importlib.util
import sys

required = ["numpy", "PIL", "cv2"]
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    print("missing packages:", ", ".join(missing))
    sys.exit(1)
print("python packages: ok")
PY

if [[ -e "$SKILL_TARGET" || -L "$SKILL_TARGET" ]]; then
  echo "codex skill link: ok ($SKILL_TARGET)"
else
  echo "codex skill link: missing ($SKILL_TARGET)"
fi

if [[ -d "$SCRIPT_DIR/external/ShutterSift" ]]; then
  echo "optional ShutterSift: installed"
else
  echo "optional ShutterSift: not installed, baseline culling fallback is available"
fi

if [[ -d "$SCRIPT_DIR/external/skin-retouching-onnxruntime" ]]; then
  echo "optional ONNX skin retouch: repository present"
else
  echo "optional ONNX skin retouch: not installed, Codex imagegen is the recommended retouch route"
fi

echo "Codex generated images folder: $HOME/.codex/generated_images"
echo "doctor: done"
