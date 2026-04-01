"""Batch integration test runner for all 5 excerpting engine test packages.

Runs scripts/run_integration_test.py on each package, aggregates results,
and produces SUMMARY.json.  Supports parallel execution (``--parallel N``)
for significant speedup — each package is fully independent.

Usage:
    python scripts/run_full_integration.py --backend cli
    python scripts/run_full_integration.py --backend cli --parallel 3
    python scripts/run_full_integration.py --output-dir path/to/output/
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import json
import os
import signal
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

# Ensure project root is on sys.path so local imports work without PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ---------------------------------------------------------------------------
# Package configuration
# ---------------------------------------------------------------------------

PACKAGES: list[dict[str, Any]] = [
    {
        "name": "ibn_aqil_v1",
        "metadata": {
            "author_name": "ابن عقيل",
            "work_title": "شرح ابن عقيل على ألفية ابن مالك",
            "science": "نحو",
            "source_school": None,
        },
    },
    {
        "name": "ibn_aqil_v3",
        "metadata": {
            "author_name": "ابن عقيل",
            "work_title": "شرح ابن عقيل على ألفية ابن مالك",
            "science": "نحو",
            "source_school": None,
        },
    },
    {
        "name": "taysir",
        "metadata": {
            "author_name": "عبد الله البسام",
            "work_title": "تيسير العلام شرح عمدة الأحكام",
            "science": "فقه",
            "source_school": "حنبلي",
        },
    },
    {
        "name": "ext_39_masala",
        "metadata": {
            "author_name": None,
            "work_title": None,
            "science": None,
            "source_school": None,
        },
    },
    {
        "name": "ext_46_qa",
        "metadata": {
            "author_name": None,
            "work_title": None,
            "science": "أصول النحو",
            "source_school": None,
        },
    },
]

PACKAGES_DIR = Path("experiments/format_diversity_test/packages")
RUNNER_SCRIPT = Path("scripts/run_integration_test.py")
SUMMARY_FILENAME = "SUMMARY.json"
RESUME_RERUN_MARKERS = (
    "phase3_fatal",
    "write_output_fatal",
    "interrupted",
    "batch_timeout",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def format_duration(seconds: float) -> str:
    """Format seconds as Xm Ys."""
    m, s = divmod(int(seconds), 60)
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


def _read_json_file(path: Path) -> dict[str, Any] | None:
    """Best-effort JSON reader for package artifacts."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _read_processing_log(path: Path) -> dict[str, Any] | None:
    """Read processing_log.jsonl, which is stored as a single JSON object."""
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not text:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None
        for line in reversed(text.splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                candidate = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, dict):
                data = candidate
                break
    return data if isinstance(data, dict) else None


def read_package_results(pkg_output_dir: Path) -> dict[str, Any]:
    """Read result files from a completed or partially completed package run."""
    result: dict[str, Any] = {
        "excerpt_count": 0,
        "error_count": 0,
        "errors": [],
        "time_seconds": 0.0,
        "cost_estimate": 0.0,
    }

    timing = _read_json_file(pkg_output_dir / "timing.json")
    if timing is not None:
        total = sum(v for v in timing.values() if isinstance(v, (int, float)))
        result["time_seconds"] = round(total, 2)

    excerpts_path = pkg_output_dir / "excerpts.jsonl"
    if excerpts_path.exists():
        try:
            with open(excerpts_path, encoding="utf-8") as fh:
                result["excerpt_count"] = sum(1 for line in fh if line.strip())
        except OSError:
            pass

    meta = _read_json_file(pkg_output_dir / "run_metadata.json")
    if meta is not None:
        result["error_count"] = int(meta.get("error_count", 0) or 0)
        errors = meta.get("errors")
        if isinstance(errors, list):
            result["errors"] = [str(error) for error in errors]

    processing_log = _read_processing_log(pkg_output_dir / "processing_log.jsonl")
    if processing_log is not None:
        if result["excerpt_count"] == 0:
            result["excerpt_count"] = int(processing_log.get("excerpt_count", 0) or 0)
        if result["time_seconds"] == 0.0:
            timings = processing_log.get("timings")
            if isinstance(timings, dict):
                total = sum(v for v in timings.values() if isinstance(v, (int, float)))
                result["time_seconds"] = round(total, 2)
        if not result["errors"]:
            errors = processing_log.get("errors")
            if isinstance(errors, list):
                result["errors"] = [str(error) for error in errors]
                result["error_count"] = max(
                    result["error_count"],
                    int(processing_log.get("error_count", len(result["errors"])) or 0),
                )

    resp_dir = pkg_output_dir / "raw_llm_responses"
    if resp_dir.exists():
        for resp_file in resp_dir.glob("*.json"):
            if resp_file.name.endswith("_error.json"):
                continue
            try:
                resp = json.loads(resp_file.read_text(encoding="utf-8"))
                usage = resp.get("usage") or {}
                cost = usage.get("cost", 0.0)
                if cost:
                    result["cost_estimate"] += cost
            except (json.JSONDecodeError, OSError):
                pass
        result["cost_estimate"] = round(result["cost_estimate"], 6)

    return result


