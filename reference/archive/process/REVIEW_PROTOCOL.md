# KR Design Review Protocol

This document defines how Claude Chat sessions review, critique, and improve the KR design.
It provides structured frameworks for different types of reviews.

---

## When to Trigger a Design Review

A design review session is appropriate when:
- A milestone is completed (post-implementation review)
- The owner has feedback or concerns about a design decision
- Implementation revealed SPEC ambiguities or gaps (accumulated in NEXT.md)
- A new capability or technology becomes relevant
- Periodic review (every 3-5 implementation sessions, audit for drift)

## Review Types

### Type 1: SPEC Integrity Review

**Purpose:** Verify a SPEC is still accurate after implementation and identify improvements.

**Procedure:**
1. Read the engine's SPEC.md fully.
2. Read all source files in the engine's `src/` directory.
3. Read all test files in the engine's `tests/` directory.
4. For each SPEC §4 behavioral rule, verify:
   - Is this rule implemented? (Find the code that implements it.)
   - Is the implementation faithful? (Does it match the rule exactly, or deviate?)
   - Are there behaviors in code that have no corresponding SPEC rule?
5. Check §9 (Implementation State) — is it accurate?
6. Check §5 (Validation) — are the specified validations actually running?

**Output format:**
```
### SPEC Integrity Review: [Engine Name]

**Faithful implementations:** [count] / [total rules]
**Deviations found:** [count]
**Unspecified behaviors:** [count]
**Missing implementations:** [count]

#### Deviations
1. SPEC §4.A.N says: "[exact quote]"
   Code does: [what it actually does]
   Assessment: [acceptable deviation / needs SPEC update / needs code fix]
   Recommendation: [specific action]

#### Unspecified Behaviors
1. [file:line] — [what the code does that has no SPEC rule]
   Assessment: [should be added to SPEC / should be removed from code]

#### Missing Implementations
1. SPEC §4.A.N: "[rule]" — not yet implemented
   Impact: [what breaks without this]
```

---

### Type 2: Cross-Engine Boundary Review

**Purpose:** Verify that adjacent engines integrate correctly.

**Procedure:**
1. Read upstream engine's SPEC §3 (Output Contract).
2. Read downstream engine's SPEC §2 (Input Contract).
3. Read both engines' actual data model definitions in code.
4. Compare field-by-field:
   - Every field the downstream expects: is it in the upstream output?
   - Every field the upstream produces: is it consumed or passed through?
   - Metadata accumulation: does the downstream output contain all upstream metadata?
5. Run integration tests if they exist.
6. Check for type mismatches, naming inconsistencies, optional-vs-required conflicts.

**Output format:**
```
### Boundary Review: [Upstream] → [Downstream]

**Fields matched:** [count] / [total expected]
**Missing fields:** [list]
**Type mismatches:** [list]
**Metadata pass-through:** [complete / incomplete — list gaps]
**Integration tests:** [pass / fail / missing]
```

---

### Type 3: Transformative Capability Review

**Purpose:** Evaluate whether §4.B capabilities are ambitious enough, feasible, and well-specified.

**Procedure:**
1. Read the engine's SPEC §4.B.
2. For each capability, evaluate:
   - **Ambition:** Would a scholar say "I didn't know that was possible"?
   - **Specificity:** Could Claude Code implement this without clarifying questions?
   - **Feasibility:** Is the named technology/approach real and appropriate?
   - **Integration:** Does this capability use data that the pipeline actually produces?
   - **Novelty:** Does this exist in any Islamic studies tool? (Web search if needed.)
3. Propose improvements: more ambitious capabilities, better specifications, or removed hand-waving.

**Output format:**
```
### Transformative Capability Review: [Engine Name]

#### §4.B.N — [Capability Name]
- Ambition: [HIGH/MEDIUM/LOW] — [why]
- Specificity: [IMPLEMENTABLE/VAGUE/HAND-WAVING] — [what's missing]
- Feasibility: [VERIFIED/PLAUSIBLE/UNCERTAIN] — [technology named]
- Integration: [CONNECTED/DISCONNECTED] — [what data it needs and whether it exists]
- Novelty: [NOVEL/INCREMENTAL/EXISTS] — [what's out there]
- Recommendation: [keep/improve/replace]

#### Proposed New Capabilities
[If the review identifies opportunities the SPEC missed]
```

---

### Type 4: Scholarly Value Audit

**Purpose:** Evaluate whether the system as designed would actually make Rayane a better scholar.

**Procedure:**
1. Read `reference/USER_SCENARIOS.md`.
2. Read `reference/ENTRY_EXAMPLE.md`.
3. For each user scenario, trace the path through the system:
   - What engines are involved?
   - What data flows?
   - What is the user experience?
   - Where could the experience break down?
4. For the entry example, verify:
   - Can the current design produce entries at that quality level?
   - What metadata is needed that might not be captured?
   - What synthesis capabilities are needed that might not be specified?
5. Think beyond the scenarios:
   - What scholarly workflows are NOT covered?
   - What questions can't the system answer that a scholar would want answered?
   - What's the path from "library exists" to "Rayane is a better scholar"?

**Output format:**
```
### Scholarly Value Audit

#### Scenario Coverage
[For each scenario: FULLY SERVED / PARTIALLY SERVED / NOT SERVED + gaps]

#### Entry Quality Assessment
[Can the pipeline produce ENTRY_EXAMPLE quality? What's missing?]

#### Uncovered Scholarly Workflows
[Workflows a scholar needs that the system doesn't address]

#### Scholarly Value Gaps
[Biggest opportunities to increase scholarly value]
```

---

### Type 5: Architecture Health Check

**Purpose:** Evaluate the overall system architecture for weaknesses.

**Procedure:**
1. Review the pipeline topology: are 7 engines the right decomposition?
2. Review shared components: are 6 the right set? Missing any?
3. Review data flow: is the linear pipeline optimal, or would some engines benefit from feedback loops?
4. Review technology choices: are the chosen tools still the best options?
5. Review scalability: what happens at 100 sources? 1000? 10000?
6. Review failure modes: what's the worst thing that can go wrong?

**Output format:**
```
### Architecture Health Check

#### Pipeline Topology
[Assessment + recommendations]

#### Shared Components
[Assessment + missing components]

#### Data Flow
[Assessment + feedback loop opportunities]

#### Technology Stack
[Assessment + alternatives worth considering]

#### Scale Analysis
[Bottlenecks at 10x, 100x, 1000x sources]

#### Failure Mode Analysis
[Top 5 worst failure scenarios + mitigations]
```

---

## Design Evolution Tracking

When a review identifies an improvement opportunity:

1. If it's a SPEC change: make the change directly, commit with rationale.
2. If it's a new architectural decision: record in kr_decisions.md.
3. If it's a new capability idea: add to the relevant SPEC §4.B, mark [NOT YET IMPLEMENTED].
4. If it's a cross-cutting concern: add to VISION.md in the appropriate section.
5. If it requires owner input: add to NEXT.md under "Pending Owner Questions."

Every review session should produce at least ONE concrete improvement to the repo, not just analysis.

---

## Review Cadence

| Trigger | Review Type |
|---------|-------------|
| Milestone completed | Type 1 (all engines in milestone) + Type 2 (all boundaries) |
| Every 3-5 implementation sessions | Type 5 (architecture health) |
| Owner feedback received | Type 4 (scholarly value) |
| New technology discovered | Type 3 (transformative capabilities) |
| SPEC issues accumulated in NEXT.md | Type 1 (affected engine) |
| Before starting a new milestone | Type 2 (upcoming boundaries) + Type 4 |
