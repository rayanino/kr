# Adversarial Review of Excerpting Foundations Hardening Batches 1 and 2

## Scope and primary artifacts reviewed

This review is based on the repo branch `excerpting-foundations-hardening-20260404` and the following artifacts:

- `engines/excerpting/SPEC.md` §1.1b, focusing on FP-19 through FP-22 and the strengthened FP-2/FP-5 language. fileciteturn6file0L1-L1  
- `engines/excerpting/reference/MERGED_ATOM_QUEUE.md`, Sections D (Batch 1) and E (Batch 2). fileciteturn7file0L1-L1  
- `engines/excerpting/src/phase2_group.py`, specifically the `GROUP_SYSTEM_PROMPT` region (your Batch 2 prompt additions A–D are already present in this branch). fileciteturn8file0L1-L1  
- The owner’s raw F1 notes (as present in this branch under `engines/excerpting/chatgpt_f1_collection/source_artifacts/f1_owner_original_notes_2026_04_03.txt`). fileciteturn13file0L1-L1  
- `engines/excerpting/reference/QUEUE_AUDIT_RAW_VS_EXTRACTION.md` documenting the 124 “gaps” (what got missed/softened/distorted relative to raw owner intent and why that matters). fileciteturn15file0L1-L1  
- `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md`, especially the “BATCH 1: Safety & Integrity” section containing the Codex + Gemini coworker findings used for hardening. fileciteturn14file0L1-L1  

## Batch 1 safety and integrity

Batch 1 is framed (in your MAQ) as “trust poisoning, silent failures, deceptive cleanliness, corruption prevention, severity classification” and includes the launch of FP-19 to FP-22 plus strengthening FP-2 and FP-5. fileciteturn7file0L1-L1  

The ledger’s summary indicates the following were implemented in `SPEC.md` §1.1b:

- **FP-2 strengthened** with an explicit “anti-rescue prohibition” and clearer separation of “source-preserving context” vs “help layers” that must sit beside rather than overwrite. fileciteturn6file0L1-L1  
- **FP-5 strengthened** with a “cascading trust collapse / blast radius” orientation (wrong excerpt → whole book suspect → engine suspect → knowledge base suspect) and the requirement for blast-radius assessment after confirmed errors. fileciteturn6file0L1-L1  
- **FP-19** (omission honesty / anti-deceptive cleanliness), **FP-20** (validation rigor), **FP-21** (severity class distinction: silent corruption vs visible flagged failure), **FP-22** (anti‑covert‑excerpter: validator must not reshape excerpts for tree-fit). fileciteturn6file0L1-L1  
- Codex and Gemini both “confirmed” these changes, with Codex narrowing FP‑22 to avoid breaking an existing validator behavior and deferring contract-level enforcement of FP‑19. fileciteturn14file0L1-L1  

### Missing failure scenario that Codex and Gemini did not surface

Codex and Gemini strongly focus on *textual* corruption modes (hidden omission, wrong speaker-role, validator reshaping) and on ensuring hard adversarial fixtures exist. fileciteturn14file0L1-L1  

The highest-impact scenario I do **not** see explicitly named in their Batch 1 notes is:

**Flag laundering via operational workflow (“visible” failures becoming de facto silent).**

Concretely:

- FP‑21’s safety model relies on a critical assumption: **“visible flagged failure” is recoverable** because the user or system sees the flag and investigates. fileciteturn6file0L1-L1  
- In practice, “visible” is only recoverable if (a) flags are *consistently surfaced at study time*, and (b) there is a *hard gate* or strong forcing function that prevents “studying anyway.” This assumption is **not stable** under load: the system will produce flagged objects at scale (PARTIAL/DEPENDENT, review flags), and the owner’s stated goal is explicitly “my only worry should be memorizing,” not adjudicating pipeline uncertainty. fileciteturn13file0L1-L1  
- Once flagged volume is high (or flags are too often “false alarms”), the human behavior pattern becomes predictable: **ignore flags** (alarm fatigue), or treat flagged outputs as “good enough.” At that moment, FP‑21’s “visible flagged failure” class collapses into effective “silent corruption,” because the library is being used as if unflagged. This breaks the intended safety partition even if the engine is technically “failing loud.” The queue audit underscores how easily urgency gets softened/normalized in translation and why intensity/priority signals matter; that same softening dynamic applies to flags at scale. fileciteturn15file0L1-L1  

Why this matters adversarially:

