# Concurrency Analysis: Excerpting Pipeline

**Date:** 2026-03-28
**Scope:** All files in `engines/excerpting/src/`, `shared/llm/cli_adapter.py`, `engines/excerpting/contracts.py`
**SPEC anchor:** SPEC.md line 811: "Chunks from different sources may be processed in parallel."
**Status:** RESEARCH ONLY -- no code changes

---

## Executive Summary

The excerpting pipeline is currently single-threaded and sequential. It was designed for sequential per-source processing but the SPEC explicitly permits inter-source parallelism. This analysis identifies **14 concurrency hazards** that would manifest under parallel execution. The most critical are: (1) file I/O using write-mode ("w") without locks, which causes data loss on concurrent writes; (2) the CLI adapter's `_tool_checked` set on a shared adapter instance, which is a race condition; and (3) Python's logging module writing to the same handlers from multiple threads/processes, which interleaves log lines. None of these are bugs today -- they are latent hazards that activate the moment parallelism is introduced.

---

## 1. Shared Mutable State

### 1.1 CLIInstructorAdapter._tool_checked (RISK: HIGH)

**File:** `shared/llm/cli_adapter.py` line 679
**Type:** Instance-level mutable `set[str]`

```python
self._tool_checked: set[str] = set()
```

The set is checked and mutated in `_CompletionsNamespace.create()` (lines 265-267):

```python
if backend not in adapter._tool_checked:
    _check_tool_available(backend)
    adapter._tool_checked.add(backend)
```

**Hazard:** If two threads share the same `CLIInstructorAdapter` instance and both call `.create()` simultaneously for the same backend, the check-then-add is a classic TOCTOU (time-of-check/time-of-use) race. Both threads could pass the `not in` check before either adds to the set. This is benign (worst case: `shutil.which` is called twice), but the pattern is a red flag for any reviewer.

**Impact if parallel:** Benign duplication. No data corruption.

### 1.2 CLIInstructorAdapter._hooks (RISK: MEDIUM)

**File:** `shared/llm/cli_adapter.py` lines 678, 684-699

The `_hooks` dict (maps event names to callback lists) is mutated by `.on()` and read by `._fire_hooks()`. If hooks are registered from one thread while another thread is iterating the callback list, `RuntimeError: dictionary changed size during iteration` or silent callback skipping can occur.

**Impact if parallel:** Hook registration during processing causes crash or silent miss. Registration typically happens at startup, so low probability.

### 1.3 Module-Level Constants (RISK: NONE)

All module-level variables in the excerpting engine are immutable:
- `CLASSIFY_SYSTEM_PROMPT`, `GROUP_SYSTEM_PROMPT`, `ENRICH_SYSTEM_PROMPT`, `VERIFY_SYSTEM_PROMPT` -- string constants
- `_ARABIC_DIACRITICS` -- `frozenset`
- `_QURAN_VERSE_RE`, `_ARABIC_NOISE_RE`, `_FOOTNOTE_MARKER_RE`, `_SENTENCE_BOUNDARY_RE` -- compiled `re.Pattern` (immutable once compiled)
- `_PROVIDER_MAP` -- dict, never mutated after module load
- `_AUTH_ERROR_PATTERNS` -- tuple (immutable)
- `_SC_LEVEL_ORDER` -- dict, never mutated after module load
- `QURAN_SURAH_AYAH_COUNTS` -- dict, never mutated after module load

These are all safe for concurrent access.

### 1.4 No Global Singletons or Caches

The pipeline has no global singleton pattern, no module-level LRU cache, and no shared mutable registry. Each `run_excerpting()` call creates its own `ExcerptingResult`, `Phase3Result`, and intermediate `dict` objects. This is excellent for parallelism.

### 1.5 ExcerptingConfig (RISK: NONE)

`ExcerptingConfig` is a Pydantic `BaseModel` (effectively immutable after construction). Passed by reference but never mutated during processing. Safe.

### 1.6 Pydantic model_copy (RISK: NONE)

