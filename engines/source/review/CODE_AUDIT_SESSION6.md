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

1. **Commit 3d18faf** — `scripts/run_session6_integration.py`:
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
