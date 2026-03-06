"""Normalization engine error codes — SPEC §7.

Every error: code, severity, human-readable message, recovery action.
Principle: never lose data silently.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ErrorSeverity(str, Enum):
    """Error severity levels. Fatal = abort normalization. Warning = continue + flag."""
    FATAL = "fatal"
    WARNING = "warning"
    INFO = "info"


class NormErrorCode(str, Enum):
    """All NORM_* error codes from SPEC §7."""
    UNKNOWN_SOURCE_FORMAT = "NORM_UNKNOWN_SOURCE_FORMAT"
    MISSING_FROZEN = "NORM_MISSING_FROZEN"
    MISSING_METADATA = "NORM_MISSING_METADATA"
    SCHEMA_VIOLATION = "NORM_SCHEMA_VIOLATION"
    OCR_FAILED = "NORM_OCR_FAILED"
    ENCODING_ERROR = "NORM_ENCODING_ERROR"
    LOW_FIDELITY = "NORM_LOW_FIDELITY"
    LAYER_UNCERTAIN = "NORM_LAYER_UNCERTAIN"
    SPARSE_STRUCTURE = "NORM_SPARSE_STRUCTURE"
    FORMAT_MISMATCH = "NORM_FORMAT_MISMATCH"
    PAGE_COUNT_MISMATCH = "NORM_PAGE_COUNT_MISMATCH"
    DUPLICATE_PAGES = "NORM_DUPLICATE_PAGES"
    PARTIAL_PAGE = "NORM_PARTIAL_PAGE"
    OCR_API_RATE_LIMIT = "NORM_OCR_API_RATE_LIMIT"
    WRITE_FAILED = "NORM_WRITE_FAILED"
    UNIT_INDEX_VIOLATION = "NORM_UNIT_INDEX_VIOLATION"
    NO_TEXT_LAYER = "NORM_NO_TEXT_LAYER"
    PAGE_ORDER_CONFLICT = "NORM_PAGE_ORDER_CONFLICT"
    FOOTNOTE_SEPARATOR_ABSENT = "NORM_FOOTNOTE_SEPARATOR_ABSENT"
    DIACRITICS_DRIFT = "NORM_DIACRITICS_DRIFT"


# Severity mapping — SPEC §7 table
ERROR_SEVERITY: dict[NormErrorCode, ErrorSeverity] = {
    NormErrorCode.UNKNOWN_SOURCE_FORMAT: ErrorSeverity.FATAL,
    NormErrorCode.MISSING_FROZEN: ErrorSeverity.FATAL,
    NormErrorCode.MISSING_METADATA: ErrorSeverity.FATAL,
    NormErrorCode.SCHEMA_VIOLATION: ErrorSeverity.FATAL,
    NormErrorCode.OCR_FAILED: ErrorSeverity.FATAL,
    NormErrorCode.ENCODING_ERROR: ErrorSeverity.WARNING,
    NormErrorCode.LOW_FIDELITY: ErrorSeverity.WARNING,
    NormErrorCode.LAYER_UNCERTAIN: ErrorSeverity.WARNING,
    NormErrorCode.SPARSE_STRUCTURE: ErrorSeverity.WARNING,
    NormErrorCode.FORMAT_MISMATCH: ErrorSeverity.INFO,
    NormErrorCode.PAGE_COUNT_MISMATCH: ErrorSeverity.WARNING,
    NormErrorCode.DUPLICATE_PAGES: ErrorSeverity.INFO,
    NormErrorCode.PARTIAL_PAGE: ErrorSeverity.WARNING,
    NormErrorCode.OCR_API_RATE_LIMIT: ErrorSeverity.WARNING,
    NormErrorCode.WRITE_FAILED: ErrorSeverity.FATAL,
    NormErrorCode.UNIT_INDEX_VIOLATION: ErrorSeverity.FATAL,
    NormErrorCode.NO_TEXT_LAYER: ErrorSeverity.FATAL,
    NormErrorCode.PAGE_ORDER_CONFLICT: ErrorSeverity.WARNING,
    NormErrorCode.FOOTNOTE_SEPARATOR_ABSENT: ErrorSeverity.INFO,
    NormErrorCode.DIACRITICS_DRIFT: ErrorSeverity.FATAL,
}


class NormalizationError(Exception):
    """Raised on normalization failures.

    Attributes:
        code: The NORM_* error code.
        severity: Fatal, warning, or info.
        source_id: The source being processed (if known).
        unit_index: The affected page (if page-specific).
        message: Human-readable description.
        recovery: What action to take.
    """

    def __init__(
        self,
        code: NormErrorCode,
        message: str,
        source_id: Optional[str] = None,
        unit_index: Optional[int] = None,
        recovery: str = "",
    ):
        self.code = code
        self.severity = ERROR_SEVERITY[code]
        self.source_id = source_id
        self.unit_index = unit_index
        self.message = message
        self.recovery = recovery
        super().__init__(f"[{code.value}] {message}")

    def to_log_entry(self) -> dict:
        """Structured log entry per SPEC §7 logging requirement."""
        return {
            "error_code": self.code.value,
            "severity": self.severity.value,
            "source_id": self.source_id,
            "unit_index": self.unit_index,
            "message": self.message,
            "recovery": self.recovery,
        }
