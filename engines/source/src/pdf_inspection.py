from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import cast
import unicodedata

import fitz

from engines.source.contracts import (
    NormalizationRoute,
    PageLayoutHint,
    PdfTextLayerStatus,
)
from engines.source.src.errors import SourceEngineError
from engines.source.contracts import ErrorCode


_PRESENTATION_FORM_RANGES = (range(0xFB50, 0xFE00), range(0xFE70, 0xFF00))
_CORRUPTION_MARKERS = ("احل", "ادل", "الذل", "كدين", "إلماـ", "··")
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PdfInspectionResult:
    page_count: int
    text_layer_status: PdfTextLayerStatus
    text_encoding: str
    normalization_route: NormalizationRoute
    sample_text: str
    sample_page_number: int | None
    page_layout_hint: PageLayoutHint


def inspect_pdf(path: Path) -> PdfInspectionResult:
    try:
        document = fitz.open(path)
    except Exception as exc:  # noqa: BLE001
        raise SourceEngineError(ErrorCode.PDF_CORRUPT, f"{path.as_posix()}: {exc}") from exc
    try:
        samples = _sample_pages(document)
        status, encoding = _classify_samples(samples)
        route = "pdf_ocr_primary" if status in {
            PdfTextLayerStatus.ABSENT,
            PdfTextLayerStatus.CORRUPT,
        } else "pdf_text_primary"
        sample_text, sample_page = _first_sample(samples)
        return PdfInspectionResult(
            page_count=document.page_count,
            text_layer_status=status,
            text_encoding=encoding,
            normalization_route=NormalizationRoute(route),
            sample_text=sample_text,
            sample_page_number=sample_page,
            page_layout_hint=PageLayoutHint.SINGLE_COLUMN,
        )
    finally:
        document.close()


def _sample_pages(document: fitz.Document) -> list[tuple[int, str]]:
    samples: list[tuple[int, str]] = []
    for page_index in range(document.page_count):
        raw_text = cast(str, document[page_index].get_text("text"))
        if raw_text.strip():
            samples.append((page_index + 1, raw_text))
        if len(samples) == 3:
            break
    return samples


def _classify_samples(
    samples: list[tuple[int, str]],
) -> tuple[PdfTextLayerStatus, str]:
    if not samples:
        return PdfTextLayerStatus.ABSENT, "unknown"
    joined = "\n".join(text for _, text in samples)
    if any(_contains_presentation_forms(text) for _, text in samples):
        return PdfTextLayerStatus.PRESENTATION_FORMS, "presentation_forms"
    if _looks_corrupt(joined):
        return PdfTextLayerStatus.CORRUPT, "mixed"
    return PdfTextLayerStatus.CLEAN, "standard_arabic"


def _contains_presentation_forms(text: str) -> bool:
    return any(ord(char) in block for char in text for block in _PRESENTATION_FORM_RANGES)


def _looks_corrupt(text: str) -> bool:
    normalized = unicodedata.normalize("NFKC", text)
    if _arabic_ratio(normalized) < 0.6:
        return True
    return any(marker in text for marker in _CORRUPTION_MARKERS)


def _arabic_ratio(text: str) -> float:
    relevant = [char for char in text if not char.isspace()]
    if not relevant:
        return 0.0
    arabic = [char for char in relevant if "\u0600" <= char <= "\u06FF"]
    return len(arabic) / len(relevant)


def _first_sample(samples: list[tuple[int, str]]) -> tuple[str, int | None]:
    if not samples:
        return "", None
    page_number, text = samples[0]
    return text, page_number
