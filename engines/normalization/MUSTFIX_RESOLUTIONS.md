# MUST-FIX Resolution Designs — Normalization Engine

**Date:** 2026-03-18
**Source:** `reference/SPEC_INTEGRITY_AUDIT_NORMALIZATION.md` — 3 MUST-FIX items

---

## MF-1: DivisionNode Field Count Mismatch — RESOLVED

**Problem:** SPEC §4.A.6 line 568 lists 14 fields. Concrete example (line 604) shows all 14. `contracts.py` `DivisionNode` has 7 fields. An implementer following the SPEC would fail at runtime.

**Decision:** Expand from 7 to 9 fields. Add `div_id` and `division_type`. Drop 5 fields that are either redundant (derivable from tree structure) or not consumed downstream.

### Fields added (2)

**`div_id: str`** — Stable identifier for cross-engine traceability. Format: `div_{source_id}_{depth}_{index}` (matches passaging engine's expected format — SPEC §2 line 28, contracts.py line 135). Examples: `div_src_00147_1_000`, `div_src_00147_2_005`. If normalization provides `div_id`, the passaging engine uses it directly instead of generating its own.

**`division_type: Optional[DivisionType]`** — Parsed structural type from heading keyword. New `DivisionType` enum with values: `كتاب`, `باب`, `فصل`, `مبحث`, `مطلب`, `فائدة`, `تنبيه`, `قاعدة`, `خاتمة`, `مقدمة`, `implicit`, `volume`, `root`. Enables hierarchy inference (§4.A.6 line 583: `كتاب > باب > فصل > مبحث > مطلب`) without re-parsing heading text. `None` when the heading doesn't match any known keyword.

### Fields NOT added (5) — with rationale

| SPEC Field | Why Dropped |
|---|---|
| `parent_div_id` | Derivable from tree traversal. Pure denormalization. Passaging doesn't read it. |
| `child_div_ids` | IS the `children` array. Redundant. Passaging doesn't read it. |
| `page_hint_start` / `page_hint_end` | Derivable from `start_unit_index` + content unit `physical_page`. Passaging doesn't read them. |
| `digestible` | Passaging computes this itself from `content_flags` (SPEC §2 line 28). Normalization shouldn't pre-compute what passaging owns. |
| `editor_inserted` | Detection requires non-trivial analysis. Not referenced in any processing rule or downstream engine. Deferred until detection logic is proven. |

### Updated Pydantic model

```python
class DivisionType(str, Enum):
    """Arabic structural division types (SPEC §4.A.6 hierarchy)."""
    KITAB = "كتاب"
    BAB = "باب"
    FASL = "فصل"
    MABHATH = "مبحث"
    MATLAB = "مطلب"
    FAIDAH = "فائدة"
    TANBIH = "تنبيه"
    QAIDAH = "قاعدة"
    KHATIMAH = "خاتمة"
    MUQADDIMAH = "مقدمة"
    IMPLICIT = "implicit"
    VOLUME = "volume"
    ROOT = "root"

class DivisionNode(BaseModel):
    """A node in the division tree (SPEC §4.A.6, manifest.division_tree)."""
    div_id: str = Field(description="Format: div_{source_id}_{depth}_{index}")
    division_type: Optional[DivisionType] = Field(
        None, description="Parsed from heading keyword. None if no keyword match."
    )
    heading_text: str
    heading_level: int = Field(ge=1, le=10)
    start_unit_index: int = Field(ge=0)
    end_unit_index: int = Field(ge=0, description="Inclusive end")
    detection_method: HeadingDetectionMethod
    confidence: HeadingConfidence
    children: list[DivisionNode] = Field(default_factory=list)
```

### Files to modify

1. **`engines/normalization/contracts.py`** — Add `DivisionType` enum, expand `DivisionNode` to 9 fields.
2. **`engines/normalization/SPEC.md` §4.A.6 line 568** — Update field list to match 9-field model. Change `title` → `heading_text`, `level` → `heading_level`. Remove `parent_div_id`, `child_div_ids`, `page_hint_start`, `page_hint_end`, `digestible`, `editor_inserted`. Add `div_id` format and `division_type`.
3. **`engines/normalization/SPEC.md` §4.A.6 lines 604-620** — Update concrete example JSON to match 9-field model.
4. **`engines/passaging/SPEC.md` §2 line 28** — Update to: "If normalization provides `div_id`, the passaging engine uses it directly. Otherwise, it generates `div_{source_id}_{depth}_{index}` during tree traversal."

### Ripple check

- `engines/passaging/contracts.py` `DivisionPathEntry.div_id` — No model change. Passaging populates from normalization's `div_id`.
- No other engine reads the division tree directly.
- Verified: the field name changes (`title`→`heading_text`, `level`→`heading_level`) align with what passaging already expects (SPEC §2 line 28 uses `heading_text` and `heading_level`).

---

## MF-2: LayerMapEntry Field Name Mismatch — RESOLVED

**Problem:** `contracts.py` has `detection_confidence`; passaging SPEC §2 line 30 expects `confidence` and `markers`.

**Resolution:** Mechanical rename + field addition.

### Updated Pydantic model

```python
class LayerMapEntry(BaseModel):
    """One layer in the source's multi-layer composition (SPEC §3 manifest)."""
    layer_type: LayerType
    author_canonical_id: Optional[str] = Field(
        None, description="sch_XXXXX reference; null if author unknown"
    )
    author_name_arabic: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)  # RENAMED from detection_confidence
    markers: list[str] = Field(
        default_factory=list,
        description="Layer detection markers found (e.g., 'bold', 'brackets', 'قال المصنف')"
    )
```

### Files to modify

1. **`engines/normalization/contracts.py`** — Rename `detection_confidence` → `confidence`, add `markers` field.

### Ripple check

- `LayerMapEntry` is only defined in normalization `contracts.py` (line 484) and referenced in `NormalizedManifest.layer_map` (line 652).
- Passaging imports `LayerType` from normalization but reads `LayerMapEntry` from JSON — the field rename changes the JSON key, which is exactly what passaging expects.
- Source engine does NOT produce or consume `LayerMapEntry`.
- No other engine references `LayerMapEntry`.

---

## MF-3: vocalization_level Upstream Dependency — DEFERRED

**Problem:** §5 check 14 references `vocalization_level` on `SourceMetadata`, which the source engine doesn't produce.

**Why deferred:** Check 14 is "OCR diacritics hallucination check (OCR sources only)." OCR normalizers are deferred. The field is referenced ONLY in §5 check 14 (line 1518) and §7 error code `NORM_OCR_DIACRITICS_HALLUCINATION` (line 1593). No core processing rule uses it.

**When resolved:** When the OCR normalizer (§4.A.4) is built. Two options remain valid: (1) add `vocalization_level` to `SourceMetadata`, (2) infer it from OCR output during normalization.