The pipeline consistently uses `model_copy(update={...})` instead of in-place mutation for `ExcerptRecord` updates (e.g., `phase3_enrichment.py` line 348, `phase3_consensus.py` line 282). This is a strong concurrency-safe pattern. The one exception is `verify_units()` in `phase2_group.py` (lines 234-265) which mutates `TeachingUnit.start_word` and `.end_word` in-place for V-P2-14 auto-repair, but these objects are local to the chunk being processed.

---

## 2. File I/O Conflicts

### 2.1 excerpts.jsonl -- Write Mode "w" (RISK: CRITICAL under parallelism)

**File:** `writer.py` line 52

```python
with open(output_path, "w", encoding="utf-8") as f:
```

Uses write mode `"w"`, not append mode `"a"`. This means the function overwrites the entire file. In the current design, `write_excerpts()` is called once at the end of `run_excerpting()` with all excerpts collected. Under parallel execution:

- **Intra-source:** No conflict. One source = one call to `write_excerpts()`.
- **Inter-source:** Each source writes to a different `output_dir` (`library/sources/{source_id}/excerpts/`). No conflict as long as source IDs are unique per parallel worker.

**Latent hazard:** If the design ever changes to write excerpts incrementally (per-chunk instead of per-source), concurrent chunks writing to the same file would clobber each other.

### 2.2 gate_queue.jsonl -- Write Mode "w" (RISK: CRITICAL under design change)

**File:** `writer.py` line 91

Same pattern as excerpts.jsonl. Same analysis: safe under current design (one write per source), dangerous if changed to incremental writes.

### 2.3 gate_queue.jsonl -- Retry Write in verify_gate_queue (RISK: MEDIUM)

**File:** `writer.py` lines 184-188

```python
write_gate_queue(gate_entries, gate_path.parent)
missing = _find_missing(gate_path)
```

The retry verification (V-P3-7) re-calls `write_gate_queue()` and re-reads the file. If another process is writing to the same file simultaneously, the re-read could see a partial write and report false missing entries, triggering `EX-M-008` (HALT).

**Impact under parallelism:** False HALT if two sources share an output directory (currently impossible since paths are `{source_id}`-scoped).

### 2.4 processing_log.jsonl -- Write Mode "w" (RISK: LOW)

**File:** `writer.py` line 245

Same write-mode pattern. Written once per source. Each source writes to its own directory. Safe under current architecture.

### 2.5 CLI Adapter Temp Files (RISK: NONE)

**File:** `cli_adapter.py` lines 583-592

The codex backend uses `tempfile.NamedTemporaryFile()` with `delete=False`, which generates unique names per invocation via the OS tempfile mechanism. The files are cleaned up in a `finally` block. Two concurrent codex calls would get different temp files.

```python
schema_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
output_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
```

The claude and gemini backends pass prompts as CLI arguments (not temp files). No temp file conflict.

### 2.6 mkdir(parents=True, exist_ok=True) (RISK: NONE)

All directory creation uses `exist_ok=True` (`writer.py` lines 43, 88, 232). This is safe under concurrent calls -- the OS handles the race atomically.

---

## 3. Subprocess Race Conditions

### 3.1 Concurrent CLI Subprocess Calls (RISK: MEDIUM)

**File:** `cli_adapter.py` lines 530-538, 604-611, 648-656

Each LLM call spawns a subprocess via `subprocess.run()`. Each subprocess is independent with its own stdin/stdout/stderr pipes (`capture_output=True`). There is no shared buffer between concurrent `subprocess.run()` calls.

**However:** On Windows, `subprocess.run()` with `capture_output=True` creates anonymous pipes. The OS imposes per-process limits on pipe handles. With 308 chunks, even 5-10 concurrent subprocesses should be fine, but 50+ might approach Windows limits (~512 file handles by default, ~8192 with `_setmaxstdio`).

### 3.2 OAuth Token Reading (RISK: LOW)

**File:** `cli_adapter.py` lines 97-113

