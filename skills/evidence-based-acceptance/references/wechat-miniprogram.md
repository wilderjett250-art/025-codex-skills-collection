# WeChat Mini Program Acceptance

Read this only for Mini Program behavior, routing, upload, experience-version, or device claims.

## Route the reported action, not only the handler

For a navigation defect, trace:

`user tap -> WXML binding -> handler -> route API -> target page type -> target page data/load -> visible result`

Check the target page registration and `tabBar` configuration before selecting a route API. In the known failure class, a target configured as a tabBar page cannot be treated as an ordinary pushed page: a `navigateTo` route to it does not prove navigation is valid; the appropriate tab switch path must be verified against the actual project configuration.

Static evidence such as “the button has `bindtap`” or “the handler calls a route API” is not runtime evidence. Verify the original tap path in Developer Tools automation, an authorized real session, or a target-version device flow.

## Version and acceptance boundary

Keep these facts distinct:

1. source changed;
2. Developer Tools compiled;
3. a development version was uploaded;
4. that exact version was selected as an experience version;
5. the intended account/device executed the original path successfully.

Only item 5 supports a target-version behavior claim. Record AppID, version, environment, and the exact page/action without placing credentials, cookies, or private device identifiers in the handoff.

## Regression case shape

For each fixed Mini Program defect, keep one focused regression case:

- original action and expected visible outcome;
- target page type and route compatibility;
- bound handler and route call;
- proof of actual original-path execution or a precise human acceptance gap.
