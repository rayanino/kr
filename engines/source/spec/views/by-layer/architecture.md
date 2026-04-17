# Source Spec Atoms by Layer: architecture

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0001 | decision | Owner hints are cross-validation, not primary data | confirmed | critical |
| DEC-SRC-0002 | decision | Science scope uses dynamic registry | confirmed | high |
| DEC-SRC-0003 | decision | Level detection strategy | confirmed | medium |
| DEC-SRC-0004 | decision | Replace trust algorithm with agent teams | confirmed | critical |
| DEC-SRC-0005 | decision | Muhaqiq standing is metadata only | confirmed | high |
| DEC-SRC-0006 | decision | Agents resolve disagreements autonomously | confirmed | critical |
| DEC-SRC-0007 | decision | Disputed metadata as multi-position evidence | confirmed | high |
| DEC-SRC-0008 | decision | Agent infrastructure is built within source-engine scope first | confirmed | medium |
| DEC-SRC-0009 | decision | Research strategy uses specialized sources | confirmed | high |
| DEC-SRC-0010 | decision | Source hints multi-layer routing and normalization confirms it | confirmed | medium |
| DEC-SRC-0011 | decision | Agent self-resolution replaces human_gate | confirmed | high |
| DEC-SRC-0012 | decision | Multi-position metadata ordered by confidence | confirmed | high |
| DEC-SRC-0013 | decision | Deliberation cell architecture with deterministic orchestrator | confirmed | critical |
| DEC-SRC-0014 | decision | Separate raw-upload tracking from official source admission | confirmed | critical |
| DEC-SRC-0015 | decision | Normalization consumes a bridge input model, not raw SourceMetadata | confirmed | high |
| DEC-SRC-0016 | decision | Owner-submission risk gate blocks admission and downstream progression | confirmed | critical |
| DEC-SRC-0017 | decision | NFKC normalization allowed at PDF extraction boundary | confirmed | critical |
| DEC-SRC-0018 | decision | Sources are immutable; collection entries evolve | confirmed | critical |
| DEC-SRC-0019 | decision | Mixed-edition volumes never silently produce a coherent edition holding | confirmed | critical |
| DEC-SRC-0020 | decision | Supersession is pointer-based, not deletion-based | confirmed | critical |

### DEC-SRC-0001 — Owner hints are cross-validation, not primary data
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002
- Chosen option: OPT-B — Hints as cross-validation signals
- Decision rationale: This matches the owner's drop-and-go workflow and preserves inference independence.

### DEC-SRC-0002 — Science scope uses dynamic registry
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0006; amended per domain-validator-review.yaml
- Chosen option: OPT-B — Growable ordered science list
- Decision rationale: This preserves intake breadth, supports cross-science books such as ahadith al-ahkam, and keeps expansion approval at the registry layer.

### DEC-SRC-0003 — Level detection strategy
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Initial closure on 2026-04-16 by ChatGPT Deep Research (dr-chatgpt-level-detection-20260416.yaml SEC-6). Hardened on 2026-04-17 by a 3-of-3 unanimous adjudication after Claude DR (dr-claude-level-detection-20260416.yaml) recommended OPT-C-asymmetric: Codex CLI (architectural fit, .kr/runtime/adjudication_codex_20260417.md), Gemini CLI runs 1 and 2 (classical scholarly defensibility, 6-0 branch win counts, .kr/runtime/adjudication_gemini_cli_run1_20260417.md and run2_20260417.md), and Gemini DR (T-2 threat model tie-breaker, .kr/runtime/adjudication_gemini_dr_20260417.md) all voted OPT-B with high confidence. Gemini DR additionally proposed a middle-path `level_status` enumerator amendment to CON-SRC-0004 to close the null-conflation gap Claude DR correctly identified — that amendment is adopted on 2026-04-17 and is orthogonal to this decision.
- Chosen option: OPT-B — Downstream content analysis
- Decision rationale: OPT-B is the only architecture that structurally aligns with the rigor of the turāth. ChatGPT DR p16 headline: level inference is downstream and content-based, authoritative ownership sits in the synthesis engine, source engine preserves evidence but does NOT populate level except via rare owner override. ChatGPT DR p17: the book's own discourse — definitions, audience markers, gloss rate, commentary layer — is the most authoritative signal. ChatGPT DR p18: the nullable SourceMetadata.level already models "unknown" cleanly, so OPT-B creates no schema mismatch. ChatGPT DR p19: synthesis is the first place a book can be seen as distributed pedagogical units — the least distortive place to attach a late-bound owner-facing judgment. ChatGPT DR p20: in a personal scholarly library, wrong visible level is more harmful than a temporarily unknown level. ChatGPT DR p21: the three-stage cascade fann → nawʿ/layer → martaba (science → genre/layer → level) is mandatory. Gemini CLI classical analyses (runs 1 and 2) reinforce: Ibn Khaldūn's tadarruj requires level to emerge from internal structural density, al-Zarnūjī's tawaqquf forbids premature commitment, al-Fihrist and Kashf al-Ẓunūn systematically refuse provisional pedagogical tags. Gemini DR T-2 threat model verdict: OPT-B residual T-2 risk (3/10) stems only from the null-conflation ambiguity, which the middle-path `level_status` enum on CON-SRC-0004 entirely mitigates. The source engine remains a pure preserver of raw structural and bibliographic evidence, leaving the authoritative pedagogical ḥukm to the downstream engines capable of examining the matn itself.

