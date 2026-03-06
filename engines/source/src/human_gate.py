"""Human Gate Checkpoint Management — SPEC §5 Layer 2

Creates, stores, retrieves, and resolves human gate checkpoints.
Checkpoints are batched per source for owner review.

Triggers (HumanGateTrigger enum):
- Author disambiguation (confidence < 0.80)
- Work match uncertain (0.50-0.85)
- Low confidence field (< 0.70)
- Trust flagged
- Consensus disagreement
- Genre chain unresolved
- Enrichment critical field
- Scholar conflict
- Missing required input
"""
