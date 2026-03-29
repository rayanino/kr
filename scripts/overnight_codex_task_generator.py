"""Task generator for the isolated Codex overnight runtime."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
from datetime import date as date_type
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.overnight_codex_common import (
        PIPELINE_ORDER,
        PROJECT_DIR,
        OVERNIGHT_CODEX_DIR,
        CodexTaskDef,
        manifest_to_json,
        repo_rel,
        write_json,
    )
except ImportError:
    from overnight_codex_common import (
        PIPELINE_ORDER,
        PROJECT_DIR,
        OVERNIGHT_CODEX_DIR,
        CodexTaskDef,
        manifest_to_json,
        repo_rel,
        write_json,
    )


CREATIVE_TEMPLATES_DIR = OVERNIGHT_CODEX_DIR / "creative_templates"
SAFE_TEMPLATE_ID = re.compile(r"^[a-z0-9_]+/[a-z0-9_]+$")


def _run(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    """Run a subprocess from the repo root."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(PROJECT_DIR),
        timeout=timeout,
        env=env,
        check=False,
    )


def _file_age_hours(path: Path) -> float | None:
    """Return file age in hours."""
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    delta = datetime.now(timezone.utc) - mtime
    return delta.total_seconds() / 3600


def _git_recent_committed_engine_files(hours: int = 72) -> dict[str, list[str]]:
    """Return recently committed engine source files by engine."""
    result = _run(
        [
            "git",
            "log",
            f"--since={hours} hours ago",
            "--name-only",
            "--pretty=format:",
            "--",
            "engines/*/src/*.py",
        ],
        timeout=30,
    )
    by_engine: dict[str, list[str]] = {}
    for raw in result.stdout.splitlines():
        normalized = raw.strip().replace("\\", "/")
        if not normalized.startswith("engines/") or "/src/" not in normalized:
            continue
        parts = normalized.split("/")
        if len(parts) < 4:
            continue
        engine = parts[1]
        by_engine.setdefault(engine, [])
        if normalized not in by_engine[engine]:
            by_engine[engine].append(normalized)
    return by_engine


def detect_focus_engine() -> str:
    """Detect the current engine focus conservatively."""
    recent = _git_recent_committed_engine_files()
    if recent:
        ranked = sorted(recent.items(), key=lambda item: (-len(item[1]), item[0]))
        return ranked[0][0]
    next_md = PROJECT_DIR / "NEXT.md"
    if next_md.exists():
        text = next_md.read_text(encoding="utf-8", errors="replace")[:5000]
        for engine in reversed(PIPELINE_ORDER):
            if re.search(rf"\b{engine}\b", text, re.IGNORECASE):
                return engine
    if (PROJECT_DIR / "engines" / "excerpting").exists():
        return "excerpting"
    for engine in reversed(PIPELINE_ORDER):
        if (PROJECT_DIR / "engines" / engine).exists():
            return engine
    return "source"


def generate_core_tasks() -> list[CodexTaskDef]:
    """Tasks that should always appear in the Codex manifest."""
    return [
        CodexTaskDef(
            task_id="val-test-regression",
            name="Regression test snapshot for completed engines",
            category="validation",
            prompt=(
                "Run the full test suite for each completed engine separately:\n"
                "1. python -m pytest engines/source/tests/ -v --tb=short\n"
                "2. python -m pytest engines/normalization/tests/ -v --tb=short\n"
                "3. python -m pytest engines/excerpting/tests/ -v --tb=short\n\n"
                "Summarize total tests, passed, failed, skipped, and the first failure if any. "
                "Do not modify repo files."
            ),
            runner_mode="exec",
            sandbox_mode="read-only",
            write_policy="readonly",
            timeout_minutes=20,
            priority=99,
            bookend=True,
            estimated_complexity="medium",
            expected_artifact="report.json",
        ),
    ]


