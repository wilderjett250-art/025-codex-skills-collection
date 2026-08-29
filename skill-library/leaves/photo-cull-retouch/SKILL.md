---
name: photo-cull-retouch
description: Select the best photos from an input folder, prepare Codex imagegen portrait-retouch tasks, and finalize edited outputs.
---

# Photo Cull Retouch

Use this skill when the user wants to process a folder of photos, select the strongest candidates, and produce final retouched outputs.

Default route: use local scoring/culling, then use CosKit workflow concepts with Codex imagegen for the actual image edit. Do not call CosKit's Gemini/OpenAI image APIs in this skill.

This skill is portable. Resolve all commands relative to the directory containing this `SKILL.md`; do not use machine-specific absolute paths.

## Input

- A local image folder path.
- Supported files: `.jpg`, `.jpeg`, `.png`, `.webp`, `.tif`, `.tiff`, `.bmp`.

## Output Contract

Given an input folder:

```text
/path/to/parent/input-folder
```

The skill writes:

```text
/path/to/parent/output/
```

The output folder contains:

- `edited/`: selected and retouched final JPG images. In Codex imagegen mode, this is filled after imagegen returns final images.
- `selected_originals/`: copies of the selected source images.
- `score_report.csv`: all source images with component scores.
- `manifest.json`: machine-readable run metadata and selected files.
- `contact_sheet.jpg`: visual overview of selected outputs when possible.
- `imagegen_tasks.json` and `imagegen_instructions.md`: Codex imagegen tasks when using the default route.

If `output/` already exists, create a timestamped run folder inside it unless the user explicitly requests overwrite.

## Standard Workflow

1. Verify the input folder exists and contains supported images.
2. Install local Python dependencies if this has not been done yet:

```bash
./install.sh
```

Use heavier optional setup only when needed:

```bash
./setup_local_engines.sh --with-shuttersift --with-onnx-export
```

3. Run the selector and task generator:

```bash
./run.sh "/path/to/input-folder"
```

4. Inspect `imagegen_tasks.json` and invoke Codex imagegen for each selected image.
5. If imagegen returns a local file path, finalize the generated images into `edited/`:

```bash
./scripts/finalize_imagegen_outputs.py "/path/to/output" "~/.codex/generated_images/.../generated-1.png"
```

Pass generated image paths in the same order as `imagegen_tasks.json`.

6. Report the generated output path and how many photos were scanned, selected, and finalized.

## Selection Standard

Score each photo on a 100-point rubric:

- Technical quality, 35 points: sharpness, exposure, contrast, noise penalty.
- Portrait quality, 25 points: face/skin-region signal, subject centrality, eye/face-likelihood heuristics.
- Composition, 20 points: subject placement, border safety, usable crop, background simplicity.
- Color and mood, 15 points: saturation, warmth balance, color harmony.
- Retouch potential, 5 points: recoverable image with no severe technical failure.

The default selection keeps the strongest 20% of images, with a minimum of 1 and a maximum of 30. The user can override this with `--keep-count`, `--keep-ratio`, or `--min-score`.

## Retouching Standard

The default retouching is visible but identity-preserving, using Codex imagegen with a CosKit-inspired portrait workflow:

- Tone adjustment: control blown highlights, lift face shadows, keep depth.
- Color style: clean white balance, airy sky/background, tasteful flower/grass vibrance.
- Detail enhancement: clearer eyes, natural hair/cloth edges, no hard halos.
- Skin smoothing: reduce blemishes, pores, and dullness while keeping real texture.
- Skin whitening: translucent, natural skin brightening, not dead-white.
- Face adjustment: only subtle vitality/complexion improvements; preserve identity.

Local `baseline` and `onnx-skin` engines remain available for fully local tests, but they are not the preferred beauty-retouch route.

## Examples

```bash
./run.sh "/path/to/raw-shoot"
```

```bash
./run.sh "/path/to/raw-shoot" --keep-count 12 --imagegen-style clean
```

```bash
./run.sh "/path/to/raw-shoot" --keep-ratio 0.1 --min-score 62 --output-name output
```

## Notes

- This skill works offline with Pillow and NumPy. OpenCV is optional but improves sharpness scoring, face detection, and skin smoothing.
- Use `run.sh` for normal execution. It prefers the local `.venv` created by `install.sh`, then falls back to `python3`.
- The current recommended implementation is baseline culling plus Codex imagegen retouching. ShutterSift-lite is an optional enhanced culling engine.
- Codex imagegen is a conversation capability, not a local Python API. The script creates tasks; the Codex agent performs image editing and then can finalize local files.
- The skill supports external local engines:
  - `--cull-engine shuttersift` uses vendored ShutterSift scoring formulas in fast lite mode by default.
  - `--shuttersift-mode cli` uses the full vendored ShutterSift CLI and its `results.json` scores. This can be much slower because it initializes pyiqa/MUSIQ and MediaPipe.
  - `--retouch-engine codex-imagegen` creates CosKit-inspired imagegen tasks and is the default.
  - `--retouch-engine onnx-skin` uses the vendored `skin-retouching-onnxruntime` pipeline for local-only tests.
  - `--retouch-engine baseline` uses deterministic local Pillow/OpenCV edits for local-only tests.
- The ONNX skin retoucher needs `model.onnx`, `retouch_generator.onnx`, and `face_detector.onnx` in the skin model directory. Local blemish removal also needs `local_detection.onnx` and `local_inpainting.onnx`.

## Current Recommended Command

Use the default local culling route and Codex imagegen retouching route:

```bash
./run.sh "/path/to/input-folder" --imagegen-style beauty
```

After optional ShutterSift setup, enhanced culling can be requested:

```bash
./run.sh "/path/to/input-folder" --cull-engine shuttersift --imagegen-style beauty
```

## CosKit + Codex Imagegen Workflow

Use this for normal high-quality portrait output, and especially when the user says image creation or image reading must use Codex imagegen.

1. Run the local selector to create `output/selected_originals/`, `imagegen_tasks.json`, and reports:

```bash
./run.sh "/path/to/input-folder" --imagegen-style beauty
```

2. Read `output/imagegen_tasks.json` or `output/imagegen_instructions.md`.
3. For each task, inspect the selected image in the conversation and invoke Codex imagegen with the CosKit-inspired prompt.
4. Save or place each generated result into `output/edited/` if the environment exposes a generated file path. Generated images are normally under `~/.codex/generated_images/`.
5. If needed, run:

```bash
./scripts/finalize_imagegen_outputs.py "/path/to/output" "~/.codex/generated_images/.../image-1.png"
```

If imagegen only returns the image in chat, return it to the user and state that the local file was not automatically written.

Do not use CosKit's own image API in this mode. Use CosKit's workflow/prompt concepts and Codex imagegen for the actual image creation.
