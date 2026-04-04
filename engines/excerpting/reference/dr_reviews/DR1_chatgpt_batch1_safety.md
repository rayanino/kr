# Adversarial Review of Proposed Foundational Principles for KR Excerpting Safety & Integrity Batch

## Evidence base and limitations

The current `engines/excerpting/SPEC.md` on `rayanino/kr` appears to be a full engine specification (v2.0.0, 2026-03-23) emphasizing knowledge-integrity threats (e.g., silent text corruption, context loss, attribution error), immutability of extracted text, and loud failure modes. fileciteturn2file0L1-L1

However, the files you specified as primary for this review were not retrievable at the given paths in the repo snapshot accessible through the GitHub connector:

- `engines/excerpting/reference/CRITICAL_ATOMS_NONNEGOTIABLES_AND_REDTEAM.md` (404 at that path)
- `engines/excerpting/reference/QUEUE_AUDIT_RAW_VS_EXTRACTION.md` (not found)
- `engines/excerpting/f1-owner-original-notes.txt` (not found)

That missing material matters because it likely contains (a) the exact “F7 Non-Negotiables / Red-Team Tests” surface you want to defend, and (b) the specific “missed” items you want to ensure the proposed FPs address. I therefore grounded this adversarial review in the strongest available adjacent authorities found in-repo:

- The excerpting engine spec emphasizing immutability, threat model, and limits of deterministic verification. fileciteturn2file0L1-L1  
- The historical gold-standard manual extraction protocol, which contains explicit “forbidden” transformations and integrity rules (verbatim capture; no correction/normalization; evidence not relegated to context; explicit provenance artifacts). fileciteturn43file0L1-L1  
- The archived ABD excerpting spec, which explicitly frames decontextualization as the most dangerous excerpting error and illustrates multi-layer attribution risks. fileciteturn23file0L1-L1  
- The repo note clarifying that certain ABD-era “precision rules and gold baselines” folders are binding authority when stage specs conflict (useful as an integrity escalation signal). fileciteturn17file0L1-L1  
- A coworker report labeled as a “Gemini” adversarial evaluation of deterministic severity triage in an Arabic pipeline. I treat it as suggestive internal reasoning rather than external fact, because it contains many claims that are not independently verified inside this repo snapshot. fileciteturn44file0L1-L1  

Given those constraints, the redundancy analysis against “FP‑1…FP‑18 in §1.1b” is necessarily approximate: I compare your proposed five principles primarily against the *effective* principles already enforced via (a) immutability guarantees, (b) the threat taxonomy, (c) “fail-loud” error design, and (d) the manual gold-standard protocol rules. fileciteturn2file0L1-L1 fileciteturn43file0L1-L1

## Strengthen FP-5: Cascading trust collapse and stop-using threshold

### What this principle is trying to prevent

Your proposed strengthening makes explicit a meta-fact the excerpting SPEC already states in plain language: excerpt output is epistemic input (“every excerpt becomes a belief”). fileciteturn2file0L1-L1 The FP‑5 change seems aimed at turning “integrity risk” into an operational policy: once corruption is confirmed, downstream trust collapses, so the correct behavior is “halt and quarantine,” not “continue with warnings.”

This direction is structurally aligned with the excerpting spec’s existing stance that some failures are worse than stopping (e.g., when uncertainty becomes invisible). fileciteturn2file0L1-L1

### Failure scenario that looks correct but becomes catastrophically wrong if implemented naively

The core ambiguity is **what counts as “confirmed corruption.”** If “confirmed” is defined loosely as “any mismatch or any warning,” the stop-using threshold becomes a denial-of-service lever in normal Arabic processing.

A concrete, plausible instance in the current excerpting design is offset alignment fallback behavior: the spec allows a warning path where snippet alignment succeeds only after diacritic-stripping (because an LLM may not copy diacritics perfectly). fileciteturn2file0L1-L1 If FP‑5 naively treats *any* diacritic mismatch as “confirmed corruption → halt,” then a single “benign” LLM transcription quirk stops processing across sources, even though the extracted text may still be faithful (the anchor search is only for alignment), and the system already designed this case as monitorable, not fatal. fileciteturn2file0L1-L1

That failure looks “correct” under a purity lens (“we detected mismatch; we stopped”), but it is catastrophically wrong operationally: it converts a *recoverable* alignment robustness measure into a pipeline-wide kill switch that can be triggered by normal model behavior, not source corruption.

### What Codex-style structural/contract analysis likely misses here

Structural analysis can tell you whether:
- invariants exist,
- contracts are enforced,
- tests execute error-code paths,

