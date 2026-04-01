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

import re
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINES_DIR = REPO_ROOT / "engines"


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
    
    current_class = None
    for line in content.split("\n"):
        # Track class definitions
        class_match = re.match(r"^class (\w+)\(", line)
        if class_match:
            current_class = class_match.group(1)
            continue
        
        if current_class is None:
            continue
        
        # Track field definitions with constraints
        field_match = re.match(
            r"\s+(\w+):\s+.*Field\((.*)\)", line
        )
        if field_match:
            field_name = field_match.group(1)
            field_args = field_match.group(2)
            
            constraints = {}
            for constraint in ["ge", "le", "gt", "lt", "min_length", "max_length"]:
                # Word boundary (\b) prevents matching substrings
                # (e.g., "lt" inside "default")
                c_match = re.search(rf"\b{constraint}\s*=\s*([^,\)]+)", field_args)
                if c_match:
                    constraints[constraint] = c_match.group(1).strip()
            
            if constraints:
                key = f"{current_class}.{field_name}"
                fields[key] = {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "constraints": constraints,
                }
    
    return fields


def extract_shared_types(filepath: Path) -> dict[str, list[str]]:
    """Extract enum/model names and their values from a contracts file."""
    content = filepath.read_text(encoding="utf-8")
    types = {}
    
    current_class = None
    current_values = []
    in_enum = False
    
    for line in content.split("\n"):
        class_match = re.match(r"^class (\w+)\(.*Enum\)", line)
        if class_match:
            if current_class and current_values:
                types[current_class] = current_values
            current_class = class_match.group(1)
            current_values = []
            in_enum = True
            continue
        
        if in_enum and current_class:
            val_match = re.match(r'\s+\w+\s*=\s*"([^"]+)"', line)
            if val_match:
                current_values.append(val_match.group(1))
            elif line.strip() and not line.strip().startswith("#") and not line.strip().startswith('"""'):
                if not line.strip().startswith('"') and "=" not in line:
                    if current_class and current_values:
                        types[current_class] = current_values
                    current_class = None
                    current_values = []
                    in_enum = False
    
    if current_class and current_values:
        types[current_class] = current_values
    
    return types


def find_cross_references() -> dict[str, list[str]]:
    """Find which engines import types from other engines."""
    refs = defaultdict(list)
    
    for py_file in ENGINES_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        
        # Join continuation lines (multi-line imports)
        joined = re.sub(r"\(\s*\n\s*", "(", content)
        joined = re.sub(r",\s*\n\s*", ", ", joined)
        joined = re.sub(r"\s*\n\s*\)", ")", joined)
        
        for line in joined.split("\n"):
            # Single-line import
            import_match = re.match(
                r"from engines\.(\w+)\.contracts import \(?(.+?)\)?$", line
            )
            if import_match:
                source_engine = import_match.group(1)
                imported = import_match.group(2).strip()
                consumer_engine = None
                parts = py_file.relative_to(ENGINES_DIR).parts
                if parts:
                    consumer_engine = parts[0]
                
                if consumer_engine and consumer_engine != source_engine and imported:
                    refs[f"{source_engine} -> {consumer_engine}"].append(
                        f"{imported.strip()} (in {py_file.relative_to(REPO_ROOT)})"
                    )
    
    return refs


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
            constraint_key = str(sorted(occ["constraints"].items()))
            constraint_groups[constraint_key].append(occ)
        
        if len(constraint_groups) > 1:
            issue_parts = [f"MISMATCH: '{field_name}' has different constraints:"]
            for _, group in constraint_groups.items():
                for occ in group:
                    issue_parts.append(
                        f"  {occ['engine']}/{occ['class_field']}: "
                        f"{occ['constraints']} ({occ['file']})"
                    )
            issues.append("\n".join(issue_parts))
    
    return issues


def main():
    print("=" * 70)
    print("KR Cross-Engine Contract Consistency Check")
    print("=" * 70)
    print()
    
    # 1. Find all contract files
    contract_files = find_contract_files()
    print(f"Contract files found: {len(contract_files)}")
    for f in contract_files:
        print(f"  {f.relative_to(REPO_ROOT)}")
    print()
    
    # 2. Cross-engine imports
    refs = find_cross_references()
    if refs:
        print("Cross-engine type imports:")
        for direction, imports in sorted(refs.items()):
            print(f"  {direction}:")
            for imp in imports:
                print(f"    {imp}")
        print()
    
    # 3. Field constraint consistency
    issues = check_field_consistency()
    if issues:
        print(f"ISSUES FOUND: {len(issues)}")
        print("-" * 50)
        for issue in issues:
            print(issue)
            print()
        sys.exit(1)
    else:
        print("All shared field constraints are consistent across engines.")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
