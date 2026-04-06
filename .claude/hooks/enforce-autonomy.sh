#!/usr/bin/env bash
# DR19 Norm 1: Autonomy Enforcement Hook
# Blocks technical guidance-seeking questions to the owner.
# Always active (not just overnight mode).
#
# Matcher: PreToolUse → AskUserQuestion
# Exit 0 = allow (legitimate preference question)
# Exit 2 = block (technical guidance seeking)
#
# Reference: Protocol §0.1 Autonomous Operations Doctrine, HR-25

set -euo pipefail

# Read tool input from stdin
input=$(cat)

# Extract the question text
QUESTION=$(echo "$input" | jq -r '.tool_input.question // .tool_input.questions[0].question // ""' 2>/dev/null)

if [ -z "$QUESTION" ]; then
    # Cannot parse question — allow through (conservative)
    exit 0
fi

# Lowercase for pattern matching
QUESTION_LOWER=$(echo "$QUESTION" | tr '[:upper:]' '[:lower:]')

# Technical guidance-seeking patterns (§0.1 banned phrases)
# These indicate the agent is asking the owner to make a technical decision
BLOCKED_PATTERNS=(
    "should i "
    "should we "
    "do you want me to"
    "want me to "
    "shall i "
    "shall we "
    "how would you like"
    "which approach"
    "which option"
    "what should i do"
    "should i proceed"
    "want me to proceed"
    "want me to continue"
    "standing by"
    "waiting for your"
    "let me know how"
    "let me know if you"
    "what do you think about"
    "do you prefer"
    "would you rather"
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$QUESTION_LOWER" | grep -qF "$pattern"; then
        # Log the violation
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TIMESTAMP] AUTONOMY VIOLATION BLOCKED: $QUESTION" >> "$CLAUDE_PROJECT_DIR/.kr/runtime/norm_violations.log" 2>/dev/null || true

        echo "{\"decision\":\"block\",\"reason\":\"§0.1 Autonomy violation: This is a technical question. The protocol and roadmap determine next steps — not the owner. Decide autonomously and report what you decided. Blocked pattern: '$pattern'\"}"
        exit 0
    fi
done

# No blocked pattern found — allow through (legitimate preference/relay question)
exit 0
