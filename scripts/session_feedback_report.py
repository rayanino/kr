"""Generate a session feedback report comparing plan predictions with actual deliverables.

Reads the plan file, extracts predictions (line counts, test counts, file lists),
compares with git diff --stat and pytest --co, and produces a structured report.

Usage:
    python scripts/session_feedback_report.py <plan_file> <engine_name> [--output <dir>]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def extract_predictions(plan_text: str) -> dict[str, int | list[str]]:
    """Extract numeric predictions from plan text."""
    predictions: dict[str, int | list[str]] = {}

    # Line count: ~550 impl lines, ~620 lines, etc.
    line_match = re.search(
        r"~?([0-9]+)\s*(?:impl(?:ementation)?|source|code)\s*lines?",
        plan_text, re.IGNORECASE,
    )
    if line_match:
        predictions["predicted_impl_lines"] = int(line_match.group(1))

    # Test count: ~38 tests, 38 new tests
    test_match = re.search(
        r"~?([0-9]+)\s*(?:new\s+)?tests?", plan_text, re.IGNORECASE
    )
    if test_match:
        predictions["predicted_tests"] = int(test_match.group(1))

    # File list from backtick-quoted .py paths
    file_patterns = re.findall(r"`([a-zA-Z_/]+\.py)`", plan_text)
    if file_patterns:
        predictions["predicted_files"] = list(set(file_patterns))
        predictions["predicted_file_count"] = len(set(file_patterns))

    # Step count
    step_matches = re.findall(
        r"(?:^|\n)\s*(?:Step|Phase|Task)\s+[0-9]+", plan_text
    )
    if step_matches:
        predictions["predicted_steps"] = len(step_matches)

    return predictions


def get_actual_stats(
    engine_name: str, project_dir: Path
) -> dict[str, int | list[str]]:
    """Get actual deliverables from git and filesystem."""
    actuals: dict[str, int | list[str]] = {}

    # Git diff stat for last commit
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD~1"],
            capture_output=True, text=True, cwd=project_dir, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            summary = lines[-1]
            ins = re.search(r"([0-9]+) insertion", summary)
            dels = re.search(r"([0-9]+) deletion", summary)
            files = re.search(r"([0-9]+) file", summary)
            if ins:
                actuals["actual_insertions"] = int(ins.group(1))
            if dels:
                actuals["actual_deletions"] = int(dels.group(1))
            if files:
                actuals["actual_files_changed"] = int(files.group(1))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Impl lines in engine src
    engine_src = project_dir / "engines" / engine_name / "src"
    if engine_src.exists():
        impl_lines = 0
        for py in engine_src.rglob("*.py"):
            if "__pycache__" not in py.parts:
                try:
                    impl_lines += len(py.read_text(encoding="utf-8").splitlines())
                except OSError:
                    pass
        actuals["actual_impl_lines"] = impl_lines

    # Test count via pytest --co
    engine_tests = project_dir / "engines" / engine_name / "tests"
    if engine_tests.exists():
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(engine_tests), "--co", "-q"],
                capture_output=True, text=True, cwd=project_dir, timeout=30,
            )
            if result.returncode == 0:
                match = re.search(r"([0-9]+) tests?\s", result.stdout)
                if match:
                    actuals["actual_test_count"] = int(match.group(1))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Test lines
    if engine_tests.exists():
        test_lines = 0
        for py in engine_tests.rglob("*.py"):
            if "__pycache__" not in py.parts:
                try:
                    test_lines += len(py.read_text(encoding="utf-8").splitlines())
                except OSError:
                    pass
        actuals["actual_test_lines"] = test_lines

    return actuals


def compute_deltas(
    predictions: dict[str, int | list[str]],
    actuals: dict[str, int | list[str]],
) -> list[dict[str, str | int | float]]:
    """Compute prediction vs actual deltas."""
    deltas: list[dict[str, str | int | float]] = []
    mapping = [
        ("predicted_impl_lines", "actual_impl_lines", "Implementation lines"),
        ("predicted_tests", "actual_test_count", "Test count"),
        ("predicted_file_count", "actual_files_changed", "Files changed"),
    ]
    for pred_key, act_key, label in mapping:
        pred = predictions.get(pred_key)
        act = actuals.get(act_key)
        if isinstance(pred, int) and isinstance(act, int) and pred > 0:
            delta_pct = ((act - pred) / pred) * 100
            deltas.append({
                "metric": label,
                "predicted": pred,
                "actual": act,
                "delta_pct": round(delta_pct, 1),
            })
    return deltas


def format_markdown(report: dict[str, object]) -> str:
    """Format report as markdown."""
    lines = [
        f"# Session Feedback Report -- {report.get('engine', '')}",
        f"*Generated: {report.get('timestamp', '')}*",
        f"*Plan: {report.get('plan_file', '')}*",
        "",
        "## Plan Accuracy",
        "",
        "| Metric | Predicted | Actual | Delta |",
        "|--------|-----------|--------|-------|",
    ]
    deltas = report.get("deltas", [])
    if isinstance(deltas, list):
        for d in deltas:
            if isinstance(d, dict):
                sign = "+" if d.get("delta_pct", 0) >= 0 else ""
                lines.append(
                    f"| {d.get('metric', '')} | {d.get('predicted', '')} | "
                    f"{d.get('actual', '')} | {sign}{d.get('delta_pct', '')}% |"
                )
    lines.extend(["", "## Raw Data", ""])
    actuals = report.get("actuals", {})
    if isinstance(actuals, dict):
        for k, v in actuals.items():
            lines.append(f"- **{k}:** {v}")
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "Usage: session_feedback_report.py <plan_file> <engine_name> "
            "[--output <dir>]"
        )
        return 1

    plan_path = Path(sys.argv[1])
    engine_name = sys.argv[2]
    project_dir = Path.cwd()

    output_dir = (
        project_dir / "engines" / engine_name / "tests" / "session_reports"
    )
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_dir = Path(sys.argv[idx + 1])

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

    if not plan_path.exists():
        print(f"Plan file not found: {plan_path}", file=sys.stderr)
        return 1

    plan_text = plan_path.read_text(encoding="utf-8", errors="ignore")
    predictions = extract_predictions(plan_text)
    actuals = get_actual_stats(engine_name, project_dir)
    deltas = compute_deltas(predictions, actuals)

    report = {
        "timestamp": datetime.now().isoformat(),
        "plan_file": str(plan_path),
        "engine": engine_name,
        "predictions": predictions,
        "actuals": actuals,
        "deltas": deltas,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = output_dir / f"session_{ts}.json"
    json_path.write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )
    md_path = output_dir / f"session_{ts}.md"
    md_path.write_text(format_markdown(report), encoding="utf-8")

    print(f"Session feedback report saved:")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    print()
    print(format_markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
