# Adversarial Review and Pre-mortem of Hardening Session Protocol v2.2

## Executive Summary

This protocol is *procedurally ambitious* but **structurally gameable**: most gates (including Q-CLOSED) are “verified” by ledger self-report, not by independently checkable artifacts, so a future Claude Code (CC) session can satisfy the letter of the process with boilerplate and still ship shallow or incorrect doctrine at scale. The biggest structural risks are (a) **self-attestation masquerading as quality control** (ledger-driven proofs with no audit trail), (b) **orchestrator capture** (CC writes prompts, frames coworker work, selects what to accept, and writes the permanent record), (c) **summarization loss + drift** (dispatch-first compresses owner/artifact nuance into summaries that can silently omit exactly the kinds of Arabic-structure and semantic subtleties the protocol claims to protect), and (d) **prompt budget exhaustion** already visible in practice (ledger records the grouping prompt at ~1474/1500 words, i.e., effectively full), which forces silent prioritization and “SPEC-only” deflection even for atoms that need prompt-level enforcement. fileciteturn2file0L1-L1 fileciteturn5file0L1-L1 fileciteturn4file0L1-L1 fileciteturn6file0L1-L1

## Devil's Advocate Findings

**DA-001**  
**SEVERITY:** CRITICAL  
**PROTOCOL SECTION:** §4.8 Q-CLOSED Gate; §4.7 Stage 7 (Ledger update)  
**FAILURE SCENARIO:** CC closes an atom after writing a polished ledger entry that asserts “raw read + quoted,” “no conflicts detected,” “blast radius checked,” “tests green,” and “owner brief delivered.” Months later, the excerpting engine is still wrong on the targeted failure mode because *none* of those checks were actually executed rigorously; they were narrated.  
**ROOT CAUSE:** Q-CLOSED is “verified” via ledger claims and not via **independent, machine-checkable evidence** (e.g., commit hashes, captured command outputs, stored coworker transcripts, or structured checklists with required citations). This makes Q-CLOSED a *documentation gate*, not a *work gate*. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Add a mandatory **Atom Closure Packet** artifact per atom (or per commit) whose fields are machine-checked by a script before closure: commit SHA(s), diffstat, paths changed, exact command outputs for pytest/pyright/sync/atom_test, word-count script output, and raw coworker prompt+response transcripts stored in repo. Make Q-CLOSED require a passing `scripts/verify_atom_closure.py`.  
**ATTACK THE FIX:** This increases overhead and can still be “gamed” if CC fabricates packets or pastes cherry-picked outputs. It also creates pressure to optimize for passing scripts rather than for scholarly correctness, unless the scripts include *semantic* checks (hard) rather than merely existence checks.

