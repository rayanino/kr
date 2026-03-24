"""Tests for Phase 3 Consensus Verification and Human Gates (SPEC §7.3).

All tests use mocked LLM clients — no real API calls.
Tests cover: consensus triggers, school/attribution/self-containment
disagreement resolution, context hint repair, gate entries, no-consensus path.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from engines.excerpting.contracts import (
    AuthorAttribution,
    ConsensusDecision,
    ConsensusRecord,
    ExcerptRecord,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    ScholarlyFunction,
    SelfContainmentLevel,
    VerificationItem,
    VerificationResult,
)
from engines.excerpting.src.phase3_consensus import (
    _find_majority,
    _needs_consensus,
    _parse_self_containment,
    _repair_context_hint,
    _resolve_school,
    _resolve_self_containment,
    check_gate_triggers,
    resolve_consensus,
    run_consensus,
    verify_chunk,
)
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk,
    _make_excerpt_record,
    _make_mock_instructor_client,
)


# ═══════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════


_SOURCE_META = {
    "author_name": "ابن قدامة",
    "work_title": "المغني",
    "science": "فقه",
    "source_school": "حنبلي",
}


def _make_vi(
    item_index: int = 0,
    agrees: bool = True,
    alternative: str | None = None,
    confidence: float = 0.9,
    reasoning: str = "Correct assessment",
) -> VerificationItem:
    """Factory for VerificationItem."""
    return VerificationItem(
        item_index=item_index,
        agrees=agrees,
        alternative=alternative,
        confidence=confidence,
        reasoning=reasoning,
    )


# ═══════════════════════════════════════════════════════════════════
# 1. Consensus Triggers (§7.3.1)
# ═══════════════════════════════════════════════════════════════════


class TestConsensusTriggers:
    """Verify correct items are flagged for consensus."""

    def test_school_non_null_triggers(self) -> None:
        exc = _make_excerpt_record(school="حنبلي", school_confidence=0.9)
        items = _needs_consensus(exc)
        types = [it["verification_type"] for it in items]
        assert "SCHOOL_ATTRIBUTION" in types

    def test_school_null_does_not_trigger(self) -> None:
        exc = _make_excerpt_record(school=None)
        items = _needs_consensus(exc)
        types = [it["verification_type"] for it in items]
        assert "SCHOOL_ATTRIBUTION" not in types

    def test_la3_triggers_author_attribution(self) -> None:
        exc = _make_excerpt_record(
            primary_author_layer=AuthorAttribution(
                layer_id="sharh",
                author_id="sch_test",
                coverage_pct=0.6,
                rule_applied="LA-3",
            ),
        )
        items = _needs_consensus(exc)
        types = [it["verification_type"] for it in items]
        assert "AUTHOR_ATTRIBUTION" in types

    def test_la1_does_not_trigger(self) -> None:
        """LA-1 is deterministic — no consensus needed."""
        exc = _make_excerpt_record(
            primary_author_layer=AuthorAttribution(
                layer_id="matn",
                author_id="sch_test",
                coverage_pct=0.95,
                rule_applied="LA-1",
            ),
        )
        items = _needs_consensus(exc)
        types = [it["verification_type"] for it in items]
        assert "AUTHOR_ATTRIBUTION" not in types

    def test_partial_triggers_self_containment(self) -> None:
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يعتمد على ما سبق",
            context_hint="سياق الباب السابق",
        )
        items = _needs_consensus(exc)
        types = [it["verification_type"] for it in items]
        assert "SELF_CONTAINMENT" in types

    def test_dependent_triggers_self_containment(self) -> None:
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.DEPENDENT,
            self_containment_notes="لا يمكن فهمه بدون السياق",
            context_hint=None,
            review_flags=["llm_enrichment_failed"],
        )
        items = _needs_consensus(exc)
        types = [it["verification_type"] for it in items]
        assert "SELF_CONTAINMENT" in types

    def test_full_does_not_trigger_self_containment(self) -> None:
        """FULL self-containment does NOT need verification (§7.3.1)."""
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.FULL,
        )
        items = _needs_consensus(exc)
        types = [it["verification_type"] for it in items]
        assert "SELF_CONTAINMENT" not in types

    def test_multiple_triggers_combined(self) -> None:
        """An excerpt can trigger school + self-containment + attribution."""
        exc = _make_excerpt_record(
            school="شافعي",
            school_confidence=0.7,
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="مرتبط بباب سابق",
            context_hint="باب الطهارة",
            primary_author_layer=AuthorAttribution(
                layer_id="sharh",
                author_id="sch_test",
                coverage_pct=0.55,
                rule_applied="LA-3",
            ),
        )
        items = _needs_consensus(exc)
        types = [it["verification_type"] for it in items]
        assert len(types) == 3
        assert "SCHOOL_ATTRIBUTION" in types
        assert "AUTHOR_ATTRIBUTION" in types
        assert "SELF_CONTAINMENT" in types


# ═══════════════════════════════════════════════════════════════════
# 2. School Disagreement Resolution (§7.3.3)
# ═══════════════════════════════════════════════════════════════════


class TestSchoolDisagreement:
    """Confidence lowered, review flag added, EX-M-003 emitted."""

    def test_school_agreement(self) -> None:
        exc = _make_excerpt_record(school="حنبلي", school_confidence=0.9)
        vi = _make_vi(agrees=True)
        decision, updates, flags, gates = _resolve_school(exc, vi, _SOURCE_META)

        assert decision.verifier_agrees is True
        assert decision.resolution_method == "consensus_agree"
        assert not flags
        assert not gates

    def test_school_disagreement_lowers_confidence(self) -> None:
        exc = _make_excerpt_record(school="حنبلي", school_confidence=0.85)
        vi = _make_vi(agrees=False, alternative="شافعي", confidence=0.7)
        decision, updates, flags, gates = _resolve_school(exc, vi, _SOURCE_META)

        assert decision.verifier_agrees is False
        assert updates["school_confidence"] == 0.7  # min(0.85, 0.7)
        assert "school_consensus_disagreement" in flags

    def test_school_disagreement_emits_ex_m_003(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        exc = _make_excerpt_record(school="حنبلي", school_confidence=0.85)
        vi = _make_vi(agrees=False, alternative="شافعي", confidence=0.6)

        with caplog.at_level("WARNING"):
            _resolve_school(exc, vi, _SOURCE_META)

        assert ExcerptingErrorCodes.EX_M_003 in caplog.text

    def test_school_disagreement_keeps_enrichment_school(self) -> None:
        """§7.3.3: excerpt produced with enrichment model's school value."""
        exc = _make_excerpt_record(school="حنبلي", school_confidence=0.85)
        vi = _make_vi(agrees=False, alternative="شافعي", confidence=0.6)
        decision, _, _, _ = _resolve_school(exc, vi, _SOURCE_META)

        assert decision.final_value == "حنبلي"


