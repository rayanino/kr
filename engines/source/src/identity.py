"""Source identity model — SPEC §4.A.1.

Generates source_id (hash-based, permanent) and work_id (author+title slug).
"""

import hashlib
import re
import unicodedata


def compute_file_hash(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_composite_hash(file_hashes: dict[str, str]) -> str:
    """Compute composite SHA-256 from sorted individual file hashes.

    For single-file sources, this is the file's own hash.
    For multi-file sources, hashes are sorted by filename and combined.
    """
    if len(file_hashes) == 1:
        return next(iter(file_hashes.values()))

    sha256 = hashlib.sha256()
    for filename in sorted(file_hashes.keys()):
        sha256.update(file_hashes[filename].encode("utf-8"))
    return sha256.hexdigest()


def generate_source_id(composite_hash: str) -> str:
    """Generate source_id from composite hash.

    Format: src_{first 8 hex chars of composite hash}.
    Collision handling deferred — astronomically unlikely.
    """
    return f"src_{composite_hash[:8]}"


def _transliterate_arabic(text: str) -> str:
    """Basic Arabic-to-ASCII transliteration for slug generation.

    Not a full transliteration — just enough to produce readable slugs.
    """
    # Common Arabic letter mappings (simplified)
    mapping = {
        "ا": "a", "أ": "a", "إ": "i", "آ": "aa", "ب": "b", "ت": "t",
        "ث": "th", "ج": "j", "ح": "h", "خ": "kh", "د": "d", "ذ": "dh",
        "ر": "r", "ز": "z", "س": "s", "ش": "sh", "ص": "s", "ض": "d",
        "ط": "t", "ظ": "z", "ع": "'", "غ": "gh", "ف": "f", "ق": "q",
        "ك": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h", "و": "w",
        "ي": "y", "ى": "a", "ة": "h", "ئ": "'", "ؤ": "'",
    }

    result = []
    for char in text:
        if char in mapping:
            result.append(mapping[char])
        elif char.isascii() and char.isalnum():
            result.append(char.lower())
        elif char in (" ", "_", "-"):
            result.append("_")
        # Skip diacritics, punctuation, etc.

    slug = "".join(result)
    # Clean up: collapse underscores, strip edges
    slug = re.sub(r"_+", "_", slug).strip("_'")
    return slug


def generate_work_id(author_name: str, title: str) -> str:
    """Generate work_id from author name and title.

    Format: wrk_{author_slug}_{title_slug} (max 40 chars total after wrk_).
    """
    author_slug = _transliterate_arabic(author_name)[:15]
    title_slug = _transliterate_arabic(title)[:20]

    # Remove the definite article from title slug
    for prefix in ("al_", "al-"):
        if title_slug.startswith(prefix):
            title_slug = title_slug[len(prefix):]

    work_id = f"wrk_{author_slug}_{title_slug}"
    # Ensure max 40 chars after wrk_
    if len(work_id) > 44:
        work_id = work_id[:44]
    return work_id


def generate_human_label(title: str) -> str:
    """Generate a human-readable label from the title.

    Used for logs, CLI output, and owner-facing displays.
    Not a primary key — need not be unique.
    """
    slug = _transliterate_arabic(title)
    # Keep it short and readable
    return slug[:30] if slug else "unknown"
