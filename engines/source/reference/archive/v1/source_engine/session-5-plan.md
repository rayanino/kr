# Session 5 Plan: Registration + Scholar Authority + Trust + Validation

**Pipeline steps:** Steps 7–8 (Registration, Trust Evaluation) + Validation + Human Gate
**Depends on:** Session 4 (hashing + dedup + freezing)

**⚠️ Scope risk:** This session builds 10 modules — roughly double the complexity of Sessions 3 and 4. If the session runs long, consider splitting: (a) shared components (scholar_authority, human_gate, validation) first, then (b) source-engine wrappers (trust_evaluator, registries, source validation) in a follow-up. The shared components are the blocking dependency for Session 6; the source-engine wrappers can overlap.

---

## Read First

1. `engines/source/SPEC_CORE.md` §4.A.2 Step 7 (Registration — atomic write-ahead log)
2. `engines/source/SPEC_CORE.md` §4.A.5 (Scholar Authority Model — full section)
3. `engines/source/SPEC_CORE.md` §4.A.8 (Trustworthiness Evaluation — full section)
4. `engines/source/SPEC_CORE.md` §4.A.9 (Work Relationship Tracking)
5. `engines/source/SPEC_CORE.md` §5 (Validation and Quality — all 6 Layer 1 checks + Layer 2)
6. `engines/source/SPEC_CORE.md` §8 (Configuration — recognized muhaqiqs, known publishers)
7. `engines/source/contracts.py` — `ScholarAuthorityRecord`, `WorkRegistryEntry`, `SourceRegistryEntry`, `TrustworthinessFactor`, `TrustTier`, `HumanGateCheckpoint`, `HumanGateTrigger`
8. `shared/scholar_authority/REQUIREMENTS_source.md`
9. `shared/human_gate/REQUIREMENTS_source.md`
10. `shared/validation/REQUIREMENTS_source.md`
11. `reference/KNOWLEDGE_INTEGRITY.md` Layer 4 (Human Gates — CAN/CANNOT verify lists)

## Modules to Build

| File | Purpose |
|------|---------|
| `shared/scholar_authority/src/scholar_authority.py` | `lookup()`, `register()`, `update()` — replace missing stub |
| `shared/scholar_authority/src/name_matching.py` | Already created in Session 3 (or 4). Verify present. |
| `shared/human_gate/src/human_gate.py` | Replace tracer stub. `create_checkpoint()`, `resolve()`, `get_pending()`, persistence. |
| `shared/validation/src/validation.py` | Replace tracer stub. Generic: schema validation, referential integrity, D-023. |
| `engines/source/src/validation.py` | Source-specific: 6 Layer 1 checks. Uses shared validation + source-specific logic. |
| `engines/source/src/trust_evaluator.py` | Replace stub. 5-factor weighted trust evaluation (§4.A.8). |
| `engines/source/src/human_gate.py` | Source-engine human gate wrapper. Batches checkpoints per source. |
| `engines/source/src/registries/source_registry.py` | Replace stub. Source registry CRUD with atomic write-ahead log. |
| `engines/source/src/registries/work_registry_store.py` | Replace stub. Work registry CRUD, work matching, relationship edges. |
| `engines/source/src/registries/scholar_registry.py` | Replace stub. Source-engine wrapper for shared/scholar_authority. |

## Fixtures to Test Against

All 13 fixtures — every fixture should be registerable:
- `tests/fixtures/shamela_real/01_nahw_simple/` through `12_multi_muq/`
- `tests/fixtures/alfiyyah_versified/`
- `tests/fixtures/GROUND_TRUTH.json` — `expected_trust` values for tier verification

**Trust evaluation specific tests:**
- Fixture 01 (classical, no muhaqiq) → should produce `verified`
- Fixture 03 (modern, no muhaqiq) → should produce `flagged`
- Fixture 11 (classical, with muhaqiq) → should produce `verified`
- Fixture 12 (modern, no muhaqiq) → should produce `flagged`

**Config files needed (create during session):**
- `library/config/recognized_muhaqiqs.json` — initial list from §8
- `library/config/known_publishers.json` — initial list from §8
- `library/config/transliteration.json` — initial table from §4.A.1
- `library/config/genre_synonyms.json` — initial synonyms from §8

## Build Steps

1. **Implement shared scholar authority.** `lookup()` with composite scoring, `register()` with ID generation, `update()` with 5 consistency checks. JSON file storage in `library/registries/scholars.json`.

2. **Implement shared human gate.** `create_checkpoint()` with persistence, `resolve()` with three-option response. MVP mode: auto-approve with logging. Persistence in `library/gates/`.

3. **Implement shared validation.** Generic `validate_output()` with Pydantic validation + referential integrity. `validate_enrichment_passthrough()` for D-023.

4. **Implement source-engine validation.** All 6 Layer 1 checks from §5. Wire confidence thresholds to human gate triggers.

5. **Implement trust evaluator.** 5-factor weighted algorithm. Create config files for recognized muhaqiqs and known publishers. Verify against GROUND_TRUTH.json expected_trust values.

6. **Implement registries.** Source, work, and scholar registry CRUD with atomic write-ahead log (pending file + backup copy pattern from §4.A.2 Step 7).

7. **Implement work relationship tracking.** When LLM infers a genre_chain, create WorkRelationshipEdge. Handle placeholder work records for referenced-but-not-acquired works.

## Done When

- [ ] Scholar authority: `lookup()` finds existing records with correct thresholds (≥0.85 auto-link, 0.50–0.85 gate, <0.50 new)
- [ ] Scholar authority: `register()` creates records with sequential IDs (sch_00001, sch_00002, ...)
- [ ] Scholar authority: `update()` runs 5 consistency checks and blocks conflicting changes
- [ ] Human gate: checkpoints persist to `library/gates/pending/`
- [ ] Human gate: auto-approve mode works for build/test
- [ ] Validation: all 6 Layer 1 checks implemented and tested
- [ ] Validation: genre↔multi-layer cross-check (Check 5e) auto-corrects and chains to Check 6
- [ ] Trust evaluation: 13/13 fixtures match GROUND_TRUTH.json expected_trust
- [ ] Trust evaluation: 5 factors computed with correct weights (0.30, 0.25, 0.15, 0.15, 0.15)
- [ ] Trust evaluation: threshold 0.65 for verified/flagged boundary
- [ ] Trust evaluation: classical scholar cutpoint at 1000 AH (not 900)
- [ ] Registries: atomic write with pending file + backup
- [ ] Registries: all three registries populated correctly for fixture 01
- [ ] Work relationships: genre chain creates WorkRelationshipEdge
- [ ] Config files created: muhaqiqs, publishers, transliteration, genre_synonyms
