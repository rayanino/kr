from __future__ import annotations

from engines.source.contracts import ErrorCode


class SourceEngineError(RuntimeError):
    def __init__(self, error_code: ErrorCode, detail: str) -> None:
        self.error_code = error_code
        self.detail = detail
        super().__init__(f"{self.error_code.value}: {self.detail}")
