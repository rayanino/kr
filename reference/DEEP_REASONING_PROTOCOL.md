# Deep Reasoning Protocol — خزانة ريان

This document defines two things: the quality standard every document must meet, and the SPEC template every engine follows. The authority model and session workflow are in the project instructions.

---

## The Perfection Standard

A document passes when ALL applicable criteria are met. Use this as a checklist during self-review.

### Tier 1 — Structural Soundness (non-negotiable)

| # | Criterion | Test |
|---|-----------|------|
| 1 | Zero ambiguity | An AI agent implements described behavior with zero clarifying questions |
| 2 | Binary sentences | Every sentence is a binding rule OR a marked open question — nothing else |
| 3 | No contradictions | No sentence contradicts anything in any KR document |
| 4 | No premature constraints | Nothing constrains an undecided matter |
| 5 | No unbounded universals | Every "always/never/all" scoped to what can be guaranteed |
| 6 | Glossary compliance | Every term matches VISION.md §2 exactly — no synonyms, no collisions |
| 7 | No duplication | Only unique content; external rules referenced, not restated |
| 8 | Accurate state | Current code described accurately; unbuilt features marked [NOT YET IMPLEMENTED] |
| 9 | Adversarial-proof | No second valid reading exists under hostile interpretation |

### Tier 2 — Content Completeness

| # | Criterion | Test |
|---|-----------|------|
| 10 | Full input coverage | Every legitimate input the engine could receive is addressed |
| 11 | Exhaustive error handling | Every failure mode has a defined recovery or escalation |
| 12 | Enumerated edge cases | Each edge case: trigger, response, justification |
| 13 | Testable rules | Every behavioral rule yields a clear pass/fail test case |
| 14 | Both-sides integration | Every boundary: what this engine expects AND what it promises |

### Tier 3 — Design Quality

