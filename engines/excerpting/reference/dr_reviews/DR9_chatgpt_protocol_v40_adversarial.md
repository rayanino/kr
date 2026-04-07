# Adversarial Review of HARDENING_SESSION_PROTOCOL v4.0

## Evidence base and scope

This review is grounded in the following files from the `excerpting-foundations-hardening-20260404` branch of the `rayanino/kr` repo on entity["company","GitHub","code hosting platform"]:

- `engines/excerpting/reference/HARDENING_SESSION_PROTOCOL.md` (governing_version: 4.0), including the full version history from v1.0 → v4.0 and the full §0–§9 body. fileciteturn2file0  
- `NEXT.md` (current task state; “Session 3 instructions” and current operational posture). fileciteturn3file0  
- `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md` (real-world artifact patterns: batching, “preliminary” debt, and what “closure” looks like under pressure). fileciteturn4file0  

Because the protocol explicitly binds itself to other repo documents (rules + skills + handoffs), and because your pre-mortem is explicitly about *interaction failures* (not local defects), I also treated the following as “behavior-shaping context” that can override how faithfully sessions execute the protocol:

- Dispatch templates and claimed access constraints: `.claude/skills/coworker-dispatch/SKILL.md`. fileciteturn5file0  
- Core workflow constraints: `.claude/rules/context-management.md`, `.claude/rules/no-single-model-conclusion.md`, `.claude/rules/mandatory-coworker-dispatch.md`. fileciteturn10file0turn11file0turn12file0  
- “Resume authority” artifacts that frequently become de-facto law in practice: `.kr/HANDOFF.md` and `reference/handoffs/excerpting_foundations_session3_kickoff_2026-04-04.md`. fileciteturn14file0turn15file0  

## Pre-mortem frame and failure model

You asked for a July 2026 retrospective on Sessions 3–15 where Session 15 discovers ~40% of “CLOSED” atoms contain undetected scholarly errors, with owner disengagement and “closed-with-hidden-gaps” as the dominant pathology. I treated that as a systems failure dominated by:

- **State-machine leakage**: ambiguous or unenforced state transitions that let items be “CLOSED” without the intended epistemic guarantees (coverage, arbitration, validation). fileciteturn2file0  
- **Scheduling deadlocks**: WIP constraints + async coworker latency + session-type gating producing “no productive moves,” pushing operators into rule-bending. fileciteturn2file0  
- **Governance drift**: conflicting “law sources” (protocol vs NEXT vs handoffs vs rules) producing inconsistent behavior and gradual doctrine divergence. fileciteturn2file0turn3file0turn14file0turn15file0  

## Findings

### 1) Checkpoint states are not part of session-start gating, so “must-resume” atoms can be skipped indefinitely

**FINDING:** §6.5 introduces checkpoint states intended to prevent fake terminal states during emergencies, but §1.6’s gate-precedence matrix never checks for checkpointed atoms. This allows “must-resume” work to be repeatedly deprioritized by session-type gates (intake/debt/refactor), creating orphaned or long-stale atoms. fileciteturn2file0

**SEVERITY:** CRITICAL

**SECTION:** §6.5; §1.6; §1.5. fileciteturn2file0

**SCENARIO (Session 8, prompt-affecting hadith isnād integrity atom):**
1. Session 8 is a `full-atom` session and reaches Stage 6 on MAQ-214 (Full Lane): “Never split isnād-matn; treat transmission formulas as atomic.” fileciteturn2file0turn13file0  
2. Context spikes into Zone 4; CC uses checkpoint `IMPLEMENTED-UNVERIFIED` (tests not run) and writes handoff instructions. fileciteturn2file0  
3. Session 9 starts. Gate 4 triggers because new bundles exist at repo root → session type forced to `intake-only`. Intake-only prohibits atom processing (and §1.5 forbids combining intake-only with full-atom). fileciteturn2file0turn3file0  
4. Session 10 starts. Prompt Refactor Gate triggers (prompt >80%) → session type forced to `prompt-architecture`. Still no checkpoint resolution. fileciteturn2file0turn3file0  
5. By Session 15, MAQ-214’s unverified implementation has either (a) been committed “to not lose work,” or (b) been reconstituted without original context, producing silent scholarly faults even if tests pass. The atom is later marked CLOSED under pressure, but its Stage 6 validation was never executed under the intended epistemic state. fileciteturn2file0  

**ROOT CAUSE:** Checkpoints are defined as “must be resolved next session,” but there is no protocol-level gate that makes them *globally blocking* ahead of other session-type gates. Reliance on human compliance via handoffs is fragile under multi-session drift. fileciteturn2file0turn14file0turn15file0

**PROPOSED FIX (amend §1.6 by inserting a new Gate 3):**
- Insert after Gate 2, before “PRELIMINARY DEBT CHECK”:  
  **“3. CHECKPOINT RESOLUTION GATE — If ANY atom is in a checkpoint state (`PAUSED-*`, `IMPLEMENTED-*`), the session type MUST be `validation-only` (if `IMPLEMENTED-*`) or `debt-clearance` (if `PAUSED-*`) until all checkpointed atoms are resolved to a terminal state or demoted to REOPENED with a written rationale.”** fileciteturn2file0

**WARNING SIGN:** Ledger shows checkpoint states persisting across ≥2 handoffs, or `.kr/HANDOFF.md` repeatedly referencing the same checkpointed MAQ-ID while NEXT-based work proceeds. fileciteturn2file0turn14file0

---

### 2) “Authority hierarchy” + Light Lane creates a bypass where `model_only` atoms can be implemented without owner confirmation

