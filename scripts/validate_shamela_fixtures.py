"""Validate hand-crafted Shamela fixtures against SHAMELA_HTML_REFERENCE format.

Checks that fixtures match real Shamela HTML patterns, catching divergences
that cause false implementation decisions (Session 2 retrospective).

Usage:
    python scripts/validate_shamela_fixtures.py [fixture_path]
    python scripts/validate_shamela_fixtures.py  # validates all fixtures
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

PAGE_TEXT_START = "<div class='PageText'>"
PAGE_NUM_RE = re.compile(r"\(ص:\s*([٠-٩0-9]+)\s*\)")
PAGE_HEAD_RE = re.compile(
    r"<div\s+class=['\"]PageHead['\"][^>]*>.*?</div>", re.DOTALL
)
METADATA_TITLE_RE = re.compile(r"<span\s+class='title'[^>]*>")
PAGE_NUMBER_SPAN_RE = re.compile(
    r"<span\s+class=['\"]PageNumber['\"][^>]*>"
)
FN_SEPARATOR_RE = re.compile(r"<hr\s+[^>]*width\s*=\s*['\"]?(\d{2,3})")


@dataclass(frozen=True)
class FixtureFinding:
    """One fixture validation finding."""
    path: str
    severity: str
    code: str
    message: str


def _add_finding(
    findings: list[FixtureFinding],
    *,
    path: Path,
    severity: str,
    code: str,
    message: str,
) -> None:
    findings.append(
        FixtureFinding(
            path=str(path),
            severity=severity,
            code=code,
            message=message,
        )
    )


def validate_fixture(path: Path) -> list[FixtureFinding]:
    """Validate a single Shamela HTML fixture. Returns structured findings."""
    findings: list[FixtureFinding] = []

    if path.is_dir():
        htm_files = sorted(
            list(path.glob("*.htm")) + list(path.glob("*.html"))
        )
    else:
        htm_files = [path]

    if not htm_files:
        _add_finding(
            findings,
            path=path,
            severity="error",
            code="missing_html",
            message=f"No .htm/.html files found in {path}",
        )
        return findings

    for htm_file in htm_files:
        try:
            text = htm_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            _add_finding(
                findings,
                path=htm_file,
                severity="error",
                code="invalid_utf8",
                message=f"{htm_file.name}: not valid UTF-8",
            )
            continue

        # Check PageText divs exist
        page_count = text.count(PAGE_TEXT_START)
        if page_count == 0:
            _add_finding(
                findings,
                path=htm_file,
                severity="error",
                code="missing_pagetext",
                message=f"{htm_file.name}: no PageText divs found",
            )
            continue

        # Split into page blocks
        positions: list[int] = []
        start = 0
        while True:
            pos = text.find(PAGE_TEXT_START, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        seen_numbered = False
        for i, pos in enumerate(positions):
            block_start = pos + len(PAGE_TEXT_START)
            block_end = (
                positions[i + 1] if i + 1 < len(positions) else len(text)
            )
            block = text[block_start:block_end]

            has_page_num = PAGE_NUM_RE.search(block) is not None
            has_page_num_span = PAGE_NUMBER_SPAN_RE.search(block) is not None
            has_metadata_title = METADATA_TITLE_RE.search(block) is not None
            has_category = "القسم" in block
            is_metadata_page = not has_page_num and not seen_numbered

            # Check: metadata pages should NOT have PageNumber spans
            if is_metadata_page:
                # This looks like a metadata page
                if has_page_num_span:
                    _add_finding(
                        findings,
                        path=htm_file,
                        severity="warning",
                        code="metadata_has_page_number",
                        message=(
                            f"{htm_file.name} page {i+1}: metadata page has "
                            f"PageNumber span (real Shamela metadata pages don't)"
                        ),
                    )
                if not has_metadata_title:
                    _add_finding(
                        findings,
                        path=htm_file,
                        severity="warning",
                        code="metadata_missing_title_span",
                        message=(
                            f"{htm_file.name} page {i+1}: metadata page missing "
                            f"expected <span class='title'> header"
                        ),
                    )
                if not has_category:
                    _add_finding(
                        findings,
                        path=htm_file,
                        severity="warning",
                        code="metadata_missing_category",
                        message=(
                            f"{htm_file.name} page {i+1}: metadata page missing "
                            f"'القسم' field"
                        ),
                    )
            else:
                seen_numbered = True

            # Check: page numbers should use Arabic-Indic digits
            pn_match = PAGE_NUM_RE.search(block)
            if pn_match:
                digits = pn_match.group(1)
                if any(c.isascii() and c.isdigit() for c in digits):
                    _add_finding(
                        findings,
                        path=htm_file,
                        severity="warning",
                        code="western_page_digits",
                        message=(
                            f"{htm_file.name} page {i+1}: uses Western digits "
                            f"'{digits}' (most Shamela uses Arabic-Indic ٠-٩)"
                        ),
                    )

            # Check: content pages should have PageHead div
            if has_page_num and not PAGE_HEAD_RE.search(block):
                _add_finding(
                    findings,
                    path=htm_file,
                    severity="warning",
                    code="missing_pagehead",
                    message=(
                        f"{htm_file.name} page {i+1}: numbered content page "
                        f"missing PageHead div"
                    ),
                )

            # Check: footnote separator width should be in 80-100 range
            for m in FN_SEPARATOR_RE.finditer(block):
                width = int(m.group(1))
                if width < 80 or width > 100:
                    _add_finding(
                        findings,
                        path=htm_file,
                        severity="warning",
                        code="hr_width_out_of_range",
                        message=(
                            f"{htm_file.name} page {i+1}: <hr> width={width} "
                            f"outside 80-100 range (not a footnote separator)"
                        ),
                    )

        if page_count < 2:
            _add_finding(
                findings,
                path=htm_file,
                severity="warning",
                code="metadata_only_fixture",
                message=(
                    f"{htm_file.name}: fixture has only {page_count} PageText block(s); "
                    f"it may be metadata-only or too small to exercise body-page logic"
                ),
            )

    return findings


def build_summary(findings: list[FixtureFinding], target_count: int) -> dict:
    """Build a machine-readable validation summary."""
    by_severity: dict[str, int] = {"error": 0, "warning": 0}
    by_code: dict[str, int] = {}
    files: dict[str, int] = {}
    for finding in findings:
        by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
        by_code[finding.code] = by_code.get(finding.code, 0) + 1
        files[finding.path] = files.get(finding.path, 0) + 1

    score = max(0, 100 - by_severity.get("error", 0) * 25 - by_severity.get("warning", 0) * 5)
    return {
        "targets_checked": target_count,
        "finding_count": len(findings),
        "by_severity": by_severity,
        "by_code": by_code,
        "affected_files": files,
        "quality_score": score,
        "findings": [asdict(f) for f in findings],
    }


def main() -> int:
    """Validate fixtures and print results."""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Validate Shamela HTML fixtures.")
    parser.add_argument("fixture_path", nargs="?", help="Optional fixture file or directory to validate")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional path to write a machine-readable JSON report")
    parser.add_argument("--fail-on-warning", action="store_true", help="Return non-zero when warnings are present")
    args = parser.parse_args()

    if args.fixture_path:
        targets = [Path(args.fixture_path)]
    else:
        # Validate all fixture directories
        targets = []
        real_dir = Path("tests/fixtures/shamela_real")
        if real_dir.exists():
            targets.extend(
                d for d in sorted(real_dir.iterdir()) if d.is_dir()
            )
        engine_fixtures = Path("engines/normalization/tests/fixtures")
        if engine_fixtures.exists():
            targets.extend(
                f
                for f in sorted(engine_fixtures.glob("*.htm"))
            )

    if not targets:
        print("No fixtures found to validate.")
        return 1

    all_findings: list[FixtureFinding] = []
    for target in targets:
        findings = validate_fixture(target)
        all_findings.extend(findings)
        if findings:
            print(f"\n{target.name}:")
            for finding in findings:
                print(f"  - [{finding.severity.upper()}:{finding.code}] {finding.message}")

    if not all_findings:
        print(f"All {len(targets)} fixtures valid.")
    else:
        summary = build_summary(all_findings, len(targets))
        print(
            f"\n{summary['finding_count']} finding(s) across {len(targets)} targets. "
            f"Score={summary['quality_score']}/100"
        )
        print(
            f"Errors={summary['by_severity'].get('error', 0)} "
            f"Warnings={summary['by_severity'].get('warning', 0)}"
        )
        if args.json_out is not None:
            args.json_out.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"JSON report written to: {args.json_out}")

        if summary["by_severity"].get("error", 0) > 0:
            return 2
        if args.fail_on_warning and summary["by_severity"].get("warning", 0) > 0:
            return 3

    return 0


if __name__ == "__main__":
    sys.exit(main())
