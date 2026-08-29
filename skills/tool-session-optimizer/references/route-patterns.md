# Access route patterns

Use the smallest matching pattern. These are routing rules, not permission to mutate external state.

## Existing browser session

- When the user asks to use an already logged-in Edge/Chrome site, use `external-browser` and the connected tab/session.
- If the target tab is absent, navigate within that approved browser session; do not silently launch an isolated browser.
- If a web server or cloud console is already authenticated in the browser, do not ask for its password or replace the requested web route with SSH.
- If the site requires password, MFA, CAPTCHA, or account confirmation, leave the real page visible for the user. Never inspect password-manager data, password fields, cookies, or tokens.

## Server operation

- For filesystem, process, log, service, or deployment work, prefer an existing authorized SSH alias/key when the user has not required a web console.
- For account, billing, graphical configuration, or a user-requested web-console action, reuse the authenticated browser instead.
- Do not translate a browser login into credential extraction, and do not ask for a server password when an approved alias/session already works.

## Native app plus CLI

- Query the real session state before invoking login.
- If logged in, use the CLI directly.
- If logged out or expired, open the official app at its native login/confirmation surface. Do not start a background login command first when it hides the required user action.
- After the app reports the required state, confirm it through the CLI and resume the original command.
- If an app explicitly presents a QR, leave that app visible; do not copy the QR into Photos or another viewer unless the user asks.

## Connected API or MCP

- Prefer a connected API/MCP for bounded, structured operations when it already has the required authorization.
- Use the native UI only for unsupported operations or a human authorization gate.
- A connector failure does not authorize installing a substitute, opening an unrelated browser, or collecting credentials.

## Fallback order

1. Retry only after checking whether the first action may already have succeeded.
2. Refresh the same route if its state changed.
3. Use an equivalent approved route only when it preserves the target and authorization boundary.
4. Otherwise open the exact user confirmation surface or report one concise blocker.