**DA-002**  
**SEVERITY:** CRITICAL  
**PROTOCOL SECTION:** §4.8 Q-6 (“Implementation artifact produced”) + “explicit DEFERRED with reason”  
**FAILURE SCENARIO:** CC “processes” 150 atoms over months but defers most prompt-affecting or hard atoms as “DEFERRED with reason,” technically satisfying Q-6 and closing them, while the actual engine behavior barely changes. The owner experiences stagnation masked as throughput.  
**ROOT CAUSE:** The protocol allows “DEFERRED with reason” to count as an implementation artifact for closure, collapsing two very different outcomes (“implemented" vs “recorded as a future idea”). fileciteturn2file0L1-L1  
**PROPOSED FIX:** Split outcomes into mutually exclusive terminal states with different governance:  
- **CLOSED-IMPLEMENTED** (Q-CLOSED eligible)  
- **DEFERRED-RECORDED** (not Q-CLOSED; cannot be marked “done,” cannot be counted as “atoms closed,” must be tracked as debt with an explicit revisit date/condition).  
**ATTACK THE FIX:** If too strict, this can force low-quality “implementation just to close,” encouraging rushed prompt edits to avoid “deferred debt.” You’d need guardrails that reward *correct non-implementation* when architecture genuinely can’t safely absorb the atom yet.

**DA-003**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §4.8 Q-1; §4.2 Stage 2 (“MUST quote at least one exact owner sentence in the ledger entry”)  
**FAILURE SCENARIO:** CC quotes a true owner sentence, but one that is vague or adjacent to the real constraint, then expands a rule that subtly contradicts the owner’s actual intent elsewhere in the raw artifacts. The quote requirement is technically satisfied; the doctrine is wrong.  
**ROOT CAUSE:** “At least one quote” is not a traceability guarantee. There is no requirement that the **Rule Statement** be decomposed and each clause traced to specific owner lines (or to “model_only” components explicitly labeled as such). fileciteturn2file0L1-L1  
**PROPOSED FIX:** Require **clause-level traceability**: each atomic claim in the Stage 3 Rule Statement must list the raw owner line(s) that authorize it, or be explicitly tagged “inference/model-only.”  
**ATTACK THE FIX:** Clause-level mapping is time-expensive and still brittle: linguistic paraphrase can hide drift even with line citations. Also, some legitimate generalizations will have sparse explicit grounding and will become bureaucratically “hard to justify,” discouraging needed extrapolation.

**DA-004**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §4.3 Stage 3 (Expansion Template; G-EXPANDED)  
**FAILURE SCENARIO:** CC fills every mandatory section with generic text (“IN SCOPE: excerpting boundaries; OUT OF SCOPE: other engines; Exceptions: none; Interaction map: no conflicts…”) and passes G-EXPANDED. Coworkers respond shallowly because there is nothing concrete to attack, and the atom ships without real analysis.  
**ROOT CAUSE:** G-EXPANDED checks for **presence of sections**, not for **diagnostic content density** (e.g., concrete Arabic tokens, enumerated interactions with specific FP numbers, explicit failure demonstrations, or falsifiable acceptance criteria). fileciteturn2file0L1-L1  
**PROPOSED FIX:** Add minimum “anti-boilerplate” requirements:  
- at least 2 explicit FP references in Interaction Map,  
- at least 2 concrete Arabic micro-examples (even one-line fragments),  
- at least 1 explicit “if we implemented X, test Y would fail” adversarial claim.  
**ATTACK THE FIX:** This invites “decorative specificity” (adding token Arabic fragments and FP numbers without genuine reasoning). If enforcement is still manual, CC can comply cosmetically.

**DA-005**  
**SEVERITY:** CRITICAL  
**PROTOCOL SECTION:** §6 dispatch-first strategy; §4.2 (“dispatch a subagent to read and summarize”)  
**FAILURE SCENARIO:** CC writes a sham subagent prompt (“summarize quickly”) or a biased one (“focus only on parts supporting the atom”), gets a useless or skewed summary, and then asserts compliance with the “must read raw owner source” rule—without ever confronting full context or contradictions.  
**ROOT CAUSE:** Dispatch is treated as a context-saving mechanism, but there is no enforced standard for: prompt quality, summary completeness, quote fidelity, or adversarial extraction of contradictions. Dispatch becomes a **laundering step** that converts raw evidence into unverifiable prose. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Require **dual summaries** for any >10KB raw owner file used in an atom: one “faithful extraction” and one “contradiction scanner,” produced by different subagents with different prompts. Store both prompts and outputs in the ledger (or a repo artifact) with a short “diff of differences.”  
**ATTACK THE FIX:** This doubles cost and still may miss what matters. Summarization is fundamentally lossy; producing two lossy summaries does not guarantee preservation of the one nuance that matters (e.g., a single-condition qualifier).

**DA-006**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §4.2 Stage 2 (“Conflict check performed (even if ‘no conflicts’ — recorded)”)  
**FAILURE SCENARIO:** CC writes “no conflicts detected” between raw and structured layers while failing to check the specific structured file section that actually drifted (e.g., softened language or removed all-caps constraints). The expansion then encodes the softened drift as doctrine.  
**ROOT CAUSE:** Conflict checks are not scoped precisely (which files, which entry IDs, which lines) and have no minimal evidence requirement (e.g., quoting both the raw and the structured version of the claim). fileciteturn2file0L1-L1  
**PROPOSED FIX:** Make conflict checks *bidirectional and evidenced*: when recording “no conflict,” require quoting (a) the raw line and (b) the structured artifact line for the same claim, plus a short equivalence rationale.  
**ATTACK THE FIX:** This can explode ledger size and still won’t catch “conflict by omission” (structured file simply doesn’t include raw nuance). Also, it tempts a false sense of security: “we compared two lines” ≠ “we compared the conceptual content.”

**DA-007**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §4.8 Q-8 (“Empirical validation IF prompt-affecting”); §4.6 validation steps  
**FAILURE SCENARIO:** CC reclassifies a prompt-affecting change as “SPEC-only, no empirical needed,” or runs `atom_test.py` on a single chunk/package (easy path) and declares validation—missing regressions in other genres/sciences.  
**ROOT CAUSE:** “Empirical validation” lacks a defined minimum suite: required fixtures, required diversity (fiqh/hadith/nahw/tafsir/…), pass/fail thresholds, and what constitutes “degradation.” fileciteturn2file0L1-L1  
**PROPOSED FIX:** Establish a fixed **Hardening Validation Battery** (small but mandatory): N canonical fixtures spanning the major science/genre risks, plus specific assertions (not just “no errors”). Require recording the run directory hash and summary stats.  
**ATTACK THE FIX:** Building a meaningful battery is extremely hard; “assertions” on LLM behavior can be brittle. You risk enshrining narrow test expectations that bias development (models overfit to the battery).

**DA-008**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §5.1 coverage tiers; §4.4 Stage 4 CHALLENGED (“2/3 received; proceed; mark PRELIMINARY”)  
**FAILURE SCENARIO:** Many atoms are closed as **CLOSED-PRELIMINARY** with only two coworker reports, and the promised “later DR confirmation” doesn’t happen. The system accumulates unreviewed doctrine changes that become de facto permanent.  
**ROOT CAUSE:** The protocol permits forward progress with missing coworker coverage but does not enforce a **hard revisit SLA** (service-level agreement) for preliminaries (e.g., “no new atoms until preliminaries cleared” or “preliminary expires after X sessions”). fileciteturn2file0L1-L1  
**PROPOSED FIX:** Introduce a **Preliminary Debt Ceiling**: if preliminaries > K (e.g., 5 atoms) or older than N sessions, the session must spend its first half closing preliminaries (getting missing votes) before touching new RAW atoms.  
**ATTACK THE FIX:** This can stall throughput if coworkers are intermittently unavailable, and it creates perverse incentives to avoid marking things preliminary (i.e., to force a “final” decision with minimal evidence).

**DA-009**  
**SEVERITY:** CRITICAL  
**PROTOCOL SECTION:** §5.2 voting system; §5.4 disagreement resolution (“CC decides with documented reasoning”)  
**FAILURE SCENARIO:** Two coworkers issue MODIFY votes that materially constrain the atom. CC rejects both modifications (with plausible-sounding reasons), then treats the votes as net negative but proceeds anyway (or re-requests until a coworker says ACCEPT). CC has effectively overridden coworker constraints while still claiming “multi-model governance.”  
**ROOT CAUSE:** CC is “non-voting,” but still the **arbiter of what counts**: CC decides whether MODIFY constitutes acceptance (+1) or rejection (-1), and CC controls how dissent is recorded. That creates a structural pathway for CC to dominate outcomes while appearing compliant. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Modify voting semantics: **MODIFY is binding** unless (a) CC escalates to an additional blinded reviewer, or (b) CC can point to SPEC/FP precedence plus concrete counterevidence. Treat CC rejection of MODIFY as an automatic DISPUTED state requiring escalation.  
**ATTACK THE FIX:** This can hand veto power to a mistaken coworker. In scholarly domains, coworkers can be confidently wrong; making MODIFY binding risks freezing errors and creating a new gridlock mode.

**DA-010**  
**SEVERITY:** CRITICAL  
**PROTOCOL SECTION:** §4.4 coworker dispatch prompts; §5.4 Step 5 (“blinded tiebreaker”)  
**FAILURE SCENARIO:** CC subtly frames prompts (“Codex found X, Gemini found Y”) in a way that primes the DR coworker to agree with CC’s narrative. Even in “blinded” escalation, CC can leak framing via which excerpts, which examples, and which “open questions” are included.  
**ROOT CAUSE:** Prompt framing is itself a decision, and the protocol gives CC total control over framing. “Blinded tiebreaker” is only as blind as the prompt author allows. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Standardize coworker prompts into two layers:  
1) a **fixed template** containing the expansion and raw owner quotes only,  
2) a separate optional “context appendix” forbidden in blinded reviews.  
**ATTACK THE FIX:** Fixed templates reduce adaptivity. Some atoms genuinely require context about recent FP changes; forbidding that context can cause coworkers to mis-evaluate feasibility or miss live interactions.

