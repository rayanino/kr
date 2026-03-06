"""Source Engine Logging — SPEC §7

Append-only log: library/logs/source_engine.jsonl
Every record is a SourceError model instance.

Logged: every intake attempt, duplicate detection, human gate creation,
enrichment write-back, registry update.

Alerts: fatal errors during batch, >10% same warning code, human gate queue > 20.
"""
