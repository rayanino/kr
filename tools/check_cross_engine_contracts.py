#!/usr/bin/env python3
"""Cross-engine contract consistency checker.

Run after any CC session that modifies contract types (Pydantic models, enums,
field constraints). Catches boundary breaks BEFORE they reach downstream engines.

Usage:
    python tools/check_cross_engine_contracts.py

Created after Session 3 review failure: normalization changed heading_level from
ge=1 to ge=0, but passaging's DivisionPathEntry still had ge=1. Would have
crashed at runtime on any multi-volume book. Owner caught it; architect didn't.

This script exists so the architect never misses a cross-engine boundary break again.
"""

import ast
import logging
import sys
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINES_DIR = REPO_ROOT / "engines"


def _relpath(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _normalized_type(type_text: str | None) -> str | None:
    if not type_text:
        return type_text
    normalized = type_text.replace(" ", "")
    if normalized.startswith("Optional[") and normalized.endswith("]"):
        return normalized[len("Optional["):-1]
    if "|" in normalized:
        parts = [part for part in normalized.split("|") if part != "None"]
        if len(parts) == 1:
            return parts[0]
    return normalized


def find_contract_files() -> list[Path]:
    """Find all contract files across engines.

    Includes both contracts.py and contracts_core.py. Taxonomy uses
    contracts_core.py as the authoritative runtime contract; contracts.py
    is the legacy full-SPEC model with deferred features.
    """
    files = set(ENGINES_DIR.rglob("contracts.py"))
    files |= set(ENGINES_DIR.rglob("contracts_core.py"))
    return sorted(files)


def extract_field_constraints(filepath: Path) -> dict[str, dict]:
    """Extract Pydantic Field constraints from a contracts file.
    
    Returns dict of {class_name.field_name: {ge, le, type, ...}}.
    """
    content = filepath.read_text(encoding="utf-8")
    fields = {}

    tree = ast.parse(content, filename=str(filepath))
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        current_class = node.name
        for item in node.body:
            if not isinstance(item, ast.AnnAssign):
                continue
            if not isinstance(item.target, ast.Name):
                continue
            if item.value is None or not isinstance(item.value, ast.Call):
                continue

            func = item.value.func
            if not isinstance(func, ast.Name) or func.id != "Field":
                continue

            constraints: dict[str, str] = {}
            for keyword in item.value.keywords:
                if keyword.arg in {"ge", "le", "gt", "lt", "min_length", "max_length"}:
                    constraints[keyword.arg] = ast.unparse(keyword.value).strip()

            if constraints:
                key = f"{current_class}.{item.target.id}"
                fields[key] = {
                    "file": _relpath(filepath),
                    "type": ast.unparse(item.annotation).strip(),
                    "constraints": constraints,
                }

    return fields


def extract_shared_types(filepath: Path) -> dict[str, list[str]]:
    """Extract enum/model names and their values from a contracts file."""
    tree = ast.parse(filepath.read_text(encoding="utf-8"), filename=str(filepath))
    types: dict[str, list[str]] = {}

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(isinstance(base, ast.Name) and base.id.endswith("Enum") for base in node.bases):
            continue

        values: list[str] = []
        for item in node.body:
            if not isinstance(item, ast.Assign) or len(item.targets) != 1:
                continue
            if not isinstance(item.targets[0], ast.Name):
                continue
            try:
                value = ast.literal_eval(item.value)
            except Exception:
                continue
            if isinstance(value, str):
                values.append(value)
        if values:
            types[node.name] = values

    return types


def find_cross_references() -> dict[str, list[str]]:
    """Find which engines import types from other engines."""
    refs = defaultdict(list)

    for py_file in ENGINES_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(py_file))
        except (UnicodeDecodeError, SyntaxError):
            continue

        consumer_engine = None
        parts = py_file.relative_to(ENGINES_DIR).parts
        if parts:
            consumer_engine = parts[0]

        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not node.module:
                continue
            module_parts = node.module.split(".")
            if len(module_parts) != 3 or module_parts[0] != "engines":
                continue
            if module_parts[2] not in {"contracts", "contracts_core"}:
                continue

            source_engine = module_parts[1]
            if not consumer_engine or consumer_engine == source_engine:
                continue

            imported = ", ".join(alias.name for alias in node.names if alias.name != "*").strip()
            if imported:
                refs[f"{source_engine} -> {consumer_engine}"].append(
                    f"{imported} (in {py_file.relative_to(REPO_ROOT)})"
                )

    return refs


