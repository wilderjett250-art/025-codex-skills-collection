[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'
$repoRoot = Split-Path -Parent $PSScriptRoot
$codexHome = if ($env:CODEX_HOME) { [System.IO.Path]::GetFullPath($env:CODEX_HOME) } else { Join-Path $env:USERPROFILE '.codex' }
$skillsTarget = Join-Path $codexHome 'skills'
$libraryTarget = Join-Path $codexHome 'skill-library\leaves'
$catalogRaw = Get-Content -LiteralPath (Join-Path $repoRoot 'mcp\catalog.json') -Raw | ConvertFrom-Json
$catalog = @($catalogRaw.GetEnumerator())

Write-Host 'Codex Skills + MCP Toolkit Doctor' -ForegroundColor Cyan
Write-Host "Codex home: $codexHome"

$codexCommand = Get-Command codex -ErrorAction SilentlyContinue
$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
$npxCommand = Get-Command npx -ErrorAction SilentlyContinue
$pwshCommand = Get-Command pwsh.exe -ErrorAction SilentlyContinue
Write-Host ("Codex CLI: " + $(if ($codexCommand) { (& codex --version) } else { 'MISSING' }))
Write-Host ("Node.js: " + $(if ($nodeCommand) { (& node --version) } else { 'MISSING' }))
Write-Host ("npx: " + $(if ($npxCommand) { 'ready' } else { 'MISSING' }))
Write-Host ("PowerShell 7: " + $(if ($pwshCommand) { 'ready' } else { 'MISSING' }))

$activeCount = if (Test-Path -LiteralPath $skillsTarget) { (Get-ChildItem -LiteralPath $skillsTarget -Directory | Where-Object Name -ne '.system').Count } else { 0 }
$coldCount = if (Test-Path -LiteralPath $libraryTarget) { (Get-ChildItem -LiteralPath $libraryTarget -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') }).Count } else { 0 }
Write-Host "Active custom skills: $activeCount"
Write-Host "On-demand library skills: $coldCount"

if ($codexCommand) {
    $configured = @()
    $raw = & codex mcp list --json 2>$null
    if ($LASTEXITCODE -eq 0 -and $raw) {
        $parsed = $raw | ConvertFrom-Json
        if ($parsed -is [array]) {
            $configured = @($parsed | ForEach-Object { $_.name })
        } else {
            $configured = @($parsed.PSObject.Properties.Name)
        }
    }
    Write-Host "Configured MCP servers: $($configured.Count)"
}

$requiredEnv = @('GITHUB_PAT', 'FIRECRAWL_API_KEY')
foreach ($name in $requiredEnv) {
    $present = -not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name, 'Process')) -or
               -not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name, 'User')) -or
               -not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name, 'Machine'))
    Write-Host ("Environment {0}: {1}" -f $name, $(if ($present) { 'present' } else { 'not set (only required when used)' }))
}

Write-Host "`nMCPs that always require machine-specific setup:" -ForegroundColor Yellow
$catalog | Where-Object { $_.installMode -eq 'manual' } | ForEach-Object {
    Write-Host ("  - {0}: {1}" -f $_.name, ($_.requirements -join ', '))
}

if ($activeCount -ge 9 -and $coldCount -ge 277) {
    Write-Host "`nSkill installation looks complete." -ForegroundColor Green
    exit 0
}
Write-Host "`nSkill installation is incomplete. Run INSTALL.cmd again." -ForegroundColor Red
exit 1
