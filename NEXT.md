# NEXT — Source Engine Validation, Step 1 Fixes

**Governing document:** `engines/source/VALIDATION_PLAN.md` — read this first in every new session.

**Previous step:** Step 1 COMPLETE — Code Audit delivered. See `engines/source/review/CODE_AUDIT_SESSION6.md`.

**Current step:** Step 1 Fixes — Claude Code implements the 6 blocking fixes from the audit.

**What to do:** This is a Claude Code session. Implement the 6 fixes listed in the "Definitive Fix List for Claude Code" section at the bottom of `engines/source/review/CODE_AUDIT_SESSION6.md`. Read the ENTIRE audit document before starting — including the Self-Review and Final Review sections, which correct errors in the inline fix descriptions. The "Definitive Fix List" section is the authoritative specification; ignore the inline fix pseudocode in the checklist items (it contains errors documented in SR-1 and SR-2).

**Fix list (6 blocking):**

1. **Gate errors ignored** — engine.py: process `severity="gate"` validation errors, create human gate checkpoints, AND raise to abort registration.
2. **Rollback silent on double corruption** — registries/__init__.py: validate .bak content after restore, raise on unrecoverable corruption.
3. **Name matching punctuation bug** — shared/scholar_authority/src/name_matching.py: strip Arabic/Latin punctuation in normalize_arabic_name.
4. **Publication year field mapping** — engine.py: read `edition_year_hijri`/`miladi` from extracted dict.
5. **Title priority reversed** — engine.py: swap `title_full` before `display_title`.
6. **Layer author dummy ID crash** — engine.py: register placeholder scholar instead of using hard-coded sch_00000.

**Also implement (non-blocking, if time permits):**
- structural_format default: change "prose" to "mixed" (engine.py:401)
- Genre chain silent drop: add logger.warning before return None (engine.py:175)
- Staging cleanup: replace pass with logger.log_event (engine.py:598)

**After fixes:** Run existing tests (`pytest engines/source/tests/ -x`). All 758 must still pass. Then update NEXT.md for Step 2 (deterministic sweep).

**GO/NO-GO:** All 6 fixes implemented. All existing tests pass. New tests added for each fix.
