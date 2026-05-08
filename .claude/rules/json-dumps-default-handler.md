---
globs: ["engines/*/src/**/*.py", "shared/*/src/**/*.py", "scripts/**/*.py"]
---
- **`json.dumps(value)` without a `default=` callback raises `TypeError` when `value` carries a Pydantic `BaseModel` (or any non-serializable type).** This is a latent crash class in audit-trail / revision-history / event-log code paths where the value being serialized may be ANY field type. Bug surfaces only when a caller exercises the BaseModel-typed path; it can stay dormant for many sessions before crashing.
- **Greppable defect signatures** (audit before any merge touching audit-trail / event-log code):
  - `json.dumps\([^)]+\)` in audit-trail / revision-history / change-log / event-log code where the input value is dynamically typed (`Any`, `dict[str, Any]`, `list`, `field_name from getattr(...)`)
  - `json.dump(... fp ...)` (file variant) without `default=` in the same code paths
  - Any code that records a "before/after" or "old_value/new_value" pair where the field type is determined at runtime
- **The fix pattern (durable since Session 11):**
  - Define a module-level `_json_default(obj: Any) -> Any` callback near where `json.dumps` is called:
    ```python
    def _json_default(obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            return obj.model_dump(mode="json")
        raise TypeError(
            f"Object of type {type(obj).__name__} is not JSON serializable"
        )
    ```
  - Thread `default=_json_default` through EVERY `json.dumps` call in the same code path (typically there is a pair: `old_value=json.dumps(...)` + `new_value=json.dumps(...)`). Forgetting one of the pair is a Session 11-class half-fix; both must use the callback.
  - For nested types (e.g., `dict[str, BaseModel]`, `list[list[BaseModel]]`), `_json_default` will be called recursively by `json.dumps` for each non-serializable subobject. The single isinstance check covers all nesting depths.
  - Re-raise `TypeError` for unhandled types — do NOT silently `str(obj)` or `return None`. Per Critical Rule 4, errors fail loud.
- **Confirmed case (1 of 1 mature in Phase 5 series):**
  - Session 11: `shared/scholar_authority/src/scholar_authority.py:update()` revision_history append previously called `json.dumps(old_value, ensure_ascii=False)` and `json.dumps(new_value, ensure_ascii=False)` with no `default=`. Latent for Sessions 1-10 because no caller passed `evidence_sources: list[ScholarEvidenceSource]` (Pydantic) through `update()`. AC-2 promotion in Session 11 was the first caller — would have crashed on first promotion attempt. Fixed adjacently per "Fix adjacent broken code" override.
- **Audit checklist when adding a new field type to a Pydantic BaseModel that may flow through audit-trail code:**
  - Does ANY code path call `json.dumps(value)` where `value` could carry the new field type? Grep `json.dumps` across the touching modules.
  - If yes: verify the call uses `default=_json_default` (or equivalent BaseModel handler).
  - If no: confirm the field is excluded from audit-trail serialization, OR add the handler defensively.
- **Test pattern for default-handler completeness (lock the contract):**
  - Construct an input where the value being audited is a list of BaseModel instances.
  - Call the function (e.g., `update(canonical_id, {"evidence_sources": [ScholarEvidenceSource(...)]})`).
  - Assert no exception raised AND the persisted revision_history entry contains a JSON-parseable old/new value (use `json.loads(entry.old_value)` to verify round-trip).
- **`default=str` is NOT an acceptable shortcut.** `BaseModel.__str__` returns the model's `repr` form (e.g., `ScholarEvidenceSource(book_id='src_x' evidence_type='colophon' raw_evidence='...')`), which is not JSON, not parseable, and ugly in audit logs. Use `model_dump(mode="json")` for proper round-trip.
- **`mode="json"` (NOT `mode="python"`) on `model_dump()`** is critical — only the `"json"` mode converts non-JSON-native types (datetime, Path, UUID, custom serializers) to JSON-compatible primitives.