**FINDING:** Stage 2 flags that `model_only` requires owner confirmation before Stage 5 synthesis, but Light Lane explicitly skips CHALLENGED + SYNTHESIZED (Stages 4–5). This creates a structural bypass where a `model_only` atom can be implemented and closed without the owner-confirmation constraint ever being checked. fileciteturn2file0

**SEVERITY:** CRITICAL

**SECTION:** §4.2 (authority + model_only handling); §4.14 (Light Lane skips); §4.5 (owner confirmation in G‑SYNTHESIZED); §4.8 (Q‑CLOSED criteria doesn’t re-impose owner confirmation for Light Lane). fileciteturn2file0

**SCENARIO (Session 6, “prompt-adjacent” doctrine atom about splitting Qur’anic citation blocks):**
1. A note extracted from Layer B is classified `model_only` (analysis expansion, not owner-explicit). fileciteturn2file0  
2. CC classifies it as Light Lane because it “adds SPEC-doctrinal guidance only” (no immediate prompt change). fileciteturn2file0  
3. Light Lane path executes Stages 2 → 3 → 6 → 7; Stage 5 is never reached, so the explicit “owner has confirmed intent” gate is never evaluated. fileciteturn2file0  
4. The atom becomes CLOSED-VERIFIED or CLOSED-IMPLEMENTED with only a spot-check (or minimal review). The owner never confirms the underlying intent. fileciteturn2file0  
5. Later sessions treat the SPEC statement as doctrine, and it silently influences real prompt-affecting decisions, amplifying into corpus-level scholarly errors. fileciteturn2file0  

**ROOT CAUSE:** Owner confirmation is implemented as a **stage-local gate (Stage 5)** rather than a **lane-invariant constraint** on any closure path that can change doctrine. fileciteturn2file0

**PROPOSED FIX (amend §4.14 eligibility rules):**
- Insert under “LIGHT LANE: Eligible ONLY for”:  
  **“ABSOLUTE PROHIBITION: No `model_only` atom is eligible for Light Lane. Owner confirmation is REQUIRED before ANY implementation or closure outcome (including CLOSED‑VERIFIED).”** fileciteturn2file0

**WARNING SIGN:** Any CLOSED atom whose authority is `model_only` but lacks an explicit owner-confirmation record (or corresponding Stage 5 synthesis artifact). fileciteturn2file0

---

### 3) WIP Cap + async coworker latency creates “no legal moves,” incentivizing Light Lane gaming and premature PRELIMINARY closure

**FINDING:** The WIP cap (max 1 Full Lane in Stages 3–5) combined with Stage 4’s variable coworker latency produces periods where the session cannot legally start new high-value work while waiting—especially when the queue is dominated by Full Lane atoms. Predictably, operators will either (a) misclassify atoms as Light Lane, or (b) close PRELIMINARY aggressively to “free WIP,” degrading scholarly reliability. fileciteturn2file0

**SEVERITY:** CRITICAL

**SECTION:** WIP Cap at start of §4; §4.4 latency/timeouts; §4.9 preliminary debt exception language; §6.1 zones/handoff pressure. fileciteturn2file0

**SCENARIO (Session 11, hadith isnād splitting + sharḥ-matn coupling):**
1. Session 11 expands MAQ-301 (Full Lane) and dispatches Codex + Gemini + DR. fileciteturn2file0  
2. Gemini returns quickly; Codex delayed; DR relay depends on owner schedule. Atom sits in Stage 4, counting as “in Stages 3–5.” fileciteturn2file0turn5file0  
3. WIP cap forbids starting another Full Lane atom in Stages 3–5, and the remaining queue items are mostly prompt-affecting (Full Lane by definition). fileciteturn2file0  
4. Session runs out of productive work. To keep throughput, CC re-labels a borderline atom as Light Lane or proceeds with 2/3 and marks PRELIMINARY to “move on.” fileciteturn2file0  
5. By Session 15, many “closed” atoms are either Light Lane with insufficient scholarly review or PRELIMINARY that never got cleared, producing the 40% error discovery. fileciteturn2file0turn4file0  

**ROOT CAUSE:** WIP is capped on **processing states** that include long-latency “waiting” states, without a separate policy for “awaiting coworker” inventory. fileciteturn2file0

**PROPOSED FIX (amend WIP Cap line in §4 and define a waiting sub-cap):**
- Replace the WIP statement with:  
  **“Max 1 Full Lane atom in Stages 3 and 5 (EXPANDED or SYNTHESIS-IN-PROGRESS) at any time. Stage 4 (AWAITING COWORKERS) is tracked separately: max 3 Full Lane atoms may be in ‘AWAITING COWORKERS’ concurrently, provided no more than 1 is actively being expanded or synthesized.”** fileciteturn2file0

**WARNING SIGN:** A rising share of atoms being marked Light Lane or CLOSED‑PRELIMINARY immediately after coworker delays, correlated with “idle waiting” in handoffs. fileciteturn2file0turn7file0

---

### 4) Gate-precedence can deadlock the entire operation when debt-clearance is impossible without owner-mediated DR

**FINDING:** Gate 3 forces a `debt-clearance` session when preliminary debt exceeds thresholds. But debt clearance is defined as re-dispatching missing coworkers, and DR relays are owner-mediated with timeout-based “proceed N‑1” behavior. When owner mediation is unavailable (even temporarily), you can end up in a loop where gate-precedence repeatedly selects debt-clearance but debt cannot practically be reduced—blocking intake and atom work for multiple sessions. fileciteturn2file0

**SEVERITY:** HIGH

**SECTION:** §1.6 Gate 3; §4.9 debt ceiling; §5.5 DR relay; §1.5 session-type restrictions. fileciteturn2file0

