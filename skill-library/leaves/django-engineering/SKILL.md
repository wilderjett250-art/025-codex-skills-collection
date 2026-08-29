---
name: django-engineering
description: 'Design, implement, test, secure, migrate, or release Django and DRF systems. Load only the reference for the current concern; use generic Python guidance for non-Django work.'
---

# Django engineering

Route the task to the smallest relevant reference:

- Architecture, DRF, ORM, caching, signals, or middleware: read [architecture.md](references/architecture.md).
- Authentication, authorization, CSRF, XSS, injection, secrets, or secure deployment: read [security.md](references/security.md).
- pytest-django, factories, mocking, API tests, TDD, or coverage: read [testing.md](references/testing.md).
- Migrations, linting, test gates, security scans, or release readiness: read [verification.md](references/verification.md).

Read more than one reference only when the task genuinely spans those concerns. Follow the repository's pinned Django and dependency versions over examples in the references, and verify current APIs when version drift matters.
