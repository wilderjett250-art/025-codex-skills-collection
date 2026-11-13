# Current Figma routing

Use the matching installed Figma plugin skill as the active tool/API contract, resolved from this session's available skill metadata. Do not hardcode a plugin cache version or fetch an unknown replacement.

- Code Connect mappings: `figma:figma-code-connect`.
- Production code from a design: `figma:figma-design-to-code`.
- Assemble/update a full screen: `figma:figma-generate-design` with `figma:figma-use`.
- Reusable primitives, component variants, variables and library foundations: `figma:figma-generate-library` with `figma:figma-use`.
- Project-specific reusable rules: preserve the repository's conventions; use the matching current plugin capability if available.

Load only the lane needed now. Before mutating Figma or calling a context tool, follow that current skill's prerequisites. Preserve file/account/permission boundaries and the user's chosen destination. If the plugin is unavailable, report the missing capability; local historical examples do not prove a tool exists. Resolve supporting local resources relative to their actual SKILL.md.