def _build_summary(
    output_dir: Path,
    results: dict[str, dict[str, Any]],
    batch_start: float,
    *,
    complete: bool,
    packages_run: int | None = None,
) -> dict[str, Any]:
    """Build the aggregate summary payload."""
    total_time = time.monotonic() - batch_start
    succeeded = sum(1 for r in results.values() if r.get("status") == "success")
    failed = sum(1 for r in results.values() if r.get("status") == "error")
    return {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "output_dir": str(output_dir),
        "complete": complete,
        "packages": results,
        "totals": {
            "packages_run": packages_run if packages_run is not None else len(results),
            "packages_succeeded": succeeded,
            "packages_failed": failed,
            "total_excerpts": sum(r.get("excerpt_count", 0) for r in results.values()),
            "total_errors": sum(r.get("error_count", 0) for r in results.values()),
            "total_time_seconds": round(total_time, 2),
            "total_cost_estimate": round(
                sum(r.get("cost_estimate", 0.0) for r in results.values()),
                6,
            ),
        },
    }


def _write_incremental_summary(
    output_dir: Path,
    results: dict[str, dict[str, Any]],
    batch_start: float,
    *,
    complete: bool = False,
    packages_run: int | None = None,
) -> None:
    """Write SUMMARY.json atomically without crashing the batch on I/O errors."""
    summary = _build_summary(
        output_dir,
        results,
        batch_start,
        complete=complete,
        packages_run=packages_run,
    )
    summary_path = output_dir / SUMMARY_FILENAME
    temp_path = summary_path.with_suffix(".json.tmp")
    try:
        temp_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(summary_path)
    except OSError as exc:
        print(f"WARNING: Failed to write {summary_path}: {exc}")


def _should_rerun_package(errors: list[str]) -> bool:
    """Return True when prior artifacts indicate an incomplete package run."""
    return any(
        marker in error
        for error in errors
        for marker in RESUME_RERUN_MARKERS
    )


def _safe_reset_package_output(output_dir: Path, pkg_output: Path) -> None:
    """Delete a package output directory only if it resolves inside the batch root."""
    expected_names = {pkg["name"] for pkg in PACKAGES}
    if pkg_output.name not in expected_names:
        raise ValueError(f"Refusing to delete unexpected package dir: {pkg_output}")
    resolved_root = output_dir.resolve(strict=False)
    resolved_pkg = pkg_output.resolve(strict=False)
    if resolved_pkg == resolved_root or resolved_pkg.parent != resolved_root:
        raise ValueError(
            f"Refusing to delete path outside batch output root: {pkg_output}",
        )
    if not pkg_output.exists():
        return
    if not pkg_output.is_dir():
        raise ValueError(f"Refusing to delete non-directory package path: {pkg_output}")

    for attempt in range(3):
        try:
            shutil.rmtree(pkg_output)
            return
        except PermissionError:
            if attempt == 2:
                raise
            time.sleep(0.5 * (attempt + 1))


