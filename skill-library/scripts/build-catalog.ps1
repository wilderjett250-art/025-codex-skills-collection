[CmdletBinding()]
param(
    [string]$SkillRoot = (Join-Path $env:USERPROFILE '.codex\skills'),
    [string]$LibraryRoot = (Join-Path $env:USERPROFILE '.codex\skill-library'),
    [string]$OutputPath = (Join-Path $env:USERPROFILE '.codex\skill-library\catalog.json'),
    [string]$ProfilePath = (Join-Path $env:USERPROFILE '.codex\skill-library\routing-profile.json')
)

$ErrorActionPreference = 'Stop'

$profile = if (Test-Path -LiteralPath $ProfilePath) {
    Get-Content -LiteralPath $ProfilePath -Raw | ConvertFrom-Json
} else {
    [pscustomobject]@{ skillOverrides = @() }
}
$skillOverrides = @{}
foreach ($item in @($profile.skillOverrides)) { $skillOverrides[[string]$item.name] = $item }

function Get-FrontMatterValue {
    param([string]$Content, [string]$Key)

    $front = [regex]::Match($Content, '(?s)\A---\s*\r?\n(.*?)\r?\n---')
    if (-not $front.Success) { return '' }
    $lines = @($front.Groups[1].Value -split "`r?`n")
    for ($index = 0; $index -lt $lines.Count; $index++) {
        $match = [regex]::Match($lines[$index], '^' + [regex]::Escape($Key) + ':\s*(.*)$')
        if (-not $match.Success) { continue }
        $value = $match.Groups[1].Value.Trim()
        if ($value -match '^[>|][+-]?$') {
            $parts = New-Object System.Collections.Generic.List[string]
            for ($next = $index + 1; $next -lt $lines.Count -and $lines[$next] -match '^\s+'; $next++) {
                if (-not [string]::IsNullOrWhiteSpace($lines[$next])) { $parts.Add($lines[$next].Trim()) }
            }
            return ($parts -join ' ')
        }
        return $value.Trim('"').Trim("'").Replace("''", "'")
    }
    return ''
}

