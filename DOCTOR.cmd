@echo off
setlocal
chcp 65001 >nul
title Codex Skills + MCP Toolkit Doctor
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\doctor.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
pause
exit /b %EXIT_CODE%
