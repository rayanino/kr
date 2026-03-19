"""Structure discovery — 4-tier heading detection and division tree construction.

Implements SPEC §4.A.6: identifies the source's internal organizational hierarchy
(headings, chapters, divisions) using a 4-tier confidence architecture.

Tier 1: HTML-tagged headings (CleanedPage.title_spans)
Tier 1.5: TOC parsing and cross-referencing
Tier 2: Keyword heuristic detection from primary_text
Tier 3: LLM semantic judgment (stub — NotImplementedError)

Called from shamela.py._pass4_discover_structure() but designed to be
normalizer-agnostic in tree-building and hierarchy inference.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from engines.normalization.contracts import (
    DivisionNode,
    DivisionType,
    HeadingConfidence,
    HeadingDetectionMethod,
    StructuralMarkers,
)
from engines.normalization.src.errors import NormErrorCode
from engines.normalization.src.normalizers.shamela import CleanedPage, arabic_to_int
from engines.source.contracts import Genre

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────
# Internal data structures (not exported)
# ──────────────────────────────────────────────────────────────────

_YAML_PATH = Path(__file__).parent.parent / "reference" / "structural_patterns.yaml"

CITATION_PREFIXES = [
    "قال في", "ذكر في", "كما في", "انظر", "ارجع إلى",
    "راجع", "في كتاب", "في باب", "في فصل",
    "ورد في", "جاء في", "نقل في",
]

TOC_EXACT_TITLES = frozenset({
    "فهرس", "المحتويات", "فهرس الموضوعات",
    "فهرس المحتويات", "الفهرس", "فهارس",
    "فهرس الكتاب", "محتويات الكتاب",
})

# Layer markers excluded from structural heading detection (handled by Pass 5)
_LAYER_MARKER_KEYWORDS = frozenset({
    "حاشية", "حواشي", "الحاشية", "شرح", "الشرح",
})

# Non-structural supplementary markers
_NON_STRUCTURAL_KEYWORDS = frozenset({
    "تقاريظ", "خطبة",
})

# Indefinite keywords requiring extra evidence (ordinal or short line)
_STRICT_INDEFINITE = frozenset({"كتاب"})

# Diacritics range for stripping in normalize_arabic_for_match
_DIACRITICS = frozenset(
    chr(c) for c in range(0x064B, 0x0656)  # harakat, tanwin, sukun, shadda, etc.
) | {"\u0670"}  # superscript alef


@dataclass
class HeadingCandidate:
    """Intermediate heading found by Tier 1, 1.5, or 2. Not exported."""
    heading_text: str
    unit_index: int
    detection_method: HeadingDetectionMethod
    confidence: HeadingConfidence
    keyword_type: Optional[DivisionType] = None
    keyword_raw: Optional[str] = None
    ordinal: Optional[int] = None
    heading_level: Optional[int] = None
    document_position: int = 0
    is_inline: bool = False


@dataclass
class TOCEntry:
    """A parsed entry from the book's table of contents."""
    title: str
    page_number: Optional[int]
    indent_level: int = 0


@dataclass
class StructureResult:
    """Return type from discover_structure()."""
    division_tree: list[DivisionNode]
    page_markers: dict[int, StructuralMarkers]
    quality_counts: dict[str, int]
    overall_confidence: HeadingConfidence
    toc_page_indices: list[int] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# Utility functions
# ──────────────────────────────────────────────────────────────────

def normalize_arabic_for_match(text: str) -> str:
    """Normalize Arabic text for fuzzy matching/dedup only — never for stored text.

    Strips diacritics, tatweel, ZWNJ/ZWJ, normalizes alef/ya, collapses whitespace.
    """
    out = "".join(c for c in text if c not in _DIACRITICS)
    # Normalize alef variants
    out = out.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("\u0671", "ا")
    # Normalize ya
    out = out.replace("ى", "ي")
    # Strip tatweel (kashida)
    out = out.replace("\u0640", "")
    # Strip ZWNJ and ZWJ
    out = out.replace("\u200c", "").replace("\u200d", "")
    # Collapse whitespace
    out = re.sub(r"\s+", " ", out).strip()
    return out


# ──────────────────────────────────────────────────────────────────
# YAML loading
# ──────────────────────────────────────────────────────────────────

