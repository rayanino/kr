"""Phase 5 Session 6 — real-LLM smoke test for verifier_dispatch.

First end-to-end exercise of the Phase 5 architecture against live LLMs.
Validates that ``make_production_verifier`` from ``verifier_dispatch.py``:

  - Successfully dispatches via OpenRouter (NEVER OpenAI/Anthropic native APIs)
    using ``instructor.from_provider`` for both consensus models.
  - Returns a schema-locked ``VerifierEmission`` per round.
  - Persists raw LLM responses to
    ``tests/results/source_engine/phase5_session5/{call_id}/llm_responses/``
    per Critical Rule 11 (every API call's full output preserved as future
    training material).
  - Routes through ``scholar_match_cell`` to a DEFINITIVE terminal for an
    unambiguous fragment with strong dossier alignment.

Provider routing rule (owner directive 2026-05-06): all LLM calls route via
OpenRouter. Both verifier specs use ``openrouter/<provider>/<model>`` IDs.
See ``memory/feedback_llm_provider_routing.md`` and the consensus-pattern SKILL.

Test gating (per ``.claude/rules/llm-call-optimization.md``):

  - ``test_kr_llm_tests_gate_fires_when_unset`` runs ALWAYS — validates that
    the ``KR_LLM_TESTS`` env-var gate prevents accidental production-LLM
    dispatch. No API calls. No cost. No skip.
  - ``test_real_llm_smoke_albukhari_definitive`` requires BOTH ``KR_LLM_TESTS=1``
    AND ``OPENROUTER_API_KEY`` set. Skipped otherwise. Cost ~EUR 0.10-0.20 per run
    (2 verifiers × 1 round-0 dispatch each on a small fragment).

Per ``.claude/rules/testing.md``: real Arabic fixtures only — al-Bukhārī
(sch_00042) is the canonical test scholar with rich biographical signal
(3rd-century hadith, Shafi'i, الجامع الصحيح) that the LLM should bind to
unambiguously when given a 2-candidate registry that includes one
adversarial alternate (Ibn Ḥajar al-ʿAsqalānī, sch_00200 — also a hadith
scholar but 9th century, distinct era).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from engines.source.contracts import ScholarAuthorityRecord
from engines.source.src.scholar_match_integration import (
    build_orchestration_for_pipeline,
)
from engines.source.src.verifier_dispatch import (
    PERSISTENCE_ROOT,
    make_production_verifier,
)
from shared.scholar_authority.src.match_contracts import DossierContext
from shared.scholar_authority.src.scholar_match_cell import scholar_match_cell
from shared.scholar_authority.src.stage1_narrowing import Registry
from shared.scholar_authority.src.stage2_verifier import (
    VerifierCallError,
    VerifierSpec,
)


# ---------------------------------------------------------------------------
# Fixtures — minimal 2-scholar registry with one adversarial alternate
# ---------------------------------------------------------------------------


_SMOKE_RELEASE_VERSION: str = "v_session6_real_llm_smoke_2026_05_06"


def _bukhari_record() -> ScholarAuthorityRecord:
    """Imam al-Bukhārī — primary hadith, 3rd century AH, Shafi'i."""
    return ScholarAuthorityRecord(
        canonical_id="sch_00042",
        canonical_name_ar="محمد بن إسماعيل البخاري",
        display_name="الإمام البخاري",
        full_name_lineage="محمد بن إسماعيل بن إبراهيم البخاري",
        known_as=["البخاري", "الإمام البخاري", "صاحب الصحيح"],
        kunya="أبو عبد الله",
        nisba=["البخاري", "الجعفي"],
        birth_date_hijri=194,
        birth_date_ce=None,
        death_date_hijri=256,
        death_date_ce=None,
        era_century_hijri=3,
        geographic_origin="بخارى",
        geographic_active=["بخارى", "نيسابور"],
        school_affiliations={"hadith": "shafii"},
        teachers=[],
        students=[],
        known_works=["الجامع الصحيح", "التاريخ الكبير"],
        primary_science="hadith",
        scholarly_standing="إمام أهل الحديث",
        last_updated="2026-05-06T00:00:00Z",
        record_completeness=0.0,
        data_provenance_score=0.0,
    )


