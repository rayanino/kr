# Session 4 Start Prompt — Excerpting SPEC Completion

Pull the repo and read NEXT.md. This is session 4 of the excerpting SPEC section-by-section writing. Run `git log --oneline -5` to see current state. Before any work, read `reference/protocols/QUALITY_AXIOM.md` and scan `ls /mnt/skills/user/` to confirm available skills.

<session_context>
Sessions 1–3 wrote 9 of 12 sections (§2.3, §2.1, §2.2, §3, §4, §5, §6, §7, §8). The SPEC is at 1970 lines. Your session 3 handoff is at `reference/archive/sessions/excerpting_spec_session3_handoff.md` — read it in full before writing anything. It contains the accumulated ID registries, 4 design decisions already made, verified reading instructions with line numbers for each remaining section, and 4 traps to avoid.

Key context from session 3 (already decided — do NOT re-derive):
- Phase 3 uses per-chunk LLM enrichment calls (not per-unit)
- No `proposed_leaf` field — topic keywords only, taxonomy engine does placement
- Default consensus verifier: `openai/gpt-4.1`, escalation: `cohere/command-a-03-2025`
- §2.3.5 now references §2.2 as the authoritative ExcerptRecord definition
- 27 error codes, 34 verification checks, 29 invariants, 22 domain rules all verified consistent
</session_context>

<task>
Write sections §1 (Purpose and Scope), §9 (Deferred Capabilities), and §10 (Test Requirements) of `engines/excerpting/SPEC.md`. Then run a final coherence review across all 12 sections.

Writing order:
1. **§9 first** — deferred capabilities (needs old SPEC §4.B reading)
2. **§10 second** — test requirements (references all processing sections)
3. **§1 last** — purpose and scope (summary of everything)
4. **Coherence review** — programmatic cross-check of all 12 sections

For each section:
1. Read the source material listed in the session 3 handoff's reading instructions for that section
2. Read the SPEC_OUTLINE.md subsection structure for that section
3. Analyze: alignment with architecture? complete? edge cases?
4. Write the section
5. Verify programmatically (cross-reference resolution, ID consistency)
6. Commit before moving to the next section

After all 3 sections are written:
7. Run a coherence review: every §2.2 field traces to §7, every §8 code is defined in §4–§7, every §6 rule appears in §7, every §3 criterion appears in the §5.3.2 prompt
8. Update the NEXT.md progress tracker
9. Write session 4 handoff (if anything remains) or transition note (if SPEC is complete)

**After SPEC completion (if all 12 sections + coherence pass):**
NEXT.md Step 3 says to update `engines/excerpting/contracts.py` and `engines/excerpting/CLAUDE.md`. If context permits, begin this. If context is degraded, note it in the handoff for session 5.
</task>

<skills>
Invoke ALL of these explicitly at session start:
- `kr-spec-review` — for analyzing old SPEC §4.B sections being absorbed into §9
- `kr-integrity` — for T-1 through T-7 threat analysis on each section
- `critical-review` — for self-verification of produced sections and coherence review
- `thinking-frameworks` — for multi-angle analysis on test strategy decisions
</skills>

<quality>
Take all your time. No rush. These 3 sections are lighter than sessions 1–3 but the coherence review is critical. If the coherence review finds inconsistencies, fix them before declaring the SPEC complete.

§9 (deferred) and §1 (purpose) are straightforward. §10 (test requirements) needs care — it defines WHAT must be tested, not HOW. Every verification check (34 total), every invariant (29 total), every error code (27 total) needs at least one test requirement. The adversarial cases (ADV-E-01 through ADV-E-10+ from the outline) need to be fleshed out.

After writing each section, run a programmatic verification script (the pattern from sessions 1, 2, and 3). After the coherence review, write a handoff document following the same structure as the session 3 handoff. If context degrades before finishing, stop, write the handoff for what's done, and tell me to start a new chat.
</quality>

Take all your time, no rush. Quality is your only metric.
