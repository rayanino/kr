# ============================================================================
# KR Project — Claude Code Environment Restore (PowerShell)
# ============================================================================
# Restores a Claude Code environment backup to a new Windows PC.
#
# Usage:
#   .\migration\restore_claude_env.ps1 -BackupDir "C:\Users\You\Desktop\claude-code-backup-migration" -ProjectPath "C:\Users\You\Desktop\kr"
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupDir,

    [Parameter(Mandatory=$false)]
    [string]$ProjectPath = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

# --- Helpers ---
function Log-Info  { param($msg) Write-Host "[INFO]  $msg" -ForegroundColor Cyan }
function Log-OK    { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Log-Warn  { param($msg) Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Log-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

# --- Configuration ---
$ClaudeDir = Join-Path $env:USERPROFILE ".claude"
$NewUser = $env:USERNAME
$NewHome = $env:USERPROFILE
$OldUser = "Rayane"
$OldHome = "C:\Users\Rayane"

# Try to read old user from metadata
$metaFile = Join-Path $BackupDir "environment_metadata.json"
if (Test-Path $metaFile) {
    try {
        $meta = Get-Content $metaFile -Raw | ConvertFrom-Json
        $OldUser = $meta.source_user
        $OldHome = $meta.source_home -replace '/', '\'
        Log-Info "Old environment: user=$OldUser, home=$OldHome"
    } catch {
        Log-Warn "Could not parse environment_metadata.json. Using defaults."
    }
}

# Build project directory name mapping
# C:\Users\Rayane\Desktop\kr -> C--Users-Rayane-Desktop-kr
$OldKrDirName = "C--Users-Rayane-Desktop-kr"
$NormalizedProjectPath = $ProjectPath -replace '\\', '-' -replace ':', '-' -replace '^-', ''
# Handle drive letter: C-\Users -> C--Users
$NewKrDirName = ($ProjectPath -replace '\\', '-') -replace '^([A-Z])-', '$1--' -replace ':', ''

Write-Host ""
Write-Host "=============================================" -ForegroundColor White
Write-Host "  Claude Code Environment Restore" -ForegroundColor White
Write-Host "=============================================" -ForegroundColor White
Write-Host ""
Write-Host "  Backup source:    $BackupDir"
Write-Host "  Target:           $ClaudeDir"
Write-Host "  Old user:         $OldUser"
Write-Host "  New user:         $NewUser"
Write-Host "  Old KR dir name:  $OldKrDirName"
Write-Host "  New KR dir name:  $NewKrDirName"
Write-Host ""

# --- Safety check ---
if (Test-Path $ClaudeDir) {
    $size = (Get-ChildItem $ClaudeDir -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round($size / 1MB, 1)
    Log-Warn "~/.claude/ already exists ($sizeMB MB). Files will be merged."
    $confirm = Read-Host "Continue? (y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Log-Info "Aborted."
        exit 0
    }
}

# --- Verify backup ---
$criticalDir = Join-Path $BackupDir "critical"
if (-not (Test-Path $criticalDir)) {
    # Maybe the archives need extracting first
    $criticalArchive = Get-ChildItem $BackupDir -Filter "claude-env-CRITICAL-*.tar.gz" | Select-Object -First 1
    $fullArchive = Get-ChildItem $BackupDir -Filter "claude-env-FULL-*.tar.gz" | Select-Object -First 1

    if ($fullArchive) {
        Log-Info "Extracting FULL archive: $($fullArchive.Name)..."
        tar -xzf $fullArchive.FullName -C $BackupDir
        Log-OK "Extracted"
    } elseif ($criticalArchive) {
        Log-Info "Extracting CRITICAL archive: $($criticalArchive.Name)..."
        tar -xzf $criticalArchive.FullName -C $BackupDir
        Log-OK "Extracted"
    }
}

if (-not (Test-Path $criticalDir)) {
    Log-Error "No 'critical' directory found in backup. Check that backup is complete."
    exit 1
}

# ============================================================================
# PHASE 1: Restore CRITICAL files
# ============================================================================
Log-Info "=== Phase 1: Restoring CRITICAL files ==="

if (-not (Test-Path $ClaudeDir)) { New-Item -ItemType Directory -Path $ClaudeDir -Force | Out-Null }

# 1a. Settings and standalone files
$standaloneFiles = @(
    "settings.json", "settings.local.json",
    "settings.json.bak", "settings.json.bak.20260330",
    "settings.json.orig", "settings.local.json.bak.20260330",
    "session_state.json", "package.json", "gsd-file-manifest.json",
    "statusline-command.sh"
)

foreach ($f in $standaloneFiles) {
    $src = Join-Path $criticalDir $f
    if (Test-Path $src) {
        Copy-Item $src -Destination (Join-Path $ClaudeDir $f) -Force
        Log-OK "  $f"
    }
}

# 1b. Hooks
$hooksDir = Join-Path $criticalDir "hooks"
if (Test-Path $hooksDir) {
    $targetHooks = Join-Path $ClaudeDir "hooks"
    if (-not (Test-Path $targetHooks)) { New-Item -ItemType Directory -Path $targetHooks -Force | Out-Null }
    Copy-Item "$hooksDir\*" -Destination $targetHooks -Recurse -Force
    $hookCount = (Get-ChildItem $targetHooks -File -Recurse).Count
    Log-OK "  hooks/ ($hookCount files)"
}

# 1c. KR project memory (the most irreplaceable data)
$krMemoryDir = Join-Path $criticalDir "kr-memory"
if (Test-Path $krMemoryDir) {
    $memoryTarget = Join-Path $ClaudeDir "projects\$NewKrDirName\memory"
    if (-not (Test-Path $memoryTarget)) { New-Item -ItemType Directory -Path $memoryTarget -Force | Out-Null }
    Copy-Item "$krMemoryDir\*" -Destination $memoryTarget -Force
    $memCount = (Get-ChildItem $memoryTarget -File).Count
    Log-OK "  KR memory: $memCount files -> projects\$NewKrDirName\memory\"
}

# 1d. Agents
foreach ($dir in @("agents", ".agents")) {
    $src = Join-Path $criticalDir $dir
    if (Test-Path $src) {
        $target = Join-Path $ClaudeDir $dir
        if (-not (Test-Path $target)) { New-Item -ItemType Directory -Path $target -Force | Out-Null }
        Copy-Item "$src\*" -Destination $target -Recurse -Force
        Log-OK "  $dir/"
    }
}

# 1e. Plugin manifests
$pluginsSrc = Join-Path $criticalDir "plugins"
if (Test-Path $pluginsSrc) {
    $pluginsTarget = Join-Path $ClaudeDir "plugins"
    if (-not (Test-Path $pluginsTarget)) { New-Item -ItemType Directory -Path $pluginsTarget -Force | Out-Null }
    Copy-Item "$pluginsSrc\*" -Destination $pluginsTarget -Force
    Log-OK "  plugins/ (manifests)"
}

# ============================================================================
# PHASE 2: Restore IMPORTANT files
# ============================================================================
$importantDir = Join-Path $BackupDir "important"
if (Test-Path $importantDir) {
    Log-Info ""
    Log-Info "=== Phase 2: Restoring IMPORTANT files ==="

    $importantFiles = @("history.jsonl", "stats-cache.json", "performance.csv", "changes.log")
    foreach ($f in $importantFiles) {
        $src = Join-Path $importantDir $f
        if (Test-Path $src) {
            Copy-Item $src -Destination (Join-Path $ClaudeDir $f) -Force
            Log-OK "  $f"
        }
    }

    $importantDirs = @("tasks", "plans", "teams", "sessions", "commands", "skills", "scripts", "get-shit-done", "todos")
    foreach ($d in $importantDirs) {
        $src = Join-Path $importantDir $d
        if (Test-Path $src) {
            $target = Join-Path $ClaudeDir $d
            if (-not (Test-Path $target)) { New-Item -ItemType Directory -Path $target -Force | Out-Null }
            Copy-Item "$src\*" -Destination $target -Recurse -Force
            $count = (Get-ChildItem $target -File -Recurse -ErrorAction SilentlyContinue).Count
            Log-OK "  $d/ ($count files)"
        }
    }
} else {
    Log-Warn "No important/ directory in backup. Skipping Phase 2."
}

# ============================================================================
# PHASE 3: Restore session data
# ============================================================================
$sessionsDir = Join-Path $BackupDir "sessions\projects"
if (Test-Path $sessionsDir) {
    Log-Info ""
    Log-Info "=== Phase 3: Restoring session data ==="

    $projectsTarget = Join-Path $ClaudeDir "projects"
    if (-not (Test-Path $projectsTarget)) { New-Item -ItemType Directory -Path $projectsTarget -Force | Out-Null }

    $projDirs = Get-ChildItem $sessionsDir -Directory
    foreach ($proj in $projDirs) {
        $projName = $proj.Name
        $newProjName = $projName -replace [regex]::Escape($OldKrDirName), $NewKrDirName

        if ($projName -ne $newProjName) {
            Log-Info "  Remapping: $projName -> $newProjName"
        }

        $target = Join-Path $projectsTarget $newProjName
        if (-not (Test-Path $target)) {
            Copy-Item $proj.FullName -Destination $target -Recurse -Force
        } else {
            # Merge without overwriting (especially memory files)
            Get-ChildItem $proj.FullName | ForEach-Object {
                $dest = Join-Path $target $_.Name
                if (-not (Test-Path $dest)) {
                    Copy-Item $_.FullName -Destination $dest -Recurse -Force
                }
            }
        }
    }

    $projCount = (Get-ChildItem $projectsTarget -Directory).Count
    Log-OK "  Restored $projCount project directories"
} else {
    Log-Warn "No sessions/ directory in backup. Skipping Phase 3."
}

# ============================================================================
# PHASE 4: Path remapping
# ============================================================================
Log-Info ""
Log-Info "=== Phase 4: Path remapping ==="

if ($OldUser -ne $NewUser) {
    Log-Info "Username changed: $OldUser -> $NewUser. Remapping paths..."

    $filesToRemap = @(
        (Join-Path $ClaudeDir "settings.json"),
        (Join-Path $ClaudeDir "settings.local.json"),
        (Join-Path $ClaudeDir "statusline-command.sh"),
        (Join-Path $ClaudeDir "plugins\installed_plugins.json"),
        (Join-Path $ClaudeDir "plugins\known_marketplaces.json")
    )

    foreach ($filepath in $filesToRemap) {
        if (Test-Path $filepath) {
            $content = Get-Content $filepath -Raw -Encoding UTF8
            $changed = $false

            # Replace forward-slash paths (C:/Users/Rayane/)
            if ($content -match "C:/Users/$OldUser/") {
                $content = $content -replace "C:/Users/$OldUser/", "C:/Users/$NewUser/"
                $changed = $true
            }

            # Replace backslash-escaped paths (C:\\Users\\Rayane\\)
            if ($content -match "C:\\\\Users\\\\$OldUser\\\\") {
                $content = $content -replace "C:\\\\Users\\\\$OldUser\\\\", "C:\\\\Users\\\\$NewUser\\"
                $changed = $true
            }

            # Replace single-backslash paths (C:\Users\Rayane\)
            if ($content -match "C:\\Users\\$OldUser\\") {
                $content = $content -replace [regex]::Escape("C:\Users\$OldUser\"), "C:\Users\$NewUser\"
                $changed = $true
            }

            if ($changed) {
                Set-Content $filepath -Value $content -Encoding UTF8 -NoNewline
                Log-OK "  Remapped: $(Split-Path $filepath -Leaf)"
            }
        }
    }
} else {
    Log-OK "Username unchanged ($NewUser). No path remapping needed."
}

# ============================================================================
# PHASE 5: Verification
# ============================================================================
Log-Info ""
Log-Info "=== Phase 5: Verification ==="

$errors = 0

# Check critical files
foreach ($f in @("settings.json", "settings.local.json")) {
    if (Test-Path (Join-Path $ClaudeDir $f)) {
        Log-OK "  $f exists"
    } else {
        Log-Error "  $f MISSING"
        $errors++
    }
}

# Check hooks
$hooksTarget = Join-Path $ClaudeDir "hooks"
if (Test-Path $hooksTarget) {
    $hookCount = (Get-ChildItem $hooksTarget -File -Recurse).Count
    Log-OK "  hooks/ ($hookCount files)"
} else {
    Log-Warn "  hooks/ missing"
}

# Check KR memory
$krMemTarget = Join-Path $ClaudeDir "projects\$NewKrDirName\memory"
if (Test-Path $krMemTarget) {
    $memCount = (Get-ChildItem $krMemTarget -File).Count
    Log-OK "  KR memory: $memCount files"
} else {
    Log-Error "  KR memory directory MISSING at: $krMemTarget"
    $errors++
}

# Check for stale old paths in settings
$settingsContent = Get-Content (Join-Path $ClaudeDir "settings.json") -Raw -ErrorAction SilentlyContinue
if ($settingsContent -and $settingsContent -match "Users/$OldUser/" -and $OldUser -ne $NewUser) {
    Log-Warn "  settings.json still contains old user paths"
} else {
    Log-OK "  No stale path references"
}

Write-Host ""
if ($errors -eq 0) {
    Write-Host "  Restore complete - no errors" -ForegroundColor Green
} else {
    Write-Host "  Restore complete with $errors error(s)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor White
Write-Host "  NEXT STEPS" -ForegroundColor White
Write-Host "=============================================" -ForegroundColor White
Write-Host ""
Write-Host "  1. Install dependencies:"
Write-Host "     .\migration\reinstall_deps.ps1"
Write-Host ""
Write-Host "  2. Login to Claude Code:"
Write-Host "     claude login"
Write-Host ""
Write-Host "  3. Launch Claude Code:"
Write-Host "     cd $ProjectPath; claude"
Write-Host ""