…but it cannot soundly decide whether a given anomaly should trigger **global trust collapse vs localized quarantine**, because that decision depends on epistemic impact and downstream propagation, not type signatures. The excerpting spec itself admits that some of the most dangerous failures (decontextualization rules) are not deterministically verifiable, because they depend on Arabic semantic understanding. fileciteturn2file0L1-L1

So a Codex CLI can “prove” that the code halts on error, while missing the essential question: “Does the halt boundary align with *confirmed* corruption, or does it halt on noisy signals?”

### What Gemini-style scholarly/Arabic analysis likely misses here

A per-text “scholarly correctness” analysis can still miss system-level trust collapse failures because:
- catastrophic impact can be in the *provenance chain* (quietly corrupted stored text or offsets), even if each excerpt still “reads plausible,”
- the harm is often cumulative and only visible at library scale (systemic drift in diacritics, systematic omission patterns, or silent misalignment). fileciteturn2file0L1-L1

The internal adversarial report’s central critique—“deterministic severity mappings misclassify catastrophic Arabic text corruption vectors as low severity because they look like string manipulation”—is a version of this point (system impact is downstream). fileciteturn44file0L1-L1 Even if I discount its specifics, the shape of the risk is real for excerpting: a small manipulation in a normalization/canonicalization step can poison the entire knowledge base.

### Redundancy check

FP‑5 (as strengthened) is **partially redundant** with protections already present:

- The spec’s “immutability” posture (no “cleanup,” no post-extraction modification) already encodes the idea that text corruption is existential. fileciteturn2file0L1-L1  
- The error-handling philosophy “every error is loud; no silent data loss” is already a trust-preserving stance. fileciteturn2file0L1-L1  

What is *not* redundant is the explicit “stop-using threshold” governance layer (“confirmed corruption means halt *use* of already-produced outputs,” not just “halt production of a bad excerpt”).

### Bottleneck-first recommendation for FP-5

To avoid turning FP‑5 into a denial-of-service trap, FP‑5 needs an explicit **two-tier definition**:

- **Confirmed corruption (hard stop + quarantine + invalidate downstream)** should be restricted to *deterministic, source-faithfulness breaking* violations, e.g.:
  - extracted `primary_text` cannot be proven to be a substring of the frozen source representation,
  - “primary text integrity” checks fail,
  - offsets produce mismatched snippets in a way that indicates wrong extraction (not just diacritic mismatch at the anchor-search stage). fileciteturn2file0L1-L1  

- **Suspected corruption (continue with flags; block owner consumption)** should cover noisy signals and semantic risks where determinism cannot adjudicate, e.g. suspected decontextualization, unresolved “كما تقدم” chains, ambiguous attributions. fileciteturn2file0L1-L1

If you cannot define “confirmed corruption” with deterministic triggers, FP‑5 becomes an “aspirational moral rule” rather than an implementable safety control—exactly the kind of principle automated review tools will falsely “check off” without providing real protection.

## New FP-19: Omission honesty

### What this principle is trying to prevent

This targets a specific deception mode: the engine produces an excerpt that *looks* like uninterrupted source flow, while it is actually stitched or cut. You called this “deceptive cleanliness.”

This dovetails strongly with two existing authorities:

- The excerpting spec’s insistence that `primary_text` is extracted verbatim and is never “cleaned up” after extraction (immutability). fileciteturn2file0L1-L1  
- The gold protocol’s explicit “forbidden transformations” (no spelling correction, no diacritic change, no editorial insertion, no reordering). fileciteturn43file0L1-L1  

So FP‑19 is directionally consistent with the project’s core integrity posture.

### Failure scenario that looks correct but is catastrophically wrong if implemented naively

A naive implementation of FP‑19 will try to “make omissions visible” by **inserting ellipses or cut markers into the excerpt text itself.** That turns omission honesty into textual alteration—exactly what the spec and gold protocol forbid. fileciteturn2file0L1-L1 fileciteturn43file0L1-L1

Concrete Arabic example using a real scholarly locus:

- In the archived spec, the *matn* line from entity["people","Ibn Malik","arabic grammarian d 672"] is given as: **«كلامُنا لفظٌ مفيدٌ كاستقم»**, and the sharḥ line from entity["people","Ibn Aqil","arabic grammarian d 769"] begins: **«يريد أن الكلام في اصطلاح النحويين…»** fileciteturn23file0L1-L1  

If FP‑19 is implemented by inserting “…”, brackets, or join-markers directly into `primary_text`, three catastrophic outcomes can occur while still “looking honest”:

