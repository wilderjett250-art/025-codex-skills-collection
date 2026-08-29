@echo off
setlocal
chcp 65001 >nul
title Codex Skills + MCP Toolkit Installer
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install.ps1" -Profile full %*
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if not "%EXIT_CODE%"=="0" echo Installation did not complete. Review the error above.
pause
exit /b %EXIT_CODE%