**SCENARIO (Sessions 9–12, “tarjīḥ/khilāf proof-stack handling” atoms):**
1. By Session 9, >5 atoms are CLOSED-PRELIMINARY due to missing DR (proceeded after 48h). fileciteturn2file0  
2. Session 10 begins: Gate 3 triggers → session type debt-clearance. fileciteturn2file0  
3. Debt-clearance requires owner relay to DR to obtain missing votes. Owner is unresponsive for several days; timeouts force N‑1 again, or “attempt within session” produces no results. fileciteturn2file0turn3file0  
4. Because debt remains > threshold, every subsequent session is forced into debt-clearance again (Gate 3), preventing bundle intake despite new bundles arriving and preventing full-atom work. fileciteturn2file0turn3file0  
5. Teams respond by informally ignoring gate-precedence (“we’ll just intake quickly”), creating governance drift and inconsistent closure standards that later manifest as undetected scholarly errors. fileciteturn2file0turn14file0  

**ROOT CAUSE:** Gate-precedence treats debt-clearance as always feasible, but DR is an externally mediated dependency with high variance and no protocol-level fallback that *reduces debt without DR*. fileciteturn2file0

**PROPOSED FIX (amend §4.9 with a hard fallback mode):**
- Add after the “Exception” clause:  
  **“If the missing coworker is DR and owner relay is unavailable for >2 sessions OR >7 calendar days, the atom MUST be downgraded from CLOSED‑PRELIMINARY to REOPENED and re-enter Stage 4 using only available coworkers (Codex+Gemini), with the DR slot explicitly waived as ‘UNAVAILABLE’ and logged as a risk. Preliminary is not a parking lot.”** fileciteturn2file0

**WARNING SIGN:** Multiple consecutive sessions where session type is debt-clearance but preliminary debt count does not decrease. fileciteturn2file0

---

### 5) The protocol’s own ecosystem contains conflicting “authoritative” session instructions, driving governance drift at the worst time

**FINDING:** The protocol declares itself “ABSOLUTE” and requires NEXT.md agreement, yet `.kr/HANDOFF.md` and the Session 3 kickoff handoff prescribe materially different Session 3 work than NEXT.md (including a different operational objective and assumptions about coworker availability). In practice, operators follow handoffs; this creates systematic divergence from gate-precedence and session-type rules. fileciteturn2file0turn3file0turn14file0turn15file0

**SEVERITY:** CRITICAL

**SECTION:** Protocol §0 boot order and “verify it matches NEXT.md”; §1.6 gate precedence; `.kr/HANDOFF.md` “start here”; Session 3 kickoff document. fileciteturn2file0turn3file0turn14file0turn15file0

**SCENARIO (Session 3, bundle intake vs validation divergence):**
1. Session 3 begins; protocol says gate-precedence must determine session type and NEXT.md is part of version reconciliation. fileciteturn2file0turn8file0turn3file0  
2. `.kr/HANDOFF.md` instructs to start with a Session 3 kickoff doc and implies Session 3 is continuing foundations hardening and validation. fileciteturn14file0turn15file0  
3. NEXT.md states Session 3 must be `intake-only` due to new bundles at repo root (Gate 4). fileciteturn3file0turn2file0  
4. CC follows the handoff doc (human tendency: “resume point” feels immediate), proceeds with validation work, and defers intake. Intake slips, later becomes rushed, and atom extraction coverage degrades. fileciteturn2file0turn14file0turn15file0  

**ROOT CAUSE:** There is no explicit **document-precedence hierarchy for “what to do this session,”** beyond version-number checks. Version reconciliation scripts verify strings, not work-plan consistency. fileciteturn2file0turn8file0

**PROPOSED FIX (add to §0 checklist, after item 1):**
- Insert:  
  **“AUTHORITATIVE TASK ORDER: If NEXT.md conflicts with any handoff document about session type or primary objective, NEXT.md wins. Handoff docs may ONLY specify resume point within the session type chosen by §1.6.”** fileciteturn2file0turn3file0

**WARNING SIGN:** Handoff docs and NEXT.md diverge on session type, or handoffs repeatedly redefine “what Session N is,” rather than just “where to resume.” fileciteturn3file0turn14file0

---

### 6) DR relay “atom-review must be 1 atom per relay” contradicts operational batching pressures and existing practice signals

**FINDING:** §4.16 forbids multi-atom DR relays for `atom-review` class to avoid shallow feedback. But the broader repo’s operational posture includes batching (ledger registers “batches”; handoff describes “6 thematic batches”), creating a strong incentive to violate the one-atom rule under owner relay fatigue. Result: DR becomes shallow or is skipped exactly where it was intended to catch blind spots. fileciteturn2file0turn4file0turn14file0

**SEVERITY:** HIGH

**SECTION:** §4.16 DR relay classes; §4 WIP cap; ledger batch framing; handoff batch framing. fileciteturn2file0turn4file0turn14file0

**SCENARIO (Session 12, owner disengagement onset):**
1. Session 12 has 6 disputed Full Lane atoms (prompt-affecting) needing DR as tiebreakers. fileciteturn2file0  
2. Protocol requires 6 separate `atom-review` relays. Owner is already fatigued by relays and requests “one combined prompt.” fileciteturn2file0  
3. CC either violates the protocol (sends combined), or avoids DR entirely to comply with DR budget/owner burden. fileciteturn2file0  
4. Without strong DR scrutiny, subtle scholarly errors pass Codex+Gemini review (especially where both models share the same blind spot). These errors remain hidden until later spot-checks. fileciteturn2file0turn11file0  