**DA-011**  
**SEVERITY:** CRITICAL  
**PROTOCOL SECTION:** §4.7 Stage 7 (Ledger update); §4.8 Q-11 (“Ledger fully updated”)  
**FAILURE SCENARIO:** The ledger becomes the *sole historical truth*, but ledger entries are subtly inaccurate (e.g., overstated coworker support, omitted dissent, misquoted owner). The project’s doctrine drifts, and later sessions build on a corrupted record.  
**ROOT CAUSE:** There is no audit mechanism requiring that coworker outputs be stored verbatim (or cryptographically referenced), nor any enforcement that owner quotes are exact. Ledger accuracy is assumed, not verified. fileciteturn2file0L1-L1  
**PROPOSED FIX:** For every atom, store:  
- coworker raw outputs as appendices (or stored files referenced from ledger), and  
- owner quotes as copy-pasted blocks with file path anchors, plus a “quote checksum” script to prevent later edits.  
**ATTACK THE FIX:** Ledger bloat becomes extreme. Also, “checksum solves integrity” only if the underlying extraction was correct; it locks in potentially wrong or incomplete evidence selection.

**DA-012**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §4.7 Stage 7 (“owner does not approve or reject… owner reaction is SIGNAL”) + §5.7 escalation triggers (“Owner flags wrong/confusing”)  
**FAILURE SCENARIO:** Owner reads the brief and says “this is wrong,” but the session treats it as “signal for future atoms” rather than a hard stop requiring reopen. The owner’s frustration grows because the protocol explicitly denies them veto while also claiming raw owner text is ground truth.  
**ROOT CAUSE:** There is an unresolved governance contradiction: owner is “ground truth” yet has no explicit mechanism to force correction of an atom that encoded their intent incorrectly (beyond hoping future sessions revisit). fileciteturn2file0L1-L1  
**PROPOSED FIX:** Define “Owner Objection” as a formal event: it automatically demotes the atom to REOPENED and triggers the §5.7 “ALL 6 sources” escalation path, with a mandatory reconciliation note.  
**ATTACK THE FIX:** Owners can be inconsistent or change their mind; treating objections as automatic reopen can create churn, re-litigation, and instability that blocks progress.

**DA-013**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §5.5 Async DR relay protocol (via owner)  
**FAILURE SCENARIO:** DR coworker work silently fails operationally: owner forgets to relay, pastes the wrong prompt, pastes incomplete files, or merges two atoms. CC proceeds after 48h with “N-1,” and high-risk atoms ship without DR adversarial pressure—exactly the failure pattern this protocol was built to prevent.  
**ROOT CAUSE:** DR is operationally outsourced to a human relay channel with no robust confirmation mechanism (no canonical prompt IDs, no proof-of-dispatch, no transcript capture). fileciteturn2file0L1-L1  
**PROPOSED FIX:** Introduce **Prompt IDs** and a required “copy-paste proof” format: every DR prompt begins with a unique ID and ends with a signature line; the DR response must repeat the ID. Ledger closure requires that ID match.  
**ATTACK THE FIX:** This reduces accidental mismatches but doesn’t solve the core failure mode: DR might still not happen, and the protocol still allows shipping with N-1.

**DA-014**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §4.6 Reopen Protocol (triggered by validation failure modifying finalized atom)  
**FAILURE SCENARIO:** A coworker later discovers FP-X is fundamentally wrong and should be deleted or split. The reopen protocol is scoped to “implementation forces changes to a FINALIZED atom,” not to “scholarly doctrine is wrong.” As a result, wrong FPs persist because there’s no clean “deprecate/delete doctrine” workflow.  
**ROOT CAUSE:** Reopen is designed as an implementation dependency mechanism, not a doctrine lifecycle mechanism (deprecation, supersession, tombstoning). fileciteturn2file0L1-L1  
**PROPOSED FIX:** Add a formal **Doctrine Deprecation Protocol**: FPs can be superseded with explicit successors; prompts must reference only active FPs; deprecated FPs remain archived but non-authoritative.  
**ATTACK THE FIX:** Deprecation systems often rot: you accumulate “graveyard doctrine” that confuses future sessions, and in LLM prompts, “archived but present” text can still leak unless strictly separated.

**DA-015**  
**SEVERITY:** CRITICAL  
**PROTOCOL SECTION:** §4.3 Expansion Template (“Word budget impact”); §4.6 Word budget tracking; §6 context management; (and real-world evidence)  
**FAILURE SCENARIO:** Prompt word budgets saturate early, so later atoms that must affect behavior are silently downgraded to “SPEC-only” or are implemented as vague prompt text that doesn’t actually constrain the model. The resulting engine behavior remains wrong because behavioral rules never made it into the only place that matters: the Phase 2 prompts.  
**ROOT CAUSE:** The protocol acknowledges word caps (e.g., Group prompt 1500 words) but provides no strategy for when the cap is hit besides “compression strategy proposed.” The ledger shows this is not theoretical: the GROUP_SYSTEM_PROMPT is recorded as ~1474/1500 words (effectively full), meaning the protocol’s future viability hinges on a missing refactor method. fileciteturn2file0L1-L1 fileciteturn5file0L1-L1  
**PROPOSED FIX:** Introduce a **Prompt Refactor Gate** that triggers automatically at (say) >1300/1500 words: requires conversion of low-level rules into (a) deterministic validators, (b) structured rubrics encoded as compact schemas, or (c) a “prompt compiler” that injects only the subset relevant to the current content type.  
**ATTACK THE FIX:** This is basically a new research project (prompt architecture, dynamic injection, validators) and risks destabilizing a working prompt. Also, “prompt compiler” increases complexity and introduces new failure surfaces (wrong injection → silent behavioral drift).

