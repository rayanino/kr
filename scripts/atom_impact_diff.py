#!/usr/bin/env python3
"""S-08: Compute with/without-atom behavior delta.

Renders a prompt with and without a specific atom's contribution and
produces a structured diff of the behavioral impact. The actual LLM
comparison is deferred; this script defines the interface and produces
the impact artifact structure.

Output: impact/<atom_id>/<run_id>.json with before/after structured diff.

Usage:
    python scripts/atom_impact_diff.py --atom-id MAQ-042 --fixture taysir --chunk 0
    python scripts/atom_impact_diff.py --atom-id MAQ-042 --fixture taysir --chunk 0 --output-dir impact/
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_atom_definition(atom_id: str) -> dict | None:
    """Locate and load an atom definition from the MAQ registry.

    Searches engines/excerpting/ for atom definitions. Returns None
    if the atom is not found.
    """
    # Search common locations for atom definitions
    search_dirs = [
        REPO_ROOT / "engines" / "excerpting" / "atoms",
        REPO_ROOT / "engines" / "excerpting" / "maq",
        REPO_ROOT / "engines" / "excerpting" / "reference" / "atoms",
    ]
    for search_dir in search_dirs:
        candidate = search_dir / f"{atom_id}.json"
        if candidate.is_file():
            with open(candidate, encoding="utf-8") as f:
                return json.load(f)
    # Also check JSONL registries
    for search_dir in search_dirs:
        registry = search_dir / "registry.jsonl"
        if registry.is_file():
            with open(registry, encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    entry = json.loads(stripped)
                    if entry.get("atom_id") == atom_id:
                        return entry
    return None


def render_prompt_with_atom(atom_def: dict, fixture: str, chunk: int) -> str:
    """Render the prompt with the atom included (stub).

    Returns a placeholder representing the rendered prompt. Actual
    prompt rendering requires the full excerpting engine context.
    """
    return f"[PROMPT with atom {atom_def.get('atom_id', '?')} | fixture={fixture} chunk={chunk}]"


def render_prompt_without_atom(atom_def: dict, fixture: str, chunk: int) -> str:
    """Render the prompt without the atom (stub).

    Returns a placeholder representing the rendered prompt. Actual
    prompt rendering requires the full excerpting engine context.
    """
    return f"[PROMPT without atom {atom_def.get('atom_id', '?')} | fixture={fixture} chunk={chunk}]"


def compute_structural_diff(with_prompt: str, without_prompt: str) -> dict:
    """Compute structural differences between with/without prompts.

    Returns a diff artifact. LLM behavioral comparison is deferred.
    """
    return {
        "prompt_with_atom_length": len(with_prompt),
        "prompt_without_atom_length": len(without_prompt),
        "char_delta": len(with_prompt) - len(without_prompt),
        "token_delta_estimate": (len(with_prompt) - len(without_prompt)) // 4,
        "llm_comparison": "DEFERRED",
        "behavioral_delta": None,
    }


def build_impact_artifact(
    atom_id: str,
    fixture: str,
    chunk: int,
    atom_def: dict | None,
    diff: dict,
) -> dict:
    """Build the full impact artifact."""
    run_id = str(uuid.uuid4())[:8]
    return {
        "run_id": run_id,
        "atom_id": atom_id,
        "fixture": fixture,
        "chunk": chunk,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "atom_found": atom_def is not None,
        "atom_definition": atom_def,
        "structural_diff": diff,
        "status": "STUB_ONLY",
        "notes": (
            "LLM behavioral comparison deferred. This artifact defines "
            "the interface and records the structural prompt delta."
        ),
    }


def main() -> int:
    """Entry point: compute atom impact diff."""
    parser = argparse.ArgumentParser(
        description="S-08: Compute with/without-atom behavior delta.",
    )
    parser.add_argument(
        "--atom-id",
        type=str,
        required=True,
        help="Identifier of the atom to test (e.g., MAQ-042).",
    )
    parser.add_argument(
        "--fixture",
        type=str,
        required=True,
        help="Fixture/package name (e.g., taysir, ibn_aqil_v1).",
    )
    parser.add_argument(
        "--chunk",
        type=int,
        required=True,
        help="Chunk index within the fixture.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: impact/<atom_id>/).",
    )
    args = parser.parse_args()

    atom_id: str = args.atom_id
    fixture: str = args.fixture
    chunk: int = args.chunk

    log.info("Computing impact diff for atom %s on %s chunk %d", atom_id, fixture, chunk)

    # Fix #11: Invalid atom ID must exit 1, not warn and succeed
    atom_def = load_atom_definition(atom_id)
    if atom_def is None:
        log.error(
            "Atom definition not found for %s — cannot compute impact diff", atom_id
        )
        return 1

    # Fix #4: Stub must exit 1 (fail-closed) until real implementation exists
    log.error(
        "STUB: atom impact comparison not yet implemented. "
        "Cannot verify behavioral delta."
    )

    # Still write the artifact for traceability, but exit 1
    with_prompt = render_prompt_with_atom(atom_def, fixture, chunk)
    without_prompt = render_prompt_without_atom(atom_def, fixture, chunk)

    diff = compute_structural_diff(with_prompt, without_prompt)
    artifact = build_impact_artifact(atom_id, fixture, chunk, atom_def, diff)

    output_dir: Path = (
        args.output_dir or REPO_ROOT / "impact" / atom_id
    ).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{artifact['run_id']}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2, ensure_ascii=False)
    log.info("Impact artifact written to %s (exit 1 — stub only)", output_path)

    return 1


if __name__ == "__main__":
    sys.exit(main())
