# خزانة ريان — Project Status

**Last updated:** 2026-03-06
**Phase:** Preparatory — SPEC refinement in progress (0/14 refined). All 14 SPECs drafted. Implementation begins after SPECs pass refinement.
**Tests:** ABD-era tests archived. No KR-specific tests yet — written during implementation.

---

## What Exists (current state of every component)

### Documents
| Document | State | Detail |
|----------|-------|--------|
| VISION.md | Corrected (v1.2.0) | All sections audited. v1.2.0: Cross-SPEC consistency verified. §8 updated with component SPEC references and D-033. §9 updated. §11 extended with Principles 13–15 (D-018, D-033, D-023). §13.2 repo layout updated for all 14 components. |
| Source engine SPEC | Complete | 582L. D-024 through D-027. |
| Normalization engine SPEC | Complete | 664L. D-028 through D-031. |
| Passaging engine SPEC | Complete | 502L. |
| Atomization engine SPEC | Complete | 580L. D-034, D-035. |
| Excerpting engine SPEC | Complete | 559L. D-036, D-037. |
| Taxonomy engine SPEC | Complete | 562L. D-038, D-039. |
| Synthesizing engine SPEC | Complete | 582L. D-040. |
| Consensus SPEC | Complete | 405L. D-041. LiteLLM + Instructor, parallel independent comparison, three comparison strategies. |
| Validation SPEC | Complete | 406L. Four validation categories, background sweep, two transformative capabilities. |
| Human Gate SPEC | Complete | 413L. Checkpoint lifecycle, pre-approval policies, bidirectional validation, confidence calibration, gate learning. |
| Feedback SPEC | Complete | 461L. |
| User Model SPEC | Complete | 368L. D-042. |
| Scholar Authority SPEC | Complete | 462L. |
| Scholar Interface SPEC | Complete | 872L. Hybrid retrieval pipeline (Qdrant + Arabic embeddings + cross-encoder). 5 transformative capabilities: debate simulation, scholarly fingerprinting, unanswered question discovery, optimal source prediction, knowledge decay prediction. |
| 7 schemas in schemas/ | ABD-era, superseded | Schemas now authoritatively defined in engine SPECs §2/§3. JSON files to be regenerated during implementation. |
| root CLAUDE.md | Complete (62L) | §13.3.2 compliant, implementation-focused. |
| 7 engine CLAUDE.md | Exist | Updated alongside each SPEC. |
| kr_decisions.md | 42 decisions | D-001 to D-042. |
| SCHEMA_ANALYSIS.md | Updated | Notes all SPECs complete; JSON files superseded by SPEC definitions. |
| DOMAIN.md | Complete (~750L) | Core identity, scholarly domain knowledge, evidence hierarchy, integrity risks, design implications. |
| USER_SCENARIOS.md | Complete (8 scenarios) | Day 1 through Year 3 + book briefing + science map + error correction. |
| ENTRY_EXAMPLE.md | Complete (~170L) | Calibration target for synthesis quality. |
| PIPELINE_TRACE.md | Complete (~165L) | Full 7-stage trace showing metadata accumulation. |
| RESOURCES.md | Updated (~320L) | Arabic NLP, OCR, synthesis tools, and related catalog. Updated with each SPEC's resource survey. |