def scan_recent_changes() -> list[CodexTaskDef]:
    """Review recently committed engine changes and optionally harden them."""
    tasks: list[CodexTaskDef] = []
    recent = _git_recent_committed_engine_files()
    for engine, files in sorted(recent.items()):
        file_list = "\n".join(f"- {path}" for path in files)
        review_id = f"review-recent-{engine}"
        tasks.append(
            CodexTaskDef(
                task_id=review_id,
                name=f"Review recent committed {engine} changes",
                category="review",
                prompt=(
                    f"Review these recently committed {engine} source files:\n{file_list}\n\n"
                    "Focus on structural correctness only:\n"
                    "1. SPEC drift against the governing engine SPEC\n"
                    "2. Missing or weak regression tests\n"
                    "3. Error handling gaps\n"
                    "4. Data-flow / contract preservation risks\n"
                    "5. Unicode / serialization hazards that do not require Arabic domain judgment\n\n"
                    "Do not propose architecture rewrites. Be a bounded employee: identify concrete, "
                    "local improvements with file-path evidence."
                ),
                runner_mode="exec",
                sandbox_mode="read-only",
                write_policy="readonly",
                timeout_minutes=20,
                priority=1,
                estimated_complexity="medium",
                expected_artifact="review.json",
            )
        )
        tasks.append(
            CodexTaskDef(
                task_id=f"harden-recent-{engine}",
                name=f"Harden recent committed {engine} changes",
                category="test",
                prompt=(
                    f"Use the findings from {review_id} to make only bounded hardening changes for "
                    f"the same {engine} files:\n{file_list}\n\n"
                    "Allowed work:\n"
                    "- add or adjust regression tests\n"
                    "- fix confirmed local bugs revealed by those tests\n"
                    "- tighten local validation or error handling when directly justified by the review\n\n"
                    "Not allowed:\n"
                    "- feature work\n"
                    "- new orchestrators or runtime systems\n"
                    "- changes outside the touched engine/tests/shared support needed by the fix\n"
                    "- edits to docs, specs, .claude, or overnight systems"
                ),
                runner_mode="exec",
                sandbox_mode="workspace-write",
                write_policy="guarded_write",
                timeout_minutes=30,
                depends_on=[review_id],
                priority=2,
                estimated_complexity="high",
                expected_artifact="findings.json",
            )
        )
    return tasks


def scan_knowledge_integrity() -> list[CodexTaskDef]:
    """Generate structural integrity probes Codex can own safely."""
    tasks: list[CodexTaskDef] = []
    writer = PROJECT_DIR / "engines" / "excerpting" / "src" / "writer.py"
    deterministic = PROJECT_DIR / "engines" / "excerpting" / "src" / "phase3_deterministic.py"
    if writer.exists():
        tasks.append(
            CodexTaskDef(
                task_id="ki-text-integrity-excerpting",
                name="Probe excerpting writer for byte-preservation regressions",
                category="test",
                prompt=(
                    "Inspect engines/excerpting/src/writer.py and the corresponding tests. "
                    "Focus on byte-preservation and Unicode safety, not Arabic semantic judgment.\n\n"
                    "Write targeted regression tests for any structural risk where serialized output "
                    "could alter bytes, escape significant characters, or drop line breaks. "
                    "Fix only a confirmed local bug needed to make the test pass."
                ),
                runner_mode="exec",
                sandbox_mode="workspace-write",
                write_policy="guarded_write",
                timeout_minutes=30,
                priority=1,
                estimated_complexity="high",
                expected_artifact="findings.json",
            )
        )
    if deterministic.exists():
        tasks.append(
            CodexTaskDef(
                task_id="ki-layer-merge-excerpting",
                name="Probe excerpting layer merge logic for structural attribution bugs",
                category="test",
                prompt=(
                    "Inspect engines/excerpting/src/phase3_deterministic.py for structural bugs in "
                    "layer merging, coverage calculation, and deterministic attribution plumbing.\n\n"
                    "Stay within Codex-safe ground:\n"
                    "- None-author merges\n"
                    "- split-boundary bookkeeping\n"
                    "- duplicate pair handling\n"
                    "- invariant preservation and warning emission\n\n"
                    "Write regression tests first. Fix only directly confirmed local defects."
                ),
                runner_mode="exec",
                sandbox_mode="workspace-write",
                write_policy="guarded_write",
                timeout_minutes=35,
                priority=1,
                estimated_complexity="high",
                expected_artifact="findings.json",
            )
        )
    return tasks


def scan_test_health() -> list[CodexTaskDef]:
    """Generate coverage-matrix tasks for engines with tests."""
    tasks: list[CodexTaskDef] = []
    for engine_tests in sorted(PROJECT_DIR.glob("engines/*/tests")):
        engine = engine_tests.parent.name
        if engine not in PIPELINE_ORDER:
            continue
        result = _run(
            ["python", "-m", "pytest", str(engine_tests), "--co", "-q", "--no-header"],
            timeout=45,
        )
        if result.returncode != 0:
            continue
        test_count = sum(1 for line in result.stdout.splitlines() if "::" in line)
        if not test_count:
            continue
        tasks.append(
            CodexTaskDef(
                task_id=f"test-coverage-{engine}",
                name=f"Map {engine} SPEC section 4 to existing tests",
                category="test",
                prompt=(
                    f"Read engines/{engine}/SPEC.md section 4 and extract the behavioral rules. "
                    f"Then inspect engines/{engine}/tests/ and map which tests cover which rules. "
                    f"Current discovered test count: {test_count}. "
                    "Produce a concrete gap matrix with exact file references. Do not modify code."
                ),
                runner_mode="exec",
                sandbox_mode="read-only",
                write_policy="readonly",
                timeout_minutes=20,
                priority=4,
                estimated_complexity="medium",
                expected_artifact="coverage.json",
            )
        )
    return tasks


