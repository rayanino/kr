# Testing Framework — إطار الاختبار

**Date:** 2026-03-08
**Author:** KR Architect
**Status:** Authoritative — Claude Code reads this to set up test infrastructure.

---

## 1. Framework Decision: DeepEval + pytest

**Choice:** DeepEval (v2.x) on top of pytest for all three test dimensions.

**Why DeepEval over pure pytest + custom scripts:**

- Native pytest integration — tests run with `pytest` or `deepeval test run`, CI-ready from day one.
- Built-in GEval metric allows custom evaluation criteria with no boilerplate. KR needs domain-specific rubrics (author identification accuracy, genre classification correctness, Arabic self-containment), and GEval lets us define these as natural-language criteria evaluated by an LLM judge.
- Native Anthropic, OpenAI, and Mistral model support — no OpenRouter needed. Pass `AnthropicModel`, `GPTModel`, or custom `DeepEvalBaseLLM` wrappers directly to metrics.
- Component-level evaluation via `@observe` decorator traces individual LLM calls inside engines, enabling 5b testing of internal LLM tasks without refactoring engine code.
- ExactMatchMetric and PatternMatchMetric for deterministic 5a checks — no need to write custom assertion logic for string-level validation.
- Test run tracking across iterations (even without Confident AI cloud — local JSON reports suffice).

**What DeepEval does NOT handle (we build ourselves):**

- Arabic text fidelity checks (byte-level diacritics comparison, Unicode normalization verification) — DeepEval's string metrics don't understand Arabic diacritics. Custom pytest fixtures.
- Pydantic schema validation — already built into KR's contracts. Use direct Pydantic `model_validate()` in pytest.
- D-023 metadata pass-through verification — custom check comparing upstream metadata fields to downstream output. Simple dict diff.
- Gold baseline comparison — custom loader that reads gold JSON, runs engine, compares output field-by-field with tolerance rules.

**Installation:**

```bash
pip install deepeval anthropic openai mistralai
# No Confident AI account needed — local evaluation only
# Set DEEPEVAL_TELEMETRY_OPT_OUT=YES to disable telemetry
```

**Environment variables (in `.env`):**

```
ANTHROPIC_API_KEY=...    # For Claude-based evaluation
OPENAI_API_KEY=...       # For GPT-based evaluation + cross-provider 5c
MISTRAL_API_KEY=...      # For Mistral-based evaluation + OCR
DEEPEVAL_TELEMETRY_OPT_OUT=YES
```

---

## 2. Directory Structure

```
engines/{engine}/
├── SPEC.md                          # Behavioral specification
├── contracts.py                     # Pydantic models (input/output schemas)
├── tests/
│   ├── conftest.py                  # Shared fixtures, model setup, helpers
│   ├── test_5a_deterministic.py     # Dimension 5a: schema, text, metadata
│   ├── test_5b_llm_worker.py        # Dimension 5b: internal LLM task quality
│   ├── test_5c_llm_evaluator.py     # Dimension 5c: independent output review
│   ├── gold/                        # Owner-verified expected outputs
│   │   ├── html_export_minimal.json
│   │   └── waraqat_usul.json
│   └── test-results/                # Output from test runs (gitignored)
│       └── {run-id}/
│           ├── 5a_report.json
│           ├── 5b_report.json
│           ├── 5c_report.json
│           └── summary.json
├── src/                             # Engine implementation
└── ...

tests/
├── fixtures/                        # Shared test fixtures (already exist)
│   ├── README.md
│   ├── waraqat_usul/
│   ├── ibn_aqil_alfiyyah/
│   ├── html_export_minimal/
│   ├── alfiyyah_versified/
│   ├── photo_scan_ilm/
│   ├── owner_note/
│   └── mughni_comparative/
├── conftest.py                      # Global conftest: API key loading, shared helpers
├── helpers/
│   ├── arabic.py                    # Arabic text comparison utilities
│   ├── metadata.py                  # D-023 metadata pass-through checker
│   └── gold.py                      # Gold baseline loader + comparator
└── integration/
    └── test_pipeline_{a}_to_{b}.py  # Cross-engine integration tests
```

**Key rule:** Test results are written to `engines/{engine}/tests/test-results/{run-id}/`. The `run-id` is a timestamp: `YYYYMMDD_HHMMSS`. Results are gitignored but the directory structure is committed (with `.gitkeep`). Claude Chat reads these files via kr-evaluate.

---

## 3. Gold Baseline Format

A gold baseline is an owner-verified JSON file representing the correct output of an engine for a specific fixture. It matches the engine's output Pydantic model exactly, with optional tolerance annotations.

### Format

