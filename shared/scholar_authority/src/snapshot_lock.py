"""Registry snapshot locking primitive (REQ-SRC-0049 + INV-SRC-0017).

A scholar match call MUST operate against a STABLE view of the internal
registry. This module provides:

  - ``RegistrySnapshot`` — a Pydantic model capturing a pinned snapshot
    identifier plus pin timestamp
  - ``RegistrySnapshotDriftError`` — raised when the loaded
    ``registry_release_version`` no longer equals the value pinned at
    case start (SRC-E-REGISTRY-SNAPSHOT-DRIFT)
  - ``RuntimeExternalCallError`` — raised when a verifier prompt template
    or other case-scoped code attempts a forbidden runtime external fetch
    against Brill EI / Usul.ai / Dorar.net / Wikidata SPARQL / OpenITI /
    LLM enrichment endpoints (SRC-E-RUNTIME-EXTERNAL)
  - ``lock_registry_snapshot()`` — context-manager helper for case-scoped
    drift detection
  - ``validate_no_drift()`` — pure check: does pinned == observed?

Session 1 provides these primitives without wiring them into the
match-call orchestrator; Session 4 ties them into ``compute_scholar_
match_score`` rewrite plus REQ-SRC-0042 build-time-only enrichment lane.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from engines.source.contracts import ErrorCode


class RegistrySnapshot(BaseModel):
    """Pinned snapshot of the scholar registry for one match-call case.

    Per REQ-SRC-0049 postconditions: a versioned snapshot is loaded and
    pinned for the case duration. ``registry_release_version`` is the
    canonical identifier (``snapshot_version`` is FORBIDDEN per Codex
    Stage-3 Defect 2 — Pydantic ``extra='forbid'`` rejects it generically
    and the contracts module's ``_reject_snapshot_version`` validator
    catches it with an explicit error message in CON-SRC-0008 +
    CON-SRC-0009 paths).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    registry_release_version: str = Field(min_length=1)
    pinned_at: str = Field(min_length=1)


class RegistrySnapshotDriftError(RuntimeError):
    """SRC-E-REGISTRY-SNAPSHOT-DRIFT — mid-case snapshot drift detected.

    Raised when the orchestrator observes a registry_release_version
    different from the one pinned at case start. Per REQ-SRC-0049 + INV-
    SRC-0017 the drift path: aborts finalization, discards verifier
    outputs from the in-flight case (retained as audit evidence per
    Critical Rule 13 — all data is future training material), and
    restarts candidate generation against the new snapshot. This is
    EXPLICIT REPLAY, not silent re-resolution.
    """

    error_code: ErrorCode = ErrorCode.REGISTRY_SNAPSHOT_DRIFT

    def __init__(self, pinned_version: str, observed_version: Optional[str]) -> None:
        observed = observed_version if observed_version is not None else "<null>"
        super().__init__(
            f"Registry snapshot drift detected. Pinned at case start: "
            f"{pinned_version!r}; observed mid-case: {observed!r}. "
            f"Aborting finalization per REQ-SRC-0049 + INV-SRC-0017 "
            f"(SRC-E-REGISTRY-SNAPSHOT-DRIFT)."
        )
        self.pinned_version = pinned_version
        self.observed_version = observed_version


class RuntimeExternalCallError(RuntimeError):
    """SRC-E-RUNTIME-EXTERNAL — forbidden runtime external lookup.

    Per REQ-SRC-0042 amendment + REQ-SRC-0049: external sources (Brill EI,
    Usul.ai API, Dorar.net API, Wikidata SPARQL endpoint, OpenITI GitHub,
    LLM enrichment endpoints) are FORBIDDEN at runtime. They are
    authorized only at build_time with ``data_provenance.enrichment_phase
    = build_time`` plus license + ``training_use_permitted`` markers.
    A verifier or orchestrator that attempts such a call is aborted; the
    case routes to disputed terminal with positions[] populated from
    locally-gathered evidence only.
    """

    error_code: ErrorCode = ErrorCode.RUNTIME_EXTERNAL

    def __init__(self, attempted_endpoint: str) -> None:
        super().__init__(
            f"Runtime external call to {attempted_endpoint!r} is FORBIDDEN. "
            "Per REQ-SRC-0042 amendment + REQ-SRC-0049 the scholar match "
            "hot path must use the locked registry snapshot only; external "
            "enrichment is build-time only "
            "(SRC-E-RUNTIME-EXTERNAL)."
        )
        self.attempted_endpoint = attempted_endpoint


def pin_registry_snapshot(registry_release_version: str) -> RegistrySnapshot:
    """Construct a RegistrySnapshot pin for one match-call case.

    The caller (Session 4 match-call orchestrator) supplies the current
    registry_release_version at case start; this helper attaches the
    UTC ISO 8601 ``pinned_at`` timestamp and returns the immutable pin.
    Raises ``ValueError`` if the input version is empty (REQ-SRC-0049
    error_conditions: registry_release_version null at case init aborts
    with SRC-E-REGISTRY-SNAPSHOT-DRIFT — handled at the orchestrator
    layer; the empty-string check here protects against silent failures
    if the orchestrator forgets to validate).
    """
    if not registry_release_version or not registry_release_version.strip():
        raise ValueError(
            "registry_release_version must be a non-empty string. "
            "Per REQ-SRC-0049 a match call cannot proceed without a "
            "pinnable release (SRC-E-REGISTRY-SNAPSHOT-DRIFT)."
        )
    return RegistrySnapshot(
        registry_release_version=registry_release_version,
        pinned_at=datetime.now(timezone.utc).isoformat(),
    )


def validate_no_drift(
    pinned: RegistrySnapshot,
    observed_release_version: Optional[str],
) -> None:
    """Raise RegistrySnapshotDriftError if observed differs from pinned.

    Pure check. Called by the match-call orchestrator at finalization
    time and (optionally) at intermediate verifier hand-off points.
    A None ``observed_release_version`` is treated as drift (registry
    became unavailable mid-case).
    """
    if observed_release_version != pinned.registry_release_version:
        raise RegistrySnapshotDriftError(
            pinned_version=pinned.registry_release_version,
            observed_version=observed_release_version,
        )


@contextmanager
def lock_registry_snapshot(
    registry_release_version: str,
) -> Iterator[RegistrySnapshot]:
    """Context manager: pin a snapshot for a case-scoped block.

    Usage::

        with lock_registry_snapshot("2026-04-15.r1") as pinned:
            # ... Stage-1 narrowing + Stage-2 verifier work ...
            validate_no_drift(pinned, current_registry_version())
            # ... emit ScholarMatchResult with provenance.registry_release_version
            #     == pinned.registry_release_version ...

    The context manager itself does not POLL for drift mid-case — drift
    detection is the orchestrator's responsibility at well-defined
    hand-off points. Polling discipline is encoded in REQ-SRC-0049
    postconditions and INV-SRC-0017's "EXPLICIT REPLAY" requirement.
    """
    pinned = pin_registry_snapshot(registry_release_version)
    try:
        yield pinned
    finally:
        # No teardown is required — the snapshot is purely informational
        # data. Resources (loaded side indexes etc.) are managed by the
        # match-call orchestrator (Session 4).
        pass


__all__ = [
    "RegistrySnapshot",
    "RegistrySnapshotDriftError",
    "RuntimeExternalCallError",
    "pin_registry_snapshot",
    "validate_no_drift",
    "lock_registry_snapshot",
]
