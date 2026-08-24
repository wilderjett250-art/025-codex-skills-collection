[CmdletBinding()]
param(
    [ValidateSet('windows', 'git', 'remote', 'browser', 'codex', 'documents', 'wechat', 'android', 'gpu', 'hardware', 'all')]
    [string]$Topic = 'all',
    [string]$Query,
    [switch]$ListTopics,
    [string]$ManualPath = $env:CODEX_EXPERIENCE_MANUAL_PATH,
    [ValidateRange(0, 5)]
    [int]$Context = 0,
    [ValidateRange(1, 50)]
    [int]$MaxMatches = 4
)

$ErrorActionPreference = 'Stop'

$patternsByTopic = [ordered]@{
    windows = @('PowerShell', 'GBK', 'UTF-8', 'LASTEXITCODE', 'automatic variable', 'Windows')
    git = @('git', 'staged', 'worktree', 'archive', 'cleanup', 'commit')
    remote = @('SSH', 'Bash', 'LF', 'Nginx', 'docker', 'systemd', 'deployment')
    browser = @('browser', 'Playwright', 'CAPTCHA', 'GitHub', 'Edge', 'WebView')
    codex = @('Codex', 'MCP', 'plugin', 'logs_2.sqlite', 'workspace', 'context')
    documents = @('DOCX', 'PDF', 'LibreOffice', 'screenshot', 'render', 'Word')
    wechat = @('Mini Program', 'DevTools', 'wx\.', 'privacy', 'experience version')
    android = @('Android', 'ADB', 'NDK', 'APK', 'emulator')
    gpu = @('GPU', 'nvidia-smi', 'cgroup', 'training', 'CUDA', 'throttled')
    hardware = @('COM[0-9]+', 'ESP32', 'serial', 'firmware', 'wiring', 'device')
}

if ($ListTopics) {
    $patternsByTopic.Keys | ForEach-Object { Write-Output $_ }
    return
}

if ([string]::IsNullOrWhiteSpace($ManualPath)) {
    throw 'Set CODEX_EXPERIENCE_MANUAL_PATH or pass -ManualPath <sanitized-manual-path>.'
}

$manualPath = $ManualPath
if (-not (Test-Path -LiteralPath $manualPath -PathType Leaf)) {
    throw "Experience manual was not found: $manualPath"
}

if (-not (Get-Command rg -ErrorAction SilentlyContinue)) {
    throw 'The local-experience Skill requires rg.exe for bounded manual search.'
}

if ([string]::IsNullOrWhiteSpace($Query) -and $Topic -eq 'all') {
    Write-Output 'Specify -Query for an exact symptom or -Topic for a bounded category search. Use -ListTopics to list categories.'
    return
}

$rgArguments = @('-n', '-i', '-C', $Context.ToString(), '--max-count', $MaxMatches.ToString())
if (-not [string]::IsNullOrWhiteSpace($Query)) {
    $rgArguments += @('-F', '--', $Query, $manualPath)
}
else {
    foreach ($pattern in $patternsByTopic[$Topic]) {
        $rgArguments += @('-e', $pattern)
    }
    $rgArguments += @('--', $manualPath)
}

Write-Output "Searching local experience manual: topic=$Topic; max_matches=$MaxMatches; context=$Context"
& rg @rgArguments
if ($LASTEXITCODE -eq 1) {
    Write-Output 'No matching experience entry was found. Treat this as a new investigation, not a failed task.'
    return
}
if ($LASTEXITCODE -ne 0) {
    throw "rg.exe failed with exit code $LASTEXITCODE"
}
