# Upload, Deployment, and Release Acceptance

Name the target precisely: artifact/version, AppID or application, environment, host/service, revision, and intended user/device path as applicable.

Separate these claims:

- artifact built;
- artifact uploaded;
- artifact deployed to target;
- target responds or process is healthy;
- original user action works in that target;
- target user/device accepted the intended version.

Each line needs its own result. A reachable health endpoint, uploaded package, or matching source hash can support its respective line, but cannot replace an original-path runtime check.

If an external action is blocked by login, MFA, CAPTCHA, permissions, billing, or a missing device, stop at the verified boundary and record the exact gate. Do not simulate a success path.
