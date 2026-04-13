# Integrity Audit — Source Engine Core SPEC

**Date:** 2026-03-09
**SPEC audited:** `engines/source/SPEC_CORE.md`
**Lenses applied:** All 8 from kr-integrity

---

## Defects Found: 11

**Defect 1** [Lens 1: Zero Ambiguity] §4.A.5 — Scholar Record Matching Score
Quote: "Scoring: ≥ 0.85 → auto-link; 0.50–0.85 → human gate; < 0.50 → new record."
Problem: The SPEC defines four matching signals (name, death date, school, works) and three thresholds, but never specifies HOW these signals combine into a 0.0–1.0 score. An implementer would have to invent a scoring algorithm. Is it the average? Weighted sum? Maximum? Does a death date match override a name mismatch?
Fix: Add a concrete scoring formula. Proposed:
```
def compute_scholar_match_score(candidate, existing) -> float:
    scores = []
    # Name match: compare normalized candidate name against all name_variants + known_as
    name_score = max(normalized_similarity(candidate.name, v) for v in existing.all_names)
    scores.append(("name", name_score, 0.50))
    
    # Death date match (if both have dates)
    if candidate.death_date and existing.death_date_hijri:
        diff = abs(candidate.death_date - existing.death_date_hijri)
        date_score = 1.0 if diff == 0 else max(0.0, 1.0 - diff / 50.0)
        scores.append(("death_date", date_score, 0.30))
    
    # School match (if both have schools)
    if candidate.school and existing.school_affiliations:
        school_score = 1.0 if candidate.school in existing.school_affiliations.values() else 0.0
        scores.append(("school", school_score, 0.10))
    
    # Works match (if candidate has known work)
    if candidate.known_work_title:
        works_score = 1.0 if any(fuzzy_match(candidate.known_work_title, w) for w in existing.known_works) else 0.0
        scores.append(("works", works_score, 0.10))
    
    # Weighted average of available signals
    total_weight = sum(w for _, _, w in scores)
    return sum(s * w for _, s, w in scores) / total_weight if total_weight > 0 else 0.0
```
Severity: **HIGH** — would cause implementation divergence; two developers would build different matching algorithms.

**Defect 2** [Lens 1: Zero Ambiguity] §4.A.1 — Slug Generation
Quote: "Slugs are derived by transliterating the canonical Arabic author name and title using a configurable mapping table (initial table in §8)"
Problem: §8 says the table is in `library/config/transliteration.json` but provides no initial content, structure definition, or fallback behavior when a name/title isn't in the table. Claude Code cannot build this without knowing the JSON schema and initial entries.
Fix: Define the structure and provide initial entries inline:
```json
// library/config/transliteration.json
{
  "scholars": {
    "ابن عقيل": "ibn_aqil",
    "ابن مالك": "ibn_malik",
    "ابن قدامة": "ibn_qudamah",
    "سيبويه": "sibawayhi",
    "الجويني": "juwayni"
  },
  "titles": {
    "ألفية": "alfiyyah",
    "المغني": "mughni",
    "الورقات": "waraqat",
    "الكتاب": "kitab"
  }
}
```
Fallback: if no table match, apply a rule-based transliteration (strip diacritics → map Arabic chars to Latin using the Buckwalter or similar scheme) → truncate to max slug length. If the result is empty or non-ASCII, use first 8 hex chars of MD5 hash.
Severity: **HIGH** — implementer would have to guess both structure and content.

**Defect 3** [Lens 1: Zero Ambiguity] §4.A.8 — Trust Factor Score Ranges
Quote: "Major classical scholar (in registry with high scholarly_standing): 0.85–0.95. Known scholar: 0.60–0.80."
Problem: Score ranges are ambiguous. What determines 0.85 vs. 0.95? What is "high scholarly_standing"? What distinguishes "major classical" from "known"?
Fix: Define concrete rules instead of ranges:
- Major classical scholar (death_date_hijri ≤ 900 AH AND scholarly_standing is non-null AND sources_encountered_in has ≥1 entry): **0.90**.
- Other known scholar (record exists in registry): **0.70**.
- Unknown (no registry record; record was just created from this intake alone): **0.30**.

