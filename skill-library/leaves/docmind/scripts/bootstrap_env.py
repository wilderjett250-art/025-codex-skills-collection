#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from environment_check import COMMANDS, MODULES, available_module, build_summary


PIP_PACKAGE_BY_MODULE = {
    "pypdf": "pypdf",
    "pdfplumber": "pdfplumber",
    "fitz": "PyMuPDF",
    "openpyxl": "openpyxl",
    "pandas": "pandas",
    "docx": "python-docx",
    "pptx": "python-pptx",
    "PIL": "Pillow",
    "extract_msg": "extract_msg",
    "oletools": "oletools",
}


def evaluate() -> dict[str, object]:
    commands = {name: __import__("shutil").which(name) is not None for name in COMMANDS}
    modules = {name: available_module(name) for name in MODULES}
    payload = build_summary(commands, modules)
    payload["missing_python_packages"] = [
        PIP_PACKAGE_BY_MODULE[name]
        for name, installed in modules.items()
        if not installed and name in PIP_PACKAGE_BY_MODULE
    ]
    return payload


def install_packages(packages: list[str]) -> list[dict[str, object]]:
    results = []
    for package in packages:
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            check=False,
        )
        results.append(
            {
                "package": package,
                "returncode": proc.returncode,
                "stderr_tail": proc.stderr[-500:],
                "stdout_tail": proc.stdout[-500:],
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DocMind bootstrap checks and optional pip installs.")
    parser.add_argument("--install-missing", action="store_true", help="Install missing Python packages with pip.")
    parser.add_argument("--stamp-path", help="Optional JSON file that records the bootstrap result.")
    parser.add_argument("--force", action="store_true", help="Ignore an existing stamp and run again.")
    args = parser.parse_args()

    stamp_path = Path(args.stamp_path).resolve() if args.stamp_path else None
    if stamp_path and stamp_path.exists() and not args.force:
        print(stamp_path)
        return 0

    payload = evaluate()
    install_results = []
    if args.install_missing and payload["missing_python_packages"]:
        install_results = install_packages(payload["missing_python_packages"])
        payload = evaluate()
    payload["install_results"] = install_results

    if stamp_path:
        stamp_path.parent.mkdir(parents=True, exist_ok=True)
        stamp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(stamp_path)
    else:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
