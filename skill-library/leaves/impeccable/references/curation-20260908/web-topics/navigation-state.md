# Navigation & State

Source: vercel-labs/web-interface-guidelines @ e3d624baaf29dc1fc645aff3e38f03e564d2d6b1, command.md.
Apply only to the requested surface; preserve native semantics.

- URL reflects state—filters, tabs, pagination, expanded panels in query params
- Links use `<a>`/`<Link>` (Cmd/Ctrl+click, middle-click support)
- Deep-link all stateful UI (if uses `useState`, consider URL sync via nuqs or similar)
- Destructive actions need confirmation modal or undo window—never immediate
