# Locale & i18n

Source: vercel-labs/web-interface-guidelines @ e3d624baaf29dc1fc645aff3e38f03e564d2d6b1, command.md.
Apply only to the requested surface; preserve native semantics.

- Dates/times: use `Intl.DateTimeFormat` not hardcoded formats
- Numbers/currency: use `Intl.NumberFormat` not hardcoded formats
- Detect language via `Accept-Language` / `navigator.languages`, not IP
- Brand names, code tokens, identifiers: wrap with `translate="no"` to prevent garbled auto-translation
