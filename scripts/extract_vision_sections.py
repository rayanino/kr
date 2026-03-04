#!/usr/bin/env python3
"""Extract specific sections from VISION.md for use as Claude Chat attachments.

Usage:
    python scripts/extract_vision_sections.py 7.1 7.4 2
    → Extracts §7.1 through §7.4 AND §2 (the glossary) into a single file.

    python scripts/extract_vision_sections.py 5
    → Extracts §5 in its entirety.

    python scripts/extract_vision_sections.py 7.5 7.6 2
    → Extracts §7.5, §7.6, and §2.

Output: prints to stdout. Redirect to file:
    python scripts/extract_vision_sections.py 7.1 7.4 2 > vision_sections_w001.md
"""
import sys
import re
import os

def find_vision_md():
    """Find VISION.md relative to this script or current directory."""
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'VISION.md'),
        'VISION.md',
        os.path.join('..', 'VISION.md'),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    print("ERROR: Cannot find VISION.md", file=sys.stderr)
    sys.exit(1)

def parse_sections(content):
    """Parse VISION.md into sections by heading.
    
    Two-level parsing:
    - Major sections keyed by number (e.g., '2', '7')
    - Subsections keyed by number.number (e.g., '2.1', '7.3')
    
    Requesting a major section returns ALL its subsections.
    Requesting a subsection returns just that subsection.
    """
    lines = content.split('\n')
    
    # First pass: identify major section boundaries
    major_sections = {}  # key -> full content including all subsections
    subsections = {}     # key -> individual subsection content
    
    current_major = None
    current_major_lines = []
    current_sub = None
    current_sub_lines = []
    
    for line in lines:
        m_major = re.match(r'^## §(\d+)', line)
        m_sub = re.match(r'^### (\d+\.\d+)', line)
        m_doc = re.match(r'^## (Document Purpose|Changelog)', line)
        m_next_major = m_major or m_doc
        
        if m_next_major:
            # Close previous subsection
            if current_sub is not None:
                subsections[current_sub] = '\n'.join(current_sub_lines)
                current_sub = None
                current_sub_lines = []
            # Close previous major section
            if current_major is not None:
                major_sections[current_major] = '\n'.join(current_major_lines)
            
            if m_major:
                current_major = m_major.group(1)
            elif m_doc:
                current_major = m_doc.group(1)
            current_major_lines = [line]
            
        elif m_sub:
            # Close previous subsection
            if current_sub is not None:
                subsections[current_sub] = '\n'.join(current_sub_lines)
            current_sub = m_sub.group(1)
            current_sub_lines = [line]
            current_major_lines.append(line)
            
        else:
            if current_sub is not None:
                current_sub_lines.append(line)
            current_major_lines.append(line)
    
    # Close final sections
    if current_sub is not None:
        subsections[current_sub] = '\n'.join(current_sub_lines)
    if current_major is not None:
        major_sections[current_major] = '\n'.join(current_major_lines)
    
    # Merge: subsections take precedence for dotted keys, major for integer keys
    merged = {}
    merged.update(major_sections)   # '2' -> full §2 with all subsections
    merged.update(subsections)      # '2.1' -> just §2.1
    return merged

def resolve_range(args):
    """Resolve arguments into a list of section keys.
    
    '7.1 7.4 2' → ['7.1', '7.2', '7.3', '7.4', '2']
    '5' → ['5']
    '7.1 7.4' with subsections → range from 7.1 to 7.4
    """
    requested = []
    i = 0
    while i < len(args):
        arg = args[i]
        # Check if this is a range (e.g., 7.1 7.4 where both have dots)
        if '.' in arg and i + 1 < len(args) and '.' in args[i + 1]:
            start_major, start_minor = arg.split('.')
            end_major, end_minor = args[i + 1].split('.')
            if start_major == end_major:
                for m in range(int(start_minor), int(end_minor) + 1):
                    requested.append(f"{start_major}.{m}")
                i += 2
                continue
        requested.append(arg)
        i += 1
    return requested

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    vision_path = find_vision_md()
    with open(vision_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = parse_sections(content)
    requested = resolve_range(sys.argv[1:])
    
    # Header
    print(f"# VISION.md — Extracted Sections: {', '.join('§' + r for r in requested)}")
    print(f"# Extracted from: {vision_path}")
    print()
    
    found = 0
    for key in requested:
        if key in sections:
            print(sections[key])
            print()
            found += 1
        else:
            # Try matching major section (e.g., '5' matches '## §5')
            # Already handled by parse_sections using major number as key
            print(f"# WARNING: Section '{key}' not found in VISION.md", file=sys.stderr)
    
    if found == 0:
        print("ERROR: No requested sections found.", file=sys.stderr)
        print(f"Available sections: {sorted(sections.keys())}", file=sys.stderr)
        sys.exit(1)
    
    # Footer with token estimate
    output_chars = sum(len(sections.get(k, '')) for k in requested if k in sections)
    print(f"\n# --- Extracted {found} section(s), ~{output_chars} chars, ~{output_chars // 3} tokens ---")

if __name__ == '__main__':
    main()
