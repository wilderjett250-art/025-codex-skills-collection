#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble a clean markdown report from DocMind artifacts.")
    parser.add_argument("--analysis", default="./_analysis", help="Analysis directory")
    parser.add_argument("--memory", default="./_external_memory", help="Memory directory")
    parser.add_argument("--out", default="./_external_memory/report.md", help="Report output path")
    parser.add_argument("--title", default="Document Review Report", help="Report title")
    args = parser.parse_args()

    analysis_dir = Path(args.analysis).resolve()
    memory_dir = Path(args.memory).resolve()
    out_path = Path(args.out).resolve()

    manifest = load_json(analysis_dir / "manifest.json")
    resume_state_path = memory_dir / "resume_state.json"
    if resume_state_path.exists():
        resume_state = load_json(resume_state_path)
    else:
        resume_state = {"documents": []}

    lines = [
        f"# {args.title}",
        "",
        "## Scope",
        "",
        f"- Root input: `{manifest['root']}`",
        f"- Documents processed: `{len(manifest['documents'])}`",
        "",
        "## Coverage Proof",
        "",
    ]
    for entry in manifest["documents"]:
        kind = entry.get("kind", "unknown")
        source = entry["source_path"]
        detail = ""
        if kind == "pdf":
            detail = f"{entry.get('page_count', 0)} pages"
        elif kind == "pptx":
            detail = f"{entry.get('slide_count', 0)} slides"
        elif kind == "xlsx":
            detail = f"{entry.get('sheet_count', 0)} sheets"
        elif kind == "docx":
            detail = f"{len(entry.get('paragraphs', []))} paragraphs"
        elif kind == "email":
            detail = f"{len(entry.get('attachments', []))} attachments"
        lines.append(f"- `{source}` | `{kind}` | {detail}".rstrip())

    lines.extend(
        [
            "",
            "## Findings",
            "",
            "- [Replace with validated high-severity findings first.]",
            "",
            "## Pending Review",
            "",
        ]
    )
    for entry in resume_state["documents"]:
        lines.append(f"- `{entry['source_path']}` -> memory: `{entry['memory_path']}`")

    lines.extend(
        [
            "",
            "## Method",
            "",
            "- Inventory the bundle and identify all container files.",
            "- Extract native text where possible.",
            "- OCR image-heavy or scanned content where needed.",
            "- Build external memory after each document.",
            "- Compare findings against the required baseline.",
            "",
            "## Appendix",
            "",
            f"- Analysis directory: `{analysis_dir}`",
            f"- Memory directory: `{memory_dir}`",
        ]
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