def _build_package_result(
    pkg_output: Path,
    *,
    status: str,
    elapsed_pkg: float,
    fallback_error: str | None = None,
) -> dict[str, Any]:
    """Merge best-effort on-disk artifacts with a synthetic package status."""
    pkg_result = read_package_results(pkg_output)
    pkg_result["status"] = status
    pkg_result["time_seconds"] = round(elapsed_pkg, 2)
    if fallback_error and fallback_error not in pkg_result["errors"]:
        pkg_result["errors"].append(fallback_error)
    if status == "error":
        pkg_result["error_count"] = max(
            pkg_result["error_count"],
            len(pkg_result["errors"]),
            1,
        )
    return pkg_result


def _persist_resume_marker(
    pkg_output: Path,
    *,
    fallback_error: str,
    elapsed_pkg: float,
) -> None:
    """Persist batch-level failure markers so resume logic can re-run the package."""
    if not pkg_output.exists():
        return
    meta_path = pkg_output / "run_metadata.json"
    meta = _read_json_file(meta_path) or {}
    existing_errors = meta.get("errors")
    merged_errors = (
        [str(error) for error in existing_errors]
        if isinstance(existing_errors, list)
        else []
    )
    if fallback_error not in merged_errors:
        merged_errors.append(fallback_error)
    payload = {
        **meta,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "error_count": max(int(meta.get("error_count", 0) or 0), len(merged_errors)),
        "errors": merged_errors,
        "batch_elapsed_seconds": round(elapsed_pkg, 2),
    }
    try:
        meta_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"WARNING: Failed to persist resume marker in {meta_path}: {exc}")


