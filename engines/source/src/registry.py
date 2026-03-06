"""Source registry — SPEC §3 shared registries.

Simple JSON-on-disk registry for sources.
Single-user system, no concurrent access handling needed.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


class RegistryError(Exception):
    """Raised on registry operation failures."""
    pass


class SourceRegistry:
    """Manages the source registry at library/registries/sources.json."""

    def __init__(self, registry_path: Path):
        self.path = Path(registry_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {"sources": {}, "version": "1.0"}
        return {"sources": {}, "version": "1.0"}

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def exists(self, source_id: str) -> bool:
        return source_id in self._data["sources"]

    def find_by_hash(self, frozen_hash: str) -> str | None:
        """Find a source_id by its frozen composite hash.

        Returns source_id if found, None otherwise.
        Used for duplicate detection.
        """
        for sid, entry in self._data["sources"].items():
            if entry.get("frozen_hash") == frozen_hash:
                return sid
        return None

    def register(
        self,
        source_id: str,
        work_id: str,
        title_arabic: str,
        author_canonical_id: str,
        trust_tier: str,
        frozen_hash: str,
        acquisition_path: str,
    ) -> None:
        """Register a new source in the registry."""
        if self.exists(source_id):
            raise RegistryError(f"SRC_REGISTRY_CONFLICT: Source {source_id} already registered")

        self._data["sources"][source_id] = {
            "source_id": source_id,
            "work_id": work_id,
            "title_arabic": title_arabic,
            "author_canonical_id": author_canonical_id,
            "trust_tier": trust_tier,
            "processing_status": "acquired",
            "frozen_hash": frozen_hash,
            "intake_timestamp": datetime.now(timezone.utc).isoformat(),
            "acquisition_path": acquisition_path,
            "error_detail": None,
        }
        self._save()

    def update_status(self, source_id: str, status: str, error_detail: str | None = None) -> None:
        """Update the processing status of a source."""
        if not self.exists(source_id):
            raise RegistryError(f"Source {source_id} not found in registry")
        self._data["sources"][source_id]["processing_status"] = status
        if error_detail is not None:
            self._data["sources"][source_id]["error_detail"] = error_detail
        self._save()

    def get(self, source_id: str) -> dict | None:
        return self._data["sources"].get(source_id)

    def list_all(self) -> dict[str, dict]:
        return dict(self._data["sources"])
