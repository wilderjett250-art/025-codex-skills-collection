# Common capability boundaries

Use only when task intent is ambiguous; existing available Skill descriptions still come first. Search metadata for the current work unit, compare at most three candidates, then read one owner. These are examples, not a mandatory lifecycle.

| Current need | Local owner / boundary |
|---|---|
| Large/legacy project coordination, milestones and agent packages | large-project-ops; not technical architecture or every small feature |
| Product-manager review, user value, priorities or uncertain scope | product-discovery; not generic visual polish |
| Journey, navigation, recovery or difficult interaction | interaction-design |
| New visual direction or full redesign | frontend-design; existing-interface refinement goes to impeccable |
| Technical options, coupling, data ownership and migration decisions | architecture-decisions |
| Unknown cross-stack performance bottleneck or measured variants | benchmark-optimization-loop; known React/Vue/database causes use their existing owner; game frame/GPU profiling uses performance-optimization |
| Requirement alignment and code maintainability review | code-quality-review; code-explanation is for learning, security-review for a security objective |
| Product standards and requirement-to-evidence test coverage | qa-methodology; e2e-testing executes relevant web journeys; evidence-based-acceptance governs completion claims |

MCP is an access layer, not a replacement for these owners:

- Repository inspection, profiling and tests: authorized CLI is often sufficient; a connector can retrieve authorized remote issues/PRs without duplicating local reads.
- Design: use connected Figma tools for a supplied design or approved design write, with their mandatory tool Skills. Canva/creative tools serve actual visual-asset requests, not generic architecture/code review.
- Runtime acceptance: use a callable browser/API tool for the actual journey and target session. Preserve an explicitly requested logged-in browser route. A configured but unavailable bridge does not prove a passed test.
- Account/cloud writes, publishing, load generation or sensitive test data still require the established permission/recovery scope. Do not enable every MCP, export sessions or assume tool availability from configuration.

Normal language is enough to describe a task; an explicit `$skill-name` is optional. Metadata search is advisory, not an LLM-selection guarantee, and an instruction-load count is not product-quality evidence.
