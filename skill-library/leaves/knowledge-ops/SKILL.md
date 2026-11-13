---
name: knowledge-ops
description: "Retrieve, organize, or explicitly save knowledge with source provenance. Pure knowledge searches are read-only; conversation imports and synchronization require their own authorized scope."
metadata:
  origin: ECC
---

# Knowledge operations

Separate retrieval from capture. Search requests are read-only and do not authorize writing memories, importing conversations, synchronizing accounts, committing, or pushing.

## Retrieve
Use the connected knowledge source or documented local index relevant to the question. Return the source location, date and uncertainty. Do not scan conversation archives merely because a current source misses. Historical notes do not prove live state.

## Capture or organize an authorized source
1. Establish the content/source, destination and permitted scope from the user's request and current workspace rules. Historical conversation imports require their own source-path/scope authorization.
2. Inspect the existing schema/index and search for duplicates. Preserve provenance; distinguish user intent, independently verified results and unresolved claims.
3. Back up affected existing records/files before changes, write the smallest authorized update, then verify the destination and index.
4. Commit, push, cross-service transfer or scheduled synchronization only within explicit authorization for that destination and operation. Do not create periodic collection by default.

Use the current host's supported memory mechanism and tools. Never assume a Claude memory directory, MCP server or remote repo exists. Follow the session's `knowledge_capture` policy; secrets and raw transcripts are excluded from ordinary knowledge capture. A task-local evidence note is not permission to ingest that task into durable memory.