def _ibn_hajar_asqalani_record() -> ScholarAuthorityRecord:
    """Ibn Ḥajar al-ʿAsqalānī — 9th-century hadith (adversarial alternate).

    Same primary_science as al-Bukhārī (hadith) but distinct era_century_hijri
    (9 vs 3) and distinct geographic_origin (mişr vs bukhārā). Shares the
    "ابن حجر" honorific only — the fragment "محمد بن إسماعيل البخاري" should
    not be attributed here.
    """
    return ScholarAuthorityRecord(
        canonical_id="sch_00200",
        canonical_name_ar="أحمد بن علي بن حجر العسقلاني",
        display_name="ابن حجر العسقلاني",
        full_name_lineage="أحمد بن علي بن محمد بن حجر العسقلاني",
        known_as=["ابن حجر", "الحافظ ابن حجر", "ابن حجر العسقلاني"],
        kunya="أبو الفضل",
        nisba=["العسقلاني", "المصري"],
        birth_date_hijri=773,
        birth_date_ce=None,
        death_date_hijri=852,
        death_date_ce=None,
        era_century_hijri=9,
        geographic_origin="عسقلان",
        geographic_active=["القاهرة", "مكة"],
        school_affiliations={"hadith": "shafii", "fiqh": "shafii"},
        teachers=[],
        students=[],
        known_works=["فتح الباري", "تهذيب التهذيب", "الإصابة في تمييز الصحابة"],
        primary_science="hadith",
        scholarly_standing="حافظ",
        last_updated="2026-05-06T00:00:00Z",
        record_completeness=0.0,
        data_provenance_score=0.0,
    )


def _build_smoke_registry() -> Registry:
    return Registry(
        release_version=_SMOKE_RELEASE_VERSION,
        scholars=[_bukhari_record(), _ibn_hajar_asqalani_record()],
    )


# ---------------------------------------------------------------------------
# Production verifier specs — OpenRouter routing only (owner directive 2026-05-06)
# ---------------------------------------------------------------------------


_PRODUCTION_VERIFIER_A = VerifierSpec(
    verifier_id="session6_smoke_verifier_a_command_a",
    model_id="openrouter/cohere/command-a",
    seed=20260506,
    round_0_prompt_template_hash="r0_session6_smoke_command_a",
    round_1_prompt_template_hash="r1_session6_smoke_command_a",
)
_PRODUCTION_VERIFIER_B = VerifierSpec(
    verifier_id="session6_smoke_verifier_b_opus_4_6",
    model_id="openrouter/anthropic/claude-opus-4.6",
    seed=20260507,
    round_0_prompt_template_hash="r0_session6_smoke_opus_4_6",
    round_1_prompt_template_hash="r1_session6_smoke_opus_4_6",
)


