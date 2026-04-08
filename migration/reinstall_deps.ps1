# ============================================================================
# KR Project — Dependency Reinstallation (PowerShell)
# ============================================================================
# Installs all required dependencies on a fresh Windows PC.
#
# Prerequisites: Python 3.13+, Node.js v24+, Git
#
# Usage:
#   .\migration\reinstall_deps.ps1 [-ProjectDir "C:\Users\You\Desktop\kr"]
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$ProjectDir = (Get-Location).Path
)

$ErrorActionPreference = "Continue"

function Log-Info  { param($msg) Write-Host "[INFO]  $msg" -ForegroundColor Cyan }
function Log-OK    { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Log-Warn  { param($msg) Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Log-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "=============================================" -ForegroundColor White
Write-Host "  KR Dependency Installation" -ForegroundColor White
Write-Host "  Project: $ProjectDir" -ForegroundColor White
Write-Host "=============================================" -ForegroundColor White
Write-Host ""

# ============================================================================
# PHASE 1: Verify prerequisites
# ============================================================================
Log-Info "=== Phase 1: Checking prerequisites ==="

$missing = 0

# Python
try {
    $pyVer = python --version 2>&1
    Log-OK "Python: $pyVer"
} catch {
    Log-Error "Python not found. Install from https://www.python.org (check 'Add to PATH')"
    $missing++
}

# Node.js
try {
    $nodeVer = node -v 2>&1
    Log-OK "Node.js: $nodeVer"
} catch {
    Log-Error "Node.js not found. Install from https://nodejs.org"
    $missing++
}

# npm
try {
    $npmVer = npm -v 2>&1
    Log-OK "npm: $npmVer"
} catch {
    Log-Error "npm not found (should come with Node.js)"
    $missing++
}

# Git
try {
    $gitVer = git --version 2>&1
    Log-OK "Git: $gitVer"
} catch {
    Log-Error "Git not found. Install from https://git-scm.com"
    $missing++
}

if ($missing -gt 0) {
    Log-Error "Missing $missing prerequisite(s). Install them and re-run."
    exit 1
}

# ============================================================================
# PHASE 2: Global npm packages
# ============================================================================
Log-Info ""
Log-Info "=== Phase 2: Installing global npm packages ==="

$npmPackages = @(
    "@google/gemini-cli@0.36.0",
    "@modelcontextprotocol/server-sequential-thinking@2025.12.18",
    "@openai/codex@0.118.0",
    "firecrawl-cli@1.11.2",
    "openclaw@2026.3.24",
    "pnpm@10.33.0",
    "promptfoo@0.121.3",
    "repomix@1.13.1",
    "tsx@4.21.0",
    "yarn@1.22.22"
)

foreach ($pkg in $npmPackages) {
    Log-Info "Installing $pkg..."
    $result = npm install -g $pkg 2>&1
    if ($LASTEXITCODE -eq 0) {
        Log-OK "  $pkg"
    } else {
        Log-Warn "  Failed: $pkg (may need manual install)"
    }
}

# ============================================================================
# PHASE 3: Python environment
# ============================================================================
Log-Info ""
Log-Info "=== Phase 3: Setting up Python environment ==="

Push-Location $ProjectDir

$makefileExists = Test-Path "Makefile"
$requirementsExists = Test-Path "requirements.txt"

if ($requirementsExists) {
    Log-Info "Creating virtual environment..."
    python -m venv .venv

    # Activate venv
    $activateScript = Join-Path ".venv" "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
        Log-OK "Virtual environment activated"
    } else {
        Log-Warn "Could not activate venv. Run manually: .\.venv\Scripts\Activate.ps1"
    }

    Log-Info "Installing Python packages from requirements.txt..."
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        $pkgCount = (pip list 2>$null | Measure-Object -Line).Lines
        Log-OK "Installed $pkgCount Python packages"
    } else {
        Log-Warn "Some packages may have failed. Check output above."
    }
} else {
    Log-Warn "No requirements.txt found at $ProjectDir"
}

Pop-Location

# ============================================================================
# PHASE 4: Claude Code CLI
# ============================================================================
Log-Info ""
Log-Info "=== Phase 4: Claude Code CLI ==="

$claudePath = Get-Command claude -ErrorAction SilentlyContinue
if ($claudePath) {
    $claudeVer = claude --version 2>&1
    Log-OK "Claude Code already installed: $claudeVer"
} else {
    Log-Info "Installing Claude Code CLI..."
    npm install -g @anthropic-ai/claude-code
    if ($LASTEXITCODE -eq 0) {
        Log-OK "Claude Code CLI installed"
    } else {
        Log-Warn "Could not install via npm. Try: npm install -g @anthropic-ai/claude-code"
        Log-Warn "Or download from: https://claude.ai/code"
    }
}

# ============================================================================
# PHASE 5: Verify coworker CLIs
# ============================================================================
Log-Info ""
Log-Info "=== Phase 5: Verifying coworker CLIs ==="

$coworkers = @("codex", "gemini")
foreach ($tool in $coworkers) {
    $cmd = Get-Command $tool -ErrorAction SilentlyContinue
    if ($cmd) {
        Log-OK "$tool CLI: installed at $($cmd.Source)"
    } else {
        Log-Warn "$tool CLI not found. Should have been installed in Phase 2."
    }
}

# ============================================================================
# PHASE 6: Environment variables
# ============================================================================
Log-Info ""
Log-Info "=== Phase 6: Environment variables ==="

Write-Host ""
Write-Host "  The following env vars may need to be set." -ForegroundColor Yellow
Write-Host "  Set them via: System Settings > Environment Variables" -ForegroundColor Yellow
Write-Host "  Or in PowerShell profile (~\Documents\PowerShell\Microsoft.PowerShell_profile.ps1):" -ForegroundColor Yellow
Write-Host ""
Write-Host '  $env:TAVILY_API_KEY = "your-key-here"'
Write-Host '  $env:MEMORY_FILE_PATH = "$env:USERPROFILE\.claude-memory\kr-engine.jsonl"'
Write-Host '  $env:CLAUDE_AUTOCOMPACT_PCT_OVERRIDE = "60"'
Write-Host '  $env:CLAUDE_CODE_SUBPROCESS_ENV_SCRUB = "1"'
Write-Host '  $env:CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING = "1"'
Write-Host '  $env:MAX_THINKING_TOKENS = "128000"'
Write-Host ""

# Create MCP memory directory
$memoryDir = Join-Path $env:USERPROFILE ".claude-memory"
if (-not (Test-Path $memoryDir)) {
    New-Item -ItemType Directory -Path $memoryDir -Force | Out-Null
    Log-OK "Created $memoryDir"
} else {
    Log-OK "$memoryDir already exists"
}

# Check for .env template
$envTemplate = Join-Path $ProjectDir ".env.template"
if (Test-Path $envTemplate) {
    Log-Info "Found .env.template. Copy it and fill in your API keys:"
    Write-Host "  Copy-Item .env.template .env"
}

# ============================================================================
# Summary
# ============================================================================
Write-Host ""
Write-Host "=============================================" -ForegroundColor White
Write-Host "  Installation Complete" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor White
Write-Host ""
Write-Host "  NEXT:"
Write-Host "  1. Set environment variables (see Phase 6 above)"
Write-Host "  2. Login: claude login"
Write-Host "  3. Launch: cd $ProjectDir; claude"
Write-Host ""
