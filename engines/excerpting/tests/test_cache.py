"""Tests for input-based LLM result caching with validation gate.

Tests compute_cache_key determinism, CacheManager save/load,
cache poisoning prevention via validate_before_caching, and
cache key sensitivity to all input parameters.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from engines.excerpting.contracts import (
    ClassificationResult,
    ClassifiedSegment,
    EnrichmentResult,
    ExtractionResult,
    ScholarlyFunction,
    SelfContainmentLevel,
    TeachingUnit,
    VerificationResult,
    UnitEnrichment,
)
from engines.excerpting.src.cache import (
    CacheManager,
    compute_cache_key,
    validate_before_caching,
)


# ═══════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture()
def cache_dir(tmp_path: Path) -> Path:
    """Return a fresh temporary cache directory."""
    d = tmp_path / "cache"
    d.mkdir()
    return d


@pytest.fixture()
def cache(cache_dir: Path) -> CacheManager:
    """Return a CacheManager pointed at a fresh temp directory."""
    return CacheManager(cache_dir)


def _make_classification_result(n_segments: int = 2) -> ClassificationResult:
    """Build a valid ClassificationResult with n segments."""
    segments = [
        ClassifiedSegment(
            segment_index=i,
            start_word=i * 10,
            end_word=i * 10 + 9,
            text_snippet="بسم الله الرحمن الرحيم الحمد"[:50],
            scholarly_function=ScholarlyFunction.DEFINITION,
            confidence=0.9,
        )
        for i in range(n_segments)
    ]
    return ClassificationResult(
        segments=segments,
        total_segments=n_segments,
    )


def _make_extraction_result(n_units: int = 1) -> ExtractionResult:
    """Build a valid ExtractionResult with n teaching units."""
    units = [
        TeachingUnit(
            unit_index=i,
            segment_indices=[i],
            start_word=i * 10,
            end_word=i * 10 + 9,
            text_snippet="بسم الله الرحمن الرحيم الحمد لله رب العالمين"[:80],
            primary_function=ScholarlyFunction.DEFINITION,
            secondary_functions=[],
            description_arabic="وصف عربي قصير للاختبار يتضمن عدة كلمات",
            self_containment=SelfContainmentLevel.FULL,
            self_containment_notes=None,
        )
        for i in range(n_units)
    ]
    return ExtractionResult(
        teaching_units=units,
        total_units=n_units,
    )


def _make_enrichment_result(n_enrichments: int = 1) -> EnrichmentResult:
    """Build a valid EnrichmentResult with n enrichments."""
    enrichments = [
        UnitEnrichment(
            unit_index=i,
            excerpt_topic=["اختبار"],
            school=None,
            school_confidence=None,
            resolved_scholars=[],
            takhrij_data=[],
            terminology_variants=[],
            cross_references=[],
            context_hint=None,
        )
        for i in range(n_enrichments)
    ]
    return EnrichmentResult(
        enrichments=enrichments,
        total_units=n_enrichments,
    )


# ═══════════════════════════════════════════════════════════════════
# compute_cache_key tests
# ═══════════════════════════════════════════════════════════════════


class TestComputeCacheKey:
    """Tests for compute_cache_key determinism and sensitivity."""

    _BASE_ARGS: dict[str, Any] = {
        "phase": "classify",
        "system_message": "You are an expert.",
        "user_message": "بسم الله الرحمن الرحيم",
        "model": "anthropic/claude-opus-4.6",
        "temperature": 0.0,
        "max_tokens": 8192,
    }

    def test_deterministic(self) -> None:
        """Same inputs produce same key."""
        key1 = compute_cache_key(**self._BASE_ARGS)
        key2 = compute_cache_key(**self._BASE_ARGS)
        assert key1 == key2
        assert len(key1) == 16  # 16 hex chars

    def test_changes_on_phase(self) -> None:
        """Changing phase changes key."""
        key1 = compute_cache_key(**self._BASE_ARGS)
        key2 = compute_cache_key(**{**self._BASE_ARGS, "phase": "group"})
        assert key1 != key2

    def test_changes_on_system_message(self) -> None:
        """Changing system prompt changes key."""
        key1 = compute_cache_key(**self._BASE_ARGS)
        key2 = compute_cache_key(
            **{**self._BASE_ARGS, "system_message": "Different prompt."}
        )
        assert key1 != key2

    def test_changes_on_user_message(self) -> None:
        """Changing user message (source text) changes key."""
        key1 = compute_cache_key(**self._BASE_ARGS)
        key2 = compute_cache_key(
            **{**self._BASE_ARGS, "user_message": "مختلف"}
        )
        assert key1 != key2

    def test_changes_on_model(self) -> None:
        """Different model name changes key."""
        key1 = compute_cache_key(**self._BASE_ARGS)
        key2 = compute_cache_key(
            **{**self._BASE_ARGS, "model": "openai/gpt-4.1"}
        )
        assert key1 != key2

    def test_changes_on_temperature(self) -> None:
        """Changing temperature changes key."""
        key1 = compute_cache_key(**self._BASE_ARGS)
        key2 = compute_cache_key(
            **{**self._BASE_ARGS, "temperature": 0.3}
        )
        assert key1 != key2

    def test_changes_on_max_tokens(self) -> None:
        """Changing max_tokens changes key."""
        key1 = compute_cache_key(**self._BASE_ARGS)
        key2 = compute_cache_key(
            **{**self._BASE_ARGS, "max_tokens": 32768}
        )
        assert key1 != key2

    def test_changes_on_prompt_edit(self) -> None:
        """Editing system prompt content changes key (auto-invalidation)."""
        original = "Classify each sentence in this text."
        edited = "Classify each sentence in this Arabic text."
        key1 = compute_cache_key(
            **{**self._BASE_ARGS, "system_message": original}
        )
        key2 = compute_cache_key(
            **{**self._BASE_ARGS, "system_message": edited}
        )
        assert key1 != key2


# ═══════════════════════════════════════════════════════════════════
# CacheManager tests
# ═══════════════════════════════════════════════════════════════════


class TestCacheManager:
    """Tests for CacheManager save/load and error handling."""

    def test_miss_returns_none(self, cache: CacheManager) -> None:
        """Load from empty cache returns None."""
        result = cache.load("classify", "nonexistent_key", ClassificationResult)
        assert result is None

    def test_save_and_load_classification(self, cache: CacheManager) -> None:
        """Save a ClassificationResult, load it back."""
        cr = _make_classification_result(n_segments=3)
        cache.save("classify", "abc123", "chunk_1", "model_a", cr)
        loaded = cache.load("classify", "abc123", ClassificationResult)
        assert loaded is not None
        assert len(loaded.segments) == 3
        assert loaded.segments[0].scholarly_function == ScholarlyFunction.DEFINITION

    def test_save_and_load_extraction(self, cache: CacheManager) -> None:
        """Save an ExtractionResult, load it back."""
        er = _make_extraction_result(n_units=2)
        cache.save("group", "def456", "chunk_2", "model_b", er)
        loaded = cache.load("group", "def456", ExtractionResult)
        assert loaded is not None
        assert len(loaded.teaching_units) == 2

    def test_save_and_load_enrichment(self, cache: CacheManager) -> None:
        """Save an EnrichmentResult, load it back."""
        enr = _make_enrichment_result(n_enrichments=2)
        cache.save("enrich", "ghi789", "chunk_3", "model_c", enr)
        loaded = cache.load("enrich", "ghi789", EnrichmentResult)
        assert loaded is not None
        assert len(loaded.enrichments) == 2

    def test_save_rejects_empty_enrichment_result(self, cache: CacheManager, cache_dir: Path) -> None:
        """Poisoned empty enrichment results are not written to cache."""
        enr = EnrichmentResult(enrichments=[], total_units=0)
        cache.save("enrich", "empty_enrich", "chunk_3", "model_c", enr)
        assert not (cache_dir / "enrich" / "empty_enrich.json").exists()

    def test_load_rejects_empty_enrichment_result(self, cache: CacheManager, cache_dir: Path) -> None:
        """Poisoned empty enrichment entries are rejected on load."""
        phase_dir = cache_dir / "enrich"
        phase_dir.mkdir(parents=True, exist_ok=True)
        entry_path = phase_dir / "empty_enrich.json"
        entry_path.write_text(
            json.dumps(
                {
                    "cache_key": "empty_enrich",
                    "chunk_id": "chunk_3",
                    "model": "model_c",
                    "timestamp": "2026-04-02T00:00:00+00:00",
                    "result": {"enrichments": [], "total_units": 0},
                }
            ),
            encoding="utf-8",
        )
        loaded = cache.load("enrich", "empty_enrich", EnrichmentResult)
        assert loaded is None

    def test_save_rejects_empty_verification_result(self, cache: CacheManager, cache_dir: Path) -> None:
        """Poisoned empty verification results are not written to cache."""
        vr = VerificationResult(items=[])
        cache.save("verify", "empty_verify", "chunk_4", "model_d", vr)
        assert not (cache_dir / "verify" / "empty_verify.json").exists()

    def test_load_rejects_empty_verification_result(self, cache: CacheManager, cache_dir: Path) -> None:
        """Poisoned empty verification entries are rejected on load."""
        phase_dir = cache_dir / "verify"
        phase_dir.mkdir(parents=True, exist_ok=True)
        entry_path = phase_dir / "empty_verify.json"
        entry_path.write_text(
            json.dumps(
                {
                    "cache_key": "empty_verify",
                    "chunk_id": "chunk_4",
                    "model": "model_d",
                    "timestamp": "2026-04-02T00:00:00+00:00",
                    "result": {"items": []},
                }
            ),
            encoding="utf-8",
        )
        loaded = cache.load("verify", "empty_verify", VerificationResult)
        assert loaded is None

    def test_corrupt_file_returns_none(
        self, cache: CacheManager, cache_dir: Path
    ) -> None:
        """Write garbage to cache file, verify load returns None."""
        phase_dir = cache_dir / "classify"
        phase_dir.mkdir(parents=True, exist_ok=True)
        corrupt_path = phase_dir / "corrupt_key.json"
        corrupt_path.write_text("NOT VALID JSON {{{", encoding="utf-8")
        result = cache.load("classify", "corrupt_key", ClassificationResult)
        assert result is None

    def test_missing_result_field_returns_none(
        self, cache: CacheManager, cache_dir: Path
    ) -> None:
        """Cache entry without 'result' field returns None."""
        phase_dir = cache_dir / "classify"
        phase_dir.mkdir(parents=True, exist_ok=True)
        entry_path = phase_dir / "no_result.json"
        entry_path.write_text(
            json.dumps({"cache_key": "no_result", "chunk_id": "c1"}),
            encoding="utf-8",
        )
        result = cache.load("classify", "no_result", ClassificationResult)
        assert result is None

    def test_wrong_model_type_returns_none(
        self, cache: CacheManager
    ) -> None:
        """Saving a ClassificationResult and loading as ExtractionResult fails."""
        cr = _make_classification_result(n_segments=2)
        cache.save("classify", "wrong_type", "chunk_1", "model_a", cr)
        # Try to load as ExtractionResult — should fail validation
        result = cache.load("classify", "wrong_type", ExtractionResult)
        assert result is None


# ═══════════════════════════════════════════════════════════════════
# validate_before_caching tests (F6 poison prevention)
# ═══════════════════════════════════════════════════════════════════


class TestValidateBeforeCaching:
    """Tests for the validation gate that prevents cache poisoning."""

    def test_classify_nonempty_passes(self) -> None:
        """ClassificationResult with segments passes validation."""
        cr = _make_classification_result(n_segments=2)
        raw = cr.model_dump_json()
        assert validate_before_caching("classify", raw, ClassificationResult) is True

    def test_classify_empty_segments_rejected(self) -> None:
        """ClassificationResult with 0 segments rejected (cache poisoning)."""
        cr = ClassificationResult(segments=[], total_segments=0)
        raw = cr.model_dump_json()
        assert validate_before_caching("classify", raw, ClassificationResult) is False

    def test_group_nonempty_passes(self) -> None:
        """ExtractionResult with teaching_units passes validation."""
        er = _make_extraction_result(n_units=1)
        raw = er.model_dump_json()
        assert validate_before_caching("group", raw, ExtractionResult) is True

    def test_group_empty_rejected(self) -> None:
        """ExtractionResult with 0 teaching_units rejected."""
        er = ExtractionResult(teaching_units=[], total_units=0)
        raw = er.model_dump_json()
        assert validate_before_caching("group", raw, ExtractionResult) is False

    def test_enrich_nonempty_passes(self) -> None:
        """EnrichmentResult with enrichments passes validation."""
        enr = _make_enrichment_result(n_enrichments=1)
        raw = enr.model_dump_json()
        assert validate_before_caching("enrich", raw, EnrichmentResult) is True

    def test_enrich_empty_rejected(self) -> None:
        """EnrichmentResult with 0 enrichments rejected."""
        enr = EnrichmentResult(enrichments=[], total_units=0)
        raw = enr.model_dump_json()
        assert validate_before_caching("enrich", raw, EnrichmentResult) is False

    def test_enrich_mismatched_total_units_rejected(self) -> None:
        """Partial enrichment batches must not be admitted to cache."""
        enr = _make_enrichment_result(1).model_copy(update={"total_units": 2})
        raw = enr.model_dump_json()
        assert validate_before_caching("enrich", raw, EnrichmentResult) is False

    def test_enrich_sparse_unit_index_coverage_rejected(self) -> None:
        """Enrichment batches must cover a contiguous 0..total_units-1 range."""
        enr = EnrichmentResult(
            enrichments=[
                UnitEnrichment(
                    unit_index=0,
                    excerpt_topic=["اختبار"],
                    school=None,
                    school_confidence=None,
                    resolved_scholars=[],
                    takhrij_data=[],
                    terminology_variants=[],
                    cross_references=[],
                    context_hint=None,
                ),
                UnitEnrichment(
                    unit_index=2,
                    excerpt_topic=["اختبار"],
                    school=None,
                    school_confidence=None,
                    resolved_scholars=[],
                    takhrij_data=[],
                    terminology_variants=[],
                    cross_references=[],
                    context_hint=None,
                ),
            ],
            total_units=2,
        )
        raw = enr.model_dump_json()
        assert validate_before_caching("enrich", raw, EnrichmentResult) is False

    def test_refusal_invalid_json_rejected(self) -> None:
        """Invalid JSON (LLM refusal text) rejected."""
        refusal = "I cannot process this content."
        assert (
            validate_before_caching("classify", refusal, ClassificationResult)
            is False
        )

    def test_malformed_json_rejected(self) -> None:
        """Malformed JSON string rejected."""
        assert (
            validate_before_caching("classify", "{bad json", ClassificationResult)
            is False
        )

    def test_unknown_phase_passes_if_parseable(self) -> None:
        """Unknown phase with parseable model passes (no specific check)."""
        cr = _make_classification_result(n_segments=2)
        raw = cr.model_dump_json()
        # "unknown_phase" has no specific check — returns True if parseable
        assert (
            validate_before_caching("unknown_phase", raw, ClassificationResult)
            is True
        )
