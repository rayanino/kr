# Human Gate Specification

## Input

Pending decision from consensus engine with required approval level.

## Output

Approved/rejected decision with approval timestamp and approver ID.

## Process

1. Fetch pending decision
2. Check pre-approval policy
3. If pre-approved, process automatically
4. Otherwise, queue for human review
5. Return decision with approval metadata

## Approval Levels

- Minor corrections (pre-approved for specific policies)
- Major content changes (requires explicit approval)
- Structural changes (requires technical approval)
- New sources (requires source validation approval)

## Error Handling

Appeals process for rejected decisions.

## Status

Implementation stub - see tools/human_gate.py in ABD repo.
