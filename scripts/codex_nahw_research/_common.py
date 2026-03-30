"""Shared utilities for Codex nahw corpus research scripts.

Pure stdlib — no BeautifulSoup, no Pydantic, no engine imports.
Replicates key patterns from normalization engine for standalone use.
"""
from __future__ import annotations

import html
import itertools
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SHAMELA_DIR = PROJECT_ROOT / "shamela-export-samples"
OUTPUT_DIR = PROJECT_ROOT / "reference" / "research"

# ──────────────────────────────────────────────────────────────────
# Regex patterns (replicated from normalization engine)
# ──────────────────────────────────────────────────────────────────

TITLE_TAG_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
VOLUME_SUFFIX_RE = re.compile(r"\s*-\s*جـ\s*[٠-٩0-9]+\s*$")
CATEGORY_RE = re.compile(
    r"<span\s+class='title'>القسم:</span>\s*(.+?)(?:<hr|<p|$)",
    re.DOTALL,
)
# Double quotes = content headings (single quotes = metadata labels)
CONTENT_TITLE_RE = re.compile(r'<span\s+class="title">(.*?)</span>', re.DOTALL)
PAGE_TEXT_START = "<div class='PageText'>"

# ──────────────────────────────────────────────────────────────────
# Arabic normalization (replicated from structure_discovery.py)
# ──────────────────────────────────────────────────────────────────

_DIACRITICS = frozenset(
    chr(c) for c in range(0x064B, 0x0656)
) | {"\u0670"}


def normalize_arabic(text: str) -> str:
    """Normalize Arabic text for matching — never for storage."""
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
# Heading type classification
# ──────────────────────────────────────────────────────────────────

class HeadingType(str, Enum):
    """Prefix-based heading classification."""
    KITAB = "كتاب"
    BAB = "باب"
    FASL = "فصل"
    MASALA = "مسألة"
    MABHATH = "مبحث"
    MATLAB = "مطلب"
    MUDKHAL = "مدخل"
    TAQSIM = "تقسيم"
    TANBIH = "تنبيه"
    FAIDA = "فائدة"
    QAIDA = "قاعدة"
    KHATIMA = "خاتمة"
    MUQADDIMA = "مقدمة"
    SHARH = "شرح"
    DHIKR = "ذكر"
    TAFSIR = "تفسير"
    IRAB = "إعراب"
    VOLUME = "مجلد"
    TATIMMA = "تتمة"
    FAR = "فرع"
    UNCLASSIFIED = "غير مصنف"


# Ordered by specificity — longer matches first to avoid partial prefix hits
_HEADING_KEYWORDS: list[tuple[str, HeadingType]] = [
    ("مقدمة", HeadingType.MUQADDIMA),
    ("خاتمة", HeadingType.KHATIMA),
    ("المجلد", HeadingType.VOLUME),
    ("الجزء", HeadingType.VOLUME),
    ("كتاب", HeadingType.KITAB),
    ("الكتاب", HeadingType.KITAB),
    ("هذا باب", HeadingType.BAB),
    ("الباب", HeadingType.BAB),
    ("باب", HeadingType.BAB),
    ("الفصل", HeadingType.FASL),
    ("فصل", HeadingType.FASL),
    ("المبحث", HeadingType.MABHATH),
    ("مبحث", HeadingType.MABHATH),
    ("المطلب", HeadingType.MATLAB),
    ("مطلب", HeadingType.MATLAB),
    ("المسألة", HeadingType.MASALA),
    ("مسألة", HeadingType.MASALA),
    ("مسائل", HeadingType.MASALA),
    ("التقسيم", HeadingType.TAQSIM),
    ("تقسيم", HeadingType.TAQSIM),
    ("تنبيهات", HeadingType.TANBIH),
    ("تنبيه", HeadingType.TANBIH),
    ("فوائد", HeadingType.FAIDA),
    ("فائدة", HeadingType.FAIDA),
    ("قواعد", HeadingType.QAIDA),
    ("قاعدة", HeadingType.QAIDA),
    ("تتمة", HeadingType.TATIMMA),
    ("الفرع", HeadingType.FAR),
    ("فرع", HeadingType.FAR),
    ("مدخل", HeadingType.MUDKHAL),
    ("شرح", HeadingType.SHARH),
    ("ذكر", HeadingType.DHIKR),
    ("تفسير", HeadingType.TAFSIR),
    ("إعراب", HeadingType.IRAB),
]

