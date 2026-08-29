#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path


COMMANDS = [
    "file",
    "pdfinfo",
    "pdftotext",
    "pdffonts",
    "tesseract",
    "libreoffice",
    "soffice",
    "unzip",
    "7z",
    "tar",
    "mutool",
]

MODULES = [
    "pypdf",
    "pdfplumber",
    "fitz",
    "openpyxl",
    "pandas",
    "docx",
    "pptx",
    "PIL",
    "extract_msg",
    "oletools",
    "py7zr",
]


def available_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def build_summary(commands: dict[str, bool], modules: dict[str, bool]) -> dict[str, object]:
    capabilities = {
        "pdf_native_extraction": commands["pdfinfo"] and modules["fitz"] and modules["pdfplumber"],
        "ocr_images": commands["tesseract"] and modules["PIL"],
        "office_openxml": modules["openpyxl"] and modules["docx"] and modules["pptx"],
        "email_msg": modules["extract_msg"],
        "archive_7z_rar": commands["7z"] or modules["py7zr"],
        "legacy_office_conversion": commands["libreoffice"] or commands["soffice"],
    }

    missing_install_candidates = []
    if not capabilities["legacy_office_conversion"]:
        missing_install_candidates.append(
            "Install LibreOffice if the bundle contains legacy .doc, .xls, or .ppt files."
        )
    if not capabilities["ocr_images"]:
        missing_install_candidates.append(
            "Install tesseract and Pillow support if image-heavy or scanned documents must be read."
        )
    if not capabilities["archive_7z_rar"]:
        missing_install_candidates.append(
            "Install 7z support if .7z or .rar archives must be unpacked."
        )

    return {
        "commands": commands,
        "modules": modules,
        "capabilities": capabilities,
        "approval_recommendations": missing_install_candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect the local environment for DocMind workflows.")
    parser.add_argument("--json-out", help="Optional path to write the result JSON.")
    args = parser.parse_args()

    commands = {name: shutil.which(name) is not None for name in COMMANDS}
    modules = {name: available_module(name) for name in MODULES}
    payload = build_summary(commands, modules)

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
