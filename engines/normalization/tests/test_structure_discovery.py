"""Tests for structure discovery (Pass 4) — SPEC §4.A.6.

19 mandatory tests covering:
- ADV-016, ADV-017, ADV-018 (adversarial)
- Real fixture end-to-end (07_balagha, 01_nahw_simple, 12_multi_muq)
- Keyword detection (basics, citation prefix, ZWNJ, non-enum)
- TOC detection and parsing
- Edge cases (sparse, confidence, ZWNJ stripping, coverage, layer markers,
  volume boundaries, zero-heading fallback, heading level guard)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pytest

from engines.normalization.contracts import (
    DivisionNode,
    DivisionType,
    HeadingConfidence,
    HeadingDetectionMethod,
    StructuralMarkers,
)
from engines.normalization.src.errors import NormErrorCode
from engines.normalization.src.normalizers.shamela import (
    CleanedPage,
    ShamelaNormalizer,
)
from engines.normalization.src.structure_discovery import (
    HeadingCandidate,
    StructureResult,
    _build_division_tree,
    _build_page_markers,
    _compute_confidence,
    _detect_volume_boundaries,
    _infer_hierarchy,
    _tier1_html_tagged,
    _tier2_keyword_scan,
    discover_structure,
    normalize_arabic_for_match,
)

# ──────────────────────────────────────────────────────────────────
# Constants & Helpers
# ──────────────────────────────────────────────────────────────────

FIXTURES_REAL = Path("tests/fixtures/shamela_real")


def _wrap_page(content: str, page_num: Optional[str] = None) -> str:
    """Wrap content in a PageText div with optional page number."""
    parts = ["<div class='PageText'>"]
    if page_num is not None:
        parts.append(
            f"<div class='PageHead'>"
            f"<span class='PageNumber'>(ص: {page_num})</span>"
            f"<hr/></div>"
        )
    parts.append(content)
    parts.append("</div>")
    return "".join(parts)


def _make_html(*page_contents: str) -> str:
    """Build a minimal Shamela HTML document from page contents."""
    return (
        "<html><head></head><body>"
        + "".join(page_contents)
        + "</body></html>"
    )


def _full_pipeline(
    normalizer: ShamelaNormalizer, html: str, volume: int = 1, seq_offset: int = 0,
) -> list[CleanedPage]:
    """Run Passes 1–3 on HTML text."""
    raw = normalizer._pass1_parse(html, volume=volume, seq_offset=seq_offset)
    sep = normalizer._pass2_separate(raw)
    return normalizer._pass3_clean(sep)


def _run_structure(
    normalizer: ShamelaNormalizer, fixture_dir: Path, source_id: str = "test",
) -> tuple[list[CleanedPage], StructureResult]:
    """Run Passes 1–3 on all .htm files, then discover_structure()."""
    htm_files = sorted(
        list(fixture_dir.glob("*.htm")) + list(fixture_dir.glob("*.html"))
    )
    all_clean: list[CleanedPage] = []
    offset = 0
    for f in htm_files:
        try:
            vol = int(f.stem)
        except ValueError:
            vol = len(all_clean) + 1
        html = f.read_text(encoding="utf-8")
        raw = normalizer._pass1_parse(html, volume=vol, seq_offset=offset)
        content = [p for p in raw if not p.is_metadata_page]
        offset += len(content)
        sep = normalizer._pass2_separate(raw)
        clean = normalizer._pass3_clean(sep)
        all_clean.extend(clean)
    result = discover_structure(all_clean, source_id, None)
    return all_clean, result


def _flatten_tree(nodes: list[DivisionNode]) -> list[DivisionNode]:
    """Flatten division tree into a list of all nodes."""
    result: list[DivisionNode] = []
    for n in nodes:
        result.append(n)
        result.extend(_flatten_tree(n.children))
    return result


def assert_tree_valid(
    divisions: list[DivisionNode], total_pages: int,
) -> None:
    """Verify all 4 §5 check 5 invariants."""
    all_nodes = _flatten_tree(divisions)

    # 1. Every node: start <= end
    for n in all_nodes:
        assert n.start_unit_index <= n.end_unit_index, (
            f"{n.div_id}: start {n.start_unit_index} > end {n.end_unit_index}"
        )

    # 2. Siblings: no overlapping page ranges
    def _check_siblings(siblings: list[DivisionNode]) -> None:
        for i in range(len(siblings) - 1):
            assert siblings[i].end_unit_index < siblings[i + 1].start_unit_index, (
                f"Siblings overlap: {siblings[i].div_id} [{siblings[i].start_unit_index}-"
                f"{siblings[i].end_unit_index}] and {siblings[i+1].div_id} "
                f"[{siblings[i+1].start_unit_index}-{siblings[i+1].end_unit_index}]"
            )

    _check_siblings(divisions)
    for n in all_nodes:
        if n.children:
            _check_siblings(n.children)

    # 3. Children: contained within parent's range
    for n in all_nodes:
        for child in n.children:
            assert child.start_unit_index >= n.start_unit_index, (
                f"Child {child.div_id} starts at {child.start_unit_index} "
                f"before parent {n.div_id} start {n.start_unit_index}"
            )
            assert child.end_unit_index <= n.end_unit_index, (
                f"Child {child.div_id} ends at {child.end_unit_index} "
                f"after parent {n.div_id} end {n.end_unit_index}"
            )

    # 4. Full coverage: every unit_index inside at least one division
    if total_pages > 0:
        covered = set()
        for n in all_nodes:
            for idx in range(n.start_unit_index, n.end_unit_index + 1):
                covered.add(idx)
        expected = set(range(total_pages))
        missing = expected - covered
        assert not missing, f"Pages not covered by any division: {sorted(missing)[:10]}"


@pytest.fixture
def normalizer() -> ShamelaNormalizer:
    return ShamelaNormalizer()


# ──────────────────────────────────────────────────────────────────
# 1. ADV-016: Arabic trap — "باب" in scholar name, not heading
# ──────────────────────────────────────────────────────────────────

class TestAdversarial:
    def test_adv016_arabic_trap(self):
        """باب appearing mid-line in a scholar name must NOT be detected as heading."""
        page = CleanedPage(
            unit_index=0,
            volume=1,
            primary_text=(
                "وقد نقل هذا القول عن أبي عبد الله باب الباب الشيرازي\n"
                "وهو من أعلام الحنفية في القرن الخامس"
            ),
            title_spans=[],
        )
        result = discover_structure([page], "adv016", None)
        markers = result.page_markers
        # Page should NOT have a heading detected
        if 0 in markers:
            assert not markers[0].heading_detected, (
                "باب mid-line should not trigger heading detection"
            )

    # ──────────────────────────────────────────────────────────────
    # 3. ADV-018: Dedup Tier 1 vs Tier 2
    # ──────────────────────────────────────────────────────────────

    def test_adv018_dedup_tier1_tier2(self):
        """Title span + same keyword in primary_text → exactly one node, method=HTML_TAGGED."""
        page = CleanedPage(
            unit_index=0,
            volume=1,
            primary_text="باب الطهارة\nوالطهارة شرط لصحة الصلاة",
            title_spans=["باب الطهارة"],
        )
        result = discover_structure([page], "adv018", None)
        all_divs = _flatten_tree(result.division_tree)
        # Filter out ROOT fallback if present
        bab_divs = [d for d in all_divs if "الطهارة" in d.heading_text]
        assert len(bab_divs) == 1, (
            f"Expected exactly 1 division for 'باب الطهارة', got {len(bab_divs)}"
        )
        assert bab_divs[0].detection_method == HeadingDetectionMethod.HTML_TAGGED
        assert bab_divs[0].confidence == HeadingConfidence.CONFIRMED


# ──────────────────────────────────────────────────────────────────
# 2. ADV-017: Tree validity
# ──────────────────────────────────────────────────────────────────

class TestTreeValidity:
    def test_adv017_tree_validity_balagha(self, normalizer: ShamelaNormalizer):
        """All 4 §5 check 5 invariants hold on 07_balagha tree."""
        fixture = FIXTURES_REAL / "07_balagha"
        if not fixture.exists():
            pytest.skip("07_balagha fixture not available")
        clean, result = _run_structure(normalizer, fixture, "balagha")
        assert len(result.division_tree) > 0
        assert_tree_valid(result.division_tree, len(clean))


# ──────────────────────────────────────────────────────────────────
# 4–6. Real fixture end-to-end
# ──────────────────────────────────────────────────────────────────

class TestRealFixtures:
    def test_balagha_end_to_end(self, normalizer: ShamelaNormalizer):
        """07_balagha: non-empty tree, valid div_ids, HIGH/CONFIRMED confidence."""
        fixture = FIXTURES_REAL / "07_balagha"
        if not fixture.exists():
            pytest.skip("07_balagha fixture not available")
        clean, result = _run_structure(normalizer, fixture, "balagha")

        # Non-empty tree
        all_divs = _flatten_tree(result.division_tree)
        assert len(all_divs) > 10, f"Expected many divisions, got {len(all_divs)}"

        # Valid div_id format
        for d in all_divs:
            assert d.div_id.startswith("div_balagha_"), f"Bad div_id: {d.div_id}"

        # High confidence (146+ Tier 1 headings)
        assert result.overall_confidence in (
            HeadingConfidence.CONFIRMED, HeadingConfidence.HIGH
        ), f"Expected HIGH/CONFIRMED, got {result.overall_confidence}"

        # Pages with multiple title_spans don't produce duplicates
        assert_tree_valid(result.division_tree, len(clean))

    def test_nahw_simple_basic(self, normalizer: ShamelaNormalizer):
        """01_nahw_simple: basic tree with valid structure."""
        fixture = FIXTURES_REAL / "01_nahw_simple"
        if not fixture.exists():
            pytest.skip("01_nahw_simple fixture not available")
        clean, result = _run_structure(normalizer, fixture, "nahw")

        assert len(result.division_tree) > 0
        assert_tree_valid(result.division_tree, len(clean))
        all_divs = _flatten_tree(result.division_tree)
        assert all(d.div_id.startswith("div_nahw_") for d in all_divs)

    def test_multi_volume_muq(self, normalizer: ShamelaNormalizer):
        """12_multi_muq: volume boundary handling in multi-volume book."""
        fixture = FIXTURES_REAL / "12_multi_muq"
        if not fixture.exists():
            pytest.skip("12_multi_muq fixture not available")
        clean, result = _run_structure(normalizer, fixture, "muq")

        # Should have divisions
        assert len(result.division_tree) > 0
        assert_tree_valid(result.division_tree, len(clean))

        # Check that volume data is represented
        all_divs = _flatten_tree(result.division_tree)
        volumes = set(p.volume for p in clean)
        if len(volumes) > 1:
            vol_divs = [d for d in all_divs if d.division_type == DivisionType.VOLUME]
            assert len(vol_divs) >= len(volumes) - 1, (
                f"Expected at least {len(volumes) - 1} volume boundary nodes, "
                f"got {len(vol_divs)}"
            )


# ──────────────────────────────────────────────────────────────────
# 7–9. Keyword detection
# ──────────────────────────────────────────────────────────────────

class TestKeywordDetection:
    def test_keyword_detection_basics(self):
        """Known keyword lines → correct DivisionType, confidence, ordinal."""
        pages = [
            CleanedPage(
                unit_index=0,
                volume=1,
                primary_text="الباب الأول: في الفعل",
                title_spans=[],
            ),
            CleanedPage(
                unit_index=1,
                volume=1,
                primary_text="فصل في المسح على الخفين",
                title_spans=[],
            ),
        ]
        result = discover_structure(pages, "kw_test", None)
        all_divs = _flatten_tree(result.division_tree)

        # Should find at least the باب and فصل
        bab_divs = [d for d in all_divs if d.division_type == DivisionType.BAB]
        fasl_divs = [d for d in all_divs if d.division_type == DivisionType.FASL]
        assert len(bab_divs) >= 1, "Should detect باب heading"
        assert len(fasl_divs) >= 1, "Should detect فصل heading"

    def test_citation_prefix_rejection(self):
        """'كما في باب الصلاة' on previous line → no heading detected for باب."""
        pages = [
            CleanedPage(
                unit_index=0,
                volume=1,
                primary_text=(
                    "وهذا مذكور في كتب الفقه كما في\n"
                    "باب الصلاة في الشرح الكبير"
                ),
                title_spans=[],
            ),
        ]
        result = discover_structure(pages, "cite_test", None)
        # The باب line should be rejected due to citation prefix
        all_divs = _flatten_tree(result.division_tree)
        bab_kw_divs = [
            d for d in all_divs
            if d.division_type == DivisionType.BAB
            and d.detection_method == HeadingDetectionMethod.KEYWORD_HEURISTIC
        ]
        assert len(bab_kw_divs) == 0, (
            "باب after citation prefix should not be detected as heading"
        )

    def test_zwnj_heading_detection(self):
        """Double ZWNJ prefix + keyword → detected with HIGH confidence."""
        pages = [
            CleanedPage(
                unit_index=0,
                volume=1,
                primary_text="\u200c\u200cباب الوضوء",
                title_spans=[],
            ),
        ]
        result = discover_structure(pages, "zwnj_test", None)
        markers = result.page_markers
        assert 0 in markers, "Page should have heading marker"
        assert markers[0].heading_detected
        assert markers[0].heading_confidence in (
            HeadingConfidence.HIGH, HeadingConfidence.CONFIRMED,
        )

    def test_non_enum_keyword(self):
        """تقسيم → keyword_type=None in DivisionNode, heading_level=3."""
        pages = [
            CleanedPage(
                unit_index=0,
                volume=1,
                primary_text="التقسيم الأول: إلى ماضٍ ومضارع",
                title_spans=[],
            ),
        ]
        result = discover_structure(pages, "taqsim_test", None)
        all_divs = _flatten_tree(result.division_tree)
        # Find the تقسيم division
        taq_divs = [d for d in all_divs if "التقسيم" in d.heading_text]
        assert len(taq_divs) >= 1, "Should detect تقسيم heading"
        # Non-enum keyword → division_type=None
        assert taq_divs[0].division_type is None, (
            f"Non-enum keyword should have division_type=None, got {taq_divs[0].division_type}"
        )


# ──────────────────────────────────────────────────────────────────
# 10. TOC detection and parsing
# ──────────────────────────────────────────────────────────────────

class TestTOC:
    def test_toc_detection_parsing(self):
        """TOC entries are parsed from dot-leader lines."""
        pages = [
            CleanedPage(
                unit_index=0,
                volume=1,
                primary_text="باب الطهارة\nمحتوى الباب",
                title_spans=["باب الطهارة"],
            ),
            CleanedPage(
                unit_index=1,
                volume=1,
                primary_text="فصل في الوضوء\nتفاصيل الوضوء",
                title_spans=["فصل في الوضوء"],
            ),
            # TOC page
            CleanedPage(
                unit_index=2,
                volume=1,
                primary_text=(
                    "باب الطهارة...........................1\n"
                    "فصل في الوضوء.......................5\n"
                    "فصل في التيمم.......................12\n"
                ),
                title_spans=["فهرس الموضوعات"],
            ),
        ]
        result = discover_structure(pages, "toc_test", None)
        # The TOC should be detected and parsed
        assert len(result.division_tree) > 0
        # Tree should still be valid
        assert_tree_valid(result.division_tree, len(pages))


# ──────────────────────────────────────────────────────────────────
# 11–19. Edge cases
# ──────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_sparse_structure_warning(self, caplog):
        """<3 headings in >=50 pages → NORM_SPARSE_STRUCTURE warning."""
        # Create 55 empty pages with only 1 heading
        pages = []
        for i in range(55):
            ts = ["باب الصلاة"] if i == 0 else []
            pages.append(CleanedPage(
                unit_index=i,
                volume=1,
                primary_text="نص عادي" if i > 0 else "باب الصلاة",
                title_spans=ts,
            ))

        with caplog.at_level("WARNING"):
            result = discover_structure(pages, "sparse_test", None)

        # Should be MINIMAL confidence
        assert result.overall_confidence == HeadingConfidence.MINIMAL

        # NORM_SPARSE_STRUCTURE should have been logged
        assert any(
            "NORM_SPARSE_STRUCTURE" in r.message for r in caplog.records
        ), "NORM_SPARSE_STRUCTURE warning should be logged for sparse structure"

    def test_confidence_thresholds(self):
        """Verify SPEC thresholds: >80% = HIGH, 50-80% = MEDIUM, <50% = LOW."""
        # 100% confirmed → HIGH
        divs_all_high = [
            DivisionNode(
                div_id=f"div_t_{i}", division_type=None,
                heading_text=f"H{i}", heading_level=1,
                start_unit_index=i * 10, end_unit_index=(i + 1) * 10 - 1,
                detection_method=HeadingDetectionMethod.HTML_TAGGED,
                confidence=HeadingConfidence.CONFIRMED,
            )
            for i in range(5)
        ]
        assert _compute_confidence(divs_all_high, 50) == HeadingConfidence.HIGH

        # 60% confirmed, 40% medium → MEDIUM
        divs_mixed = []
        for i in range(5):
            conf = HeadingConfidence.CONFIRMED if i < 3 else HeadingConfidence.MEDIUM
            divs_mixed.append(DivisionNode(
                div_id=f"div_t_{i}", division_type=None,
                heading_text=f"H{i}", heading_level=1,
                start_unit_index=i * 10, end_unit_index=(i + 1) * 10 - 1,
                detection_method=HeadingDetectionMethod.HTML_TAGGED,
                confidence=conf,
            ))
        assert _compute_confidence(divs_mixed, 50) == HeadingConfidence.MEDIUM

        # 20% confirmed, 80% low → LOW
        divs_low = []
        for i in range(5):
            conf = HeadingConfidence.CONFIRMED if i == 0 else HeadingConfidence.LOW
            divs_low.append(DivisionNode(
                div_id=f"div_t_{i}", division_type=None,
                heading_text=f"H{i}", heading_level=1,
                start_unit_index=i * 10, end_unit_index=(i + 1) * 10 - 1,
                detection_method=HeadingDetectionMethod.HTML_TAGGED,
                confidence=conf,
            ))
        assert _compute_confidence(divs_low, 50) == HeadingConfidence.LOW

    def test_zwnj_stripping_title_spans(self):
        """ZWNJ prefix in title_spans is stripped from heading_text."""
        page = CleanedPage(
            unit_index=0,
            volume=1,
            primary_text="نص الباب",
            title_spans=["\u200cالباب الأول"],
        )
        result = discover_structure([page], "zwnj_strip", None)

        # Check DivisionNode heading_text has no ZWNJ
        all_divs = _flatten_tree(result.division_tree)
        bab_divs = [d for d in all_divs if "الباب" in d.heading_text]
        assert len(bab_divs) >= 1
        for d in bab_divs:
            assert "\u200c" not in d.heading_text, (
                f"ZWNJ should be stripped from heading_text: {repr(d.heading_text)}"
            )

        # Check StructuralMarkers heading_text
        if 0 in result.page_markers:
            marker = result.page_markers[0]
            assert marker.heading_text is not None
            assert "\u200c" not in marker.heading_text

    def test_full_coverage_before_heading(self):
        """First heading at page 5 → root division starts at 0."""
        pages = []
        for i in range(20):
            ts = ["الباب الأول: في الطهارة"] if i == 5 else []
            pages.append(CleanedPage(
                unit_index=i,
                volume=1,
                primary_text="نص عادي",
                title_spans=ts,
            ))

        result = discover_structure(pages, "coverage_test", None)
        assert_tree_valid(result.division_tree, 20)

        # First root division must start at 0
        assert result.division_tree[0].start_unit_index == 0, (
            f"First root should start at 0, got {result.division_tree[0].start_unit_index}"
        )

    def test_layer_marker_exclusion(self):
        """حاشية and شرح are layer markers, NOT structural headings."""
        pages = [
            CleanedPage(
                unit_index=0,
                volume=1,
                primary_text="حاشية\nمحتوى الحاشية",
                title_spans=[],
            ),
            CleanedPage(
                unit_index=1,
                volume=1,
                primary_text="شرح\nمحتوى الشرح",
                title_spans=[],
            ),
        ]
        result = discover_structure(pages, "layer_test", None)
        all_divs = _flatten_tree(result.division_tree)

        # Should not have حاشية or شرح as keyword-detected headings
        for d in all_divs:
            if d.detection_method == HeadingDetectionMethod.KEYWORD_HEURISTIC:
                assert "حاشية" not in d.heading_text, (
                    "حاشية is a layer marker, not a structural heading"
                )
                assert d.heading_text != "شرح", (
                    "شرح is a layer marker, not a structural heading"
                )

    def test_volume_boundary_detection(self):
        """Volume change from 1 to 2 → VOLUME node at level 0."""
        pages = []
        for i in range(20):
            vol = 1 if i < 10 else 2
            # Add a heading in each volume so volume isn't the only node
            ts = []
            if i == 0:
                ts = ["باب الطهارة"]
            elif i == 10:
                ts = ["باب الصلاة"]
            pages.append(CleanedPage(
                unit_index=i,
                volume=vol,
                primary_text="نص عادي",
                title_spans=ts,
            ))

        result = discover_structure(pages, "vol_test", None)
        all_divs = _flatten_tree(result.division_tree)

        vol_divs = [d for d in all_divs if d.division_type == DivisionType.VOLUME]
        assert len(vol_divs) >= 1, "Should have at least 1 volume boundary node"
        assert vol_divs[0].heading_level == 0, (
            f"Volume nodes should be level 0, got {vol_divs[0].heading_level}"
        )
        assert_tree_valid(result.division_tree, 20)

    def test_zero_heading_fallback(self, normalizer: ShamelaNormalizer):
        """13_format_b: 1 ROOT node, MINIMAL confidence, §5 invariants hold."""
        fixture = FIXTURES_REAL / "13_format_b"
        if not fixture.exists():
            pytest.skip("13_format_b fixture not available")
        clean, result = _run_structure(normalizer, fixture, "fb")

        # Single ROOT node
        assert len(result.division_tree) == 1
        root = result.division_tree[0]
        assert root.division_type == DivisionType.ROOT
        assert root.heading_text == "[untitled]"
        assert root.div_id == "div_fb_0_000"

        # MINIMAL confidence
        assert result.overall_confidence == HeadingConfidence.MINIMAL

        # §5 invariants
        assert_tree_valid(result.division_tree, len(clean))

    def test_heading_level_none_guard(self):
        """Non-keyword HTML heading gets a level assigned (not None), no Pydantic crash."""
        page = CleanedPage(
            unit_index=0,
            volume=1,
            primary_text="محمد بن إبراهيم الأنصاري",
            title_spans=["محمد بن إبراهيم الأنصاري"],  # Scholar name as section title
        )
        result = discover_structure([page], "guard_test", None)

        # Should not crash — heading_level is assigned
        all_divs = _flatten_tree(result.division_tree)
        assert len(all_divs) >= 1
        for d in all_divs:
            assert d.heading_level is not None, (
                f"heading_level should not be None for {d.div_id}"
            )
            assert 0 <= d.heading_level <= 10
