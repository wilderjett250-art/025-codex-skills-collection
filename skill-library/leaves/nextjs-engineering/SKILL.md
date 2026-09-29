---
name: nextjs-engineering
description: Resolve Next.js App Router, Server Components, hydration, caching, revalidation and framework upgrade issues using version-matched documentation. Next.js缓存、服务端组件、水合、路由。Not generic React rendering.
---
# Next.js engineering
Read installed Next.js version, App/Pages Router, build configuration and existing project AGENTS.md. Prefer relevant files in node_modules/next/dist/docs or .next-docs when present; search by the exact API/problem and load only the matching page.
Check that bundled documents match the installed framework. If unavailable, consult official Next.js docs for that version. Do not generate project rules, run codemods, enable new cache behavior or upgrade dependencies merely to obtain documentation.
Trace server/client boundaries, serializable props, async request APIs and caching ownership against the actual version. For stale data establish which layer caches it and which mutation invalidates it. Keep authorization near protected data; client routing is not authorization.
Use react-engineering only when React-specific behavior is relevant. Verify the affected route with the project's build and runtime where needed; development success does not prove production caching.
Upstream migration source: https://github.com/vercel-labs/next-skills/blob/b76d687cf3e026eac3b1032f610f06b47a56377c/README.md
Old next-best-practices/next-upgrade skills are retired upstream; do not reinstall them as current guidance.