# ═══════════════════════════════════════════════════════════════════
# 3. Attribution Escalation (LA-3)
# ═══════════════════════════════════════════════════════════════════


class TestAttributionEscalation:
    """2-of-3 majority wins, all-3-disagree → EX-G-001."""

    def test_attribution_agreement(self) -> None:
        exc = _make_excerpt_record(
            primary_author_layer=AuthorAttribution(
                layer_id="sharh", author_id="sch_a",
                coverage_pct=0.6, rule_applied="LA-3",
            ),
        )
        vi = _make_vi(agrees=True)

        result, _cr, gates = resolve_consensus(
            exc, [vi], ["AUTHOR_ATTRIBUTION"], None, ExcerptingConfig()
        )

        assert result.attribution_confidence == 1.0
        assert not gates

    def test_2_of_3_majority_wins(self) -> None:
        """Enrichment + escalation agree, verifier disagrees."""
        exc = _make_excerpt_record(
            primary_author_layer=AuthorAttribution(
                layer_id="sharh", author_id="sch_a",
                coverage_pct=0.6, rule_applied="LA-3",
            ),
        )
        vi = _make_vi(agrees=False, alternative="sch_b", confidence=0.7)

        # Mock escalation that agrees with enrichment
        from pydantic import BaseModel, Field

        class EscResp(BaseModel):
            author_id: str
            reasoning: str

        esc_client = _make_mock_instructor_client(
            return_value=EscResp(author_id="sch_a", reasoning="test")
        )

        result, _cr, gates = resolve_consensus(
            exc, [vi], ["AUTHOR_ATTRIBUTION"],
            esc_client, ExcerptingConfig(), _SOURCE_META,
        )

        assert result.attribution_confidence == 0.67
        assert ExcerptingErrorCodes.EX_G_001 not in gates

    def test_all_3_disagree_triggers_gate(self) -> None:
        """All 3 models disagree → EX-G-001 gate."""
        exc = _make_excerpt_record(
            primary_author_layer=AuthorAttribution(
                layer_id="sharh", author_id="sch_a",
                coverage_pct=0.6, rule_applied="LA-3",
            ),
        )
        vi = _make_vi(agrees=False, alternative="sch_b", confidence=0.7)

        from pydantic import BaseModel

        class EscResp(BaseModel):
            author_id: str
            reasoning: str

        esc_client = _make_mock_instructor_client(
            return_value=EscResp(author_id="sch_c", reasoning="third opinion")
        )

        result, _cr, gates = resolve_consensus(
            exc, [vi], ["AUTHOR_ATTRIBUTION"],
            esc_client, ExcerptingConfig(), _SOURCE_META,
        )

        assert result.attribution_confidence == 0.0
        assert ExcerptingErrorCodes.EX_G_001 in gates

    def test_find_majority_2_of_3(self) -> None:
        assert _find_majority(["a", "b", "a"]) == "a"
        assert _find_majority(["b", "a", "b"]) == "b"
        assert _find_majority(["a", "a", "b"]) == "a"

    def test_find_majority_all_different(self) -> None:
        assert _find_majority(["a", "b", "c"]) is None


