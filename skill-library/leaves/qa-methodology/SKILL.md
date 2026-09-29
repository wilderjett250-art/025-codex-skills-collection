---
name: qa-methodology
description: Plan risk-based testing, regression selection, exploratory checks and release quality criteria. 测试策略、测试计划、风险覆盖、探索测试。Not routine bug tracing or automatic browser control.
license: MIT
---
# Test strategy
Map the real acceptance criteria and highest-impact failure modes to the smallest useful test levels. Separate implemented, exercised and unverified behavior. Untested means unverified, not automatically broken.
Prioritize authorization, data integrity, concurrency and recovery when relevant. Do not invent numeric risk scores or force a document template for a small change. Reuse the project's runners and existing fixtures.
Choose only the needed reference:
- [Strategy](references/test-strategy.md) for level/scope allocation.
- [Regression](references/regression-testing.md) for change-impact selection.
- [Design techniques](references/test-design-techniques.md) for boundary/state cases.
- [Exploration](references/exploratory-testing.md) for scenario charters.
- [Data](references/test-data-management.md) for isolated fixtures.
- [Performance](references/performance-testing.md) for explicit load goals.
- [Automation](references/test-automation.md) for runner/flake infrastructure.
References are techniques, not permission to adopt mandatory independent agents, fixed retry counts, arbitrary coverage thresholds or unconditional escalation stops. Investigate a flaky check; do not report retries as a clean first pass.
Use e2e-testing for user-journey execution and systematic-debugging for causal fault tracing. The resulting plan names what is checked, where, what observable outcome passes, and what remains unverified.
