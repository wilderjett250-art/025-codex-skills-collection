---
name: shadcn-ui
description: Add, compose or update shadcn/ui components using the project's actual aliases, theme and primitive library. shadcn组件、弹窗、表单、主题。Only when shadcn is used or requested.
---
# shadcn/ui components
Read components.json, package.json and actual installed component source first. Establish aliases, Tailwind version, icon library, primitive base (Radix or Base UI), local modifications and existing tokens. No dynamic command interpolation is assumed to run when this Skill loads.
Preserve existing components before adding new ones. Use the project's package runner and a compatible CLI; inspect help/version before relying on newer flags. For a new API or upstream update, consult matching official component docs.
Read only the necessary reference in references/upstream/shadcn/:
- rules/base-vs-radix.md for primitive composition/API differences.
- rules/forms.md for fields and validation.
- rules/composition.md for dialogs, menus and component composition.
- rules/styling.md or customization.md for tokens/themes.
- rules/chat.md only for chat components.
- cli.md for an actual CLI operation; registry.md for registry authoring.
Keep raw upstream SKILL.md as provenance, not an automatically injected instruction set. Its latest-CLI preference, preset flows and mandatory questions do not expand the user's request.
Before component updates inspect dry-run/diff where supported, back up modified source and merge user changes. A component request does not authorize replacing the project's theme or base library. Verify keyboard/focus, disabled/loading/error states and imports on the actual component.
