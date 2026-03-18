"""Shamela HTML normalizer — SPEC §4.A.2.

Transforms Shamela desktop HTML exports into intermediate data structures
(RawPage → SeparatedPage → CleanedPage) via a 3-pass pipeline.
Passes 4–6 (structure discovery, layer detection, output assembly) are
implemented in Sessions 3–5.

ABD code location: reference/archive/abd_code/normalization/normalize_shamela.py
Shamela HTML reference: engines/normalization/reference/SHAMELA_HTML_REFERENCE.md

Processing pipeline (6 passes — this file implements 1–3):
  Pass 1 — HTML parsing and page extraction (deterministic)
  Pass 2 — Content/footnote separation + coarse type classification
  Pass 3 — HTML stripping, entity decoding, text cleaning
  Pass 4 — Structure discovery (Session 3)
  Pass 5 — Multi-layer detection (Session 4)
  Pass 6 — Output assembly + validation (Session 5)
"""

from __future__ import annotations

import html as html_lib
import logging
import re
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from engines.normalization.contracts import NormalizedPackage
from engines.normalization.src.errors import NormalizationError, NormErrorCode
from engines.normalization.src.normalizers.base import BaseNormalizer
from engines.source.contracts import SourceMetadata

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════
# Constants and compiled regex patterns
# ══════════════════════════════════════════════════════════════════════

# Page block boundary — find start positions, do NOT regex-match div pairs
# (nested <div class='footnote'> breaks closing-tag matching).
PAGE_TEXT_START = "<div class='PageText'>"

# Running header — handles both <div> and <span> variants (ADV-010).
PAGE_HEAD_RE = re.compile(
    r"<(?:div|span)\s+class=['\"]PageHead['\"][^>]*>.*?</(?:div|span)>",
    re.DOTALL,
)

# Page number marker: Arabic-Indic OR Western digits inside (ص: N).
# Most Shamela exports use Arabic-Indic (٠-٩) but some use Western (0-9).
PAGE_NUM_RE = re.compile(r"\(ص:\s*([٠-٩0-9]+)\s*\)")

# Arabic-Indic digit → Western digit mapping.
_ARABIC_INDIC_MAP: dict[str, str] = {
    "٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4",
    "٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9",
}

# Footnote separator — SPEC §4.A.2 regex (more general than ABD).
# Captures 2–3 digit number; caller MUST verify 80 <= N <= 100.
FN_SEPARATOR_RE = re.compile(
    r"<hr\s+[^>]*width\s*=\s*['\"]?(\d{2,3})['\"]?[^>]*>",
    re.IGNORECASE,
)

# Footnote content div.
FN_DIV_RE = re.compile(r"<div class='footnote'>(.*?)</div>", re.DOTALL)

# Red font tags (Shamela numbering / decorative).
FONT_COLOR_RE = re.compile(r"<font\s+color=[^>]+>(.*?)</font>", re.DOTALL)

# Font size tags — for Pass 5 layer detection.
FONT_SIZE_RE = re.compile(
    r"<font\s+size=['\"]?(\d+)['\"]?[^>]*>(.*?)</font>", re.DOTALL
)

# Bold tags — for Pass 5 layer detection.
BOLD_RE = re.compile(r"<b>(.*?)</b>", re.DOTALL)

# Title span with DOUBLE quotes only (content headings, NOT metadata labels).
TITLE_SPAN_DOUBLE_RE = re.compile(
    r'<span\s+class="title"[^>]*>(.*?)</span>', re.DOTALL
)

# PageHead inner text extraction.
# PageNumber span removal (may be outside PageHead in some formats).
PAGE_NUMBER_SPAN_RE = re.compile(
    r"<span\s+class=['\"]PageNumber['\"][^>]*>.*?</span>", re.DOTALL
)

# Bare page number text pattern (safety net after span removal).
PAGE_NUMBER_TEXT_RE = re.compile(r"\(ص:\s*[٠-٩0-9]+\s*\)")

PAGEHEAD_PARTNAME_RE = re.compile(
    r"<span\s+class=['\"]PartName['\"][^>]*>(.*?)</span>", re.DOTALL
)
PAGEHEAD_TITLE_RE = re.compile(
    r"<span\s+class=['\"]title['\"][^>]*>(.*?)</span>", re.DOTALL
)

# Footnote boundary in footnote section: (N) at start or after newline.
# Uses [0-9] not \d — Python \d matches Arabic-Indic digits which are NOT footnote markers.
FN_BOUNDARY_RE = re.compile(
    r"(?:^|\n)\s*\(([0-9]+)\)\s*(?:[ـ\-–]\s*)?", re.MULTILINE
)

# Footnote reference in primary text: (N) where N is ASCII digits only.
# Uses [0-9] not \d — \d matches Arabic-Indic digits (٠-٩) which are hadith/verse numbers.
FN_REF_RE = re.compile(r"\(([0-9]+)\)")

