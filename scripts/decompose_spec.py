#!/usr/bin/env python3
"""Extract implementable tasks from a SPEC.md file.

Parses §4 (Processing Specification) rules and produces a task list
that Claude Code can use to plan implementation sessions.

Usage:
    python3 scripts/decompose_spec.py engines/source/SPEC.md
    python3 scripts/decompose_spec.py engines/source/SPEC.md --section 4.A
"""

import re
import sys
import argparse
from pathlib import Path


def parse_spec_sections(text: str) -> dict:
    """Parse SPEC into a section hierarchy."""
    sections = {}
    current_section = None
    current_content = []

    for line in text.split('\n'):
        # Match section headers: ## N. Title or ### §N.A.N — Title
        header_match = re.match(
            r'^(#{2,4})\s+(?:§?(\d+(?:\.\w+(?:\.\d+)?)?)[\s.—-]+)?(.+)', line
        )
        if header_match:
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            level = len(header_match.group(1))
            number = header_match.group(2) or ''
            title = header_match.group(3).strip()
            current_section = f"§{number} {title}" if number else title
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        sections[current_section] = '\n'.join(current_content)

    return sections


def extract_rules(section_text: str) -> list:
    """Extract binding rules from a section's text.
    
    A binding rule is a sentence that describes a specific behavior:
    - Contains action verbs (validates, rejects, produces, writes, computes)
    - Contains error codes (SRC_*, NORM_*, etc.)
    - Contains specific values (thresholds, field names, formats)
    """
    rules = []
    sentences = re.split(r'(?<=[.!])\s+', section_text)

    action_patterns = [
        r'\b(validates?|rejects?|produces?|writes?|computes?|creates?|assigns?)\b',
        r'\b(returns?|triggers?|detects?|extracts?|generates?|classif(?:y|ies))\b',
        r'\b(must|shall|always|never|requires?)\b',
        r'[A-Z]{2,}_[A-Z_]+',  # Error codes like SRC_EMPTY_INPUT
        r'`[^`]+`',  # Inline code references
    ]

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 20:
            continue
        if any(re.search(p, sentence) for p in action_patterns):
            rules.append(sentence)

    return rules


def extract_implementation_status(section_text: str) -> list:
    """Extract [NOT YET IMPLEMENTED] markers."""
    markers = []
    for line in section_text.split('\n'):
        if '[NOT YET IMPLEMENTED]' in line:
            markers.append(line.strip())
    return markers


def format_task_list(spec_path: str, sections: dict, filter_section: str = None):
    """Format extracted rules as an implementation task list."""
    engine_name = Path(spec_path).parent.name
    print(f"# Implementation Tasks — {engine_name}")
    print(f"# Extracted from: {spec_path}")
    print()

    task_num = 0
    for section_key, content in sections.items():
        if filter_section and not section_key.startswith(f"§{filter_section}"):
            continue

        rules = extract_rules(content)
        not_implemented = extract_implementation_status(content)

        if not rules and not not_implemented:
            continue

        print(f"## {section_key}")
        print()

        if rules:
            print(f"### Behavioral Rules ({len(rules)} rules)")
            for rule in rules:
                task_num += 1
                # Truncate long rules for readability
                display = rule[:200] + '...' if len(rule) > 200 else rule
                print(f"  {task_num}. [ ] {display}")
            print()

        if not_implemented:
            print(f"### Not Yet Implemented ({len(not_implemented)} items)")
            for marker in not_implemented:
                task_num += 1
                print(f"  {task_num}. [!] {marker}")
            print()

    print(f"\n# Total tasks: {task_num}")


def main():
    parser = argparse.ArgumentParser(description='Extract implementation tasks from SPEC.md')
    parser.add_argument('spec_path', help='Path to SPEC.md file')
    parser.add_argument('--section', '-s', help='Filter to specific section (e.g., "4.A")')
    args = parser.parse_args()

    spec_path = Path(args.spec_path)
    if not spec_path.exists():
        print(f"Error: {spec_path} not found", file=sys.stderr)
        sys.exit(1)

    text = spec_path.read_text(encoding='utf-8')
    sections = parse_spec_sections(text)
    format_task_list(str(spec_path), sections, args.section)


if __name__ == '__main__':
    main()
