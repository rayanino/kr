# Adversarial review of KR excerpting engine's five proposed Safety & Integrity FPs

**Verdict: ITERATE.** All five proposed FPs address genuine safety gaps and should advance—but two carry internal contradictions that will produce wrong outcomes if implemented naively, and the batch collectively leaves three existential-grade threats unaddressed. The most dangerous finding: **FP-5 and FP-21 directly conflict on halt conditions**, and none of the five FPs protect against silent context-window truncation, the single most invisible corruption vector in the LLM-based pipeline.

The proposed principles correctly identify the safety surface they target—omission honesty, severity classification, validation discipline. But they underestimate two things: the genre-dependent nature of what constitutes "corruption" in Islamic scholarly texts, and the infrastructure layer's ability to silently undermine every content-level guarantee. What follows is the adversarial breakdown, FP by FP, across all five review questions.

---

## Q1: The failure scenario that looks correct but kills knowledge integrity

### Strengthened FP-5 — the tashkeel phantom cascade

Consider *Radd al-Muḥtār* by Ibn ʿĀbidīn, the canonical Ḥanafī ḥāshiyah layering three authorial voices: Timurtāshī's *Tanwīr al-Abṣār* (matn), al-Ḥaskafī's *al-Durr al-Mukhtār* (sharḥ), and Ibn ʿĀbidīn's own super-commentary. Shamila exports of this work routinely have **stripped or inconsistent diacritization**. The consonantal skeleton حرم yields both حَرُمَ (*ḥaruma*, "it became forbidden") and حَرَمَ (*ḥarama*, "he deprived")—opposite legal meanings from identical rasm.

If the LLM resolves this ambiguity incorrectly in one excerpt and downstream validation catches it, naive FP-5 triggers cascading trust collapse: the entire 8-volume reference work is quarantined, every cross-referencing Ḥanafī text loses trust, and the engine halts. But the root cause isn't engine corruption—it's **source-inherited ambiguity** that affects ~90% of all Arabic prose. Naive FP-5 means the engine can never process unvoweled text without permanent halt risk.

**Required refinement:** FP-5 must distinguish three error provenance classes. **Class A** (engine-introduced: fabrication, misattribution) warrants full cascade and halt. **Class B** (source-inherited, systematically predictable: tashkeel ambiguity, ة/ه confusion, ى/ي confusion) warrants per-excerpt flagging with a "source ambiguity" marker but no cascade. **Class C** (source-inherited, idiosyncratic: OCR errors in a specific Shamila export) warrants quarantine of the affected volume, not the entire work. The halt threshold must require a *pattern* of Class A errors, not any single Class B occurrence.

### FP-19 (Omission honesty) — the authorial attribution reversal

In al-Nawawī's *al-Majmūʿ Sharḥ al-Muhadhdhab*, the sharḥ quotes al-Shīrāzī's matn piecemeal, introduced by markers like "قال المصنف رحمه الله." In printed editions, the matn appears in distinct formatting; in Shamila exports, that visual layer is stripped. Only textual markers remain.

When the excerpter extracts part of al-Nawawī's commentary followed by the next matn section, FP-19 requires inserting an omission marker `[...]` at the cut. The result attributes both al-Nawawī's words and al-Shīrāzī's matn to a single continuous voice. The "قال المصنف" signal that marks the layer transition has been excised and replaced with a continuity marker that **actively misleads about authorship**. The cure is worse than the disease: without the marker, the reader might encounter the attribution signal; with it, that signal is gone and replaced by false continuity.

**Required refinement:** Omission markers must be **layer-aware**. When a cut crosses an authorial boundary (matn→sharḥ or sharḥ→matn), the marker must preserve the layer-transition signal—e.g., retaining "قال المصنف" even when surrounding text is cut—or carry layer metadata like `[... sharḥ content omitted; begins matn of al-Shīrāzī ...]`. An omission marker that crosses an authorial boundary without indicating it should be classified as silent corruption under FP-21.

### FP-20 (Validation rigor) — the school-dependent terminology trap

Al-Zamakhsharī's *al-Mufaṣṣal* (Basran-leaning) and al-Farrāʾ's *Maʿānī al-Qurʾān* (foundational Kufan) both discuss الفعل المضارع. The terms are identical; the technical scopes differ between schools. The same applies across fiqh: the Ḥanafī distinction between واجب and فرض (obligation from probable vs. definitive evidence) collapses in the Shāfiʿī school where these terms are synonymous.