### DEC-SRC-0004 — Replace trust algorithm with agent teams
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0009; amended per both coworker reviews
- Chosen option: OPT-B — Minimum two-verifier trust workflow
- Decision rationale: This matches the owner's trust direction while keeping unresolved team architecture out of the runtime contract.

### DEC-SRC-0005 — Muhaqiq standing is metadata only
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010; amended per domain-validator-review.yaml
- Chosen option: OPT-B — Metadata plus parsing-confidence signal
- Decision rationale: This keeps the owner's non-rejection rule intact while preserving the structural risk signal Gemini flagged for normalization.

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

### DEC-SRC-0007 — Disputed metadata as multi-position evidence
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013; amended per contract-architect-review.yaml
- Chosen option: OPT-B — Record all positions in a positions array
- Decision rationale: This keeps disputed metadata truthful and gives REQ-SRC-0012 a stable contract to implement.

### DEC-SRC-0008 — Agent infrastructure is built within source-engine scope first
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0015
- Chosen option: OPT-A — Build within source engine scope first
- Decision rationale: The owner explicitly prioritized building the best possible source-engine scope first.

### DEC-SRC-0009 — Research strategy uses specialized sources
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0016; amended per both coworker reviews and Gemini DR on Islamic scholarly metadata verification sources (2026-04-14) which resolved OQ-SRC-0007 with a concrete curated inventory.
- Chosen option: OPT-B — Canonical specialized source categories
- Decision rationale: This gives REQ-SRC-0013 a stable source-type taxonomy. The concrete inventory was resolved by Gemini DR (OQ-SRC-0007 superseded). Key sources per category are now curated in REQ-SRC-0013 preconditions with access modalities documented.

### DEC-SRC-0010 — Source hints multi-layer routing and normalization confirms it
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Resolved from OQ-SRC-0002 per domain-validator-review.yaml; amended per 2026-04-14 PDF format directive
- Chosen option: OPT-C — Source hints, normalization confirms
- Decision rationale: This gives source enough responsibility to route early across both Shamela and PDF without pretending format-specific hint evidence is authoritative on its own.

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

### DEC-SRC-0012 — Multi-position metadata ordered by confidence
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Resolves OQ-SRC-0006; builds on DEC-SRC-0007 and REQ-SRC-0012
- Chosen option: OPT-B — Sort by confidence descending with primary marker
- Decision rationale: Confidence ordering gives downstream engines a natural default (positions[0]) while preserving all scholarly positions. The owner's principle is truth-seeking — all positions stay, but the most-evidenced one is first.

### DEC-SRC-0013 — Deliberation cell architecture with deterministic orchestrator
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR report on agent-team architecture (2026-04-14). Resolves OQ-SRC-0003. The DR evaluated fixed roles, dynamic composition, and hierarchical escalation, recommending dynamic composition with fixed minimums under a deterministic orchestrator.
- Chosen option: OPT-B — Deterministic orchestrator with deliberation cells
- Decision rationale: Smallest system that enforces independence, produces evidence-traceable outputs, guarantees bounded disagreement loops, supports fast-track without bypassing logging, and produces always-valid output shapes. Deterministic orchestration avoids the LLM supervisor single-point-of-failure problem while maintaining the agent team's deliberative power.

