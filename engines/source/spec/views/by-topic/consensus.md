# Source Spec Atoms by Topic: consensus

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0006 | decision | Agents resolve disagreements autonomously | confirmed | critical |
| DEC-SRC-0011 | decision | Agent self-resolution replaces human_gate | confirmed | high |
| INV-SRC-0004 | invariant | Truth-seeking over consensus-forcing | confirmed | high |
| OF-SRC-0011 | feedback | Agents resolve disagreements without human gate | confirmed | critical |
| OF-SRC-0013 | feedback | Disagreement may itself be the true answer | confirmed | high |
| OQ-SRC-0004 | question | Formal replacement for human_gate | superseded | high |
| REQ-SRC-0009 | requirement | Agent self-resolution of disagreements | confirmed | critical |
| REQ-SRC-0052 | requirement | Scholar match verification cell with hybrid round-0 / round-1 protocol | confirmed | critical |
| REQ-SRC-0053 | requirement | Scholar disagreement routing with compound 4-condition threshold | confirmed | critical |

### DEC-SRC-0006 — Agents resolve disagreements autonomously
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011
- Chosen option: OPT-B — Agent self-resolution with failure analysis
- Decision rationale: This matches the owner's desire for autonomous resolution plus system learning.

### DEC-SRC-0011 — Agent self-resolution replaces human_gate
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Resolves OQ-SRC-0004; derived from OF-SRC-0011 and REQ-SRC-0009
- Chosen option: OPT-B — REQ-SRC-0009 pipeline with multi-position fallback
- Decision rationale: Owner said agents resolve everything. REQ-SRC-0009 already specifies the resolution flow, terminal states, failure analysis, and fallback. Adding a separate module creates unnecessary indirection.

### INV-SRC-0004 — Truth-seeking over consensus-forcing
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013; amended per contract-architect-review.yaml
- Rule: A metadata field qualifies as genuine scholarly dispute only when at least two independent agents provide evidence-backed positions for that field.

### OF-SRC-0011 — Agents resolve disagreements without human gate
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 3 question 3
- Interview question: What should happen when agents disagree on metadata?
- Owner answer: Human gate checkpoints for metadata disagreements should be removed. Agents resolve disagreements autonomously, and the agent that erred should analyze its own failure so the system improves.

### OF-SRC-0013 — Disagreement may itself be the true answer
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 4 question 1
- Interview question: What counts as successful resolution when scholars disagree?
- Owner answer: Resolution does not mean forcing one entity. If scholars genuinely disagree, the engine should record every supported position with evidence because the goal is truth-seeking, not consensus-forcing.

### OQ-SRC-0004 — Formal replacement for human_gate
- Type: question
- Layer: questions
- Step: n/a
- Status: superseded
- Priority: high
- Confidence: medium
- Source: Derived from OF-SRC-0011
- Candidates:
  - OPT-A: Agent-gate module (likely)
  - OPT-B: Confidence threshold resolver (possible)
  - OPT-C: Supervisor veto (possible)

### REQ-SRC-0009 — Agent self-resolution of disagreements
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011; amended per contract-architect-review.yaml, adversary-review.yaml ADV-005/ADV-012, and ChatGPT DR on agent-team architecture (2026-04-14) which specifies the structured round protocol.
- Trigger: Independent agents disagree about a metadata field.
- Postconditions:
  - disagreement_case.resolution_state is set to resolved_error or genuine_scholarly_dispute.
  - resolved_error writes one corrected value and structured failure_analysis for the losing agent.
  - genuine_scholarly_dispute delegates the field to the REQ-SRC-0012 multi-position schema.
  - When disagreement_case.round_count reaches 3 without convergence on resolved_error, disagreement_case.resolution_state defaults to genuine_scholarly_dispute and emits REQ-SRC-0012 output.
  - Each round follows a structured protocol where each verification agent receives the other agent's position and evidence traces, then emits a steelman of the other position, a list of attack points with evidence, at most 2 targeted research requests, and a revised position.
  - Convergence is detected mechanically by the orchestrator when both agents emit the same canonicalized output and the winning position's evidence list is non-empty.
  - When one agent's evidence becomes empty while the other remains evidence-backed, the case resolves as resolved_error rather than genuine_scholarly_dispute.
  - failure_analysis for resolved_error must include error_type, what_missed, corrective_evidence, and guardrail_suggestion fields.
