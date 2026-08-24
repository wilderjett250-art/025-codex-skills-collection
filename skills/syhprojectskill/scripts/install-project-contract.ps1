[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'

$resolvedRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
if (-not (Test-Path -LiteralPath $resolvedRoot -PathType Container)) {
    throw "Project root is not a directory: $ProjectRoot"
}

$artifacts = [ordered]@{
    'AGENTS.md' = @'
# Project Operating Contract

## Scope and sources

- Treat this root as the project boundary unless the user confirms another boundary.
- Read the applicable root or module `AGENTS.md`, compact `PROJECT_PROFILE.md`, and only the relevant `HANDOFF.md` section before non-trivial work.
- Prefer current source, runtime, command output, and user-provided artifacts over old notes.

## Changes and evidence

- Inspect the current implementation and Git state before changing existing work.
- Preserve unrelated files and user changes. Make the smallest change that satisfies the confirmed task.
- Run the smallest relevant validation, and distinguish local, remote, and real-user acceptance.

## Safety and continuity

- Never copy, expose, or commit passwords, tokens, cookies, private keys, or secret values.
- Confirm exact target and scope before irreversible, external, permission, deployment, publication, or deletion actions.
- At meaningful handoff points, update `HANDOFF.md` with verified state, evidence, risks, and the next safe action.

## Project-specific rules

- Record only stable constraints that change normal task decisions.
'@
    'PROJECT_PROFILE.md' = @'
# Project Profile

- Project:
- Root:
- Category: unknown
- Capability tags: unknown
- Risk level: unknown
- Repository and branch:
- Runtime or submission target:
- Data or device boundary:
- Required technology or algorithm route:
- Required validation:
- Required handoff artifact:
- Out-of-scope systems:
- Profile verified:

## Evidence

- Confirmed sources:
- Open classification questions:

## Skill routing hints

- Prefer:
- Escalate to:
- Avoid unless the task requires it:
'@
    'HANDOFF.md' = @'
# Handoff

## Current state

- Verified at:
- Completed:
- Current behavior or deployment state:
- Uncommitted or unpushed work:

## Evidence

- Files and revisions:
- Commands, tests, or live checks:
- External confirmations:

## Risks and boundaries

- Not verified:
- Required user input or authorization:
- Rollback or recovery reference:

## Next safe action

- Action:
- Acceptance evidence:
'@
}

$plan = foreach ($artifact in $artifacts.GetEnumerator()) {
    $target = Join-Path -Path $resolvedRoot -ChildPath $artifact.Key
    [pscustomobject]@{
        File = $target
        Action = if (Test-Path -LiteralPath $target) { 'preserve-existing' } elseif ($Apply) { 'create' } else { 'would-create' }
    }
}

$plan | Format-Table -AutoSize

if (-not $Apply) {
    Write-Output 'Preview only. Re-run with -Apply after confirming this project root.'
    return
}

$utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
foreach ($artifact in $artifacts.GetEnumerator()) {
    $target = Join-Path -Path $resolvedRoot -ChildPath $artifact.Key
    if (-not (Test-Path -LiteralPath $target)) {
        [System.IO.File]::WriteAllText($target, $artifact.Value, $utf8WithoutBom)
    }
}

Write-Output 'Created only missing contract files. Existing project files were preserved.'
