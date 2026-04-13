#!/usr/bin/env python3
"""Check SPEC quality for machine-readability and silent failure patterns.

This script detects the defects that Claude Chat tends to miss during self-review:
vague language, missing examples, hand-waving technology references, unbounded
lists, missing error paths, and untestable rules.

Maps directly to reference/SILENT_FAILURES.md patterns and DEEP_REASONING_PROTOCOL.md
Perfection Standard criteria.

Usage:
    python3 scripts/check_spec_quality.py engines/source/SPEC.md
    python3 scripts/check_spec_quality.py --all
    python3 scripts/check_spec_quality.py --all --severity high
"""

import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict


# === Defect Patterns ===

VAGUE_QUANTIFIERS = [
    (r'\b(multiple|several|various|numerous|many|few|some)\b(?!\s*\()',
     "VAGUE_QUANTIFIER", "high",
     "Unbounded quantifier — how many exactly? An implementer must guess."),
    (r'\bappropriate(ly)?\b',
     "VAGUE_APPROPRIATE", "high",
     "Who decides what's 'appropriate'? Replace with specific criteria."),
    (r'\bsufficient(ly)?\b',
     "VAGUE_SUFFICIENT", "high",
     "What threshold makes something 'sufficient'? Give a number or condition."),
    (r'\brelevant\b(?!.*\brelevance\s*(score|threshold|≥|>=|>|<|≤|<=|\d))',
     "VAGUE_RELEVANT", "medium",
     "What makes something 'relevant'? Define the relevance criteria."),
    (r'\bsignificant(ly)?\b',
     "VAGUE_SIGNIFICANT", "medium",
     "How much is 'significant'? Give a threshold."),
    (r'\breasonabl[ey]\b',
     "VAGUE_REASONABLE", "high",
     "'Reasonable' is subjective. Replace with measurable criteria."),
    (r'\bgenerally\b',
     "VAGUE_GENERALLY", "medium",
     "'Generally' implies exceptions — what are they? Be explicit."),
    (r'\b(if needed|as needed|when necessary|as appropriate)\b',
     "VAGUE_CONDITIONAL", "high",
     "Who decides when it's 'needed'? Specify the trigger condition."),
]

UNBOUNDED_LISTS = [
    (r'\betc\.?\b',
     "UNBOUNDED_ETC", "high",
     "'etc.' means the list is incomplete. An implementer doesn't know what else to include."),
    (r'\band so on\b',
     "UNBOUNDED_AND_SO_ON", "high",
     "'and so on' leaves the list open. Enumerate all items."),
    (r'\bsuch as\b(?!.*\bspecifically\b)',
     "UNBOUNDED_SUCH_AS", "low",
     "'such as' may indicate an open list. Verify the list is exhaustive or mark as extensible."),
    (r'\bincluding but not limited to\b',
     "UNBOUNDED_INCLUSIVE", "medium",
     "An implementer cannot implement an unbounded set. List all items or define the boundary."),
]

HANDWAVE_TECHNOLOGY = [
    (r'\busing (the |an? )?(LLM|AI|ML|model|algorithm)\b(?!.*\b(Claude|GPT|LiteLLM|Instructor|consensus)\b)',
     "HANDWAVE_LLM", "high",
     "Which LLM? Through what interface? With what prompt? Name the specific tool."),
    (r'\b(through|via|using) (content |text )?(analysis|processing|evaluation)\b'
     r'(?!.*\b(CAMeL|Farasa|spaCy|regex|heuristic|rule|pattern)\b)',
     "HANDWAVE_ANALYSIS", "high",
     "'Analysis' is not a technique. Name the specific method, library, or algorithm."),
    (r'\b(NLP|natural language processing)\b(?!.*\b(CAMeL|Farasa|spaCy|NLTK|stanza|token|morpho|POS)\b)',
     "HANDWAVE_NLP", "medium",
     "Which NLP tool? What specific capability? Name the library and function."),
    (r'\bmachine learning\b(?!.*\b(classifier|model|train|fine-tune|embed|vector)\b)',
     "HANDWAVE_ML", "medium",
     "'Machine learning' is not specific. What model? What training? What inference?"),
]

