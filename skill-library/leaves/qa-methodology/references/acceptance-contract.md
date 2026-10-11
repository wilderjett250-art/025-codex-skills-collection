# Product acceptance contract

Derive the standard from the supplied requirements, actual product contract and applicable verified specification, not a generic score or test percentage. For an external standard, check its current primary source and target scope; a checklist or automated scan alone is not certification.

Map each in-scope material criterion to: user action/input, expected observable behavior, environment/target version, chosen test or direct observation, evidence location and status (passed, failed, unverified, not applicable with reason). Use a small table only when the mapping helps. Keep one canonical record.

Exercise the critical journey and meaningful boundaries: authorization, data integrity, invalid input, state transitions, concurrency and failure/recovery as applicable. Frontend/API/schema agreement matters more than isolated green unit checks. Use real user-facing content and relevant viewports/accessibility checks for UI; realistic synthetic data for writes.

Prefer tests through stable public boundaries with expectations independent of implementation. Include a known failing behavior or boundary to show a regression test can detect the defect. Avoid tautological assertions, snapshots generated from the same logic and mocks that hide the failing integration.

Report exact command/action, result and uncovered risk. Separate code/build checks from exercised runtime, uploaded target, deployed target and device acceptance. An unavailable browser or device leaves that journey unverified, not passed. Repeated flaky runs do not erase initial failure. Respect existing permission and recovery gates; acceptance planning does not authorize a production release.
