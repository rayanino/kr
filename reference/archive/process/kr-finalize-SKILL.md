---
name: kr-finalize
description: ALWAYS activate when comment resolution is complete. Triggers: "finalize", "all comments done", "assemble the spec", "wrap up". Do not produce final SPEC without the phased process.
---

# KR Finalize — إنهاء المواصفات

You are finalizing a KR engine SPEC after comment resolution. This is a PHASED process designed to work across multiple chats, because a single-chat finalization of a 1500-line SPEC will hit context limits and degrade quality.

**The standard:** When finished, the SPEC must be implementable by Claude Code with zero clarifying questions.

---

## Phase Overview

Finalization happens in 3-4 focused chats, not one marathon session:

```
Chat 1: CONSOLIDATE — gather all changes, check interactions, plan the audit
Chat 2+: AUDIT — one chat per major SPEC section (run kr-integrity)
Final chat: ASSEMBLE — produce the complete updated SPEC text
```

The owner can do these in separate sessions over days. Each chat produces a concrete output that feeds the next.

---

## Phase A: Consolidation (1 chat)

### Step 1: Collect All Resolutions

Gather every comment resolution from the review chats. Build a change manifest:

```
| # | SPEC Section | Change Type | Summary | Resolved In |
|---|-------------|-------------|---------|-------------|
| 1 | §4.A.2      | Modified    | Added sharh/matn detection | Chat 2 |
| 2 | §7          | Added       | New error NORM_LAYER_AMBIGUOUS | Chat 2 |
| 3 | §2          | Modified    | Expanded manual input types | Chat 3 |
```

Source: comment resolution logs from kr-spec-review sessions, the owner's memory, or uploaded summaries.

### Step 2: Interaction Check

Do any changes conflict? Does change #3 invalidate change #1's assumption? Read changes as a SET:
- **Within-section conflicts:** Two changes to the same section that contradict
- **Cross-section breaks:** If §4 rules changed, does §2 still provide the right input? Does §3 describe what §4 now produces?
- **Cross-SPEC breaks:** Does the downstream engine's input contract still match this engine's output?

### Step 3: Plan the Audit

Divide the SPEC into audit chunks (typically 3-4 chunks):
- Chunk 1: §1 Purpose + §2 Input + §3 Output (the contracts)
- Chunk 2: §4 Processing (often the longest section — may need its own chat)
- Chunk 3: §5 Validation + §6 Consensus + §7 Errors
- Chunk 4: §8 Config + §9 State + §10 Tests

For each chunk, note which changes apply and what to watch for.

### Step 4: Output

Produce a finalization plan and commit it to the repo:

```markdown
# Finalization Plan — [Engine Name]
# Committed to: skills/handoffs/{engine}-finalization-plan.md

## Change Manifest
[The table from Step 1]

## Interaction Issues Found
[Any conflicts or breaks from Step 2]

## Audit Chunks
[The division from Step 3 with notes per chunk]
```

If the SPEC is large (>800 lines), split it into section files in the repo:
```
engines/{engine}/spec-sections/
├── sections_1-3_contracts.md
├── section_4_processing.md
├── sections_5-7_validation.md
└── sections_8-10_config.md
```
Each audit chat reads only the relevant section file.

---

## Phase B: Audit (1 chat per chunk)

For each chunk, run the kr-integrity skill on that section. The audit checks:

1. **Perfection Standard** (25 criteria from DEEP_REASONING_PROTOCOL.md) — applied to this section
2. **Integrity threats** (7 threats from KNOWLEDGE_INTEGRITY.md) — which apply to this section
3. **Silent failure patterns** (7 patterns from SILENT_FAILURES.md) — scan this section
4. **Change verification** — do the applied changes actually work? Are they complete?

Each audit chat produces:
- A defect list with fixes (exact replacement text for each defect)
- A section-level risk assessment
- Confirmation that changes from Phase A are correctly integrated

See the kr-integrity skill for the full audit procedure.

---

## Phase C: Assembly (1 chat)

### Step 1: Collect Audit Results

Gather defect fixes from all audit chats.

### Step 2: Apply All Changes

Starting from the current SPEC, apply in order:
1. Comment resolutions (from Phase A manifest)
2. Audit fixes (from Phase B)
3. Any cross-section adjustments needed for consistency

### Step 3: The Anti-Secretary Test

Answer honestly:
1. **Is the SPEC RICHER, not just CLEANER?** If it only got cleaner (fixed typos, removed contradictions) without gaining new capabilities or deeper edge-case handling, the work was secretarial.
2. **Did any resolution ORIGINATE a new capability?** Something not just fixing what was broken but seeing an opportunity the comment revealed.
3. **Would a world-class Islamic scholar be surprised by §4.B?** If not, the transformative section needs work.

### Step 4: Produce Complete SPEC

Output the FULL updated SPEC text — not diffs, not "change X to Y," the complete document with all changes applied. This is what gets committed to the repo.

---

## Session Bridging

Each phase produces artifacts committed to the repo:
- Phase A → `skills/handoffs/{engine}-finalization-plan.md`
- Phase B → per-section defect lists (in handoffs or inline)
- Phase C → complete updated SPEC committed and pushed

Since the project knowledge syncs files from the GitHub repo, all phase artifacts are available to the next chat after the owner clicks "Sync now." If using the fallback clone approach, artifacts are available immediately. No manual file uploads needed.

If any phase chat gets too long, commit a handoff to `skills/handoffs/` and start a fresh chat. The owner should sync the project knowledge to pick up the new files.

---

## Critical Reminders

- **Every defect needs a fix, not just a flag.** Exact replacement text.
- **At least one defect must be structural or semantic.** Cosmetic-only audits are superficial.
- **Cross-SPEC consistency matters.** If this engine's output changes, verify the downstream contract.
- **Be brutally honest in the Anti-Secretary Test.** If the session was secretarial, say so.
