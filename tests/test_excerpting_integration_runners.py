from __future__ import annotations

import json
from types import SimpleNamespace

from scripts.run_full_integration import (
    _safe_reset_package_output,
    read_package_results,
)
from scripts.run_integration_test import (
    _persist_failure_artifacts,
    make_hook_logger,
)
from shared.llm.cli_adapter import CLIBackendError


def test_read_package_results_falls_back_to_processing_log(tmp_path) -> None:
    pkg_dir = tmp_path / "ibn_aqil_v1"
    pkg_dir.mkdir()
    (pkg_dir / "timing.json").write_text("{not json", encoding="utf-8")
    (pkg_dir / "run_metadata.json").write_text("{broken", encoding="utf-8")
    (pkg_dir / "processing_log.jsonl").write_text(
        json.dumps(
            {
                "source_id": "src_test",
                "excerpt_count": 7,
                "error_count": 1,
                "errors": ["phase3_fatal: boom"],
                "timings": {"phase1": 1.5, "phase2": 2.5},
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    resp_dir = pkg_dir / "raw_llm_responses"
    resp_dir.mkdir()
    (resp_dir / "resp.json").write_text(
        json.dumps({"usage": {"cost": 0.125}}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = read_package_results(pkg_dir)

    assert result["excerpt_count"] == 7
    assert result["error_count"] == 1
    assert result["errors"] == ["phase3_fatal: boom"]
    assert result["time_seconds"] == 4.0
    assert result["cost_estimate"] == 0.125


def test_safe_reset_package_output_rejects_escape_path(tmp_path) -> None:
    output_dir = tmp_path / "batch"
    output_dir.mkdir()
    escaped = output_dir / ".." / "ibn_aqil_v1"
    escaped.mkdir()

    try:
        _safe_reset_package_output(output_dir, escaped)
    except ValueError as exc:
        assert "outside batch output root" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ValueError for escaped package path")


def test_make_hook_logger_persists_full_payloads(tmp_path) -> None:
    on_request, on_response, on_error, _ctx = make_hook_logger(tmp_path, "enrich")
    request_body = "x" * 5000
    response_body = "y" * 60000

    on_request(
        model="openai/gpt-5.4",
        temperature=0.0,
        max_tokens=123,
        messages=[
            {"role": "user", "content": request_body},
        ],
    )
    on_response(
        SimpleNamespace(
            usage=None,
            choices=[
                SimpleNamespace(
                    finish_reason="stop",
                    message=SimpleNamespace(content=response_body),
                )
            ],
            model="openai/gpt-5.4",
        )
    )
    on_error(
        CLIBackendError(
            "boom",
            backend="codex",
            raw_output='{"partial": true}',
            stderr="stderr text",
        )
    )

    request_json = json.loads(
        (tmp_path / "raw_llm_requests" / "enrich_0001.json").read_text(
            encoding="utf-8"
        )
    )
    response_json = json.loads(
        (tmp_path / "raw_llm_responses" / "enrich_0001.json").read_text(
            encoding="utf-8"
        )
    )
    error_json = json.loads(
        (tmp_path / "raw_llm_responses" / "enrich_0001_error.json").read_text(
            encoding="utf-8"
        )
    )

    assert request_json["messages"][0]["content"] == request_body
    assert response_json["raw_content"] == response_body
    assert error_json["raw_output"] == '{"partial": true}'
    assert error_json["stderr"] == "stderr text"


def test_persist_failure_artifacts_writes_processing_log_and_metadata(tmp_path) -> None:
    resp_dir = tmp_path / "raw_llm_responses"
    resp_dir.mkdir()
    (resp_dir / "call_0001_error.json").write_text("{}", encoding="utf-8")

    errors = ["write_output_fatal: disk full"]
    _persist_failure_artifacts(
        output_dir=tmp_path,
        source_id="src_test",
        timings={"phase1": 1.0},
        errors=errors,
        config=SimpleNamespace(model_dump=lambda mode="json": {"x": 1}),
        source_metadata={"author_name": "test"},
        excerpt_count=3,
        gate_count=1,
    )

    processing_log = json.loads(
        (tmp_path / "processing_log.jsonl").read_text(encoding="utf-8").strip()
    )
    run_metadata = json.loads(
        (tmp_path / "run_metadata.json").read_text(encoding="utf-8")
    )

    assert "llm_call_errors:1" in processing_log["errors"]
    assert "llm_call_errors:1" in run_metadata["errors"]
    assert processing_log["excerpt_count"] == 3
    assert processing_log["gate_count"] == 1
