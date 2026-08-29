# API and Service Acceptance

Model the reported effect as:

`request / event -> authentication and routing -> validation -> data or external operation -> response -> observable client or persisted result`

Validate the contract and the behavior that matters:

- successful response shape and status;
- validation and failure branch;
- state change, idempotency, rollback, or side effect where relevant;
- parity across mock/sandbox and production-like branches when both exist.

Do not call a route “fixed” because a handler returns 200 if the original request, authorization, response contract, or state transition was not exercised.