# Verse detection.
VERSE_STAR_RE = re.compile(r"\*\s*([^*]+?)\s*\*")
HEMISTICH_SEP = "\u2026"  # … (horizontal ellipsis)
_ETC_PATTERNS = ("إلخ", "الخ", "إلى آخره", "إلى آخر")

# HTML tables.
TABLE_RE = re.compile(r"<table[^>]*>(.*?)</table>", re.IGNORECASE | re.DOTALL)
TABLE_ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
TABLE_CELL_RE = re.compile(
    r"<t[dh][^>]*>(.*?)</t[dh]>", re.IGNORECASE | re.DOTALL
)

# Image tags.
IMG_TAG_RE = re.compile(r"<img\s[^>]*>", re.IGNORECASE)

# Generic HTML tag stripping.
HTML_TAG_RE = re.compile(r"<[^>]+>")

# Block-level break conversion.
BREAK_P_RE = re.compile(r"</p>", re.IGNORECASE)
BREAK_BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)

# Tahqiq markers for coarse footnote classification.
_TAHQIQ_MARKERS = [
    "صحيح", "حسن", "ضعيف", "أخرجه",
    "في نسخة", "في الأصل",
    "البخاري", "مسلم", "أبو داود", "الترمذي",
    "الحاكم", "البيهقي", "ابن حبان",
]

# Author voice markers.
_AUTHOR_VOICE_STARTS = ("قلت:", "أقول:")

# Arabic diacritics Unicode codepoints for verification.
_ARABIC_DIACRITICS: set[int] = (
    set(range(0x064B, 0x0654))   # fathatan through sukun + maddah (U+0653)
    | {0x0670}                    # superscript alef
    | set(range(0x0656, 0x0660))  # additional marks
)

# Typographic spaces to normalize (§4.A.8).
_TYPOGRAPHIC_SPACES: set[int] = set(range(0x2000, 0x200B))


# ══════════════════════════════════════════════════════════════════════
# Intermediate data structures (internal to Shamela normalizer)
# ══════════════════════════════════════════════════════════════════════


class ParsedFootnote(BaseModel):
    """One footnote entry parsed from the footnote section."""

    number: int = Field(description="The (N) number")
    text: str = Field(description="Cleaned footnote text")
    raw_text: str = Field(description="Original text before cleaning")
    footnote_type: str = Field(
        default="unknown_footnote_type",
        description="tahqiq_editor | author_original | unknown_footnote_type",
    )
    classification_confidence: float = Field(
        default=0.5, ge=0.0, le=1.0
    )


class RawPage(BaseModel):
    """Output of Pass 1 — one entry per page block."""

    unit_index: int = Field(description="Monotonic from 0 across all volumes; -1 for metadata")
    volume: int
    page_number_display: Optional[str] = Field(
        None, description="Arabic-Indic numeral string, e.g. '٤٥'"
    )
    page_number_int: Optional[int] = None
    raw_html: str = Field(description="Full PageText div content minus outer wrapper")
    is_metadata_page: bool = False
    is_image_only: bool = False
    bold_spans: list[tuple[int, int, str]] = Field(
        default_factory=list,
        description="(start, end, text) in matn HTML for Pass 5",
    )
    font_size_spans: list[tuple[int, int, str, str]] = Field(
        default_factory=list,
        description="(start, end, text, size_value) for Pass 5",
    )
    title_spans: list[str] = Field(
        default_factory=list,
        description='Double-quote class="title" text content for Pass 4',
    )
    pagehead_text: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)


class SeparatedPage(BaseModel):
    """Output of Pass 2 — content/footnote separation."""

    unit_index: int
    volume: int
    page_number_display: Optional[str] = None
    page_number_int: Optional[int] = None
    primary_html: str = Field(description="HTML above footnote separator")
    footnote_html: str = Field(default="", description="HTML below separator")
    footnotes: list[ParsedFootnote] = Field(default_factory=list)
    footnote_format: str = Field(default="none")
    footnote_preamble: str = Field(default="")
    known_fn_numbers: set[int] = Field(default_factory=set)
    has_footnote_separator: bool = False
    is_image_only: bool = False
    bold_spans: list[tuple[int, int, str]] = Field(default_factory=list)
    font_size_spans: list[tuple[int, int, str, str]] = Field(default_factory=list)
    title_spans: list[str] = Field(default_factory=list)
    pagehead_text: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)