```json
{
  "_meta": {
    "fixture": "html_export_minimal",
    "engine": "source",
    "verified_by": "owner",
    "verified_date": "2026-03-15",
    "notes": "Verified author, title, science, genre. Trust score approximate."
  },
  "_tolerances": {
    "trust_score": { "type": "range", "min": 0.5, "max": 0.8 },
    "confidence.science_scope": { "type": "range", "min": 0.7, "max": 1.0 },
    "description": { "type": "skip", "reason": "LLM-generated, not deterministic" }
  },
  "source_id": "nahw_ibnhisham_qatralnada_a3f2",
  "work_id": "ibnhisham_qatralnada",
  "title_ar": "قطر الندى وبل الصدى",
  "author": {
    "canonical_id": "ibnhisham_761",
    "name_ar": "ابن هشام الأنصاري",
    "death_hijri": 761
  },
  "science_scope": ["nahw"],
  "genre": "matn",
  "structural_format": "prose",
  "trust_tier": "verified",
  "trust_score": 0.72
}
```

### Tolerance Types

| Type | Meaning | Example |
|------|---------|---------|
| `exact` | Must match exactly (default for strings, enums, IDs) | `source_id`, `genre` |
| `range` | Numeric value within [min, max] | `trust_score`, confidence values |
| `skip` | Not compared (LLM-generated, non-deterministic) | `description`, `summary` |
| `set_equal` | List compared as sets (order doesn't matter) | `science_scope` |
| `substring` | Gold value is a substring of actual (for Arabic text) | Rarely used |

### Gold Baseline Comparison Logic

```python
# tests/helpers/gold.py — pseudocode
def compare_to_gold(actual: dict, gold: dict) -> list[GoldMismatch]:
    tolerances = gold.get("_tolerances", {})
    mismatches = []
    for key, expected in gold.items():
        if key.startswith("_"):
            continue
        tolerance = tolerances.get(key, {"type": "exact"})
        if tolerance["type"] == "skip":
            continue
        actual_val = get_nested(actual, key)
        if tolerance["type"] == "range":
            if not (tolerance["min"] <= actual_val <= tolerance["max"]):
                mismatches.append(GoldMismatch(key, expected, actual_val, "out_of_range"))
        elif tolerance["type"] == "set_equal":
            if set(actual_val) != set(expected):
                mismatches.append(GoldMismatch(key, expected, actual_val, "set_mismatch"))
        else:  # exact
            if actual_val != expected:
                mismatches.append(GoldMismatch(key, expected, actual_val, "exact_mismatch"))
    return mismatches
```

### Initial Gold Baselines Required (Source Engine)

The owner must hand-verify these before Step 3 (BUILD):

1. **`html_export_minimal.json`** — The synthetic Shamela-style export. Verify: title, author, science, genre, structural_format. Fastest to create because the fixture is small and the metadata is known.

2. **`waraqat_usul.json`** — Real PDF. Verify: title (متن الورقات), author (الجويني), science (أصول الفقه), genre (matn), trust evaluation. Requires running the source engine once and correcting the output.

**Two gold baselines are the minimum for Step 3 (BUILD).** Additional baselines (ibn_aqil_alfiyyah, owner_note) are added during Step 4 (TEST) iteration.

---

## 4. Dimension 5a — Deterministic Checks

These tests use standard pytest assertions. No LLM calls. No DeepEval metrics. They run in seconds and must all pass before 5b/5c are meaningful.

### Global 5a Checks (all engines)

```python
# tests/conftest.py

import pytest
from pathlib import Path

@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def api_keys():
    """Load API keys from .env — skip tests if missing."""
    from dotenv import load_dotenv
    import os
    load_dotenv()
    keys = {
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "mistral": os.getenv("MISTRAL_API_KEY"),
    }
    return keys
```

```python
# tests/helpers/arabic.py

def verify_arabic_fidelity(original: str, processed: str) -> list[str]:
    """Compare Arabic text character-by-character, flag diacritic loss.
    
    Returns list of issues. Empty list = perfect fidelity.
    Checks:
    - No characters dropped (length comparison)
    - No diacritics stripped (tashkeel: fatha, damma, kasra, shadda, sukun, tanwin)
    - No Unicode normalization changes (NFC vs NFD)
    - No invisible character insertion (zero-width joiner/non-joiner)
    """
    issues = []
    import unicodedata
    
    # Normalize both to NFC for comparison
    orig_nfc = unicodedata.normalize("NFC", original)
    proc_nfc = unicodedata.normalize("NFC", processed)
    
    if orig_nfc != proc_nfc:
        # Find first divergence point
        for i, (a, b) in enumerate(zip(orig_nfc, proc_nfc)):
            if a != b:
                issues.append(
                    f"Char mismatch at position {i}: "
                    f"expected U+{ord(a):04X} ({unicodedata.name(a, '?')}), "
                    f"got U+{ord(b):04X} ({unicodedata.name(b, '?')})"
                )
                break
        if len(orig_nfc) != len(proc_nfc):
            issues.append(
                f"Length mismatch: expected {len(orig_nfc)}, got {len(proc_nfc)}"
            )
    
    # Check diacritics specifically
    TASHKEEL = set("\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0670")
    orig_diacritics = [c for c in orig_nfc if c in TASHKEEL]
    proc_diacritics = [c for c in proc_nfc if c in TASHKEEL]
    if len(orig_diacritics) != len(proc_diacritics):
        issues.append(
            f"Diacritic count mismatch: expected {len(orig_diacritics)}, "
            f"got {len(proc_diacritics)}"
        )
    
    return issues
```

```python
# tests/helpers/metadata.py

def verify_d023_passthrough(upstream_output: dict, downstream_output: dict,
                             expected_passthrough_fields: list[str]) -> list[str]:
    """Verify D-023: all upstream metadata is preserved in downstream output.
    
    Returns list of missing/changed fields. Empty = compliant.
    """
    issues = []
    for field in expected_passthrough_fields:
        upstream_val = get_nested(upstream_output, field)
        downstream_val = get_nested(downstream_output, field)
        if upstream_val is None:
            continue  # field wasn't in upstream, nothing to pass through
        if downstream_val is None:
            issues.append(f"D-023 violation: field '{field}' lost in downstream")
        elif upstream_val != downstream_val:
            issues.append(
                f"D-023 violation: field '{field}' changed from "
                f"'{upstream_val}' to '{downstream_val}'"
            )
    return issues
```

### Source Engine 5a Checks

```python
# engines/source/tests/test_5a_deterministic.py

import pytest
import json
import hashlib
from pathlib import Path
from engines.source.contracts import (
    SourceMetadata, SourceFormat, TrustTier, Genre,
    ErrorCode, SourceRegistryEntry
)

class TestSchemaCompliance:
    """Every metadata record must validate against the Pydantic model."""
    
    def test_metadata_validates(self, source_engine_output):
        """Output must parse as valid SourceMetadata."""
        metadata = SourceMetadata.model_validate(source_engine_output["metadata"])
        assert metadata.source_id is not None
        assert metadata.work_id is not None
    
    def test_required_fields_non_null(self, source_engine_output):
        """Critical fields cannot be None."""
        meta = source_engine_output["metadata"]
        required = ["source_id", "work_id", "title_ar", "source_format",
                     "structural_format", "trust_tier"]
        for field in required:
            assert meta.get(field) is not None, f"Required field '{field}' is null"
    
    def test_confidence_scores_present(self, source_engine_output):
        """Every inferred field must have a confidence score."""
        meta = source_engine_output["metadata"]
        inferred_fields = ["author", "science_scope", "genre", "trust_score"]
        confidences = meta.get("confidence", {})
        for field in inferred_fields:
            assert field in confidences, f"Missing confidence for inferred field '{field}'"
            assert 0.0 <= confidences[field] <= 1.0, f"Confidence for '{field}' out of range"
    
    def test_enum_values_valid(self, source_engine_output):
        """All enum fields contain values from the defined enums."""
        meta = source_engine_output["metadata"]
        assert meta["source_format"] in [e.value for e in SourceFormat]
        assert meta["trust_tier"] in [e.value for e in TrustTier]
        if meta.get("genre"):
            assert meta["genre"] in [e.value for e in Genre]


class TestFreezeIntegrity:
    """Frozen source files must be bit-identical to input."""
    
    def test_frozen_hash_matches(self, source_engine_output, original_file_path):
        """SHA-256 of frozen file matches the hash in metadata."""
        frozen_path = source_engine_output["frozen_path"]
        with open(frozen_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        assert actual_hash == source_engine_output["metadata"]["freeze_hash"]
    
    def test_frozen_matches_original(self, original_file_path, source_engine_output):
        """Frozen file is byte-identical to the original input."""
        frozen_path = source_engine_output["frozen_path"]
        with open(original_file_path, "rb") as orig, open(frozen_path, "rb") as frozen:
            assert orig.read() == frozen.read()


class TestDeduplication:
    """Duplicate detection must work correctly."""
    
    def test_exact_duplicate_rejected(self, source_engine, html_fixture):
        """Ingesting the same file twice raises SRC_DUPLICATE_EXACT."""
        source_engine.ingest(html_fixture)
        result = source_engine.ingest(html_fixture)
        assert result.error_code == ErrorCode.SRC_DUPLICATE_EXACT
    
    def test_different_editions_coexist(self, source_engine, edition_a, edition_b):
        """Two editions of the same work get different source_ids, same work_id."""
        result_a = source_engine.ingest(edition_a)
        result_b = source_engine.ingest(edition_b)
        assert result_a.metadata.source_id != result_b.metadata.source_id
        assert result_a.metadata.work_id == result_b.metadata.work_id


class TestIdentityDeterminism:
    """Same input must produce same IDs every time."""
    
    def test_source_id_deterministic(self, source_engine, html_fixture):
        """Running intake twice on identical input produces identical source_id."""
        result1 = source_engine.ingest(html_fixture, dry_run=True)
        result2 = source_engine.ingest(html_fixture, dry_run=True)
        assert result1.metadata.source_id == result2.metadata.source_id
        assert result1.metadata.work_id == result2.metadata.work_id


class TestErrorHandling:
    """Every error code must be triggerable and produce correct output."""
    
    @pytest.mark.parametrize("error_case,expected_code", [
        ("empty_file", ErrorCode.SRC_EMPTY_INPUT),
        ("unsupported_format", ErrorCode.SRC_UNSUPPORTED_FORMAT),
        ("corrupt_html", ErrorCode.SRC_PARSE_ERROR),
    ])
    def test_error_codes(self, source_engine, error_fixtures, error_case, expected_code):
        """Each error case produces the correct error code."""
        result = source_engine.ingest(error_fixtures[error_case])
        assert result.error_code == expected_code
        assert result.severity is not None


class TestGoldBaseline:
    """Output matches owner-verified gold baselines."""
    
    @pytest.mark.parametrize("fixture_name", ["html_export_minimal", "waraqat_usul"])
    def test_matches_gold(self, source_engine, fixtures_dir, fixture_name):
        """Engine output matches gold baseline within tolerances."""
        from tests.helpers.gold import compare_to_gold
        
        gold_path = Path(f"engines/source/tests/gold/{fixture_name}.json")
        if not gold_path.exists():
            pytest.skip(f"Gold baseline not yet created: {fixture_name}")
        
        gold = json.loads(gold_path.read_text())
        result = source_engine.ingest(fixtures_dir / fixture_name)
        mismatches = compare_to_gold(result.metadata.model_dump(), gold)
        
        assert len(mismatches) == 0, (
            f"Gold baseline mismatches:\n" +
            "\n".join(f"  {m}" for m in mismatches)
        )
```

---

## 5. Dimension 5b — LLM-Worker Quality

5b tests evaluate whether the LLM calls INSIDE the engine produce correct results. These use DeepEval's GEval metric with custom criteria specific to each LLM task.

### Model Selection for 5b

5b uses the SAME model the engine uses internally. If the source engine's metadata enrichment uses Claude Sonnet, 5b tests are also evaluated with Claude Sonnet. The point is to test whether the engine's LLM integration works correctly — not to cross-validate with a different model (that's 5c's job).

### Source Engine LLM Tasks

The source engine makes LLM calls for three tasks during metadata enrichment:

| Task | Input | Expected Output | Risk |
|------|-------|-----------------|------|
| Science classification | Title + author + first 2000 chars | Science enum value(s) | Medium — most books clearly belong to one science |
| Author identification | Title + metadata hints + text sample | Author canonical_id + confidence | High — classical texts often misattribute to editors |
| Genre/layer detection | Structural analysis of text | Genre enum + genre chain | Medium — sharh/hashiyah detection is subtle |

### Source Engine 5b Tests

```python
# engines/source/tests/test_5b_llm_worker.py

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.models import AnthropicModel

# Use the same model the engine uses internally
engine_model = AnthropicModel(model="claude-sonnet-4-20250514", temperature=0)

class TestScienceClassification:
    """Does the engine's LLM correctly classify the Islamic science?"""
    
    SCIENCE_METRIC = GEval(
        name="ScienceClassificationAccuracy",
        criteria=(
            "The 'actual output' is a science classification for an Arabic Islamic text. "
            "The 'expected output' is the correct classification. "
            "Evaluate whether the classification is correct. "
            "Accept both exact matches and reasonable broader categories "
            "(e.g., 'nahw_wa_sarf' is acceptable for a pure nahw text). "
            "WRONG means a completely different science (e.g., fiqh for a nahw text)."
        ),
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.7,
        model=engine_model,
    )
    
    @pytest.mark.parametrize("fixture_name,expected_science", [
        ("waraqat_usul", "usul_al_fiqh"),
        ("ibn_aqil_alfiyyah", "nahw"),
        ("alfiyyah_versified", "nahw"),
        ("mughni_comparative", "fiqh"),
        ("owner_note", "fiqh"),  # ruling on photography
    ])
    def test_science_classification(self, source_engine, fixtures_dir,
                                     fixture_name, expected_science):
        result = source_engine.ingest(fixtures_dir / fixture_name)
        test_case = LLMTestCase(
            input=f"Classify the Islamic science of: {result.metadata.title_ar}",
            actual_output=str(result.metadata.science_scope),
            expected_output=expected_science,
        )
        assert_test(test_case, [self.SCIENCE_METRIC])


class TestAuthorIdentification:
    """Does the engine's LLM correctly identify the author?"""
    
    AUTHOR_METRIC = GEval(
        name="AuthorIdentificationAccuracy",
        criteria=(
            "The 'actual output' is an author identification for an Arabic Islamic text. "
            "The 'expected output' is the correct author. "
            "CRITICAL: The author is the ORIGINAL author of the work, NOT the muhaqiq "
            "(critical editor) or commentator. For sharh texts, the author is the "
            "commentator (e.g., Ibn Aqil for شرح ابن عقيل), not the matn author "
            "(e.g., NOT Ibn Malik). "
            "Accept name variations (e.g., 'ابن عقيل' and 'بهاء الدين ابن عقيل' are the same). "
            "WRONG means a completely different person."
        ),
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.7,
        model=engine_model,
    )
    
    @pytest.mark.parametrize("fixture_name,expected_author", [
        ("waraqat_usul", "إمام الحرمين الجويني"),
        ("ibn_aqil_alfiyyah", "ابن عقيل"),
        ("alfiyyah_versified", "ابن مالك"),
        ("owner_note", "owner"),
    ])
    def test_author_identification(self, source_engine, fixtures_dir,
                                    fixture_name, expected_author):
        result = source_engine.ingest(fixtures_dir / fixture_name)
        actual_author = result.metadata.author.name_ar if result.metadata.author else "unknown"
        test_case = LLMTestCase(
            input=f"Identify the author of: {result.metadata.title_ar}",
            actual_output=actual_author,
            expected_output=expected_author,
        )
        assert_test(test_case, [self.AUTHOR_METRIC])


class TestGenreDetection:
    """Does the engine's LLM correctly detect genre and genre chains?"""
    
    GENRE_METRIC = GEval(
        name="GenreDetectionAccuracy",
        criteria=(
            "The 'actual output' is a genre classification for an Arabic Islamic text. "
            "The 'expected output' is the correct genre. "
            "For sharh (commentary) texts, also verify the genre chain correctly "
            "identifies the base work. "
            "Accept: matn, sharh, hashiyah, taqrirat, nazm, mukhtasar, mawsuah."
        ),
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.7,
        model=engine_model,
    )
    
    @pytest.mark.parametrize("fixture_name,expected_genre", [
        ("waraqat_usul", "matn"),
        ("ibn_aqil_alfiyyah", "sharh"),
        ("alfiyyah_versified", "nazm"),
    ])
    def test_genre_detection(self, source_engine, fixtures_dir,
                              fixture_name, expected_genre):
        result = source_engine.ingest(fixtures_dir / fixture_name)
        test_case = LLMTestCase(
            input=f"Classify the genre of: {result.metadata.title_ar}",
            actual_output=str(result.metadata.genre),
            expected_output=expected_genre,
        )
        assert_test(test_case, [self.GENRE_METRIC])
```

### 5b Accuracy Threshold

A 5b test passes when the GEval score is ≥ 0.7 (the threshold parameter). This means the evaluation LLM considers the engine's LLM output "mostly correct" for that task. Across all 5b tests for an engine:

- **≥90% pass rate:** Engine's LLM integration is solid. Proceed.
- **80-90% pass rate:** Investigate failures. Likely prompt engineering needed.
- **<80% pass rate:** Fundamental issue — model choice, task design, or context insufficient.

---

## 6. Dimension 5c — LLM-Evaluator Assessment

5c is an independent review of the engine's complete output by a DIFFERENT model family. This catches errors that the engine's own self-validation missed.

### Model Selection for 5c (Cross-Provider Rule)

The evaluator model MUST be from a different provider than the engine's internal LLM. This prevents self-model bias.

| Engine's internal LLM | 5c evaluator model |
|------------------------|--------------------|
| Claude (Anthropic) | GPT-4.1 (OpenAI) |
| GPT (OpenAI) | Claude Sonnet (Anthropic) |
| Mistral | Claude Sonnet (Anthropic) |

The source engine uses Claude for metadata enrichment → 5c uses GPT-4.1.

### Source Engine 5c Tests

```python
# engines/source/tests/test_5c_llm_evaluator.py

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.models import GPTModel

# Cross-provider: source engine uses Claude, so 5c uses GPT
evaluator_model = GPTModel(model="gpt-4.1", temperature=0)


class TestMetadataCorrectness:
    """Independent model reviews the engine's complete metadata output."""
    
    METADATA_REVIEW = GEval(
        name="SourceMetadataCorrectness",
        criteria=(
            "You are an expert in classical Islamic texts and bibliography. "
            "Review this source metadata record produced by an automated system. "
            "The 'input' contains the source text sample and raw file metadata. "
            "The 'actual output' contains the system's metadata extraction. "
            "Evaluate whether ALL of the following are correct: "
            "1. Author identification (is this the right person?) "
            "2. Science classification (does this book belong to this field?) "
            "3. Genre classification (matn/sharh/hashiyah/nazm/etc.) "
            "4. Title accuracy "
            "5. If it's a sharh, is the base work correctly identified? "
            "Score 1.0 if all fields are correct. "
            "Score 0.5 if minor issues (e.g., science is broader than ideal). "
            "Score 0.0 if any CRITICAL field is wrong (wrong author, wrong genre)."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=0.5,
        model=evaluator_model,
    )
    
    @pytest.mark.parametrize("fixture_name", [
        "html_export_minimal",
        "waraqat_usul",
        "ibn_aqil_alfiyyah",
        "alfiyyah_versified",
        "owner_note",
    ])
    def test_metadata_independent_review(self, source_engine, fixtures_dir, fixture_name):
        """A different LLM reviews the source engine's metadata output."""
        result = source_engine.ingest(fixtures_dir / fixture_name)
        
        # Build context: give the evaluator the raw source info
        # (NOT the engine's metadata — let it judge independently)
        source_sample = result.text_sample[:3000]  # first 3000 chars
        
        test_case = LLMTestCase(
            input=(
                f"Source file: {fixture_name}\n"
                f"Text sample (first 3000 chars):\n{source_sample}"
            ),
            actual_output=result.metadata.model_dump_json(indent=2),
        )
        assert_test(test_case, [self.METADATA_REVIEW])


class TestTrustAssessment:
    """Independent review of trustworthiness scoring."""
    
    TRUST_REVIEW = GEval(
        name="TrustAssessmentReasonableness",
        criteria=(
            "Review the trustworthiness assessment for this Islamic text source. "
            "The 'input' describes the source (title, author, format, tahqiq info). "
            "The 'actual output' is the system's trust assessment (tier + score + factors). "
            "A 'verified' source should have: known author, published by a recognized publisher, "
            "critical edition with named muhaqiq, or owner-verified. "
            "A 'flagged' source should have: unknown author, suspicious provenance, "
            "no editorial apparatus, poor text quality. "
            "Score 1.0 if the tier is appropriate. "
            "Score 0.5 if the tier is debatable but defensible. "
            "Score 0.0 if the tier is clearly wrong."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=0.5,
        model=evaluator_model,
    )
```

### 5c Result Tracking

Every 5c test produces a structured finding:

```json
{
  "fixture": "ibn_aqil_alfiyyah",
  "evaluator_model": "gpt-4.1",
  "metric": "SourceMetadataCorrectness",
  "score": 0.45,
  "reason": "Author identified as Ibn Aqil (correct for sharh) but genre chain missing base work reference to Alfiyyah Ibn Malik",
  "verdict": "ISSUE_FOUND",
  "self_validation_caught": false
}
```

These findings feed directly into kr-evaluate's categorization workflow. Over time, tracking `self_validation_caught: false` across engines builds the evidence for or against adding inter-engine LLM gates to the production pipeline.

---

## 7. Test Result Storage Format

Each test run writes results to `engines/{engine}/tests/test-results/{run-id}/`.

### summary.json

```json
{
  "run_id": "20260315_143022",
  "engine": "source",
  "timestamp": "2026-03-15T14:30:22Z",
  "fixtures_tested": ["html_export_minimal", "waraqat_usul"],
  "dimensions": {
    "5a": {
      "total": 24,
      "passed": 22,
      "failed": 2,
      "skipped": 0,
      "failures": [
        {
          "test": "test_confidence_scores_present[waraqat_usul]",
          "error": "Missing confidence for 'genre'",
          "category": null
        }
      ]
    },
    "5b": {
      "total": 10,
      "passed": 9,
      "failed": 1,
      "accuracy": 0.90,
      "failures": [
        {
          "test": "test_author_identification[ibn_aqil_alfiyyah]",
          "score": 0.3,
          "reason": "Identified muhaqiq as author instead of commentator",
          "category": null
        }
      ]
    },
    "5c": {
      "total": 5,
      "issues_found": 1,
      "details": [
        {
          "fixture": "ibn_aqil_alfiyyah",
          "metric": "SourceMetadataCorrectness",
          "score": 0.45,
          "reason": "Genre chain incomplete",
          "self_validation_caught": false
        }
      ]
    }
  },
  "trust_level": 1,
  "trust_level_explanation": "5a has failures — Level 1 not reached"
}
```

The `category` field is null when Claude Code writes results; it gets filled in by the owner + Claude Chat during kr-evaluate analysis (one of: ENGINE_BUG, LLM_QUALITY, SPEC_GAP, DATA_ISSUE, UPSTREAM_ERROR, EVALUATOR_NOISE).

### conftest.py for result writing

```python
# engines/source/tests/conftest.py

import pytest
import json
from datetime import datetime
from pathlib import Path

class TestResultCollector:
    """Collects test results during a run and writes summary."""
    
    def __init__(self):
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {"5a": [], "5b": [], "5c": []}
    
    def record(self, dimension: str, test_name: str, passed: bool, **kwargs):
        self.results[dimension].append({
            "test": test_name,
            "passed": passed,
            **kwargs
        })
    
    def write(self, engine: str):
        output_dir = Path(f"engines/{engine}/tests/test-results/{self.run_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        summary = self._build_summary(engine)
        (output_dir / "summary.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False)
        )
        
        for dim in ["5a", "5b", "5c"]:
            (output_dir / f"{dim}_report.json").write_text(
                json.dumps(self.results[dim], indent=2, ensure_ascii=False)
            )
    
    def _build_summary(self, engine: str) -> dict:
        # ... build summary dict from self.results
        pass

@pytest.fixture(scope="session")
def result_collector():
    collector = TestResultCollector()
    yield collector
    collector.write("source")
```

---

## 8. Trust Graduation Thresholds

These are the measurable criteria for each trust level, adapted from ENGINE_PROTOCOL.md:

| Level | Name | Criteria | Measured By |
|-------|------|----------|-------------|
| 0 | Runs | Engine runs without crashing on ≥2 test fixtures | pytest exit code 0 (ignoring expected failures) |
| 1 | Schema-valid | ALL 5a deterministic checks pass on ≥2 fixtures | `summary.json → dimensions.5a.failed == 0` |
| 2 | LLM-accurate | 5b pass rate ≥ 90% across all fixtures | `summary.json → dimensions.5b.accuracy >= 0.90` |
| 3 | Independently-verified | 5c finds zero errors that self-validation missed, on ≥3 fixtures | `summary.json → dimensions.5c.issues_found == 0` where `self_validation_caught == false` |
| 4 | Owner-approved | Owner has reviewed and approved output for their real sources | Manual — owner commits an approval record |

**Minimum to proceed to next engine:** Level 2. This means all deterministic checks pass AND the engine's internal LLM calls are ≥90% accurate.

**Level 3 is aspirational for early engines.** The inter-engine gate decision depends on accumulating 5c data across 3-4 engines. If 5c consistently finds errors self-validation missed, we add inter-engine LLM gates. If not, 5c becomes testing-only.

**Level 4 is per-source, not per-engine.** The engine reaches Level 4 when the owner has approved its output on sources they actually study from. This happens during Step 4 (TEST) iteration, not as a one-time gate.

---

## 9. Running Tests

### Full run (all dimensions)

```bash
cd engines/source
pytest tests/ -v --tb=short 2>&1 | tee tests/test-results/latest.log

# Or with DeepEval's runner (includes metric tracking):
deepeval test run tests/ -v
```

### 5a only (fast, no API calls)

```bash
pytest tests/test_5a_deterministic.py -v
```

### 5b only (requires API keys)

```bash
pytest tests/test_5b_llm_worker.py -v -k "science or author or genre"
```

### 5c only (requires API keys, cross-provider)

```bash
pytest tests/test_5c_llm_evaluator.py -v
```

### Specific fixture

```bash
pytest tests/ -v -k "waraqat_usul"
```

### Cost Estimate Per Run

| Dimension | API calls | Approx cost per fixture |
|-----------|-----------|------------------------|
| 5a | 0 | $0.00 |
| 5b | 3-5 (one per LLM task) | ~$0.02 |
| 5c | 2-3 (one per evaluation metric) | ~$0.05 |

Full source engine test run on 5 fixtures: ~$0.35. Negligible.

---

## 10. Per-Engine Test Templates

Each engine's test suite follows the same 5a/5b/5c structure. Here is what each engine must test:

### Source Engine (detailed above in §4-§6)

- 5a: Schema, freeze integrity, deduplication, identity determinism, error codes, gold baselines
- 5b: Science classification, author identification, genre detection
- 5c: Independent metadata review, trust assessment review

### Normalization Engine

- 5a: Output schema validates. Arabic text preserved (byte-level fidelity check). Page references survive normalization. Content completeness (no paragraphs dropped). Structural annotations present.
- 5b: Layer detection (matn vs sharh vs hashiyah). Footnote extraction accuracy. Header hierarchy recognition.
- 5c: Independent review of normalized output — "does this normalization accurately represent the original source?"

### Passaging Engine

- 5a: Every unit in exactly one passage (coverage invariant). Passage ordering matches source order. Text preservation. Passage metadata complete.
- 5b: Boundary quality — "is each passage a complete, coherent unit?" Topic coherence scoring per passage.
- 5c: Independent passage review — "would you split this text differently?"

### Atomization Engine

- 5a: Every character in exactly one atom (coverage invariant). Atom ordering. Scholarly function enum values valid. Layer attribution consistent with source metadata.
- 5b: Atom boundary accuracy. Scholarly function classification (opinion vs evidence vs definition vs example). Layer attribution (matn vs sharh vs hashiyah).
- 5c: Independent atom review — "are these atomic units correctly identified and classified?"

### Excerpting Engine

- 5a: Every excerpt traces to source atoms. Self-containment metadata present. Attribution fields complete. D-023 metadata preserved.
- 5b: Self-containment evaluation. Attribution detection accuracy. Implicit reference resolution.
- 5c: Independent excerpt review — "is this self-contained? Is the attribution correct?" **This engine has the highest corruption risk — 5c is essential.**

### Taxonomy Engine

- 5a: Every placed excerpt has a valid taxonomy leaf. Tree structure valid (no cycles, no orphans). Placement metadata complete.
- 5b: Placement accuracy — "does this excerpt belong in this taxonomy leaf?"
- 5c: Independent placement review with full taxonomy tree visible.

### Synthesis Engine

- 5a: Every claim tagged with grounding_type. Every source_grounded claim cites a real excerpt. Temporal ordering. Schema compliance.
- 5b: Entry quality (scholarly narrative vs flat compilation). Arabic language quality. Metadata utilization (does the entry use teacher-student chains, school context?).
- 5c: **Full multi-model panel (3 judges).** Attribution accuracy. Completeness. Tone and scholarly quality. Faithfulness check (SelfCheckGPT: run synthesis 3x, check claim consistency).

---

## 11. Integration Tests

Integration tests verify the contract between adjacent engines.

```
tests/integration/
├── test_source_to_normalization.py
├── test_normalization_to_passaging.py
├── test_passaging_to_atomization.py
├── test_atomization_to_excerpting.py
├── test_excerpting_to_taxonomy.py
└── test_taxonomy_to_synthesis.py
```

Each integration test:
1. Runs engine A on a fixture.
2. Feeds engine A's output to engine B.
3. Verifies engine B accepts the input without errors.
4. Verifies D-023 metadata pass-through from A to B.

Integration tests are 5a-only (deterministic). They run with no API calls if the engines have cached outputs from previous runs.

Build integration tests incrementally — `test_source_to_normalization.py` is created when both the source and normalization engines are built. Others are added as engines are built.

---

## 12. Implementation Notes for Claude Code

**When setting up test infrastructure for an engine:**

1. Install dependencies: `pip install deepeval anthropic openai mistralai python-dotenv`
2. Create the directory structure from §2.
3. Copy the global conftest and helpers from `tests/`.
4. Write `engines/{engine}/tests/conftest.py` with engine-specific fixtures.
5. Implement 5a tests first — these require no API calls and validate basic functionality.
6. Implement 5b tests next — these test the engine's LLM integration.
7. Implement 5c tests last — these require cross-provider API keys.
8. Create `.gitignore` in `test-results/` to exclude run data but keep directory structure.
9. Verify all tests can be run with `pytest engines/{engine}/tests/ -v`.

**When running tests:**

1. Run 5a first. If 5a fails, 5b and 5c results are meaningless.
2. Run 5b. If 5b shows <80% accuracy, focus on prompt engineering before running 5c.
3. Run 5c. Record findings in `test-results/` for kr-evaluate analysis.
4. Write `summary.json` with the trust level assessment.

**Cost discipline:** 5b and 5c make API calls. During development, run 5a continuously (free). Run 5b/5c only when 5a passes and you're ready for evaluation. Use `pytest -k "5a"` to run only deterministic checks during iteration.
