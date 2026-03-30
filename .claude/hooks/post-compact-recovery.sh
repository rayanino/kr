#!/usr/bin/env bash
# PostCompact hook: re-injects critical invariants after context compaction.
# Compaction is the #1 cause of quality degradation in long sessions — Claude
# loses SPEC rules, Arabic handling constraints, and D-023 semantics.
# This hook fires immediately after compaction and provides recovery context.

set -euo pipefail

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

cat <<'RECOVERY'
=== POST-COMPACTION: CRITICAL INVARIANTS ===

KNOWLEDGE SAFETY (non-negotiable):
- Library IS the user's knowledge — errors propagate into his mind
- Accuracy > Protection > Intelligence (D-006)
- Primary text bytes NEVER modified after extraction (D-004)

DATA INTEGRITY:
- Metadata never deleted, only enriched (D-023)
- Every API call persists full output + update COST_LOG.json
- Multi-model consensus for ALL content decisions (D-041)

ARABIC TEXT SAFETY:
- NEVER .lower()/.upper()/.strip() on Arabic strings
- NEVER use \d in regex (matches Arabic-Indic digits)
- Preserve diacritics — silent loss is T-1 corruption threat

CODE QUALITY:
- Errors fail loud — never silent default (D-033)
- Never implement spec errors — fix the spec first
- Shared concept changes: grep ALL consumers before modifying

ACTION REQUIRED: Re-read the active engine's CLAUDE.md and the
relevant SPEC section before continuing implementation work.
=== END RECOVERY ===
RECOVERY

exit 0
