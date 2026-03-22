"""Retry Approach B for taysir divisions with higher MAX_TOKENS.

The 2500-3100w taysir divisions produce 80+ classified segments,
exceeding the 8192 token limit. This retry uses 32768 tokens.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Literal, Optional

import instructor
import openai
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DIVISIONS_DIR = Path(__file__).resolve().parent / "divisions"
RESULTS_DIR = Path(__file__).resolve().parent / "results"

MODEL = "anthropic/claude-opus-4.6"
TEMPERATURE = 0
MAX_TOKENS = 32768  # Increased from 8192 for longer classify output
MAX_RETRIES = 2

# ── Schemas (identical) ──

FUNCTION_ENUM = Literal[
    "definition", "rule_statement", "evidence_quran", "evidence_hadith",
    "evidence_ijma", "evidence_qiyas", "evidence_rational",
    "opinion_statement", "refutation", "example", "condition_exception",
    "cross_reference", "narration", "editorial_note", "structural_transition",
    "unclassified",
]


class TeachingUnit(BaseModel):
    unit_index: int = Field(description="0-based index within this division")
    start_word: int = Field(description="Approximate start word offset in assembled text")
    end_word: int = Field(description="Approximate end word offset in assembled text")
    text_snippet: str = Field(description="First 80 characters of this unit's text")
    description_arabic: str = Field(description="Brief Arabic description of what this unit teaches, 10-30 words")
    primary_function: FUNCTION_ENUM
    secondary_functions: list[str] = Field(default_factory=list)
    self_contained: bool = Field(description="Can this unit be understood without surrounding context?")
    self_containment_notes: Optional[str] = None


class ExtractionResult(BaseModel):
    teaching_units: list[TeachingUnit]
    total_units: int
    notes: Optional[str] = None


class ClassifiedSegment(BaseModel):
    segment_index: int
    start_word: int
    end_word: int
    text_snippet: str = Field(description="First 50 chars of segment text")
    scholarly_function: FUNCTION_ENUM
    confidence: float = Field(ge=0.0, le=1.0)


class ClassificationResult(BaseModel):
    segments: list[ClassifiedSegment]
    total_segments: int


# ── Prompts (identical) ──

APPROACH_B_CLASSIFY_SYSTEM = """You are an expert in classical Islamic scholarly text analysis.

Classify each sentence or closely bonded group of sentences in this Arabic text by scholarly function:
definition, rule_statement, evidence_quran, evidence_hadith, evidence_ijma,
evidence_qiyas, evidence_rational, opinion_statement, refutation, example,
condition_exception, cross_reference, narration, editorial_note,
structural_transition, unclassified

Rules:
- An isnad chain + its matn = one segment (narration or evidence_hadith)
- A position marker ("قال X") + the stated position = one segment
- Each Quran citation with its introduction = one segment
- Each distinct sentence or bonded group gets exactly one classification
- Include text_snippet: the first 50 characters of each segment"""

APPROACH_B_GROUP_SYSTEM = """You are an expert in classical Islamic scholarly text analysis.

You previously classified segments of this Arabic text by scholarly function.
Now group these classified segments into TEACHING UNITS — self-contained scholarly
segments that each teach one distinct concept, ruling, or argument.

Rules:
- A position (opinion_statement) + its evidence + any counter-evidence + conclusion = one unit
- A definition + its examples = one unit
- Never group unrelated content (e.g., two different مسائل) into one unit
- Each unit should be self-contained: a student can learn from it without the surrounding text
- Include text_snippet: the first 80 characters of each unit"""


# ── Client ──

def get_client() -> instructor.Instructor:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    return instructor.from_openai(
        openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        ),
        mode=instructor.Mode.JSON,
    )


api_log: list[dict] = []


def call_llm(client, system_prompt, user_message, response_model, fixture, div_id, approach, call_label):
    start_time = time.time()
    result = client.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        max_retries=MAX_RETRIES,
        response_model=response_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    latency_ms = int((time.time() - start_time) * 1000)
    log_entry = {"fixture": fixture, "div": div_id, "approach": approach, "call": call_label, "model": MODEL, "latency_ms": latency_ms}
    api_log.append(log_entry)
    print(f"    [{approach}/{call_label}] {latency_ms}ms")
    return result, log_entry


def save_result(fixture, div_start, approach, result):
    out_dir = RESULTS_DIR / fixture
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"div_{div_start}_approach_{approach.lower()}.json"
    with open(path, "w", encoding="utf-8") as f:
        f.write(result.model_dump_json(indent=2))
    return path


def main() -> None:
    client = get_client()

    # Load only taysir divisions
    taysir_dir = DIVISIONS_DIR / "taysir"
    divisions: list[dict] = []
    for json_file in sorted(taysir_dir.glob("div_*.json")):
        if "_text" in json_file.name:
            continue
        with open(json_file, "r", encoding="utf-8") as f:
            divisions.append(json.load(f))

    print(f"Retrying Approach B for {len(divisions)} taysir divisions (MAX_TOKENS={MAX_TOKENS})\n")

    for div in divisions:
        fixture = div["fixture_name"]
        div_start = div["div_start_unit"]
        heading_short = div["heading_text"][:50]

        # Check if B already succeeded
        b_path = RESULTS_DIR / fixture / f"div_{div_start}_approach_b.json"
        if b_path.exists():
            with open(b_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if "error" not in existing:
                print(f"  {fixture}/div_{div_start}: B already succeeded, skipping")
                continue

        print(f"\n  {fixture} / div_{div_start}: {heading_short} ({div['arabic_word_count']}w)")

        # Remove old error file
        error_path = RESULTS_DIR / fixture / f"div_{div_start}_approach_b_error.json"
        if error_path.exists():
            error_path.unlink()

        try:
            # Call 1: Classify
            classification, _ = call_llm(
                client, APPROACH_B_CLASSIFY_SYSTEM,
                div["assembled_text"], ClassificationResult,
                fixture, f"div_{div_start}", "B", "classify",
            )

            # Call 2: Group
            user_msg = (
                "Classified segments:\n"
                + classification.model_dump_json(indent=2)
                + "\n\nOriginal text:\n"
                + div["assembled_text"]
            )
            extraction, _ = call_llm(
                client, APPROACH_B_GROUP_SYSTEM,
                user_msg, ExtractionResult,
                fixture, f"div_{div_start}", "B", "group",
            )

            save_result(fixture, div_start, "b", extraction)
            save_result(fixture, div_start, "b_classify", classification)
            print(f"  B: {extraction.total_units} teaching units ({classification.total_segments} segments)")

        except Exception as e:
            print(f"  B: ERROR - {e}")
            out_dir = RESULTS_DIR / fixture
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / f"div_{div_start}_approach_b_error.json", "w", encoding="utf-8") as f:
                json.dump({"error": str(e), "type": type(e).__name__}, f, indent=2)

    print(f"\nTotal API calls: {len(api_log)}")
    total_latency = sum(e["latency_ms"] for e in api_log)
    print(f"Total latency: {total_latency / 1000:.1f}s")


if __name__ == "__main__":
    main()