class CleanedPage(BaseModel):
    """Output of Pass 3 — cleaned text with preserved diacritics."""

    unit_index: int
    volume: int
    page_number_display: Optional[str] = None
    page_number_int: Optional[int] = None
    primary_text: str = Field(description="Cleaned text, diacritics preserved, ⌜N⌝ markers")
    footnotes: list[ParsedFootnote] = Field(default_factory=list)
    footnote_format: str = Field(default="none")
    footnote_preamble: str = Field(default="")
    footnote_ref_numbers: list[int] = Field(
        default_factory=list, description="Replaced ref numbers (sorted)"
    )
    orphan_refs: list[int] = Field(
        default_factory=list, description="Refs in text with no matching footnote"
    )
    orphan_footnotes: list[int] = Field(
        default_factory=list, description="Footnotes with no matching ref"
    )
    has_verse: bool = False
    has_tables: bool = False
    is_blank: bool = False
    is_image_only: bool = False
    has_footnote_separator: bool = False
    starts_with_zwnj_heading: bool = False
    bold_spans: list[tuple[int, int, str]] = Field(default_factory=list)
    font_size_spans: list[tuple[int, int, str, str]] = Field(default_factory=list)
    title_spans: list[str] = Field(default_factory=list)
    pagehead_text: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)


# ══════════════════════════════════════════════════════════════════════
# Utility functions
# ══════════════════════════════════════════════════════════════════════


def arabic_to_int(arabic_str: str) -> int:
    """Convert Arabic-Indic digit string to integer. e.g. '٤٥' → 45."""
    western = "".join(_ARABIC_INDIC_MAP.get(c, c) for c in arabic_str)
    return int(western)


def strip_tags(text: str) -> str:
    """Remove all HTML tags, keeping text content."""
    return HTML_TAG_RE.sub("", text)


def decode_entities(text: str) -> str:
    """Decode HTML entities (e.g. &nbsp; → space, &#x200C; → ZWNJ)."""
    return html_lib.unescape(text)


def normalize_whitespace(text: str) -> str:
    """SPEC §4.A.8 whitespace normalization.

    - \\r\\n / \\r → \\n
    - U+00A0 (NBSP) → space
    - U+202F (narrow NBSP) → space
    - U+2000–U+200A (typographic spaces) → space
    - U+FEFF (BOM) → strip at file start only
    - PRESERVE: U+200C (ZWNJ), U+200B (ZWSP), U+200D (ZWJ)
    - 2+ spaces → 1 space
    - 3+ blank lines → 1 blank line
    - Trim lines and result
    """
    # Line ending normalization
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # BOM at file start only
    if text.startswith("\ufeff"):
        text = text[1:]

    # Unicode space normalization (character by character for safety)
    result_chars: list[str] = []
    for ch in text:
        cp = ord(ch)
        if cp == 0x00A0 or cp == 0x202F or cp in _TYPOGRAPHIC_SPACES:
            result_chars.append(" ")
        else:
            result_chars.append(ch)
    text = "".join(result_chars)

    # Collapse multiple spaces (NOT newlines) to single space per line
    lines = text.split("\n")
    lines = [re.sub(r"  +", " ", line) for line in lines]

    # Trim each line
    lines = [line.strip() for line in lines]

    # Join and collapse 3+ blank lines → 1 blank line
    # 3 blank lines = 4 consecutive \n; collapse to 2 \n (1 blank line)
    text = "\n".join(lines)
    text = re.sub(r"\n{4,}", "\n\n", text)

    return text.strip()


def detect_verse(text: str) -> bool:
    """Detect verse/poetry in text.

    A hemistich separator (…) triggers has_verse ONLY when balanced:
    ≥5 chars on each side, excluding prose 'إلخ' patterns.
    Star markers (* text *) also trigger.
    """
    if VERSE_STAR_RE.search(text):
        return True
    for line in text.split("\n"):
        if HEMISTICH_SEP not in line:
            continue
        parts = line.split(HEMISTICH_SEP)
        if len(parts) >= 2:
            left = parts[0].strip()
            right = HEMISTICH_SEP.join(parts[1:]).strip()
            if len(left) >= 5 and len(right) >= 5:
                if any(right.startswith(pat) for pat in _ETC_PATTERNS):
                    continue
                return True
    return False


def extract_table_text(table_html: str) -> str:
    """Convert an HTML table to pipe-separated text."""
    rows = TABLE_ROW_RE.findall(table_html)
    text_rows: list[str] = []
    for row_html in rows:
        cells = TABLE_CELL_RE.findall(row_html)
        cell_texts = [normalize_whitespace(strip_tags(c)) for c in cells]
        cell_texts = [t for t in cell_texts if t]
        if cell_texts:
            text_rows.append(" | ".join(cell_texts))
    return "\n".join(text_rows)


def replace_tables_with_text(html_text: str) -> tuple[str, int]:
    """Replace <table> blocks with extracted text. Returns (html, count)."""
    count = 0

    def replacer(m: re.Match[str]) -> str:
        nonlocal count
        count += 1
        text = extract_table_text(m.group(0))
        return f"\n{text}\n"

    result = TABLE_RE.sub(replacer, html_text)
    return result, count


def classify_footnote_type(text: str) -> tuple[str, float]:
    """Coarse footnote classification (SPEC §4.A.2 Pass 2).

    Returns (footnote_type, classification_confidence).
    """
    for marker in _TAHQIQ_MARKERS:
        if marker in text:
            return "tahqiq_editor", 0.8
    for start in _AUTHOR_VOICE_STARTS:
        if text.strip().startswith(start):
            return "author_original", 0.7
    return "unknown_footnote_type", 0.5


