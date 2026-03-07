"""§4.B.2 — Implicit Structure Discovery. [NOT YET IMPLEMENTED]

For sources with minimal or no division tree (headingless texts).
Discovers topic boundaries using semantic similarity of sentence embeddings.

When normalization quality_report.overall_confidence is 'low',
this capability cross-validates LLM-proposed boundaries against
division boundaries, preferring LLM boundaries when they disagree.

Gated by config.enable_implicit_structure (default: true).
"""

from __future__ import annotations
