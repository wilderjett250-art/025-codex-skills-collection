# Application performance diagnosis

Define the user-visible operation, current environment/build mode, realistic workload and correctness invariant. Separate browser wait/render, network, server work, database and external-service time; measure the suspected segment with available trusted tooling. If runtime access is absent, label static hypotheses and name the measurement needed.

- Frontend: waterfall, critical assets/bundle, long tasks, rendering and interaction responsiveness.
- Backend/data: query count/plan, round trips, CPU/I/O, locks, connection lifetime, queue delay and bounded concurrency.
- Whole journey: elapsed time plus relevant latency distribution, throughput, memory/error rate. A p95 needs an actual sample set and workload, not one request.

Test one causal hypothesis at a time. Prefer the smallest change on the measured critical path. Explain cache invalidation/freshness and concurrency tradeoffs before adding them; speed cannot come from skipped validation or lost work. Use the actual framework owner for implementation.

Repeat baseline and candidate with comparable inputs and conditions; disclose warm/cold caches, sample count and noise. Keep correctness, resource/cost limits and rollback alongside the performance result. Claims stop at the observed environment. Read-only diagnosis does not authorize writes, production load generation, billing changes or deployments. Use isolated/synthetic load and existing approval/recovery gates when implementing.