FP-20 defines "hard cases" as structurally complex texts—long debates, multi-page digressions. But a three-line excerpt from al-Farrāʾ taxonomized under the same node as a Basran treatment by Sībawayhi is **surface-clean but semantically corrupted** through terminological equivocation. It passes every "hard case" test because it's short, well-formed, and unambiguous at the surface level.

**Required refinement:** Hard cases must include **terminologically polysemous texts**—texts where identical Arabic terms carry school-specific technical meanings. FP-20 should mandate cross-school consistency checks and explicitly define hard cases as including "texts that are surface-clean but semantically school-dependent."

### FP-21 (Severity classes) — the isnād narrator as content, not metadata

A ḥadīth's isnād (حدثنا مسدد قال حدثنا يحيى عن شعبة عن قتادة...) is not mere metadata—it IS the scholarly content that determines authenticity classification. Many narrator names share consonantal skeletons distinguishable only by diacritics: **سَعِيد** (Saʿīd) vs. **سُعَيْد** (Suʿayd), **يحيى بن سعيد القطان** (a towering authority) vs. **يحيى بن سعيد الأنصاري** (a different narrator entirely). Research on automated isnād processing shows only ~94.6% accuracy on narrator disambiguation—meaning **5.4% of narrator identifications are wrong**.

Naive FP-21 classifies a narrator name error as "visible misplacement"—the excerpt is in the right topic category, the subject is correct, just a name in the chain is off. But in ḥadīth science, misidentifying a narrator **reverses authentication**. Confusing a weak narrator (ضعيف) with a trustworthy one (ثقة) of similar name means the KR user forms a wrong belief about a prophetic statement—the exact Knowledge Integrity Axiom violation the system exists to prevent.

**Required refinement:** FP-21 must include a **genre-sensitive severity map**. In ḥadīth: any isnād error is existential. In fiqh: misattributed school/scholar is existential. In naḥw: wrong school-specific term scope is existential. In tafsīr: misattributed Qurʾānic interpretation is existential. The "silent corruption" classification must expand based on genre-specific loci of scholarly authority.

### FP-22 (Anti-covert-excerpter) — dialectical fragmentation in fiqh khilāf

Classical fiqh khilāf texts follow a dialectical sequence: present Position A → evidence for A → present Position B → evidence for B → refute A's evidence → author's tarjīḥ (preference). The excerpter extracts Step 5 (refutation of A) and Step 6 (tarjīḥ favoring B). FP-22 says: don't reshape, just validate. The excerpt passes validation—it fits under "Topic X — Impermissibility."

But separately, Step 1 (presentation of Position A with its evidence) was also extracted and placed under "Topic X — Permissibility." The KR now contains **two contradictory excerpts from the same discussion**, both attributed to the same author, neither marked as part of a dialectical sequence. The author's actual position is encoded in the *relationship between arguments*, not in any single excerpt.

**Required refinement:** FP-22's "check, don't fix" must extend to "check *context*, don't fix *content*." When an excerpt contains dialectical terms (القول الأول, والجواب عن ذلك, والراجح) that reference arguments not present in the excerpt, Phase 3 must flag this as **incomplete dialectical context**. A tarjīḥ ("والراجح عندنا") without its alternatives present or referenced is decontextualized meaning—silent corruption under FP-21.

---

## Q2: What Codex CLI's structural analysis cannot catch

Codex validates form. Four specific failure patterns pass every structural check while carrying existential corruption:

**Schema-valid attribution inversion.** An excerpt attributed to Ibn Taymiyyah may contain text where he quotes al-Ghazālī for purposes of refutation. The JSON schema is perfect—author field correct, source book correct, page numbers match. But the content represents the *opposite* of the attributed author's position. No schema, type check, or contract can detect that extracted text represents a quoted opponent rather than the quoting author's own view. **None of the five FPs mandate semantic provenance verification**—checking own-position vs. quoted/refuted position.

**Conditional-to-absolute decontextualization.** A fiqh ruling "fasting is obligatory *for those who are able*" extracted without the condition produces an absolute obligation with no exceptions. Every data contract is satisfied: text exists in source, page reference valid, author valid, excerpt length within bounds. FP-19 partially addresses this (mark where cuts occurred), but marking a cut doesn't communicate that the omitted text contained a meaning-altering qualifier. **FP-21 should explicitly classify condition-stripping as existential silent corruption.**

**Inter-phase information loss.** Phase 1 normalization strips tashkeel. Phase 2 extraction operates on stripped text. Each phase's contracts only reference its own input—Phase 2's output is "correct" relative to Phase 1's output. But relative to the original source, disambiguation information has been destroyed. Research on Arabic tokenization confirms that "preserving Alif variants leads to lower language modeling loss... suggesting that Alif variants carry disambiguating information." **No proposed FP mandates end-to-end data lineage**—tracing output back to the *original source*, not just the immediate upstream phase.

