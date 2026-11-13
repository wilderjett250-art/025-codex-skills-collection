# Shared library and automatic model context — 2026-11-13

## Result and boundaries

One public library: 10 active + 292 on-demand Skills. Existing canonical domain/discipline/family routing remains; model notes do not create four copies or change tool access, sandbox, permissions or task scope.

The common-library repair preserves explicit legacy invocation policies, prefers supported primary plugins, removes retired runtime assumptions from entrypoints, and corrects task/platform false positives. Supporting resources remain. Previous entrypoints are recoverable from Git revision `a9911e07cd2eb2981825d5a7effeb995595714e6`; the maintainer separately verified exact private local backups. Machine-local backup contents and paths are not exported.

The newly catalogued mind-atlas entry matches pinned upstream `jessepwj/mind-atlas` revision `5a37a88ce2e796356310e25393ae8e029a0d19c8`; MIT license and source attribution are retained with the Skill.

## Model route

- Source: the active `model` field in the official Codex command-hook envelope. Never prompts, writing style, transcript files, cached guesses or the configured default model.
- Events: SessionStart and UserPromptSubmit. A switch is applied at the next submitted prompt. SessionStart also covers resume and compaction.
- Exact current-id allowlist selects one short note. Unknown/missing ids invalidate earlier model-specific notes and silently use shared rules.
- Per-session/agent hash-keyed state deduplicates unchanged submissions. Records contain only model, family and profile fingerprint. Cache failure permits repeated short context rather than blocking a turn.
- No model or reasoning-level switching, provider calls, network requests, prompt storage, transcript reads, automatic training, model evaluation or paid optimizer loops.
- This does add a short selected note to model input. No claim of zero input-token overhead or benchmark-certified model performance is made.

## Validation

Executed locally on Windows, with no inference requests:

| Check | Result |
|---|---|
| Model hook, stdin boundary, switching/fallback, isolation and installer | 15/15 |
| Shared-library identity, restrictions, retrieval and CLI consistency | 8/8 |
| Original retrieval checks | 86/86 |
| Lexical route checks | 98/98 |
| Context boundary checks | 17/17 |
| Activity tests | 4/4 |
| Capability retrieval | 21 cases passed, plus six boundaries |
| Isolated PowerShell 5.1 installation | 10 active + 292 on-demand |
| Desktop-bundled core hook discovery and trust | Both definitions enabled and trusted, existing PostToolUse unchanged |

The desktop package's bundled core reported `0.167.0-alpha.4.1`. Trust was registered through the official hook-review interface and independently read back with `hooks/list`; no trust bypass or copied trust hash was used. A no-prompt ephemeral runtime probe created no inference request and emitted no hook completion; it is not proof of message-time context delivery. Real next-message/model-switch delivery remains unverified under the user's no-model-test constraint. No promise is made about older clients or future model quality.

## Reproduce without a model

After materializing the portable catalog into an isolated home, set `MODEL_CONTEXT_TEST_ROOT` to an approved data-drive scratch directory and run:

```text
node --test skill-library/scripts/model-context.test.mjs
node --test skill-library/scripts/common-library.test.mjs
node skill-library/scripts/search-skills.test.mjs
node skill-library/scripts/route-task.test.mjs
```

First-time installation requires official hook review; subsequent model switches do not. Clients that do not support these events, disabled/untrusted hooks or unavailable model metadata retain shared rules. A changed hook definition/script may require review again, according to the client; do not disable the review mechanism to avoid that prompt.

Sources: [OpenAI hooks](https://learn.chatgpt.com/docs/hooks), [model selection](https://developers.openai.com/api/docs/guides/model-selection), [Astra skills guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).
