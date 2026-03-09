"""Atomization engine — tracer bullet entry point.

Splits passages into atomic scholarly units.
Simple strategy: split on Arabic sentence boundaries.
"""

import json
import re
from pathlib import Path


def process(input_path: Path, output_path: Path, config: dict) -> None:
    """Atomize passages into atoms.

    Args:
        input_path: Path to PassageStream JSON.
        output_path: Path to write AtomStream JSON.
        config: Engine configuration.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    stream = json.loads(input_path.read_text(encoding="utf-8"))
    source_id = stream["source_id"]
    passages = stream["passages"]

    atoms = []
    for passage in passages:
        passage_id = passage["passage_id"]
        passage_text = passage["passage_text"]
        text_layers = passage.get("text_layers", [])

        # Split into sentences on Arabic period, question mark, or newline
        sentences = _split_arabic_sentences(passage_text)

        for seq, sentence in enumerate(sentences):
            if not sentence.strip():
                continue

            atom_id = f"{passage_id}_a{seq:03d}"
            start = passage_text.find(sentence)
            end = start + len(sentence) if start >= 0 else len(sentence)

            # Determine source layer for this atom
            source_layer = "sharh"  # default
            for tl in text_layers:
                if tl["start"] <= start < tl["end"]:
                    source_layer = tl["layer_type"]
                    break

            # Guess scholarly function from content
            scholarly_function = _guess_scholarly_function(sentence)

            atom = {
                "schema_version": "0.1.0",
                "atom_id": atom_id,
                "passage_id": passage_id,
                "source_id": source_id,
                "sequence_in_passage": seq,
                "atom_text": sentence.strip(),
                "anchor_span": {"start": max(start, 0), "end": end},
                "structural_type": "prose_sentence",
                "scholarly_function": scholarly_function,
                "function_confidence": 0.6,
                "source_layer": source_layer,
                "layer_author_id": None,
                "embedded_refs": [],
                "footnote_source_index": None,
                "footnote_refs": [],
                "atom_relations": [],
                "attributions": None,
                "fingerprint_text_hash": None,
                "fingerprint_key_terms": None,
                "fingerprint_embedding": None,
                "concordance_entry": None,
                "evidence_quality_signals": None,
                "classification_notes": None,
                "bonded_reason": None,
                "review_flags": [],
            }
            atoms.append(atom)

    atom_stream = {
        "source_id": source_id,
        "atoms": atoms,
    }

    output_path.write_text(
        json.dumps(atom_stream, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _split_arabic_sentences(text: str) -> list[str]:
    """Split Arabic text into sentences."""
    # Split on period followed by space, or explicit newlines
    # Arabic sentence endings: . (period), ؟ (question mark), ! (exclamation)
    # Also split on newlines which often mark paragraph boundaries
    parts = re.split(r'(?<=[.؟!])\s+|\n+', text)
    result = []
    for p in parts:
        p = p.strip()
        if p:
            result.append(p)
    return result


def _guess_scholarly_function(text: str) -> str:
    """Heuristic classification of scholarly function."""
    # Check for definition markers
    if any(marker in text for marker in ["هو", "هي", "المراد", "معنى", "اصطلاح"]):
        return "definition"
    # Check for rule/condition
    if any(marker in text for marker in ["يجب", "يجوز", "لا يجوز", "شرط", "شروط"]):
        return "rule_statement"
    # Check for evidence
    if any(marker in text for marker in ["قال الله", "قوله تعالى", "الآية"]):
        return "evidence_quran"
    if any(marker in text for marker in ["قال النبي", "حديث", "رواه"]):
        return "evidence_hadith"
    # Check for example
    if any(marker in text for marker in ["نحو", "مثال", "كقولك"]):
        return "example"
    # Check for exclusion/caveat
    if any(marker in text for marker in ["احترز", "أخرج", "فصل"]):
        return "condition_exception"
    # Check for opinion
    if any(marker in text for marker in ["قال", "ذهب", "مذهب", "رأى"]):
        return "opinion_statement"
    return "unclassified"
