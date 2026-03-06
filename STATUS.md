# خزانة ريان — Project Status

**Last updated:** 2026-03-06
**Phase:** Preparatory phase — shared component SPECs in progress (human gate complete, feedback complete, user_model next)
**Tests:** 903 pass, 37 skip, 1 fail (API key) — all ABD-era; no KR-specific tests yet

---

## What Exists (current state of every component)

### Documents
| Document | State | Detail |
|----------|-------|--------|
| VISION.md | Corrected (v1.1.0) | All sections audited and corrected. §6.4 OPEN QUESTION resolved (D-040). §10, §12 rewritten for D-019. §13.2.6 updated for SPEC-defined directory structure. §2 glossary updated. |
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
| 7 schemas in schemas/ | ABD-era, superseded | Schemas now authoritatively defined in engine SPECs §2/§3. JSON files to be regenerated during implementation. |
| root CLAUDE.md | Exists | Needs update for implementation phase. |
| 7 engine CLAUDE.md | Exist | Updated alongside each SPEC. |
| kr_decisions.md | 41 decisions | D-001 to D-041. |
| SCHEMA_ANALYSIS.md | Updated | Notes all SPECs complete; JSON files superseded by SPEC definitions. |
| DOMAIN.md | Complete (~750L) | Core identity, scholarly domain knowledge, evidence hierarchy, integrity risks, design implications. |
| USER_SCENARIOS.md | Complete (8 scenarios) | Day 1 through Year 3 + book briefing + science map + error correction. |
| ENTRY_EXAMPLE.md | Complete (~170L) | Calibration target for synthesis quality. |
| PIPELINE_TRACE.md | Complete (~165L) | Full 7-stage trace showing metadata accumulation. |
| RESOURCES.md | Updated (~320L) | Arabic NLP, OCR, synthesis tools, and related catalog. Updated with each SPEC's resource survey. |

### Cross-SPEC Consistency (verified 2026-03-05)
| Boundary | Status |
|----------|--------|
| Source → Normalization | Consistent. Normalization reads frozen files + metadata.json as source SPEC defines. |
| Normalization → Passaging | Consistent. Passaging reads manifest.json + content.jsonl as normalization SPEC defines. |
| Passaging → Atomization | Consistent. Atomization reads passages.jsonl as passaging SPEC defines. |
| Atomization → Excerpting | Consistent. Fixed: removed spurious `primary` value from excerpting's `source_layer` input. |
| Excerpting → Taxonomy | Consistent. Taxonomy validates excerpt fields matching excerpting's output contract. |
| Taxonomy → Synthesizing | Consistent. Synthesizing reads placed excerpts as taxonomy SPEC defines. |
| Metadata pass-through (D-023) | Verified. All metadata accumulates from source to synthesis without loss. |

### Code (legacy from ABD — functional but not designed for KR)
ABD code has zero design authority (D-019). SPECs define what to build. ABD code is reference material only.

| Engine | ABD Source Lines | ABD Tests |
|--------|-----------------|-----------|
| source | 2,284L | 112 |
| normalization | 4,352L | 292 |
| passaging | 279L (scaffold) | 0 |
| atomization | 0L (in excerpting) | 0 |
| excerpting | 3,309L | 258 |
| taxonomy | 2,377L | 109 |
| synthesis | 0L | 0 |
| shared/consensus | 1,749L | passing |
| shared/human_gate | 881L | 28 |
| shared/validation | 779L | passing |

### Infrastructure
| Component | State |
|-----------|-------|
| `.claude/` | Exists but empty — needs population for Claude Code |
| CI/CD | None |
| Python packaging | `_paths.py` only |
| Integration tests | None |
| API keys | `.env.template` exists. Owner provides keys on request. |

---

## What Remains Before Implementation

The preparatory phase deliverables are substantially complete. Remaining items:

1. **Shared component SPECs** — human_gate SPEC complete, feedback SPEC complete, consensus SPEC complete (D-041), validation SPEC complete. Remaining: user_model, scholar_authority. These are lower priority than engine SPECs but needed before implementation.
2. **Scholar interface SPEC** — the user-facing intelligence layer has no SPEC yet.
3. **User model SPEC** — shared component for persistent user state.
4. **`.claude/` directory** — needs population with agents, commands, hooks, settings for Claude Code.
5. **Root CLAUDE.md rewrite** — needs to conform to §13.3.2 requirements for implementation phase.
6. **إملاء SCIENCE.md** — minimal Level 3 doc for first science.

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
