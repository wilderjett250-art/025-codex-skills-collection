# Claim Gate

Use separate statuses rather than a single vague “done” state. Each status needs a source that directly establishes that fact.

| Status / permitted conclusion | Minimum direct evidence | Does not prove it |
| --- | --- | --- |
| `implemented` — code/config was changed | changed path, revision, or diff | test result, build, upload |
| `static_validated` — static checks passed | named check and real result | code inspection alone |
| `build_validated` — build/compile succeeded | command, artifact, and result | unit tests or upload receipt |
| `runtime_validated` — reported action now succeeds | original action, environment/version, observed successful result | source inspection, tests, build, upload, or deployment |
| `uploaded` — a specified development artifact was uploaded | version/AppID or artifact identity and upload result | selection as experience version, runtime success |
| `deployed` — specified target received the artifact | target identity, revision/artifact, deployment result | local build, HTTP reachability, upload |
| `device_accepted` — target version works for the target user/device path | target version, account/device, original action, observed success | CLI upload, deployment, or a different version |

## Invariants

- A release event never upgrades an unverified behavior claim. `uploaded` and `deployed` are independent from `runtime_validated`.
- “Fixed”, “usable”, “complete”, and “accepted” are behavior or acceptance claims. Do not use them unless the relevant direct status is verified.
- An absence of a failing test is not evidence that the reported action succeeded.
- The final response must name both verified facts and the highest-impact missing evidence. Do not hide the latter in a generic caveat.

## Compact final ledger

Use this only when the task has a material validation boundary:

| Scope | Verified facts | Not verified | Next safe action |
| --- | --- | --- | --- |
| reported behavior | exact direct evidence | original action / target version / device if missing | smallest action that supplies it |

Do not list every command. Link or cite the one result that proves each verified fact.
