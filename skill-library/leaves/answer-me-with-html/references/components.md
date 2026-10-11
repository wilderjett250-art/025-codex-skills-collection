# Minimal component syntax

Frontmatter is optional. Use `title:`, `lang: zh` and `template: sheet` for an overview or `template: doc` for sequential reading. `##` headings become panels; use only panels that materially help. Ordinary Markdown tables need no custom syntax.

````markdown
---
title: Example request path
lang: en
---
The service checks the request before writing a result.

## Request flow
```flow
Client -> API: request
API -> Database: validated write
Database --> API: result
API --> Client: response
```

## Responsibilities
| Part | Owns |
|---|---|
| Client | User action |
| API | Validation |
| Database | Durable state |
````

The default flow direction is top-to-bottom. Use `flow LR` for a genuinely wide layout; keep edge labels short and verify narrow-screen behavior.

Other components, only when relevant:

- `sequence`: `A -> B: message`, `B --> A: response`; use for actors over time.
- `tree`: indentation expresses hierarchy; `label | explanation` is optional.
- `timeline`: `time | title | detail`; facts need real dates or an illustrative label.
- `limits`: `label | 13 / 20 | unit`; requires verified numbers.
- `callout warn Title`: a conclusion or meaningful caveat, not decoration.

Run `node <skill-dir>/scripts/am.mjs help <component>` for richer syntax; do not read the entire bundle into model context. The safe wrapper excludes raw HTML/SVG fences, Markdown images and code-source/file embedding. For literal markup examples use escaped text, not executable blocks. Do not launch `serve`, run updates or generate a video merely because the CLI supports them.