**Hamza normalization as meaning destruction.** Normalizing أ, إ, آ → ا and ؤ → و collapses distinctions that matter: سَأَلَ (sa'ala, "he asked") becomes indistinguishable from سَالَ (sāla, "it flowed"); رُؤْيَة (ru'ya, "seeing") collapses into رُوِيَة (ruwiya, "it was narrated")—critical in ḥadīth science. The contract says "valid UTF-8 Arabic"; the normalization satisfies it while destroying meaning. **No FP addresses normalization policy**—which normalizations are safe for scholarly text vs. which destroy meaning.

---

## Q3: What Gemini CLI's scholarly analysis cannot catch

Gemini validates per-excerpt, per-science. Five system-level failure modes are invisible to this approach:

**Cross-engine contract violations.** Individually correct excerpts may violate the taxonomy engine's structural expectations downstream. An excerpt with a ḥadīth reference in prose form ("as narrated by Muslim") is valid fiqh—but the taxonomy engine may require structured ḥadīth metadata (book, chapter, number) for cross-indexing. Gemini validates producers without knowledge of consumers. **No proposed FP addresses cross-engine interface contracts.**

**Error accumulation across 2,500+ books.** A 2% error rate in topic boundary detection sounds acceptable per-excerpt. Across 250,000+ excerpts, that's **~5,000 incorrect topic boundaries**, clustering around ambiguous transitions—which are disproportionately the most important scholarly passages. FP-20 helps reduce per-excerpt error rates but **no FP defines corpus-level quality thresholds** or statistical monitoring.

**Taxonomy drift from processing order.** The taxonomy grows as books are processed. Book #500 gets finer-grained categorization than Book #1, even if they cover the same topic. If early books are predominantly from one school (madhhab), they dominate category definitions, biasing how later books from other schools are categorized. **No FP mandates processing-order invariance testing or re-categorization sweeps.**

**Self-referential corruption propagation.** If a corrupt excerpt becomes a reference example for processing subsequent books, the error is self-reinforcing: multiple "independent" excerpts now agree on the wrong attribution. FP-22 prevents validation from covering up errors but doesn't prevent corrupt output from becoming input. **No FP prohibits using system output as unverified input for subsequent extraction.**

**Inter-science relationship corruption.** A legal ruling paired with the wrong evidencing ḥadīth—because the actual evidence was on the previous page, split into a different excerpt—passes both fiqh validation and ḥadīth validation independently. The *relationship* between them is corrupt. **No FP addresses inter-science relationship integrity.**

---

## Q4: Redundancy is minimal but one genuine conflict exists

**FP-19 vs. existing source fidelity FPs: NOT redundant.** Source fidelity governs the accuracy of what IS extracted. FP-19 governs the visibility of what is NOT extracted. Every excerpt omits something by definition; FP-19 uniquely addresses the meta-level transparency of the excerpting act itself, targeting the "deceptive cleanliness" failure mode where non-contiguous passages are stitched together without marking the gap.

**FP-21 vs. strengthened FP-5: GENUINE CONFLICT requiring resolution.** FP-5 operates on binary logic: corruption detected → cascade → halt. FP-21 introduces a spectrum: existential vs. recoverable. If FP-21 classifies something as "visible misplacement" (recoverable), but FP-5 says any corruption triggers cascading trust collapse, **which principle governs?** This is not redundancy—it's a governance ambiguity that could either paralyze the system (everything triggers halt) or create a loophole (corruption rationalized as "just misplacement"). Resolution: FP-21 must be positioned as the *classification layer* and FP-5 as the *response layer*. FP-5's halt triggers only for FP-21's existential class. A "when in doubt, treat as existential" tiebreaker rule is mandatory.

**FP-22 vs. existing excerpt integrity FPs: NOT redundant.** Existing integrity FPs likely govern Phase 2 (extraction): "don't modify source text." FP-22 specifically targets Phase 3 (validation): the validation layer must check, not fix. The failure mode is second-order corruption—validation "fixing" a misattribution by fabricating correct metadata, which is worse than the original extraction error.

**Cross-proposal analysis: No duplicates.** FP-19 and FP-22 share a transparency theme but target different boundaries (content boundary vs. process boundary). FP-20 and FP-21 share a severity-awareness theme but target different aspects (test methodology vs. failure taxonomy). A system can comply with FP-19 while violating FP-22, and vice versa. The pairings are complementary, not redundant.

---

## Q5: Three existential-grade threats that none of the five FPs address

