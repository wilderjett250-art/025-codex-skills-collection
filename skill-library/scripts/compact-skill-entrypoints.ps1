[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$CatalogPath = (Join-Path $env:USERPROFILE '.codex\skill-library\catalog.json')
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $CatalogPath)) {
    throw "Skill catalog is missing: $CatalogPath"
}

# Only routing prose is rewritten. Safety boundaries, required prerequisites, and
# neighboring-Skill exclusions are retained. Skill bodies receive whitespace-only
# normalization; no instruction, example, command, or reference is deleted.
$descriptionOverrides = [ordered]@{
    'drama' = 'Use only for AI-animated melodrama shorts or a named series continuation through Pika MCP, with recurring characters, narration, music, and synced captions. Skip celebrities, UGC ads, URL explainers, and podcasts.'
    'social' = 'Create, repurpose, schedule, or optimize organic social content and short-form scripts, or triage engagement. Use content-strategy for broad planning, ad-creative for paid ads, and public-relations for earned media.'
    'scripting-adb-for-ci' = 'Build reliable adb CI scripts: device fan-out, forward versus reverse, instrumentation status, sharding, real timeouts, transient retries, idempotent setup, cleanup, failure capture, and Android Test Orchestrator wiring.'
    'video' = 'Create or reproduce video with AI generators or programmatic frameworks, including avatars, explainers, demos, templates, and reference-style matching. Use social for posting strategy and ad-creative for paid ads.'
    'figma-generate-design' = 'Use with figma-use to build or update a complete Figma page, screen, modal, or multi-section view from code or a description. Reuse discovered design-system components, variables, styles, and tokens.'
    'generate-project-plan' = 'Create an interactive FigJam project-plan board from a PRD and codebase context, with per-section research and user confirmation before rendering content blocks and diagrams.'
    'product-description-generator' = 'Create or optimize e-commerce listings from product specs using competitor research, keyword gaps, and FABE copywriting. Produces titles, bullets, descriptions, and backend keywords for major marketplaces.'
    'figma-use' = 'Mandatory prerequisite before every use_figma call. Load it for Figma JavaScript reads or writes: inspect structure; create or edit nodes, variables, components, variants, auto-layout, fills, or property bindings.'
    'video-editor' = '用于 9:16 和 16:9 短视频剪辑、片头、动效、B-roll 合成和 Whisper 高亮字幕。触发后先确认只做字幕、标题、动画/整片，还是全流程；需要实拍素材时再调用 footage-finder。'
    'science-illustration-skill' = 'Create scientific paper figures, graphical abstracts, mechanism or workflow schematics, study designs, or model diagrams. Never fabricate data, plots, microscopy, gels, spectra, molecular structures, or measurements.'
    'darktable-editor' = 'Edit, develop, color-grade, tone-map, or export RAW photos through the dt-edit-mcp Darktable server. Uses XMP sidecars and rendered previews with a human approval step.'
    'edge-assistant' = 'Operate Microsoft Edge for visible or login-gated web tasks, cloud consoles, forms, and downloads, with external-result verification. Prefer a reliable API or CLI when it can complete the same task.'
    'photo-toolkit' = 'Convert RAW, JPG, or HEIC photos, create thumbnails and layout previews, filter by EXIF date, deflicker timelapse frames, or assemble frame video. Requires rawpy, Pillow, and NumPy; HEIC support is optional.'
    'figma-implement-design' = 'Implement production UI from Figma with visual fidelity when given a Figma link, component, or design-to-code request. For writes to the Figma canvas itself, use figma-use.'
    'figma-create-design-system-rules' = 'Create project-specific design-system rules for Figma-to-code workflows from the target codebase. Use when establishing or customizing those conventions; requires a Figma MCP connection.'
    'speech' = 'Generate text-to-speech narration, voiceovers, accessibility reads, audio prompts, or batches with the bundled OpenAI Audio CLI. Live calls require OPENAI_API_KEY; custom voice creation is out of scope.'
    'photo-grader' = 'Color-grade RAW, JPG, or HEIC photos with RawTherapee CLI and Lightroom-style JSON settings, including tone, HSL, lens correction, camera matching, batch work, timelapse consistency, and PP3 export.'
    'office-quality-gate' = 'Perform final QA or post-QA fixes for DOCX, PDF, XLSX, or PPTX, including rendering, accessibility, typography, formulas, citations, and handoff. It is not the normal file-generation engine.'
    'esp32-device-ops' = 'Identify, back up, flash, verify, or diagnose ESP32 and ESP32-S3 devices on Windows without confusing COM labels, logs, firmware state, and physical output.'
    'syhprojectskill' = 'Classify a confirmed project as coursework, commercial-small, special-large, or unknown, then emit a compact fingerprint for execution, Skill routing, validation depth, and handoff.'
    'wechat-miniprogram-engineering' = 'Trace, change, and verify native WeChat Mini Program behavior across app.json, pages, tabBar routes, handlers, requests, DevTools builds, uploads, and release boundaries. Skip ordinary mobile-native apps.'
    'frontend-design' = 'Design a new web UI or full visual redesign with a brief-specific direction and calibrated design dials while preserving existing product strengths. Skip minor polish, motion-only, Figma, Canva, and Sites tasks.'
    'research-paper-figures' = 'Plan, create, or review publication-quality research and thesis figures, experiment plots, result tables, model or method diagrams, architecture schematics, Mermaid diagrams, and captions.'
    'karpathy-llm-wiki' = 'Build, ingest, query, maintain, or lint a personal LLM-powered wiki or Karpathy-style knowledge base, including requests such as add to wiki or what do I know about.'
    'knowledge-ops' = 'Manage, ingest, sync, deduplicate, organize, or search a knowledge base spanning local files, MCP memory, vector stores, and Git repositories.'
    'photoshop-editing' = 'Operate the local Windows Photoshop installation for scripted PSD or image creation, layer and text edits, opening, saving, batch export, and bridge validation.'
    'skill-library-router' = 'Route each atomic intent in non-trivial local or compound work to a unique domain path and the best installed on-demand Skill.'
    'ui-ux-pro-max' = 'Query the local UI/UX database for design systems, palettes, typography, accessibility, charts, and stack-specific patterns. Use as evidence-backed design reference, not the default frontend builder.'
    'firecrawl-build' = 'Use only when Firecrawl is explicitly requested or already selected for application web search, scraping, extraction, or browser interaction. Skip ordinary research and generic web access.'
    'ui-demo' = 'Record a polished web-app demo, walkthrough, screen recording, or tutorial with Playwright, visible cursor, natural pacing, and WebM output.'
    'security-review' = 'Use only for an explicit security review, secure-by-default design, or hardening of authentication, inputs, secrets, APIs, payments, or sensitive data. Skip routine feature work without a security objective.'
    'workspace-surface-audit' = 'Audit a repository or Codex installation for MCPs, plugins, connectors, automations, hooks, prompts, permissions, Skill routing, environment state, secrets exposure, and harness risk.'
    'jupyter-notebook' = 'Create, scaffold, or edit Jupyter notebooks for experiments, explorations, and tutorials using the bundled template and new_notebook.py helper.'
    'ito-trade-planner' = 'Build a non-advisory prediction-market planning worksheet for Itô or venue workflows, covering venues, underliers, constraints, order prerequisites, and manual steps without placing or recommending trades.'
    'motion-ui' = 'Implement purposeful React or Next.js animation with Motion or Framer Motion for transitions, state changes, shared layout, and scroll effects with reduced-motion support. Skip CSS-only polish and non-React UI.'
    'x-api' = 'Integrate the X or Twitter API for authentication, tweets, threads, timelines, search, analytics, rate limits, and platform-native programmatic posting.'
    'ito-basket-compare' = 'Compare Itô prediction-market baskets with a user knowledge base, portfolio notes, watchlist, financial context, or research thesis for read-only gap analysis without advice or trading.'
    'code-tour' = 'Create persona-specific CodeTour .tour walkthroughs with real file and line anchors for onboarding, architecture, pull requests, root-cause analysis, or structured code explanations.'
    'prediction-market-risk-review' = 'Review prediction-market, basket, oracle, and trading-agent workflows for compliance, safety, data quality, privacy, and execution risk before handling venue auth, portfolios, keys, or trade plans.'
    'mle-workflow' = 'Engineer production ML systems with data contracts, reproducible training, model evaluation, deployment, monitoring, and rollback. Skip one-off notebook experiments.'
    'java-coding-standards' = 'Apply Java standards for Spring Boot and Quarkus services, including naming, immutability, Optional, streams, exceptions, generics, CDI, reactive patterns, and project layout.'
    'cost-tracking' = 'Report Claude Code token use, spending, and budgets from the local cost database by project, tool, session, or date.'
    'email-ops' = 'Triage mail, draft or send through the real mailbox, verify delivery, and perform sent-mail-safe follow-up with evidence.'
    'open-design' = 'Use only when Open Design is explicitly named, its catalogue must be browsed, or a named Open Design system or template must be bound to a project. Skip general UI and presentation work.'
    'python-engineering' = 'Implement, refactor, type, or test Python with idiomatic patterns, pytest fixtures, mocking, parametrization, TDD, and coverage. Prefer a framework Skill when Django or FastAPI controls the solution.'
    'automation-audit-ops' = 'Inventory automations, jobs, hooks, connectors, MCP servers, and wrappers; identify live, broken, redundant, or missing paths with evidence before changing them.'
    'django-engineering' = 'Design, implement, test, secure, migrate, or release Django and DRF systems. Load only the reference for the current concern; use generic Python guidance for non-Django work.'
    'unified-notifications-ops' = 'Operate and audit notification routing, deduplication, escalation, and inbox consolidation across GitHub, Linear, desktop alerts, hooks, and connected communication surfaces.'
    'laravel-engineering' = 'Design, implement, test, secure, or release Laravel systems using Eloquent, API patterns, Pest, or PHPUnit. Use laravel-plugin-discovery only to find or evaluate packages.'
    'performance-optimization' = 'Profile and fix game performance by frame-time budget and CPU/GPU bottleneck, then apply pooling, batching, allocation, GC, draw-call, or asset-budget changes. Use for low FPS, stutter, lag, or profiler work.'
    'design-game-design-fundamentals' = 'Design or review core game loops, feedback, player motivation, MDA, progression, difficulty, rewards, and other engine-independent game-design fundamentals.'
    'design-ui-ux-game' = 'Design game HUDs, menus, onboarding, feedback, accessibility, notifications, and other player-facing UI or UX patterns.'
    'game-ai' = 'Design engine-neutral NPC and enemy behavior with state machines, behavior trees, blackboards, steering, flocking, A-star pathfinding, patrol, or chase logic.'
    'game-ui-ux' = 'Build responsive game HUDs, menus, and overlays with scaling, safe areas, keyboard or gamepad focus, screen-state stacks, accessibility, and event-driven updates.'
    'rpg' = 'Build RPG or JRPG systems for stats, leveling, inventory, equipment, quests, branching dialogue, save/load, and combat.'
    'unity-animation' = 'Implement Unity character animation with Animator Controllers, states, transitions, parameters, blend trees, layers, Avatar IK, and scripted parameter updates.'
    'unity-build-pipeline' = 'Configure or automate Unity builds, scenes, player and quality settings, IL2CPP versus Mono, code stripping, BuildPipeline.BuildPlayer, CI, headless builds, and build size.'
    'unity-csharp-scripting' = 'Write or modify Unity C# gameplay scripts using MonoBehaviour lifecycle methods, components, coroutines, and Inspector serialization.'
    'unity-input-system' = 'Implement Unity Input System actions, action maps, PlayerInput, control schemes, rebinding, callbacks, and polling when the project uses .inputactions or com.unity.inputsystem.'
    'unity-navmesh' = 'Implement Unity AI navigation with NavMeshSurface baking, NavMeshAgent movement, destinations, dynamic obstacles, chase behavior, and pathfinding.'
    'unity-physics' = 'Implement Unity 3D physics with rigidbodies, forces, colliders, triggers, collisions, layers, raycasts, joints, kinematic behavior, and linear velocity.'
    'unity-scriptableobjects' = 'Design Unity data and decoupling with ScriptableObject config assets, shared runtime variables, event channels, runtime sets, registries, and CreateAssetMenu.'
    'unity-tilemap-2d' = 'Build Unity 2D tilemaps with Grid and Tilemap, palettes, colliders, rule or animated tiles, and runtime SetTile or GetTile generation.'
    'ghidra-headless' = 'Reverse-engineer compiled binaries with Ghidra headless analysis, including decompilation, functions, strings, symbols, and call graphs without the GUI.'
    'save-systems' = 'Design engine-neutral game save/load with serialization choices, formats, slots, atomic crash-safe writes, schema versioning, migration, autosave, and corruption handling.'
    'router' = 'Route game-development requests to the correct engine and specialist Skill for gameplay, levels, art, UI, physics, input, audio, saving, multiplayer, AI, genres, performance, or shipping.'
    'qa-methodology' = 'QA strategy, regression, automation, gates, risk-based and exploratory tests, mutation hardening, eval datasets, flaky-eval discipline, and SDET practice. Skip incident debugging, security design, and eval governance.'
    'photo-previewer' = 'Run a localhost-only web preview for comparing RAW grading results with original toggles, styles, grids, and mobile gestures before export. Requires Python 3.8+ and binds to 127.0.0.1.'
    'video-interaction-mapper' = 'Analyze a UI screen recording, extract key states and interaction triggers, then build an annotated Figma storyboard from uploaded frame captures. Use for video-to-Figma interaction mapping or design review.'
}

