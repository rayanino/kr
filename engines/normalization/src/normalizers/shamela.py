"""Shamela HTML normalizer — SPEC §4.A.2.

Transforms Shamela desktop HTML exports into KR normalized packages.
This is the most mature normalizer — ABD-era code (1123 lines) handles
basic content/footnote separation. The KR upgrade adds:
- Output schema upgrade (ABD JSONL → KR normalized package format)
- Footnote type classification (Pass 2 upgrade)
- Multi-layer detection (Pass 5 — new capability)
- Content flagging expansion (Quran/hadith detection)
- Content census (post-processing statistics)
- Per-page text fidelity scoring
- Diacritics preservation verification
- Atomic write procedure

ABD code location: reference/archive/abd_code/normalization/normalize_shamela.py
ABD spec: engines/normalization/reference/ABD_NORMALIZATION_SPEC.md
Shamela HTML format reference: engines/normalization/reference/SHAMELA_HTML_REFERENCE.md

Processing pipeline (6 passes):
  Pass 1 — HTML parsing and page extraction (ABD §4.1–§4.4, deterministic)
  Pass 2 — Content/footnote separation + type classification (ABD §4.5–§4.6, upgraded)
  Pass 3 — HTML stripping and text cleaning (ABD §4.7–§4.9, deterministic)
  Pass 4 — Structure discovery (ABD discover_structure.py, integrated)
  Pass 5 — Multi-layer detection [NEW]
  Pass 6 — Output generation + validation + atomic write [NEW]

Implementation order: Build incrementally per IMPL_BRIEF.md.
"""

from __future__ import annotations

from pathlib import Path

from engines.normalization.contracts import NormalizedPackage
from engines.normalization.src.normalizers.base import BaseNormalizer
from engines.normalization.src.errors import NormalizationError, NormErrorCode
from engines.source.contracts import SourceMetadata


class ShamelaNormalizer(BaseNormalizer):
    """SPEC §4.A.2: Shamela HTML → KR normalized package.

    Internally uses 6 passes. ABD code provides the foundation for Passes 1–3.
    Pass 4 integrates existing discover_structure.py.
    Passes 5–6 are new KR capabilities.
    """

    def validate_input(
        self,
        frozen_path: Path,
        metadata: SourceMetadata,
    ) -> None:
        """SPEC §5 check 9: Verify at least one PageText div exists.

        Also verifies:
        - frozen_path directory exists and is non-empty
        - At least one .htm or .html file present
        - Files are valid UTF-8
        """
        # TODO (Claude Code): Implement. See SPEC §5 check 9 and §4.A.2 input description.
        raise NotImplementedError("ShamelaNormalizer.validate_input")

    def normalize(
        self,
        frozen_path: Path,
        metadata: SourceMetadata,
    ) -> NormalizedPackage:
        """Execute the 6-pass pipeline.

        See SPEC §4.A.2 for complete behavioral specification of each pass.
        See IMPL_BRIEF.md for implementation order.
        """
        # TODO (Claude Code): Implement the 6-pass pipeline.
        # Phase 1: Adapt ABD normalize_shamela.py passes 1-3 to produce
        #          intermediate data structures (not final output).
        # Phase 2: Integrate discover_structure.py for Pass 4.
        # Phase 3: Implement layer_detector.py for Pass 5.
        # Phase 4: Assemble KR output format, validate, atomic write.
        raise NotImplementedError("ShamelaNormalizer.normalize")