`_get_oauth_token()` reads `~/.claude/.credentials.json` on every call (no caching). Two concurrent calls both reading the same JSON file is safe (reads are non-destructive). If the credentials file is being updated simultaneously by the `claude` CLI refreshing its token, a read could see a partially-written file, but this is extremely unlikely (file is small, write is nearly atomic).

### 3.3 `time.sleep()` in Retry Loops (RISK: LOW)

**Files:** `phase2_classify.py` line 467, `phase2_group.py` line 379, `phase3_enrichment.py` line 505, `cli_adapter.py` lines 421, 445

Retry backoff uses `time.sleep(2**attempt)`. In a threaded context, `time.sleep()` blocks the calling thread but not others. In a multiprocessing context, each process sleeps independently. No race condition, but the backoff delay stacks if multiple chunks fail simultaneously (resource wasted, not corrupted).

---

## 4. Resource Exhaustion

### 4.1 Subprocess Handle Limits on Windows (RISK: HIGH for >10 concurrent)

Windows default per-process handle limit is 512 (including file handles, pipe handles, socket handles). Each `subprocess.run()` with `capture_output=True` consumes 3 handles (stdin, stdout, stderr) plus the process handle. With 10 concurrent LLM calls: ~40 handles. With 50 concurrent calls: ~200 handles. The margin is tight if other file operations are also happening.

**Recommendation:** Limit concurrent subprocesses to 5-10 via a semaphore.

### 4.2 Memory: Arabic Text in Flight (RISK: MEDIUM for >20 concurrent)

Each chunk's processing holds:
- `assembled_text`: 500-10,000 Arabic words = ~5KB-100KB
- LLM response: ~2-30KB JSON
- `ExcerptRecord` objects: ~1-5KB each, ~5-30 per chunk
- System + user prompts: ~3-10KB (with the full ENRICH_SYSTEM_PROMPT at ~5KB)

Per chunk: ~50-200KB peak. With 10 concurrent: ~2MB. With 100 concurrent: ~20MB. Memory is not a bottleneck.

**Real risk:** The `cli_adapter.py` captures the full stdout of each subprocess (`capture_output=True`). If an LLM backend returns an unexpectedly large response (malformed, repeating output), the buffer grows unbounded until subprocess termination or timeout.

### 4.3 Disk Space for Processing Log (RISK: NONE)

`processing_log.jsonl` contains one JSON line per source run. Even with 1000 sources, each line is ~500 bytes = ~500KB total. Negligible.

### 4.4 File Handle Limits for JSONL Writing (RISK: NONE)

Each write function opens a file, writes, and closes within a `with` block. No handles are held open across chunk processing. Safe even with 308 chunks.

---

## 5. Error Propagation

### 5.1 Chunk N Failure Does Not Corrupt Chunk N+1 (RISK: NONE -- well designed)

Each phase iterates over chunks independently:

- `run_phase2a()` (`phase2_classify.py` lines 356-478): Each chunk has its own `error_feedback`, `last_error_code`, and `success` variables. Failed chunks are omitted from the result dict. No shared state between iterations.
- `run_phase2b()` (`phase2_group.py` lines 272-390): Same pattern. Failed chunks are absent from result.
- `run_phase3_enrichment()` (`phase3_enrichment.py` lines 412-522): Failed chunks get `llm_enrichment_failed` flag appended. Other chunks unaffected.
- `run_consensus()` (`phase3_consensus.py` lines 696-877): Failed chunks get `verification_skipped` flag. Other chunks unaffected.

This isolation is excellent for parallelism. Each chunk's processing is self-contained.

### 5.2 Partial Results on Crash (RISK: MEDIUM)

**File:** `pipeline.py` lines 170-199

If the process is killed during Phase 3, no output files exist yet (writing happens at the end). All intermediate state (the `all_excerpts` list) is lost. This is by design -- the pipeline writes atomically at the end.

**Under parallelism:** If one worker crashes, its source's output is lost. Other workers' outputs are unaffected (different output directories). The processing_log for the crashed source is also lost, making debugging harder.

### 5.3 The Phase3Result Accumulator (RISK: MEDIUM under naive parallelism)

