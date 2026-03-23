#!/usr/bin/env python3
"""Batch push shamela-export-samples to GitHub.

Pushes 23K+ files in manageable batches to avoid the
'remote hung up unexpectedly' error. Resumable — safe to
re-run if interrupted.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO_DIR = Path("shamela-export-samples")
REMOTE_URL = "https://github.com/rayanino/shamela-export-samples.git"
BATCH_SIZE = 500  # top-level entries per commit (~1 GB each)
MAX_RETRIES = 3


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a git command with UTF-8 encoding."""
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd or REPO_DIR,
        env=env,
    )
    if check and result.returncode != 0:
        print(f"  FAILED: {' '.join(cmd[:4])}...")
        print(f"  stderr: {result.stderr[:500]}")
        return result
    return result


def git_push_with_retry(sha: str, attempt: int = 1) -> bool:
    """Push a single commit SHA to remote with retry logic."""
    result = run(
        ["git", "push", "origin", f"{sha}:refs/heads/main"],
        check=False,
    )
    if result.returncode == 0:
        return True
    if attempt < MAX_RETRIES:
        wait = 5 * attempt
        print(f"  Push failed, retrying in {wait}s (attempt {attempt + 1}/{MAX_RETRIES})...")
        time.sleep(wait)
        return git_push_with_retry(sha, attempt + 1)
    return False


def get_committed_files(cwd: Path) -> set[str]:
    """Get set of files already tracked in git."""
    result = run(["git", "ls-files"], cwd=cwd, check=False)
    if result.returncode != 0:
        return set()
    return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()


def get_local_commits() -> list[str]:
    """Get all local commit SHAs in chronological order."""
    result = run(["git", "log", "--reverse", "--format=%H"], check=False)
    if result.returncode != 0 or not result.stdout.strip():
        return []
    return result.stdout.strip().split("\n")


def get_remote_head() -> str | None:
    """Get the remote HEAD SHA, or None if remote is empty."""
    result = run(["git", "ls-remote", "origin", "refs/heads/main"], check=False)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.strip().split()[0]


def main() -> None:
    os.chdir(Path(__file__).resolve().parent.parent)

    if not REPO_DIR.exists():
        print(f"ERROR: {REPO_DIR} not found")
        sys.exit(1)

    # === Step 1: Initialize repo ===
    git_dir = REPO_DIR / ".git"
    if not git_dir.exists():
        print("Initializing git repo...")
        run(["git", "init"])
        run(["git", "config", "http.postBuffer", "524288000"])
        run(["git", "config", "core.autocrlf", "false"])
        run(["git", "config", "pack.windowMemory", "256m"])
        run(["git", "remote", "add", "origin", REMOTE_URL])
    else:
        print("Git repo already initialized, resuming...")
        run(["git", "config", "http.postBuffer", "524288000"])

    # === Step 2: Collect top-level entries ===
    entries = sorted(
        [e.name for e in REPO_DIR.iterdir() if e.name != ".git"],
    )
    print(f"Total top-level entries: {len(entries)}")

    # Check what's already committed
    committed = get_committed_files(REPO_DIR)
    uncommitted = []
    for entry in entries:
        entry_path = REPO_DIR / entry
        if entry_path.is_file():
            if entry not in committed:
                uncommitted.append(entry)
        elif entry_path.is_dir():
            # Check if any file in this dir is uncommitted
            dir_files = list(entry_path.rglob("*"))
            dir_has_new = any(
                str(f.relative_to(REPO_DIR)).replace("\\", "/") not in committed
                for f in dir_files
                if f.is_file()
            )
            if dir_has_new:
                uncommitted.append(entry)

    if uncommitted:
        print(f"Entries to commit: {len(uncommitted)}")
    else:
        print("All entries already committed locally.")

    # === Step 3: Batch commit ===
    total_batches = (len(uncommitted) + BATCH_SIZE - 1) // BATCH_SIZE if uncommitted else 0

    for i in range(0, len(uncommitted), BATCH_SIZE):
        batch = uncommitted[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        print(f"\n[Commit {batch_num}/{total_batches}] Adding {len(batch)} entries...")
        t0 = time.time()

        # Add each entry (file or directory)
        for entry in batch:
            run(["git", "add", "--", entry])

        # Commit
        msg = f"Add batch {batch_num}/{total_batches} ({len(batch)} entries)"
        result = run(["git", "commit", "-m", msg], check=False)
        if result.returncode != 0 and "nothing to commit" in result.stdout:
            print(f"  (already committed, skipping)")
            continue

        elapsed = time.time() - t0
        print(f"  Committed in {elapsed:.1f}s")

    # === Step 4: Push commits one at a time ===
    commits = get_local_commits()
    if not commits:
        print("No commits to push.")
        return

    remote_head = get_remote_head()
    print(f"\nLocal commits: {len(commits)}")
    print(f"Remote HEAD: {remote_head[:8] if remote_head else 'empty'}")

    # Find which commits still need pushing
    if remote_head:
        try:
            start_idx = commits.index(remote_head) + 1
        except ValueError:
            start_idx = 0  # remote diverged, push all
    else:
        start_idx = 0

    remaining = commits[start_idx:]
    if not remaining:
        print("All commits already pushed!")
        return

    print(f"Commits to push: {len(remaining)}\n")

    for i, sha in enumerate(remaining):
        print(f"[Push {i + 1}/{len(remaining)}] {sha[:8]}...", end=" ", flush=True)
        t0 = time.time()

        if git_push_with_retry(sha):
            elapsed = time.time() - t0
            print(f"OK ({elapsed:.1f}s)")
        else:
            print(f"\nFATAL: Push failed after {MAX_RETRIES} retries.")
            print(f"Re-run this script to resume from commit {sha[:8]}.")
            sys.exit(1)

    print(f"\n{'=' * 50}")
    print(f"DONE — All {len(commits)} commits pushed to GitHub.")
    print(f"Repo: https://github.com/rayanino/shamela-export-samples")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
