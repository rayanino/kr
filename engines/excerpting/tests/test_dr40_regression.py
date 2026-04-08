"""DR40 regression tests — owner rejection fixtures (2026-03-31).

Tests that the contract models, prompt content, and FP-13 precedence stack
correctly support the granularity calibration decisions from DR40:
  1. Conditional evidence splitting (FP-24, §6.25)
  2. Definition pair splitting (FP-25, §6.24)
  3. Relationship links between split units (FP-23)
  4. Re-ranked FP-13 precedence stack
  5. Regression fixtures from 2 owner rejections

These are deterministic (no LLM calls). They verify the data model
can represent the correct output and that prompt content includes
the new rules.
"""

from __future__ import annotations

from engines.excerpting.contracts import (
    ExtractionResult,
    RelationshipType,
    ScholarlyFunction,
    SelfContainmentLevel,
    TeachingUnit,
    UnitRelationship,
)
from engines.excerpting.src.phase2_group import compute_active_modules
from engines.excerpting.src.prompts import (
    CONSTITUTION,
    GROUP_CORE_RULES,
    GROUP_CRITICAL_REMINDERS,
    GROUP_FIQH_RULES,
    GROUP_OUTPUT_FORMAT,
)
from engines.excerpting.tests.conftest import (
    _make_classified_segment,
    _make_excerpt_record,
    _make_teaching_unit,
)


# ═══════════════════════════════════════════════════════════════════
# Fixture: Owner rejection 1 — talaq definition pair (2026-03-31)
#
# Source text (taysir, كتاب الطلاق مقدمة):
#   الطلاق: في اللغة: حل الوثاق. مشتق من الإطلاق، وهو الترك والإرسال.
#   وفي الشرع: حَل عقدة التزويج، والتعريف الشرعي فَرْد من معناه اللغوي
#   العام. قال إمام الحرمين: هو لفظ جاهلي ورد الشرع بتقريره.
#
# Owner verdict: REJECT — must be TWO excerpts (لغة and شرعا).
# The شرعا excerpt keeps the relationship sentence.
# ═══════════════════════════════════════════════════════════════════


class TestDefinitionPairSplitting:
    """FP-25 / §6.24 — Definition pair splitting regression."""

    def test_companion_definition_relationship_roundtrip(self) -> None:
        """UnitRelationship with companion_definition type validates correctly."""
        link = UnitRelationship(
            target_unit_index=1,
            relationship=RelationshipType.COMPANION_DEFINITION,
            description="paired linguistic definition for الطلاق",
        )
        assert link.relationship == RelationshipType.COMPANION_DEFINITION
        assert link.target_unit_index == 1

    def test_definition_pair_produces_two_units_with_links(self) -> None:
        """The expected output for the talaq definition pair: 2 units with
        companion_definition links pointing to each other."""
        # Unit 0: linguistic definition
        unit_lugha = _make_teaching_unit(
            unit_index=0,
            segment_indices=[0],
            start_word=0,
            end_word=10,
            text_snippet="الطلاق: في اللغة: حل الوثاق. مشتق من الإطلاق، وهو الترك والإرسال."[:80],
            primary_function=ScholarlyFunction.DEFINITION,
            description_arabic="تعريف الطلاق في اللغة وبيان اشتقاقه",
            related_units=[
                UnitRelationship(
                    target_unit_index=1,
                    relationship=RelationshipType.COMPANION_DEFINITION,
                    description="paired technical definition (شرعا)",
                )
            ],
        )
        # Unit 1: technical definition (includes relationship sentence)
        unit_shari = _make_teaching_unit(
            unit_index=1,
            segment_indices=[1],
            start_word=11,
            end_word=30,
            text_snippet="الطلاق في الشرع: حَل عقدة التزويج، والتعريف الشرعي فَرْد من"[:80],
            primary_function=ScholarlyFunction.DEFINITION,
            description_arabic="تعريف الطلاق في الشرع وعلاقته بالمعنى اللغوي",
            related_units=[
                UnitRelationship(
                    target_unit_index=0,
                    relationship=RelationshipType.COMPANION_DEFINITION,
                    description="paired linguistic definition (لغة)",
                )
            ],
        )

        # Verify: 2 units, each with exactly 1 companion link
        assert unit_lugha.related_units[0].target_unit_index == 1
        assert unit_shari.related_units[0].target_unit_index == 0
        assert len(unit_lugha.related_units) == 1
        assert len(unit_shari.related_units) == 1

        # Verify: ExtractionResult accepts units with related_units
        result = ExtractionResult(
            teaching_units=[unit_lugha, unit_shari],
            total_units=2,
        )
        assert len(result.teaching_units) == 2

    def test_shari_unit_not_fragment_start(self) -> None:
        """FP-25: شرعا unit must NOT start with bare 'وفي الشرع...' —
        it must include the definiendum for independent comprehensibility."""
        # This is a content test — verifying the principle is encoded
        # in the prompt. The actual enforcement is by the LLM.
        assert "وفي الشرع" in GROUP_FIQH_RULES
        assert "must NOT start with a bare" in GROUP_FIQH_RULES

    def test_definition_triggers_fiqh_rules(self) -> None:
        """DEFINITION segments must trigger GROUP_FIQH_RULES loading
        so the pair-splitting instruction is visible to the LLM."""
        segments = [
            _make_classified_segment(
                segment_index=0,
                scholarly_function=ScholarlyFunction.DEFINITION,
            ),
        ]
        modules = compute_active_modules(segments)
        assert GROUP_FIQH_RULES in modules