def scan_spec_quality() -> list[CodexTaskDef]:
    """Generate local SPEC audit tasks from the existing checker."""
    checker = PROJECT_DIR / "scripts" / "check_spec_quality.py"
    if not checker.exists():
        return []

    tasks: list[CodexTaskDef] = []
    for spec_path in sorted(PROJECT_DIR.glob("engines/*/SPEC.md")):
        engine = spec_path.parent.name
        if engine not in PIPELINE_ORDER:
            continue
        result = _run(["python", str(checker), str(spec_path), "--severity", "high"], timeout=60)
        high_hits = sum(1 for line in result.stdout.lower().splitlines() if "high" in line)
        if high_hits <= 0:
            continue
        tasks.append(
            CodexTaskDef(
                task_id=f"spec-audit-{engine}",
                name=f"Audit local SPEC quality for {engine}",
                category="spec",
                prompt=(
                    f"Audit engines/{engine}/SPEC.md locally. "
                    f"The automated checker reported {high_hits} HIGH-severity findings.\n\n"
                    "Find only concrete local defects:\n"
                    "- contradictions with contracts or code\n"
                    "- ambiguous rules with no executable edge-case behavior\n"
                    "- broken cross-references\n"
                    "- missing failure-mode definitions\n\n"
                    "Do not redesign the engine. Produce local, implementation-safe findings only."
                ),
                runner_mode="exec",
                sandbox_mode="read-only",
                write_policy="readonly",
                timeout_minutes=20,
                priority=5,
                estimated_complexity="medium",
                expected_artifact="audit.json",
            )
        )
    return tasks


def scan_code_quality() -> list[CodexTaskDef]:
    """Produce a structural code-quality scan when local issues are present."""
    issues: list[str] = []
    digit_result = _run(["rg", "-n", r"\\d", "engines/source", "engines/normalization", "engines/excerpting"], timeout=20)
    digit_matches = [
        line for line in digit_result.stdout.splitlines()
        if line.strip() and "tests/" not in line.replace("\\", "/")
    ]
    if digit_matches:
        issues.append(f"\\d regex uses: {len(digit_matches)}")

    bare_except = _run(["rg", "-n", "except:", "engines/source", "engines/normalization", "engines/excerpting"], timeout=20)
    bare_matches = [line for line in bare_except.stdout.splitlines() if line.strip()]
    if bare_matches:
        issues.append(f"bare except handlers: {len(bare_matches)}")

    if not issues:
        return []
    return [
        CodexTaskDef(
            task_id="code-quality-scan",
            name=f"Structural code quality scan ({', '.join(issues)})",
            category="code_quality",
            prompt=(
                "Inspect engines/*/src/ for structural code-quality hazards:\n"
                "1. regex digit traps\n"
                "2. broad exception handling\n"
                "3. silent error swallowing\n"
                "4. missing local regression coverage for risky branches\n\n"
                "Focus on evidence and bounded fixes candidates. Do not modify code."
            ),
            runner_mode="exec",
            sandbox_mode="read-only",
            write_policy="readonly",
            timeout_minutes=15,
            priority=6,
            estimated_complexity="medium",
            expected_artifact="scan.json",
        )
    ]


def scan_contract_boundaries() -> list[CodexTaskDef]:
    """Generate a local contract-boundary validation task."""
    metadata_script = PROJECT_DIR / "scripts" / "verify_metadata_flow.py"
    if not metadata_script.exists():
        return []
    return [
        CodexTaskDef(
            task_id="val-contracts",
            name="Validate cross-engine contracts and metadata flow",
            category="validation",
            prompt=(
                "Inspect the local contract boundaries between adjacent engines.\n\n"
                "Read:\n"
                "- scripts/verify_metadata_flow.py\n"
                "- tools/check_cross_engine_contracts.py\n"
                "- engines/source/contracts.py\n"
                "- engines/normalization/contracts.py\n"
                "- engines/excerpting/contracts.py\n"
                "- engines/taxonomy/contracts.py\n"
                "- engines/synthesis/contracts.py\n\n"
                "Summarize likely mismatches, broken guarantees, and concrete evidence from the code. "
                "Do not modify files and do not attempt to launch scripts."
            ),
            runner_mode="exec",
            sandbox_mode="read-only",
            write_policy="readonly",
            timeout_minutes=15,
            priority=3,
            estimated_complexity="low",
            expected_artifact="boundaries.json",
        )
    ]


