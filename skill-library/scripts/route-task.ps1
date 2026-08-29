[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Prompt,
    [ValidateRange(1, 20)][int]$Limit = 8,
    [string]$CatalogPath = (Join-Path $env:USERPROFILE '.codex\skill-library\catalog.json'),
    [string]$ProfilePath = (Join-Path $env:USERPROFILE '.codex\skill-library\routing-profile.json'),
    [switch]$AsJson
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $CatalogPath)) { throw "Skill catalog is missing: $CatalogPath. Run build-catalog.ps1 first." }
if (-not (Test-Path -LiteralPath $ProfilePath)) { throw "Routing profile is missing: $ProfilePath." }

$catalog = Get-Content -LiteralPath $CatalogPath -Raw | ConvertFrom-Json
$profile = Get-Content -LiteralPath $ProfilePath -Raw | ConvertFrom-Json
$promptLower = $Prompt.ToLowerInvariant()

function Get-AliasMatches {
    param([string]$Text, [object[]]$Definitions)
    $hits = @()
    foreach ($definition in @($Definitions)) {
        $matched = @($definition.aliases | Where-Object {
            -not [string]::IsNullOrWhiteSpace([string]$_) -and $Text.Contains(([string]$_).ToLowerInvariant())
        } | Select-Object -Unique)
        if ($matched.Count -gt 0) {
            $hits += [pscustomobject]@{ name = [string]$definition.name; aliases = $matched }
        }
    }
    return $hits
}

function Test-Intersection {
    param([object[]]$Left, [object[]]$Right)
    foreach ($item in @($Left)) {
        if (@($Right) -contains [string]$item) { return $true }
    }
    return $false
}

function Add-Reason {
    param([System.Collections.Generic.List[string]]$Reasons, [string]$Value)
    if (-not [string]::IsNullOrWhiteSpace($Value) -and -not $Reasons.Contains($Value)) { $Reasons.Add($Value) }
}

$projectHits = @(Get-AliasMatches -Text $promptLower -Definitions $profile.projectTypes)
$phaseHits = @(Get-AliasMatches -Text $promptLower -Definitions $profile.phases)
$domainHits = @(Get-AliasMatches -Text $promptLower -Definitions $profile.domains)
$disciplineHits = @(Get-AliasMatches -Text $promptLower -Definitions $profile.disciplines)
$familyHits = @(Get-AliasMatches -Text $promptLower -Definitions $profile.families)
$routeHits = @(Get-AliasMatches -Text $promptLower -Definitions $profile.routes)

$projectNames = @($projectHits | ForEach-Object { $_.name } | Select-Object -Unique)
$phaseNames = @($phaseHits | ForEach-Object { $_.name } | Select-Object -Unique)
$domainNames = @($domainHits | ForEach-Object { $_.name } | Select-Object -Unique)
$disciplineNames = @($disciplineHits | ForEach-Object { $_.name } | Select-Object -Unique)
$familyNames = @($familyHits | ForEach-Object { $_.name } | Select-Object -Unique)
$routeNames = @($routeHits | ForEach-Object { $_.name } | Select-Object -Unique)
$englishTokens = @([regex]::Matches($promptLower, '[a-z0-9][a-z0-9.+#_-]{2,}') | ForEach-Object { $_.Value } | Select-Object -Unique)

$routeMap = @{}
foreach ($route in @($profile.routes)) { $routeMap[[string]$route.name] = $route }
$rawRouteNames = @($routeNames)
$routeNames = @($routeNames | Where-Object {
    $route = $routeMap[[string]$_]
    $suppressedBy = @($route.suppressedByRoutes)
    $suppressedBy.Count -eq 0 -or -not (Test-Intersection -Left $rawRouteNames -Right $suppressedBy)
} | Sort-Object @{ Expression = {
    $route = $routeMap[[string]$_]
    if ($null -ne $route.sequence) { [int]$route.sequence } else { 50 }
} }, @{ Expression = { [string]$_ } })

$skillMap = @{}
foreach ($skill in @($catalog.skills)) { $skillMap[[string]$skill.name] = $skill }

function Test-SupportApplies {
    param([object]$Support)
    $phaseOk = $true
    $aliasOk = $true
    if ($null -ne $Support.whenPhases -and @($Support.whenPhases).Count -gt 0) {
        $phaseOk = Test-Intersection -Left $phaseNames -Right @($Support.whenPhases)
    }
    if ($null -ne $Support.whenAliases -and @($Support.whenAliases).Count -gt 0) {
        $aliasOk = @($Support.whenAliases | Where-Object { $promptLower.Contains(([string]$_).ToLowerInvariant()) }).Count -gt 0
    }
    return ($phaseOk -and $aliasOk)
}

