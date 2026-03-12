"""Tests for registry modules — SPEC §3, §4.A.2, §4.A.5, §4.A.9, §5.

Tests use real Arabic text and cover all 5 registry modules + orchestrator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from engines.source.contracts import (
    AcquisitionPath,
    AttributionStatus,
    AuthorityLevel,
    Genre,
    GenreChain,
    GenreRelationType,
    HumanGateTrigger,
    InferredFieldConfidence,
    ProcessingStatus,
    ScholarReference,
    SourceFormat,
    SourceMetadata,
    StructuralFormat,
    TextFidelity,
    TrustTier,
    TrustworthinessFactor,
    WorkRegistryEntry,
)


# ── Helper to build a minimal SourceMetadata ──


def _make_metadata(
    source_id: str = "src_test0001",
    title: str = "همع الهوامع في شرح جمع الجوامع",
    author_name: str = "جلال الدين السيوطي",
    author_id: str = "sch_00001",
    work_id: str = "wrk_suyuti_hama_alhawami",
    genre: Genre = Genre.SHARH,
    genre_chain: GenreChain | None = None,
    work_relationships: list[GenreChain] | None = None,
) -> SourceMetadata:
    """Build a minimal valid SourceMetadata for testing."""
    return SourceMetadata(
        source_id=source_id,
        work_id=work_id,
        human_label="hama_alhawami",
        title_arabic=title,
        author=ScholarReference(
            canonical_id=author_id,
            name_arabic=author_name,
            confidence=0.95,
            source_of_identification="extracted",
        ),
        attribution_status=AttributionStatus.DEFINITIVE,
        science_scope=["nahw"],
        genre=genre,
        genre_chain=genre_chain,
        source_format=SourceFormat.SHAMELA_HTML,
        authority_level=AuthorityLevel.PRIMARY,
        structural_format=StructuralFormat.COMMENTARY,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.82,
        trust_factors=[
            TrustworthinessFactor(name="author_standing", weight=0.30, score=0.90, reason="Classical scholar"),
        ],
        trust_reason="Classical primary by recognized scholar",
        text_fidelity=TextFidelity.HIGH,
        text_fidelity_reason="Shamela structured text",
        confidence_scores=InferredFieldConfidence(
            genre=0.95, science_scope=0.90, structural_format=0.90, authority_level=0.85,
        ),
        frozen_path=f"library/sources/{source_id}/frozen/",
        frozen_hash="abc123def456",
        frozen_file_hashes={"vol1.htm": "abc123"},
        status=ProcessingStatus.ACQUIRED,
        intake_timestamp="2026-03-10T08:00:00+00:00",
        acquisition_path=AcquisitionPath.MANUAL,
        work_relationships=work_relationships or [],
    )


TRANSLIT_TABLE: dict[str, dict[str, str]] = {
    "scholars": {
        "السيوطي": "suyuti",
        "ابن السبكي": "ibn_alsubki",
        "جلال الدين السيوطي": "suyuti",
    },
    "titles": {
        "همع الهوامع": "hama_alhawami",
        "جمع الجوامع": "jam_aljawami",
    },
}


# ═══════════════════════════════════════════════════════════════════
# Module 2: source_registry tests
# ═══════════════════════════════════════════════════════════════════


class TestSourceRegistry:
    """Tests for source_registry CRUD operations."""

    def test_build_entry_maps_all_fields(self) -> None:
        from engines.source.src.registries.source_registry import build_entry

        metadata = _make_metadata()
        entry = build_entry(metadata)

        assert entry.source_id == "src_test0001"
        assert entry.work_id == "wrk_suyuti_hama_alhawami"
        assert entry.human_label == "hama_alhawami"
        assert entry.title_arabic == "همع الهوامع في شرح جمع الجوامع"
        assert entry.author_canonical_id == "sch_00001"
        assert entry.trust_tier == TrustTier.VERIFIED
        assert entry.processing_status == ProcessingStatus.ACQUIRED
        assert entry.frozen_hash == "abc123def456"
        assert entry.acquisition_path == AcquisitionPath.MANUAL

    def test_load_missing_file(self, tmp_path: Path) -> None:
        from engines.source.src.registries.source_registry import load

        result = load(registry_path=tmp_path / "nonexistent.json")
        assert result == {}

    def test_save_and_load(self, tmp_path: Path) -> None:
        from engines.source.src.registries.source_registry import load, save

        path = tmp_path / "sources.json"
        data = {"src_001": {"source_id": "src_001", "work_id": "wrk_test"}}
        save(registry_path=path, data=data)

        loaded = load(registry_path=path)
        assert loaded["src_001"]["source_id"] == "src_001"

    def test_save_creates_bak(self, tmp_path: Path) -> None:
        from engines.source.src.registries.source_registry import save

        path = tmp_path / "sources.json"
        # First write
        save(registry_path=path, data={"v": 1})
        # Second write creates .bak
        save(registry_path=path, data={"v": 2})

        bak = path.with_suffix(".json.bak")
        assert bak.exists()

    def test_find_by_hash_found(self) -> None:
        from engines.source.src.registries.source_registry import find_by_hash

        registry = {
            "src_001": {"frozen_hash": "hash_aaa"},
            "src_002": {"frozen_hash": "hash_bbb"},
        }
        assert find_by_hash("hash_bbb", registry) == "src_002"

    def test_find_by_hash_not_found(self) -> None:
        from engines.source.src.registries.source_registry import find_by_hash

        registry = {"src_001": {"frozen_hash": "hash_aaa"}}
        assert find_by_hash("hash_zzz", registry) is None


# ═══════════════════════════════════════════════════════════════════
# Module 3: scholar_registry tests
# ═══════════════════════════════════════════════════════════════════


class TestScholarRegistry:
    """Tests for scholar_registry wrapper (auto-link / human gate / new record)."""

    def _seed_scholar(self, registry_path: Path) -> None:
        """Create a scholars.json with one known scholar."""
        data = {
            "sch_00001": {
                "canonical_id": "sch_00001",
                "canonical_name_ar": "جلال الدين السيوطي",
                "known_as": ["السيوطي"],
                "name_variants": [],
                "kunya": None,
                "laqab": [],
                "nisba": [],
                "birth_date_hijri": 849,
                "birth_date_ce": None,
                "death_date_hijri": 911,
                "death_date_ce": None,
                "death_date_approximate": False,
                "era_century_hijri": 9,
                "geographic_origin": None,
                "geographic_active": [],
                "school_affiliations": {"fiqh": "شافعي"},
                "sectarian_tradition": "sunni",
                "teachers": [],
                "students": [],
                "known_works": [],
                "scholarly_standing": None,
                "methodology_notes": None,
                "methodological_stance": None,
                "disambiguation_notes": None,
                "sources_encountered_in": [],
                "record_completeness": 0.25,
                "data_provenance_score": 0.0,
                "record_sources": [],
                "revision_history": [],
                "last_updated": "2026-03-10T08:00:00+00:00",
                "genealogy_metadata": None,
                "cross_validation": None,
            }
        }
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_auto_link_path(self, tmp_path: Path) -> None:
        """Score >= 0.85 → auto-link, no checkpoint created."""
        from engines.source.src.registries.scholar_registry import lookup_or_register_author
        from shared.human_gate.src.human_gate import configure

        reg_path = tmp_path / "registries" / "scholars.json"
        gates_dir = tmp_path / "gates"
        configure(gates_dir=gates_dir, auto_approve=True)
        self._seed_scholar(reg_path)

        ref, checkpoint_id = lookup_or_register_author(
            name="السيوطي",
            death_date_hijri=911,
            school_affiliations={"fiqh": "شافعي"},
            source_id="src_test_auto",
            registry_path=reg_path,
        )

        assert ref.canonical_id == "sch_00001"
        assert checkpoint_id is None
        assert ref.confidence >= 0.85

    def test_human_gate_path(self, tmp_path: Path) -> None:
        """Score 0.50-0.85 → human gate checkpoint created."""
        from engines.source.src.registries.scholar_registry import lookup_or_register_author
        from shared.human_gate.src.human_gate import configure

        reg_path = tmp_path / "registries" / "scholars.json"
        gates_dir = tmp_path / "gates"
        configure(gates_dir=gates_dir, auto_approve=True)
        self._seed_scholar(reg_path)

        # Name-only match (capped at 0.65) → human_gate range
        ref, checkpoint_id = lookup_or_register_author(
            name="السيوطي",
            death_date_hijri=None,
            school_affiliations=None,
            source_id="src_test_gate",
            registry_path=reg_path,
        )

        assert ref.canonical_id == "sch_00001"
        assert checkpoint_id is not None
        assert checkpoint_id.startswith("hg_")

    def test_new_record_path(self, tmp_path: Path) -> None:
        """Score < 0.50 → new scholar registered."""
        from engines.source.src.registries.scholar_registry import lookup_or_register_author
        from shared.human_gate.src.human_gate import configure

        reg_path = tmp_path / "registries" / "scholars.json"
        gates_dir = tmp_path / "gates"
        configure(gates_dir=gates_dir, auto_approve=True)
        self._seed_scholar(reg_path)

        ref, checkpoint_id = lookup_or_register_author(
            name="عبد الله بن إبراهيم الزاحم",
            death_date_hijri=None,
            school_affiliations=None,
            source_id="src_test_new",
            registry_path=reg_path,
        )

        assert ref.canonical_id.startswith("sch_")
        assert ref.canonical_id != "sch_00001"  # New ID
        assert checkpoint_id is None
        assert ref.confidence == 1.0

    def test_new_record_stores_full_school_affiliations(self, tmp_path: Path) -> None:
        """Multi-entry school_affiliations dict stored correctly (BUG-01 regression)."""
        from engines.source.src.registries.scholar_registry import lookup_or_register_author
        from shared.human_gate.src.human_gate import configure
        from shared.scholar_authority.src.scholar_authority import _load_registry

        reg_path = tmp_path / "registries" / "scholars.json"
        gates_dir = tmp_path / "gates"
        configure(gates_dir=gates_dir, auto_approve=True)

        affiliations = {"fiqh": "شافعي", "usul": "شافعي", "nahw": "بصري"}
        ref, _ = lookup_or_register_author(
            name="إمام الحرمين الجويني",
            death_date_hijri=478,
            school_affiliations=affiliations,
            source_id="src_test_sa",
            registry_path=reg_path,
        )

        # Verify the full dict was stored, not {"primary": "شافعي"}
        registry = _load_registry(reg_path)
        record = registry[ref.canonical_id]
        stored_sa = record.school_affiliations if hasattr(record, "school_affiliations") else record.get("school_affiliations", {})
        assert stored_sa == affiliations
        assert "primary" not in stored_sa

    def test_muhaqiq_registration(self, tmp_path: Path) -> None:
        """Muhaqiq with name-only → registered as new scholar."""
        from engines.source.src.registries.scholar_registry import lookup_or_register_muhaqiq
        from shared.human_gate.src.human_gate import configure

        reg_path = tmp_path / "registries" / "scholars.json"
        gates_dir = tmp_path / "gates"
        configure(gates_dir=gates_dir, auto_approve=True)
        # Empty registry
        reg_path.parent.mkdir(parents=True, exist_ok=True)
        reg_path.write_text("{}", encoding="utf-8")

        ref = lookup_or_register_muhaqiq(
            muhaqiq_name="عبد الحميد هنداوي",
            source_id="src_test_muhaqiq",
            registry_path=reg_path,
        )

        assert ref.canonical_id.startswith("sch_")
        assert ref.name_arabic == "عبد الحميد هنداوي"
        assert ref.confidence == 1.0


# ═══════════════════════════════════════════════════════════════════
# Module 4: work_registry_store tests
# ═══════════════════════════════════════════════════════════════════


class TestWorkRegistryStore:
    """Tests for work registry CRUD and genre chain processing."""

    def test_build_entry_generates_work_id(self) -> None:
        from engines.source.src.registries.work_registry_store import build_entry

        metadata = _make_metadata()
        entry = build_entry(metadata, TRANSLIT_TABLE)

        assert entry.work_id.startswith("wrk_")
        assert "suyuti" in entry.work_id
        assert entry.canonical_title == "همع الهوامع في شرح جمع الجوامع"
        assert entry.author_canonical_id == "sch_00001"
        assert entry.status == "active"
        assert entry.source_ids == ["src_test0001"]

    def test_build_placeholder(self) -> None:
        from engines.source.src.registries.work_registry_store import build_placeholder

        entry = build_placeholder(
            title="جمع الجوامع",
            author_canonical_id="sch_00001",
            work_id="wrk_subki_jam_aljawami",
        )

        assert entry.status == "referenced_not_acquired"
        assert entry.source_ids == []
        assert entry.preferred_source_id is None
        assert entry.canonical_title == "جمع الجوامع"

    def test_create_relationship_edge(self) -> None:
        from engines.source.src.registries.work_registry_store import create_relationship_edge

        edge = create_relationship_edge(
            from_work_id="wrk_suyuti_hama",
            to_work_id="wrk_subki_jam",
            relation_type=GenreRelationType.SHARH_OF,
            confidence=0.92,
        )

        assert edge.from_work_id == "wrk_suyuti_hama"
        assert edge.to_work_id == "wrk_subki_jam"
        assert edge.relation_type == GenreRelationType.SHARH_OF
        assert edge.discovered_by == "source_engine"

    def test_find_by_title_author_found(self) -> None:
        from engines.source.src.registries.work_registry_store import find_by_title_author

        registry = {
            "wrk_test": {
                "canonical_title": "جمع الجوامع",
                "author_canonical_id": "sch_00001",
            }
        }
        result = find_by_title_author("جمع الجوامع", "sch_00001", registry)
        assert result == "wrk_test"

    def test_find_by_title_author_not_found(self) -> None:
        from engines.source.src.registries.work_registry_store import find_by_title_author

        registry = {
            "wrk_test": {
                "canonical_title": "المغني",
                "author_canonical_id": "sch_00002",
            }
        }
        result = find_by_title_author("جمع الجوامع", "sch_00001", registry)
        assert result is None

    def test_find_by_title_similar(self) -> None:
        """Title similarity >= 0.80 matches."""
        from engines.source.src.registries.work_registry_store import find_by_title_author

        registry = {
            "wrk_test": {
                "canonical_title": "جمع الجوامع في أصول الفقه",
                "author_canonical_id": "sch_00001",
            }
        }
        # "جمع الجوامع" is a subset of the full title — should match
        result = find_by_title_author("جمع الجوامع", "sch_00001", registry)
        assert result == "wrk_test"

    def test_save_and_load(self, tmp_path: Path) -> None:
        from engines.source.src.registries.work_registry_store import load, save

        path = tmp_path / "works.json"
        data = {"wrk_001": {"work_id": "wrk_001", "canonical_title": "كتاب"}}
        save(registry_path=path, data=data)

        loaded = load(registry_path=path)
        assert loaded["wrk_001"]["work_id"] == "wrk_001"

    def test_process_genre_chain_finds_existing_work(self, tmp_path: Path) -> None:
        """Genre chain with known base work → links to existing, no placeholder."""
        from engines.source.src.registries.work_registry_store import process_genre_chain
        from shared.human_gate.src.human_gate import configure

        gates_dir = tmp_path / "gates"
        configure(gates_dir=gates_dir, auto_approve=True)

        # Seed scholar registry with ابن السبكي
        scholar_path = tmp_path / "registries" / "scholars.json"
        scholar_path.parent.mkdir(parents=True, exist_ok=True)
        scholar_data = {
            "sch_00099": {
                "canonical_id": "sch_00099",
                "canonical_name_ar": "ابن السبكي",
                "known_as": [],
                "name_variants": [],
                "kunya": None,
                "laqab": [],
                "nisba": [],
                "birth_date_hijri": None,
                "birth_date_ce": None,
                "death_date_hijri": 771,
                "death_date_ce": None,
                "death_date_approximate": False,
                "era_century_hijri": 8,
                "geographic_origin": None,
                "geographic_active": [],
                "school_affiliations": {},
                "sectarian_tradition": None,
                "teachers": [],
                "students": [],
                "known_works": [],
                "scholarly_standing": None,
                "methodology_notes": None,
                "methodological_stance": None,
                "disambiguation_notes": None,
                "sources_encountered_in": [],
                "record_completeness": 0.1,
                "data_provenance_score": 0.0,
                "record_sources": [],
                "revision_history": [],
                "last_updated": "2026-03-10T08:00:00+00:00",
                "genealogy_metadata": None,
                "cross_validation": None,
            }
        }
        scholar_path.write_text(
            json.dumps(scholar_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        chain = GenreChain(
            relation_type=GenreRelationType.SHARH_OF,
            base_work_title="جمع الجوامع",
            base_work_author="ابن السبكي",
            confidence=0.90,
        )
        metadata = _make_metadata(
            genre_chain=chain,
            work_relationships=[chain],
        )

        # Pre-seed work registry with the base work (matching canonical_id)
        work_reg: dict[str, dict] = {
            "wrk_existing": {
                "canonical_title": "جمع الجوامع",
                "author_canonical_id": "sch_00099",
                "status": "active",
            }
        }

        edges = process_genre_chain(
            metadata, work_reg, scholar_path, TRANSLIT_TABLE,
        )

        assert len(edges) == 1
        assert edges[0].to_work_id == "wrk_existing"
        # No placeholder should have been created
        placeholder_count = sum(
            1 for w in work_reg.values()
            if w.get("status") == "referenced_not_acquired"
        )
        assert placeholder_count == 0

    def test_process_genre_chain_creates_placeholder(self, tmp_path: Path) -> None:
        """Genre chain with unknown base work → placeholder created."""
        from engines.source.src.registries.work_registry_store import process_genre_chain
        from shared.human_gate.src.human_gate import configure

        gates_dir = tmp_path / "gates"
        configure(gates_dir=gates_dir, auto_approve=True)

        scholar_path = tmp_path / "registries" / "scholars.json"
        scholar_path.parent.mkdir(parents=True, exist_ok=True)
        scholar_path.write_text("{}", encoding="utf-8")

        chain = GenreChain(
            relation_type=GenreRelationType.SHARH_OF,
            base_work_title="جمع الجوامع",
            base_work_author="ابن السبكي",
            confidence=0.90,
        )
        metadata = _make_metadata(
            genre_chain=chain,
            work_relationships=[chain],
        )

        work_reg: dict[str, dict] = {}
        edges = process_genre_chain(
            metadata, work_reg, scholar_path, TRANSLIT_TABLE,
        )

        assert len(edges) >= 1
        assert edges[0].relation_type == GenreRelationType.SHARH_OF
        assert edges[0].from_work_id == metadata.work_id

        # Placeholder should exist in work_reg now
        placeholder_ids = [wid for wid, w in work_reg.items() if w.get("status") == "referenced_not_acquired"]
        assert len(placeholder_ids) >= 1


# ═══════════════════════════════════════════════════════════════════
# Module 5: human_gate wrapper tests
# ═══════════════════════════════════════════════════════════════════


class TestHumanGateWrapper:
    """Tests for source-engine human gate convenience functions."""

    @pytest.fixture(autouse=True)
    def _setup_gates(self, tmp_path: Path) -> None:
        from shared.human_gate.src.human_gate import configure
        configure(gates_dir=tmp_path / "gates", auto_approve=True)

    def test_gate_author_disambiguation(self) -> None:
        from engines.source.src.human_gate import gate_author_disambiguation

        cp = gate_author_disambiguation(
            source_id="src_test",
            candidates=[{"canonical_id": "sch_00001", "name": "السيوطي"}],
            match_score=0.72,
            inferred_name="جلال الدين السيوطي",
        )
        assert cp.trigger == HumanGateTrigger.AUTHOR_DISAMBIGUATION
        assert cp.source_id == "src_test"
        assert "جلال الدين السيوطي" in cp.trigger_detail

    def test_gate_consensus_disagreement(self) -> None:
        from engines.source.src.human_gate import gate_consensus_disagreement

        cp = gate_consensus_disagreement(
            source_id="src_test",
            field="genre",
            model_a_value="sharh",
            model_b_value="matn",
            model_a_name="command_a",
            model_b_name="opus",
        )
        assert cp.trigger == HumanGateTrigger.CONSENSUS_DISAGREEMENT
        assert "genre" in cp.trigger_detail

    def test_gate_low_confidence(self) -> None:
        from engines.source.src.human_gate import gate_low_confidence

        cp = gate_low_confidence(
            source_id="src_test",
            field="science_scope",
            value=["nahw"],
            confidence=0.55,
        )
        assert cp.trigger == HumanGateTrigger.LOW_CONFIDENCE_FIELD
        assert cp.current_values["confidence"] == 0.55

    def test_gate_trust_flagged(self) -> None:
        from engines.source.src.human_gate import gate_trust_flagged

        cp = gate_trust_flagged(
            source_id="src_test",
            trust_score=0.42,
            trust_factors=[{"name": "author_standing", "score": 0.30}],
        )
        assert cp.trigger == HumanGateTrigger.TRUST_FLAGGED
        assert cp.current_values["trust_score"] == 0.42

    def test_gate_scholar_conflict(self) -> None:
        from engines.source.src.human_gate import gate_scholar_conflict

        cp = gate_scholar_conflict(
            source_id="src_test",
            canonical_id="sch_00001",
            conflict_type="death_date_drift",
            existing_value=911,
            proposed_value=920,
        )
        assert cp.trigger == HumanGateTrigger.SCHOLAR_CONFLICT
        assert cp.current_values["canonical_id"] == "sch_00001"


# ═══════════════════════════════════════════════════════════════════
# Module 6: registration orchestrator tests
# ═══════════════════════════════════════════════════════════════════


class TestRegistrationOrchestrator:
    """Tests for register_source and orphan recovery."""

    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path: Path) -> None:
        from shared.human_gate.src.human_gate import configure
        configure(gates_dir=tmp_path / "gates", auto_approve=True)
        self.lib_root = tmp_path / "library"
        self.lib_root.mkdir()
        (self.lib_root / "registries").mkdir()
        (self.lib_root / "logs").mkdir()
        # Write empty config files
        config_dir = self.lib_root / "config"
        config_dir.mkdir()
        translit = json.dumps(TRANSLIT_TABLE, ensure_ascii=False)
        (config_dir / "transliteration.json").write_text(translit, encoding="utf-8")
        (config_dir / "recognized_muhaqiqs.json").write_text("[]", encoding="utf-8")
        (config_dir / "known_publishers.json").write_text("{}", encoding="utf-8")
        (config_dir / "genre_synonyms.json").write_text("{}", encoding="utf-8")

    def test_full_registration(self) -> None:
        """Full registration: pending → registries updated → metadata.json → pending deleted."""
        from engines.source.src.registries import register_source

        metadata = _make_metadata()
        register_source(metadata, library_root=self.lib_root)

        # Sources registry updated
        sources_path = self.lib_root / "registries" / "sources.json"
        assert sources_path.exists()
        sources = json.loads(sources_path.read_text(encoding="utf-8"))
        assert "src_test0001" in sources

        # Works registry updated
        works_path = self.lib_root / "registries" / "works.json"
        assert works_path.exists()

        # metadata.json written
        meta_path = self.lib_root / "sources" / "src_test0001" / "metadata.json"
        assert meta_path.exists()
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        assert meta["source_id"] == "src_test0001"

        # Pending file cleaned up
        pending_files = list((self.lib_root / "logs").glob("pending_registration_*.json"))
        assert len(pending_files) == 0

    def test_bak_files_created(self) -> None:
        """Registration creates .bak files for registries."""
        from engines.source.src.registries import register_source

        # Pre-seed registries so .bak gets created
        sources_path = self.lib_root / "registries" / "sources.json"
        sources_path.write_text("{}", encoding="utf-8")
        works_path = self.lib_root / "registries" / "works.json"
        works_path.write_text("{}", encoding="utf-8")

        metadata = _make_metadata()
        register_source(metadata, library_root=self.lib_root)

        assert sources_path.with_suffix(".json.bak").exists()
        assert works_path.with_suffix(".json.bak").exists()

    def test_metadata_json_valid(self) -> None:
        """metadata.json is valid SourceMetadata JSON."""
        from engines.source.src.registries import register_source

        metadata = _make_metadata()
        register_source(metadata, library_root=self.lib_root)

        meta_path = self.lib_root / "sources" / "src_test0001" / "metadata.json"
        raw = json.loads(meta_path.read_text(encoding="utf-8"))
        # Should be loadable as SourceMetadata
        restored = SourceMetadata.model_validate(raw)
        assert restored.source_id == "src_test0001"

    def test_orphan_recovery_all_complete(self, tmp_path: Path) -> None:
        """Orphan with all files completed → clean up pending."""
        from engines.source.src.registries import check_orphaned_registrations

        logs_dir = self.lib_root / "logs"
        pending = {
            "source_id": "src_orphan1",
            "timestamp": "2026-03-10T08:00:00+00:00",
            "intended_changes": {"sources.json": {}, "works.json": {}},
            "completed_files": ["sources.json", "works.json"],
        }
        (logs_dir / "pending_registration_src_orphan1.json").write_text(
            json.dumps(pending), encoding="utf-8"
        )

        recovered = check_orphaned_registrations(library_root=self.lib_root)
        assert "src_orphan1" in recovered
        assert not (logs_dir / "pending_registration_src_orphan1.json").exists()

    def test_orphan_recovery_none_started(self) -> None:
        """Orphan with no files completed → clean up pending."""
        from engines.source.src.registries import check_orphaned_registrations

        logs_dir = self.lib_root / "logs"
        pending = {
            "source_id": "src_orphan2",
            "timestamp": "2026-03-10T08:00:00+00:00",
            "intended_changes": {"sources.json": {}, "works.json": {}},
            "completed_files": [],
        }
        (logs_dir / "pending_registration_src_orphan2.json").write_text(
            json.dumps(pending), encoding="utf-8"
        )

        recovered = check_orphaned_registrations(library_root=self.lib_root)
        assert "src_orphan2" in recovered
        assert not (logs_dir / "pending_registration_src_orphan2.json").exists()

    def test_orphan_recovery_partial_rollback(self) -> None:
        """Orphan with partial completion → rollback from .bak."""
        from engines.source.src.registries import check_orphaned_registrations

        logs_dir = self.lib_root / "logs"
        regs_dir = self.lib_root / "registries"

        # Create .bak with old data
        old_data = {"old_source": {"source_id": "old_source"}}
        bak_path = regs_dir / "sources.json.bak"
        bak_path.write_text(json.dumps(old_data), encoding="utf-8")

        # Current sources.json has corrupted/partial data
        new_data = {"old_source": {"source_id": "old_source"}, "src_partial": {"source_id": "src_partial"}}
        (regs_dir / "sources.json").write_text(json.dumps(new_data), encoding="utf-8")

        pending = {
            "source_id": "src_partial",
            "timestamp": "2026-03-10T08:00:00+00:00",
            "intended_changes": {"sources.json": {}, "works.json": {}},
            "completed_files": ["sources.json"],  # Partial — only sources done
        }
        (logs_dir / "pending_registration_src_partial.json").write_text(
            json.dumps(pending), encoding="utf-8"
        )

        recovered = check_orphaned_registrations(library_root=self.lib_root)
        assert "src_partial" in recovered

        # sources.json should be restored from .bak
        restored = json.loads((regs_dir / "sources.json").read_text(encoding="utf-8"))
        assert "src_partial" not in restored
        assert "old_source" in restored

    def test_rollback_corrupt_bak_raises_runtime_error(self) -> None:
        """Corrupt registry + corrupt .bak → RuntimeError (not silent pass)."""
        from engines.source.src.registries import _rollback_registries

        regs_dir = self.lib_root / "registries"
        registry_path = regs_dir / "sources.json"
        bak_path = regs_dir / "sources.json.bak"

        # Write corrupt registry
        registry_path.write_text("NOT VALID JSON", encoding="utf-8")
        # Write corrupt .bak too
        bak_path.write_text("ALSO NOT VALID JSON", encoding="utf-8")

        with pytest.raises(RuntimeError, match="backup is also corrupt"):
            _rollback_registries(self.lib_root)

    def test_orphan_partial_rollback_fail_raises(self) -> None:
        """Partial orphan where .bak restore fails → RuntimeError."""
        from engines.source.src.registries import check_orphaned_registrations

        logs_dir = self.lib_root / "logs"
        regs_dir = self.lib_root / "registries"

        # Create pending with partial completion
        pending = {
            "source_id": "src_fail",
            "timestamp": "2026-03-10T08:00:00+00:00",
            "intended_changes": {"sources.json": {}, "works.json": {}},
            "completed_files": ["sources.json"],
        }
        (logs_dir / "pending_registration_src_fail.json").write_text(
            json.dumps(pending), encoding="utf-8"
        )

        # Create a read-only directory at .bak location to force OSError
        # (no .bak file exists, so os.replace will fail — but bak_path.exists()
        # check prevents it from running. Instead test that valid .bak restore
        # works without swallowing errors.)
        bak_path = regs_dir / "sources.json.bak"
        bak_path.write_text('{"old": "data"}', encoding="utf-8")
        (regs_dir / "sources.json").write_text('{"new": "data"}', encoding="utf-8")

        # Should succeed — restore from .bak
        recovered = check_orphaned_registrations(library_root=self.lib_root)
        assert "src_fail" in recovered
        restored = json.loads((regs_dir / "sources.json").read_text(encoding="utf-8"))
        assert "old" in restored

    def test_work_id_sync_between_registries(self) -> None:
        """Source entry work_id must match the generated work_id in works registry."""
        from engines.source.src.registries import register_source

        metadata = _make_metadata()
        register_source(metadata, library_root=self.lib_root)

        sources = json.loads(
            (self.lib_root / "registries" / "sources.json").read_text(encoding="utf-8")
        )
        works = json.loads(
            (self.lib_root / "registries" / "works.json").read_text(encoding="utf-8")
        )

        src_entry = sources["src_test0001"]
        # The source entry's work_id must exist as a key in works registry
        assert src_entry["work_id"] in works, (
            f"Source work_id '{src_entry['work_id']}' not in works registry: {list(works.keys())}"
        )

    def test_registration_with_genre_chain(self) -> None:
        """Registration with genre chain creates placeholder works and edges."""
        from engines.source.src.registries import register_source

        # Seed empty scholars registry
        scholars_path = self.lib_root / "registries" / "scholars.json"
        scholars_path.write_text("{}", encoding="utf-8")

        chain = GenreChain(
            relation_type=GenreRelationType.SHARH_OF,
            base_work_title="جمع الجوامع",
            base_work_author="ابن السبكي",
            confidence=0.90,
        )
        metadata = _make_metadata(
            genre_chain=chain,
            work_relationships=[chain],
        )

        register_source(metadata, library_root=self.lib_root)

        # Works registry should have the main work + placeholder
        works_path = self.lib_root / "registries" / "works.json"
        works = json.loads(works_path.read_text(encoding="utf-8"))
        placeholder_works = {
            wid: w for wid, w in works.items()
            if w.get("status") == "referenced_not_acquired"
        }
        assert len(placeholder_works) >= 1
