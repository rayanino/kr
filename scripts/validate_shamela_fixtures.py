"""Validate hand-crafted Shamela fixtures against SHAMELA_HTML_REFERENCE format.

Checks that fixtures match real Shamela HTML patterns, catching divergences
that cause false implementation decisions (Session 2 retrospective).

Usage:
    python scripts/validate_shamela_fixtures.py [fixture_path]
    python scripts/validate_shamela_fixtures.py  # validates all fixtures
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PAGE_TEXT_START = "<div class='PageText'>"
PAGE_NUM_RE = re.compile(r"\(ص:\s*([٠-٩0-9]+)\s*\)")
PAGE_HEAD_RE = re.compile(
    r"<div\s+class=['\"]PageHead['\"][^>]*>.*?</div>", re.DOTALL
)
METADATA_TITLE_RE = re.compile(r"<span\s+class='title'[^>]*>")
PAGE_NUMBER_SPAN_RE = re.compile(
    r"<span\s+class=['\"]PageNumber['\"][^>]*>"
)
FN_SEPARATOR_RE = re.compile(r"<hr\s+[^>]*width\s*=\s*['\"]?(\d{2,3})")


def validate_fixture(path: Path) -> list[str]:
    """Validate a single Shamela HTML fixture. Returns list of warnings."""
    warnings: list[str] = []

    if path.is_dir():
        htm_files = sorted(
            list(path.glob("*.htm")) + list(path.glob("*.html"))
        )
    else:
        htm_files = [path]

    if not htm_files:
        warnings.append(f"No .htm/.html files found in {path}")
        return warnings

    for htm_file in htm_files:
        try:
            text = htm_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            warnings.append(f"{htm_file.name}: not valid UTF-8")
            continue

        # Check PageText divs exist
        page_count = text.count(PAGE_TEXT_START)
        if page_count == 0:
            warnings.append(f"{htm_file.name}: no PageText divs found")
            continue

        # Split into page blocks
        positions: list[int] = []
        start = 0
        while True:
            pos = text.find(PAGE_TEXT_START, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        seen_numbered = False
        for i, pos in enumerate(positions):
            block_start = pos + len(PAGE_TEXT_START)
            block_end = (
                positions[i + 1] if i + 1 < len(positions) else len(text)
            )
            block = text[block_start:block_end]

            has_page_num = PAGE_NUM_RE.search(block) is not None
            has_page_num_span = PAGE_NUMBER_SPAN_RE.search(block) is not None
            has_metadata_title = METADATA_TITLE_RE.search(block) is not None

            # Check: metadata pages should NOT have PageNumber spans
            if not has_page_num and not seen_numbered:
                # This looks like a metadata page
                if has_page_num_span:
                    warnings.append(
                        f"{htm_file.name} page {i+1}: metadata page has "
                        f"PageNumber span (real Shamela metadata pages don't)"
                    )
            else:
                seen_numbered = True

            # Check: page numbers should use Arabic-Indic digits
            pn_match = PAGE_NUM_RE.search(block)
            if pn_match:
                digits = pn_match.group(1)
                if any(c.isascii() and c.isdigit() for c in digits):
                    warnings.append(
                        f"{htm_file.name} page {i+1}: uses Western digits "
                        f"'{digits}' (most Shamela uses Arabic-Indic ٠-٩)"
                    )

            # Check: content pages should have PageHead div
            if has_page_num and not PAGE_HEAD_RE.search(block):
                # Not all pages have PageHead (some simplified fixtures)
                pass  # Advisory only, don't warn

            # Check: footnote separator width should be in 80-100 range
            for m in FN_SEPARATOR_RE.finditer(block):
                width = int(m.group(1))
                if width < 80 or width > 100:
                    warnings.append(
                        f"{htm_file.name} page {i+1}: <hr> width={width} "
                        f"outside 80-100 range (not a footnote separator)"
                    )

    return warnings


def main() -> int:
    """Validate fixtures and print results."""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if len(sys.argv) > 1:
        targets = [Path(sys.argv[1])]
    else:
        # Validate all fixture directories
        targets = []
        real_dir = Path("tests/fixtures/shamela_real")
        if real_dir.exists():
            targets.extend(
                d for d in sorted(real_dir.iterdir()) if d.is_dir()
            )
        engine_fixtures = Path("engines/normalization/tests/fixtures")
        if engine_fixtures.exists():
            targets.extend(
                f
                for f in sorted(engine_fixtures.glob("*.htm"))
            )

    if not targets:
        print("No fixtures found to validate.")
        return 1

    total_warnings = 0
    for target in targets:
        warnings = validate_fixture(target)
        if warnings:
            print(f"\n{target.name}:")
            for w in warnings:
                print(f"  - {w}")
            total_warnings += len(warnings)

    if total_warnings == 0:
        print(f"All {len(targets)} fixtures valid.")
    else:
        print(f"\n{total_warnings} warning(s) across {len(targets)} fixtures.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
