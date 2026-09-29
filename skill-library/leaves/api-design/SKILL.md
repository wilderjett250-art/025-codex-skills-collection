---
name: api-design
description: Design or review REST API contracts, pagination, error semantics, authorization boundaries and backwards compatibility. API接口设计、分页、错误码、接口契约。Not framework implementation tutorials.
metadata:
  origin: ECC
---
# API contracts
Inspect existing consumers and conventions before changing routes, envelopes or status codes. Record request/response fields, validation, authorization and observable failure behavior for the affected operation.
Choose stable pagination ordering with a unique tie-breaker; define cursor/filter consistency and realistic limits. Check tenant/resource ownership on the server. Mutations need deliberate retry/idempotency and conflict behavior, with transaction scope matching the business invariant.
Keep existing versioning and compatibility promises. Example quotas, two-version limits, six-month retirement timelines and universal envelope rules are not requirements.
For concrete syntax, read only the matching section under references/curation-20260908/ (resource-design, http-methods-and-status-codes, response-format, pagination, filtering-sorting-and-search, authentication-and-authorization, rate-limiting, versioning, implementation-patterns). These preserved examples require adaptation to the project's actual API.
Verify contract behavior and relevant consumers, including validation, denied access, empty results and retries when applicable. A schema that parses does not prove runtime compatibility.
