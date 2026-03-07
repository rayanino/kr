"""Atomization Engine — Main Orchestrator.

Implements SPEC §4.A.1: The five-phase per-passage pipeline.

For each source, processes the passage stream sequentially:
  Phase 1: Pre-screen (prescreen.py) — strategy selection, model selection
  Phase 2: Rule-based pre-detection (predetection.py) — pattern scanning
  Phase 3: LLM atomization (llm_atomizer.py) — boundary + classification
  Phase 4: Deterministic post-processing (postprocessor.py) — offset correction,
           coverage enforcement, layer attribution, footnote linkage
  Phase 5: Self-validation (validator.py) — 9 checks with auto-repair

On validation failure: retry up to max_retries_per_passage times with error
feedback to the LLM. If still failing, produce best available result with
review flags.

Parallelism: passages from the same source are sequential (monotonic atom_id).
Passages from different sources may be processed in parallel.

After all passages: emit atom stream, distribution report, fingerprint
manifest, terminological index (emitter.py). Update source status.
"""

from __future__ import annotations


def process_source(source_id: str) -> str:
    """Atomize all passages for a source.

    Returns path to the produced atoms.jsonl.
    Raises on fatal unrecoverable errors.
    """
    raise NotImplementedError


def process_passage(passage: dict, atom_id_counter: int,
                    config: "AtomizationConfig") -> tuple[list[dict], int]:
    """Execute the five-phase pipeline on a single passage.

    Returns (atoms_for_passage, next_atom_id_counter).
    """
    raise NotImplementedError
