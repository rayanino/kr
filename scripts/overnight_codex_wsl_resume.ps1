param(
    [string]$Distro = "Ubuntu-24.04",
    [string]$RuntimeDir = "~/kr-codex",
    [switch]$RunShadowRehearsal,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Convert-WindowsPathToWsl {
    param([string]$Path)

    $resolved = (Resolve-Path -LiteralPath $Path).Path
    $drive = $resolved.Substring(0, 1).ToLowerInvariant()
    $rest = $resolved.Substring(2).Replace("\", "/")
    return "/mnt/$drive$rest"
}

function Convert-ToBashSingleQuoted {
    param([AllowNull()][string]$Value)

    if ($null -eq $Value) {
        return "''"
    }

    return "'" + ($Value -replace "'", "'""'""'") + "'"
}

function Invoke-Step {
    param(
        [string]$Description,
        [scriptblock]$Action
    )

    Write-Host "== $Description =="
    if ($DryRun) {
        return
    }
    & $Action
}

function Normalize-WslText {
    param([string]$Text)

    if ($null -eq $Text) {
        return ""
    }

    return ($Text -replace "`0", "").Trim()
}

function Invoke-WslBash {
    param(
        [string]$ResolvedDistro,
        [string]$Command
    )

    & wsl.exe -d $ResolvedDistro --cd / -e bash -lc $Command
    $exitCodeVar = Get-Variable -Name LASTEXITCODE -ErrorAction SilentlyContinue
    if ($exitCodeVar -and $exitCodeVar.Value -ne 0) {
        throw "WSL command failed with exit code $($exitCodeVar.Value)."
    }
}

function New-RuntimeDirScript {
    param([string]$RuntimeDirValue)

    return @'
RUNTIME_DIR=__KR_RUNTIME_DIR__
case "$RUNTIME_DIR" in
  '~') RUNTIME_DIR="$HOME" ;;
  '~/'*) RUNTIME_DIR="$HOME/${RUNTIME_DIR:2}" ;;
esac
'@.Replace("__KR_RUNTIME_DIR__", (Convert-ToBashSingleQuoted -Value $RuntimeDirValue))
}

function Resolve-WslRuntimeDir {
    param(
        [string]$ResolvedDistro,
        [string]$RuntimeDirValue
    )

    $resolveScript = @'
set -euo pipefail
__KR_RUNTIME_BLOCK__
printf '%s\n' "$RUNTIME_DIR"
'@
    $resolveScript = $resolveScript.Replace("__KR_RUNTIME_BLOCK__", (New-RuntimeDirScript -RuntimeDirValue $RuntimeDirValue))
    $resolvedPath = Normalize-WslText ((Invoke-WslBash -ResolvedDistro $ResolvedDistro -Command $resolveScript | Out-String))
    if (-not $resolvedPath) {
        throw "Unable to resolve the WSL runtime dir for $RuntimeDirValue."
    }
    return ($resolvedPath.Split("`n") | Select-Object -Last 1).Trim()
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$bootstrapPath = Convert-WindowsPathToWsl -Path (Join-Path $repoRoot "scripts/overnight_codex_wsl_bootstrap.sh")
$repoRootWsl = Convert-WindowsPathToWsl -Path $repoRoot
$homeWsl = Convert-WindowsPathToWsl -Path $HOME
$authority = Get-Content -Raw (Join-Path $repoRoot "ACTIVE_AUTHORITY.md")

if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw "wsl.exe is not available on PATH. Install WSL first."
}

Write-Host "Repo root: $repoRoot"
Write-Host "WSL distro request: $Distro"
Write-Host "Runtime dir: $RuntimeDir"
Write-Host

$statusOutput = ""
try {
    $statusOutput = Normalize-WslText ((& wsl.exe --status 2>&1 | Out-String))
} catch {
    $statusOutput = Normalize-WslText ($_ | Out-String)
}

if ($statusOutput -match "not installed|is not installed|optional component is not enabled") {
    throw "WSL is not active yet. Finish the Windows-side installation and reboot if required, then rerun this script."
}

$distrosOutput = ""
try {
    $distrosOutput = Normalize-WslText ((& wsl.exe --list --quiet 2>&1 | Out-String))
} catch {
    $distrosOutput = Normalize-WslText ($_ | Out-String)
}

$distros = $distrosOutput.Split("`n") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
$resolvedDistro = if ($distros -contains $Distro) {
    $Distro
} else {
    ($distros | Where-Object { $_ -like "Ubuntu*" } | Select-Object -First 1)
}

if (-not $resolvedDistro) {
    Invoke-Step "Launching Ubuntu 24.04 first-run setup" {
        ubuntu2404.exe
    }
    Write-Host
    Write-Host "If prompted, finish the first Linux user creation, close the Ubuntu window, and rerun this same command."
    exit 0
}

 $resolvedRuntimeDir = Resolve-WslRuntimeDir -ResolvedDistro $resolvedDistro -RuntimeDirValue $RuntimeDir
Write-Host "Resolved WSL distro: $resolvedDistro"
Write-Host "Resolved runtime dir: $resolvedRuntimeDir"
Write-Host

Invoke-Step "Bootstrapping WSL runtime clone" {
    $bootstrapCommand = "KR_WINDOWS_REPO={0} KR_WINDOWS_HOME={1} KR_WSL_RUNTIME_DIR={2} {3}" -f `
        (Convert-ToBashSingleQuoted -Value $repoRootWsl), `
        (Convert-ToBashSingleQuoted -Value $homeWsl), `
        (Convert-ToBashSingleQuoted -Value $resolvedRuntimeDir), `
        (Convert-ToBashSingleQuoted -Value $bootstrapPath)

    Invoke-WslBash -ResolvedDistro $resolvedDistro -Command $bootstrapCommand
}

if ($RunShadowRehearsal) {
    Invoke-Step "Running first shadow rehearsal" {
        $shadowTemplate = @'
set -euo pipefail
__KR_RUNTIME_BLOCK__
export KR_WINDOWS_HOME=__KR_WINDOWS_HOME__
cd "$RUNTIME_DIR" &&
python scripts/overnight_codex_task_generator.py --output overnight_codex/manifest.json &&
python scripts/overnight_codex_orchestrator.py --manifest overnight_codex/manifest.json --task val-contracts --hours 0.35
'@
        $shadowCommand = $shadowTemplate.Replace("__KR_RUNTIME_BLOCK__", (New-RuntimeDirScript -RuntimeDirValue $resolvedRuntimeDir))
        $shadowCommand = $shadowCommand.Replace("__KR_WINDOWS_HOME__", (Convert-ToBashSingleQuoted -Value $homeWsl))

        Invoke-WslBash -ResolvedDistro $resolvedDistro -Command $shadowCommand
    }
} else {
    Write-Host
    Write-Host "Shadow rehearsal not requested."
    Write-Host "Run this command when you want the first bounded rehearsal:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\overnight_codex_wsl_resume.ps1 -RunShadowRehearsal"
}

Write-Host
Write-Host "Authority snapshot:"
Write-Host $authority