**ROOT CAUSE:** The protocol bans batched DR review but does not supply a *lower-burden alternative* that preserves per-atom adversarial depth (e.g., structured DR forms or sampling). fileciteturn2file0

**PROPOSED FIX (revise §4.16 by adding a “sampling-based DR” option):**
- Add under DR relay classes:  
  **“`atom-review-sampled`: DR reviews 1 atom in depth and 3 additional atoms for ‘red-flag scan’ only (max 10 minutes each). Counts as 1 budget unit. Output must clearly separate ‘deep review’ vs ‘scan.’”** fileciteturn2file0

**WARNING SIGN:** DR prompts increasingly cover multiple MAQ-IDs, or DR participation rate drops sharply while dispute rate remains constant. fileciteturn2file0

---

### 7) “2 of 3 coworker reports” gate is necessary but not sufficient; it ignores *coverage tier requirements* for the specific atom type

**FINDING:** G‑CHALLENGED requires “at least 2 of 3 coworker reports,” but §5.1 coverage tiers specify which coworkers are minimally required per change type (e.g., prompt-affecting requires Codex + Gemini). As written, a Full Lane scholarly atom could proceed with Codex + DR but without Gemini, meeting the 2/3 rule while violating the intended scholarly floor. fileciteturn2file0

**SEVERITY:** CRITICAL

**SECTION:** §4.4 G‑CHALLENGED; §5.1 Coverage Tiers; §5.6 scope table; mandatory coworker dispatch rule. fileciteturn2file0turn12file0

**SCENARIO (Session 7, “Qirāʾāt/Tajwīd waqf symbol handling” prompt-affecting atom):**
1. MAQ-188 is prompt-affecting (Full Lane) and explicitly touches Qirāʾāt/Tajwīd integrity (added science domain). fileciteturn2file0  
2. Gemini CLI is temporarily unavailable; Codex returns and a DR returns. fileciteturn2file0turn5file0  
3. CC proceeds to Stage 5 because “2/3 reports received” → G‑CHALLENGED passes. fileciteturn2file0  
4. Atom becomes CLOSED‑PRELIMINARY. The missing coworker is *the only one designated for scholarly Arabic auditing*. Later, debt is not cleared promptly, so the atom’s scholarly validity was never actually evaluated at the required tier. fileciteturn2file0turn4file0  

**ROOT CAUSE:** The gate is defined as a numeric threshold rather than a **type-specific coverage predicate** (“did we get the right reviewers for this atom type?”). fileciteturn2file0

**PROPOSED FIX (amend §4.4 Exit gate):**
- Replace the first checkbox with:  
  **“Received the minimum coverage tier required by §5.1 for this atom’s change type (not merely 2-of-3). If a required specialty reviewer is missing (e.g., Gemini for Arabic), the atom MUST remain PAUSED‑CHALLENGED, not PRELIMINARY.”** fileciteturn2file0

**WARNING SIGN:** CLOSED‑PRELIMINARY atoms whose missing coworker corresponds to the atom’s primary risk domain (Arabic/scholarly vs contract/technical). fileciteturn2file0turn5file0

---

### 8) DR “tiebreaker” independence is undermined by the default DR template that includes other coworker findings

**FINDING:** §5.4 calls for a blinded DR tiebreaker, but the default DR dispatch template in Stage 4 includes “Codex found / Gemini found” summaries. That contaminates independence exactly when DR is needed as an unbiased adjudicator, inflating false consensus and letting subtle errors slip through. fileciteturn2file0

**SEVERITY:** HIGH

**SECTION:** §5.4 step 5 (blinded tiebreaker); §4.4 DR templates (include other findings). fileciteturn2file0

**SCENARIO (Session 10, prompt-affecting atom about “Muṭlaq/Muqayyad must remain coupled”):**
1. Codex says ACCEPT (implementation safe); Gemini says ITERATE (scholarly counterexample). fileciteturn2file0  
2. Per §5.2 tie rules, CC escalates to DR as tiebreaker. fileciteturn2file0  
3. CC uses the default DR template that includes both Codex and Gemini summaries. DR is biased toward “resolving” rather than independently evaluating, and may overweight whichever summary is rhetorically stronger. fileciteturn2file0  
4. Atom is FINALIZED with a “majority,” but the independent-check property the protocol relies on was not actually present. Errors remain latent. fileciteturn2file0  

**ROOT CAUSE:** The protocol has two different DR functions (“gap-detection with full context” vs “blinded tiebreak”), but provides only one default template, which violates one of those functions. fileciteturn2file0

**PROPOSED FIX (amend §5.4 step 5 and §4.4 DR templates):**
- Add to §5.4 step 5:  
  **“BLINDED means: DR prompt MUST include ONLY the expansion and raw source excerpts. It MUST NOT include Codex/Gemini verdicts or summaries.”** fileciteturn2file0  
- Add a separate DR template labeled “BLINDED TIEBREAK.” fileciteturn2file0

**WARNING SIGN:** DR verdicts that mirror CLI language/structure unusually closely, or DR reports that fail to introduce novel counterexamples in tie situations. fileciteturn2file0

---

### 9) Session-type “compatibility” is underspecified, enabling expensive mixed-mode sessions that recreate Session 2 context failures

**FINDING:** §1.5 allows combining two “compatible” session types but defines only one explicit incompatibility (intake-only + full-atom). This ambiguity invites operators to combine prompt-architecture with full-atom work (or debt-clearance with intake) in a single context, directly contradicting the “context is scarce” design premise and the new lane budgets. fileciteturn2file0

**SEVERITY:** HIGH

