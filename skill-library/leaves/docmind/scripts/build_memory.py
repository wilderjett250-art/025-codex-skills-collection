#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def summary_line(meta: dict) -> str:
    kind = meta.get("kind", "unknown")
    if kind == "pdf":
        return f"pages={meta.get('page_count', 0)}"
    if kind == "pptx":
        return f"slides={meta.get('slide_count', 0)}"
    if kind == "xlsx":
        return f"sheets={meta.get('sheet_count', 0)}"
    if kind == "docx":
        return f"paragraphs={len(meta.get('paragraphs', []))}"
    if kind == "email":
        return f"attachments={len(meta.get('attachments', []))}"
    return kind


def unique_doc_id(source_path: str) -> str:
    source = Path(source_path)
    digest = hashlib.sha1(source_path.encode("utf-8")).hexdigest()[:10]
    return f"{source.stem}-{digest}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build resumable memory files from DocMind analysis artifacts.")
    parser.add_argument("--analysis", default="./_analysis", help="Analysis directory created by extract_bundle.py")
    parser.add_argument("--memory", default="./_external_memory", help="Output memory directory")
    args = parser.parse_args()

    analysis_dir = Path(args.analysis).resolve()
    memory_dir = Path(args.memory).resolve()
    memory_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_json(analysis_dir / "manifest.json")
    index_lines = [
        "# DocMind Memory Index",
        "",
        f"- Root: `{manifest['root']}`",
        f"- Documents: `{len(manifest['documents'])}`",
        "",
    ]
    resume_state = {"root": manifest["root"], "documents": []}

    for meta in manifest["documents"]:
        source = Path(meta["source_path"])
        doc_id = unique_doc_id(meta["source_path"])
        memory_path = memory_dir / f"{doc_id}.md"
        lines = [
            f"# Memory: {source.name}",
            "",
            f"- Source: `{source}`",
            f"- Kind: `{meta.get('kind', 'unknown')}`",
            f"- Coverage: `{summary_line(meta)}`",
            "",
            "## Ready Facts",
        ]

        if meta.get("kind") == "pdf":
            ocr_pages = [page["page"] for page in meta.get("pages", []) if page.get("ocr_text")]
            lines.append(f"- OCR used on pages: `{ocr_pages}`")
        if meta.get("kind") == "xlsx":
            hidden = [sheet["title"] for sheet in meta.get("sheets", []) if sheet.get("sheet_state") != "visible"]
            lines.append(f"- Hidden sheets: `{hidden}`")
        if meta.get("kind") == "pptx":
            noted = [slide["slide"] for slide in meta.get("slides", []) if slide.get("notes")]
            lines.append(f"- Slides with notes: `{noted}`")
        if meta.get("kind") == "docx":
            revisions = meta.get("revisions", {})
            lines.append(f"- Revisions detected: `{revisions}`")
        if meta.get("embedded_media"):
            lines.append(f"- Embedded media files: `{len(meta['embedded_media'])}`")

        lines.extend(
            [
                "",
                "## Outstanding Review Tasks",
                "- Compare this document against the user's target source or baseline.",
                "- Confirm whether OCR-derived text needs manual review.",
                "- Promote validated findings into the report and findings tracker.",
                "",
            ]
        )
        memory_path.write_text("\n".join(lines), encoding="utf-8")

        index_lines.append(f"- `{source.name}` | `{meta.get('kind', 'unknown')}` | `{summary_line(meta)}` | `{memory_path.name}`")
        resume_state["documents"].append(
            {
                "source_path": meta["source_path"],
                "kind": meta.get("kind", "unknown"),
                "memory_path": str(memory_path),
            }
        )

    (memory_dir / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    (memory_dir / "resume_state.json").write_text(
        json.dumps(resume_state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(memory_dir / "index.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
