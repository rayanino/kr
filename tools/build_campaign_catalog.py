#!/usr/bin/env python3
"""Build a structured catalog of a campaign run for downstream analysis.

Usage:
    python tools/build_campaign_catalog.py --root integration_tests/campaign_20260331
    python tools/build_campaign_catalog.py --root integration_tests/campaign_20260331 --output-dir analysis

Produces 6 files in the output directory:
  1. run_fingerprint.json   — campaign identity and aggregate stats
  2. package_summary.json   — per-package quality metrics
  3. excerpt_catalog.jsonl   — one row per excerpt with key fields
  4. trace_catalog.jsonl     — one row per LLM call with provenance
  5. function_summary.json   — (package, primary_function) distribution
  6. self_containment_summary.json — (package, self_containment) distribution
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace",
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace",
    )

REPO_ROOT = Path(__file__).resolve().parents[1]

PACKAGES = ["ext_39_masala", "ext_46_qa", "ibn_aqil_v1", "ibn_aqil_v3", "taysir"]


def read_json(path: Path) -> Any:
    """Read a JSON file with UTF-8 encoding."""
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file, returning empty list if missing."""
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            rows.append(json.loads(stripped))
    return rows


def write_json(path: Path, data: Any) -> None:
    """Write JSON with UTF-8 encoding, no ASCII escaping."""
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write JSONL with UTF-8 encoding."""
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def sha256_text(text: str) -> str:
    """Compute SHA-256 hex digest of text encoded as UTF-8."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def count_arabic_words(text: str) -> int:
    """Count whitespace-delimited tokens containing Arabic characters."""
    count = 0
    for token in text.split():
        for ch in token:
            if "\u0600" <= ch <= "\u06ff":
                count += 1
                break
    return count