# ---------------------------------------------------------------------------
# Test 1 — gate validation (always runs; no API calls; no skip)
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0052", "AC-6")
def test_kr_llm_tests_gate_fires_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    """The production verifier MUST fail loud when KR_LLM_TESTS is not "1".

    Per ``.claude/rules/llm-call-optimization.md``: real-LLM dispatch is gated
    to prevent accidental cost in CI / dev workflows. The gate is enforced
    INSIDE the returned VerifierCallable, raising ``VerifierCallError`` with a
    clear message before any network call is attempted.

    Invokes the production callable DIRECTLY (not via scholar_match_cell) —
    the orchestrator's _safe_call_round_0 helper deliberately catches
    VerifierCallError and routes to insufficient_evidence per REQ-SRC-0052
    AC-6, so testing the gate via scholar_match_cell would observe
    insufficient_evidence rather than the underlying gate raise. Direct
    invocation is the right granularity for asserting the gate fires.
    """
    monkeypatch.delenv("KR_LLM_TESTS", raising=False)

    callable_ = make_production_verifier()

    # Construct a minimal valid ScholarEvidencePacket — the production callable
    # only inspects the packet AFTER passing the env-var gate, so any
    # syntactically valid packet works for asserting the gate raises.
    from shared.scholar_authority.src.match_contracts import (
        NormalizedFragment,
        ScholarCandidate,
        ScholarEvidencePacket,
    )

    packet = ScholarEvidencePacket(
        display_fragment="محمد بن إسماعيل البخاري",
        normalized_fragment="محمد بن إسماعيل البخاري",
        match_key="محمد بن اسماعيل البخاري",
        parsed_components=NormalizedFragment(
            ism="محمد",
            kunyah=None,
            nasab_chain=["بن إسماعيل"],
            laqab=[],
            nisba_list=["البخاري"],
        ),
        candidate_set=[
            ScholarCandidate(
                canonical_id="sch_00042",
                canonical_name_ar="محمد بن إسماعيل البخاري",
                provenance_for_inclusion="gate_test_minimal",
            )
        ],
        dossier_context=DossierContext(),
        source_snippets=[],
        registry_release_version=_SMOKE_RELEASE_VERSION,
    )

    with pytest.raises(VerifierCallError) as exc_info:
        callable_(_PRODUCTION_VERIFIER_A, packet, 0, None, None)
    # Message must mention the env-var gate so the failure is self-explanatory
    assert "KR_LLM_TESTS" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Test 2 — real LLM smoke (gated; ~EUR 0.10-0.20 per run)
# ---------------------------------------------------------------------------


_REAL_LLM_REASON = (
    "real-LLM smoke test requires KR_LLM_TESTS=1 AND OPENROUTER_API_KEY "
    "set; this test makes paid OpenRouter API calls (~EUR 0.10-0.20 per run)"
)