### Cross-SPEC Consistency (verified 2026-03-06, all 14 SPECs)
| Boundary | Status |
|----------|--------|
| Source → Normalization | Consistent. Normalization reads frozen files + metadata.json as source SPEC defines. |
| Normalization → Passaging | Consistent. Passaging reads manifest.json + content.jsonl as normalization SPEC defines. |
| Passaging → Atomization | Consistent. All fields atomization expects (content_flags, text_fidelity, verse_info, review_flags) present in passaging output. |
| Atomization → Excerpting | Consistent. Excerpting reads all atom fields including atom_relations and embedded_refs. |
| Excerpting → Taxonomy | Consistent. All required and expected taxonomy input fields present in excerpting output. Fixed: added school_confidence to taxonomy provenance list. |
| Taxonomy → Synthesizing | Consistent. Synthesis reads placed excerpts + coverage data + tree structure as taxonomy SPEC defines. |
| Shared components ↔ engines | Consistent. Consensus, validation, human_gate use library-call patterns. Feedback uses pull model from human gate archive. |
| Scholar authority ↔ all engines | Consistent. Lookup/enrichment API pattern. Source engine is primary creator. |
| User model ↔ scholar interface | Consistent. Event-based writes, query-based reads. D-042 expertise consolidation verified in human_gate SPEC. |
| Scholar interface ← all components | Consistent. All reads through defined APIs matching component output contracts. |
| Metadata pass-through (D-023) | Verified across full chain. All metadata accumulates from source to synthesis without loss. |
| Terminology coherence | Verified. "entry", "excerpt", "leaf", "passage", "source" used consistently across all 14 SPECs + VISION.md. |

### Code
ABD-era code archived to `reference/archive/abd_code/` (D-019: zero design authority). Engine `src/` and `tests/` directories are clean — ready for KR-specific implementation after SPEC refinement.

ABD-era schemas archived to `schemas/archive/`. New schemas will be generated from SPEC §2/§3 during implementation.

### Infrastructure
| Component | State |
|-----------|-------|
| `.claude/` | Populated — settings.json, 7 commands, 4 agents (researcher, spec-writer, integrity-checker, code-reviewer), 5 skills |
| Scripts | orient.py, check_compliance.py, check_spec_quality.py, creative_verification.py, session_quality_gate.py, verify_metadata_flow.py, refinement_status.py, extract_vision_sections.py, decompose_spec.py |
| CI/CD | None |
| Python packaging | `_paths.py` only |
| Integration tests | None |
| API keys | `.env.template` exists. Owner provides keys on request. |

---

## What Remains Before Implementation

Remaining preparatory tasks (tracked by `SESSION_TYPES.md` and `IMPLEMENTATION_GATE.md`):

**SPEC refinement (CREATIVE → PRECISION → optional HARDENING per engine):**
| Engine | CREATIVE | PRECISION | HARDENING | Ready? |
|--------|----------|-----------|-----------|--------|
| source | pending | - | - | No |
| normalization | pending | - | - | No |
| passaging | pending | - | - | No |
| atomization | pending | - | - | No |
| excerpting | pending | - | - | No |
| taxonomy | pending | - | - | No |
| synthesis | pending | - | - | No |
| shared (6) | skip (have §4.B) | pending | - | No |
| scholar interface | pending | - | - | No |

**Other preparatory tasks:**
1. Machine-readable contracts — 2/7 engines have contracts.py (source, normalization)
2. Test data — 7 fixture sets exist. Gold baselines not yet created.
3. GUI skeleton — not yet created (see `interface/GUI.md`)
4. API keys — .env file not yet created from .env.template
5. Claude Code environment verification — `.claude/` populated but not tested with Claude Code

---

## Key Decisions Made

All major architectural decisions are resolved. See kr_decisions.md for full details (D-001 through D-040). Key decisions by engine:

- **Source:** Three-tier identity (D-024), scholar authority registry (D-025), text fidelity separate from trust (D-026), work relationship graph (D-027)
- **Normalization:** OCR strategy (D-028), normalized package schema (D-029), multi-layer detection (D-030), footnote markers (D-031)
- **Passaging:** Passage containment rule (D-011)
- **Atomization:** Two-tier type system (D-034)
- **Excerpting:** Multi-model consensus (D-036), three-phase pipeline (D-037)
- **Taxonomy:** Two-stage placement (D-038), limited consensus (D-039)
- **Synthesis:** Grounding_type traceability (D-040), entries in Arabic (D-032)

---

## Session Handoff

The next session's task, context, and file list are in `NEXT.md` at the repo root.
