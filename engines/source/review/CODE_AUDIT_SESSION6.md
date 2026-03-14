# Code Audit — Source Engine Step 1

**Date:** 2026-03-10
**Auditor:** Claude Chat (architect session)
**Method:** Full code read of every file in the trace path for each checklist item, with line-level citations. SPEC_CORE.md is the specification authority.
**Scope:** 10 checklist items from NEXT.md + 1 additional pass on engine.py.

---

## Checklist Item 1: Consensus Retry Flow

### SPEC Reference

SPEC §6 (lines 1518–1521): "Author identification (highest cascade risk): if one model times out or fails, a single-model result is NOT accepted. Human gate checkpoint with the single model's suggestion." §8 (line 1604): `consensus_model_fallback` is `{"openai": "openai/gpt-5.4"}` — "Fallback non-Anthropic model if primary fails after retries. Via OpenRouter."

### Code Trace

1. **engine.py:297** — `inference = await infer_metadata(extracted, ...)` is the only call site.
2. **metadata_inference.py:384–395** — `simplified_messages` is built by stripping library context markers from the prompt. Both `messages` and `simplified_messages` are passed to `evaluate()`.
3. **metadata_inference.py:413–419** — `evaluate(task="author_identification", messages=messages, ..., simplified_messages=simplified_messages)` — correct task name and all args forwarded.
4. **consensus.py:204–217** — Both primary models dispatched concurrently via `asyncio.gather()`. Each `_call_model` receives `simplified_messages`.
5. **consensus.py:126–128** — `_call_model` uses `simplified_messages` on retry attempt (attempt 1 uses original, attempt 2 uses simplified if provided). `MAX_RETRIES_PER_MODEL = 2` (line 46).
6. **consensus.py:252–319** — One-model-failed path:
   - Line 258: `if task == "author_identification" and "cohere" in failed_model.model_id:` → triggers fallback swap to `FALLBACK_MODEL` (GPT-5.4 via OpenRouter, line 41–43).
   - Line 264–270: Fallback model is called. If it succeeds, the failed response is replaced and flow falls through to "both succeeded" comparison (line 321).
   - Line 280–291: If fallback also fails → human gate.
   - Line 293–307: If Opus failed instead of Cohere, no fallback attempted → human gate (correct per SPEC: "single-model result is NOT accepted").

### Verdict: NO ISSUE

The flow is correct for the current configuration. `simplified_messages` propagates correctly. Fallback GPT-5.4 fires when Cohere fails. When Opus fails, no non-Anthropic fallback is possible (the only configured fallback IS non-Anthropic), so it correctly goes to human gate.

**Note for future:** The fallback condition is hardcoded to check `"cohere" in failed_model.model_id` (consensus.py:258). If the consensus pair is reconfigured to a different non-Anthropic provider, this check would fail silently — no fallback would trigger. This is not a bug against the current SPEC but should be generalized when the consensus pair is changed. The correct condition would be `failed_model.provider != "anthropic"` (i.e., fallback fires when any non-Anthropic primary fails).

---

## Checklist Item 2: Registration Atomicity — Double Corruption

### SPEC Reference

SPEC §4.A.2 Step 7 (lines 442–448): "A registry file with JSON parse failure is restored from its .bak copy." CONSTRAINTS: "Errors must fail loudly with defined error codes. Never silently drop data or default on uncertainty."

### Code Trace

1. **registries/__init__.py:270–287** — `_rollback_registries()`:
   ```python
   def _rollback_registries(library_root: Path) -> None:
       for bak_file in registries_dir.glob("*.json.bak"):
           registry_path = bak_file.with_suffix("").with_suffix(".json")
           try:
               raw = registry_path.read_text(encoding="utf-8")
               json.loads(raw)
           except (json.JSONDecodeError, OSError):
               try:
                   os.replace(str(bak_file), str(registry_path))
               except OSError:
                   pass  # ← SILENT on double corruption (line 286)
   ```
