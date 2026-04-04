# Critical Atoms: Non-Negotiables and Red-Team Tests (F3-F8)

Exhaustive extraction from all NONNEGOTIABLES and RED-TEAM-TESTS files across F3-F8 collections.
Cross-referenced against SPEC.md §1.1b (FP-1 through FP-18).

---

## Table of Contents

1. [F3 Non-Negotiables](#f3-non-negotiables)
2. [F3 Red-Team Tests](#f3-red-team-tests)
3. [F4 Non-Negotiables](#f4-non-negotiables)
4. [F4 Red-Team Tests](#f4-red-team-tests)
5. [F5 Non-Negotiables](#f5-non-negotiables)
6. [F5 Red-Team Tests](#f5-red-team-tests)
7. [F6 Non-Negotiables](#f6-non-negotiables)
8. [F6 Red-Team Tests](#f6-red-team-tests)
9. [F7 Non-Negotiables](#f7-non-negotiables)
10. [F7 Red-Team Tests](#f7-red-team-tests)
11. [F8 Non-Negotiables](#f8-non-negotiables)
12. [F8 Red-Team Tests](#f8-red-team-tests)
13. [Coverage Summary](#coverage-summary)

---

## F3 Non-Negotiables

Source: `chatgpt_f3_collection/09_nonnegotiables.jsonl`

| ID | Atom | Severity | Authority | Captured in SPEC? |
|----|------|----------|-----------|-------------------|
| NN-001 | Do not treat surface chapter-intro language as decisive if the passage actually performs ruling or other substantive functions. | high | owner_explicit | Partial -- FP-6 (rules + intelligence) addresses surface-vs-function reasoning generally, but no FP explicitly prohibits surface-driven function misclassification. |
| NN-002 | Do not keep a multi-function passage merged as one entry when introduction, ruling, proof-overview, and refutation are all substantively present. | high | owner_explicit | No direct FP. Relates to FP-9 (overgranulation vs undergranulation) but addresses the opposite direction -- forced merging of distinct functions. |
| NN-003 | Do not sever linking dependencies blindly, especially at `لأن` and similar continuations. | critical | owner_explicit | Yes -- FP-3 (Linking-word intelligence). Directly captured. |
| NN-004 | Do not remove the chapter title from an excerpt when `هذا الباب` or equivalent chapter-reference language depends on it. | high | owner_explicit | Partial -- FP-2 (context resolution hierarchy) covers context needs generally, but the specific chapter-title-retention-for-reference-anchoring is not explicitly stated. |
| NN-005 | Do not mistake a chapter-specific introduction for a full-topic introduction without qualification. | high | owner_explicit | No direct FP. Scope-mismatch in introduction classification is not covered. |
| NN-006 | Allow small, strongly linked carryover to remain when removing it would produce a worse self-containment outcome. | high | owner_explicit | Partial -- FP-13 (principle conflict precedence) addresses tradeoffs, but the specific forgiving-rule for small carryover is not an FP. |
| NN-007 | Do not let the forgiving rule justify keeping later substantial functions merged once the overlap is no longer negligible. | high | owner_explicit | No direct FP. Anti-over-forgiveness constraint is not captured. |
| NN-008 | Do not solve multi-home relevance by copying the whole large merged passage into several leaves when careful sub-excerpting is available. | medium_high | owner_explicit | No direct FP. Duplication-avoidance via sub-excerpting is not stated. |
| NN-009 | Do not let short hukm-return material disappear from the hukm home merely because it also appears inside a refutation-oriented segment. | high | owner_explicit | No direct FP. Knowledge-scattering prevention for hukm visibility is not captured. |
| NN-010 | Do not automate title retention, function classification, or split points by one blunt heuristic; dependency analysis must happen first. | critical | owner_consistent_inference | Partial -- FP-6 (rules + intelligence) implies this, but the specific anti-blunt-heuristic directive is not an FP. |

---

## F3 Red-Team Tests

Source: `chatgpt_f3_collection/10_red_team_tests.jsonl`

| ID | Targets | Type | Test Description | Authority | Captured in SPEC? |
|----|---------|------|-----------------|-----------|-------------------|
| RT-001 | CE-001, LD-001, NN-004 | mutation | Remove the chapter title from the introduction excerpt and test whether `هذا الباب` remains safely interpretable. | owner_explicit | No explicit test requirement in FP. |
| RT-002 | CE-002, LD-002, NN-003 | mutation | Start the ruling excerpt directly at `لأن` and evaluate whether the excerpt remains safe without retained upstream context. | owner_explicit | Partially covered by FP-3. |
| RT-003 | LD-003, LD-004, CE-002 | mutation | Remove the retained lead-in and test whether `عليهما` and `غسلهما` still have a safe internal anchor. | owner_explicit | Relates to FP-12 (implied dependency). |
| RT-004 | DL-003, GA-001, NN-002 | contrast | Keep the entire passage merged as one entry and compare it against the split candidates for function clarity. | owner_explicit | No direct FP. |
| RT-005 | FP-002, NN-001 | audit | Classify the whole passage as introduction-only and inspect what ruling/proof/refutation information becomes misplaced. | owner_explicit | No direct FP test. |
| RT-006 | FP-002, NN-005 | simulation | Treat the first sentence as a full-topic introduction to المسح على الخفين rather than a proof-specific chapter introduction. | owner_explicit | No direct FP. |
| RT-007 | GA-003, NN-006, NN-007 | stress | Apply the forgiving rule too aggressively and see whether proof overview and refutation remain wrongly trapped inside one broad hukm entry. | owner_explicit | No direct FP test. |
| RT-008 | CE-003, LD-005 | mutation | Isolate the proof-overview excerpt exactly at `فهو ...` with no retained anchor and evaluate whether the proof unit remains safely grounded. | model_only | No. |
| RT-009 | CE-004, GA-005, NN-009 | contrast | Compare two versions of the refutation excerpt: one keeping the short hukm-return clause and one stripping it out entirely. | owner_explicit | No direct FP. |

---

## F4 Non-Negotiables

Source: `chatgpt_f4_collection/09_nonnegotiables.jsonl`

| ID | Atom | Severity | Authority | Captured in SPEC? |
|----|------|----------|-----------|-------------------|
| NN-001 | Do not merge an unbiased disagreement marker with a scholar's tarjih when they answer different questions. | high | (not stated) | Yes -- FP-8 (Khilaf-tarjih distinction). Directly captured. |
| NN-002 | Do not let surrounding context rescue the owner verdict on the excerpt as given. | high | (not stated) | No direct FP. Engineering-layer vs owner-layer separation is not explicitly stated. |
| NN-003 | Do not lose the attribution-critical nature of tarjih. | high | (not stated) | Partial -- FP-8 covers the distinction but not the specific attribution-loss risk. |
| NN-004 | Do not treat every opening `و` as the same type of dependency. | medium | (not stated) | Yes -- FP-3 (Linking-word intelligence). Directly captured. |
| NN-005 | Do not accept a clipped tarjih lead-in as a standalone completed excerpt. | high | (not stated) | No direct FP. Completeness of tarjih segments is not covered. |
| NN-006 | Do not split a disagreement marker from a full unbiased opinion listing if both answer the same disagreement-structuring question and are too tightly linked. | medium | (not stated) | Partial -- FP-8 distinguishes khilaf and tarjih but does not cover intra-khilaf clustering. |
| NN-007 | Do not classify the function of a segment by surface appearance alone. | high | (not stated) | Partial -- FP-6 (rules + intelligence) implies this but does not state it as a prohibition. |
| NN-008 | Do not automate split decisions without asking what question each segment is answering. | high | (not stated) | No direct FP. Question-cluster methodology is not in the FPs. |
| NN-009 | Do not mistake the corrected engineering candidates for the excerpt as given. | high | (not stated) | No direct FP. Owner-verdict vs engineering-reconstruction separation is not stated. |

---

## F4 Red-Team Tests

Source: `chatgpt_f4_collection/10_red_team_tests.jsonl`

| ID | Targets | Type | Test Description | Authority | Captured in SPEC? |
|----|---------|------|-----------------|-----------|-------------------|
| RT-001 | FP-001, NN-001 | contrast | Keep the excerpt merged exactly as given and compare it to a split treatment separating disagreement marker from tarjih. | owner_explicit | Relates to FP-8. |
| RT-002 | QC-003, NN-001 | mutation | Split the disagreement marker from the tarjih and evaluate whether clarity improves. | owner_explicit | Relates to FP-8. |
| RT-003 | QC-002, NN-006 | simulation | Simulate a full source where the disagreement marker is immediately followed by an unbiased list of opinions and test whether the cluster remains coherent as one excerpt. | owner_explicit | No direct FP test. |
| RT-004 | CD-001, NN-004 | contrast | Treat the opening `و` as always externally dependent and compare the result to an intelligent local-continuation reading. | owner_explicit | Yes -- tests FP-3. |
| RT-005 | CD-003, CD-004, NN-002, NN-009 | audit | Use surrounding context to complete the tarjih in the engineering layer only, and verify that the owner verdict on the excerpt as given remains unchanged. | owner_explicit | No direct FP test. |
| RT-006 | FP-002, FP-003, NN-003 | mutation | Classify the whole excerpt as pure disagreement material and inspect what attribution is lost. | model_only | Relates to FP-8. |
| RT-007 | FP-001, NN-007 | mutation | Classify the whole excerpt as pure tarjih and inspect what unbiased disagreement signal disappears. | model_only | Relates to FP-8. |
| RT-008 | QC-004, NN-005 | stress | Strip the explicit completion of the preferred view from the tarjih candidate and test whether the excerpt still works as attributed preference. | owner_consistent_inference | No direct FP test. |
| RT-009 | DL-008, QC-001, QC-003, QC-004 | audit | Run a question-cluster analysis first, then rerun the case with only surface segmentation, and compare the resulting excerpt map. | owner_explicit | No direct FP test. |

---

## F5 Non-Negotiables

Source: `chatgpt_f5_collection/10_nonnegotiables.jsonl`

| ID | Atom | Severity | Authority | Captured in SPEC? |
|----|------|----------|-----------|-------------------|
| NN-001 | Do not let a generated summary note silently replace source-preserving context where source integrity materially matters. | high | owner_explicit | Partial -- FP-2 (context resolution hierarchy) establishes the priority order, but the anti-summary-replacement prohibition is stronger than what FP-2 states. |
| NN-002 | Do not separate explanation from the explained text blindly. | high | owner_explicit | Yes -- FP-1 (Explained-explanation unity). Directly captured. |
| NN-003 | Do not rely on a book's loose proof rendering as the only authoritative proof layer. | high | owner_explicit | Yes -- FP-7 (Fetched proof vs book-preserved proof). Directly captured. |
| NN-004 | Do not discard book-preserved proof excerpts just because authoritative fetching exists. | high | owner_explicit | Yes -- FP-7 (Fetched proof vs book-preserved proof). Directly captured. |
| NN-005 | Do not assume all scholar methodologies fit prewritten rules and protocols. | high | owner_explicit | Yes -- FP-6 (Rules + intelligence). Directly captured. |
| NN-006 | Do not treat the note question as the whole issue when the pair is structurally malformed before the note enters the picture. | high | owner_explicit | No direct FP. Structural malformation vs note-quality conflation is not stated. |
| NN-007 | Do not treat a readable note-backed explanation as proven safe if the explanation-to-proof linkage is still unresolved. | high | model_only | No direct FP. Readability-masking-integrity-failure is not explicitly an FP. |
| NN-008 | Do not collapse all hadith explanations into one generic proof source when version, wording, or grading may differ. | high | owner_explicit | Partial -- FP-7 covers dual-layer preservation but not the version-sensitivity of hadith explanations specifically. |
| NN-009 | Do not proceed with confident automated separation when the system cannot determine the methodology fit with high certainty. | high | owner_explicit | Yes -- FP-6 (uncertainty gates). Captured in spirit. |
| NN-010 | Do not optimize for neat separation-of-concerns at the expense of knowledge integrity. | high | owner_explicit | Yes -- FP-5 (knowledge corruption is the worst failure). Captured in spirit. |

---

## F5 Red-Team Tests

Source: `chatgpt_f5_collection/11_red_team_tests.jsonl`

| ID | Targets | Type | Test Description | Authority | Captured in SPEC? |
|----|---------|------|-----------------|-----------|-------------------|
| RT-001 | NA-001, NA-004 | mutation | Remove the note entirely and present the current explanation excerpt starting at "المعنى الإجمالي:". | owner_explicit | No direct FP test. |
| RT-002 | CCB-001, CCB-002 | contrast | Compare the current generated summary note against a source-preserving context block containing the actual hadith material. | owner_explicit | Relates to FP-2. |
| RT-003 | EE-002, MR-001 | stress | Split explanation from explained text, then inject two similar hadith variants and check whether the system keeps the explanation tied to the right one. | owner_explicit | Tests FP-1 edge case. |
| RT-004 | PI-001, PI-002, PI-003 | contrast | Compare studying from the proof as found in the book alone versus the authoritative fetched proof alone versus both layers linked together. | owner_explicit | Tests FP-7. |
| RT-005 | MR-002, PI-004 | simulation | Use a scholar explanation that presupposes one grading/authenticity assumption while the fetched proof layer defaults to another. | owner_explicit | Extends FP-7. |
| RT-006 | MR-003, EE-004 | simulation | Test a scholar methodology where topic, proof, and explanation are deeply interwoven and cannot be cleanly separated by prewritten rules. | owner_explicit | Tests FP-6. |
| RT-007 | NA-001, NA-003 | contrast | For the current broken pair, compare default-visible note versus collapsible note. | owner_consistent_inference | No direct FP test. |
| RT-008 | PI-003, PI-004 | audit | Audit whether a fetched authoritative proof record is explicitly linked to the exact wording/version the scholar's explanation appears to assume. | owner_consistent_inference | Extends FP-7 (unresolved linkage). |
| RT-009 | NN-006, MR-005 | stress | Make the note rich enough to feel readable while leaving the explained/explanation split untouched. | model_only | No direct FP test. |

---

## F6 Non-Negotiables

Source: `chatgpt_f6_collection/12_nonnegotiables.jsonl`

| ID | Atom | Severity | Authority | Captured in SPEC? |
|----|------|----------|-----------|-------------------|
| NN-001 | Do not treat a scholar-book proof rendering as the final authoritative memorization source by default. | high | (not stated) | Yes -- FP-7 (Fetched proof vs book-preserved proof). Directly captured. |
| NN-002 | Do not mutate the original author's wording merely to make the text more study-friendly. | high | (not stated) | Yes -- FP-5 (knowledge corruption) + frozen source principle (Rule 1/2 in CLAUDE.md). |
| NN-003 | Do not withhold authoritative fetched proofs where direct memorization depends on certainty. | high | (not stated) | Yes -- FP-7. Directly captured. |
| NN-004 | Do not lose the relationship between a scholar's wording and the authoritative proof variants it corresponds to. | high | (not stated) | Partial -- FP-7 preserves both layers but does not explicitly mandate the scholar-to-variant mapping. |
| NN-005 | Do not collapse scholar-book witness and authoritative proof into one undifferentiated proof layer. | high | (not stated) | Yes -- FP-7. Directly captured. |
| NN-006 | Do not reduce this case to a mere reading-preference or layout-preference question. | medium | (not stated) | No direct FP. Anti-trivialization of proof-layer design is not stated. |
| NN-007 | Do not assume all future scholar methodologies fit a closed set of hard rules. | high | (not stated) | Yes -- FP-6 (Rules + intelligence). Directly captured. |
| NN-008 | Do not apply study-friendly chunking to the wrong layer as if it were the preserved original text. | high | (not stated) | Partial -- FP-7 separates layers, but layer-aware chunking is not explicit. |
| NN-009 | Do not hide whether wording differences are significant, non-significant, or still uncertain. | high | (not stated) | No direct FP. Variant-significance transparency is not stated. |
| NN-010 | Do not let secondary help layers silently replace the preserved source layer. | high | (not stated) | Partial -- FP-2 (context hierarchy) and FP-7 both imply this, but the explicit anti-replacement prohibition is not an FP. |

---

## F6 Red-Team Tests

Source: `chatgpt_f6_collection/13_red_team_tests.jsonl`

| ID | Targets | Type | Test Description | Authority | Captured in SPEC? |
|----|---------|------|-----------------|-----------|-------------------|
| RT-001 | NN-001, PL-001, PL-002, MP-001, MP-002 | contrast | Compare direct memorization from the scholar-book proof witness against direct memorization from the authoritative fetched proof layer. | (not stated) | Tests FP-7. |
| RT-002 | VD-001, VD-002, DA-002 | contrast | Compare one pair of proof variants with only non-significant wording drift against one pair where the wording materially changes the conclusion. | (not stated) | No direct FP test. |
| RT-003 | DA-001, PL-003 | audit | Test whether the system can correctly link each scholar's explanation or conclusion to the specific proof version relied on in the book witness layer. | (not stated) | Extends FP-7. |
| RT-004 | TP-001, TP-002, NN-008 | mutation | Apply study-friendly chunking directly to the scholar-book witness text and see whether the layer boundary is lost. | (not stated) | Extends FP-7. |
| RT-005 | DL-007, NN-007 | simulation | Introduce a new scholar methodology in which rule, proof, and explanation are interwoven differently from known patterns. | (not stated) | Tests FP-6. |
| RT-006 | VD-004, NN-009 | stress | Give the system a variant difference whose significance is genuinely unclear and test whether it reports uncertainty instead of false confidence. | (not stated) | Tests FP-6 (uncertainty gates). |
| RT-007 | NN-010, TP-003, TP-004 | mutation | Present a generated summary or help layer without clear separation from the original source text. | (not stated) | Tests FP-2 indirectly. |
| RT-008 | PL-002, PL-003, NN-003 | audit | Remove the authoritative fetched proof layer and see whether the remaining system still pushes direct memorization from the scholar-book witness. | (not stated) | Tests FP-7. |
| RT-009 | DA-003, DA-004 | stress | Run large-scale cross-source analysis and check whether the system can produce scholar/proof/opinion insights without collapsing different proof layers together. | (not stated) | No direct FP test. |

---

## F7 Non-Negotiables

Source: `chatgpt_f7_collection/08_nonnegotiables.jsonl`

| ID | Atom | Severity | Authority | Captured in SPEC? |
|----|------|----------|-----------|-------------------|
| NG-001 | The library must never silently alter source knowledge into a different meaning while presenting it as faithful. | existential | (not stated) | Yes -- FP-5 (knowledge corruption is the worst failure). Directly captured. |
| NG-002 | Every study-facing unit must remain auditably tied to source, version, and processing lineage. | existential | (not stated) | Partial -- FP-10 (source surroundings) provides location metadata. Full provenance/lineage is implied by D-023 but not an explicit FP. |
| NG-003 | No unbounded content error may remain live without immediate containment, blast-radius assessment, and visible warning. | existential | (not stated) | Partial -- FP-5 (fail loud) covers the visible-warning part but not blast-radius containment specifically. |
| NG-004 | The system must never present low-confidence or weakly verified knowledge with the same confidence profile as strongly verified knowledge. | catastrophic | (not stated) | Partial -- FP-6 (uncertainty gates) covers uncertainty but not confidence-profile differentiation in presentation. |
| NG-005 | Boundary decisions must not distort meaning, remove necessary anchoring, or atomize study units into unusable fragments. | catastrophic | (not stated) | Yes -- FP-9 (overgranulation is worse) + FP-13 (precedence stack) + FP-3 (linking-word intelligence). Collectively captured. |
| NG-006 | Attribution, quote-layer, and current-source function must never be flattened into a single undifferentiated authorship assumption. | existential | (not stated) | Yes -- FP-14 (speaker-role inversion) + FP-15 (rhetorical posture detection). Directly captured. |
| NG-007 | The taxonomy and relation graph must not place content under the wrong science, wrong branch, or wrong proof/example linkage without detection. | catastrophic | (not stated) | Partial -- FP-4 (taxonomy independence) covers the excerpting side. Taxonomy-level detection is a taxonomy engine concern. |
| NG-008 | The system must not hide excerpting cuts in a way that makes the result look like uninterrupted source flow. | serious | (not stated) | No direct FP. Anti-deceptive-cleanliness is not stated. FP-18 (three-level quality) distinguishes acceptability but not cut visibility. |
| NG-009 | Validation must prove hard cases rather than merely passing polished easy-path examples. | catastrophic | (not stated) | No direct FP. Validation rigor requirement is not stated. |
| NG-010 | No core engine or contract may be built on unresearched or weakly justified assumptions in a way that is hard to reverse later. | catastrophic | (not stated) | No direct FP. Anti-premature-commitment is not stated. |
| NG-011 | The economics and performance model must remain compatible with full-corpus ambition; local success on tiny slices is not enough. | catastrophic | (not stated) | No direct FP. Scale-compatibility requirement is not stated. |
| NG-012 | Project memory must be durable: progress, artifacts, backups, exports, and datasets must survive failure and migration. | existential | (not stated) | No direct FP. Project durability is a project-level concern, not an excerpting FP. |
| NG-013 | Collected data must be structured for future reuse, audit, and training; today's outputs cannot be disposable or schema-fragile. | catastrophic | (not stated) | No direct FP. Future-training-data concern is a project-level constraint (Rule 13 in CLAUDE.md). |
| NG-014 | The build environment, research surface, and agent collaboration model must not be allowed to remain the hidden ceiling of the project. | serious | (not stated) | No direct FP. Tooling/environment ceiling is a project-level concern. |

---

## F7 Red-Team Tests

Source: `chatgpt_f7_collection/09_red_team_tests.jsonl`

| ID | Targets | Type | Test Description | Authority | Captured in SPEC? |
|----|---------|------|-----------------|-----------|-------------------|
| RT-001 | SC-001, SC-030 | injection | Inject a single-character or diacritic-altering corruption into Arabic source text and verify that frozen-source comparison, downstream lineage, and study-facing surfaces all fail loudly. | (not stated) | Tests FP-5. |
| RT-002 | SC-004, SC-011, SC-024 | mutation | Force alternative split/merge decisions on the same passage and check whether meaning, anchoring, omission honesty, and study usability are preserved or broken. | (not stated) | Tests FP-9 + FP-13. |
| RT-003 | SC-018, SC-019, SC-031 | audit | Pick random study-facing units and require full reconstruction of source, edition/version, page, and processing path from the stored lineage alone. | (not stated) | Tests FP-10 + D-023. |
| RT-004 | SC-020, SC-021 | contrast | Construct cases where the same quoted text plays different roles in different parent sources and verify that the system classifies by current-source function, not just surface wording. | (not stated) | Tests FP-14 + FP-15. |
| RT-005 | SC-022, SC-028 | contrast | Feed pairs of near-neighbor branches and secondary mentions to the taxonomy layer and inspect whether the system can distinguish true topic placement from mere mention. | (not stated) | Tests FP-4 (taxonomy independence). |
| RT-006 | SC-023, SC-026 | simulation | Hide one proof link, one example link, and one ranking signal in otherwise plausible records, then observe whether downstream study surfaces become misleading without obvious errors. | (not stated) | No direct FP test. |
| RT-007 | SC-027, SC-044 | audit | Audit all study-facing views for places where confidence, uncertainty, missing lineage, or weak validation are visually suppressed or normalized. | (not stated) | Tests FP-6 (uncertainty gates). |
| RT-008 | SC-035, SC-042 | stress | Deliberately build happy-path test suites that would pass even if the real edge rule were implemented incorrectly, then verify the harness catches the hollowness. | (not stated) | No direct FP test. |
| RT-009 | SC-005, SC-015, SC-041 | audit | Pick a core contract or schema and ask what breaks if one field or assumption changes; enumerate downstream consequences before build continuation. | (not stated) | No direct FP test. |
| RT-010 | SC-009, SC-010, SC-040 | stress | Run corpus-scale cost and latency projections using worst-case realistic assumptions rather than demo averages. | (not stated) | No direct FP test. |
| RT-011 | SC-006, SC-007, SC-038 | simulation | Perform an end-to-end disaster recovery drill: restore the app, structured data, lineage, and searchability from backups and exports only. | (not stated) | No direct FP test. |
| RT-012 | SC-012, SC-039 | audit | Sample the training-candidate dataset and trace whether each record retains enough structure, lineage, and error history to be safe for future local-model use. | (not stated) | No direct FP test. |
| RT-013 | SC-013, SC-014, SC-016, SC-017, SC-045 | audit | Red-team the build environment itself: missing tools, missing hooks, weak role definition, absent review routes, and unclaimed responsibility zones. | (not stated) | No direct FP test. |
| RT-014 | SC-029 | contrast | Run the same footnote-heavy source under crude policies (always glue vs always split) and compare knowledge retention, pollution, and study usability. | (not stated) | No direct FP test. |
| RT-015 | SC-034 | simulation | Force the pipeline onto weaker fallback models for ambiguous and high-risk cases, then compare outputs and confidence signaling against the strongest path. | (not stated) | Tests FP-6 (uncertainty gates). |
| RT-016 | SC-043, SC-046 | mutation | Introduce a defect, let it survive into multiple stored artifacts and study surfaces, then fix it and test whether the system can precisely enumerate everything contaminated during the bad period. | (not stated) | No direct FP test. |

---

## F8 Non-Negotiables

Source: `chatgpt_f8_collection/09_nonnegotiables.jsonl`

| ID | Atom | Severity | Authority | Captured in SPEC? |
|----|------|----------|-----------|-------------------|
| NN-001 | Excerpting must not be biased by the current taxonomy tree. | catastrophic | (not stated) | Yes -- FP-4 (Taxonomy independence). Directly captured. |
| NN-002 | Rightful excerpt output must remain invariant under changes in tree granulation. | catastrophic | (not stated) | Yes -- FP-4. Directly captured. |
| NN-003 | Guidance allowed for placement must not leak backward into excerpt boundary formation. | catastrophic | (not stated) | Yes -- FP-4. Directly captured (stage contamination). |
| NN-004 | Visible wrong placement and silent excerpt corruption must be tracked as different severity classes. | serious | (not stated) | No direct FP. Severity-class distinction between visible-wrong-placement and silent-corruption is not stated. FP-5 covers silent corruption only. |
| NN-005 | Overgranulated placement must not force one natural topic into multiple leaves without a defensible common denominator. | serious | (not stated) | Yes -- FP-9 (Overgranulation is worse than undergranulation). Directly captured. |
| NN-006 | Blind or weakly guided processing must be audited for boundary consistency across comparable passages. | serious | (not stated) | No direct FP. Cross-passage boundary consistency auditing is not stated. |
| NN-007 | Placement validation must never silently reject or reshape excerpts merely because they fit the current tree badly. | catastrophic | (not stated) | Yes -- FP-4 (taxonomy independence). Covert second excerpter risk is directly covered. |
| NN-008 | Tree revision must not retroactively rewrite already-frozen excerpt truth. | catastrophic | (not stated) | Partial -- FP-4 covers excerpting independence from taxonomy. Retroactive-rewrite is stronger than what FP-4 states (frozen excerpt immutability). |
| NN-009 | Search, ranking, and presentation must not turn a wrong box into false authority. | serious | (not stated) | No direct FP. Presentation-amplified structural bias is not stated. |
| NN-010 | Any sign that the excerpting stage is configuration-sensitive rather than source-sensitive must trigger audit, not normalization. | catastrophic | (not stated) | No direct FP. Configuration-sensitivity detection is not stated. |

---

## F8 Red-Team Tests

Source: `chatgpt_f8_collection/10_red_team_tests.jsonl`

| ID | Targets | Type | Test Description | Authority | Captured in SPEC? |
|----|---------|------|-----------------|-----------|-------------------|
| RT-001 | SC-001, SC-002, NN-001, NN-002 | contrast | Run the same source passage under correctly granulated, undergranulated, and overgranulated trees; compare excerpt outputs for invariance. | (not stated) | Tests FP-4. |
| RT-002 | SC-017, SC-006, NN-006 | contrast | Process the same passage once with prior topic guidance and once blind; compare excerpt boundaries, grouping, and consistency. | (not stated) | Tests FP-4 edge case. |
| RT-003 | SC-008, NN-001 | injection | Inject a misleading prior doctrinal box and test whether the excerpter starts cutting or framing the passage to fit it. | (not stated) | Tests FP-4 (excerpting-bias). |
| RT-004 | SC-004, SC-005, SC-014 | stress | Place the same correct excerpt set into an overgranulated tree and an undergranulated tree, then compare user confusion and repair difficulty. | (not stated) | Tests FP-9. |
| RT-005 | SC-003, SC-010, NN-004 | contrast | Contrast a visible wrong leaf placement with a silent excerpt corruption while holding source passage and topic constant. | (not stated) | Tests FP-5 + F8-NN-004. |
| RT-006 | SC-016, NN-007 | audit | Instrument placement validation to prove whether tree-fit scores ever suppress, reject, or reshape excerpts. | (not stated) | Tests FP-4. |
| RT-007 | SC-009, NN-008 | simulation | Freeze excerpts, then redesign the tree and verify that placement changes do not alter excerpt identity. | (not stated) | Tests FP-4 + frozen source rule. |
| RT-008 | SC-015, NN-009 | stress | Surface a deliberately misboxed excerpt repeatedly through search/ranking and test whether the interface makes the placement feel authoritative. | (not stated) | No direct FP test. |
| RT-009 | SC-006, SC-018, NN-006 | audit | Audit boundary consistency across a family of similar passages from different books or sections. | (not stated) | No direct FP test. |
| RT-010 | SC-011, TH-006 | simulation | Simulate delayed discovery: compare source text against a long-used excerpt set after memorization has already occurred. | (not stated) | Tests FP-5 (delayed-discovery variant). |

---

## Coverage Summary

### Non-Negotiables: SPEC Coverage Statistics

| Collection | Total NNs | Fully Captured | Partially Captured | Not Captured |
|------------|-----------|----------------|-------------------|--------------|
| F3 | 10 | 1 (NN-003) | 5 (NN-001, NN-004, NN-005, NN-006, NN-010) | 4 (NN-002, NN-007, NN-008, NN-009) |
| F4 | 9 | 2 (NN-001, NN-004) | 3 (NN-003, NN-006, NN-007) | 4 (NN-002, NN-005, NN-008, NN-009) |
| F5 | 10 | 5 (NN-002, NN-003, NN-004, NN-005, NN-009) | 3 (NN-001, NN-008, NN-010) | 2 (NN-006, NN-007) |
| F6 | 10 | 5 (NN-001, NN-003, NN-005, NN-007, NN-002) | 3 (NN-004, NN-008, NN-010) | 2 (NN-006, NN-009) |
| F7 | 14 | 2 (NG-001, NG-006) | 4 (NG-002, NG-003, NG-004, NG-005) | 8 (NG-007 thru NG-014) |
| F8 | 10 | 5 (NN-001, NN-002, NN-003, NN-005, NN-007) | 1 (NN-008) | 4 (NN-004, NN-006, NN-009, NN-010) |
| **TOTAL** | **63** | **20 (32%)** | **19 (30%)** | **24 (38%)** |

### Key Uncaptured Themes (recurring across collections, no FP coverage)

1. **Anti-over-forgiveness** (F3-NN-007): The forgiving rule must not justify keeping substantial functions merged.
2. **Question-cluster methodology** (F4-NN-008): Split decisions should be driven by what question each segment answers.
3. **Owner-verdict vs engineering-reconstruction separation** (F4-NN-002, F4-NN-009): Engineering fixes must not contaminate owner-facing verdicts.
4. **Structural malformation vs note quality** (F5-NN-006): Do not let note UX mask broken excerpt structure.
5. **Readability masking integrity failure** (F5-NN-007): Readable output is not the same as correct output.
6. **Variant-significance transparency** (F6-NN-009): The system must expose whether proof-text differences are significant.
7. **Configuration-sensitivity detection** (F8-NN-010): If excerpting changes with configuration, trigger audit.
8. **Boundary consistency auditing** (F8-NN-006): Similar passages must get consistent boundary treatment.
9. **Presentation-amplified bias** (F8-NN-009): Wrong placement can become authoritative through repetition.
10. **Validation rigor** (F7-NG-009): Validation must target hard cases, not polished happy paths.
11. **Anti-deceptive cleanliness** (F7-NG-008): Excerpting cuts must be visible, not hidden.
12. **Project durability** (F7-NG-012): Memory, backups, and exports must survive failure.
13. **Scale compatibility** (F7-NG-011): Economic model must work for full corpus, not just demo slices.
14. **Severity-class distinction** (F8-NN-004): Wrong placement and silent corruption are different failure classes.

### Red-Team Tests: SPEC Coverage Statistics

| Collection | Total RTs | Tests an FP | No FP Coverage |
|------------|-----------|-------------|----------------|
| F3 | 9 | 3 (RT-002, RT-003, RT-005) | 6 |
| F4 | 9 | 4 (RT-001, RT-002, RT-004, RT-006) | 5 |
| F5 | 9 | 4 (RT-002, RT-004, RT-005, RT-006) | 5 |
| F6 | 9 | 6 (RT-001, RT-003, RT-004, RT-005, RT-006, RT-008) | 3 |
| F7 | 16 | 6 (RT-001, RT-002, RT-003, RT-004, RT-005, RT-007) | 10 |
| F8 | 10 | 7 (RT-001, RT-003, RT-004, RT-005, RT-006, RT-007, RT-010) | 3 |
| **TOTAL** | **62** | **30 (48%)** | **32 (52%)** |

---

*Generated 2026-04-04. Source files: 12 JSONL files across chatgpt_f3_collection through chatgpt_f8_collection.*
