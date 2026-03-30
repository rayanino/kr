#!/usr/bin/env bash
set -euo pipefail

WINDOWS_REPO="${KR_WINDOWS_REPO:-/mnt/c/Users/Rayane/Desktop/kr}"
WINDOWS_HOME="${KR_WINDOWS_HOME:-/mnt/c/Users/Rayane}"
TARGET_DIR="${KR_WSL_RUNTIME_DIR:-$HOME/kr-codex}"
NODE_MAJOR="${KR_NODE_MAJOR:-22}"
LOCAL_NPM_PREFIX="${HOME}/.local"

SYNC_EXCLUDES=(
  --exclude ".claude/session_state.json"
  --exclude "overnight_codex/backlog.json"
  --exclude "overnight_codex/creative_run_log.json"
  --exclude "overnight_codex/decisions.log"
  --exclude "overnight_codex/events.jsonl"
  --exclude "overnight_codex/findings_registry.json"
  --exclude "overnight_codex/manifest.json"
  --exclude "overnight_codex/manifest_readonly.json"
  --exclude "overnight_codex/manifest_write.json"
  --exclude "overnight_codex/MORNING_REPORT.md"
  --exclude "overnight_codex/progress.md"
  --exclude "overnight_codex/queue/"
  --exclude "overnight_codex/run_snapshots/"
  --exclude "overnight_codex/state.json"
  --exclude ".pytest_cache/"
  --exclude ".venv/"
  --exclude "__pycache__/"
  --exclude "integration_tests/quality_gate_smoke/"
  --exclude "overnight_codex/.heartbeat"
  --exclude "overnight_codex/.overnight_codex.lock"
  --exclude "overnight_codex/results/"
  --exclude "overnight_codex/worktrees/"
)

SYNC_FLAGS=(
  -a
  --checksum
  --delete
)

fail() {
  echo "$*" >&2
  exit 1
}

resolve_home_path() {
  local path_value="$1"
  if [[ "$path_value" == "$HOME/~/"* ]]; then
    path_value="~/${path_value#"$HOME/~/"}"
  fi
  case "$path_value" in
    "~")
      printf '%s\n' "$HOME"
      ;;
    "~/"*)
      printf '%s/%s\n' "$HOME" "${path_value:2}"
      ;;
    *)
      printf '%s\n' "$path_value"
      ;;
  esac
}

ensure_local_bin_path() {
  mkdir -p "$HOME/.local/bin"
  export PATH="$HOME/.local/bin:$PATH"

  local profile="$HOME/.profile"
  local marker="# KR Codex local bin"
  if ! grep -Fq "$marker" "$profile" 2>/dev/null; then
    {
      echo
      echo "$marker"
      echo 'case ":$PATH:" in'
      echo '  *":$HOME/.local/bin:"*) ;;'
      echo '  *) export PATH="$HOME/.local/bin:$PATH" ;;'
      echo 'esac'
    } >> "$profile"
  fi
}

ensure_base_packages() {
  local need_packages=0
  local cmd
  for cmd in git jq make python pytest rg rsync; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      need_packages=1
      break
    fi
  done

  if [ "$need_packages" -eq 0 ]; then
    return
  fi

  if ! sudo -n true >/dev/null 2>&1; then
    fail "Missing base packages and sudo requires a password. Install the WSL prerequisites interactively once, then rerun bootstrap."
  fi

  sudo apt-get update
  sudo apt-get install -y \
    build-essential \
    ca-certificates \
    curl \
    git \
    gnupg \
    jq \
    python-is-python3 \
    python3 \
    python3-pip \
    python3-pytest \
    python3-venv \
    ripgrep \
    rsync
}

if ! grep -qi microsoft /proc/sys/kernel/osrelease 2>/dev/null; then
  fail "This bootstrap script must run inside WSL."
fi

if [ ! -d "$WINDOWS_REPO/.git" ]; then
  fail "Windows repo not found at $WINDOWS_REPO"
fi

sync_entry() {
  local src="$1"
  local dst="$2"
  if [ ! -e "$src" ]; then
    return
  fi
  mkdir -p "$(dirname "$dst")"
  rsync -a "$src" "$dst"
}

sync_dir() {
  local src="$1"
  local dst="$2"
  if [ ! -d "$src" ]; then
    return
  fi
  mkdir -p "$dst"
  rsync -a "$src"/ "$dst"/
}

