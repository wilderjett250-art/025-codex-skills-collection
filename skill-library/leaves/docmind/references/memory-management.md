# Memory Management

## Directory Contract

- `./_analysis/`: raw extraction artifacts, manifests, rendered pages, OCR outputs
- `./_external_memory/`: resumable task memory, findings tracker, report draft

Keep both directories inside the current working directory so the task remains portable.

## Minimal Memory Set

- `index.md`: global map of reviewed documents
- `resume_state.json`: machine-readable continuation state
- one memory file per source document
- `report.md`: current formal output

## Chunking Strategy

For large jobs, chunk by:

- PDF pages or chapters
- slide ranges
- workbook sheets
- attachment groups
- archive subtrees

Only keep the active chunk in context. Everything else should be read back from disk.

## Write After Every Milestone

Write memory after:

- finishing one document
- unpacking a large container
- resolving a major finding
- generating a new report version

## Low-Confidence OCR

If OCR looks noisy, record that in memory rather than silently treating it as trusted text.
