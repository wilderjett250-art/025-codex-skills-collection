#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


KIND_BY_EXTENSION = {
    ".pdf": "pdf",
    ".ppt": "legacy-ppt",
    ".pptx": "pptx",
    ".xls": "legacy-xls",
    ".xlsx": "xlsx",
    ".doc": "legacy-doc",
    ".docx": "docx",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".tif": "image",
    ".tiff": "image",
    ".bmp": "image",
    ".webp": "image",
    ".zip": "archive",
    ".7z": "archive",
    ".rar": "archive",
    ".tar": "archive",
    ".gz": "archive",
    ".tgz": "archive",
    ".eml": "email",
    ".msg": "email",
}


def detect_kind(path: Path) -> str:
    suffixes = [s.lower() for s in path.suffixes]
    if path.name.lower().endswith(".tar.gz") or path.name.lower().endswith(".tar.bz2"):
        return "archive"
    return KIND_BY_EXTENSION.get(path.suffix.lower(), "other")


def route_for_kind(kind: str) -> str:
    return {
        "pdf": "native-text-plus-ocr",
        "pptx": "office-text-notes-media",
        "xlsx": "office-cells-comments-hidden-media",
        "docx": "office-text-comments-revisions-media",
        "image": "ocr",
        "archive": "unpack-then-recurse",
        "email": "expand-attachments-then-recurse",
        "legacy-ppt": "needs-conversion-or-install-approval",
        "legacy-xls": "needs-conversion-or-install-approval",
        "legacy-doc": "needs-conversion-or-install-approval",
        "other": "manual-review",
    }[kind]


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for dirpath, _, filenames in os.walk(root):
        for filename in sorted(filenames):
            yield Path(dirpath) / filename


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a file inventory for a document bundle.")
    parser.add_argument("input_path", help="File or directory to inventory.")
    parser.add_argument("--out", default="./_analysis", help="Directory for inventory outputs.")
    args = parser.parse_args()

    input_path = Path(args.input_path).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for path in iter_files(input_path):
        kind = detect_kind(path)
        files.append(
            {
                "path": str(path),
                "relative_path": str(path.relative_to(input_path)) if input_path.is_dir() else path.name,
                "kind": kind,
                "route": route_for_kind(kind),
                "size_bytes": path.stat().st_size,
            }
        )

    inventory = {
        "root": str(input_path),
        "file_count": len(files),
        "files": files,
    }

    (out_dir / "inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = ["# Inventory", "", f"- Root: `{input_path}`", f"- Files: `{len(files)}`", ""]
    for entry in files:
        lines.append(
            f"- `{entry['relative_path']}` | `{entry['kind']}` | `{entry['route']}` | `{entry['size_bytes']}` bytes"
        )
    (out_dir / "inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out_dir / "inventory.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
