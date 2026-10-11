# 025 Codex 技能与 MCP 工具箱 / Codex Skills + MCP Toolkit

> 这是一套可一键安装的 Codex Skill、MCP 配置和按需能力路由工具。

## 项目内容

- 9 个常驻 Skill 提供精确入口；292 个按需 Skill 保存在冷库中。
- 元数据检索最多返回 3 个候选，只在选定后读取完整 Skill；本地读取器可记录元数据级的加载次数。
- 33 个非知识库 MCP 条目按照开发、研究、设计、视频和工程场景分组；另附本机启停状态的无凭证快照。
- 25 个插件预设用于恢复对应的官方能力来源。
- Windows 和 macOS 安装器会备份同名配置并完成安装。
- `presets/global/` 提供最新全局规则、无凭证 Codex 设置和元数据统计 Hook 模板。

## Windows 安装

Windows 用户解压项目后双击 `INSTALL.cmd`。

安装完成后，用户完全退出 Codex 并重新打开，然后双击 `DOCTOR.cmd` 检查结果。

PowerShell 提供相同的安装方式。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Profile full
```

Windows PowerShell 5.1 和 PowerShell 7 均可重建 Skill 目录。已有安装中的旧常驻 Skill 不会被安装器擅自删除；从旧版升级时应运行诊断并检查重复入口。

## macOS 安装

macOS 用户解压项目后双击 `INSTALL.command`。

安装完成后，用户完全退出 Codex 并重新打开，然后双击 `DOCTOR.command` 检查结果。

终端提供相同的安装方式。

```bash
bash ./scripts/install.sh --profile full
```

## MCP 分组

安装器提供 `recommended`、`development`、`research`、`design`、`video`、`engineering` 和 `full` 七种 Profile。

`full` Profile 会安装全部可自动配置的内容，并列出需要本机软件、账号授权、密钥或路径的条目。

Catalog 是安装候选，不代表这些 MCP 已在当前 Codex 会话中启用或连通。机器专用桥接、私有知识库和插件自带工具应留在本机配置，不上传 `config.toml`。真实工具调用才是可用性证据。

`filesystem` MCP 通过参数接收允许访问的工作目录。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Profile development -FilesystemRoot I:\workspace
```

## 更新

用户拉取仓库更新后重新运行安装器可同步仓库中的 Skill、MCP 候选和插件预设，但安装器会保留已有同名 MCP 与用户自定义设置。全局规则和 Hook 通过下面的独立命令按需安装。

安装器会在覆盖同名内容前创建备份。大容量 Skill 库请先确认目标盘有足够的备份空间。

### 全局规则与设置

本机 2026-10-11 的全局规则保存在 `presets/global/AGENTS.md`；机器用户名路径已改为 `<codex-home>`，安装时按目标电脑展开。规则内容保留当前版本，包括按需 Skill 路由、权限、备份、证据验证和知识采集开关。

先安装 Skill Library，再选择安装全局规则与统计 Hook：

```bash
node scripts/install-global.mjs --rules --hook
# 指定独立安装目录时：
node scripts/install-global.mjs --target <codex-home> --rules --hook
```