**SECTION:** §1.5 “may combine two compatible types”; §2.1 context budgeting; §6 context zones. fileciteturn2file0

**SCENARIO (Session 5, prompt cap crisis + “just do one atom too”):**
1. Prompt Refactor Gate trips; session type should be prompt-architecture. fileciteturn2file0turn3file0  
2. Operator decides to “also close one easy atom” (full-atom) while already holding prompt refactor state in context. fileciteturn2file0  
3. Compound mode blows past real context budget assumptions; the atom’s expansion is abbreviated, and syntheses become hurried. fileciteturn2file0  
4. Errors become more likely exactly in prompt-affecting decisions that have corpus-wide blast radius. fileciteturn2file0  

**ROOT CAUSE:** “Compatibility” is treated as a judgment call without an explicit allowed-pairs matrix or a “do not mix” rule for high-entropy work types. fileciteturn2file0

**PROPOSED FIX (amend §1.5 with an explicit compatibility matrix):**
- Add:  
  **“Allowed combinations are ONLY: (`debt-clearance` + `prompt-architecture`) and (`validation-only` + `debt-clearance`). All other combinations are FORBIDDEN.”** fileciteturn2file0

**WARNING SIGN:** Session handoffs describing “we did prompt refactor + implemented atoms” or recurring Zone 4/5 near-misses during mixed-mode sessions. fileciteturn2file0turn7file0

---

### 10) Lane-based budgets are not structurally compatible with the mandatory Stage 3 expansion template, leading to “checkbox theater” compliance

**FINDING:** §2.1 budgets Full Lane work at ~50K tokens/atom with 15–20 minutes for Stage 3 expansion, but the mandated template requires 13+ dense sections including 16-science and 23-unit checklists, plus multi-layer and pedagogy fields. The predictable result at 600 atoms is superficial completion (“checked all”) rather than real scholarly reasoning, producing hidden quality gaps that the ledger format cannot detect. fileciteturn2file0

**SEVERITY:** HIGH

**SECTION:** §2.1 budgets; §4.3 expansion template + Full Lane requirements. fileciteturn2file0

**SCENARIO (Session 13, Full Lane atom about “takhrīj must bind grading to matn”):**
1. CC tries to hit target “5–8 atoms/session” with “50K tokens per Full Lane atom.” fileciteturn2file0  
2. Stage 3 becomes a templating exercise: Cross‑Science Variation and Atomic Integrity Risk are filled with “APPLIES / no risk” without concrete examples or counterexamples. fileciteturn2file0  
3. Coworkers evaluate the narrative coherence of the expansion, not the underlying factual correctness across obscure sciences (e.g., rijāl/takhrīj edge cases). fileciteturn2file0  
4. The atom is CLOSED as “process-complete,” but later audits reveal real scholarly counterexamples were never surfaced. fileciteturn2file0  

**ROOT CAUSE:** The template forces breadth without providing a “minimum evidence bar” per section; it optimizes for completeness of form, not correctness of reasoning. fileciteturn2file0

**PROPOSED FIX (amend §4.3 template requirements with evidence minima):**
- Add a global rule under Stage 3:  
  **“For Cross‑Science Variation and Atomic Integrity Risk, ‘checked’ is invalid without evidence. Minimum: (a) 2 sciences with concrete Arabic counterexamples OR (b) 1 science with a named classical-genre exemplar AND an explicit non-applicability rationale for 2 other sciences.”** fileciteturn2file0

**WARNING SIGN:** Expansions that repeatedly contain “No risk identified. Checked: [16 sciences]” without any concrete examples, especially on prompt-affecting atoms. fileciteturn2file0

---

### 11) Owner briefing optimization creates a “silent disengagement trap” that neuters the owner-objection safety valve

**FINDING:** §4.15 shifts to batched owner delivery after 50 atoms, while §4.10 treats owner objection as an override that can reopen atoms. If the owner disengages (stops reading batches or skims), the objection mechanism silently stops functioning, and errors persist until deep audits—matching your pre-mortem outcome. fileciteturn2file0

**SEVERITY:** CRITICAL

**SECTION:** §4.15 Phase B batching; §4.10 objection mechanism; Stage 7 “owner brief is informational” framing. fileciteturn2file0

**SCENARIO (Session 15 discovery pattern, errors in “CLOSED” atoms):**
1. After atom 50, owner receives batch summaries that omit nuance (only “what changed”). fileciteturn2file0  
2. A subtle scholarly error in a “CLOSED” atom would have triggered an immediate owner objection if seen in full context, but the batch summary doesn’t expose the problematic edge case. fileciteturn2file0  
3. Owner gradually disengages (“nothing to react to”), and the system loses its only non-model epistemic validator. fileciteturn2file0turn12file0  
4. Session 15 runs a deeper corpus check and discovers systemic errors that should have been caught by owner objections earlier—but the protocol made owner visibility optional at scale. fileciteturn2file0  

**ROOT CAUSE:** The protocol treats owner delivery as an optimization lever, but owner feedback is also a **core quality-control actuator** (explicitly overriding consensus). Optimizing it away removes a safety layer. fileciteturn2file0turn12file0

**PROPOSED FIX (amend §4.15 Phase B with a mandatory “owner engagement heartbeat”):**
- Add after Phase B description:  
  **“Owner Engagement Heartbeat: every 10 CLOSED atoms (post‑50), the owner MUST review 2 full per‑atom briefs chosen by CC (1 ‘lowest confidence’, 1 random). If owner does not respond within 7 days, Session type MUST switch to `validation-only` and produce a 10‑atom retrospective before more closures.”** fileciteturn2file0

