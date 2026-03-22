"""Deliverable 3: Run LLM teaching-unit extraction tests on format diversity divisions.

Two approaches (no Approach C):
  A — Single-call joint extraction
  B — Two-call classify-then-group

All calls go through OpenRouter using anthropic/claude-opus-4.6.
Results saved to experiments/format_diversity_test/results/{fixture}/{div}_{approach}.json.
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
MAX_TOKENS = 32768  # 8192 insufficient for classify on 2500+ word divisions
MAX_RETRIES = 2

# ──────────────────────────────────────────────────────────────────
# Pydantic Schemas (IDENTICAL to architecture_test — DO NOT MODIFY)
# ──────────────────────────────────────────────────────────────────

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


# ──────────────────────────────────────────────────────────────────
# Prompts (IDENTICAL to architecture_test — DO NOT MODIFY)
# ──────────────────────────────────────────────────────────────────

APPROACH_A_SYSTEM = """You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).

You will receive Arabic scholarly text from a single division of a book. Your task:

1. Identify the natural TEACHING UNITS — self-contained scholarly segments that each teach one distinct concept, ruling, or argument. A teaching unit is the smallest segment a student could study and learn something complete from. Examples:
   - A definition with its explanation
   - A scholarly position (مسألة) with its evidence and conclusion
   - A hadith with its chain and commentary
   - A grammatical rule with its examples

2. For each teaching unit, classify its PRIMARY scholarly function from this list:
   definition, rule_statement, evidence_quran, evidence_hadith, evidence_ijma,
   evidence_qiyas, evidence_rational, opinion_statement, refutation, example,
   condition_exception, cross_reference, narration, editorial_note,
   structural_transition, unclassified

3. Evaluate whether each teaching unit is SELF-CONTAINED: can a student with general familiarity of the science understand what is being taught without reading the surrounding text?

Important rules:
- Never split an argument (position + evidence + counter-evidence + conclusion) across units
- Never split an isnad chain from its matn
- A reported position ("قال أبو حنيفة") and its refutation ("ورد عليه بأن") belong in the same unit
- Consecutive definitions of related terms may be separate units if each is independently understandable
- Include text_snippet: the first 80 characters of each unit's text (copy exactly from input)"""

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

# ──────────────────────────────────────────────────────────────────
# API Client
# ──────────────────────────────────────────────────────────────────

def get_client() -> instructor.Instructor:
    """Create Instructor-wrapped OpenAI client pointing to OpenRouter."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY environment variable not set. "
            "Set it before running: export OPENROUTER_API_KEY=sk-or-..."
        )
    return instructor.from_openai(
        openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        ),
        mode=instructor.Mode.JSON,
    )


# ──────────────────────────────────────────────────────────────────
# API Call Wrapper
# ──────────────────────────────────────────────────────────────────

api_log: list[dict] = []


def call_llm(
    client: instructor.Instructor,
    system_prompt: str,
    user_message: str,
    response_model: type,
    fixture: str,
    div_id: str,
    approach: str,
    call_label: str,
) -> tuple[object, dict]:
    """Make an Instructor-wrapped LLM call with logging."""
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

    log_entry = {
        "fixture": fixture,
        "div": div_id,
        "approach": approach,
        "call": call_label,
        "model": MODEL,
        "latency_ms": latency_ms,
    }
    api_log.append(log_entry)
    print(f"    [{approach}/{call_label}] {latency_ms}ms")

    return result, log_entry


# ──────────────────────────────────────────────────────────────────
# Approach Implementations
# ──────────────────────────────────────────────────────────────────

def run_approach_a(
    client: instructor.Instructor,
    division: dict,
) -> ExtractionResult:
    """Approach A: Single-call joint extraction."""
    result, _ = call_llm(
        client=client,
        system_prompt=APPROACH_A_SYSTEM,
        user_message=division["assembled_text"],
        response_model=ExtractionResult,
        fixture=division["fixture_name"],
        div_id=f"div_{division['div_start_unit']}",
        approach="A",
        call_label="extract",
    )
    return result


def run_approach_b(
    client: instructor.Instructor,
    division: dict,
) -> tuple[ExtractionResult, ClassificationResult]:
    """Approach B: Two-call classify-then-group."""
    # Call 1: Classify segments
    classification, _ = call_llm(
        client=client,
        system_prompt=APPROACH_B_CLASSIFY_SYSTEM,
        user_message=division["assembled_text"],
        response_model=ClassificationResult,
        fixture=division["fixture_name"],
        div_id=f"div_{division['div_start_unit']}",
        approach="B",
        call_label="classify",
    )

    # Call 2: Group into teaching units
    user_msg = (
        "Classified segments:\n"
        + classification.model_dump_json(indent=2)
        + "\n\nOriginal text:\n"
        + division["assembled_text"]
    )
    extraction, _ = call_llm(
        client=client,
        system_prompt=APPROACH_B_GROUP_SYSTEM,
        user_message=user_msg,
        response_model=ExtractionResult,
        fixture=division["fixture_name"],
        div_id=f"div_{division['div_start_unit']}",
        approach="B",
        call_label="group",
    )

    return extraction, classification


# ──────────────────────────────────────────────────────────────────
# Division Loading
# ──────────────────────────────────────────────────────────────────

def load_all_divisions() -> list[dict]:
    """Load all division JSON files from the divisions directory."""
    divisions: list[dict] = []
    for fixture_dir in sorted(DIVISIONS_DIR.iterdir()):
        if not fixture_dir.is_dir():
            continue
        for json_file in sorted(fixture_dir.glob("div_*.json")):
            if "_text" in json_file.name:
                continue
            with open(json_file, "r", encoding="utf-8") as f:
                divisions.append(json.load(f))
    return divisions


# ──────────────────────────────────────────────────────────────────
# Result Saving
# ──────────────────────────────────────────────────────────────────

def save_result(fixture: str, div_start: int, approach: str, result: BaseModel) -> Path:
    """Save a Pydantic result to JSON."""
    out_dir = RESULTS_DIR / fixture
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"div_{div_start}_approach_{approach.lower()}.json"
    with open(path, "w", encoding="utf-8") as f:
        f.write(result.model_dump_json(indent=2))
    return path


def save_error(fixture: str, div_start: int, approach: str, error: Exception) -> Path:
    """Save an error result."""
    out_dir = RESULTS_DIR / fixture
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"div_{div_start}_approach_{approach.lower()}_error.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"error": str(error), "type": type(error).__name__}, f, indent=2)
    return path


# ──────────────────────────────────────────────────────────────────
# Summary Generation
# ──────────────────────────────────────────────────────────────────

def generate_run_summary(divisions: list[dict], results: dict[str, dict]) -> None:
    """Write RUN_SUMMARY.md with per-division results and totals."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / "RUN_SUMMARY.md"

    total_calls = len(api_log)
    total_latency = sum(e["latency_ms"] for e in api_log)

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Format Diversity Experiment — Run Summary\n\n")
        f.write(f"**Model:** {MODEL}\n")
        f.write(f"**Total API calls:** {total_calls}\n")
        f.write(f"**Total latency:** {total_latency / 1000:.1f}s\n\n")

        f.write("## Per-Division Results\n\n")
        f.write("| Fixture | Div | Heading | Words | A Units | B Units | Errors |\n")
        f.write("|---------|-----|---------|-------|---------|---------|--------|\n")

        for div in divisions:
            key = f"{div['fixture_name']}/div_{div['div_start_unit']}"
            r = results.get(key, {})
            heading_short = div["heading_text"][:40]

            a_units = r.get("a_units", "ERR")
            b_units = r.get("b_units", "ERR")
            errors = r.get("errors", [])
            error_str = ", ".join(errors) if errors else "none"

            f.write(
                f"| {div['fixture_name']} | {div['div_start_unit']} "
                f"| {heading_short} | {div['arabic_word_count']} "
                f"| {a_units} | {b_units} | {error_str} |\n"
            )

        f.write("\n## API Call Log\n\n")
        f.write("| Fixture | Div | Approach | Call | Latency (ms) |\n")
        f.write("|---------|-----|----------|------|-------------|\n")
        for entry in api_log:
            f.write(
                f"| {entry['fixture']} | {entry['div']} "
                f"| {entry['approach']} | {entry['call']} "
                f"| {entry['latency_ms']} |\n"
            )

        f.write(f"\n**Total API calls:** {total_calls}\n")
        f.write(f"**Total latency:** {total_latency / 1000:.1f}s\n")

    print(f"\nRun summary written to: {path}")