2. The function checks whether the main file is corrupt, then replaces from `.bak`. But if the `.bak` file is ALSO corrupt JSON, `os.replace` succeeds (it's a valid filesystem operation), and the main registry file is now corrupt `.bak` content. No validation of `.bak` integrity is performed.
3. Even if `.bak` replacement fails (OSError), the `pass` on line 286 swallows the error entirely. The caller (`check_orphaned_registrations` line 228–229) deletes the pending file and moves on — the corrupt registry is never surfaced.
4. **registries/__init__.py:253–264** — Partial rollback in `check_orphaned_registrations`:
   ```python
   for filename in completed:
       registry_path = registries_dir / filename
       bak_path = registry_path.with_suffix(".json.bak")
       if bak_path.exists():
           try:
               os.replace(str(bak_path), str(registry_path))
           except OSError:
               pass  # ← Also silent (line 263)
   ```

### Verdict: BUG — CONFIRMED (Step 0 finding A2)

**Two distinct failures, both silent:**

(a) `.bak` file is itself corrupt JSON — `os.replace` succeeds, but the registry is now unreadable. Next startup treats it as empty, causing duplicate scholars and works.

(b) `os.replace` fails (disk full, permissions) — `pass` swallows. Corrupt registry persists.

**Fix:** In `_rollback_registries`, after replacing from `.bak`, validate the restored file parses as JSON. If it doesn't, raise `SourceEngineError` with `ErrorCode.REGISTRY_CONFLICT` and message "Registry {path} is corrupt and .bak copy is also corrupt — manual recovery required." Same for the `OSError` catch: raise instead of pass.

In `check_orphaned_registrations`, the partial rollback `OSError: pass` should likewise raise, or at minimum log a FATAL error and return the source_id in a separate `unrecoverable` list so the engine can halt.

**Precise fix specification:**

File: `engines/source/src/registries/__init__.py`

Function `_rollback_registries` — replace lines 283–286:
```python
            try:
                os.replace(str(bak_file), str(registry_path))
            except OSError:
                pass
```
with:
```python
            try:
                os.replace(str(bak_file), str(registry_path))
            except OSError as exc:
                raise RuntimeError(
                    f"FATAL: Cannot restore registry {registry_path} from backup: {exc}. "
                    f"Manual recovery required."
                ) from exc
            # Validate restored content
            try:
                restored_raw = registry_path.read_text(encoding="utf-8")
                json.loads(restored_raw)
            except (json.JSONDecodeError, OSError) as exc:
                raise RuntimeError(
                    f"FATAL: Registry {registry_path} restored from backup but backup "
                    f"is also corrupt. Manual recovery required."
                ) from exc
```

Function `check_orphaned_registrations` — replace line 263 (`pass`) with logging + error tracking.

---

## Checklist Item 3: Concurrent Scholar Updates

### SPEC Reference

SPEC §4.A.2 (lines 448–449): "Steps 4 and 7 acquire exclusive file locks on target registry files before reading. Step 4's scholar matching holds the lock on scholars.json through record creation."

### Code Trace

1. **scholar_registry.py:47–52** — `lookup_or_register_author` calls `lookup()` from shared module.
2. **scholar_authority.py:231–291** — `lookup()` reads registry WITHOUT a lock: `registry = _load_registry(registry_path)` (line 246). No `FileLock` acquired.
3. **scholar_authority.py:294–323** — `register()` acquires `FileLock` (line 307), reads, creates new ID, saves. Lock released at end of `with` block.
4. **Gap:** Between `lookup()` returning `action="new_record"` and `register()` acquiring the lock, another process could register the same scholar. `register()` re-reads the registry inside the lock (line 309), generates the next sequential ID (line 311), and writes — but never re-checks whether the same scholar name already exists. Two concurrent processes would both create records for the same scholar with different canonical_ids.
5. **engine.py:675** — `acquire_batch` processes sources sequentially: `for path in source_paths: ... await acquire_source(path, config)`. Within a single process, there is no concurrency gap.

### Verdict: CONFIRMED (Step 0 finding A3) — DEFERRED to Stage 2

The SPEC requires that the lock be held from lookup through register. The code violates this — `lookup()` is lockless while `register()` is locked. However, Stage 1 processes sources sequentially in a single process (engine.py:675), making the race condition unexploitable.

**Extension hook:** When parallelism is introduced (Stage 2 batch processing), the `lookup` + `register` sequence must be wrapped in a single lock acquisition. The simplest fix: add a `lookup_and_register` function in `scholar_authority.py` that holds the lock across both operations. Core must not assume sequential processing.

---

## Checklist Item 4: Human Gate Auto-Approve

### SPEC Reference

VALIDATION_PLAN.md (line 56): "Does auto_approve=True use the same code path as real owner review?"

### Code Trace

1. **human_gate.py:38–39** — Module defaults: `_AUTO_APPROVE = True`.
2. **human_gate.py:123–165** — `create_checkpoint()`:
   - Lines 139–149: Creates `HumanGateCheckpoint` with `status="pending"`.
   - Lines 152–154: Persists to `library/gates/pending/{source_id}.json`.
   - Lines 157–159: Updates `index.json`.
   - Lines 162–163: `if _AUTO_APPROVE: checkpoint = resolve(checkpoint_id, "approve", notes="auto_approved")`.
3. **human_gate.py:168–222** — `resolve()`:
   - Line 187–195: Finds checkpoint in pending list by ID.
   - Line 199–203: Determines status based on decision. For auto-approve: `if notes == "auto_approved": status = "auto_approved"`. For real approval: `status = "approved"`.
   - Line 207–209: Sets `status`, `resolution`, `resolved_at` on checkpoint data.
   - Line 211: Validates via `HumanGateCheckpoint.model_validate(cp_data)`.
   - Lines 214–220: Removes from pending, adds to resolved.
4. The auto-approve path executes the identical sequence: create → persist to pending → resolve → move to resolved. The only difference is the status string (`"auto_approved"` vs `"approved"`), which correctly distinguishes auto-approved from owner-approved in the audit trail.

### Verdict: NO ISSUE

Auto-approve uses the exact same `resolve()` code path as real owner review. Checkpoint creation, persistence, index update, and resolution all execute identically. The distinct status string preserves audit trail integrity.

---

## Checklist Item 5: Validation Check Ordering (5e → Check 6)

### SPEC Reference

SPEC §5 (lines 1445, 1455–1466): "Six checks run in order. Any failure aborts the write." Check 5e auto-corrects `is_multi_layer`. Check 6 reads `is_multi_layer`.

### Code Trace

1. **validation.py:36–77** — `validate_source_metadata()`:
   - Line 71: `errors.extend(_check_consistency(data, registries, prior_sources))` — runs Checks 5a–5e.
   - Line 75: `errors.extend(_check_multi_layer_coherence(data, registries))` — runs Checks 6a–6c.
   - Ordering: Check 5 runs BEFORE Check 6. Correct.
2. **validation.py:229–240** — Check 5e:
   ```python
   if genre in ("sharh", "hashiyah") and not is_multi_layer:
       data["is_multi_layer"] = True  # Auto-correct in-place
   ```
   Mutates `data` dict in place.
3. **validation.py:251** — Check 6a reads from the same `data` dict:
   ```python
   is_multi_layer = data.get("is_multi_layer", False)
   ```
   After 5e's mutation, this correctly reads `True`.
4. **engine.py:570–572** — Propagation back to metadata object:
   ```python
   if data_for_validation.get("is_multi_layer") != metadata.is_multi_layer:
       metadata.is_multi_layer = data_for_validation["is_multi_layer"]
   ```
   This was the bug fixed in commit 77b9b42 ("Validation auto-correction not propagated"). The fix correctly reads back auto-corrections from the validation dict.

### Verdict: NO ISSUE (fix verified)

Check 5e correctly propagates to Check 6 via in-place dict mutation. Engine correctly reads back auto-corrections. The Session 6 fix (commit 77b9b42) is complete and correct.

---

## Checklist Item 6: Trust Re-Evaluation Gating

### SPEC Reference

SPEC §4.A.8 (lines 1349–1352): "Trust re-evaluation on enrichment. When enrichment modifies any of the five trust input fields... If upgrade flagged → verified: human gate checkpoint."

### Code Trace

1. **trust_evaluator.py:46–97** — `evaluate_trust()` implements the 5-factor formula. Uses the VALIDATED first-intake formula (death_date only for author standing).
2. **trust_evaluator.py:100–116** — `_score_author_standing()`: Only checks `death_date_hijri`. Does NOT check `scholarly_standing` or `sources_encountered_in`. This is documented as intentional in the module docstring (lines 16–28): "The 'prior sources' check belongs in trust RE-EVALUATION, not in initial evaluation."
3. **enrichment.py** — 512 bytes, stub only. No re-evaluation logic exists.
4. **engine.py** — No re-evaluation code path. Trust evaluation runs once during intake (lines 489–510).

### Verdict: DEFERRED to Stage 2

The extension hook exists naturally: `evaluate_trust()` accepts `author_record` and `source_id` as parameters. A re-evaluation function would call `evaluate_trust()` with the enriched author record, then apply the additional conditions from SPEC §4.A.8:
- Check `scholarly_standing non-null` for the 0.90 tier
- Check `sources_encountered_in` contains at least one prior source_id
- If upgrade flagged → verified: create human gate
- If downgrade verified → flagged: apply immediately + stale-marking cascade

**What core must not assume:** The first-intake formula is NOT the permanent formula. The re-evaluation path must use the full SPEC conditions. The `evaluate_trust` function signature already accommodates this (it receives the full `author_record`), but a separate `reevaluate_trust` wrapper should enforce the additional checks. The enrichment module, when implemented, must wire through to this wrapper.

---

## Checklist Item 7: Validation Gate-Severity Errors Ignored

### SPEC Reference

SPEC §5 Layer 1 (line 1451): "If any critical inferred field has confidence < 0.50 → abort write → create human gate checkpoint." SPEC §5 Layer 1 Check 5c (line 1458): "Author-science mismatch... flag SRC_METADATA_INCONSISTENCY with human gate trigger AUTHOR_SCIENCE_MISMATCH." SPEC §5 Layer 1 Check 6a (line 1464): "If is_multi_layer is true, text_layers must be non-empty... abort write, create human gate checkpoint."

### Code Trace

1. **validation.py** produces three `severity="gate"` error types:
   - Check 3 (line 97–104): `severity="gate"`, `recovery="human_gate"` for confidence < 0.50.
   - Check 5c (line 194–204): `severity="gate"`, `recovery="human_gate"` for author-science mismatch.
   - Check 6a (line 256–266): `severity="gate"`, `recovery="human_gate"` for multi_layer=true + empty layers.

2. **engine.py:574–581** — Only handles fatal:
   ```python
   fatal_errors = [e for e in validation_errors if e.severity == "fatal"]
   if fatal_errors:
       raise make_error(...)
   ```
   Gate-severity errors are present in `validation_errors` but never processed.

3. **engine.py:532–533** — Separate low-confidence gate check:
   ```python
   if confidence_scores.genre < config.confidence_threshold_block:
       gate_low_confidence(source_id, "genre", genre.value, confidence_scores.genre)
   ```
   Only checks `genre`. Does NOT check `author.confidence` or `science_scope` confidence. These are supposed to be caught by validation Check 3, but validation gate errors are ignored.

4. **No code path** creates human gates from Check 5c (author-science mismatch) or Check 6a (empty layers) validation errors.

### Verdict: BUG — CONFIRMED (Step 0 finding A1)

Three SPEC-mandated human gate triggers are silently ignored because engine.py only filters for `severity="fatal"`.

**Not triggered in Step 0** because all confidence scores were > 0.50, no author-science mismatches existed in 13 fixtures (empty registries), and no multi_layer=true with empty layers occurred. **Will trigger at scale** when processing 2,519 books with a growing scholar registry.

**Fix:** After the fatal error check in engine.py (after line 581), add:

```python
# Process gate-severity errors → create human gate checkpoints
gate_errors = [e for e in validation_errors if e.severity == "gate"]
for gate_error in gate_errors:
    if gate_error.check == "confidence_threshold":
        gate_low_confidence(
            source_id, gate_error.field,
            _resolve_nested_field(data_for_validation, gate_error.field),
            _get_confidence_value(data_for_validation, gate_error.field),
        )
    elif gate_error.check == "consistency_author_science":
        from engines.source.src.human_gate import gate_author_disambiguation
        create_checkpoint(
            source_id=source_id,
            trigger=HumanGateTrigger.AUTHOR_SCIENCE_MISMATCH,
            trigger_detail=gate_error.message,
            fields_to_review=["science_scope", "author"],
            current_values={"error": gate_error.message},
        )
    elif gate_error.check == "multi_layer_empty_layers":
        gate_low_confidence(
            source_id, "text_layers", "[]", 0.0,
        )
```

Also remove the redundant standalone genre check at line 532–533 (it duplicates what validation Check 3 should handle). Or keep it as a belt-and-suspenders check, but the validation gate processing is the authoritative path.

---

## Checklist Item 8: Name Matching Punctuation Bug

### SPEC Reference

SPEC §4.A.1 (lines 271–289): `normalize_arabic_name()` specification. Steps listed: strip diacritics, normalize hamza, normalize taa marbuta, strip definite article, collapse whitespace. No explicit step for punctuation stripping.

### Code Trace

1. **name_matching.py:15–33** — `normalize_arabic_name()`:
   ```python
   def normalize_arabic_name(name: str) -> str:
       result = name
       result = re.sub(r'\([^)]*\)', '', result)  # Strip parentheticals
       # Strip diacritics
       diacritics = '...'
       for d in diacritics:
           result = result.replace(d, '')
       result = result.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
       result = result.replace('ة', 'ه')
       result = re.sub(r'\bال[ـ]?', '', result)
       result = re.sub(r'\s+', ' ', result).strip()
       return result
   ```
   No punctuation stripping. Arabic comma ، (U+060C) and other punctuation pass through.

2. **name_matching.py:36–44** — `_extract_name_tokens()`:
   ```python
   normalized = normalize_arabic_name(name)
   particles = {'بن', 'ابن'}
   return {t for t in normalized.split() if t not in particles}
   ```
   Splits on whitespace. Token "زجاجي،" (with trailing comma) differs from "زجاجي" (without).

3. **Concrete example:** LLM returns `"الزجاجي، أبو القاسم"`. After normalization: `"زجاجي، ابو قاسم"`. Tokenized: `{"زجاجي،", "ابو", "قاسم"}`. Compared against registry name `"الزجاجي"` → normalized `"زجاجي"` → tokens `{"زجاجي"}`. Intersection: empty (because "زجاجي،" ≠ "زجاجي"). Score: 0.0 → creates duplicate record.

### Verdict: BUG — CONFIRMED (Step 0 finding A4)

**Fix:** Add punctuation stripping to `normalize_arabic_name` in `shared/scholar_authority/src/name_matching.py`, after the definite article strip and before whitespace collapse:

```python
# Strip Arabic and common punctuation
result = re.sub(r'[،؛,;:.!؟?»«\-–—/]', ' ', result)
```

This must be placed BEFORE the whitespace collapse step (which already exists) so that punctuation is replaced with spaces and then collapsed. The punctuation list covers: Arabic comma (،), Arabic semicolon (؛), Latin comma, semicolon, colon, period, exclamation, Arabic question mark (؟), Latin question mark, guillemets (» «), hyphens and dashes, and forward slash.

---

## Checklist Item 9: `validate_enrichment_passthrough` Imported But Never Called

### SPEC Reference

SPEC §2.2 (lines 57–72): Enrichment write-back invariants. Invariant #3: "No field deletion." D-023 (lines 105–116): "No field is 'just for documentation' — each has a specific downstream consumer."

### Code Trace

1. **validation.py:30** — Import exists:
   ```python
   from shared.validation.src.validation import (
       ValidationError,
       validate_enrichment_passthrough,
       validate_referential_integrity,
       validate_schema,
   )
   ```
2. **validation.py:36–298** — `validate_source_metadata()` and all sub-functions: `validate_enrichment_passthrough` is never called anywhere.
3. **shared/validation/src/validation.py:112–143** — The function compares a `before` and `after` dict, checking that no non-null field was set to null. This requires TWO states — it is not applicable during initial intake (there is no "before" state).
4. **enrichment.py** — 512 bytes, stub. The enrichment write-back path does not exist yet.

### Verdict: DEFERRED — No action needed for Stage 1

The function is correctly unused during initial intake because there is no "before" metadata state to compare against. The import is forward-looking preparation for the enrichment module.

**When enrichment.py is implemented:** The enrichment write-back handler must call `validate_enrichment_passthrough(before_metadata, after_metadata)` before applying any enrichment. This enforces D-023 (no upstream field deletion).

**Extension hook:** The function's signature (`before: dict, after: dict`) is compatible with the enrichment flow. No core assumptions need changing.

---

## Checklist Item 10: Integration Script `level` Field and Author Comparison

### SPEC Reference

This item relates to the integration test script, not the engine itself.

### Code Trace

1. **Commit 3d18faf** — `scripts/phases/run_session6_integration.py`:
   - **Level field (line 148):** Added `result["level"] = metadata.level.value if metadata.level else None`. Previously, the level field was not captured in result JSON files.
   - **Author comparison (lines 96–98):** Changed from brittle substring matching:
     ```python
     # BEFORE (broken):
     results["author_match"] = (
         metadata.author.name_arabic in truth["author_identified"]
         or truth["author_identified"] in metadata.author.name_arabic
     )
     ```
     To proper name normalization:
     ```python
     # AFTER (fixed):
     gt_name = re.sub(r"\s*\(ت\s+\d+هـ\)\s*$", "", truth["author_identified"]).strip()
     results["author_match"] = normalized_name_similarity(gt_name, metadata.author.name_arabic) >= 0.80
     ```
2. The regex correctly strips death date suffixes like "(ت 337هـ)" from ground truth entries before comparison.
3. The 0.80 threshold is conservative — allows minor name variation while requiring substantial overlap.

### Verdict: ALREADY FIXED

Commit 3d18faf correctly addresses both issues. The level field is now captured in results. Author comparison uses the production `normalized_name_similarity` function with proper death-date stripping. No further action needed.

---

## Additional Findings (Full engine.py Pass)

### AF-1: Publication Year Fields Always Null — Field Mapping Bug

**Severity:** BUG (data loss)

**Code trace:**

engine.py:461–462:
```python
publication_year_hijri=extracted.get("publication_year_hijri"),
publication_year_miladi=extracted.get("publication_year_miladi"),
```

But the Shamela extractor (`extractors/shamela_html.py:420–442`) stores these values under different keys:
```python
result["edition_year_hijri"] = year_val  # line 420
result["edition_year_miladi"] = year_val  # line 422
```

The extractor produces `edition_year_hijri` / `edition_year_miladi`. The engine reads `publication_year_hijri` / `publication_year_miladi`. These keys don't match. The SPEC field mapping table (line 951–952) documents this translation: "Extractor Key: `edition_year_hijri` → SourceMetadata Field: `publication_year_hijri`" — but the engine code never performs this translation.

**Verified:** Test result `02_nahw_muhaqiq.json` has `publication_year_hijri: null` and `publication_year_miladi: null` despite the source having الطبعة field with year data.

**Fix:** In engine.py, change lines 461–462 to:
```python
publication_year_hijri=extracted.get("edition_year_hijri"),
publication_year_miladi=extracted.get("edition_year_miladi"),
```

### AF-2: Author Inference Confidence Not Stored or Checked for Needs Review

**Severity:** Minor gap (partially mitigated)

**Code trace:**

metadata_inference.py `apply_confidence_caps()` (line 264) returns a dict with an `"author"` key containing the capped author confidence. But `InferredFieldConfidence` (engine.py:141–152 via `_build_confidence_scores`) has no `author` field — the key is read from `scores.get("author")` but there is no matching Pydantic field, so it's silently dropped.

engine.py `_build_needs_review()` (lines 220–238) iterates over `InferredFieldConfidence` fields to build the needs_review list. Since there is no `author` field on the model, author inference confidence is never checked for needs_review.

**Mitigation:** The `ScholarReference.confidence` (set during `lookup_or_register_author`) serves as a proxy, and validation Check 3 checks `author.confidence` (the matching score). Additionally, the consensus directed comparison (§6.3) catches disputed/unknown attribution. However, the LLM's own confidence in author identification (which may be low even when matching succeeds) is lost.

**Not blocking for Step 2.** The primary safety mechanisms (consensus, validation, matching score) are intact. The lost signal is the LLM's self-reported identification confidence, which is less reliable than the consensus mechanism.

### AF-3: `_build_genre_chain` Silently Drops Invalid Relation Types

**Severity:** Minor (safe degradation)

**Code trace:**

engine.py:173–176:
```python
try:
    relation_type = GenreRelationType(gc.relation_type)
except ValueError:
    return None  # ← entire genre chain dropped, no log
```

If the LLM returns a relation_type not in the `GenreRelationType` enum, the entire genre chain is silently dropped. No logging, no needs_review flag.

**Mitigation:** This is rare (the LLM prompt constrains relation_type to valid values) and the degradation is safe (missing a genre chain is less harmful than accepting an invalid one). However, the fail-loud constraint suggests at minimum a warning log.

**Fix (non-blocking):** Add `logger.warning(f"Invalid genre relation_type '{gc.relation_type}', dropping genre chain")` before the `return None`.

---

## Summary

### Bugs Requiring Fix Before Step 2: 4

| # | Item | Severity | Fix Description |
|---|------|----------|-----------------|
| 1 | **Checklist 7: Validation gate-severity errors ignored** | High | engine.py must process `severity="gate"` validation errors and create human gate checkpoints |
| 2 | **Checklist 2: Registration rollback silent on double corruption** | Medium | `_rollback_registries` must validate .bak content and raise on unrecoverable corruption |
| 3 | **Checklist 8: Name matching punctuation bug** | Medium | `normalize_arabic_name` must strip Arabic/Latin punctuation before tokenization |
| 4 | **AF-1: Publication year field mapping bug** | Medium | engine.py must read `edition_year_hijri`/`miladi` (not `publication_year_*`) from extracted dict |

### Deferred to Stage 2: 3

| # | Item | Extension Hook |
|---|------|---------------|
| 1 | **Checklist 3: Concurrent scholar updates** | `lookup_and_register` function with single lock scope. Core must not assume sequential processing. |
| 2 | **Checklist 6: Trust re-evaluation gating** | `reevaluate_trust()` wrapper using full SPEC conditions (scholarly_standing + prior sources). Called from enrichment module. |
| 3 | **Checklist 9: `validate_enrichment_passthrough` not wired** | Call `validate_enrichment_passthrough(before, after)` in enrichment write-back handler when enrichment.py is implemented. |

### No Issue: 4

| # | Item | Evidence |
|---|------|---------|
| 1 | **Checklist 1: Consensus retry flow** | Correct propagation of simplified_messages, correct fallback logic, correct human gate on single-model failure |
| 2 | **Checklist 4: Human gate auto-approve** | Same resolve() code path, distinct status string for audit trail |
| 3 | **Checklist 5: Validation check ordering** | 5e → 6 propagation via dict mutation, engine propagation fix verified (commit 77b9b42) |
| 4 | **Checklist 10: Integration script fixes** | Commit 3d18faf correctly adds level field and uses proper name similarity comparison |

### Minor Findings (Non-Blocking): 2

| # | Finding | Recommendation |
|---|---------|---------------|
| 1 | AF-2: Author inference confidence not stored | Consider adding `author` field to `InferredFieldConfidence` in a future iteration |
| 2 | AF-3: Genre chain silently drops invalid relation types | Add warning log before returning None |

---

## Self-Review — Errors and Gaps in This Audit

This section was added after a skeptical re-read of the entire audit. It documents mistakes, incomplete analysis, and missed findings.

### SR-1: CRITICAL — Checklist 7 Fix Does Not Abort the Write

**Problem:** My proposed fix for Checklist 7 (gate-severity errors ignored) creates human gate checkpoints but does NOT raise an exception to prevent Steps 12–13 (registration and cleanup) from executing. The source would be registered as if nothing is wrong, defeating the purpose of the gate.

**SPEC evidence:** SPEC §5 line 1445: "Six checks run in order. Any failure aborts the write." Check 3 (line 1451): explicit "abort write." Check 6a (line 1464): explicit "abort write." Check 5c (line 1461): "EXCEPT author-science mismatch which triggers a human gate" — the exception to "not blocking" implies this IS blocking.

**Corrected fix:** After creating gate checkpoints for gate-severity errors, the fix must raise to prevent registration:

```python
gate_errors = [e for e in validation_errors if e.severity == "gate"]
if gate_errors:
    for gate_error in gate_errors:
        # ... create appropriate gate checkpoints ...
    raise make_error(
        ErrorCode.LOW_CONFIDENCE,
        f"Validation produced {len(gate_errors)} gate-severity error(s) "
        f"requiring human review before registration",
        source_id=source_id,
        context={"gate_errors": [e.message for e in gate_errors]},
    )
```

Without this raise, the fix is worse than useless: it creates gates that imply the source needs review while simultaneously registering it as if approved.

### SR-2: MODERATE — Checklist 7 Fix Contains Code Errors

**Problem:** The pseudocode in my fix references functions that don't exist in engine.py:
- `_resolve_nested_field(data_for_validation, gate_error.field)` — this function exists in `shared/validation/src/validation.py`, not in engine.py. It would need to be imported or the logic inlined.
- `_get_confidence_value(data_for_validation, gate_error.field)` — this function does not exist anywhere.
- The import `from engines.source.src.human_gate import gate_author_disambiguation` is wrong — the code calls `create_checkpoint`, not `gate_author_disambiguation`. The correct import is `from shared.human_gate.src.human_gate import create_checkpoint`.

**Impact:** Claude Code would encounter import errors if it implemented the fix verbatim. The FIX INTENTION is correct but the FIX CODE is not copy-pasteable. Claude Code needs to understand the intent and write correct code.

### SR-3: MODERATE — AF-1 Evidence Claim Is Overstated

**Problem:** I wrote: "Verified: Test result 02_nahw_muhaqiq.json has publication_year_hijri: null and publication_year_miladi: null despite the source having الطبعة field with year data."

This evidence is wrong on two counts:
1. Fixture 02_nahw_muhaqiq does NOT have an الطبعة field in its source HTML.
2. Fixture 03_fiqh DOES have الطبعة with year data ("الأولى 1354 هـ"), but `format_specific_metadata` is completely empty for ALL 13 fixtures. This means the extractor's secondary field collection may have its own issues — the null `publication_year_hijri` could be caused by extraction failure upstream, not just the field mapping bug.

**The bug itself is still real** — provable from code inspection alone: `shamela_html.py` writes `result["edition_year_hijri"]`, `engine.py` reads `extracted.get("publication_year_hijri")`. These keys do not match. But my evidence from test results does not demonstrate this bug because the data never reaches the mapping stage.

**Bonus finding:** `format_specific_metadata` is empty for all 13 fixtures. This is likely a separate extraction issue (the fixtures may lack the expected HTML structure for secondary fields, or the extractor's `_assemble_format_specific_metadata` isn't being called correctly). Step 2 (deterministic sweep on real data) will reveal whether this is a fixture limitation or a real extraction bug.

### SR-4: MINOR — Checklist 1 Understates the Fallback Asymmetry

**Problem:** My analysis correctly identified that fallback GPT-5.4 fires only when Cohere fails (consensus.py:258 checks `"cohere" in failed_model.model_id`). But I framed this as a "note for future" when it's actually a present asymmetry worth documenting more clearly.

When Opus fails, NO fallback is attempted — the system goes straight to human gate. When Cohere fails, the system tries GPT-5.4 as a replacement, potentially avoiding the human gate. This means Opus failures cause strictly more human gate checkpoints than Cohere failures.

The SPEC doesn't require symmetric fallback, so this remains NO ISSUE. But the practical consequence — Opus instability would cause a disproportionate gate queue — should be called out for operational awareness during Step 5 (full 2,519-book run). A symmetric fallback (also try GPT-5.4 when Opus fails, paired with surviving Cohere) would be a sensible hardening step before Step 5.

### SR-5: MINOR — Missed Finding: Single-Model Work Matching Lacks needs_review

**Problem I missed:** SPEC §6 (line 1520): "Work matching (lower cascade risk): if one model fails, the single model's result is accepted provisionally with single_model_confidence flag and needs_review on work_id."

In the code (`metadata_inference.py:452–477`), when only one model succeeds, the work matching comparison is skipped entirely (it requires `len(successful) >= 2`). The surviving model's genre_chain is accepted without setting `needs_review` on `work_id` or marking `single_model_confidence`.

**Risk:** Low. When one model fails for `author_identification`, the consensus result already triggers a human gate (`needs_human_gate=True`). The owner will review the entire source. The missing `work_id` needs_review flag is technically a SPEC-code mismatch but has no practical impact because the source is already flagged for review.

**Recommendation:** Add `work_id` to `needs_review_fields` when `len(successful) == 1` in `metadata_inference.py`. Non-blocking for Step 2 but should be fixed for SPEC compliance.

### SR-6: MINOR — SPEC Says Two evaluate() Calls, Code Makes One

**Problem:** SPEC §6 line 1534: "The source engine calls evaluate() twice during Step 4: once for author identification, once for work matching." The code calls `evaluate()` once (`metadata_inference.py:413`) and performs work matching locally on the same model responses (`metadata_inference.py:458`).

This is architecturally correct — the same prompt produces the same responses, so a second call would be wasteful. The work matching comparison (`check_work_agreement`) correctly extracts genre_chain fields from both models' responses. But the SPEC text is misleading.

**Action:** SPEC documentation fix only (no code change). The SPEC should say: "The source engine calls evaluate() once during Step 4 for author identification. Work matching (§6.2) and attribution status comparison (§6.3) are performed locally on the same model responses — they do not require additional evaluate() calls."

### SR-7: MINOR — Staging Cleanup Failure Is Silent

**Problem I noted but underweighted:** `engine.py:596–599`:
```python
try:
    shutil.move(str(staging_result.source_path), str(processed_dir / source_id))
except Exception:
    pass  # Non-fatal if move fails
```

This violates the fail-loud constraint. If the move fails, the original staging files remain in place alongside the frozen copies. Next startup, `cleanup_orphaned_locks` won't catch this (no lock file remains). The staging directory gradually accumulates processed files.

**Fix:** Replace `pass` with `logger.log_event("cleanup_warning", source_id, f"Failed to move staging files to .processed: {exc}")`. Non-blocking for Step 2.

### Summary of Self-Review Changes

| # | Finding | Impact on Audit |
|---|---------|----------------|
| SR-1 | Checklist 7 fix missing abort raise | **CRITICAL** — Fix as written would register sources that should be blocked. Claude Code must add the raise. |
| SR-2 | Checklist 7 fix has code errors | **MODERATE** — Fix cannot be copied verbatim. Claude Code needs to understand intent. |
| SR-3 | AF-1 evidence was wrong | **MODERATE** — Bug is still real (code proves it), but "verified" claim was based on bad evidence. Bonus: format_specific_metadata empty for all fixtures. |
| SR-4 | Checklist 1 understated fallback asymmetry | **MINOR** — Verdict unchanged, but operational note needed. |
| SR-5 | Missed: work_id needs_review on single-model | **MINOR** — SPEC-code gap, no practical impact due to existing human gate coverage. |
| SR-6 | SPEC says two evaluate() calls, code has one | **MINOR** — SPEC documentation fix only. |
| SR-7 | Staging cleanup failure silent | **MINOR** — Add logging. |

**Final bug count (unchanged):** 4 bugs requiring fix before Step 2. But the fix specification for bug #1 (Checklist 7) is materially wrong as originally written — SR-1 and SR-2 correct it.

---

## Final Review — New Findings and Definitive Fix List

This section was added after a third, independent re-trace of every code path in engine.py, validation.py, metadata_inference.py, consensus.py, scholar_authority.py, and the extractors. It found 2 additional bugs that must be fixed before Step 2, 3 lower-severity issues, and corrected a factual error in the self-review.

### FR-1: BUG — Title Priority Reversed (engine.py:376–381)

**Code:**
```python
title_arabic = (
    extracted.get("display_title")    # ← checked first
    or extracted.get("title_full")    # ← checked second
    or extracted.get("title_arabic")
    or ""
)
```

**SPEC (line 946):** "Use `title_full` if present (from الكتاب field), else `display_title` (from card header)."

`display_title` is the Shamela card header — a short UI display name. `title_full` is the الكتاب metadata field — the authoritative book title. Python's `or` short-circuits: when `display_title` is non-empty (which it always is for Shamela exports), `title_full` is never checked.

**Cascade:** `title_arabic` feeds into `generate_work_id(author_name, title_arabic, ...)`. Wrong title → wrong `work_id` → two sources of the same work with different display titles but identical الكتاب fields would get different work_ids, defeating deduplication.

**Fix:** Swap the priority order:
```python
title_arabic = (
    extracted.get("title_full")
    or extracted.get("display_title")
    or extracted.get("title_arabic")
    or ""
)
```

### FR-2: BUG — Layer Author Dummy ID Crashes Validation (engine.py:208–213)

**Code:**
```python
if author_name:
    ref = lookup_or_register_muhaqiq(...)
else:
    ref = ScholarReference(
        canonical_id="sch_00000",
        name_arabic="مجهول",
        confidence=0.0,
        source_of_identification="inferred",
    )
```

When the LLM returns a text layer with an empty `author_name`, the engine creates a dummy `ScholarReference` with `canonical_id="sch_00000"`. This ID does not exist in `scholars.json` (sequential IDs start at `sch_00001`).

Validation Check 6c (`validation.py:281–296`) then checks:
```python
if layer_author_id and layer_author_id not in registries["scholars"]:
    errors.append(ValidationError(severity="fatal", ...))
```

Result: any multi-layer source where the LLM omits a layer author name triggers a FATAL validation error and the source is rejected. The engine should degrade gracefully — either register a placeholder "unknown" scholar or omit the layer from `text_layers`.

**Fix:** Register a placeholder scholar instead of using a hard-coded dummy ID:
```python
else:
    # Register anonymous layer author as a placeholder scholar
    unknown_record = ScholarAuthorityRecord(
        canonical_id="",
        canonical_name_ar="مجهول",
        sources_encountered_in=[source_id],
        last_updated="",
    )
    registered = register(unknown_record, registry_path=registry_path)
    ref = ScholarReference(
        canonical_id=registered.canonical_id,
        name_arabic="مجهول",
        confidence=0.0,
        source_of_identification="inferred",
    )
```

Or, more conservatively, skip layers with unknown authors and flag `text_layers` for human review.

### FR-3: Low severity — structural_format Defaults to "prose" Instead of "mixed" (engine.py:401)

**Code:** `structural_format_val = inference.structural_format or "prose"` — when inference returns `None`, the engine defaults to `"prose"`.

**SPEC (line 1094):** "set the field to the most conservative value... `'mixed'` for structural_format."

`metadata_inference.py:486` correctly uses `StructuralFormat.MIXED.value` for invalid LLM values, but that's a different code path. The engine's `None` handling overrides it. "prose" is a specific claim; "mixed" is honest uncertainty.

**Fix:** Change `"prose"` to `"mixed"` on engine.py:401. Trivial.

### FR-4: Low severity — Check 5d (Attribution vs Prior Sources) Is Dead Code

`engine.py:564` calls `validate_source_metadata(data_for_validation, registries=registries)` without passing `prior_sources`. The parameter defaults to `None`, so `_check_consistency` (validation.py:208–226) skips the entire Check 5d branch. The check is correctly implemented but never receives data.

**Impact:** Low. Only matters when another source of the same work_id already exists with a different attribution_status. During Step 2 (processing 2,519 books against an empty registry), work-level duplicates are uncommon. The check becomes relevant during Step 5 (full collection processing).

**Fix (defer to before Step 5):** After the work_reg lookup (engine.py:432–439), if `work_id in work_reg`, load the existing source's metadata and pass as `prior_sources` to validation.

### FR-5: Low severity — Layer Authors Use Muhaqiq Registration Path (engine.py:202)

`_build_text_layers` calls `lookup_or_register_muhaqiq` for layer authors. Muhaqiq registration auto-links in the 0.50–0.85 range without creating a human gate (scholar_registry.py:139–145), while author registration would create a gate in that range (scholar_registry.py:63–90).

Layer authors (e.g., the matn author in a sharh) are primary authors, not editors. They should receive the same deduplication rigor. An ambiguous match at score 0.65 would auto-link silently instead of requesting owner confirmation.

**Fix:** Use `lookup_or_register_author` with available death date and school info. Non-blocking for Step 2 — in practice, layer authors are usually already registered as primary authors of their own works, so the auto-link is typically correct.

### FR-6: Correction to SR-3 — Evidence Was Even Weaker Than Stated

The self-review noted that `format_specific_metadata` is "empty for all 13 fixtures" and speculated about extraction issues. This is wrong. The integration script (`scripts/phases/run_session6_integration.py`) simply does not capture `format_specific_metadata`, `publication_year_hijri`, `publication_year_miladi`, or `edition_number` in its output JSON. The actual `SourceMetadata` object created during the run may have had these fields populated — we cannot tell from the script output.

The AF-1 field mapping bug remains provable from code alone (extractor writes `edition_year_hijri`, engine reads `publication_year_hijri` — keys don't match). No empirical verification of this bug was actually performed or is available from current test outputs.

---

## Definitive Fix List for Claude Code

This is the authoritative, corrected specification of all fixes. It supersedes the inline fix descriptions in the checklist items above (which contain errors identified in the self-review). Fixes are ordered by severity.

### Fix 1 (HIGH): Validation Gate Errors — Create Gates AND Abort

**File:** `engines/source/src/engine.py`
**Location:** After line 581 (after the fatal_errors check)
**What to do:**

1. Filter validation_errors for `severity == "gate"`.
2. For each gate error, create the appropriate human gate checkpoint based on `gate_error.check`:
   - `"confidence_threshold"` → call `gate_low_confidence(source_id, gate_error.field, <value>, <confidence>)`. Extract the value and confidence from `data_for_validation` using the field path in `gate_error.field`.
   - `"consistency_author_science"` → call `create_checkpoint(source_id=source_id, trigger=HumanGateTrigger.AUTHOR_SCIENCE_MISMATCH, trigger_detail=gate_error.message, fields_to_review=["science_scope", "author"], current_values={"detail": gate_error.message})`. Import `create_checkpoint` from `shared.human_gate.src.human_gate` and `HumanGateTrigger` from `engines.source.contracts`.
   - `"multi_layer_empty_layers"` → call `gate_low_confidence(source_id, "text_layers", "[]", 0.0)`.
3. After creating all gate checkpoints, **raise** to prevent registration:
   ```python
   raise make_error(
       ErrorCode.LOW_CONFIDENCE,
       f"Validation gate: {len(gate_errors)} issue(s) require human review",
       source_id=source_id,
       context={"gate_errors": [e.message for e in gate_errors]},
   )
   ```

**Why the raise is essential:** SPEC §5 line 1445 says "Any failure aborts the write." Check 3 and Check 6a explicitly say "abort write." Without the raise, the source is registered with unreviewed gate conditions — the gate checkpoint exists but the damage is already done.

### Fix 2 (MEDIUM): Registration Rollback — Validate .bak and Fail Loud

**File:** `engines/source/src/registries/__init__.py`
**Function:** `_rollback_registries` (line 270)

After `os.replace(str(bak_file), str(registry_path))` succeeds, validate the restored file:
```python
try:
    restored_raw = registry_path.read_text(encoding="utf-8")
    json.loads(restored_raw)
except (json.JSONDecodeError, OSError) as exc:
    raise RuntimeError(
        f"Registry {registry_path} restored from backup but backup is also corrupt. "
        f"Manual recovery required."
    ) from exc
```

Replace the `except OSError: pass` (line 286) with a raise:
```python
except OSError as exc:
    raise RuntimeError(
        f"Cannot restore registry {registry_path} from backup: {exc}. "
        f"Manual recovery required."
    ) from exc
```

**Also fix** the partial rollback in `check_orphaned_registrations` (line 263): same pattern — replace `pass` with a logged error and append to an unrecoverable list.

### Fix 3 (MEDIUM): Name Matching — Strip Punctuation

**File:** `shared/scholar_authority/src/name_matching.py`
**Function:** `normalize_arabic_name` (line 15)

Add after the definite article strip (line 30) and before whitespace collapse (line 32):
```python
# Strip Arabic and Latin punctuation (prevents token mismatches from LLM commas)
result = re.sub(r'[،؛,;:.!؟?\u00BB\u00AB\-\u2013\u2014/]', ' ', result)
```

This replaces: Arabic comma (،), Arabic semicolon (؛), Latin comma, semicolon, colon, period, exclamation, Arabic question mark (؟), Latin question mark, guillemets (» «), hyphens/dashes, forward slash — all with spaces, which the subsequent whitespace collapse normalizes.

### Fix 4 (MEDIUM): Publication Year Field Mapping

**File:** `engines/source/src/engine.py`
**Lines:** 461–462

Change:
```python
publication_year_hijri=extracted.get("publication_year_hijri"),
publication_year_miladi=extracted.get("publication_year_miladi"),
```
To:
```python
publication_year_hijri=extracted.get("edition_year_hijri"),
publication_year_miladi=extracted.get("edition_year_miladi"),
```

### Fix 5 (MEDIUM): Title Priority — title_full Before display_title

**File:** `engines/source/src/engine.py`
**Lines:** 376–381

Change:
```python
title_arabic = (
    extracted.get("display_title")
    or extracted.get("title_full")
    or extracted.get("title_arabic")
    or ""
)
```
To:
```python
title_arabic = (
    extracted.get("title_full")
    or extracted.get("display_title")
    or extracted.get("title_arabic")
    or ""
)
```

### Fix 6 (MEDIUM): Layer Author Dummy ID — Register Placeholder Instead

**File:** `engines/source/src/engine.py`
**Function:** `_build_text_layers` (lines 207–213)

Replace the dummy ScholarReference with a real placeholder registration. Either:

Option A (preferred): Register a placeholder "مجهول" scholar:
```python
else:
    from shared.scholar_authority.src.scholar_authority import register
    unknown_record = ScholarAuthorityRecord(
        canonical_id="",
        canonical_name_ar="مجهول",
        sources_encountered_in=[source_id],
        last_updated="",
    )
    registered = register(unknown_record, registry_path=registry_path)
    ref = ScholarReference(
        canonical_id=registered.canonical_id,
        name_arabic="مجهول",
        confidence=0.0,
        source_of_identification="inferred",
    )
```

Option B (simpler): Skip layers with no author and flag for review. This avoids polluting the scholar registry with anonymous placeholders but means the layer isn't tracked.

Claude Code should choose based on which behavior is safer: registering anonymous scholars (Option A, complete layer tracking) or omitting anonymous layers (Option B, cleaner registry). I recommend Option A for layer tracking completeness, with a note that each "مجهول" registration gets its own unique ID, so they won't conflict.

### Non-Blocking Fixes (implement during Step 2 fix cycle or later)

| Fix | File | Change |
|-----|------|--------|
| structural_format default | engine.py:401 | Change `"prose"` to `"mixed"` |
| Genre chain silent drop | engine.py:175 | Add `logger.warning(...)` before `return None` |
| Staging cleanup silent | engine.py:598 | Replace `pass` with `logger.log_event(...)` |
| Layer author human gate | engine.py:202 | Change `lookup_or_register_muhaqiq` to `lookup_or_register_author` |
| Single-model work_id needs_review | metadata_inference.py | Add `work_id` to needs_review when `len(successful) == 1` |
| prior_sources for Check 5d | engine.py:564 | Pass existing source metadata when work_id exists in registry |
| SPEC text: two evaluate calls | SPEC_CORE.md:1534 | Correct to "one evaluate call, local comparisons on same responses" |

### Revised Summary

| Category | Count | Items |
|----------|-------|-------|
| **Bugs requiring fix before Step 2** | **6** | Gate errors ignored (#1), rollback silent (#2), punctuation bug (#3), publication year mapping (#4), title priority (#5), layer author crash (#6) |
| **Deferred to Stage 2** | 3 | Concurrent scholar locking, trust re-evaluation, enrichment passthrough |
| **Non-blocking fixes** | 7 | structural_format default, genre chain log, staging cleanup log, layer author human gate, work_id needs_review, prior_sources wiring, SPEC text correction |
| **No issue** | 4 | Consensus retry, human gate auto-approve, validation ordering, integration script fixes |