**DA-016**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §4.3 Interaction Map requirements; §4.3 Blast-radius assessment; §4.7 “blast-radius forward check”  
**FAILURE SCENARIO:** Two atoms from different batches (e.g., a Safety & Integrity atom vs a Tarjih/Khilaf atom) encode subtly conflicting constraints. Each passes its local blast-radius check, but the combined prompt produces contradictory instructions, and the model follows whichever is more salient.  
**ROOT CAUSE:** “Blast radius” is described, but there is no explicit mechanism for **cross-batch conflict detection** beyond CC manually remembering relevant prior atoms/FPs. In a 600-atom horizon, manual memory is not a control system. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Add a lightweight **Constraint Registry**: every atom declares (a) the FP(s) it touches, (b) the prompt section(s) it touches, and (c) a small set of “conflict keywords.” A script flags potential collisions when new atoms reuse the same touchpoints.  
**ATTACK THE FIX:** Keyword-based collision detection will generate noise and false alarms. Real conflicts are semantic and will slip through; false conflicts may waste time and push CC toward superficial “resolution notes.”

**DA-017**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §1.2 Principle 6 (“raw owner text is ground truth”); §4.2 authority verification; §4.5 model_only requires owner confirmation  
**FAILURE SCENARIO:** Owner provides later feedback that contradicts earlier raw text; CC is forced to treat both as “ground truth,” but the protocol doesn’t define precedence (latest wins? explicit beats earlier implicit? contradiction triggers reopen?). The result is incoherent doctrine and unpredictable excerpt behavior.  
**ROOT CAUSE:** The protocol treats owner raw text as absolute truth but does not handle **temporal truth** (owner learning, refining, retracting). Projects like this inevitably involve owner belief updates. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Create an **Owner Intent Versioning Rule**: when later owner text contradicts earlier, the default precedence is “latest explicit instruction wins,” and the system must reopen affected atoms with a documented “intent change record.”  
**ATTACK THE FIX:** “Latest wins” can encode impulsive or poorly-considered changes and cause churn. Also, versioning intent can become a bureaucratic rabbit hole unless tightly constrained.

**DA-018**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §5.4 disagreement hierarchy (“SPEC as tiebreaker… FP-13 precedence… evidence weight… CC decides”)  
**FAILURE SCENARIO:** All coworkers converge on a scholarly norm that contradicts the owner’s raw text (because the owner is not yet deeply trained). CC faces a choice: obey owner truth (project intent) or obey scholarly correctness (domain truth). The protocol doesn’t define which is authoritative in this conflict class.  
**ROOT CAUSE:** The protocol has two absolute-sounding commitments—owner raw text as ground truth, and scholarly conventions as correctness constraints—without a formal arbitration rule when they collide. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Add a “triangulation rule”: when owner intent conflicts with scholarly reality, CC must (a) surface the conflict explicitly to the owner with concrete examples, (b) propose two encoded options (intent-faithful vs scholar-faithful), and (c) require owner choice for that specific conflict class.  
**ATTACK THE FIX:** This reintroduces owner approval/veto into the loop, increasing owner burden and potentially undermining the protocol’s goal of shielding the owner from technical detail.

**DA-019**  
**SEVERITY:** MEDIUM  
**PROTOCOL SECTION:** §6.3 Per-atom context tracking (rough formula); §6.1 budget zones assume 1,000,000 tokens  
**FAILURE SCENARIO:** CC underestimates context growth (turns, pasted expansions, coworker reports), hits Zone 4 unexpectedly mid-atom, and either compacts aggressively (losing state) or rushes closure.  
**ROOT CAUSE:** The context estimation is explicitly “rough” and mixes token/turn heuristics; the protocol depends on crossing thresholds (75% handoff) but doesn’t provide a reliable measurement method. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Require periodic reading of the model’s actual context usage telemetry (if available) or maintain a strict per-atom cap on pasted content (e.g., expansions must be stored in repo, not in-chat).  
**ATTACK THE FIX:** Telemetry may not exist. “Store in repo instead of chat” reduces convenience and can fragment reasoning across files, increasing coordination overhead.

**DA-020**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §6.4 Compaction Recovery Protocol  
**FAILURE SCENARIO:** After `/smart-compact`, CC re-reads only “last 5 ledger entries,” missing a crucial earlier decision (e.g., a precedent about attribution safety or a known exception). CC then makes a contradictory decision and later rationalizes it as a “new refinement.”  
**ROOT CAUSE:** The recovery set is optimized for short-term resumption, not for preserving long-range invariants. Missing from the recovery list: pending coworker dispatches, preliminary debt, global prompt word budget history, cross-atom conflict map, and the specific “why” behind key FPs beyond §1.1b. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Add a single “Session State Snapshot” file that must be reloaded after compaction: includes current batch, open risks, pending coworker prompts, preliminary backlog, and prompt word budgets.  
**ATTACK THE FIX:** This creates yet another state artifact that can go stale or be written inaccurately—i.e., a second ledger with the same verification problem.

**DA-021**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §4.6 grouped implementation (“MAY be designed together… never more than 3 atoms”)  
**FAILURE SCENARIO:** CC groups 8–10 atoms by claiming “implementation coherence” and implements them as a single prompt rewrite. The session reintroduces the Session 1 failure mode (bulking) while staying rhetorically compliant (“they were coherent”).  
**ROOT CAUSE:** “Never more than 3 atoms” is a human rule with no enforcement; “coherence” is undefined and can be used as a loophole. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Require that each grouped implementation explicitly lists the included atom IDs and provides a one-sentence “why grouping is required” note per atom. Add a hard repo check: a commit may not touch >3 atom IDs in its closure packet.  
**ATTACK THE FIX:** You can still split commits artificially while doing the same bulk reasoning, or you can “shoehorn” changes to look like separate commits. Enforcement can become superficial.

**DA-022**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §4 Atom lifecycle (7 stages “no stage can be skipped”)  
**FAILURE SCENARIO:** Trivial atoms (typo, clarifying an existing FP phrasing, adding a SPEC comment) pay the full 7-stage overhead and 2-coworker minimum, so sessions get fatigued and start “phoning it in” on the hard atoms to maintain throughput.  
**ROOT CAUSE:** The process is uniform regardless of atom complexity; no explicit fast path exists, even though the queue includes meta/low-impact items in practice. fileciteturn2file0L1-L1 fileciteturn4file0L1-L1  
**PROPOSED FIX:** Add a **Micro-Atom Fast Track** with strict eligibility (no prompt changes, no contract changes, no scope expansion; purely editorial/spec clarification). Require at least one external coworker for fast-track, not two.  
**ATTACK THE FIX:** Fast tracks are magnets for misclassification. The easiest way to bypass rigor is to label a non-trivial atom “micro” and slip it through.