| # | Criterion | Test |
|---|-----------|------|
| 15 | Best-known design | Alternatives considered; this is the best, with reasoning |
| 16 | Earned complexity | Every element justifies its existence |
| 17 | Scale-graceful | Works at 1x and 1000x; limitations stated if not |
| 18 | Vendor-neutral | No unjustified tool/platform lock-in |
| 19 | Forward-compatible | Known extension points identified |
| 20 | Transformative ambition | At least one capability that makes previously impossible scholarship possible; architect-originated, not from VISION.md or owner requests |
| 21 | Scholarly integrity | Every knowledge product is verifiable, every claim traceable to source, no error can propagate undetected into the library (which IS the user's knowledge) |

### Tier 4 — Communication Quality

| # | Criterion | Test |
|---|-----------|------|
| 22 | Parseable structure | Consistent numbering, exact cross-references |
| 23 | Necessary and sufficient | Removing any sentence would cause a wrong implementation |
| 24 | Clean dependencies | External dependencies explicit and minimal |
| 25 | Operational clarity | A new agent with no KR context can follow this document alone |

---

## SPEC Template

Every engine and shared component SPEC follows this structure. Each section has a specific purpose — do not mix content between sections.

```
# {Engine Name} — {Arabic Name} — Specification

## 1. Purpose and Scope
What this engine does. What is NOT this engine's responsibility.
Phase classification. Normalization boundary relationship.
Which user scenarios (reference/USER_SCENARIOS.md) this engine serves,
and what it must produce for each scenario to work.

## 2. Input Contract
Reference to input schema. What the engine expects from upstream.
Validation performed on input. What triggers rejection vs. warning.

## 3. Output Contract
Reference to output schema. What the engine produces for downstream.
Guarantees about output (completeness, ordering, uniqueness).

## 4. Processing Specification
The behavioral rules governing input→output transformation.
This is the core section — every processing decision lives here.
Edge cases with explicit resolution rules.

This section has two parts:
§4.A — Core Processing: the baseline rules for transforming input to output.
§4.B — Transformative Capabilities: features this engine provides that go
beyond basic processing — capabilities that make previously impossible
scholarship possible. These are not nice-to-haves; they are the reason
this application exists. Every engine must have at least one capability
in §4.B that the architect originated (not from VISION.md, not from
the owner's requests). Design them fully here even if unbuilt.

Subsections as needed for both parts.

## 5. Validation and Quality
How this engine ensures its output meets publishable scholarship standards.
Self-validation the engine performs on its own output (§8 Layer 1) — be specific:
what checks, what thresholds, what happens on failure.
Automated checks available (§8 Layer 2).
Human gate integration (§9), if applicable — what triggers human review,
what the human reviews, what happens after review.
Remember: an error in this engine's output is an error in Rayane's knowledge.
What prevents that?

## 6. Consensus Integration
Which decisions in this engine use multi-model consensus.
Consensus configuration (number of models, agreement threshold).
If this engine does NOT use consensus, say so explicitly and explain why.
Not every engine needs consensus — but the decision must be conscious.

## 7. Error Handling
Malformed input. Partial failures. Consensus disagreement.
Every error: error code, severity (fatal/warning/info), recovery action.
The principle: never lose data silently. An unhandled error that corrupts
the library is worse than a visible failure that stops processing.
Include: what gets logged, what triggers alerts, what blocks the pipeline.

## 8. Configuration
Parameters controlling engine behavior (with defaults and valid ranges).
Per-science configuration hooks (Level 3 / SCIENCE.md).
What is configurable vs. what is hardcoded and why.

## 9. Current Implementation State
Existing files with line counts. What works today.
Known gaps between current code and this spec — be brutally honest.
Everything unbuilt marked [NOT YET IMPLEMENTED].
External tools and libraries this engine depends on (from reference/RESOURCES.md).
What each external tool handles vs. what is custom code.
This section is a snapshot. Claude Code reads it to know what to build.
If it says "works" and the code is broken, Claude Code wastes sessions.

## 10. Test Requirements
Test coverage requirements — what MUST be tested, not just "everything."
Gold baseline usage: what baselines exist, what new ones this SPEC demands.
Regression testing strategy: what must not break when code changes.
Integration test requirements: what must this engine verify with its
upstream producer and downstream consumer?
```

---

## Example: What a Good SPEC Section Looks Like

This is an illustrative example of SPEC quality — not the actual source engine SPEC, which must be written from the real code and reference docs.

<example name="good_spec_section">
## 2. Input Contract

The source engine is the pipeline entry point. It receives input from two paths:

**Autonomous discovery.** The source engine queries configured source repositories (§2.5) using repository-specific interface modules. Each repository module returns candidate sources as structured metadata: title, author (if available), repository identifier, and a download handle. The source engine does not access repositories directly — it delegates to repository modules that encapsulate connection, authentication, and rate-limiting logic. Adding a new repository requires only a new repository module; no source engine core logic changes.

**Manual input.** The owner provides content through a manual input interface. Manual input arrives as: a text payload (the content itself), an input type identifier (one of: `typed_passage`, `lesson_transcription`, `study_note`, `external_reference`), and optional metadata hints (author name, science scope, source title). The source engine validates that the text payload is non-empty and the input type is recognized. Unrecognized input types are rejected with error `SOURCE_INVALID_INPUT_TYPE`.

**Validation on input.** For autonomous sources: the repository module must return a non-empty title and a valid download handle. Sources with empty titles are logged and skipped (not errors — some repositories have incomplete metadata). For manual input: text payload must be non-empty; input type must be one of the four recognized types. Failed validation produces a structured error with the source identifier (if known) and the validation failure reason.
</example>

Notice: every sentence is either a binding rule ("Unrecognized input types are rejected with error SOURCE_INVALID_INPUT_TYPE") or a design decision with rationale ("The source engine does not access repositories directly — it delegates to repository modules that encapsulate connection, authentication, and rate-limiting logic"). No filler. No aspirational language. A developer reading this section knows exactly what to build.

---

## Example: What a Good Self-Audit Looks Like

After completing a SPEC draft, perform the structured self-review defined in the project instructions. Here is an example of what the visible deliverable should look like:

<example name="good_self_audit">
### Self-Audit Results (Source Engine SPEC Draft 1)

**Defect 1 (Structural — Criterion #1 Zero Ambiguity):** §4.2 says "the source engine evaluates relevance using content analysis." This is ambiguous — what does "content analysis" mean concretely? An implementing agent would have to guess. **Fix:** Replace with: "The source engine evaluates relevance by extracting the source's table of contents (or first 2000 characters if no TOC), sending it to the LLM with the library's science inventory, and classifying the match as `relevant`, `partially_relevant`, or `not_relevant`."

**Defect 2 (Completeness — Criterion #10 Full Input Coverage):** §2 defines manual input types but never addresses what happens when the owner provides a file (PDF, audio) rather than text. The input contract silently ignores this case. **Fix:** Add to §2: "File-based manual input (PDF, audio, image) is not processed by the source engine directly. The owner is informed that file-based input requires a normalizer for that file type. If no normalizer exists, the input is rejected with error `SOURCE_UNSUPPORTED_FORMAT` and a suggestion to provide the content as typed text."

**Defect 3 (Design — Criterion #16 Earned Complexity):** §8 defines 12 configuration parameters, but 4 of them (`max_concurrent_downloads`, `retry_backoff_base`, `retry_max_attempts`, `connection_pool_size`) are implementation details that belong in code, not in a SPEC. A SPEC should define behavioral rules, not HTTP client tuning. **Fix:** Remove the 4 parameters. Add a note: "Network behavior (concurrency, retries, connection management) is an implementation concern configured in code, not specified here."

**Defect 4 (Communication — Criterion #9 Adversarial-Proof):** §3 says "the source engine outputs a frozen source and source metadata." Under hostile reading, "outputs" could mean "writes to disk" or "returns as a data structure" or "publishes to a message queue." **Fix:** Replace with: "The source engine writes two artifacts to disk: the frozen source file at `library/sources/{source_id}/frozen/{filename}` and the source metadata record at `library/sources/{source_id}/metadata.json`."
</example>

Notice: each defect quotes the exact failing text, names the specific Perfection Standard criterion it violates, and provides a concrete fix. Cosmetic-only audits (typos, formatting) indicate the audit was superficial — at least one defect must be structural or semantic.

---

## Example: What a Good VISION Correction Looks Like

When correcting VISION.md sections, produce a defect ledger like this:

<example name="good_vision_correction">
### VISION.md §7.2 Defect Ledger

**Defect 1 (Severity: HIGH).** Line 769: "The source engine maintains a source registry that tracks all acquired sources with sufficient identifying information to detect duplicates."
**Problem:** "Sufficient identifying information" is unbounded — Criterion #1 (zero ambiguity). What fields are sufficient? Title alone? Title + author? Hash?
**Correction:** "The source engine maintains a source registry that tracks all acquired sources. Deduplication uses a composite key of: author name (normalized), work title (normalized), and edition identifier (if available). Sources with identical composite keys are flagged as potential duplicates for human review rather than silently rejected, because different editions of the same work may contain meaningful textual differences."

**Defect 2 (Severity: MEDIUM).** Line 774: "Adding a new repository to this registry is a configuration decision."
**Problem:** "Configuration decision" is vague — Criterion #2 (binary sentences). This sentence is neither a binding rule nor a marked open question.
**Correction:** "Adding a new repository requires: (1) implementing a repository module conforming to the repository interface defined in the source engine SPEC, and (2) registering the repository in the application's configuration. No source engine core logic changes are required."
</example>

---

## Example: What Good §4.A Rules Look Like

§4.A rules are precise enough for Claude Code to implement without clarifying questions, but they specify BEHAVIOR, not code structure. Here is a calibration example showing the right level of detail:

**Important:** This example shows the level of precision to AIM FOR, not design decisions to copy. The specific field names, formats, and behaviors shown below are illustrative — the architect decides the actual design based on their own analysis of what's best.

<example name="good_core_processing_rules">
### §4.A — Core Processing

#### §4.A.1 — Source Identification

Every source receives a `source_id` at registration time, formatted as `{science}_{author_slug}_{title_slug}_{edition_hash}` (e.g., `nahw_ibnhisham_qatralnada_a3f2`). The `edition_hash` is a 4-character hash of the edition-distinguishing metadata (tahqiq editor + publisher + edition number), ensuring that the same book with different tahqiq receives a different `source_id`.

The same logical work (e.g., "al-Mughni by Ibn Qudamah") may appear multiple times in the registry with different `source_id` values if different editions exist. These share a `work_id` (format: `{author_slug}_{title_slug}`) that groups all editions of the same work. The source registry tracks the owner's preferred edition per `work_id` (default: the edition with the highest tahqiq quality score).

If the system cannot determine a unique `source_id` because essential metadata is missing (no author identified, no title identified), the source is registered as `unidentified_{intake_timestamp}` and a human gate checkpoint is created. The source is available for normalization but cannot proceed to excerpting until identification is resolved.

#### §4.A.2 — Metadata Extraction: Shamela Format

**Note:** This example shows ONE source format's extraction rules. The actual SPEC must define extraction rules for every supported source type, not just Shamela. Shamela is used here because it's the only format with existing code.

For Shamela-format sources, the source engine extracts metadata from two locations: the `info.html` file (title, author, category, description) and the `content.html` structure (volume/page organization, footnote presence, section headers).

Extraction rules for `info.html`:
- `title`: The first `<h1>` content, stripped of HTML tags. If absent, use the directory name.
- `author`: Extracted from the "المؤلف" field. If the field contains multiple names separated by "و", each is recorded as a contributor with role `author`. If absent, flag as `author_unknown` and create a human gate checkpoint.
- `category`: Mapped to the nearest KR science classification. If no mapping exists, recorded as `unclassified` with the original Shamela category preserved in `raw_category`.

If `info.html` is malformed (not valid HTML, missing expected fields), the engine logs a structured warning and extracts what it can. Extraction never fails entirely on a malformed `info.html` — partial metadata is always better than no metadata.
</example>

Notice: these rules specify WHAT the engine does in precise detail, including edge cases and failure handling, but they do NOT specify HOW the code should be organized (no function names, no class hierarchies, no specific libraries). That's Claude Code's domain.

---

## Example: What a Transformative §4.B Section Looks Like

SPEC §4.B should not be a wish list. It should be fully specified capabilities — with inputs, outputs, triggers, and behavioral rules — that happen to be unprecedented. Here is a calibration example:

<example name="good_transformative_section">
### §4.B — Transformative Capabilities

#### §4.B.1 — Citation Network Discovery

When the source engine processes a new source and the excerpting engine identifies a textual reference to another work (e.g., "as Ibn Qudamah states in al-Mughni" or "ذكر في المغني"), the source engine receives a discovery request containing: the referenced author name (normalized), the referenced work title (normalized), and the citing excerpt ID.

The source engine queries all registered repositories for candidate matches using the normalized author+title pair. If exactly one candidate is found with confidence ≥0.85, the source engine creates an acquisition request with priority `citation_discovered` (higher than periodic crawl, lower than owner-requested). If multiple candidates are found, the engine creates a human gate checkpoint presenting the candidates with their provenance metadata for owner selection.

The citation relationship (citing_excerpt_id → discovered_source_id) is recorded in the source registry regardless of whether the discovered source is ultimately acquired. This builds a citation graph over time that reveals scholarly influence networks even before all referenced works are in the library.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: excerpting engine's implicit reference detection (§4.B.2 in excerpting SPEC) and repository search interface (§4.A.3).
</example>

Notice: the capability is novel (no Islamic studies tool auto-discovers sources from citation networks), but it is specified with the same precision as any §4.A rule — inputs, outputs, thresholds, edge cases, dependencies. This is what Criterion #20 (Transformative Ambition) requires.

**Do not copy this example into a SPEC.** It exists to calibrate the level of detail and ambition expected. Every §4.B capability in an actual SPEC must be architect-originated for that specific engine. If you find yourself reproducing this example, stop — think about what THIS engine specifically enables that was previously impossible.
