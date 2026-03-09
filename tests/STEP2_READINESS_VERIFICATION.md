# Step 2 Readiness Verification — Handoff Summary for Claude Code

**Date:** 2026-03-09
**Verified by:** Claude Chat (computational bibliographer session)
**Scope:** Pre-flight checks for LLM assumption testing (Step 2 Phases 1–3)

---

## Task 1: Prompt Schema vs Contracts.py — Field-by-Field Sync

### Method
Compared every field in `engines/source/prompts/inference_v1.py` output schema against the Pydantic models in `engines/source/contracts.py`, and verified the eval harness `tests/eval_harness.py` field name mapping.

### Field-by-Field Comparison Table

| # | Prompt Output Field | contracts.py Target | Type Match | Enum Match | Notes |
|---|---|---|---|---|---|
| 1 | genre | SourceMetadata.genre (Genre) | ✓ str→enum | ✓ 18/18 | |
| 2 | genre_confidence | InferredFieldConfidence.genre | ✓ float | N/A | |
| 3 | genre_chain | GenreChain model | ✓ obj\|null | | 3 sub-fields below |
| 3a | genre_chain.relation_type | GenreRelationType enum | ✓ str→enum | ✓ 7/7 | |
| 3b | genre_chain.base_work_title | GenreChain.base_work_title | ✓ str | N/A | |
| 3c | genre_chain.base_work_author | GenreChain.base_work_author | ✓ str | N/A | |
| 4 | genre_chain_confidence | InferredFieldConfidence.genre_chain | ✓ float\|null | N/A | Also maps to GenreChain.confidence at implementation time |
| 5 | structural_format | SourceMetadata.structural_format | ✓ str→enum | ✓ 7/7 | |
| 6 | structural_format_confidence | InferredFieldConfidence.structural_format | ✓ float | N/A | |
| 7 | is_multi_layer | SourceMetadata.is_multi_layer | ✓ bool | N/A | |
| 8 | multi_layer_confidence | InferredFieldConfidence.multi_layer | ✓ float | N/A | |
| 9 | layers | SourceMetadata.text_layers | ⚠️ NAME | | See Issue 1 below |
| 9a | layers[].layer_type | TextLayer.layer_type | ✓ str→Literal | ✓ 4/4 | |
| 9b | layers[].author_name | TextLayer.author (ScholarReference) | ⚠️ TYPE | N/A | See Issue 2 below |
| 10 | science_scope | SourceMetadata.science_scope | ✓ list[str] | N/A | Open vocabulary, not enum |
| 11 | science_scope_confidence | InferredFieldConfidence.science_scope | ✓ float | N/A | |
| 12 | level | SourceMetadata.level (WorkLevel) | ✓ str\|null→enum | ✓ 4/4 | |
| 13 | level_confidence | InferredFieldConfidence.level | ✓ float\|null | N/A | |
| 14 | authority_level | SourceMetadata.authority_level | ✓ str→enum | ✓ 3/3 | |
| 15 | authority_level_confidence | InferredFieldConfidence.authority_level | ✓ float | N/A | |
| 16 | author_identification | ScholarReference + ScholarAuthorityRecord | ✓ obj | | 7 sub-fields below |
| 16a | .canonical_name_ar | ScholarReference.name_arabic + SAR.canonical_name_ar | ✓ str | N/A | |
| 16b | .known_as | SAR.known_as | ✓ list[str] | N/A | |
| 16c | .death_date_hijri | SAR.death_date_hijri | ✓ int\|null | N/A | |
| 16d | .school_affiliations | SAR.school_affiliations | ✓ dict | N/A | |
| 16e | .sectarian_tradition | SAR.sectarian_tradition | ✓ str | N/A | Free string, not enum |
| 16f | .scholarly_standing | SAR.scholarly_standing | ✓ str | N/A | |
| 16g | .methodological_stance | SAR.methodological_stance | ✓ str\|null | N/A | |
| 17 | author_identification_confidence | ScholarReference.confidence | ✓ float | N/A | |
| 18 | attribution_status | SourceMetadata.attribution_status | ✓ str→enum | ✓ 4/4 | |
| 19 | attribution_notes | SourceMetadata.attribution_notes | ✓ str\|null | N/A | |
| 20 | scholarly_context | ScholarlyContext model | ✓ obj | | 10 sub-fields below |
| 20a | .composition_period | ScholarlyContext.composition_period | ✓ str\|null | N/A | |
| 20b | .composition_date_hijri | ScholarlyContext.composition_date_hijri | ✓ int\|null | N/A | |
| 20c | .tradition_position | ScholarlyContext.tradition_position | ✓ str\|null | N/A | |
| 20d | .known_textual_issues | ScholarlyContext.known_textual_issues | ✓ list[str] | N/A | |
| 20e | .historical_significance | ScholarlyContext.historical_significance | ✓ str\|null | N/A | |
| 20f | .muhaqiq_reputation | ScholarlyContext.muhaqiq_reputation | ✓ str\|null | N/A | |
| 20g | .tahqiq_methodology_note | ScholarlyContext.tahqiq_methodology_note | ✓ str\|null | N/A | |
| 20h | .edition_known_issues | ScholarlyContext.edition_known_issues | ✓ list[str] | N/A | |
| 20i | .context_richness | ScholarlyContext.context_richness | ✓ str→Literal | ✓ 3/3 | |
| 20j | .uncertain_dimensions | ScholarlyContext.uncertain_dimensions | ✓ list[str] | N/A | |