**WARNING SIGN:** Owner responses drop to near-zero while closure rate continues, and reopen events from owner objections fall to zero for long spans. fileciteturn2file0

---

### 12) “Per-atom ledger artifact always” is correct, but the protocol doesn’t define a machine-checkable ledger schema, so Q‑CLOSED becomes performative

**FINDING:** Q‑CLOSED defines 11 criteria and proposes a future `verify_atom_closure.py` script, but the script does not exist. Without machine enforcement, “ledger complete” becomes a self-attestation under time pressure—exactly the condition that yields “closed with hidden gaps.” fileciteturn2file0turn9file0

**SEVERITY:** CRITICAL

**SECTION:** §4.8 Machine verification note; absence of verify script (404). fileciteturn2file0

**SCENARIO (Session 14, “CLOSED” without objective evidence):**
1. CC marks MAQ-277 as CLOSED‑IMPLEMENTED and writes a ledger entry claiming tests ran and sync passed. fileciteturn2file0  
2. No script verifies that (a) referenced file:line changes exist, (b) prompts and SPEC are synchronized, (c) word counts match, (d) queue status aligns. fileciteturn2file0turn9file0  
3. Under deadline/burnout, some closures are “close enough,” and the ledger’s presence is treated as sufficient. fileciteturn2file0  
4. Session 15 later discovers many atoms were “closed” without the intended evidence, and some contained scholarly errors that a real validation harness would have flagged. fileciteturn2file0  

**ROOT CAUSE:** Q‑CLOSED’s objective components are not mechanically enforced; the protocol explicitly defers the key enforcement mechanism. fileciteturn2file0turn9file0

**PROPOSED FIX (amend §0 checklist + §4.8):**
- Add to §0 checklist:  
  **“Run `python scripts/verify_atom_closure_minimal.py` — MUST PASS (required before any atom can be marked CLOSED).”** fileciteturn2file0  
- Replace the aspirational note in §4.8 with:  
  **“DA‑001 is now REQUIRED. Until the full script exists, use a minimal verifier that checks presence of required ledger markers, queue status, and prompt/SPEC sync.”** fileciteturn2file0turn9file0  

**WARNING SIGN:** Any closure where the evidence is textual (“ran tests”) rather than attached outputs/paths, and repeated “will build verifier later” notes across handoffs. fileciteturn2file0turn7file0

---

### 13) Prompt coherence review trigger is not globally tracked, so contradictions accumulate silently across sessions

**FINDING:** §4.12 requires prompt coherence review after every 5 prompt-affecting atoms, but there is no durable counter or machine-enforced trigger across sessions. In a 75–120 session program, this will be missed repeatedly, leading to contradictory micro-rules and rising scholarly error rates. fileciteturn2file0

**SEVERITY:** HIGH

**SECTION:** §4.12; §7 handoff template sections don’t include a “prompt-affecting count since last coherence review” field; context-management warns compaction fragility. fileciteturn2file0turn10file0

**SCENARIO (Sessions 6–15, gradual prompt incoherence):**
1. Prompt-affecting atoms are processed in multiple short sessions (5–8 atoms/session target). fileciteturn2file0  
2. Each session adds 1–2 prompt tweaks; no one remembers whether they crossed the “5 prompt-affecting” boundary since the last coherence review. fileciteturn2file0turn10file0  
3. Contradictions appear (“keep title even if no linking word” vs “don’t excerpt mentions”), and the model’s behavior becomes non-deterministic and genre-skewed. fileciteturn2file0turn4file0  
4. Session 15’s audit sees many scholarly errors, but their cause is emergent prompt incoherence, not any single atom. fileciteturn2file0  

**ROOT CAUSE:** The trigger is defined procedurally but not instrumented; it depends on human memory across compactions and handoffs. fileciteturn2file0turn10file0

**PROPOSED FIX (amend §7.2 handoff template + §4.12):**
- Add to §7.2 “Prompt changes” line:  
  **“Prompt-affecting atoms since last coherence review: N. Last coherence review: Session X, date Y.”** fileciteturn2file0  
- Add to §4.12:  
  **“Coherence review is keyed to a ledger counter `PROMPT_AFFECTING_COUNT_TOTAL`. When divisible by 5, coherence review is mandatory before next closure.”** fileciteturn2file0  

**WARNING SIGN:** Prompt is near cap and keeps changing, but no multi-atom prompt coherence review artifacts appear in the ledger for long spans. fileciteturn2file0turn4file0

---

### 14) Prompt refactor gate freezes prompt-affecting atoms but does not enforce a safe migration for “rules moved out of the prompt”

**FINDING:** §4.11 correctly freezes new prompt-affecting atoms when reaching 80% word budget and suggests moving deterministically checkable rules to validators. But it does not define (a) acceptance tests for refactor safety or (b) a migration checklist ensuring removed prompt rules reappear as deterministic validators. This makes refactor sessions a high-risk source of silent regressions. fileciteturn2file0

**SEVERITY:** HIGH

**SECTION:** §4.11; §4.6 validation suite scope (empirical validation only if prompt-affecting, but refactor *is* prompt-affecting and can change meaning broadly). fileciteturn2file0

**SCENARIO (Session 10, refactor removes a critical scholarly safeguard):**
1. Prompt exceeds 80% → freeze; Session 10 is prompt-architecture. fileciteturn2file0turn3file0  
2. To save words, CC compresses or removes a rule that encoded an exception for dialectical structures (e.g., radd/jawāb coupling). fileciteturn2file0  
3. No deterministic validator is added (migration is “medium-term strategy”). Tests pass because they are largely structural/presence checks, and empirical validation is run on too narrow a fixture slice. fileciteturn2file0turn4file0  
4. Subsequent excerpts drift, producing subtle but widespread scholarly decontextualization. fileciteturn2file0  

