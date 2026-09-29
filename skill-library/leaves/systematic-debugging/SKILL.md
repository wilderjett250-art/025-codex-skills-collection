---
name: systematic-debugging
description: Trace a reproducible bug, failing test or cross-component fault to evidence before patching. 根因定位、反复修不好、故障排查。Scale investigation to the failure; not a mandatory ceremony for trivial edits.
---
# Systematic debugging
Adapted from obra/superpowers; see LICENSE and the pinned source record.
1. Identify the exact action, expected observation, actual result and environment. Reproduce or collect the smallest discriminating evidence.
2. Trace boundaries from the user action to the failing component; compare a known-working path and recent relevant changes.
3. State a testable hypothesis and use a minimal check to separate it from alternatives. Change one causal factor at a time when practical.
4. Patch the supported cause, replay the original action and check nearby invariants. A passing unrelated test does not prove recovery.
If evidence disproves the hypothesis, revise it rather than accumulating patches. Repeated failures justify revisiting the boundary or architecture; uncertainty alone does not authorize a rewrite.
Never dump environment variables, credentials or full customer payloads for diagnostics. Log only necessary non-secret metadata. Follow the project's recovery gate before writes.
For deep call stacks read [root-cause tracing](root-cause-tracing.md); for timing issues read [condition-based waiting](condition-based-waiting.md). These are optional techniques.
Use the existing testing owner and the global Evidence and handoff rules. No new agent, installation or user approval is implied by this Skill.
