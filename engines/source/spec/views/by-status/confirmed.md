# Source Spec Atoms by Status: confirmed

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0001 | constraint | Shamela HTML and PDF are production formats | confirmed | high |
| CON-SRC-0002 | constraint | Hadith literature dominates source-engine benchmark quality | confirmed | high |
| CON-SRC-0003 | constraint | No existing pipeline contract is binding on the rebuild | confirmed | critical |
| OF-SRC-0001 | feedback | Collection unchanged for source intake | confirmed | high |
| OF-SRC-0002 | feedback | Drop-and-go intake with optional hints | confirmed | critical |
| OF-SRC-0003 | feedback | Minimize owner review load | confirmed | critical |
| OF-SRC-0004 | feedback | Author attribution errors are catastrophic | confirmed | critical |
| OF-SRC-0005 | feedback | Science hints follow the same cross-validation rule | confirmed | high |
| OF-SRC-0006 | feedback | Science registry must keep growing | confirmed | high |
| OF-SRC-0007 | feedback | Preserve and infer level metadata from content | confirmed | medium |
| OF-SRC-0008 | feedback | Multi-layer detection ownership is unresolved | confirmed | medium |
| OF-SRC-0009 | feedback | Replace numeric trust scoring with agent teams | confirmed | critical |
| OF-SRC-0010 | feedback | Muhaqiq standing is informational only | confirmed | high |
| OF-SRC-0011 | feedback | Agents resolve disagreements without human gate | confirmed | critical |
| OF-SRC-0012 | feedback | Hadith classification is the primary benchmark surface | confirmed | high |
| OF-SRC-0013 | feedback | Disagreement may itself be the true answer | confirmed | high |
| OF-SRC-0014 | feedback | Legacy contracts do not cap the rebuild | confirmed | critical |
| OF-SRC-0015 | feedback | Build source-engine teams inside the source-engine scope first | confirmed | medium |
| OF-SRC-0016 | feedback | Research must use specialized source channels | confirmed | high |

### CON-SRC-0001 — Shamela HTML and PDF are production formats
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0001; amended per OWNER_SANITY_CHECK_ANSWERS.md Q10, reference/pdf_fixture_observations_2026-04-14.md, and owner cross-validation on 2026-04-14 that normalization owns PDF-to-text conversion
- Rule: Production source intake must support Shamela HTML and PDF inputs, while plain text remains a minimal-metadata test format rather than a production collection format.

### CON-SRC-0002 — Hadith literature dominates source-engine benchmark quality
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0012; amended per contract-architect-review.yaml
- Rule: At least 40 percent of source-engine benchmark fixtures must be hadith literature or hadith-adjacent works.

### CON-SRC-0003 — No existing pipeline contract is binding on the rebuild
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0014
- Rule: Archived and legacy source-engine contracts are reference material only and cannot overrule the current atom set.

### OF-SRC-0001 — Collection unchanged for source intake
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 1 question 1
- Interview question: What changed about the source collection and intake formats?
- Owner answer: Collection unchanged. The source engine still targets the same ~2,519 Shamela HTML books, with no new production sources added.

### OF-SRC-0002 — Drop-and-go intake with optional hints
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 1 question 2
- Interview question: How much manual structure should the owner provide at intake time?
- Owner answer: The owner wants drop-and-go intake. Optional fields such as author or science are allowed as hints only, never as primary data. Matching hints boost confidence; diverging hints trigger investigation.

### OF-SRC-0003 — Minimize owner review load
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 1 question 3
- Interview question: How often should the owner review metadata decisions?
- Owner answer: The owner wants as few reviews as possible. The system should auto-decide aggressively and only send genuinely unresolvable cases to the owner.

### OF-SRC-0004 — Author attribution errors are catastrophic
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 1 question 4
- Interview question: Which metadata failure matters most to the owner?
- Owner answer: Author attribution errors are devastating. If attribution fails, the owner would doubt the whole library. This is the number one quality metric.

### OF-SRC-0005 — Science hints follow the same cross-validation rule
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 2 question 1
- Interview question: Should a science hint influence source inference?
- Owner answer: Science hints are optional and follow the same pattern as author hints. They never bias inference and are used only as post-inference cross-validation.

### OF-SRC-0006 — Science registry must keep growing
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 2 question 2
- Interview question: What happens when a book belongs to a science outside the current registry?
- Owner answer: The library never refuses knowledge. Sciences are a growable registry. New sciences may be added with owner confirmation, and no book is rejected only because its science is absent today.

### OF-SRC-0007 — Preserve and infer level metadata from content
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: medium
- Source: Owner interview batch 2 question 3
- Interview question: Is level metadata useful, and how should it be inferred?
- Owner answer: The level field is valuable. The owner recommends detecting it from content analysis rather than relying only on book-level metadata, but the final engine ownership is still unresolved.

### OF-SRC-0008 — Multi-layer detection ownership is unresolved
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: low
- Source: Owner interview batch 2 question 4
- Interview question: Should multi-layer detection happen in source or normalization?
- Owner answer: The owner is unsure. He thinks source-level hints that route normalization may be better, but explicitly said he is not confident about the final boundary.

### OF-SRC-0009 — Replace numeric trust scoring with agent teams
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 3 question 1
- Interview question: How should trust evaluation work?
- Owner answer: Trust evaluation should be rebuilt around agent teams rather than numeric factors. Two web researchers and two reasoners work under supervisors, supervisors deliberate, and monitor agents provide process-improvement feedback.

### OF-SRC-0010 — Muhaqiq standing is informational only
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 3 question 2
- Interview question: How should muhaqiq reputation affect source evaluation?
- Owner answer: Muhaqiq standing is metadata only. Unknown muhaqiqs should be flagged, and standing can be graduated from unknown to elite, but it must never cause the text to be discarded.

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

### OF-SRC-0012 — Hadith classification is the primary benchmark surface
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 3 question 4
- Interview question: Which part of the collection should dominate source-engine quality evaluation?
- Owner answer: Hadith is the owner's main focus and represents 48.7% of the collection. Fine-grained classification within hadith literature is therefore very important.

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

### OF-SRC-0014 — Legacy contracts do not cap the rebuild
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 4 question 2
- Interview question: How much authority do existing pipeline contracts keep during the rebuild?
- Owner answer: All engines will be rebuilt. No existing contract is binding, and the source engine should be engineered to the best possible quality without being capped by old infrastructure.

### OF-SRC-0015 — Build source-engine teams inside the source-engine scope first
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Owner interview batch 4 question 3
- Interview question: Where should the first agent infrastructure land?
- Owner answer: The immediate focus is the source engine. The best spec, build, and agent-team design should be created inside source-engine scope first, while reusable questions can be lifted later when downstream engines are built.

### OF-SRC-0016 — Research must use specialized source channels
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 4 question 4
- Interview question: What kind of research capability does the source engine need?
- Owner answer: Research should be much more accurate than generic web search. Dedicated agents should cover general web, specific scholarly sources, and well-defined reference databases.
