"""Shamela HTML Metadata Extractor — SPEC §4.A.3

Parses the metadata card (بطاقة الكتاب) embedded in the first PageText div
of Shamela desktop HTML exports. Extracts: title, author, publisher, muhaqiq,
page count, edition, volume structure, quality inspection.

The full structural specification is in reference/SHAMELA_FORMAT_ANALYSIS.md
(derived from analysis of 2,519 real Shamela exports).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from engines.source.contracts import ErrorCode, ErrorSeverity
from engines.source.src.exceptions import make_error
from engines.source.src.text_utils import parse_arabic_ordinal, strip_tags

# ──────────────────────────────────────────────────────────────────
# Field mapping: Arabic metadata card labels → internal field names
# ──────────────────────────────────────────────────────────────────

FIELD_MAP: dict[str, str] = {
    # Primary fields
    "الكتاب": "title_full",
    "اسم الكتاب": "title_full",  # Alternative (0.9%)
    "المؤلف": "author_name_raw",
    # Muhaqiq-equivalent labels — all map to muhaqiq_name_raw.
    # Frequencies from collection audit (2,256 exports analyzed):
    "المحقق": "muhaqiq_name_raw",  # 32.4%
    "تحقيق": "muhaqiq_name_raw",  # 7.4%
    "دراسة وتحقيق": "muhaqiq_name_raw",  # 2.3%
    "تحقيق ودراسة": "muhaqiq_name_raw",  # 0.9%
    "تحقيق وتعليق": "muhaqiq_name_raw",  # 0.8%
    "راجعه": "muhaqiq_name_raw",  # 1.2%
    "راجعه ودققه": "muhaqiq_name_raw",  # <0.1%
    "اعتناء وتخريج": "muhaqiq_name_raw",  # 0.6%
    "تخريج": "muhaqiq_name_raw",  # 0.6%
    "حققه وخرج أحاديثه": "muhaqiq_name_raw",  # 0.6%
    "تحقيق وتخريج": "muhaqiq_name_raw",  # 0.5%
    "حققه وعلق عليه": "muhaqiq_name_raw",  # 0.5%
    "اعتنى به": "muhaqiq_name_raw",  # 0.4%
    "تقديم وتحقيق": "muhaqiq_name_raw",  # 0.4%
    "حققه وخرج أحاديثه وعلق عليه": "muhaqiq_name_raw",  # 0.4%
    "مراجعة": "muhaqiq_name_raw",  # 0.2%
    "حققه": "muhaqiq_name_raw",  # 0.2%
    # Publishing fields
    "الناشر": "publisher",
    "دار النشر": "publisher",  # Alternative (0.9%)
    "توزيع": "distributor",  # Distributor (0.3%) — format_specific_metadata
    "الطبعة": "edition_raw",
    "عدد الأجزاء": "volume_count_raw",
    "عدد المجلدات": "volume_count_raw",  # Alternative (0.2%)
    "عدد الصفحات": "page_count_raw",
    "عدد صفحات (الكتاب الورقي)": "page_count_raw",  # Alternative
    "عام النشر": "publication_year_raw",
    "سنة النشر": "publication_year_raw",  # Alternative (0.4%)
    "تاريخ النشر بالشاملة": "shamela_publish_date",
    "مصدر الكتاب": "source_note",
    "تنبيه": "editorial_note",
    "[تنبيه]": "editorial_note",  # Variant with brackets (0.3%)
    # Multi-layer attribution fields (ground truth when present)
    "مؤلف الأصل": "original_author_name_raw",  # 0.3% — for sharh/hashiyah
    "الشارح": "commentator_name_raw",  # 0.3% — the commentator
    # Compilation and translation
    "جمع وترتيب": "compiler_name_raw",  # 0.4%
    "ترجمة": "translator",  # 0.2%
    "تقديم": "foreword_by",  # 0.8% — NOT muhaqiq
    "قدم له": "foreword_by",  # 0.5% — NOT muhaqiq
    # Thesis/academic fields
    "إعداد": "author_name_raw",  # Thesis author (when المؤلف absent)
    "إشراف": "supervisor",
    "رسالة": "thesis_info",
    "كود المادة": "_academic_course_code",
    "المرحلة": "_academic_level",
    "العام الجامعي": "_academic_year",
    # Source provenance
    "أصل الكتاب": "_source_origin",  # 0.4%
    "أصل التحقيق": "_tahqiq_origin",  # 0.4% — origin of the tahqiq (NOT a muhaqiq)
    # Shamela digitization provenance (user requirement, 17.7% in collection)
    "أعده للشاملة": "preparer",
    "قدمه للشاملة": "preparer",  # Alternative (1.9%)
    "أهداه للشاملة": "preparer",  # Alternative (0.3%)
    # Notes
    "ملاحظة": "editorial_note",  # 0.2% — same semantics as تنبيه
}

# Muhaqiq pattern matching for long-tail labels not in FIELD_MAP.
# IMPORTANT: Arabic Form II masdar (تفعيل) inserts ي between 2nd and 3rd
# radicals, so trilateral roots are NOT substrings of their masdar forms:
# حقق ∉ تحقيق, خرج ∉ تخريج, علق ∉ تعليق. Both forms must be listed.
MUHAQIQ_KEYWORDS: list[str] = [
    # Root verb forms
    "حقق",
    "خرج",
    "ضبط",
    "صحح",
    "علق",
    "راجع",
    "اعتن",
    # Form II masdar forms
    "تحقيق",
    "تخريج",
    "تعليق",
    "تصحيح",
    "مراجع",
]

MUHAQIQ_EXCLUSIONS: list[str] = ["أصل التحقيق", "المحقق (رسالة علمية)"]


# ──────────────────────────────────────────────────────────────────
# Regex patterns (compiled once)
# ──────────────────────────────────────────────────────────────────

_RE_CARD = re.compile(r"<div class='PageText'>(.*?)</div>", re.DOTALL)

_RE_HEADER = re.compile(
    r"\s*<span class='title'>(.*?)(?:&nbsp;)+\s*</span>"
    r"\s*(?:<span class='footnote'>\((.*?)\)</span>)?",
)

_RE_CATEGORY = re.compile(
    r"<span class='title'>القسم.*?</span>\s*(.*?)(?:<hr|<p>)",
    re.DOTALL,
)

_RE_FIELD = re.compile(
    r"<span class='title'>(.*?)(?:<font[^>]*>)?:(?:</font>)?</span>\s*(.*?)(?:<p>|<hr|$)",
    re.DOTALL,
)

_RE_AUTHOR_DEATH = re.compile(r"\(.*?(?:المتوفى|ت)\s*:?\s*(\d+)\s*هـ\)?")
_RE_AUTHOR_RANGE = re.compile(r"\((\d+)\s*-\s*(\d+)\s*هـ\)")
_RE_AUTHOR_CLEAN = re.compile(r"^(.*?)\s*\(")
_RE_MUHAQIQ_DEATH = re.compile(r"\[.*?ت\s*(\d+)\s*هـ\]")
_RE_MUHAQIQ_CLEAN = re.compile(r"^(.*?)\s*\[")
_RE_YEAR_SUFFIX = re.compile(r"(\d{4})\s*(هـ|م)")
_RE_BARE_YEAR = re.compile(r"(\d{4})")
_RE_DIGITS = re.compile(r"\d+")
_RE_PAGETEXT = re.compile(r"<div class='PageText'>")
_RE_FOOTNOTE_HR = re.compile(r"<hr[^>]*>.*$", re.DOTALL)


# ──────────────────────────────────────────────────────────────────
# Main extractor
# ──────────────────────────────────────────────────────────────────


def extract_shamela_metadata(source_path: Path) -> dict[str, Any]:
    """Extract metadata from a Shamela desktop HTML export.

    Parses the بطاقة الكتاب (metadata card) embedded in the first PageText
    div, counts body pages, extracts a text sample, and runs 5 quality
    inspection checks.

    Args:
        source_path: Either a single .htm file or a directory of .htm files.

    Returns:
        Dict of extracted metadata fields with internal field names.

    Raises:
        SourceEngineError: FORMAT_STRUCTURE_MISSING if no PageText div found.
        SourceEngineError: UNSUPPORTED_FORMAT if file is not valid UTF-8.
    """
    # ── Volume detection ──
    first_file, is_multi_volume, volume_count, muqaddima_file = _detect_volumes(
        source_path
    )

    # ── Read content ──
    try:
        content = first_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise make_error(
            ErrorCode.UNSUPPORTED_FORMAT,
            f"File is not valid UTF-8: {first_file.name}",
            context={"file": str(first_file), "error": str(exc)},
        ) from exc

    result: dict[str, Any] = {
        "is_multi_volume": is_multi_volume,
        "volume_count": volume_count,
        "has_muqaddima": muqaddima_file is not None,
    }

    # ── Parse the metadata card (first PageText div) ──
    card = _extract_card(content, first_file.name)

    # ── Card header: display title + short author ──
    _parse_header(card, result)

    # ── Category (القسم) ──
    _parse_category(card, result)

    # ── Bibliographic fields ──
    _parse_bibliographic_fields(card, result)

    # ── Death dates ──
    _parse_death_dates(result)

    # ── Physical page count ──
    _parse_physical_page_count(result)

    # ── Edition number and years ──
    _parse_edition(result)

    # ── Publication year fallback ──
    _parse_publication_year_fallback(result)

    # ── Metadata volume count cross-check ──
    _parse_metadata_volume_count(result)

    # ── Digital body page count ──
    body_page_count = len(_RE_PAGETEXT.findall(content)) - 1
    result["body_page_count"] = body_page_count
    result["page_count"] = body_page_count

    # ── Text sample ──
    result["text_sample"] = _extract_text_sample(content)

    # ── Quality inspection ──
    page_segments = re.split(r"<div class='PageText'>", content)
    result["_quality_issues"] = _run_quality_inspection(
        body_page_count, result, content, page_segments
    )

    # ── Format-specific metadata ──
    _assemble_format_specific_metadata(result)

    return result


# ──────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────


def _detect_volumes(
    source_path: Path,
) -> tuple[Path, bool, int, Path | None]:
    """Classify files and determine volume structure.

    Args:
        source_path: Single .htm file or directory of .htm files.

    Returns:
        Tuple of (first_file, is_multi_volume, volume_count, muqaddima_file).
    """
    if source_path.is_dir():
        htm_files = sorted(
            f for f in source_path.iterdir() if f.suffix.lower() in (".htm", ".html")
        )
        if not htm_files:
            raise make_error(
                ErrorCode.EMPTY_INPUT,
                "Directory has no .htm files",
                context={"path": str(source_path)},
            )

        numbered_files = [f for f in htm_files if re.match(r"^\d+$", f.stem)]
        muqaddima_file = next((f for f in htm_files if f.stem == "المقدمة"), None)

        first_file = numbered_files[0] if numbered_files else htm_files[0]
        is_multi_volume = len(numbered_files) > 1 or (
            len(numbered_files) == 1 and muqaddima_file is not None
        )
        volume_count = len(numbered_files) if numbered_files else 1
    else:
        first_file = source_path
        is_multi_volume = False
        volume_count = 1
        muqaddima_file = None

    return first_file, is_multi_volume, volume_count, muqaddima_file


def _extract_card(content: str, filename: str) -> str:
    """Extract the metadata card from the first PageText div.

    The non-greedy (.*?)</div> regex works because the metadata card
    has NO nested <div> elements (verified across all 2,519 exports).

    Args:
        content: Full HTML content of the Shamela file.
        filename: Filename for error messages.

    Returns:
        HTML content of the metadata card.

    Raises:
        SourceEngineError: FORMAT_STRUCTURE_MISSING if no PageText div found.
    """
    card_match = _RE_CARD.search(content)
    if not card_match:
        raise make_error(
            ErrorCode.FORMAT_STRUCTURE_MISSING,
            f"No PageText div found — file may not be a Shamela export: {filename}",
            context={"filename": filename},
        )
    return card_match.group(1)


def _parse_header(card: str, result: dict[str, Any]) -> None:
    """Extract display title and short author from card header.

    Pattern: <span class='title'>TITLE&nbsp;&nbsp;&nbsp;</span>
             <span class='footnote'>(AUTHOR_SHORT)</span>
    """
    header_match = _RE_HEADER.match(card)
    if header_match:
        result["display_title"] = strip_tags(header_match.group(1)).strip()
        if header_match.group(2):
            result["author_short"] = header_match.group(2).strip()


def _parse_category(card: str, result: dict[str, Any]) -> None:
    """Extract القسم (category) from the card."""
    cat_match = _RE_CATEGORY.search(card)
    if cat_match:
        result["shamela_category"] = strip_tags(cat_match.group(1)).strip()


def _parse_bibliographic_fields(card: str, result: dict[str, Any]) -> None:
    """Parse all bibliographic fields from the metadata card.

    Uses FIELD_MAP for known labels, MUHAQIQ_KEYWORDS for long-tail
    editorial labels, and _extra_card_fields for everything else.
    """
    for m in _RE_FIELD.finditer(card):
        label = strip_tags(m.group(1)).strip()
        value = strip_tags(m.group(2)).strip()

        if label in FIELD_MAP and value:
            internal_name = FIELD_MAP[label]
            # Don't overwrite primary fields with alternatives
            if internal_name not in result or label in (
                "الكتاب",
                "المؤلف",
                "المحقق",
            ):
                result[internal_name] = value
                result[f"_field_source_{internal_name}"] = label
        elif (
            value
            and label not in MUHAQIQ_EXCLUSIONS
            and any(kw in label for kw in MUHAQIQ_KEYWORDS)
        ):
            # Long-tail muhaqiq label caught by pattern matching.
            if "muhaqiq_name_raw" not in result:
                result["muhaqiq_name_raw"] = value
                result["_field_source_muhaqiq_name_raw"] = label
        elif value:
            # Capture unmapped card fields rather than silently dropping them.
            if "_extra_card_fields" not in result:
                result["_extra_card_fields"] = {}
            result["_extra_card_fields"][label] = value


def _parse_death_dates(result: dict[str, Any]) -> None:
    """Extract death dates from author and muhaqiq fields.

    Author patterns: (ت NNN هـ), (المتوفى: NNN هـ), (NNN - NNN هـ)
    Muhaqiq pattern: [ت NNN هـ] (square brackets)
    """
    if "author_name_raw" in result:
        raw = result["author_name_raw"]
        death_match = _RE_AUTHOR_DEATH.search(raw)
        if death_match:
            result["author_death_hijri"] = int(death_match.group(1))
        else:
            range_match = _RE_AUTHOR_RANGE.search(raw)
            if range_match:
                result["author_birth_hijri"] = int(range_match.group(1))
                result["author_death_hijri"] = int(range_match.group(2))
        # Extract clean name (before parenthetical)
        clean_match = _RE_AUTHOR_CLEAN.match(raw)
        if clean_match:
            result["author_name_clean"] = clean_match.group(1).strip()

    if "muhaqiq_name_raw" in result:
        raw = result["muhaqiq_name_raw"]
        muh_death = _RE_MUHAQIQ_DEATH.search(raw)
        if muh_death:
            result["muhaqiq_death_hijri"] = int(muh_death.group(1))
        clean_muh = _RE_MUHAQIQ_CLEAN.match(raw)
        if clean_muh:
            result["muhaqiq_name_clean"] = clean_muh.group(1).strip()


def _parse_physical_page_count(result: dict[str, Any]) -> None:
    """Parse physical page count from عدد الصفحات.

    This is the PHYSICAL BOOK page count — NOT the digital body pages.
    """
    if "page_count_raw" in result:
        digits = _RE_DIGITS.findall(result["page_count_raw"])
        if digits:
            result["_physical_page_count"] = int(digits[0])


def _parse_edition(result: dict[str, Any]) -> None:
    """Parse edition number and year(s) from الطبعة.

    Handles suffix-based years (هـ/م) and bare-year heuristics.
    """
    if "edition_raw" not in result:
        return

    edition_raw = result["edition_raw"]
    result["edition_number"] = parse_arabic_ordinal(edition_raw)

    # Extract ALL year+suffix pairs
    for year_m in _RE_YEAR_SUFFIX.finditer(edition_raw):
        year_val = int(year_m.group(1))
        if year_m.group(2) == "هـ":
            result["edition_year_hijri"] = year_val
        else:
            result["edition_year_miladi"] = year_val

    # Bare years without suffix (fallback)
    if "edition_year_hijri" not in result and "edition_year_miladi" not in result:
        bare_years = _RE_BARE_YEAR.findall(edition_raw)
        if len(bare_years) == 2:
            y1, y2 = int(bare_years[0]), int(bare_years[1])
            if y1 <= 1500 and y2 > 1500:
                result["edition_year_hijri"] = y1
                result["edition_year_miladi"] = y2
            elif y1 > 1500 and y2 <= 1500:
                result["edition_year_miladi"] = y1
                result["edition_year_hijri"] = y2
            else:
                result["edition_year_miladi"] = max(y1, y2)
        elif len(bare_years) == 1:
            year_val = int(bare_years[0])
            if year_val > 1500:
                result["edition_year_miladi"] = year_val
            else:
                result["edition_year_hijri"] = year_val


def _parse_publication_year_fallback(result: dict[str, Any]) -> None:
    """Parse publication year from عام النشر / سنة النشر as fallback.

    Only fires when the edition field didn't already produce year values.
    """
    if "publication_year_raw" not in result:
        return
    if "edition_year_hijri" in result or "edition_year_miladi" in result:
        return

    pub_raw = result["publication_year_raw"]
    for year_m in _RE_YEAR_SUFFIX.finditer(pub_raw):
        year_val = int(year_m.group(1))
        if year_m.group(2) == "هـ":
            result["edition_year_hijri"] = year_val
        else:
            result["edition_year_miladi"] = year_val

    if "edition_year_hijri" not in result and "edition_year_miladi" not in result:
        bare_years = _RE_BARE_YEAR.findall(pub_raw)
        if len(bare_years) == 1:
            year_val = int(bare_years[0])
            if year_val > 1500:
                result["edition_year_miladi"] = year_val
            else:
                result["edition_year_hijri"] = year_val


def _parse_metadata_volume_count(result: dict[str, Any]) -> None:
    """Parse volume count from عدد الأجزاء / عدد المجلدات as cross-check."""
    if "volume_count_raw" in result:
        digits = _RE_DIGITS.findall(result["volume_count_raw"])
        if digits:
            result["_metadata_volume_count"] = int(digits[0])


def _extract_text_sample(content: str) -> str:
    """Extract first 2000 chars of body text for LLM inference.

    Uses split-based extraction (NOT regex) because PageText contains
    a nested <div class='PageHead'>...</div>, and the non-greedy regex
    stops at PageHead's closing </div>.

    Args:
        content: Full HTML content.

    Returns:
        Up to 2000 characters of stripped body text.
    """
    body_text_parts: list[str] = []
    page_segments = re.split(r"<div class='PageText'>", content)

    for i, seg in enumerate(page_segments):
        if i <= 1:  # Before first PageText (HTML head) + metadata card
            continue
        # Each segment = PageHead div + body text + </div> (PageText close) + ...
        after_pagehead = seg.split("</div>", 1)
        if len(after_pagehead) < 2:
            continue
        body_html = after_pagehead[1].split("</div>")[0]
        # Remove footnotes (after <hr> separator)
        body_html = _RE_FOOTNOTE_HR.sub("", body_html)
        body = strip_tags(body_html).strip()
        if body:
            body_text_parts.append(body)
        if sum(len(p) for p in body_text_parts) > 2000:
            break

    return "\n".join(body_text_parts)[:2000]


def _run_quality_inspection(
    body_page_count: int,
    result: dict[str, Any],
    content: str,
    page_segments: list[str],
) -> list[dict[str, str]]:
    """Run 5 deterministic quality checks on the extracted content.

    Args:
        body_page_count: Number of digital body pages.
        result: Extraction result dict (for physical page count).
        content: Full HTML content (for encoding check).
        page_segments: Content split by PageText divs.

    Returns:
        List of quality issue dicts with keys: check, severity, detail.
    """
    quality_issues: list[dict[str, str]] = []

    # Check 1: Minimum content threshold
    if body_page_count < 3:
        quality_issues.append(
            {
                "check": "content_minimal",
                "severity": "info",
                "detail": f"Only {body_page_count} content pages",
            }
        )

    # Check 2: Page count consistency
    if "_physical_page_count" in result and body_page_count > 0:
        physical = result["_physical_page_count"]
        if physical > 0:
            ratio = body_page_count / physical
            if ratio < 0.15:
                quality_issues.append(
                    {
                        "check": "page_count_mismatch",
                        "severity": "warning",
                        "detail": (
                            f"Digital pages ({body_page_count}) are {ratio:.0%} of "
                            f"claimed physical pages ({physical}) — likely partial export"
                        ),
                    }
                )
            elif ratio > 8.0:
                quality_issues.append(
                    {
                        "check": "page_count_mismatch",
                        "severity": "info",
                        "detail": (
                            f"Digital pages ({body_page_count}) exceed claimed physical "
                            f"pages ({physical}) by {ratio:.1f}x — likely metadata error"
                        ),
                    }
                )

    # Check 3: Encoding quality (U+FFFD replacement characters)
    replacement_count = content.count("\ufffd")
    if replacement_count > 0:
        quality_issues.append(
            {
                "check": "encoding_suspect",
                "severity": "warning",
                "detail": f"{replacement_count} Unicode replacement characters found",
            }
        )

    # Check 4: Empty page ratio
    empty_page_count = 0
    for i, seg in enumerate(page_segments):
        if i <= 1:
            continue
        seg_text = strip_tags(seg).strip()
        if len(seg_text) < 50:
            empty_page_count += 1
    if body_page_count > 10 and empty_page_count / body_page_count > 0.25:
        quality_issues.append(
            {
                "check": "high_empty_ratio",
                "severity": "warning",
                "detail": (
                    f"{empty_page_count}/{body_page_count} pages have <50 chars of content"
                ),
            }
        )

    # Check 5: Truncation detection (only meaningful with page_count_mismatch)
    has_page_mismatch = any(q["check"] == "page_count_mismatch" for q in quality_issues)
    if has_page_mismatch and body_page_count > 5:
        last_seg = page_segments[-1] if len(page_segments) > 2 else ""
        last_seg_html = last_seg.split("</div>", 1)
        last_body_text = ""
        if len(last_seg_html) >= 2:
            last_body_html = last_seg_html[1].split("</div>")[0]
            last_body_html = _RE_FOOTNOTE_HR.sub("", last_body_html)
            last_body_text = strip_tags(last_body_html).strip()
        last_char = last_body_text[-1:] if last_body_text else ""
        if last_char and last_char not in ".؟!»)﴾]،" and not last_char.isdigit():
            quality_issues.append(
                {
                    "check": "truncation_with_mismatch",
                    "severity": "warning",
                    "detail": (
                        "Last page ends without sentence-ending punctuation AND "
                        "page count is inconsistent — strongly suggests truncated export"
                    ),
                }
            )

    return quality_issues


# Keys to collect into format_specific_metadata
_FORMAT_SPECIFIC_KEYS: tuple[str, ...] = (
    "shamela_category",
    "shamela_publish_date",
    "source_note",
    "editorial_note",
    "thesis_info",
    "supervisor",
    "distributor",
    "foreword_by",
    "compiler_name_raw",
    "translator",
    "original_author_name_raw",
    "commentator_name_raw",
    "publication_year_raw",
    "volume_count_raw",
    "edition_raw",
    "page_count_raw",
    "author_short",
    "preparer",
    "_academic_course_code",
    "_academic_level",
    "_academic_year",
    "_source_origin",
    "_tahqiq_origin",
)


def _assemble_format_specific_metadata(result: dict[str, Any]) -> None:
    """Collect secondary fields into format_specific_metadata dict."""
    fmt: dict[str, Any] = {}

    for key in _FORMAT_SPECIFIC_KEYS:
        if key in result:
            fmt[key] = result[key]

    if result.get("has_muqaddima"):
        fmt["has_muqaddima"] = True
    if "_physical_page_count" in result:
        fmt["physical_page_count"] = result["_physical_page_count"]
    if "_metadata_volume_count" in result:
        fmt["metadata_volume_count"] = result["_metadata_volume_count"]
    if "_extra_card_fields" in result:
        fmt["extra_card_fields"] = result["_extra_card_fields"]
    if result.get("_quality_issues"):
        fmt["quality_issues"] = result["_quality_issues"]

    result["format_specific_metadata"] = fmt
