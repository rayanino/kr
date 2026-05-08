---
globs: ["engines/*/src/**/*.py", "shared/*/src/**/*.py"]
---
- **Single-key `sort()` / `sorted()` over a tie-prone sequence is a PYTHONHASHSEED determinism trap.** When the sequence is derived from a set (`sorted(some_set)`, `for item in some_set` then sort), a dict's value iteration, or LLM output (where confidence/score values may tie), the input order leaks into the post-sort "top" pick — different runs on different `PYTHONHASHSEED` values produce different downstream verdicts. The fix is a **tuple-key with a total-order secondary field**: `key=lambda x: (-primary_descending, secondary_total_order)`.
- **Greppable defect signatures** (audit before merging any change touching ranked output):
  - `sorted(... key=lambda ... reverse=True)` over LLM output (rankings, scores, confidences)
  - `.sort(key=lambda x: x[N], reverse=True)` over tuple lists where index N may tie
  - `sorted({...})` or `sorted(set(...))` over BaseModel-like objects without explicit secondary key
  - `max(..., key=lambda ...)` where two items can produce the same key (max returns first match in iteration order — same trap, different surface)
- **The fix pattern (durable across all 3 confirmed cases — Sessions 5, 7, 10):**
  - For descending-by-primary + ascending-by-secondary: `key=lambda r: (-r.score, r.canonical_id)` (drop `reverse=True`; the negation handles direction)
  - For ascending-by-primary + ascending-by-secondary: `key=lambda r: (r.start, r.id)`
  - The secondary field MUST be a total-order type (str, int, tuple of total-order types) — NOT a Pydantic BaseModel directly (BaseModel.__lt__ is undefined; comparison falls back to id() which is non-deterministic). Use a hashable identifier field: canonical_id, leaf_path, start_offset, etc.
- **Confirmed cases (3 of 3 in Phase 5 series):**
  - Session 5: `_build_positions_for_disputed` in `shared/scholar_authority/src/threshold_compounding.py` — `(-confidence, canonical_id)` tiebreak; fix locked positions[0] leader determinism.
  - Session 7: same module, defensive coverage.
  - Session 10: `route_excerpt` + `place_excerpt` UNPLACED diagnostics in `engines/taxonomy/src/placer.py` — `(-r.score, r.leaf_path)`; `compute_layer_attribution` in `engines/excerpting/src/phase3_deterministic.py` — `(-x[1], x[0].start)`.
- **When auditing a new sort site, decide SAFE / RISK / REGRESSION using this matrix:**

  | Input source | Key field tie-prone? | Verdict |
  |--------------|---------------------|---------|
  | `dict.values()` / `list[...]` from deterministic upstream + total-order key | No | SAFE |
  | `sorted(set(...))` over `int` or `str` with no duplicates | No (set dedupes; sort key is total-order) | SAFE |
  | LLM output (rankings, scores, confidences) | Yes (LLMs can return ties) | RISK — add tuple key |
  | `set(...)` of BaseModel objects iterated then sorted by float field | Yes (set iteration order is hash-derived) | REGRESSION — add tuple key + canonical_id secondary |
  | `dict.items()` sorted by value where values can tie | Yes | RISK — add tuple key with key as secondary |
  | `max(seq, key=...)` where multiple items can produce the same key | Yes | RISK — add `max(seq, key=lambda x: (key1, secondary))` |

- **Test pattern for tiebreak determinism (lock the contract):**
  - Construct two distinct input orderings that contain the SAME items at the SAME values (e.g., `[A(score=0.9), B(score=0.9)]` vs `[B(score=0.9), A(score=0.9)]`).
  - Call the function on each.
  - Assert the top pick / chosen leader / first emitted is identical across BOTH orderings.
  - Run repeatedly (e.g., 10x) to also catch hash-derived non-determinism.
  - Use real Arabic fixtures from `tests/fixtures/` for content, not synthetic Unicode (per `.claude/rules/testing.md`).
- **NEVER add a tiebreak via `random.shuffle` or `random.choice`** — that introduces non-determinism rather than fixing it. The deterministic tiebreak field must be deterministic from the input data alone (canonical_id, leaf_path, byte-offset, etc.).
