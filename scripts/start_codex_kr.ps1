param(
    [ValidateSet("kr_interactive", "kr_shadow", "kr_peer_review", "kr_research")]
    [string]$Profile = "kr_interactive",
    [switch]$NoLaunch,
    [switch]$RunAuthPreflight,
    [switch]$SkipSetupAudit,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CodexArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
}

function Resolve-PythonCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    $candidates = @(
        (Join-Path $RepoRoot ".venv\Scripts\python.exe"),
        (Join-Path $RepoRoot ".venv\bin\python")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        return $python.Source
    }

    throw "Python is not available. Install Python or create a repo-local .venv before launching KR Codex."
}

function Resolve-CodexCommand {
    $codex = Get-Command codex -ErrorAction SilentlyContinue
    if ($null -eq $codex) {
        throw "Codex CLI is not available in PATH."
    }
    return $codex.Source
}

function Get-AuthorityState {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    $authorityFile = Join-Path $RepoRoot "ACTIVE_AUTHORITY.md"
    if (-not (Test-Path -LiteralPath $authorityFile)) {
        throw "Missing ACTIVE_AUTHORITY.md at $authorityFile"
    }

    $state = @{
        active_authority = "unknown"
        runtime_mode = "unknown"
    }

    foreach ($line in Get-Content -LiteralPath $authorityFile) {
        if ($line -match "^\s*(active_authority|runtime_mode)\s*:\s*(.+?)\s*$") {
            $state[$Matches[1]] = $Matches[2]
        }
    }

    return $state
}

$repoRoot = Resolve-RepoRoot
$python = Resolve-PythonCommand -RepoRoot $repoRoot
$codex = Resolve-CodexCommand
$authority = Get-AuthorityState -RepoRoot $repoRoot
$env:PYTHONIOENCODING = "utf-8"

Push-Location $repoRoot
try {
    Write-Host "=== KR Codex Windows Launcher ==="
    Write-Host "Repo:            $repoRoot"
    Write-Host "Profile:         $Profile"
    Write-Host "Authority:       $($authority.active_authority)"
    Write-Host "Runtime mode:    $($authority.runtime_mode)"
    Write-Host "Python:          $python"
    Write-Host "Codex:           $codex"
    Write-Host

    if ($SkipSetupAudit -and $RunAuthPreflight) {
        Write-Warning "RunAuthPreflight was ignored because SkipSetupAudit was requested."
    }

    if (-not $SkipSetupAudit) {
        $auditArgs = @("scripts/check_codex_kr_setup.py")
        if ($RunAuthPreflight) {
            $auditArgs += "--auth-preflight"
        }

        Write-Host "Running KR Codex setup audit..."
        & $python @auditArgs
        $auditExit = $LASTEXITCODE
        if ($auditExit -ne 0) {
            throw "KR Codex setup audit failed with exit code $auditExit."
        }
        Write-Host
    }

    if ($NoLaunch) {
        Write-Host "Setup complete. Launch skipped because -NoLaunch was provided."
        return
    }

    $launchArgs = @("-p", $Profile)
    if ($CodexArgs) {
        $launchArgs += $CodexArgs
    }

    Write-Host "Launching Codex..."
    & $codex @launchArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
