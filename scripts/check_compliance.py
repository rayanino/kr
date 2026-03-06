#!/usr/bin/env python3
"""Check implementation compliance against SPEC behavioral rules.

Scans engine source code for SPEC section comments and markers,
verifies test coverage, and identifies unimplemented rules.

Usage:
    python3 scripts/check_compliance.py engines/source
    python3 scripts/check_compliance.py --all
"""

import re
import sys
import argparse
from pathlib import Path


def count_spec_rules(spec_path: Path) -> dict:
    """Count behavioral rules in each §4 subsection."""
    if not spec_path.exists():
        return {}

    text = spec_path.read_text(encoding='utf-8')
    rules = {}

    # Find §4 subsections
    in_section_4 = False
    current_subsection = None
    rule_count = 0

    for line in text.split('\n'):
        if re.match(r'^##\s+4\.\s', line):
            in_section_4 = True
            continue
        if re.match(r'^##\s+[5-9]\.\s', line) or re.match(r'^##\s+1[0-9]\.\s', line):
            if current_subsection:
                rules[current_subsection] = rule_count
            in_section_4 = False
            continue

        if in_section_4:
            subsection_match = re.match(r'^###\s+(§[\d.A-Z]+)', line)
            if subsection_match:
                if current_subsection:
                    rules[current_subsection] = rule_count
                current_subsection = subsection_match.group(1)
                rule_count = 0
            elif current_subsection:
                # Count sentences with binding language
                sentences = re.split(r'(?<=[.])\s+', line)
                for s in sentences:
                    if re.search(r'\b(must|shall|always|never|rejects?|validates?|produces?|writes?|creates?|triggers?)\b', s):
                        rule_count += 1

    if current_subsection:
        rules[current_subsection] = rule_count

    return rules


def scan_source_code(src_dir: Path) -> dict:
    """Scan source code for SPEC reference comments."""
    results = {
        'spec_references': [],  # Comments referencing SPEC sections
        'ambiguity_markers': [],  # SPEC-AMBIGUITY comments
        'todos': [],  # TODO/FIXME comments
        'total_lines': 0,
        'files': 0,
    }

    if not src_dir.exists():
        return results

    for py_file in src_dir.rglob('*.py'):
        results['files'] += 1
        for i, line in enumerate(py_file.read_text(encoding='utf-8').split('\n'), 1):
            results['total_lines'] += 1

            # SPEC section references
            spec_ref = re.search(r'#.*§([\d.A-Z]+)', line)
            if spec_ref:
                results['spec_references'].append({
                    'file': str(py_file),
                    'line': i,
                    'section': spec_ref.group(1),
                })

            # Ambiguity markers
            if 'SPEC-AMBIGUITY' in line:
                results['ambiguity_markers'].append({
                    'file': str(py_file),
                    'line': i,
                    'text': line.strip(),
                })

            # TODOs without SPEC reference
            todo_match = re.search(r'#\s*(TODO|FIXME)(.*)$', line)
            if todo_match:
                has_spec_ref = '§' in line
                results['todos'].append({
                    'file': str(py_file),
                    'line': i,
                    'text': line.strip(),
                    'has_spec_ref': has_spec_ref,
                })

    return results


def scan_tests(tests_dir: Path) -> dict:
    """Scan test files for coverage indicators."""
    results = {
        'test_files': 0,
        'test_functions': 0,
        'spec_section_coverage': set(),  # Which §4 subsections have tests
    }

    if not tests_dir.exists():
        return results

    for py_file in tests_dir.rglob('test_*.py'):
        results['test_files'] += 1
        text = py_file.read_text(encoding='utf-8')

        # Count test functions
        results['test_functions'] += len(re.findall(r'^def test_', text, re.MULTILINE))

        # Find SPEC section references in test names or comments
        for match in re.finditer(r'(?:test_|§)([\d]+[a-z]?\d*)', text):
            results['spec_section_coverage'].add(match.group(1))

    return results


def check_not_yet_implemented(spec_path: Path) -> list:
    """Find [NOT YET IMPLEMENTED] markers in SPEC."""
    if not spec_path.exists():
        return []

    text = spec_path.read_text(encoding='utf-8')
    markers = []
    for i, line in enumerate(text.split('\n'), 1):
        if '[NOT YET IMPLEMENTED]' in line:
            markers.append({'line': i, 'text': line.strip()})

    return markers


