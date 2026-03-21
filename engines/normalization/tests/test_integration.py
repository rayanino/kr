"""Integration tests for the normalization engine — Session 7.

Tests in this file exercise the full normalization pipeline (normalize_source,
normalize_and_write) on real fixture files. Supersedes the placeholder tests
in test_kr_output.py.

Test categories:
  A: TestShamelaNormalizer (9) — schema, content, footnotes, layers, diacritics,
     pages, structure, flags, boundary continuity
  B: TestContentFlagger (3) — quran, hadith, poetry detection on constructed pages
  C: TestContentCensus (1 skip) — deferred §4.B.5
  D: TestFixtureIntegration (63 parametrized) — all fixtures with silent page loss check
  E: TestNormalizeAndWrite (3) — end-to-end write+read, roundtrip, plain text
  F: TestAdversarialGap (8) — ADV-019, 020, 022, 034, 038, 040, 048, 049
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from engines.normalization.contracts import (
    LayerType,
    NormalizedManifest,
    NormalizedPackage,
)
from engines.normalization.src.content_flagger import compute_content_flags
from engines.normalization.src.dispatcher import normalize_and_write, normalize_source
from engines.normalization.tests.conftest import (
    FIXTURES_REAL,
    _make_cleaned_page,
    _make_html,
    _make_source_metadata,
    _wrap_page,
)


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════


def _get_fixture(name: str) -> Path:
    """Resolve a named fixture from shamela_real/ to its .htm file."""
    fixture_dir = FIXTURES_REAL / name
    htms = list(fixture_dir.glob("*.htm"))
    assert htms, f"No .htm files in {fixture_dir}"
    return htms[0]


def _discover_fixtures() -> list[tuple[str, Path]]:
    """Discover all Shamela fixtures (real + extended) for parametrized testing."""
    project_root = Path(__file__).parent.parent.parent.parent  # kr/
    fixtures: list[tuple[str, Path]] = []
    for base in [
        project_root / "tests" / "fixtures" / "shamela_real",
        project_root / "tests" / "fixtures" / "shamela_extended",
    ]:
        if not base.exists():
            continue
        for d in sorted(base.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            htms = list(d.glob("*.htm"))
            if htms:
                fixtures.append((d.name, htms[0]))
    return fixtures


FIXTURES = _discover_fixtures()
MULTI_LAYER_FIXTURES = {"02_nahw_muhaqiq"}

# Diacritics codepoints: U+064B-U+0652 + U+0670 (superscript alef) + U+0640 (tatweel)
_DIACRITICS = {chr(cp) for cp in range(0x064B, 0x0653)} | {"\u0670", "\u0640"}


# ══════════════════════════════════════════════════════════════════════
# A: TestShamelaNormalizer — Integration tests on real fixtures
# ══════════════════════════════════════════════════════════════════════


class TestShamelaNormalizer:
    """SPEC §4.A.2: Shamela normalizer integration tests on real fixtures."""

    def test_output_schema_compliance(self) -> None:
        """Output conforms to NormalizedPackage schema with valid manifest."""
        path = _get_fixture("02_nahw_muhaqiq")
        meta = _make_source_metadata(is_multi_layer=True)
        pkg = normalize_source(path, meta)

        assert isinstance(pkg, NormalizedPackage)
        assert isinstance(pkg.manifest, NormalizedManifest)
        assert pkg.manifest.source_id == "src_test0001"
        assert pkg.manifest.total_content_units == len(pkg.content_units)
        assert len(pkg.manifest.division_tree) > 0
        assert len(pkg.manifest.layer_map) == 2

    def test_content_preservation_arabic_text(self) -> None:
        """Arabic text preserved through normalization — no HTML tags, >50% Arabic."""
        path = _get_fixture("02_nahw_muhaqiq")
        meta = _make_source_metadata(is_multi_layer=True)
        pkg = normalize_source(path, meta)

        total_arabic = 0
        total_chars = 0
        for cu in pkg.content_units:
            assert cu.primary_text  # non-empty
            total_chars += len(cu.primary_text)
            total_arabic += sum(
                1 for c in cu.primary_text if "\u0600" <= c <= "\u06FF"
            )
            assert "<" not in cu.primary_text
            assert ">" not in cu.primary_text
        assert total_arabic > total_chars * 0.5

    def test_footnote_separation(self) -> None:
        """Footnotes correctly separated in 03_fiqh (32 pages with footnotes)."""
        path = _get_fixture("03_fiqh")
        meta = _make_source_metadata()
        pkg = normalize_source(path, meta)

        pages_with_fn = sum(
            1 for cu in pkg.content_units if len(cu.footnotes) > 0
        )
        assert pages_with_fn >= 20
        for cu in pkg.content_units:
            for fn in cu.footnotes:
                assert fn.text  # non-empty

    def test_multi_layer_detection(self) -> None:
        """Matn/sharh layers detected in 02_nahw_muhaqiq commentary."""
        path = _get_fixture("02_nahw_muhaqiq")
        meta = _make_source_metadata(is_multi_layer=True)
        pkg = normalize_source(path, meta)

        layer_types = {entry.layer_type for entry in pkg.manifest.layer_map}
        assert LayerType.MATN in layer_types
        assert LayerType.SHARH in layer_types
        multi_layer_count = sum(
            1 for cu in pkg.content_units if len(cu.text_layers) >= 2
        )
        assert multi_layer_count >= 3

    def test_diacritics_preservation(self) -> None:
        """Tashkeel diacritics preserved in 04_hadith (confirmed: 11,120)."""
        path = _get_fixture("04_hadith")
        meta = _make_source_metadata()
        pkg = normalize_source(path, meta)

        total_diacritics = sum(
            sum(1 for c in cu.primary_text if c in _DIACRITICS)
            for cu in pkg.content_units
        )
        assert total_diacritics > 5000  # confirmed: 11,120

    def test_page_boundaries(self) -> None:
        """Page boundaries: contiguous unit_index, valid volumes, count match."""
        path = _get_fixture("02_nahw_muhaqiq")
        meta = _make_source_metadata(is_multi_layer=True)
        pkg = normalize_source(path, meta)

        indices = [cu.unit_index for cu in pkg.content_units]
        assert indices == list(range(len(indices)))
        for cu in pkg.content_units:
            assert cu.physical_page.volume is not None
            assert cu.physical_page.volume >= 1
        assert len(pkg.content_units) == pkg.manifest.total_content_units

    def test_structure_discovery(self) -> None:
        """Division tree detected in 06_usul (9 divisions confirmed)."""
        path = _get_fixture("06_usul")
        meta = _make_source_metadata()
        pkg = normalize_source(path, meta)

        assert len(pkg.manifest.division_tree) >= 5
        for node in pkg.manifest.division_tree:
            assert node.heading_text  # non-empty
            assert node.start_unit_index <= node.end_unit_index

    def test_content_flags(self) -> None:
        """Hadith flags in 04_hadith (>=30), minimal in 01_nahw_simple."""
        path_hadith = _get_fixture("04_hadith")
        meta = _make_source_metadata()
        pkg_hadith = normalize_source(path_hadith, meta)
        hadith_count = sum(
            1 for cu in pkg_hadith.content_units
            if cu.content_flags.has_hadith_citation
        )
        assert hadith_count >= 30  # confirmed: 36

        path_nahw = _get_fixture("01_nahw_simple")
        pkg_nahw = normalize_source(path_nahw, meta)
        nahw_hadith = sum(
            1 for cu in pkg_nahw.content_units
            if cu.content_flags.has_hadith_citation
        )
        # 01_nahw_simple uses hadith examples for grammatical illustration,
        # so it has some hadith flags — but proportionally fewer than 04_hadith
        nahw_ratio = nahw_hadith / max(1, len(pkg_nahw.content_units))
        hadith_ratio = hadith_count / max(1, len(pkg_hadith.content_units))
        assert nahw_ratio < hadith_ratio  # grammar text has lower hadith density

    def test_boundary_continuity_signals(self) -> None:
        """Boundary continuity in 01_nahw_simple: >=50% coverage, >=2 types.

        F2 — Session 5 integration coverage.
        Confirmed: mid_sentence=47, mid_paragraph=17, mid_argument=1,
        section_break=7 out of 73 units = 72/73 with signals.
        """
        path = _get_fixture("01_nahw_simple")
        meta = _make_source_metadata()
        pkg = normalize_source(path, meta)

        with_bc = [
            cu for cu in pkg.content_units
            if cu.boundary_continuity is not None
        ]
        assert len(with_bc) >= len(pkg.content_units) * 0.5

        bc_types = set()
        for cu in with_bc:
            assert cu.boundary_continuity is not None
            bc_types.add(cu.boundary_continuity.type)
        assert len(bc_types) >= 2

        for cu in with_bc:
            assert cu.boundary_continuity is not None
            assert cu.boundary_continuity.confidence > 0


# ══════════════════════════════════════════════════════════════════════
# B: TestContentFlagger — Unit-level flag verification
# ══════════════════════════════════════════════════════════════════════


class TestContentFlagger:
    """SPEC §4.A.9: Content flag detection on constructed CleanedPages."""

    def test_quran_verse_detection(self) -> None:
        """Quran citation patterns detected and flagged."""
        page = _make_cleaned_page(
            primary_text="قال تعالى {وَأَقِيمُوا الصَّلَاةَ}",
            unit_index=0,
            title_spans=[],
            has_verse=False,
            has_tables=False,
            is_blank=False,
            is_image_only=False,
        )
        flags = compute_content_flags(page, is_toc_page=False)
        assert flags.has_quran_citation is True

        # Without Quran pattern -> False
        page_clean = _make_cleaned_page(
            primary_text="هذا نص عادي بدون آيات قرآنية",
            unit_index=0,
            title_spans=[],
            has_verse=False,
            has_tables=False,
            is_blank=False,
            is_image_only=False,
        )
        flags_clean = compute_content_flags(page_clean, is_toc_page=False)
        assert flags_clean.has_quran_citation is False

    def test_hadith_marker_detection(self) -> None:
        """Hadith citation patterns detected: rawahu + collector, SAWS."""
        # Pattern: rawahu al-bukhari
        page_rawahu = _make_cleaned_page(
            primary_text="رواه البخاري ومسلم",
            unit_index=0,
            title_spans=[],
            has_verse=False,
            has_tables=False,
            is_blank=False,
            is_image_only=False,
        )
        flags = compute_content_flags(page_rawahu, is_toc_page=False)
        assert flags.has_hadith_citation is True

        # Pattern: U+FDFA (sallallahu alayhi wasallam)
        page_saws = _make_cleaned_page(
            primary_text="قال رسول الله \uFDFA",
            unit_index=0,
            title_spans=[],
            has_verse=False,
            has_tables=False,
            is_blank=False,
            is_image_only=False,
        )
        flags_saws = compute_content_flags(page_saws, is_toc_page=False)
        assert flags_saws.has_hadith_citation is True

        # Clean text -> False
        page_clean = _make_cleaned_page(
            primary_text="هذا نص عادي بدون أحاديث نبوية",
            unit_index=0,
            title_spans=[],
            has_verse=False,
            has_tables=False,
            is_blank=False,
            is_image_only=False,
        )
        flags_clean = compute_content_flags(page_clean, is_toc_page=False)
        assert flags_clean.has_hadith_citation is False

    def test_poetry_verse_detection(self) -> None:
        """Poetry flag passed through from Pass 3 has_verse signal."""
        page_verse = _make_cleaned_page(
            primary_text="ألا كل شيء ما خلا الله باطل",
            unit_index=0,
            title_spans=[],
            has_verse=True,
            has_tables=False,
            is_blank=False,
            is_image_only=False,
        )
        flags = compute_content_flags(page_verse, is_toc_page=False)
        assert flags.has_verse is True

        page_no_verse = _make_cleaned_page(
            primary_text="هذا نص عادي",
            unit_index=0,
            title_spans=[],
            has_verse=False,
            has_tables=False,
            is_blank=False,
            is_image_only=False,
        )
        flags2 = compute_content_flags(page_no_verse, is_toc_page=False)
        assert flags2.has_verse is False


# ══════════════════════════════════════════════════════════════════════
# C: TestContentCensus — Deferred
# ══════════════════════════════════════════════════════════════════════


class TestContentCensus:
    """SPEC §4.B.5: Content census — DEFERRED per CORE_EXTRACTION.md (D7-1)."""

    def test_census_deferred(self) -> None:
        """Census stays deferred per D7-1."""
        pytest.skip("§4.B.5 DEFERRED — content census not in core build")


# ══════════════════════════════════════════════════════════════════════
# D: TestFixtureIntegration — Parametrized over all 63 fixtures
# ══════════════════════════════════════════════════════════════════════


class TestFixtureIntegration:
    """Run normalize_source on every available fixture with invariant checks."""

    @pytest.mark.parametrize("name,path", FIXTURES, ids=[f[0] for f in FIXTURES])
    def test_normalize_source_all_fixtures(self, name: str, path: Path) -> None:
        """Every fixture normalizes with no silent page loss (F1)."""
        is_multi = name in MULTI_LAYER_FIXTURES
        meta = _make_source_metadata(is_multi_layer=is_multi)
        pkg = normalize_source(path, meta)

        assert isinstance(pkg, NormalizedPackage)
        assert len(pkg.content_units) == pkg.manifest.total_content_units
        indices = [cu.unit_index for cu in pkg.content_units]
        assert indices == list(range(len(indices)))
        for cu in pkg.content_units:
            if not cu.content_flags.is_blank:
                assert any("\u0600" <= c <= "\u06FF" for c in cu.primary_text)
        assert len(pkg.manifest.layer_map) >= 1

        # F1: Silent page loss check — count raw PageText divs
        from bs4 import BeautifulSoup

        raw_html = path.read_text(encoding="utf-8")
        raw_page_count = len(
            BeautifulSoup(raw_html, "lxml").find_all("div", class_="PageText")
        )
        assert abs(raw_page_count - len(pkg.content_units)) <= 5, (
            f"Silent page loss: {raw_page_count} raw pages "
            f"-> {len(pkg.content_units)} content units"
        )


# ══════════════════════════════════════════════════════════════════════
# E: TestNormalizeAndWrite — End-to-end write + read
# ══════════════════════════════════════════════════════════════════════


class TestNormalizeAndWrite:
    """End-to-end normalize -> validate -> write -> read-back tests."""

    def test_end_to_end_write_and_read(self, tmp_path: Path) -> None:
        """Shamela normalize_and_write produces valid manifest + content."""
        fixture_path = _get_fixture("01_nahw_simple")
        meta = _make_source_metadata()
        result_dir = normalize_and_write(fixture_path, meta, tmp_path)

        assert (result_dir / "manifest.json").exists()
        assert (result_dir / "content.jsonl").exists()

        with open(result_dir / "manifest.json", encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest["source_id"] == "src_test0001"

        with open(result_dir / "content.jsonl", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        assert len(lines) == manifest["total_content_units"]
        assert "primary_text" in lines[0]

    def test_roundtrip_content_integrity(self, tmp_path: Path) -> None:
        """Written primary_text matches in-memory primary_text exactly."""
        fixture_path = _get_fixture("01_nahw_simple")
        meta = _make_source_metadata()

        pkg = normalize_source(fixture_path, meta)
        first_text = pkg.content_units[0].primary_text

        result_dir = normalize_and_write(fixture_path, meta, tmp_path)
        with open(result_dir / "content.jsonl", encoding="utf-8") as f:
            first_line = json.loads(f.readline())
        assert first_line["primary_text"] == first_text

    def test_plain_text_normalize_and_write(self, tmp_path: Path) -> None:
        """F3 — Session 6 integration: plain text end-to-end write."""
        arabic = (
            "بسم الله الرحمن الرحيم\n\n"
            "الحمد لله رب العالمين\n\n"
            "والصلاة والسلام على رسوله الكريم\n"
        )
        txt_file = tmp_path / "source.txt"
        txt_file.write_text(arabic, encoding="utf-8")

        meta = _make_source_metadata(source_format="plain_text", source_id="pt_test")
        result_dir = normalize_and_write(txt_file, meta, tmp_path)

        assert (result_dir / "manifest.json").exists()
        assert (result_dir / "content.jsonl").exists()

        with open(result_dir / "manifest.json", encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest["source_id"] == "pt_test"
        assert "plain_text" in manifest["normalizer_id"]

        with open(result_dir / "content.jsonl", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        assert len(lines) >= 1
        assert "بسم الله" in lines[0]["primary_text"]


# ══════════════════════════════════════════════════════════════════════
# F: TestAdversarialGap — Remaining core ADV cases
# ══════════════════════════════════════════════════════════════════════


class TestAdversarialGap:
    """Adversarial test cases closing remaining core ADV gaps.

    References: reference/SPEC_ADVERSARY_NORMALIZATION.md
    """

    def test_adv019_unit_index_contiguity(self) -> None:
        """ADV-019: unit_index forms contiguous 0..N-1 on large fixtures."""
        for name in ("02_nahw_muhaqiq", "03_fiqh"):
            path = _get_fixture(name)
            is_multi = name in MULTI_LAYER_FIXTURES
            meta = _make_source_metadata(is_multi_layer=is_multi)
            pkg = normalize_source(path, meta)
            indices = [cu.unit_index for cu in pkg.content_units]
            assert indices == list(range(len(indices))), (
                f"Non-contiguous indices in {name}"
            )

    def test_adv020_duplicate_page_numbers(self, tmp_path: Path) -> None:
        """ADV-020: duplicate page numbers -> unique unit_index values."""
        html = _make_html(
            _wrap_page("حدثنا أبو بكر عن عمر", page_num="12"),
            _wrap_page("قال رسول الله صلى الله عليه وسلم", page_num="12"),
        )
        htm_file = tmp_path / "book.htm"
        htm_file.write_text(html, encoding="utf-8")
        meta = _make_source_metadata()
        pkg = normalize_source(htm_file, meta)

        assert len(pkg.content_units) == 2
        assert pkg.content_units[0].unit_index == 0
        assert pkg.content_units[1].unit_index == 1
        assert pkg.content_units[0].physical_page.page_number_int == 12
        assert pkg.content_units[1].physical_page.page_number_int == 12

    def test_adv022_trailing_diacritics_preserved(self, tmp_path: Path) -> None:
        """ADV-022: trailing kasra (U+0650) preserved in output."""
        text = "بِسْمِ اللَّهِ الرَّحِيمِ"  # ends with kasra U+0650
        html = _make_html(_wrap_page(text, page_num="1"))
        htm_file = tmp_path / "book.htm"
        htm_file.write_text(html, encoding="utf-8")
        meta = _make_source_metadata()
        pkg = normalize_source(htm_file, meta)

        assert "\u0650" in pkg.content_units[0].primary_text

    def test_adv034_universal_footnote_marker(self, tmp_path: Path) -> None:
        """ADV-034: (1) ref replaced with corner brackets when footnote exists."""
        body = "بسم الله (1) وبعد<hr width='95'>(1) هذا تعليق المحقق"
        html = _make_html(_wrap_page(body, page_num="1"))
        htm_file = tmp_path / "book.htm"
        htm_file.write_text(html, encoding="utf-8")
        meta = _make_source_metadata()
        pkg = normalize_source(htm_file, meta)

        primary = pkg.content_units[0].primary_text
        assert "\u231c1\u231d" in primary  # corner brackets around footnote ref
        assert "(1)" not in primary

    def test_adv038_interrupted_write_missing_content(self) -> None:
        """ADV-038: interrupted write with missing content.jsonl.

        Covered by test_writer.py::TestRecoverInterruptedWrite
        ::test_adv047_invalid_temp_restores_from_latest_prev
        which creates temp with manifest but no content.jsonl = missing content.
        """
        pytest.skip(
            "Covered by test_writer.py::TestRecoverInterruptedWrite"
            "::test_adv047_invalid_temp_restores_from_latest_prev — ADV-047"
        )

    def test_adv040_arabic_filename_multi_volume(self, tmp_path: Path) -> None:
        """ADV-040: Arabic filenames handled correctly in multi-volume."""
        html1 = _make_html(_wrap_page("حدثنا أبو بكر", page_num="1"))
        html2 = _make_html(_wrap_page("قال رسول الله", page_num="1"))
        (tmp_path / "\u0627\u0644\u0645\u062c\u0644\u062f_\u0627\u0644\u0623\u0648\u0644.htm").write_text(
            html1, encoding="utf-8"
        )
        (tmp_path / "\u0627\u0644\u0645\u062c\u0644\u062f_\u0627\u0644\u062b\u0627\u0646\u064a.htm").write_text(
            html2, encoding="utf-8"
        )

        meta = _make_source_metadata()
        pkg = normalize_source(tmp_path, meta)

        assert len(pkg.content_units) == 2
        for cu in pkg.content_units:
            assert cu.physical_page.volume is not None
        volumes = sorted(cu.physical_page.volume for cu in pkg.content_units)  # type: ignore[type-var]
        assert volumes == [1, 2]

    def test_adv048_windows_1256_encoding(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """ADV-048: Windows-1256 encoded file triggers fallback with warning."""
        text = "بسم الله الرحمن الرحيم"
        html = _make_html(_wrap_page(text, page_num="1"))
        htm_file = tmp_path / "book.htm"
        htm_file.write_bytes(html.encode("windows-1256"))

        meta = _make_source_metadata()
        with caplog.at_level(logging.WARNING):
            pkg = normalize_source(htm_file, meta)

        assert len(pkg.content_units) >= 1
        assert any(
            "\u0600" <= c <= "\u06FF"
            for c in pkg.content_units[0].primary_text
        )
        assert "NORM_ENCODING_ERROR" in caplog.text

    def test_adv049_page_number_overflow(self, tmp_path: Path) -> None:
        """ADV-049: extremely large page number does not crash."""
        html = _make_html(
            _wrap_page("بسم الله الرحمن الرحيم", page_num="999999999999999")
        )
        htm_file = tmp_path / "book.htm"
        htm_file.write_text(html, encoding="utf-8")
        meta = _make_source_metadata()
        pkg = normalize_source(htm_file, meta)

        assert len(pkg.content_units) >= 1
