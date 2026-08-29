param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Error "npx not found. Install Node.js/npm first."
}

& npx --yes --package @playwright/cli playwright-cli @ArgsList
exit $LASTEXITCODE