def scan_documentation() -> list[CodexTaskDef]:
    """Generate a bounded documentation freshness task."""
    next_md = PROJECT_DIR / "NEXT.md"
    age = _file_age_hours(next_md)
    if age is None or age < 48:
        return []
    return [
        CodexTaskDef(
            task_id="doc-freshness",
            name="Check local docs against committed code reality",
            category="doc",
            prompt=(
                "Audit local operational docs for freshness:\n"
                "- NEXT.md\n"
                "- engine CLAUDE.md files\n"
                "- KNOWN_LIMITATIONS.md files\n\n"
                "Identify factual drift only. Do not rewrite docs and do not propose roadmap changes."
            ),
            runner_mode="exec",
            sandbox_mode="read-only",
            write_policy="readonly",
            timeout_minutes=15,
            priority=7,
            estimated_complexity="low",
            expected_artifact="doc_audit.json",
        )
    ]


def _load_creative_run_log() -> dict[str, str]:
    """Load the creative run log."""
    if not (OVERNIGHT_CODEX_DIR / "creative_run_log.json").exists():
        return {}
    try:
        data = json.loads((OVERNIGHT_CODEX_DIR / "creative_run_log.json").read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        runs = data.get("runs", {})
        return runs if isinstance(runs, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _days_since(date_str: str) -> int:
    """Days since a YYYY-MM-DD string."""
    return (date_type.today() - date_type.fromisoformat(date_str)).days


def _resolve_variable(var_def: dict[str, Any], focus_engine: str) -> str:
    """Resolve a creative template variable."""
    source = var_def.get("source", "literal")
    if source == "focus_engine":
        return focus_engine
    if source == "upstream_engine":
        try:
            idx = PIPELINE_ORDER.index(focus_engine)
        except ValueError:
            return "normalization"
        return PIPELINE_ORDER[max(0, idx - 1)]
    if source == "downstream_engine":
        try:
            idx = PIPELINE_ORDER.index(focus_engine)
        except ValueError:
            return "taxonomy"
        return PIPELINE_ORDER[min(len(PIPELINE_ORDER) - 1, idx + 1)]
    if source == "literal":
        return str(var_def.get("value", ""))
    return str(var_def.get("fallback", ""))


def _validate_template(raw: dict[str, Any], path: Path) -> dict[str, Any] | None:
    """Validate a Codex creative template."""
    required_strings = ["template_id", "name", "description", "prompt_template"]
    for field_name in required_strings:
        if not isinstance(raw.get(field_name), str) or not raw[field_name].strip():
            print(f"  REJECTED template {repo_rel(path)}: invalid {field_name}")
            return None
    template_id = raw["template_id"]
    if not SAFE_TEMPLATE_ID.fullmatch(template_id):
        print(f"  REJECTED template {repo_rel(path)}: unsafe template_id {template_id!r}")
        return None
    capability_flags = raw.get("capability_flags", [])
    if not isinstance(capability_flags, list) or any(not isinstance(v, str) for v in capability_flags):
        print(f"  REJECTED template {repo_rel(path)}: capability_flags must be a list[str]")
        return None
    forbidden = {"requires_web", "requires_arabic_judgment", "generates_arabic_content"} & set(capability_flags)
    if forbidden:
        joined = ", ".join(sorted(forbidden))
        print(f"  REJECTED template {repo_rel(path)}: forbidden capability_flags {joined}")
        return None
    for numeric in ("cooldown_days", "timeout_minutes", "priority"):
        if numeric in raw and not isinstance(raw[numeric], int):
            print(f"  REJECTED template {repo_rel(path)}: {numeric} must be int")
            return None
    if raw.get("write_policy", "readonly") != "readonly":
        print(f"  REJECTED template {repo_rel(path)}: creative templates must stay readonly")
        return None
    if raw.get("sandbox_mode", "read-only") != "read-only":
        print(f"  REJECTED template {repo_rel(path)}: creative templates must stay read-only")
        return None
    if raw.get("runner_mode", "exec") != "exec":
        print(f"  REJECTED template {repo_rel(path)}: unsupported runner_mode")
        return None
    if raw.get("output_mode", "json") != "json":
        print(f"  REJECTED template {repo_rel(path)}: output_mode must be json")
        return None
    variables = raw.get("variables", {})
    if not isinstance(variables, dict):
        print(f"  REJECTED template {repo_rel(path)}: variables must be an object")
        return None
    return raw


def _load_creative_templates() -> list[dict[str, Any]]:
    """Load validated creative templates."""
    templates: list[dict[str, Any]] = []
    if not CREATIVE_TEMPLATES_DIR.exists():
        return templates
    for template_path in sorted(CREATIVE_TEMPLATES_DIR.rglob("*.json")):
        try:
            raw = json.loads(template_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"  REJECTED template {repo_rel(template_path)}: {exc}")
            continue
        validated = _validate_template(raw, template_path)
        if validated is not None:
            templates.append(validated)
    return templates


def scan_creative() -> list[CodexTaskDef]:
    """Generate bounded, local creative tasks."""
    templates = _load_creative_templates()
    if not templates:
        return []
    focus_engine = detect_focus_engine()
    today = date_type.today().isoformat()
    run_log = _load_creative_run_log()
    tasks: list[CodexTaskDef] = []
    for template in templates:
        template_id = template["template_id"]
        cooldown_days = template.get("cooldown_days", 14)
        run_key = f"{template_id}:{focus_engine}"
        last_run = run_log.get(run_key)
        if last_run and _days_since(last_run) < cooldown_days:
            continue

        variables = {
            key: _resolve_variable(value, focus_engine)
            for key, value in template.get("variables", {}).items()
        }
        variables["run_date"] = today
        prompt = template["prompt_template"]
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{key}}}", value)

        task_id = f"creative-{template_id.replace('/', '-')}-{focus_engine}"
        tasks.append(
            CodexTaskDef(
                task_id=task_id,
                name=template["name"].replace("{target}", focus_engine),
                category="creative",
                prompt=prompt,
                runner_mode="exec",
                sandbox_mode="read-only",
                write_policy="readonly",
                model=template.get("model", "gpt-5.4"),
                timeout_minutes=template.get("timeout_minutes", 20),
                priority=template.get("priority", 3),
                estimated_complexity=template.get("estimated_complexity", "medium"),
                output_mode="json",
                expected_artifact="creative.json",
                capability_flags=list(template.get("capability_flags", [])),
                authority_level="low",
            )
        )
    return tasks


