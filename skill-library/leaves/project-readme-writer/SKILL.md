---
name: project-readme-writer
description: Use to create or update a concise Chinese-first project README with English translation, verified highlights, real screenshots, technology summary, and reproducible setup steps.
---

# Project README Writer

## Core rule

Write for a person who has just opened the repository. Explain what the project solves,
what the person can do with it, and how to run it. Keep the README compact; prefer one
clear sentence and a useful screenshot over general praise. Never claim a feature,
metric, model, platform, or test result unless it is visible in the repository or was
actually verified in this task.

## Workflow

1. **Identify the project boundary.** Confirm the repository root and read its current
   README, manifests, entry points, deployment files, tests, and delivery notes. Use
   `rg --files` and targeted reads; do not scan or copy secret directories, credentials,
   tokens, private keys, production configuration, virtual environments, caches, or
   generated dependency trees.
2. **Map the real user path.** Find the simplest verified flow: double-click an EXE,
   install an APK, open a web page, run a local server, or execute a documented command.
   Record the exact prerequisites and the expected visible result. Separate source,
   build output, demo data, and optional artifacts.
3. **Select only real evidence.** Prefer an existing screenshot, GIF, diagram, or
   local page capture. Link images with repository-relative paths and check that each
   target exists. If no visual evidence exists, show a short input -> processing ->
   output flow instead of inventing a screenshot.
4. **Write the README.** Use the compact outline below. Put Chinese first and place
   the English translation immediately after each important paragraph or table row.
   Keep the main description to roughly 3-6 short sections; add detail only when it
   helps a user reproduce the project.
5. **Validate the artifact.** Check Markdown headings, links, image paths, code fences,
   bilingual parity, command accuracy, and secret hygiene. Re-read the result as a
   non-technical user: the first run should be obvious without knowing the source code.
6. **Respect change boundaries.** Edit only the requested README and explicitly scoped
   supporting screenshots/docs. Do not commit, push, publish, or change GitHub settings
   unless the user separately authorizes that action.

## Compact README outline

Use the applicable parts of this order:

1. **Title and one-line value proposition** - Chinese title first; English subtitle
   second. Add at most four relevant badges, never decorative badge spam.
2. **解决什么问题 / Problem** - one Chinese sentence, then one English sentence;
   name the user, input, and useful result.
3. **项目展示 / Demo** - one real screenshot or a four-step flow. Add a short caption
   explaining what the reader should notice.
4. **高光亮点 / Highlights** - three to five concrete differentiators. Include
   measurable results only when verified, and name the evidence source in a link or
   sentence.
5. **技术名词 / Tech** - list only technologies actually used, grouped in one compact
   line or table.
6. **从 ZIP 开始复现 / Reproduce from ZIP** - explain extraction, prerequisites,
   the shortest run command or launch action, and the expected result. For an EXE or
   APK, tell a non-developer exactly which file to open or install. For a source-only
   project, provide the verified install/build/run commands.
7. **范围与安全 / Scope and safety** - mention required external services, local-only
   behavior, model/data licensing, or known integration conditions when they affect use.
8. **交流 / Contact** - include only the contact line the user requested.

For Chinese-English tables, keep the Chinese and English meaning aligned; do not add an
English paragraph that claims more than the Chinese paragraph. Use relative links for
files inside the repository and never expose a secret value in a screenshot or example.

## Project-type adjustments

- **Desktop or web tool:** show the main screen and the shortest launch path.
- **Mobile or mini-program:** show the real screen/preview and state whether an APK,
  DevTools import, or a signed release is required.
- **AI/ML:** state the model, input/output, inference route, and verified test scope;
  distinguish training, inference, and demo-only assets.
- **Embedded/IoT:** show the device-to-service path and required hardware/firmware;
  do not imply hardware acceptance from a source build alone.
- **Library or educational project:** replace the screenshot with a minimal usage
  example and a small architecture or learning flow.

## Quality gates

Before handing off, confirm:

- The first screenful answers “what is it and why use it?”
- Every highlight is traceable to code, a test, a real screenshot, or a supplied artifact.
- No placeholder text, generic marketing claims, invented metrics, fake screenshots, or
  unverified commands remain.
- Internal links and image paths resolve from the repository root.
- The README explains the route from a downloaded ZIP to a visible result.
- The English translation is present wherever the user requested bilingual content.

For the reusable section order and examples, read
[`references/compact-template.md`](references/compact-template.md).
