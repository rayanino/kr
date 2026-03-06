# Knowledge Integrity Protocol — بروتوكول سلامة المعرفة

This document defines the verification and safety mechanisms that protect Rayane's knowledge from corruption. It is the most important operational document in the repository.

The foundational axiom: **the knowledge cannot defend itself.** Once an error enters the library — a misattributed quote, a wrong school classification, a corrupted text — it becomes part of what Rayane "knows." Unlike a human scholar who might notice inconsistencies, the library has no immune system unless we build one.

---

## Threat Model

Every threat below has happened in real Islamic studies scholarship. These are not hypothetical.

### T-1: Silent Text Corruption
**Vector:** OCR error, encoding issue, normalization bug, or copy corruption changes Arabic text.
**Consequence:** Rayane cites a scholarly opinion that doesn't exist in the original source.
**Detection difficulty:** HIGH — a single diacritic change can reverse meaning (حَرَّمَ vs حَرَمَ).
**Mitigation chain:**
1. Frozen source with SHA-256 hash — tamper-evident baseline (source engine)
2. Text fidelity score at normalization — character-level comparison with frozen original
3. Primary text immutability — no engine may modify excerpt primary_text after extraction
4. Spot-check validation — periodic random sampling of excerpts against frozen sources
5. Human gate on low-fidelity passages — owner reviews anything below confidence threshold

### T-2: Attribution Error
**Vector:** LLM incorrectly identifies author, school, or date. Multi-layer text (sharh/matn) attributed to wrong author.
**Consequence:** Rayane attributes a Hanbali position to a Shafi'i scholar, or a commentary opinion to the original author.
**Detection difficulty:** MEDIUM — cross-referencing with scholar authority data can catch many cases.
**Mitigation chain:**
1. Multi-model consensus for all attribution decisions (consensus module)
2. Scholar authority registry with verified data — LLM assertions checked against registry
3. Multi-layer detection at normalization — explicit layer→author mapping
4. Confidence scores on every attribution — low confidence triggers human gate
5. Cross-source verification — if the same author appears in multiple sources, attributions should be consistent

### T-3: Taxonomic Misplacement
**Vector:** Excerpt placed under wrong taxonomy leaf. Topic classification error.
**Consequence:** When Rayane looks up "conditions of prayer," he sees content about "conditions of sale."
**Detection difficulty:** LOW — misplacement is often obvious to a domain expert.
**Mitigation chain:**
1. Two-stage placement with multiple candidate sources (taxonomy engine)
2. Consensus for ambiguous-range placements
3. Coverage analysis — detect suspiciously dense or empty leaves
4. Human gate for cross-science placements
5. User feedback loop — if Rayane marks an excerpt as misplaced, the feedback propagates

### T-4: Context Loss (Self-Containment Failure)
**Vector:** Excerpt extracted without sufficient context to be independently understandable.
**Consequence:** Rayane reads an excerpt that says "the ruling is as stated above" with no reference to what was stated above.
**Detection difficulty:** MEDIUM — requires understanding Arabic scholarly discourse conventions.
**Mitigation chain:**
1. Self-containment verification at excerpting (LLM check: "can this be understood alone?")
2. Self-containment context field — explicitly added context for dependent excerpts
3. Consensus on self-containment assessment
4. Human gate on borderline cases
5. User feedback — "I don't understand this excerpt" triggers review

### T-5: Synthesis Hallucination
**Vector:** LLM synthesizer adds claims not grounded in source excerpts. Fabricates scholarly positions.
**Consequence:** Rayane's entry contains "Ibn Taymiyyah argued X" when no source says this.
**Detection difficulty:** HIGH — the entry reads naturally and the claim is plausible.
**Mitigation chain:**
1. Grounding_type traceability — every claim in an entry tagged as source_grounded, metadata_derived, or analytical (D-040)
2. Source_grounded claims must cite specific excerpt IDs — verifiable link
3. Analytical claims explicitly marked as synthesizer contributions, not source claims
4. Post-synthesis verification — check that cited excerpts actually support the claims
5. Human gate on all new entries — owner reviews before entry enters the library
6. No entry may contain a factual claim that isn't traceable to either a source excerpt or an explicit "analytical" tag

