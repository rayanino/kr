# Source Spec Atoms by Topic: trust

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0004 | decision | Replace trust algorithm with agent teams | proposed | critical |
| DEC-SRC-0005 | decision | Muhaqiq standing is metadata only | proposed | high |
| INV-SRC-0005 | invariant | Muhaqiq never gates trust decisions | proposed | high |
| OF-SRC-0003 | feedback | Minimize owner review load | confirmed | critical |
| OF-SRC-0009 | feedback | Replace numeric trust scoring with agent teams | confirmed | critical |
| OF-SRC-0010 | feedback | Muhaqiq standing is informational only | confirmed | high |
| REQ-SRC-0003 | requirement | Minimal owner review load | proposed | critical |
| REQ-SRC-0008 | requirement | Agent-team trust evaluation | proposed | critical |

### DEC-SRC-0004 — Replace trust algorithm with agent teams
- Type: decision
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0009; amended per both coworker reviews
- Chosen option: OPT-B — Minimum two-verifier trust workflow
- Decision rationale: This matches the owner's trust direction while keeping unresolved team architecture out of the runtime contract.

### DEC-SRC-0005 — Muhaqiq standing is metadata only
- Type: decision
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010; amended per domain-validator-review.yaml
- Chosen option: OPT-B — Metadata plus parsing-confidence signal
- Decision rationale: This keeps the owner's non-rejection rule intact while preserving the structural risk signal Gemini flagged for normalization.

### INV-SRC-0005 — Muhaqiq never gates trust decisions
- Type: invariant
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010
- Rule: Muhaqiq standing may annotate parsing confidence, but it may never reject a source or block trust_decision finalization.

### OF-SRC-0003 — Minimize owner review load
- Type: feedback
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 1 question 3
- Interview question: How often should the owner review metadata decisions?
- Owner answer: The owner wants as few reviews as possible. The system should auto-decide aggressively and only send genuinely unresolvable cases to the owner.

### OF-SRC-0009 — Replace numeric trust scoring with agent teams
- Type: feedback
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 3 question 1
- Interview question: How should trust evaluation work?
- Owner answer: Trust evaluation should be rebuilt around agent teams rather than numeric factors. Two web researchers and two reasoners work under supervisors, supervisors deliberate, and monitor agents provide process-improvement feedback.

### OF-SRC-0010 — Muhaqiq standing is informational only
- Type: feedback
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 3 question 2
- Interview question: How should muhaqiq reputation affect source evaluation?
- Owner answer: Muhaqiq standing is metadata only. Unknown muhaqiqs should be flagged, and standing can be graduated from unknown to elite, but it must never cause the text to be discarded.

### REQ-SRC-0003 — Minimal owner review load
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0003; amended per contract-architect-review.yaml
- Trigger: Metadata inference reaches a case that cannot be finalized automatically.
- Postconditions:
  - Cases with evidence-backed automatic resolution do not create owner_review_case records.
  - Routed cases write owner_review_case with fields route_reason, target_field, evidence_summary, and candidate_positions.
  - Owner review is never requested for reasons outside the approved route_reason taxonomy.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/06_usul/book.htm; When source metadata resolution completes; Then No owner_review_case is written..
  - AC-2 [deterministic] Given A Shamela HTML source whose metadata card, title, and colophon contain no author signal; When source metadata resolution completes; Then owner_review_case.route_reason="zero_author_evidence" and owner_review_case.target_field="author_name"..
  - AC-3 [integration] Given A source classified as mustalah_al_hadith while science_registry lacks that entry; When science classification completes; Then owner_review_case.route_reason="new_science_not_in_registry" and owner_review_case.target_field="science_scope"..

### REQ-SRC-0008 — Agent-team trust evaluation
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0009; amended per both coworker reviews and adversary-review.yaml ADV-003
- Trigger: The engine must emit a trust_decision for a source or metadata claim.
- Postconditions:
  - trust_decision contains decision, trust_path, supporting_agents, and evidence_summary fields.
  - Every run writes monitor_feedback records even when the case follows the fast_track path.
  - Books meeting all fast_track predicates may use trust_path=fast_track instead of full_deliberation.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/05_tafsir/book.htm with definitive author attribution, scholar_authority[author_canonical_id].authority_level="primary", and author_death_hijri=774; When trust evaluation executes; Then trust_decision.trust_path="fast_track" and trust_decision.decision="verified"..
  - AC-2 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When trust evaluation executes; Then trust_decision includes decision, trust_path, supporting_agents, and evidence_summary, and at least one monitor_feedback record is written..
  - AC-3 [deterministic] Given A trust evaluation run with only one verification agent available; When trust evaluation executes; Then Finalization aborts with error_code=SRC-E-TRUST-AGENT-COUNT..
  - AC-4 [deterministic] Given tests/fixtures/shamela_real/03_fiqh/book.htm with genre="risalah" or author_death_hijri=null; When trust evaluation executes; Then trust_decision.trust_path="full_deliberation"..
