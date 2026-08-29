---
name: agent-orchestration
description: Use when a task genuinely needs multiple agents, parallel work lanes, isolated worktrees, team selection, or a named orchestration runtime. Routes to one focused operating model without loading every runtime guide.
metadata:
  consolidation: team-agent-orchestration, team-builder, parallel-execution-optimizer, claude-devfleet, dmux-workflows
---

# Agent Orchestration

Use this Skill only when parallel specialist work materially improves the task or the user explicitly asks for multiple agents. Keep ordinary work in the current agent.

## Route by need

- For ownership, Kanban state, handoffs, evidence, and merge gates, read [team operations](references/team-operations.md).
- For discovering and selecting agent personas, read [agent picker](references/agent-picker.md).
- For dependency graphs, batched checks, and collision-free parallel lanes, read [parallel execution](references/parallel-execution.md).
- For an explicitly configured Claude DevFleet service, read [Claude DevFleet](references/claude-devfleet.md).
- For an explicitly requested dmux workflow, read [dmux workflows](references/dmux-workflows.md).

Load only the selected branch. Runtime-specific instructions do not apply unless that runtime exists and the user placed it in scope.

## Common contract

Before dispatching work, define:

- objective and acceptance evidence;
- lane owner and exact read/write scope;
- dependencies and merge order;
- stop conditions and timeout handling;
- final integrator and verification gate.

Parallelize independent reads and non-overlapping writes. Do not parallelize destructive actions, shared-state mutations, or edits to the same files without isolation.

## Completion

Report which lanes ran, their artifacts, failures or conflicts, the integration decision, and the verification that proves the combined result.
