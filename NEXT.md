# NEXT SESSION

## Session Type
HARDENING (see SESSION_TYPES.md for full framework)

## Immediate Task

**Verify no knowledge corruption paths exist in the source engine SPEC.**

This is NOT a creative session. Do NOT invent new capabilities. This session exists for ONE purpose: ensure that no path exists where bad data can silently enter the library through the source engine.

## What to Read

1. `engines/source/SPEC.md` — **Focus on §4.A (processing rules), §5 (validation), §7 (error handling).** These are the corruption-relevant sections.
2. `KNOWLEDGE_INTEGRITY.md` — the full threat model. Read this FIRST to know what threats to look for.
3. `reference/ENTRY_EXAMPLE.md` — understand what metadata the synthesizer needs (a metadata error in the source engine → a wrong claim in an entry).

**Do NOT read:** CREATIVE_MANDATE.md, other engine SPECs, VISION.md sections unrelated to source engine.

**Budget:** ~15K tokens on reading (including KNOWLEDGE_INTEGRITY.md). ~50K tokens on hardening analysis. ~15K tokens on fixes. ~10K tokens on handoff.

## The Hardening Work (follow this sequence)

### Step 1: Threat analysis
For each §4.A processing step, identify:
- What data enters (from where? trusted or untrusted?)
- What transformation occurs
- What data exits (to where? does downstream engine trust it?)
- What could go wrong (corrupted input, LLM hallucination, race condition, silent default)
- What prevents each failure mode (validation, consensus, human gate, logging)

Focus especially on:
- **Author identification** (§4.A.4, §4.A.5): Wrong author ID cascades to every excerpt and entry.
- **Work matching** (§4.A.1, §4.A.7): Wrong work_id means excerpts from different works are mixed.
- **Trust evaluation** (§4.A.8): Wrong trust tier means unreliable content enters as verified.
- **Enrichment write-back** (§2): A downstream engine could write corrupt data back.

### Step 2: Identify gaps
For each threat identified, check: does the SPEC specify a mitigation? Is the mitigation sufficient? Could an implementer accidentally skip it?

### Step 3: Fix gaps
Write concrete SPEC additions for any unmitigated threats. Use the precision style: exact rules, exact error codes, exact recovery actions.

### Step 4: Verify
```
python3 scripts/check_spec_quality.py engines/source/SPEC.md --verbose
```
Target: ≤4 high-severity defects (maintaining baseline from PRECISION session).

## Definition of Done

1. Threat analysis documented (can be inline in SPEC or a separate section)
2. All identified corruption paths have explicit mitigations in the SPEC
3. No new SPEC defects introduced
4. `check_spec_quality.py` ≤4 high-severity defects
5. NEXT.md written for next session (IMPLEMENTATION_PREP for source engine)
6. SESSION_LOG.md updated
7. Committed and pushed

## What the Previous Session Did

PRECISION session (2026-03-06): Made the source engine SPEC implementation-ready.

Changes:
- Added 12 worked examples with Arabic text to §4.A and §4.B subsections
- Replaced all "etc." (6 instances) with exhaustive lists
- Replaced all vague quantifiers ("multiple", "many", "some") with specific numbers (7 instances)
- Replaced "appropriate" with specific criteria (2 instances)
- Added explicit validation references at all write points
- Expanded genre list to 18 exhaustive entries
- Added Genre enum, CompositionalProfile, EditionComparison, GenealogyMetadata Pydantic models to contracts.py
- Added MIXED structural format to contracts.py

Quality results:
- check_spec_quality: 41 HIGH → 4 HIGH (all false positives in §4.B narrative and §9 gaps)
- creative_verification: §4.B score 90/100 (maintained from creative session)

## Pending Owner Questions

- **API keys:** Will be needed for the IMPLEMENTATION_PREP session (after HARDENING). Not needed yet.