- A system that generates many flagged items can **appear safer** (lots of warnings), yet be **less safe** if it induces habituation.  
- This is a failure mode that slips past both “contract guardian” and “scholarly auditor” mindsets because it is **behavioral + operational**, not purely semantic or contract-level.

Minimal mitigation that fits Batch 1’s intent (without architecture sprawl):

- Introduce an explicit “no-study surface” rule: anything meeting the *highest-risk flag criteria* must not appear in the owner’s default studying view until resolved. This is consistent with FP‑5’s blast‑radius philosophy (contain first), and aligns with owner intent that “pipeline correctness should not be my concern.” fileciteturn6file0L1-L1  
- Add an explicit **“flag budget”** operational invariant: if flagged‑rate exceeds a threshold per run (e.g., too many DEPENDENT or too many “verification_skipped”), the run must stop + request engineering attention, because risk has shifted from “recoverable visible” to “user-normalizes ignoring.” This is philosophically consistent with MAQ’s “blast-radius containment requirement.” fileciteturn7file0L1-L1  

This scenario is not a request to add UI features; it is a *safety contract about user-facing exposure*, which is squarely Batch‑1‑aligned.

## Batch 2 self-containment prompt additions A–D

Batch 2 is framed as “self-containment” with proposed prompt additions: (A) anti-surface classification, (B) forgiving retention, (C) title retention asymmetry, (D) dependency-first splits. fileciteturn7file0L1-L1  

Two important grounding facts from this branch:

- The ledger records Batch 2 prompt additions as **implemented in prompt** (and some also in SPEC), though still “preliminary.” fileciteturn14file0L1-L1  
- The `GROUP_SYSTEM_PROMPT` currently already contains A–D verbatim (the rules are present as “ANTI-SURFACE CLASSIFICATION,” “FORGIVING RETENTION,” “TITLE RETENTION,” and “DEPENDENCY-FIRST SPLITS”). fileciteturn8file0L1-L1  

Given your adversarial task is about failure if rules get applied “too aggressively” or “exploited,” I treat these as *behavioral attack surfaces*, regardless of whether they are “proposed” vs “already staged.”

### Over-aggressive rule A anti-surface classification

**Rule intent:** prevent naive heuristics (“starts with مقدمة / اعلم / الأصل → introduction filler”) from causing the model to treat function as “intro” when it’s actually carrying rulings/definitions/evidence. fileciteturn8file0L1-L1  

**Failure mode if applied too aggressively:** the model **refuses to classify anything as introduction/structural transition** (or treats “intro” as a forbidden concept), so it over-ascribes “core function” everywhere.

In this architecture, even though grouping is “post-classification,” this failure still shows up in at least four ways:

- **Structural transitions stop being treated as boundaries.** If headings, basmala, “باب/فصل” markers, and genuinely framing-only prefaces are treated as substantive content (rule_statement/definition/etc.), they get glued into teaching units as “core.” That directly increases *unit breadth* and harms “one distinct concept” isolation. fileciteturn8file0L1-L1  
- **Function mixing inflates systematically.** The model becomes reluctant to say “this segment is basically structural” and will instead classify it as one of the substantive scholarly functions, increasing secondary functions and weakening granularity discipline. That creates downstream pressure: either (a) you accept larger mixed units, or (b) you split more aggressively elsewhere, increasing the risk of orphaned dependencies (exactly what Batch 2 is trying to prevent). fileciteturn8file0L1-L1  
- **Chapter-intro vs full-topic-intro confusion gets worse, not better.** A key owner concern is distinguishing a chapter-scoped intro from a true “topic leaf” introduction (reading a partial-source intro as if it defined the entire subject is harmful). The queue emphasizes this as a real danger; if rule A collapses “intro” as a valid function classification, you lose an important discriminatory dimension, which can create systematic misplacement into topic leafs (even before taxonomy placement). fileciteturn7file0L1-L1  
- **Model rationalizes away legitimate framing-only segments.** Many classical texts contain real prefatory material: praise, methodology, scope, definition of terms for the chapter, “we will now discuss…” signposts. Some of these are substantive, some are genuinely structural. Over-aggressive anti-surface pushes the model into a one-way decision: “it must be substantive.” That is a systematic bias.

**Adversarial exploit angle:** a weak model can use rule A as a “get out of jail free” card to avoid making hard calls about “what is this doing?” It can say “it might contain rulings” and then keep it merged, causing under-segmentation.

**Mitigation that preserves the intent of rule A:**