@pytest.mark.spec("DEC-SRC-0013", "REQ-SRC-0052", "REQ-SRC-0053")
@pytest.mark.skipif(
    os.environ.get("KR_LLM_TESTS") != "1"
    or not os.environ.get("OPENROUTER_API_KEY"),
    reason=_REAL_LLM_REASON,
)
def test_real_llm_smoke_albukhari_definitive(tmp_path: Path) -> None:
    """End-to-end real-LLM dispatch — al-Bukhārī DEFINITIVE binding via OpenRouter.

    Fragment: ``محمد بن إسماعيل البخاري`` (the canonical full name; unambiguous).
    Registry: 2 candidates (al-Bukhārī sch_00042 + Ibn Ḥajar sch_00200).
    Dossier: full alignment on al-Bukhārī (3rd-c. hadith, Shafi'i school,
    الجامع الصحيح work, Bukhārā origin) and zero alignment on Ibn Ḥajar
    (9th c., Egypt origin, different works).

    Expected outcome: Both verifiers agree at round 0 → DEFINITIVE →
    canonical_scholar_id == "sch_00042" with confidence ≥ 0.85.

    Side-effects validated:
      - Raw LLM response files exist on disk under
        ``{persistence_root}/{call_id}/llm_responses/``.
      - Each persisted file is valid JSON with the expected shape.
    """
    # Use tmp_path for the persistence root so the smoke test does not pollute
    # the canonical results directory; we still validate the persistence
    # mechanism end-to-end against this isolated path.
    smoke_persistence_root = tmp_path / "phase5_session5"

    callable_ = make_production_verifier(persistence_root=smoke_persistence_root)
    registry = _build_smoke_registry()
    orchestration = build_orchestration_for_pipeline(
        registry=registry,
        verifier_a_spec=_PRODUCTION_VERIFIER_A,
        verifier_b_spec=_PRODUCTION_VERIFIER_B,
        call_verifier=callable_,
    )

    dossier = DossierContext(
        genre="ḥadīth",
        primary_science="hadith",
        century_active_hijri_estimates=[3],
        school_affiliation_hints={"hadith": "shafii"},
        attributed_works=["الجامع الصحيح"],
        geographic_signals=["بخارى"],
    )

    result = scholar_match_cell(
        "محمد بن إسماعيل البخاري", dossier, orchestration
    )

    # ---- Terminal-state assertions ----
    assert result.disambiguation_state == "definitive", (
        f"Expected DEFINITIVE for unambiguous al-Bukhārī fragment; got "
        f"{result.disambiguation_state!r}. Verifier record: "
        f"a={result.provenance.stage_2_verifier_record.verifier_a_id} "
        f"b={result.provenance.stage_2_verifier_record.verifier_b_id} "
        f"round_count={result.provenance.stage_2_verifier_record.round_count}."
    )
    assert result.canonical_scholar_id == "sch_00042", (
        f"Expected canonical_id sch_00042 (al-Bukhārī); got "
        f"{result.canonical_scholar_id!r}."
    )
    assert result.confidence is not None and result.confidence >= 0.85, (
        f"DEFINITIVE confidence must be ≥ 0.85 per REQ-SRC-0053 mean threshold; "
        f"got {result.confidence!r}."
    )

    # ---- Provenance assertions (INV-SRC-0015) ----
    assert result.record_status is not None, (
        "DEFINITIVE result must populate record_status per CON-SRC-0008 validator."
    )
    assert (
        result.provenance.registry_release_version == _SMOKE_RELEASE_VERSION
    ), "Snapshot version must round-trip through provenance per INV-SRC-0017."
    record = result.provenance.stage_2_verifier_record
    assert record.verifier_a_id == _PRODUCTION_VERIFIER_A.verifier_id, (
        "Verifier A identity must round-trip through provenance."
    )
    assert record.verifier_b_id == _PRODUCTION_VERIFIER_B.verifier_id, (
        "Verifier B identity must round-trip through provenance."
    )
    assert record.round_count >= 1, (
        f"At least one round must have run; round_count={record.round_count!r}."
    )

    # ---- Persistence assertions (Critical Rule 11) ----
    assert smoke_persistence_root.exists(), (
        f"Persistence root {smoke_persistence_root} must be created during dispatch."
    )
    persisted_files = list(smoke_persistence_root.rglob("llm_responses/*.json"))
    assert len(persisted_files) >= 2, (
        f"Expected ≥2 persisted LLM responses (one per verifier × round-0); "
        f"got {len(persisted_files)} files: {[str(p) for p in persisted_files]}"
    )
    for persisted_path in persisted_files:
        # Each file must be valid JSON with the expected envelope shape
        payload = json.loads(persisted_path.read_text(encoding="utf-8"))
        assert "verifier_id" in payload, (
            f"Persisted response {persisted_path} missing verifier_id field."
        )
        assert "model_id" in payload, (
            f"Persisted response {persisted_path} missing model_id field."
        )
        assert payload["model_id"].startswith("openrouter/"), (
            f"Persisted response {persisted_path} has non-OpenRouter model_id "
            f"{payload['model_id']!r} — owner directive 2026-05-06 violated."
        )
        assert "raw_llm_output" in payload, (
            f"Persisted response {persisted_path} missing raw_llm_output."
        )
        raw = payload["raw_llm_output"]
        assert "chosen_id" in raw and "positions" in raw, (
            f"Raw LLM output {persisted_path} missing chosen_id/positions."
        )


# Note on canonical persistence:
#
# This smoke test deliberately uses ``tmp_path`` as the persistence root so
# the test does not pollute ``tests/results/source_engine/phase5_session5/``
# with one-off smoke artifacts. For a real production run that wants to
# preserve responses as canonical training data per Critical Rule 13, omit
# the ``persistence_root`` kwarg and let it default to ``PERSISTENCE_ROOT``.
# The default behavior is exercised by the verifier_dispatch.py docstring
# example and is the production path.
assert PERSISTENCE_ROOT == Path("tests/results/source_engine/phase5_session5"), (
    "Test depends on the documented default persistence root; if "
    "PERSISTENCE_ROOT changes, update this docstring + smoke test path."
)
