"""F5 enforcement: Detect stale file path references in .claude/ configuration.

Scans all .md and .sh files in .claude/ for file path patterns and verifies
each referenced path exists in the repository.

Exit codes:
  0 = no stale references found (or only warnings)
  1 = stale references found (advisory, not blocking)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Patterns to extract file paths from markdown/shell files
PATH_PATTERNS = [
    # Backtick-quoted paths with at least one slash
    r'`([a-zA-Z0-9_./-]+/[a-zA-Z0-9_./-]+)`',
    # Markdown links [text](path)
    r'\[(?:[^\]]*)\]\(([a-zA-Z0-9_./-]+/[a-zA-Z0-9_./-]+)\)',
]

# Paths to skip (not real file references)
SKIP_PATTERNS = [
    "http", "https", "#", "$", "{", "CLAUDE_", "example", "e.g.",
    "//", "*.py", "*.md", "*.sh", "*.json",  # Glob patterns
    "engines/<", "shared/<", "<n>", "<file>", "<path>",  # Template patterns
]


def extract_paths(content: str) -> list[str]:
    """Extract file path references from markdown/shell content."""
    paths: list[str] = []
    for pattern in PATH_PATTERNS:
        for match in re.finditer(pattern, content):
            path = match.group(1).strip()
            # Clean trailing punctuation
            path = path.rstrip(".,;:)")
            # Skip if too short or matches skip patterns
            if len(path) < 8:
                continue
            if any(skip in path for skip in SKIP_PATTERNS):
                continue
            paths.append(path)
    return paths


def scan_directory(claude_dir: Path, project_root: Path) -> list[tuple[str, str]]:
    """Scan .claude/ for stale references. Returns [(source_file, stale_path)]."""
    stale: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for ext in ("*.md", "*.sh"):
        for file_path in claude_dir.rglob(ext):
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            rel_source = str(file_path.relative_to(project_root))
            for ref_path in extract_paths(content):
                full_path = project_root / ref_path
                if not full_path.exists():
                    key = (rel_source, ref_path)
                    if key not in seen:
                        seen.add(key)
                        stale.append((rel_source, ref_path))

    return stale


def main() -> int:
    project_root = Path.cwd()
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])

    claude_dir = project_root / ".claude"
    if not claude_dir.exists():
        print("No .claude/ directory found.", file=sys.stderr)
        return 0

    stale = scan_directory(claude_dir, project_root)

    if not stale:
        print("No stale references found in .claude/ files.")
        return 0

    print(f"Found {len(stale)} stale file reference(s) in .claude/ files:\n")
    for source, ref in sorted(stale):
        print(f"  {source}: -> {ref}")

    print(f"\nTotal: {len(stale)} stale references")
    return 1


if __name__ == "__main__":
    sys.exit(main())
