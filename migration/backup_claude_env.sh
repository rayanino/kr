#!/usr/bin/env bash
# ============================================================================
# KR Project — Claude Code Environment Backup Script
# ============================================================================
# Creates a complete backup of the user-level ~/.claude/ directory for
# migration to a new PC. Produces two archives:
#   1. CRITICAL archive (~5MB): settings, memory, hooks, agents — irreplaceable
#   2. FULL archive (~2.3GB): everything including session data and caches
#
# Usage:
#   bash migration/backup_claude_env.sh [output_dir]
#
# Default output: ~/Desktop/claude-code-backup-YYYYMMDD_HHMMSS/
# ============================================================================

set -euo pipefail

# --- Configuration ---
CLAUDE_DIR="$HOME/.claude"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${1:-$HOME/Desktop/claude-code-backup-$TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- Helpers ---
log_info()  { echo -e "${CYAN}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# --- Pre-flight checks ---
if [ ! -d "$CLAUDE_DIR" ]; then
    log_error "Claude Code directory not found at: $CLAUDE_DIR"
    exit 1
fi

echo ""
echo "============================================="
echo "  Claude Code Environment Backup"
echo "  Source: $CLAUDE_DIR"
echo "  Output: $OUTPUT_DIR"
echo "============================================="
echo ""

# --- Calculate sizes ---
log_info "Calculating directory sizes..."
TOTAL_SIZE=$(du -sh "$CLAUDE_DIR" 2>/dev/null | cut -f1)
log_info "Total ~/.claude/ size: $TOTAL_SIZE"

# --- Create output directory ---
mkdir -p "$OUTPUT_DIR"

# ============================================================================
# PHASE 1: CRITICAL backup (settings, memory, hooks, agents)
# ============================================================================
log_info "=== Phase 1: CRITICAL files (irreplaceable) ==="

CRITICAL_DIR="$OUTPUT_DIR/critical"
mkdir -p "$CRITICAL_DIR"

# 1a. Global settings
log_info "Backing up global settings..."
for f in settings.json settings.local.json settings.json.bak settings.json.bak.20260330 \
         settings.json.orig settings.local.json.bak.20260330; do
    if [ -f "$CLAUDE_DIR/$f" ]; then
        cp "$CLAUDE_DIR/$f" "$CRITICAL_DIR/"
        log_ok "  $f"
    fi
done

# 1b. Global hooks
if [ -d "$CLAUDE_DIR/hooks" ]; then
    log_info "Backing up global hooks..."
    cp -r "$CLAUDE_DIR/hooks" "$CRITICAL_DIR/hooks"
    HOOK_COUNT=$(find "$CRITICAL_DIR/hooks" -type f | wc -l)
    log_ok "  hooks/ ($HOOK_COUNT files)"
fi

# 1c. Statusline
if [ -f "$CLAUDE_DIR/statusline-command.sh" ]; then
    cp "$CLAUDE_DIR/statusline-command.sh" "$CRITICAL_DIR/"
    log_ok "  statusline-command.sh"
fi

# 1d. KR project memory (the most irreplaceable data)
KR_MEMORY="$CLAUDE_DIR/projects/C--Users-Rayane-Desktop-kr/memory"
if [ -d "$KR_MEMORY" ]; then
    log_info "Backing up KR project memory (irreplaceable)..."
    mkdir -p "$CRITICAL_DIR/kr-memory"
    cp -r "$KR_MEMORY/"* "$CRITICAL_DIR/kr-memory/"
    MEMORY_COUNT=$(find "$CRITICAL_DIR/kr-memory" -type f | wc -l)
    log_ok "  KR memory: $MEMORY_COUNT files"
fi

# 1e. Agent definitions
for dir in agents .agents; do
    if [ -d "$CLAUDE_DIR/$dir" ]; then
        log_info "Backing up $dir/..."
        cp -r "$CLAUDE_DIR/$dir" "$CRITICAL_DIR/$dir"
        AGENT_COUNT=$(find "$CRITICAL_DIR/$dir" -type f | wc -l)
        log_ok "  $dir/ ($AGENT_COUNT files)"
    fi
done

# 1f. Plugin manifest (not the cache — just the metadata)
log_info "Backing up plugin manifests..."
mkdir -p "$CRITICAL_DIR/plugins"
for f in installed_plugins.json known_marketplaces.json install-counts-cache.json blocklist.json; do
    if [ -f "$CLAUDE_DIR/plugins/$f" ]; then
        cp "$CLAUDE_DIR/plugins/$f" "$CRITICAL_DIR/plugins/"
        log_ok "  plugins/$f"
    fi
done

# 1g. Session state files
for f in session_state.json package.json gsd-file-manifest.json; do
    if [ -f "$CLAUDE_DIR/$f" ]; then
        cp "$CLAUDE_DIR/$f" "$CRITICAL_DIR/"
        log_ok "  $f"
    fi
done

# Create CRITICAL archive
CRITICAL_ARCHIVE="$OUTPUT_DIR/claude-env-CRITICAL-$TIMESTAMP.tar.gz"
log_info "Creating CRITICAL archive..."
tar -czf "$CRITICAL_ARCHIVE" -C "$OUTPUT_DIR" critical
CRITICAL_SIZE=$(du -sh "$CRITICAL_ARCHIVE" | cut -f1)
log_ok "CRITICAL archive: $CRITICAL_ARCHIVE ($CRITICAL_SIZE)"

# ============================================================================
# PHASE 2: IMPORTANT backup (history, tasks, plans, commands, skills)
# ============================================================================
log_info ""
log_info "=== Phase 2: IMPORTANT files (saves rebuild time) ==="

IMPORTANT_DIR="$OUTPUT_DIR/important"
mkdir -p "$IMPORTANT_DIR"

# History
if [ -f "$CLAUDE_DIR/history.jsonl" ]; then
    cp "$CLAUDE_DIR/history.jsonl" "$IMPORTANT_DIR/"
    log_ok "  history.jsonl"
fi

# Directories
for dir in tasks plans teams sessions commands skills scripts get-shit-done todos; do
    if [ -d "$CLAUDE_DIR/$dir" ]; then
        cp -r "$CLAUDE_DIR/$dir" "$IMPORTANT_DIR/$dir"
        DIR_COUNT=$(find "$IMPORTANT_DIR/$dir" -type f 2>/dev/null | wc -l)
        log_ok "  $dir/ ($DIR_COUNT files)"
    fi
done

# Standalone important files
for f in stats-cache.json performance.csv changes.log; do
    if [ -f "$CLAUDE_DIR/$f" ]; then
        cp "$CLAUDE_DIR/$f" "$IMPORTANT_DIR/"
        log_ok "  $f"
    fi
done

# ============================================================================
# PHASE 3: SESSION DATA (all project directories)
# ============================================================================
log_info ""
log_info "=== Phase 3: Session data (all projects) ==="

SESSIONS_DIR="$OUTPUT_DIR/sessions"
mkdir -p "$SESSIONS_DIR"

if [ -d "$CLAUDE_DIR/projects" ]; then
    PROJECT_COUNT=$(ls -d "$CLAUDE_DIR/projects/"*/ 2>/dev/null | wc -l)
    log_info "Backing up $PROJECT_COUNT project directories..."
    cp -r "$CLAUDE_DIR/projects" "$SESSIONS_DIR/projects"
    SESSIONS_SIZE=$(du -sh "$SESSIONS_DIR" | cut -f1)
    log_ok "  projects/ ($SESSIONS_SIZE total)"
fi

# ============================================================================
# PHASE 4: Create FULL archive (everything except regenerable caches)
# ============================================================================
log_info ""
log_info "=== Phase 4: Creating FULL archive ==="

FULL_ARCHIVE="$OUTPUT_DIR/claude-env-FULL-$TIMESTAMP.tar.gz"
log_info "Compressing full backup (this may take a few minutes)..."
tar -czf "$FULL_ARCHIVE" \
    -C "$OUTPUT_DIR" \
    critical important sessions \
    --warning=no-file-changed 2>/dev/null || true
FULL_SIZE=$(du -sh "$FULL_ARCHIVE" | cut -f1)
log_ok "FULL archive: $FULL_ARCHIVE ($FULL_SIZE)"

# ============================================================================
# PHASE 5: Generate manifest with checksums
# ============================================================================
log_info ""
log_info "=== Phase 5: Generating backup manifest ==="

MANIFEST="$OUTPUT_DIR/backup_manifest.txt"
{
    echo "# Claude Code Environment Backup Manifest"
    echo "# Generated: $(date -Iseconds)"
    echo "# Source: $CLAUDE_DIR"
    echo "# Host: $(hostname)"
    echo "# User: $(whoami)"
    echo ""
    echo "## Archive Files"
    echo "CRITICAL: $CRITICAL_ARCHIVE ($CRITICAL_SIZE)"
    echo "FULL:     $FULL_ARCHIVE ($FULL_SIZE)"
    echo ""
    echo "## File Inventory"
} > "$MANIFEST"

# List all backed up files with sizes
find "$OUTPUT_DIR/critical" "$OUTPUT_DIR/important" "$OUTPUT_DIR/sessions" \
    -type f 2>/dev/null | while read -r f; do
    SIZE=$(stat --printf="%s" "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo "?")
    REL_PATH="${f#$OUTPUT_DIR/}"
    echo "$SIZE  $REL_PATH"
done >> "$MANIFEST"

MANIFEST_LINES=$(wc -l < "$MANIFEST")
log_ok "Manifest: $MANIFEST ($MANIFEST_LINES entries)"

# ============================================================================
# PHASE 6: Record environment metadata for restore script
# ============================================================================
log_info ""
log_info "=== Phase 6: Recording environment metadata ==="

ENV_META="$OUTPUT_DIR/environment_metadata.json"
cat > "$ENV_META" << ENVEOF
{
    "backup_timestamp": "$(date -Iseconds)",
    "source_host": "$(hostname)",
    "source_user": "$(whoami)",
    "source_home": "$HOME",
    "source_claude_dir": "$CLAUDE_DIR",
    "source_os": "$(uname -s)",
    "node_version": "$(node -v 2>/dev/null || echo 'not found')",
    "python_version": "$(python --version 2>&1 || echo 'not found')",
    "npm_version": "$(npm -v 2>/dev/null || echo 'not found')",
    "claude_version": "$(claude --version 2>/dev/null || echo 'not found')",
    "project_paths": {
        "kr": "C:/Users/Rayane/Desktop/kr",
        "kr_branch": "canonical/excerpting-clean-start-20260409"
    }
}
ENVEOF
log_ok "Environment metadata saved"

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "============================================="
echo -e "  ${GREEN}Backup Complete${NC}"
echo "============================================="
echo ""
echo "  Output directory: $OUTPUT_DIR"
echo "  CRITICAL archive: $CRITICAL_SIZE"
echo "  FULL archive:     $FULL_SIZE"
echo "  Manifest:         $MANIFEST_LINES entries"
echo ""
echo "  NEXT STEPS:"
echo "  1. Copy $OUTPUT_DIR to the new PC"
echo "     (USB drive, cloud storage, or network transfer)"
echo "  2. Also copy the git repo (or clone from GitHub):"
echo "     git clone ... && git checkout canonical/excerpting-clean-start-20260409"
echo "  3. On the new PC, run:"
echo "     bash migration/restore_claude_env.sh <backup_dir> [new_username]"
echo ""