1. **You violate immutability and corrupt the text layer.** The system now stores an excerpt that never existed in the source, contradicting “verbatim text” constraints. fileciteturn2file0L1-L1  
2. **You introduce authorship deception.** An ellipsis between matn and sharḥ can read like a single author’s continuous prose unless the UI also surfaces layer attribution; the result “looks clean” but is epistemically wrong (the user may attribute commentary content to the matn author, or read the matn as having prose continuity). Multi-layer attribution is already flagged as a top-risk integrity concern. fileciteturn2file0L1-L1 fileciteturn23file0L1-L1  
3. **You mis-handle sacred quotations.** If cuts occur inside a Qur’anic citation, inserting ellipses into the cited text creates a “modified quotation of ​entity["book","Qur'an","islamic scripture"].” Even if your UI marks it as an omission marker, you have now stored and displayed a mutated string that can be copied downstream (into synthesis, citations, or user notes). The spec is explicit that diacritics/Unicode changes can invert meaning and that the engine must not modify the text post-extraction. fileciteturn2file0L1-L1  

This is exactly the class of failure that “looks correct” (visible omission markers = “honest”) but is catastrophically wrong (you committed text corruption under the banner of honesty).

### What Codex-style structural analysis likely misses here

Codex can verify “a cut marker is inserted” or “a field exists,” but it will not catch whether your implementation violates the *higher-order invariant* “text the owner reads is exactly the text the source contains.” fileciteturn2file0L1-L1

If the interface uses the same field for storage and display, structural tests may pass while you have silently introduced a data-integrity regression that is only visible to a domain reader comparing against source text.

### What Gemini-style scholarly/Arabic analysis likely misses here

Gemini can read the resulting excerpt and find it linguistically coherent and even pedagogically improved—especially if ellipses are placed “sensibly.” But FP‑19’s target is not linguistic coherence; it is **provenance truthfulness**.

A per-science correctness check cannot reliably detect “hidden cuts” unless the evaluator has the *source text* and a strong “diff lens.” If the excerpt is internally coherent, a scholarly check will often approve it—even though the excerpt is a stitched artifact that violates KR’s immutability contract.

### Redundancy check

FP‑19 overlaps strongly with existing non-negotiables implied by:

- “primary_text immutability / no cleanup.” fileciteturn2file0L1-L1  
- the gold protocol’s “forbidden: editorial insertions, reordering, correction.” fileciteturn43file0L1-L1  

It is not redundant if it adds one missing guarantee: a structured way to surface “this excerpt is discontinuous / stitched” **without altering the stored Arabic.**

### Bottleneck-first recommendation for FP-19

FP‑19 should be implemented as a **display-layer + provenance-layer** rule, not a text mutation rule:

- Keep `primary_text` immutable.
- Add an explicit `source_spans` / `extraction_spans` structure (or reuse existing provenance objects) so the UI can render visible cut markers **outside** the canonical text.
- Require that any discontinuity also renders *authorship/layer transitions* prominently, otherwise FP‑19 ironically increases misattribution risk (it makes stitching “look deliberate and safe”).

If the system cannot represent discontinuity without corrupting `primary_text`, then FP‑19 should **block** the feature “non-contiguous excerpt assembly” entirely (force contiguity), rather than attempting to paper over it with ellipses.

## New FP-20: Validation rigor

### What this principle is trying to prevent

FP‑20 is explicitly fighting “demo-safety”: tests that only cover polished examples and miss real-world hard cases (ambiguous boundaries, intertwined topics, long debates).

This is already strongly aligned with the excerpting spec’s existing testing philosophy: it explicitly rejects “happy path only” tests and mandates adversarial cases. fileciteturn2file0L1-L1 The gold protocol similarly emphasizes iterative human checkpoints and validation artifacts, not just “it ran.” fileciteturn43file0L1-L1

### Adversarial failure mode if implemented naively

The naïve implementation trap is: **“hard case” becomes “un-ground-truthable case.”** If your “hard cases” are long intertwined debates with no crisp objective boundaries, you can build a test suite that is impressive-looking but epistemically empty.

Excerpt boundaries are *sometimes* intrinsically underdetermined; the spec itself indicates calibration boundaries (e.g., PARTIAL vs DEPENDENT) must be empirically tuned during probes. fileciteturn2file0L1-L1 If FP‑20 produces tests where correctness is “whatever the model says,” then you have only shifted the problem to test selection.

### What Codex-style structural analysis likely misses here

Codex can confirm that:
- tests exist,
- fixtures exist,
- coverage hits code paths,

…but cannot tell whether your test set is *adversarial in the right ways*. Structural signals (line coverage, schema validation) don’t measure:
- semantic decontextualization risk,
- multi-layer attribution correctness,
- scholarly completeness of arguments. fileciteturn2file0L1-L1  

