#!/usr/bin/env python3
"""Bundle all files Claude needs for a session into a single attachable file.

Usage:
    python3 scripts/bundle_session.py source
    python3 scripts/bundle_session.py normalization
    python3 scripts/bundle_session.py excerpting
    python3 scripts/bundle_session.py passaging
    python3 scripts/bundle_session.py atomization
    python3 scripts/bundle_session.py taxonomy
    python3 scripts/bundle_session.py synthesis
    python3 scripts/bundle_session.py shared
    python3 scripts/bundle_session.py crosscutting
    python3 scripts/bundle_session.py custom file1.py file2.md ...

Each engine has a predefined set of files (code, reference docs, schemas, VISION
sections). The script concatenates them with clear delimiters into a single file
that the owner attaches to the Claude Chat session.

Output: session_bundle.md in repo root (gitignored).
"""

import sys
import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def vision_extract(sections):
    """Extract VISION.md sections using the extraction script."""
    script = os.path.join(REPO_ROOT, 'scripts', 'extract_vision_sections.py')
    cmd = [sys.executable, script] + sections
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    return result.stdout

# Define what each engine session needs
# Format: { 'engine_name': { 'files': [...], 'vision_sections': [...], 'notes': '...' } }
# IMPORTANT: Every bundle MUST include '2' (full glossary) for self-review glossary compliance.
# Additional VISION sections are engine-specific.
ENGINE_BUNDLES = {
    'source': {
        'files': [
            'engines/source/src/intake.py',
            'engines/source/src/enrich.py',
            'engines/source/src/corpus_audit.py',
            'engines/source/reference/ABD_INTAKE_SPEC.md',
            'engines/source/reference/edge_cases.md',
            'engines/source/CLAUDE.md',
            'schemas/source_metadata.json',
            'schemas/SCHEMA_ANALYSIS.md',
        ],
        'vision_sections': ['7.1', '7.4', '2'],
        'notes': 'First engine in the pipeline. No upstream SPECs exist yet.',
    },
    'normalization': {
        'files': [
            'engines/normalization/src/normalizers/normalize_shamela.py',
            'engines/normalization/src/discover_structure.py',
            'engines/normalization/src/validate_structure.py',
            'engines/normalization/reference/ABD_NORMALIZATION_SPEC.md',
            'engines/normalization/reference/ABD_STRUCTURE_SPEC.md',
            'engines/normalization/CLAUDE.md',
            'schemas/normalized_package.json',
            'schemas/source_metadata.json',
        ],
        'vision_sections': ['7.5', '7.6', '2'],
        'notes': 'Heaviest engine. discover_structure.py is ~2900L. Key decision: normalization/passaging boundary.',
        'session_split': {
            1: {
                'files': [
                    'engines/normalization/src/discover_structure.py',
                    'engines/normalization/src/normalizers/normalize_shamela.py',
                    'engines/normalization/src/validate_structure.py',
                    'engines/normalization/reference/ABD_NORMALIZATION_SPEC.md',
                    'engines/normalization/reference/ABD_STRUCTURE_SPEC.md',
                    'engines/normalization/CLAUDE.md',
                    'schemas/normalized_package.json',
                    'schemas/source_metadata.json',
                ],
                'note': 'Session 1: Code study + boundary decision. Also attach source SPEC if written.',
            },
            2: {
                'files': [
                    'engines/normalization/reference/SHAMELA_HTML_REFERENCE.md',
                    'engines/normalization/reference/structure_edge_cases.md',
                    'schemas/normalized_package.json',
                ],
                'note': 'Session 2: SPEC drafting. Also attach session 1 draft + source SPEC.',
            },
        },
    },
    'passaging': {
        'files': [
            'engines/passaging/src/scaffold_passage.py',
            'engines/passaging/CLAUDE.md',
            'schemas/passage.json',
            'schemas/normalized_package.json',
        ],
        'vision_sections': ['2.2', '2'],
        'notes': 'Light engine. Scope depends on normalization/passaging boundary decision. Also attach normalization SPEC.',
    },
    'atomization': {
        'files': [
            'engines/atomization/reference/ABD_ATOMIZATION_SPEC.md',
            'engines/atomization/reference/ABD_ZOOM_BRIEF.md',
            'engines/atomization/CLAUDE.md',
            'engines/excerpting/src/extract_passages.py',  # atomization logic lives here
            'schemas/atoms.json',
            'schemas/passage.json',
        ],
        'vision_sections': ['2'],
        'notes': 'No dedicated code — logic is in excerpting/extract_passages.py. Key decision: atomization/excerpting boundary. Also attach passaging SPEC.',
    },
    'excerpting': {
        'files': [
            'engines/excerpting/src/extract_passages.py',
            'engines/excerpting/src/assemble_excerpts.py',
            'engines/excerpting/reference/ABD_BINDING_DECISIONS.md',
            'engines/excerpting/reference/ABD_EXCERPTING_SPEC.md',
            'engines/excerpting/reference/edge_cases.md',
            'engines/excerpting/CLAUDE.md',
            'schemas/excerpt.json',
            'schemas/atoms.json',
        ],
        'vision_sections': ['5', '2'],
        'notes': 'Most complex engine. 9 reference docs total — load critical ones first. Also attach atomization SPEC.',
        'session_split': {
            1: {
                'files': [
                    'engines/excerpting/src/extract_passages.py',
                    'engines/excerpting/src/assemble_excerpts.py',
                    'engines/excerpting/reference/ABD_BINDING_DECISIONS.md',
                    'engines/excerpting/reference/ABD_EXCERPTING_SPEC.md',
                    'engines/excerpting/reference/edge_cases.md',
                    'engines/excerpting/CLAUDE.md',
                    'schemas/excerpt.json',
                    'schemas/atoms.json',
                ],
                'note': 'Session 1: Code + critical reference docs. Also attach atomization SPEC.',
            },
            2: {
                'files': [
                    'engines/excerpting/reference/ABD_EXTRACTION_PROTOCOL.md',
                    'engines/excerpting/reference/ABD_RUNBOOK.md',
                    'engines/excerpting/reference/ABD_CHECKLISTS.md',
                ],
                'note': 'Session 2: Deeper reference docs + SPEC refinement. Also attach session 1 draft.',
            },
            3: {
                'files': [
                    'engines/excerpting/reference/ABD_EXCERPT_DEFINITION.md',
                ],
                'note': 'Session 3 (if needed): The 34K-token definition doc. Also attach session 2 draft.',
            },
        },
    },
    'taxonomy': {
        'files': [
            'engines/taxonomy/src/evolve_taxonomy.py',
            'engines/taxonomy/reference/ABD_TAXONOMY_SPEC.md',
            'engines/taxonomy/CLAUDE.md',
            'schemas/placed_excerpt.json',
            'schemas/excerpt.json',
        ],
        'vision_sections': ['4', '2'],
        'notes': 'Also attach excerpting SPEC. Key topics: placement, evolution, human gates.',
    },
    'synthesis': {
        'files': [
            'engines/synthesis/CLAUDE.md',
            'schemas/placed_excerpt.json',
        ],
        'vision_sections': ['6', '2'],
        'notes': 'No code exists. SPEC is pure design. Also attach taxonomy SPEC. Needs إملاء SCIENCE.md if it exists.',
    },
    'shared': {
        'files': [
            'shared/consensus/src/consensus.py',
            'shared/consensus/SPEC.md',
            'shared/human_gate/src/human_gate.py',
            'shared/human_gate/SPEC.md',
            'shared/validation/src/cross_validate.py',
            'shared/validation/SPEC.md',
            'shared/feedback/SPEC.md',
        ],
        'vision_sections': ['8', '9', '2'],
        'notes': '4 shared components in one session. consensus and human_gate have real code; feedback has none.',
    },
    'crosscutting': {
        'files': [
            'schemas/SCHEMA_ANALYSIS.md',
        ],
        'vision_sections': ['8', '9', '10', '11', '12', '2'],
        'notes': 'VISION sections not owned by any single engine. Do after all engine SPECs. Also: verify §0-§5, §13 with engine expertise.',
    },
}


