#!/usr/bin/env python3
"""Session quality gate — run before every commit.

This script objectively verifies that a session produced real work,
not just cosmetic changes. It catches the failure modes that
Claude Chat self-review misses.

Usage:
    python3 scripts/session_quality_gate.py [--spec engines/source/SPEC.md]
"""

import re
import sys
import subprocess
from pathlib import Path


def get_staged_diff():
    """Get the git diff of staged changes."""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--stat'],
        capture_output=True, text=True
    )
    return result.stdout


def get_staged_diff_full():
    """Get full diff content."""
    result = subprocess.run(
        ['git', 'diff', '--cached'],
        capture_output=True, text=True
    )
    return result.stdout


def check_substance(diff_text: str) -> list:
    """Check that changes have substance, not just cosmetic edits."""
    issues = []
    
    additions = [l for l in diff_text.split('\n') if l.startswith('+') and not l.startswith('+++')]
    deletions = [l for l in diff_text.split('\n') if l.startswith('-') and not l.startswith('---')]
    
    if not additions and not deletions:
        issues.append("NO_CHANGES: No staged changes found. Did you forget to `git add`?")
        return issues
    
    # Check for cosmetic-only changes (whitespace, formatting)
    substantive_additions = [l for l in additions if l.strip('+').strip() and 
                           not re.match(r'^\+\s*$', l)]
    if len(substantive_additions) < 5:
        issues.append(f"THIN_CHANGES: Only {len(substantive_additions)} substantive lines added. "
                      "Is this a cosmetic-only session?")
    
    return issues


def check_next_md() -> list:
    """Verify NEXT.md was updated."""
    issues = []
    diff = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True, text=True
    ).stdout
    
    if 'NEXT.md' not in diff:
        issues.append("NEXT_MD_MISSING: NEXT.md was not updated. Every session must write handoff instructions.")
    
    return issues


def check_session_log() -> list:
    """Verify SESSION_LOG.md was updated."""
    issues = []
    diff = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True, text=True
    ).stdout
    
    if 'SESSION_LOG.md' not in diff:
        issues.append("SESSION_LOG_MISSING: SESSION_LOG.md was not updated. "
                      "Add an entry documenting what this session did.")
    
    return issues


def check_creative_output(diff_text: str) -> list:
    """Check for evidence of creative/inventive work, not just review."""
    issues = []
    
    # Look for §4.B additions (transformative capabilities)
    has_4b_work = bool(re.search(r'§4\.B|4\.B\.|transformative|capability|novel|invent', diff_text, re.IGNORECASE))
    
    # Look for new features, not just corrections
    has_new_content = bool(re.search(r'\+.*(?:new|add|creat|design|propos|discover)', diff_text, re.IGNORECASE))
    
    if not has_4b_work and not has_new_content:
        issues.append("NO_CREATIVE_SIGNAL: No evidence of creative/inventive work in changes. "
                     "Was this a secretary session? Check CREATIVE_MANDATE.md.")
    
    return issues


def check_spec_quality_improvement(spec_path: str = None) -> list:
    """If a SPEC was modified, check that quality improved."""
    issues = []
    
    if not spec_path:
        return issues
    
    spec = Path(spec_path)
    if not spec.exists():
        return issues
    
    # Run the quality checker
    result = subprocess.run(
        ['python3', 'scripts/check_spec_quality.py', str(spec), '--severity', 'high'],
        capture_output=True, text=True
    )
    
    # Extract defect count from output
    match = re.search(r'Defects:\s*(\d+)\s*\(high:\s*(\d+)', result.stdout)
    if match:
        total = int(match.group(1))
        high = int(match.group(2))
        if high > 15:
            issues.append(f"SPEC_QUALITY_LOW: {spec.parent.name} SPEC still has {high} high-severity defects. "
                         "Refinement target: ≤10 high-severity.")
    
    return issues


def check_knowledge_corruption_risk(diff_text: str) -> list:
    """Flag changes that could silently corrupt knowledge."""
    issues = []
    
    # Changes to processing logic without test changes
    has_processing_change = bool(re.search(r'\+.*(?:def |class |process|extract|classify|detect|compute)', diff_text))
    has_test_change = bool(re.search(r'test.*\.py', diff_text))
    
    if has_processing_change and not has_test_change:
        issues.append("UNTESTED_PROCESSING: Processing logic changed without corresponding test changes. "
                     "Knowledge corruption risk — untested processing can silently produce wrong output.")
    
    # Changes to validation thresholds
    threshold_changes = re.findall(r'\+.*(?:threshold|confidence|score)\s*[=<>≥≤]+\s*[\d.]+', diff_text)
    if threshold_changes:
        issues.append(f"THRESHOLD_CHANGE: {len(threshold_changes)} validation threshold(s) changed. "
                     "Verify these don't weaken knowledge protection. "
                     "Changes: " + "; ".join(t.strip('+').strip()[:60] for t in threshold_changes[:3]))
    
    return issues


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Pre-commit session quality gate')
    parser.add_argument('--spec', help='Path to SPEC.md being refined (for quality check)')
    args = parser.parse_args()
    
    print("=" * 60)
    print("  SESSION QUALITY GATE")
    print("=" * 60)
    
    diff_stat = get_staged_diff()
    diff_full = get_staged_diff_full()
    
    all_issues = []
    
    # Run all checks
    checks = [
        ("Substance", check_substance(diff_full)),
        ("NEXT.md handoff", check_next_md()),
        ("Session log", check_session_log()),
        ("Creative output", check_creative_output(diff_full)),
        ("Knowledge safety", check_knowledge_corruption_risk(diff_full)),
    ]
    
    if args.spec:
        checks.append(("SPEC quality", check_spec_quality_improvement(args.spec)))
    
    passed = 0
    failed = 0
    warnings = 0
    
    for name, issues in checks:
        if issues:
            failed += 1
            print(f"\n  ✗ {name}:")
            for issue in issues:
                print(f"    → {issue}")
                all_issues.append(issue)
        else:
            passed += 1
            print(f"  ✓ {name}")
    
    print(f"\n{'=' * 60}")
    print(f"  Result: {passed} passed, {failed} failed")
    
    if failed > 0:
        print(f"\n  ⚠ Address the issues above before committing.")
        print(f"  These checks prevent sessions that look productive but aren't.")
        print(f"  If a check is a false positive, proceed — but be honest about why.")
    else:
        print(f"\n  ✓ All checks passed. Ready to commit.")
    
    print("=" * 60)
    
    return 0  # Always return 0 — these are warnings, not blockers


if __name__ == '__main__':
    sys.exit(main())
