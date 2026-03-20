"""Pre-flight: detect Pydantic model instantiations missing explicit None.

Pyright cannot infer that Field(None, ...) means default=None, so every call site
must pass explicit `field=None` for Optional fields that use Field(None) as default.

Usage:
    python scripts/check_pydantic_fields.py <file.py> [--project-dir <dir>]
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


def find_pydantic_models(source: str) -> dict[str, list[str]]:
    """Find BaseModel subclasses -> {ModelName: [optional_field_names_with_field_none]}."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}

    models: dict[str, list[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(_name(b).endswith("BaseModel") for b in node.bases):
            continue

        optional_fields: list[str] = []
        for stmt in node.body:
            if (
                isinstance(stmt, ast.AnnAssign)
                and isinstance(stmt.target, ast.Name)
                and _is_optional(stmt.annotation)
                and _is_field_none(stmt.value)
            ):
                optional_fields.append(stmt.target.id)

        if optional_fields:
            models[node.name] = optional_fields
    return models


def find_missing_none(
    source: str, models: dict[str, list[str]]
) -> list[tuple[int, str, str]]:
    """Find model() calls that omit explicit None for Optional+Field(None) fields."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    issues: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _name(node.func)
        if name not in models:
            continue
        provided = {kw.arg for kw in node.keywords if kw.arg is not None}
        for field in models[name]:
            if field not in provided:
                issues.append((node.lineno, name, field))
    return issues


def _name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _is_optional(ann: ast.expr | None) -> bool:
    if ann is None:
        return False
    if isinstance(ann, ast.Subscript) and _name(ann.value) == "Optional":
        return True
    if isinstance(ann, ast.BinOp) and isinstance(ann.op, ast.BitOr):
        if isinstance(ann.right, ast.Constant) and ann.right.value is None:
            return True
        if isinstance(ann.left, ast.Constant) and ann.left.value is None:
            return True
    return False


def _is_field_none(val: ast.expr | None) -> bool:
    if not isinstance(val, ast.Call):
        return False
    if _name(val.func) != "Field":
        return False
    if val.args and isinstance(val.args[0], ast.Constant) and val.args[0].value is None:
        return True
    return any(
        kw.arg == "default"
        and isinstance(kw.value, ast.Constant)
        and kw.value.value is None
        for kw in val.keywords
    )


def build_model_registry(project_dir: Path) -> dict[str, list[str]]:
    """Scan contracts.py + engine/shared src for Pydantic model definitions."""
    registry: dict[str, list[str]] = {}
    search_patterns = [
        "engines/*/contracts.py",
        "shared/*/contracts.py",
        "engines/*/src/*.py",
        "shared/*/src/*.py",
    ]
    for pattern in search_patterns:
        for py_file in project_dir.glob(pattern):
            try:
                src = py_file.read_text(encoding="utf-8", errors="ignore")
                registry.update(find_pydantic_models(src))
            except OSError:
                continue
    return registry


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: check_pydantic_fields.py <file.py> [--project-dir <dir>]")
        return 1

    target = Path(sys.argv[1])
    if not target.exists() or target.suffix != ".py":
        return 0

    project_dir = Path.cwd()
    if "--project-dir" in sys.argv:
        idx = sys.argv.index("--project-dir")
        if idx + 1 < len(sys.argv):
            project_dir = Path(sys.argv[idx + 1])

    registry = build_model_registry(project_dir)

    target_src = target.read_text(encoding="utf-8", errors="ignore")
    registry.update(find_pydantic_models(target_src))

    if not registry:
        return 0

    issues = find_missing_none(target_src, registry)
    if issues:
        print(f"PYDANTIC FIELD(NONE) CHECK — {target}")
        for line, model, field in issues:
            print(
                f"  {target}:{line}: {model}() missing `{field}=None` "
                f"(pyright can't infer Field(None) default)"
            )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
