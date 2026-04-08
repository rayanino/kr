from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace

import pytest

from scripts import codex_kb_bridge as bridge
from scripts.autonomous_schemas import (
    Finding,
    FindingSeverity,
    ResearchCategory,
    VerificationStatus,
)


def _make_finding() -> Finding:
    return Finding(
        finding_id="F-test-001",
        source_type="codex_task",
        source_id="codex-test",
        severity=FindingSeverity.HIGH,
        category=ResearchCategory.CROSS_CUTTING,
        title="Bridge should verify confirmed findings",
        description="A regression in the verification path blocks backlog promotion.",
        affected_files=["scripts/codex_kb_bridge.py"],
        action_required="Fix the verifier pipeline.",
        confidence=0.9,
        raw_text_hash="deadbeefcafebabe",
        prompt_id=None,
        section_heading="",
        verification_status=VerificationStatus.PRELIMINARY,
        verified_by=None,
        verified_at=None,
        verification_response="",
    )


def test_build_verifier_backends_prefers_anthropic_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        bridge,
        "_load_api_key",
        lambda env_name: {
            "ANTHROPIC_API_KEY": "anthropic-key",
            "OPENROUTER_API_KEY": "openrouter-key",
        }.get(env_name),
    )
    backends = bridge._build_verifier_backends()

    assert [label for label, _ in backends] == [
        "anthropic_api",
        "openrouter_api",
    ]


def test_run_anthropic_api_verify_parses_agree_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    finding = _make_finding()

    class FakeMessages:
        def create(self, **kwargs: object) -> SimpleNamespace:
            assert kwargs["model"] == bridge._ANTHROPIC_VERIFY_MODEL
            assert kwargs["temperature"] == 0
            return SimpleNamespace(
                content=[SimpleNamespace(type="text", text="AGREE\nThe finding is real.")]
            )

    class FakeAnthropic:
        def __init__(self, *, api_key: str) -> None:
            assert api_key == "test-key"
            self.messages = FakeMessages()

    fake_module = ModuleType("anthropic")
    setattr(fake_module, "Anthropic", FakeAnthropic)
    monkeypatch.setitem(sys.modules, "anthropic", fake_module)

    status, response = bridge._run_anthropic_api_verify(finding, "test-key")

    assert status == VerificationStatus.CONFIRMED
    assert response.startswith("AGREE")


def test_run_openrouter_verify_parses_disagree_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    finding = _make_finding()

    class FakeResponse:
        status_code = 200
        text = ""

        @staticmethod
        def json() -> dict[str, object]:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "DISAGREE\nThe finding is stale.",
                        }
                    }
                ]
            }

    fake_httpx = ModuleType("httpx")
    setattr(
        fake_httpx,
        "post",
        lambda *args, **kwargs: FakeResponse(),
    )
    monkeypatch.setitem(sys.modules, "httpx", fake_httpx)

    status, response = bridge._run_openrouter_verify(finding, "test-key")

    assert status == VerificationStatus.DISPUTED
    assert response.startswith("DISAGREE")


def test_verify_findings_falls_back_to_next_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    finding = _make_finding()
    rewritten: dict[str, list[Finding]] = {}

    monkeypatch.setattr(
        bridge,
        "_build_verifier_backends",
        lambda: [
            ("anthropic_api", lambda item: (VerificationStatus.PRELIMINARY, "timeout")),
            ("openrouter_api", lambda item: (VerificationStatus.CONFIRMED, "AGREE\nConfirmed")),
        ],
    )
    monkeypatch.setattr(bridge, "read_jsonl", lambda path, model: [finding])
    monkeypatch.setattr(
        bridge,
        "rewrite_jsonl",
        lambda path, items: rewritten.setdefault("items", list(items)),
    )

    stats = bridge.verify_findings([finding])

    assert stats == {"verified": 1, "confirmed": 1, "disputed": 0, "skipped": 0}
    assert finding.verification_status == VerificationStatus.CONFIRMED
    assert finding.verified_by == "openrouter_api"
    assert finding.verified_at is not None
    assert rewritten["items"][0].verification_status == VerificationStatus.CONFIRMED
