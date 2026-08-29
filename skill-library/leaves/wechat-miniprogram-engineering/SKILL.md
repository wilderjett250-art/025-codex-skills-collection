---
name: wechat-miniprogram-engineering
description: 'Trace, change, and verify native WeChat Mini Program behavior across app.json, pages, tabBar routes, handlers, requests, DevTools builds, uploads, and release boundaries. Skip ordinary mobile-native apps.'
---

# WeChat Mini Program Engineering

Own the Mini Program execution chain, not the whole product.

1. Confirm the Mini Program root, framework type, AppID boundary, target environment, and original failing user action.
2. Trace the smallest complete path from visible control to handler, route or request, target page, state load, and rendered result. For page registration and `tabBar` navigation, read [routing.md](references/routing.md).
3. Make the narrowest source/configuration change that repairs that path. Keep AppSecret, service credentials, and privileged logic server-side.
4. Re-run the exact path at the highest available level. Treat source checks, DevTools compilation, development upload, selected experience version, and real-device acceptance as different evidence.
5. For upload, release, or version claims, read [release-boundaries.md](references/release-boundaries.md) and use `evidence-based-acceptance` as the claim gate.

Do not replace a user-required framework or project route without approval. If automation cannot reach DevTools or the target account/device, leave the exact remaining action instead of claiming runtime success.
