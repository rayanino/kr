"""Validation stub — tracer bullet.

Passes everything. Real implementation will run schema validation,
text integrity checks, and cross-engine consistency checks.
"""

from typing import Any


def validate_output(data: Any, schema: Any = None) -> list[str]:
    """Validate engine output against a schema.
    
    Tracer bullet stub: returns empty list (passes everything).
    """
    return []


def validate_text_integrity(text: str) -> list[str]:
    """Check Arabic text for corruption.
    
    Tracer bullet stub: returns empty list.
    """
    return []