def _write_timeout_report(
    pkg_output: Path,
    *,
    timeout_seconds: int,
    elapsed_pkg: float,
) -> None:
    """Write a durable timeout report from whatever artifacts exist on disk."""
    report_path = pkg_output / "STALL_REPORT.md"
    progress_path = pkg_output / "progress.jsonl"
    excerpts_path = pkg_output / "excerpts.jsonl"
    timing_path = pkg_output / "timing.json"
    processing_log_path = pkg_output / "processing_log.jsonl"
    last_activity_path = pkg_output / "last_llm_activity.json"
    meta = _read_json_file(pkg_output / "run_metadata.json") or {}
    last_activity = _read_json_file(last_activity_path)

    phase_counts: dict[tuple[str, str], int] = {}
    last_entry: dict[str, Any] | None = None
    total_entries = 0
    if progress_path.exists():
        try:
            for raw in progress_path.read_text(encoding="utf-8").splitlines():
                raw = raw.strip()
                if not raw:
                    continue
                entry = json.loads(raw)
                if not isinstance(entry, dict):
                    continue
                total_entries += 1
                phase = str(entry.get("phase", "unknown"))
                status = str(entry.get("status", "unknown"))
                phase_counts[(phase, status)] = phase_counts.get((phase, status), 0) + 1
                last_entry = entry
        except (OSError, json.JSONDecodeError):
            pass

    def _latest_file_info(subdir: str) -> str:
        root = pkg_output / subdir
        if not root.is_dir():
            return "none"
        files = [p for p in root.glob("*.json") if p.is_file()]
        if not files:
            return "none"
        latest = max(files, key=lambda p: p.stat().st_mtime)
        ts = datetime.datetime.fromtimestamp(
            latest.stat().st_mtime,
            datetime.timezone.utc,
        ).isoformat().replace("+00:00", "Z")
        return f"{latest.name} @ {ts}"

    def _trace_health() -> dict[str, Any]:
        req_root = pkg_output / "raw_llm_requests"
        resp_root = pkg_output / "raw_llm_responses"
        summary: dict[str, Any] = {
            "request_counts": {},
            "response_counts": {},
            "missing_response_calls": [],
            "abnormal_responses": [],
        }
        if not req_root.is_dir() or not resp_root.is_dir():
            return summary

        request_files = sorted(p for p in req_root.glob("*.json") if p.is_file())
        response_files = sorted(p for p in resp_root.glob("*.json") if p.is_file())

        def _prefix(name: str) -> str:
            return name.split("_")[0]

        request_counts: dict[str, int] = {}
        response_counts: dict[str, int] = {}
        for path in request_files:
            key = _prefix(path.stem)
            request_counts[key] = request_counts.get(key, 0) + 1
        for path in response_files:
            key = _prefix(path.stem)
            response_counts[key] = response_counts.get(key, 0) + 1
        summary["request_counts"] = request_counts
        summary["response_counts"] = response_counts

        response_stems = {
            path.stem
            for path in response_files
            if not path.name.endswith("_error.json")
        }
        error_response_stems = {
            path.stem[:-6]
            for path in response_files
            if path.name.endswith("_error.json")
        }
        summary["missing_response_calls"] = [
            path.stem
            for path in request_files
            if path.stem not in response_stems and path.stem not in error_response_stems
        ]

        abnormal: list[dict[str, Any]] = []
        for path in response_files:
            if path.name.endswith("_error.json"):
                continue
            try:
                entry = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(entry, dict):
                continue
            usage = entry.get("usage") or {}
            completion_tokens = usage.get("completion_tokens")
            finish_reason = entry.get("finish_reason")
            if finish_reason in (None, "") or (
                isinstance(completion_tokens, int) and completion_tokens <= 1
            ):
                abnormal.append({
                    "call_id": entry.get("call_id", path.stem),
                    "finish_reason": finish_reason,
                    "completion_tokens": completion_tokens,
                    "latency_seconds": entry.get("latency_seconds"),
                })
        summary["abnormal_responses"] = abnormal[-5:]
        return summary

    trace_health = _trace_health()

    lines = [
        "# Timeout Report",
        "",
        f"- Timeout marker: `batch_timeout: exceeded {timeout_seconds}s in batch runner`",
        f"- Elapsed seconds: `{round(elapsed_pkg, 2)}`",
        f"- `excerpts.jsonl` present: `{excerpts_path.exists()}`",
        f"- `processing_log.jsonl` present: `{processing_log_path.exists()}`",
        f"- `timing.json` present: `{timing_path.exists()}`",
        "",
        "## run_metadata.json",
        "",
        "```json",
        json.dumps(meta, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Progress Snapshot",
        "",
        f"- Total progress entries: `{total_entries}`",
    ]

    if last_entry is not None:
        lines.extend([
            "- Last progress entry:",
            "",
            "```json",
            json.dumps(last_entry, ensure_ascii=False),
            "```",
        ])

    if phase_counts:
        lines.extend([
            "",
            "- Phase/status counts:",
        ])
        for (phase, status), count in sorted(phase_counts.items()):
            lines.append(f"  - `{phase}` / `{status}`: `{count}`")

    lines.extend([
        "",
        "## Raw Trace Tail",
        "",
        f"- `last_llm_activity.json` present: `{last_activity_path.exists()}`",
        f"- Latest request file: `{_latest_file_info('raw_llm_requests')}`",
        f"- Latest response file: `{_latest_file_info('raw_llm_responses')}`",
    ])

    if trace_health["request_counts"] or trace_health["response_counts"]:
        lines.extend([
            "",
            "## Trace Health",
            "",
            "```json",
            json.dumps(trace_health, ensure_ascii=False, indent=2),
            "```",
        ])

    if isinstance(last_activity, dict) and last_activity:
        lines.extend([
            "",
            "## Last LLM Activity",
            "",
            "```json",
            json.dumps(last_activity, ensure_ascii=False, indent=2),
            "```",
        ])

    lines.extend([
        "",
        "## Note",
        "",
        "- This report is written by the batch runner after killing a timed-out package subprocess.",
        "- Missing `processing_log.jsonl`, `timing.json`, or `excerpts.jsonl` usually means the child process never reached the output-writing block.",
    ])

    try:
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"WARNING: Failed to write timeout report {report_path}: {exc}")


