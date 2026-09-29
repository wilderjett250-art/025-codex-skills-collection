[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Prompt,
    [ValidateRange(1, 20)][int]$Limit = 5,
    [string]$CatalogPath = (Join-Path $env:USERPROFILE '.codex\skill-library\catalog.json'),
    [string]$ProfilePath = (Join-Path $env:USERPROFILE '.codex\skill-library\routing-profile.json'),
    [switch]$AsJson
)

$ErrorActionPreference = 'Stop'
$node = Get-Command node -CommandType Application -ErrorAction Stop | Select-Object -First 1
$request = @{ prompt = $Prompt; catalogPath = $CatalogPath; profilePath = $ProfilePath; limit = $Limit } | ConvertTo-Json -Compress
$previousEncoding = $OutputEncoding
try {
    $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $raw = $request | & $node.Source (Join-Path $PSScriptRoot 'route-cli.mjs')
    if ($LASTEXITCODE -ne 0) { throw 'Shared Skill router failed; no recommendations were produced.' }
} finally {
    $OutputEncoding = $previousEncoding
}
$result = $raw | ConvertFrom-Json
if ($AsJson) { $result | ConvertTo-Json -Depth 10; return }
$result | Select-Object status, advisory, routes, candidateCount, truncated | Format-List
$result.workUnits | Select-Object route, @{n='owner';e={$_.owner.name}} | Format-Table -AutoSize
$result.candidates | Select-Object rank, role, name, matched, skillPath | Format-Table -AutoSize -Wrap