# ═══════════════════════════════════════════════════════════════════
# 4. Self-Containment Conservatism (§7.3.3)
# ═══════════════════════════════════════════════════════════════════


class TestSelfContainmentConservatism:
    """Always use lower level, never upgrade."""

    def test_agreement_keeps_level(self) -> None:
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يحتاج سياقاً",
            context_hint="باب الطهارة",
        )
        vi = _make_vi(agrees=True)
        decision, updates, _, _ = _resolve_self_containment(exc, vi)

        assert decision.verifier_agrees is True
        assert "self_containment" not in updates

    def test_downgrade_partial_to_dependent(self) -> None:
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يحتاج سياقاً",
            context_hint="باب الطهارة",
        )
        vi = _make_vi(agrees=False, alternative="DEPENDENT")
        decision, updates, _, gates = _resolve_self_containment(exc, vi)

        assert updates["self_containment"] == SelfContainmentLevel.DEPENDENT
        assert ExcerptingErrorCodes.EX_G_002 in gates

    def test_never_upgrade_partial_to_full(self) -> None:
        """Conservative rule: consensus never upgrades (§7.3.3)."""
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يحتاج سياقاً",
            context_hint="باب الطهارة",
        )
        vi = _make_vi(agrees=False, alternative="FULL")
        decision, updates, _, _ = _resolve_self_containment(exc, vi)

        # FULL has higher level than PARTIAL — conservative keeps PARTIAL
        assert "self_containment" not in updates
        assert decision.final_value == "PARTIAL"

    def test_parse_self_containment_levels(self) -> None:
        assert _parse_self_containment("FULL") == SelfContainmentLevel.FULL
        assert _parse_self_containment("PARTIAL") == SelfContainmentLevel.PARTIAL
        assert _parse_self_containment("DEPENDENT") == SelfContainmentLevel.DEPENDENT
        assert _parse_self_containment("This is PARTIAL really") == SelfContainmentLevel.PARTIAL
        assert _parse_self_containment(None) is None
        assert _parse_self_containment("unknown") is None


# ═══════════════════════════════════════════════════════════════════
# 5. Context Hint Repair (§7.3.3)
# ═══════════════════════════════════════════════════════════════════


class TestContextHintRepair:
    """FULL→PARTIAL generates hint, →DEPENDENT nullifies hint."""

    def test_full_to_partial_generates_hint_from_notes(self) -> None:
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.FULL,
            self_containment_notes=None,
            context_hint=None,
        )
        updates: dict[str, object] = {
            "self_containment": SelfContainmentLevel.PARTIAL,
        }
        # Simulate having self_containment_notes on the excerpt
        exc_with_notes = exc.model_copy(
            update={
                "self_containment": SelfContainmentLevel.PARTIAL,
                "self_containment_notes": "يعتمد على الباب السابق",
                "context_hint": "placeholder",
                "review_flags": ["llm_enrichment_failed"],
            }
        )
        result = _repair_context_hint(exc_with_notes, updates)
        # FULL→PARTIAL: should generate hint
        # Here exc_with_notes is already PARTIAL, so the repair checks
        # if the *original* was FULL. Since we passed FULL excerpt, we test directly
        result2 = _repair_context_hint(exc, {
            "self_containment": SelfContainmentLevel.PARTIAL,
        })
        assert "context_hint" in result2

    def test_downgrade_to_dependent_nullifies_hint(self) -> None:
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يحتاج سياقاً",
            context_hint="باب الطهارة",
        )
        updates: dict[str, object] = {
            "self_containment": SelfContainmentLevel.DEPENDENT,
        }
        result = _repair_context_hint(exc, updates)
        assert result["context_hint"] is None

    def test_no_change_no_repair(self) -> None:
        """If consensus keeps same level, no repair needed."""
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يحتاج سياقاً",
            context_hint="باب الطهارة",
        )
        updates: dict[str, object] = {}
        result = _repair_context_hint(exc, updates)
        assert "context_hint" not in result


# ═══════════════════════════════════════════════════════════════════
# 6. Gate Entry Format (§7.3.4)
# ═══════════════════════════════════════════════════════════════════