def _terminate_process_tree(proc: subprocess.Popen[Any]) -> None:
    """Terminate a runner subprocess and its descendants.

    Try a graceful interrupt first so the child can persist partial artifacts
    through its KeyboardInterrupt handlers, then fall back to a hard kill.
    """
    if proc.poll() is not None:
        return
    grace_seconds = 15
    try:
        if os.name == "nt":
            try:
                proc.send_signal(signal.CTRL_BREAK_EVENT)
                proc.wait(timeout=grace_seconds)
                return
            except (subprocess.TimeoutExpired, ValueError, OSError):
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
        else:
            try:
                os.killpg(proc.pid, signal.SIGINT)
                proc.wait(timeout=grace_seconds)
                return
            except ProcessLookupError:
                return
            except subprocess.TimeoutExpired:
                pass
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                return
    finally:
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


def _run_package_subprocess(
    cmd: list[str],
    *,
    env: dict[str, str],
    timeout: int,
) -> int:
    """Run a package subprocess with timeout-aware tree cleanup."""
    popen_kwargs: dict[str, Any] = {"env": env}
    if os.name == "nt":
        popen_kwargs["creationflags"] = getattr(
            subprocess,
            "CREATE_NEW_PROCESS_GROUP",
            0,
        )
    else:
        popen_kwargs["start_new_session"] = True

    proc = subprocess.Popen(cmd, **popen_kwargs)
    try:
        return proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        _terminate_process_tree(proc)
        raise


# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------

_PROMPT_PREFLIGHT: dict[str, tuple[list[str], str]] = {
    "codex": (
        ["codex", "exec", "Say 1"],
        "Run: codex  (ensure npm install -g @openai/codex)",
    ),
    "gemini": (
        ["gemini", "-p", "Say 1", "-y", "--output-format", "text"],
        "Run: gemini  (ensure npm install -g @google/gemini-cli)",
    ),
}


def _preflight_cli(backends: list[str]) -> bool:
    """Test each CLI backend before the real run.

    Claude: binary-exists check only (startup is slow without --bare
    because it loads plugins/MCP; auth uses the same subscription as
    Claude Code — if CC works, Claude CLI works).

    Codex/Gemini: send a trivial prompt and verify a response.
    """
    all_ok = True
    for name in backends:
        resolved = shutil.which(name)
        if resolved is None:
            print(f"  PREFLIGHT FAIL: {name} — not found on PATH")
            all_ok = False
            continue

        # Claude: just verify binary exists — it uses subscription auth
        if name == "claude":
            print(f"  PREFLIGHT OK:   {name} ({resolved})")
            continue

        entry = _PROMPT_PREFLIGHT.get(name)
        if entry is None:
            print(f"  PREFLIGHT OK:   {name} ({resolved})")
            continue

        cmd_template, fix_hint = entry
        cmd = [resolved] + cmd_template[1:]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60,
            )
            if result.returncode != 0:
                stderr = (result.stderr or "").strip()[:200]
                stdout = (result.stdout or "").strip()[:200]
                msg = stderr or stdout or "(no output)"
                print(f"  PREFLIGHT FAIL: {name} — exit {result.returncode}: {msg}")
                print(f"    Fix: {fix_hint}")
                all_ok = False
            else:
                print(f"  PREFLIGHT OK:   {name}")
        except FileNotFoundError:
            print(f"  PREFLIGHT FAIL: {name} — CLI not found on PATH")
            print(f"    Fix: {fix_hint}")
            all_ok = False
        except subprocess.TimeoutExpired:
            print(f"  PREFLIGHT FAIL: {name} — timed out after 60s")
            all_ok = False

    return all_ok


def _determine_needed_backends() -> list[str]:
    """Determine which CLI backends the current config will use."""
    from engines.excerpting.contracts import ExcerptingConfig

    model_override = os.environ.get("KR_PRIMARY_MODEL", "")
    config = ExcerptingConfig()

    needed = set()
    primary_models = [model_override] if model_override else [config.CLASSIFY_MODEL]

    for model in primary_models:
        if model.startswith("anthropic/"):
            needed.add("claude")
        elif model.startswith("openai/"):
            needed.add("codex")
        elif model.startswith("google/"):
            needed.add("gemini")

    # Verify model — respect KR_VERIFY_MODEL override
    verify_model = os.environ.get("KR_VERIFY_MODEL", config.VERIFY_MODEL)
    if verify_model.startswith("anthropic/"):
        needed.add("claude")
    elif verify_model.startswith("openai/"):
        needed.add("codex")
    elif verify_model.startswith("google/"):
        needed.add("gemini")

    escalation_model = config.ESCALATION_MODEL
    if escalation_model.startswith("anthropic/"):
        needed.add("claude")
    elif escalation_model.startswith("openai/"):
        needed.add("codex")
    elif escalation_model.startswith("google/"):
        needed.add("gemini")
    elif escalation_model.startswith("mistralai/"):
        needed.add("codex")

    return sorted(needed)