def analyze_component(component_path: Path, verbose: bool = False):
    """Full compliance analysis for one component."""
    name = component_path.name
    spec_path = component_path / 'SPEC.md'
    src_dir = component_path / 'src'
    tests_dir = component_path / 'tests'

    print(f"\n{'='*60}")
    print(f"  Compliance Check: {name}")
    print(f"{'='*60}")

    # SPEC rules
    rules = count_spec_rules(spec_path)
    total_rules = sum(rules.values())
    print(f"\n  SPEC §4 behavioral rules: {total_rules}")
    if verbose and rules:
        for section, count in sorted(rules.items()):
            print(f"    {section}: {count} rules")

    # Source code scan
    code = scan_source_code(src_dir)
    print(f"\n  Source code: {code['files']} files, {code['total_lines']} lines")
    print(f"  SPEC references in code: {len(code['spec_references'])}")
    print(f"  SPEC-AMBIGUITY markers: {len(code['ambiguity_markers'])}")
    print(f"  TODOs: {len(code['todos'])} ({sum(1 for t in code['todos'] if not t['has_spec_ref'])} without SPEC ref)")

    if code['ambiguity_markers']:
        print(f"\n  ⚠ SPEC Ambiguities Found:")
        for m in code['ambiguity_markers']:
            print(f"    {m['file']}:{m['line']}: {m['text']}")

    orphan_todos = [t for t in code['todos'] if not t['has_spec_ref']]
    if orphan_todos:
        print(f"\n  ⚠ TODOs Without SPEC Reference:")
        for t in orphan_todos[:5]:
            print(f"    {t['file']}:{t['line']}: {t['text']}")
        if len(orphan_todos) > 5:
            print(f"    ... and {len(orphan_todos) - 5} more")

    # Test coverage
    tests = scan_tests(tests_dir)
    print(f"\n  Tests: {tests['test_files']} files, {tests['test_functions']} functions")

    # Not yet implemented
    nyi = check_not_yet_implemented(spec_path)
    if nyi:
        print(f"\n  [NOT YET IMPLEMENTED]: {len(nyi)} items")
        if verbose:
            for m in nyi:
                print(f"    SPEC line {m['line']}: {m['text'][:100]}")

    # No code at all
    if code['files'] == 0 and total_rules > 0:
        print(f"\n  ⚠ NO IMPLEMENTATION EXISTS — {total_rules} SPEC rules with 0 code files")

    return {
        'name': name,
        'spec_rules': total_rules,
        'code_files': code['files'],
        'code_lines': code['total_lines'],
        'test_functions': tests['test_functions'],
        'ambiguities': len(code['ambiguity_markers']),
        'nyi': len(nyi),
    }


def main():
    parser = argparse.ArgumentParser(description='Check SPEC compliance of implementation')
    parser.add_argument('component', nargs='?', help='Path to engine/component directory')
    parser.add_argument('--all', action='store_true', help='Check all components')
    parser.add_argument('--verbose', '-v', action='store_true', help='Detailed output')
    args = parser.parse_args()

    if args.all:
        summaries = []
        for engine_dir in sorted(Path('engines').iterdir()):
            if (engine_dir / 'SPEC.md').exists():
                summaries.append(analyze_component(engine_dir, args.verbose))
        for shared_dir in sorted(Path('shared').iterdir()):
            if (shared_dir / 'SPEC.md').exists():
                summaries.append(analyze_component(shared_dir, args.verbose))
        if (Path('interface/scholar/SPEC.md')).exists():
            summaries.append(analyze_component(Path('interface/scholar'), args.verbose))

        # Summary table
        print(f"\n{'='*60}")
        print(f"  SUMMARY")
        print(f"{'='*60}")
        print(f"  {'Component':<20} {'Rules':>6} {'Code':>6} {'Tests':>6} {'NYI':>4}")
        print(f"  {'-'*20} {'-'*6} {'-'*6} {'-'*6} {'-'*4}")
        for s in summaries:
            print(f"  {s['name']:<20} {s['spec_rules']:>6} {s['code_lines']:>6} {s['test_functions']:>6} {s['nyi']:>4}")

    elif args.component:
        component_path = Path(args.component)
        if not component_path.exists():
            print(f"Error: {component_path} not found", file=sys.stderr)
            sys.exit(1)
        analyze_component(component_path, args.verbose)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
