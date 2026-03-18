# Skill Updates — Installation Required

These files contain updated or new Claude Chat skills that fix gaps identified in the normalization build prep session (2026-03-18).

## How to install

In Claude.ai Settings → Skills → find the skill → Edit → replace content with the file below.

For the new skill, create it: Settings → Skills → Create → paste the content.

## Files

### 1. `kr-reviewing-cc-output_SKILL.md` — CRITICAL FIX

**Problem:** The original skill had "ACCEPT WITH FIXES" as a valid verdict and "Non-blocking fixes" in the template. Memory entry #10 says both are BANNED. The skill and memory contradicted each other — the skill would win during execution because it provides the template.

**Fix:** Replaced three-verdict system (ACCEPT / ACCEPT WITH FIXES / REJECT) with two-verdict system (ACCEPT / BLOCKED). Removed all "non-blocking" language. Added Step 4 (run tests and verification commands). Added regression testing requirement.

**Install:** Replace the existing `kr-reviewing-cc-output` skill content.

### 2. `kr-core-extract_SKILL.md` — METHODOLOGY FIX

**Problem:** The original skill classified capabilities top-down (read description → gut call → verify). This caused the §4.B.8 error: boundary continuity was split into "basic = core, argument = deferred" based on description reading, when bottom-up analysis (reading what the passaging engine consumes) would have immediately shown it's fully core.

**Fix:** Added "Classification Methodology: Bottom-Up First, Top-Down Verify" section before the workflow. Primary method: read downstream engine's input contract first, trace required fields to producing capabilities. Top-down is verification only.

**Install:** Replace the existing `kr-core-extract` skill content.

### 3. `kr-session-retrospective_SKILL.md` — NEW SKILL

**Problem:** No mechanism to catch process failures at session end. The architect delivered unreviewed output twice in one session — both times the owner had to request a review. Without a session-end gate, the same pattern will repeat.

**Fix:** New skill with 6-step protocol: errors caught late, quality pipeline compliance audit, resources not requested, skill audit, context health assessment, required updates. Forces concrete fixes (memory entries, skill updates, repo artifacts) — not vague "I'll be more careful."

**Install:** Create a new skill named `kr-session-retrospective` with this content.

## After installing

Delete this directory (`reference/skill_updates/`) once all three skills are installed. The files are archived in git history if ever needed.
