#!/usr/bin/env bash
# ============================================================================
# KR Project — Claude Code Environment Restore Script
# ============================================================================
# Restores a Claude Code environment backup to a new PC.
# Handles path remapping if the username or project location changed.
#
# Usage:
#   bash migration/restore_claude_env.sh <backup_dir> [new_project_path]
#
# Arguments:
#   backup_dir        Path to the extracted backup directory
#   new_project_path  (Optional) New KR project path. Default: current directory
#
# Example:
#   bash migration/restore_claude_env.sh ~/Desktop/claude-code-backup-20260409 ~/Desktop/kr
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

# --- Parse arguments ---
if [ $# -lt 1 ]; then
    echo "Usage: bash migration/restore_claude_env.sh <backup_dir> [new_project_path]"
    echo ""
    echo "  backup_dir        Path to the backup directory (containing critical/, important/, sessions/)"
    echo "  new_project_path  Optional: where the KR project lives on this PC (default: pwd)"
    exit 1
fi

BACKUP_DIR="$1"
NEW_PROJECT_PATH="${2:-$(pwd)}"
NEW_CLAUDE_DIR="$HOME/.claude"
NEW_USER="$(whoami)"
NEW_HOME="$HOME"

# --- Read old environment metadata ---
ENV_META="$BACKUP_DIR/environment_metadata.json"
if [ -f "$ENV_META" ]; then
    # Extract old values (basic parsing without jq dependency)
    OLD_USER=$(grep '"source_user"' "$ENV_META" | sed 's/.*: *"\(.*\)".*/\1/')
    OLD_HOME=$(grep '"source_home"' "$ENV_META" | sed 's/.*: *"\(.*\)".*/\1/' | sed 's|\\\\|/|g')
    OLD_KR_PATH=$(grep '"kr"' "$ENV_META" | sed 's/.*: *"\(.*\)".*/\1/' | sed 's|\\\\|/|g')
    log_info "Old environment: user=$OLD_USER, home=$OLD_HOME, kr=$OLD_KR_PATH"
else
    # Fallback defaults if metadata is missing
    OLD_USER="Rayane"
    OLD_HOME="/c/Users/Rayane"
    OLD_KR_PATH="C:/Users/Rayane/Desktop/kr"
    log_warn "No environment_metadata.json found. Using defaults: user=$OLD_USER"
fi

# Convert new project path to the format used in directory names
# C:\Users\NewUser\Desktop\kr -> C--Users-NewUser-Desktop-kr
NEW_PROJECT_PATH_NORMALIZED=$(echo "$NEW_PROJECT_PATH" | sed 's|\\|/|g')
NEW_KR_DIR_NAME=$(echo "$NEW_PROJECT_PATH_NORMALIZED" | sed 's|^/c/|C--|' | sed 's|/|--|g' | sed 's|:|-|g')
OLD_KR_DIR_NAME="C--Users-Rayane-Desktop-kr"

echo ""
echo "============================================="
echo "  Claude Code Environment Restore"
echo "============================================="
echo ""
echo "  Backup source:    $BACKUP_DIR"
echo "  Target:           $NEW_CLAUDE_DIR"
echo "  Old user:         $OLD_USER"
echo "  New user:         $NEW_USER"
echo "  Old KR path:      $OLD_KR_PATH"
echo "  New KR path:      $NEW_PROJECT_PATH_NORMALIZED"
echo "  Old dir name:     $OLD_KR_DIR_NAME"
echo "  New dir name:     $NEW_KR_DIR_NAME"
echo ""

# --- Safety check ---
if [ -d "$NEW_CLAUDE_DIR" ]; then
    EXISTING_SIZE=$(du -sh "$NEW_CLAUDE_DIR" 2>/dev/null | cut -f1)
    log_warn "~/.claude/ already exists ($EXISTING_SIZE). Files will be merged (not overwritten)."
    echo ""
    read -p "Continue? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Aborted."
        exit 0
    fi
fi

# --- Verify backup structure ---
MISSING=0
for dir in critical; do
    if [ ! -d "$BACKUP_DIR/$dir" ]; then
        log_error "Missing required directory: $BACKUP_DIR/$dir"
        MISSING=1
    fi
done
if [ "$MISSING" -eq 1 ]; then
    log_error "Backup appears incomplete. Check that archives were extracted correctly."
    exit 1
fi

# ============================================================================
# PHASE 1: Restore CRITICAL files
# ============================================================================
log_info "=== Phase 1: Restoring CRITICAL files ==="

mkdir -p "$NEW_CLAUDE_DIR"

# 1a. Settings files
for f in settings.json settings.local.json settings.json.bak settings.json.bak.20260330 \
         settings.json.orig settings.local.json.bak.20260330 session_state.json \
         package.json gsd-file-manifest.json statusline-command.sh; do
    if [ -f "$BACKUP_DIR/critical/$f" ]; then
        cp "$BACKUP_DIR/critical/$f" "$NEW_CLAUDE_DIR/$f"
        log_ok "  $f"
    fi
done

# 1b. Hooks
if [ -d "$BACKUP_DIR/critical/hooks" ]; then
    mkdir -p "$NEW_CLAUDE_DIR/hooks"
    cp -r "$BACKUP_DIR/critical/hooks/"* "$NEW_CLAUDE_DIR/hooks/"
    log_ok "  hooks/"
fi

# 1c. KR project memory
if [ -d "$BACKUP_DIR/critical/kr-memory" ]; then
    MEMORY_TARGET="$NEW_CLAUDE_DIR/projects/$NEW_KR_DIR_NAME/memory"
    mkdir -p "$MEMORY_TARGET"
    cp -r "$BACKUP_DIR/critical/kr-memory/"* "$MEMORY_TARGET/"
    MEMORY_COUNT=$(find "$MEMORY_TARGET" -type f | wc -l)
    log_ok "  KR memory: $MEMORY_COUNT files -> projects/$NEW_KR_DIR_NAME/memory/"
fi

# 1d. Agents
for dir in agents .agents; do
    if [ -d "$BACKUP_DIR/critical/$dir" ]; then
        mkdir -p "$NEW_CLAUDE_DIR/$dir"
        cp -r "$BACKUP_DIR/critical/$dir/"* "$NEW_CLAUDE_DIR/$dir/"
        log_ok "  $dir/"
    fi
done

# 1e. Plugin manifests
if [ -d "$BACKUP_DIR/critical/plugins" ]; then
    mkdir -p "$NEW_CLAUDE_DIR/plugins"
    cp -r "$BACKUP_DIR/critical/plugins/"* "$NEW_CLAUDE_DIR/plugins/"
    log_ok "  plugins/ (manifests only)"
fi

# ============================================================================
# PHASE 2: Restore IMPORTANT files
# ============================================================================
if [ -d "$BACKUP_DIR/important" ]; then
    log_info ""
    log_info "=== Phase 2: Restoring IMPORTANT files ==="

    # Files
    for f in history.jsonl stats-cache.json performance.csv changes.log; do
        if [ -f "$BACKUP_DIR/important/$f" ]; then
            cp "$BACKUP_DIR/important/$f" "$NEW_CLAUDE_DIR/$f"
            log_ok "  $f"
        fi
    done

    # Directories
    for dir in tasks plans teams sessions commands skills scripts get-shit-done todos; do
        if [ -d "$BACKUP_DIR/important/$dir" ]; then
            mkdir -p "$NEW_CLAUDE_DIR/$dir"
            cp -r "$BACKUP_DIR/important/$dir/"* "$NEW_CLAUDE_DIR/$dir/" 2>/dev/null || true
            log_ok "  $dir/"
        fi
    done
else
    log_warn "No important/ directory found in backup. Skipping Phase 2."
fi

# ============================================================================
# PHASE 3: Restore session data (if present)
# ============================================================================
if [ -d "$BACKUP_DIR/sessions/projects" ]; then
    log_info ""
    log_info "=== Phase 3: Restoring session data ==="

    mkdir -p "$NEW_CLAUDE_DIR/projects"

    # Copy all project directories, renaming KR-related ones
    for proj_dir in "$BACKUP_DIR/sessions/projects/"*/; do
        proj_name=$(basename "$proj_dir")

        # Remap directory names containing the old path
        new_proj_name="$proj_name"
        if [[ "$proj_name" == *"$OLD_KR_DIR_NAME"* ]]; then
            new_proj_name="${proj_name//$OLD_KR_DIR_NAME/$NEW_KR_DIR_NAME}"
            log_info "  Remapping: $proj_name -> $new_proj_name"
        fi

        # Skip if this is the KR memory dir (already restored in Phase 1)
        TARGET="$NEW_CLAUDE_DIR/projects/$new_proj_name"
        if [ -d "$TARGET" ]; then
            # Merge — don't overwrite memory files
            cp -rn "$proj_dir"* "$TARGET/" 2>/dev/null || true
        else
            cp -r "$proj_dir" "$TARGET"
        fi
    done

    PROJECT_COUNT=$(ls -d "$NEW_CLAUDE_DIR/projects/"*/ 2>/dev/null | wc -l)
    log_ok "  Restored $PROJECT_COUNT project directories"
else
    log_warn "No sessions/ directory found in backup. Skipping Phase 3."
fi

# ============================================================================
# PHASE 4: Path remapping
# ============================================================================
log_info ""
log_info "=== Phase 4: Path remapping ==="

if [ "$OLD_USER" != "$NEW_USER" ] || [ "$OLD_HOME" != "$NEW_HOME" ]; then
    log_info "Username or home path changed. Remapping paths..."

    # Patterns to replace (both forward-slash and backslash variants)
    OLD_PATHS=(
        "C:/Users/$OLD_USER/"
        "C:\\\\Users\\\\$OLD_USER\\\\"
        "/c/Users/$OLD_USER/"
    )
    NEW_PATHS=(
        "C:/Users/$NEW_USER/"
        "C:\\\\Users\\\\$NEW_USER\\\\"
        "/c/Users/$NEW_USER/"
    )

    # Files that contain hardcoded paths
    FILES_TO_REMAP=(
        "$NEW_CLAUDE_DIR/settings.json"
        "$NEW_CLAUDE_DIR/settings.local.json"
        "$NEW_CLAUDE_DIR/statusline-command.sh"
        "$NEW_CLAUDE_DIR/plugins/installed_plugins.json"
        "$NEW_CLAUDE_DIR/plugins/known_marketplaces.json"
    )

    for filepath in "${FILES_TO_REMAP[@]}"; do
        if [ -f "$filepath" ]; then
            for i in "${!OLD_PATHS[@]}"; do
                if grep -q "${OLD_PATHS[$i]}" "$filepath" 2>/dev/null; then
                    sed -i "s|${OLD_PATHS[$i]}|${NEW_PATHS[$i]}|g" "$filepath"
                fi
            done
            log_ok "  Remapped: $(basename "$filepath")"
        fi
    done

    # Also remap the KR project path specifically if it changed
    OLD_KR_ESCAPED=$(echo "$OLD_KR_PATH" | sed 's|/|\\/|g')
    NEW_KR_ESCAPED=$(echo "$NEW_PROJECT_PATH_NORMALIZED" | sed 's|/|\\/|g')
    for filepath in "${FILES_TO_REMAP[@]}"; do
        if [ -f "$filepath" ] && grep -q "$OLD_KR_PATH" "$filepath" 2>/dev/null; then
            sed -i "s|$OLD_KR_PATH|$NEW_PROJECT_PATH_NORMALIZED|g" "$filepath"
            log_ok "  Remapped KR path in: $(basename "$filepath")"
        fi
    done
else
    log_ok "Username unchanged ($NEW_USER). No path remapping needed."
fi

# ============================================================================
# PHASE 5: Verification
# ============================================================================
log_info ""
log_info "=== Phase 5: Verification ==="

ERRORS=0

# Check critical files exist
for f in settings.json settings.local.json; do
    if [ -f "$NEW_CLAUDE_DIR/$f" ]; then
        log_ok "  $f exists"
    else
        log_error "  $f MISSING"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check hooks exist
if [ -d "$NEW_CLAUDE_DIR/hooks" ]; then
    HOOK_COUNT=$(find "$NEW_CLAUDE_DIR/hooks" -type f | wc -l)
    log_ok "  hooks/ ($HOOK_COUNT files)"
else
    log_warn "  hooks/ missing"
fi

# Check KR memory
KR_MEM_DIR="$NEW_CLAUDE_DIR/projects/$NEW_KR_DIR_NAME/memory"
if [ -d "$KR_MEM_DIR" ]; then
    MEM_COUNT=$(find "$KR_MEM_DIR" -type f | wc -l)
    log_ok "  KR memory: $MEM_COUNT files"
else
    log_error "  KR memory directory MISSING"
    ERRORS=$((ERRORS + 1))
fi

# Check for hardcoded old paths
if grep -r "Users/$OLD_USER" "$NEW_CLAUDE_DIR/settings.json" 2>/dev/null | grep -v "Users/$NEW_USER" > /dev/null 2>&1; then
    log_warn "  settings.json still contains old user paths — may need manual fix"
else
    log_ok "  No stale path references in settings.json"
fi

# Check plugins manifest
if [ -f "$NEW_CLAUDE_DIR/plugins/installed_plugins.json" ]; then
    PLUGIN_COUNT=$(grep -c '"installPath"' "$NEW_CLAUDE_DIR/plugins/installed_plugins.json" || echo 0)
    log_ok "  Plugin manifest: $PLUGIN_COUNT plugins registered"
else
    log_warn "  Plugin manifest missing — plugins will need manual reinstall"
fi

echo ""
if [ "$ERRORS" -eq 0 ]; then
    echo -e "  ${GREEN}Restore complete — no errors${NC}"
else
    echo -e "  ${RED}Restore complete with $ERRORS error(s) — review above${NC}"
fi

echo ""
echo "============================================="
echo "  NEXT STEPS"
echo "============================================="
echo ""
echo "  1. Install Claude Code CLI if not already installed:"
echo "     npm install -g @anthropic-ai/claude-code"
echo ""
echo "  2. Re-authenticate Claude Code:"
echo "     claude login"
echo ""
echo "  3. Install dependencies:"
echo "     bash migration/reinstall_deps.sh"
echo ""
echo "  4. Launch Claude Code in the KR project:"
echo "     cd $NEW_PROJECT_PATH_NORMALIZED && claude"
echo "     - Plugins should auto-install from marketplace definitions"
echo "     - If not, run: claude plugins install <plugin-name>"
echo ""
echo "  5. Verify with the checklist:"
echo "     cat migration/MIGRATION_CHECKLIST.md"
echo ""
