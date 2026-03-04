#!/usr/bin/env python3
"""Extract specific sections from VISION.md for Claude Chat session attachments.

Usage:
    python tools/extract_vision_sections.py 2 7 > vision_excerpt.md
    python tools/extract_vision_sections.py 2 5 > vision_excerpt.md

Sections are identified by `## §N` headers. Each section runs from its
header to the next `## §` header (or end of file).

This tool exists to reduce context overhead: VISION.md is ~245KB but
a typical session only needs 2-3 sections (~50-60KB).
"""
import re
import sys
from pathlib import Path


def find_vision():
    for p in [
        Path(__file__).resolve().parent.parent / "VISION.md",
        Path("VISION.md"),
    ]:
        if p.exists():
            return p
    print("ERROR: Cannot find VISION.md", file=sys.stderr)
    sys.exit(1)


def extract(text, nums):
    pattern = re.compile(r'^(## §(\d+).*)$', re.MULTILINE)
    matches = list(pattern.finditer(text))
    if not matches:
        print("ERROR: No `## §N` headers found in VISION.md", file=sys.stderr)
        sys.exit(1)

    sections = {}
    for i, m in enumerate(matches):
        n = int(m.group(2))
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        sections[n] = text[start:end].rstrip()

    parts = []
    for n in sorted(nums):
        if n in sections:
            parts.append(sections[n])
        else:
            print(f"WARNING: §{n} not found. Available: {sorted(sections.keys())}", file=sys.stderr)

    header = f"# VISION.md — Extracted: {', '.join(f'§{n}' for n in sorted(nums))}\n"
    header += "# Use full VISION.md for complete document.\n\n"
    return header + "\n\n---\n\n".join(parts) + "\n"


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/extract_vision_sections.py 2 7 > vision_excerpt.md")
        sys.exit(1)

    try:
        nums = [int(x) for x in sys.argv[1:]]
    except ValueError as e:
        print(f"ERROR: All arguments must be section numbers (integers). Got: {e}", file=sys.stderr)
        sys.exit(1)

    text = find_vision().read_text(encoding="utf-8")
    result = extract(text, nums)

    orig = len(text.encode())
    extracted = len(result.encode())
    print(f"Extracted §{', §'.join(str(n) for n in sorted(nums))}: {extracted:,} bytes ({100 - extracted*100//orig}% smaller)", file=sys.stderr)

    sys.stdout.write(result)


if __name__ == "__main__":
    main()
