#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
PYTHON_BIN="${PYTHON:-python3}"
WITH_SHUTTERSIFT=0
WITH_EXPORT=0

for arg in "$@"; do
  case "$arg" in
    --with-shuttersift) WITH_SHUTTERSIFT=1 ;;
    --with-onnx-export) WITH_EXPORT=1 ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Usage: $0 [--with-shuttersift] [--with-onnx-export]" >&2
      exit 2
      ;;
  esac
done

"$PYTHON_BIN" -m venv "$SCRIPT_DIR/.venv"
"$SCRIPT_DIR/.venv/bin/python" -m pip install --upgrade pip
"$SCRIPT_DIR/.venv/bin/python" -m pip install -r "$SCRIPT_DIR/requirements.txt"

mkdir -p "$PROJECT_DIR/external"

if [[ "$WITH_SHUTTERSIFT" == "1" && ! -d "$PROJECT_DIR/external/ShutterSift" ]]; then
  git clone --depth 1 https://github.com/host452b/ShutterSift.git "$PROJECT_DIR/external/ShutterSift"
fi

if [[ "$WITH_EXPORT" == "1" ]]; then
  if [[ ! -d "$PROJECT_DIR/external/skin-retouching-onnxruntime" ]]; then
    git clone --depth 1 https://github.com/aoguai/skin-retouching-onnxruntime.git "$PROJECT_DIR/external/skin-retouching-onnxruntime"
  fi
  "$SCRIPT_DIR/.venv/bin/python" -m pip install -r "$SCRIPT_DIR/requirements-onnx.txt"
  FACE_DIR="$PROJECT_DIR/external/skin-retouching-onnxruntime/cv_resnet50_face-detection_retinaface"
  mkdir -p "$FACE_DIR"
  if [[ ! -f "$FACE_DIR/pytorch_model.pt" && -f "$PROJECT_DIR/external/skin-retouching-onnxruntime/retinaface_resnet50_2020-07-20_old_torch.pth" ]]; then
    cp "$PROJECT_DIR/external/skin-retouching-onnxruntime/retinaface_resnet50_2020-07-20_old_torch.pth" "$FACE_DIR/pytorch_model.pt"
  fi
  "$SCRIPT_DIR/.venv/bin/python" -m pip install -r "$PROJECT_DIR/external/skin-retouching-onnxruntime/requirements-export.txt"
  "$SCRIPT_DIR/.venv/bin/python" "$PROJECT_DIR/external/skin-retouching-onnxruntime/export_skin_retouching_onnx.py" \
    --model-dir "$PROJECT_DIR/external/skin-retouching-onnxruntime" \
    --face-model-dir "$FACE_DIR"
fi

if [[ "$WITH_SHUTTERSIFT" == "1" ]]; then
  "$SCRIPT_DIR/.venv/bin/python" -m pip install "$PROJECT_DIR/external/ShutterSift"
  "$SCRIPT_DIR/.venv/bin/python" -c "from shuttersift.cli.main import app; app()" setup || true
fi

echo "Local engine environment is ready at $SCRIPT_DIR/.venv"