# Heading type → hierarchy depth level
HEADING_DEPTH: dict[HeadingType, int] = {
    HeadingType.VOLUME: 0,
    HeadingType.KITAB: 1,
    HeadingType.BAB: 2,
    HeadingType.FASL: 3,
    HeadingType.MABHATH: 3,
    HeadingType.TAQSIM: 3,
    HeadingType.MUDKHAL: 3,
    HeadingType.IRAB: 3,
    HeadingType.SHARH: 3,
    HeadingType.DHIKR: 3,
    HeadingType.TAFSIR: 3,
    HeadingType.MASALA: 4,
    HeadingType.MATLAB: 4,
    HeadingType.FAR: 4,
    HeadingType.TANBIH: 5,
    HeadingType.FAIDA: 5,
    HeadingType.QAIDA: 5,
    HeadingType.TATIMMA: 5,
    HeadingType.KHATIMA: 5,
    HeadingType.MUQADDIMA: 2,
    HeadingType.UNCLASSIFIED: -1,
}


def classify_heading(text: str) -> HeadingType:
    """Classify a heading by its prefix keyword."""
    normalized = normalize_arabic(text)
    for keyword, htype in _HEADING_KEYWORDS:
        kw_norm = normalize_arabic(keyword)
        if normalized.startswith(kw_norm) or normalized.startswith("هذا " + kw_norm):
            return htype
    # Check for bracketed numbered headings: [الباب الأول: ...]
    if normalized.startswith("["):
        inner = normalized.lstrip("[").split("]")[0]
        for keyword, htype in _HEADING_KEYWORDS:
            kw_norm = normalize_arabic(keyword)
            if inner.startswith(kw_norm):
                return htype
    return HeadingType.UNCLASSIFIED


# ──────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────

@dataclass
class BookEntry:
    """A single book (possibly multi-volume)."""
    name: str
    title: str
    category: str
    first_file: Path
    is_multivolume: bool
    all_files: list[Path] = field(default_factory=list)
    match_tier: str = ""
    match_reason: str = ""


@dataclass
class RawHeading:
    """A heading extracted from a Shamela HTML file."""
    raw: str
    full: str
    heading_type: str
    position: int
    volume: int = 1
    file_name: str = ""


# ──────────────────────────────────────────────────────────────────
# Book discovery
# ──────────────────────────────────────────────────────────────────

def discover_all_books(shamela_dir: Path | None = None) -> list[tuple[str, Path, bool, list[Path]]]:
    """Find all Shamela .htm books.

    Returns list of (name, first_file, is_multivolume, all_files).
    Adapted from scripts/normalization_corpus_sweep.py:discover_books.
    """
    root = shamela_dir or SHAMELA_DIR
    results: list[tuple[str, Path, bool, list[Path]]] = []
    if not root.exists():
        logger.error("Shamela directory not found: %s", root)
        return results

    for item in sorted(root.iterdir()):
        if item.name.startswith("."):
            continue
        if item.is_dir():
            htms = sorted(item.glob("*.htm"))
            if htms:
                results.append((item.name, htms[0], True, htms))
        elif item.suffix.lower() == ".htm":
            results.append((item.stem, item, False, [item]))

    return results


def extract_title_fast(path: Path) -> str:
    """Extract book title from first 60 lines. Strips volume suffix."""
    try:
        with open(path, encoding="utf-8") as f:
            head = "".join(itertools.islice(f, 60))
        m = TITLE_TAG_RE.search(head)
        if m:
            title = html.unescape(m.group(1)).strip()
            return VOLUME_SUFFIX_RE.sub("", title)
        return ""
    except Exception as e:
        logger.warning("Failed to read title from %s: %s", path, e)
        return ""


def extract_category_fast(path: Path) -> str:
    """Extract القسم field from the metadata card (first 60 lines)."""
    try:
        with open(path, encoding="utf-8") as f:
            head = "".join(itertools.islice(f, 60))
        m = CATEGORY_RE.search(head)
        if m:
            raw = m.group(1).strip()
            # Strip residual HTML tags
            raw = re.sub(r"<[^>]+>", "", raw).strip()
            return html.unescape(raw)
        return ""
    except Exception as e:
        logger.warning("Failed to read category from %s: %s", path, e)
        return ""