# ---------------------------------------------------------------------------
# Batch execution
# ---------------------------------------------------------------------------


def _run_single_package(
    pkg: dict[str, Any],
    output_dir: Path,
    backend: str,
    max_chunks: int | None,
    per_package_timeout: int,
    batch_start: float,
    results: dict[str, dict[str, Any]],
    lock: threading.Lock,
    label: str,
    concurrency: int = 1,
) -> None:
    """Run a single package — designed to be called from a thread or sequentially."""
    name = pkg["name"]
    pkg_path = PACKAGES_DIR / name
    pkg_output = output_dir / name

    elapsed = time.monotonic() - batch_start
    print(f"\n{'=' * 60}")
    print(f"[{label}] {name} (elapsed: {format_duration(elapsed)})")
    print(f"{'=' * 60}\n")

    pkg_result: dict[str, Any] | None = None
    t0 = time.monotonic()

    try:
        if not pkg_path.exists():
            print(f"  [{name}] ERROR: Package directory not found: {pkg_path}")
            pkg_result = {
                "status": "error",
                "excerpt_count": 0,
                "error_count": 1,
                "errors": [f"Package directory not found: {pkg_path}"],
                "time_seconds": 0.0,
                "cost_estimate": 0.0,
            }
        else:
            done_marker = pkg_output / "processing_log.jsonl"
            if done_marker.exists():
                prev = read_package_results(pkg_output)
                if _should_rerun_package(prev.get("errors", [])):
                    print(f"  [{name}] RE-RUNNING — previous run ended fatally")
                    _safe_reset_package_output(output_dir, pkg_output)
                    pkg_output.mkdir(parents=True, exist_ok=True)
                else:
                    print(
                        f"  [{name}] SKIPPING — already completed "
                        f"({prev['excerpt_count']} excerpts, "
                        f"{prev['error_count']} errors)"
                    )
                    pkg_result = prev
                    pkg_result["status"] = "success"

            if pkg_result is None:
                cmd = [
                    sys.executable,
                    str(RUNNER_SCRIPT),
                    "--package-path",
                    str(pkg_path),
                    "--output-dir",
                    str(pkg_output),
                    "--source-metadata",
                    json.dumps(pkg["metadata"], ensure_ascii=False),
                    "--backend",
                    backend,
                ]
                if max_chunks is not None:
                    cmd.extend(["--max-chunks", str(max_chunks)])
                if concurrency > 1:
                    cmd.extend(["--concurrency", str(concurrency)])

                env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
                returncode = _run_package_subprocess(
                    cmd,
                    env=env,
                    timeout=per_package_timeout,
                )
                elapsed_pkg = time.monotonic() - t0

                if returncode != 0:
                    print(
                        f"\n  [{name}] FAILED (exit code {returncode}, "
                        f"{format_duration(elapsed_pkg)})"
                    )
                    pkg_result = _build_package_result(
                        pkg_output,
                        status="error",
                        elapsed_pkg=elapsed_pkg,
                        fallback_error=f"Exit code {returncode}",
                    )
                else:
                    print(
                        f"\n  [{name}] COMPLETED "
                        f"({format_duration(elapsed_pkg)})"
                    )
                    pkg_result = _build_package_result(
                        pkg_output,
                        status="success",
                        elapsed_pkg=elapsed_pkg,
                    )

    except subprocess.TimeoutExpired:
        elapsed_pkg = time.monotonic() - t0
        print(f"\n  [{name}] TIMEOUT after {format_duration(elapsed_pkg)}")
        marker = (
            f"batch_timeout: exceeded {per_package_timeout}s in batch runner"
        )
        _persist_resume_marker(
            pkg_output,
            fallback_error=marker,
            elapsed_pkg=elapsed_pkg,
        )
        _write_timeout_report(
            pkg_output,
            timeout_seconds=per_package_timeout,
            elapsed_pkg=elapsed_pkg,
        )
        pkg_result = _build_package_result(
            pkg_output,
            status="error",
            elapsed_pkg=elapsed_pkg,
            fallback_error=marker,
        )
    except Exception as exc:
        elapsed_pkg = time.monotonic() - t0
        print(f"\n  [{name}] CRASH: {exc}")
        marker = f"batch_runner_crash: {exc}"
        _persist_resume_marker(
            pkg_output,
            fallback_error=marker,
            elapsed_pkg=elapsed_pkg,
        )
        pkg_result = _build_package_result(
            pkg_output,
            status="error",
            elapsed_pkg=elapsed_pkg,
            fallback_error=marker,
        )

    if pkg_result is not None:
        with lock:
            results[name] = pkg_result
            _write_incremental_summary(output_dir, results, batch_start)