- Acceptance criteria:
  - AC-1 [integration] Given A disagreement where one agent treats "إعداد" as author evidence and another agent corrects it to compiler evidence; When disagreement resolution executes; Then disagreement_case.resolution_state="resolved_error" and the corrected metadata field is stored as a single resolved value..
  - AC-2 [integration] Given A disputed authorship case with two evidence-backed positions from independent agents; When disagreement resolution executes; Then disagreement_case.resolution_state="genuine_scholarly_dispute" and the output field uses the REQ-SRC-0012 positions array..
  - AC-3 [deterministic] Given A resolved_error case with one losing agent; When disagreement resolution finalizes; Then failure_analysis.agent_id is recorded and linked to disagreement_case.case_id..
  - AC-4 [deterministic] Given A disagreement that remains unresolved after disagreement_case.round_count=3; When disagreement resolution executes; Then disagreement_case.resolution_state="genuine_scholarly_dispute" and the output field uses the REQ-SRC-0012 positions array..

### REQ-SRC-0052 — Scholar match verification cell with hybrid round-0 / round-1 protocol
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §2.3 (Pivot (c) verifier-independence mechanism HYBRID adjudication) + §5.2 (renumbered from ChatGPT DR's stale REQ-SRC-0047 to REQ-SRC-0052 per repo verification — slot 0047 already taken by "Owner override pathway for level at intake"). Cross-provider 2-of-2 contributing pivots: Claude DR §6 (adversarial scaffold) + ChatGPT DR §6 (functional independence with no-peeking + different prompts). Synthesis adopts HYBRID — ChatGPT DR's no-peeking as round-0 baseline; Claude DR's adversarial scaffold ONLY in round-1 disagreement-resolution. 4-evaluator wave: 4-of-4 UNANIMOUS HIGH on Pivot (c). Round cap = 2; both DRs converge. NO new candidates introduced in round-1 (Claude DR § + ChatGPT DR §5 Stage 10 both, ChatGPT DR's more conservative framing adopted: "no new candidate may be introduced unless it already existed in the frozen packet"). This atom specializes DEC-SRC-0013's deliberation-cell pattern as scholar_match_cell.
- Trigger: A locked CON-SRC-0009 evidence packet has been emitted by Stage-1 (REQ-SRC-0051 deterministic candidate generation); the orchestrator initiates Stage-2 verifier consensus.
- Postconditions:
  - Round-0 — Two verifiers receive the SAME CON-SRC-0009 packet (byte-identical input). Each verifier executes its own round-0 prompt template (different reasoning instructions but identical evidence). NO-PEEKING: neither verifier sees the other's output before forming its own round-0 verdict. Each verifier returns a ranked positions list with chosen_id, confidence, score_breakdown (9 sub-scores per ChatGPT DR §3b), and cited_evidence per position.
  - INV-SRC-0016 chosen_id-closure check runs on EVERY round-0 verifier output BEFORE any routing or convergence check reads the output. F-4 hallucinations are rejected up-front per the closure invariant.
  - Convergence check at round-0 (deterministic, no LLM involvement) — convergence requires: (a) both verifiers' top-ranked chosen_id is the same, (b) mean confidence ≥ 0.92, (c) each verifier's confidence ≥ 0.90, (d) no rival candidate within 0.07 of leader confidence (per REQ-SRC-0053 compound threshold), and (e) ≥2 non-name attributes intersect per INV-SRC-0013 floor. If ALL conditions met → DEFINITIVE terminal (REQ-SRC-0053 routing reads this as definitive). If any condition fails AND verifiers' top chosen_id is the same → fall through to round-1 (treated as disagreement on confidence shape rather than identity); if verifiers' top chosen_id differs → round-1 triggered.
  - Round-1 (only on round-0 non-convergence; otherwise skipped) — adversarial scaffold: verifier A receives a prompt template where it DEFENDS its round-0 leader against the round-0 alternative; verifier B receives a prompt template where it ATTACKS A's round-0 leader AND DEFENDS B's round-0 leader. The CON-SRC-0009 evidence packet is UNCHANGED (immutable per the contract). NO new candidates may be introduced — chosen_id MUST remain in candidate_set per INV-SRC-0016. Each verifier returns updated ranked positions.
  - INV-SRC-0016 chosen_id-closure check runs on EVERY round-1 verifier output (same closure as round-0).
  - Final convergence check at round-1 (deterministic, same compound threshold as round-0). If converged → DEFINITIVE per REQ-SRC-0053; if competing within 0.07 of leader → DISPUTED per REQ-SRC-0053; if neither candidate clears 0.70 → INSUFFICIENT_EVIDENCE per REQ-SRC-0053.
  - Round cap = 2 (no rounds beyond round-1; case finalizes with whatever terminal applies after round-1).
  - The provenance trail per CON-SRC-0008 records: verifier_a_id, verifier_b_id, round_count (1 if round-0 converged; 2 if round-1 ran), prompt template hashes for each round each verifier, all score_breakdowns, all cited_evidence references.
