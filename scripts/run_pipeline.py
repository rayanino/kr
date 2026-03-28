#!/usr/bin/env python3
"""Pipeline runner — tracer bullet.

Chains all 7 engines sequentially, validating output contracts
at each boundary using Pydantic model_validate().
"""

import json
import sys
import time
import traceback
from pathlib import Path

# Add project root to path
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))


def validate_json_against_model(json_path: Path, model_cls, label: str) -> list[str]:
    """Validate a JSON file against a Pydantic model.
    
    Returns list of validation errors (empty if valid).
    """
    errors = []
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        model_cls.model_validate(data)
    except Exception as e:
        errors.append(f"[{label}] Validation failed: {e}")
    return errors


def run_pipeline(
    fixture_path: Path,
    work_dir: Path,
    traces_dir: Path | None = None,
) -> dict:
    """Run the full 7-engine pipeline on a fixture.

    When *traces_dir* is provided, wraps the run in a recursive-improve
    session that captures all LLM call traces for later analysis.

    Returns a report dict with results and errors.
    """
    work_dir.mkdir(parents=True, exist_ok=True)

    # ── Optional trace capture via recursive-improve ──────────────
    ri_session = None
    if traces_dir:
        try:
            import recursive_improve as ri

            ri.patch()  # captures SDK-based LLM calls (consensus, instructor)
            ri_session = ri.session(
                traces_dir=str(traces_dir),
                metadata={"engine": "pipeline", "fixture": str(fixture_path)},
            )
            ri_session.__enter__()
            print(f"  Traces enabled: {traces_dir}")
        except ImportError:
            print("  WARNING: recursive-improve not installed, traces disabled")

    report = {
        "fixture": str(fixture_path),
        "stages": [],
        "boundary_errors": [],
        "total_errors": 0,
        "success": False,
    }

    # Define pipeline stages
    stages = [
        {
            "name": "source",
            "module": "engines.source.src.tracer",
            "input": str(fixture_path),
            "output": str(work_dir / "01_source_metadata.json"),
            "config": {},
        },
        {
            "name": "normalization",
            "module": "engines.normalization.src.tracer",
            "input": str(work_dir / "01_source_metadata.json"),
            "output": str(work_dir / "02_normalized_package.json"),
            "config": {},
        },
        {
            "name": "passaging",
            "module": "engines.passaging.src.tracer",
            "input": str(work_dir / "02_normalized_package.json"),
            "output": str(work_dir / "03_passage_stream.json"),
            "config": {},
        },
        {
            "name": "atomization",
            "module": "engines.atomization.src.tracer",
            "input": str(work_dir / "03_passage_stream.json"),
            "output": str(work_dir / "04_atom_stream.json"),
            "config": {},
        },
        {
            "name": "excerpting",
            "module": "engines.excerpting.src.tracer",
            "input": str(work_dir / "04_atom_stream.json"),
            "output": str(work_dir / "05_excerpt_stream.json"),
            "config": {
                "passage_stream_path": str(work_dir / "03_passage_stream.json"),
            },
        },
        {
            "name": "taxonomy",
            "module": "engines.taxonomy.src.tracer",
            "input": str(work_dir / "05_excerpt_stream.json"),
            "output": str(work_dir / "06_taxonomy_output.json"),
            "config": {},
        },
        {
            "name": "synthesis",
            "module": "engines.synthesis.src.tracer",
            "input": str(work_dir / "06_taxonomy_output.json"),
            "output": str(work_dir / "07_entry.json"),
            "config": {
                "excerpt_stream_path": str(work_dir / "05_excerpt_stream.json"),
                "source_metadata_path": str(work_dir / "01_source_metadata.json"),
            },
        },
    ]

    # Run each stage
    for stage in stages:
        stage_report = {
            "name": stage["name"],
            "input": stage["input"],
            "output": stage["output"],
            "success": False,
            "duration_ms": 0,
            "error": None,
        }

        print(f"\n{'='*60}")
        print(f"  Stage: {stage['name']}")
        print(f"{'='*60}")

        t0 = time.time()
        try:
            # Import and run the engine
            mod = __import__(stage["module"], fromlist=["process"])
            mod.process(
                input_path=Path(stage["input"]),
                output_path=Path(stage["output"]),
                config=stage["config"],
            )
            stage_report["success"] = True
            stage_report["duration_ms"] = int((time.time() - t0) * 1000)
            print(f"  ✓ Completed in {stage_report['duration_ms']}ms")

            # Show output size
            out_path = Path(stage["output"])
            if out_path.exists():
                size = out_path.stat().st_size
                print(f"  Output: {size:,} bytes")

        except Exception as e:
            stage_report["error"] = f"{type(e).__name__}: {e}"
            stage_report["duration_ms"] = int((time.time() - t0) * 1000)
            print(f"  ✗ FAILED: {e}")
            traceback.print_exc()

        report["stages"].append(stage_report)

    # Validate contracts at each boundary
    print(f"\n{'='*60}")
    print(f"  Contract Validation")
    print(f"{'='*60}")

    boundary_validations = _get_boundary_validations(work_dir)
    for bv in boundary_validations:
        label = bv["label"]
        json_path = Path(bv["json_path"])
        
        if not json_path.exists():
            msg = f"[{label}] Output file missing: {json_path}"
            report["boundary_errors"].append(msg)
            print(f"  ✗ {msg}")
            continue

        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            if "model" in bv:
                model_cls = bv["model"]
                model_cls.model_validate(data)
                print(f"  ✓ {label}: valid")
            elif "validator_fn" in bv:
                errs = bv["validator_fn"](data)
                if errs:
                    for err in errs:
                        msg = f"[{label}] {err}"
                        report["boundary_errors"].append(msg)
                    print(f"  ✗ {label}: {len(errs)} error(s)")
                    for err in errs[:3]:
                        print(f"    {str(err)[:200]}")
                else:
                    print(f"  ✓ {label}: valid")
        except Exception as e:
            msg = f"[{label}] {type(e).__name__}: {e}"
            report["boundary_errors"].append(msg)
            print(f"  ✗ {label}: FAILED")
            # Print first 500 chars of error
            err_str = str(e)[:500]
            print(f"    {err_str}")

    report["total_errors"] = (
        sum(1 for s in report["stages"] if not s["success"])
        + len(report["boundary_errors"])
    )
    report["success"] = report["total_errors"] == 0

    # Print summary
    print(f"\n{'='*60}")
    print(f"  PIPELINE SUMMARY")
    print(f"{'='*60}")
    for s in report["stages"]:
        status = "✓" if s["success"] else "✗"
        print(f"  {status} {s['name']}: {s['duration_ms']}ms")
    print(f"\n  Boundary errors: {len(report['boundary_errors'])}")
    print(f"  Total errors: {report['total_errors']}")
    print(f"  Overall: {'SUCCESS' if report['success'] else 'FAILED'}")

    # ── Finalize trace session ───────────────────────────────────
    if ri_session is not None:
        ri_session.finish(
            output=json.dumps(
                {"success": report["success"], "total_errors": report["total_errors"]},
            ),
            success=report["success"],
        )
        ri_session.__exit__(None, None, None)
        print(f"\n  Traces written to: {traces_dir}")

    # Save report
    report_path = work_dir / "pipeline_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  Report saved: {report_path}")

    return report