# ═══════════════════════════════════════════════════════════════════
# Fixture: Owner rejection 2 — talaq ruling + evidence bundle (2026-03-31)
#
# Source text (taysir, كتاب الطلاق مقدمة):
#   وحكمه ثابت في الكتاب، والسنة، والإجماع، والقياس الصحيح.
#   فأما الكتاب فنحو {الطلاقُ مَرتَانِ} وغيرها من الآيات.
#   [continued with sunnah + ijma evidence]
#
# Owner verdict: REJECT — must be split by evidence type.
# The general ruling = one excerpt. Each evidence type = separate excerpt.
# Per-ayah granularity for Quranic proofs.
# ═══════════════════════════════════════════════════════════════════


class TestEvidenceTypeSplitting:
    """FP-24 / §6.25 — Conditional evidence splitting regression."""

    def test_evidence_for_relationship_roundtrip(self) -> None:
        """UnitRelationship with evidence_for type validates correctly."""
        link = UnitRelationship(
            target_unit_index=0,
            relationship=RelationshipType.EVIDENCE_FOR,
            description="Quranic proof for permissibility of divorce",
        )
        assert link.relationship == RelationshipType.EVIDENCE_FOR

    def test_ruling_with_split_evidence_produces_linked_units(self) -> None:
        """Expected output: ruling unit + separate evidence_quran unit,
        linked with evidence_for relationship."""
        # Unit 0: general ruling statement
        unit_ruling = _make_teaching_unit(
            unit_index=0,
            segment_indices=[0],
            start_word=0,
            end_word=8,
            text_snippet="وحكمه ثابت في الكتاب، والسنة، والإجماع، والقياس الصحيح."[:80],
            primary_function=ScholarlyFunction.RULE_STATEMENT,
            description_arabic="حكم الطلاق ثابت بالكتاب والسنة والإجماع والقياس",
        )
        # Unit 1: Quranic evidence
        unit_quran = _make_teaching_unit(
            unit_index=1,
            segment_indices=[1],
            start_word=9,
            end_word=20,
            text_snippet="فأما الكتاب فنحو {الطلاقُ مَرتَانِ} وغيرها من الآيات."[:80],
            primary_function=ScholarlyFunction.EVIDENCE_QURAN,
            description_arabic="الاستدلال من القرآن على مشروعية الطلاق بآية الطلاق مرتان",
            related_units=[
                UnitRelationship(
                    target_unit_index=0,
                    relationship=RelationshipType.EVIDENCE_FOR,
                    description="proof for ruling on divorce permissibility",
                )
            ],
        )

        assert unit_quran.related_units[0].target_unit_index == 0
        assert unit_quran.related_units[0].relationship == RelationshipType.EVIDENCE_FOR

        result = ExtractionResult(
            teaching_units=[unit_ruling, unit_quran],
            total_units=2,
        )
        assert len(result.teaching_units) == 2

    def test_condition_for_relationship_roundtrip(self) -> None:
        """UnitRelationship with condition_for type validates correctly."""
        link = UnitRelationship(
            target_unit_index=0,
            relationship=RelationshipType.CONDITION_FOR,
        )
        assert link.relationship == RelationshipType.CONDITION_FOR
        assert link.description is None