The excerpting spec explicitly states that decontextualization prevention patterns are not independently verifiable by deterministic checks because they depend on Arabic semantic understanding. fileciteturn2file0L1-L1 So “structural coverage is high” can coexist with “the most dangerous error still slips through.”

### What Gemini-style scholarly/Arabic analysis likely misses here

Gemini can judge whether a particular excerpt correctly reflects fiqh/nahw/usul logic. What it cannot see—unless prompted explicitly—is whether the *evaluation set is structurally biased* toward easy patterns, or whether “correctness” is being judged after-the-fact on already excerpted outputs (confirming the model’s own boundary choices).

A system-level failure that per-science review won’t catch is **cross-case overfitting**: prompts and validators tuned to perform well on curated hard cases may degrade performance on ordinary text, producing a net increase in silent corruption volume.

### Redundancy check

FP‑20 is **largely redundant** with the spec’s existing explicit test posture: tests must cover adversarial cases, not just happy paths. fileciteturn2file0L1-L1 Its value would be in sharpening the definition of “hard cases” into an explicit, named battery (so it can’t be satisfied by token “edge case” tests).

### Bottleneck-first recommendation for FP-20

Define a **minimal hard-case battery** that is objectively testable and maps to known corruption risks (not “interesting debates”):

- reported position + refutation (decontextualization),
- implicit references (“كما تقدم / المذكور”) that require cross-reference metadata,
- multi-layer matn/sharḥ/hashiyah overlaps with ambiguous dominance,
- enumerated arguments (“الأول… الثاني…”) where truncation is detectable,
- long passages with repeated structural templates (where segmenters drift). fileciteturn2file0L1-L1 fileciteturn23file0L1-L1  

Those can be made into fixtures with clear expected properties even if boundaries are not uniquely defined.

## New FP-21: Severity class distinction

### What this principle is trying to prevent

FP‑21 wants to separate:
- “silent corruption” (existential) vs
- “visible misplacement” (serious but recoverable),

and track them separately.

This corresponds cleanly to the excerpting spec’s threat framing (e.g., silent text corruption and context loss vs taxonomic misplacement). fileciteturn2file0L1-L1

### Adversarial failure mode if implemented naively

The dangerous naive assumption is: **visible = recoverable.** In a knowledge system, many “visible” issues are operationally invisible at the point of consumption:

- If a user trusts the taxonomy tree and studies what appears under a node without cross-checking provenance, misplacement behaves like silent corruption in practice.
- If synthesis consumes mis-placed excerpts, the resulting entry may state false generalizations even if the raw excerpt text is fine.

So severity should be defined by **visibility to the user and downstream engines**, not by whether an engineer can “see the bug” in logs.

### What Codex CLI likely misses

Codex can support the creation of separate counters, error codes, and logging categories. What it cannot do is decide the epistemic severity class for a given defect, because that depends on *who sees it, when, and how it propagates*—a system-level question.

The spec’s own threat model makes this clear: different threats have different mitigations and different downstream consumers. fileciteturn2file0L1-L1

### What Gemini CLI likely misses

A scholarly reviewer may see the text is correct and conclude severity is low, overlooking that the excerpt is placed in the wrong concept leaf and will therefore be studied as evidence for the wrong proposition.

Per-science correctness is not the same thing as **epistemic routing correctness**.

### Redundancy check

FP‑21 is partially redundant with the spec’s explicit split between:
- text integrity threats,
- context loss threats,
- taxonomy misplacement delegated downstream. fileciteturn2file0L1-L1

But FP‑21 adds operational value if it forces reporting and gating to mirror the epistemic harm asymmetry (a small amount of silent corruption must dominate a large amount of visible nuisance in prioritization).

### Bottleneck-first recommendation for FP-21

Make the distinction **actionable**, not cosmetic:

- Silent corruption category must be able to trigger FP‑5 quarantine/stop‑use.
- Visible misplacement must still be treated as potentially epistemically silent unless the UI guarantees it is surfaced to the reader before study (e.g., “uncertain placement” banners, obvious provenance links).

Without a clear mapping from severity class → action, FP‑21 risks becoming a bookkeeping principle.

## New FP-22: Anti-covert-excerpter

### What this principle is trying to prevent

This is a governance boundary: **excerpting must not be covertly rewritten to match the taxonomy**, especially during validation/Phase 3.

The excerpting spec already takes a strong position in this direction by removing taxonomy leaf proposals from excerpting and instead producing topic keywords for the taxonomy engine to map. fileciteturn2file0L1-L1

