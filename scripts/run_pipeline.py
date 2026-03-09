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


def run_pipeline(fixture_path: Path, work_dir: Path) -> dict:
    """Run the full 7-engine pipeline on a fixture.
    
    Returns a report dict with results and errors.
    """
    work_dir.mkdir(parents=True, exist_ok=True)
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
            model_cls = bv["model"]
            model_cls.model_validate(data)
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

    # Save report
    report_path = work_dir / "pipeline_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  Report saved: {report_path}")

    return report


def _get_boundary_validations(work_dir: Path) -> list[dict]:
    """Define contract validations for each pipeline boundary.
    
    We validate each engine's output against its own output contract model.
    This catches structural issues before the next engine tries to read.
    """
    # Import contract models (only core ones)
    from engines.source.contracts import SourceMetadata
    from engines.normalization.contracts import NormalizedPackage
    from engines.passaging.contracts import PassageStream
    from engines.atomization.contracts import AtomStream
    from engines.excerpting.contracts import ExcerptStream

    # Note: taxonomy and synthesis outputs are custom structures,
    # not directly validated against their full contract models
    # because the tracer bullet uses simplified output formats.

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
    args = parser.parse_args()

    fixture = Path(args.fixture)
    if not fixture.is_absolute():
        fixture = _root / fixture
    work = Path(args.work_dir)
    if not work.is_absolute():
        work = _root / work

    report = run_pipeline(fixture, work)
    sys.exit(0 if report["success"] else 1)
