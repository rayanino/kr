#!/usr/bin/env python3
"""S-09: Gated Dispatch PromptCard generator.

Reads a draft and an optimized prompt file, computes SHA-256 hashes,
and writes a PromptCard JSON artifact plus an entry in dispatch_log.jsonl.

Usage:
    python scripts/generate_promptcard.py \
        --draft prompts/draft.txt \
        --optimized prompts/optimized.txt \
        --optimizer prompt-architect \
        --target codex \
        --session-id hardening-s4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def compute_sha256(text: str) -> str:
    """Return hex SHA-256 digest of the given text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_promptcard(
    draft_text: str,
    optimized_text: str,
    optimizer_name: str,
    target_agent: str,
    session_id: str,
) -> dict[str, str]:
    """Assemble the PromptCard dictionary."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "draft_prompt": draft_text,
        "optimizer_name": optimizer_name,
        "optimized_prompt": optimized_text,
        "draft_hash": compute_sha256(draft_text),
        "optimized_hash": compute_sha256(optimized_text),
        "timestamp": now,
        "session_id": session_id,
        "target_agent": target_agent,
    }


def write_promptcard(card: dict[str, str], output_dir: Path) -> Path:
    """Write PromptCard JSON and return the written path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ts_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{card['session_id']}_{ts_slug}.json"
    out_path = output_dir / filename
    out_path.write_text(
        json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("PromptCard written to %s", out_path)
    return out_path


def append_dispatch_log(
    card: dict[str, str], promptcard_path: Path, project_root: Path
) -> None:
    """Append an entry to .kr/runtime/dispatch_log.jsonl."""
    log_path = project_root / ".kr" / "runtime" / "dispatch_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": card["timestamp"],
        "target_agent": card["target_agent"],
        "promptcard_id": promptcard_path.name,
        "prompt_architect_used": True,
        "optimized_hash": card["optimized_hash"],
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logger.info("Dispatch log entry appended to %s", log_path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="S-09: Generate a Gated Dispatch PromptCard."
    )
    parser.add_argument(
        "--draft", type=Path, required=True,
        help="Path to the draft prompt text file.",
    )
    parser.add_argument(
        "--optimized", type=Path, required=True,
        help="Path to the optimized prompt text file.",
    )
    parser.add_argument(
        "--optimizer", type=str, required=True,
        help="Name of the optimizer (e.g. prompt-architect).",
    )
    parser.add_argument(
        "--target", type=str, required=True,
        help="Target agent (e.g. codex, gemini, claude-dr).",
    )
    parser.add_argument(
        "--session-id", type=str, required=True,
        help="Current session identifier.",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path(".kr/runtime/promptcards"),
        help="Output directory for PromptCard JSON (default: .kr/runtime/promptcards/).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s"
    )
    args = parse_args(argv)

    project_root = Path(__file__).resolve().parent.parent

    # --- Validate inputs ---
    if not args.draft.exists():
        logger.error("Draft file not found: %s", args.draft)
        return 1
    if not args.optimized.exists():
        logger.error("Optimized file not found: %s", args.optimized)
        return 1

    try:
        draft_text = args.draft.read_text(encoding="utf-8")
        optimized_text = args.optimized.read_text(encoding="utf-8")
    except OSError as exc:
        logger.error("Failed to read input file: %s", exc)
        return 1

    # --- Build and write PromptCard ---
    card = build_promptcard(
        draft_text=draft_text,
        optimized_text=optimized_text,
        optimizer_name=args.optimizer,
        target_agent=args.target,
        session_id=args.session_id,
    )

    try:
        output_dir = (
            project_root / args.output_dir
            if not args.output_dir.is_absolute()
            else args.output_dir
        )
        card_path = write_promptcard(card, output_dir)
    except OSError as exc:
        logger.error("Failed to write PromptCard: %s", exc)
        return 1

    # --- Append dispatch log ---
    try:
        append_dispatch_log(card, card_path, project_root)
    except OSError as exc:
        logger.error("Failed to append dispatch log: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