- Acceptance criteria:
  - AC-1 [integration] Given A locked CON-SRC-0009 packet for fragment "البخاري" with K=4 candidates. Both verifiers run round-0 and independently return chosen_id=sch_00042 with confidence 0.96 (verifier A) and 0.94 (verifier B); no rival within 0.07 of leader; ≥2-non-name floor satisfied (primary_science=hadith + attributed_works intersect).; When round-0 convergence check runs; Then All 5 conditions met (same chosen_id, mean 0.95 ≥ 0.92, each ≥ 0.90, no rival within 0.07, ≥2 non-name). Round-0 converges to DEFINITIVE. Round-1 is NOT triggered. provenance.round_count=1. CON-SRC-0008 emits with disambiguation_state=definitive..
  - AC-2 [integration] Given A locked CON-SRC-0009 packet where round-0 verifiers return DIFFERENT chosen_ids (verifier A: sch_00042 with 0.88; verifier B: sch_00115 with 0.85).; When round-0 convergence check runs; Then Conditions fail (different chosen_id). Round-1 is triggered. Verifier A receives "defend sch_00042" prompt; verifier B receives "attack sch_00042 + defend sch_00115" prompt. Both reason on the UNCHANGED CON-SRC-0009 packet. INV-SRC-0016 closure runs on both round-1 outputs..
  - AC-3 [integration] Given Round-1 verifiers return: verifier A reaffirms sch_00042 at 0.93 (defended successfully); verifier B revises to sch_00042 at 0.91 (attacker conceded). Mean = 0.92 ≥ 0.92, each ≥ 0.90, no rival within 0.07, ≥2-non-name satisfied.; When final convergence check at round-1 runs; Then All compound-threshold conditions met. Definitive terminal at REQ-SRC-0053. provenance.round_count=2. The audit trail shows the round-1 adversarial resolution with full prompt template hashes for both rounds, both verifiers..
  - AC-4 [integration] Given Round-1 verifiers continue to disagree: verifier A defends sch_00042 at 0.85; verifier B defends sch_00115 at 0.83. Competing within 0.07 (gap = 0.02).; When final convergence check at round-1 runs; Then Disputed routing per REQ-SRC-0053 (competing within 0.07). CON-SRC-0008 emits with disambiguation_state= disputed; positions[] populated with both candidates' score_breakdowns and cited_evidence; canonical_scholar_id is the leading id (top of positions). provenance .round_count=2. Round cap = 2 holds; no round-2..
  - AC-5 [integration] Given Verifier A returns chosen_id="sch_99999" (NOT in candidate_set — F-4 hallucination at round-0).; When orchestrator runs INV-SRC-0016 closure check; Then Verifier A output is REJECTED (per INV-SRC-0016). Logged as F-4. The case proceeds with verifier B's output only; if verifier B legitimately converged on an in-packet candidate, the case is treated as structural disagreement (one valid + one rejected) → disputed terminal with positions populated from legitimate candidates only..
  - AC-6 [deterministic] Given Only 1 verifier is available (the second model is rate-limited; both retries fail).; When REQ-SRC-0052 attempts to run; Then Match call aborts with SRC-E-TRUST-AGENT-COUNT (existing code, contracts.py:572). The case routes to disputed (with the single verifier's positions if any) or insufficient_evidence (if no verifier returned). Reuses the existing error code per ChatGPT DR existing-error-citation discipline..

### REQ-SRC-0053 — Scholar disagreement routing with compound 4-condition threshold
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §2.4 (Pivot (d) compound 4-condition threshold adjudication) + §5.2 (renumbered from ChatGPT DR's stale REQ-SRC-0048 to REQ-SRC-0053 per repo verification — slot 0048 already taken by "Deferred validation surface for owner_level_override"). Cross-provider DR sources: Claude DR §6 (single threshold 0.95) + ChatGPT DR §6 (compound 4-condition: mean ≥ 0.92 AND each ≥ 0.90 AND no rival within 0.07 AND ≥2 corroborating attributes beyond fragment). Synthesis adopts ChatGPT DR's compound rule per knowledge-integrity primacy: strictly more conservative in adversarial cases; rival-margin guard closes a class of false-definitive errors that the flat threshold would miss. 4-evaluator wave: 3-of-4 cross- provider HIGH on Pivot (d) + 1 AMEND with partition fix (Codex Stage-3 Defect 1 — threshold partition gap [0.05, 0.07)). Codex Defect 1 reconciliation applied: the disputed routing margin is widened to 0.07 so the definitive / disputed / insufficient_evidence predicates partition cleanly without the [0.05, 0.07) gap — Codex's recommended fix path (cleaner: extend disputed routing to "competing within 0.07 OR mean ∈ [0.75, 0.92)" per closure §3.1 Defect 1).
- Trigger: Stage-2 verifier consensus (REQ-SRC-0052) has emitted final round outputs (round-0 if converged at round-0; round-1 otherwise); the orchestrator runs terminal routing.
- Postconditions:
  - DEFINITIVE predicate (compound 4-condition AND) — all 4 conditions MUST be true: (a) both verifiers' final-round chosen_id is the same (convergent identity); (b) mean confidence ≥ 0.92; (c) each verifier's confidence ≥ 0.90; (d) no rival candidate within 0.07 of leader confidence; AND (e) the ≥2-non-name floor from INV-SRC-0013 is satisfied (corroboration_count ≥ 2 on eligible attributes). If ALL 5 conditions met → terminal = DEFINITIVE, canonical_scholar_id = chosen_id, confidence = mean, positions = empty.
  - DISPUTED predicate — ANY ONE of the following: (a) convergent identity but mean ∈ [0.75, 0.92); OR (b) verifiers diverge after round-1 (different chosen_ids at round-1 final); OR (c) competing candidates within 0.07 of leader (per Codex Defect 1 reconciliation: widened from 0.05 to 0.07 so the [0.05, 0.07) partition gap closes; this matches definitive's no-rival guard at exactly the same threshold for clean partitioning); OR (d) ≥2-non- name floor not met for any candidate even if confidence numbers would otherwise pass; OR (e) convergent identity at round-1 (same chosen_id) but at least one verifier's confidence < 0.90 (both_pass=false) — even when mean ≥ 0.92, no rival within 0.07, and ≥2-non-name floor met (Stage-4 Codex re-review closure: previously the partition left this case in a routing gap because (a) excludes mean ≥ 0.92, (b) excludes convergence, (c) requires close rival, and (d) requires floor unmet — none covered the convergent-but-both_pass=false case that AC-2 below exercises). If any condition true → terminal = DISPUTED, positions[] populated with all candidates that cleared the disputed floor (ranked by mean confidence descending).
  - INSUFFICIENT_EVIDENCE predicate — ANY ONE of the following: (a) no candidate scores ≥ 0.70 across both verifiers; OR (b) ambiguity remains after round cap (round-1 finalized as disputed but no candidate cleared the disputed-floor of mean 0.75). If any condition true → terminal = INSUFFICIENT_EVIDENCE, canonical_scholar_id = null, positions = empty.
  - The 3 predicates are MUTUALLY EXCLUSIVE and JOINTLY EXHAUSTIVE — every match-cell run terminates in exactly one of the 3 states (per Codex Defect 1 reconciliation: the partition is exhaustive after widening disputed to 0.07 AND adding the convergent-identity-but-both_pass=false branch (e) to disputed at Stage-4 closure).
  - provenance.threshold_audit records all 4 compound- threshold predicates' results (mean_passes, both_pass, no_rival_close, corroboration_count_ge_2) plus the numeric backing values (mean_confidence, leader_confidence, rival_confidence, corroboration_count) per INV-SRC-0015.
- Acceptance criteria:
  - AC-1 [deterministic] Given Round-1 final: both verifiers converge on chosen_id=sch_00042, confidences (0.95, 0.93). Mean = 0.94 ≥ 0.92, both ≥ 0.90, no rival within 0.07, ≥2 non-name attributes intersect.; When REQ-SRC-0053 routing runs; Then Terminal = DEFINITIVE. canonical_scholar_id=sch_00042. confidence=0.94. positions=empty. threshold_audit records all 4 predicates true with backing values..
  - AC-2 [deterministic] Given Round-1 final: both verifiers converge on chosen_id=sch_00042, confidences (0.99, 0.89). Mean = 0.94 ≥ 0.92, but each ≥ 0.90 FAILS (0.89 < 0.90).; When REQ-SRC-0053 routing runs; Then Terminal = DISPUTED. The "each ≥ 0.90" guard prevents one strong verifier from carrying a weak one. positions[] populated. threshold_audit records both_pass=false (the binding failure) along with the other 3 predicate values..
  - AC-3 [deterministic] Given Round-1 final: both verifiers converge on sch_00042 with confidences (0.95, 0.95) but a rival candidate sch_00115 has aggregated confidence 0.91. Rival gap = 0.04 < 0.07.; When REQ-SRC-0053 routing runs; Then Terminal = DISPUTED. The "no rival within 0.07" guard fires (gap 0.04 < 0.07). positions[] populated with both sch_00042 (leader) and sch_00115 (rival). threshold_audit records no_rival_close=false with rival gap 0.04 numeric backing. This AC documents the textbook ambiguous case classical methodology flags as disputed..
  - AC-4 [deterministic] Given Round-1 final: confidences satisfy all numeric predicates (mean 0.95, each ≥ 0.94, no rival within 0.07) but only 1 non-name attribute intersects between dossier and registry (INV-SRC-0013 floor unmet).; When REQ-SRC-0053 routing runs; Then Terminal = DISPUTED. INV-SRC-0013 ≥2-non-name floor is the binding constraint regardless of confidence values. positions[] populated. threshold_audit records corroboration_count_ge_2= false with corroboration_count=1 numeric backing..
  - AC-5 [deterministic] Given Round-1 final with rival gap exactly = 0.06 (in the previously-under-specified [0.05, 0.07) range identified by Codex Stage-3 Defect 1).; When REQ-SRC-0053 routing runs; Then Terminal = DISPUTED. The widened disputed-routing margin (0.07 per Codex Defect 1 reconciliation) captures this case cleanly. The previously under-specified gap [0.05, 0.07) is now closed: rival gaps in this range route to disputed (as the synthesis intended). threshold_audit records no_rival_close=false with rival gap 0.06 backing..
  - AC-6 [deterministic] Given Round-1 final: no candidate has confidence ≥ 0.70 across both verifiers (max individual confidence is 0.65).; When REQ-SRC-0053 routing runs; Then Terminal = INSUFFICIENT_EVIDENCE. canonical_scholar_id= null. positions=empty. threshold_audit records which predicate failed (no candidate ≥ 0.70 floor) with full backing values. The case is preserved for future re-attribution against a richer registry release..
  - AC-7 [deterministic] Given Round-1 final: verifiers diverge — verifier A chose sch_00042 at 0.88; verifier B chose sch_00115 at 0.86. Adversarial round-1 did not collapse the disagreement.; When REQ-SRC-0053 routing runs; Then Terminal = DISPUTED. The "verifiers diverge after round-1" condition fires. positions[] populated with both candidates. canonical_scholar_id is the leading id (sch_00042 by 0.88 vs 0.86 + aggregated rival score). threshold_audit records the specific failure (verifier_disagreement=true)..
