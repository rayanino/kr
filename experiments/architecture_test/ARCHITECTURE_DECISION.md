# Architecture Decision: Commit Architecture C (C-1)

**Date:** 2026-03-22
**Decision maker:** Claude Chat (Architect)
**Status:** COMMITTED

---

## Decision

KR commits to **Architecture C, variant C-1** (two-phase internal LLM) for the remaining 4 engines.

**D-011 (passage containment rule):** Stays HARD. Experiment showed no measurable benefit from cross-boundary context.

## Remaining Engine Pipeline

```
Source Engine ✅ → Normalization Engine ✅ → Passaging → Excerpting → Taxonomy → Synthesis
                                            (det.)      (LLM, 2-phase)  (LLM)    (LLM)
```

**4 engines remain**, down from the original 5 (atomization merged into excerpting):

1. **Passaging engine** — Deterministic. Cross-page assembly, format-specific chunking, passage boundary placement. Core-only: drops the argument detection, completeness forecasting, and discourse_flow machinery from §4.B of the original passaging SPEC. D-011 (passage must contain complete teaching units) remains a hard constraint, enforced by passage boundary heuristics not by LLM inference.

2. **Excerpting engine** — LLM-powered. Absorbs atomization. Internal two-phase architecture:
   - **Phase 1 (classify):** LLM classifies each sentence/segment in a passage by scholarly function (definition, evidence_hadith, opinion_statement, etc.)
   - **Phase 2 (group):** LLM groups classified segments into teaching units, evaluates self-containment, produces structured excerpt records
   - Input: normalized passages from passaging engine
   - Output: teaching unit records with boundaries, classifications, self-containment flags, Arabic descriptions

3. **Taxonomy engine** — Unchanged from original design. Builds topic hierarchies from teaching units.

4. **Synthesis engine** — Unchanged from original design. Produces encyclopedic entries at taxonomy leaves from excerpts.

## Evidence Summary

### Q1: Can an LLM identify teaching units? → YES (10/10 divisions, both approaches)

Tested on 10 divisions across 5 genres (nahw, fiqh, usul, balagha, hadith). Both single-phase and two-phase approaches produced boundaries that a careful reader of the Arabic text would agree with. Key evidence:

- **Structurally explicit texts** (nahw حروف زائدة, hadith collections): Perfect alignment with text's own organizational markers (one letter per unit, one hadith per unit)
- **Conceptually complex texts** (usul أقسام المفتين, fiqh scholarly مسألة): Correct identification of hierarchical structures (حالات المفتي), scholarly positions (أقوال الثلاثة), and ترجيح
- **Survey texts** (balagha الإيجاز): Correct segmentation of sequential scholar-by-scholar exposition
- **Arabic descriptions** are accurate and demonstrate genuine scholarly comprehension, not surface pattern matching
- **Self-containment judgments** are reasonable and internally consistent

### Q2: Single-phase vs two-phase → TWO-PHASE WINS (B ≥ A in 10/10 divisions)

| Metric | Single-phase (A) | Two-phase (B) |
|--------|-------------------|---------------|
| Avg units/division | 15.1 | 12.2 |
| Over-segmentation cases | 4/10 (nahw 20, fiqh 4, fiqh 64, usul 22) | 0/10 |
| Units marked not self-contained | ~30% in over-segmented divisions | <10% |

The mechanism: single-phase tries to identify, classify, and segment simultaneously, creating pressure toward finer granularity (each classified sentence → potential boundary). Two-phase first classifies, then groups into pedagogically meaningful units.

The most dramatic case: nahw div_20 (أبنية الأسماء الثنائية) — A produced 26 units (each morphological pattern as a unit), B produced 13 (grouped by category). A's units are not self-contained; B's are.

### Q3: Cross-boundary context → NO MEASURABLE BENEFIT (2 divisions tested)

- fiqh div_4: B=8 units, C=7 units (minor regrouping, no split argument detected)
- fiqh div_64: B=8 units, C=9 units (minor refinement, no split argument corrected)

Neither case demonstrated the scenario D-011 softening was designed for. Context caused minor regroupings, not fundamental corrections.

**Implication:** D-011 stays hard. If future evidence shows split arguments are a real problem at scale, revisit during the excerpting engine's own evaluation — but do not relax the constraint preemptively.

## What Changes in the Passaging SPEC

The original passaging SPEC (§4.B) included significant complexity to support downstream atomization:
- Argument detection and classification
- Completeness forecasting (will a passage contain a complete teaching unit?)
- `discourse_flow` field dependency (which is `None` in all normalization output)
- Complex D-011 enforcement logic requiring near-perfect boundary placement

Under Architecture C, the passaging engine becomes simpler:
- **Keeps:** Cross-page assembly, format-specific chunking (hadith vs commentary vs fiqh), passage size targeting, boundary placement at structural markers
- **Drops:** Argument detection, completeness forecasting, discourse_flow dependency, LLM-assisted boundary refinement
- **D-011:** Enforced by deterministic heuristics (break at structural markers, never mid-sentence), not by LLM inference about argument completeness

## What the Merged Excerpting Engine Looks Like

The excerpting engine handles what was previously two engines (atomization + excerpting). Internally:

```
Passage → [Phase 1: Classify] → Classified segments → [Phase 2: Group] → Teaching Units
```

Phase 1 (classify): One LLM call per passage. Classifies each segment by scholarly function using the function taxonomy: definition, rule_statement, evidence_quran, evidence_hadith, evidence_ijma, evidence_rational, opinion_statement, refutation, condition_exception, example, narration, cross_reference, editorial_note, structural_transition.

Phase 2 (group): One LLM call per passage. Takes classified segments and produces teaching unit records:
- Unit boundaries (word offsets into passage text)
- Primary and secondary scholarly functions
- Self-containment assessment
- Arabic description
- Cross-reference to source passage and source book

The two-phase approach was validated empirically: it produces more pedagogically appropriate boundaries than single-phase across all genres tested.

## Risks and Mitigations

**Risk: 10 divisions is a small sample.**
Mitigation: This was a viability test, not a final evaluation. The excerpting engine build will include its own evaluation phase with 50+ baselines per the Engine Build Blueprint. If viability were the wrong conclusion, the per-engine evaluation would catch it before the taxonomy engine depends on its output.

**Risk: Same model family (Opus) for test and evaluation.**
Mitigation: The evaluation was qualitative — the architect read the Arabic text and judged whether boundaries are sensible. Most boundary placements are structurally obvious (one hadith per unit, one مسألة per unit). The formal metrics (F1, classification accuracy) are secondary to this qualitative judgment.

**Risk: Simplified passaging may produce passages that are harder for the excerpting engine to process.**
Mitigation: The passaging engine still targets structural boundaries and appropriate passage sizes. The excerpting engine's LLM is more resilient to imperfect passage boundaries than the original atomization engine would have been, because it can use context within the passage to identify teaching units even when the passage boundary isn't perfect.

**Risk: D-011 staying hard may cause problems at scale.**
Mitigation: Conservative choice. If the excerpting engine's evaluation reveals systematic problems with hard D-011, we can soften it then with much more data. Premature relaxation without empirical evidence would be worse.

## Next Step

Begin passaging engine SPEC design under the simplified Architecture C requirements.