$catalog = Get-Content -LiteralPath $CatalogPath -Raw | ConvertFrom-Json
$pathsByName = @{}
foreach ($skill in @($catalog.skills)) { $pathsByName[[string]$skill.name] = [string]$skill.skillPath }

$changed = New-Object System.Collections.Generic.List[object]
$skipped = New-Object System.Collections.Generic.List[object]

foreach ($item in $descriptionOverrides.GetEnumerator()) {
    if (-not $pathsByName.ContainsKey($item.Key)) {
        $skipped.Add([pscustomobject]@{ name = $item.Key; reason = 'not-found' })
        continue
    }

    $path = $pathsByName[$item.Key]
    $content = [IO.File]::ReadAllText($path)
    $newline = if ($content.Contains("`r`n")) { "`r`n" } else { "`n" }
    $blockDescriptionMatch = [regex]::Match($content, '(?ms)^description:\s*[>|][+-]?\s*\r?\n(?:[ \t]+[^\r\n]*(?:\r?\n|$))+')
    $inlineDescriptionMatch = [regex]::Match($content, '(?m)^description:\s*([^\r\n]*)(?=\r?$)')
    $descriptionMatch = if ($blockDescriptionMatch.Success) { $blockDescriptionMatch } else { $inlineDescriptionMatch }
    if (-not $descriptionMatch.Success) {
        $skipped.Add([pscustomobject]@{ name = $item.Key; reason = 'description-not-found' })
        continue
    }

    $oldDescription = if ($blockDescriptionMatch.Success) {
        (($descriptionMatch.Value -split "`r?`n" | Select-Object -Skip 1 | ForEach-Object { $_.Trim() } | Where-Object { $_ }) -join ' ')
    } else {
        $descriptionMatch.Groups[1].Value.Trim().Trim('"').Trim("'")
    }
    $newDescription = [string]$item.Value
    if ($newDescription.Length -gt 220) {
        throw "Compact description exceeds 220 characters for $($item.Key): $($newDescription.Length)"
    }
    if ($newDescription.Length -ge $oldDescription.Length) {
        $skipped.Add([pscustomobject]@{ name = $item.Key; reason = 'not-shorter'; before = $oldDescription.Length; after = $newDescription.Length })
        continue
    }

    $yamlDescription = "description: '" + $newDescription.Replace("'", "''") + "'"
    $replacement = if ($blockDescriptionMatch.Success) { $yamlDescription + $newline } else { $yamlDescription }
    $updated = $content.Substring(0, $descriptionMatch.Index) + $replacement + $content.Substring($descriptionMatch.Index + $descriptionMatch.Length)
    if ($PSCmdlet.ShouldProcess($path, "compact description $($oldDescription.Length) -> $($newDescription.Length)")) {
        [IO.File]::WriteAllText($path, $updated, (New-Object System.Text.UTF8Encoding($false)))
    }
    $changed.Add([pscustomobject]@{ name = $item.Key; path = $path; before = $oldDescription.Length; after = $newDescription.Length; saved = $oldDescription.Length - $newDescription.Length })
}

# Whitespace-only normalization across every entrypoint is safe and idempotent.
$normalizedCount = 0
foreach ($skill in @($catalog.skills)) {
    $path = [string]$skill.skillPath
    $content = [IO.File]::ReadAllText($path)
    $newline = if ($content.Contains("`r`n")) { "`r`n" } else { "`n" }
    $normalized = [regex]::Replace($content, '(?m)[ \t]+$', '')
    $normalized = [regex]::Replace($normalized, '(?:\r?\n){3,}', $newline + $newline)
    $normalized = $normalized.TrimEnd("`r", "`n") + $newline
    if ($normalized -ne $content) {
        if ($PSCmdlet.ShouldProcess($path, 'normalize trailing whitespace and repeated blank lines')) {
            [IO.File]::WriteAllText($path, $normalized, (New-Object System.Text.UTF8Encoding($false)))
        }
        $normalizedCount += 1
    }
}

[pscustomobject][ordered]@{
    overrides = $descriptionOverrides.Count
    changed = $changed.Count
    savedDescriptionCharacters = ($changed.saved | Measure-Object -Sum).Sum
    normalizedEntrypoints = $normalizedCount
    skipped = $skipped.ToArray()
    changes = $changed.ToArray()
} | ConvertTo-Json -Depth 5