MISSING_SPECIFICS = [
    (r'\b(high|medium|low)\s+(confidence|quality|priority|score)\b(?!.*\b(\d+\.?\d*|≥|>=|threshold)\b)',
     "MISSING_THRESHOLD", "high",
     "What number is 'high'? Define the threshold explicitly."),
    (r'\bperiodic(ally)?\b(?!.*\b(every|hour|day|minute|weekly|daily|cron|\d+)\b)',
     "MISSING_FREQUENCY", "medium",
     "'Periodically' — how often? Specify the interval."),
    (r'\b(large|small|big|tiny)\b(?!\s*(enough|$))',
     "MISSING_SIZE", "low",
     "How large/small? Give a number or range."),
]

CIRCULAR_PATTERNS = [
    (r'\b(\w{4,})\s+(?:is|are)\s+(?:the\s+)?\1\b',
     "CIRCULAR_DEFINITION", "high",
     "Potential circular definition — X is defined as X."),
]


def extract_sections(text: str) -> dict:
    """Extract SPEC sections by number."""
    sections = {}
    current = None
    current_lines = []

    for i, line in enumerate(text.split('\n'), 1):
        m = re.match(r'^##\s+(\d+)\.\s+(.*)', line)
        if m:
            if current:
                sections[current] = '\n'.join(current_lines)
            current = f"§{m.group(1)}"
            current_lines = []
        elif current:
            current_lines.append(line)

    if current:
        sections[current] = '\n'.join(current_lines)

    return sections


def extract_subsections(text: str) -> dict:
    """Extract §4.A and §4.B subsections."""
    subsections = {}
    current = None
    current_lines = []

    for line in text.split('\n'):
        m = re.match(r'^###\s+(§[\d.]+[A-Z]?[\d.]*)\b', line)
        if not m:
            m = re.match(r'^####\s+(§[\d.]+[A-Z]?[\d.]*)\b', line)
        if m:
            if current:
                subsections[current] = '\n'.join(current_lines)
            current = m.group(1)
            current_lines = []
        elif current:
            current_lines.append(line)

    if current:
        subsections[current] = '\n'.join(current_lines)

    return subsections


def check_pattern_defects(text: str, filename: str) -> list:
    """Run all regex patterns against text, return defects."""
    defects = []
    all_patterns = (VAGUE_QUANTIFIERS + UNBOUNDED_LISTS +
                    HANDWAVE_TECHNOLOGY + MISSING_SPECIFICS + CIRCULAR_PATTERNS)

    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        # Skip code blocks
        if line.strip().startswith('```') or line.strip().startswith('|'):
            continue
        # Skip examples (they quote external text)
        if line.strip().startswith('>'):
            continue
        # Skip [NOT YET IMPLEMENTED] lines (known gaps)
        if '[NOT YET IMPLEMENTED]' in line:
            continue

        for pattern, code, severity, message in all_patterns:
            matches = list(re.finditer(pattern, line, re.IGNORECASE))
            for match in matches:
                defects.append({
                    'file': filename,
                    'line': i,
                    'code': code,
                    'severity': severity,
                    'match': match.group(0),
                    'context': line.strip()[:120],
                    'message': message,
                })

    return defects


def check_missing_examples(text: str, filename: str) -> list:
    """Check that §4 subsections have concrete examples."""
    defects = []
    subsections = extract_subsections(text)

    for name, content in subsections.items():
        if not name.startswith('§4.'):
            continue
        # Check for example blocks
        has_example = bool(re.search(
            r'\*\*Example[:\*]|```(?:json|python|yaml)|Input:|Output:|→.*→',
            content, re.IGNORECASE
        ))
        if not has_example and len(content.strip()) > 200:
            defects.append({
                'file': filename,
                'line': 0,
                'code': 'MISSING_EXAMPLE',
                'severity': 'high',
                'match': name,
                'context': f'{name} has no concrete input/output example',
                'message': 'Every §4 subsection needs at least one worked example '
                          'showing input → processing → output with real Arabic text.',
            })

    return defects


