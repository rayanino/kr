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

### Tier 4 — Communication Quality

| # | Criterion | Test |
|---|-----------|------|
| 20 | Parseable structure | Consistent numbering, exact cross-references |
| 21 | Necessary and sufficient | Removing any sentence would cause a wrong implementation |
| 22 | Clean dependencies | External dependencies explicit and minimal |
| 23 | Operational clarity | A new agent with no KR context can follow this document alone |

---

## SPEC Template

Every engine and shared component SPEC follows this structure:

```
# {Engine Name} — {Arabic Name} — Specification

## 1. Purpose and Scope
## 2. Input Contract
## 3. Output Contract
## 4. Processing Specification
## 5. Validation and Quality
## 6. Consensus Integration
## 7. Error Handling
## 8. Configuration
## 9. Current Implementation State
## 10. Test Requirements
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