def bundle_files(file_list, vision_sections=None, notes=None, session_num=None):
    """Bundle files into a single text with clear delimiters."""
    parts = []

    parts.append("# Session Bundle for Claude Chat")
    parts.append(f"# Generated by scripts/bundle_session.py")
    parts.append(f"# Files: {len(file_list)} source files" +
                 (f" + VISION sections {vision_sections}" if vision_sections else ""))
    if notes:
        parts.append(f"# Notes: {notes}")
    if session_num:
        parts.append(f"# This is session {session_num} of a multi-session work item")
    parts.append("")
    parts.append("=" * 80)
    parts.append("")

    for filepath in file_list:
        full_path = os.path.join(REPO_ROOT, filepath)
        if not os.path.exists(full_path):
            parts.append(f"### FILE: {filepath}")
            parts.append(f"### WARNING: File not found at {full_path}")
            parts.append("")
            continue

        size = os.path.getsize(full_path)
        line_count = sum(1 for _ in open(full_path, 'r', encoding='utf-8', errors='replace'))
        est_tokens = size // 3

        parts.append(f"{'=' * 80}")
        parts.append(f"FILE: {filepath}")
        parts.append(f"SIZE: {line_count} lines, ~{est_tokens:,} tokens")
        parts.append(f"{'=' * 80}")
        parts.append("")

        with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        # Strip trailing whitespace but keep content intact
        parts.append(content.rstrip())
        parts.append("")
        parts.append("")

    # Add VISION sections if requested
    if vision_sections:
        parts.append(f"{'=' * 80}")
        parts.append(f"VISION.md EXTRACTED SECTIONS: {', '.join(vision_sections)}")
        parts.append(f"{'=' * 80}")
        parts.append("")
        vision_content = vision_extract(vision_sections)
        if vision_content:
            parts.append(vision_content.rstrip())
        else:
            parts.append("### WARNING: VISION extraction failed")
        parts.append("")

    return '\n'.join(parts)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable engines:")
        for name in ENGINE_BUNDLES:
            info = ENGINE_BUNDLES[name]
            file_count = len(info['files'])
            has_split = 'session_split' in info
            print(f"  {name:20s} — {file_count} files" +
                  (f" (multi-session: use '{name}/1', '{name}/2')" if has_split else ""))
        print(f"  {'custom':20s} — specify files manually")
        sys.exit(1)

    target = sys.argv[1]

    # Handle session-specific bundles: "normalization/1", "excerpting/2"
    session_num = None
    if '/' in target:
        target, session_num = target.split('/', 1)
        session_num = int(session_num)

    if target == 'custom':
        files = sys.argv[2:]
        if not files:
            print("Usage: bundle_session.py custom file1.py file2.md ...")
            sys.exit(1)
        content = bundle_files(files)
    elif target in ENGINE_BUNDLES:
        info = ENGINE_BUNDLES[target]

        if session_num and 'session_split' in info:
            split = info['session_split'][session_num]
            content = bundle_files(
                split['files'],
                vision_sections=info.get('vision_sections'),
                notes=split.get('note', info.get('notes')),
                session_num=session_num,
            )
        else:
            content = bundle_files(
                info['files'],
                vision_sections=info.get('vision_sections'),
                notes=info.get('notes'),
            )
    else:
        print(f"Unknown engine: {target}")
        print(f"Available: {', '.join(ENGINE_BUNDLES.keys())}, custom")
        sys.exit(1)

    # Write to repo root
    output_path = os.path.join(REPO_ROOT, 'session_bundle.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Report
    size = os.path.getsize(output_path)
    est_tokens = size // 3
    print(f"✓ session_bundle.md ready ({size:,} bytes, ~{est_tokens:,} tokens)")
    print(f"  Attach this single file to your Claude Chat session.")

    if est_tokens > 80000:
        print(f"  ⚠️  WARNING: Bundle is large (~{est_tokens:,} tokens).")
        print(f"  Consider using session splits: {target}/1, {target}/2")


if __name__ == '__main__':
    main()