def _load_yaml() -> dict:
    """Load structural_patterns.yaml once."""
    with open(_YAML_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_ordinals(patterns: dict) -> dict[str, int]:
    """Build ordinal lookup from structural_patterns.yaml."""
    ordinals: dict[str, int] = {}
    raw_list = patterns.get("ordinal_patterns", {}).get("arabic_ordinals", [])
    for i, entry in enumerate(raw_list, start=1):
        for variant in entry.split("|"):
            variant = variant.strip()
            if variant:
                ordinals[variant] = i
    return ordinals


def _load_keywords(patterns: dict) -> dict[str, dict]:
    """Build keyword dict from structural_patterns.yaml.

    Excludes layer markers (حاشية, شرح) and non-structural markers (تقاريظ, خطبة).
    Returns dict mapping keyword text -> {level, keyword, ...}.
    """
    keywords: dict[str, dict] = {}
    kp = patterns.get("keyword_patterns", {})

    for level_name, level_data in [
        ("top_level", kp.get("top_level", [])),
        ("mid_level", kp.get("mid_level", [])),
        ("low_level", kp.get("low_level", [])),
        ("supplementary", kp.get("supplementary", [])),
    ]:
        if not isinstance(level_data, list):
            continue
        for entry in level_data:
            kw = entry.get("keyword", "")
            if not kw:
                continue
            # Skip layer markers and non-structural markers
            if kw in _LAYER_MARKER_KEYWORDS or kw in _NON_STRUCTURAL_KEYWORDS:
                continue

            info = {"level": level_name, **entry}
            keywords[kw] = info

            definite = entry.get("definite_form", "")
            if definite and definite != kw:
                if definite not in _LAYER_MARKER_KEYWORDS:
                    keywords[definite] = info

            # Add plural/dual/variants
            for form_key in ("plural", "dual", "variants"):
                forms = entry.get(form_key)
                if isinstance(forms, str):
                    forms = [forms]
                if isinstance(forms, list):
                    for form in forms:
                        if form and form not in _LAYER_MARKER_KEYWORDS:
                            keywords[form] = info

    return keywords


def _build_ordinal_regex(ordinals: dict[str, int]) -> re.Pattern:
    """Build regex matching any Arabic ordinal (longest first)."""
    sorted_ords = sorted(ordinals.keys(), key=len, reverse=True)
    escaped = [re.escape(o) for o in sorted_ords]
    return re.compile(r"(?:" + "|".join(escaped) + r")")


# Map DivisionType enum values to their Arabic keyword text for reverse lookup
_DIVISION_TYPE_KEYWORDS: dict[str, DivisionType] = {
    "كتاب": DivisionType.KITAB,
    "الكتاب": DivisionType.KITAB,
    "باب": DivisionType.BAB,
    "الباب": DivisionType.BAB,
    "فصل": DivisionType.FASL,
    "الفصل": DivisionType.FASL,
    "مبحث": DivisionType.MABHATH,
    "المبحث": DivisionType.MABHATH,
    "مطلب": DivisionType.MATLAB,
    "المطلب": DivisionType.MATLAB,
    "فائدة": DivisionType.FAIDAH,
    "فوائد": DivisionType.FAIDAH,
    "تنبيه": DivisionType.TANBIH,
    "تنبيهات": DivisionType.TANBIH,
    "تنبيهان": DivisionType.TANBIH,
    "قاعدة": DivisionType.QAIDAH,
    "قواعد": DivisionType.QAIDAH,
    "القاعدة": DivisionType.QAIDAH,
    "خاتمة": DivisionType.KHATIMAH,
    "الخاتمة": DivisionType.KHATIMAH,
    "مقدمة": DivisionType.MUQADDIMAH,
    "المقدمة": DivisionType.MUQADDIMAH,
    "المجلد": DivisionType.VOLUME,
    "الجزء": DivisionType.VOLUME,
}

# Keyword type → heading level mapping (NEXT.md hierarchy table)
_KEYWORD_LEVEL: dict[Optional[DivisionType], int] = {
    DivisionType.VOLUME: 0,
    DivisionType.KITAB: 1,
    DivisionType.BAB: 2,
    DivisionType.FASL: 3,
    DivisionType.MABHATH: 4,
    DivisionType.MATLAB: 5,
    DivisionType.FAIDAH: 6,
    DivisionType.TANBIH: 6,
    DivisionType.QAIDAH: 6,
}

# Non-enum keyword_raw → heading level mapping
_RAW_KEYWORD_LEVEL: dict[str, int] = {
    "تقسيم": 3,
    "التقسيم": 3,
    "مدخل": 4,
    "المدخل": 4,
    "إعراب": 4,
    "الإعراب": 4,
    "مسألة": 5,
    "المسألة": 5,
    "فرع": 5,
    "الفرع": 5,
    "تتمة": 6,
}


def _parse_keyword_from_text(
    text: str, keywords: dict[str, dict]
) -> tuple[Optional[DivisionType], Optional[str]]:
    """Parse a structural keyword from heading text.

    Returns (DivisionType or None, raw_keyword or None).
    """
    stripped = text.strip().lstrip("\u200c")
    for kw in sorted(keywords.keys(), key=len, reverse=True):
        if stripped.startswith(kw):
            after = stripped[len(kw):]
            if not after or after[0] in " \t:؛\u200c\n-–—":
                dtype = _DIVISION_TYPE_KEYWORDS.get(kw)
                raw = kw if dtype is None else None
                return dtype, raw
    # Also check without keywords dict — direct enum lookup
    for kw, dtype in sorted(_DIVISION_TYPE_KEYWORDS.items(), key=lambda x: len(x[0]), reverse=True):
        if stripped.startswith(kw):
            after = stripped[len(kw):]
            if not after or after[0] in " \t:؛\u200c\n-–—":
                return dtype, None
    return None, None


# ──────────────────────────────────────────────────────────────────
# Tier 1: HTML-Tagged Heading Extraction
# ──────────────────────────────────────────────────────────────────

def _tier1_html_tagged(
    pages: list[CleanedPage],
    keywords: dict[str, dict],
) -> tuple[list[HeadingCandidate], list[int]]:
    """Extract headings from CleanedPage.title_spans (Tier 1).

    Returns (list of HeadingCandidate, list of TOC page unit_indices).
    """
    candidates: list[HeadingCandidate] = []
    toc_indices: list[int] = []
    doc_pos = 0

    for page in pages:
        for span_idx, raw_text in enumerate(page.title_spans):
            # Strip leading ZWNJ (U+200C) — Session 2 decoded &#8204; entities
            text = raw_text.lstrip("\u200c").strip()
            if not text:
                continue

            # Detect TOC headings
            if text in TOC_EXACT_TITLES:
                toc_indices.append(page.unit_index)

            # Parse keyword type from heading text
            ktype, kraw = _parse_keyword_from_text(text, keywords)

            candidates.append(HeadingCandidate(
                heading_text=text,
                unit_index=page.unit_index,
                detection_method=HeadingDetectionMethod.HTML_TAGGED,
                confidence=HeadingConfidence.CONFIRMED,
                keyword_type=ktype,
                keyword_raw=kraw,
                document_position=doc_pos,
            ))
            doc_pos += 1

    return candidates, toc_indices


# ──────────────────────────────────────────────────────────────────
# Tier 1.5: TOC Parsing and Cross-Referencing
# ──────────────────────────────────────────────────────────────────

_TOC_LINE_RE = re.compile(
    r"^(.+?)\s*[\.·…]{3,}\s*([٠-٩0-9]+)\s*$"
)


def _tier1_5_toc_parse(
    pages: list[CleanedPage],
    toc_unit_indices: list[int],
) -> list[TOCEntry]:
    """Parse dot-leader lines from TOC pages."""
    if not toc_unit_indices:
        return []

    entries: list[TOCEntry] = []
    toc_set = set(toc_unit_indices)
    min_toc = min(toc_set)
    max_toc = max(toc_set)
    scan_end = max_toc + 10

    pages_without_entries = 0

    for page in pages:
        if page.unit_index < min_toc:
            continue
        if page.unit_index > scan_end:
            break

        page_had_entries = False
        lines = page.primary_text.split("\n")
        for line_i, raw_line in enumerate(lines):
            line = raw_line.strip()
            if not line:
                continue

            m = _TOC_LINE_RE.match(line)
            if not m:
                continue

            title = m.group(1).strip()
            page_str = m.group(2)
            try:
                # Handle Arabic-Indic digits
                if any("\u0660" <= c <= "\u0669" for c in page_str):
                    page_num = arabic_to_int(page_str)
                else:
                    page_num = int(page_str)
            except (ValueError, KeyError):
                continue

            # Estimate indent from leading whitespace
            indent = len(raw_line) - len(raw_line.lstrip())
            indent_level = indent // 2

            entries.append(TOCEntry(
                title=title,
                page_number=page_num,
                indent_level=indent_level,
            ))
            page_had_entries = True

        # Density check after last TOC heading
        if page.unit_index > max_toc:
            if page_had_entries:
                pages_without_entries = 0
            else:
                pages_without_entries += 1
                if pages_without_entries >= 3:
                    break

    return entries


def _toc_match_score(toc_title: str, heading_text: str) -> float:
    """Fuzzy match score between TOC entry and heading text."""
    t = normalize_arabic_for_match(toc_title.strip())
    d = normalize_arabic_for_match(heading_text.strip())

    if not t or not d:
        return 0.0
    if t == d:
        return 1.0

    min_len = min(len(t), len(d))
    if min_len < 4:
        return 0.0

    # Prefix match
    prefix_len = 0
    for i in range(min_len):
        if t[i] == d[i]:
            prefix_len += 1
        else:
            break

    max_len = max(len(t), len(d))
    if prefix_len >= 12 or (prefix_len / max_len > 0.5 and prefix_len >= 5):
        return prefix_len / max_len

    # Containment
    if len(t) > 5 and t in d:
        return 0.8
    if len(d) > 5 and d in t:
        return 0.8

    return 0.0


def _tier1_5_toc_crossref(
    candidates: list[HeadingCandidate],
    toc_entries: list[TOCEntry],
    pages: list[CleanedPage],
) -> list[HeadingCandidate]:
    """Cross-reference TOC entries against discovered headings.

    Promotes matching candidates to HIGH confidence; creates new
    TOC_INFERRED candidates for unmatched entries.
    """
    if not toc_entries:
        return candidates

    # Build page_number → unit_index mapping
    page_to_unit: dict[int, int] = {}
    page_numbers_sorted: list[int] = []
    for page in pages:
        if page.page_number_int is not None:
            page_to_unit[page.page_number_int] = page.unit_index
            page_numbers_sorted.append(page.page_number_int)
    page_numbers_sorted.sort()

    def _find_nearest_unit(target_page: int) -> Optional[int]:
        """Find unit_index for nearest page number match."""
        if target_page in page_to_unit:
            return page_to_unit[target_page]
        if not page_numbers_sorted:
            return None
        # Binary search for nearest
        lo, hi = 0, len(page_numbers_sorted) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if page_numbers_sorted[mid] < target_page:
                lo = mid + 1
            else:
                hi = mid
        # Check closest
        best = page_numbers_sorted[lo]
        if lo > 0:
            prev = page_numbers_sorted[lo - 1]
            if abs(prev - target_page) < abs(best - target_page):
                best = prev
        return page_to_unit.get(best)

    new_candidates: list[HeadingCandidate] = []
    doc_pos = max((c.document_position for c in candidates), default=-1) + 1

    for toc in toc_entries:
        if toc.page_number is None:
            continue

        target_unit = _find_nearest_unit(toc.page_number)
        if target_unit is None:
            continue

        # Try to match against existing candidates
        best_score = 0.0
        best_candidate = None
        for c in candidates:
            # Check same page and adjacent pages
            if abs(c.unit_index - target_unit) <= 1:
                score = _toc_match_score(toc.title, c.heading_text)
                if score > best_score:
                    best_score = score
                    best_candidate = c

        if best_score >= 0.4 and best_candidate is not None:
            # Promote confidence
            if best_candidate.confidence == HeadingConfidence.MEDIUM:
                best_candidate.confidence = HeadingConfidence.HIGH
        else:
            # Create new TOC-inferred candidate
            new_candidates.append(HeadingCandidate(
                heading_text=toc.title,
                unit_index=target_unit,
                detection_method=HeadingDetectionMethod.TOC_INFERRED,
                confidence=HeadingConfidence.MEDIUM,
                document_position=doc_pos,
            ))
            doc_pos += 1

    return candidates + new_candidates


# ──────────────────────────────────────────────────────────────────
# Tier 2: Keyword Heuristic Detection
# ──────────────────────────────────────────────────────────────────

# TOC dot-leader rejection pattern
_TOC_DOT_RE = re.compile(r"[\.·]{3,}\s*[٠-٩0-9]+\s*$")
_TOC_ELLIPSIS_RE = re.compile(r"…+\s*[٠-٩0-9]+\s*$")


def _tier2_keyword_scan(
    pages: list[CleanedPage],
    tier1_headings: list[HeadingCandidate],
    keywords: dict[str, dict],
    ordinals: dict[str, int],
) -> list[HeadingCandidate]:
    """Scan primary_text for keyword-based heading candidates (Tier 2).

    Returns new candidates NOT already found by Tier 1.
    """
    ordinal_re = _build_ordinal_regex(ordinals) if ordinals else None

    # Build Tier 1 dedup index
    tier1_index: set[tuple[int, str]] = set()
    for h in tier1_headings:
        norm = normalize_arabic_for_match(h.heading_text)[:30]
        tier1_index.add((h.unit_index, norm))

    # Build keyword regex (sorted by length descending for priority)
    sorted_kws = sorted(keywords.keys(), key=len, reverse=True)
    if not sorted_kws:
        return []
    kw_pattern = re.compile(
        r"^(" + "|".join(re.escape(kw) for kw in sorted_kws) + r")(?=[\s:؛\-–—]|$)"
    )

    candidates: list[HeadingCandidate] = []
    doc_pos = max((h.document_position for h in tier1_headings), default=-1) + 1

    for page in pages:
        lines = page.primary_text.split("\n")
        for line_idx, raw_line in enumerate(lines):
            line = raw_line.strip()
            if not line:
                continue

            # Check for ZWNJ-prefixed heading (double ZWNJ at line start)
            zwnj_prefix = False
            check_line = line
            if line.startswith("\u200c\u200c"):
                zwnj_prefix = True
                check_line = line.lstrip("\u200c").strip()
                if not check_line:
                    continue

            # Keyword match at line start
            m = kw_pattern.match(check_line)
            if not m:
                continue

            matched_keyword = m.group(1)
            rest_after_kw = check_line[m.end():]

            # Skip layer markers that might have leaked through
            if matched_keyword in _LAYER_MARKER_KEYWORDS:
                continue

            # Strict indefinite check (كتاب without ال)
            if matched_keyword in _STRICT_INDEFINITE:
                has_ordinal_check = False
                if ordinal_re:
                    rest_check = rest_after_kw.strip()
                    if rest_check and ordinal_re.match(rest_check):
                        has_ordinal_check = True
                if not has_ordinal_check and len(check_line) > 20:
                    continue

            # TOC entry rejection
            if _TOC_DOT_RE.search(check_line):
                continue
            if _TOC_ELLIPSIS_RE.search(check_line):
                continue

            # Confidence assignment
            confidence = None
            ordinal_value = None
            is_inline = False

            rest_stripped = rest_after_kw.strip()

            # Pattern: KEYWORD ORDINAL[:] TITLE (max 120 chars)
            if ordinal_re and len(check_line) <= 120:
                ord_match = ordinal_re.match(rest_stripped) if rest_stripped else None
                if ord_match:
                    ordinal_text = ord_match.group(0)
                    ordinal_value = ordinals.get(ordinal_text)
                    after_ord = rest_stripped[ord_match.end():].strip()
                    if after_ord and after_ord[0] in ":؛":
                        confidence = HeadingConfidence.HIGH
                    elif not after_ord or len(after_ord) < 3:
                        if len(check_line) <= 60:
                            confidence = HeadingConfidence.HIGH
                    elif len(check_line) <= 120:
                        confidence = HeadingConfidence.HIGH

            # Pattern: KEYWORD في/: TITLE (max 100 chars)
            if confidence is None and len(check_line) <= 100:
                if rest_stripped and rest_stripped[0] in ":؛":
                    confidence = HeadingConfidence.MEDIUM
                elif rest_stripped.startswith("في ") or rest_stripped.startswith("فى "):
                    confidence = HeadingConfidence.MEDIUM

            # Pattern: KEYWORD alone (max 30 chars)
            if confidence is None and len(check_line) <= 30 and not rest_stripped:
                confidence = HeadingConfidence.MEDIUM

            # Pattern: KEYWORD - CONTENT (inline, max 400 chars)
            if confidence is None and len(check_line) <= 400:
                sep_match = re.match(r"\s*[-–—:؛]\s*", rest_after_kw)
                if sep_match:
                    confidence = HeadingConfidence.MEDIUM
                    is_inline = True

            # ZWNJ prefix: keyword match alone is sufficient for HIGH confidence
            if zwnj_prefix and confidence is None:
                confidence = HeadingConfidence.HIGH
            elif zwnj_prefix and confidence == HeadingConfidence.MEDIUM:
                confidence = HeadingConfidence.HIGH

            if confidence is None:
                continue

            # Citation prefix filtering — check preceding line
            if line_idx > 0:
                prev_line = lines[line_idx - 1].strip()
                if prev_line:
                    prev_tail = prev_line[-40:] if len(prev_line) > 40 else prev_line
                    if any(cp in prev_tail for cp in CITATION_PREFIXES):
                        continue

            # Dedup with Tier 1
            norm_title = normalize_arabic_for_match(check_line)[:30]
            if (page.unit_index, norm_title) in tier1_index:
                continue

            # Build heading title
            if is_inline:
                # For inline headings, title is just the keyword part
                sep_m = re.match(r"\s*[-–—:؛]\s*", rest_after_kw)
                if sep_m:
                    title = check_line[:m.end() + sep_m.start()].strip().rstrip("-–—:؛").strip()
                else:
                    title = check_line
            else:
                title = check_line

            # Determine keyword_type and keyword_raw
            ktype = _DIVISION_TYPE_KEYWORDS.get(matched_keyword)
            kraw = matched_keyword if ktype is None else None

            candidates.append(HeadingCandidate(
                heading_text=title,
                unit_index=page.unit_index,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=confidence,
                keyword_type=ktype,
                keyword_raw=kraw,
                ordinal=ordinal_value,
                document_position=doc_pos,
                is_inline=is_inline,
            ))
            doc_pos += 1

    return candidates


# ──────────────────────────────────────────────────────────────────
# Tier 3: LLM Semantic Judgment (stub)
# ──────────────────────────────────────────────────────────────────

def _tier3_llm_discover(
    candidates: list[HeadingCandidate],
    genre: Optional[Genre],
    total_pages: int,
    structure_llm_threshold: int = 3,
    structure_min_pages_for_llm: int = 50,
) -> list[HeadingCandidate]:
    """LLM-assisted structure discovery — STUB.

    Raises NotImplementedError after logging NORM_SPARSE_STRUCTURE
    when the trigger condition is met.
    """
    if (
        len(candidates) < structure_llm_threshold
        and total_pages >= structure_min_pages_for_llm
    ):
        logger.warning(
            "[%s] Sparse structure: %d candidates in %d pages "
            "(threshold: %d candidates, %d pages). "
            "Tier 3 LLM would be invoked here.",
            NormErrorCode.SPARSE_STRUCTURE.value,
            len(candidates),
            total_pages,
            structure_llm_threshold,
            structure_min_pages_for_llm,
        )

    raise NotImplementedError("Tier 3 LLM structure discovery")


# ──────────────────────────────────────────────────────────────────
# Volume Boundary Detection
# ──────────────────────────────────────────────────────────────────

def _detect_volume_boundaries(
    pages: list[CleanedPage],
) -> list[HeadingCandidate]:
    """Detect volume changes and create synthetic volume HeadingCandidates."""
    boundaries: list[HeadingCandidate] = []
    if not pages:
        return boundaries

    prev_volume = pages[0].volume
    for page in pages[1:]:
        if page.volume != prev_volume:
            boundaries.append(HeadingCandidate(
                heading_text=f"المجلد {page.volume}",
                unit_index=page.unit_index,
                detection_method=HeadingDetectionMethod.HTML_TAGGED,
                confidence=HeadingConfidence.CONFIRMED,
                keyword_type=DivisionType.VOLUME,
                heading_level=0,
            ))
        prev_volume = page.volume

    return boundaries


# ──────────────────────────────────────────────────────────────────
# Hierarchy Inference
# ──────────────────────────────────────────────────────────────────

def _infer_hierarchy(
    candidates: list[HeadingCandidate],
) -> list[HeadingCandidate]:
    """Assign heading_level (0-10) to all candidates based on keyword type.

    Modifies candidates in place and returns them.
    """
    if not candidates:
        return candidates

    # Sort by position for context-based inference
    candidates.sort(key=lambda c: (c.unit_index, c.document_position))

    # Phase 1: Assign levels from keyword_type / keyword_raw
    for c in candidates:
        if c.heading_level is not None:
            continue  # Already assigned (e.g., volume boundaries)

        # Try enum-based lookup
        if c.keyword_type is not None and c.keyword_type in _KEYWORD_LEVEL:
            c.heading_level = _KEYWORD_LEVEL[c.keyword_type]
            continue

        # Try raw keyword lookup
        if c.keyword_raw is not None and c.keyword_raw in _RAW_KEYWORD_LEVEL:
            c.heading_level = _RAW_KEYWORD_LEVEL[c.keyword_raw]
            continue

        # Special cases: مقدمة and خاتمة
        if c.keyword_type == DivisionType.MUQADDIMAH:
            # At book start (before any كتاب/باب) → level 2
            # Within a section → same level as preceding division
            preceding_levels = [
                p.heading_level for p in candidates
                if p.unit_index < c.unit_index and p.heading_level is not None
            ]
            if not preceding_levels:
                c.heading_level = 2  # Book-start مقدمة
            else:
                c.heading_level = preceding_levels[-1]
            continue

        if c.keyword_type == DivisionType.KHATIMAH:
            # Same level as surrounding divisions
            preceding_levels = [
                p.heading_level for p in candidates
                if p.unit_index < c.unit_index and p.heading_level is not None
            ]
            if preceding_levels:
                c.heading_level = preceding_levels[-1]
            else:
                c.heading_level = 2
            continue

    # Phase 2: Ordinal sequence siblings — consecutive same-type + sequential ordinals = same level
    for i in range(1, len(candidates)):
        curr = candidates[i]
        prev = candidates[i - 1]
        if (
            curr.heading_level is None
            and prev.heading_level is not None
            and curr.keyword_type is not None
            and curr.keyword_type == prev.keyword_type
            and curr.ordinal is not None
            and prev.ordinal is not None
            and curr.ordinal == prev.ordinal + 1
        ):
            curr.heading_level = prev.heading_level

    # Phase 3: Implicit headings (no keyword match)
    deepest_seen = max(
        (c.heading_level for c in candidates if c.heading_level is not None),
        default=3,
    )

    for i, c in enumerate(candidates):
        if c.heading_level is not None:
            continue

        # Find preceding and following assigned levels
        prev_level = None
        for j in range(i - 1, -1, -1):
            if candidates[j].heading_level is not None:
                prev_level = candidates[j].heading_level
                break

        next_level = None
        for j in range(i + 1, len(candidates)):
            if candidates[j].heading_level is not None:
                next_level = candidates[j].heading_level
                break

        # Rule 1: Between two headings of same level → that level
        if prev_level is not None and next_level is not None and prev_level == next_level:
            c.heading_level = prev_level
        # Rule 2: After level N, before level N+1 → level N
        elif prev_level is not None and next_level is not None and next_level == prev_level + 1:
            c.heading_level = prev_level
        # Rule 3: deepest + 1, capped at 10
        elif prev_level is not None:
            c.heading_level = min(deepest_seen + 1, 10)
        # Rule 4: fallback
        else:
            c.heading_level = 3

    # Post-condition: ALL candidates must have heading_level
    for c in candidates:
        if c.heading_level is None:
            logger.warning(
                "HeadingCandidate at unit_index=%d has None heading_level after "
                "hierarchy inference. Assigning fallback level 3.",
                c.unit_index,
            )
            c.heading_level = 3

    return candidates


# ──────────────────────────────────────────────────────────────────
# Division Tree Construction
# ──────────────────────────────────────────────────────────────────

def _build_division_tree(
    candidates: list[HeadingCandidate],
    total_pages: int,
    source_id: str,
) -> list[DivisionNode]:
    """Build nested DivisionNode tree from hierarchy-annotated candidates.

    Returns list of top-level (root) DivisionNodes with nested children.
    """
    if total_pages == 0:
        return []

    # Zero-heading fallback
    if not candidates:
        return [DivisionNode(
            div_id=f"div_{source_id}_0_000",
            division_type=DivisionType.ROOT,
            heading_text="[untitled]",
            heading_level=1,
            start_unit_index=0,
            end_unit_index=total_pages - 1,
            detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
            confidence=HeadingConfidence.LOW,
            children=[],
        )]

    # Sort by position
    sorted_cands = sorted(candidates, key=lambda c: (c.unit_index, c.document_position))

    # Dedup exact duplicates (same page, same normalized title prefix)
    deduped: list[HeadingCandidate] = []
    seen: set[tuple[int, str]] = set()
    for c in sorted_cands:
        key = (c.unit_index, normalize_arabic_for_match(c.heading_text)[:40])
        if key not in seen:
            seen.add(key)
            deduped.append(c)

    # Build flat list of DivisionNodes
    level_counters: dict[int, int] = {}
    nodes: list[DivisionNode] = []

    for c in deduped:
        level = c.heading_level if c.heading_level is not None else 3
        level_counters[level] = level_counters.get(level, 0)
        idx = level_counters[level]
        level_counters[level] += 1

        div_id = f"div_{source_id}_{level}_{idx:03d}"
        ktype = c.keyword_type
        # Non-enum keywords → division_type=None
        if ktype is None and c.keyword_raw is not None:
            ktype = None

        node = DivisionNode(
            div_id=div_id,
            division_type=ktype,
            heading_text=c.heading_text,
            heading_level=level,
            start_unit_index=c.unit_index,
            end_unit_index=c.unit_index,  # placeholder
            detection_method=c.detection_method,
            confidence=c.confidence,
            children=[],
        )
        nodes.append(node)

    # Build parent-child relationships using heading_level
    # Lower level = higher in hierarchy = potential parent
    root_nodes: list[DivisionNode] = []
    stack: list[DivisionNode] = []  # Stack of ancestors (most recent at end)

    for node in nodes:
        # Pop stack until we find a suitable parent (lower level)
        last_popped: Optional[DivisionNode] = None
        while stack and stack[-1].heading_level >= node.heading_level:
            last_popped = stack.pop()

        # Same-page sibling resolution (§5 check 5 overlap prevention):
        # If we just popped a node at the same level on the same page,
        # chain the current node as a child of the deepest same-page descendant.
        # This prevents sibling overlap when multiple headings share a page.
        if (
            last_popped is not None
            and last_popped.heading_level == node.heading_level
            and last_popped.start_unit_index == node.start_unit_index
        ):
            # Find deepest same-page same-level descendant for linear chaining
            target = last_popped
            while target.children:
                last_child = target.children[-1]
                if (
                    last_child.heading_level == node.heading_level
                    and last_child.start_unit_index == node.start_unit_index
                ):
                    target = last_child
                else:
                    break
            target.children.append(node)
            stack.append(last_popped)
            stack.append(node)
        elif stack:
            stack[-1].children.append(node)
            stack.append(node)
        else:
            root_nodes.append(node)
            stack.append(node)

    # Compute page ranges
    _compute_ranges(root_nodes, total_pages - 1)

    # Full coverage enforcement: extend first root to page 0
    if root_nodes and root_nodes[0].start_unit_index > 0:
        root_nodes[0].start_unit_index = 0

    # Iterative containment enforcement (max 5 iterations)
    for _ in range(5):
        detached = _enforce_containment(root_nodes)
        if detached == 0:
            break
        _compute_ranges(root_nodes, total_pages - 1)

    return root_nodes


def _compute_ranges(nodes: list[DivisionNode], max_end: int) -> None:
    """Compute page ranges for a list of sibling nodes and their children."""
    for i, node in enumerate(nodes):
        # Sibling range: from start to next sibling's start - 1
        if i + 1 < len(nodes):
            node.end_unit_index = max(
                node.start_unit_index,
                nodes[i + 1].start_unit_index - 1,
            )
        else:
            node.end_unit_index = max_end

        # Clamp
        node.end_unit_index = min(node.end_unit_index, max_end)
        node.end_unit_index = max(node.end_unit_index, node.start_unit_index)

        # Recurse into children
        if node.children:
            _compute_ranges(node.children, node.end_unit_index)


def _enforce_containment(nodes: list[DivisionNode]) -> int:
    """Verify children are within parent bounds. Detach violators. Returns count."""
    detached = 0
    for node in nodes:
        valid_children: list[DivisionNode] = []
        for child in node.children:
            if (
                child.start_unit_index < node.start_unit_index
                or child.start_unit_index > node.end_unit_index
            ):
                detached += 1
                logger.debug(
                    "Detaching %s from %s: child starts at %d, parent range [%d-%d]",
                    child.div_id, node.div_id,
                    child.start_unit_index, node.start_unit_index, node.end_unit_index,
                )
            else:
                valid_children.append(child)
        node.children = valid_children
        # Recurse
        detached += _enforce_containment(node.children)
    return detached


# ──────────────────────────────────────────────────────────────────
# Confidence Scoring
# ──────────────────────────────────────────────────────────────────

def _count_all_divisions(nodes: list[DivisionNode]) -> list[DivisionNode]:
    """Flatten tree into list of all nodes."""
    result: list[DivisionNode] = []
    for node in nodes:
        result.append(node)
        result.extend(_count_all_divisions(node.children))
    return result


def _compute_confidence(
    divisions: list[DivisionNode],
    total_pages: int,
) -> HeadingConfidence:
    """Compute overall structure confidence per SPEC §4.A.6 thresholds."""
    all_divs = _count_all_divisions(divisions)
    total = len(all_divs)

    if total == 0:
        return HeadingConfidence.MINIMAL

    # Single ROOT fallback node
    if total == 1 and all_divs[0].division_type == DivisionType.ROOT:
        return HeadingConfidence.MINIMAL

    # Sparse: <3 divisions in 50+ pages
    if total < 3 and total_pages >= 50:
        logger.warning(
            "[%s] Sparse structure: %d divisions in %d pages.",
            NormErrorCode.SPARSE_STRUCTURE.value,
            total,
            total_pages,
        )
        return HeadingConfidence.MINIMAL

    # Count high-confidence divisions
    high_conf_count = sum(
        1 for d in all_divs
        if d.confidence in (HeadingConfidence.CONFIRMED, HeadingConfidence.HIGH)
    )
    ratio = high_conf_count / total

    if ratio > 0.80:
        return HeadingConfidence.HIGH
    elif ratio >= 0.50:
        return HeadingConfidence.MEDIUM
    else:
        return HeadingConfidence.LOW


# ──────────────────────────────────────────────────────────────────
# Page Markers
# ──────────────────────────────────────────────────────────────────

def _build_page_markers(
    candidates: list[HeadingCandidate],
) -> dict[int, StructuralMarkers]:
    """Build per-page StructuralMarkers from the first candidate on each page."""
    markers: dict[int, StructuralMarkers] = {}

    # Group by unit_index, pick first (lowest document_position)
    by_page: dict[int, list[HeadingCandidate]] = {}
    for c in candidates:
        by_page.setdefault(c.unit_index, []).append(c)

    for unit_idx, page_cands in by_page.items():
        first = min(page_cands, key=lambda c: c.document_position)
        markers[unit_idx] = StructuralMarkers(
            heading_detected=True,
            heading_text=first.heading_text,
            heading_level=first.heading_level,
            heading_detection_method=first.detection_method,
            heading_confidence=first.confidence,
        )

    return markers


# ──────────────────────────────────────────────────────────────────
# Orchestrator
# ──────────────────────────────────────────────────────────────────

def discover_structure(
    pages: list[CleanedPage],
    source_id: str,
    genre: Optional[Genre],
) -> StructureResult:
    """Orchestrator: run 4-tier heading detection and build division tree.

    Args:
        pages: CleanedPage output from Passes 1–3.
        source_id: Source identifier for div_id generation.
        genre: Source genre (passed to Tier 3 stub).

    Returns:
        StructureResult with division_tree, page_markers, quality_counts,
        and overall_confidence.
    """
    # Load patterns
    yaml_data = _load_yaml()
    keywords = _load_keywords(yaml_data)
    ordinals = _load_ordinals(yaml_data)

    # Tier 1: HTML-tagged headings
    tier1_candidates, toc_indices = _tier1_html_tagged(pages, keywords)

    # Tier 1.5: TOC parsing and cross-referencing
    toc_entries = _tier1_5_toc_parse(pages, toc_indices)
    all_candidates = _tier1_5_toc_crossref(tier1_candidates, toc_entries, pages)

    # Tier 2: Keyword heuristic scan
    tier2_candidates = _tier2_keyword_scan(pages, all_candidates, keywords, ordinals)
    all_candidates = all_candidates + tier2_candidates

    # Tier 3: LLM discovery (stub — catches NotImplementedError)
    try:
        tier3_candidates = _tier3_llm_discover(
            all_candidates, genre, len(pages),
        )
        all_candidates = all_candidates + tier3_candidates
    except NotImplementedError:
        pass  # Expected — Tier 3 not yet implemented

    # Volume boundary detection (before hierarchy inference)
    volume_candidates = _detect_volume_boundaries(pages)
    all_candidates = all_candidates + volume_candidates

    # Hierarchy inference — assign heading_level to all candidates
    all_candidates = _infer_hierarchy(all_candidates)

    # Build division tree
    division_tree = _build_division_tree(all_candidates, len(pages), source_id)

    # Compute overall confidence
    overall_confidence = _compute_confidence(division_tree, len(pages))

    # Build page markers
    page_markers = _build_page_markers(all_candidates)

    # Count divisions by confidence tier
    all_divs = _count_all_divisions(division_tree)
    quality_counts: dict[str, int] = {}
    for d in all_divs:
        tier = d.confidence.value
        quality_counts[tier] = quality_counts.get(tier, 0) + 1

    return StructureResult(
        division_tree=division_tree,
        page_markers=page_markers,
        quality_counts=quality_counts,
        overall_confidence=overall_confidence,
        toc_page_indices=toc_indices,
    )
