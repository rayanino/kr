# NEXT — Passaging Engine SPEC Design

## Context

Architecture C has been committed (see `experiments/architecture_test/ARCHITECTURE_DECISION.md`).

The pipeline is now 6 engines total, 4 remaining:
```
Source ✅ → Normalization ✅ → Passaging → Excerpting → Taxonomy → Synthesis
```

The passaging engine is the next engine to build. It is **deterministic** (no LLM calls) and **simplified** under Architecture C — it no longer needs argument detection, completeness forecasting, or discourse_flow dependency.

## Your Task

Design the passaging engine SPEC (`engines/passaging/SPEC_CORE.md`).

### What the Passaging Engine Does

Takes normalized content units (from normalization engine output) and assembles them into **passages** — contiguous text segments that are the input to the excerpting engine.

Core responsibilities:
1. **Cross-page assembly:** Join content units that belong to the same division across page boundaries, using boundary_continuity signals to determine join behavior (mid_word → no space, mid_sentence → space, mid_paragraph → newline, section_break → double newline)
2. **Passage sizing:** Target a passage size range appropriate for LLM processing (experiment showed 300-2000 Arabic words works well for excerpting). Split oversized divisions into passages; keep small divisions as single passages.
3. **Boundary placement:** Place passage boundaries at natural structural breaks (section headers, paragraph breaks, topic transitions). D-011 (hard): never split mid-teaching-unit. Enforce via structural heuristics — break at headings, numbered items, explicit topic markers — not by LLM inference.
4. **Format-specific handling:** Different text types (hadith collections, commentary, fiqh مسائل, grammatical catalogs) have different natural chunking points. The passaging engine must handle these differently.
5. **Metadata assembly:** Each passage carries forward its source metadata, division path, text layer information, content flags, and boundary_continuity signals for the excerpting engine's benefit.

### What the Passaging Engine Does NOT Do

- **No LLM calls.** Passaging is entirely deterministic.
- **No argument detection.** This was moved to the excerpting engine under Architecture C.
- **No completeness forecasting.** The excerpting engine handles self-containment evaluation.
- **No discourse_flow dependency.** This field is `None` in all normalization output and will remain so.

### Design Approach

Use `kr-research` and `thinking-frameworks` (DEEP tier — this is the SPEC for the next engine to build).

1. **Read the normalization engine's output contracts.** The passaging engine's input IS the normalization engine's output. Read:
   - `engines/normalization/SPEC_CORE.md` — especially the output schema (§5, §6)
   - `engines/normalization/tests/` — understand what the normalized packages look like
   - `experiments/architecture_test/packages/` — real normalized packages from the experiment

2. **Read the original passaging SPEC if it exists.** There may be a draft at `engines/passaging/SPEC_CORE.md`. If so, read it and decide what to keep vs discard under Architecture C.

3. **Study the experiment's division extraction script.** `experiments/architecture_test/extract_divisions.py` already implements basic cross-page assembly and passage construction. This is a prototype of the passaging engine's core logic. Read it for patterns and edge cases.

4. **Research passage boundary heuristics.** What structural signals in Arabic scholarly text indicate natural break points? Headings, numbered مسائل, hadith boundaries (عن... عن...), paragraph breaks, verse markers, etc. Search broadly.

5. **Write the SPEC.** Follow the established SPEC format from normalization engine:
   - §1: Purpose and scope
   - §2: Input contracts (what normalization engine provides)
   - §3: Output contracts (what the excerpting engine needs)
   - §4: Processing rules (the actual passaging logic)
   - §5: Error handling
   - §6: Known limitations

### Constraints

- D-011 stays HARD. Never split a passage mid-teaching-unit. Enforce with structural heuristics.
- Target passage size: 300-2000 Arabic words (validated in Architecture C experiment).
- Must handle multi-layer texts (sharh/matn) — layers may need independent passage boundary placement.
- Must preserve ALL upstream metadata fields (D-023: never delete, always pass through).
- CRLF normalization — owner is on Windows.
- Error codes must follow the SPEC §7 pattern from normalization engine.

### Skills to Use

- `kr-research` (study normalization output contracts, passage boundary heuristics)
- `thinking-frameworks` (DEEP tier — engine-level architectural decisions)
- `critical-review` (verify SPEC before delivering)
- `kr-integrity` (audit SPEC for silent failure patterns and knowledge corruption threats)

### Do NOT Do

1. Do NOT write implementation code. The SPEC is the deliverable. Claude Code builds from the SPEC.
2. Do NOT modify normalization or source engine code.
3. Do NOT relax D-011. It stays hard per the architecture decision.
4. Do NOT assume discourse_flow will ever be populated. It won't.
5. Do NOT design for LLM-assisted passaging. This engine is deterministic.

## Read First

1. This file (NEXT.md)
2. `experiments/architecture_test/ARCHITECTURE_DECISION.md` — the architecture commitment
3. `engines/normalization/SPEC_CORE.md` — input contracts
4. `experiments/architecture_test/extract_divisions.py` — passaging prototype
5. `reference/ENGINE_BUILD_BLUEPRINT.md` — engine build process
6. `KNOWLEDGE_INTEGRITY.md` — corruption threats to design against
