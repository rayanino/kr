from __future__ import annotations

import json
import logging
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from jsonschema.protocols import Validator

from spec_common import (
    LoadedAtom,
    index_path,
    load_atoms,
    relative_spec_path,
    schema_path,
    spec_root,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ValidationResult:
    atoms: list[LoadedAtom]
    errors: list[str]
    by_type: Counter[str]
    by_status: Counter[str]
    by_topic: Counter[str]


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stdout,
    )


def load_schema(root: Path) -> dict[str, object]:
    return cast(
        dict[str, object],
        json.loads(schema_path(root).read_text(encoding="utf-8")),
    )


def load_index_entries(root: Path) -> list[dict[str, object]]:
    raw = yaml.safe_load(index_path(root).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("INDEX.yaml is not a mapping.")
    atoms = raw.get("atoms")
    if not isinstance(atoms, list):
        raise ValueError("INDEX.yaml is missing the atoms list.")
    entries = [entry for entry in atoms if isinstance(entry, dict)]
    if len(entries) != len(atoms):
        raise ValueError("INDEX.yaml contains non-mapping atom entries.")
    return cast(list[dict[str, object]], entries)


def format_error_path(error: ValidationError) -> str:
    if not error.path:
        return "<root>"
    return ".".join(str(part) for part in error.path)


def validate_atoms(
    root: Path,
    validator: Validator,
) -> tuple[list[LoadedAtom], list[str]]:
    errors: list[str] = []
    validated_atoms: list[LoadedAtom] = []
    for atom in load_atoms(root):
        atom_errors = sorted(
            validator.iter_errors(cast(dict[str, Any], atom.data)),
            key=lambda item: list(item.path),
        )
        if atom_errors:
            for error in atom_errors:
                errors.append(
                    f"{relative_spec_path(atom.path, root)}: "
                    f"{format_error_path(error)}: {error.message}"
                )
            continue
        validated_atoms.append(atom)
    return validated_atoms, errors


def check_index_consistency(root: Path, atoms: list[LoadedAtom]) -> list[str]:
    errors: list[str] = []
    spec_dir = spec_root(root)
    index_entries = load_index_entries(root)
    indexed_by_id = {
        cast(str, entry.get("id")): entry
        for entry in index_entries
        if isinstance(entry.get("id"), str)
    }
    atoms_by_id = {atom.atom_id: atom for atom in atoms}

    for atom_id, entry in indexed_by_id.items():
        relative_file = entry.get("file")
        if not isinstance(relative_file, str):
            errors.append(f"INDEX.yaml: atoms[{atom_id}].file: missing string file path")
            continue
        target_path = spec_dir / Path(relative_file)
        if not target_path.exists():
            errors.append(f"INDEX.yaml: {atom_id}: file not found: {relative_file}")
            continue
        atom = atoms_by_id.get(atom_id)
        if atom is None:
            errors.append(f"INDEX.yaml: {atom_id}: entry exists but atom file did not validate")
            continue
        actual_path = relative_spec_path(atom.path, root)
        if actual_path != relative_file:
            errors.append(
                f"INDEX.yaml: {atom_id}: file mismatch, expected {relative_file}, "
                f"found {actual_path}"
            )

    for atom_id, atom in atoms_by_id.items():
        if atom_id not in indexed_by_id:
            errors.append(
                f"{relative_spec_path(atom.path, root)}: id missing from INDEX.yaml: {atom_id}"
            )
    return errors


def check_cross_references(root: Path, atoms: list[LoadedAtom]) -> list[str]:
    errors: list[str] = []
    known_ids = {atom.atom_id for atom in atoms}
    for atom in atoms:
        depends_on = atom.data.get("depends_on")
        if not isinstance(depends_on, list):
            continue
        for index, dependency in enumerate(depends_on):
            if not isinstance(dependency, str):
                errors.append(
                    f"{relative_spec_path(atom.path, root)}: "
                    f"depends_on.{index}: dependency is not a string"
                )
                continue
            if dependency not in known_ids:
                errors.append(
                    f"{relative_spec_path(atom.path, root)}: "
                    f"depends_on.{index}: unknown atom id {dependency}"
                )
    return errors


def build_counters(
    atoms: list[LoadedAtom],
) -> tuple[Counter[str], Counter[str], Counter[str]]:
    by_type = Counter(cast(str, atom.data["type"]) for atom in atoms)
    by_status = Counter(cast(str, atom.data["status"]) for atom in atoms)
    by_topic = Counter(cast(str, atom.data["topic"]) for atom in atoms)
    return by_type, by_status, by_topic


def format_counter(counter: Counter[str]) -> str:
    parts = [f"{key}={counter[key]}" for key in sorted(counter)]
    return ", ".join(parts)


def validate_source_spec(root: Path | None = None) -> ValidationResult:
    base_root = root or Path(__file__).resolve().parents[1]
    schema = load_schema(base_root)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    atoms, errors = validate_atoms(base_root, validator)
    errors.extend(check_index_consistency(base_root, atoms))
    errors.extend(check_cross_references(base_root, atoms))
    by_type, by_status, by_topic = build_counters(atoms)
    return ValidationResult(
        atoms=atoms,
        errors=errors,
        by_type=by_type,
        by_status=by_status,
        by_topic=by_topic,
    )


def main() -> int:
    configure_logging()
    try:
        result = validate_source_spec()
    except Exception as exc:  # noqa: BLE001
        logger.error("Validation failed before completion: %s", exc)
        return 1

    for error in result.errors:
        logger.error("%s", error)

    logger.info("Total atoms: %d", len(result.atoms))
    logger.info("By type: %s", format_counter(result.by_type))
    logger.info("By status: %s", format_counter(result.by_status))
    logger.info("By topic: %s", format_counter(result.by_topic))
    logger.info("Validation errors: %d", len(result.errors))
    return 0 if not result.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
