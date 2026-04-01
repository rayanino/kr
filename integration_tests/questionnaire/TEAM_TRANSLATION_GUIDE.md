# Team Translation Guide (Document C)

> Maps each owner answer to SPEC rules, prompt parameters, and DR decisions. **Never shown to the owner.**

## How to Use This Guide

After the owner completes the questionnaire and after the 6-coworker critical evaluation:
1. For each confirmed answer, find the matching row below
2. Update the referenced SPEC section or prompt parameter
3. Record the traceability: "SPEC change X traces to owner answer [ID] + coworker confirmation [list]"

## Translation Table

| Interaction | Dimension | Owner Answer Maps To | SPEC Section | Prompt Parameter | Current Default | DR Decision |
|---|---|---|---|---|---|---|
| F-1 | Mental model | Owner's definition of "excerpt" | excerpting/SPEC.md §1 (Definition) | — | "A self-contained unit of scholarly knowledge" | — |
| F-2 | User model | Study workflow expectations | All engines (user model) | — | No user model defined | — |
| F-3 | Quality baseline | What "good" means to the owner | excerpting/SPEC.md §4 (Behavioral Rules) | Quality gate thresholds | — | — |
| F-4 | Quality floor | What's unacceptable | excerpting/SPEC.md §4 (minimum viability) | Rejection criteria | — | — |
| F-5 | Self-containment gate | Accept/reject PARTIAL with hints | excerpting/SPEC.md §4.A (Self-Containment) | Phase 2c gate strictness | PARTIAL allowed with context_hint | — |
| F-6 | Original text fidelity | Reference tool vs learning tool | All engines (design philosophy) | Verbatim-copy rule strictness | Verbatim copy required | — |
| F-7 | Failure modes | Absolute constraints | excerpting/SPEC.md §4 (Error Handling) | — | — | — |
| F-8 | Taxonomy independence | Whether excerpting sees taxonomy tree | excerpting/SPEC.md §2 (Input) | Taxonomy input toggle | No taxonomy input | — |
| G-1 | Min excerpt size | Minimum viable excerpt length | excerpting/SPEC.md §4.B (Granularity) | min_excerpt_threshold | No minimum defined | — |
| G-2 | Max excerpt size | When to split long excerpts | excerpting/SPEC.md §4.B (Granularity) | max_excerpt_threshold | No maximum defined | — |
| G-3 | List handling | Numbered items: together or split | excerpting/SPEC.md §4.B (List Handling) | Phase 2b grouping criteria | Together (one excerpt) | — |
| G-4 | Semantic coupling | Exception + ruling coupling | excerpting/SPEC.md §4.B (Grouping) | Phase 2b coupling rules | Separate by function | — |
| SC-1 | Context hint quality | When summary notes are sufficient | excerpting/SPEC.md §4.A (Context Hints) | context_hint quality threshold | Any summary accepted | — |
| SC-2 | Cross-reference handling | Backward references (كما تقدم) | excerpting/SPEC.md §4.C (Cross-References) | xref_resolution_policy | Preserve as-is | — |
| SC-3 | Implicit context | Chapter-dependent excerpts | excerpting/SPEC.md §4.A (Self-Containment) | implicit_context_policy | Accept if FULL tagged | — |
| D-1 | Definition threshold | Minimum definition size for split | excerpting/SPEC.md §4.D (DR-1) | dr1_min_definition_length | 3 words (from DR rule) | DR-1 |
| D-2 | Connecting sentence | Split when relationship stated | excerpting/SPEC.md §4.D (DR-1) | dr1_connecting_sentence_rule | Split regardless | DR-1 |
| D-3 | Triple definitions | 3+ definitions per term | excerpting/SPEC.md §4.D (DR-1 extension) | dr1_multi_definition_policy | Not yet defined | DR-1 |
| E-1 | Evidence grouping | Per-verse vs grouped Quran evidence | excerpting/SPEC.md §4.E (DR-2) | dr2_quran_grouping | Currently deferred | DR-2 |
| E-2 | Evidence coupling | Hadith + ruling separation | excerpting/SPEC.md §4.E (DR-2) | dr2_evidence_ruling_coupling | Together | DR-2 |
| E-3 | Evidence type splitting | Multi-type evidence organization | excerpting/SPEC.md §4.E (DR-2) | dr2_multi_type_policy | Together | DR-2 |
| K-1 | Short khilaf | Short debate: together or split | excerpting/SPEC.md §4.F (DR-3) | dr3_short_threshold | Together (<800 words) | DR-3 |
| K-2 | Long khilaf | Long debate: split threshold | excerpting/SPEC.md §4.F (DR-3) | dr3_long_threshold | Split (>800 words) | DR-3 |
| K-3 | Position linking | Separate positions with links | excerpting/SPEC.md §4.F (DR-3) | dr3_link_policy | Preserve + link | DR-3 |
| GN-1 | Genre uniformity | One approach vs per-genre | excerpting/SPEC.md §4.G (Genre) | genre_specific_prompts | One-size-fits-all | — |
| GN-2 | Shaahid handling | Grammar examples in/out | excerpting/SPEC.md §4.G (Nahw) | nahw_shaahid_policy | Not yet defined | — |
| L-1 | Layer attribution | Editor note ownership | excerpting/SPEC.md §4.H (Layers) | layer_attribution_rule | Attribute to editor | — |
| L-2 | Commentary structure | Sharh+matn: one or two | excerpting/SPEC.md §4.H (Layers) | sharh_matn_split | Together | — |
| CJ-1 | Excerpting approach | Preferred split granularity | excerpting/SPEC.md §4.B + §4.E | Phase 2b + DR-2 calibration | — | DR-2 |
| CJ-4 | Metadata sufficiency | What metadata to display | excerpting/SPEC.md §3 (Output) | metadata_display_fields | All available fields | — |
| S-1 | Priority ranking | Dimension hierarchy | excerpting/SPEC.md §4 (Conflict Resolution) | dimension_priority_order | Not yet defined | — |
| S-2 | Ideal/worst excerpt | Quality definition | excerpting/SPEC.md §1 (Quality Definition) | — | — | — |