# ═══════════════════════════════════════════════════════════════════
# FP-13 precedence stack — re-ranked per DR40
# ═══════════════════════════════════════════════════════════════════


class TestFP13PrecedenceStack:
    """FP-13 — verify the precedence stack is correctly re-ranked."""

    def test_leaf_atomicity_above_pedagogical_in_constitution(self) -> None:
        """Leaf-atomicity (item 4) must appear BEFORE pedagogical packaging
        (item 5) in the CONSTITUTION prompt."""
        leaf_pos = CONSTITUTION.index("Leaf-atomicity")
        ped_pos = CONSTITUTION.index("Pedagogical packaging")
        assert leaf_pos < ped_pos, (
            "Leaf-atomicity must precede Pedagogical packaging in precedence"
        )

    def test_granularity_not_lowest_priority(self) -> None:
        """The old 'Granularity — lowest priority' wording must be gone."""
        assert "lowest priority" not in CONSTITUTION
        assert "optimize separately" not in CONSTITUTION


# ═══════════════════════════════════════════════════════════════════
# Prompt content verification — new rules present
# ═══════════════════════════════════════════════════════════════════


class TestPromptContentDR40:
    """Verify DR40 rules are present in prompt text."""

    def test_conditional_evidence_in_core_rules(self) -> None:
        """GROUP_CORE_RULES must contain the conditional evidence rule,
        not the old unconditional 'MUST stay with the ruling'."""
        assert "Evidence stays with its ruling ONLY when" in GROUP_CORE_RULES
        # Old unconditional rule should be gone
        assert "Evidence cited for a ruling MUST stay with the ruling" not in GROUP_CORE_RULES

    def test_definition_pair_in_fiqh_rules(self) -> None:
        """GROUP_FIQH_RULES must contain definition pair splitting (FP-25)."""
        assert "DEFINITION PAIR SPLITTING" in GROUP_FIQH_RULES
        assert "companion_definition" in GROUP_FIQH_RULES

    def test_evidence_type_in_fiqh_rules(self) -> None:
        """GROUP_FIQH_RULES must contain evidence type splitting (FP-24)."""
        assert "EVIDENCE TYPE SPLITTING" in GROUP_FIQH_RULES
        assert "evidence_for" in GROUP_FIQH_RULES

    def test_related_units_in_output_format(self) -> None:
        """GROUP_OUTPUT_FORMAT must include related_units field."""
        assert "related_units" in GROUP_OUTPUT_FORMAT
        assert "companion_definition" in GROUP_OUTPUT_FORMAT
        assert "evidence_for" in GROUP_OUTPUT_FORMAT
        assert "condition_for" in GROUP_OUTPUT_FORMAT

    def test_critical_reminders_include_split_rules(self) -> None:
        """GROUP_CRITICAL_REMINDERS must include the new split reminders."""
        assert "FP-25" in GROUP_CRITICAL_REMINDERS
        assert "FP-24" in GROUP_CRITICAL_REMINDERS
        assert "related_units" in GROUP_CRITICAL_REMINDERS


# ═══════════════════════════════════════════════════════════════════
# Contract propagation — related_units through Phase 3
# ═══════════════════════════════════════════════════════════════════


class TestRelatedUnitsPropagation:
    """Verify related_units propagates from TeachingUnit to ExcerptRecord."""

    def test_excerpt_record_accepts_related_units(self) -> None:
        """ExcerptRecord must accept the related_units field."""
        record = _make_excerpt_record(
            related_units=[
                UnitRelationship(
                    target_unit_index=1,
                    relationship=RelationshipType.COMPANION_DEFINITION,
                    description="paired definition",
                )
            ],
        )
        assert len(record.related_units) == 1
        assert record.related_units[0].relationship == RelationshipType.COMPANION_DEFINITION

    def test_excerpt_record_default_empty_related_units(self) -> None:
        """ExcerptRecord with no related_units gets empty list."""
        record = _make_excerpt_record()
        assert record.related_units == []

    def test_teaching_unit_default_empty_related_units(self) -> None:
        """TeachingUnit with no related_units gets empty list."""
        unit = _make_teaching_unit()
        assert unit.related_units == []

    def test_relationship_type_enum_values(self) -> None:
        """All three relationship types exist with correct string values."""
        assert RelationshipType.COMPANION_DEFINITION == "companion_definition"
        assert RelationshipType.EVIDENCE_FOR == "evidence_for"
        assert RelationshipType.CONDITION_FOR == "condition_for"