def _detect_fn_section_format(fn_text: str) -> str:
    """Classify footnote section format."""
    if re.search(r"\([0-9]+\)", fn_text):
        return "numbered_parens"
    if re.search(r"^[0-9]+\s", fn_text, re.MULTILINE):
        return "bare_number"
    if fn_text.strip():
        return "unnumbered"
    return "none"


# ══════════════════════════════════════════════════════════════════════
# ShamelaNormalizer
# ══════════════════════════════════════════════════════════════════════


class ShamelaNormalizer(BaseNormalizer):
    """SPEC §4.A.2: Shamela HTML → KR normalized package.

    Internally uses 6 passes. This class implements Passes 1–3.
    Passes 4–6 are implemented in Sessions 3–5.
    """

    def validate_input(
        self,
        frozen_path: Path,
        metadata: SourceMetadata,
    ) -> None:
        """Verify frozen source is valid Shamela HTML."""
        if not frozen_path.exists():
            raise NormalizationError(
                code=NormErrorCode.MISSING_FROZEN,
                message=f"Frozen path does not exist: {frozen_path}",
            )

        if frozen_path.is_file():
            files = [frozen_path]
        elif frozen_path.is_dir():
            files = list(frozen_path.glob("*.htm")) + list(frozen_path.glob("*.html"))
        else:
            raise NormalizationError(
                code=NormErrorCode.MISSING_FROZEN,
                message=f"Frozen path is not a file or directory: {frozen_path}",
            )

        if not files:
            raise NormalizationError(
                code=NormErrorCode.MISSING_FROZEN,
                message=f"No .htm/.html files found in {frozen_path}",
            )

        # Check at least one file has PageText div
        for f in files:
            try:
                text = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    text = f.read_text(encoding="windows-1256")
                except Exception:
                    continue
            if PAGE_TEXT_START in text:
                return

        raise NormalizationError(
            code=NormErrorCode.SCHEMA_VIOLATION,
            message="No PageText div found in any input file",
        )

    def normalize(
        self,
        frozen_path: Path,
        metadata: SourceMetadata,
    ) -> NormalizedPackage:
        """Execute the 6-pass pipeline (Passes 1–3 implemented)."""
        htm_files = self._resolve_input_files(frozen_path)

        # Pass 1: Parse all volumes
        all_raw_pages: list[RawPage] = []
        seq_offset = 0
        for volume_num, htm_file in htm_files:
            html_text = self._read_html(htm_file)
            raw_pages = self._pass1_parse(html_text, volume_num, seq_offset)
            content_pages = [p for p in raw_pages if not p.is_metadata_page]
            seq_offset += len(content_pages)
            all_raw_pages.extend(raw_pages)

        # Pass 2: Separate content from footnotes
        separated = self._pass2_separate(all_raw_pages)

        # Pass 3: Clean HTML and produce text
        cleaned = self._pass3_clean(separated)

        # Pass 4: Structure discovery
        division_tree, page_markers, div_counts, struct_confidence = \
            self._pass4_discover_structure(cleaned, metadata)

        # Passes 5–6: NOT YET IMPLEMENTED (Sessions 4–5)
        raise NotImplementedError(
            "Passes 5–6 not yet implemented. "
            f"Pass 4 discovered {sum(div_counts.values())} divisions "
            f"({struct_confidence.value} confidence) "
            f"from {len(cleaned)} pages."
        )

    # ──────────────────────────────────────────────────────────────
    # Input resolution
    # ──────────────────────────────────────────────────────────────

    def _resolve_input_files(
        self, frozen_path: Path
    ) -> list[tuple[int, Path]]:
        """Resolve frozen_path to (volume_number, path) tuples.

        Handles: single file, directory with book.htm, directory with
        numbered volumes, mixed numeric/non-numeric stems.
        """
        if frozen_path.is_file():
            return [(1, frozen_path)]

        htm_files = sorted(
            list(frozen_path.glob("*.htm")) + list(frozen_path.glob("*.html"))
        )
        if not htm_files:
            raise NormalizationError(
                code=NormErrorCode.MISSING_FROZEN,
                message=f"No .htm/.html files in {frozen_path}",
            )

        if len(htm_files) == 1:
            return [(1, htm_files[0])]

        # Multiple files → multi-volume
        numeric: list[tuple[int, Path]] = []
        non_numeric: list[Path] = []

        for f in htm_files:
            try:
                vol = int(f.stem)
                numeric.append((vol, f))
            except ValueError:
                non_numeric.append(f)
                logger.warning(
                    "%s: cannot parse '%s' as volume number",
                    NormErrorCode.VOLUME_NUMBER_UNPARSEABLE.value,
                    f.name,
                )

        numeric.sort(key=lambda x: x[0])

        # Assign sequential volume numbers to non-numeric files
        next_vol = (max(v for v, _ in numeric) + 1) if numeric else 1
        for f in sorted(non_numeric, key=lambda p: p.name):
            numeric.append((next_vol, f))
            next_vol += 1

        # Check for duplicate volume numbers
        volumes = [v for v, _ in numeric]
        if len(volumes) != len(set(volumes)):
            logger.warning(
                "%s: duplicate volume numbers detected: %s",
                NormErrorCode.VOLUME_MISMATCH.value,
                sorted(v for v in volumes if volumes.count(v) > 1),
            )

        return sorted(numeric, key=lambda x: x[0])

    def _read_html(self, htm_file: Path) -> str:
        """Read HTML file: UTF-8 with Windows-1256 fallback."""
        try:
            return htm_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning(
                "%s: %s is not valid UTF-8, falling back to Windows-1256",
                NormErrorCode.ENCODING_ERROR.value,
                htm_file.name,
            )
            return htm_file.read_text(encoding="windows-1256")

    # ──────────────────────────────────────────────────────────────
    # Pass 1 — HTML Parsing and Page Extraction
    # ──────────────────────────────────────────────────────────────

    def _pass1_parse(
        self,
        html_text: str,
        volume: int,
        seq_offset: int,
    ) -> list[RawPage]:
        """SPEC §4.A.2 Pass 1: Split HTML into page blocks, extract metadata.

        Returns one RawPage per page block. Metadata pages have
        is_metadata_page=True and unit_index=-1.
        """
        # B1: Split at PageText div start positions
        blocks: list[str] = []
        positions: list[int] = []
        start = 0
        while True:
            pos = html_text.find(PAGE_TEXT_START, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        for i, pos in enumerate(positions):
            block_start = pos + len(PAGE_TEXT_START)
            block_end = positions[i + 1] if i + 1 < len(positions) else len(html_text)
            blocks.append(html_text[block_start:block_end])

        # B3: Metadata detection state
        seen_numbered_page = False
        content_counter = 0
        seen_page_numbers: dict[int, int] = {}  # page_num → first unit_index
        pages: list[RawPage] = []

        for block in blocks:
            warnings: list[str] = []

            # B2: Extract page number
            pn_match = PAGE_NUM_RE.search(block)
            page_display: Optional[str] = None
            page_int: Optional[int] = None

            if pn_match:
                digits = pn_match.group(1)
                page_display = digits
                page_int = arabic_to_int(digits)

            # B3: Metadata page detection
            if page_int is None and not seen_numbered_page:
                # No page number AND before first numbered page → metadata
                pages.append(RawPage(
                    unit_index=-1,
                    volume=volume,
                    page_number_display=None,
                    page_number_int=None,
                    raw_html=block,
                    is_metadata_page=True,
                    warnings=warnings,
                ))
                continue

            if page_int is not None:
                seen_numbered_page = True

            if page_int is None and seen_numbered_page:
                # No page number AFTER content pages → content with missing number.
                # Note: NORM_SUSPICIOUS_PAGEHEAD has a different SPEC trigger
                # (PageHead >100 chars not matching heading patterns), so we use
                # a descriptive warning without an error code here.
                warnings.append(
                    "MISSING_PAGE_NUMBER: page without page number after "
                    "content pages (not a metadata page)"
                )

            # B10: Duplicate page number detection
            if page_int is not None and page_int in seen_page_numbers:
                warnings.append(
                    f"{NormErrorCode.DUPLICATE_PAGES.value}: "
                    f"page number {page_int} duplicates unit_index "
                    f"{seen_page_numbers[page_int]}"
                )

            # B4: Image-only detection
            is_image_only = self._detect_image_only(block)

            # Extract spans for downstream passes (B5–B8)
            # Determine matn HTML bounds: after PageHead, before footnote separator
            content_html = PAGE_HEAD_RE.sub("", block)

            # Find footnote separator position in content_html (for matn bounds)
            separator_pos = len(content_html)
            for m in FN_SEPARATOR_RE.finditer(content_html):
                width_val = int(m.group(1))
                if 80 <= width_val <= 100:
                    separator_pos = m.start()
                    break

            matn_html = content_html[:separator_pos]

            # B5: Bold span extraction
            bold_spans: list[tuple[int, int, str]] = []
            if not is_image_only:
                for m in BOLD_RE.finditer(matn_html):
                    bold_spans.append((m.start(), m.end(), m.group(1)))

            # B6: Font size span extraction
            font_size_spans: list[tuple[int, int, str, str]] = []
            if not is_image_only:
                for m in FONT_SIZE_RE.finditer(matn_html):
                    font_size_spans.append(
                        (m.start(), m.end(), m.group(2), m.group(1))
                    )

            # B7: Title span extraction (double-quote ONLY)
            title_spans: list[str] = []
            if not is_image_only:
                for m in TITLE_SPAN_DOUBLE_RE.finditer(block):
                    span_text = decode_entities(strip_tags(m.group(1))).strip()
                    if span_text:
                        title_spans.append(span_text)

            # B8: PageHead text extraction
            pagehead_text = self._extract_pagehead_text(block)

            # B9: Assign unit_index
            unit_idx = seq_offset + content_counter
            content_counter += 1

            if page_int is not None:
                seen_page_numbers[page_int] = unit_idx

            pages.append(RawPage(
                unit_index=unit_idx,
                volume=volume,
                page_number_display=page_display,
                page_number_int=page_int,
                raw_html=block,
                is_metadata_page=False,
                is_image_only=is_image_only,
                bold_spans=bold_spans,
                font_size_spans=font_size_spans,
                title_spans=title_spans,
                pagehead_text=pagehead_text,
                warnings=warnings,
            ))

        return pages

    @staticmethod
    def _detect_image_only(block: str) -> bool:
        """B4: Detect if page is an embedded image scan with <10 chars text."""
        if not IMG_TAG_RE.search(block):
            return False
        content = PAGE_HEAD_RE.sub("", block)
        content = IMG_TAG_RE.sub("", content)
        text = strip_tags(content).strip()
        return len(text) < 10

    @staticmethod
    def _extract_pagehead_text(block: str) -> Optional[str]:
        """B8: Extract heading text from PageHead div."""
        head_match = PAGE_HEAD_RE.search(block)
        if not head_match:
            return None

        head_html = head_match.group(0)

        # Try PartName first, then title
        for regex in (PAGEHEAD_PARTNAME_RE, PAGEHEAD_TITLE_RE):
            m = regex.search(head_html)
            if m:
                text = decode_entities(strip_tags(m.group(1))).strip()
                if text:
                    return text
        return None

    # ──────────────────────────────────────────────────────────────
    # Pass 2 — Content/Footnote Separation
    # ──────────────────────────────────────────────────────────────

    def _pass2_separate(
        self, pages: list[RawPage]
    ) -> list[SeparatedPage]:
        """SPEC §4.A.2 Pass 2: Split each page into primary/footnote HTML."""
        result: list[SeparatedPage] = []

        for page in pages:
            # C1: Skip metadata pages
            if page.is_metadata_page:
                continue

            warnings = list(page.warnings)

            # C1: Image-only pages get minimal SeparatedPage
            if page.is_image_only:
                result.append(SeparatedPage(
                    unit_index=page.unit_index,
                    volume=page.volume,
                    page_number_display=page.page_number_display,
                    page_number_int=page.page_number_int,
                    primary_html="",
                    footnote_html="",
                    has_footnote_separator=False,
                    is_image_only=True,
                    bold_spans=page.bold_spans,
                    font_size_spans=page.font_size_spans,
                    title_spans=page.title_spans,
                    pagehead_text=page.pagehead_text,
                    warnings=warnings,
                ))
                continue

            # C2: Find footnote separator in raw_html
            raw = page.raw_html
            has_separator = False
            sep_pos: Optional[int] = None

            for m in FN_SEPARATOR_RE.finditer(raw):
                width_val = int(m.group(1))
                if 80 <= width_val <= 100:
                    has_separator = True
                    sep_pos = m.start()
                    break

            # C3: Split
            if has_separator and sep_pos is not None:
                primary_html = raw[:sep_pos]
                footnote_html = raw[sep_pos:]
            else:
                primary_html = raw
                footnote_html = ""
                warnings.append(
                    f"{NormErrorCode.FOOTNOTE_SEPARATOR_ABSENT.value}: "
                    f"no footnote separator on page {page.page_number_int}"
                )

            # C4: Parse footnotes
            footnotes, preamble, fn_format, known_numbers = self._parse_footnotes(
                footnote_html
            )

            # C5: Classify each footnote
            for fn in footnotes:
                fn_type, fn_conf = classify_footnote_type(fn.text)
                fn.footnote_type = fn_type
                fn.classification_confidence = fn_conf

            result.append(SeparatedPage(
                unit_index=page.unit_index,
                volume=page.volume,
                page_number_display=page.page_number_display,
                page_number_int=page.page_number_int,
                primary_html=primary_html,
                footnote_html=footnote_html,
                footnotes=footnotes,
                footnote_format=fn_format,
                footnote_preamble=preamble,
                known_fn_numbers=known_numbers,
                has_footnote_separator=has_separator,
                is_image_only=False,
                bold_spans=page.bold_spans,
                font_size_spans=page.font_size_spans,
                title_spans=page.title_spans,
                pagehead_text=page.pagehead_text,
                warnings=warnings,
            ))

        # TODO (Session 5, Pass 6): Check if >30% of pages lack footnote
        # separator. If so, set `no_footnote_apparatus` flag in quality_report.
        # Per SPEC §4.A.2 Pass 2: "If >30% of pages lack it, set
        # no_footnote_apparatus flag." This is a source-level flag written
        # during output assembly, not a per-page concern.

        return result

    @staticmethod
    def _parse_footnotes(
        footnote_html: str,
    ) -> tuple[list[ParsedFootnote], str, str, set[int]]:
        """Parse footnote HTML into individual entries with monotonic merge.

        Returns (footnotes, preamble, format, known_numbers).
        """
        if not footnote_html.strip():
            return [], "", "none", set()

        # Extract footnote div content
        div_match = FN_DIV_RE.search(footnote_html)
        if div_match:
            fn_content = div_match.group(1)
        else:
            # No footnote div — try parsing the raw HTML after separator
            fn_content = footnote_html

        # Unwrap red font tags
        fn_text = FONT_COLOR_RE.sub(r"\1", fn_content)
        # Strip remaining HTML tags and decode entities
        fn_text = decode_entities(strip_tags(fn_text))

        # Detect format
        fn_format = _detect_fn_section_format(fn_text)

        if fn_format not in ("numbered_parens", "bare_number"):
            # No structured footnotes — entire text is preamble
            return [], fn_text.strip(), fn_format, set()

        # Split at (N) boundaries with monotonic merge
        matches = list(FN_BOUNDARY_RE.finditer(fn_text))
        if not matches:
            return [], fn_text.strip(), fn_format, set()

        # Preamble = text before first (N)
        preamble = fn_text[: matches[0].start()].strip()

        # First pass: split at all boundaries
        raw_records: list[ParsedFootnote] = []
        for i, m in enumerate(matches):
            num = int(m.group(1))
            text_start = m.end()
            text_end = matches[i + 1].start() if i + 1 < len(matches) else len(fn_text)
            text = fn_text[text_start:text_end].strip()
            raw_text = fn_text[m.start():text_end].strip()
            raw_records.append(ParsedFootnote(
                number=num, text=text, raw_text=raw_text
            ))

        # Second pass: monotonic merge (ABD pattern lines 388–404)
        merged: list[ParsedFootnote] = []
        for rec in raw_records:
            if merged and rec.number <= merged[-1].number:
                # Non-monotonic → merge into previous
                prev = merged[-1]
                merged[-1] = ParsedFootnote(
                    number=prev.number,
                    text=prev.text + "\n" + rec.raw_text,
                    raw_text=prev.raw_text + "\n" + rec.raw_text,
                    footnote_type=prev.footnote_type,
                    classification_confidence=prev.classification_confidence,
                )
            else:
                merged.append(rec)

        known = {fn.number for fn in merged}
        return merged, preamble, fn_format, known

    # ──────────────────────────────────────────────────────────────
    # Pass 4 — Structure Discovery
    # ──────────────────────────────────────────────────────────────

    def _pass4_discover_structure(
        self,
        cleaned: list[CleanedPage],
        metadata: SourceMetadata,
    ) -> tuple:
        """SPEC §4.A.6: 4-tier heading detection + division tree construction.

        Returns (division_tree, page_markers, division_count_by_tier, overall_confidence).
        """
        from engines.normalization.src.structure_discovery import discover_structure

        result = discover_structure(cleaned, metadata.source_id, metadata.genre)
        return (
            result.division_tree,
            result.page_markers,
            result.quality_counts,
            result.overall_confidence,
        )

    # Pass 3 — HTML Stripping and Text Cleaning
    # ──────────────────────────────────────────────────────────────

    def _pass3_clean(
        self, pages: list[SeparatedPage]
    ) -> list[CleanedPage]:
        """SPEC §4.A.2 Pass 3: Strip HTML, decode entities, clean text."""
        result: list[CleanedPage] = []
        diacritics_verified = False

        for page in pages:
            warnings = list(page.warnings)

            # Image-only pages → minimal CleanedPage
            if page.is_image_only:
                result.append(CleanedPage(
                    unit_index=page.unit_index,
                    volume=page.volume,
                    page_number_display=page.page_number_display,
                    page_number_int=page.page_number_int,
                    primary_text="",
                    is_blank=True,
                    is_image_only=True,
                    has_footnote_separator=page.has_footnote_separator,
                    bold_spans=page.bold_spans,
                    font_size_spans=page.font_size_spans,
                    title_spans=page.title_spans,
                    pagehead_text=page.pagehead_text,
                    warnings=warnings,
                ))
                continue

            html = page.primary_html

            # D2a: Remove running header and page number elements
            html = PAGE_HEAD_RE.sub("", html)
            html = PAGE_NUMBER_SPAN_RE.sub("", html)
            html = PAGE_NUMBER_TEXT_RE.sub("", html)

            # D2b: Replace tables with extracted text
            html, table_count = replace_tables_with_text(html)
            has_tables = table_count > 0

            # D2c: Remove <img> tags
            html = IMG_TAG_RE.sub("", html)

            # D2d: Detect verse BEFORE tag stripping
            text_for_verse = strip_tags(html)
            has_verse = detect_verse(text_for_verse)

            # D2e: Unwrap <font color=#be0000> tags (keep text)
            html = FONT_COLOR_RE.sub(r"\1", html)

            # D2f: Convert block-level breaks
            html = BREAK_P_RE.sub("\n", html)
            html = BREAK_BR_RE.sub("\n", html)

            # D3: Diacritics canary check (first content page only)
            if not diacritics_verified and html.strip():
                self._verify_diacritics_canary(html)
                diacritics_verified = True

            # D2g+h: Strip remaining tags and decode entities
            text = decode_entities(strip_tags(html))

            # D2i: Clean verse markers (* text * → text)
            text = VERSE_STAR_RE.sub(r"\1", text)

            # D2j: Replace footnote refs with universal markers
            text, replaced_refs, orphan_ref_list = self._replace_footnote_refs(
                text, page.known_fn_numbers
            )
            for ref_num in orphan_ref_list:
                warnings.append(
                    f"{NormErrorCode.ORPHAN_FOOTNOTE_REF.value}: "
                    f"ref ({ref_num}) in text has no matching footnote"
                )

            # D2k: Whitespace normalization (§4.A.8)
            text = normalize_whitespace(text)

            # D4: Post-cleaning flags
            is_blank = not text.strip()
            starts_with_zwnj = text.startswith("\u200c\u200c")

            # Cross-reference validation
            fn_numbers_set = page.known_fn_numbers
            replaced_set = set(replaced_refs)
            orphan_fns = sorted(fn_numbers_set - replaced_set)

            if orphan_fns:
                warnings.append(
                    f"Footnotes with no matching ref in text: {orphan_fns}"
                )

            result.append(CleanedPage(
                unit_index=page.unit_index,
                volume=page.volume,
                page_number_display=page.page_number_display,
                page_number_int=page.page_number_int,
                primary_text=text,
                footnotes=page.footnotes,
                footnote_format=page.footnote_format,
                footnote_preamble=page.footnote_preamble,
                footnote_ref_numbers=sorted(set(replaced_refs)),
                orphan_refs=sorted(set(orphan_ref_list)),
                orphan_footnotes=orphan_fns,
                has_verse=has_verse,
                has_tables=has_tables,
                is_blank=is_blank,
                is_image_only=False,
                has_footnote_separator=page.has_footnote_separator,
                starts_with_zwnj_heading=starts_with_zwnj,
                bold_spans=page.bold_spans,
                font_size_spans=page.font_size_spans,
                title_spans=page.title_spans,
                pagehead_text=page.pagehead_text,
                warnings=warnings,
            ))

        return result

    @staticmethod
    def _replace_footnote_refs(
        text: str,
        known_fn_numbers: set[int],
    ) -> tuple[str, list[int], list[int]]:
        """Replace (N) with ⌜N⌝ where N ∈ known_fn_numbers.

        Returns (cleaned_text, replaced_refs, orphan_refs).
        Orphan refs = (N) patterns where N ∉ known_fn_numbers.
        """
        if not known_fn_numbers:
            return text, [], []

        replaced: list[int] = []
        orphans: list[int] = []

        def replacer(m: re.Match[str]) -> str:
            n = int(m.group(1))
            if n in known_fn_numbers:
                replaced.append(n)
                return f"\u231c{n}\u231d"
            # Track as orphan only if it looks like a plausible footnote ref
            # (small number, not a date or verse reference)
            if n <= 200:
                orphans.append(n)
            return m.group(0)

        cleaned = FN_REF_RE.sub(replacer, text)
        return cleaned, replaced, orphans

    @staticmethod
    def _verify_diacritics_canary(html_fragment: str) -> None:
        """D3: Verify entity decoding preserves Arabic diacritics.

        Compares regex+unescape vs BS4 on first 500 chars. If diacritics
        differ, raises NORM_DIACRITICS_ENTITY_CORRUPTION (Fatal).
        Run once per source on the first content page.
        """
        # Method 1: regex strip + html.unescape (our primary method)
        text_regex = decode_entities(strip_tags(html_fragment))

        # Method 2: BS4 parse
        try:
            soup = BeautifulSoup(html_fragment, "lxml")
            text_bs4 = soup.get_text()
        except Exception:
            try:
                soup = BeautifulSoup(html_fragment, "html5lib")
                text_bs4 = soup.get_text()
            except Exception:
                return  # Cannot verify — proceed with regex method

        # Compare diacritic sequences in first 500 chars
        d_regex = [
            c for c in text_regex[:500] if ord(c) in _ARABIC_DIACRITICS
        ]
        d_bs4 = [
            c for c in text_bs4[:500] if ord(c) in _ARABIC_DIACRITICS
        ]

        if d_regex != d_bs4:
            raise NormalizationError(
                code=NormErrorCode.DIACRITICS_ENTITY_CORRUPTION,
                message=(
                    f"Diacritic sequence mismatch: regex found {len(d_regex)} "
                    f"diacritics, BS4 found {len(d_bs4)} in first 500 chars"
                ),
                recovery="Investigate HTML parser entity decoding behavior",
            )