## Conflicting Answers Resolution

If the owner's answers contradict each other (common — e.g., wanting absolute self-containment AND per-ayah evidence splitting):

1. Note both answers and the conflict
2. Check if the priority ranking (S-1) resolves it
3. If not, present the conflict to the owner with a concrete example showing the tension
4. The resolution becomes a SPEC rule with explicit precedence

## Deferred Dimensions

These are NOT covered in the questionnaire, with reasoning:

| Dimension | Why deferred |
|-----------|-------------|
| Cross-book comparison (full) | Zero topics appear in 3+ campaign books. Revisit after Phase 3 with more books. |
| Multi-leaf taxonomy tagging | Requires VISION §1.2 amendment. Deferred to taxonomy pilot. |
| DR-2 (evidence-type splitting) | 3/5 reviewers rejected. Owner may re-open via E-1/E-2/E-3 answers. |
| UI/display preferences | No UI exists yet. Premature to ask. |
| Classical text validation | Rules derived from this questionnaire are calibrated on modern pedagogical texts (Taysir, Ibn Aqil, al-Iqtirah). Must be re-validated against classical unpunctuated texts (Al-Mughni, Fath al-Bari) when they enter the pipeline. Classical khilaf is structurally different from modern (nested dialectics vs numbered lists). See Gemini DR corpus diversification finding at `docs/coworker_reports/2026-04-01_phase0_hardening/gemini_dr_pedagogical_alignment.md`. |
| Pedagogical workflows (hifz, muraja'a, I'dad) | These are synthesis/UI layer concerns, not excerpting calibration. Owner's F-2 response provides initial signals. Deeper workflow integration belongs to the synthesis engine. See Gemini DR memorization framework analysis. |

## Technical Feasibility Flags

Some owner preferences may conflict with technical constraints. Known tensions:

| Owner Preference | Technical Constraint | Resolution Path |
|-----------------|---------------------|----------------|
| Per-ayah evidence splitting | Increases excerpt count 3-5x per evidence passage | Budget impact assessment needed |
| Absolute self-containment | Some scholarly texts are inherently referential | May need tiered self-containment (FULL_STRONG vs FULL_WEAK) |
| Taxonomy-aware excerpting | Taxonomy trees not trustworthy yet | Phase dependency — excerpting must work without taxonomy first |
