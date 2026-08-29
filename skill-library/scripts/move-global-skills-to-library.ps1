[CmdletBinding()]
param(
    [switch]$Apply,
    [string]$SkillRoot = (Join-Path $env:USERPROFILE '.codex\skills'),
    [string]$LibraryRoot = (Join-Path $env:USERPROFILE '.codex\skill-library')
)

$ErrorActionPreference = 'Stop'
$expectedSkillRoot = [System.IO.Path]::GetFullPath((Join-Path $env:USERPROFILE '.codex\skills')).TrimEnd('\')
$resolvedSkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path.TrimEnd('\')
if ($resolvedSkillRoot -ne $expectedSkillRoot) {
    throw "Refusing to move: SkillRoot must be the configured global Skill directory: $expectedSkillRoot"
}

$leavesRoot = Join-Path $LibraryRoot 'leaves'
if (-not (Test-Path -LiteralPath $leavesRoot)) {
    New-Item -ItemType Directory -Path $leavesRoot -Force | Out-Null
}
$expectedLeavesRoot = [System.IO.Path]::GetFullPath((Join-Path $env:USERPROFILE '.codex\skill-library\leaves')).TrimEnd('\')
$resolvedLeavesRoot = (Resolve-Path -LiteralPath $leavesRoot).Path.TrimEnd('\')
if ($resolvedLeavesRoot -ne $expectedLeavesRoot) {
    throw "Refusing to move: library destination must be $expectedLeavesRoot"
}

$hot = @(
    'skill-library-router',
    'syhprojectskill',
    'work-handoff',
    'large-project-ops',
    'local-experience',
    'external-browser',
    'ui-image-parity',
    'evidence-based-acceptance'
)

$sourceDirs = @(Get-ChildItem -LiteralPath $resolvedSkillRoot -Directory -Force | Where-Object {
    $_.Name -ne '.system' -and (Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md'))
})
$cold = @($sourceDirs | Where-Object { $hot -notcontains $_.Name } | Sort-Object Name)
$conflicts = @($cold | Where-Object { Test-Path -LiteralPath (Join-Path $resolvedLeavesRoot $_.Name) })
if ($conflicts.Count -gt 0) {
    throw ("Refusing to overwrite existing library modules: " + (($conflicts | Select-Object -ExpandProperty Name) -join ', '))
}

$manifest = [pscustomobject][ordered]@{
    schemaVersion = 1
    createdAt = (Get-Date).ToUniversalTime().ToString('o')
    mode = if ($Apply) { 'applied' } else { 'preview' }
    activeRoot = $resolvedSkillRoot
    libraryRoot = $resolvedLeavesRoot
    keptActive = $hot
    movedToLibrary = @($cold | Select-Object -ExpandProperty Name)
    movedCount = $cold.Count
}

if ($Apply) {
    foreach ($directory in $cold) {
        $source = (Resolve-Path -LiteralPath $directory.FullName).Path
        if (-not $source.StartsWith($resolvedSkillRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to move an unexpected source: $source"
        }
        $destination = Join-Path $resolvedLeavesRoot $directory.Name
        Move-Item -LiteralPath $source -Destination $destination -ErrorAction Stop
    }
}

$manifestPath = Join-Path $LibraryRoot 'migration-manifest.json'
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

[pscustomobject]@{
    mode = $manifest.mode
    activeAfter = if ($Apply) { $hot.Count } else { $sourceDirs.Count }
    libraryMoveCount = $cold.Count
    manifest = $manifestPath
    keptActive = $hot
} | ConvertTo-Json -Depth 4