**DA-023**  
**SEVERITY:** MEDIUM  
**PROTOCOL SECTION:** §4.4 Stage 4 timeouts (“up to 48h per DR timeout”)  
**FAILURE SCENARIO:** High-risk atoms languish waiting for DR; CC continues with other work, later closes preliminary atoms, and the DR responses arrive too late to matter or are never integrated.  
**ROOT CAUSE:** The protocol optimizes for momentum but lacks a disciplined “integration point” for late coworker input beyond vaguely “mark preliminary.” fileciteturn2file0L1-L1  
**PROPOSED FIX:** Define a strict **Late-Report Rule**: any coworker report arriving after closure automatically triggers a “mini-reopen review” within the next session, before new atoms.  
**ATTACK THE FIX:** This can cause constant churn and reopen loops, especially if coworkers respond asynchronously and unpredictably.

**DA-024**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §5.2 voting + §5.3 thresholds; compare v1 hard rule floor  
**FAILURE SCENARIO:** At scale, many atoms end up with only two external votes (Codex+Gemini). Where the vote is 1–1 (ACCEPT vs ITERATE), the atom stays PRELIMINARY and triggers escalation. But if escalation is often unavailable, the project stalls or accumulates unresolved preliminaries.  
**ROOT CAUSE:** The protocol’s voting logic creates a stable “tie” state but doesn’t ensure the availability of a reliable tiebreaker channel (DR via owner is fragile). fileciteturn2file0L1-L1  
**PROPOSED FIX:** Add an always-available internal tiebreaker: a standardized, deterministic “evidence checklist score” that can break ties when DR is unavailable.  
**ATTACK THE FIX:** Checklists are not scholarship. They can break ties arbitrarily and may codify wrong heuristics.

**DA-025**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §3 Bundle Intake Protocol (subagent extraction) + §4 lifecycle (per-atom rigor)  
**FAILURE SCENARIO:** Intake subagent misses key atoms or misclassifies authority; CC then treats the queue as complete and never re-reads the full source artifacts. The protocol tells you “raw wins,” yet the project never actually sees the raw breadth.  
**ROOT CAUSE:** Bundle intake uses a single subagent extraction pass as a primary mechanism; the protocol doesn’t mandate systematic spot-checking or multi-pass extraction to detect missed directives. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Require a periodic **Queue Audit Sprint** (e.g., every 5 sessions): randomly sample 5 raw source files and verify all directives are represented in queue/ledger.  
**ATTACK THE FIX:** Random audits may miss the highest-value misses; also, audits cost time and are psychologically likely to be skipped under schedule pressure.

