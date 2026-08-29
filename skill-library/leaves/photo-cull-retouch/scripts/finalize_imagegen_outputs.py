#!/usr/bin/env python3
"""Copy Codex imagegen results into a photo-cull-retouch output folder."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Finalize Codex imagegen images by placing them into output/edited/ according to imagegen_tasks.json."
    )
    parser.add_argument("output_folder", type=Path, help="Folder containing imagegen_tasks.json and edited/.")
    parser.add_argument("generated_images", type=Path, nargs="+", help="Generated image files, in the same order as the tasks.")
    parser.add_argument("--quality", type=int, default=94, help="JPEG quality for finalized edited outputs.")
    return parser.parse_args()


def load_tasks(output_folder: Path) -> list[dict[str, object]]:
    tasks_file = output_folder / "imagegen_tasks.json"
    if not tasks_file.exists():
        raise FileNotFoundError(f"Missing imagegen task file: {tasks_file}")
    data = json.loads(tasks_file.read_text(encoding="utf-8"))
    tasks = data.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        raise ValueError(f"No tasks found in: {tasks_file}")
    return tasks


def load_rgb(path: Path) -> Image.Image:
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def save_as_jpeg(source: Path, target: Path, quality: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    image = load_rgb(source)
    image.save(target, quality=quality, optimize=True)


def make_contact_sheet(images: list[Path], output_path: Path) -> None:
    thumbs: list[Image.Image] = []
    for path in images[:30]:
        image = load_rgb(path)
        image.thumbnail((360, 360), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (360, 360), "white")
        canvas.paste(image, ((360 - image.width) // 2, (360 - image.height) // 2))
        thumbs.append(canvas)
    if not thumbs:
        return
    cols = min(5, len(thumbs))
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 360, rows * 360), "white")
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % cols) * 360, (index // cols) * 360))
    sheet.save(output_path, quality=90)


def update_manifest(output_folder: Path, copied: list[dict[str, str]]) -> None:
    manifest_file = output_folder / "manifest.json"
    if not manifest_file.exists():
        return
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest["imagegen_finalized_at"] = datetime.now().isoformat(timespec="seconds")
    manifest["imagegen_finalized_files"] = copied
    manifest["retouch_warnings"] = [
        warning
        for warning in manifest.get("retouch_warnings", [])
        if "Codex imagegen must create the final image" not in str(warning)
    ]
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_folder = args.output_folder.expanduser().resolve()
    tasks = load_tasks(output_folder)
    generated = [path.expanduser().resolve() for path in args.generated_images]
    if len(generated) != len(tasks):
        raise ValueError(f"Expected {len(tasks)} generated images, got {len(generated)}.")

    copied: list[dict[str, str]] = []
    edited_paths: list[Path] = []
    for task, source in zip(tasks, generated, strict=True):
        if not source.exists():
            raise FileNotFoundError(f"Generated image does not exist: {source}")
        target = Path(str(task["expected_output"])).expanduser().resolve()
        save_as_jpeg(source, target, args.quality)
        edited_paths.append(target)
        copied.append({"generated_image": str(source), "edited_output": str(target)})

    make_contact_sheet(edited_paths, output_folder / "contact_sheet.jpg")
    update_manifest(output_folder, copied)
    print(json.dumps({"output_folder": str(output_folder), "finalized": len(copied)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
