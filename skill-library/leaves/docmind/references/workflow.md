# Workflow

## Goal

Use DocMind when completeness matters more than speed. The default standard is: read everything, prove coverage, preserve evidence, and leave a resumable trail.

## Operating Sequence

1. Run `environment_check.py`.
2. Run `inventory_bundle.py`.
3. Expand archives and email containers through `extract_bundle.py`.
4. Review the generated `manifest.json`.
5. Build external memory with `build_memory.py`.
6. Compare documents against the user's baseline.
7. Generate or refresh the report with `compile_report.py`.

## Default Review Depth

- PDF: native text plus OCR fallback for low-text pages.
- PPT/PPTX: slide text, notes, tables, and embedded images.
- Excel: visible sheets, hidden sheets, very hidden sheets, comments, formulas, and embedded images.
- DOCX: paragraphs, tables, headers, footers, comments, revision signals, and embedded images.
- Images: OCR if possible.
- Email bundles: body plus attachments.
- Archives: unpack then recurse.

## When to Request Install Approval

Request approval instead of stopping when:

- legacy `.doc`, `.xls`, or `.ppt` files are in scope and no conversion tool is available
- OCR is required but `tesseract` is missing
- a critical archive format cannot be unpacked

Always say what is blocked, what tool is missing, and what will become possible after install.

## Recovery Rule

After each document or major chunk:

- update `./_external_memory/index.md`
- refresh the per-document memory file
- keep unresolved questions explicit

If context gets tight, reload `index.md`, `resume_state.json`, and the relevant document memory before continuing.