### DEC-SRC-0014 — Separate raw-upload tracking from official source admission
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that uploaded artifacts must not pollute the official source collection before source-engine acceptance.
- Chosen option: OPT-B — Two registries with staged admission
- Decision rationale: This preserves full upload traceability without polluting the official source collection before the source engine genuinely accepts the source.

### DEC-SRC-0015 — Normalization consumes a bridge input model, not raw SourceMetadata
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Added on 2026-04-14 after contract-auditor review found that the redesigned SourceMetadata surface no longer matches the live normalization boundary.
- Chosen option: OPT-B — Emit a NormalizationInput bridge inside the handoff bundle
- Decision rationale: This preserves source-engine clarity while giving normalization a concrete boundary contract that can evolve independently later.

### DEC-SRC-0016 — Owner-submission risk gate blocks admission and downstream progression
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that any uncertainty materially affecting study quality should trigger a human gate before valuable downstream work proceeds.
- Chosen option: OPT-B — Emit provisional output and block progression
- Decision rationale: This preserves pipeline-quality analysis while protecting the collection and downstream work from materially risky owner submissions.

### DEC-SRC-0017 — NFKC normalization allowed at PDF extraction boundary
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Empirical finding from pdf_collection_characterization_2026-04-14.md. 10/10 sampled PDFs store Arabic text in Unicode Presentation Forms (U+FB50-FEFF), not standard Arabic (U+0600-06FF). NFKC normalization deterministically recovers standard Arabic from Presentation Forms without altering scholarly content.
- Chosen option: OPT-B — Allow NFKC at PDF extraction boundary only
- Decision rationale: Grounded in empirical evidence from 10 real PDFs. NFKC is not altering scholarly content — it is recovering actual characters from rendering-layer artifacts. The distinction between rendering normalization and content normalization is clear and documentable.

### DEC-SRC-0018 — Sources are immutable; collection entries evolve
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15). FRBR/IFLA LRM separates abstract content from concrete carriers. Fedora/DSpace repositories keep immutable versions and expose 'latest' pointers without deleting history. KR's existing invariant (frozen sources are immutable) and INV-SRC-0003 (library never refuses knowledge) together require that collection membership evolves without mutating the carrier layer. The DR identifies this as the structural resolution to incremental volumes, supersession, and mixed-edition handling.
- Chosen option: OPT-B — Attach immutable sources to evolving collection entries (holdings)
- Decision rationale: Satisfies immutability (sources untouched), INV-SRC-0003 (nothing refused), INV-SRC-0009 (all evidence preserved), and enables progressive completeness tracking. The 'attach not merge' principle is the minimum mechanism that handles all six DR edge cases (incremental volumes, duplicate editions, mixed editions, supersession, partial-of-complete, composite evolution).

### DEC-SRC-0019 — Mixed-edition volumes never silently produce a coherent edition holding
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15), Edge Case 3. Silent mixing of editions is dangerous in Islamic scholarly study because citations, page numbers, and tahqiq notes differ by edition. Mixing breaks scholarly reliability. The DR recommends either two separate holdings or one holding explicitly marked as ActiveMixed with a study-quality warning.
- Chosen option: OPT-B — Separate mixed editions into distinct holdings with explicit warning
- Decision rationale: Preserves scholarly reliability by keeping edition-coherent holdings separate. INV-SRC-0003 (never refuse knowledge) is respected because both editions are admitted. INV-SRC-0009 (zero knowledge loss) is respected because the mixing evidence is preserved, not hidden. The ActiveMixed state provides usability without false coherence claims.

### DEC-SRC-0020 — Supersession is pointer-based, not deletion-based
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15), Edge Case 4. Fedora API specification requires resource versioning via the Memento protocol where an Original Resource can have multiple immutable Mementos listed in a TimeMap. DSpace's item-level versioning treats each version as a separate item with a base identifier pointing to the most recent version while older versions remain accessible and citable. Both models align with KR's immutability and zero-knowledge-loss invariants.
- Chosen option: OPT-B — Pointer-based supersession with configurable regeneration policy
- Decision rationale: Preserves full history (Fedora/Memento model), enables DSpace-style 'only most recent in search, older still accessible', and avoids compute explosion by making regeneration conditional on actual text-quality impact. Satisfies all three governing invariants (immutability, never-refuse, zero-loss) simultaneously.