function Get-Domain {
    param([string]$Name, [string]$Description)
    $text = (($Name + ' ' + $Description).ToLowerInvariant())
    $overrides = @{
        'skill-library-router' = 'project-flow'; 'syhprojectskill' = 'project-flow'
        'work-handoff' = 'project-flow'; 'large-project-ops' = 'project-flow'
        'local-experience' = 'project-flow'; 'terminal-ops' = 'project-flow'
        'workspace-surface-audit' = 'project-flow'; 'project-flow-ops' = 'project-flow'
        'project-readme-writer' = 'project-flow'; 'code-tour' = 'project-flow'
        'github-ops' = 'project-flow'; 'external-browser' = 'browser-desktop'
        'edge-assistant' = 'browser-desktop'; 'playwright' = 'browser-desktop'
        'screenshot' = 'browser-desktop'; 'windows-desktop-e2e' = 'browser-desktop'
        'ui-image-parity' = 'frontend-ui'; 'ui-ux-pro-max' = 'frontend-ui'
        'anthropic-frontend-design' = 'frontend-ui'; 'frontend-slides' = 'documents-media'
        'office-quality-gate' = 'documents-media'; 'dashiai-ppt' = 'documents-media'
        'academic-research-suite' = 'research-knowledge'; 'research-ops' = 'research-knowledge'
        'mcp-server-patterns' = 'ai-ml'; 'agent-architecture-audit' = 'ai-ml'
        'agent-evaluation' = 'ai-ml'; 'agent-harness-construction' = 'ai-ml'
        'agent-orchestration' = 'ai-ml'; 'prompt-optimizer' = 'ai-ml'
        'openai-media' = 'ai-ml'; 'autocad-cad-homework' = 'hardware-iot'
        'angular-developer' = 'frontend-ui'; 'react-engineering' = 'frontend-ui'
        'audit-design-system' = 'frontend-ui'; 'figma-create-design-system-rules' = 'frontend-ui'
        'figma-generate-design' = 'frontend-ui'; 'figma-implement-design' = 'frontend-ui'
        'figma-use' = 'frontend-ui'; 'figma-workflows' = 'frontend-ui'
        'impeccable' = 'frontend-ui'; 'sync-figma-token' = 'frontend-ui'
        'api-connector-builder' = 'backend-api'; 'api-design' = 'backend-api'
        'backend-patterns' = 'backend-api'; 'django-engineering' = 'backend-api'
        'fastapi-patterns' = 'backend-api'; 'laravel-engineering' = 'backend-api'
        'nestjs-patterns' = 'backend-api'; 'springboot-engineering' = 'backend-api'
        'aspnet-core' = 'backend-api'; 'quarkus-engineering' = 'backend-api'
        'jpa-patterns' = 'backend-api'; 'postgres-patterns' = 'data-database'
        'mysql-patterns' = 'data-database'; 'prisma-patterns' = 'data-database'
        'clickhouse-io' = 'data-database'; 'data-scraper-agent' = 'data-database'
        'artifact-tool-excel-legacy' = 'data-database'; 'configure-ecc' = 'project-flow'
        'coding-standards' = 'code-engineering'; 'csharp-testing' = 'code-engineering'
        'e2e-testing' = 'code-engineering'; 'tdd-workflow' = 'code-engineering'
        'qa-methodology' = 'security-quality'; 'constant-time-analysis' = 'security-quality'
        'carrier-relationship-management' = 'business-ops'; 'enterprise-agent-ops' = 'business-ops'
        'finance-billing-ops' = 'business-ops'; 'jira-integration' = 'business-ops'
        'google-workspace-ops' = 'business-ops'; 'laravel-plugin-discovery' = 'backend-api'
        'skill-stocktake' = 'project-flow'; 'research-paper-figures' = 'research-knowledge'
        'scripting-adb-for-ci' = 'mobile-interactive'; 'pixel2motion' = 'documents-media'
        'python-engineering' = 'code-engineering'; 'chatgpt-apps' = 'ai-ml'
        'regex-vs-llm-structured-text' = 'ai-ml'
        'evidence-based-acceptance' = 'security-quality'
    }
    if ($overrides.ContainsKey($Name)) { return $overrides[$Name] }

    if ($text -match '\b(android|ios|swift|kotlin|flutter|compose|unity|game|rpg)\b') { return 'mobile-interactive' }
    if ($text -match '\b(pdf|docx?|office|pptx?|slides?|photo|video|audio|speech|transcrib|media|image|camera|davinci|photoshop|darktable|blender|remotion|manim)\b') { return 'documents-media' }
    if ($text -match '\b(autocad|cad|iot|embedded|firmware|hardware|pcb|3d.print)\b') { return 'hardware-iot' }
    if ($text -match '\b(backend|api|server|django|fastapi|laravel|nestjs|springboot|asp\.net|quarkus|jpa|web.api|connector)\b') { return 'backend-api' }
    if ($text -match '\b(frontend|ui|ux|figma|design|css|react|vue|angular|canvas|logo|motion|web.site|web.ui|impeccable)\b') { return 'frontend-ui' }
    if ($text -match '\b(browser|playwright|edge|chrome|desktop|windows|webview|adb)\b') { return 'browser-desktop' }
    if ($text -match '\b(database|postgres|mysql|clickhouse|prisma|data|scrap|spreadsheet|analytics|dashboard|migration|etl)\b') { return 'data-database' }
    if ($text -match '\b(finance|billing|trade|market|sales|customer|carrier|logistics|inventory|content|social|seo|investor|product|commerce|email|messages|notion|jira|google.workspace|visa|customs|energy|supply.chain|returns)\b') { return 'business-ops' }
    if ($text -match '\b(deploy|docker|network|homelab|cisco|netmiko|production|latency|performance|systemd|ssh|runtime|infrastructure)\b') { return 'devops-runtime' }
    if ($text -match '\b(research|academic|scientific|literature|paper|knowledge|pubmed|uspto|experiment|citation)\b') { return 'research-knowledge' }
    if ($text -match '\b(python|java|rust|golang|go.engineering|csharp|\.net|cpp|perl|node|code|cli|programming|error|regex|algorithm|library)\b') { return 'code-engineering' }
    if ($text -match '\b(security|audit|scan|codeql|semgrep|yara|vulnerab|cryptograph|quality|qa\b|testing|test\b|tdd|compliance|risk.review|forensic)\b') { return 'security-quality' }
    if ($text -match '\b(ai|llm|agent|mcp|prompt|model|machine.learning|\bml\b|mle|openai|chatgpt|rag|foundation.model)\b') { return 'ai-ml' }
    return 'project-flow'
}