# ──────────────────────────────────────────────────────────────────
# Main Execution
# ──────────────────────────────────────────────────────────────────

def main() -> None:
    client = get_client()
    divisions = load_all_divisions()
    print(f"Loaded {len(divisions)} divisions\n")

    results_tracker: dict[str, dict] = {}

    for div in divisions:
        fixture = div["fixture_name"]
        div_start = div["div_start_unit"]
        key = f"{fixture}/div_{div_start}"
        heading_short = div["heading_text"][:50]

        print(f"\n{'='*60}")
        print(f"  {fixture} / div_{div_start}: {heading_short}")
        print(f"  Words: {div['arabic_word_count']}")
        print(f"{'='*60}")

        tracker: dict[str, object] = {"errors": []}

        # Approach A
        try:
            result_a = run_approach_a(client, div)
            save_result(fixture, div_start, "a", result_a)
            tracker["a_units"] = result_a.total_units
            print(f"  A: {result_a.total_units} teaching units")
        except Exception as e:
            save_error(fixture, div_start, "a", e)
            tracker["a_units"] = "ERR"
            tracker["errors"].append(f"A:{type(e).__name__}")
            print(f"  A: ERROR - {e}")

        # Approach B
        try:
            result_b, classification_b = run_approach_b(client, div)
            save_result(fixture, div_start, "b", result_b)
            save_result(fixture, div_start, "b_classify", classification_b)
            tracker["b_units"] = result_b.total_units
            print(f"  B: {result_b.total_units} teaching units ({classification_b.total_segments} segments)")
        except Exception as e:
            save_error(fixture, div_start, "b", e)
            tracker["b_units"] = "ERR"
            tracker["errors"].append(f"B:{type(e).__name__}")
            print(f"  B: ERROR - {e}")

        results_tracker[key] = tracker

    # Generate summary
    generate_run_summary(divisions, results_tracker)

    # Final table
    print("\n" + "=" * 100)
    print("FINAL RESULTS TABLE")
    print("=" * 100)
    print(f"{'Fixture':<20} {'Div':>5} {'Heading':<42} {'Words':>6} {'A':>4} {'B':>4} {'Errors'}")
    print("-" * 100)

    for div in divisions:
        key = f"{div['fixture_name']}/div_{div['div_start_unit']}"
        r = results_tracker.get(key, {})
        heading_short = div["heading_text"][:40]
        errors = r.get("errors", [])
        error_str = ", ".join(errors) if errors else ""
        print(
            f"{div['fixture_name']:<20} {div['div_start_unit']:>5} {heading_short:<42} "
            f"{div['arabic_word_count']:>6} {r.get('a_units', '?'):>4} "
            f"{r.get('b_units', '?'):>4} {error_str}"
        )

    print(f"\nTotal API calls: {len(api_log)}")


if __name__ == "__main__":
    main()
