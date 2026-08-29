[CmdletBinding()]
param(
    [ValidateSet('recommended', 'development', 'research', 'design', 'video', 'engineering', 'full')]
    [string]$Profile = 'full',
    [string]$FilesystemRoot,
    [switch]$Force,
    [switch]$SkipMcp,
    [switch]$SkipPlugins
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$activeSource = Join-Path $repoRoot 'skills'
$librarySource = Join-Path $repoRoot 'skill-library'
$catalogPath = Join-Path $repoRoot 'mcp\catalog.json'
$profilesPath = Join-Path $repoRoot 'mcp\profiles.json'
$pluginsPath = Join-Path $repoRoot 'presets\plugins.json'

if ($env:CODEX_HOME) {
    $codexHome = [System.IO.Path]::GetFullPath($env:CODEX_HOME)
} else {
    $codexHome = Join-Path $env:USERPROFILE '.codex'
}

$skillsTarget = Join-Path $codexHome 'skills'
$libraryTarget = Join-Path $codexHome 'skill-library'
$configPath = Join-Path $codexHome 'config.toml'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupRoot = Join-Path $codexHome "backups\codex-skills-mcp-toolkit\$stamp"

function Write-Step([string]$Message) {
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Backup-Directory([string]$Source, [string]$Destination) {
    if (Test-Path -LiteralPath $Source) {
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
        & robocopy.exe $Source $Destination /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
        if ($LASTEXITCODE -ge 8) {
            throw "Backup failed from $Source to $Destination (robocopy code $LASTEXITCODE)"
        }
    }
}

function Test-McpExists([string]$Name) {
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & codex mcp get $Name --json *> $null
    $ok = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $previous
    return $ok
}

function Add-McpEntry($Entry, [string]$ResolvedFilesystemRoot) {
    $name = [string]$Entry.name
    if (Test-McpExists $name) {
        if (-not $Force) {
            Write-Host "  Existing MCP kept: $name"
            return 'existing'
        }
        & codex mcp remove $name | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Unable to remove existing MCP: $name"
        }
    }

    if ($Entry.installMode -eq 'manual') {
        Write-Host "  Requires local setup: $name" -ForegroundColor Yellow
        return 'manual'
    }

    if ($Entry.installMode -eq 'parameter') {
        if ($name -ne 'filesystem' -or -not $ResolvedFilesystemRoot) {
            Write-Host "  Requires installer parameter: $name" -ForegroundColor Yellow
            return 'manual'
        }
        $arguments = @('mcp', 'add', $name, '--', [string]$Entry.command)
        $arguments += @($Entry.args | ForEach-Object { [string]$_ })
        $arguments += $ResolvedFilesystemRoot
        & codex @arguments | Out-Null
    } elseif ($Entry.type -eq 'http') {
        $arguments = @('mcp', 'add', $name, '--url', [string]$Entry.url)
        if ($Entry.bearerTokenEnvVar) {
            $arguments += @('--bearer-token-env-var', [string]$Entry.bearerTokenEnvVar)
        }
        & codex @arguments | Out-Null
    } elseif ($Entry.type -eq 'stdio') {
        $arguments = @('mcp', 'add', $name, '--', [string]$Entry.command)
        $arguments += @($Entry.args | ForEach-Object { [string]$_ })
        & codex @arguments | Out-Null
    } else {
        throw "Unsupported MCP type: $name"
    }

    if ($LASTEXITCODE -ne 0) {
        throw "MCP registration failed: $name"
    }
    Write-Host "  MCP registered: $name" -ForegroundColor Green
    return 'installed'
}

function Add-PluginPreset([array]$Plugins) {
    if (-not (Test-Path -LiteralPath $configPath)) {
        New-Item -ItemType File -Path $configPath -Force | Out-Null
    }
    $configText = Get-Content -LiteralPath $configPath -Raw
    if ($null -eq $configText) { $configText = '' }

    $pluginCommandAvailable = $false
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & codex plugin --help *> $null
    $pluginCommandAvailable = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $previous

    foreach ($plugin in $Plugins) {
        $id = [string]$plugin.id
        if ($pluginCommandAvailable) {
            $previous = $ErrorActionPreference
            $ErrorActionPreference = 'Continue'
            & codex plugin add $id *> $null
            $ErrorActionPreference = $previous
        }

        $section = '[plugins."' + $id + '"]'
        $pattern = '(?m)^' + [regex]::Escape($section) + '\s*$'
        if (-not [regex]::IsMatch($configText, $pattern)) {
            $value = if ([bool]$plugin.enabled) { 'true' } else { 'false' }
            $configText += "`r`n$section`r`nenabled = $value`r`n"
            Write-Host "  Plugin preset added: $id ($value)"
        } else {
            Write-Host "  Existing plugin setting kept: $id"
        }
    }
    Set-Content -LiteralPath $configPath -Value $configText -Encoding UTF8
}

foreach ($requiredPath in @($activeSource, $librarySource, $catalogPath, $profilesPath, $pluginsPath)) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Installer package is missing: $requiredPath"
    }
}

