"""Canonical backlog helpers for overnight_codex."""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    from scripts.overnight_codex_common import (
        BACKLOG_FILE,
        FINDINGS_REGISTRY_FILE,
        PIPELINE_ORDER,
        QUEUE_DIR,
        RESULTS_DIR,
        repo_rel,
        safe_slug,
        utc_now_iso,
        write_json,
    )
except ImportError:
    from overnight_codex_common import (
        BACKLOG_FILE,
        FINDINGS_REGISTRY_FILE,
        PIPELINE_ORDER,
        QUEUE_DIR,
        RESULTS_DIR,
        repo_rel,
        safe_slug,
        utc_now_iso,
        write_json,
    )


BACKLOG_STATUSES = {
    "proposed",
    "approved",
    "scheduled",
    "implemented",
    "blocked",
    "superseded",
}
PRIORITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
RUNTIME_SUBSYSTEM = "codex_runtime"
RUNTIME_WRITE_PREFIXES = [
    "scripts/overnight_codex_",
    "scripts/quality_gate.py",
    "scripts/append_codex_findings.py",
    "tests/test_overnight_codex_runtime.py",
    "docs/codex/",
    "overnight_codex/README.md",
]


def _default_backlog() -> dict[str, Any]:
    return {
        "meta": {
            "schema_version": 1,
            "last_synced_at": None,
            "last_sync_run": None,
        },
        "items": {},
    }


def load_backlog(path: Path | None = None) -> dict[str, Any]:
    """Load backlog state from disk."""
    path = path or BACKLOG_FILE
    if not path.exists():
        return _default_backlog()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _default_backlog()
    if not isinstance(payload, dict):
        return _default_backlog()
    payload.setdefault("meta", {})
    payload.setdefault("items", {})
    if not isinstance(payload["items"], dict):
        payload["items"] = {}
    return payload


def save_backlog(payload: dict[str, Any], path: Path | None = None) -> None:
    """Persist backlog state."""
    path = path or BACKLOG_FILE
    write_json(path, payload)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _normalize_repo_path(value: str) -> str:
    if not value:
        return ""
    normalized = value.replace("\\", "/").strip()
    if re.match(r"^[A-Za-z]:/", normalized):
        candidate = Path(normalized)
        try:
            return repo_rel(candidate)
        except Exception:
            return normalized
    return normalized