**ROOT CAUSE:** The protocol formalizes *when* to refactor but not *how to prove the refactor preserved meaning*, especially across the expanded science list. fileciteturn2file0

**PROPOSED FIX (add checklist to §4.11):**
- Append:  
  **“Refactor Safety Checklist (MANDATORY): (1) for every removed/merged rule, record destination: [kept in prompt / moved to validator / moved to tests / deprecated]. (2) run `atom_test.py` on 3 fixtures spanning 3 different sciences. (3) Gemini CLI must supply at least 1 counterexample check for each removed rule class.”** fileciteturn2file0

**WARNING SIGN:** Large prompt edits with only “word count improved” justification, and no explicit “rule migration map” artifact. fileciteturn2file0

---

### 15) Stage 7 “owner brief is informational” conflicts with the actual power of owner objections and encourages underweighting owner signal

**FINDING:** Stage 7 says the owner “does not approve or reject” and their reaction is “signal,” while §4.10 treats owner objection as a hard override that forces reopening. This mixed framing pushes sessions toward treating owner input as optional—especially once delivery is batched—raising the probability that owner-catchable scholarly errors persist. fileciteturn2file0

**SEVERITY:** MEDIUM

**SECTION:** §4.7 owner brief framing; §4.10 objection override; §4.15 batching. fileciteturn2file0

**SCENARIO (Session 9, owner disagreement doesn’t trigger reopen):**
1. Owner gives a weak negative reaction in a batch summary (“feels off”). fileciteturn2file0  
2. Because Stage 7 frames the brief as informational and owner as non-approver, CC treats it as “future signal,” not as a reopen trigger. fileciteturn2file0  
3. The “wrongness” would have been concrete if the owner saw the full brief; batching obscures it. fileciteturn2file0  
4. The atom remains CLOSED; later audits reveal it was indeed wrong. fileciteturn2file0  

**ROOT CAUSE:** The protocol doesn’t distinguish between “owner as decision-maker” (not desired) and “owner as safety-critical validator” (functionally required). fileciteturn2file0

**PROPOSED FIX (amend Stage 7 wording):**
- Replace “owner does not approve or reject” with:  
  **“Owner does not vote on consensus, but owner objections on intent/reading-experience are safety-critical and trigger automatic reopening (§4.10).”** fileciteturn2file0

**WARNING SIGN:** Owner feedback is logged as “signal for later” without either (a) reopening, or (b) a concrete explanation of why it is not an objection. fileciteturn2file0

---

### 16) “Never bulk atoms” is declared, but the protocol permits subtle batching via grouped implementation + ledger patterns, and repo artifacts show batching pressure is real

**FINDING:** The protocol bans bulking yet allows grouped implementation (up to 3), and the surrounding repo artifacts reflect processing in thematic batches. Without an explicit mechanism that prevents “batch thinking” during analysis/challenge (not just implementation), the system returns to the failure mode Session 2 reported: context exhaustion + missed edge cases. fileciteturn2file0turn14file0turn4file0

**SEVERITY:** HIGH

**SECTION:** Hard Rule 11 “Never bulk atoms”; §4.6 grouped implementation note; `.kr/HANDOFF.md` “6 thematic batches” summary; ledger “batch” register. fileciteturn2file0turn14file0turn4file0

**SCENARIO (Session 7, partial batching reappears):**
1. CC selects 3 related atoms and expands them “together” to save time, intending to implement as a group (permitted). fileciteturn2file0  
2. Even if each atom gets a ledger entry, the *cognitive work* (exceptions, counterexamples, interaction mapping) is done in batch mode. fileciteturn2file0  
3. Coworker prompts become less specific, coworker feedback becomes cross-contaminated, and subtle atom-specific risks are missed. fileciteturn2file0turn5file0  
4. “Closed” atoms look compliant but have hidden gaps, accumulating into the Session 15 discovery. fileciteturn2file0turn4file0  

**ROOT CAUSE:** The protocol enforces per-atom artifacts, but does not enforce per-atom *attention isolation* (which is the real anti-batching property). fileciteturn2file0

**PROPOSED FIX (amend §4.6 grouped implementation rule):**
- Add:  
  **“Grouped implementation does NOT permit grouped expansion/challenge. Evidence: each atom must have a distinct Stage 3 document and distinct coworker prompts (no shared ‘combined prompt’ except in `research` DR class).”** fileciteturn2file0

**WARNING SIGN:** Coworker prompts reuse the same expansion content across multiple MAQ-IDs, or DR prompts are framed as “review these atoms together.” fileciteturn2file0turn3file0

---

### 17) Doctrine drift is not countered by any scheduled re-audit/backfill mechanism after protocol amendments

**FINDING:** §8 establishes self-improvement (retro + amendments) but provides no “migration/backfill” protocol for already-closed atoms when doctrine changes. In a long operation with multiple amendments, this guarantees a growing population of CLOSED atoms that are incompatible with current doctrine—exactly the kind of “hidden gap” that appears as a large error rate later. fileciteturn2file0

**SEVERITY:** HIGH

**SECTION:** §8 amendment process; reopen protocol only triggers on implementation conflicts, not doctrine drift; ledger shows many atoms / batches already recorded as terminal-ish states. fileciteturn2file0turn4file0

