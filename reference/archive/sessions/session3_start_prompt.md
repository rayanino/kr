# Session 3 Start Prompt — Paste This Into a New Chat

---

Pull the repo and read NEXT.md. This is session 3 of the excerpting SPEC section-by-section writing. Run `git log --oneline -5` to see current state. Before any work, read `reference/protocols/QUALITY_AXIOM.md` and scan `ls /mnt/skills/user/` to confirm available skills.

<session_context>
Sessions 1–2 wrote 6 of 12 sections (§2.3, §2.1, §3, §4, §5, §6). The SPEC is at 1145 lines. Your session 2 handoff is at `reference/archive/sessions/excerpting_spec_session2_handoff.md` — read it in full before writing anything. It contains critical findings, a complete ID registry, 4 design decisions you must make, a Phase 3 field inventory, reading instructions with verified file paths and line numbers, and 6 specific traps to avoid.
</session_context>

<task>
Write sections §7 (Phase 3: Metadata Enrichment), §2.2 (Output Contract), and §8 (Error Handling and Configuration) of `engines/excerpting/SPEC.md`. Follow the dependency order: §7 first (defines the processing), then §2.2 (defined by what §7 produces), then §8 (catalogs everything from §4–§7).

For each section:
1. Read the source material listed in the handoff's reading instructions for that section
2. Analyze: alignment with architecture? best design? future regrets? evidence-grounded? edge cases?
3. Write the section
4. Verify programmatically (cross-reference resolution, field traceability, ID consistency)
5. Commit before moving to the next section

Make the 4 design decisions documented in the handoff (Phase 3 LLM call granularity, proposed_leaf ownership, consensus model providers, §2.3.5 update scope). Make each with reasoning — don't defer.
</task>

<skills>
Invoke ALL of these explicitly at session start:
- `kr-spec-review` — for analyzing old SPEC sections being absorbed into §7
- `kr-research` — for domain research on design choices (consensus mechanisms, taxonomy placement)
- `thinking-frameworks` — for multi-angle analysis on the 4 design decisions
- `kr-integrity` — for T-1 through T-7 threat analysis on each section
- `critical-review` — for self-verification of produced sections
- `prompt-engineer` — for Phase 3 LLM prompt specification in §7.2
</skills>

<quality>
Take all your time. No rush. Use maximum depth of thinking. Every field in §7 becomes a real piece of knowledge in my mind — a wrong attribution rule means I study a text believing the wrong scholar wrote it. Every error code in §8 that's missing means a failure goes silent. Every field in §2.2 that doesn't trace back to a §7 step is an orphan that will confuse the builder.

After writing each section, run a programmatic verification script (the pattern from sessions 1 and 2). After all three sections, write a session 3 handoff document following the same structure as the session 2 handoff. If context degrades before finishing all three sections, stop, write the handoff for what's done, and tell me to start a new chat.
</quality>
