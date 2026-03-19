# Skill Updates — Installation Required

These files contain updated or new Claude Chat skills that fix gaps identified in the normalization build prep session (2026-03-18).

## How to install

In Claude.ai project settings → Skills → find the skill → Edit → replace content with the file below.

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

### 4. `kr-spec-review_SKILL.md` — DESCRIPTION FIX

**Problem:** Line 8 described the owner as having "deep domain knowledge." Memory #6 says the owner "has NOT studied Islamic texts yet — KR exists to CREATE that environment." This mismatch could cause the architect to over-trust the owner's domain comments rather than independently verifying them.

**Fix:** Changed description from "deep domain knowledge but no technical background" to "has NOT yet studied Islamic texts — KR exists to CREATE that study environment. He has domain intuitions and access to scholars and resources, but his comments are hypotheses, not expert assertions." Added guidance to ask the owner to consult scholars or provide samples when verification is needed.

**Install:** Replace the existing `kr-spec-review` skill content.

## After installing

### 5. `kr-reviewing-cc-output_SKILL_v3.md` — MULTI-ROUND ENFORCEMENT (March 2026)

**Problem:** The skill (even after v2 fix) allowed the architect to cram the entire review into one response — 16 probes, verdict, all in one shot. Session 4 proved this pattern misses real gaps: factual error from truncated file read, never traced the SPEC's own worked example, no cooling-off period before verdict.

**Fix:** Complete rewrite to enforce 3-pass multi-round structure (RULE 8). Pass 1 → STOP, wait for owner. Pass 2 (including mandatory SPEC example trace per RULE 5) → STOP, wait. Pass 3 (self-verify per RULES 6-7) → verdict. Added: RULE 5 (SPEC example trace), RULE 6 (verify own claims by grep), RULE 7 (no truncated reads). Session 4 failure documented as permanent lesson.

**Install:** Replace the existing `kr-reviewing-cc-output` skill content with this file.

**NOTE:** This is the THIRD version of this skill. v1 had "ACCEPT WITH FIXES." v2 fixed verdicts but allowed single-response reviews. v3 enforces multi-round. The progression shows the same pattern: each failure mode gets patched after it costs real review quality.

Delete this directory (`reference/skill_updates/`) once all five skills are installed. The files are archived in git history if ever needed.
