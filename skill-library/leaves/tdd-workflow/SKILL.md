---
name: tdd-workflow
description: Develop behavior with a failing regression test, minimal implementation and refactoring when TDD is requested or valuable for logic changes. 测试驱动、回归测试、业务规则测试。Not a mandatory gate for every edit.
metadata:
  origin: ECC
---
# Behavior-driven test loop
Use the existing test runner and the smallest boundary that can observe the required behavior.
1. Express the expected behavior and a meaningful counterexample. For a reported bug, reproduce the failing action first.
2. Run the test and verify the intended failure, not a missing import or setup error.
3. Make the minimal implementation and rerun the affected checks.
4. Refactor only with behavior still protected; broaden tests when changed dependencies or failures justify it.
Prioritize authorization, money/data invariants, concurrency, retries and edge cases by actual risk. A coverage percentage alone is not acceptance; follow explicit repository coverage requirements rather than imposing a universal threshold.
Do not invent tests that mirror source wording or require a full TDD cycle for a trivial text/style edit. Use e2e-testing for a user journey crossing the browser/API boundary; global Evidence and handoff rules govern completion claims.
[Legacy examples](references/testing-examples.md) are optional recipes. Their blanket 80% coverage and all-changes-TDD rules are superseded by this scoped entrypoint.