### T-6: Metadata Poisoning
**Vector:** Incorrect metadata propagates through the pipeline, affecting all downstream decisions.
**Consequence:** A source incorrectly tagged as "Hanafi fiqh" corrupts all entries it feeds into.
**Detection difficulty:** LOW to MEDIUM — often catchable by cross-referencing.
**Mitigation chain:**
1. Metadata enrichment uses consensus
2. Critical metadata (author, school, science) requires higher consensus threshold
3. Metadata consistency checks — same author's school shouldn't change between sources
4. Pipeline-wide metadata validation at each engine boundary
5. Metadata correction cascade — when metadata is corrected, all downstream products are flagged for re-processing

### T-7: Duplication and Contradiction
**Vector:** Same content enters the library through different sources and receives contradictory treatment.
**Consequence:** The same passage has two entries in the taxonomy with different metadata.
**Detection difficulty:** MEDIUM — requires cross-source comparison.
**Mitigation chain:**
1. Deduplication at source registration (source engine)
2. Work-level matching (same work, different editions)
3. Excerpt-level similarity detection at excerpting
4. Entry-level contradiction detection at synthesis
5. Periodic integrity sweep across the library

---

## Verification Layers

### Layer 0: Immutable Baselines
- Frozen sources are write-once, never modified, SHA-256 hashed
- Gold baselines in `gold/` are hand-crafted and never auto-modified
- These are the ground truth against which everything else is verified

### Layer 1: Engine Self-Validation (every run)
Each engine validates its own output before writing to the library:
- Schema conformance (all required fields present, correct types)
- Metadata completeness (no empty required fields)
- Metadata consistency (no contradictions within the output)
- Confidence thresholds met (low-confidence decisions flagged)

### Layer 2: Boundary Validation (every pipeline run)
At each engine boundary:
- Output of engine N matches input contract of engine N+1
- Metadata accumulation — no fields lost
- Text integrity — primary text unchanged
- Run `scripts/verify_metadata_flow.py` as automated check

### Layer 3: Library-Wide Integrity (periodic)
- Referential integrity — every ID reference resolves
- Cross-source consistency — same entities have consistent metadata
- Coverage analysis — detect gaps and anomalies in taxonomy
- Spot-check sampling — random excerpts verified against frozen sources
- Run integrity-checker agent

### Layer 4: Human Gates (triggered by uncertainty)
- Every low-confidence decision creates a checkpoint
- Every new entry requires owner approval
- Every correction triggers review of affected entries
- The owner is the final authority on all knowledge products

### Layer 5: User Feedback (continuous)
- Rayane's corrections feed back into the pipeline
- Misplacement reports → taxonomy engine
- Attribution errors → source engine + scholar authority
- Quality issues → excerpting engine
- Feedback is tracked and analyzed for systemic issues

---

## Invariants

These are absolute rules. No engine, no configuration, no optimization may violate them.

1. **Frozen sources are immutable.** Once frozen, the bytes never change. If corruption is detected, the source is re-acquired, not repaired.

2. **Primary text is never modified.** The Arabic text in an excerpt's primary_text field is exactly as it appears in the normalized source. No correction, no improvement, no "cleanup."

3. **Every claim is traceable.** Every factual statement in an entry can be traced to either a specific excerpt (with source, page, volume) or an explicit analytical tag.

4. **Errors fail loudly.** No engine may silently drop data, silently default on an uncertain decision, or silently skip a validation. If something is wrong, the pipeline stops or flags it.

5. **Human gates are not optional.** The bypass mechanism for human gates requires explicit owner authentication. No automated process may auto-approve a human gate checkpoint.

6. **Metadata flows forward, never backward-deleted.** An engine may ADD metadata fields. An engine may ENRICH metadata values. No engine may DELETE a metadata field that arrived in its input.

---

## What Claude Code Must Do

When implementing any engine:

1. **Before writing output to disk:** Run Layer 1 self-validation. If validation fails, raise an error — do NOT write invalid data.

2. **Before marking a task complete:** Verify that the output preserves all upstream metadata (D-023). Use `scripts/verify_metadata_flow.py` as a sanity check.

3. **When handling Arabic text:** Never apply string transformations to primary_text that could alter meaning (no case changes, no whitespace normalization beyond what the SPEC explicitly allows, no character substitutions).

4. **When making attribution decisions:** Always use multi-model consensus. Never rely on a single LLM call for author identification, school classification, or date estimation.

5. **When uncertain:** Create a human gate checkpoint with full context. The cost of bothering the owner is infinitely lower than the cost of a silent error.

6. **When writing tests:** Include negative tests that verify the error paths. Test that invalid data is rejected, that low-confidence decisions trigger human gates, and that metadata is preserved.