sync_auth_and_config() {
  echo
  echo "== Syncing Windows CLI auth/config into WSL =="

  sync_entry "$WINDOWS_HOME/.gitconfig" "$HOME/.gitconfig"

  mkdir -p "$HOME/.codex"
  sync_entry "$WINDOWS_HOME/.codex/auth.json" "$HOME/.codex/auth.json"
  sync_entry "$WINDOWS_HOME/.codex/config.toml" "$HOME/.codex/config.toml"
  sync_entry "$WINDOWS_HOME/.codex/AGENTS.md" "$HOME/.codex/AGENTS.md"
  sync_dir "$WINDOWS_HOME/.codex/skills" "$HOME/.codex/skills"
  sync_dir "$WINDOWS_HOME/.codex/plugins" "$HOME/.codex/plugins"

  mkdir -p "$HOME/.claude"
  sync_entry "$WINDOWS_HOME/.claude/.credentials.json" "$HOME/.claude/.credentials.json"
  sync_entry "$WINDOWS_HOME/.claude/settings.json" "$HOME/.claude/settings.json"
  sync_entry "$WINDOWS_HOME/.claude/settings.local.json" "$HOME/.claude/settings.local.json"
  sync_entry "$WINDOWS_HOME/.claude.json" "$HOME/.claude.json"

  sync_dir "$WINDOWS_HOME/.gemini" "$HOME/.gemini"
}

verify_mirror_file() {
  local src="$1"
  local dst="$2"
  local label="$3"
  if [ ! -e "$src" ]; then
    return
  fi
  if [ ! -e "$dst" ]; then
    fail "Expected mirrored $label at $dst"
  fi
}

verify_mirror_dir() {
  local src="$1"
  local dst="$2"
  local label="$3"
  if [ ! -d "$src" ]; then
    return
  fi
  if [ ! -d "$dst" ]; then
    fail "Expected mirrored $label directory at $dst"
  fi
}

