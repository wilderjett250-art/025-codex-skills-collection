# Dark Mode & Theming

Source: vercel-labs/web-interface-guidelines @ e3d624baaf29dc1fc645aff3e38f03e564d2d6b1, command.md.
Apply only to the requested surface; preserve native semantics.

- `color-scheme: dark` on `<html>` for dark themes (fixes scrollbar, inputs)
- `<meta name="theme-color">` matches page background
- Native `<select>`: explicit `background-color` and `color` (Windows dark mode)
