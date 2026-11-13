---
name: dimensional-analysis
description: Use to annotate and verify units, dimensions, decimal scaling, and arithmetic formulas in code, especially for authorized DeFi or blockchain security review.
allowed-tools: Read Write Grep List Glob Task TodoRead TodoWrite
---

# Dimensional analysis

Audit units, fixed-point decimal scaling and arithmetic within the user's exact target and requested mode. Preserve an explicitly selected method. A single-formula spot check needs no repository-wide pipeline.

## Scope and execution
- Respect requested read-only/review/annotation scope and any supplied mode; never silently ignore it or widen the target. Annotation writes require their normal backup/authorization.
- Use the current model inline by default. Optional supported agents may own independent phases only when delegation is authorized and useful. Legacy `Task`/role names describe responsibilities, not proof of a registered runtime.
- Keep the full audit sequence: establish scope/vocabulary, annotate anchors when authorized, propagate dimensions, validate mismatches. The same substantive coverage is required regardless of executor.

## Method
1. Inspect the arithmetic inputs, denominations/units, decimal conventions and trust boundaries. Establish every in-scope arithmetic file and its priority. A discovery sample never narrows the approved full-audit scope.
2. Reuse `DIMENSIONAL_SCOPE.json` and `DIMENSIONAL_UNITS.md` only if their project identity, content/version and per-file phase states are still valid. Create/update such task artifacts only within the user's authority. For read-only work use the permitted artifact location rather than modifying the checkout.
3. Use [common dimensions](references/common-dimensions.md) and [dimension algebra](references/dimension-algebra.md) to trace actual inputs and scaling. Read [annotation rules](references/annotate.md) only when annotations are part of the task.
4. Propagate dimensions through conversions, multiplication/division, rounding and external calls. Validate candidate mismatches against actual code and [bug patterns](references/bug-patterns.md); do not report an unverified unit guess as an exploitable flaw.
5. For a full pipeline, track each file's anchor/propagation/validation state. A no-anchor or no-propagation result is valid only with evidence. Retry a failed phase once with a focused recovery; retain terminal blocked reasons and process independent files.
6. Report verified findings, explicit assumptions and exact unprocessed files/phases. Do not call a partial run a full audit, simulate unlaunched specialists, or mark missing work passed. If a specified method cannot be performed, explain the concrete gap and obtain agreement before substituting it.

The bundled references/assets and original orchestration guide remain preserved. Current task scope and supported tools govern execution.