def check_enum_consistency() -> list[str]:
    """Check that same-named enums do not silently diverge across contracts."""
    all_types: dict[str, list[dict[str, object]]] = defaultdict(list)
    issues: list[str] = []
    imported_names = {
        entry.split(" (in ", 1)[0]
        for imports in find_cross_references().values()
        for entry in imports
    }

    for contracts_file in find_contract_files():
        engine = contracts_file.relative_to(ENGINES_DIR).parts[0]
        for type_name, values in extract_shared_types(contracts_file).items():
            if type_name not in imported_names:
                continue
            all_types[type_name].append(
                {
                    "engine": engine,
                    "file": _relpath(contracts_file),
                    "values": values,
                }
            )

    for type_name, occurrences in all_types.items():
        if len(occurrences) < 2:
            continue
        value_groups: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
        for occ in occurrences:
            value_groups[tuple(occ["values"])].append(occ)
        if len(value_groups) > 1:
            issue_parts = [f"MISMATCH: enum '{type_name}' has different values:"]
            for _, group in value_groups.items():
                for occ in group:
                    issue_parts.append(
                        f"  {occ['engine']}/{type_name}: {occ['values']} ({occ['file']})"
                    )
            issues.append("\n".join(issue_parts))

    return issues


def check_field_consistency() -> list[str]:
    """Check that shared field names have consistent constraints across engines."""
    all_fields = {}
    issues = []
    
    for contracts_file in find_contract_files():
        fields = extract_field_constraints(contracts_file)
        engine = contracts_file.relative_to(ENGINES_DIR).parts[0]
        
        for key, info in fields.items():
            field_name = key.split(".")[-1]
            if field_name not in all_fields:
                all_fields[field_name] = []
            all_fields[field_name].append({
                "engine": engine,
                "class_field": key,
                **info,
            })
    
    # Fields that are intentionally different across engines (same name, different values by design)
    EXPECTED_DIVERGENT = {"schema_version"}
    
    # Check for mismatches in same-named fields
    for field_name, occurrences in all_fields.items():
        if len(occurrences) < 2:
            continue
        if field_name in EXPECTED_DIVERGENT:
            continue
        
        # Group by constraint values
        constraint_groups = defaultdict(list)
        for occ in occurrences:
            normalized_type = _normalized_type(occ.get("type"))
            constraint_key = str((normalized_type, sorted(occ["constraints"].items())))
            constraint_groups[constraint_key].append(occ)
        
        if len(constraint_groups) > 1:
            issue_parts = [f"MISMATCH: '{field_name}' has different types/constraints:"]
            for _, group in constraint_groups.items():
                for occ in group:
                    issue_parts.append(
                        f"  {occ['engine']}/{occ['class_field']}: "
                        f"type={occ.get('type')} constraints={occ['constraints']} ({occ['file']})"
                    )
            issues.append("\n".join(issue_parts))
    
    return issues


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info("=" * 70)
    logger.info("KR Cross-Engine Contract Consistency Check")
    logger.info("=" * 70)
    logger.info("")

    # 1. Find all contract files
    contract_files = find_contract_files()
    logger.info("Contract files found: %d", len(contract_files))
    for f in contract_files:
        logger.info("  %s", f.relative_to(REPO_ROOT))
    logger.info("")

    # 2. Cross-engine imports
    refs = find_cross_references()
    if refs:
        logger.info("Cross-engine type imports:")
        for direction, imports in sorted(refs.items()):
            logger.info("  %s:", direction)
            for imp in imports:
                logger.info("    %s", imp)
        logger.info("")

    # 3. Field constraint consistency
    issues = check_field_consistency() + check_enum_consistency()
    if issues:
        logger.info("ISSUES FOUND: %d", len(issues))
        logger.info("-" * 50)
        for issue in issues:
            logger.info("%s", issue)
            logger.info("")
        sys.exit(1)
    else:
        logger.info("All shared field constraints are consistent across engines.")
        logger.info("")
        sys.exit(0)


if __name__ == "__main__":
    main()
