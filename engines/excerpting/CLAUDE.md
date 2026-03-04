# Excerpting Engine — محرك الاقتطاف

**Responsibility:** Grouping atoms into self-contained excerpts (§5).
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md
2. VISION.md §5 (the excerpt definition — the core intellectual specification)
3. VISION.md §2.3 (excerpt vocabulary)
4. Input boundary: atoms from atomization engine
5. Output boundary: draft excerpts → taxonomy engine

## Current State
Legacy code migrated from ABD. The excerpting engine is the intellectual core of the pipeline — ABD's reference docs encode months of extraction experience. However, ABD design decisions have zero authority in KR (D-019). Read ABD reference docs for domain knowledge, not as binding rules.

Code: `engines/excerpting/src/` (extract_passages.py 2288L, assemble_excerpts.py 1021L).
Tests: 258 tests in `engines/excerpting/tests/`.
Reference: 10 ABD-era docs (including binding decisions, runbook, edge cases — treat as historical reference).

## Key Constraints
1. **Self-containment is the defining property** (§5.1): every excerpt must be independently understandable. An excerpt that requires another excerpt to make sense is defective.
2. **Taxonomy-independent creation** (§5.2): excerpts are created without reference to any taxonomy tree. Placement happens later.
3. **Content integrity over taxonomic precision** (§5.3 Rule 3): never break an excerpt's self-containment to achieve cleaner taxonomy placement.
4. **Decontextualization risk:** When a scholar says "Scholar X holds that..." before refuting it, the excerpt must capture BOTH the reported position AND the refutation. Extracting only the reported position would misattribute it. The excerpting engine must detect "reporting another's view" patterns common in Islamic scholarly texts (قال فلان، وذهب فلان إلى، حُكي عن).
5. **Metadata enrichment (D-023):** The excerpting engine adds critical metadata that the synthesizer needs — author identification, school attribution, content type, hadith references with grading status where applicable. The excerpt is not just text; it's text + metadata that enables scholarly narrative synthesis.
6. **Editor vs. author text:** If the normalization engine has marked editorial apparatus, the excerpting engine must attribute correctly — editor's footnote analysis is NOT the original author's position.
7. **LLM extraction confidence.** Every content decision (topic classification, school attribution, content type) has an associated confidence level. This confidence is metadata that flows downstream — low-confidence excerpts get flagged for human review, and the synthesizer weights high-confidence excerpts more heavily. See DOMAIN.md "LLM Extraction Confidence."
8. **التخريج (takhrij) capture.** When tahqiq footnotes contain hadith source tracing (which collection, book/chapter/number, grading), the excerpting engine must capture this as structured metadata. The synthesizer uses takhrij to produce evidence-aware entries.
9. **Multi-layer attribution.** In multi-layer texts, the excerpting engine must attribute each excerpt to the correct AUTHOR based on the layer tags from atomization. An excerpt from Layer 1 atoms belongs to the matn author, even though the source is a sharh.
10. **Ellipsis and implicit context (حذف).** Arabic scholarly texts omit words "understood from context." Self-containment is harder when the text relies on implicit knowledge. The excerpting engine must evaluate self-containment from the perspective of the target reader — what's "understood" to a specialist may be opaque to a beginner. When in doubt, include more context to ensure the excerpt is independently comprehensible.
11. **Terminology normalization.** The same concept may appear under different names across sources (e.g., "المفعول له" vs "المفعول من أجله"). The excerpting engine should tag terminology variants so the taxonomy engine can map them to the correct leaf and the synthesizer can note the variation.
