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


def discover_default_targets() -> list[Path]:
    """Discover the default fixture corpus used for evaluation."""
    targets: list[Path] = []
    real_dir = Path("tests/fixtures/shamela_real")
    if real_dir.exists():
        targets.extend(d for d in sorted(real_dir.iterdir()) if d.is_dir())

    extended_dir = Path("tests/fixtures/shamela_extended")
    if extended_dir.exists():
        targets.extend(d for d in sorted(extended_dir.iterdir()) if d.is_dir())

    edge_dir = Path("tests/fixtures/shamela_edge_cases")
    if edge_dir.exists():
        targets.extend(sorted(edge_dir.glob("*.htm")))

    engine_fixtures = Path("engines/normalization/tests/fixtures")
    if engine_fixtures.exists():
        targets.extend(sorted(engine_fixtures.glob("*.htm")))

    return targets


def classify_provenance(path: Path) -> str:
    """Classify fixture provenance for reporting."""
    path_str = str(path).replace("\\", "/")
    if "tests/fixtures/shamela_edge_cases/" in path_str:
        return "edge_extract"
    if "engines/normalization/tests/fixtures/" in path_str:
        return "hand_crafted"
    if "tests/fixtures/shamela_extended/" in path_str:
        return "real_extended"
    if "tests/fixtures/shamela_real/" in path_str:
        if path.name == "13_format_b" or path_str.endswith("/13_format_b"):
            return "synthetic"
        return "real"
    return "unknown"


def load_fixture_category(path: Path) -> str | None:
    """Load edge-case category metadata when available."""
    if path.is_file() and path.suffix == ".htm":
        sidecar = path.with_suffix(".json")
        if sidecar.exists():
            try:
                data = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
            category = data.get("category")
            if isinstance(category, str) and category:
                return category
    return None


def collect_corpus_drift_findings() -> list[FixtureFinding]:
    """Check a few critical fixture corpus docs for obvious count drift."""
    findings: list[FixtureFinding] = []
    readme = Path("tests/fixtures/shamela_real/README.md")
    manifest_path = Path("tests/fixtures/shamela_real/MANIFEST.json")
    if readme.exists() and manifest_path.exists():
        try:
            readme_text = readme.read_text(encoding="utf-8")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            selected_match = re.search(r"Selected:\s*(\d+)\s+fixtures", readme_text)
            if selected_match and isinstance(manifest, dict):
                readme_count = int(selected_match.group(1))
                manifest_count = len(manifest)
                if readme_count != manifest_count:
                    _add_finding(
                        findings,
                        path=readme,
                        severity="warning",
                        code="fixture_count_drift",
                        message=(
                            f"{readme.name}: README says {readme_count} fixtures, "
                            f"but MANIFEST.json contains {manifest_count}"
                        ),
                    )
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    expected_count: int | None = None
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(manifest, dict):
                expected_count = len(manifest)
        except (OSError, json.JSONDecodeError):
            expected_count = None

    if expected_count is not None:
        doc_checks = [
            (
                Path("reference/SHAMELA_COLLECTION.md"),
                re.compile(r"In the repo.*?:\s*(\d+)\s+selected fixtures", re.IGNORECASE | re.DOTALL),
            ),
            (
                Path("engines/source/tests/test_deterministic.py"),
                re.compile(r"all\s+(\d+)\s+Shamela fixtures", re.IGNORECASE),
            ),
        ]
        for doc_path, pattern in doc_checks:
            if not doc_path.exists():
                continue
            try:
                text = doc_path.read_text(encoding="utf-8")
            except OSError:
                continue
            match = pattern.search(text)
            if match:
                doc_count = int(match.group(1))
                if doc_count != expected_count:
                    _add_finding(
                        findings,
                        path=doc_path,
                        severity="warning",
                        code="fixture_doc_count_drift",
                        message=(
                            f"{doc_path.name}: document says {doc_count} fixtures, "
                            f"but shamela_real/MANIFEST.json contains {expected_count}"
                        ),
                    )
    return findings


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


def build_summary(findings: list[FixtureFinding], target_count: int, targets: list[Path]) -> dict:
    """Build a machine-readable validation summary."""
    by_severity: dict[str, int] = {"error": 0, "warning": 0}
    by_code: dict[str, int] = {}
    files: dict[str, int] = {}
    by_provenance: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for finding in findings:
        by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
        by_code[finding.code] = by_code.get(finding.code, 0) + 1
        files[finding.path] = files.get(finding.path, 0) + 1
    for target in targets:
        provenance = classify_provenance(target)
        by_provenance[provenance] = by_provenance.get(provenance, 0) + 1
        category = load_fixture_category(target)
        if category:
            by_category[category] = by_category.get(category, 0) + 1

    score = max(0, 100 - by_severity.get("error", 0) * 25 - by_severity.get("warning", 0) * 5)
    return {
        "targets_checked": target_count,
        "finding_count": len(findings),
        "by_severity": by_severity,
        "by_code": by_code,
        "by_provenance": by_provenance,
        "by_category": by_category,
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
        targets = discover_default_targets()

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
    all_findings.extend(collect_corpus_drift_findings())

    if not all_findings:
        print(f"All {len(targets)} fixtures valid.")
    else:
        summary = build_summary(all_findings, len(targets), targets)
        print(
            f"\n{summary['finding_count']} finding(s) across {len(targets)} targets. "
            f"Score={summary['quality_score']}/100"
        )
        print(
            f"Errors={summary['by_severity'].get('error', 0)} "
            f"Warnings={summary['by_severity'].get('warning', 0)}"
        )
        print(f"Provenance={summary['by_provenance']}")
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