def apply_creative_mix_ceiling(tasks: list[CodexTaskDef]) -> list[CodexTaskDef]:
    """Cap creative tasks to roughly 37% of the manifest."""
    hardening = [task for task in tasks if task.category != "creative"]
    creative = [task for task in tasks if task.category == "creative"]
    if not hardening or not creative:
        return tasks
    max_creative = max(1, math.floor(len(hardening) * 37 / 63))
    if len(creative) <= max_creative:
        return tasks
    creative.sort(key=lambda task: (task.priority, task.task_id))
    keep = set(task.task_id for task in creative[:max_creative])
    return [task for task in tasks if task.category != "creative" or task.task_id in keep]


def build_manifest() -> list[CodexTaskDef]:
    """Build the full Codex manifest."""
    all_tasks: list[CodexTaskDef] = []
    all_tasks.extend(generate_core_tasks())

    scanners = [
        ("Knowledge Integrity", scan_knowledge_integrity),
        ("Recent Changes", scan_recent_changes),
        ("Test Health", scan_test_health),
        ("SPEC Quality", scan_spec_quality),
        ("Code Quality", scan_code_quality),
        ("Contract Boundaries", scan_contract_boundaries),
        ("Documentation", scan_documentation),
        ("Creative", scan_creative),
    ]

    print("Scanning repo state for Codex-safe overnight work...")
    for name, scanner in scanners:
        try:
            found = scanner()
            if found:
                print(f"  {name}: {len(found)} tasks")
                all_tasks.extend(found)
        except Exception as exc:
            print(f"  {name}: FAILED ({exc})")

    filtered = apply_creative_mix_ceiling(all_tasks)
    for task in filtered:
        task.validate()
    filtered.sort(key=lambda task: (task.priority, task.task_id))
    return filtered


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Generate Codex overnight tasks")
    parser.add_argument(
        "--output",
        default=str(OVERNIGHT_CODEX_DIR / "manifest.json"),
        help="Where to write the manifest JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print tasks without writing the manifest",
    )
    args = parser.parse_args()

    tasks = build_manifest()
    print(f"Total Codex tasks: {len(tasks)}")
    if args.dry_run:
        for task in tasks:
            deps = f" | depends: {', '.join(task.depends_on)}" if task.depends_on else ""
            print(
                f"  P{task.priority} [{task.write_policy}] {task.task_id}: {task.name}{deps}"
            )
        return

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_path, manifest_to_json(tasks))
    print(f"Manifest written to {repo_rel(output_path)}")


if __name__ == "__main__":
    main()
