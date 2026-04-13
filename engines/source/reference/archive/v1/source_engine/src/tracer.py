"""Source engine — tracer bullet entry point.

Reads a Shamela HTML export directory, extracts metadata from info.html,
freezes source files, and writes SourceMetadata JSON.
"""

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


def process(input_path: Path, output_path: Path, config: dict) -> None:
    """Process a Shamela HTML source directory into SourceMetadata JSON.
    
    Args:
        input_path: Directory containing info.html and content.html
        output_path: Path to write the output JSON file
        config: Engine configuration (source_id override, etc.)
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Parse info.html ---
    info_html = (input_path / "info.html").read_text(encoding="utf-8")
    metadata = _parse_info_html(info_html)

    # --- Generate source_id ---
    author_slug = _slugify(metadata.get("author_name", "unknown"))
    title_slug = _slugify(metadata.get("title", "unknown"))
    science_slug = _category_to_science(metadata.get("category", ""))
    edition_hash = hashlib.md5(
        f"{metadata.get('muhaqiq', '')}{metadata.get('publisher', '')}{metadata.get('edition', '')}".encode()
    ).hexdigest()[:4]
    source_id = config.get("source_id", f"{science_slug}_{author_slug}_{title_slug}_{edition_hash}")
    work_id = f"{author_slug}_{title_slug}"

    # --- Freeze source files ---
    frozen_dir = output_path.parent / "frozen"
    frozen_dir.mkdir(parents=True, exist_ok=True)
    file_hashes = {}
    for src_file in input_path.iterdir():
        if src_file.is_file():
            content = src_file.read_bytes()
            file_hashes[src_file.name] = hashlib.sha256(content).hexdigest()
            shutil.copy2(src_file, frozen_dir / src_file.name)

    frozen_hash = hashlib.sha256(
        json.dumps(file_hashes, sort_keys=True).encode()
    ).hexdigest()[:16]

    # --- Build SourceMetadata ---
    now_utc = datetime.now(timezone.utc).isoformat()

    source_metadata = {
        "source_id": source_id,
        "work_id": work_id,
        "human_label": metadata.get("title", "Unknown"),
        "title_arabic": metadata.get("title", ""),
        "title_transliterated": None,
        "author": {
            "canonical_id": author_slug,
            "name_arabic": metadata.get("author_name", "Unknown"),
            "confidence": 0.9,
            "source_of_identification": "info.html المؤلف field",
        },
        "muhaqiq": {
            "canonical_id": _slugify(metadata.get("muhaqiq", "")),
            "name_arabic": metadata.get("muhaqiq", ""),
            "confidence": 0.85,
            "source_of_identification": "info.html المحقق field",
        } if metadata.get("muhaqiq") else None,
        "additional_authors": [],
        "science_scope": [science_slug],
        "genre": "sharh",
        "genre_chain": None,
        "level": None,
        "publisher": metadata.get("publisher"),
        "edition_number": _parse_edition_number(metadata.get("edition", "")),
        "publication_year_hijri": None,
        "publication_year_miladi": None,
        "source_format": "shamela_html",
        "authority_level": "primary",
        "structural_format": "commentary",
        "language": "ar",
        "page_count": None,
        "is_multi_layer": True,
        "text_layers": [
            {"layer_type": "matn", "author": {"canonical_id": "ibn_malik", "name_arabic": "ابن مالك", "confidence": 0.95, "source_of_identification": "known work attribution"}},
            {"layer_type": "sharh", "author": {"canonical_id": author_slug, "name_arabic": metadata.get("author_name", ""), "confidence": 0.95, "source_of_identification": "info.html"}},
        ],
        "trust_tier": "verified",
        "trust_score": 0.85,
        "trust_factors": [{"name": "known_publisher", "weight": 0.3, "score": 0.85, "reason": metadata.get("publisher", "Established publisher")}],
        "trust_reason": "Shamela HTML export from established publisher",
        "text_fidelity": "high",
        "text_fidelity_reason": "Digital text export, not OCR",
        "confidence_scores": {
            "genre": 0.85,
            "science_scope": 0.90,
            "structural_format": 0.90,
            "authority_level": 0.85,
        },
        "needs_review_fields": [],
        "volume_count": _parse_int(metadata.get("volumes", "1")),
        "volumes": [],
        "volumes_missing": [],
        "frozen_path": str(frozen_dir),
        "frozen_hash": frozen_hash,
        "frozen_file_hashes": file_hashes,
        "format_specific_metadata": {
            "shamela_description": metadata.get("description", ""),
        },
        "work_relationships": [],
        "status": "acquired",
        "intake_timestamp": now_utc,
        "acquisition_path": "manual",
        "metadata_history": [{
            "field": "initial_registration",
            "old_value": None,
            "new_value": "all fields extracted from info.html",
            "changed_by": "source_engine_tracer",
            "timestamp": now_utc,
        }],
        "enrichment_sources": [],
        "owner_authored_type": None,
        "compositional_profile": None,
        "difficulty_prediction": None,
        "tahqiq_fingerprint": None,
    }

    output_path.write_text(
        json.dumps(source_metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _parse_info_html(html: str) -> dict[str, str]:
    """Extract metadata fields from Shamela info.html table."""
    result = {}
    
    # Extract title from h1
    h1_match = re.search(r"<h1>(.*?)</h1>", html, re.DOTALL)
    if h1_match:
        result["title"] = _strip_tags(h1_match.group(1)).strip()

    # Extract table rows
    field_map = {
        "المؤلف": "author_name",
        "المحقق": "muhaqiq",
        "الناشر": "publisher",
        "الطبعة": "edition",
        "عدد الأجزاء": "volumes",
        "التصنيف": "category",
        "الوصف": "description",
    }
    for match in re.finditer(r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>", html, re.DOTALL):
        key = _strip_tags(match.group(1)).strip()
        value = _strip_tags(match.group(2)).strip()
        if key in field_map:
            result[field_map[key]] = value

    # Extract author short name from full name
    if "author_name" in result:
        full = result["author_name"]
        # Try to extract the kunya/laqab before the parenthetical
        paren_match = re.match(r"^(.*?)\s*\(", full)
        if paren_match:
            result["author_short"] = paren_match.group(1).strip()

    return result


def _strip_tags(html: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", html)


def _slugify(text: str) -> str:
    """Create a URL-safe slug from Arabic text.
    
    Checks longest matches first to avoid substring collisions
    (e.g., "ابن عقيل" matching inside "شرح ابن عقيل على ألفية ابن مالك").
    """
    # Transliterate common Arabic names — checked longest-first
    replacements = {
        "شرح ابن عقيل على ألفية ابن مالك": "sharh_ibn_aqil",
        "محمد محيي الدين عبد الحميد": "abdulhamid",
        "ابن عقيل": "ibn_aqil",
        "ابن مالك": "ibn_malik",
    }
    # Sort by key length descending to match longest substring first
    for arabic, latin in sorted(replacements.items(), key=lambda kv: len(kv[0]), reverse=True):
        if arabic in text:
            return latin
    # Fallback: hash
    return hashlib.md5(text.encode()).hexdigest()[:8]


def _category_to_science(category: str) -> str:
    """Map Shamela category text to a normalized science slug.
    
    Shamela categories are free-text Arabic like "نحو وصرف" or "فقه شافعي".
    This maps them to the KR science classification IDs.
    """
    mapping = {
        "نحو": "nahw",
        "صرف": "sarf",
        "نحو وصرف": "nahw",
        "بلاغة": "balagha",
        "فقه": "fiqh",
        "أصول الفقه": "usul_fiqh",
        "أصول": "usul_fiqh",
        "حديث": "hadith",
        "تفسير": "tafsir",
        "عقيدة": "aqidah",
        "توحيد": "aqidah",
        "سيرة": "sirah",
        "تاريخ": "tarikh",
        "أدب": "adab",
        "منطق": "mantiq",
    }
    # Check longest matches first (substring match)
    for arabic, slug in sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True):
        if arabic in category:
            return slug
    return "unclassified"


def _parse_edition_number(text: str) -> int | None:
    """Parse Arabic edition number text to integer."""
    ordinal_map = {
        "الأولى": 1, "الثانية": 2, "الثالثة": 3, "الرابعة": 4,
        "الخامسة": 5, "السادسة": 6, "السابعة": 7, "الثامنة": 8,
        "التاسعة": 9, "العاشرة": 10, "العشرون": 20,
    }
    for word, num in ordinal_map.items():
        if word in text:
            return num
    digits = re.findall(r"\d+", text)
    return int(digits[0]) if digits else None


def _parse_int(text: str) -> int | None:
    """Extract first integer from text."""
    digits = re.findall(r"\d+", text)
    return int(digits[0]) if digits else None
