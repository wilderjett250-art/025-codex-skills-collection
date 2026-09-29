---
name: vue-engineering
description: Implement or debug Vue 3 components, reactivity, Pinia state, Vue Router and Vue component tests. Vue开发、状态不更新、路由守卫、组件测试。Not React or visual direction.
---
# Vue engineering
Inspect package versions, existing SFC conventions and the user's target behavior. Preserve Options API, JavaScript, state libraries and component organization already in use; do not migrate the stack merely to match examples.
Read only the relevant pinned reference under references/upstream/:
- Reactive values and watchers: vue-best-practices/references/reactivity.md.
- SFC/template behavior: vue-best-practices/references/sfc.md.
- Props/emits: vue-best-practices/references/component-data-flow.md.
- Composable lifecycle: vue-best-practices/references/composables.md.
- Pinia problems: the short index vue-pinia-best-practices/SKILL.md, then its matching rule.
- Router guards/params: vue-router-best-practices/SKILL.md, then the matching rule.
- Component tests: vue-testing-best-practices/SKILL.md, then the matching rule.
For other Vue behavior, list reference filenames and select by the observed problem. Do not preload the original vue-best-practices entry or all four foundation documents.
Upstream mandatory component counts, SFC order and blanket reading requirements are examples, not local mandates. Split components when ownership/reuse warrants it. Validate the user's original action, including state after navigation or asynchronous updates; use the existing test runner.
