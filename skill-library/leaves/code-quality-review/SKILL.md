---
name: code-quality-review
description: Review a diff or scoped module for requirement alignment, correctness and maintainability with actionable evidence. 代码审查、代码混乱、职责耦合、重复代码、过度抽象、重构建议。Not beginner code explanation or a dedicated security audit.
---

# Code quality review

Default to read-only. Pin the requested diff/base or named module and applicable project rules; include dirty changes only when in scope. Infer an obvious baseline from repository evidence rather than requesting unnecessary setup. If multiple comparisons materially change the review, ask one precise question. A missing spec is a stated limit, not a reason to invent one or halt all review.

Examine two separate axes:

- Requirement/behavior: missing or unintended behavior, contracts, state transitions, error paths and meaningful test gaps. Trace callers and data ownership beyond a suspicious hunk before declaring a bug.
- Maintainability: domain cohesion, change hotspots, dependency direction, repeated business logic, dispersed edits, opaque naming and speculative abstraction. Explain the real change/debugging cost; length, layer count or a personal preference alone is not a defect. Project conventions override generic heuristics.

For each material finding, cite file/line, triggering condition, user or maintenance impact, supporting evidence and the smallest plausible remedy. Separate introduced defects from relevant pre-existing problems, verified violations from hypotheses, and urgent fixes from optional refactors. Investigate contradictory evidence; suppress disproven claims. A self-assigned numeric confidence is not proof. Do not pad the report with formatter noise or claim CI ran without inspecting it.

Run permitted focused read-only checks where useful; write-based tests must use the existing isolation/recovery gates. Independent review is optional when complexity warrants it and delegation is available; otherwise review the axes separately without claiming independent agents. No automatic PR comments, rewrites or releases. A review request does not authorize implementation.

Return findings by impact with evidence and coverage limits. "No material findings in the inspected scope" is not "the entire product is correct." Use a dedicated security owner only for an actual security objective; architecture-decisions for consequential boundary redesign, and the actual framework owner if fixes are subsequently authorized.
