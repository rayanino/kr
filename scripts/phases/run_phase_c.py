"""Phase C — Targeted LLM Probes on 73 Books.

Runs the FULL source engine pipeline (Steps 1–13) on owner-selected books,
captures every intermediate artifact per RESULT_PRESERVATION.md, and produces
structured results ready for owner review.

Usage:
    python scripts/run_phase_c.py COLLECTION_DIR --books books.txt
    python scripts/run_phase_c.py COLLECTION_DIR --book "الأربعون النووية"
    python scripts/run_phase_c.py COLLECTION_DIR --books books.txt --resume
    python scripts/run_phase_c.py COLLECTION_DIR --books books.txt --force
    python scripts/run_phase_c.py COLLECTION_DIR --books books.txt --dry-run

Requires: ANTHROPIC_API_KEY, OPENROUTER_API_KEY environment variables.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.source.contracts import ErrorCode, SourceMetadata
from engines.source.src.config import SourceEngineConfig, load_config
from engines.source.src.engine import acquire_source
from engines.source.src.exceptions import SourceEngineError
from engines.source.src.extractors import extract_metadata
from engines.source.src.format_detection import detect_format
from engines.source.src.metadata_inference import build_prompt_context
from engines.source.prompts.inference_v1 import SYSTEM_MESSAGE, USER_MESSAGE_TEMPLATE
from shared.scholar_authority.src.name_matching import normalized_name_similarity

# Monkey-patch: capture infer_metadata results from engine.py's namespace
import engines.source.src.engine as engine_mod

_original_infer = engine_mod.infer_metadata
_captured_inference: Any = None


async def _capturing_infer(*args: Any, **kwargs: Any) -> Any:
    """Wrapper that captures MetadataInferenceResult from infer_metadata."""
    global _captured_inference
    result = await _original_infer(*args, **kwargs)
    _captured_inference = result
    return result


engine_mod.infer_metadata = _capturing_infer

# Constants
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "tests" / "results" / "source_engine" / "phase_c"
COST_LOG_PATH = PROJECT_ROOT / "tests" / "results" / "source_engine" / "COST_LOG.json"
GROUND_TRUTH_PATH = PROJECT_ROOT / "tests" / "fixtures" / "GROUND_TRUTH.json"
FIXTURE_MAPPINGS_PATH = PROJECT_ROOT / "tests" / "fixtures" / "phase_c_fixture_mappings.json"
DEFAULT_COST_PER_BOOK = 0.15  # EUR, conservative estimate
METADATA_FIELDS_CHECK = [
    "display_title", "title_full", "author_name_raw", "author_short",
    "muhaqiq_name_raw", "publisher", "shamela_category", "edition_raw",
    "compiler_name_raw", "commentator_name_raw", "riwayah",
    "page_count", "volume_count", "source_format",
]


# ── CLI ──


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase C — Targeted LLM Probes")
    parser.add_argument("collection_dir", type=Path, help="Shamela collection directory")
    parser.add_argument("--books", type=Path, help="Text file with book directory names")
    parser.add_argument("--book", type=str, action="append", help="Single book directory name (repeatable)")
    parser.add_argument("--resume", action="store_true", help="Skip books with status success/gate_abort")
    parser.add_argument("--force", action="store_true", help="Re-process all books")
    parser.add_argument("--dry-run", action="store_true", help="Validate setup only")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--budget-eur", type=float, default=50.0, help="Budget ceiling in EUR")
    return parser.parse_args()


def check_env() -> None:
    missing = []
    if not os.environ.get("OPENROUTER_API_KEY"):
        missing.append("OPENROUTER_API_KEY")
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)


def load_books(books_file: Path) -> list[str]:
    lines = books_file.read_text(encoding="utf-8").splitlines()
    books = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            books.append(stripped)
    return books


def _resolve_book_path(collection_dir: Path, book_name: str) -> Path | None:
    """Resolve book name to actual path (directory or .htm file).

    Shamela books come in two formats:
    - Multi-volume: directories containing .htm page files
    - Single-volume: standalone .htm files (book list omits extension)
    """
    p = collection_dir / book_name
    if p.is_dir():
        return p
    htm = collection_dir / (book_name + ".htm")
    if htm.is_file():
        return htm
    if p.is_file():
        return p
    return None


def validate_books(collection_dir: Path, book_names: list[str]) -> None:
    missing = [name for name in book_names if _resolve_book_path(collection_dir, name) is None]
    if missing:
        print(f"ERROR: {len(missing)} books not found in {collection_dir}:")
        for name in missing[:10]:
            print(f"  - {name}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
        sys.exit(1)


def load_ground_truth() -> tuple[dict[str, dict], dict[str, str]]:
    """Load ground truth + fixture mappings. Returns (ground_truth, fixture_mappings)."""
    gt: dict[str, dict] = {}
    mappings: dict[str, str] = {}
    if GROUND_TRUTH_PATH.exists():
        gt = json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))
    if FIXTURE_MAPPINGS_PATH.exists():
        mappings = json.loads(FIXTURE_MAPPINGS_PATH.read_text(encoding="utf-8"))
    return gt, mappings


def get_git_commit_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


# ── Temp Library ──


def create_temp_library(base_dir: Path) -> SourceEngineConfig:
    library_root = base_dir / "library"
    staging = library_root / "staging"
    for d in [
        staging,
        library_root / "registries",
        library_root / "logs",
        library_root / "config",
        library_root / "gates" / "pending",
        library_root / "gates" / "resolved",
        library_root / "sources",
    ]:
        d.mkdir(parents=True, exist_ok=True)

    # Copy config from real library
    real_config = PROJECT_ROOT / "library" / "config"
    if real_config.exists():
        for cfg_file in real_config.iterdir():
            if cfg_file.is_file():
                shutil.copy2(cfg_file, library_root / "config" / cfg_file.name)

    # Configure human gate for this temp library
    from shared.human_gate.src.human_gate import configure as configure_gate
    configure_gate(gates_dir=library_root / "gates", auto_approve=True)

    return load_config(library_root)


# ── JSON Save ──


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


# ── Cost Tracking ──


def load_cost_log() -> dict:
    if COST_LOG_PATH.exists():
        return json.loads(COST_LOG_PATH.read_text(encoding="utf-8"))
    return {"phases": {}, "total_eur": 0.0, "budget_ceiling_eur": 100.0}


def save_cost_log(cost_log: dict) -> None:
    save_json(COST_LOG_PATH, cost_log)


def estimate_book_cost(captured: Any) -> float:
    """Estimate cost from captured inference result. Returns EUR."""
    if captured and hasattr(captured, "_full_consensus_result") and captured._full_consensus_result:
        cr = captured._full_consensus_result
        n_models = sum(1 for r in cr.model_responses if r.parse_success)
        return 0.05 * n_models  # ~0.05 per successful model call
    return DEFAULT_COST_PER_BOOK


# ── Per-Model Response Saving ──


def save_per_model_responses(captured: Any, output_dir: Path) -> None:
    """Save each ModelResponse to llm_responses/{model_name}.json."""
    if not captured or not hasattr(captured, "_full_consensus_result"):
        return
    cr = captured._full_consensus_result
    if not cr:
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    for resp in cr.model_responses:
        # Sanitize model name for filename
        model_name = resp.model_id.split("/")[-1].replace(".", "_").replace("-", "_")
        data = {
            "model_id": resp.model_id,
            "provider": resp.provider,
            "parse_success": resp.parse_success,
            "error": resp.error,
            "latency": resp.latency,
            "parsed": resp.parsed.model_dump(mode="json") if resp.parsed else None,
        }
        save_json(output_dir / f"{model_name}.json", data)


def save_consensus_details(captured: Any, output_path: Path) -> None:
    """Save consensus.json with agreement details."""
    if not captured or not hasattr(captured, "_full_consensus_result"):
        return
    cr = captured._full_consensus_result
    if not cr:
        return

    data = {
        "agreed": cr.agreed,
        "single_model_fallback": cr.single_model_fallback,
        "needs_human_gate": cr.needs_human_gate,
        "human_gate_trigger": cr.human_gate_trigger,
        "model_count": len(cr.model_responses),
        "successful_models": [r.model_id for r in cr.model_responses if r.parse_success],
        "failed_models": [r.model_id for r in cr.model_responses if not r.parse_success],
    }
    if hasattr(cr, "canonical_result") and cr.canonical_result:
        data["canonical_result_model"] = getattr(cr, "_canonical_source", "unknown")
    save_json(output_path, data)


# ── Ground Truth Comparison ──


def compare_science_scope(expected: list[str], actual: list[str]) -> dict:
    exp_set = set(expected)
    act_set = set(actual)
    result: dict[str, Any] = {
        "expected": expected,
        "actual": actual,
        "overlap": sorted(exp_set & act_set),
        "extra_in_actual": sorted(act_set - exp_set),
        "missing_from_actual": sorted(exp_set - act_set),
    }
    if exp_set == act_set:
        result["match_type"] = "exact_match"
    elif exp_set.issubset(act_set):
        result["match_type"] = "superset"
    elif act_set.issubset(exp_set):
        result["match_type"] = "subset"
    elif exp_set & act_set:
        result["match_type"] = "overlap"
    else:
        result["match_type"] = "disjoint"
    return result


def compare_ground_truth(result_data: dict, truth: dict) -> dict:
    """Compare pipeline output against ground truth with correct field mapping."""
    comparisons: dict[str, Any] = {}
    all_match = True

    if "genre" in truth:
        actual = result_data.get("genre", "")
        match = actual == truth["genre"]
        comparisons["genre"] = {"expected": truth["genre"], "actual": actual, "match": match}
        if not match:
            all_match = False

    if "author_identified" in truth:
        author = result_data.get("author", {})
        actual_name = author.get("name_arabic", "") if isinstance(author, dict) else ""
        gt_name = re.sub(r"\s*\(ت\s+\d+\s*هـ\)\s*$", "", truth["author_identified"]).strip()
        sim = normalized_name_similarity(gt_name, actual_name) if (gt_name and actual_name) else 0.0
        match = sim >= 0.80
        comparisons["author"] = {
            "expected": truth["author_identified"],
            "actual": actual_name,
            "match": match,
            "similarity": round(sim, 3),
        }
        if not match:
            all_match = False

    if "expected_trust" in truth:
        actual = result_data.get("trust_tier", "")
        match = actual == truth["expected_trust"]
        comparisons["trust_tier"] = {"expected": truth["expected_trust"], "actual": actual, "match": match}
        if not match:
            all_match = False

    if "is_multi_layer" in truth:
        actual = result_data.get("is_multi_layer", None)
        match = actual == truth["is_multi_layer"]
        comparisons["is_multi_layer"] = {"expected": truth["is_multi_layer"], "actual": actual, "match": match}
        if not match:
            all_match = False

    if "science_scope" in truth:
        actual = result_data.get("science_scope", [])
        sci_comp = compare_science_scope(truth["science_scope"], actual)
        comparisons["science_scope"] = sci_comp
        if sci_comp["match_type"] not in ("exact_match", "superset"):
            all_match = False

    if "structural_format" in truth:
        actual = result_data.get("structural_format", "")
        match = actual == truth["structural_format"]
        comparisons["structural_format"] = {"expected": truth["structural_format"], "actual": actual, "match": match}
        if not match:
            all_match = False

    if "authority_level" in truth:
        actual = result_data.get("authority_level", "")
        match = actual == truth["authority_level"]
        comparisons["authority_level"] = {"expected": truth["authority_level"], "actual": actual, "match": match}
        if not match:
            all_match = False

    if "level" in truth:
        actual = result_data.get("level", None)
        expected = truth["level"]
        match = actual == expected
        comparisons["level"] = {"expected": expected, "actual": actual, "match": match}
        if not match:
            all_match = False

    if "attribution_status" in truth:
        actual = result_data.get("attribution_status", "")
        match = actual == truth["attribution_status"]
        comparisons["attribution_status"] = {"expected": truth["attribution_status"], "actual": actual, "match": match}
        if not match:
            all_match = False

    return {"comparisons": comparisons, "all_match": all_match}


# ── Sanity Checks ──


def run_sanity_checks(result_data: dict, extraction: dict, prompt_sent: dict) -> dict:
    """6 deterministic post-pipeline checks. No LLM calls."""
    flags: list[dict] = []

    # 1. Multi-layer but empty layers
    if result_data.get("is_multi_layer") and not result_data.get("text_layers"):
        flags.append({
            "check": "multi_layer_no_layers",
            "severity": "error",
            "detail": "is_multi_layer=true but text_layers is empty",
        })

    # 2. Author name blank — only for success books (gate_abort has no author in result_data)
    author = result_data.get("author", {})
    if result_data.get("status") != "gate_abort":
        if isinstance(author, dict) and not author.get("name_arabic", "").strip():
            flags.append({
                "check": "author_name_blank",
                "severity": "error",
                "detail": "author.name_arabic is empty",
            })

    # 3. Death date mismatch between extraction and inference
    ext_death = extraction.get("author_death_hijri")
    inf_death = author.get("death_date_hijri") if isinstance(author, dict) else None
    if ext_death and inf_death and abs(ext_death - inf_death) > 20:
        flags.append({
            "check": "death_date_mismatch",
            "severity": "warning",
            "detail": f"Extracted {ext_death}, inferred {inf_death} (diff > 20 years)",
        })

    # 4. Genre-title plausibility
    title = result_data.get("title_arabic", "") or ""
    genre = result_data.get("genre", "")
    if "شرح" in title and genre not in ("sharh", "hashiyah", "taqrirat", "other"):
        flags.append({
            "check": "genre_title_mismatch",
            "severity": "warning",
            "detail": f"Title contains 'شرح' but genre is '{genre}'",
        })
    if "مختصر" in title and genre != "mukhtasar":
        flags.append({
            "check": "genre_title_mismatch",
            "severity": "info",
            "detail": f"Title contains 'مختصر' but genre is '{genre}'",
        })

    # 5. Muhaqiq in prompt but absent from scholarly_context
    sc = result_data.get("scholarly_context") or {}
    fields_present = prompt_sent.get("metadata_fields_present", [])
    if "muhaqiq_name_raw" in fields_present and not sc.get("muhaqiq_reputation"):
        flags.append({
            "check": "muhaqiq_not_in_context",
            "severity": "info",
            "detail": "Muhaqiq was in extraction but scholarly_context.muhaqiq_reputation is null",
        })

    # 6. High confidence on sparse data
    text_len = prompt_sent.get("text_sample_length", 0)
    conf = result_data.get("confidence_scores", {})
    if isinstance(conf, dict) and text_len < 500 and conf.get("author", 0) > 0.85:
        flags.append({
            "check": "high_confidence_sparse_data",
            "severity": "warning",
            "detail": f"Author confidence {conf.get('author')} with only {text_len} chars of text",
        })

    return {
        "total_flags": len(flags),
        "errors": sum(1 for f in flags if f["severity"] == "error"),
        "warnings": sum(1 for f in flags if f["severity"] == "warning"),
        "info": sum(1 for f in flags if f["severity"] == "info"),
        "flags": flags,
    }


# ── Per-Book Processing ──


async def process_book(
    book_name: str,
    collection_dir: Path,
    output_dir: Path,
    ground_truth: dict[str, dict],
    fixture_mappings: dict[str, str],
) -> dict:
    """Process a single book through the full pipeline. Returns result dict."""
    global _captured_inference

    book_output = output_dir / book_name
    book_output.mkdir(parents=True, exist_ok=True)

    # Resolve actual path: directory or .htm file
    actual_path = _resolve_book_path(collection_dir, book_name)
    if actual_path is None:
        raise FileNotFoundError(f"Book not found: {book_name} in {collection_dir}")

    start_time = time.time()
    book_result: dict[str, Any] = {
        "book": book_name,
        "status": "error",
        "processing_time_seconds": 0,
        "cost_estimate_eur": 0,
    }

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        try:
            # ── PRE-PIPELINE (zero cost) ──

            # 1. Create isolated temp library
            config = create_temp_library(tmp_path)

            # 2. Copy book to staging
            staging_path = config.staging_path / book_name
            if actual_path.is_dir():
                shutil.copytree(actual_path, staging_path)
            else:
                staging_path.mkdir(parents=True, exist_ok=True)
                shutil.copy2(actual_path, staging_path / actual_path.name)

            # 3-4. Extract metadata directly (read-only, zero side effects)
            source_format = detect_format(staging_path)
            extracted = extract_metadata(staging_path, source_format)
            save_json(book_output / "extraction.json", extracted)

            # 5. Build and save prompt context BEFORE any API call
            prompt_context = build_prompt_context(extracted)
            text_sample = extracted.get("text_sample", "")[:2000]

            fields_present = [f for f in METADATA_FIELDS_CHECK if extracted.get(f)]
            fields_absent = [f for f in METADATA_FIELDS_CHECK if not extracted.get(f)]

            prompt_sent = {
                "system_message": SYSTEM_MESSAGE,
                "user_message": USER_MESSAGE_TEMPLATE.format(
                    prompt_context=prompt_context, text_sample=text_sample,
                ),
                "prompt_context_raw": prompt_context,
                "text_sample_length": len(text_sample),
                "metadata_fields_present": fields_present,
                "metadata_fields_absent": fields_absent,
            }
            save_json(book_output / "prompt_sent.json", prompt_sent)

            # ── PIPELINE (API calls) ──

            # Reset capture before each book
            _captured_inference = None

            # 6. Run full pipeline
            metadata: SourceMetadata = await acquire_source(staging_path, config)

            # ── POST-PIPELINE ──

            elapsed = time.time() - start_time
            result_data = metadata.model_dump(mode="json")
            result_data["status"] = "success"
            result_data["processing_time_seconds"] = round(elapsed, 2)

            # 7-8. Save per-model responses and consensus
            save_per_model_responses(_captured_inference, book_output / "llm_responses")
            save_consensus_details(_captured_inference, book_output / "consensus.json")

            # 9. Save full result
            save_json(book_output / "result.json", result_data)

            # 10. Ground truth comparison
            fixture_key = fixture_mappings.get(book_name)
            if fixture_key and fixture_key in ground_truth:
                comparison = compare_ground_truth(result_data, ground_truth[fixture_key])
                comparison["book"] = book_name
                comparison["ground_truth_key"] = fixture_key
                save_json(book_output / "ground_truth_comparison.json", comparison)
                book_result["ground_truth_available"] = True
                book_result["ground_truth_match"] = comparison["all_match"]
            else:
                book_result["ground_truth_available"] = False

            # 11. Sanity checks
            sanity = run_sanity_checks(result_data, extracted, prompt_sent)
            sanity["book"] = book_name
            save_json(book_output / "sanity_checks.json", sanity)

            book_result["status"] = "success"
            book_result["processing_time_seconds"] = round(elapsed, 2)
            book_result["cost_estimate_eur"] = round(estimate_book_cost(_captured_inference), 4)

        except SourceEngineError as exc:
            elapsed = time.time() - start_time
            error_code = exc.error.error_code

            if error_code == ErrorCode.LOW_CONFIDENCE:
                # Gate abort — expected for disputed attribution
                book_result["status"] = "gate_abort"
                book_result["error_code"] = error_code.value
                book_result["error_message"] = exc.error.message
                if exc.error.context:
                    book_result["gate_errors"] = exc.error.context.get("gate_errors", [])
                book_result["partial_data"] = {
                    "extraction_completed": True,
                    "inference_completed": _captured_inference is not None,
                    "metadata_assembled": True,
                    "metadata_returned": False,
                }
            else:
                book_result["status"] = "error"
                book_result["error_code"] = error_code.value
                book_result["error_message"] = exc.error.message
                book_result["partial_data"] = {
                    "extraction_completed": (book_output / "extraction.json").exists(),
                    "inference_completed": _captured_inference is not None,
                }

            # Still save LLM responses if captured
            if _captured_inference:
                save_per_model_responses(_captured_inference, book_output / "llm_responses")
                save_consensus_details(_captured_inference, book_output / "consensus.json")

            book_result["processing_time_seconds"] = round(elapsed, 2)
            book_result["cost_estimate_eur"] = round(estimate_book_cost(_captured_inference), 4)

            # Save result.json with error/gate_abort status
            save_json(book_output / "result.json", book_result)

            # Ground truth comparison for gate_abort books (LLM data is available)
            if error_code == ErrorCode.LOW_CONFIDENCE and _captured_inference:
                fixture_key = fixture_mappings.get(book_name)
                if fixture_key and fixture_key in ground_truth:
                    canon = getattr(_captured_inference, "canonical_output", None)
                    if canon:
                        author_id = getattr(canon, "author_identification", None)
                        pseudo_result = {
                            "genre": getattr(canon, "genre", ""),
                            "author": {
                                "name_arabic": author_id.canonical_name_ar if author_id else "",
                            },
                            "is_multi_layer": getattr(canon, "is_multi_layer", None),
                            "science_scope": getattr(canon, "science_scope", []),
                            "structural_format": getattr(canon, "structural_format", ""),
                            "authority_level": getattr(canon, "authority_level", ""),
                            "level": getattr(canon, "level", None),
                            "attribution_status": getattr(canon, "attribution_status", ""),
                        }
                        comparison = compare_ground_truth(pseudo_result, ground_truth[fixture_key])
                        comparison["book"] = book_name
                        comparison["ground_truth_key"] = fixture_key
                        comparison["from_gate_abort"] = True
                        save_json(book_output / "ground_truth_comparison.json", comparison)
                        book_result["ground_truth_available"] = True
                        book_result["ground_truth_match"] = comparison["all_match"]

            # Still run sanity checks on extraction if available
            extraction_path = book_output / "extraction.json"
            prompt_path = book_output / "prompt_sent.json"
            if extraction_path.exists() and prompt_path.exists():
                ext = json.loads(extraction_path.read_text(encoding="utf-8"))
                ps = json.loads(prompt_path.read_text(encoding="utf-8"))
                sanity = run_sanity_checks(book_result, ext, ps)
                sanity["book"] = book_name
                save_json(book_output / "sanity_checks.json", sanity)

        except Exception as exc:
            elapsed = time.time() - start_time
            book_result["status"] = "error"
            book_result["error_message"] = str(exc)
            book_result["traceback"] = traceback.format_exc()
            book_result["processing_time_seconds"] = round(elapsed, 2)
            book_result["partial_data"] = {
                "extraction_completed": (book_output / "extraction.json").exists(),
                "inference_completed": _captured_inference is not None,
            }
            save_json(book_output / "result.json", book_result)

    return book_result


# ── Edition Groups ──


def _load_llm_genre_author(output_dir: Path, book_name: str) -> tuple[str, str]:
    """Load genre and author from LLM responses for gate_abort books."""
    llm_dir = output_dir / book_name / "llm_responses"
    if not llm_dir.exists():
        return "", ""
    for f in llm_dir.iterdir():
        if f.suffix == ".json":
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                parsed = data.get("parsed")
                if parsed:
                    genre = parsed.get("genre", "")
                    author_id = parsed.get("author_identification", {})
                    author_name = author_id.get("canonical_name_ar", "") if isinstance(author_id, dict) else ""
                    return genre, author_name
            except (json.JSONDecodeError, KeyError):
                continue
    return "", ""


def compute_edition_groups(
    all_results: dict[str, dict],
    output_dir: Optional[Path] = None,
) -> list[dict]:
    """Group results by normalized title similarity. Compare across editions.

    Includes both success and gate_abort books — gate_abort books have LLM
    responses saved (inference completed before validation aborted).
    """
    # Known edition groups — exact directory names from collection
    known_groups = {
        "إعلام الموقعين": [
            "أعلام الموقعين عن رب العالمين - ط عطاءات العلم",
            "إعلام الموقعين عن رب العالمين - ط العلمية",
            "إعلام الموقعين عن رب العالمين - ت مشهور",
        ],
        "البداية والنهاية": [
            "البداية والنهاية - ت التركي",
            "البداية والنهاية - ط السعادة",
        ],
        "شرح العقيدة الطحاوية": [
            "شرح العقيدة الطحاوية - ط الرسالة",
            "شرح العقيدة الطحاوية - ط الأوقاف السعودية - بتعليقات أحمد شاكر",
        ],
        "تفسير الطبري": [
            "تفسير الطبري جامع البيان - ت التركي",
            "تفسير الطبري جامع البيان - ط دار التربية والتراث",
        ],
        "حاشية ابن عابدين": [
            "حاشية ابن عابدين = رد المحتار - ط الحلبي",
            "تكملة حاشية ابن عابدين = قرة عيون الأخيار تكملة رد المحتار - ط الفكر",
        ],
        "تحفة المودود": [
            "تحفة المودود بأحكام المولود - ت الأرنؤوط",
            "تحفة المودود بأحكام المولود - ط عطاءات العلم",
        ],
        "الإبانة": [
            "الإبانة عن أصول الديانة - ت العصيمي",
            "الإبانة عن أصول الديانة - ت فوقية",
        ],
        "فتاوى اللجنة الدائمة": [
            "فتاوى اللجنة الدائمة - المجموعة الأولى",
            "فتاوى اللجنة الدائمة - المجموعة الثانية",
        ],
        "ألفية ابن مالك": [
            "ألفية ابن مالك - ت القاسم",
            "ألفية ابن مالك - ط التعاون",
        ],
    }

    groups: list[dict] = []
    for work_short, editions in known_groups.items():
        present = [
            e for e in editions
            if e in all_results and all_results[e].get("status") in ("success", "gate_abort")
        ]
        if len(present) < 2:
            continue

        genres: set[str] = set()
        authors: set[str] = set()
        multi_layers: set[Optional[bool]] = set()
        for e in present:
            r = all_results[e]
            if r.get("status") == "success":
                genres.add(r.get("genre", ""))
                author = r.get("author", {})
                if isinstance(author, dict):
                    authors.add(author.get("name_arabic", ""))
                multi_layers.add(r.get("is_multi_layer", None))
            elif r.get("status") == "gate_abort" and output_dir:
                genre, author_name = _load_llm_genre_author(output_dir, e)
                if genre:
                    genres.add(genre)
                if author_name:
                    authors.add(author_name)

        group = {
            "work_short": work_short,
            "editions": present,
            "genre_consistent": len(genres) <= 1,
            "author_consistent": len(authors) <= 1,
            "is_multi_layer_consistent": len(multi_layers) <= 1,
            "genres_found": sorted(g for g in genres if g),
            "authors_found": sorted(a for a in authors if a),
        }
        groups.append(group)

    return groups


# ── Summary Generation ──


def generate_summary(
    all_results: dict[str, dict],
    edition_groups: list[dict],
    git_hash: str,
    total_cost: float,
) -> dict:
    statuses = [r.get("status", "error") for r in all_results.values()]

    # Field coverage
    field_coverage: dict[str, dict] = {}
    for field in ["genre", "author", "is_multi_layer"]:
        present = 0
        high_conf = 0
        for r in all_results.values():
            if r.get("status") != "success":
                continue
            if field == "author":
                author = r.get("author", {})
                if isinstance(author, dict) and author.get("name_arabic"):
                    present += 1
                conf = r.get("confidence_scores", {})
                if isinstance(conf, dict) and conf.get("author", 0) >= 0.80:
                    high_conf += 1
            else:
                if r.get(field) is not None:
                    present += 1
                conf = r.get("confidence_scores", {})
                if isinstance(conf, dict) and conf.get(field, 0) >= 0.80:
                    high_conf += 1
        field_coverage[field] = {"present": present, "high_confidence": high_conf}

    # Ground truth results
    gt_results: dict[str, int] = {}
    for r in all_results.values():
        gt_path = Path(r.get("_output_dir", "")) / "ground_truth_comparison.json" if "_output_dir" in r else None
        # We'll compute from result data instead
    gt_total = sum(1 for r in all_results.values() if r.get("ground_truth_available"))

    # Sanity check summary
    total_flags = 0
    by_severity: dict[str, int] = {"error": 0, "warning": 0, "info": 0}
    by_check: dict[str, int] = {}
    clean_books = 0
    for r in all_results.values():
        sc = r.get("_sanity_checks", {})
        if isinstance(sc, dict):
            total_flags += sc.get("total_flags", 0)
            if sc.get("total_flags", 0) == 0:
                clean_books += 1
            for f in sc.get("flags", []):
                by_severity[f.get("severity", "info")] = by_severity.get(f.get("severity", "info"), 0) + 1
                by_check[f["check"]] = by_check.get(f["check"], 0) + 1

    return {
        "phase": "C",
        "pipeline_version": git_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_books": len(all_results),
        "successful": statuses.count("success"),
        "gate_abort": statuses.count("gate_abort"),
        "failed": statuses.count("error"),
        "total_cost_eur": round(total_cost, 2),
        "avg_cost_per_book_eur": round(total_cost / max(len(all_results), 1), 4),
        "avg_processing_time_seconds": round(
            sum(r.get("processing_time_seconds", 0) for r in all_results.values()) / max(len(all_results), 1), 1
        ),
        "field_coverage": field_coverage,
        "ground_truth_results": {"total_compared": gt_total},
        "edition_groups": edition_groups,
        "sanity_check_summary": {
            "total_flags": total_flags,
            "by_severity": by_severity,
            "by_check": by_check,
            "clean_books": clean_books,
        },
        "errors": [
            {"book": r["book"], "error_code": r.get("error_code", ""), "message": r.get("error_message", "")}
            for r in all_results.values()
            if r.get("status") == "error"
        ],
    }


def generate_manifest(all_results: dict[str, dict], git_hash: str, output_dir: Path) -> dict:
    books: dict[str, dict] = {}
    for name, r in all_results.items():
        books[name] = {
            "status": r.get("status", "error"),
            "needs_rerun": r.get("status") == "error",
            "result_path": f"phase_c/{name}/result.json",
            "ground_truth_available": r.get("ground_truth_available", False),
            "ground_truth_match": r.get("ground_truth_match", None),
            "cost_estimate_eur": r.get("cost_estimate_eur", 0),
            "processing_time_seconds": r.get("processing_time_seconds", 0),
        }
    return {
        "phase": "C",
        "pipeline_version": git_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_books": len(all_results),
        "books": books,
    }


# ── Main ──


async def main() -> None:
    args = parse_args()
    check_env()

    # Build book list
    book_names: list[str] = []
    if args.books:
        book_names = load_books(args.books)
    if args.book:
        book_names.extend(args.book)
    if not book_names:
        print("ERROR: Provide --books FILE or --book NAME")
        sys.exit(1)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_books: list[str] = []
    for name in book_names:
        if name not in seen:
            seen.add(name)
            unique_books.append(name)
    book_names = unique_books

    validate_books(args.collection_dir, book_names)
    ground_truth, fixture_mappings = load_ground_truth()
    git_hash = get_git_commit_hash()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Phase C: {len(book_names)} books from {args.collection_dir}")
    print(f"Output: {args.output_dir}")
    print(f"Budget ceiling: {args.budget_eur:.2f} EUR")

    if args.dry_run:
        cost_log = load_cost_log()
        already_spent = cost_log.get("total_eur", 0)
        estimated = len(book_names) * DEFAULT_COST_PER_BOOK
        print(f"\nDry run validation:")
        print(f"  Books: {len(book_names)}")
        print(f"  Already spent: {already_spent:.2f} EUR")
        print(f"  Estimated cost: {estimated:.2f} EUR")
        print(f"  Projected total: {already_spent + estimated:.2f} EUR")
        print(f"  Budget: {args.budget_eur:.2f} EUR")
        gt_count = sum(1 for b in book_names if b in fixture_mappings)
        print(f"  Books with ground truth: {gt_count}")
        print(f"\nAll directories found. Environment OK.")
        return

    # Pre-flight budget check
    cost_log = load_cost_log()
    already_spent = cost_log.get("total_eur", 0)
    estimated = len(book_names) * DEFAULT_COST_PER_BOOK
    if estimated + already_spent > args.budget_eur:
        max_books = int((args.budget_eur - already_spent) / DEFAULT_COST_PER_BOOK)
        print(f"ERROR: Estimated cost {estimated + already_spent:.2f} EUR exceeds budget {args.budget_eur:.2f} EUR")
        print(f"  Can process at most {max_books} books within budget")
        sys.exit(1)

    # Process books
    all_results: dict[str, dict] = {}
    running_cost = 0.0
    consecutive_api_failures = 0
    first_book_done = False

    for i, book_name in enumerate(book_names, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(book_names)}] {book_name}")

        # Resume check
        result_path = args.output_dir / book_name / "result.json"
        if args.resume and not args.force and result_path.exists():
            try:
                existing = json.loads(result_path.read_text(encoding="utf-8"))
                status = existing.get("status", "")
                if status in ("success", "gate_abort"):
                    print(f"  Skipping (status: {status})")
                    all_results[book_name] = existing
                    continue
                print(f"  Re-processing (status: {status})")
            except (json.JSONDecodeError, KeyError):
                print("  Re-processing (invalid existing result)")

        # Process
        result = await process_book(
            book_name, args.collection_dir, args.output_dir,
            ground_truth, fixture_mappings,
        )
        all_results[book_name] = result

        # Read back sanity checks for summary
        sanity_path = args.output_dir / book_name / "sanity_checks.json"
        if sanity_path.exists():
            result["_sanity_checks"] = json.loads(sanity_path.read_text(encoding="utf-8"))

        status = result.get("status", "error")
        cost = result.get("cost_estimate_eur", 0)
        elapsed = result.get("processing_time_seconds", 0)
        running_cost += cost

        print(f"  Status: {status} | Cost: {cost:.4f} EUR | Time: {elapsed:.1f}s")
        if result.get("ground_truth_available"):
            match = "PASS" if result.get("ground_truth_match") else "FAIL"
            print(f"  Ground truth: {match}")

        # Update cost log after each book
        cost_log["phases"]["C"]["books"] = sum(
            1 for r in all_results.values() if r.get("status") in ("success", "gate_abort")
        )
        cost_log["phases"]["C"]["cost_eur"] = round(running_cost, 2)
        cost_log["phases"]["C"]["status"] = "in_progress"
        cost_log["total_eur"] = round(already_spent + running_cost, 2)
        save_cost_log(cost_log)

        # API failure tracking
        is_api_error = (
            status == "error"
            and "api" in result.get("error_message", "").lower()
            or "timeout" in result.get("error_message", "").lower()
            or "connection" in result.get("error_message", "").lower()
        )

        if is_api_error:
            if not first_book_done:
                print("\nABORT: First book failed with API error. Check API keys.")
                break
            consecutive_api_failures += 1
            if consecutive_api_failures >= 3:
                print("\nPAUSE: 3 consecutive API failures. Saving progress.")
                break
        else:
            if status in ("success", "gate_abort"):
                first_book_done = True
            consecutive_api_failures = 0

        # Rolling budget check every 5 books
        if i % 5 == 0 and first_book_done:
            books_done = sum(1 for r in all_results.values() if r.get("status") in ("success", "gate_abort"))
            if books_done > 0:
                projected = (running_cost / books_done) * len(book_names)
                if projected > args.budget_eur * 1.2:
                    print(f"\n  WARNING: Projected cost {projected:.2f} EUR exceeds budget by >20%")
                    print(f"  Running: {running_cost:.2f} EUR for {books_done} books")

        # Hard ceiling
        if running_cost > args.budget_eur:
            print(f"\nHARD CEILING: Running cost {running_cost:.2f} EUR exceeds budget {args.budget_eur:.2f} EUR")
            break

    # Final updates
    cost_log["phases"]["C"]["status"] = "complete"
    cost_log["phases"]["C"]["books"] = sum(
        1 for r in all_results.values() if r.get("status") in ("success", "gate_abort")
    )
    cost_log["phases"]["C"]["cost_eur"] = round(running_cost, 2)
    cost_log["total_eur"] = round(already_spent + running_cost, 2)
    save_cost_log(cost_log)

    # Generate manifest and summary
    edition_groups = compute_edition_groups(all_results, output_dir=args.output_dir)
    manifest = generate_manifest(all_results, git_hash, args.output_dir)
    save_json(args.output_dir / "PHASE_C_MANIFEST.json", manifest)

    summary = generate_summary(all_results, edition_groups, git_hash, running_cost)
    save_json(args.output_dir / "PHASE_C_SUMMARY.json", summary)

    # Final report
    print(f"\n{'='*60}")
    print(f"PHASE C COMPLETE")
    print(f"  Total: {len(all_results)} books")
    print(f"  Success: {summary['successful']}")
    print(f"  Gate abort: {summary['gate_abort']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Total cost: {running_cost:.2f} EUR")
    print(f"  Results: {args.output_dir}")


if __name__ == "__main__":
    asyncio.run(main())