### Issues Found

**Issue 1 (naming): `layers` vs `text_layers`**
- Prompt asks LLM to produce field named `layers`
- contracts.py has `SourceMetadata.text_layers: list[TextLayer]`
- **Impact on testing:** None. The eval harness does not score layer content, only `is_multi_layer` (boolean).
- **Impact on implementation:** The post-processing code that maps LLM output → SourceMetadata must rename `layers` → `text_layers`. This is a known mapping step, not a bug.

**Issue 2 (type): `layers[].author_name` (string) vs `TextLayer.author` (ScholarReference)**
- The LLM cannot produce a ScholarReference (requires canonical_id from registry lookup).
- The prompt correctly asks for just `author_name` (string). Implementation creates the ScholarReference via scholar matching during post-processing.
- **Impact on testing:** None. Not scored in eval harness.
- **Impact on implementation:** Documented in SPEC §4.A.4 as a post-processing step.

### Phantom / Missing Fields
- **Phantom fields (prompt has, contracts.py doesn't):** None
- **Missing from prompt (contracts.py has, prompt doesn't):** `GenreChain.base_work_id` (correct to omit — registry lookup), `GenreChain.confidence` (maps from top-level `genre_chain_confidence`)
- **All enum values match exactly** across all 7 enum-constrained fields

### Eval Harness Field Name Mapping — Verified
The `_parse_llm_json` function extracts:
- `author_name` from `parsed['author_identification']['canonical_name_ar']`
- `author_death_hijri` from `parsed['author_identification']['death_date_hijri']`

The `score_fixture` function correctly uses:
- `predicted.get('author_name')` against `expected['author_identified']`
- `predicted.get('author_death_hijri')` against `expected.get('author_death_hijri')`

All 7 scored fields have correct name mapping across the prompt → eval harness → ground truth chain.

**Verdict:** ✅ Prompt schema is synced with contracts.py. No blocking issues.

---

## Task 2: Model Name Verification

### NEXT.md Model IDs — All Correct

| Model | NEXT.md ID | Verified Source | Status |
|---|---|---|---|
| Claude Opus 4.6 | `claude-opus-4-6` | [Anthropic docs](https://platform.claude.com/docs/en/about-claude/models/overview) | ✅ |
| GPT-5.4 | `openai/gpt-5.4` | [OpenRouter listing](https://openrouter.ai/openai/gpt-5.4) | ✅ |
| Gemini 3.1 Pro | `google/gemini-3.1-pro-preview` | [OpenRouter listing](https://openrouter.ai/google/gemini-3.1-pro-preview) | ✅ |
| Mistral Large 3 | `mistralai/mistral-large-2512` | [OpenRouter listing](https://openrouter.ai/mistralai/mistral-large-2512) | ✅ |
| Cohere Command A | `cohere/command-a` | [OpenRouter listing](https://openrouter.ai/cohere/command-a) | ✅ |

All models support JSON output / structured responses. All are current and not deprecated.

### Test Runner Model IDs — Two Fixed

| Config Key | Was (WRONG) | Now (CORRECT) | Problem |
|---|---|---|---|
| PHASE1_MODELS['sonnet-4.6'] | `claude-sonnet-4-6-20250514` | `claude-sonnet-4-6` | Fabricated snapshot date (May 2025 for a Feb 2026 model). Would cause 400 API error. |
| PHASE2_MODELS['opus-4.6'] | `claude-opus-4-6-20250528` | `claude-opus-4-6` | Same issue. No such snapshot exists in Anthropic's catalog. |

**File modified:** `tests/test_llm_inference.py` (2 lines changed)

---

## Task 3: Fixture Coverage for Newer Fields

### Fields Added During Step 1 and Their Test Status

| Field | In GROUND_TRUTH.json? | Scored for Accuracy? | Enum Compliance Check? | Action Taken |
|---|---|---|---|---|
| `attribution_status` | ✅ Added (all 13) | No (see rationale below) | ✅ Added to test runner | Ground truth populated, enum check added |
| `attribution_notes` | Not needed | No | N/A (free text) | Tested via JSON parse only |
| `scholarly_context` (10 sub-fields) | Not needed | No | ✅ `context_richness` enum check added | Narrative fields — JSON parse + enum compliance sufficient |
| `sectarian_tradition` | Not needed | No | N/A (free string) | Nearly all fixtures are "sunni" — insufficient discrimination |
| `methodological_stance` | Not needed | No | N/A (free text) | JSON parse test only |
| `genre_chain.relation_type` | Not needed | No (scored only in Phase 2 per SCORING_CRITERIA.md) | ✅ Added to test runner | Enum check added |

### attribution_status Ground Truth Values

All 13 fixtures have uncontested, well-documented authors:

| Fixture | attribution_status | Confidence in Value |
|---|---|---|
| 01_nahw_simple (al-Zajjaji) | definitive | >95% |
| 02_nahw_muhaqiq (Ibn al-Qatta') | definitive | >95% |
| 03_fiqh (al-Zahim) | definitive | >90% |
| 04_hadith (al-Qadi Isma'il) | definitive | >90% |
| 05_tafsir (al-Khamis) | definitive | >90% |
| 06_usul (al-Nawawi) | definitive | >95% |
| 07_balagha (Ahmad Matloub) | definitive | >90% |
| 08_death_date (al-Sulami) | definitive | >90% |
| 09_alt_title (al-Ruhayili) | definitive | >90% |
| 10_no_author (al-Sayf) | definitive | 85% |
| 11_multi_small (al-Suyuti) | definitive | >95% |
| 12_multi_muq (Malik Bennabi) | definitive | >95% |
| alfiyyah_versified (Ibn Malik) | definitive | >95% |

### Why NOT Add attribution_status to Weighted Scoring

All 13 fixtures are "definitive." This means the field has zero discrimination power in the current fixture set — a model that defaults to "definitive" for everything scores 100%. Adding it to weighted scoring would inflate aggregate scores without providing useful signal.

**Recommendation for future:** Add at least one fixture with genuinely disputed attribution (e.g., a work attributed to a famous scholar but actually by a student — these exist in the tradition) and one with "traditional" attribution. Once the fixture set has at least 2 non-definitive entries, add attribution_status to weighted scoring at weight 0.05 (taken equally from genre and author_identification).

---

## Changes Made

| File | Change | Why |
|---|---|---|
| `tests/test_llm_inference.py` line 161 | `claude-sonnet-4-6-20250514` → `claude-sonnet-4-6` | Invalid snapshot ID would cause API 400 error |
| `tests/test_llm_inference.py` line 169 | `claude-opus-4-6-20250528` → `claude-opus-4-6` | Invalid snapshot ID would cause API 400 error |
| `tests/test_llm_inference.py` lines 130-153 | Added enum compliance checks for `attribution_status`, `context_richness`, `genre_chain.relation_type` | New fields from Step 1 were not being validated |
| `tests/fixtures/GROUND_TRUTH.json` | Added `attribution_status: "definitive"` to all 13 fixtures | Expected values for enum compliance testing |

## Issues Found But Not Fixed (Need Owner Input)

1. **No disputed-attribution fixture exists.** All 13 fixtures have "definitive" attribution. This means the system's handling of disputed/traditional/unknown attribution cannot be tested. Consider adding a fixture from the owner's collection where authorship is genuinely uncertain. Examples from the Islamic scholarly tradition: works attributed to al-Ghazali that may be by students, or Sufi texts with contested attribution chains.

2. **attribution_status not yet in weighted scoring.** Once a disputed-attribution fixture exists, this should be added. Current decision: defer.

3. **layers → text_layers naming gap.** Not a testing bug, but implementation code must map this. Documented here so Claude Code doesn't miss it.

---

## Verdict

### ✅ YES — The test infrastructure is ready for Claude Code to run Step 2 Phases 1–3.

All blocking issues have been fixed:
- Prompt schema matches contracts.py (no phantom fields, no enum mismatches)
- All model IDs verified against live APIs (2 Anthropic IDs were wrong, now fixed)
- Eval harness field name mapping is correct across the full chain
- Enum compliance checks cover all enum-constrained fields including new Step 1 additions
- Ground truth has expected values for all scored fields
- Dry-run mode verified working with corrected model IDs
- Eval harness self-tests passing

Claude Code can proceed with Phase 1 (Sonnet prompt iteration) immediately.