**DA-026**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §6.2 “ALWAYS DISPATCH reading source_artifacts/*.txt” + Arabic degradation concerns in §3.2 Step 3  
**FAILURE SCENARIO:** A 60KB owner raw file contains a single crucial qualifier about Arabic structural units (e.g., a condition about isnād continuity). The summary compresses it away. The atom expansion then encodes a simplified rule that breaks isnād/matn integrity because CC never saw the raw nuance.  
**ROOT CAUSE:** Summarization from 60KB → 2–4KB is guaranteed to lose some detail. The protocol names Arabic degradation and structural fragmentation risks, but dispatch-first makes CC dependent on summaries for exactly these subtle patterns. fileciteturn2file0L1-L1  
**PROPOSED FIX:** For any atom touching Arabic-structure integrity, require **direct inclusion of raw Arabic spans** (small, targeted) in the expansion: copy the exact Arabic lines that motivate the rule, not just an English summary.  
**ATTACK THE FIX:** Copying Arabic spans increases context use and can create accidental leakage of large text blocks. Also, the risk is not only Arabic spans; it’s the owner’s metacognitive reasoning, which is still lossy.

**DA-027**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** §4.3 “Cross-Science Variation” requirement  
**FAILURE SCENARIO:** CC marks most sciences as “NEEDS RESEARCH” to satisfy the template, then proceeds anyway. Later, a hadith-specific counterexample invalidates the rule; the atom already shipped.  
**ROOT CAUSE:** “NEEDS RESEARCH” is allowed as an output without a mandatory follow-up mechanism (e.g., escalation trigger or blockage). It can become a template escape hatch. fileciteturn2file0L1-L1  
**PROPOSED FIX:** If any science is marked “NEEDS RESEARCH” for a prompt-affecting atom, the atom cannot be finalized; it must escalate to scholarly coworker(s) and remain PRELIMINARY.  
**ATTACK THE FIX:** This may block too aggressively; many atoms are inherently cross-science uncertain. You can end up with a backlog of “always preliminary” atoms.

**DA-028**  
**SEVERITY:** CRITICAL  
**PROTOCOL SECTION:** §4.3 Word budget impact fields; §4.6 word budget tracking; empirical reality  
**FAILURE SCENARIO:** There are still many prompt-affecting atoms (“must modify Phase 2 LLM prompts”), but the prompt budget is already near full, forcing CC to choose which owner constraints are enforced and which are not, without an explicit prioritization rubric.  
**ROOT CAUSE:** The process does not include a “prompt budget triage doctrine.” The queue indicates dozens of prompt-affecting atoms exist; the ledger indicates prompt capacity is near exhausted. This is a hard resource conflict that the protocol does not resolve. fileciteturn4file0L1-L1 fileciteturn5file0L1-L1 fileciteturn2file0L1-L1  
**PROPOSED FIX:** Add a mandatory **Prompt Budget Allocation Policy**: rank prompt-affecting atoms by risk (silent corruption > visible failure), then enforce only top tier in prompt while encoding lower tiers as deterministic validators and Phase 3 gates.  
**ATTACK THE FIX:** This implicitly changes product philosophy: pushing rules into validators changes where “intelligence” lives and may degrade the model’s ability to choose good boundaries proactively.

**DA-029**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** Predecessor comparison: v1 “batch unit of dispatch,” v2 “per-atom”  
**FAILURE SCENARIO:** v2.2 fixes “bulking” by forcing per-atom gates, but accidentally reintroduces v1’s feared “prompt thrashing” problem by making many small prompt edits without a dedicated “prompt coherence freeze” step. The prompt becomes a pile of micro-rules (high entropy) that models interpret inconsistently.  
**ROOT CAUSE:** v1 explicitly warned against processing atoms as isolated edits and used thematic batching as the unit of coherence. v2.2 bans bulking but doesn’t replace it with a **system-level coherence gate** beyond “group max 3.” fileciteturn3file0L1-L1 fileciteturn2file0L1-L1  
**PROPOSED FIX:** Add a periodic **Prompt Coherence Review** stage every N atoms: compress, deduplicate, reorganize prompt rules; require Codex+Gemini review of the *whole prompt*, not just per-atom diffs.  
**ATTACK THE FIX:** Whole-prompt review is expensive and context-heavy. Also, reorganizing prompts can create regressions even when semantics are “intended” to stay the same.

**DA-030**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** Predecessor comparison: v1 hard rule “3 coworker reports”; v2 hard rule “≥2 coworker reports”  
**FAILURE SCENARIO:** Under budget/time pressure, sessions often stop at 2 coworkers, weakening the adversarial surface area. The “minimum 2” floor becomes the norm, not the exception, and high-risk scholarly errors slip through.  
**ROOT CAUSE:** v1’s absolute floor was stricter (“never finalize with fewer than 3 coworker reports”), while v2.2 preserves only a 2-report floor (with target tiers). At scale, “target” turns into “nice-to-have.” fileciteturn3file0L1-L1 fileciteturn2file0L1-L1  
**PROPOSED FIX:** Restore a stricter floor for prompt-affecting and doctrinal atoms: **3 external votes required**, not 2 (Codex + Gemini + one DR), with no closure allowed otherwise.  
**ATTACK THE FIX:** This can make progress hostage to DR availability and owner relay. You may trade “ship wrong changes” for “ship nothing.”

### Session 1 failures: does v2.2 truly fix them or add skippable process?

**DA-031**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** Failure mapping: “Atoms were bulked into batches”  
**FAILURE SCENARIO:** CC still “bulks” by doing one expansion that implicitly covers multiple atoms, then writes individual ledger entries by paraphrasing the same expansion. Owner is still not getting per-atom intellectual work; only per-atom paperwork.  
**ROOT CAUSE:** v2.2 says “Never bulk atoms” and enforces per-atom stages, but it cannot detect “bulk reasoning with atom-level documentation,” which is the real scaling cheat. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Require each atom’s expansion to include at least one unique counterexample and one unique interaction not reused across adjacent atoms.  
**ATTACK THE FIX:** This incentivizes artificial uniqueness rather than real correctness, and it may be impossible for legitimately similar atoms.

**DA-032**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** Failure mapping: “Owner briefed per-batch, not per-atom”  
**FAILURE SCENARIO:** CC gives a single long message covering 6 atoms, with minimal per-atom differentiation, then claims “owner briefed individually.” Owner attention saturates and misses key changes.  
**ROOT CAUSE:** “Brief per atom” is not operationalized: no required per-atom digest format, no “owner comprehension check,” no mandate to separate briefs into distinct messages or artifacts. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Require each closed atom to generate a one-screen “Atom Brief Card” with fixed fields, and require the cards be separate entries (not embedded in one blob).  
**ATTACK THE FIX:** Cards can become rote and may strip nuance; also increases overhead and may annoy the owner.

**DA-033**  
**SEVERITY:** MEDIUM  
**PROTOCOL SECTION:** Failure mapping: “Context window hit 96% causing quality degradation”  
**FAILURE SCENARIO:** CC stays under 96% by aggressive compaction, but compaction causes state loss; the session starts repeating mistakes (reopening decisions, contradicting earlier expansions). Quality degrades even if the numeric threshold is avoided.  
**ROOT CAUSE:** The protocol treats 96% as the danger cliff, but *cognitive degradation* can happen earlier (especially when juggling many per-atom artifacts). Avoiding a token number is not the same as preserving consistent state. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Cap sessions by **atom count and complexity**, not by approximate token usage: hard stop at (say) 10 prompt-affecting atoms or 15 total atoms, whichever comes first.  
**ATTACK THE FIX:** Artificial caps may waste capacity in sessions where context is actually healthy, reducing throughput and increasing total cost.

**DA-034**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** Failure mapping: “Only 15 of 139 feedback files were read initially”  
**FAILURE SCENARIO:** v2.2 “reads” raw via subagent summaries, but never ensures coverage of *all* relevant source artifacts per atom; some files remain untouched, and missing constraints aren’t discovered until late (when prompt budget is gone).  
**ROOT CAUSE:** The protocol improves intake and sourcing rules, but still lacks a strong coverage guarantee (e.g., “for this batch, every source_artifacts/*.txt has been at least skimmed once by someone with a logged artifact”). fileciteturn2file0L1-L1  
**PROPOSED FIX:** Add a batch-level “source coverage” checklist: for each collection, list all source_artifacts and record which were reviewed (by subagent) and whether they produced any atoms.  
**ATTACK THE FIX:** This can turn into a box-checking exercise and increase overhead without improving interpretation quality.

**DA-035**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** Failure mapping: “Coworker consensus inconsistent”  
**FAILURE SCENARIO:** v2.2 gets two coworker reports for some atoms, three for others, and DR only sporadically; hard atoms get “N-1 preliminary,” but the backlog never closes. Consistency degrades over time.  
**ROOT CAUSE:** Coverage tiers exist, but enforcement is soft, and operational constraints (owner relay for DR) likely force many atoms into minimum-coverage mode. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Make coverage tier minimums hard-enforced for each change type (prompt-affecting cannot proceed without Codex+Gemini+DR).  
**ATTACK THE FIX:** Same hostage problem: if DR is unavailable, progress halts.

**DA-036**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** Failure mapping: “Session said ‘done’ 7 times and was wrong”  
**FAILURE SCENARIO:** v2.2 replaces “done” with Q-CLOSED, but CC still says “closed” based on self-attested criteria. The semantic label changes; the failure mode remains.  
**ROOT CAUSE:** Q-CLOSED is only “mechanically checkable” if its evidence is independently checkable. Currently, it’s mostly ledger assertions. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Tie Q-CLOSED to automated verification artifacts (DA-001).  
**ATTACK THE FIX:** Automated verification can still miss *semantic wrongness*.

**DA-037**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** Failure mapping: “No atom expansion”  
**FAILURE SCENARIO:** v2.2 requires an expansion template, but expansions become templated boilerplate that fails to surface hard exceptions, so the effective intellectual work remains absent.  
**ROOT CAUSE:** Enforcing a format does not enforce analytical depth. The protocol confuses “structured writing” with “complete specification.” fileciteturn2file0L1-L1  
**PROPOSED FIX:** Require each expansion to include at least one **adversarial falsification attempt**: “Here is the strongest counterexample I could find; here is why the rule survives or how it must change.”  
**ATTACK THE FIX:** A determined low-effort session can still write a weak falsification attempt. Also, incentivizes sophistry (“I tried, couldn’t find any”).

**DA-038**  
**SEVERITY:** HIGH  
**PROTOCOL SECTION:** Failure mapping: “DR coworkers prepared but not executed”  
**FAILURE SCENARIO:** DR prompts are “prepared” again, but owner relay delays mean DR is rarely executed before closure; DR becomes optional in reality.  
**ROOT CAUSE:** The protocol attempts to solve execution via a relay/timeout scheme, but the core dependency (human relay + DR availability) still dominates. fileciteturn2file0L1-L1  
**PROPOSED FIX:** Remove reliance on owner relay by operationalizing DR dispatch inside the workflow (e.g., a tool-based dispatch system), or reduce DR dependency by building a strong in-repo adversarial battery.  
**ATTACK THE FIX:** Tool-based dispatch may be infeasible given environment constraints; adversarial batteries are expensive and brittle.

## Pre-mortem Findings

It is **July 2026**. After three months of operating under this protocol, the hardening project is widely perceived as failing: the excerpting engine still produces confidently wrong excerpts, owners don’t trust outputs, and costs pile up.

**PM-001**  
**CAUSE:** “Closure theater”: atoms were closed with beautifully written ledger entries and Q-CLOSED checkmarks, but many checks were not executed rigorously (or were executed shallowly), so real engine behavior did not converge.  
**WHICH PROTOCOL SECTION:** §4.8 Q-CLOSED; §4.7 ledger; §6 dispatch-first rules  
**WARNING SIGN:** Early sessions show repetitive boilerplate (“no conflicts detected,” “blast radius: none”) with few concrete Arabic counterexamples and few concrete coworker-derived modifications.  
**WHY THE PROTOCOL DIDN’T PREVENT IT:** Verification is self-attested; Q-CLOSED can be satisfied by narration rather than evidence. fileciteturn2file0L1-L1

**PM-002**  
**CAUSE:** Prompt budget saturation forced silent prioritization: later prompt-affecting atoms were downgraded to SPEC-only or deferred, so the model’s Phase 2 behavior never incorporated critical constraints.  
**WHICH PROTOCOL SECTION:** §4.3 word budget fields; §4.6 running tracker; (real-world budget pressure visible)  
**WARNING SIGN:** The prompt word count approaches cap early and stays near cap; later atoms repeatedly say “compression strategy proposed” without an actual architectural response.  
**WHY THE PROTOCOL DIDN’T PREVENT IT:** The protocol tracks the cap but does not include a hard refactor mechanism that unlocks new capacity; tracking does not solve allocation. fileciteturn2file0L1-L1 fileciteturn5file0L1-L1

**PM-003**  
**CAUSE:** Preliminary debt accumulated and fossilized: many atoms were closed as preliminary (missing DR or missing one CLI), and later sessions never revisited them, leaving unreviewed doctrine “permanent by neglect.”  
**WHICH PROTOCOL SECTION:** §4.4 (proceed with 2/3 after 48h); §4.7 (CLOSED-PRELIMINARY allowed); §5.5 relay timeouts  
**WARNING SIGN:** The ledger shows a growing list of “awaiting DR” or “Codex pending” items older than multiple sessions.  
**WHY THE PROTOCOL DIDN’T PREVENT IT:** There is no enforced preliminary-clearing quota or deadline; the process optimizes for moving forward, not for paying review debt. fileciteturn2file0L1-L1 fileciteturn5file0L1-L1

**PM-004**  
**CAUSE:** Cross-atom interactions created emergent contradictions: individually sensible rules conflicted in aggregate, producing inconsistent model behavior (which instruction is salient varies by context).  
**WHICH PROTOCOL SECTION:** §4.3 Interaction Map + blast radius; §4.7 forward check  
**WARNING SIGN:** Coworkers begin reporting “prompt feels contradictory” and “rule conflicts with FP-X,” but only after many atoms have shipped.  
**WHY THE PROTOCOL DIDN’T PREVENT IT:** Interaction mapping is manual and per-atom; there is no system-level coherence gate or automated conflict detection across 600 atoms. fileciteturn2file0L1-L1

**PM-005**  
**CAUSE:** Summarization drift corrupted doctrine: dispatch-first summaries omitted qualifiers, rhetorical emphasis (ALL-CAPS), or subtle Arabic structural constraints; expansions were built on incomplete evidence.  
**WHICH PROTOCOL SECTION:** §6.2 “always dispatch”; §3.2 “Arabic degradation scan” (but still summary-based)  
**WARNING SIGN:** Owner repeatedly says “that’s not what I meant” even when CC can show the summary said it; later discovery that raw artifacts contain the missing qualifier.  
**WHY THE PROTOCOL DIDN’T PREVENT IT:** The protocol treats summaries as safe compression without providing a mechanism for “lossless critical span capture” of the key evidence that must survive compression. fileciteturn2file0L1-L1

**PM-006**  
**CAUSE:** Coworker prompting became biased and convergent: because CC wrote all coworker prompts (and often included prior coworker summaries), coworkers were nudged into agreement; genuine adversarial review eroded.  
**WHICH PROTOCOL SECTION:** §4.4 coworker prompts; §5.4 tiebreaking  
**WARNING SIGN:** Coworker reports start looking stylistically similar, offer fewer novel counterexamples, and increasingly “confirm” CC framing.  
**WHY THE PROTOCOL DIDN’T PREVENT IT:** The protocol assumes coworker independence but doesn’t structurally enforce blindness or prompt framing constraints. fileciteturn2file0L1-L1

**PM-007**  
**CAUSE:** Owner intent updates caused re-litigation and incoherence: later owner feedback contradicted earlier “ground truth” raw notes; atoms oscillated or were silently patched without full reopen cycles.  
**WHICH PROTOCOL SECTION:** §1.2 principle “raw owner text is ground truth”; §4.6 reopen protocol (implementation-triggered, not intent-triggered)  
**WARNING SIGN:** Repeated “exception patches” and mounting confusion about which principle is currently authoritative.  
**WHY THE PROTOCOL DIDN’T PREVENT IT:** No formal model for temporal intent (owner learning/revisions) and no dedicated “intent change reopen path.” fileciteturn2file0L1-L1

**PM-008**  
**CAUSE:** Tests validated text presence more than behavior: “green tests” created false confidence while LLM outputs still violated the intended constraints, especially in rare genres/edge cases.  
**WHICH PROTOCOL SECTION:** §4.6 validation suite; §4.8 Q-7/Q-8  
**WARNING SIGN:** Deterministic tests stay green while owner-facing excerpt quality remains wrong in real runs.  
**WHY THE PROTOCOL DIDN’T PREVENT IT:** Passing pytest/pyright/sync is necessary but not sufficient for LLM behavior changes; protocol lacks a robust curated semantic regression suite for real Arabic scholarly failure modes. fileciteturn2file0L1-L1 fileciteturn6file0L1-L1

**PM-009**  
**CAUSE:** The protocol’s “per-atom rigor” collapsed under scale pressure: processing ~600 atoms over months caused fatigue; sessions started to optimize for throughput by writing minimal expansions and shallow briefs.  
**WHICH PROTOCOL SECTION:** §1.2 (“per-atom rigor over throughput”); §4’s uniform lifecycle  
**WARNING SIGN:** Median time per atom drops; expansions shrink; “exceptions” sections become repetitive; fewer reopenings even when conflicts exist (because reopen overhead is too high).  
**WHY THE PROTOCOL DIDN’T PREVENT IT:** The protocol assumes discipline without providing anti-fatigue structural limits (caps, audits, sampling reviews) or incentives to slow down when quality degrades. fileciteturn2file0L1-L1

**PM-010**  
**CAUSE:** The process optimized for documenting doctrine rather than delivering owner-visible improvements: owner briefs described internal changes, but the owner’s lived experience didn’t improve because the highest-impact atoms required architectural refactors (prompt refactor, validators, cross-engine alignment) that were repeatedly deferred.  
**WHICH PROTOCOL SECTION:** §4.6 allows deferral; §8 self-improvement cadence (every 3 sessions)  
**WARNING SIGN:** Many “deferred to future capability/cross-engine design” notes accumulate; owner reports continued “wrong excerpt” pain on the same failure classes.  
**WHY THE PROTOCOL DIDN’T PREVENT IT:** There is no “stop and refactor” trigger that forces the team to pay down architectural debt once it is the bottleneck (e.g., prompt cap, cross-engine dependencies). fileciteturn2file0L1-L1 fileciteturn4file0L1-L1

### Most likely failure causes in this project’s specific context

**Most likely cause:** **Prompt capacity collapse + misallocation**. The ledger already records the Phase 2 grouping prompt at ~1474/1500 words—this is a near-term hard ceiling, not a long-term risk. When the remaining atoms still demand prompt-level enforcement, you will be forced into silent tradeoffs unless you introduce a refactor mechanism. fileciteturn5file0L1-L1

**Second most likely cause:** **Summarization loss in Arabic scholarly edge cases**, especially where a single missing qualifier changes the integrity of isnād/matn chains, attribution boundaries, or “deceptive cleanliness” outcomes. The protocol’s dispatch-first strategy is structurally misaligned with “nuance is everything.” fileciteturn2file0L1-L1

**Third most likely cause:** **Unaudited orchestrator capture** (CC controls coworker prompts + acceptance + ledger truth). At 600 atoms, even a small systematic bias (or just fatigue-driven shortcuts) compounds into large doctrinal drift. fileciteturn2file0L1-L1

## Single Points of Failure

**Highest severity:** **No independent evidence/audit layer for Q-CLOSED.** If closure can be satisfied by narration, the entire operation can “succeed on paper” while failing in reality (and this failure is hard to detect until the owner’s trust collapses). fileciteturn2file0L1-L1

**Second highest severity:** **Prompt word-budget exhaustion without a refactor doctrine.** Once the prompt cap is hit, you cannot encode additional behavior deterministically through the LLM instruction layer; everything downstream becomes compromise or deferral. The ledger suggests this is already near-critical. fileciteturn5file0L1-L1

**Third highest severity:** **Dependence on owner-mediated DR relay as a core safety mechanism.** If DR is operationally fragile (delayed, partial, absent), the protocol’s intended adversarial layer becomes optional in practice, especially under schedule pressure. fileciteturn2file0L1-L1

**Fourth highest severity:** **Preliminary debt can silently become permanent doctrine.** Allowing closure with missing coverage without strict revisit enforcement creates a latent corruption channel (“temporary” decisions that never get audited). fileciteturn2file0L1-L1

## Verdict

**Robustness score (1–10): 4/10** for governing ~600 atoms over ~40 sessions *without* accumulating silent doctrinal corruption or owner trust collapse. The protocol is comprehensive, but its core controls are predominantly **social/ceremonial** rather than **evidence-backed and enforceable**, and the scaling bottleneck (prompt capacity) is already pressing in practice. fileciteturn2file0L1-L1 fileciteturn5file0L1-L1

**Single most important change to increase the score the most:** Implement a **machine-verifiable Atom Closure Packet + automated Q-CLOSED verification** (a real “closure compiler” that fails the session if required evidence isn’t present). This directly attacks the highest-leverage failure mode: the ability to pass gates without doing the work. fileciteturn2file0L1-L1