class TestGateEntries:
    """Correct JSON structure per §7.3.4."""

    def test_gate_trigger_ex_g_001(self) -> None:
        exc = _make_excerpt_record(
            primary_author_layer=AuthorAttribution(
                layer_id="sharh", author_id="sch_a",
                coverage_pct=0.6, rule_applied="LA-3",
            ),
            attribution_confidence=0.0,
        )
        config = ExcerptingConfig()
        gates = check_gate_triggers(exc, _SOURCE_META, config)
        assert ExcerptingErrorCodes.EX_G_001 in gates

    def test_gate_trigger_ex_g_002(self) -> None:
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.DEPENDENT,
            self_containment_notes="لا يمكن فهمه",
            context_hint=None,
            review_flags=["llm_enrichment_failed"],
        )
        config = ExcerptingConfig()
        gates = check_gate_triggers(exc, _SOURCE_META, config)
        assert ExcerptingErrorCodes.EX_G_002 in gates

    def test_gate_trigger_ex_g_003(self) -> None:
        """School conflicts with source metadata AND both models disagree."""
        exc = _make_excerpt_record(
            school="شافعي",
            school_confidence=0.5,
            review_flags=["school_consensus_disagreement"],
        )
        meta = {"source_school": "حنبلي"}
        config = ExcerptingConfig()
        gates = check_gate_triggers(exc, meta, config)
        assert ExcerptingErrorCodes.EX_G_003 in gates

    def test_no_gate_when_school_matches_source(self) -> None:
        exc = _make_excerpt_record(
            school="حنبلي",
            school_confidence=0.9,
            review_flags=["school_consensus_disagreement"],
        )
        meta = {"source_school": "حنبلي"}
        config = ExcerptingConfig()
        gates = check_gate_triggers(exc, meta, config)
        assert ExcerptingErrorCodes.EX_G_003 not in gates

    def test_gate_disabled_by_config(self) -> None:
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.DEPENDENT,
            self_containment_notes="لا يمكن فهمه",
            context_hint=None,
            review_flags=["llm_enrichment_failed"],
        )
        config = ExcerptingConfig(GATE_ON_DEPENDENT=False)
        gates = check_gate_triggers(exc, _SOURCE_META, config)
        assert ExcerptingErrorCodes.EX_G_002 not in gates


# ═══════════════════════════════════════════════════════════════════
# 7. No-Consensus Path
# ═══════════════════════════════════════════════════════════════════


class TestNoConsensusPath:
    """Chunks with no consensus-required units skip verification."""

    def test_no_consensus_needed_skips_verification(self) -> None:
        """Units with school=None, LA-1, FULL → skip verification."""
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(
            div_id=chunk.div_id,
            school=None,
            self_containment=SelfContainmentLevel.FULL,
            primary_author_layer=AuthorAttribution(
                layer_id="matn", author_id="sch_test",
                coverage_pct=0.95, rule_applied="LA-1",
            ),
        )

        # verify_client should NOT be called
        verify_client = _make_mock_instructor_client()
        config = ExcerptingConfig()

        result, gates = run_consensus(
            [exc], [chunk], MagicMock(), verify_client, None, config
        )

        assert len(result) == 1
        assert not gates
        assert verify_client.chat.completions.create.call_count == 0

    def test_verify_chunk_returns_none_for_no_items(self) -> None:
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(
            div_id=chunk.div_id,
            school=None,
            self_containment=SelfContainmentLevel.FULL,
        )
        client = _make_mock_instructor_client()
        config = ExcerptingConfig()

        result = verify_chunk(chunk, [exc], client, config)
        assert result is None
        assert client.chat.completions.create.call_count == 0


# ═══════════════════════════════════════════════════════════════════
# 8. Full Consensus Flow
# ═══════════════════════════════════════════════════════════════════


class TestFullConsensusFlow:
    """Integration-style tests with mocked verification call."""

    def test_consensus_with_school_agreement(self) -> None:
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(
            div_id=chunk.div_id,
            school="حنبلي",
            school_confidence=0.9,
        )
        vr = VerificationResult(items=[
            VerificationItem(
                item_index=0, agrees=True, confidence=0.95,
                reasoning="Correct school",
            ),
        ])
        verify_client = _make_mock_instructor_client(return_value=vr)
        config = ExcerptingConfig()

        result, gates = run_consensus(
            [exc], [chunk], MagicMock(), verify_client, None, config, _SOURCE_META
        )

        assert len(result) == 1
        assert result[0].consensus_metadata is not None
        assert not gates

    def test_verification_failure_adds_flag(self) -> None:
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(
            div_id=chunk.div_id,
            school="حنبلي",
            school_confidence=0.9,
        )
        verify_client = _make_mock_instructor_client(
            side_effect=Exception("API error")
        )
        config = ExcerptingConfig()

        result, gates = run_consensus(
            [exc], [chunk], MagicMock(), verify_client, None, config
        )

        assert len(result) == 1
        assert "verification_skipped" in result[0].review_flags