def check_error_coverage(text: str, filename: str) -> list:
    """Check that §4 processing rules have corresponding §7 error codes."""
    defects = []
    sections = extract_sections(text)

    section_4 = sections.get('§4', '')
    section_7 = sections.get('§7', '')

    if not section_4 or not section_7:
        return defects

    # Find error codes referenced in §4
    s4_errors = set(re.findall(r'error\s+`?([A-Z_]+_[A-Z_]+)`?', section_4))
    # Find error codes defined in §7
    s7_errors = set(re.findall(r'`?([A-Z_]+_[A-Z_]+)`?', section_7))

    # Errors referenced in §4 but not defined in §7
    undefined = s4_errors - s7_errors
    for err in undefined:
        defects.append({
            'file': filename,
            'line': 0,
            'code': 'UNDEFINED_ERROR',
            'severity': 'medium',
            'match': err,
            'context': f'Error code {err} referenced in §4 but not defined in §7',
            'message': 'Every error code used in processing rules must be '
                      'defined in §7 with severity and recovery action.',
        })

    return defects


def check_implementation_state(text: str, filename: str) -> list:
    """Check §9 for accuracy markers."""
    defects = []
    sections = extract_sections(text)
    section_9 = sections.get('§9', '')

    if not section_9:
        defects.append({
            'file': filename,
            'line': 0,
            'code': 'MISSING_SECTION_9',
            'severity': 'high',
            'match': '§9',
            'context': 'No §9 (Current Implementation State) section found',
            'message': '§9 is required. It tells Claude Code what exists vs. what to build.',
        })
        return defects

    nyi_count = section_9.count('[NOT YET IMPLEMENTED]')
    if nyi_count == 0 and 'no code exists' not in section_9.lower():
        defects.append({
            'file': filename,
            'line': 0,
            'code': 'SUSPICIOUS_S9',
            'severity': 'medium',
            'match': '§9',
            'context': '§9 has no [NOT YET IMPLEMENTED] markers and doesn\'t say "no code exists"',
            'message': 'Most engines have no code yet. §9 should accurately reflect this.',
        })

    return defects


def check_corruption_paths(text: str, filename: str) -> list:
    """Check for silent corruption risks — the MOST IMPORTANT check."""
    defects = []

    # Pattern: data modification without validation
    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        # Writes/stores/saves without mentioning validation
        if re.search(r'\b(writes?|stores?|saves?|records?|updates?)\b.*\b(to|in|into)\b.*\b(disk|file|library|registry)', line, re.IGNORECASE):
            # Check next 5 lines for validation mention
            context = '\n'.join(lines[i:i+5]) if i < len(lines) else ''
            if not re.search(r'\b(validat|verif|check|assert|ensure|confirm|§5)\b', context, re.IGNORECASE):
                defects.append({
                    'file': filename,
                    'line': i,
                    'code': 'UNVALIDATED_WRITE',
                    'severity': 'high',
                    'match': line.strip()[:80],
                    'context': 'Data written to library without nearby validation mention',
                    'message': 'Every write to the library is a potential corruption point. '
                              'Specify what validation occurs before the write.',
                })

    return defects


def analyze_spec(spec_path: Path, severity_filter: str = None) -> dict:
    """Full quality analysis for one SPEC."""
    text = spec_path.read_text(encoding='utf-8')
    filename = str(spec_path)

    all_defects = []
    all_defects.extend(check_pattern_defects(text, filename))
    all_defects.extend(check_missing_examples(text, filename))
    all_defects.extend(check_error_coverage(text, filename))
    all_defects.extend(check_implementation_state(text, filename))
    all_defects.extend(check_corruption_paths(text, filename))

    if severity_filter:
        all_defects = [d for d in all_defects if d['severity'] == severity_filter]

    # Count by severity
    counts = defaultdict(int)
    for d in all_defects:
        counts[d['severity']] += 1

    # Count by category
    categories = defaultdict(int)
    for d in all_defects:
        cat = d['code'].split('_')[0]
        categories[cat] += 1

    return {
        'path': filename,
        'name': spec_path.parent.name,
        'total_defects': len(all_defects),
        'high': counts['high'],
        'medium': counts['medium'],
        'low': counts['low'],
        'categories': dict(categories),
        'defects': all_defects,
        'lines': len(text.split('\n')),
        'nyi_count': text.count('[NOT YET IMPLEMENTED]'),
    }


