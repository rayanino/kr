"""Phase 3: Output Validation (SPEC §7.4).

Final self-validation before output. Checks V-P3-1 through V-P3-9.
"""

from __future__ import annotations

import logging

from engines.excerpting.contracts import (
    ExcerptRecord,
    ExcerptingErrorCodes,
    validate_er_invariants,
)

logger = logging.getLogger(__name__)


def validate_phase3(excerpts: list[ExcerptRecord]) -> list[dict]:
    """Run V-P3-1 through V-P3-9 on all ExcerptRecords (§7.4).

    V-P3-1: excerpt_id uniqueness. Fatal.
    V-P3-2: primary_text integrity (I-ER-2). Fatal.
    V-P3-3: primary_author_layer non-null (I-ER-5). Fatal.
    V-P3-4: self_containment metadata consistency (I-ER-4). Warning.
    V-P3-5: excerpt_topic count 1–3 (I-ER-6). Warning.
    V-P3-6: evidence_refs type consistency (I-ER-7). Warning.
    V-P3-7: gate flags written for all gate triggers. Fatal (EX-M-008).
    V-P3-8: div_path non-empty. Warning.
    V-P3-9: word range validity (start_word <= end_word). Fatal.

    Returns list of validation result dicts with 'check', 'status', 'detail'.
    """
    raise NotImplementedError
