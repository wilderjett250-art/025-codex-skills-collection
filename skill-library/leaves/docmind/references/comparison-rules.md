# Comparison Rules

## Evidence Boundaries

- Treat direct quotations and extracted source text as evidence.
- Treat translations as fidelity judgments, not literal word-for-word matches across languages.
- Treat summaries as derived statements that must be checked against the source.
- Treat legal or business implications as inferences unless the source states them directly.

## Required Output for Every Finding

- source file
- exact locator: page, slide, sheet, cell, or paragraph
- the claim being tested
- the reason it is wrong, incomplete, or uncertain
- whether the issue is a hard error, likely drift, or needs review

## Severity Hints

- High: legal effect changed, obligation scope changed, date or threshold wrong, quoted source text altered
- Medium: summary is overstated, understated, or missing a condition
- Low: wording is clumsy, typo in non-critical prose, formatting issue

## Translation Review Rule

Never claim "exact match" across languages. Use:

- faithful
- partially faithful
- omitted condition
- added meaning
- mistranslated legal effect

## Large Bundle Rule

Do not compare from memory alone. Open the extracted artifact or source-adjacent memory before writing the finding.
