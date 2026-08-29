---
name: agent-evaluation
description: Use when designing or running evaluation datasets, graders, promotion gates, or regression tests for AI agents and AI-generated changes. Routes formal eval construction separately from bug-derived regression coverage.
metadata:
  consolidation: eval-harness, ai-regression-testing
---

# Agent Evaluation

Use this Skill for repeatable evidence about agent or AI-assisted engineering quality. It is not a substitute for the project test suite or ordinary diff review.

## Route by objective

- For datasets, graders, thresholds, pass rates, and promotion decisions, read [eval harness](references/eval-harness.md).
- For preserving discovered AI coding failures as focused tests, read [AI regression testing](references/ai-regression-testing.md).

Load one branch unless the task explicitly needs both. Keep eval inputs, scoring rules, and acceptance thresholds separate from the system under test.

## Minimum evidence

- named behavior or failure class;
- representative cases and expected outcomes;
- deterministic checks where possible;
- recorded command, environment, and result;
- explicit remaining blind spots.

Do not infer production quality from a single anecdotal run or from an evaluator that shares the same untested assumptions as the implementation.
