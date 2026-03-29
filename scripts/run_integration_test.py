"""Standalone CLI integration test runner for the excerpting engine.

Loads a NormalizedPackage from disk, runs all excerpting phases, and saves
every intermediate artifact plus raw LLM request/response logs. Designed for
the LLM integration test protocol — NOT a pytest test.

Usage:
    python scripts/run_integration_test.py --package-path path/to/pkg/
    python scripts/run_integration_test.py --package-path path/to/pkg/ --mock
    python scripts/run_integration_test.py --package-path path/to/pkg/ \
        --source-metadata '{"author_name":"ابن قدامة","work_title":"المغني",...}'
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

# Ensure stdout/stderr can handle Arabic text on Windows (cp1252 default)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is on sys.path so local imports work without PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if TYPE_CHECKING:
    import instructor

    from engines.normalization.contracts import NormalizedPackage

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("integration_test")

# ---------------------------------------------------------------------------
# Client creation
# ---------------------------------------------------------------------------


def create_client(timeout: int = 120) -> instructor.Instructor:
    """Create an Instructor client via OpenRouter (mode=JSON)."""
    import instructor
    import openai

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    return instructor.from_openai(
        openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=timeout,
        ),
        mode=instructor.Mode.JSON,
    )


def create_cli_client() -> Any:
    """Create a CLI adapter client (SPEC §9.1)."""
    from shared.llm.cli_adapter import CLIInstructorAdapter

    return CLIInstructorAdapter()


# ---------------------------------------------------------------------------
# Instructor hook-based logging
# ---------------------------------------------------------------------------


def make_hook_logger(output_dir: Path, client_name: str) -> tuple[
    Callable[..., None],
    Callable[..., None],
    Callable[..., None],
]:
    """Create logging hooks for an Instructor client.

    Returns (on_request, on_response, on_error) callables suitable for
    ``client.on("completion:kwargs", ...)``, etc.
    """
    req_dir = output_dir / "raw_llm_requests"
    resp_dir = output_dir / "raw_llm_responses"
    req_dir.mkdir(parents=True, exist_ok=True)
    resp_dir.mkdir(parents=True, exist_ok=True)

    call_counter: dict[str, int] = {"n": 0}
    call_start_time: dict[str, float] = {"t": 0.0}

    def on_request(**kwargs: Any) -> None:
        call_counter["n"] += 1
        call_start_time["t"] = time.monotonic()
        call_id = f"{client_name}_{call_counter['n']:04d}"
        entry: dict[str, Any] = {
            "call_id": call_id,
            "model": kwargs.get("model"),
            "temperature": kwargs.get("temperature"),
            "max_tokens": kwargs.get("max_tokens"),
            "messages": [
                {
                    "role": m.get("role", ""),
                    "content": m.get("content", "")[:2000],
                }
                for m in kwargs.get("messages", [])
            ],
        }
        path = req_dir / f"{call_id}.json"
        path.write_text(
            json.dumps(entry, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def on_response(response: Any) -> None:
        call_id = f"{client_name}_{call_counter['n']:04d}"
        latency = time.monotonic() - call_start_time["t"]
        usage_dict: Optional[dict[str, Any]] = None
        if hasattr(response, "usage") and response.usage is not None:
            usage_dict = response.usage.model_dump()

        finish_reason: Optional[str] = None
        raw_content: Optional[str] = None
        if (
            hasattr(response, "choices")
            and response.choices
            and len(response.choices) > 0
        ):
            finish_reason = response.choices[0].finish_reason
            if hasattr(response.choices[0], "message"):
                raw_content = (
                    response.choices[0].message.content[:50000]
                    if response.choices[0].message.content
                    else None
                )

        entry: dict[str, Any] = {
            "call_id": call_id,
            "latency_seconds": round(latency, 2),
            "model": getattr(response, "model", None),
            "usage": usage_dict,
            "finish_reason": finish_reason,
            "raw_content": raw_content,
        }
        path = resp_dir / f"{call_id}.json"
        path.write_text(
            json.dumps(entry, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def on_error(error: Exception) -> None:
        call_id = f"{client_name}_{call_counter['n']:04d}"
        entry: dict[str, Any] = {
            "call_id": call_id,
            "error_type": type(error).__name__,
            "error": str(error)[:500],
        }
        path = resp_dir / f"{call_id}_error.json"
        path.write_text(
            json.dumps(entry, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return on_request, on_response, on_error


# ---------------------------------------------------------------------------
# Package loading
# ---------------------------------------------------------------------------


def load_package(package_path: Path) -> NormalizedPackage:
    """Load a NormalizedPackage from manifest.json + content.jsonl on disk."""
    from engines.normalization.contracts import (
        ContentUnit,
        NormalizedManifest,
        NormalizedPackage,
    )

    manifest_path = package_path / "manifest.json"
    content_path = package_path / "content.jsonl"

    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.json not found in {package_path}")
    if not content_path.exists():
        raise FileNotFoundError(f"content.jsonl not found in {package_path}")

    manifest = NormalizedManifest.model_validate_json(
        manifest_path.read_text(encoding="utf-8")
    )

    units: list[ContentUnit] = []
    with open(content_path, encoding="utf-8") as fh:
        for line_num, line in enumerate(fh, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                units.append(ContentUnit.model_validate_json(stripped))
            except Exception as exc:
                raise ValueError(
                    f"Failed to parse content unit at line {line_num} "
                    f"in {content_path}: {exc}"
                ) from exc

    return NormalizedPackage(manifest=manifest, content_units=units)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def get_git_info() -> dict[str, Any]:
    """Return git commit hash and dirty status."""
    info: dict[str, Any] = {
        "commit_hash": None,
        "dirty": None,
    }
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            info["commit_hash"] = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            info["dirty"] = len(result.stdout.strip()) > 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return info


# ---------------------------------------------------------------------------
# API key validation
# ---------------------------------------------------------------------------


def validate_api_key() -> bool:
    """Test OpenRouter API key with a minimal 10-token call."""
    import openai

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        return False

    try:
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=30,
        )
        response = client.chat.completions.create(
            model="anthropic/claude-sonnet-4",
            messages=[{"role": "user", "content": "Say OK."}],
            max_tokens=10,
        )
        logger.info(
            "API key validated (model: %s)",
            getattr(response, "model", "unknown"),
        )
        return True
    except Exception as exc:
        logger.error("API key validation failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Mock client factory
# ---------------------------------------------------------------------------


def create_mock_clients() -> tuple[Any, Any, Any]:
    """Create MagicMock clients that return plausible Instructor responses.

    The mocks produce structurally valid (but content-empty) results so that
    the file-writing infrastructure is fully exercised.
    """
    from unittest.mock import MagicMock

    enrich_client = MagicMock(name="mock_enrich_client")
    verify_client = MagicMock(name="mock_verify_client")
    escalation_client = MagicMock(name="mock_escalation_client")

    return enrich_client, verify_client, escalation_client


# ---------------------------------------------------------------------------
# Pre-run checklist
# ---------------------------------------------------------------------------


def run_pre_checks(
    package_path: Path,
    output_dir: Path,
    mock: bool,
    backend: str = "api",
) -> bool:
    """Run automated pre-run checks. Returns True if all pass."""
    all_ok = True

    # 1. Validate normalized package loads
    print("\n=== Pre-run Checklist ===")
    try:
        pkg = load_package(package_path)
        unit_count = len(pkg.content_units)
        print(
            f"  [PASS] Package loaded: source_id={pkg.manifest.source_id}, "
            f"units={unit_count}"
        )
    except Exception as exc:
        print(f"  [FAIL] Package load failed: {exc}")
        return False

    # 2. Test API key (skip in mock and CLI mode)
    if mock:
        print("  [SKIP] API key validation (mock mode)")
    elif backend == "cli":
        print("  [SKIP] API key validation (CLI backend)")
    else:
        if validate_api_key():
            print("  [PASS] API key validated")
        else:
            print("  [FAIL] API key validation failed")
            all_ok = False

    # 3. Verify output directory
    if output_dir.exists():
        contents = list(output_dir.iterdir())
        if contents:
            print(
                f"  [WARN] Output directory exists and is not empty: "
                f"{output_dir} ({len(contents)} items)"
            )
        else:
            print(f"  [PASS] Output directory exists and is empty")
    else:
        print(f"  [PASS] Output directory does not exist (will be created)")

    # 4. Git info
    git_info = get_git_info()
    commit = git_info.get("commit_hash", "unknown")
    dirty = git_info.get("dirty")
    short_hash = commit[:10] if commit else "unknown"
    print(f"  [INFO] Git commit: {short_hash}")
    if dirty:
        print("  [WARN] Uncommitted changes detected")
    elif dirty is False:
        print("  [PASS] Working tree clean")
    else:
        print("  [WARN] Could not determine git status")

    print()
    return all_ok


# ---------------------------------------------------------------------------
# JSON serialization helpers
# ---------------------------------------------------------------------------


def _serialize_chunks(chunks: list[Any], output_dir: Path) -> None:
    """Save Phase 1 chunks to phase1_chunks.json."""
    path = output_dir / "phase1_chunks.json"
    data = [c.model_dump(mode="json") for c in chunks]
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Saved %d chunks to %s", len(data), path)


def _serialize_classifications(
    classified: dict[str, list[Any]], output_dir: Path
) -> None:
    """Save Phase 2a classifications, one file per chunk."""
    cls_dir = output_dir / "phase2a_classifications"
    cls_dir.mkdir(parents=True, exist_ok=True)
    for chunk_id, segments in classified.items():
        path = cls_dir / f"chunk_{chunk_id}.json"
        data = [s.model_dump(mode="json") for s in segments]
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    logger.info(
        "Saved classifications for %d chunks to %s",
        len(classified),
        cls_dir,
    )


def _serialize_groupings(grouped: dict[str, list[Any]], output_dir: Path) -> None:
    """Save Phase 2b groupings, one file per chunk."""
    grp_dir = output_dir / "phase2b_groupings"
    grp_dir.mkdir(parents=True, exist_ok=True)
    for chunk_id, units in grouped.items():
        path = grp_dir / f"chunk_{chunk_id}.json"
        data = [u.model_dump(mode="json") for u in units]
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    logger.info(
        "Saved groupings for %d chunks to %s",
        len(grouped),
        grp_dir,
    )


# ---------------------------------------------------------------------------
# Main pipeline execution
# ---------------------------------------------------------------------------


def run_pipeline(
    package_path: Path,
    output_dir: Path,
    source_metadata: Optional[dict[str, str]],
    mock: bool,
    max_chunks: Optional[int] = None,
    backend: str = "api",
    traces_dir: Optional[Path] = None,
) -> int:
    """Execute the full excerpting pipeline and save all artifacts.

    When *traces_dir* is provided, captures all LLM call traces via
    recursive-improve for later analysis and improvement.

    Returns 0 on success, 1 on failure.
    """
    from engines.excerpting.contracts import ExcerptingConfig
    from engines.excerpting.src.phase1_assembly import run_phase1
    from engines.excerpting.src.phase2_classify import run_phase2a
    from engines.excerpting.src.phase2_group import run_phase2b
    from engines.excerpting.src.phase3_orchestrator import run_phase3
    from engines.excerpting.src.writer import (
        write_excerpts,
        write_gate_queue,
        write_processing_log,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    config = ExcerptingConfig()
    timings: dict[str, Any] = {}
    all_errors: list[str] = []

    # ── Optional trace capture via recursive-improve ──────────────
    ri_session = None
    if traces_dir and not mock:
        try:
            import recursive_improve as ri

            ri.patch()  # captures SDK-based calls (OpenRouter/Instructor)
            ri_session = ri.session(
                traces_dir=str(traces_dir),
                metadata={
                    "engine": "excerpting",
                    "backend": backend,
                    "package": str(package_path),
                },
            )
            ri_session.__enter__()
            logger.info("Traces enabled: %s", traces_dir)
        except ImportError:
            logger.warning("recursive-improve not installed, traces disabled")

    # ── Load package ──────────────────────────────────────────────
    t0 = time.monotonic()
    try:
        package = load_package(package_path)
    except Exception as exc:
        logger.error("Failed to load package: %s", exc)
        return 1
    timings["load_package"] = round(time.monotonic() - t0, 3)
    logger.info(
        "Loaded package: source_id=%s, units=%d",
        package.manifest.source_id,
        len(package.content_units),
    )

    # ── Config override for CLI backend (SPEC §9.3) ────────────────
    if backend == "cli":
        config = config.model_copy(
            update={"ESCALATION_MODEL": "google/gemini-2.5-pro"}
        )

    # ── Create clients ────────────────────────────────────────────
    if mock:
        logger.info("Mock mode: using MagicMock clients")
        enrich_client, verify_client, escalation_client = create_mock_clients()
    elif backend == "cli":
        logger.info("Creating CLI adapter clients")
        enrich_client = create_cli_client()
        verify_client = create_cli_client()
        escalation_client = create_cli_client()

        # Register logging hooks on each client
        for client, name in [
            (enrich_client, "enrich"),
            (verify_client, "verify"),
            (escalation_client, "escalation"),
        ]:
            req_hook, resp_hook, err_hook = make_hook_logger(output_dir, name)
            client.on("completion:kwargs", req_hook)
            client.on("completion:response", resp_hook)
            client.on("completion:error", err_hook)

        # Attach ri trace bridge to CLI clients (captures subprocess calls)
        if ri_session is not None:
            from shared.llm.ri_trace_bridge import attach as ri_attach

            for client in (enrich_client, verify_client, escalation_client):
                ri_attach(client, ri_session)
    else:
        logger.info("Creating OpenRouter Instructor clients")
        enrich_client = create_client(timeout=config.TIMEOUT_SECONDS)
        verify_client = create_client(timeout=config.TIMEOUT_SECONDS)
        escalation_client = create_client(timeout=config.TIMEOUT_SECONDS)

        # Register logging hooks on each client
        for client, name in [
            (enrich_client, "enrich"),
            (verify_client, "verify"),
            (escalation_client, "escalation"),
        ]:
            req_hook, resp_hook, err_hook = make_hook_logger(output_dir, name)
            client.on("completion:kwargs", req_hook)
            client.on("completion:response", resp_hook)
            client.on("completion:error", err_hook)

    # ── Phase 1: Deterministic assembly ───────────────────────────
    logger.info("=== Phase 1: Deterministic assembly ===")
    t0 = time.monotonic()
    try:
        chunks, _validation_results = run_phase1(package, config)
    except Exception as exc:
        if mock:
            logger.warning(
                "Phase 1 validation failed in mock mode — generating "
                "synthetic chunks for infrastructure testing: %s", exc,
            )
            all_errors.append(f"phase1_validation: {exc}")
            # Generate synthetic chunks so mock mode exercises Phases 2-3
            from engines.excerpting.contracts import (
                AssembledChunk,
                AssemblyMetadata,
            )
            from engines.normalization.contracts import (
                ContentFlags,
                LayerType,
                PhysicalPage,
                StructuralFormat,
                TextLayerSegment,
            )
            chunks = []
            for i, unit in enumerate(package.content_units[:5]):
                text = unit.primary_text
                words = text.split()
                chunk = AssembledChunk(
                    chunk_id=f"synthetic_{i}",
                    source_id=package.manifest.source_id,
                    div_id=f"div_synthetic_{i}",
                    div_path=["synthetic"],
                    assembled_text=text,
                    total_tokens=len(words),
                    word_count=len(words),
                    text_layers=[
                        TextLayerSegment(
                            layer_type=LayerType.MATN,
                            author_canonical_id=None,
                            start=0,
                            end=len(text),
                            confidence=1.0,
                        )
                    ],
                    content_flags=ContentFlags(),
                    physical_pages=[
                        PhysicalPage(
                            volume=1,
                            page_number_display=str(i + 1),
                            page_number_int=i + 1,
                        )
                    ],
                    structural_format=StructuralFormat.PROSE,
                    heading_alignment_ok=True,
                    assembly_metadata=AssemblyMetadata(
                        constituent_unit_indices=[i],
                        join_points=[],
                        layer_split_points=[],
                        footnote_renumber_map=None,
                    ),
                    merge_history=None,
                    split_info=None,
                )
                chunks.append(chunk)
            logger.info("Generated %d synthetic chunks for mock mode", len(chunks))
        else:
            logger.error("Phase 1 failed: %s", exc)
            all_errors.append(f"phase1_fatal: {exc}")
            _save_timing_and_metadata(
                output_dir, timings, all_errors, config, source_metadata
            )
            return 1
    timings["phase1"] = round(time.monotonic() - t0, 3)
    logger.info("Phase 1 produced %d chunks", len(chunks))
    _serialize_chunks(chunks, output_dir)

    # Truncate chunk list for LLM phases if --max-chunks is set.
    # Phase 1 artifacts (phase1_chunks.json) already serialized above with ALL chunks.
    if max_chunks is not None:
        original_count = len(chunks)
        chunks = chunks[:max_chunks]
        logger.info(
            "--max-chunks=%d: processing %d of %d chunks in Phases 2-3",
            max_chunks, len(chunks), original_count,
        )

    if not chunks:
        logger.warning("Phase 1 produced 0 chunks — nothing to process")
        # Still write processing log and metadata so output dir is populated
        write_processing_log(
            source_id=package.manifest.source_id,
            errors=all_errors,
            timings=timings,
            excerpt_count=0,
            gate_count=0,
            output_dir=output_dir,
        )
        _save_timing_and_metadata(
            output_dir, timings, all_errors, config, source_metadata
        )
        return 0

    # ── Phase 2a: Classification ──────────────────────────────────
    logger.info("=== Phase 2a: Classification ===")
    chunk_timings_2a: dict[str, float] = {}
    t0 = time.monotonic()
    if mock:
        classified = _mock_phase2a(chunks)
    else:
        try:
            classified = run_phase2a(chunks, enrich_client, config)
        except Exception as exc:
            logger.error("Phase 2a failed: %s", exc)
            all_errors.append(f"phase2a_fatal: {exc}")
            _save_timing_and_metadata(
                output_dir, timings, all_errors, config, source_metadata
            )
            return 1
    timings["phase2a"] = round(time.monotonic() - t0, 3)
    for chunk_id in classified:
        chunk_timings_2a[chunk_id] = timings["phase2a"] / max(len(classified), 1)
    timings["phase2a_per_chunk"] = chunk_timings_2a
    logger.info(
        "Phase 2a classified %d chunks (%d total segments)",
        len(classified),
        sum(len(v) for v in classified.values()),
    )
    _serialize_classifications(classified, output_dir)

    # ── Phase 2b: Grouping ────────────────────────────────────────
    logger.info("=== Phase 2b: Grouping ===")
    chunk_timings_2b: dict[str, float] = {}
    t0 = time.monotonic()
    if mock:
        grouped = _mock_phase2b(chunks, classified)
    else:
        try:
            grouped = run_phase2b(chunks, classified, enrich_client, config)
        except Exception as exc:
            logger.error("Phase 2b failed: %s", exc)
            all_errors.append(f"phase2b_fatal: {exc}")
            _save_timing_and_metadata(
                output_dir, timings, all_errors, config, source_metadata
            )
            return 1
    timings["phase2b"] = round(time.monotonic() - t0, 3)
    for chunk_id in grouped:
        chunk_timings_2b[chunk_id] = timings["phase2b"] / max(len(grouped), 1)
    timings["phase2b_per_chunk"] = chunk_timings_2b
    logger.info(
        "Phase 2b grouped %d chunks (%d total teaching units)",
        len(grouped),
        sum(len(v) for v in grouped.values()),
    )
    _serialize_groupings(grouped, output_dir)

    # ── Phase 3: Enrichment + consensus + validation ──────────────
    logger.info("=== Phase 3: Enrichment + consensus + validation ===")
    t0 = time.monotonic()
    if mock:
        phase3_result = _mock_phase3(
            chunks, grouped, classified, config, source_metadata
        )
    else:
        try:
            phase3_result = run_phase3(
                chunks=chunks,
                teaching_units=grouped,
                classified=classified,
                config=config,
                enrich_client=enrich_client,
                verify_client=verify_client,
                escalation_client=escalation_client,
                source_metadata=source_metadata,
            )
        except Exception as exc:
            logger.error("Phase 3 failed: %s", exc)
            all_errors.append(f"phase3_fatal: {exc}")
            _save_timing_and_metadata(
                output_dir, timings, all_errors, config, source_metadata
            )
            return 1
    timings["phase3"] = round(time.monotonic() - t0, 3)
    all_errors.extend(phase3_result.errors)
    logger.info(
        "Phase 3 produced %d excerpts, %d gate entries",
        len(phase3_result.excerpts),
        len(phase3_result.gate_entries),
    )

    # ── Write output files ────────────────────────────────────────
    logger.info("=== Writing output files ===")
    t0 = time.monotonic()
    if phase3_result.excerpts:
        write_excerpts(phase3_result.excerpts, output_dir)
    if phase3_result.gate_entries:
        write_gate_queue(phase3_result.gate_entries, output_dir)
    write_processing_log(
        source_id=package.manifest.source_id,
        errors=all_errors,
        timings=timings,
        excerpt_count=len(phase3_result.excerpts),
        gate_count=len(phase3_result.gate_entries),
        output_dir=output_dir,
    )
    timings["write_output"] = round(time.monotonic() - t0, 3)

    # ── Save timing + run metadata ────────────────────────────────
    _save_timing_and_metadata(output_dir, timings, all_errors, config, source_metadata)

    # ── Summary ───────────────────────────────────────────────────
    total_time = sum(v for v in timings.values() if isinstance(v, (int, float)))
    print(f"\n=== Integration Test Complete ===")
    print(f"  Output:     {output_dir}")
    print(f"  Chunks:     {len(chunks)}")
    print(f"  Excerpts:   {len(phase3_result.excerpts)}")
    print(f"  Gates:      {len(phase3_result.gate_entries)}")
    print(f"  Errors:     {len(all_errors)}")
    print(f"  Total time: {total_time:.2f}s")
    print()

    # ── Finalize trace session ────────────────────────────────────
    if ri_session is not None:
        ri_session.finish(
            output=f"excerpts={len(phase3_result.excerpts)} "
            f"gates={len(phase3_result.gate_entries)} "
            f"errors={len(all_errors)}",
            success=len(all_errors) == 0,
        )
        ri_session.__exit__(None, None, None)
        logger.info("Traces written to: %s", traces_dir)

    return 0


# ---------------------------------------------------------------------------
# Mock phase implementations
# ---------------------------------------------------------------------------


def _mock_phase2a(
    chunks: list[Any],
) -> dict[str, list[Any]]:
    """Produce mock Phase 2a classifications (one segment per chunk)."""
    from engines.excerpting.contracts import (
        ClassifiedSegment,
        ScholarlyFunction,
    )

    classified: dict[str, list[Any]] = {}
    for chunk in chunks:
        words = chunk.assembled_text.split()
        total_words = len(words)
        seg = ClassifiedSegment(
            segment_index=0,
            start_word=0,
            end_word=max(total_words - 1, 0),
            text_snippet=chunk.assembled_text[:50],
            scholarly_function=ScholarlyFunction.RULE_STATEMENT,
            confidence=0.85,
        )
        classified[chunk.chunk_id] = [seg]
    return classified


def _mock_phase2b(
    chunks: list[Any],
    classified: dict[str, list[Any]],
) -> dict[str, list[Any]]:
    """Produce mock Phase 2b groupings (one teaching unit per chunk)."""
    from engines.excerpting.contracts import (
        ScholarlyFunction,
        SelfContainmentLevel,
        TeachingUnit,
    )

    grouped: dict[str, list[Any]] = {}
    for chunk in chunks:
        segs = classified.get(chunk.chunk_id, [])
        if not segs:
            continue
        words = chunk.assembled_text.split()
        total_words = len(words)
        tu = TeachingUnit(
            unit_index=0,
            segment_indices=[s.segment_index for s in segs],
            start_word=0,
            end_word=max(total_words - 1, 0),
            text_snippet=chunk.assembled_text[:80],
            primary_function=ScholarlyFunction.RULE_STATEMENT,
            secondary_functions=[],
            description_arabic="وحدة تعليمية تجريبية للاختبار",
            self_containment=SelfContainmentLevel.FULL,
            self_containment_notes=None,
        )
        grouped[chunk.chunk_id] = [tu]
    return grouped


def _mock_phase3(
    chunks: list[Any],
    grouped: dict[str, list[Any]],
    classified: dict[str, list[Any]],
    config: Any,
    source_metadata: Optional[dict[str, str]],
) -> Any:
    """Produce mock Phase 3 results with deterministic-only excerpts."""
    from engines.excerpting.src.phase3_orchestrator import run_phase3

    # Run Phase 3 with no LLM clients (deterministic-only mode)
    return run_phase3(
        chunks=chunks,
        teaching_units=grouped,
        classified=classified,
        config=config,
        enrich_client=None,
        verify_client=None,
        escalation_client=None,
        source_metadata=source_metadata,
    )


# ---------------------------------------------------------------------------
# Metadata persistence
# ---------------------------------------------------------------------------


def _save_timing_and_metadata(
    output_dir: Path,
    timings: dict[str, Any],
    errors: list[str],
    config: Any,
    source_metadata: Optional[dict[str, str]],
) -> None:
    """Save timing.json and run_metadata.json to the output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # timing.json
    timing_path = output_dir / "timing.json"
    timing_path.write_text(
        json.dumps(timings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Saved timing to %s", timing_path)

    # run_metadata.json
    git_info = get_git_info()
    metadata: dict[str, Any] = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_commit": git_info.get("commit_hash"),
        "git_dirty": git_info.get("dirty"),
        "config": (
            config.model_dump(mode="json")
            if hasattr(config, "model_dump")
            else str(config)
        ),
        "source_metadata": source_metadata,
        "error_count": len(errors),
        "errors": errors,
        "python_version": sys.version,
    }
    meta_path = output_dir / "run_metadata.json"
    meta_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Saved run metadata to %s", meta_path)


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Excerpting engine LLM integration test runner. "
            "Runs all phases, saves every intermediate artifact."
        ),
    )
    parser.add_argument(
        "--package-path",
        type=Path,
        required=True,
        help="Path to the normalized package directory "
        "(contains manifest.json + content.jsonl)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: integration_tests/run_{timestamp}/)",
    )
    parser.add_argument(
        "--source-metadata",
        type=str,
        default=None,
        help="JSON string with keys: author_name, work_title, "
        "science, source_school",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock clients instead of real LLM calls "
        "(tests file-writing infrastructure)",
    )
    parser.add_argument(
        "--max-chunks",
        type=int,
        default=None,
        help="Limit Phase 2/3 processing to the first N chunks from Phase 1. "
        "Default: None (process all). Useful for smoke-testing LLM calls.",
    )
    parser.add_argument(
        "--backend",
        choices=["cli", "api"],
        default="api",
        help="LLM backend: 'cli' for CLI tools, 'api' for OpenRouter (default: api)",
    )
    parser.add_argument(
        "--traces",
        type=Path,
        default=None,
        help="Directory for recursive-improve traces (enables LLM call tracing)",
    )
    args = parser.parse_args(argv)

    # Default output dir with timestamp
    if args.output_dir is None:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_dir = Path("integration_tests") / f"run_{ts}"

    # Parse source metadata JSON
    if args.source_metadata is not None:
        try:
            parsed = json.loads(args.source_metadata)
            if not isinstance(parsed, dict):
                parser.error("--source-metadata must be a JSON object")
            args.source_metadata = parsed
        except json.JSONDecodeError as exc:
            parser.error(f"--source-metadata is not valid JSON: {exc}")

    return args


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point. Returns exit code."""
    args = parse_args(argv)

    print(f"Package path:    {args.package_path.resolve()}")
    print(f"Output dir:      {args.output_dir.resolve()}")
    print(f"Mock mode:       {args.mock}")
    print(f"Max chunks:      {args.max_chunks or 'all'}")
    print(f"Backend:         {args.backend}")
    print(f"Traces:          {args.traces or 'disabled'}")
    print(
        f"Source metadata: "
        f"{json.dumps(args.source_metadata, ensure_ascii=False) if args.source_metadata else 'None'}"
    )

    # Pre-run checks
    checks_ok = run_pre_checks(
        args.package_path, args.output_dir, args.mock, args.backend
    )
    if not checks_ok:
        print("Pre-run checks failed. Aborting.")
        return 1

    # Run pipeline
    return run_pipeline(
        package_path=args.package_path,
        output_dir=args.output_dir,
        source_metadata=args.source_metadata,
        mock=args.mock,
        max_chunks=args.max_chunks,
        backend=args.backend,
        traces_dir=args.traces,
    )


if __name__ == "__main__":
    sys.exit(main())
