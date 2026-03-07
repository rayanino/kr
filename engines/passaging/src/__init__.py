"""Passaging Engine — محرك التقطيع

Segments normalized content into passages for downstream processing.
Phase 2 engine (source-agnostic, below normalization boundary).

Module architecture:
  engine.py          — Main orchestrator (§4.A.1 pipeline)
  loader.py          — Input loading and validation (§2)
  assembly.py        — Cross-page text assembly (§4.A.2)
  strategy.py        — Strategy selection (§4.A.3)
  strategies/        — Format-specific strategies (§4.A.4–§4.A.9)
  emitter.py         — Passage emission (§4.A.10)
  validator.py       — Self-validation checks (§4.A.10)
  errors.py          — Error handling (§7)
  config.py          — Configuration loading (§8)
  arguments.py       — §4.B.6 Argument boundary detection
  discourse_optimization.py — §4.B.7 Discourse-aware boundary optimization
  completeness_forecast.py  — §4.B.8 Completeness forecast
  adaptive_passaging.py     — §4.B.5 Content census adaptation
  quality_prediction.py     — §4.B.1 Quality prediction [NYI]
  implicit_structure.py     — §4.B.2 Implicit structure discovery [NYI]
  commentary_alignment.py   — §4.B.3 Commentary-matn alignment [NYI]
  cross_edition.py          — §4.B.4 Cross-edition correspondence [NYI]
"""
