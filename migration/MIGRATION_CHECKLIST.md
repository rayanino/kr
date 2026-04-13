# Claude Code Environment Migration Checklist

Step-by-step guide for migrating the KR Claude Code environment to a new PC.

---

## Before You Start

You need:
- [ ] A USB drive, cloud storage, or network share to transfer ~2.5GB of backup data
- [ ] The new PC with Windows 11 installed
- [ ] Internet access on the new PC (for installing tools and cloning the repo)

---

## On the OLD PC (do this FIRST, before destroying it)

### Step 1: Run the backup script

Open Git Bash and run:
```bash
cd ~/Desktop/kr
bash migration/backup_claude_env.sh
```

This creates a folder on your Desktop: `claude-code-backup-YYYYMMDD_HHMMSS/`
containing two archives and a manifest.

### Step 2: Verify the backup

Check that the backup folder contains:
- [ ] `claude-env-CRITICAL-*.tar.gz` (should be ~2-5MB)
- [ ] `claude-env-FULL-*.tar.gz` (should be ~500MB-2GB)
- [ ] `backup_manifest.txt` (file listing)
- [ ] `environment_metadata.json` (old PC info)
- [ ] `critical/` folder with your memory files
- [ ] `important/` folder with history and tasks
- [ ] `sessions/` folder with project data

### Step 3: Copy to transfer medium

Copy these items to your USB/cloud:
- [ ] The entire `claude-code-backup-*` folder
- [ ] Your Codex setup bundle: `kr-codex-setup-bundle-20260408_235052.zip`
- [ ] Any `.env` files or API keys you need (check password manager)

The git repo is already on GitHub at branch `canonical/excerpting-clean-start-20260409`.

---

## On the NEW PC

### Step 4: Install prerequisites

Download and install (in this order):
- [ ] **Git**: https://git-scm.com/download/win (includes Git Bash)
- [ ] **Python 3.13+**: https://www.python.org/downloads/ (check "Add to PATH")
- [ ] **Node.js v24+**: https://nodejs.org (LTS or Current)

Verify in Git Bash:
```bash
git --version
python --version
node -v
npm -v
```

### Step 5: Clone the repository

```bash
cd ~/Desktop
git clone https://github.com/YOUR_USERNAME/kr.git
cd kr
git checkout canonical/excerpting-clean-start-20260409
```

### Step 6: Copy backup to new PC

Copy the `claude-code-backup-*` folder from your USB/cloud to the Desktop.

If you only have the `.tar.gz` archives, extract them first:
```bash
cd ~/Desktop/claude-code-backup-*
tar -xzf claude-env-CRITICAL-*.tar.gz
tar -xzf claude-env-FULL-*.tar.gz
```

### Step 7: Run the restore script

```bash
cd ~/Desktop/kr
bash migration/restore_claude_env.sh ~/Desktop/claude-code-backup-* ~/Desktop/kr
```

This will:
- Copy settings, memory, hooks, and agents to `~/.claude/`
- Remap any paths if your username changed
- Restore all 122 KR project memory files

### Step 8: Install dependencies

```bash
cd ~/Desktop/kr
bash migration/reinstall_deps.sh
```

This installs:
- 11 global npm packages (Codex CLI, Gemini CLI, etc.)
- Python virtual environment with 206 packages
- Claude Code CLI

### Step 9: Set up environment variables

Create or edit your `.env` file:
```bash
cp .env.template .env
# Edit .env and add your API keys:
# - TAVILY_API_KEY
# - Any other keys from your password manager
```

### Step 10: Authenticate Claude Code

```bash
claude login
```

Follow the prompts to sign in with your Anthropic account.

### Step 11: Restore Codex settings

Extract your Codex bundle:
```bash
# Follow the Codex migration instructions from the bundle
unzip kr-codex-setup-bundle-20260408_235052.zip
```

---

## Verification

### Step 12: Launch Claude Code and verify

```bash
cd ~/Desktop/kr
claude
```

Check each of these:

- [ ] **Statusline**: Shows KR project info (branch, budget, phase)
- [ ] **SessionStart hook**: Shows git status and budget on startup
- [ ] **Memory**: Ask "what do you know about the KR project?" — should recall 93+ memories
- [ ] **Plugins**: Skills like `/commit`, `/prompt-architect`, `/catchup` should be available
- [ ] **Hooks**: Try editing a file — PostToolUse hooks should fire (arabic-safety, code-quality, etc.)

### Step 13: Verify Python environment

```bash
cd ~/Desktop/kr
make test
# Or: python -m pytest engines/*/tests/ -q
```

- [ ] All tests pass (expect 1000+ tests)

### Step 14: Verify coworker CLIs

```bash
codex --version
gemini --version
```

- [ ] Both commands return version numbers

### Step 15: Verify MCP servers

In Claude Code, try:
- [ ] Use a Context7 tool (e.g., look up Pydantic docs)
- [ ] Use a Tavily tool (e.g., web search)
- [ ] Check that the memory MCP server connects

---

## Troubleshooting

### Plugins not loading
If plugins don't auto-install from the marketplace definitions:
```bash
# In Claude Code, manually install:
claude plugins install pyright-lsp
claude plugins install superpowers
# ... etc for each plugin
```

Or add the custom marketplaces first:
```bash
claude marketplace add rtd ryanthedev/rtd-claude-inn
claude marketplace add claude-lens-marketplace Astro-Han/claude-lens
claude marketplace add prompt-architect-marketplace ckelsoe/prompt-architect
claude marketplace add compound-engineering-plugin EveryInc/compound-engineering-plugin
```

### Hooks not firing
Check that hook scripts are executable:
```bash
chmod +x ~/.claude/hooks/*.js
chmod +x ~/.claude/statusline-command.sh
```

Also check that paths in `~/.claude/settings.json` point to the correct location.

### Memory not found
If Claude Code can't find your memories, the project directory name may not match.
Check:
```bash
ls ~/.claude/projects/
```
The directory name should match your project path with dashes instead of slashes:
`C--Users-YourName-Desktop-kr`

### Python tests failing
```bash
# Ensure you're in the venv:
source .venv/Scripts/activate  # Windows
python -m pytest engines/source/tests/ -x -q  # Test one engine at a time
```

---

## What Was Preserved

| Category | Items | Status |
|----------|-------|--------|
| Project `.claude/` config | 132 files (agents, hooks, rules, skills, commands) | In git |
| Global settings | settings.json, settings.local.json | Backed up |
| KR project memory | 122 memory files (8 months of knowledge) | Backed up |
| Global hooks | 5 scripts (GSD, context monitor, statusline) | Backed up |
| Plugin manifest | 17 enabled, 7 marketplaces | Backed up |
| Session history | Full command history | Backed up |
| Tasks & plans | 220 tasks, session plans | Backed up |
| Python packages | 206 packages | Reinstalled |
| npm global tools | 11 packages (Codex, Gemini, etc.) | Reinstalled |
| Auth tokens | OAuth credentials | Re-authenticated |