### Failure scenario that looks correct but is catastrophically wrong if implemented naively

The naive implementation trap is focusing on “Phase 3 must never reshape excerpts,” while missing the actual covert excerpter attack surface: earlier phases or downstream engines.

Concrete scholarly pattern:

- A fiqh discussion may include a *rejected* position followed by the author’s refutation and tarjīḥ. If taxonomy wants a “clean leaf” of “الراجح” only, a covert excerpter might drop the rejected position and keep only the preferred ruling, producing a beautiful, clean “fact.”  
- That *looks correct* because the conclusion is correct.
- But it is catastrophically wrong because it alters what the scholar taught: it removes the dialogue completeness and the reasons the author rejected the rival view (which is core knowledge in fiqh methodology). The excerpting spec treats this decontextualization risk as the highest-risk failure mode. fileciteturn2file0L1-L1 fileciteturn23file0L1-L1  

If FP‑22 is enforced only in Phase 3, but Phase 2 grouping is subtly tuned to align with taxonomy (e.g., by including taxonomy context in prompts), you can still get a covert-excerpter outcome while “passing” FP‑22.

### What Codex CLI likely misses

Codex can verify “Phase 3 doesn’t change `primary_text`.” It cannot detect taxonomy-shaped boundary decisions if:
- the LLM prompt contains taxonomy information,
- validators prefer outputs that match the taxonomy tree shape,
- or downstream synthesis selects only the parts that “fit.”

Those are semantic and cross-component effects not captured by local contracts.

### What Gemini CLI likely misses

A scholarly correctness pass may approve the resulting excerpt because the remaining content is orthodox and coherent. But FP‑22 is protecting the knowledge system against *epistemic laundering*: turning a complex debated discourse into a decontextualized “clean” claim.

Per-science review frequently judges “is the content correct,” not “is the excerpt faithful to the author’s argumentative structure.”

### Redundancy check

FP‑22 overlaps with:
- FP‑19 (both are anti-deception, anti-cleanliness), and
- existing excerpting policy: excerpting produces topic keywords, not taxonomy placement. fileciteturn2file0L1-L1  

Its unique value is to explicitly prohibit “taxonomy-driven reshaping”—but it must be broadened beyond “Phase 3 validation” to cover the real attack surface.

### Bottleneck-first recommendation for FP-22

Make the invariant cross-engine:

- Excerpting: never change `primary_text` after extraction.
- Taxonomy: never change excerpt boundaries/text, only placement.
- Synthesis: if it summarizes or excludes portions, it must label those outputs as synthesis, not as source-grounded excerpts.

Otherwise FP‑22 is too narrow to stop the actual covert reshaping that can happen later.

## Recommendation and batch disposition

**ITERATE** (not PROCEED, not BLOCK).

The proposed principles are directionally correct, but as currently phrased they are vulnerable to “paper compliance” (easy to add as slogans, hard to enforce safely) unless you tighten definitions and explicitly reconcile them with existing immutability and provenance constraints.

The single best next move for this batch is to convert each proposed FP into a **testable operational contract** (with an action mapping), prioritizing two definitions that currently look under-specified and are therefore likely to fail adversarially:

- **FP‑5:** define “confirmed corruption” as a closed set of deterministic faithfulness violations (not warnings, not heuristics), and define quarantine/stop‑use actions at *library* scope. fileciteturn2file0L1-L1  
- **FP‑19:** require omission visibility **without mutating stored Arabic text**; enforce via provenance spans and UI rendering, and treat author/layer transitions as first-class honesty signals (otherwise omissions become a new misattribution channel). fileciteturn2file0L1-L1 fileciteturn43file0L1-L1  

### The uncovered safety concern most likely missing from these five FPs

Because the owner’s `f1-owner-original-notes.txt` could not be located in this repo snapshot, I cannot quote the exact threat-detection items you referenced. But based on the strongest available adjacent authority (gold protocol + “no silent data loss” philosophy), the most likely unaddressed category is:

- **End-to-end provenance + tamper-evident auditability as a first-class safety control** (not just “be honest”): cryptographic hashes of source slices, reproducible reconstruction of `primary_text` from frozen inputs, and explicit “diff against source” tooling as part of gates. The gold protocol’s emphasis on checkpoint artifacts and validation outputs suggests the project already treats “audit trail as safety” in the manual workflow. fileciteturn43file0L1-L1  

None of the five proposed FPs directly enforces “tamper-evident provenance for every excerpt” as an invariant—yet that is the constraint that makes FP‑19 and FP‑5 enforceable without relying on subjective judgments.