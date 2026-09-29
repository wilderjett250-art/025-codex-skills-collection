---
name: e2e-testing
description: Verify web user journeys end to end, diagnose flaky Playwright tests and capture actual browser evidence. 端到端测试、点击流程、登录购物流程验收。Not unit tests or synthetic screenshots.
metadata:
  origin: ECC
---
# End-to-end verification
Choose the actual user journey and the closest authorized environment. Use the project's existing runner and browser tooling.
- Reuse the requested browser/profile. An existing logged-in Edge request uses external-browser; do not silently switch to an isolated browser.
- Default write tests to disposable identities and isolated data. Control notifications/jobs/payments. Existing production customer data is not a test fixture.
- Inspect rendered controls and use resilient role/label selectors. Wait for a meaningful readiness condition or response; a universal networkidle wait fails on polling/streaming apps. Avoid arbitrary sleeps.
- Assert the user-visible outcome and the relevant persisted effect. A click, HTTP 200 or screenshot file alone is insufficient.
- Preserve a concise failure trace and real final evidence; rerun only affected checks after a change. Do not blindly retry flaky tests until green.
For maintaining a Playwright suite, read [suite patterns](references/suite-patterns.md).
For a local app without a server harness, inspect help for references/anthropic/webapp-testing/scripts/with_server.py. Use it only when owning the test processes is appropriate; verify Windows subprocess cleanup before use on long-running services. Its Python Playwright examples are optional, not a stack replacement.
Keep server lifecycle, browser navigation and actual business assertions separate. State which original action was and was not exercised.