def run_batch(
    output_dir: Path,
    backend: str = "api",
    max_chunks: int | None = None,
    per_package_timeout: int = 28800,
    parallel: int = 1,
    concurrency: int = 1,
) -> dict[str, Any]:
    """Run all packages and return aggregated results.

    Args:
        parallel: Max concurrent packages. 1 = sequential (default).
            Values >1 run packages in parallel threads, each spawning
            its own subprocess. Packages are independent — no shared
            state except the results dict (protected by a lock).
        concurrency: Max concurrent LLM calls per package subprocess.
            Forwarded to run_integration_test.py --concurrency.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, Any]] = {}
    lock = threading.Lock()
    batch_start = time.monotonic()

    parallel = max(1, parallel)

    # Preflight: verify CLI backends before committing to a multi-hour run
    if backend == "cli":
        needed = _determine_needed_backends()
        print(f"Preflight check ({', '.join(needed)})...")
        if not _preflight_cli(needed):
            print("\nABORTING — fix the failing backends before running.")
            print("This check took <30s. Without it, you'd wait hours to find out.\n")
            return _build_summary(
                output_dir, results, batch_start,
                complete=False, packages_run=0,
            )
        print()

    if parallel > 1:
        print(f"Parallel mode: up to {parallel} packages concurrently\n")

    try:
        if parallel == 1:
            # Sequential — same behavior as before, cleaner output
            for i, pkg in enumerate(PACKAGES, start=1):
                label = f"{i}/{len(PACKAGES)}"
                _run_single_package(
                    pkg, output_dir, backend, max_chunks,
                    per_package_timeout, batch_start, results, lock, label,
                    concurrency=concurrency,
                )
        else:
            # Parallel — launch up to N packages concurrently
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=parallel
            ) as pool:
                futures: dict[concurrent.futures.Future[None], str] = {}
                for i, pkg in enumerate(PACKAGES, start=1):
                    label = f"{i}/{len(PACKAGES)}"
                    fut = pool.submit(
                        _run_single_package,
                        pkg, output_dir, backend, max_chunks,
                        per_package_timeout, batch_start, results, lock, label,
                        concurrency,
                    )
                    futures[fut] = pkg["name"]

                # Wait for all to complete; propagate first exception
                for fut in concurrent.futures.as_completed(futures):
                    exc = fut.exception()
                    if exc is not None and not isinstance(exc, KeyboardInterrupt):
                        print(
                            f"  [{futures[fut]}] thread exception: {exc}"
                        )

    except KeyboardInterrupt:
        _write_incremental_summary(output_dir, results, batch_start, complete=False)
        raise

    final = _build_summary(
        output_dir,
        results,
        batch_start,
        complete=True,
        packages_run=len(PACKAGES),
    )
    _write_incremental_summary(
        output_dir,
        results,
        batch_start,
        complete=True,
        packages_run=len(PACKAGES),
    )
    return final


# ---------------------------------------------------------------------------
# Summary display
# ---------------------------------------------------------------------------


def print_summary(summary: dict[str, Any]) -> None:
    """Print a human-readable summary table."""
    print(f"\n{'=' * 60}")
    print("FULL INTEGRATION TEST SUMMARY")
    print(f"{'=' * 60}\n")

    header = (
        f"  {'Package':<20} {'Status':<10} {'Excerpts':>10} "
        f"{'Errors':>8} {'Time':>10} {'Cost':>10}"
    )
    divider = (
        f"  {'-' * 18:<20} {'-' * 8:<10} {'-' * 8:>10} "
        f"{'-' * 6:>8} {'-' * 8:>10} {'-' * 8:>10}"
    )
    print(header)
    print(divider)

    for name, result in summary["packages"].items():
        status = "OK" if result["status"] == "success" else "FAIL"
        time_str = format_duration(result["time_seconds"])
        cost_str = f"\u20ac{result['cost_estimate']:.4f}"
        print(
            f"  {name:<20} {status:<10} {result['excerpt_count']:>10} "
            f"{result['error_count']:>8} {time_str:>10} {cost_str:>10}"
        )

    print(divider)
    totals = summary["totals"]
    time_str = format_duration(totals["total_time_seconds"])
    cost_str = f"\u20ac{totals['total_cost_estimate']:.4f}"
    ok_str = f"{totals['packages_succeeded']}/{totals['packages_run']}"
    print(
        f"  {'TOTAL':<20} {ok_str:<10} {totals['total_excerpts']:>10} "
        f"{totals['total_errors']:>8} {time_str:>10} {cost_str:>10}"
    )
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run full integration tests on all 5 excerpting engine packages.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: integration_tests/full_run_{YYYYMMDD}/)",
    )
    parser.add_argument(
        "--backend",
        choices=["cli", "api"],
        default="api",
        help="LLM backend passed to run_integration_test.py",
    )
    parser.add_argument(
        "--max-chunks",
        type=int,
        default=None,
        help="Limit Phase 2/3 to first N chunks per package (default: all)",
    )
    parser.add_argument(
        "--per-package-timeout",
        type=int,
        default=28800,
        help="Per-package subprocess timeout in seconds (default: 28800 = 8h).",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help=(
            "Max concurrent packages (default: 1 = sequential). "
            "Each package runs in its own subprocess with its own output "
            "directory — no shared state. Recommended: 3 for CLI backend."
        ),
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help=(
            "Max concurrent LLM calls per package (default: 1 = sequential). "
            "Forwarded to run_integration_test.py --concurrency."
        ),
    )
    args = parser.parse_args()

    if args.output_dir is None:
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        args.output_dir = Path("integration_tests") / f"full_run_{date_str}"

    if args.backend == "api":
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("ERROR: OPENROUTER_API_KEY environment variable not set")
            return 1
        api_key_display = f"{'*' * 8}...{api_key[-4:]}"
    else:
        api_key_display = "(CLI backend — no API key needed)"

    if not PACKAGES_DIR.exists():
        print(f"ERROR: Packages directory not found: {PACKAGES_DIR}")
        return 1

    print(f"Output directory: {args.output_dir.resolve()}")
    print(f"Packages:         {len(PACKAGES)}")
    print(f"Backend:          {args.backend}")
    print(f"API key:          {api_key_display}")
    print(f"Max chunks:       {args.max_chunks or 'all'}")
    print(f"Pkg timeout:      {args.per_package_timeout}s")
    print(f"Parallel:         {args.parallel}")
    print(f"Concurrency:      {args.concurrency}")

    summary = run_batch(
        args.output_dir,
        backend=args.backend,
        max_chunks=args.max_chunks,
        per_package_timeout=args.per_package_timeout,
        parallel=args.parallel,
        concurrency=args.concurrency,
    )
    print_summary(summary)

    summary_path = args.output_dir / SUMMARY_FILENAME
    print(f"Summary saved to: {summary_path}")

    return 0 if summary.get("complete") and summary["totals"]["packages_failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
