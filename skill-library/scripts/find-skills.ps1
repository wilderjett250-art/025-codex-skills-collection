[CmdletBinding()]
param(
    [ValidateSet('domain', 'control')][string]$Plane = 'domain',
    [string]$Domain = '', [string]$Discipline = '', [string]$Family = '',
    [switch]$ListDisciplines, [switch]$ListFamilies,
    [string]$Query = '', [ValidateRange(1, 20)][int]$Limit = 3,
    [string]$CatalogPath = (Join-Path $env:USERPROFILE '.codex\skill-library\catalog.json'),
    [string]$DiscoveryPath = (Join-Path $env:USERPROFILE '.codex\skill-library\discovery-profile.json'),
    [switch]$AsJson
)
$ErrorActionPreference = 'Stop'
$catalog = Get-Content -LiteralPath $CatalogPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($Domain) {
    $valid = if ($Plane -eq 'control') { @($catalog.controlDomains) } else { @($catalog.domains) }
    if ($valid -notcontains $Domain) { throw "Unknown domain: $Domain" }
}
$scope = @($catalog.skills | Where-Object { $_.plane -eq $Plane -and (-not $Domain -or $_.domain -eq $Domain) -and (-not $Discipline -or $_.discipline -eq $Discipline) -and (-not $Family -or $_.family -eq $Family) })
if ($ListDisciplines -or $ListFamilies) {
    $groupBy = if ($ListDisciplines) { 'discipline' } else { 'family' }
    $groups = @($scope | Group-Object $groupBy | Select-Object Name, Count)
    if ($AsJson) { ConvertTo-Json -InputObject $groups; return }
    $groups | Format-Table -AutoSize; return
}
if ([string]::IsNullOrWhiteSpace($Query)) { throw 'Provide a task-focused -Query, or use a listing switch.' }
$options = @{limit=$Limit;domain=$Domain;discipline=$Discipline;family=$Family}
if ($PSBoundParameters.ContainsKey('Plane') -or $Domain) { $options.plane=$Plane }
$request = @{query=$Query;catalogPath=$CatalogPath;discoveryPath=$DiscoveryPath;options=$options} | ConvertTo-Json -Compress
# ASCII JSON escapes survive Windows PowerShell 5.1 native-pipeline encodings.
$request = [regex]::Replace($request, '[^\x00-\x7F]', { param($m) '\u{0:x4}' -f [int][char]$m.Value })
$node = Get-Command node -CommandType Application | Select-Object -First 1
$previousEncoding = $OutputEncoding
$previousConsoleEncoding = [Console]::OutputEncoding
try {
    $OutputEncoding = New-Object Text.UTF8Encoding($false)
    [Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
    $raw = $request | & $node.Source (Join-Path $PSScriptRoot 'search-skills.mjs')
    if ($LASTEXITCODE -ne 0) { throw 'Metadata search failed' }
} finally { $OutputEncoding=$previousEncoding; [Console]::OutputEncoding=$previousConsoleEncoding }
$result=$raw | ConvertFrom-Json
if ($AsJson) { $result | ConvertTo-Json -Depth 8; return }
$result | Select-Object status,candidateCount,next | Format-List
$result.candidates | Select-Object name,description,path,matched | Format-Table -AutoSize -Wrap