function Get-Layer1Domain {
    param([string]$Discipline)
    switch ($Discipline) {
        { $_ -in @('project-flow', 'code-engineering', 'frontend-ui', 'backend-api', 'data-database', 'devops-runtime', 'browser-desktop', 'ai-ml', 'mobile-interactive', 'security-quality') } { return 'computing-digital' }
        'hardware-iot' { return 'engineering-hardware' }
        'documents-media' { return 'documents-media' }
        'research-knowledge' { return 'research-education' }
        'business-ops' { return 'business-operations' }
        default { throw "No layer-1 domain mapping for discipline: $Discipline" }
    }
}

function Get-Plane {
    param([object]$Override)
    if ($null -ne $Override -and -not [string]::IsNullOrWhiteSpace([string]$Override.plane)) {
        return [string]$Override.plane
    }
    return 'domain'
}

function Get-Family {
    param([string]$Name, [string]$Description, [string]$Domain)
    $text = (($Name + ' ' + $Description).ToLowerInvariant())

    switch ($Domain) {
        'project-flow' {
            if ($text -match 'handoff|local.experience') { return 'continuity-memory' }
            if ($text -match 'skill|router|workspace|audit') { return 'skill-system' }
            if ($text -match 'terminal|github|code.tour') { return 'repo-execution' }
            return 'project-control'
        }
        'code-engineering' {
            if ($text -match 'test|tdd|standard|quality|error') { return 'code-quality' }
            if ($text -match 'python|java|rust|golang|csharp|cpp|perl|node') { return 'language-engineering' }
            return 'code-architecture'
        }
        'frontend-ui' {
            if ($text -match 'figma|design.system|token') { return 'design-system' }
            if ($text -match 'parity|screenshot|vue|react|angular|frontend') { return 'implementation-parity' }
            if ($text -match 'motion|logo|canvas|visual|open.design') { return 'visual-design' }
            return 'web-ui'
        }
        'backend-api' {
            if ($text -match 'fastapi|django|laravel|nestjs|spring|asp\.net|quarkus|jpa') { return 'framework-services' }
            if ($text -match 'connector|integration|provider|chatgpt.apps') { return 'connectors-integrations' }
            if ($text -match 'api|backend|server') { return 'api-contracts' }
            return 'service-implementation'
        }
        'data-database' {
            if ($text -match 'postgres|mysql|clickhouse|prisma|database|migration') { return 'database-schema' }
            if ($text -match 'scrap|retriev|collect|etl') { return 'collection-retrieval' }
            if ($text -match 'dashboard|analytics|spreadsheet|excel') { return 'analysis-reporting' }
            return 'data-processing'
        }
        'devops-runtime' {
            if ($text -match 'network|cisco|netmiko|homelab') { return 'network-infrastructure' }
            if ($text -match 'latency|performance|throughput|benchmark') { return 'performance-reliability' }
            if ($text -match 'deploy|docker|production|runtime|systemd') { return 'deployment-runtime' }
            return 'operations'
        }
        'browser-desktop' {
            if ($text -match 'external.browser|edge.assistant') { return 'authenticated-session' }
            if ($text -match 'playwright|e2e|browser') { return 'browser-automation' }
            if ($text -match 'screenshot|desktop|windows') { return 'desktop-capture' }
            return 'web-interaction'
        }
        'documents-media' {
            if ($text -match 'pdf|doc|office|word') { return 'documents-pdf' }
            if ($text -match 'ppt|slides|deck') { return 'presentations' }
            if ($text -match 'photo|image|portrait|photoshop|darktable') { return 'image-production' }
            if ($text -match 'video|motion|animation|remotion|davinci|blender') { return 'video-motion' }
            if ($text -match 'audio|speech|transcrib') { return 'audio-speech' }
            return 'creative-media'
        }
        'research-knowledge' {
            if ($text -match 'literature|academic|paper|scholar|pubmed|uspto') { return 'scholarly-research' }
            if ($text -match 'search|retriev|knowledge') { return 'retrieval-knowledge' }
            return 'research-production'
        }
        'ai-ml' {
            if ($text -match 'agent|evaluation|harness|orchestrat') { return 'agent-systems' }
            if ($text -match 'prompt|mcp|openai|chatgpt|llm|model') { return 'llm-integration' }
            if ($text -match 'media|manju') { return 'ai-media' }
            return 'ml-workflows'
        }
        'hardware-iot' {
            if ($text -match 'esp32|embedded|firmware|serial|esptool|device') { return 'embedded-device' }
            if ($text -match 'autocad|cad|3d.print') { return 'cad' }
            return 'device-operations'
        }
        'mobile-interactive' {
            if ($text -match 'unity|game|rpg') { return 'game-interaction' }
            if ($text -match 'android|kotlin|flutter|swift|ios|compose') { return 'mobile-native' }
            if ($text -match 'adb|device') { return 'device-automation' }
            return 'interactive-apps'
        }
        'security-quality' {
            if ($text -match 'security|codeql|semgrep|yara|vulnerab|cryptograph') { return 'security-analysis' }
            if ($text -match 'compliance|hipaa|supply.chain|risk') { return 'compliance-risk' }
            return 'quality-testing'
        }
        'business-ops' {
            if ($text -match 'market|content|social|seo|brand|article') { return 'content-marketing' }
            if ($text -match 'finance|billing|trade|investor') { return 'finance-trade' }
            if ($text -match 'customer|carrier|sales|lead') { return 'customer-revenue' }
            if ($text -match 'logistics|inventory|supply|returns') { return 'operations-logistics' }
            return 'business-productivity'
        }
        default { return 'general' }
    }
}

