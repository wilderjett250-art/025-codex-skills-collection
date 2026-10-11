---
name: qa-methodology
description: Assess product conformance and plan risk-based tests against requirements and release criteria. 产品测试、上线标准、需求验收、验收证据、质量门禁、测试策略。Not routine bug tracing or browser control.
license: MIT
---
# Test strategy
Map the real acceptance criteria and highest-impact failure modes to the smallest useful test levels. Separate implemented, exercised and unverified behavior. Untested means unverified, not automatically broken.
Prioritize authorization, data integrity, concurrency and recovery when relevant. Do not invent numeric risk scores or force a document template for a small change. Reuse the project's runners and existing fixtures.
Choose only the needed reference:
- [Acceptance contract](references/acceptance-contract.md) for product conformance, release criteria or missing requirement-to-evidence coverage.
- [Strategy](references/test-strategy.md) for level/scope allocation.
- [Regression](references/regression-testing.md) for change-impact selection.
- [Design techniques](references/test-design-techniques.md) for boundary/state cases.
- [Exploration](references/exploratory-testing.md) for scenario charters.
- [Data](references/test-data-management.md) for isolated fixtures.
- [Performance](references/performance-testing.md) for explicit load goals.
- [Automation](references/test-automation.md) for runner/flake infrastructure.
References are techniques, not permission to adopt mandatory independent agents, fixed retry counts, arbitrary coverage thresholds or unconditional escalation stops. Investigate a flaky check; do not report retries as a clean first pass.
Use e2e-testing for user-journey execution and systematic-debugging for causal fault tracing. The resulting plan names what is checked, where, what observable outcome passes, and what remains unverified.
