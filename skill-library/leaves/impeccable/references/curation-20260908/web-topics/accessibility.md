# Accessibility

Source: vercel-labs/web-interface-guidelines @ e3d624baaf29dc1fc645aff3e38f03e564d2d6b1, command.md.
Apply only to the requested surface; preserve native semantics.

- Icon-only buttons need `aria-label`
- Form controls need `<label>` or `aria-label`
- Interactive elements need keyboard handlers (`onKeyDown`/`onKeyUp`)
- `<button>` for actions, `<a>`/`<Link>` for navigation (not `<div onClick>`)
- Images need `alt` (or `alt=""` if decorative)
- Decorative icons need `aria-hidden="true"`
- Async updates (toasts, validation) need `aria-live="polite"`
- Use semantic HTML (`<button>`, `<a>`, `<label>`, `<table>`) before ARIA
- Headings hierarchical `<h1>`–`<h6>`; include skip link for main content
- `scroll-margin-top` on heading anchors
- Meaningful media needs captions, transcripts, or descriptions as applicable
- Media controls need keyboard support; decorative media needs assistive-tech hiding