function Get-Tags {
    param([string]$Name, [string]$Description, [string]$Domain)
    $text = (($Name + ' ' + $Description).ToLowerInvariant())
    $rules = [ordered]@{
        'web' = '\b(web|browser|site|frontend|backend)\b'; 'api' = '\b(api|connector|integration)\b'
        'ui' = '\b(ui|ux|figma|design|css|visual)\b'; 'data' = '\b(data|database|sql|analytics|spreadsheet)\b'
        'automation' = '\b(automati|workflow|agent|orchestrat)\b'; 'testing' = '\b(test|qa|tdd|e2e|validation)\b'
        'security' = '\b(security|audit|scan|vulnerab|compliance)\b'; 'deployment' = '\b(deploy|docker|production|network|runtime)\b'
        'research' = '\b(research|academic|scientific|paper|citation)\b'; 'ai' = '\b(ai|llm|model|prompt|mcp|agent)\b'
        'document' = '\b(pdf|doc|office|slide|ppt|report)\b'; 'media' = '\b(image|photo|video|audio|speech|animation)\b'
        'mobile' = '\b(android|ios|flutter|kotlin|swift|unity)\b'; 'business' = '\b(market|finance|customer|sales|logistics|content|seo)\b'
        'hardware' = '\b(cad|hardware|iot|embedded|device)\b'
    }
    $tags = New-Object System.Collections.Generic.List[string]
    $tags.Add($Domain)
    foreach ($rule in $rules.GetEnumerator()) { if ($text -match $rule.Value) { $tags.Add($rule.Key) } }
    return @($tags | Select-Object -Unique | Select-Object -First 5)
}

function Get-Role {
    param([string]$Name, [string]$Description)
    return 'candidate'
}

