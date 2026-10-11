# 常用产品与工程能力升级 · 2026-10-11

## 结果与边界

9 个常驻入口 + 291 个按需 Skill，总计 300。保留元数据检索 → 比较候选 → 读取当前阶段专家的二级路由，不加载整套角色包。新增 `code-quality-review`；复用并升级 `benchmark-optimization-loop`，没有重复安装另一套性能工具。

| 能力 | 本次改变 |
|---|---|
| 大型项目 | 依赖顺序、最高风险未知、跨层纵向切片、集成负责人和验收；不按文件数机械拆任务 |
| 产品经理视角 | 明确支持已有产品评估：价值、易用性、商业可行性、技术可行性；保留有效功能，区分事实/假设 |
| 审美 / UI | 区分新设计与现有精修；将“高级”落到信息层级、密度、字排和一致性，不靠额外装饰 |
| 架构 | 正常/失败请求链、模块耦合、真实变化热点、可观测性、迁移与回滚；反对为分层而分层 |
| 前后端效率 | 跨层测量 → 单个瓶颈假设 → 同条件对照；React 关注瀑布/包体，后端关注查询/往返/资源边界 |
| 代码审查 | 需求行为与可维护性双轴，文件/行/触发条件/影响/证据；抑制误报，审查不自动改代码或发 PR 评论 |
| 产品测试 | 需求 → 用户动作 → 可观察结果 → 目标环境/版本 → 证据；独立期望值，未实际执行的行为标为未验证 |

另补了澄清的停止条件：先从代码和材料找事实，只问影响当前决定的问题；可以执行当前范围后继续工作。无法通过聊天解决的未知用有边界的实证检查，不要求自称“95% 确信”。

## 开源方案中值得借鉴的内容

以下星数是 2026-10-11 GitHub API 查询的近似快照，不是效果排名；查看了对应原始文档。这里是本地重写的方法提炼，不代表安装了这些完整框架。

| 来源 | 当时星数约 | 借鉴 / 不直接照搬 |
|---|---:|---|
| [GitHub Spec Kit](https://github.com/github/spec-kit/blob/main/spec-driven.md) | 14.1 万 | 需求、技术决定、任务与验收可追踪；不采纳“规格天然消除实现差距”的保证，不强制每个改动写完整规格 |
| [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/README.md) | 5.4 万 | 按工作规模选择规划深度，产品/架构/UX/测试各有边界；不默认开启全部角色或流程 |
| [GSD](https://github.com/gsd-build/get-shit-done/blob/main/docs/workflow-discuss-mode.md) | 6.4 万 | 从代码提取带证据的假设，按阶段保留决策；查询时仓库已归档，仅作为方法参考 |
| [PM Skills](https://github.com/phuryn/pm-skills/blob/main/pm-product-discovery/skills/identify-assumptions-existing/SKILL.md) | 2.7 万 | 价值、易用性、商业可行性和技术可行性的风险检查；不伪造调研或评分 |
| [Impeccable](https://github.com/pbakaus/impeccable/blob/main/README.md) | 7.9 万 | 区分产品事实与表面视觉方向，针对性 critique/audit/polish；不自动开 Hook、装扩展或采用一刀切审美禁令 |
| [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills/blob/main/skills/react-best-practices/SKILL.md) | 3.2 万 | 先检查请求瀑布和包体等高影响路径；只读当前相关规则，遵守实际 React 版本 |
| [Matt Pocock Skills](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md) | 28.5 万 | 需求与代码规范双轴审查；[行为测试](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md)避免实现耦合与自证断言；独立代理和逐次确认不作为普遍前提 |
| [Anthropic Code Review](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-review/commands/code-review.md) | 3.8 万 | 回查上下文、压制误报、给出代码证据；不照搬固定多模型并发、数字置信度或自动发评论 |

[OpenAI Skill 说明](https://developers.openai.com/plugins/concepts/skills)区分可复用方法与工具访问；[Skill 评估指南](https://developers.openai.com/blog/eval-skills)强调观察行为。本库因此保留渐进加载，并把检索测试与真实模型/产品验收分开。

## MCP 与全局规则

全局规则仅新增一条当前需求/阶段选择提醒；具体方法放在按需 Skill 或条件引用中。本次不修改账号授权、MCP 开关或权限策略，不为了提高计数调用无关工具。

当前任务工具清单可发现 Figma 与 GitHub 类工具，未发现本机 external-browser 工具入口。这是工具暴露观察，不是账户授权、服务连通或浏览器故障诊断。设计任务使用匹配的设计工具；本地源码与测试优先可靠 CLI；真实用户流程要在指定会话/版本实际验证。MCP 配置为 enabled 不等于本任务已可调用。

## 验证与未验证项

- 本机 21 条针对性检索回归：修改前预期入口命中 13/21，修改后 21/21；最多三个候选，路径均可解析。[修改前](evals/capability-routing-before.json)、[修改后](evals/capability-routing-after.json)。
- 六条边界用例检查首位候选：游戏、Vue、React、源码学习、简历和 RAW；通过。保留原有 34 条检索用例和 lexical 路由回归。
- 原有检索回归 86 项、lexical 路由回归 98 项、加载/Hook 单元测试 4 项均通过；11 个新改入口通过 Skill 结构校验。隔离安装得到 9 + 291 个入口，全局规则/Hook 安装及 21 条用例通过；没有变更真实 MCP 授权或开关。
- 固定 Impeccable 的既有分类，避免描述调整导致 canonical 路径漂移；基准优化入口明确归到应用性能测量分类，其余既有入口保留原 canonical 路径。
- Skill 文件结构检查不证明工作方法有效；检索改善不等于真实模型在每次请求中都会自动选中。这里不是盲测，没有伪称独立代理评估。
- 具体项目的审美、性能、架构和验收改善仍需要对应真实材料、运行环境和行为证据。后续更新以实际失败/结果为依据，而不是不断堆全局规则。

复验命令（先安装到隔离或已授权的目标目录）：

```bash
node <codex-home>/skill-library/scripts/capability-routing.test.mjs
node <codex-home>/skill-library/scripts/search-skills.test.mjs
node <codex-home>/skill-library/scripts/route-task.test.mjs
node --test <codex-home>/skill-library/scripts/activity.test.mjs
```
