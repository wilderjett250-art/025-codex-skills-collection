# Hydration Safety

Source: vercel-labs/web-interface-guidelines @ e3d624baaf29dc1fc645aff3e38f03e564d2d6b1, command.md.
Apply only to the requested surface; preserve native semantics.

- Inputs with `value` need `onChange` (or use `defaultValue` for uncontrolled)
- Date/time rendering: guard against hydration mismatch (server vs client)
- `suppressHydrationWarning` only where truly needed