该命令先校验备份再覆盖 `AGENTS.md`，并将统计 Hook 合并到已有 `hooks.json`，保留其他 Hook。`presets/global/config.defaults.toml` 是本机模型、推理、权限、功能开关、Windows 和桌面偏好的无凭证参考，需手动审核合并；其中模型、权限和沙箱设置不应自动套用到别人的电脑。`settings-scope.json` 说明已导出和需要目标电脑重新配置的项目；项目信任路径、通知程序、私有环境值和 Hook 信任哈希不跨机器复制。安装 Hook 后按 Codex 当前界面完成信任/重载；模板存在不代表实际调用已计数。配置入口参见 [Codex 官方配置文档](https://learn.chatgpt.com/docs/config-file/config-basic)。

`mcp/local-state.json` 记录 33 个非知识库 MCP 的启停状态、环境变量名称和无凭证连接信息，包含启用的百度网盘两个条目。它是配置快照，不会强制改变接收电脑的服务开关，也不证明账号授权或连接可用。

维护者在已审查且有 Git 恢复点的工作副本中，可重新导出当前个人 Skill 和设置：

```bash
python scripts/export-local.py --home <codex-home> --canonical-root <canonical-skills-root> --date YYYY-MM-DD
```

导出后仍需审核差异、检查凭证和私有信息、重建目录并验证。导出器不是自动发布工具。`presets/sync-manifest.json` 记录本次同步范围和便携适配；本机软件路径、活动目录和经验手册入口保留参数化版本。

## 按需检索与本地计数

安装后用任务文字检索，再按精确名称读取选中的 Skill：

```bash
node <codex-home>/skill-library/scripts/find-skills.mjs --query "DaVinci Resolve 视频调色" --limit 3
node <codex-home>/skill-library/scripts/read-skill.mjs davinci-resolve-color
```

`<codex-home>` 是实际 Codex 配置目录（通常为 `~/.codex`，可由 `CODEX_HOME` 覆盖）。本地事件默认写入 `<codex-home>/skill-activity`，可用 `SKILL_ACTIVITY_DIR` 改到批准的数据盘。`node <codex-home>/skill-library/scripts/activity-report.mjs --days 7` 只统计读取器观察到的 Skill 加载；MCP 调用还需要用户自行信任并配置 `PostToolUse` Hook。这不是 Codex 内置活动页，也不能证明模型在每次真实请求中都会自动选中 Skill。

## 项目结构

- `skills/` 保存 9 个常驻 Skill。
- `skill-library/` 保存 292 个按需 Skill、目录和路由脚本。
- `mcp/` 保存 MCP Catalog 和 Profile。
- `presets/` 保存插件来源预设。
- `presets/global/` 保存全局规则、无凭证设置及统计 Hook 模板。
- `scripts/` 保存安装、诊断和路由脚本。
- `.codex-plugin/` 保存 Codex Plugin 清单。

## 常用产品与工程能力

保留二级路由：先匹配已有入口；缺少专门能力时检索元数据，比较最多三个候选，再加载当前阶段的一个 owner。直接描述任务即可，不要求记住 Skill 名称，也不预加载整套产品开发流程。

| 任务 | 按需入口 |
|---|---|
| 大项目、遗留系统、里程碑和协作 | `large-project-ops` |
| 产品经理视角、用户价值、需求取舍 | `product-discovery` |
| 新 UI / 现有界面审美和打磨 | `frontend-design` / `impeccable` |
| 技术方案、模块边界、架构合理性 | `architecture-decisions` |
| 跨前后端性能瓶颈和实测优化 | `benchmark-optimization-loop`，已知原因用对应框架 Skill |
| 代码质量、需求一致性、可维护性 | `code-quality-review` |
| 产品标准、测试策略、验收证据 | `qa-methodology`，实际 web 流程用 `e2e-testing` |

通用代码质量审查强化现有产品/工程能力；全局规则保留阶段选择提醒和按需加载。MCP 负责访问设计、代码平台和真实运行环境，不替代领域 Skill，也不默认全部启用。七类能力借鉴与验证范围见[升级说明](presets/capability-upgrade-20261011.md)。

## 上下文成本与图文说明

```bash
node <codex-home>/skill-library/scripts/audit-context-cost.mjs --home <codex-home> --limit 10
```

该命令只输出入口体积、引用和目录链接元数据，不导出 Skill 正文、聊天或配置秘密；体积不是质量评分或真实 token 账单。需要更细的完整审计时才使用 `--rows`。大型 Windows 测试入口已拆为短入口和条件参考，原指南可按记录重组。

`answer-me-with-html` 按需把短 Markdown 转为离线图文说明页，使用固定版本的本地渲染器；不默认打开浏览器、检查更新或把每次回答都变成网页。Windows-MCP 的 UIA 优先/局部快照方法已借鉴到操作与测试 Skill，本仓库没有因此安装或启用 Windows-MCP 服务。测量方法、限制和规则保留清单见[本轮审计](presets/context-efficiency-20261011.md)。

## 安全与许可

安装器通过环境变量和本机配置接收服务凭据。

仓库不包含个人知识库、经验手册正文、聊天归档、账号凭证、登录会话、应用程序、虚拟环境或插件缓存。`memory` 是通用 MCP 安装条目，知识管理类 Skill 也只是操作说明；`personal_knowledge` 私有服务未导出。MCP 手动条目需要目标电脑自行安装软件/桥接并配置授权。

第三方能力继续使用各自的许可证和署名，来源记录位于 `THIRD_PARTY_NOTICES.md` 和 `skill-library/sources-lock.json`。

本项目根目录代码使用 MIT License。
