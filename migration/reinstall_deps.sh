#!/usr/bin/env bash
# ============================================================================
# KR Project — Dependency Reinstallation Script
# ============================================================================
# Installs all required dependencies for the KR project on a fresh PC.
# Run this AFTER restoring the Claude Code environment.
#
# Prerequisites:
#   - Python 3.13+ installed
#   - Node.js v24+ installed
#   - Git installed
#
# Usage:
#   bash migration/reinstall_deps.sh [project_dir]
# ============================================================================

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${CYAN}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

PROJECT_DIR="${1:-$(pwd)}"

echo ""
echo "============================================="
echo "  KR Dependency Installation"
echo "  Project: $PROJECT_DIR"
echo "============================================="
echo ""

# ============================================================================
# PHASE 1: Verify prerequisites
# ============================================================================
log_info "=== Phase 1: Checking prerequisites ==="

MISSING=0

# Python
if command -v python &> /dev/null; then
    PY_VER=$(python --version 2>&1)
    log_ok "Python: $PY_VER"
else
    log_error "Python not found. Install Python 3.13+ from https://www.python.org"
    MISSING=1
fi

# Node.js
if command -v node &> /dev/null; then
    NODE_VER=$(node -v)
    log_ok "Node.js: $NODE_VER"
else
    log_error "Node.js not found. Install from https://nodejs.org"
    MISSING=1
fi

# npm
if command -v npm &> /dev/null; then
    NPM_VER=$(npm -v)
    log_ok "npm: $NPM_VER"
else
    log_error "npm not found (should come with Node.js)"
    MISSING=1
fi

# Git
if command -v git &> /dev/null; then
    GIT_VER=$(git --version)
    log_ok "Git: $GIT_VER"
else
    log_error "Git not found. Install from https://git-scm.com"
    MISSING=1
fi

if [ "$MISSING" -eq 1 ]; then
    log_error "Missing prerequisites. Install them and re-run this script."
    exit 1
fi

# ============================================================================
# PHASE 2: Global npm packages
# ============================================================================
log_info ""
log_info "=== Phase 2: Installing global npm packages ==="

NPM_PACKAGES=(
    "@google/gemini-cli@0.36.0"
    "@modelcontextprotocol/server-sequential-thinking@2025.12.18"
    "@openai/codex@0.118.0"
    "firecrawl-cli@1.11.2"
    "openclaw@2026.3.24"
    "pnpm@10.33.0"
    "promptfoo@0.121.3"
    "repomix@1.13.1"
    "tsx@4.21.0"
    "yarn@1.22.22"
)

for pkg in "${NPM_PACKAGES[@]}"; do
    PKG_NAME=$(echo "$pkg" | sed 's/@[^@]*$//')
    log_info "Installing $pkg..."
    if npm install -g "$pkg" 2>/dev/null; then
        log_ok "  $pkg"
    else
        log_warn "  Failed to install $pkg — may need manual install"
    fi
done

# ============================================================================
# PHASE 3: Python environment
# ============================================================================
log_info ""
log_info "=== Phase 3: Setting up Python environment ==="

cd "$PROJECT_DIR"

if [ -f "Makefile" ]; then
    log_info "Running 'make install'..."
    if make install; then
        log_ok "Python environment created via Makefile"
    else
        log_warn "Makefile install failed. Trying manual setup..."
        python -m venv .venv
        source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
        pip install -r requirements.txt
        log_ok "Python environment created manually"
    fi
elif [ -f "requirements.txt" ]; then
    log_info "Creating virtual environment..."
    python -m venv .venv
    source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
    pip install -r requirements.txt
    log_ok "Python environment created from requirements.txt"
else
    log_warn "No Makefile or requirements.txt found. Skipping Python setup."
fi

# ============================================================================
# PHASE 4: Claude Code CLI
# ============================================================================
log_info ""
log_info "=== Phase 4: Claude Code CLI ==="

if command -v claude &> /dev/null; then
    CLAUDE_VER=$(claude --version 2>&1 || echo "unknown")
    log_ok "Claude Code already installed: $CLAUDE_VER"
else
    log_info "Installing Claude Code CLI..."
    if npm install -g @anthropic-ai/claude-code; then
        log_ok "Claude Code CLI installed"
    else
        log_warn "Could not install Claude Code via npm."
        log_warn "Try: npm install -g @anthropic-ai/claude-code"
        log_warn "Or download from: https://claude.ai/code"
    fi
fi

# ============================================================================
# PHASE 5: Verify coworker CLIs
# ============================================================================
log_info ""
log_info "=== Phase 5: Verifying coworker CLIs ==="

# Codex
if command -v codex &> /dev/null; then
    log_ok "Codex CLI: $(codex --version 2>&1 | head -1)"
else
    log_warn "Codex CLI not found. Should have been installed in Phase 2."
fi

# Gemini
if command -v gemini &> /dev/null; then
    log_ok "Gemini CLI: installed"
else
    log_warn "Gemini CLI not found. Should have been installed in Phase 2."
fi

# ============================================================================
# PHASE 6: Environment variables
# ============================================================================
log_info ""
log_info "=== Phase 6: Environment variables ==="

log_info "The following env vars may need to be set manually:"
echo ""
echo "  # Add to your shell profile (~/.bashrc, ~/.zshrc, or Windows env vars):"
echo ""
echo "  # Tavily API key (for web search MCP server)"
echo "  export TAVILY_API_KEY='your-key-here'"
echo ""
echo "  # MCP memory storage"
echo '  export MEMORY_FILE_PATH="${HOME}/.claude-memory/kr-engine.jsonl"'
echo ""
echo "  # These are set in Claude Code settings, but may also be needed globally:"
echo "  export CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=60"
echo "  export CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1"
echo "  export CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1"
echo "  export MAX_THINKING_TOKENS=128000"
echo ""

# Check if .env.template exists
if [ -f "$PROJECT_DIR/.env.template" ]; then
    log_info "Found .env.template — copy it to .env and fill in your API keys:"
    echo "  cp .env.template .env"
fi

# ============================================================================
# PHASE 7: MCP memory directory
# ============================================================================
log_info ""
log_info "=== Phase 7: MCP memory directory ==="

MEMORY_DIR="$HOME/.claude-memory"
if [ ! -d "$MEMORY_DIR" ]; then
    mkdir -p "$MEMORY_DIR"
    log_ok "Created $MEMORY_DIR"
else
    log_ok "$MEMORY_DIR already exists"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "============================================="
echo -e "  ${GREEN}Dependency Installation Complete${NC}"
echo "============================================="
echo ""
echo "  Installed:"
echo "    - $(echo "${NPM_PACKAGES[@]}" | wc -w) global npm packages"
echo "    - Python venv with $(pip list 2>/dev/null | wc -l) packages (approx)"
echo "    - Claude Code CLI"
echo ""
echo "  NEXT: Open Claude Code in the KR project:"
echo "    cd $PROJECT_DIR && claude"
echo ""
echo "  Then verify with:"
echo "    cat migration/MIGRATION_CHECKLIST.md"
echo ""