- Reframe rule A from “don’t classify as intro” to “**never drop/discount** because it looks like intro.” I.e., allow “structural_transition” as a classification when warranted, but forbid treating it as “safe to ignore.” This matches the MAQ framing (“don’t classify by appearance”) without making “intro” taboo. fileciteturn7file0L1-L1  
- Add a *positive* counterbalance sentence: “Some introductions are genuinely structural; when so, keep them as structural_transition and group as either standalone marker or attached framing, but do not mis-label substantive content as structural.” This reduces one-sided bias.

### Exploiting rule B forgiving retention

**Rule intent:** avoid creating unsafe orphaned fragments by not splitting in a way that causes the next unit to start with causal continuations like “لأن / فإن” without their antecedent, which is a direct self-containment hazard. fileciteturn8file0L1-L1  

**Failure mode if exploited:** the model “always keeps carryover, never splits.”

There are two exploit styles:

- **Always-merge exploit:** The model argues that any split risks starting the next unit with a dependency (causal continuation, pronoun, demonstrative). It therefore keeps stitching, producing very large units, “resolving” self-containment by swallowing context rather than doing precise segmentation. This is functionally equivalent to refusing the excerpting problem.  
- **Percent-threshold evasion exploit:** Your rule uses “≤15% of the unit,” but the model can avoid measuring and simply assert that the carryover is “small,” repeatedly. Over many boundaries, “small” accumulates, and the unit becomes structurally huge.

Downstream harms:

- **Granularity collapse and study experience regression.** A core owner requirement is high granulation without sending the user on manhunts; exploitation of B produces the opposite: a broad, mixed unit that is self-contained mainly because it hoards context. This undermines the “open a leaf and see one exact thing” vision. fileciteturn13file0L1-L1  
- **False confidence through apparent coherence.** These units can still score `FULL` self-containment because dependencies resolve internally. But the “one distinct concept/ruling/argument” property fails, and the unit becomes a “garbage drawer” that is easy to read but hard to study (the owner’s nightmare: thinking he’s building connections inside one leaf while some text belongs elsewhere). fileciteturn13file0L1-L1  
- **Rule B becomes a covert “merge permission” rather than a narrow exception.** That’s precisely the “blunt heuristic” anti-pattern the owner calls out (encountered pattern → enforce protocol) except inverted (encountered dependency risk → never split). fileciteturn13file0L1-L1  

**Mitigation: move the “≤15%” from a prompt suggestion to an enforceable post-check.**

The key leverage is that this pipeline already has deterministic access to:

- segment word ranges
- unit segment indices
- segment functions per unit

So you can compute, deterministically, for every unit:

- word-count by function inside the unit
- minority-function ratio

If you compute something like “secondary_function_word_ratio,” you can enforce:

- If a unit mixes functions and the minority function is >15% (or >X tokens), then the unit is not allowed to call itself “forgiving retention”; it must either:
  - split, or
  - mark self_containment lower + push to gate/review (depending on your desired strictness).

This directly addresses exploitability: it doesn’t matter what the model claims; the measured ratio governs.

**Also add a non-accumulation rule:** forgiving retention may be applied *at most once per boundary neighborhood* (e.g., it cannot be chained across >1 consecutive boundary). The model can still propose such chains, but deterministic checks can detect “carryover kept repeatedly” by counting how often a unit begins with (or includes) bridging content from a different prior function.

## Redundancy analysis across A–D vs existing rules

This is specifically about whether A–D add new decision constraints, or whether they simply restate existing constraints already present in prompt/SPEC.

### Anti-surface classification

- The prompt already has a general instruction to “analyze scholarly FUNCTION,” and the entire pipeline is function-driven. However, MAQ explicitly calls out “surface appearance must not override actual function analysis” as a distinct owner directive, meaning it is not redundant as *a reminder in the highest-salience part of the prompt*. fileciteturn7file0L1-L1  
- That said, in the current implementation it is inserted into the grouping prompt as a “classification” admonition; this is *structurally redundant* (grouping is post-classification), but still behaviorally impactful because the grouper assigns `primary_function` and decides how to treat “structural_transition” segments. fileciteturn8file0L1-L1  

Net: not conceptually redundant, but possibly misplaced; it may belong in the Phase 2a classify prompt more than Phase 2b.

### Forgiving retention

- The prompt already warns about dangling references and explicitly lists “opening conjunctions (لأن/فإن)” in self-containment evaluation criteria (C‑SC‑2). fileciteturn8file0L1-L1  
- But rule B is not merely “detect dependency”; it gives an *action policy*: prefer retaining a small carryover rather than splitting to a “because” start even when function mixing results. That is not otherwise encoded.

Net: not redundant; it changes the decision outcome, not just awareness.

