---
name: docmind
description: Use for complete, image-aware review of large or mixed document bundles, including PDF, Office, scans, email attachments, archives, OCR, comparison, extraction, and formal reporting.
---

# DocMind

## Overview

Use this skill to run an end-to-end document review workflow that proves coverage, extracts text and image content, builds recoverable external memory, and produces a clean formal report. Default behavior is full reading, not sampling.

## Workflow

1. Run `scripts/bootstrap_env.py --stamp-path ./_analysis/docmind-bootstrap.json --install-missing` once per conversation before committing to the workflow. This performs the Python package self-check, installs missing pip dependencies when possible, and leaves a reusable stamp in the current work directory.
2. Run `scripts/environment_check.py` after bootstrap if you still need a detailed command and capability matrix.
3. Run `scripts/inventory_bundle.py INPUT --out ./_analysis` on the working bundle. Treat archives, email files, embedded images, notes pages, hidden sheets, and comments as first-class content.
4. Run `scripts/extract_bundle.py INPUT --out ./_analysis`. This writes per-document artifacts under `./_analysis/documents/`, expands archives and email attachments, OCRs image-only content where possible, and records coverage flags.
5. Run `scripts/build_memory.py --analysis ./_analysis --memory ./_external_memory` after each document or major chunk. For very large jobs, do this incrementally so the task survives context loss.
6. Compare source artifacts against each other using [comparison-rules.md](./references/comparison-rules.md). Keep direct quotes, translation judgments, summaries, and inferences separate.
7. Draft or refresh the report with `scripts/compile_report.py --analysis ./_analysis --memory ./_external_memory --out ./_external_memory/report.md`. Then replace placeholders with the actual findings.

## Coverage Rules

- Read every file in scope unless the user explicitly narrows scope.
- For PDFs, do not trust text extraction alone. Render and OCR pages that look image-only or low-text.
- For PPT/PPTX, inspect slide text, notes, tables, and embedded images.
- For Excel, inspect visible sheets, hidden sheets, very hidden sheets, comments, formulas, and embedded images.
- For DOCX, inspect body text, tables, headers, footers, comments, tracked changes signals, and embedded images.
- For archives and email containers, unpack them and review their children.
- If extraction is incomplete, say exactly what is missing and why.

## External Memory

Use `./_analysis/` for extraction artifacts and `./_external_memory/` for resumable task memory. Never rely on chat history for large reviews. After each document, write:

- what was read
- what was extracted
- what remains unresolved
- where the evidence lives
- whether OCR confidence is low anywhere

Read [memory-management.md](./references/memory-management.md) when the bundle is large or the task is likely to exceed context.

## Install and Approval Strategy

- Prefer local tools first.
- If a critical path is blocked by missing conversion tools such as `libreoffice` for legacy Office files, request installation approval instead of stopping at advice.
- If the user asks to install the skill for future sessions, copy or sync this `docmind/` folder into the active Codex skills directory and validate it there. Do not write outside the workspace without approval.
- For repo-based installation across Codex, Claude, and OpenClaw, use the repository root installer: `python install_global_skill.py --target all --create-missing`.

## Comparison and Reporting

- Use [comparison-rules.md](./references/comparison-rules.md) for direct-quote, translation, summary, and inference boundaries.
- Use [report-writing.md](./references/report-writing.md) for the final deliverable style. Reports should be clear, sparse, source-linked, and immediately usable by legal, compliance, and business readers.
- For large reviews, keep a running findings file in `./_external_memory/` and regenerate the formal report as the findings mature.

## Resource Map

- `scripts/environment_check.py`: Inspect commands, Python modules, and likely gaps.
- `scripts/bootstrap_env.py`: Run the once-per-conversation package bootstrap and optional pip installation.
- `scripts/inventory_bundle.py`: Build a recursive file inventory with route hints.
- `scripts/extract_bundle.py`: Extract text, OCR image-heavy content, expand archives and email bundles, and write structured artifacts.
- `scripts/build_memory.py`: Build resumable memory files from `./_analysis/`.
- `scripts/compile_report.py`: Assemble a clean markdown report from memory and findings.
- `../install_global_skill.py`: Install this skill repo into Codex, Claude, or OpenClaw global skill directories.
- [workflow.md](./references/workflow.md): End-to-end operating procedure.
- [comparison-rules.md](./references/comparison-rules.md): Review rules and evidence boundaries.
- [memory-management.md](./references/memory-management.md): Chunking and recovery guidance.
- [report-writing.md](./references/report-writing.md): Report structure and tone.

## Default Expectations

- Do the work end to end when feasible: extraction, comparison, memory, and reporting.
- Do not present a summary as if it were full coverage.
- Do not claim "word-for-word" equivalence across languages. Use fidelity language for translations.
- Surface hard blockers early, but keep moving with partial work where possible.
