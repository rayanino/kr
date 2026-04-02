"""Input-based LLM result caching for the excerpting pipeline.

Caches raw LLM results keyed by the full prompt content (system+user messages).
Any change to the prompt, model, or config auto-invalidates the cache.

Validation gate: results are validated before caching to prevent
poisoning from LLM refusals or empty responses (F6).
"""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, TypeVar

from pydantic import BaseModel, ValidationError  # pyright: ignore[reportMissingImports]

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def compute_cache_key(
    phase: str,
    system_message: str,
    user_message: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    """Compute SHA-256 cache key from all inputs that affect LLM output.

    Hashes the full constructed prompt (not template constants) so that
    any change to prompt construction, source text, or config invalidates.
    Returns first 16 hex chars (64-bit, collision-negligible for corpus sizes).
    """
    payload = json.dumps(
        {
            "phase": phase,
            "system": system_message,
            "user": user_message,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def validate_before_caching(
    phase: str,
    raw_json: str,
    response_model: type[BaseModel],
) -> bool:
    """Reject LLM refusals, empty results, and malformed responses before caching.

    Prevents cache poisoning (F6): only cache results that parse correctly
    AND have non-empty primary fields.
    """
    try:
        parsed = json.loads(raw_json)
        obj = response_model.model_validate(parsed)
        # Phase-specific non-empty checks using getattr for type safety
        if phase == "classify":
            segments = getattr(obj, "segments", None)
            return segments is not None and len(segments) > 0
        if phase == "group":
            units = getattr(obj, "teaching_units", None)
            return units is not None and len(units) > 0
        if phase == "enrich":
            enrichments = getattr(obj, "enrichments", None)
            total_units = getattr(obj, "total_units", None)
            if enrichments is None or total_units is None or len(enrichments) == 0:
                return False
            if len(enrichments) != total_units:
                return False
            raw_unit_indices = [getattr(ue, "unit_index", None) for ue in enrichments]
            if any(index is None for index in raw_unit_indices):
                return False
            unit_indices = sorted(int(index) for index in raw_unit_indices if index is not None)
            return unit_indices == list(range(total_units))
        if phase == "verify":
            items = getattr(obj, "items", None)
            return items is not None and len(items) > 0
        return True
    except (json.JSONDecodeError, ValidationError, AttributeError):
        return False


class CacheManager:
    """Manage LLM result caching with file-based storage.

    Storage layout: {cache_dir}/{phase}/{cache_key}.json
    Each cache entry contains metadata (chunk_id, model, timestamp)
    alongside the raw LLM result for auditability.
    """

    def __init__(self, cache_dir: Path) -> None:
        self._dir = cache_dir

    def _phase_dir(self, phase: str) -> Path:
        """Return the directory for a given phase."""
        return self._dir / phase

    def _entry_path(self, phase: str, cache_key: str) -> Path:
        """Return the file path for a cache entry."""
        return self._phase_dir(phase) / f"{cache_key}.json"

    def load(
        self,
        phase: str,
        cache_key: str,
        response_model: type[T],
    ) -> Optional[T]:
        """Load a cached result if it exists and is valid.

        Returns None on cache miss, corrupt file, or validation failure.
        """
        path = self._entry_path(phase, cache_key)
        if not path.exists():
            return None
        try:
            text = path.read_text(encoding="utf-8")
            entry = json.loads(text)
            raw_result = entry.get("result")
            if raw_result is None:
                logger.warning("Cache entry missing 'result' field: %s", path)
                return None
            raw_json = (
                raw_result
                if isinstance(raw_result, str)
                else json.dumps(raw_result, ensure_ascii=False)
            )
            if not validate_before_caching(phase, raw_json, response_model):
                logger.warning("Cache load rejected poisoned entry for %s/%s", phase, cache_key)
                return None
            # Re-validate on load (cache could be from an older version)
            parsed = json.loads(raw_json)
            obj = response_model.model_validate(parsed)
            logger.debug("Cache hit: %s/%s", phase, cache_key)
            return obj
        except (json.JSONDecodeError, ValidationError, OSError, KeyError) as exc:
            logger.warning("Cache load failed for %s/%s: %s", phase, cache_key, exc)
            return None

    def save(
        self,
        phase: str,
        cache_key: str,
        chunk_id: str,
        model: str,
        result: BaseModel,
    ) -> None:
        """Save an LLM result to cache."""
        import datetime

        phase_dir = self._phase_dir(phase)
        phase_dir.mkdir(parents=True, exist_ok=True)
        raw_result_json = result.model_dump_json()
        if not validate_before_caching(phase, raw_result_json, type(result)):
            logger.warning("Cache save rejected poisoned entry for %s/%s", phase, cache_key)
            return
        entry = {
            "cache_key": cache_key,
            "chunk_id": chunk_id,
            "model": model,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "result": json.loads(raw_result_json),
        }
        path = self._entry_path(phase, cache_key)
        try:
            path.write_text(
                json.dumps(entry, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            logger.warning("Cache save failed for %s/%s: %s", phase, cache_key, exc)
