Pull the repo and read NEXT.md. This is the kr-integrity 8-lens audit of the complete excerpting SPEC. Run `git log --oneline -5` to see current state. Before any work, read `reference/protocols/QUALITY_AXIOM.md` and scan `ls /mnt/skills/user/` to confirm available skills.

<session_context>
The excerpting SPEC is COMPLETE — 2342 lines, 12 sections (§1–§10, with §2 split into §2.1/§2.2/§2.3). Written across sessions 1–4. Session 4 handoff: `reference/archive/sessions/excerpting_spec_session4_handoff.md`.

The SPEC synthesizes three old SPECs (passaging, atomization, excerpting) into a single 3-phase engine validated by experiments on 23 Shamela divisions across 7 genres.

No owner domain comments to resolve — this is a pure technical integrity audit. The goal: can Claude Code build from this SPEC with zero clarifying questions?

HEAD commit: `f525372` (session 4 handoff). Working tree is clean.
</session_context>

<task>
Run the kr-integrity 8-lens audit on `engines/excerpting/SPEC.md`.

**Audit in 2 chunks (respond to each, I will say "continue" between them):**

**Chunk 1 — Structural foundation (§1 through §5, lines 16–1204, 1189 lines):**
- §1 Purpose and Scope (lines 16–78)
- §2.3 Internal Data Model (lines 79–278)
- §2.1 Input Contract (lines 279–362)
- §2.2 Output Contract (lines 363–514)
- §3 Self-Containment Standard (lines 515–600)
- §4 Phase 1: Deterministic Preprocessing (lines 601–764)
- §5 Phase 2: LLM Teaching Unit Extraction (lines 765–1204)

**Chunk 2 — Behavioral specification (§6 through §10, lines 1205–2342, 1138 lines):**
- §6 Domain-Specific Processing Rules (lines 1205–1359)
- §7 Phase 3: Metadata Enrichment (lines 1360–1868)
- §8 Error Handling and Configuration (lines 1869–2032)
- §9 Deferred Capabilities (lines 2033–2109)
- §10 Test Requirements (lines 2110–2342)

**For each chunk, apply all 8 lenses:**
1. Zero Ambiguity — could two developers build different things?
2. Knowledge Corruption Paths — read `KNOWLEDGE_INTEGRITY.md` (224 lines), check T-1 through T-7
3. Silent Failure Patterns — read `SILENT_FAILURES.md` (176 lines), check all 7 patterns
4. Error Path Completeness — every error code reachable? every failure handled?
5. Contract Consistency — §2.2 output matches what §4/§5/§7 actually produce?
6. Assumption Identification — what hasn't been empirically tested?
7. Implementer's Reading — read as CC about to build. any "I'd have to guess" moments?
8. Extension-Blocking Assumptions — do deferred capabilities (§9) have working hooks?

**After both chunks:** Compile all findings into a single verdict. If any findings exist → BLOCKED (fix in SPEC before proceeding). If zero findings → ACCEPT (SPEC is implementation-ready, proceed to contracts.py rewrite).

If context degrades during Chunk 1 (you're past prompt 4-5 and losing precision), stop, write what you have, and tell me to start a new chat for Chunk 2.
</task>

<what_to_read>
In this order:
1. `NEXT.md` — current task directive (110 lines)
2. `reference/archive/sessions/excerpting_spec_session4_handoff.md` — accumulated ID registries, design decisions (98 lines)
3. `reference/protocols/QUALITY_AXIOM.md` — the architect is the sole quality gate
4. `KNOWLEDGE_INTEGRITY.md` — the 7 corruption threats (224 lines) — needed for Lens 2
5. `SILENT_FAILURES.md` — the 7 silent failure patterns (176 lines) — needed for Lens 3
6. `engines/excerpting/SPEC.md` lines 16–1204 (Chunk 1) — read in full, do NOT skip

Do NOT read the full SPEC upfront. Read Chunk 1, audit it, deliver findings. Then read Chunk 2 after I say "continue."
</what_to_read>

<skills>
Invoke ALL of these explicitly at session start:
- `kr-integrity` — the primary skill for this task (8 lenses)
- `critical-review` — self-verification of your own audit findings
- `thinking-frameworks` — multi-angle analysis on ambiguous cases
</skills>

<quality>
Take all your time. No rush. The integrity audit is the last quality gate before implementation. Every missed finding becomes a bug in the engine, which becomes a wrong belief in the owner's mind.

The most dangerous finding is the one that looks like "not a problem" at first glance. When you encounter something that makes you think "this is probably fine," that's the signal to investigate harder, not to skip it.

Every finding blocks. There is no "non-blocking" category. If it's worth writing down, it blocks.

After the audit, if you find zero issues, say so with confidence. If you find issues, list them precisely with SPEC line numbers and proposed fixes. Do NOT rationalize findings away to maintain momentum.
</quality>
