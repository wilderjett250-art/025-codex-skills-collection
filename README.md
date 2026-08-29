# Codex Skills + MCP Toolkit

这不是把几百个提示词全部塞进 Codex，而是一套可迁移的“能力层 + 路由层 + 工具层”。它复刻当前工作方式，同时避免把知识库、聊天记录、登录状态、密钥和机器路径带给其他人。

## 一键安装（Windows）

1. 登录有权访问本私有仓库的 GitHub 账号，下载 ZIP 或克隆仓库。
2. 解压后双击 `INSTALL.cmd`。
3. 安装结束后完全退出 Codex，重新打开并新建一个任务。
4. 双击 `DOCTOR.cmd` 检查结果。

安装器会先备份同名 Skill、Skill Library 和 `config.toml`，再执行以下操作：

- 安装 9 个常驻核心 Skill；
- 安装 277 个按需 Skill 到冷库，由路由器按任务选择；
- 写入 25 个官方/插件 Skill 来源预设；
- 从 31 个非知识库 MCP 中自动注册可移植项，并列出需要本机软件、登录、密钥或路径的项目；
- 不复制任何 token、cookie、密码、个人知识、浏览器资料或本机绝对路径。

默认运行 `full` Profile。这里的“full”表示完整盘点并尽可能安装：能安全自动注册的直接注册，必须绑定本机环境的 MCP 会显示为“待本机配置”，不会伪造成功。

## 能力结构

| 层 | 数量 | 位置 | 加载方式 |
|---|---:|---|---|
| 常驻核心 Skill | 9 | `skills/` | Codex 根据任务触发 |
| 按需 Skill 冷库 | 277 | `skill-library/leaves/` | `skill-library-router` 只加载命中的 Skill |
| 插件 Skill 来源预设 | 25 | `presets/plugins.json` | Codex 官方市场/运行时恢复 |
| MCP Catalog | 31 | `mcp/catalog.json` | 按 Profile 注册；本机型 MCP 延迟配置 |

Codex 自带的系统 Skill 不复制进仓库，因为它们随 Codex 版本提供；复制旧系统 Skill 反而会造成冲突。第三方插件的 Skill 也优先从原始插件恢复，而不是把插件缓存当源码提交。

## MCP Profiles

双击 `INSTALL.cmd` 使用完整 Profile。也可以在 PowerShell 中选择更轻的分组：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Profile recommended
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Profile development -FilesystemRoot I:\workspace
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Profile design
```

可用 Profile：`recommended`、`development`、`research`、`design`、`video`、`engineering`、`full`。

`filesystem` MCP 必须显式传入 `-FilesystemRoot`，安装器不会默认暴露整个用户目录。Photoshop、DaVinci Resolve、AutoCAD、Figma 本地桥、外部浏览器、百度网盘等 MCP 需要朋友电脑上的应用或授权，因此只提供无密钥模板和诊断说明。

## 为什么上下文不会被撑爆

- 常驻层只保留少量控制和验收 Skill。
- 277 个领域 Skill 放在冷库，路由命中后才读取一个具体入口。
- MCP 按分组安装，依赖重型桌面软件的服务不会被安装器强行常驻。
- 项目规则仍应放进项目自己的 `AGENTS.md`，不要继续扩大全局提示词。

## 更新

仓库更新后重新运行 `INSTALL.cmd` 即可。同名内容会先备份再覆盖；已有 MCP 默认保留，传入 `-Force` 才会按当前 Profile 重建：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Profile full -Force
```

## 安全边界

- 仓库不包含知识库、Memory、历史对话、项目源码或部署记录。
- 仓库不包含 `.env`、token、cookie、私钥、浏览器 Profile 或账号授权 URL。
- HTTP MCP 只保存公共服务地址和环境变量名称；密钥由每位使用者自己设置。
- 桌面控制类 MCP 不自动开启，必须由使用者在自己的机器上完成依赖和授权。
- `local-experience` 只提供空白模板，不带操作者的真实经验手册。
- 聚合 Skill 的原始许可和署名继续有效；详见 `THIRD_PARTY_NOTICES.md`。在完成逐项来源审计前，不应把本仓库改成公开仓库。

## 开发与贡献

根目录本身也是一个经过校验的 Codex Plugin，清单位于 `.codex-plugin/plugin.json`。贡献前请先运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\doctor.ps1
```

更多贡献约束见 `CONTRIBUTING.md`。