**File:** `phase3_orchestrator.py` lines 75-192

`run_phase3()` accumulates `all_excerpts` in a list across all chunks:

```python
all_excerpts: list[ExcerptRecord] = []
for chunk in chunks:
    excerpts = build_deterministic_excerpts(chunk, units, segments)
    all_excerpts.extend(excerpts)
```

If chunks were processed in parallel and appended to the same `all_excerpts` list, `list.extend()` is NOT thread-safe in CPython (the GIL protects individual bytecode operations, but `.extend()` may involve multiple operations).

**Fix required for parallelism:** Use a `collections.deque` or `queue.Queue`, or collect per-chunk results and merge after parallel completion.

---

## 6. Lock Analysis

### 6.1 No Locks Exist

Zero threading locks, mutexes, file locks, or database transactions exist anywhere in the excerpting engine or CLI adapter. The codebase has zero imports of `threading`, `multiprocessing.Lock`, `fcntl`, `msvcrt`, or `portalocker`.

### 6.2 Python Logging (RISK: LOW)

All modules use `logging.getLogger(__name__)`. Python's logging module is thread-safe internally (handlers use locks). However:

- **FileHandler** writes may interleave lines if two threads log simultaneously at very high frequency. The logging module's internal lock ensures each `emit()` call is atomic, but the handler's buffer flush timing can cause partial lines on disk.
- **StreamHandler** (stdout/stderr) is similarly protected but may interleave on Windows console output.

Under multiprocessing (not threading), logging is NOT safe without a `QueueHandler` / `QueueListener` pattern. Each process would need its own log file or a centralized logging process.

### 6.3 What SHOULD Have a Lock But Does Not

| Resource | Lock Type Needed | When |
|----------|-----------------|------|
| `_tool_checked` set in CLI adapter | `threading.Lock` | If adapter instance shared across threads |
| `_hooks` dict in CLI adapter | `threading.Lock` | If `.on()` called during processing |
| `all_excerpts` list in phase3_orchestrator | `threading.Lock` or per-chunk collection | If chunks processed in parallel |
| Output JSONL files | File lock or single-writer pattern | If incremental writes introduced |
| Processing log | File lock or append mode | If multiple sources share output dir |

---

## 7. SPEC Parallelism Mandate

SPEC.md line 811 states:

> **Per-source ordering:** Chunks from the same source are processed sequentially (by `div_id` order). Chunks from different sources may be processed in parallel.

This means the SPEC permits:
- **Inter-source parallelism:** Two different books processed simultaneously. Each gets its own `run_excerpting()` call with its own `NormalizedPackage`.
- **Intra-source sequential:** Chunks within a source must be processed in `div_id` order.

Under inter-source parallelism, the current code is **mostly safe** because:
1. Each source writes to `library/sources/{source_id}/excerpts/` (unique per source)
2. Each `run_excerpting()` creates its own intermediate state
3. No shared mutable module-level state

The hazards arise only if:
- Two workers share the same `CLIInstructorAdapter` instance (1.1, 1.2)
- Two workers log to the same file handler (6.2)
- A design change introduces shared output paths or incremental writes

---

## Risk Matrix