### Title retention asymmetry

- C‑SC‑2 already references demonstratives like “هذا/هذه” and explicitly mentions demonstrative references in general; but it does not say “retain chapter title *inside* the unit when demonstratives depend on it,” and it definitely does not cover the “semantic anchor” case where the title is jurisprudential content even without a grammatical link (Bukhari tarajim pattern). fileciteturn8file0L1-L1  

Net: not redundant.

### Dependency-first splits

- There are already strong bundling rules: “question + answer must stay together,” “position + refutation must stay together,” “qualifiers must stay with the statement,” etc. fileciteturn8file0L1-L1  
- Rule D’s unique content is a **general method**: always ask “what question does this segment answer?” before any split. That can reduce reliance on brittle marker heuristics. The owner explicitly calls out this anti-pattern in raw feedback and the MAQ includes it as a cross-collection directive. fileciteturn13file0L1-L1  

Net: partially overlapping but not redundant; it’s a generalization and a “meta-policy,” not one more pattern rule.

## Prompt-cap prioritization under the 1500-word ceiling

You state: prompt cap is 1500 words, current is 1072 words, so you have ~428 words of headroom. Under that budget, A–D can all plausibly fit, but the question is which is highest leverage if you must choose. fileciteturn14file0L1-L1  

I’ll answer in terms of **marginal risk reduction per word** and **how catastrophic the failure is if absent.**

### Most important to include

**Dependency-first splits (D)** is the highest leverage.

Reason: it attacks the “blunt heuristic” failure class that creates *systematic* errors (not one edge case). If the model internalizes “question/answering analysis first,” it improves:

- when to merge vs split,
- when to keep objection + refutation together,
- when numbered items are actually one cluster,
- when intros serve as scope constraints vs filler.

It is also strongly aligned with the owner’s repeated meta-directive: not “ENCOUNTERED → enforce protocol,” but reason about the scenario. fileciteturn13file0L1-L1  

If D is absent, you can still survive via many specific DP rules, but you will keep seeing brittle pattern mistakes in novel configurations.

### Next most important

**Title retention asymmetry (C)** is unusually high value per word *because the harm is subtle but severe*: missing titles can create invisible “where am I in the book?” loss, and in some corpora (hadith tarajim style) the **title is the ruling**; dropping it is dropping the core content or making evidence look unmoored. fileciteturn8file0L1-L1  

### Candidates to defer (if you must)

**Anti-surface classification (A)** is the easiest to accidentally bloat or misapply (including the “never classify as intro” overreach). Its intent is important, but the safest version of it is “don’t discount,” not “never classify,” and that can be expressed more compactly or moved to Phase 2a where classification actually happens. fileciteturn7file0L1-L1  

**Forgiving retention (B)** is high-frequency and useful, but it is also the most exploitable. If you can’t also afford the deterministic post-checks that prevent abuse (function-mix ratio caps, non-accumulation), adding B alone can backfire by encouraging merge-happy behavior.

So if the real constraint is not word budget but *total risk surface*, B is the one I would stage carefully: add it only alongside enforcement/guardrails.

## Batch verdicts

### Batch 1 verdict: ITERATE

Batch 1’s doctrines are directionally correct and align strongly with owner intent around “no deception,” “trust poisoning is existential,” and “validator must not become a covert excerpter.” fileciteturn6file0L1-L1  

But I would not call it “PROCEED” yet because:

- The ledger itself labels Batch 1 “preliminary” pending DR review and notes missing red-team automation and fixture coverage for the “hardest patterns” that FP‑20 demands. fileciteturn14file0L1-L1  
- There is an unaddressed operational failure mode: **flag laundering / alarm fatigue turning ‘visible failure’ into de facto silent corruption**, which is directly contrary to FP‑21’s safety partition and the owner’s “my only worry is memorizing” requirement. fileciteturn13file0L1-L1  

### Batch 2 verdict: ITERATE

Batch 2’s direction is correct (it targets exactly the “manhunt” and self-containment pain described by the owner), and the A–D rules are already present in the current `GROUP_SYSTEM_PROMPT` in this branch. fileciteturn8file0L1-L1  

But it should not be considered stable until you address the two adversarial risks you explicitly asked about:

- Rule A can bias the model into “everything is substantive,” collapsing the usefulness of structural transitions and producing overbroad units unless it is reframed or counterbalanced. fileciteturn8file0L1-L1  
- Rule B can be exploited into “never split,” unless you pair it with deterministic enforcement of the ≤15% constraint and an anti-accumulation policy. fileciteturn8file0L1-L1