def print_report(result: dict, verbose: bool = False):
    """Print analysis report."""
    print(f"\n{'='*70}")
    print(f"  SPEC Quality: {result['name']} ({result['lines']}L)")
    print(f"{'='*70}")
    print(f"  Defects: {result['total_defects']} "
          f"(high: {result['high']}, medium: {result['medium']}, low: {result['low']})")
    print(f"  [NOT YET IMPLEMENTED]: {result['nyi_count']}")

    if result['categories']:
        print(f"\n  By category:")
        for cat, count in sorted(result['categories'].items(), key=lambda x: -x[1]):
            print(f"    {cat}: {count}")

    if verbose or result['high'] > 0:
        high_defects = [d for d in result['defects'] if d['severity'] == 'high']
        if high_defects:
            print(f"\n  HIGH severity defects:")
            for d in high_defects[:20]:
                print(f"    L{d['line']:>4} [{d['code']}] {d['match']}")
                print(f"         → {d['message']}")
                if verbose:
                    print(f"         Context: {d['context']}")
            if len(high_defects) > 20:
                print(f"    ... and {len(high_defects) - 20} more")

    if verbose:
        med_defects = [d for d in result['defects'] if d['severity'] == 'medium']
        if med_defects:
            print(f"\n  MEDIUM severity defects:")
            for d in med_defects[:15]:
                print(f"    L{d['line']:>4} [{d['code']}] {d['match']}")
                print(f"         → {d['message']}")


def main():
    parser = argparse.ArgumentParser(description='Check SPEC quality for machine-readability')
    parser.add_argument('spec', nargs='?', help='Path to SPEC.md file')
    parser.add_argument('--all', action='store_true', help='Check all SPECs')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all defects')
    parser.add_argument('--severity', '-s', choices=['high', 'medium', 'low'],
                       help='Filter by severity')
    args = parser.parse_args()

    if args.all:
        specs = []
        for d in sorted(Path('engines').iterdir()):
            s = d / 'SPEC.md'
            if s.exists():
                specs.append(s)
        for d in sorted(Path('shared').iterdir()):
            s = d / 'SPEC.md'
            if s.exists():
                specs.append(s)
        s = Path('interface/scholar/SPEC.md')
        if s.exists():
            specs.append(s)

        results = [analyze_spec(s, args.severity) for s in specs]
        for r in results:
            print_report(r, args.verbose)

        # Summary
        print(f"\n{'='*70}")
        print(f"  SUMMARY")
        print(f"{'='*70}")
        print(f"  {'SPEC':<20} {'Lines':>6} {'Total':>6} {'High':>5} {'Med':>5} {'Low':>5}")
        print(f"  {'-'*20} {'-'*6} {'-'*6} {'-'*5} {'-'*5} {'-'*5}")
        total = {'total': 0, 'high': 0, 'medium': 0, 'low': 0}
        for r in results:
            print(f"  {r['name']:<20} {r['lines']:>6} {r['total_defects']:>6} "
                  f"{r['high']:>5} {r['medium']:>5} {r['low']:>5}")
            total['total'] += r['total_defects']
            total['high'] += r['high']
            total['medium'] += r['medium']
            total['low'] += r['low']
        print(f"  {'TOTAL':<20} {'':>6} {total['total']:>6} "
              f"{total['high']:>5} {total['medium']:>5} {total['low']:>5}")

    elif args.spec:
        spec_path = Path(args.spec)
        if not spec_path.exists():
            print(f"Error: {spec_path} not found", file=sys.stderr)
            sys.exit(1)
        result = analyze_spec(spec_path, args.severity)
        print_report(result, args.verbose)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
