#!/usr/bin/env bash
# Usage: bash tools/start_review.sh <session_number> <from_commit> <to_commit>
# Example: bash tools/start_review.sh 6 f8255e2 HEAD
#
# Automates the 5 rote setup steps that every review begins with.

set -euo pipefail

SESSION="${1:?Usage: start_review.sh <session> <from> <to>}"
FROM="${2:?Usage: start_review.sh <session> <from> <to>}"
TO="${3:-HEAD}"

echo "═══════════════════════════════════════════════════"
echo "  KR Review Setup — Session $SESSION"
echo "═══════════════════════════════════════════════════"
echo

# Step 1: Pull latest
echo "▸ Pulling latest..."
git pull origin master --quiet
echo "  Done."
echo

# Step 2: Show NEXT.md header
echo "▸ NEXT.md header:"
head -8 NEXT.md
echo "  ..."
echo

# Step 3: Copy checklist
DEST="reference/archive/sessions/reviews/review_session_${SESSION}.md"
if [ -f "$DEST" ]; then
    echo "▸ Checklist already exists: $DEST"
else
    cp reference/protocols/REVIEW_CHECKLIST_TEMPLATE.md "$DEST"
    echo "▸ Checklist copied to: $DEST"
fi
echo

# Step 4: Diff stats
echo "▸ Diff stats ($FROM..$TO):"
git diff "$FROM".."$TO" --stat
echo

# Step 5: Run tests
echo "▸ Running tests..."
python -m pytest engines/normalization/tests/ -q 2>&1 | tail -3
echo

# Step 6: Cross-engine contracts
echo "▸ Cross-engine contracts:"
python tools/check_cross_engine_contracts.py 2>&1 | tail -2
echo

echo "═══════════════════════════════════════════════════"
echo "  Setup complete. Begin Pass 1."
echo "═══════════════════════════════════════════════════"