This collapses the ranges to specific values that are deterministic from the registry state. Fine-tuning in Step 2 testing.
Severity: **MEDIUM** — implementer could make reasonable choices, but two implementers would make different ones.

**Defect 4** [Lens 3: Silent Failure] §4.A.4 — LLM Returns Invalid Enum Value
Problem: The SPEC defines the LLM output schema with enum constraints (genre must be one of 18 values), but doesn't specify what happens when the LLM returns a value outside the enum (e.g., `"genre": "manzumah"` instead of `"nazm"`). Pydantic validation would catch this AFTER the value is written to the metadata dict, but the LLM response parsing itself could silently accept it if validation is deferred.
Fix: Add explicit validation after LLM response parsing:
"After parsing the LLM JSON response, validate each field against its enum: `genre` against `Genre`, `structural_format` against `StructuralFormat`, `authority_level` against `AuthorityLevel`, `level` against `WorkLevel`. If any field has a value not in the enum, log a WARNING, map the value to the closest valid enum value if possible (configurable synonym table: `manzumah` → `nazm`, `شرح` → `sharh`), or set the field to `other` / `unknown` with confidence 0.50 and add to `needs_review_fields`."
Severity: **MEDIUM** — would cause a runtime error at Pydantic validation, but not a silent corruption.

**Defect 5** [Lens 5: Contract Consistency] §4.A.4 — text_fidelity in LLM Output Schema
Quote (LLM output schema): `"text_fidelity": "high"` ... (later): "The text_fidelity field is NOT inferred by the LLM — it is determined deterministically by source format."
Problem: The LLM output schema includes `text_fidelity`, then the SPEC says the LLM doesn't determine it. An implementer would be confused: should the LLM prompt ask for it or not? Should the LLM response be ignored for this field?
Fix: Remove `text_fidelity` and `text_fidelity_reason` from the LLM output schema JSON. Add a note: "text_fidelity is set by the engine after LLM inference, based on source_format. It is not part of the LLM prompt or response."
Severity: **MEDIUM** — contradictory instructions would cause implementation confusion.

**Defect 6** [Lens 6: Assumption] §4.A.4 — LLM Structured JSON Output Reliability
Quote: "[ASSUMPTION — NEEDS STEP 2 TESTING] The LLM can produce this structured JSON reliably"
Problem: This assumption is marked but insufficiently scoped. The key risk is not whether the LLM CAN produce JSON (function calling handles this), but whether the inferred VALUES are correct. Specifically:
- Can the LLM correctly identify `genre_chain` relationships from title alone?
- Can the LLM distinguish `commentary` vs `prose` structural format?
- Can the LLM detect multi-layer composition from 2000 characters of text?
Fix: Split into three separate assumptions with specific test criteria:
- [ASSUMPTION A1] LLM genre inference accuracy ≥ 85% on test fixtures with known genres.
- [ASSUMPTION A2] LLM genre_chain inference accuracy ≥ 80% on fixtures that are sharh/hashiyah/mukhtasar.
- [ASSUMPTION A3] LLM multi-layer detection accuracy ≥ 90% when CSS classes are present (combining CSS signal with LLM signal).
Severity: **MEDIUM** — if any fails, the SPEC needs a different approach for that specific task.

**Defect 7** [Lens 2: Corruption Path] §4.A.5 — data_provenance_score Always 0.0 in Stage 1
Problem: The SPEC says `data_provenance_score` will be 0.0 for all scholars in Stage 1 (no external enrichment). The synthesizer uses this score: < 0.30 → hedged statements. This means ALL biographical claims will be hedged in Stage 1, even for well-known scholars like Sibawayhi where the LLM inference is almost certainly correct. This degrades synthesis quality without proportionate benefit.
Fix: Two options:
(a) Set `data_provenance_score` to 0.0 as stated, but adjust the synthesizer's threshold for Stage 1: when no external sources are available (detectable from `record_sources`), the synthesizer uses LLM inference confidence instead of `data_provenance_score` for hedging decisions.
(b) Define `data_provenance_score` differently for Stage 1: count fields where the LLM had high confidence (≥ 0.85) as "provisionally corroborated" and compute a provisional score. External corroboration in Stage 2 upgrades this.
Recommendation: Option (a) — it keeps the source engine simple and puts the responsibility where it belongs (synthesis). Note this as an interface contract with the synthesis engine.
Severity: **MEDIUM** — not a corruption path but a quality degradation.

