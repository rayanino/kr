"""Verify HARDENING_SESSION_PROTOCOL.md version consistency.

Checks that the protocol title, frontmatter governing_version, and NEXT.md
reference all agree on the current protocol version. Exits 1 on mismatch.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROTOCOL = REPO_ROOT / "engines" / "excerpting" / "reference" / "HARDENING_SESSION_PROTOCOL.md"
NEXT_MD = REPO_ROOT / "NEXT.md"


def extract_title_version(text: str) -> str | None:
    m = re.search(r"^#\s+Hardening Session Protocol\s+v([\d.]+)", text, re.MULTILINE)
    return m.group(1) if m else None


def extract_frontmatter_version(text: str) -> str | None:
    m = re.search(r'^governing_version:\s*"?([\d.]+)"?', text, re.MULTILINE)
    return m.group(1) if m else None


def extract_next_md_version(text: str) -> str | None:
    m = re.search(r"HARDENING_SESSION_PROTOCOL\.md.*?v([\d.]+)", text)
    return m.group(1) if m else None


def main() -> int:
    protocol_text = PROTOCOL.read_text(encoding="utf-8")
    next_text = NEXT_MD.read_text(encoding="utf-8")

    title_v = extract_title_version(protocol_text)
    fm_v = extract_frontmatter_version(protocol_text)
    next_v = extract_next_md_version(next_text)

    versions = {"title": title_v, "frontmatter": fm_v, "NEXT.md": next_v}
    found = {k: v for k, v in versions.items() if v is not None}

    if not found:
        print("ERROR: No version found in any source")
        return 1

    unique = set(found.values())
    if len(unique) == 1:
        print(f"OK: All sources agree on v{unique.pop()}")
        return 0

    print("VERSION MISMATCH:")
    for source, ver in versions.items():
        print(f"  {source}: {ver or 'NOT FOUND'}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