verify_tool() {
  local tool="$1"
  local require_native="${2:-0}"
  local tool_path
  local version_output
  local status

  tool_path="$(command -v "$tool" || true)"
  if [ -z "$tool_path" ]; then
    fail "Missing required tool: $tool"
  fi
  if [ "$require_native" = "1" ] && [[ "$tool_path" == /mnt/* ]]; then
    fail "$tool resolved to Windows path $tool_path; expected a Linux-native install"
  fi

  set +e
  version_output="$(timeout 20 "$tool" --version 2>&1)"
  status=$?
  set -e
  if [ $status -ne 0 ]; then
    fail "$tool --version failed: $version_output"
  fi

  echo "$tool_path"
  printf '%s\n' "$version_output" | head -n 1
}

ensure_native_clis() {
  local tool
  local tool_path
  local need_install=0

  for tool in codex claude gemini; do
    tool_path="$(command -v "$tool" || true)"
    if [ -z "$tool_path" ] || [[ "$tool_path" == /mnt/* ]]; then
      need_install=1
      break
    fi
    if ! timeout 20 "$tool" --version >/dev/null 2>&1; then
      need_install=1
      break
    fi
  done

  if [ "$need_install" -eq 0 ]; then
    return
  fi

  npm install --global --prefix "$LOCAL_NPM_PREFIX" @anthropic-ai/claude-code @google/gemini-cli @openai/codex
  hash -r
}

restore_excluded_repo_placeholders() {
  local rel_path
  for rel_path in \
    "overnight_codex/queue/.gitkeep" \
    "overnight_codex/results/.gitkeep" \
    "overnight_codex/run_snapshots/.gitkeep" \
    "overnight_codex/worktrees/.gitkeep"
  do
    if [ -f "$WINDOWS_REPO/$rel_path" ]; then
      mkdir -p "$(dirname "$TARGET_DIR/$rel_path")"
      cp "$WINDOWS_REPO/$rel_path" "$TARGET_DIR/$rel_path"
    fi
  done
}

verify_synced_path() {
  local rel_path="$1"
  local src_path="$WINDOWS_REPO/$rel_path"
  local dst_path="$TARGET_DIR/$rel_path"
  local src_hash
  local dst_hash

  if [ ! -e "$src_path" ]; then
    fail "Expected source path is missing from the Windows checkout: $rel_path"
  fi
  if [ ! -e "$dst_path" ]; then
    fail "Expected runtime path is missing after sync: $rel_path"
  fi

  src_hash="$(sha256sum "$src_path" | awk '{print $1}')"
  dst_hash="$(sha256sum "$dst_path" | awk '{print $1}')"
  if [ "$src_hash" != "$dst_hash" ]; then
    fail "Runtime sync mismatch for $rel_path"
  fi
}

copy_runtime_surface_path() {
  local rel_path="$1"
  local src_path="$WINDOWS_REPO/$rel_path"
  local dst_path="$TARGET_DIR/$rel_path"

  if [ ! -e "$src_path" ]; then
    fail "Expected source path is missing from the Windows checkout: $rel_path"
  fi

  mkdir -p "$(dirname "$dst_path")"
  cp -f "$src_path" "$dst_path"
}

copy_runtime_sync_surface() {
  local rel_path
  for rel_path in \
    "ACTIVE_AUTHORITY.md" \
    "scripts/append_codex_findings.py" \
    "scripts/overnight_codex_backlog.py" \
    "scripts/overnight_codex_common.py" \
    "scripts/overnight_codex_orchestrator.py" \
    "scripts/overnight_codex_task_generator.py" \
    "scripts/overnight_codex_wsl_bootstrap.sh" \
    "scripts/overnight_codex_wsl_resume.ps1" \
    "scripts/quality_gate.py" \
    "docs/codex/runtime-policy.md"
  do
    copy_runtime_surface_path "$rel_path"
  done
}

verify_runtime_sync_surface() {
  local rel_path
  for rel_path in \
    "ACTIVE_AUTHORITY.md" \
    "scripts/append_codex_findings.py" \
    "scripts/overnight_codex_backlog.py" \
    "scripts/overnight_codex_common.py" \
    "scripts/overnight_codex_orchestrator.py" \
    "scripts/overnight_codex_task_generator.py" \
    "scripts/overnight_codex_wsl_bootstrap.sh" \
    "scripts/overnight_codex_wsl_resume.ps1" \
    "scripts/quality_gate.py" \
    "docs/codex/runtime-policy.md"
  do
    verify_synced_path "$rel_path"
  done
}

WINDOWS_HEAD="$(git -C "$WINDOWS_REPO" rev-parse HEAD)"
TARGET_DIR="$(resolve_home_path "$TARGET_DIR")"
ensure_local_bin_path

echo "=== KR Codex WSL Bootstrap ==="
echo "Windows repo: $WINDOWS_REPO"
echo "Target repo:  $TARGET_DIR"
echo

case "$TARGET_DIR" in
  /mnt/*)
    fail "Runtime dir must stay inside the WSL filesystem, not a mounted Windows path: $TARGET_DIR"
    ;;
esac

ensure_base_packages

need_node=1
if command -v node >/dev/null 2>&1; then
  current_node_major="$(node -p 'process.versions.node.split(".")[0]')"
  if [ "${current_node_major:-0}" -ge 20 ]; then
    need_node=0
  fi
fi

if [ "$need_node" -eq 1 ]; then
  if ! sudo -n true >/dev/null 2>&1; then
    fail "Node.js is missing or too old and sudo requires a password. Install Node interactively once, then rerun bootstrap."
  fi
  curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | sudo -E bash -
  sudo apt-get install -y nodejs
fi

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

mkdir -p "$TARGET_DIR"
rsync "${SYNC_FLAGS[@]}" "${SYNC_EXCLUDES[@]}" "$WINDOWS_REPO/" "$TARGET_DIR/"

cd "$TARGET_DIR"
if [ ! -d "$TARGET_DIR/.git" ]; then
  fail "Runtime sync did not produce a git repo at $TARGET_DIR"
fi
git config core.autocrlf input
git config core.filemode false
restore_excluded_repo_placeholders

ensure_native_clis
sync_auth_and_config
verify_mirror_file "$WINDOWS_HOME/.codex/auth.json" "$HOME/.codex/auth.json" "Codex auth"
verify_mirror_file "$WINDOWS_HOME/.codex/config.toml" "$HOME/.codex/config.toml" "Codex config"
verify_mirror_file "$WINDOWS_HOME/.claude/.credentials.json" "$HOME/.claude/.credentials.json" "Claude credentials"
verify_mirror_file "$WINDOWS_HOME/.claude/settings.json" "$HOME/.claude/settings.json" "Claude settings"
verify_mirror_dir "$WINDOWS_HOME/.gemini" "$HOME/.gemini" "Gemini config"

copy_runtime_sync_surface
verify_runtime_sync_surface
RUNTIME_HEAD="$(git rev-parse HEAD)"
if [ "$RUNTIME_HEAD" != "$WINDOWS_HEAD" ]; then
  fail "Runtime HEAD $RUNTIME_HEAD does not match Windows HEAD $WINDOWS_HEAD after sync."
fi

echo
echo "== Tool Verification =="
printf 'git -> '; verify_tool git 0
printf 'make -> '; verify_tool make 0
printf 'python -> '; verify_tool python 0
printf 'uv -> '; verify_tool uv 0
printf 'node -> '; verify_tool node 0
printf 'npm -> '; verify_tool npm 0
printf 'codex -> '; verify_tool codex 1
printf 'claude -> '; verify_tool claude 1
printf 'gemini -> '; verify_tool gemini 1
printf 'pytest -> '; verify_tool pytest 0
printf 'rg -> '; verify_tool rg 0
printf 'jq -> '; verify_tool jq 0

echo
echo "== Runtime Repo Status =="
echo "Windows HEAD: $WINDOWS_HEAD"
echo "Runtime HEAD: $RUNTIME_HEAD"
git status --short --branch

echo
echo "Bootstrap complete."
echo "Next rehearsal command:"
echo "  cd \"$TARGET_DIR\" && python scripts/overnight_codex_task_generator.py --output overnight_codex/manifest.json && KR_WINDOWS_HOME=\"$WINDOWS_HOME\" python scripts/overnight_codex_orchestrator.py --manifest overnight_codex/manifest.json --task val-contracts --hours 0.35"
