"""End-to-end DR response digestion orchestrator (Component G).

Chains the full pipeline:
  1. Auto-detect provider (dr_format_detectors)
  2. Parse into findings (process_dr_response)
  3. Cross-reference with existing findings (cross_reference_findings)
  4. Run quality gate (digestion_quality_gate)
  5. Generate follow-up prompts (generate_followup_prompts)

Supports single-file and batch modes.

Usage:
    # Single file
    python scripts/digest_dr.py responses/DR40.md --dr-id DR40

    # Batch: process all .md files in a directory
    python scripts/digest_dr.py responses/ --batch

    # Re-run cross-referencing and follow-ups on existing KB
    python scripts/digest_dr.py --reprocess
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.autonomous_schemas import (
    DRResponse,
    DRTarget,
    DigestionRecord,
    Finding,
    append_jsonl,
    read_jsonl,
)
from scripts.cross_reference_findings import cross_reference, persist_cross_references
from scripts.digestion_quality_gate import (
    build_digestion_record,
    run_quality_gate,
)
from scripts.generate_followup_prompts import generate_followups
from scripts.process_dr_response import persist_results, process_response

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent
KB_DIR = PROJECT_DIR / "overnight_codex" / "autonomous" / "knowledge_base"
FINDINGS_JSONL = KB_DIR / "findings.jsonl"
DIGESTION_LOG = KB_DIR / "digestion_log.jsonl"


# ═══════════════════════════════════════════════════════════════════
# Single-file digestion
# ═══════════════════════════════════════════════════════════════════


def digest_single(
    response_file: Path,
    dr_id: str,
    prompt_id: str = "unknown",
    source: DRTarget | None = None,
    followup_batch: str = "auto",
) -> tuple[DRResponse, list[Finding], str]:
    """Process a single DR response file through the full pipeline.

    Returns (response, findings, verdict).
    """
    logger.info("=" * 60)
    logger.info("DIGESTING: %s (DR ID: %s)", response_file.name, dr_id)
    logger.info("=" * 60)

    # Stage 1-2: Parse
    logger.info("[1/5] Parsing response...")
    response, findings = process_response(response_file, dr_id, prompt_id, source)
    logger.info("  Extracted %d findings", len(findings))

    # Stage 2: Persist raw results
    logger.info("[2/5] Persisting raw findings...")
    persist_results(response, findings)

    # Stage 3: Cross-reference with ALL existing findings
    logger.info("[3/5] Cross-referencing...")
    all_findings_raw = read_jsonl(FINDINGS_JSONL, Finding)
    all_findings: list[Finding] = [f for f in all_findings_raw if isinstance(f, Finding)]
    related_map, contradictions = cross_reference(all_findings)
    persist_cross_references(all_findings, related_map, contradictions)
    logger.info("  %d cross-refs, %d contradictions", len(related_map), len(contradictions))

    # Stage 4: Quality gate
    logger.info("[4/5] Quality gate...")
    # Reload findings (cross-referencing updated them)
    dr_findings_raw = read_jsonl(FINDINGS_JSONL, Finding)
    dr_findings: list[Finding] = [
        f for f in dr_findings_raw
        if isinstance(f, Finding) and f.source_id == dr_id
    ]
    dr_contras = [c for c in contradictions if c.dr_id_a == dr_id or c.dr_id_b == dr_id]
    checks, score, verdict = run_quality_gate(response, dr_findings)

    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        logger.info("  [%s] %s: %s", status, check.name, check.detail)

    # Persist digestion record
    record = build_digestion_record(response, dr_findings, dr_contras, score, verdict)
    append_jsonl(DIGESTION_LOG, record)

    # Stage 5: Generate follow-up prompts (non-fatal — don't crash pipeline)
    logger.info("[5/5] Generating follow-up prompts...")
    try:
        followups = generate_followups(batch=followup_batch)
        logger.info("  %d follow-up prompts generated", len(followups))

        if followups:
            from scripts.autonomous_schemas import append_jsonl as _append
            prompts_dir = KB_DIR / "dr_prompts"
            prompts_dir.mkdir(parents=True, exist_ok=True)
            batch_file = prompts_dir / f"{followup_batch}.jsonl"
            for p in followups:
                _append(batch_file, p)
            logger.info("  Persisted to %s", batch_file)
    except Exception as e:
        logger.warning("Follow-up generation failed (non-fatal): %s", e)

    return response, dr_findings, verdict


# ═══════════════════════════════════════════════════════════════════
# Batch mode
# ═══════════════════════════════════════════════════════════════════


def digest_batch(
    directory: Path,
    followup_batch: str = "auto",
) -> list[tuple[str, str, int]]:
    """Process all .md files in a directory. Returns [(dr_id, verdict, finding_count)]."""
    md_files = sorted(directory.glob("*.md"))
    if not md_files:
        logger.warning("No .md files found in %s", directory)
        return []

    # Check which DRs are already digested
    existing_ids: set[str] = set()
    if DIGESTION_LOG.exists():
        records_raw = read_jsonl(DIGESTION_LOG, DigestionRecord)
        for r in records_raw:
            if isinstance(r, DigestionRecord):
                existing_ids.add(r.dr_id)

    results: list[tuple[str, str, int]] = []
    for md_file in md_files:
        # Derive DR ID from filename (e.g., DR40.md -> DR40)
        dr_id = md_file.stem
        if dr_id in existing_ids:
            logger.info("Skipping %s — already digested", dr_id)
            continue

        _, findings, verdict = digest_single(
            md_file, dr_id, followup_batch=followup_batch,
        )
        results.append((dr_id, verdict, len(findings)))

    return results


# ═══════════════════════════════════════════════════════════════════
# Reprocess mode — re-run cross-referencing and follow-ups
# ═══════════════════════════════════════════════════════════════════


def reprocess_existing() -> None:
    """Re-run cross-referencing and follow-up generation on existing KB."""
    logger.info("Reprocessing existing knowledge base...")

    # Cross-reference
    all_findings_raw = read_jsonl(FINDINGS_JSONL, Finding)
    all_findings: list[Finding] = [f for f in all_findings_raw if isinstance(f, Finding)]

    if not all_findings:
        logger.info("No findings to reprocess.")
        return

    logger.info("Cross-referencing %d findings...", len(all_findings))
    related_map, contradictions = cross_reference(all_findings)
    persist_cross_references(all_findings, related_map, contradictions)

    # Follow-ups
    logger.info("Generating follow-up prompts...")
    followups = generate_followups(batch="reprocess")
    logger.info("Generated %d follow-up prompts", len(followups))

    if followups:
        prompts_dir = KB_DIR / "dr_prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        batch_file = prompts_dir / "reprocess.jsonl"
        for p in followups:
            append_jsonl(batch_file, p)


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="End-to-end DR response digestion orchestrator",
    )
    parser.add_argument(
        "path", nargs="?", type=Path,
        help="DR response file (.md) or directory for batch mode",
    )
    parser.add_argument("--dr-id", help="DR identifier (single-file mode)")
    parser.add_argument("--prompt-id", default="unknown", help="Which prompt this responds to")
    parser.add_argument(
        "--source", choices=["chatgpt_dr", "claude_dr", "gemini_dr"],
        default=None, help="DR source (auto-detected if omitted)",
    )
    parser.add_argument("--batch", action="store_true", help="Batch mode — process all .md in directory")
    parser.add_argument("--reprocess", action="store_true", help="Re-run cross-refs and follow-ups on existing KB")
    parser.add_argument("--followup-batch", default="auto", help="Batch name for follow-up prompts")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.reprocess:
        reprocess_existing()
        return

    if not args.path:
        parser.error("Specify a file/directory path or use --reprocess")

    if args.batch:
        if not args.path.is_dir():
            parser.error(f"Batch mode requires a directory, got: {args.path}")
        results = digest_batch(args.path, args.followup_batch)

        print(f"\n{'=' * 60}")
        print("BATCH DIGESTION COMPLETE")
        print(f"{'=' * 60}")
        for dr_id, verdict, count in results:
            print(f"  {dr_id}: [{verdict}] {count} findings")
        if not results:
            print("  No new files to process.")

    else:
        if not args.dr_id:
            # Default: derive from filename
            args.dr_id = args.path.stem

        if not args.path.is_file():
            parser.error(f"File not found: {args.path}")

        source = DRTarget(args.source) if args.source else None
        response, findings, verdict = digest_single(
            args.path, args.dr_id, args.prompt_id, source, args.followup_batch,
        )

        print(f"\n{'=' * 60}")
        print(f"DIGESTION COMPLETE: {args.dr_id}")
        print(f"{'=' * 60}")
        print(f"  Verdict:       {verdict}")
        print(f"  Findings:      {len(findings)}")
        print(f"  Source:        {response.source.value}")
        print(f"  KB location:   {KB_DIR}")


if __name__ == "__main__":
    main()
