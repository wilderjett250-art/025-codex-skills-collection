---
name: react-engineering
description: Implement React/Next.js components, state and server/client boundaries; diagnose render performance or component API problems. React开发、请求瀑布、重复渲染、组件组合。Not Vue or visual art direction.
---
# React engineering
Read the repository's actual React/Next/router versions and component conventions first. Select only the relevant branch:
- Ordinary components, hooks, errors, forms, fetching or state: [patterns](references/patterns.md).
- Performance: inspect the relevant rule under references/vercel/react-best-practices/rules/ (async-, bundle-, server-, client-, rerender- or rendering-). Start with an observed waterfall, bundle or render problem; measure the affected behavior.
- Boolean-prop proliferation or component composition: inspect matching architecture-, state- or patterns- files under references/vercel/composition-patterns/rules/.
- Component/hook tests: [testing](references/testing.md).
- Existing ECC examples only when needed: [additional patterns](references/additional-patterns.md).
The Vercel modules are pinned upstream references, not additional always-loaded Skills. Their root AGENTS.md files compile all rules; do not preload them. React 19-specific rules do not apply to earlier versions.
Keep the established stack and public component behavior. Do not add memoization, providers, libraries or abstractions without a concrete benefit. Keep visual direction with the chosen UI owner.
