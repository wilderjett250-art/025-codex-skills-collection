---
name: "playwright-interactive"
description: "Debug a local browser or Electron app in an explicitly requested persistent session using the current supported runtime; preserve an existing user-selected browser/profile."
---

# Persistent browser and Electron debugging

Use for an explicitly requested persistent debugging session. Current tool documentation and the user's selected browser/session determine the control route; historical `js_repl` names are not a requirement.

1. Identify the target app/project, existing session, and callable browser/debugging capability. For an already logged-in browser use its supported bridge. For local app debugging use only an authorized debug instance. Never silently replace the user's selected browser or profile.
2. Reuse a live supported session and handles; reset only after an observed session failure or ownership change. Tool names such as `node_repl` and `cua_repl` describe different interfaces and are not interchangeable by renaming a variable.
3. Check only the runtime/dependencies needed for this target. Do not disable the sandbox, enable old feature flags, restart Codex, initialize npm, or install global tools simply because this guide was loaded. If a prerequisite really is missing, use an authorized equivalent or state the exact dependency and permitted recovery.
4. Exercise the requested behavior and relevant failure case with real inputs, then inspect the actual visual result when layout matters. Preserve meaningful handles and observations rather than taking the same full screenshot repeatedly.
5. After a transient failure, check whether the action completed, reconnect/refresh the same session as appropriate, and retry once. For a real password/MFA/CAPTCHA/permission gate show that official surface and resume when its resolution is observable.
6. Clean up only processes, pages and fixtures created by this task. Report what was actually tested and what remains unavailable.

For this host, load the currently available official computer-use/browser skill when that route owns the operation. The legacy recipes are preserved in the recovery set; their old feature flags and sandbox assumptions are not current setup instructions.