def clean_heading_text(raw_html: str) -> str:
    """Clean a raw heading extracted from <span class="title">."""
    text = html.unescape(raw_html)
    # Strip ZWNJ (&#8204; / U+200C)
    text = text.replace("\u200c", "")
    # Strip nested <font> tags (decorative in Shamela)
    text = re.sub(r"</?font[^>]*>", "", text)
    # Strip any remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Clean up whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Strip leading/trailing colons and whitespace
    text = text.strip(": \t\n\r،")
    return text


def extract_headings_from_file(
    path: Path,
    volume: int = 1,
) -> list[RawHeading]:
    """Extract all content headings from a Shamela HTML file.

    Skips the first PageText div (metadata card).
    Uses double-quote title spans only.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning("Failed to read %s: %s", path, e)
        return []

    # Skip the metadata card (first PageText div)
    first_page = content.find(PAGE_TEXT_START)
    if first_page == -1:
        return []
    second_page = content.find(PAGE_TEXT_START, first_page + len(PAGE_TEXT_START))
    search_start = second_page if second_page != -1 else first_page + len(PAGE_TEXT_START)

    body = content[search_start:]
    matches = list(CONTENT_TITLE_RE.finditer(body))

    headings: list[RawHeading] = []
    for i, m in enumerate(matches):
        raw = clean_heading_text(m.group(1))
        if not raw:
            continue
        htype = classify_heading(raw)
        headings.append(RawHeading(
            raw=raw,
            full=raw,
            heading_type=htype.value,
            position=i + 1,
            volume=volume,
            file_name=path.name,
        ))

    # Merge consecutive title spans (Sibawayh pattern):
    # If two headings appear with <50 chars between them in HTML,
    # and the second doesn't start with a keyword prefix, merge them.
    merged: list[RawHeading] = []
    i = 0
    while i < len(headings):
        current = headings[i]
        # Check if next heading should merge
        if i + 1 < len(headings):
            nxt = headings[i + 1]
            nxt_type = classify_heading(nxt.raw)
            if i < len(matches) - 1:
                gap = matches[i + 1].start() - matches[i].end()
                if gap < 80 and nxt_type == HeadingType.UNCLASSIFIED:
                    merged_text = f"{current.raw} {nxt.raw}"
                    merged_type = classify_heading(merged_text)
                    merged.append(RawHeading(
                        raw=merged_text,
                        full=merged_text,
                        heading_type=merged_type.value,
                        position=current.position,
                        volume=volume,
                        file_name=path.name,
                    ))
                    i += 2
                    continue
        merged.append(current)
        i += 1

    return merged


def strip_heading_prefix(text: str) -> str:
    """Strip structural prefix (باب, فصل, etc.) to get the core topic.

    Also handles: هذا باب X, [الباب الأول: X], باب في X.
    """
    normalized = normalize_arabic(text)

    # Handle bracketed: [الباب الأول: X] → X
    bracket_match = re.match(r"\[.*?:\s*(.*)\]", normalized)
    if bracket_match:
        return bracket_match.group(1).strip()

    # Handle "هذا باب X" → X
    if normalized.startswith("هذا "):
        normalized = normalized[4:].strip()

    # Strip known prefixes
    prefixes = [
        "كتاب", "الكتاب",
        "باب", "الباب",
        "فصل", "الفصل",
        "مبحث", "المبحث",
        "مطلب", "المطلب",
        "مسالة", "المسالة", "مسايل",
        "التقسيم", "تقسيم",
        "تنبيه", "تنبيهات",
        "فايدة", "فوايد",
        "قاعدة", "قواعد",
        "مقدمة", "خاتمة", "تتمة",
        "مدخل", "المدخل",
        "ذكر", "شرح", "تفسير", "اعراب",
    ]

    for prefix in sorted(prefixes, key=len, reverse=True):
        if normalized.startswith(prefix):
            rest = normalized[len(prefix):].strip()
            # Skip ordinals after prefix: الأول, الثاني, etc.
            rest = re.sub(
                r"^(الاول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر)"
                r"(\s*:\s*|\s+في\s+|\s+فى\s+|\s+)",
                "", rest
            )
            # Strip leading في/فى
            rest = re.sub(r"^(في|فى)\s+", "", rest)
            if rest:
                return rest
            break

    return normalized
