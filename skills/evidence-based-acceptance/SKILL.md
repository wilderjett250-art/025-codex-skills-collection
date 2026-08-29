---
name: evidence-based-acceptance
description: Prevent unsupported completion claims for fixes, releases, uploads, deployments, and user-visible behavior. Use when a user reports a failure or asks whether work is fixed, complete, usable, released, or accepted.
---

# Evidence-Based Acceptance

Treat implementation, static checks, build, runtime behavior, upload, deployment, and device acceptance as separate facts.

1. Record the user's original action, expected observation, and the shortest execution chain between them before changing code.
2. Choose the minimum direct check that exercises that same chain. Code inspection, tests, build, upload, and deployment are useful evidence, but none substitutes for a successful original action.
3. Build an evidence ledger using [claim-gate.md](references/claim-gate.md). Every user-facing conclusion must name its evidence and may not exceed it.
4. If a direct runtime check is unavailable, deliver the implemented scope honestly and state the exact unverified action, environment, and next safe acceptance step.
5. If the user reports the same problem after a previous closure, invalidate that closure and its diagnosis. Reproduce or trace the original action end to end before applying another patch.

Read only the branch that matches the work:

- [wechat-miniprogram.md](references/wechat-miniprogram.md) for Mini Program routes, versions, or device acceptance;
- [web-ui.md](references/web-ui.md) for browser UI behavior;
- [api-service.md](references/api-service.md) for API/state/side-effect behavior;
- [deployment.md](references/deployment.md) for upload, release, deployment, or rollback claims.
