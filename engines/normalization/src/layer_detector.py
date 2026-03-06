"""Text layer detection — SPEC §4.A.2 Pass 5 (format-agnostic interface).

Detects text layers (matn, sharh, hashiyah, tahqiq notes) in normalized content.
Each source format provides its own detection signals through a pluggable backend.

Format-specific signals:
  - Shamela HTML: bold tags (~75% of commentary exports use bold for matn), font size, brackets
  - PDF: font size differences, indentation patterns, column positions
  - Image/OCR: spatial analysis of text blocks, font weight detection

The interface is format-agnostic. Normalizers register their format-specific
detection backend at initialization time.

SPEC reference: §4.A.2 Pass 5 (layer detection), §4.A.4 (multi-layer detection)
"""

from typing import Protocol


class LayerDetectionBackend(Protocol):
    """Format-specific layer detection strategy.
    
    Each normalizer provides an implementation of this protocol
    that knows how to extract layer signals from its specific format.
    """

    def detect_layers(self, page_content: str, format_hints: dict) -> list:
        """Detect text layers in a single page.
        
        Args:
            page_content: The text content of one page/unit.
            format_hints: Format-specific signals (e.g., bold spans, font sizes).
        
        Returns:
            List of TextLayerSegment (from contracts.py).
        """
        ...


# Normalizers register their backends here.
# Claude Code implements the actual detection logic per format.
