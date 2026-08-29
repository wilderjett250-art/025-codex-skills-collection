[CmdletBinding()]
param(
    [ValidateSet('domain', 'control')][string]$Plane = 'domain',
    [string]$Domain = '',
    [string]$Discipline = '',
    [string]$Family = '',
    [switch]$ListDisciplines,
    [switch]$ListFamilies,
    [string]$Query = '',
    [ValidateRange(1, 20)][int]$Limit = 8,
    [string]$CatalogPath = (Join-Path $env:USERPROFILE '.codex\skill-library\catalog.json')
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $CatalogPath)) { throw "Skill catalog is missing: $CatalogPath. Run build-catalog.ps1 first." }
$catalog = Get-Content -LiteralPath $CatalogPath -Raw | ConvertFrom-Json

if ([string]::IsNullOrWhiteSpace($Domain)) {
    if ([string]::IsNullOrWhiteSpace($Query)) { throw 'Provide -Domain for a taxonomy drill-down or -Query for prompt routing.' }
    $router = Join-Path (Split-Path -Parent $PSCommandPath) 'route-task.ps1'
    & $router -Prompt $Query -Limit $Limit -CatalogPath $CatalogPath
    exit $LASTEXITCODE
}
$validDomains = if ($Plane -eq 'control') { @($catalog.controlDomains) } else { @($catalog.domains) }
if ($validDomains -notcontains $Domain) { throw "Unknown $Plane domain '$Domain'. Valid values: $($validDomains -join ', ')" }

$tokens = @($Query.ToLowerInvariant().Split([char[]]' ,;:/\|()[]{}-_', [System.StringSplitOptions]::RemoveEmptyEntries) | Where-Object { $_.Length -ge 2 } | Select-Object -Unique)
$domainSkills = @($catalog.skills | Where-Object { $_.plane -eq $Plane -and $_.domain -eq $Domain })

if ($ListDisciplines) {
    $domainSkills | Group-Object discipline | Sort-Object Name | ForEach-Object {
        [pscustomobject]@{ domain = $Domain; discipline = $_.Name; skills = $_.Count }
    } | Format-Table -AutoSize
    exit 0
}

if (-not [string]::IsNullOrWhiteSpace($Discipline)) {
    $domainSkills = @($domainSkills | Where-Object { $_.discipline -eq $Discipline })
    if ($domainSkills.Count -eq 0) {
        throw "No discipline '$Discipline' exists in domain '$Domain'. Use -ListDisciplines to inspect valid disciplines."
    }
}

if ($ListFamilies) {
    $domainSkills | Group-Object family | Sort-Object Name | ForEach-Object {
        [pscustomobject]@{ domain = $Domain; discipline = if ([string]::IsNullOrWhiteSpace($Discipline)) { '*' } else { $Discipline }; family = $_.Name; skills = $_.Count }
    } | Format-Table -AutoSize
    exit 0
}

if (-not [string]::IsNullOrWhiteSpace($Family)) {
    $domainSkills = @($domainSkills | Where-Object { $_.family -eq $Family })
    if ($domainSkills.Count -eq 0) {
        throw "No Skill family '$Family' exists in the selected domain/discipline. Use -ListFamilies to inspect valid families."
    }
}

$candidates = foreach ($skill in $domainSkills) {
    $score = 100
    if ($skill.source -eq 'active') { $score += 2 }
    $haystack = (($skill.name + ' ' + ($skill.tags -join ' ') + ' ' + $skill.trigger).ToLowerInvariant())
    foreach ($token in $tokens) { if ($haystack.Contains($token)) { $score += 12 } }
    [pscustomobject][ordered]@{
        score = $score; discipline = $skill.discipline; family = $skill.family; name = $skill.name; role = $skill.role; source = $skill.source
        tags = ($skill.tags -join ', '); skillPath = $skill.skillPath; trigger = $skill.trigger
    }
}
$candidates | Sort-Object @{ Expression = 'score'; Descending = $true }, name | Select-Object -First $Limit | Format-Table -AutoSize -Wrap
