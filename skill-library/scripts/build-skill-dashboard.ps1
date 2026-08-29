[CmdletBinding()]
param(
    [string]$CatalogPath = (Join-Path $env:USERPROFILE '.codex\skill-library\catalog.json'),
    [string]$OutputDirectory = (Join-Path $env:USERPROFILE '.codex\skill-library\dashboard')
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $CatalogPath)) {
    throw "Skill catalog is missing: $CatalogPath"
}

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$catalog = Get-Content -LiteralPath $CatalogPath -Raw | ConvertFrom-Json

function Get-FrontMatter {
    param([string]$Content)

    $match = [regex]::Match($Content, '(?s)\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n')
    if (-not $match.Success) {
        return [pscustomobject]@{ Found = $false; Length = 0; Name = ''; Description = '' }
    }

    $lines = @($match.Groups[1].Value -split "`r?`n")
    $values = @{}
    foreach ($key in @('name', 'description')) {
        for ($index = 0; $index -lt $lines.Count; $index++) {
            $valueMatch = [regex]::Match($lines[$index], '^' + [regex]::Escape($key) + ':\s*(.*)$')
            if (-not $valueMatch.Success) { continue }
            $value = $valueMatch.Groups[1].Value.Trim()
            if ($value -match '^[>|][+-]?$') {
                $parts = New-Object System.Collections.Generic.List[string]
                for ($next = $index + 1; $next -lt $lines.Count -and $lines[$next] -match '^\s+'; $next++) {
                    if (-not [string]::IsNullOrWhiteSpace($lines[$next])) { $parts.Add($lines[$next].Trim()) }
                }
                $values[$key] = ($parts -join ' ')
            } else {
                $values[$key] = $value.Trim('"').Trim("'").Replace("''", "'")
            }
            break
        }
    }
    $name = if ($values.ContainsKey('name')) { [string]$values['name'] } else { '' }
    $description = if ($values.ContainsKey('description')) { [string]$values['description'] } else { '' }

    return [pscustomobject]@{
        Found = $true
        Length = $match.Length
        Name = $name
        Description = $description
    }
}

function Get-AuditNotes {
    param(
        [int]$Lines,
        [int]$DescriptionChars,
        [int]$RepeatedLongLines,
        [int]$Headings,
        [int]$CodeFences,
        [bool]$MetadataComplete
    )

    $notes = New-Object System.Collections.Generic.List[string]
    if (-not $MetadataComplete) { $notes.Add('入口元数据不完整，需要先修复 name 或 description。') }
    if ($DescriptionChars -gt 220) { $notes.Add("路由描述 ${DescriptionChars} 字符；建议压缩到 220 以内并保留触发边界。") }
    if ($Lines -gt 400) { $notes.Add("入口 ${Lines} 行；优先把示例、参考表和故障排查移到按需 reference。") }
    elseif ($Lines -gt 200) { $notes.Add("入口 ${Lines} 行；检查能否用渐进披露拆出按需 reference。") }
    if ($RepeatedLongLines -gt 0) { $notes.Add("发现 ${RepeatedLongLines} 处重复长行；需要人工判断是必要强调还是冗余。") }
    if ($Headings -gt 24) { $notes.Add("共有 ${Headings} 个标题；入口可能承担了参考手册职责。") }
    if ($CodeFences -gt 20) { $notes.Add("共有 ${CodeFences} 个代码围栏；代码样例适合按需加载。") }
    return @($notes)
}

