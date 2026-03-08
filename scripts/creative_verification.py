#!/usr/bin/env python3
"""Verify creative output was produced during a SPEC refinement session.

Checks for evidence of inventive work — not just review and correction.

NOTE: This script was designed for the old CREATIVE/PRECISION/HARDENING session model.
The current process uses ENGINE_PROTOCOL.md (4-step per engine). The §4.B substance
checks are still useful for SPEC quality assessment, but the "secretary session" warning
should be interpreted in the new context.

Usage:
    python3 scripts/creative_verification.py engines/source/SPEC.md
"""

import re
import sys
import subprocess
from pathlib import Path


def check_4b_substance(spec_path: Path) -> dict:
    """Analyze §4.B for substance vs hand-waving."""
    text = spec_path.read_text(encoding='utf-8')
    
    # Find §4.B section
    m = re.search(r'(###\s+§4\.B.*?\n)(.*?)(?=\n###\s+§4\.[C-Z]|\n##\s+[5-9]|\n##\s+1[0-9]|\Z)', text, re.DOTALL)
    if not m:
        # Try alternative format
        m = re.search(r'(##\s+.*4\.B.*?\n)(.*?)(?=\n##\s+[5-9]|\n##\s+1[0-9]|\Z)', text, re.DOTALL)
    if not m:
        return {'error': 'No §4.B section found', 'score': 0}
    
    section = m.group(2)
    
    # Count capabilities
    capabilities = re.findall(r'#{3,4}\s+§4\.B\.\d+', section)
    
    # Check for named technologies (not hand-waving)
    named_tech = re.findall(r'(?:using|via|through|with)\s+(?:[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)', section)
    
    # Check for concrete output examples
    has_examples = bool(re.search(r'\*\*Example|```|Output:|→.*→', section))
    
    # Check for NOT YET IMPLEMENTED markers (acceptable — means it's designed but not built)
    nyi = section.count('[NOT YET IMPLEMENTED]')
    
    # Check for vague capability descriptions
    vague_patterns = re.findall(r'(?:could potentially|might be able to|possibly|in the future)', section, re.I)
    
    # Score
    score = 0
    score += min(len(capabilities) * 20, 60)  # Up to 60 for 3+ capabilities
    score += 15 if has_examples else 0          # 15 for examples
    score += 15 if named_tech else 0            # 15 for named technologies
    score -= len(vague_patterns) * 10           # -10 for each vague phrase
    score = max(0, min(100, score))
    
    return {
        'capabilities': len(capabilities),
        'named_technologies': len(named_tech),
        'has_examples': has_examples,
        'vague_phrases': len(vague_patterns),
        'nyi_markers': nyi,
        'score': score,
    }


def check_invention_in_diff() -> dict:
    """Check git diff for evidence of new invention vs. just corrections."""
    result = subprocess.run(
        ['git', 'diff', '--cached', '-U0'],
        capture_output=True, text=True
    )
    diff = result.stdout
    
    # Count added lines that indicate invention
    additions = [l for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]
    
    invention_signals = 0
    correction_signals = 0
    
    for line in additions:
        # Invention: new capabilities, new features, new approaches
        if re.search(r'(?:§4\.B|capability|novel|discover|detect|predict|generate|infer|cross-reference|network|pattern)', line, re.I):
            invention_signals += 1
        # Correction: fixing existing content
        if re.search(r'(?:fix|correct|clarif|ambig|vague|missing|defect|error code)', line, re.I):
            correction_signals += 1
    
    total = invention_signals + correction_signals
    ratio = invention_signals / max(total, 1)
    
    return {
        'invention_signals': invention_signals,
        'correction_signals': correction_signals,
        'invention_ratio': ratio,
        'assessment': 'creative' if ratio > 0.3 else 'review-heavy' if ratio > 0.1 else 'secretary'
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/creative_verification.py <SPEC.md path>")
        sys.exit(1)
    
    spec_path = Path(sys.argv[1])
    if not spec_path.exists():
        print(f"Error: {spec_path} not found")
        sys.exit(1)
    
    print("=" * 60)
    print("  CREATIVE VERIFICATION")
    print("=" * 60)
    
    # Check §4.B substance
    b_result = check_4b_substance(spec_path)
    print(f"\n  §4.B Analysis ({spec_path.parent.name}):")
    if 'error' in b_result:
        print(f"    ✗ {b_result['error']}")
    else:
        print(f"    Capabilities: {b_result['capabilities']}")
        print(f"    Named technologies: {b_result['named_technologies']}")
        print(f"    Has examples: {b_result['has_examples']}")
        print(f"    Vague phrases: {b_result['vague_phrases']}")
        print(f"    Score: {b_result['score']}/100")
        
        if b_result['score'] < 40:
            print(f"    ⚠ LOW CREATIVE SCORE. This engine's §4.B is underdeveloped.")
            print(f"      Ask: What does this engine KNOW after processing that didn't exist before?")
            print(f"      Ask: What would make a scholar say 'I didn't know that was possible'?")
        elif b_result['score'] < 70:
            print(f"    → ADEQUATE but could be stronger. Add examples and name specific tools.")
        else:
            print(f"    ✓ Strong transformative capabilities section.")
    
    # Check diff for invention vs correction ratio
    diff_result = check_invention_in_diff()
    print(f"\n  Session Output Analysis:")
    print(f"    Invention signals: {diff_result['invention_signals']}")
    print(f"    Correction signals: {diff_result['correction_signals']}")
    print(f"    Invention ratio: {diff_result['invention_ratio']:.0%}")
    print(f"    Assessment: {diff_result['assessment'].upper()}")
    
    if diff_result['assessment'] == 'secretary':
        print(f"\n    ⚠ SECRETARY SESSION DETECTED.")
        print(f"      This session only corrected existing content.")
        print(f"      Ensure substantive design work was produced, not just corrections.")
    
    print(f"\n{'=' * 60}")


if __name__ == '__main__':
    main()