| # | Issue | Likelihood | Impact | Risk | Recommended Fix |
|---|-------|-----------|--------|------|-----------------|
| 1 | `_tool_checked` TOCTOU race | Medium (shared adapter) | Low (benign duplication) | LOW | Wrap in `threading.Lock`, or make per-thread |
| 2 | `_hooks` concurrent mutation | Low (hooks registered at startup) | Medium (crash or silent miss) | LOW | Wrap `.on()` and `._fire_hooks()` in lock |
| 3 | `write_excerpts()` mode "w" clobber | None (per-source dirs) | Critical (total data loss) | NONE now, CRITICAL if design changes | Document contract: one writer per output_dir |
| 4 | `write_gate_queue()` mode "w" clobber | None (per-source dirs) | Critical (data loss + false HALT) | NONE now, CRITICAL if design changes | Same as above |
| 5 | `verify_gate_queue()` retry read race | None (single-process) | Critical (false HALT via EX-M-008) | NONE now, HIGH if shared dirs | File lock during write-verify cycle |
| 6 | `write_processing_log()` clobber | None (per-source dirs) | Medium (lost telemetry) | NONE now, MEDIUM if design changes | Use append mode "a" |
| 7 | `all_excerpts.extend()` thread safety | None (sequential) | High (corrupted excerpt list) | NONE now, HIGH if intra-source parallel | Collect per-chunk, merge after join |
| 8 | Subprocess handle exhaustion (Windows) | Medium (>10 concurrent) | High (OSError, failed LLM calls) | MEDIUM | Semaphore limiting concurrent subprocesses |
| 9 | Unbounded subprocess stdout buffer | Low (malformed LLM output) | Medium (memory exhaustion) | LOW | Set max output size or use streaming |
| 10 | OAuth token file read during refresh | Very low | Low (JSONDecodeError, retry fixes) | VERY LOW | Cache token with TTL, or catch decode error |
| 11 | Logging interleave (threading) | Medium (concurrent sources) | Low (garbled log lines) | LOW | Use QueueHandler for file logging |
| 12 | Logging interleave (multiprocessing) | High (if mp used) | Medium (garbled + lost log lines) | MEDIUM | QueueHandler + QueueListener pattern |
| 13 | `verify_units()` in-place mutation | None (local objects) | None | NONE | No fix needed; mutation is chunk-local |
| 14 | Partial results on worker crash | Medium (LLM timeouts) | Medium (lost work, no debug info) | MEDIUM | Write per-chunk checkpoints before final merge |

---

## Recommendations for Parallelism Implementation

### Tier 1: Required before any parallel execution

1. **Semaphore on subprocess calls.** Create a `threading.BoundedSemaphore(max_concurrent_llm_calls)` in the CLI adapter. Wrap `subprocess.run()` calls. Default to 5 on Windows.

2. **Per-source isolation contract.** Document and enforce: each parallel worker gets its own `CLIInstructorAdapter` instance, its own output directory, and its own logger. No shared mutable state across workers.

3. **Collect-then-merge pattern for Phase 3.** Replace `all_excerpts.extend()` with per-chunk result lists, merged after all chunks complete. This is required even for intra-source parallelism.

### Tier 2: Required for production robustness

4. **Per-chunk checkpoint files.** Write intermediate results after each chunk's Phase 2/3 completes. On crash recovery, resume from last checkpoint. Without this, a 308-chunk source that fails on chunk 300 loses all work.

5. **Structured logging for parallel workers.** Use `logging.handlers.QueueHandler` with a centralized `QueueListener`. Each worker includes its source_id in log records.

6. **File lock for shared resources.** If any future design shares output paths (e.g., a global gate queue), use `portalocker` or `msvcrt.locking()` for Windows-compatible file locks.

### Tier 3: Nice to have

7. **Token caching in CLI adapter.** Cache the OAuth token with a TTL (e.g., 55 minutes for a 60-minute token). Eliminates redundant file reads and the minuscule read-during-refresh race.

8. **Subprocess output size limit.** Add `subprocess.PIPE` with a read loop that aborts after N bytes, preventing unbounded memory consumption from malformed LLM output.

---

## Architectural Strengths (no changes needed)

These patterns are already parallelism-friendly and should be preserved:

- **Immutable config:** `ExcerptingConfig` is a frozen-after-construction Pydantic model
- **Immutable module constants:** All prompts, regexes, and lookup tables are module-level immutable
- **model_copy() for updates:** ExcerptRecord mutation uses copy-on-write, not in-place
- **Per-source output directories:** `library/sources/{source_id}/excerpts/` naturally partitions writes
- **Independent chunk error handling:** Each chunk's success/failure is independent; no cross-chunk state contamination
- **Temp file uniqueness:** `tempfile.NamedTemporaryFile` guarantees unique names per invocation
- **No global singletons:** No module-level caches, registries, or shared state accumulators

---

*Analysis performed on the codebase at commit f65af2ab. No code was modified.*
