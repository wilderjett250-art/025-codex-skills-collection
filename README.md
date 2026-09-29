# 025 Codex 技能与 MCP 工具箱 / Codex Skills + MCP Toolkit

> 这是一套可一键安装的 Codex Skill、MCP 配置和按需能力路由工具。

## 项目内容

- 9 个常驻 Skill 提供精确入口；290 个按需 Skill 保存在冷库中。
- 元数据检索最多返回 3 个候选，只在选定后读取完整 Skill；本地读取器可记录元数据级的加载次数。
- 31 个可移植 MCP 条目按照开发、研究、设计、视频和工程场景分组。
- 25 个插件预设用于恢复对应的官方能力来源。
- Windows 和 macOS 安装器会备份同名配置并完成安装。

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

用户拉取仓库更新后重新运行安装器可同步仓库中的 Skill、MCP 候选和插件预设，但安装器会保留已有同名 MCP 与用户自定义设置；它不会把本机私有服务自动发布到仓库，也不会覆盖全局 `AGENTS.md` 或 `hooks.json`。

安装器会在覆盖同名内容前创建备份。大容量 Skill 库请先确认目标盘有足够的备份空间。

## 按需检索与本地计数

安装后用任务文字检索，再按精确名称读取选中的 Skill：

```bash
node <codex-home>/skill-library/scripts/find-skills.mjs --query "DaVinci Resolve 视频调色" --limit 3
node <codex-home>/skill-library/scripts/read-skill.mjs davinci-resolve-color
```

`<codex-home>` 是实际 Codex 配置目录（通常为 `~/.codex`，可由 `CODEX_HOME` 覆盖）。本地事件默认写入 `<codex-home>/skill-activity`，可用 `SKILL_ACTIVITY_DIR` 改到批准的数据盘。`node <codex-home>/skill-library/scripts/activity-report.mjs --days 7` 只统计读取器观察到的 Skill 加载；MCP 调用还需要用户自行信任并配置 `PostToolUse` Hook。这不是 Codex 内置活动页，也不能证明模型在每次真实请求中都会自动选中 Skill。

## 项目结构

- `skills/` 保存 9 个常驻 Skill。
- `skill-library/` 保存 290 个按需 Skill、目录和路由脚本。
- `mcp/` 保存 MCP Catalog 和 Profile。
- `presets/` 保存插件来源预设。
- `scripts/` 保存安装、诊断和路由脚本。
- `.codex-plugin/` 保存 Codex Plugin 清单。

## 安全与许可

安装器通过环境变量和本机配置接收服务凭据。

第三方能力继续使用各自的许可证和署名，来源记录位于 `THIRD_PARTY_NOTICES.md` 和 `skill-library/sources-lock.json`。

本项目根目录代码使用 MIT License。