**SCENARIO (Sessions 4–15, “silent drift accumulation”):**
1. Session 6 amends the interpretation of an indivisible unit (e.g., adds/changes handling of sabab al‑nuzūl coupling). fileciteturn2file0  
2. Previously CLOSED atoms that touched related boundaries remain CLOSED, because reopen protocol is only invoked when a current implementation forces a change to a finalized atom. fileciteturn2file0  
3. Over time, closure semantics become inconsistent: older atoms violate newer invariants, but nothing triggers reopening. fileciteturn2file0turn4file0  
4. Session 15’s audit discovers a high error rate concentrated in “old closures pre‑amendment.” fileciteturn2file0  

**ROOT CAUSE:** Protocol change management lacks a “schema migration” equivalent: no sampling audit, no backfill requirement, and no constraint that “amendment implies review of affected closures.” fileciteturn2file0

**PROPOSED FIX (add §8.4 “Doctrine Backfill Protocol”):**
- Add new subsection §8.4:  
  **“Any amendment that changes either (a) Cross‑Science Variation categories, (b) Atomic Integrity Risk units, or (c) a prompt rule MUST trigger a backfill audit: sample 5 previously CLOSED atoms impacted by the changed rule. If ≥1 fails, escalate to a targeted reopening campaign.”** fileciteturn2file0

**WARNING SIGN:** Frequent protocol version bumps accompanied by no corresponding reopening activity, despite known “we changed how we do X now” shifts. fileciteturn2file0

---

### 18) The single biggest unaddressed architectural failure mode: process gates verify *inputs and artifacts*, not *outcomes on real Arabic corpora* for most atom classes

**FINDING:** The protocol is strong on artifact discipline (ledger entries, votes, templates) but relatively weak on *systematic outcome verification* beyond “if prompt-affecting run atom_test.py.” Many scholarly errors will not be caught by template completeness or consensus alone, especially when all reviewers share blind spots. This is the most plausible root of a large “CLOSED but wrong” percentage. fileciteturn2file0turn11file0turn4file0

**SEVERITY:** CRITICAL

**SECTION:** §4.6 validation suite; §4.8 Q‑CLOSED; empirical validation conditionality; “no single model conclusion” rule highlights why artifact-only validation is insufficient. fileciteturn2file0turn11file0

**SCENARIO (Session 12, SPEC-structural atoms with no prompt change):**
1. A SPEC-structural rule is adopted that affects boundary decisions conceptually but does not immediately change prompts or validators (e.g., how to treat “bāb headings as rulings in Bukhārī”). fileciteturn2file0turn4file0  
2. Q‑CLOSED can be satisfied (sources quoted, expansion exists, coworker reports exist, ledger updated) without any empirical run that demonstrates behavior on real text. fileciteturn2file0  
3. Months later, when prompts evolve, that conceptual doctrine influences decisions and causes scholarly errors at scale. The issue is discovered only during large-run evaluation or owner spot-check. fileciteturn3file0turn4file0  

**ROOT CAUSE:** The protocol treats empirical verification as mostly prompt-affecting, but scholarly correctness failures often arise from doctrine interactions and later prompt evolution, not from the single atom’s immediate code diff. fileciteturn2file0turn11file0

**PROPOSED FIX (amend §4.8 by adding Q‑12 for high-risk doctrine):**
- Add criterion:  
  **“Q‑12 Outcome Spot‑Check (for any atom tagged ‘cross‑science’ OR touching any ALWAYS INDIVISIBLE unit): run a mini‑fixture (one representative Arabic passage) through the relevant pipeline step and record the observed behavior vs expected.”** fileciteturn2file0

**WARNING SIGN:** Rising number of CLOSED atoms with “no empirical validation needed” while later smoke data reveals regressions in exactly those conceptual domains. fileciteturn2file0turn3file0

## Synthesis of likely and preventable failure causes

### Top likely failure causes for the July 2026 outcome

First: **Closure semantics drift because enforcement is insufficiently machine-checkable.** The protocol explicitly defers machine verification of Q‑CLOSED while depending on ledger attestation; at scale, this becomes performative and yields “closed” atoms missing real guarantees. fileciteturn2file0turn9file0turn4file0

Second: **Scheduling deadlocks (WIP + async + session-type gating) create pressure to game Light Lane and PRELIMINARY status.** When the system produces “no legal productive moves,” operators will bend rules to keep progress, and scholarly risk accumulates exactly in the bypass paths. fileciteturn2file0

Third: **Owner disengagement via batching removes a safety layer while leaving the system believing it still exists.** Owner objection is defined as an override, but owner delivery is optimized away after 50; that mismatch creates a silent failure of the “human backstop.” fileciteturn2file0

### Top preventable causes where protocol amendments now help most

First: **Add a checkpoint-resolution gate and integrate it into gate-precedence.** This closes a major orphan/drift channel and prevents “stale unverified implementations” from lingering across session-type shifts. fileciteturn2file0

Second: **Make coverage tier satisfaction part of G‑CHALLENGED, not just “2 of 3.”** This prevents “technical-only” or “biased” report combinations from substituting for required scholarly validation. fileciteturn2file0turn12file0

Third: **Ship a minimal closure verifier and require it in §0 before closure.** You do not need the full DA‑001 vision to get 80% of the value: enforce ledger markers + sync + queue status deterministically and you eliminate a large class of “claimed closure.” fileciteturn2file0turn9file0

## Single point of failure

**Conflicting sources of operational authority (protocol vs NEXT vs handoffs) is the single-point failure most capable of undermining the entire hardening operation on its own.** The protocol’s success depends on consistent session typing, gating, and closure discipline; when handoff docs and NEXT diverge materially, sessions will fragment into incompatible interpretations, producing doctrine drift and non-uniform closure quality that later reads as “40% error rate.” fileciteturn2file0turn3file0turn14file0turn15file0