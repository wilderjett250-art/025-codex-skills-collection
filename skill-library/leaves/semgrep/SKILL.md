---
name: semgrep
description: Use in authorized security work to run Semgrep scans, including full or high-confidence modes, multi-language parallel analysis, and Semgrep Pro cross-file tainting when available.
allowed-tools: Bash Read Glob Task AskUserQuestion TaskCreate TaskList TaskUpdate
---

# Semgrep security scan

Run an authorized local scan and produce reproducible findings. The user's request determines target, mode and output scope. A clear scan request can authorize its ordinary local scan; do not require a second approval merely because a plan was printed.

1. Identify the exact checkout/target and existing Semgrep setup. Reuse a specified CI/ruleset/mode. If scope is materially unclear, ask one concise question; otherwise state the safe selection and proceed.
2. Check the installed executable/version and available engine. Do not acquire a Pro license, send source to a cloud service, install tools, or download extra third-party rules without the applicable authority. Use reviewed local/project rules first; additional compatible rules are optional and must be justified.
3. Record target, engine, ruleset versions/paths, mode and output directory. Use the permitted task/artifact location (on this Windows machine prefer I:, then G:). Preserve existing reports; do not overwrite a user's files.
4. Validate the chosen configuration and run the supported CLI with `--metrics=off`. Keep telemetry disabled on every Semgrep invocation. Avoid `--config auto` and implicit network discovery. Check current CLI flags instead of assuming an old severity or Pro option is supported.
5. Run small scans inline. Parallel execution is optional when supported, authorized and useful; never invent a `Task` tool or `static-analysis:semgrep-scanner` agent. Keep the same target/rules across execution methods.
6. Save real JSON/SARIF plus scan status. Where multiple SARIF files need merging, use the existing [merge_sarif.py](scripts/merge_sarif.py) with the actual Python executable and explicit raw/output paths. Missing or failed scans are not a clean bill of health.
7. Triage findings with source locations, confidence, limitations and reproduction evidence. Distinguish scanner output from verified exploitability and unchanged pre-existing findings.

Do not auto-approve new paid resources, external transfers, expanded targets or destructive tests. Respect genuine approval boundaries already supplied by the user. Historical `workflows/scan-workflow.md` and Task templates remain intact as upstream reference material; they are not the active authorization or runtime contract.
