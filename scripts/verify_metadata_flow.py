#!/usr/bin/env python3
"""Verify metadata flows through the pipeline without loss (D-023).

Reads each engine's SPEC §2 (Input Contract) and §3 (Output Contract) to build
a metadata field inventory, then checks that no field is lost between stages.

Usage:
    python3 scripts/verify_metadata_flow.py
    python3 scripts/verify_metadata_flow.py --verbose
    python3 scripts/verify_metadata_flow.py --boundary source normalization
"""

import re
import sys
import argparse

# Ensure Unicode output works on Windows (cp1252 can't encode → and ⚠)
_reconfigure = getattr(sys.stdout, "reconfigure", None)
if _reconfigure is not None:
    _reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

# Pipeline order
PIPELINE = [
    'source', 'normalization', 'passaging', 'atomization',
    'excerpting', 'taxonomy', 'synthesis'
]

ENGINE_DIRS = {
    name: Path(f'engines/{name}/SPEC.md') for name in PIPELINE
}

# Engines where the SPEC output section describes more fields than the
# runtime contract actually emits (deferred features, human-gate, etc.).
# For these engines, SPEC-based field analysis overestimates the active
# boundary. The authoritative runtime contract file is listed here.
_DUAL_CONTRACT_ENGINES = {
    'taxonomy': 'engines/taxonomy/contracts_core.py',
}


def extract_field_names(spec_text: str, section_pattern: str) -> set:
    """Extract field names mentioned in a SPEC section.
    
    Looks for:
    - `field_name` (backtick-quoted identifiers)
    - field_name: (colon-terminated identifiers in lists)
    - "field_name" in JSON-like contexts
    """
    # Find the target section
    section_match = re.search(
        rf'##\s+{section_pattern}.*?\n(.*?)(?=\n##\s|\Z)',
        spec_text,
        re.DOTALL
    )
    if not section_match:
        return set()

    section_text = section_match.group(1)
    fields = set()

    # Backtick-quoted identifiers
    fields.update(re.findall(r'`([a-z][a-z_0-9]*)`', section_text))

    # JSON-style field references
    fields.update(re.findall(r'"([a-z][a-z_0-9]*)"', section_text))

    # Remove common non-field words
    noise = {
        'true', 'false', 'null', 'none', 'json', 'jsonl', 'html', 'utf',
        'sha', 'api', 'llm', 'pdf', 'epub', 'ocr', 'info', 'content',
        'e', 'g', 'i', 'etc', 'not', 'yet', 'implemented'
    }
    fields -= noise

    return fields


def analyze_boundary(upstream: str, downstream: str, verbose: bool = False) -> dict:
    """Analyze metadata flow at one pipeline boundary."""
    upstream_path = ENGINE_DIRS.get(upstream)
    downstream_path = ENGINE_DIRS.get(downstream)

    if not upstream_path or not upstream_path.exists():
        return {'error': f'{upstream} SPEC not found'}
    if not downstream_path or not downstream_path.exists():
        return {'error': f'{downstream} SPEC not found'}

    upstream_text = upstream_path.read_text(encoding='utf-8')
    downstream_text = downstream_path.read_text(encoding='utf-8')

    # Extract output fields from upstream (handles both "## 3. Output Contract"
    # and "## §2.2 — Output Contract" heading formats across engines)
    upstream_output = extract_field_names(upstream_text, r'.*?Output\s*Contract')

    # Extract input fields from downstream
    downstream_input = extract_field_names(downstream_text, r'.*?Input\s*Contract')

    # Extract output fields from downstream (for pass-through check)
    downstream_output = extract_field_names(downstream_text, r'.*?Output\s*Contract')

    # Fields downstream expects but upstream doesn't produce
    missing_from_upstream = downstream_input - upstream_output

    # Fields upstream produces but downstream doesn't mention
    unused_by_downstream = upstream_output - downstream_input - downstream_output

    # Fields that appear in upstream output but not in downstream output (potential loss)
    potential_loss = upstream_output - downstream_output

    result = {
        'boundary': f'{upstream} → {downstream}',
        'upstream_output_fields': len(upstream_output),
        'downstream_input_fields': len(downstream_input),
        'downstream_output_fields': len(downstream_output),
        'missing_from_upstream': missing_from_upstream,
        'unused_by_downstream': unused_by_downstream,
        'potential_metadata_loss': potential_loss,
    }

    if verbose:
        result['upstream_output_detail'] = sorted(upstream_output)
        result['downstream_input_detail'] = sorted(downstream_input)
        result['downstream_output_detail'] = sorted(downstream_output)

    return result


def print_result(result: dict):
    """Pretty-print a boundary analysis result."""
    if 'error' in result:
        print(f"  ERROR: {result['error']}")
        return

    boundary = result['boundary']
    print(f"\n{'='*60}")
    print(f"  Boundary: {boundary}")

    # Flag dual-contract engines where SPEC overstates the runtime boundary
    upstream_name = boundary.split(' → ')[0].strip() if ' → ' in boundary else ''
    if upstream_name in _DUAL_CONTRACT_ENGINES:
        print(f"  NOTE: {upstream_name} runtime contract is {_DUAL_CONTRACT_ENGINES[upstream_name]}")
        print(f"        SPEC output section includes deferred fields not in runtime shape.")

    print(f"  Upstream output fields: {result['upstream_output_fields']}")
    print(f"  Downstream input fields: {result['downstream_input_fields']}")
    print(f"  Downstream output fields: {result['downstream_output_fields']}")

    if result['missing_from_upstream']:
        print(f"\n  ⚠ DOWNSTREAM EXPECTS BUT UPSTREAM DOESN'T PRODUCE:")
        for f in sorted(result['missing_from_upstream']):
            print(f"    - {f}")

    if result['potential_metadata_loss']:
        print(f"\n  ⚠ POTENTIAL METADATA LOSS (in upstream output, not in downstream output):")
        for f in sorted(result['potential_metadata_loss']):
            print(f"    - {f}")

    if not result['missing_from_upstream'] and not result['potential_metadata_loss']:
        print(f"\n  ✓ No metadata flow issues detected at this boundary.")

    if 'upstream_output_detail' in result:
        print(f"\n  Upstream output: {result['upstream_output_detail']}")
        print(f"  Downstream input: {result['downstream_input_detail']}")
        print(f"  Downstream output: {result['downstream_output_detail']}")


def main():
    parser = argparse.ArgumentParser(description='Verify metadata flow through the pipeline')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show field details')
    parser.add_argument('--boundary', '-b', nargs=2, metavar=('UPSTREAM', 'DOWNSTREAM'),
                       help='Check a specific boundary')
    args = parser.parse_args()

    print("KR Metadata Flow Verification (D-023)")
    print("=" * 60)

    if args.boundary:
        result = analyze_boundary(args.boundary[0], args.boundary[1], args.verbose)
        print_result(result)
    else:
        # Check all pipeline boundaries
        issues_found = 0
        for i in range(len(PIPELINE) - 1):
            result = analyze_boundary(PIPELINE[i], PIPELINE[i+1], args.verbose)
            print_result(result)
            if result.get('missing_from_upstream') or result.get('potential_metadata_loss'):
                issues_found += 1

        print(f"\n{'='*60}")
        if issues_found:
            print(f"⚠ {issues_found} boundaries with potential issues.")
        else:
            print("✓ All boundaries clear.")
        print()
        print("NOTE: This is a static analysis based on field names extracted from SPEC text.")
        print("It may produce false positives. Cross-reference with actual SPEC reading.")


if __name__ == '__main__':
    main()
