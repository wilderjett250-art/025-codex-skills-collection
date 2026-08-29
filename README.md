# 025 Codex 技能与 MCP 工具箱 / Codex Skills + MCP Toolkit

> 这是一套可一键安装的 Codex Skill、MCP 配置和按需能力路由工具。

## 项目内容

- 9 个常驻 Skill 负责项目分类、任务路由、工具使用、交接和验收。
- 277 个按需 Skill 保存在冷库中，并由路由器根据任务选择。
- 31 个 MCP 条目按照开发、研究、设计、视频和工程场景分组。
- 25 个插件预设用于恢复对应的官方能力来源。
- Windows 和 macOS 安装器会备份同名配置并完成安装。

## Windows 安装

Windows 用户解压项目后双击 `INSTALL.cmd`。

安装完成后，用户完全退出 Codex 并重新打开，然后双击 `DOCTOR.cmd` 检查结果。

PowerShell 提供相同的安装方式。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Profile full
```

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

`filesystem` MCP 通过参数接收允许访问的工作目录。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Profile development -FilesystemRoot I:\workspace
```

## 更新

用户拉取仓库更新后重新运行安装器即可同步 Skill、MCP 和插件预设。

安装器会在覆盖同名内容前创建备份。

## 项目结构

- `skills/` 保存 9 个常驻 Skill。
- `skill-library/` 保存 277 个按需 Skill、目录和路由脚本。
- `mcp/` 保存 MCP Catalog 和 Profile。
- `presets/` 保存插件来源预设。
- `scripts/` 保存安装、诊断和路由脚本。
- `.codex-plugin/` 保存 Codex Plugin 清单。

## 安全与许可

安装器通过环境变量和本机配置接收服务凭据。

第三方能力继续使用各自的许可证和署名，来源记录位于 `THIRD_PARTY_NOTICES.md`。

本项目根目录代码使用 MIT License。
