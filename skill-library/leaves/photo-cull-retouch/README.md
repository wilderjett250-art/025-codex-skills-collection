# photo-cull-retouch

Select the best photos from a folder, prepare a clear score report, and create
CosKit-inspired Codex imagegen tasks for high-quality portrait retouching.

The default workflow is designed for Codex users:

1. The local script scans and scores the input folder.
2. It copies selected originals into `output/selected_originals/`.
3. It writes `imagegen_tasks.json` and `imagegen_instructions.md`.
4. A Codex agent uses Codex imagegen to create the final retouched images.
5. Generated files can be finalized into `output/edited/`.

CosKit is used only as a workflow and prompt reference. This project does not
call CosKit's Gemini/OpenAI image APIs.

## Requirements

- macOS or Linux
- Python 3.10+
- Codex, if you want the default `codex-imagegen` retouching route
- Git, only if you install optional external engines

## Install For Codex

```bash
git clone <repo-url>
cd photo-cull-retouch
./install.sh
```

This creates a local `.venv`, installs the minimal Python dependencies, and
links the skill into:

```text
~/.codex/skills/photo-cull-retouch
```

If a previous skill already exists:

```bash
./install.sh --force
```

Optional ShutterSift setup:

```bash
./install.sh --with-optional-engines --force
```

## Quick Start

```bash
./run.sh "/path/to/image-folder"
```

The default command uses the built-in baseline culling engine, so it works
without downloading external repos. After optional ShutterSift setup, use:

```bash
./run.sh "/path/to/image-folder" --cull-engine shuttersift
```

The output folder is created next to the input folder:

```text
/path/to/output/
```

It contains:

- `selected_originals/`
- `edited/`
- `score_report.csv`
- `manifest.json`
- `contact_sheet.jpg`
- `imagegen_tasks.json`
- `imagegen_instructions.md`

## Use In Codex

After running `./install.sh`, ask Codex:

```text
使用 photo-cull-retouch 处理这个图片文件夹：/path/to/image-folder
```

Codex should:

1. Run `./run.sh`.
2. Read `imagegen_tasks.json`.
3. Call Codex imagegen for every selected source image.
4. Put final files into `output/edited/` when a generated file path is available.

Codex-generated images are usually saved under:

```text
~/.codex/generated_images/
```

Finalize generated files into `edited/`:

```bash
./scripts/finalize_imagegen_outputs.py "/path/to/output" "~/.codex/generated_images/.../image-1.png"
```

Pass generated image paths in the same order as `imagegen_tasks.json`.

## Local-Only Mode

If you do not have Codex imagegen, you can still use local-only output:

```bash
./run.sh "/path/to/image-folder" --retouch-engine baseline
```

This produces deterministic local edits, but the result is weaker than Codex
imagegen portrait retouching.

## Optional Engines

The default command works without optional engines. Optional integrations are:

- ShutterSift lite culling: `./setup_local_engines.sh --with-shuttersift`
- ONNX skin retouch export: `./setup_local_engines.sh --with-onnx-export`

ONNX skin retouching is kept for local tests and is not the recommended beauty
route.

## Health Check

```bash
./doctor.sh
```

## Important Limitation

Codex imagegen is not a Python package and cannot be called directly from
`photo_cull_retouch.py`. The local script creates tasks; the Codex conversation
performs the final image generation.