function Get-SkillReference {
    param([string]$Name)
    if (-not $skillMap.ContainsKey($Name)) { throw "Route references an unknown Skill: $Name" }
    $skill = $skillMap[$Name]
    return [pscustomobject][ordered]@{
        name = [string]$skill.name
        plane = [string]$skill.plane
        domain = [string]$skill.domain
        discipline = [string]$skill.discipline
        family = [string]$skill.family
        canonicalPath = [string]$skill.canonicalPath
        source = [string]$skill.source
        skillPath = [string]$skill.skillPath
    }
}

$workUnits = New-Object System.Collections.Generic.List[object]
$accessSkills = New-Object System.Collections.Generic.List[object]
$controlSkills = New-Object System.Collections.Generic.List[object]
foreach ($routeName in $routeNames) {
    $route = $routeMap[$routeName]
    $owners = @($route.ownerSkills)
    if ($owners.Count -ne 1) { throw "Every atomic route must have exactly one owner Skill: $routeName" }
    $owner = Get-SkillReference -Name ([string]$owners[0])
    $supports = @($route.supportingSkills | Where-Object { Test-SupportApplies -Support $_ } | ForEach-Object {
        Get-SkillReference -Name ([string]$_.name)
    })
    $kind = if ([string]::IsNullOrWhiteSpace([string]$route.kind)) { 'capability' } else { [string]$route.kind }
    switch ($kind) {
        'capability' {
            $workUnits.Add([pscustomobject][ordered]@{
                route = [string]$route.name
                plane = [string]$route.plane
                domain = [string]$route.domain
                discipline = [string]$route.discipline
                family = [string]$route.family
                owner = $owner
                supportingSkills = $supports
            })
        }
        'access' {
            $accessSkills.Add($owner)
            foreach ($support in $supports) {
                if ([string]$support.plane -eq 'control') { $controlSkills.Add($support) }
            }
        }
        'control' {
            $controlSkills.Add($owner)
            foreach ($support in $supports) { $controlSkills.Add($support) }
        }
        default { throw "Unknown route kind '$kind' on route: $routeName" }
    }
}

$candidates = foreach ($skill in @($catalog.skills)) {
    $score = 0
    $role = 'candidate'
    $directMatch = $false
    $reasons = New-Object System.Collections.Generic.List[string]
    $skillName = [string]$skill.name
    $skillAliases = @($skill.aliases)
    $skillText = (($skillName + ' ' + ($skill.tags -join ' ') + ' ' + ($skillAliases -join ' ') + ' ' + [string]$skill.trigger).ToLowerInvariant())

    if ($promptLower.Contains($skillName.ToLowerInvariant())) {
        $score += 100
        $directMatch = $true
        Add-Reason -Reasons $reasons -Value 'name'
    }

    foreach ($alias in $skillAliases) {
        $aliasText = ([string]$alias).ToLowerInvariant()
        if (-not [string]::IsNullOrWhiteSpace($aliasText) -and $promptLower.Contains($aliasText)) {
            $score += 34
            $directMatch = $true
            Add-Reason -Reasons $reasons -Value ("alias:" + [string]$alias)
        }
    }

    if ($domainNames -contains [string]$skill.domain) {
        $score += 10
        Add-Reason -Reasons $reasons -Value ("domain:" + [string]$skill.domain)
    }
    if ($disciplineNames -contains [string]$skill.discipline) {
        $score += 18
        Add-Reason -Reasons $reasons -Value ("discipline:" + [string]$skill.discipline)
    }
    if ($familyNames -contains [string]$skill.family) {
        $score += 26
        Add-Reason -Reasons $reasons -Value ("family:" + [string]$skill.family)
    }
    if ($projectNames.Count -gt 0 -and (Test-Intersection -Left $projectNames -Right @($skill.projectTypes))) {
        $score += 5
        Add-Reason -Reasons $reasons -Value ("project:" + (($projectNames | Where-Object { @($skill.projectTypes) -contains $_ }) -join ','))
    }
    if ($phaseNames.Count -gt 0 -and (Test-Intersection -Left $phaseNames -Right @($skill.phases))) {
        $score += 7
        Add-Reason -Reasons $reasons -Value ("phase:" + (($phaseNames | Where-Object { @($skill.phases) -contains $_ }) -join ','))
    }

    foreach ($token in $englishTokens) {
        $tokenPattern = '(?<![a-z0-9])' + [regex]::Escape([string]$token) + '(?![a-z0-9])'
        if ($skillText -match $tokenPattern) {
            $score += 6
            $directMatch = $true
            Add-Reason -Reasons $reasons -Value ("term:" + [string]$token)
        }
    }

    foreach ($routeName in $routeNames) {
        $route = $routeMap[$routeName]
        if (@($route.ownerSkills) -contains $skillName) {
            $score += 120
            $role = 'owner'
            Add-Reason -Reasons $reasons -Value ("route:" + $routeName)
        }
        foreach ($support in @($route.supportingSkills)) {
            if ([string]$support.name -ne $skillName) { continue }
            $phaseOk = $true
            $aliasOk = $true
            if ($null -ne $support.whenPhases -and @($support.whenPhases).Count -gt 0) {
                $phaseOk = Test-Intersection -Left $phaseNames -Right @($support.whenPhases)
            }
            if ($null -ne $support.whenAliases -and @($support.whenAliases).Count -gt 0) {
                $aliasOk = @($support.whenAliases | Where-Object { $promptLower.Contains(([string]$_).ToLowerInvariant()) }).Count -gt 0
            }
            if ($phaseOk -and $aliasOk) {
                $score += 70
                if ($role -ne 'owner') { $role = 'support' }
                Add-Reason -Reasons $reasons -Value ("support:" + $routeName)
            }
        }
        if ([string]$route.plane -eq [string]$skill.plane) { $score += 4 }
        if ([string]$route.domain -eq [string]$skill.domain) { $score += 8 }
        if ([string]$route.discipline -eq [string]$skill.discipline) { $score += 10 }
        if ([string]$route.family -eq [string]$skill.family) { $score += 12 }
    }

    if ($score -gt 0) {
        if ([string]$skill.source -eq 'active') { $score += 2 }
        [pscustomobject][ordered]@{
            score = $score
            role = $role
            name = $skillName
            plane = [string]$skill.plane
            domain = [string]$skill.domain
            discipline = [string]$skill.discipline
            family = [string]$skill.family
            canonicalPath = [string]$skill.canonicalPath
            source = [string]$skill.source
            directMatch = $directMatch
            matched = ($reasons -join '; ')
            skillPath = [string]$skill.skillPath
        }
    }
}