def _get_boundary_validations(work_dir: Path) -> list[dict]:
    """Define contract validations for each pipeline boundary.
    
    We validate each engine's output against its own output contract model.
    This catches structural issues before the next engine tries to read.
    
    Each entry has either:
    - "model": a Pydantic model class (validated via model_validate on the whole JSON)
    - "validator_fn": a callable(data) -> list[str] of errors (for custom structures)
    """
    # Import contract models (only core ones)
    from engines.source.contracts import SourceMetadata
    from engines.normalization.contracts import NormalizedPackage
    from engines.passaging.contracts import PassageStream
    from engines.atomization.contracts import AtomStream
    from engines.excerpting.contracts import ExcerptStream
    from engines.taxonomy.contracts import PlacedExcerptAdditions, TreeNode

    def _validate_taxonomy_output(data: dict) -> list[str]:
        """Validate taxonomy output's placements and tree against contracts."""
        errors = []
        # Validate tree
        tree = data.get("tree")
        if tree is None:
            errors.append("Missing 'tree' key in taxonomy output")
        else:
            try:
                TreeNode.model_validate(tree)
            except Exception as e:
                errors.append(f"tree: {e}")

        # Validate each placement
        placements = data.get("placements", [])
        if not placements:
            errors.append("No placements in taxonomy output")
        for i, p in enumerate(placements):
            try:
                PlacedExcerptAdditions.model_validate(p)
            except Exception as e:
                errors.append(f"placements[{i}]: {e}")
                if i >= 2:  # Cap at 3 errors to avoid flood
                    errors.append(f"... and {len(placements) - i - 1} more placements not checked")
                    break
        return errors

    return [
        {
            "label": "source → normalization",
            "json_path": str(work_dir / "01_source_metadata.json"),
            "model": SourceMetadata,
        },
        {
            "label": "normalization → passaging",
            "json_path": str(work_dir / "02_normalized_package.json"),
            "model": NormalizedPackage,
        },
        {
            "label": "passaging → atomization",
            "json_path": str(work_dir / "03_passage_stream.json"),
            "model": PassageStream,
        },
        {
            "label": "atomization → excerpting",
            "json_path": str(work_dir / "04_atom_stream.json"),
            "model": AtomStream,
        },
        {
            "label": "excerpting → taxonomy",
            "json_path": str(work_dir / "05_excerpt_stream.json"),
            "model": ExcerptStream,
        },
        {
            "label": "taxonomy → synthesis",
            "json_path": str(work_dir / "06_taxonomy_output.json"),
            "validator_fn": _validate_taxonomy_output,
        },
    ]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the KR pipeline tracer bullet")
    parser.add_argument(
        "--fixture",
        type=str,
        default="tests/fixtures/html_export_minimal",
        help="Path to input fixture directory",
    )
    parser.add_argument(
        "--work-dir",
        type=str,
        default="tmp/tracer_run",
        help="Working directory for intermediate outputs",
    )
    parser.add_argument(
        "--traces",
        type=str,
        default=None,
        help="Directory for recursive-improve traces (enables LLM call tracing)",
    )
    args = parser.parse_args()

    fixture = Path(args.fixture)
    if not fixture.is_absolute():
        fixture = _root / fixture
    work = Path(args.work_dir)
    if not work.is_absolute():
        work = _root / work

    traces = Path(args.traces) if args.traces else None
    if traces and not traces.is_absolute():
        traces = _root / traces

    report = run_pipeline(fixture, work, traces_dir=traces)
    sys.exit(0 if report["success"] else 1)