### Context-window silent truncation — the invisible input corruption

When a long Arabic scholarly text exceeds the LLM's context window, the input is silently truncated. The LLM produces output "as if it saw everything." This is **the ultimate silent corruption**: the system shows no error, the output looks plausible, the JSON schema validates perfectly, but the extraction is based on partial input. For multi-volume works common in Shamila (e.g., *al-Mughnī* at 15 volumes, *Fatḥ al-Bārī* at 13), context-window limits are not edge cases—they are the default processing condition.

None of the five FPs address this. The needed safeguard: when input exceeds context limits, the system must NOT silently truncate. It must chunk intelligently, track chunk boundaries explicitly, and never produce an excerpt that implies it processed text it didn't see.

### Model version drift — the ground shifting under every guarantee

If the LLM model used for extraction is updated between processing Book #1 and Book #2,500, the excerpting behavior changes silently. Same prompt, different output. Every content-level guarantee (source fidelity, omission honesty, severity classification) is built on the assumption of consistent processing behavior. **Model version drift invalidates this assumption without any detectable signal.** Research confirms this is a pervasive production problem: studies found 0 of 18 LLM-based systems achieved full reproducibility.

None of the five FPs address model versioning, pinning, or reproducibility. The needed safeguard: model versions must be pinned, recorded per-book, and changes must trigger re-validation of a representative sample.

### Prompt injection through source text — untrusted input treated as trusted

Shamila HTML exports may contain formatting artifacts, editorial annotations, or Unicode oddities that an LLM could interpret as instructions. Arabic scholarly texts also contain phrases that could function as prompt-injection vectors (e.g., editorial notes like "انتهى كلام المصنف وما يلي من إضافات المحقق" — "the author's text ends here; what follows is the editor's additions"). None of the five FPs address input sanitization or adversarial input resistance.

### Additional uncovered gaps

**Structural fidelity loss.** The MISSED-F8 findings likely include lost formatting that encoded meaning—indentation distinguishing matn from sharḥ from ḥāshiyah, تحقيق footnotes containing variant readings and manuscript sources. Dropping these collapses distinct scholarly voices into flat text. None of the five FPs address structural relationship preservation.

**Reporting honesty.** The NO DECEPTION principle (owner's notes lines 342-388) is partially covered by FP-19 and FP-22 at the content layer but completely uncovered at the metadata and system-reporting layers. If the engine reports "100% validated" while silently skipping sections that exceeded context limits, or reports "high confidence" on excerpts processed at the boundary of the context window, the system deceives the user about its own operations.

**Cross-reference preservation.** Arabic scholarly texts are densely self-referential ("كما ذكرنا في باب كذا" — "as we mentioned in the chapter on X"). When excerpting severs these references, the excerpt loses a critical semantic feature. The MISSED-F7 findings likely include lost within-book references. None of the five FPs explicitly address this.

---

## Consolidated recommendation: ITERATE

The five proposed FPs are **non-redundant, correctly targeted, and necessary**—but not sufficient. Before implementation:

**Must resolve before proceeding (blocking):**
- Reconcile the FP-5/FP-21 conflict with an explicit precedence rule: FP-21 classifies severity; FP-5's halt triggers only for FP-21's existential class
- Add error provenance classification to FP-5 (engine-introduced vs. source-inherited) to prevent false cascades on tashkeel ambiguity
- Add genre-sensitive severity maps to FP-21 (isnād errors in ḥadīth = existential, not recoverable)

**Must add before the batch is complete (high priority):**
- Add layer-aware omission markers to FP-19 (cuts across authorial boundaries must preserve layer-transition signals)
- Expand FP-20's "hard cases" to include terminologically polysemous texts, not just structurally complex ones
- Extend FP-22 to require dialectical context checking (flag excerpts containing tarjīḥ without alternatives)

**Must address as companion FPs (the batch covers less than half the safety surface):**
- **Infrastructure safety FP**: Model version pinning, context-window handling, non-determinism management. Without this, every content-level guarantee is built on sand.
- **Adversarial input resistance FP**: Source text is untrusted input from Shamila exports.
- **Reporting honesty FP**: Extend the NO DECEPTION principle to metadata, confidence scores, and processing reports.
- **Corpus-level quality monitoring**: Statistical thresholds on aggregate error rates, not just per-excerpt validation.

The proposed five principles represent genuine progress in KR's safety posture. But the adversarial review reveals that **the most dangerous failure modes live at the boundaries**—between pipeline phases, between engines, between Islamic sciences, between model versions—and the current batch focuses almost entirely on within-excerpt, within-phase safety. The next iteration must lift the safety perimeter to the system level.