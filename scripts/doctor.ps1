[CmdletBinding()]
param([string]$TargetCodexHome)

$ErrorActionPreference = 'Continue'
$repoRoot = Split-Path -Parent $PSScriptRoot
$codexHome = if ($TargetCodexHome) { [System.IO.Path]::GetFullPath($TargetCodexHome) } elseif ($env:CODEX_HOME) { [System.IO.Path]::GetFullPath($env:CODEX_HOME) } else { Join-Path $env:USERPROFILE '.codex' }
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
$expectedActive = (Get-ChildItem -LiteralPath (Join-Path $repoRoot 'skills') -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') }).Count
$expectedCold = (Get-ChildItem -LiteralPath (Join-Path $repoRoot 'skill-library\leaves') -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') }).Count
$installedCatalogPath = Join-Path $codexHome 'skill-library\catalog.json'
$catalogCount = if (Test-Path -LiteralPath $installedCatalogPath) { @((Get-Content -LiteralPath $installedCatalogPath -Raw -Encoding UTF8 | ConvertFrom-Json).skills).Count } else { 0 }
$duplicates = @(Get-ChildItem -LiteralPath $skillsTarget -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path -LiteralPath (Join-Path $libraryTarget ($_.Name + '\SKILL.md')) } | ForEach-Object Name)
Write-Host "Active custom skills: $activeCount"
Write-Host "On-demand library skills: $coldCount"
Write-Host "Installed catalog entries: $catalogCount"
if ($duplicates.Count -gt 0) { Write-Host "Duplicate active/library names (review before removal): $($duplicates -join ', ')" -ForegroundColor Yellow }

$loadSmoke = $false
$reader = Join-Path $codexHome 'skill-library\scripts\read-skill.mjs'
if ($nodeCommand -and (Test-Path -LiteralPath $reader) -and $catalogCount -gt 0) {
    $testRoot = if ($env:SKILL_ACTIVITY_TEST_ROOT -and (Test-Path -LiteralPath $env:SKILL_ACTIVITY_TEST_ROOT -PathType Container)) { $env:SKILL_ACTIVITY_TEST_ROOT } else { [System.IO.Path]::GetTempPath() }
    $testRoot = [System.IO.Path]::GetFullPath($testRoot).TrimEnd('\', '/')
    $testDir = Join-Path $testRoot ('codex-skill-doctor-' + [guid]::NewGuid().ToString('N'))
    $oldActivityDir = $env:SKILL_ACTIVITY_DIR
    try {
        New-Item -ItemType Directory -Path $testDir -ErrorAction Stop | Out-Null
        $env:SKILL_ACTIVITY_DIR = $testDir
        $loaded = & $nodeCommand.Source $reader 'skill-library-router' 2>$null
        $loadSmoke = ($LASTEXITCODE -eq 0 -and (($loaded -join "`n") -match 'name: skill-library-router'))
    } finally {
        $env:SKILL_ACTIVITY_DIR = $oldActivityDir
        if ((Test-Path -LiteralPath $testDir) -and (Split-Path -Parent $testDir) -eq $testRoot) {
            Remove-Item -LiteralPath $testDir -Recurse -Force
        }
    }
}
Write-Host ("On-demand Skill read: " + $(if ($loadSmoke) { 'passed' } else { 'FAILED' }))

$cliCodexHome = if ($env:CODEX_HOME) { [System.IO.Path]::GetFullPath($env:CODEX_HOME) } else { Join-Path $env:USERPROFILE '.codex' }
if ($codexCommand -and $codexHome.TrimEnd('\', '/') -eq $cliCodexHome.TrimEnd('\', '/')) {
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
} elseif ($TargetCodexHome) {
    Write-Host 'Configured MCP servers: not checked (isolated target differs from CLI config)'
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

if ($activeCount -ge $expectedActive -and $coldCount -ge $expectedCold -and $catalogCount -ge ($expectedActive + $expectedCold) -and $duplicates.Count -eq 0 -and $loadSmoke) {
    Write-Host "`nSkill installation looks complete." -ForegroundColor Green
    exit 0
}
Write-Host "`nSkill installation is incomplete. Run INSTALL.cmd again." -ForegroundColor Red
exit 1