Write-Step "Target Codex home: $codexHome"
New-Item -ItemType Directory -Path $codexHome -Force | Out-Null
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

Write-Step 'Back up matching Skills, Skill Library, and Codex config'
if (Test-Path -LiteralPath $configPath) {
    Copy-Item -LiteralPath $configPath -Destination (Join-Path $backupRoot 'config.toml') -Force
}
Get-ChildItem -LiteralPath $activeSource -Directory | ForEach-Object {
    $existing = Join-Path $skillsTarget $_.Name
    Backup-Directory $existing (Join-Path (Join-Path $backupRoot 'skills') $_.Name)
}
Backup-Directory $libraryTarget (Join-Path $backupRoot 'skill-library')
Write-Host "  Backup: $backupRoot"

Write-Step 'Install active core Skills'
New-Item -ItemType Directory -Path $skillsTarget -Force | Out-Null
Get-ChildItem -LiteralPath $activeSource -Directory | ForEach-Object {
    $target = Join-Path $skillsTarget $_.Name
    if (-not (Test-Path -LiteralPath $target)) {
        New-Item -ItemType Directory -Path $target -Force | Out-Null
    }
    Get-ChildItem -LiteralPath $_.FullName -Force | Copy-Item -Destination $target -Recurse -Force
    Write-Host "  Installed: $($_.Name)"
}

Write-Step 'Install the on-demand Skill Library'
if (-not (Test-Path -LiteralPath $libraryTarget)) {
    New-Item -ItemType Directory -Path $libraryTarget -Force | Out-Null
}
Get-ChildItem -LiteralPath $librarySource -Force | Copy-Item -Destination $libraryTarget -Recurse -Force
$catalogBuilder = Join-Path $libraryTarget 'scripts\build-catalog.ps1'
if (-not (Test-Path -LiteralPath $catalogBuilder)) {
    throw "Missing Skill Catalog builder: $catalogBuilder"
}
$pwshCommand = Get-Command pwsh.exe -ErrorAction SilentlyContinue
if (-not $pwshCommand) {
    throw 'PowerShell 7 (pwsh.exe) is required by the on-demand Skill router.'
}
& $pwshCommand.Source -NoProfile -ExecutionPolicy Bypass -File $catalogBuilder -SkillRoot $skillsTarget -LibraryRoot $libraryTarget -OutputPath (Join-Path $libraryTarget 'catalog.json') -ProfilePath (Join-Path $libraryTarget 'routing-profile.json') | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'Skill Catalog rebuild failed.'
}
$coldCount = (Get-ChildItem -LiteralPath (Join-Path $libraryTarget 'leaves') -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') }).Count
Write-Host "  On-demand Skills installed: $coldCount"

if (-not $SkipPlugins) {
    Write-Step 'Apply plugin Skill source preset'
    $pluginsRaw = Get-Content -LiteralPath $pluginsPath -Raw | ConvertFrom-Json
    $plugins = @($pluginsRaw.GetEnumerator())
    Add-PluginPreset $plugins
}

if (-not $SkipMcp) {
    Write-Step "Register MCP profile: $Profile"
    if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
        throw 'The codex command is missing. Skills were copied, but MCP registration requires Codex CLI.'
    }
    $catalogRaw = Get-Content -LiteralPath $catalogPath -Raw | ConvertFrom-Json
    $catalog = @($catalogRaw.GetEnumerator())
    $profiles = Get-Content -LiteralPath $profilesPath -Raw | ConvertFrom-Json
    $selectedNames = @($profiles.$Profile)
    $resolvedFilesystemRoot = $null
    if ($FilesystemRoot) {
        if (-not (Test-Path -LiteralPath $FilesystemRoot -PathType Container)) {
            throw "FilesystemRoot is not a valid directory: $FilesystemRoot"
        }
        $resolvedFilesystemRoot = (Resolve-Path -LiteralPath $FilesystemRoot).Path
    }

    $results = @{ installed = 0; existing = 0; manual = 0 }
    foreach ($selectedName in $selectedNames) {
        $entry = $catalog | Where-Object { $_.name -eq $selectedName } | Select-Object -First 1
        if (-not $entry) { throw "MCP catalog entry is missing: $selectedName" }
        $status = Add-McpEntry $entry $resolvedFilesystemRoot
        $results[$status] = [int]$results[$status] + 1
    }
    Write-Host "  MCP result: installed $($results.installed), kept $($results.existing), local setup $($results.manual)"
}

Write-Step 'Installation complete'
Write-Host 'Fully exit and reopen Codex, then start a new task for testing.' -ForegroundColor Green
Write-Host "Run DOCTOR.cmd when needed. Backup: $backupRoot"
