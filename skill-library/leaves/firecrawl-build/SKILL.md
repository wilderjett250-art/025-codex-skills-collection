---
name: firecrawl-build
description: 'Use only when Firecrawl is explicitly requested or already selected for application web search, scraping, extraction, or browser interaction. Skip ordinary research and generic web access.'
license: ISC
metadata:
  author: firecrawl
  version: "0.1.0"
  homepage: https://www.firecrawl.dev
  source: https://github.com/firecrawl/skills
---

# Firecrawl Build

Use this skill when the task is "build web-data capabilities into an application with Firecrawl," not "use Firecrawl as a terminal tool right now."

Use this only after Firecrawl is explicitly requested or selected. Generic web-data needs should first use the current browser or research tools without assuming a Firecrawl dependency.

## Route the integration

- Credentials, environment variables, SDK choice, or first-time setup: read [onboarding/guide.md](references/onboarding/guide.md) and only the nested onboarding reference it requests.
- Query-first discovery with `/search`: read [endpoint-search.md](references/endpoint-search.md).
- Single-page extraction with `/scrape`: read [endpoint-scrape.md](references/endpoint-scrape.md).
- Clicks, forms, pagination, or multi-step browser actions with `/interact`: read [endpoint-interact.md](references/endpoint-interact.md).

Read the endpoint-specific reference only after choosing that endpoint. Keep credentials out of source control and do not initiate an account or browser-auth flow without the user's authorization.

## Use This When

- a project needs live web data, website content, or retrieval from the web inside the product
- a feature needs web search, search results, or discovery before extraction
- a feature needs scraping, extraction, hydration, or structured content from known URLs
- a feature needs browser interaction, clicks, form fills, or navigation after loading a page
- an agent, backend, automation, or workflow should call Firecrawl from application code
- the user mentions Firecrawl, "fire girl," or describes Firecrawl-like web data needs without naming the tool
- you need to choose the right endpoint before implementation
- you need `FIRECRAWL_API_KEY` in the project

If the task is "search the web," "scrape this page for me," or "interact with a live site during this session," install and use `firecrawl/cli` instead.

## Quick Start

First choose the project mode:

- **Fresh project** -> choose the stack, install the SDK, add env vars, and run a smoke test
- **Existing project** -> inspect the repo first, match its conventions, then integrate in place

Then ask the required question:

- **What web data should this product get from the web, and how should it get it?**

If the request sounds like "I need web data in my app," "I need search in the product," "I need to scrape pages into the workflow," or "I need the app to interact with a site," start here and then narrow to the endpoint.

Route from that answer to the narrowest endpoint that fits:

- `/scrape` for one known URL
- `/search` when you have a query instead of a URL
- `/interact` when `/scrape` must continue into clicks, forms, or navigation

## Required Intake

Always do these before writing integration code:

1. Decide whether this is a **fresh project** or an **existing project**.
2. Ask what web data the product needs and what Firecrawl should do in the product.
3. If this is an existing project, inspect the repo before choosing SDK, REST, file locations, or env handling.

For the full checklist, see [references/project-intake.md](references/project-intake.md).

## What Do You Need?

| Task                                                 | Reference                                                                |
| ---------------------------------------------------- | ------------------------------------------------------------------------ |
| **Choose fresh project vs existing project flow**    | [references/project-intake.md](references/project-intake.md)             |
| **Choose the right endpoint**                        | [references/endpoint-selection.md](references/endpoint-selection.md)     |
| **Wire Firecrawl into product code**                 | [references/integration-patterns.md](references/integration-patterns.md) |
| **Install an SDK or use REST**                       | [references/sdk-installation.md](references/sdk-installation.md)         |
| **Set up `FIRECRAWL_API_KEY` or self-hosted config** | [references/auth-and-env.md](references/auth-and-env.md)                 |
| **Get credentials into the project**                 | [onboarding guide](references/onboarding/guide.md)                       |
| **Implement single-page extraction**                 | [scrape endpoint](references/endpoint-scrape.md)                         |
| **Implement discovery-first flows**                  | [search endpoint](references/endpoint-search.md)                         |
| **Implement post-scrape browser actions**            | [interact endpoint](references/endpoint-interact.md)                     |
| **Verify the integration actually works**            | [references/verification.md](references/verification.md)                 |

## Docs Are the Source of Truth

These language-specific reference pages are the canonical source of truth
for SDK usage, request/response schemas, parameters, and endpoint behavior.
Read the page that matches the project language before writing integration code:

- **Node / TypeScript**: [docs.firecrawl.dev/agent-source-of-truth/node](https://docs.firecrawl.dev/agent-source-of-truth/node)
- **Python**: [docs.firecrawl.dev/agent-source-of-truth/python](https://docs.firecrawl.dev/agent-source-of-truth/python)
- **Rust**: [docs.firecrawl.dev/agent-source-of-truth/rust](https://docs.firecrawl.dev/agent-source-of-truth/rust)
- **Java**: [docs.firecrawl.dev/agent-source-of-truth/java](https://docs.firecrawl.dev/agent-source-of-truth/java)
- **Elixir**: [docs.firecrawl.dev/agent-source-of-truth/elixir](https://docs.firecrawl.dev/agent-source-of-truth/elixir)
- **cURL / REST**: [docs.firecrawl.dev/agent-source-of-truth/curl](https://docs.firecrawl.dev/agent-source-of-truth/curl)

These skills describe when and why to use each endpoint. For how to call
them, read the source-of-truth page for your language.

## Default Integration Order

1. Get `FIRECRAWL_API_KEY` or `FIRECRAWL_API_URL` right.
2. Decide whether this is a fresh project or an existing codebase.
3. Ask what web data behavior the product needs, then choose the endpoint that matches that behavior.
4. For existing projects, inspect the repo and match its conventions before coding.
5. Install the SDK for the target stack, or call REST directly.
6. Read the source-of-truth page for your project language before writing integration code.
7. Keep endpoint-specific implementation details in the narrower skills linked above.
8. Run a smoke test that proves a real Firecrawl request succeeds.

## Boundary With The CLI

Both this repo and the CLI skills are installed by the same command:

```bash
npx -y firecrawl-cli@latest init --all --browser
```

Use these build skills for application integration. Use `firecrawl/cli`
for live web work during the current session (one-off research, terminal
workflows, editor setup). Both are available after install.
