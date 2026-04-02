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
stdout_reconfigure = getattr(sys.stdout, "reconfigure", None)
if callable(stdout_reconfigure):
    stdout_reconfigure(encoding="utf-8", errors="replace")
stderr_reconfigure = getattr(sys.stderr, "reconfigure", None)
if callable(stderr_reconfigure):
    stderr_reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is on sys.path so local imports work without PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if TYPE_CHECKING:
    import instructor  # type: ignore[import-not-found]

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
    import instructor  # type: ignore[import-not-found]
    import openai  # type: ignore[import-not-found]

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
    dict[str, Any],
]:
    """Create logging hooks for an Instructor client.

    Returns (on_request, on_response, on_error, trace_context) where
    trace_context is a mutable dict the caller can update to annotate
    traces with ``semantic_phase`` and ``chunk_id`` metadata.
    """
    req_dir = output_dir / "raw_llm_requests"
    resp_dir = output_dir / "raw_llm_responses"
    req_dir.mkdir(parents=True, exist_ok=True)
    resp_dir.mkdir(parents=True, exist_ok=True)
    last_activity_path = output_dir / "last_llm_activity.json"

    call_counter: dict[str, int] = {"n": 0}
    call_start_time: dict[str, float] = {"t": 0.0}
    trace_context: dict[str, Any] = {
        "semantic_phase": None,
        "chunk_id": None,
    }

    def _write_last_activity(entry: dict[str, Any]) -> None:
        temp = last_activity_path.with_suffix(".json.tmp")
        try:
            temp.write_text(
                json.dumps(entry, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            temp.replace(last_activity_path)
        except OSError as exc:
            logger.warning("Failed to persist last_llm_activity.json: %s", exc)

    def on_request(**kwargs: Any) -> None:
        call_counter["n"] += 1
        call_start_time["t"] = time.monotonic()
        call_id = f"{client_name}_{call_counter['n']:04d}"
        entry: dict[str, Any] = {
            "call_id": call_id,
            "semantic_phase": trace_context.get("semantic_phase"),
            "chunk_id": trace_context.get("chunk_id"),
            "model": kwargs.get("model"),
            "temperature": kwargs.get("temperature"),
            "max_tokens": kwargs.get("max_tokens"),
            "messages": [
                {
                    "role": m.get("role", ""),
                    "content": m.get("content", ""),
                }
                for m in kwargs.get("messages", [])
            ],
        }
        path = req_dir / f"{call_id}.json"
        path.write_text(
            json.dumps(entry, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        _write_last_activity(
            {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "event": "request",
                "call_id": call_id,
                "client_name": client_name,
                "semantic_phase": trace_context.get("semantic_phase"),
                "chunk_id": trace_context.get("chunk_id"),
                "model": kwargs.get("model"),
            }
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
                    response.choices[0].message.content
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
        _write_last_activity(
            {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "event": "response",
                "call_id": call_id,
                "client_name": client_name,
                "semantic_phase": trace_context.get("semantic_phase"),
                "chunk_id": trace_context.get("chunk_id"),
                "model": getattr(response, "model", None),
                "finish_reason": finish_reason,
            }
        )

    def on_error(error: Exception) -> None:
        call_id = f"{client_name}_{call_counter['n']:04d}"
        entry: dict[str, Any] = {
            "call_id": call_id,
            "error_type": type(error).__name__,
            "error": str(error)[:2000],
            "raw_output": str(getattr(error, "raw_output", None) or ""),
            "stdout": str(
                getattr(error, "stdout", None)
                or getattr(error, "output", None)
                or ""
            ),
            "stderr": str(getattr(error, "stderr", None) or ""),
            "exit_code": getattr(
                error, "returncode", getattr(error, "exit_code", None)
            ),
        }
        path = resp_dir / f"{call_id}_error.json"
        path.write_text(
            json.dumps(entry, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        _write_last_activity(
            {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "event": "error",
                "call_id": call_id,
                "client_name": client_name,
                "semantic_phase": trace_context.get("semantic_phase"),
                "chunk_id": trace_context.get("chunk_id"),
                "error_type": type(error).__name__,
                "error": str(error)[:500],
            }
        )

    return on_request, on_response, on_error, trace_context


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
    import openai  # type: ignore[import-not-found]

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


def _provider_name(model_id: str) -> str:
    """Return provider prefix from provider/model ids, fail loudly otherwise."""
    provider, sep, _model = model_id.partition("/")
    if not sep or not provider:
        raise ValueError(
            f"Expected provider/model identifier, got {model_id!r}. "
            "Use OpenRouter-style ids such as 'openai/gpt-5.4'."
        )
    return provider


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


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    """Write a list of dicts as one JSON object per line."""
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


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


def _load_done_artifacts(
    chunks: list[Any],
    progress: Any,
    output_dir: Path,
    phase: str,
) -> dict[str, list[Any]]:
    """Load cached artifacts for chunks marked done by the progress tracker.

    Validates that each artifact file exists, is non-empty, parses as JSON,
    and has the expected structure (list of dicts). If any check fails the
    chunk is NOT included in the result -- the phase runner will re-process it.
    """
    if progress is None:
        return {}

    phase_dirs = {
        "phase2a": "phase2a_classifications",
        "phase2b": "phase2b_groupings",
    }
    artifact_dir_name = phase_dirs.get(phase)
    if artifact_dir_name is None:
        return {}

    from engines.excerpting.contracts import ClassifiedSegment, TeachingUnit

    model_cls = ClassifiedSegment if phase == "phase2a" else TeachingUnit

    loaded: dict[str, list[Any]] = {}
    for chunk in chunks:
        if not progress.is_done(chunk.chunk_id, phase):
            continue
        artifact_path = output_dir / artifact_dir_name / f"chunk_{chunk.chunk_id}.json"
        if not artifact_path.exists():
            logger.warning(
                "Chunk %s %s artifact missing at %s, will re-process",
                chunk.chunk_id,
                phase,
                artifact_path,
            )
            continue
        try:
            raw = artifact_path.read_text(encoding="utf-8")
            if not raw.strip():
                logger.warning(
                    "Chunk %s %s artifact is empty, will re-process",
                    chunk.chunk_id,
                    phase,
                )
                continue
            data = json.loads(raw)
            if not isinstance(data, list) or not data:
                logger.warning(
                    "Chunk %s %s artifact is not a non-empty list, will re-process",
                    chunk.chunk_id,
                    phase,
                )
                continue
            items = [model_cls(**d) for d in data]
            loaded[chunk.chunk_id] = items
        except (json.JSONDecodeError, TypeError, Exception) as exc:
            logger.warning(
                "Chunk %s %s artifact corrupt (%s), will re-process",
                chunk.chunk_id,
                phase,
                exc,
            )
            continue
    return loaded


def _append_error_once(errors: list[str], error: str) -> None:
    """Append a runner error marker only once."""
    if error not in errors:
        errors.append(error)


def _count_llm_call_errors(output_dir: Path) -> int:
    """Count call-level LLM error artifacts already written to disk."""
    resp_dir = output_dir / "raw_llm_responses"
    if not resp_dir.is_dir():
        return 0
    return len(list(resp_dir.glob("*_error.json")))


def _persist_failure_artifacts(
    *,
    output_dir: Path,
    source_id: Optional[str],
    timings: dict[str, Any],
    errors: list[str],
    config: Any,
    source_metadata: Optional[dict[str, str]],
    excerpt_count: int,
    gate_count: int,
) -> None:
    """Persist best-effort runner artifacts without raising on I/O failures."""
    llm_error_count = _count_llm_call_errors(output_dir)
    if llm_error_count > 0:
        _append_error_once(errors, f"llm_call_errors:{llm_error_count}")

    if source_id:
        try:
            from engines.excerpting.src.writer import write_processing_log

            write_processing_log(
                source_id=source_id,
                errors=errors,
                timings=timings,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
                output_dir=output_dir,
            )
        except OSError as exc:
            logger.error("Failed to write processing_log.jsonl: %s", exc)

    try:
        _save_timing_and_metadata(
            output_dir,
            timings,
            errors,
            config,
            source_metadata,
        )
    except OSError as exc:
        logger.error("Failed to write timing/run metadata: %s", exc)


def _finalize_trace_session(
    ri_session: Any,
    *,
    traces_dir: Optional[Path],
    excerpt_count: int,
    gate_count: int,
    error_count: int,
) -> None:
    """Close recursive-improve tracing even on early return or interrupt."""
    if ri_session is None:
        return
    try:
        ri_session.finish(
            output=(
                f"excerpts={excerpt_count} "
                f"gates={gate_count} "
                f"errors={error_count}"
            ),
            success=error_count == 0,
        )
    except Exception as exc:  # pragma: no cover - defensive shutdown path
        logger.warning("Failed to finalize trace session cleanly: %s", exc)
    finally:
        try:
            ri_session.__exit__(None, None, None)
        finally:
            logger.info("Traces written to: %s", traces_dir)


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
    concurrency: int = 1,
) -> int:
    """Execute the full excerpting pipeline and save all artifacts.

    When *traces_dir* is provided, captures all LLM call traces via
    recursive-improve for later analysis and improvement.

    When *concurrency* > 1 and backend is "cli", uses the parallel
    pipeline orchestrator for chunk-level parallelism.

    Returns 0 on success, 1 on failure.
    """
    from engines.excerpting.contracts import ExcerptingConfig
    from engines.excerpting.src.cache import CacheManager
    from engines.excerpting.src.phase1_assembly import run_phase1
    from engines.excerpting.src.phase2_classify import run_phase2a
    from engines.excerpting.src.phase2_group import run_phase2b
    from engines.excerpting.src.phase3_orchestrator import run_phase3
    from engines.excerpting.src.progress import ProgressTracker
    from engines.excerpting.src.writer import (
        GateQueueVerificationError,
        verify_gate_queue,
        write_excerpts,
        write_gate_queue,
        write_processing_log,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    config = (
        ExcerptingConfig(CONCURRENCY=concurrency)
        if concurrency > 1
        else ExcerptingConfig()
    )
    timings: dict[str, Any] = {}
    all_errors: list[str] = []
    source_id: Optional[str] = None
    excerpt_count = 0
    gate_count = 0

    # WAL-based progress tracker for chunk-level resume
    progress = ProgressTracker(output_dir / "progress.jsonl")
    # Input-based LLM result cache
    llm_cache = CacheManager(output_dir / "cache")
    progress_summary = progress.summary()
    if progress_summary["total"] > 0:
        logger.info(
            "Resuming: %d done, %d failed entries from previous run",
            progress_summary["done"],
            progress_summary["failed"],
        )

    def _finalize_traces() -> None:
        _finalize_trace_session(
            ri_session,
            traces_dir=traces_dir,
            excerpt_count=excerpt_count,
            gate_count=gate_count,
            error_count=len(all_errors),
        )

    # ── Optional trace capture via recursive-improve ──────────────
    ri_session = None
    if traces_dir and not mock:
        try:
            import recursive_improve as ri  # type: ignore[import-not-found]

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
    except KeyboardInterrupt:
        _append_error_once(all_errors, "interrupted: KeyboardInterrupt")
        _persist_failure_artifacts(
            output_dir=output_dir,
            source_id=source_id,
            timings=timings,
            errors=all_errors,
            config=config,
            source_metadata=source_metadata,
            excerpt_count=excerpt_count,
            gate_count=gate_count,
        )
        _finalize_traces()
        raise
    except Exception as exc:
        logger.error("Failed to load package: %s", exc)
        _append_error_once(all_errors, f"load_package_fatal: {exc}")
        _persist_failure_artifacts(
            output_dir=output_dir,
            source_id=source_id,
            timings=timings,
            errors=all_errors,
            config=config,
            source_metadata=source_metadata,
            excerpt_count=excerpt_count,
            gate_count=gate_count,
        )
        _finalize_traces()
        return 1
    timings["load_package"] = round(time.monotonic() - t0, 3)
    source_id = package.manifest.source_id
    logger.info(
        "Loaded package: source_id=%s, units=%d",
        source_id,
        len(package.content_units),
    )

    # ── Config override for CLI backend (SPEC §9.3) ────────────────
    if backend == "cli":
        config = config.model_copy(
            update={"ESCALATION_MODEL": "google/gemini-2.5-pro"}
        )

    # ── Environment variable model overrides (for comparison tests) ──
    model_override = os.environ.get("KR_PRIMARY_MODEL")
    if model_override:
        config = config.model_copy(
            update={
                "CLASSIFY_MODEL": model_override,
                "GROUP_MODEL": model_override,
                "ENRICH_MODEL": model_override,
            }
        )
        logger.info("Model override via KR_PRIMARY_MODEL: %s", model_override)

    verify_override = os.environ.get("KR_VERIFY_MODEL")
    if verify_override:
        config = config.model_copy(update={"VERIFY_MODEL": verify_override})
        logger.info("Verify model override via KR_VERIFY_MODEL: %s", verify_override)

    # D-041: hard-fail on same-provider consensus
    primary_provider = _provider_name(config.CLASSIFY_MODEL)
    verify_provider = _provider_name(config.VERIFY_MODEL)
    if primary_provider == verify_provider:
        raise ValueError(
            f"D-041 violation: primary ({config.CLASSIFY_MODEL}) and verify "
            f"({config.VERIFY_MODEL}) use same provider '{primary_provider}'. "
            f"Set KR_VERIFY_MODEL to a different provider."
        )

    # ── Create clients ────────────────────────────────────────────
    trace_contexts: dict[str, dict[str, Any]] = {}

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
            req_hook, resp_hook, err_hook, ctx = make_hook_logger(output_dir, name)
            trace_contexts[name] = ctx
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
        enrich_client = create_client(timeout=config.ENRICH_TIMEOUT)
        verify_client = create_client(timeout=config.VERIFY_TIMEOUT)
        escalation_client = create_client(timeout=config.ESCALATION_TIMEOUT)

        # Register logging hooks on each client
        for client, name in [
            (enrich_client, "enrich"),
            (verify_client, "verify"),
            (escalation_client, "escalation"),
        ]:
            req_hook, resp_hook, err_hook, ctx = make_hook_logger(output_dir, name)
            trace_contexts[name] = ctx
            client.on("completion:kwargs", req_hook)
            client.on("completion:response", resp_hook)
            client.on("completion:error", err_hook)

    # ── Phase 1: Deterministic assembly ───────────────────────────
    logger.info("=== Phase 1: Deterministic assembly ===")
    t0 = time.monotonic()
    try:
        chunks, _validation_results = run_phase1(package, config)
    except KeyboardInterrupt:
        _append_error_once(all_errors, "interrupted: KeyboardInterrupt during phase1")
        _persist_failure_artifacts(
            output_dir=output_dir,
            source_id=source_id,
            timings=timings,
            errors=all_errors,
            config=config,
            source_metadata=source_metadata,
            excerpt_count=excerpt_count,
            gate_count=gate_count,
        )
        _finalize_traces()
        raise
    except Exception as exc:
        if mock:
            logger.warning(
                "Phase 1 validation failed in mock mode — generating "
                "synthetic chunks for infrastructure testing: %s", exc,
            )
            _append_error_once(all_errors, f"phase1_validation: {exc}")
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
                            confidence=0.95,
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
            _append_error_once(all_errors, f"phase1_fatal: {exc}")
            _persist_failure_artifacts(
                output_dir=output_dir,
                source_id=source_id,
                timings=timings,
                errors=all_errors,
                config=config,
                source_metadata=source_metadata,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
            )
            _finalize_traces()
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
        _persist_failure_artifacts(
            output_dir=output_dir,
            source_id=source_id,
            timings=timings,
            errors=all_errors,
            config=config,
            source_metadata=source_metadata,
            excerpt_count=0,
            gate_count=0,
        )
        _finalize_traces()
        return 0

    # ── Parallel pipeline (concurrency > 1) ──────────────────────
    if config.CONCURRENCY > 1 and not mock:
        from engines.excerpting.src.parallel_orchestrator import (
            run_parallel_pipeline,
        )

        logger.info(
            "=== Parallel pipeline (concurrency=%d) ===",
            config.CONCURRENCY,
        )

        # Pre-load resume artifacts
        pre_classified = _load_done_artifacts(
            chunks, progress, output_dir, "phase2a",
        )
        pre_grouped = _load_done_artifacts(
            chunks, progress, output_dir, "phase2b",
        )

        if backend == "cli":
            factory_counts = {"enrich": 0, "verify": 0, "escalation": 0}

            def _logged_client(base_name: str, client: Any) -> Any:
                factory_counts[base_name] += 1
                client_name = f"{base_name}_p{factory_counts[base_name]:03d}"
                req_hook, resp_hook, err_hook, _ctx = make_hook_logger(
                    output_dir,
                    client_name,
                )
                client.on("completion:kwargs", req_hook)
                client.on("completion:response", resp_hook)
                client.on("completion:error", err_hook)
                if ri_session is not None:
                    from shared.llm.ri_trace_bridge import attach as ri_attach

                    ri_attach(client, ri_session)
                return client

            def _enrich_factory() -> Any:
                return _logged_client("enrich", create_cli_client())

            def _verify_factory() -> Any:
                return _logged_client("verify", create_cli_client())

            def _escalation_factory() -> Any:
                return _logged_client("escalation", create_cli_client())
        else:
            factory_counts = {"enrich": 0, "verify": 0, "escalation": 0}

            def _logged_client(base_name: str, client: Any) -> Any:
                factory_counts[base_name] += 1
                client_name = f"{base_name}_p{factory_counts[base_name]:03d}"
                req_hook, resp_hook, err_hook, _ctx = make_hook_logger(
                    output_dir,
                    client_name,
                )
                client.on("completion:kwargs", req_hook)
                client.on("completion:response", resp_hook)
                client.on("completion:error", err_hook)
                return client

            def _enrich_factory() -> Any:
                return _logged_client(
                    "enrich",
                    create_client(timeout=config.ENRICH_TIMEOUT),
                )

            def _verify_factory() -> Any:
                return _logged_client(
                    "verify",
                    create_client(timeout=config.VERIFY_TIMEOUT),
                )

            def _escalation_factory() -> Any:
                return _logged_client(
                    "escalation",
                    create_client(timeout=config.ESCALATION_TIMEOUT),
                )

        t0 = time.monotonic()
        try:
            parallel_excerpts, parallel_gates = run_parallel_pipeline(
                chunks=chunks,
                config=config,
                enrich_client_factory=_enrich_factory,
                verify_client_factory=_verify_factory,
                escalation_client_factory=_escalation_factory,
                progress=progress,
                cache=llm_cache,
                source_metadata=source_metadata,
                classified_data=pre_classified,
                grouped_data=pre_grouped,
            )
        except KeyboardInterrupt:
            _append_error_once(
                all_errors,
                "interrupted: KeyboardInterrupt during parallel pipeline",
            )
            _persist_failure_artifacts(
                output_dir=output_dir,
                source_id=source_id,
                timings=timings,
                errors=all_errors,
                config=config,
                source_metadata=source_metadata,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
            )
            _finalize_traces()
            raise
        except Exception as exc:
            logger.error("Parallel pipeline failed: %s", exc)
            _append_error_once(all_errors, f"parallel_pipeline_fatal: {exc}")
            _persist_failure_artifacts(
                output_dir=output_dir,
                source_id=source_id,
                timings=timings,
                errors=all_errors,
                config=config,
                source_metadata=source_metadata,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
            )
            _finalize_traces()
            return 1
        timings["parallel_pipeline"] = round(time.monotonic() - t0, 3)

        # Build a minimal Phase3Result-compatible object for the writer
        from types import SimpleNamespace

        phase3_result = SimpleNamespace(
            excerpts=parallel_excerpts,
            gate_entries=parallel_gates,
            errors=[],
            validation_drops=[],
        )
        excerpt_count = len(phase3_result.excerpts)
        gate_count = len(phase3_result.gate_entries)
        logger.info(
            "Parallel pipeline produced %d excerpts, %d gate entries",
            excerpt_count,
            gate_count,
        )

        # Jump to output writing (shared with sequential path below)
        # We replicate the write_output block inline to avoid goto-like structure
        logger.info("=== Writing output files ===")
        t0 = time.monotonic()
        try:
            from engines.excerpting.src.writer import (
                GateQueueVerificationError,
                verify_gate_queue,
                write_excerpts,
                write_gate_queue,
                write_processing_log,
            )

            if phase3_result.excerpts:
                write_excerpts(phase3_result.excerpts, output_dir)
            if phase3_result.gate_entries:
                write_gate_queue(phase3_result.gate_entries, output_dir)
                gate_path = output_dir / "gate_queue.jsonl"
                gate_errors = verify_gate_queue(
                    phase3_result.gate_entries, gate_path
                )
                all_errors.extend(gate_errors)

            timings["write_output"] = round(time.monotonic() - t0, 3)
            llm_error_count = _count_llm_call_errors(output_dir)
            if llm_error_count > 0:
                _append_error_once(
                    all_errors, f"llm_call_errors:{llm_error_count}"
                )

            assert source_id is not None
            write_processing_log(
                source_id=source_id,
                errors=all_errors,
                timings=timings,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
                output_dir=output_dir,
            )
            _save_timing_and_metadata(
                output_dir,
                timings,
                all_errors,
                config,
                source_metadata,
            )
        except KeyboardInterrupt:
            timings["write_output"] = round(time.monotonic() - t0, 3)
            _append_error_once(
                all_errors,
                "interrupted: KeyboardInterrupt during output writing",
            )
            _persist_failure_artifacts(
                output_dir=output_dir,
                source_id=source_id,
                timings=timings,
                errors=all_errors,
                config=config,
                source_metadata=source_metadata,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
            )
            _finalize_traces()
            raise
        except (OSError, GateQueueVerificationError) as exc:
            logger.error("Output writing failed: %s", exc)
            timings["write_output"] = round(time.monotonic() - t0, 3)
            _append_error_once(all_errors, f"write_output_fatal: {exc}")
            _persist_failure_artifacts(
                output_dir=output_dir,
                source_id=source_id,
                timings=timings,
                errors=all_errors,
                config=config,
                source_metadata=source_metadata,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
            )
            _finalize_traces()
            return 1

        total_time = sum(
            v for v in timings.values() if isinstance(v, (int, float))
        )
        final_progress = progress.summary()
        print(f"\n=== Integration Test Complete (parallel) ===")
        print(f"  Output:      {output_dir}")
        print(f"  Chunks:      {len(chunks)}")
        print(f"  Concurrency: {config.CONCURRENCY}")
        print(f"  Excerpts:    {excerpt_count}")
        print(f"  Gates:       {gate_count}")
        print(f"  Errors:      {len(all_errors)}")
        print(
            f"  Progress:    {final_progress['done']} done, "
            f"{final_progress['failed']} failed"
        )
        print(f"  Total time:  {total_time:.2f}s")
        print()

        _finalize_traces()
        return 0

    # ── Phase 2a: Classification ──────────────────────────────────
    logger.info("=== Phase 2a: Classification ===")
    # Set semantic_phase on trace contexts before LLM calls
    for ctx in trace_contexts.values():
        ctx["semantic_phase"] = "classification"
    chunk_timings_2a: dict[str, float] = {}

    # Pre-load phase2a artifacts for chunks already done (resume support)
    pre_classified: dict[str, list[Any]] = {}
    if not mock:
        pre_classified = _load_done_artifacts(
            chunks, progress, output_dir, "phase2a",
        )
        if pre_classified:
            logger.info(
                "Resumed %d phase2a chunks from artifacts", len(pre_classified)
            )

    t0 = time.monotonic()
    if mock:
        classified = _mock_phase2a(chunks)
    else:
        try:
            classified = run_phase2a(chunks, enrich_client, config, progress=progress, cache=llm_cache, trace_context=trace_contexts.get("enrich"))
        except KeyboardInterrupt:
            _append_error_once(
                all_errors,
                "interrupted: KeyboardInterrupt during phase2a",
            )
            _persist_failure_artifacts(
                output_dir=output_dir,
                source_id=source_id,
                timings=timings,
                errors=all_errors,
                config=config,
                source_metadata=source_metadata,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
            )
            _finalize_traces()
            raise
        except Exception as exc:
            logger.error("Phase 2a failed: %s", exc)
            _append_error_once(all_errors, f"phase2a_fatal: {exc}")
            _persist_failure_artifacts(
                output_dir=output_dir,
                source_id=source_id,
                timings=timings,
                errors=all_errors,
                config=config,
                source_metadata=source_metadata,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
            )
            _finalize_traces()
            return 1
    timings["phase2a"] = round(time.monotonic() - t0, 3)
    # Merge pre-loaded artifacts with newly processed results
    classified = {**pre_classified, **classified}
    for chunk_id in classified:
        chunk_timings_2a[chunk_id] = timings["phase2a"] / max(len(classified), 1)
    timings["phase2a_per_chunk"] = chunk_timings_2a
    logger.info(
        "Phase 2a classified %d chunks (%d total segments, %d resumed)",
        len(classified),
        sum(len(v) for v in classified.values()),
        len(pre_classified),
    )
    _serialize_classifications(classified, output_dir)

    # A1: Write Phase 2a failure ledger
    phase2a_failures = [
        {
            "chunk_id": chunk.chunk_id,
            "source_id": chunk.source_id,
            "div_id": chunk.div_id,
            "word_count": chunk.word_count,
        }
        for chunk in chunks
        if chunk.chunk_id not in classified
    ]
    if phase2a_failures:
        _write_jsonl(output_dir / "phase2a_failures.jsonl", phase2a_failures)
        all_errors.append(f"phase2a_chunk_failures:{len(phase2a_failures)}")
        logger.warning(
            "%d chunk(s) failed Phase 2a: %s",
            len(phase2a_failures),
            [f["chunk_id"] for f in phase2a_failures],
        )

    # ── Phase 2b: Grouping ────────────────────────────────────────
    logger.info("=== Phase 2b: Grouping ===")
    for name, ctx in trace_contexts.items():
        if name == "enrich":
            ctx["semantic_phase"] = "grouping"
    chunk_timings_2b: dict[str, float] = {}

    # Pre-load phase2b artifacts for chunks already done (resume support)
    pre_grouped: dict[str, list[Any]] = {}
    if not mock:
        pre_grouped = _load_done_artifacts(
            chunks, progress, output_dir, "phase2b",
        )
        if pre_grouped:
            logger.info(
                "Resumed %d phase2b chunks from artifacts", len(pre_grouped)
            )

    t0 = time.monotonic()
    if mock:
        grouped = _mock_phase2b(chunks, classified)
    else:
        try:
            grouped = run_phase2b(chunks, classified, enrich_client, config, progress=progress, cache=llm_cache, trace_context=trace_contexts.get("enrich"))
        except KeyboardInterrupt:
            _append_error_once(
                all_errors,
                "interrupted: KeyboardInterrupt during phase2b",
            )
            _persist_failure_artifacts(
                output_dir=output_dir,
                source_id=source_id,
                timings=timings,
                errors=all_errors,
                config=config,
                source_metadata=source_metadata,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
            )
            _finalize_traces()
            raise
        except Exception as exc:
            logger.error("Phase 2b failed: %s", exc)
            _append_error_once(all_errors, f"phase2b_fatal: {exc}")
            _persist_failure_artifacts(
                output_dir=output_dir,
                source_id=source_id,
                timings=timings,
                errors=all_errors,
                config=config,
                source_metadata=source_metadata,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
            )
            _finalize_traces()
            return 1
    timings["phase2b"] = round(time.monotonic() - t0, 3)
    # Merge pre-loaded artifacts with newly processed results
    grouped = {**pre_grouped, **grouped}
    for chunk_id in grouped:
        chunk_timings_2b[chunk_id] = timings["phase2b"] / max(len(grouped), 1)
    timings["phase2b_per_chunk"] = chunk_timings_2b
    logger.info(
        "Phase 2b grouped %d chunks (%d total teaching units, %d resumed)",
        len(grouped),
        sum(len(v) for v in grouped.values()),
        len(pre_grouped),
    )
    _serialize_groupings(grouped, output_dir)

    # A1: Write Phase 2b failure ledger
    phase2b_failures = [
        {"chunk_id": chunk_id}
        for chunk_id in classified
        if chunk_id not in grouped
    ]
    if phase2b_failures:
        _write_jsonl(output_dir / "phase2b_failures.jsonl", phase2b_failures)
        all_errors.append(f"phase2b_chunk_failures:{len(phase2b_failures)}")
        logger.warning(
            "%d chunk(s) failed Phase 2b: %s",
            len(phase2b_failures),
            [f["chunk_id"] for f in phase2b_failures],
        )

    # ── Phase 3: Enrichment + consensus + validation ──────────────
    logger.info("=== Phase 3: Enrichment + consensus + validation ===")
    for name, ctx in trace_contexts.items():
        if name == "enrich":
            ctx["semantic_phase"] = "enrichment"
        elif name == "verify":
            ctx["semantic_phase"] = "verification"
        elif name == "escalation":
            ctx["semantic_phase"] = "escalation"
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
                progress=progress,
                cache=llm_cache,
            )
        except KeyboardInterrupt:
            _append_error_once(
                all_errors,
                "interrupted: KeyboardInterrupt during phase3",
            )
            _persist_failure_artifacts(
                output_dir=output_dir,
                source_id=source_id,
                timings=timings,
                errors=all_errors,
                config=config,
                source_metadata=source_metadata,
                excerpt_count=excerpt_count,
                gate_count=gate_count,
            )
            _finalize_traces()
            raise
        except Exception as exc:
            logger.error("Phase 3 failed: %s", exc)
            _append_error_once(all_errors, f"phase3_fatal: {exc}")
            _persist_failure_artifacts(
                output_dir=output_dir,
                source_id=source_id,
                timings=timings,
                errors=all_errors,
                config=config,
                source_metadata=source_metadata,
                excerpt_count=0,
                gate_count=0,
            )
            _finalize_traces()
            return 1
    timings["phase3"] = round(time.monotonic() - t0, 3)
    all_errors.extend(phase3_result.errors)
    excerpt_count = len(phase3_result.excerpts)
    gate_count = len(phase3_result.gate_entries)
    logger.info(
        "Phase 3 produced %d excerpts, %d gate entries",
        excerpt_count,
        gate_count,
    )

    # ── Write output files ────────────────────────────────────────
    logger.info("=== Writing output files ===")
    t0 = time.monotonic()
    try:
        if phase3_result.excerpts:
            write_excerpts(phase3_result.excerpts, output_dir)
        if phase3_result.gate_entries:
            write_gate_queue(phase3_result.gate_entries, output_dir)
            gate_path = output_dir / "gate_queue.jsonl"
            gate_errors = verify_gate_queue(
                phase3_result.gate_entries, gate_path
            )
            all_errors.extend(gate_errors)

        if (
            hasattr(phase3_result, "validation_drops")
            and phase3_result.validation_drops
        ):
            _write_jsonl(
                output_dir / "validation_drops.jsonl",
                phase3_result.validation_drops,
            )
            logger.info(
                "Wrote %d validation drop(s) to validation_drops.jsonl",
                len(phase3_result.validation_drops),
            )

        timings["write_output"] = round(time.monotonic() - t0, 3)
        llm_error_count = _count_llm_call_errors(output_dir)
        if llm_error_count > 0:
            _append_error_once(all_errors, f"llm_call_errors:{llm_error_count}")

        assert source_id is not None
        write_processing_log(
            source_id=source_id,
            errors=all_errors,
            timings=timings,
            excerpt_count=excerpt_count,
            gate_count=gate_count,
            output_dir=output_dir,
        )
        _save_timing_and_metadata(
            output_dir,
            timings,
            all_errors,
            config,
            source_metadata,
        )
    except KeyboardInterrupt:
        timings["write_output"] = round(time.monotonic() - t0, 3)
        _append_error_once(
            all_errors,
            "interrupted: KeyboardInterrupt during output writing",
        )
        _persist_failure_artifacts(
            output_dir=output_dir,
            source_id=source_id,
            timings=timings,
            errors=all_errors,
            config=config,
            source_metadata=source_metadata,
            excerpt_count=excerpt_count,
            gate_count=gate_count,
        )
        _finalize_traces()
        raise
    except (OSError, GateQueueVerificationError) as exc:
        logger.error("Output writing failed: %s", exc)
        timings["write_output"] = round(time.monotonic() - t0, 3)
        _append_error_once(all_errors, f"write_output_fatal: {exc}")
        _persist_failure_artifacts(
            output_dir=output_dir,
            source_id=source_id,
            timings=timings,
            errors=all_errors,
            config=config,
            source_metadata=source_metadata,
            excerpt_count=excerpt_count,
            gate_count=gate_count,
        )
        _finalize_traces()
        return 1

    # ── Summary ───────────────────────────────────────────────────
    total_time = sum(v for v in timings.values() if isinstance(v, (int, float)))
    final_progress = progress.summary()
    print(f"\n=== Integration Test Complete ===")
    print(f"  Output:     {output_dir}")
    print(f"  Chunks:     {len(chunks)}")
    print(f"  Excerpts:   {excerpt_count}")
    print(f"  Gates:      {gate_count}")
    print(f"  Errors:     {len(all_errors)}")
    print(f"  Progress:   {final_progress['done']} done, {final_progress['failed']} failed")
    print(f"  Total time: {total_time:.2f}s")
    print()

    _finalize_traces()
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
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Max concurrent LLM calls (default: 1 = sequential)",
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
    print(f"Concurrency:     {args.concurrency}")
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
        concurrency=args.concurrency,
    )


if __name__ == "__main__":
    sys.exit(main())