**Defect 8** [Lens 7: Implementer's Reading] §6 — Consensus Result When Both Models Agree on "New Record"
Problem: The SPEC says "both must select the same canonical_id." But when both models agree a new scholar record should be created, there IS no canonical_id yet — the ID is assigned later. What does "agreement" mean in this case? Both models would return the same author identification metadata (name, death date, etc.) but they can't return the same canonical_id.
Fix: Define agreement for the "new record" case explicitly: "If both models return no existing canonical_id match (both conclude the author is new to the registry), AND both models' author identification metadata agrees on: (a) the canonical Arabic name (after normalization), and (b) the death date (within ±10 years, or both null), then the models are considered in agreement. The engine creates a new scholar record using the merged metadata from both models (prefer the model with higher stated confidence for any disagreeing biographical fields)."
Severity: **HIGH** — implementer would not know how to handle the most common case (new scholar on first source intake).

**Defect 9** [Lens 4: Error Path Completeness] §4.A.3 — Empty Shamela info.html Table
Problem: The Shamela extractor parses `<tr>` rows from the info.html table. What if `info.html` exists and has valid HTML but the table has zero matching field rows (e.g., a corrupted or empty metadata card)? The extractor would return a dict with only `title_arabic` (from `<h1>`) and nothing else. The LLM inference step would then need to fill author, publisher, category — all from the title and 2000 chars of content. But is the flow correct? Does the SPEC handle this as a partial extraction or an error?
Fix: After Shamela extraction, check whether `author_name_raw` was extracted. If not, flag `SRC_FORMAT_STRUCTURE_MISSING` (same as missing info.html) and set all extracted fields to `needs_review`. This ensures the owner knows the metadata was entirely inferred. Add this check explicitly: "If the Shamela extractor produces a result with no `author_name_raw`, treat it as equivalent to missing info.html: log `SRC_FORMAT_STRUCTURE_MISSING`, flag all fields as `needs_review`."
Severity: **MEDIUM** — partial extraction would work but the owner wouldn't know the metadata is entirely LLM-inferred.

**Defect 10** [Lens 8: Extension-Blocking] §4.A.1 — work_id Max Length
Quote: "max 40 characters total"
Problem: 40 characters may be too short for some work-author combinations when Stage 2 adds more sources. Arabic scholar names can be very long (e.g., أبو الوليد سليمان بن خلف بن سعد بن أيوب الباجي = 14+ transliterated words). With a 40-char limit, many work_ids would be hash-truncated rather than human-readable, defeating the purpose.
Fix: Increase to 60 characters. Or, make the truncation strategy explicit: "If the combined slug exceeds 40 characters, truncate the title slug first (preserving the first distinctive word), then truncate the author slug. If still over 40 characters, use the first 30 characters of the combined slug plus an 8-character hash suffix." This is an implementation detail but the limit impacts the data model.
Severity: **LOW** — 40 chars works for most cases; edge cases produce hash-based IDs which are functional but opaque.

**Defect 11** [Lens 7: Implementer's Reading] §4.A.4 — Inference Prompt Content Not Specified
Problem: The SPEC defines the LLM output schema and the input requirements (extracted metadata, first 2000 chars, TOC, library context) but does not specify the actual prompt structure. Claude Code would need to craft the prompt from scratch. While the output schema constrains the response, the quality of inference depends heavily on prompt engineering — a poorly worded prompt would produce low-quality results even with the correct schema.
Fix: Add a prompt template specification:
"The inference prompt MUST include: (1) A system message establishing the LLM as an Islamic bibliographic specialist, (2) The extracted metadata fields (formatted as key-value pairs), (3) The first 2000 characters of source text (or note that no text is available), (4) For Shamela sources: whether CSS layer classes were detected, (5) The expected JSON output schema with field descriptions, (6) Instructions to return ONLY the JSON object with no preamble, (7) Instructions to set confidence to 0.50 for any field the LLM is uncertain about.
The exact prompt text is an implementation detail refined during Step 2 testing, but the above elements are required."
Severity: **MEDIUM** — Claude Code could build a reasonable prompt, but the SPEC should constrain the minimum elements.

---

## Assumptions Needing Step 2 Testing: 7

| ID | Assumption | What to Test | What Changes If It Fails |
|----|-----------|-------------|--------------------------|
| A1 | LLM genre inference ≥ 85% accuracy | Run on 5+ fixtures with known genres (Ibn Aqil=sharh, Alfiyyah=matn, Waraqat=matn, Mughni=fiqh_comparative) | If < 70%: add title-keyword rules as pre-filter before LLM. If 70-84%: add human gate for low-confidence genre. |
| A2 | LLM genre_chain inference ≥ 80% on sharh/hashiyah titles | Test with 5+ commentary titles | If < 70%: use title-keyword extraction rules instead of LLM for genre_chain |
| A3 | LLM multi-layer detection ≥ 90% when CSS classes present | Test on html_export_minimal (multi-layer) and alfiyyah (single-layer) | If < 85%: use CSS classes as authoritative signal, LLM as fallback only |
| A4 | Two-model consensus catches attribution errors | Run same prompt through Claude + GPT on 10+ fixtures, measure agreement rate | If agreement < 80%: increase to 3 models. If models frequently agree on wrong answer: add rule-based pre-filter |
| A5 | Scholar matching score formula produces sensible thresholds | Run on fixture scholars (Ibn Aqil, Ibn Malik, Ibn Qudamah) with variant spellings | If formula produces false positives (different scholars matched): tighten weights. If false negatives (same scholar not matched): loosen weights |
| A6 | Trust evaluation weights and threshold produce correct tiers | Run on 5+ sources covering verified and flagged cases | If boundary cases are wrong: adjust weights. This is empirical tuning |
| A7 | Name normalization (diacritic strip + hamza/taa normalize) is sufficient for matching | Test with variant spellings from real Shamela exports | If insufficient: add Levenshtein distance or CAMeL Tools morphological normalization |

---

## Summary

- **HIGH defects: 3** — Defects 1, 2, 8. Would cause wrong implementation or implementation divergence.
- **MEDIUM defects: 7** — Defects 3-7, 9, 11. Missing detail or untested assumptions that could degrade quality.
- **LOW defects: 1** — Defect 10. Minor extensibility concern.
- **Assumptions for Step 2: 7**

### Recommendation

All HIGH defects have been fixed in SPEC_CORE.md:
1. Scholar matching score formula (Defect 1) — added concrete `compute_scholar_match_score` pseudocode
2. Slug generation rules (Defect 2) — added `generate_slug` pseudocode, initial transliteration table, and fallback behavior
3. Consensus "new record" agreement definition (Defect 8) — defined three agreement cases explicitly

Additionally fixed MEDIUM defects:
- Defect 3: Trust factor scores collapsed from ranges to deterministic values
- Defect 4: Added LLM response enum validation with synonym table
- Defect 5: Removed text_fidelity from LLM output schema
- Defect 9: Added empty Shamela table handling
- Defect 11: Added required prompt elements specification

Remaining MEDIUM defects for Step 2:
- Defect 6: LLM inference assumption needs splitting into A1/A2/A3 (documented in assumptions table)
- Defect 7: data_provenance_score Stage 1 behavior (synthesis engine interface decision)
- Defect 10: work_id max length (changed to 50 chars in fix)

### Post-Audit Critical Discovery (2026-03-09)

After the integrity audit, a structural survey of 2,519 real Shamela exports revealed that the SPEC's extraction rules were built on entirely wrong assumptions. The synthetic `html_export_minimal` fixture does not match real Shamela exports in ANY structural detail:

- No `info.html` exists (metadata is in first PageText div)
- No `<table>` metadata format (uses `<span class='title'>label:</span> value`)
- No `class="matn"` / `class="sharh"` / `class="hashiyah"` CSS classes exist anywhere
- Page markers use `<span class='PageNumber'>(ص: ١٥)</span>`, not `<span class="pg">15</span>`

All extraction rules in §4.A.3 were rewritten. Multi-layer detection (§4.A.4) was updated to remove CSS-class reliance. The assumption A3 (multi-layer detection ≥ 90%) is now a higher-risk assumption since it relies on LLM inference alone with no structural signal.

Full findings documented in `reference/SHAMELA_FORMAT_ANALYSIS.md`. 12 real fixtures added to `tests/fixtures/shamela_real/`.
