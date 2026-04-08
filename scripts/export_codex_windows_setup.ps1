param(
    [string]$OutputDir = (Join-Path $HOME ("Desktop\kr-codex-setup-bundle-" + (Get-Date -Format "yyyyMMdd_HHmmss"))),
    [switch]$IncludePluginCache
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Copy-OptionalFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        return $false
    }

    $destinationDir = Split-Path -Parent $Destination
    if ($destinationDir) {
        New-Item -ItemType Directory -Force -Path $destinationDir | Out-Null
    }

    Copy-Item -LiteralPath $Source -Destination $Destination -Force
    return $true
}

function Copy-OptionalDirectory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        return $false
    }

    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
    return $true
}

function Get-CommandVersion {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        return $null
    }

    try {
        $result = & $command.Source @Args 2>$null
        return (($result | Select-Object -First 1) -join "").Trim()
    }
    catch {
        return $null
    }
}

$codexHome = Join-Path $HOME ".codex"
$agentsHome = Join-Path $HOME ".agents"
$bundleRoot = [System.IO.Path]::GetFullPath($OutputDir)
$bundleCodexHome = Join-Path $bundleRoot "home\.codex"
$bundleAgentsHome = Join-Path $bundleRoot "home\.agents"
$copiedEntries = New-Object System.Collections.Generic.List[string]

New-Item -ItemType Directory -Force -Path $bundleRoot | Out-Null

if (Copy-OptionalFile -Source (Join-Path $codexHome "config.toml") -Destination (Join-Path $bundleCodexHome "config.toml")) {
    $copiedEntries.Add(".codex/config.toml") | Out-Null
}
if (Copy-OptionalFile -Source (Join-Path $codexHome "AGENTS.md") -Destination (Join-Path $bundleCodexHome "AGENTS.md")) {
    $copiedEntries.Add(".codex/AGENTS.md") | Out-Null
}
if (Copy-OptionalDirectory -Source (Join-Path $codexHome "skills") -Destination (Join-Path $bundleCodexHome "skills")) {
    $copiedEntries.Add(".codex/skills/") | Out-Null
}
if (Copy-OptionalDirectory -Source (Join-Path $codexHome "superpowers") -Destination (Join-Path $bundleCodexHome "superpowers")) {
    $copiedEntries.Add(".codex/superpowers/") | Out-Null
}
if (Copy-OptionalDirectory -Source (Join-Path $agentsHome "skills") -Destination (Join-Path $bundleAgentsHome "skills")) {
    $copiedEntries.Add(".agents/skills/") | Out-Null
}
if (Copy-OptionalFile -Source (Join-Path $agentsHome ".skill-lock.json") -Destination (Join-Path $bundleAgentsHome ".skill-lock.json")) {
    $copiedEntries.Add(".agents/.skill-lock.json") | Out-Null
}
if ($IncludePluginCache -and (Copy-OptionalDirectory -Source (Join-Path $codexHome "plugins\cache") -Destination (Join-Path $bundleCodexHome "plugins\cache"))) {
    $copiedEntries.Add(".codex/plugins/cache/") | Out-Null
}

$versions = [ordered]@{
    codex = Get-CommandVersion -Name "codex" -Args @("--version")
    python = Get-CommandVersion -Name "python" -Args @("--version")
    git = Get-CommandVersion -Name "git" -Args @("--version")
    node = Get-CommandVersion -Name "node" -Args @("--version")
    claude = Get-CommandVersion -Name "claude" -Args @("--version")
    gemini = Get-CommandVersion -Name "gemini" -Args @("--version")
}

$envPresence = [ordered]@{}
foreach ($name in @("OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MISTRAL_API_KEY", "TAVILY_API_KEY")) {
    $envPresence[$name] = [bool](Test-Path -LiteralPath ("Env:\" + $name))
}

$manifest = [ordered]@{
    created_at = (Get-Date).ToString("o")
    bundle_root = $bundleRoot
    mode = "clean_bootstrap"
    copied_entries = $copiedEntries
    intentionally_excluded = @(
        ".codex/auth.json",
        ".codex/history.jsonl",
        ".codex/session_index.jsonl",
        ".codex/state_*.sqlite*",
        ".codex/logs_*.sqlite*",
        ".codex/cache/",
        ".codex/tmp/",
        ".codex/.tmp/",
        ".codex/.sandbox*"
    )
    optional_entries = @(".codex/plugins/cache/")
    tool_versions = $versions
    env_presence = $envPresence
}

$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $bundleRoot "manifest.json") -Encoding UTF8

$readme = @"
# KR Codex Windows Setup Bundle

This bundle is for a clean bootstrap on another Windows PC.

## Included

$(($copiedEntries | ForEach-Object { "- $_" }) -join [Environment]::NewLine)

## Intentionally Excluded

- `.codex/auth.json`
- session history, sqlite state, caches, sandbox artifacts
- repo files (clone KR separately from GitHub)
- secrets and API keys

## Restore On The Target Windows PC

1. Install `codex`, Python, Git, Node.js, `claude`, and `gemini`.
2. Copy `home\.codex\*` into `%USERPROFILE%\.codex\`.
3. Copy `home\.agents\*` into `%USERPROFILE%\.agents\`.
4. Recreate secrets with environment variables or a fresh KR `.env`.
5. Clone KR from GitHub.
6. Update `%USERPROFILE%\.codex\config.toml` trusted project entries if the new checkout path differs.
7. From the KR repo root, run:
   - `python scripts/check_codex_kr_setup.py`
   - `python scripts/check_codex_kr_setup.py --auth-preflight`

## Optional

- If you included `.codex/plugins/cache`, copy it into `%USERPROFILE%\.codex\plugins\cache\` to avoid re-downloading plugin cache data.
"@

$readme | Set-Content -LiteralPath (Join-Path $bundleRoot "README.md") -Encoding UTF8

Write-Host "Created KR Codex setup bundle at $bundleRoot"