$rows = foreach ($skill in @($catalog.skills)) {
    $content = [IO.File]::ReadAllText([string]$skill.skillPath)
    $frontMatter = Get-FrontMatter -Content $content
    $body = if ($frontMatter.Found) { $content.Substring($frontMatter.Length) } else { $content }
    $lines = @($content -split "`r?`n")
    $bodyLines = @($body -split "`r?`n")
    $normalizedLongLines = @(
        $bodyLines |
            ForEach-Object { ($_ -replace '\s+', ' ').Trim().ToLowerInvariant() } |
            Where-Object { $_.Length -ge 48 -and $_ -notmatch '^```|^\|[- :|]+\|$' }
    )
    $repeatMeasure = $normalizedLongLines |
        Group-Object |
        Where-Object { $_.Count -gt 1 } |
        ForEach-Object { $_.Count - 1 } |
        Measure-Object -Sum
    $repeatedLongLines = if ($null -eq $repeatMeasure.Sum) { 0 } else { [int]$repeatMeasure.Sum }
    $description = if (-not [string]::IsNullOrWhiteSpace($frontMatter.Description)) {
        $frontMatter.Description
    } else {
        [string]$skill.trigger
    }
    $headings = @($bodyLines | Where-Object { $_ -match '^#{1,6}\s+' }).Count
    $codeFences = @($bodyLines | Where-Object { $_ -match '^```' }).Count
    $metadataComplete = $frontMatter.Found -and
        -not [string]::IsNullOrWhiteSpace($frontMatter.Name) -and
        -not [string]::IsNullOrWhiteSpace($description)
    $notes = @(Get-AuditNotes -Lines $lines.Count -DescriptionChars $description.Length -RepeatedLongLines $repeatedLongLines -Headings $headings -CodeFences $codeFences -MetadataComplete $metadataComplete)
    $score = 0
    if (-not $metadataComplete) { $score += 100 }
    if ($description.Length -gt 220) { $score += [Math]::Min(30, [Math]::Ceiling(($description.Length - 220) / 20)) }
    if ($lines.Count -gt 200) { $score += [Math]::Min(40, [Math]::Ceiling(($lines.Count - 200) / 20)) }
    if ($lines.Count -gt 400) { $score += 12 }
    if ($repeatedLongLines -gt 0) { $score += [Math]::Min(12, $repeatedLongLines * 2) }

    [pscustomobject][ordered]@{
        name = [string]$skill.name
        source = [string]$skill.source
        plane = [string]$skill.plane
        domain = [string]$skill.domain
        discipline = [string]$skill.discipline
        family = [string]$skill.family
        canonicalPath = [string]$skill.canonicalPath
        skillPath = [string]$skill.skillPath
        trigger = $description
        tags = @($skill.tags)
        aliases = @($skill.aliases)
        projectTypes = @($skill.projectTypes)
        phases = @($skill.phases)
        platforms = @($skill.platforms)
        riskTags = @($skill.riskTags)
        metrics = [pscustomobject][ordered]@{
            lines = $lines.Count
            bodyLines = $bodyLines.Count
            chars = $content.Length
            descriptionChars = $description.Length
            headings = $headings
            codeFences = $codeFences
            repeatedLongLines = $repeatedLongLines
        }
        audit = [pscustomobject][ordered]@{
            score = $score
            status = if ($notes.Count -eq 0) { 'compact' } elseif ($score -ge 25) { 'priority' } else { 'review' }
            notes = $notes
        }
    }
}

$summary = [pscustomobject][ordered]@{
    total = $rows.Count
    active = @($rows | Where-Object source -eq 'active').Count
    library = @($rows | Where-Object source -eq 'library').Count
    totalLines = ($rows.metrics.lines | Measure-Object -Sum).Sum
    totalChars = ($rows.metrics.chars | Measure-Object -Sum).Sum
    descriptionChars = ($rows.metrics.descriptionChars | Measure-Object -Sum).Sum
    oversized = @($rows | Where-Object { $_.metrics.lines -gt 200 }).Count
    extreme = @($rows | Where-Object { $_.metrics.lines -gt 400 }).Count
    longDescriptions = @($rows | Where-Object { $_.metrics.descriptionChars -gt 220 }).Count
    repeated = @($rows | Where-Object { $_.metrics.repeatedLongLines -gt 0 }).Count
    priority = @($rows | Where-Object { $_.audit.status -eq 'priority' }).Count
}

$payload = [pscustomobject][ordered]@{
    schemaVersion = 1
    generatedAt = (Get-Date).ToUniversalTime().ToString('o')
    catalogGeneratedAt = [string]$catalog.generatedAt
    summary = $summary
    skills = @($rows | Sort-Object @{ Expression = { $_.audit.score }; Descending = $true }, name)
}

$json = $payload | ConvertTo-Json -Depth 10
$utf8 = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $OutputDirectory 'audit.json'), $json, $utf8)
[IO.File]::WriteAllText((Join-Path $OutputDirectory 'data.js'), ('window.SKILL_LIBRARY_DATA = ' + $json + ';'), $utf8)

[pscustomobject]@{
    output = (Join-Path $OutputDirectory 'index.html')
    data = (Join-Path $OutputDirectory 'data.js')
    total = $summary.total
    active = $summary.active
    library = $summary.library
    priority = $summary.priority
    oversized = $summary.oversized
    longDescriptions = $summary.longDescriptions
} | ConvertTo-Json