$roleOrder = @{ owner = 0; support = 1; candidate = 2 }
$hasOwner = @($candidates | Where-Object { $_.role -eq 'owner' }).Count -gt 0
$eligible = if ($hasOwner) {
    @($candidates | Where-Object { $_.role -ne 'candidate' -or $_.directMatch })
} else {
    @($candidates)
}
$selected = @($eligible | Sort-Object @{ Expression = { $roleOrder[$_.role] }; Ascending = $true }, @{ Expression = 'score'; Descending = $true }, name | Select-Object -First $Limit)
for ($index = 0; $index -lt $selected.Count; $index++) {
    $selected[$index] | Add-Member -NotePropertyName rank -NotePropertyValue ($index + 1)
    $selected[$index].PSObject.Properties.Remove('directMatch')
}

$uniqueAccessSkills = @($accessSkills | Group-Object name | ForEach-Object { $_.Group[0] })
$uniqueControlSkills = @($controlSkills | Group-Object name | ForEach-Object { $_.Group[0] })

$result = [pscustomobject][ordered]@{
    projectTypes = $projectNames
    phases = $phaseNames
    domains = $domainNames
    disciplines = $disciplineNames
    families = $familyNames
    routes = $routeNames
    workUnits = $workUnits.ToArray()
    accessSkills = $uniqueAccessSkills
    controlSkills = $uniqueControlSkills
    candidateCount = $eligible.Count
    candidates = $selected
}

if ($AsJson) {
    $result | ConvertTo-Json -Depth 8
    return
}

[pscustomobject][ordered]@{
    project = if ($projectNames.Count) { $projectNames -join ',' } else { 'unspecified' }
    phase = if ($phaseNames.Count) { $phaseNames -join ',' } else { 'unspecified' }
    domain = if ($domainNames.Count) { $domainNames -join ',' } else { 'unspecified' }
    discipline = if ($disciplineNames.Count) { $disciplineNames -join ',' } else { 'unspecified' }
    route = if ($routeNames.Count) { $routeNames -join ',' } else { 'generic' }
} | Format-List
$workUnits | Select-Object route, domain, discipline, family, @{n='owner';e={$_.owner.name}} | Format-Table -AutoSize -Wrap
$selected | Select-Object rank, score, role, name, plane, domain, discipline, family, source, matched, skillPath | Format-Table -AutoSize -Wrap
