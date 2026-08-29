---
name: photoshop-editing
description: 'Operate the local Windows Photoshop installation for scripted PSD or image creation, layer and text edits, opening, saving, batch export, and bridge validation.'
metadata:
  short-description: Automate local Photoshop on Windows
---

# Photoshop Editing

Use this skill for local Photoshop automation on the current machine.

## Environment

- Discover Photoshop from the Windows registry or the user's confirmed install location.
- Configure the Photoshop MCP or `photoshop-python-api` environment on this machine; do not reuse another operator's virtual environment path.
- Use a user-approved workspace with separate `input` and `output` folders.

## Preferred Route

1. Confirm Photoshop is installed and can launch.
2. For user requests that explicitly require Photoshop, use Photoshop MCP or `photoshop-python-api`; do not fall back to PIL/OpenCV unless the user approves.
3. Prefer direct `photoshop-python-api` scripts for precise local automation and export.
4. Use the MCP server for simple tool calls after verifying it starts in the current Codex session.
5. Keep generated files under the user-approved workspace.
6. For user images, never overwrite the source; export edited results to `output`.

## Commands

Run a smoke test:

```powershell
& '<PHOTOSHOP_MCP_PYTHON>' '<CODEX_HOME>\skill-library\leaves\photoshop-editing\scripts\photoshop_smoke.py'
```

Start the MCP server manually for diagnostics:

```powershell
& '<PHOTOSHOP_MCP_SERVER>' --help
```

## Notes

- Confirm the installed `photoshop-mcp-server` version and tool list on the current machine before relying on it.
- If an MCP tool call hangs, stop only the spawned `photoshop-mcp-server.exe` or related venv `python.exe` processes and fall back to direct `photoshop-python-api`.
- If Photoshop shows login, license, or modal dialogs, let the user clear them before retrying automation.