def _payload_paths(payload: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for evidence in payload.get("evidence", []):
        if isinstance(evidence, dict):
            path = _normalize_repo_path(str(evidence.get("path", "")))
            if path and path not in paths:
                paths.append(path)
    for item in payload.get("files_changed", []):
        path = _normalize_repo_path(str(item))
        if path and path not in paths:
            paths.append(path)
    return paths


def infer_subsystem(task_id: str, paths: list[str]) -> str:
    """Infer the subsystem a backlog item belongs to."""
    for path in paths:
        parts = path.split("/")
        if len(parts) >= 3 and parts[0] == "engines":
            return parts[1]
        if path.startswith("shared/"):
            return "shared"
        if path.startswith("docs/codex/") or path.startswith("scripts/overnight_codex_"):
            return RUNTIME_SUBSYSTEM
        if path in {
            "scripts/quality_gate.py",
            "scripts/append_codex_findings.py",
            "tests/test_overnight_codex_runtime.py",
            "overnight_codex/README.md",
        }:
            return RUNTIME_SUBSYSTEM
    for engine in PIPELINE_ORDER:
        if engine in task_id:
            return engine
    if "overnight_codex" in task_id or "codex" in task_id:
        return RUNTIME_SUBSYSTEM
    if "contract" in task_id or "boundary" in task_id:
        return "cross_engine"
    return "general"


def infer_frontier_tag(subsystem: str) -> str:
    if subsystem in PIPELINE_ORDER:
        return subsystem
    if subsystem == RUNTIME_SUBSYSTEM:
        return RUNTIME_SUBSYSTEM
    if subsystem in {"cross_engine", "shared"}:
        return "cross_engine"
    return "general"


def infer_allowed_write_prefixes(subsystem: str) -> list[str]:
    if subsystem in PIPELINE_ORDER:
        return [f"engines/{subsystem}/src/", f"engines/{subsystem}/tests/"]
    if subsystem == RUNTIME_SUBSYSTEM:
        return list(RUNTIME_WRITE_PREFIXES)
    if subsystem == "shared":
        return ["shared/"]
    return []


def dedupe_key(*, subsystem: str, category: str, summary: str) -> str:
    normalized = safe_slug(f"{subsystem}-{category}-{_normalize_text(summary)}")
    return normalized[:120]


def _status_value(record: dict[str, Any]) -> str:
    status = str(record.get("status", "proposed"))
    return status if status in BACKLOG_STATUSES else "proposed"


def _merge_evidence_paths(existing: list[str], new_paths: list[str]) -> list[str]:
    merged = [path for path in existing if path]
    for path in new_paths:
        if path and path not in merged:
            merged.append(path)
    return merged[:12]


def _merge_source_task_ids(existing: list[str], task_id: str) -> list[str]:
    merged = [item for item in existing if item]
    if task_id and task_id not in merged:
        merged.append(task_id)
    return merged[:12]


def _upsert_result_action_items(
    payload: dict[str, Any],
    *,
    task_id: str,
    source_signature: str,
    backlog: dict[str, Any],
    run_id: str,
    result_filename: str = "final_response.json",
) -> tuple[int, int]:
    created = 0
    updated = 0
    items = payload.get("action_items", [])
    if not isinstance(items, list):
        return created, updated
    paths = _payload_paths(payload)
    subsystem = infer_subsystem(task_id, paths)
    frontier_tag = infer_frontier_tag(subsystem)
    write_prefixes = infer_allowed_write_prefixes(subsystem)
    evidence_paths = _merge_evidence_paths(
        paths,
        [repo_rel(RESULTS_DIR / task_id / result_filename)],
    )
    seen_keys: set[str] = set()
    for raw_item in items:
        if not isinstance(raw_item, dict):
            continue
        summary = _normalize_text(str(raw_item.get("summary", "")))
        category = str(raw_item.get("category", "")).strip().upper() or "FOLLOW_UP"
        priority = str(raw_item.get("priority", "")).strip().upper() or "MEDIUM"
        effort = str(raw_item.get("effort", "")).strip().upper() or "M"
        if not summary:
            continue
        item_key = dedupe_key(subsystem=subsystem, category=category, summary=summary)
        if item_key in seen_keys:
            continue
        seen_keys.add(item_key)
        existing = backlog["items"].get(item_key)
        if isinstance(existing, dict):
            if source_signature == str(existing.get("latest_source_signature", "")):
                continue
            existing["summary"] = summary
            existing["category"] = category
            existing["priority"] = priority
            existing["effort"] = effort
            existing["last_seen"] = utc_now_iso()
            existing["last_touched_run"] = run_id
            existing["frontier_tag"] = existing.get("frontier_tag") or frontier_tag
            existing["subsystem"] = existing.get("subsystem") or subsystem
            existing["allowed_write_prefixes"] = existing.get("allowed_write_prefixes") or write_prefixes
            existing["source_task_ids"] = _merge_source_task_ids(
                list(existing.get("source_task_ids", [])),
                task_id,
            )
            existing["evidence_paths"] = _merge_evidence_paths(
                list(existing.get("evidence_paths", [])),
                evidence_paths,
            )
            existing["latest_result_path"] = repo_rel(RESULTS_DIR / task_id / result_filename)
            existing["latest_source_signature"] = source_signature
            existing["occurrences"] = int(existing.get("occurrences", 1)) + 1
            updated += 1
            continue
        backlog["items"][item_key] = {
            "item_id": item_key,
            "dedupe_key": item_key,
            "summary": summary,
            "proposed_action": summary,
            "category": category,
            "priority": priority,
            "effort": effort,
            "status": "proposed",
            "frontier_tag": frontier_tag,
            "subsystem": subsystem,
            "allowed_write_prefixes": write_prefixes,
            "gate_mode": "all",
            "evidence_paths": evidence_paths,
            "source_task_ids": [task_id],
            "source_kind": "result_action_item",
            "legacy_input": False,
            "created_at": utc_now_iso(),
            "created_by_run": run_id,
            "last_seen": utc_now_iso(),
            "last_touched_run": run_id,
            "status_updated_at": utc_now_iso(),
            "status_updated_by_run": run_id,
            "occurrences": 1,
            "latest_result_path": repo_rel(RESULTS_DIR / task_id / result_filename),
            "latest_source_signature": source_signature,
        }
        created += 1
    return created, updated


def _migrate_findings_registry(backlog: dict[str, Any], run_id: str) -> int:
    migrated = 0
    if not FINDINGS_REGISTRY_FILE.exists():
        return migrated
    try:
        payload = json.loads(FINDINGS_REGISTRY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return migrated
    records = payload.get("items", {})
    if not isinstance(records, dict):
        return migrated
    for record in records.values():
        if not isinstance(record, dict):
            continue
        summary = _normalize_text(str(record.get("summary", "")))
        category = str(record.get("category", "")).strip().upper() or "FOLLOW_UP"
        source = _normalize_repo_path(str(record.get("source", "")))
        task_id = safe_slug(source or "legacy-findings")
        subsystem = infer_subsystem(task_id, [source] if source else [])
        item_key = dedupe_key(subsystem=subsystem, category=category, summary=summary)
        existing = backlog["items"].get(item_key)
        if not isinstance(existing, dict):
            backlog["items"][item_key] = {
                "item_id": item_key,
                "dedupe_key": item_key,
                "summary": summary,
                "proposed_action": summary,
                "category": category,
                "priority": "MEDIUM",
                "effort": "M",
                "status": "proposed",
                "frontier_tag": infer_frontier_tag(subsystem),
                "subsystem": subsystem,
                "allowed_write_prefixes": infer_allowed_write_prefixes(subsystem),
                "gate_mode": "all",
                "evidence_paths": [source] if source else [],
                "source_task_ids": [],
                "source_kind": "legacy_findings_registry",
                "legacy_input": True,
                "created_at": utc_now_iso(),
                "created_by_run": run_id,
                "last_seen": utc_now_iso(),
                "last_touched_run": run_id,
                "status_updated_at": utc_now_iso(),
                "status_updated_by_run": run_id,
                "occurrences": int(record.get("occurrences", 1)),
                "latest_result_path": source,
            }
            migrated += 1
            continue
        existing["occurrences"] = max(int(existing.get("occurrences", 1)), int(record.get("occurrences", 1)))
        existing["legacy_input"] = True
        existing["evidence_paths"] = _merge_evidence_paths(
            list(existing.get("evidence_paths", [])),
            [source] if source else [],
        )
    return migrated


def _migrate_legacy_queue(backlog: dict[str, Any], run_id: str) -> int:
    migrated = 0
    for metadata_path in sorted(QUEUE_DIR.glob("*.json")):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        task_id = str(metadata.get("task_id", "")).strip()
        if not task_id:
            continue
        subsystem = infer_subsystem(task_id, [])
        item_key = f"legacy-patch-{safe_slug(task_id)}"
        if item_key in backlog["items"]:
            continue
        patch_path = _normalize_repo_path(str(metadata.get("patch_path", "")))
        backlog["items"][item_key] = {
            "item_id": item_key,
            "dedupe_key": item_key,
            "summary": f"Review legacy queued patch for `{task_id}` and promote it only if the bounded change is still wanted.",
            "proposed_action": f"Review queued patch for `{task_id}` before any implementation retry.",
            "category": "LEGACY_PATCH",
            "priority": "MEDIUM",
            "effort": "M",
            "status": "proposed",
            "frontier_tag": infer_frontier_tag(subsystem),
            "subsystem": subsystem,
            "allowed_write_prefixes": infer_allowed_write_prefixes(subsystem),
            "gate_mode": "all",
            "evidence_paths": [patch_path] if patch_path else [],
            "source_task_ids": [task_id],
            "source_kind": "legacy_queue",
            "legacy_input": True,
            "created_at": utc_now_iso(),
            "created_by_run": run_id,
            "last_seen": utc_now_iso(),
            "last_touched_run": run_id,
            "status_updated_at": utc_now_iso(),
            "status_updated_by_run": run_id,
            "occurrences": 1,
            "legacy_patch_path": patch_path,
            "legacy_commit_hash": str(metadata.get("commit_hash", "")).strip(),
        }
        migrated += 1
    return migrated


def _find_result_files(results_dir: Path) -> list[tuple[Path, str]]:
    """Discover result JSON files across all task directories.

    Scans ``final_response.json`` first.  For ``creative-*`` directories that
    lack a ``final_response.json``, falls back to ``creative.json`` so that
    partial creative-task outputs still flow into the backlog.
    """
    found: list[tuple[Path, str]] = []
    if not results_dir.is_dir():
        return found
    for task_dir in sorted(results_dir.iterdir()):
        if not task_dir.is_dir():
            continue
        primary = task_dir / "final_response.json"
        if primary.exists():
            found.append((primary, task_dir.name))
            continue
        # Fallback: creative tasks may only have creative.json
        if task_dir.name.startswith("creative-"):
            fallback = task_dir / "creative.json"
            if fallback.exists():
                found.append((fallback, task_dir.name))
    return found


def sync_backlog_from_artifacts(run_id: str) -> dict[str, int]:
    """Sync actionable runtime artifacts into the canonical backlog."""
    backlog = load_backlog()
    created = 0
    updated = 0
    for result_file, task_id in _find_result_files(RESULTS_DIR):
        try:
            payload = json.loads(result_file.read_text(encoding="utf-8"))
        except OSError:
            logger.error("Cannot read result file %s: OS error", result_file)
            continue
        except json.JSONDecodeError as exc:
            logger.error(
                "Invalid JSON in %s: %s", result_file, exc,
            )
            continue
        source_signature = f"{task_id}:{result_file.stat().st_mtime_ns}"
        add_created, add_updated = _upsert_result_action_items(
            payload,
            task_id=task_id,
            source_signature=source_signature,
            backlog=backlog,
            run_id=run_id,
            result_filename=result_file.name,
        )
        created += add_created
        updated += add_updated
    migrated_findings = _migrate_findings_registry(backlog, run_id)
    migrated_queue = _migrate_legacy_queue(backlog, run_id)
    backlog["meta"]["last_synced_at"] = utc_now_iso()
    backlog["meta"]["last_sync_run"] = run_id
    save_backlog(backlog)
    return {
        "created": created,
        "updated": updated,
        "migrated_findings": migrated_findings,
        "migrated_queue": migrated_queue,
    }


def update_backlog_status(
    item_id: str,
    *,
    status: str,
    run_id: str,
    note: str = "",
    patch_path: str = "",
) -> bool:
    """Update one backlog item status in place."""
    if status not in BACKLOG_STATUSES:
        raise ValueError(f"Unsupported backlog status: {status}")
    backlog = load_backlog()
    item = backlog["items"].get(item_id)
    if not isinstance(item, dict):
        return False
    item["status"] = status
    item["status_updated_at"] = utc_now_iso()
    item["status_updated_by_run"] = run_id
    item["last_touched_run"] = run_id
    if patch_path:
        item["latest_patch_path"] = patch_path
    if note:
        notes = list(item.get("notes", []))
        if note not in notes:
            notes.append(note)
        item["notes"] = notes[-6:]
    save_backlog(backlog)
    return True


def summarize_backlog(*, run_id: str | None = None) -> dict[str, Any]:
    """Return compact backlog counts for reporting."""
    backlog = load_backlog()
    items = [
        record
        for record in backlog["items"].values()
        if isinstance(record, dict)
    ]
    counts = {status: 0 for status in sorted(BACKLOG_STATUSES)}
    for record in items:
        counts[_status_value(record)] += 1
    summary = {
        "total": len(items),
        "counts": counts,
        "created_this_run": 0,
        "approved_this_run": 0,
        "implemented_this_run": 0,
        "blocked_this_run": 0,
    }
    if run_id is None:
        return summary
    for record in items:
        if record.get("created_by_run") == run_id:
            summary["created_this_run"] += 1
        if record.get("status_updated_by_run") == run_id:
            status = _status_value(record)
            if status == "approved":
                summary["approved_this_run"] += 1
            elif status == "implemented":
                summary["implemented_this_run"] += 1
            elif status == "blocked":
                summary["blocked_this_run"] += 1
    return summary


def approved_backlog_items(frontier_tag: str) -> list[dict[str, Any]]:
    """Return approved backlog items aligned to the current frontier."""
    backlog = load_backlog()
    items = [
        record
        for record in backlog["items"].values()
        if isinstance(record, dict) and _status_value(record) == "approved"
    ]
    eligible = []
    for record in items:
        item_frontier = str(record.get("frontier_tag", "general"))
        if item_frontier not in {frontier_tag, "cross_engine", "general"}:
            continue
        if not record.get("allowed_write_prefixes"):
            continue
        eligible.append(record)
    eligible.sort(
        key=lambda record: (
            PRIORITY_ORDER.get(str(record.get("priority", "MEDIUM")), 9),
            -int(record.get("occurrences", 1)),
            str(record.get("last_seen", "")),
            str(record.get("item_id", "")),
        ),
        reverse=False,
    )
    return eligible


def _item_age_days(record: dict[str, Any]) -> float:
    """Return the age of an item in days since its creation."""
    created = str(record.get("created_at", ""))
    if not created:
        return 0.0
    try:
        ts = datetime.fromisoformat(created)
    except ValueError:
        return 0.0
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - ts
    return delta.total_seconds() / 86400


def auto_approve_aged_items(*, days: int = 7, run_id: str) -> int:
    """Approve all proposed items older than *days*.

    Returns the number of items approved.
    """
    backlog = load_backlog()
    approved = 0
    for record in backlog["items"].values():
        if not isinstance(record, dict):
            continue
        if _status_value(record) != "proposed":
            continue
        if _item_age_days(record) < days:
            continue
        record["status"] = "approved"
        record["status_updated_at"] = utc_now_iso()
        record["status_updated_by_run"] = run_id
        record["last_touched_run"] = run_id
        approved += 1
    if approved:
        save_backlog(backlog)
    return approved


def proposed_items_needing_review(max_age_days: int = 3) -> list[dict[str, Any]]:
    """Return proposed items older than *max_age_days* for the morning report."""
    backlog = load_backlog()
    items: list[dict[str, Any]] = []
    for record in backlog["items"].values():
        if not isinstance(record, dict):
            continue
        if _status_value(record) != "proposed":
            continue
        if _item_age_days(record) < max_age_days:
            continue
        items.append(record)
    items.sort(
        key=lambda r: (
            PRIORITY_ORDER.get(str(r.get("priority", "MEDIUM")), 9),
            -int(r.get("occurrences", 1)),
        ),
    )
    return items


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cmd_approve(args: argparse.Namespace) -> None:
    ok = update_backlog_status(
        args.item_id, status="approved", run_id="cli-manual",
    )
    if ok:
        print(f"Approved: {args.item_id}")
    else:
        print(f"Item not found: {args.item_id}", file=sys.stderr)
        sys.exit(1)


def _cmd_reject(args: argparse.Namespace) -> None:
    ok = update_backlog_status(
        args.item_id, status="superseded", run_id="cli-manual",
    )
    if ok:
        print(f"Rejected (superseded): {args.item_id}")
    else:
        print(f"Item not found: {args.item_id}", file=sys.stderr)
        sys.exit(1)


def _cmd_list(args: argparse.Namespace) -> None:
    backlog = load_backlog()
    rows: list[tuple[str, str, str, str, int]] = []
    for record in backlog["items"].values():
        if not isinstance(record, dict):
            continue
        status = _status_value(record)
        if args.status and status != args.status:
            continue
        rows.append((
            str(record.get("item_id", "")),
            status,
            str(record.get("priority", "")),
            str(record.get("summary", ""))[:72],
            int(record.get("occurrences", 1)),
        ))
    rows.sort(key=lambda r: (PRIORITY_ORDER.get(r[2], 9), -r[4]))
    if not rows:
        print("No items found.")
        return
    print(f"{'ID':<42} {'STATUS':<12} {'PRI':<7} {'OCC':>3}  SUMMARY")
    print("-" * 120)
    for item_id, status, priority, summary, occ in rows:
        print(f"{item_id:<42} {status:<12} {priority:<7} {occ:>3}  {summary}")
    print(f"\nTotal: {len(rows)} items")


def _cmd_auto_approve(args: argparse.Namespace) -> None:
    count = auto_approve_aged_items(days=args.days, run_id="cli-auto-approve")
    print(f"Auto-approved {count} items older than {args.days} days.")


def main(argv: list[str] | None = None) -> None:
    """CLI entry point for backlog management."""
    parser = argparse.ArgumentParser(
        prog="overnight_codex_backlog",
        description="Manage the overnight Codex backlog.",
    )
    sub = parser.add_subparsers(dest="command")

    p_approve = sub.add_parser("approve", help="Approve a proposed item")
    p_approve.add_argument("item_id")
    p_approve.set_defaults(func=_cmd_approve)

    p_reject = sub.add_parser("reject", help="Reject (supersede) an item")
    p_reject.add_argument("item_id")
    p_reject.set_defaults(func=_cmd_reject)

    p_list = sub.add_parser("list", help="List backlog items")
    p_list.add_argument("--status", default="", help="Filter by status")
    p_list.set_defaults(func=_cmd_list)

    p_auto = sub.add_parser("auto-approve", help="Auto-approve aged items")
    p_auto.add_argument(
        "--days", type=int, default=7,
        help="Approve proposed items older than N days (default: 7)",
    )
    p_auto.set_defaults(func=_cmd_auto_approve)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
