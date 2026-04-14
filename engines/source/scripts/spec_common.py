from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import cast

import yaml

AtomData = dict[str, object]


@dataclass(frozen=True)
class LoadedAtom:
    atom_id: str
    path: Path
    data: AtomData


def engine_root() -> Path:
    return Path(__file__).resolve().parents[1]


def spec_root(root: Path | None = None) -> Path:
    base = root if root is not None else engine_root()
    return base / "spec"


def schema_path(root: Path | None = None) -> Path:
    return spec_root(root) / "schema.json"


def index_path(root: Path | None = None) -> Path:
    return spec_root(root) / "INDEX.yaml"


def discover_atom_files(root: Path | None = None) -> list[Path]:
    spec_dir = spec_root(root)
    files: list[Path] = []
    for child in sorted(spec_dir.iterdir()):
        if not child.is_dir() or child.name in {"views", "reviews", "interview"}:
            continue
        files.extend(sorted(child.glob("*.yaml")))
    return files


def load_yaml_dict(path: Path) -> AtomData:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"YAML document is not a mapping: {path}")
    return cast(AtomData, raw)


def load_atoms(root: Path | None = None) -> list[LoadedAtom]:
    atoms: list[LoadedAtom] = []
    for path in discover_atom_files(root):
        data = load_yaml_dict(path)
        atom_id = data.get("id")
        if not isinstance(atom_id, str):
            raise ValueError(f"Atom file is missing a string id: {path}")
        atoms.append(LoadedAtom(atom_id=atom_id, path=path, data=data))
    return atoms


def relative_spec_path(path: Path, root: Path | None = None) -> str:
    return path.relative_to(spec_root(root)).as_posix()