function Get-SkillRecord {
    param([System.IO.DirectoryInfo]$Directory, [string]$Source, [string]$LeavesRoot)
    $skillPath = Join-Path $Directory.FullName 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skillPath)) { return $null }
    $raw = Get-Content -LiteralPath $skillPath -Raw
    $name = Get-FrontMatterValue -Content $raw -Key 'name'
    if ([string]::IsNullOrWhiteSpace($name)) { $name = $Directory.Name }
    $description = Get-FrontMatterValue -Content $raw -Key 'description'
    $override = if ($skillOverrides.ContainsKey($name)) { $skillOverrides[$name] } else { $null }
    $discipline = if ($null -ne $override -and -not [string]::IsNullOrWhiteSpace([string]$override.discipline)) {
        [string]$override.discipline
    } elseif ($null -ne $override -and -not [string]::IsNullOrWhiteSpace([string]$override.domain)) {
        # Backward compatibility for schema-1 routing profiles.
        [string]$override.domain
    } else {
        Get-Domain -Name $name -Description $description
    }
    $family = if ($null -ne $override -and -not [string]::IsNullOrWhiteSpace([string]$override.family)) {
        [string]$override.family
    } else {
        Get-Family -Name $name -Description $description -Domain $discipline
    }
    $plane = Get-Plane -Override $override
    $domain = if ($plane -eq 'control') { 'execution-governance' } else { Get-Layer1Domain -Discipline $discipline }
    $relativePath = if ($Source -eq 'library') { $Directory.FullName.Substring($LeavesRoot.Length).TrimStart('\', '/') } else { $Directory.Name }
    $canonicalPath = ($plane, $domain, $discipline, $family, $name) -join '/'
    return [pscustomobject][ordered]@{
        name = $name; directory = $Directory.Name; plane = $plane; domain = $domain; discipline = $discipline; family = $family
        canonicalPath = $canonicalPath
        tags = @(Get-Tags -Name $name -Description $description -Domain $discipline)
        aliases = if ($null -ne $override) { @($override.aliases) } else { @() }
        projectTypes = if ($null -ne $override) { @($override.projectTypes) } else { @() }
        phases = if ($null -ne $override) { @($override.phases) } else { @() }
        platforms = if ($null -ne $override) { @($override.platforms) } else { @() }
        riskTags = if ($null -ne $override) { @($override.riskTags) } else { @() }
        role = Get-Role -Name $name -Description $description
        source = $Source; relativePath = $relativePath; skillPath = $skillPath; trigger = $description
    }
}

$leavesRoot = Join-Path $LibraryRoot 'leaves'
$records = New-Object System.Collections.Generic.List[object]
foreach ($directory in @(Get-ChildItem -LiteralPath $SkillRoot -Directory -Force | Where-Object { $_.Name -ne '.system' })) {
    $record = Get-SkillRecord -Directory $directory -Source 'active' -LeavesRoot $leavesRoot
    if ($null -ne $record) { $records.Add($record) }
}
if (Test-Path -LiteralPath $leavesRoot) {
    foreach ($directory in @(Get-ChildItem -LiteralPath $leavesRoot -Directory -Force)) {
        $record = Get-SkillRecord -Directory $directory -Source 'library' -LeavesRoot $leavesRoot
        if ($null -ne $record) { $records.Add($record) }
    }
}

$invalid = @($records | Where-Object {
    [string]::IsNullOrWhiteSpace([string]$_.plane) -or
    [string]::IsNullOrWhiteSpace([string]$_.domain) -or
    [string]::IsNullOrWhiteSpace([string]$_.discipline) -or
    [string]::IsNullOrWhiteSpace([string]$_.family) -or
    [string]::IsNullOrWhiteSpace([string]$_.canonicalPath)
})
if ($invalid.Count -gt 0) {
    throw ('Every Skill must have one complete canonical path. Invalid: ' + (($invalid.name | Sort-Object) -join ', '))
}
$duplicatePaths = @($records | Group-Object canonicalPath | Where-Object { $_.Count -gt 1 })
if ($duplicatePaths.Count -gt 0) {
    throw ('Canonical Skill paths must be unique. Duplicates: ' + (($duplicatePaths.Name | Sort-Object) -join ', '))
}

$ordered = @($records | Sort-Object plane, domain, discipline, family, name, source)
$payload = [pscustomobject][ordered]@{
    schemaVersion = 4
    generatedAt = (Get-Date).ToUniversalTime().ToString('o')
    domains = @('computing-digital', 'engineering-hardware', 'documents-media', 'research-education', 'business-operations')
    controlDomains = @('execution-governance')
    skills = $ordered
}
$payload | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $OutputPath -Encoding UTF8

[pscustomobject]@{
    output = $OutputPath; total = $ordered.Count
    active = @($ordered | Where-Object { $_.source -eq 'active' }).Count
    library = @($ordered | Where-Object { $_.source -eq 'library' }).Count
    byPlane = @($ordered | Group-Object plane | Sort-Object Name | ForEach-Object { [pscustomobject]@{ plane = $_.Name; count = $_.Count } })
    byDomain = @($ordered | Group-Object { $_.plane + '/' + $_.domain } | Sort-Object Name | ForEach-Object { [pscustomobject]@{ domain = $_.Name; count = $_.Count } })
    byDiscipline = @($ordered | Group-Object { $_.plane + '/' + $_.domain + '/' + $_.discipline } | Sort-Object Name | ForEach-Object { [pscustomobject]@{ discipline = $_.Name; count = $_.Count } })
    byFamily = @($ordered | Group-Object { $_.plane + '/' + $_.domain + '/' + $_.discipline + '/' + $_.family } | Sort-Object Name | ForEach-Object { [pscustomobject]@{ family = $_.Name; count = $_.Count } })
} | ConvertTo-Json -Depth 4
