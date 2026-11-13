---
name: data-scraper-agent
description: Use to build a scheduled public-data collection agent that scrapes, enriches, stores, and tracks sources such as jobs, prices, news, GitHub, or sports.
metadata:
  origin: community
---

# Public-data collection workflow

Build or repair a source-backed collection process with the user's selected stack and destination. Collection, enrichment, storage and scheduling are separate components; simple deterministic extraction does not require an LLM.

1. Establish sources, fields/schema, deduplication key, update cadence, output destination and completion evidence. Reuse an existing project/config before choosing new infrastructure.
2. Prefer an official structured API or deterministic parser when suitable. For rendered pages, reuse the authorized browser route. Preserve source URLs/timestamps, errors and unsupported fields instead of inventing data.
3. Make throttling, retries/backoff, timeouts and quotas explicit configuration. Obey source/account limits. Validate duplicates and incremental updates on isolated fixtures before a real scheduled run.
4. If AI enrichment is actually requested and useful, use the user's authorized OpenAI runtime/provider. Resolve the exact current model/API through official documentation. Model ids, fallback chains, prices, RPM and budgets belong in configuration, not universal free-tier claims. Do not call another provider or create an API key merely to follow an old example.
5. Store only the authorized fields and verify rows against the source. Keep source manifests and a focused failure report; do not log credentials or export authenticated browser storage.
6. Set up recurring execution only if requested and through the supported scheduler for this host. A one-time collection does not authorize continuous scraping, cloud provisioning or publishing. Prove the requested one-shot/result and schedule separately.

The pre-change Gemini 2.0/free-quota recipe is preserved in the recovery set as historical source, not an executable default. Google listed `gemini-2.0-flash` and `gemini-2.0-flash-lite` as shut down on 2026-06-01: https://aistudio.google.com/docs/deprecations . Do not generate a new integration around those retired models.
