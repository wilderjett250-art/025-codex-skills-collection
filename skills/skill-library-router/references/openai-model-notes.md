# One shared library: OpenAI model notes

Reviewed 2026-11-13. These are official-guidance-based usage notes, not four benchmark-certified skill variants. Keep domain procedures, scripts, templates, user preferences, permissions and acceptance criteria shared.

- **Astra:** use clear outcomes and completion criteria. Avoid broad mandatory preliminary reading, duplicated coaching and unnecessary approval checkpoints; its stronger instruction following can make conflicting skill rules unusually blocking.
- **Sol:** use the shared workflow. Official positioning balances complex work with time/cost; it does not justify inventing an extra mandatory recipe for every skill.
- **Terra:** official positioning emphasizes visual reasoning, precise computer use, concise writing and scoped fixes. Use the actual supported app/browser tools and observed state; this is not permission to take the desktop or change the user's tool route.
- **Luna:** official positioning favors focused, bounded tasks. Clear inputs/outputs and a short set of necessary steps are a usage recommendation, not evidence that a separate long prompt improves every task.

Automatic selection uses the active `model` field supplied by Codex's SessionStart/UserPromptSubmit hook envelope. The short data source is [model-profiles.json](model-profiles.json); only the selected note enters model context. A model switch takes effect on the next submitted prompt. Initial load, resume and compaction re-deliver the note; unchanged prompts are deduplicated per session/agent. The cache contains model/family/profile fingerprint only, and never substitutes for missing current metadata.

Unknown exact ids, missing metadata or a disabled/untrusted hook use the shared workflow, without asking the user or guessing from prompts, transcripts or config defaults. Do not silently change models, reasoning effort, sandbox or client configuration. These are recommendations, not stronger constraints than the user's task. Do not run self-improvement loops or paid evaluations to use these notes. Installation and hook trust are separate; see the repository's model-routing setup.

Sources:
- [OpenAI: model selection](https://developers.openai.com/api/docs/guides/model-selection)
- [OpenAI: rethinking skills and prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [OpenAI: hooks and active model metadata](https://learn.chatgpt.com/docs/hooks)

New model/client releases justify a bounded source/compatibility review of affected instructions. They do not justify copying the entire library or declaring unmeasured performance gains.
