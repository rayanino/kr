Pull the repo and read NEXT.md. Your task is to prepare a Claude Code handoff for the contracts.py rewrite. Run `git log --oneline -5` to see current state. Before any work, scan `ls /mnt/skills/user/` for available skills.

<session_context>
The excerpting SPEC passed its kr-integrity 8-lens audit AND a deep post-audit review. Total defects found and fixed: 11 HIGH, 15 MEDIUM, 2 LOW across commits `10537ce` and `2ae92ac`. The SPEC is now 2387 lines, 28 error codes, 29 invariants, 34 verification checks, 22 domain rules. It is implementation-ready.

The current `engines/excerpting/contracts.py` (557 lines) was written for the OLD 7-engine architecture. It defines types like `LifecycleStage`, `ContextAtomRole`, `ExcerptStatus` that no longer exist in the new SPEC. It must be rewritten from scratch — not patched.

HEAD commit: `2ae92ac` (deep review fixes). Working tree is clean.
</session_context>

<task>
Prepare a CC handoff for the contracts.py rewrite. This means:

1. **Invoke `kr-preparing-cc-handoffs`** — follow all 9 steps literally. This skill defines the handoff protocol.
2. **Also invoke `critical-review`** — self-verify the handoff before committing.
3. **Rewrite NEXT.md** as a CC-ready directive for the contracts.py task.

The CC task (what NEXT.md should instruct CC to do):
- Delete the existing `contracts.py` and write it from scratch.
- Define all types from the SPEC: enumerations (§2.3.1), intermediate types (§2.3.2–§2.3.4), output type (§2.2.2), sub-types, error codes (§8.1), and invariant validators.
- Use Pydantic models. Follow normalization engine patterns (`engines/normalization/contracts.py`).
- Add factory helpers for tests (following `engines/normalization/tests/conftest.py` patterns).
- All 28 error codes as constants or an enum.
- Invariant validator functions for I-AC-*, I-CS-*, I-TU-*, I-ER-*.

What the NEXT.md must NOT tell CC to do:
- No implementation logic (Phase 1/2/3 processing code). Only type definitions and validators.
- No LLM prompt text (that stays in the SPEC, not in code).
- No test files yet (those come in build prep, Step 3c).
</task>

<what_to_read>
In this order — read each fully before starting work:

1. `NEXT.md` — current task directive (confirms Step 3b is next)
2. `reference/archive/sessions/excerpting_integrity_audit_handoff.md` — lists ALL new artifacts from the audit (chunk_index in excerpt_id, PageRange type, layer_split_points, footnote_renumber_map, school_confidence, verification confidence, new review flags, EX-A-012, merge size guard, F-DET-2 substring extraction, F-DET-9 ScholarAttribution mapping, evidence_refs scope correction). These MUST appear in contracts.py.
3. `reference/protocols/HANDOFF_PROTOCOL.md` — the 9-step protocol (if it exists; otherwise follow the kr-preparing-cc-handoffs skill steps)
4. `engines/excerpting/SPEC.md` — the behavioral authority. Read §2.3 (data model, lines ~79–278), §2.2 (output contract, lines ~363–520), and §8.1 (error codes, lines ~1915–1970) in full. These define what contracts.py must contain.
5. `engines/normalization/contracts.py` — the reference implementation CC should follow for patterns (Pydantic models, field validation, error code constants)
6. `engines/normalization/tests/conftest.py` — the factory helper patterns CC should follow

Do NOT read the entire SPEC — only the sections listed above. The SPEC is 2387 lines; reading it all would waste context. The data model and error catalog sections are what CC needs for contracts.py.
</what_to_read>

<critical_new_artifacts>
The integrity audit and deep review introduced artifacts that the old NEXT.md doesn't mention. The handoff MUST account for all of these:

1. **excerpt_id format changed:** `exc_{source_id}_{div_id}_{chunk_index}_{unit_index}` (was missing chunk_index)
2. **chunk_index derivation:** 0 for unsplit, split_info.chunk_index for split
3. **PageRange type:** `{volume: int|null, start_page: int, end_page: int}` — new type definition needed
4. **AssemblyMetadata gained 2 fields:** `layer_split_points: list[int]`, `footnote_renumber_map: dict[str,str]|null`
5. **school_confidence:** now produced by enrichment LLM (added to UnitEnrichment schema)
6. **VerificationItem gained `confidence` field:** for school_confidence computation
7. **review_flags expanded:** added `decontextualization_risk`, `verification_skipped`
8. **EX-A-012:** new error code (diacritic-mismatched snippet)
9. **F-DET-2 primary_text:** substring extraction, not split+rejoin
10. **F-DET-9 ScholarAttribution:** explicit field mapping + dedup rule with §7.2
11. **evidence_refs source:** Deterministic only (not "Deterministic + LLM")
12. **Merge size guard:** §4.4 step 2 checks combined size before merging
</critical_new_artifacts>

<skills>
Invoke ALL of these explicitly at session start:
- `kr-preparing-cc-handoffs` — the primary skill (9-step handoff protocol)
- `critical-review` — self-verify the handoff

Also scan `ls /mnt/skills/user/` and pick any additional relevant skills.
</skills>

<quality>
The handoff is the last artifact before CC starts building. Every gap in the handoff becomes a guess in the implementation. Every stale reference becomes a wrong type definition.

Specific quality checks:
- Every type, field, and enum in the SPEC §2.2, §2.3, and §8.1 must appear in the handoff.
- Every file reference in the handoff must be verified to exist (tool call, not memory).
- The normalization engine's contracts.py patterns must be read fresh, not described from memory.
- The handoff must explicitly list the 12 new artifacts above and verify each appears in the SPEC.

After writing the handoff, do the kr-preparing-cc-handoffs Step 8 adversarial read: re-read NEXT.md as CC seeing it for the first time. Any place CC would have to guess → fix before committing.
</quality>
