# Web UI Acceptance

For a reported UI failure, test the same meaningful action a user reported:

`starting page/state -> user action -> browser event -> client logic -> network/state transition -> target DOM or page observation`

A component test, lint result, screenshot of a static page, or successful API response does not by itself prove the interaction. Prefer an authorized real browser/session when login state, routing, permissions, or persisted data affects the result.

When direct browser automation is unavailable, report the exact unverified click path and provide the smallest reproducible manual check. Do not replace it with coordinate-based guesses or a fresh unauthenticated browser when the user asked to reuse an existing session.
