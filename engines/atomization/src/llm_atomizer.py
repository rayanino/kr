"""Atomization Engine — LLM-Driven Type Classification (Phase 3).

Implements SPEC §4.A.5: LLM atomization.

Sends the passage text, pre-detection hints, structural format, layer
information, and few-shot examples to the LLM. The LLM identifies atom
boundaries and classifies each atom by structural type and scholarly function.

Uses the Instructor library for structured output with Pydantic schema
enforcement and automatic retries on schema violation. DSPy may be used
for prompt optimization against gold baselines.

The LLM prompt includes:
  - The passage text
  - Pre-detection hints as constraints (from Phase 2)
  - The structural format (determines which boundary rules apply)
  - Text layer information (for multi-layer attribution awareness)
  - Few-shot examples from gold baselines (format-specific)
  - The atom type taxonomy (structural types + scholarly functions)
  - Atom boundary rules (AB-1 through AB-7 from §4.A.2)

When enable_attribution_detection is true (§4.B.4), the prompt also
requests scholarly attribution chain extraction per atom.

When enable_concordance_extraction is true (§4.B.7), the prompt also
requests concordance entry extraction for definition atoms.
"""

from __future__ import annotations


def atomize_passage_llm(passage_text: str, predetection_hints: list[dict],
                        structural_format: str, text_layers: list[dict],
                        prescreen_params: dict,
                        config: "AtomizationConfig") -> list[dict]:
    """Send passage to LLM for atomization and return raw atom objects.

    Returns a list of raw atom dicts from the LLM (before post-processing).
    On LLM failure after retries, raises with ATOM_LLM_FAILURE.
    On schema violation after retries, raises with ATOM_SCHEMA_VIOLATION.
    """
    raise NotImplementedError


def build_atomization_prompt(passage_text: str, predetection_hints: list[dict],
                             structural_format: str, text_layers: list[dict],
                             config: "AtomizationConfig") -> list[dict]:
    """Build the LLM prompt messages for atomization.

    Selects few-shot examples based on structural_format.
    Includes pre-detection hints as constraints.
    Returns message list suitable for Instructor.
    """
    raise NotImplementedError