def build_run_fingerprint(
    root: Path, summary: dict[str, Any], packages_meta: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Build run_fingerprint.json."""
    first_meta = next(iter(packages_meta.values()), {})
    config = first_meta.get("config", {})
    git_commit = first_meta.get("git_commit", "unknown")

    per_package_counts: dict[str, dict[str, int]] = {}
    total_raw_responses = 0
    for pkg_name in PACKAGES:
        pkg_dir = root / pkg_name
        resp_dir = pkg_dir / "raw_llm_responses"
        req_dir = pkg_dir / "raw_llm_requests"
        resp_count = len(list(resp_dir.glob("*.json"))) if resp_dir.exists() else 0
        req_count = len(list(req_dir.glob("*.json"))) if req_dir.exists() else 0
        total_raw_responses += resp_count
        pkg_summary = summary.get("packages", {}).get(pkg_name, {})
        per_package_counts[pkg_name] = {
            "excerpts": pkg_summary.get("excerpt_count", 0),
            "errors": pkg_summary.get("error_count", 0),
            "raw_responses": resp_count,
            "raw_requests": req_count,
        }

    return {
        "campaign_id": f"campaign_{root.name}",
        "timestamp": summary.get("timestamp", "unknown"),
        "git_commit": git_commit,
        "git_dirty": first_meta.get("git_dirty", None),
        "config": config,
        "per_package_counts": per_package_counts,
        "total_excerpts": summary.get("totals", {}).get("total_excerpts", 0),
        "total_errors": summary.get("totals", {}).get("total_errors", 0),
        "total_cost_estimate": summary.get("totals", {}).get("total_cost_estimate", 0),
        "total_time_seconds": summary.get("totals", {}).get("total_time_seconds", 0),
        "total_raw_responses": total_raw_responses,
    }


def build_package_summary(
    root: Path, summary: dict[str, Any], packages_meta: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build package_summary.json — one row per package."""
    rows: list[dict[str, Any]] = []
    for pkg_name in PACKAGES:
        pkg_dir = root / pkg_name
        pkg_summary = summary.get("packages", {}).get(pkg_name, {})
        meta = packages_meta.get(pkg_name, {})
        source_meta = meta.get("source_metadata", {})

        # Count validation drops and phase failures
        drops = read_jsonl(pkg_dir / "validation_drops.jsonl")
        phase2a_failures = read_jsonl(pkg_dir / "phase2a_failures.jsonl")
        phase2b_failures = read_jsonl(pkg_dir / "phase2b_failures.jsonl")

        rows.append({
            "package": pkg_name,
            "genre": source_meta.get("science", "unknown"),
            "author": source_meta.get("author_name", "unknown"),
            "work_title": source_meta.get("work_title", "unknown"),
            "excerpt_count": pkg_summary.get("excerpt_count", 0),
            "error_count": pkg_summary.get("error_count", 0),
            "validation_drops": len(drops),
            "phase2a_failures": len(phase2a_failures),
            "phase2b_failures": len(phase2b_failures),
            "time_seconds": pkg_summary.get("time_seconds", 0),
            "cost_estimate": pkg_summary.get("cost_estimate", 0),
            "status": pkg_summary.get("status", "unknown"),
        })
    return rows


def build_excerpt_catalog(root: Path) -> list[dict[str, Any]]:
    """Build excerpt_catalog.jsonl — one row per excerpt with key fields."""
    rows: list[dict[str, Any]] = []
    for pkg_name in PACKAGES:
        pkg_dir = root / pkg_name
        excerpts = read_jsonl(pkg_dir / "excerpts.jsonl")
        for exc in excerpts:
            primary_text = exc.get("primary_text", "")
            quoted_scholars = exc.get("quoted_scholars", [])
            evidence_refs = exc.get("evidence_refs", [])
            excerpt_topic = exc.get("excerpt_topic", [])

            rows.append({
                "package": pkg_name,
                "excerpt_id": exc.get("excerpt_id", ""),
                "div_path": exc.get("div_path", []),
                "word_count": count_arabic_words(primary_text),
                "primary_function": exc.get("primary_function", ""),
                "self_containment": exc.get("self_containment", ""),
                "topic_count": len(excerpt_topic),
                "scholar_count": len(quoted_scholars),
                "evidence_count": len(evidence_refs),
                "gate_flags": exc.get("gate_flags", []),
                "review_flags": exc.get("review_flags", []),
                "primary_text_sha256": sha256_text(primary_text),
                "text_snippet": exc.get("text_snippet", ""),
                "excerpt_topic": excerpt_topic,
                "self_containment_notes": exc.get("self_containment_notes"),
                "description_arabic": exc.get("description_arabic", ""),
            })
    return rows


def build_trace_catalog(root: Path) -> list[dict[str, Any]]:
    """Build trace_catalog.jsonl — one row per LLM call."""
    rows: list[dict[str, Any]] = []
    for pkg_name in PACKAGES:
        pkg_dir = root / pkg_name
        resp_dir = pkg_dir / "raw_llm_responses"
        req_dir = pkg_dir / "raw_llm_requests"
        if not resp_dir.exists():
            continue

        # Build request lookup for semantic_phase and chunk_id
        req_lookup: dict[str, dict[str, Any]] = {}
        if req_dir.exists():
            for req_path in sorted(req_dir.glob("*.json")):
                try:
                    req_data = read_json(req_path)
                    call_id = req_data.get("call_id", req_path.stem)
                    req_lookup[call_id] = req_data
                except (json.JSONDecodeError, OSError):
                    continue

        for resp_path in sorted(resp_dir.glob("*.json")):
            try:
                resp = read_json(resp_path)
            except (json.JSONDecodeError, OSError):
                continue

            call_id = resp.get("call_id", resp_path.stem)
            req = req_lookup.get(call_id, {})
            usage = resp.get("usage", {})

            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

            # Estimate cost (rough: $3/M input, $15/M output for Opus)
            model = resp.get("model", req.get("model", "unknown"))
            cost_estimate = 0.0
            if "opus" in model.lower() or "claude" in model.lower():
                cost_estimate = (prompt_tokens * 15 + completion_tokens * 75) / 1_000_000
            elif "gpt" in model.lower():
                cost_estimate = (prompt_tokens * 2 + completion_tokens * 8) / 1_000_000
            elif "mistral" in model.lower():
                cost_estimate = (prompt_tokens * 2 + completion_tokens * 6) / 1_000_000

            rows.append({
                "package": pkg_name,
                "call_id": call_id,
                "semantic_phase": req.get("semantic_phase", _infer_phase(call_id)),
                "chunk_id": req.get("chunk_id", "unknown"),
                "model": model,
                "latency_seconds": resp.get("latency_seconds", 0),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost_estimate": round(cost_estimate, 6),
                "finish_reason": resp.get("finish_reason", "unknown"),
                "has_error": resp.get("finish_reason", "stop") != "stop",
            })
    return rows


def _infer_phase(call_id: str) -> str:
    """Infer semantic phase from call_id prefix when request data missing."""
    for prefix in ("classify", "enrich", "group", "verify", "escalat"):
        if call_id.startswith(prefix):
            return prefix.rstrip("_")
    return "unknown"


def build_function_summary(
    excerpt_catalog: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build function_summary.json — grouped by (package, primary_function)."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in excerpt_catalog:
        key = (row["package"], row["primary_function"])
        groups[key].append(row)

    result: list[dict[str, Any]] = []
    for (pkg, func), items in sorted(groups.items()):
        word_counts = [item["word_count"] for item in items]
        full_count = sum(1 for item in items if item["self_containment"] == "FULL")
        topic_filled = sum(1 for item in items if item["topic_count"] > 0)

        result.append({
            "package": pkg,
            "primary_function": func,
            "count": len(items),
            "median_words": int(median(word_counts)) if word_counts else 0,
            "min_words": min(word_counts) if word_counts else 0,
            "max_words": max(word_counts) if word_counts else 0,
            "full_rate": round(full_count / len(items), 3) if items else 0,
            "topic_fill_rate": round(topic_filled / len(items), 3) if items else 0,
        })
    return result


def build_self_containment_summary(
    excerpt_catalog: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build self_containment_summary.json — grouped by (package, self_containment)."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in excerpt_catalog:
        key = (row["package"], row["self_containment"])
        groups[key].append(row)

    result: list[dict[str, Any]] = []
    for (pkg, sc_level), items in sorted(groups.items()):
        # Collect reasons (self_containment_notes) for PARTIAL/DEPENDENT
        reason_counts: Counter[str] = Counter()
        if sc_level in ("PARTIAL", "DEPENDENT"):
            for item in items:
                note = item.get("self_containment_notes") or ""
                if note:
                    # Truncate to first 80 chars for grouping
                    reason_counts[note[:80]] += 1

        entry: dict[str, Any] = {
            "package": pkg,
            "self_containment": sc_level,
            "count": len(items),
        }
        if reason_counts:
            entry["top_reasons"] = [
                {"reason": reason, "count": count}
                for reason, count in reason_counts.most_common(10)
            ]
        result.append(entry)
    return result


def main() -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Root directory of the campaign run.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: <root>/analysis/).",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = (args.output_dir or root / "analysis").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load campaign-level data
    summary = read_json(root / "SUMMARY.json")
    packages_meta: dict[str, dict[str, Any]] = {}
    for pkg_name in PACKAGES:
        meta_path = root / pkg_name / "run_metadata.json"
        if meta_path.exists():
            packages_meta[pkg_name] = read_json(meta_path)

    # 1. Run fingerprint
    print("Building run_fingerprint.json...")
    fingerprint = build_run_fingerprint(root, summary, packages_meta)
    write_json(output_dir / "run_fingerprint.json", fingerprint)

    # 2. Package summary
    print("Building package_summary.json...")
    pkg_summary = build_package_summary(root, summary, packages_meta)
    write_json(output_dir / "package_summary.json", pkg_summary)

    # 3. Excerpt catalog
    print("Building excerpt_catalog.jsonl...")
    excerpt_catalog = build_excerpt_catalog(root)
    write_jsonl(output_dir / "excerpt_catalog.jsonl", excerpt_catalog)

    # 4. Trace catalog
    print("Building trace_catalog.jsonl...")
    trace_catalog = build_trace_catalog(root)
    write_jsonl(output_dir / "trace_catalog.jsonl", trace_catalog)

    # 5. Function summary
    print("Building function_summary.json...")
    func_summary = build_function_summary(excerpt_catalog)
    write_json(output_dir / "function_summary.json", func_summary)

    # 6. Self-containment summary
    print("Building self_containment_summary.json...")
    sc_summary = build_self_containment_summary(excerpt_catalog)
    write_json(output_dir / "self_containment_summary.json", sc_summary)

    # Print summary
    print(f"\nCatalog complete. Output: {output_dir}")
    print(f"  Excerpts cataloged:  {len(excerpt_catalog)}")
    print(f"  LLM traces:         {len(trace_catalog)}")
    print(f"  Function groups:    {len(func_summary)}")
    print(f"  SC groups:          {len(sc_summary)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
