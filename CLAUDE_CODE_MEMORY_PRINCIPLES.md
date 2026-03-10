# KR Project — Claude Code Persistent Memory Principles

These are governing principles for every session on the خزانة ريان (KR) project. They are non-negotiable. When in doubt, re-read these before making any decision.

---

## 1. PIPELINE FIRST — THE PRIME DIRECTIVE

The goal is building a correct, robust, fully-tested 7-engine pipeline. The goal is NEVER populating the library, building a user interface, producing the owner's scholarly library, or optimizing throughput.

Library population is a CONSEQUENCE of a working pipeline — not an objective. A correct pipeline with zero books processed is infinitely more valuable than a populated library built on fragile code. You run a correct pipeline once and the library is correct forever. You run a broken pipeline a thousand times and the library is wrong a thousand ways.

Every session, every task, every decision optimizes for: correctness, robustness, test coverage, error handling. Every session, every task, every decision NEVER optimizes for: throughput, user experience, interface design, "finishing" an engine before it's proven correct, or any work on the Scholar Interface or owner-facing features.

When unsure whether to fix a subtle edge case or move on to the next phase: FIX THE EDGE CASE. The pipeline must be right before it is complete.

---

## 2. RESULT PRESERVATION — EVERY API CALL IS SACRED

Every LLM API call costs real money. Every test run produces data that downstream engines and future sessions can reuse. NEVER make an API call whose output is not persisted in full structured form. NEVER persist results in a format that requires re-running the API call to extract what downstream engines need.

Save EVERYTHING: raw per-model LLM responses, full extraction dicts (including internal _ prefixed debug fields), complete SourceMetadata output, per-field confidence from each model individually, consensus agreement/disagreement details, human gate checkpoints with diagnostic values, per-file SHA-256 hashes and composite hashes.

Each phase produces: per-book structured JSON results, a phase summary, a lessons learned document (PHASE_X_LESSONS.md), and a reusability manifest (PHASE_X_MANIFEST.json) tracking which books were processed, by which pipeline version (git commit), and whether they need re-running after bug fixes.

Later phases SKIP books already successfully processed in earlier phases (checked via manifest). Phase E (full collection) only processes books NOT already covered by Phase C and D. This is not optional — it is the mechanism that prevents wasting budget.

When a bug is found between phases: assess which specific books it could have affected, mark ONLY those as needs_rerun=true in the manifest, and the next phase re-processes only the affected books. NEVER blanket re-run an entire phase because of one bug.

See /RESULT_PRESERVATION.md for the full protocol.

---

## 3. THE LIBRARY IS THE OWNER'S KNOWLEDGE

The library IS what the owner knows. An error in the pipeline becomes an error in his mind. A misattributed quote, a wrong school classification, a corrupted diacritic — these propagate through 6 downstream engines into the owner's understanding of his own religion. This is not a database problem. This is a knowledge corruption problem.

This means: every silent default is a potential wrong belief. Every dropped field is lost context that could prevent a misunderstanding. Every low-confidence decision that auto-approves instead of flagging is a bet on correctness that may be wrong. The cost of a false positive (flagging something that's fine) is the owner spends 30 seconds reviewing it. The cost of a false negative (letting through something wrong) is the owner learns something false about his deen.

---

## 4. ERRORS FAIL LOUDLY — NEVER SILENTLY

No engine may silently drop data, silently default on an uncertain decision, or silently skip a validation check. If something is wrong or uncertain, the pipeline STOPS or FLAGS it. Silent failures are the single most dangerous category of bug because they produce output that looks correct but is wrong.

Every error uses a defined error code from the SPEC's §7 error taxonomy. Every error produces a structured record with: error_code, severity, message, context dict, source_id, recovery_action. Bare `except: pass` or `except Exception: continue` patterns are FORBIDDEN — every exception must be caught, classified, and recorded.

When a function encounters an ambiguous situation: raise a structured error or create a human gate checkpoint. NEVER pick a "reasonable default" and continue silently. The owner cannot review what he doesn't know happened.

---

## 5. ARABIC TEXT IS FRAGILE — TREAT IT AS SACRED

A single diacritic change can reverse meaning: حَرَّمَ (prohibited) vs حَرَمَ (deprived). A normalization bug that strips diacritics destroys the distinction between legal rulings. This is not a theoretical concern — it has happened in real Islamic studies digital libraries.

Rules: Apply NFC Unicode normalization ONLY. Preserve all diacritics exactly. Primary text bytes are NEVER modified after extraction — no correction, no cleanup, no "improvement." Use encoding="utf-8" for ALL file operations. Test Arabic text handling with adversarial inputs: mixed diacritics, rare Unicode codepoints, zero-width joiners, Arabic comma (،) vs Western comma.

When processing Arabic names: the Arabic comma (،) and other punctuation must be stripped during name matching. LLM-generated full nasab names include commas (e.g., "الزجاجي، أبو القاسم"). Punctuation-insensitive matching is required.

---

## 6. MULTI-MODEL CONSENSUS IS MANDATORY

Never rely on a single LLM call for any content decision: author identification, school classification, genre assignment, multi-layer detection, date estimation, or any attribution. Always use multi-model consensus (currently: Opus 4.6 + Command A, with GPT-5.4 via OpenRouter as fallback).

The same LLM provider must NEVER both generate and verify a content decision (Layer 3.5 in KNOWLEDGE_INTEGRITY.md). This prevents self-reinforcing hallucination — the most dangerous failure mode because it produces high-confidence wrong answers.

When models disagree: escalate to 3+ model consensus or create a human gate checkpoint. NEVER silently pick one model's answer.

---

## 7. HUMAN GATES ARE NOT OPTIONAL

Every low-confidence decision creates a checkpoint the owner must resolve. No automated process may auto-approve a human gate checkpoint. The owner may respond "yes," "no," or "I'm not sure" — and "I'm not sure" triggers elevated multi-model verification, NOT auto-approval.

The owner is an Islamic studies student with deep domain knowledge but no technical background. He CAN reliably verify: book recognition, well-known author identification, coarse science classification, utility of outputs. He CANNOT reliably verify: precise death dates for lesser-known scholars, isnad chain parsing, subtle taxonomic distinctions. Design gates accordingly.

---

## 8. METADATA FLOWS FORWARD, NEVER DELETED

No engine may DELETE a metadata field that arrived in its input (D-023). Engines may ADD new fields and ENRICH existing values. This is because metadata is synthesis fuel — a field that seems irrelevant to the source engine may be critical for the taxonomy engine six steps downstream. The cost of carrying an unused field is zero. The cost of deleting a field that turns out to be needed is re-running the entire pipeline.

---

## 9. SPEC IS LAW — SPEC_CORE SUPERSEDES SPEC

SPEC_CORE.md is the behavioral authority for each engine. When SPEC_CORE.md and implementation code disagree, SPEC_CORE.md wins — fix the code. When SPEC.md (the old full spec) and SPEC_CORE.md disagree, SPEC_CORE.md wins — SPEC.md is archived, kept only as a reference for deferred Stage 2 capabilities.

contracts.py is the schema authority. Pydantic models define the exact data structures at every boundary. When SPEC prose and contracts.py disagree, update contracts.py to match SPEC_CORE.md.

ABD legacy code has ZERO design authority (D-019). SPECs define what to build, not old prototypes.

---

## 10. TEST PHILOSOPHY — SAME-AGENT TESTS CATCH NOTHING

Tests written by the same agent that wrote the code are nearly worthless for finding logic bugs. The agent makes the same assumptions in both the code and the tests. This was proven in Step 1 (code audit): 6 real bugs were found by manual review that 758 passing tests missed.

This means: after Claude Code writes code + tests, a separate review step (Claude Chat architect or a different session) must audit the code against the SPEC. Tests verify behavior; audits verify correctness.

Phase A (deterministic sweep on 2,519 real books) exists specifically because test fixtures are synthetic and curated — real data has edge cases that no one anticipated. Always prefer testing against real data over testing against fixtures.

---

## 11. DOMAIN AUTHORITY BOUNDARIES

The owner makes ALL domain decisions: what constitutes correct metadata for a book, which genre a book belongs to, whether an attribution is correct. Claude Chat (architect) makes ALL technical decisions: architecture, data structures, algorithms, error handling, testing strategy. Claude Code (builder) implements what the architect specifies, following SPEC_CORE.md.

When the owner gives domain input about Islamic scholarship, defer to his judgment absolutely. When the topic is technical or architectural, LEAD — the owner has no technical background and relies on your expertise. Misapplied domain knowledge corrupts the library, but so does letting a non-technical owner make architecture decisions.

---

## 12. THREE-TIER IDENTITY (D-024)

Every source has three levels of identity: source_id (this specific file/edition — src_{8_hex}), work_id (this book regardless of edition — wrk_{author_slug}_{title_slug}), canonical_id (the scholar who wrote it — sch_{5_digit}). These three tiers are the backbone of the entire pipeline. Confusing them (e.g., treating two editions as two different works) corrupts deduplication, scholar registries, and downstream synthesis.

---

## 13. THE NORMALIZATION BOUNDARY

Source and Normalization engines are Phase 1 (source-format-specific — above the boundary). All engines from Passaging through Synthesis are Phase 2 (source-agnostic — below the boundary). NO source-format-specific logic may exist below the normalization boundary. This means: if Passaging or later engines need to know "this came from Shamela," the architecture is wrong. The normalization engine strips all format specificity.

---

## 14. TECHNOLOGY FIRST — NO CUSTOM CODE FOR SOLVED PROBLEMS

Before writing any significant custom code, search for existing tools that handle the capability. Search pattern: "python library [capability] arabic" → domain-specific tools, "[capability] NLP tool 2025 2026" → recent developments. Read the actual documentation, not just the README tagline. Most sentence-transformers models don't handle Arabic well — verify Arabic support empirically, not by assumption.

If a well-maintained library handles 80% of the need, use it and build the 20% custom adapter. If the library handles <50% or doesn't support Arabic, build custom but document the decision.

---

## 15. NO SCOPE CREEP — CORE ONLY IN STAGE 1

During Stage 1, focus entirely on core architecture depth. Note transformative possibilities (Stage 2 / §4.B capabilities) briefly if they arise, but do NOT pursue them. Document extension hooks — what the core must not assume — to keep Stage 2 paths open without building Stage 2 features.

When reviewing a capability: ask "could this be implemented using ONLY this engine's input and tools?" If it requires calling other engines or data this engine doesn't have, it's scope creep. Defer it.

---

## 16. SESSION CONTINUITY — INSTITUTIONAL MEMORY ACROSS SESSIONS

NEXT.md is the handoff document. It tells the next session exactly what to do and what to read. Every session starts by reading NEXT.md. Every session ends by updating NEXT.md with: what was accomplished, what the next step is, what files to read, what traps to avoid.

PHASE_X_LESSONS.md documents what was learned in each validation phase: bugs found, patterns observed, what went wrong, what worked, recommendations for the next phase. The agent running the next phase reads this BEFORE starting. This is how institutional memory works across sessions with no shared state.

SESSION_LOG.md tracks the high-level arc across all sessions. It is the project's long-term memory.

---

## 17. BUDGET DISCIPLINE

Total API budget: €98 remaining. Phases: Step 3 (€5-10), Step 4 (€20-30), Step 5 (€40-50). NEVER start a phase without checking the cost log at tests/results/source_engine/COST_LOG.json. NEVER start a run if remaining budget is below estimated cost.

Cost-saving via result reuse is mandatory (see principle #2). Re-running books already successfully processed is burning budget for zero new information.

---

## 18. FROZEN SOURCES ARE IMMUTABLE

Once a source is frozen (SHA-256 hashed), the bytes NEVER change. If corruption is detected, the source is re-acquired from the original, not repaired. The frozen source is the tamper-evident baseline against which all downstream text is verified. Modifying a frozen source invalidates every hash, every deduplication check, and every text fidelity score in the entire pipeline.

---

## 19. GROUNDING TYPE TRACEABILITY (D-040)

Every factual claim in every synthesized entry must be tagged with its grounding type: source_grounded (traceable to a specific excerpt with source, page, volume), metadata_derived (derived from source metadata like author dates), or analytical (the synthesizer's own contribution — explicitly marked as such). An entry may NEVER contain an untagged factual claim. This is the mechanism that prevents synthesis hallucination (T-5).

---

## 20. FAIL LOUD ON UNCERTAINTY (D-033)

Low confidence → FLAG, not silent default. When a field's confidence score falls below the block threshold (0.50), the pipeline creates a human gate checkpoint. It does NOT pick the best guess and continue. When confidence is between 0.50 and the auto-accept threshold (0.70), the result is accepted but flagged for review. Only above 0.70 is the result accepted without flagging.

---

## 21. TRUST EVALUATION IS EMPIRICALLY VALIDATED

The 5-factor trust algorithm (author standing 0.30, tahqiq quality 0.25, publisher reputation 0.15, source authority 0.15, text fidelity 0.15) with threshold 0.65 was validated in Step 2 testing: 13/13 PASS, uniquely optimal across the 0.55-0.75 range. This is not arbitrary — it was tested empirically. Do not modify the weights or threshold without re-running the validation suite.

---

## 22. NO MODIFICATIONS TO WORKING CODE UNLESS EXPLICITLY TASKED

The point of validation phases is to find bugs by running existing code against real data. If the task is "run Phase A," do NOT refactor the extraction code, do NOT "improve" the regex patterns, do NOT fix things preemptively. Run the code as-is, record the failures, and fix them in a separate session after review. Premixing testing and fixing makes it impossible to know what the original code's failure rate was.

---

## 23. RALPH IS FOR SMALL INDEPENDENT TASKS ONLY

Ralph (snarktank/ralph autonomous loop) works for small, independent bug fixes and extensions — NOT for sequential, coupled build sessions. If a task requires reading the full SPEC, modifying multiple files, or understanding cross-module dependencies, it is a Claude Code task, not a Ralph task.

---

## 24. EVERY CLAIM IN THE SPEC MUST BE GROUNDED

Every claim in the SPEC must be traceable to a source (research, test result, domain expert input) or explicitly marked as a design decision. Ungrounded claims in the SPEC become unquestioned assumptions in Claude Code's implementation, which become permanent bugs in the pipeline. Mark uncertainty explicitly: distinguish what evidence shows, what you infer, and what you are guessing.

---

## 25. SEVEN KNOWLEDGE CORRUPTION THREATS

These threats from KNOWLEDGE_INTEGRITY.md must be actively prevented by every engine:
- T-1: Silent text corruption (diacritics, encoding, normalization)
- T-2: Attribution error (wrong author, wrong school, sharh/matn confusion)
- T-3: Taxonomic misplacement (content under wrong topic)
- T-4: Context loss (excerpt not self-contained)
- T-5: Synthesis hallucination (LLM fabricates scholarly positions)
- T-6: Metadata poisoning (wrong metadata propagates through pipeline)
- T-7: Duplication and contradiction (same content, different treatment)

Every engine must implement specific mitigations for the threats in its scope. Read KNOWLEDGE_INTEGRITY.md before implementing any engine.

---

## 26. SILENT FAILURE PATTERN AWARENESS

Seven patterns from SILENT_FAILURES.md that produce output that LOOKS correct but is subtly wrong:
1. Hollow examples (happy path only — wouldn't catch a wrong implementation)
2. Circular definitions (defines X using X)
3. Hand-waving technology references (named tech doesn't work for Arabic)
4. Phantom metadata (field name mismatch across engine boundaries)
5. Untestable rules (subjective language masquerading as precision)
6. Missing error paths (SPEC only describes the happy path)
7. Scope creep disguise (capability requires data this engine doesn't have)

Apply these as detection lenses during every code review and SPEC review.

---

## 27. GIT DISCIPLINE

Clone the repo fresh at session start: `git clone https://{token}@github.com/rayanino/kr.git`. NEVER upload repo files as project knowledge — they become stale immediately. The git clone gives the full, current repo every session.

Commit with meaningful messages that reference what was changed and why. Push before ending a session. Update NEXT.md before pushing.

---

## 28. THE OWNER'S SHAMELA COLLECTION

2,519 books exported from Shamela desktop v4. 1,932 single .htm files + 587 multi-volume directories. Owner's collection is at: C:\Users\Rayane\Desktop\kr\shamela export samples. 263 books had filenames exceeding filesystem limits during the original audit (may or may not be present in owner's copy). The collection is the test dataset for the source engine — all validation phases run against it. The owner wants full nasab names for all authors.

---

## 29. THE VALIDATION STEP SEQUENCE

Step 0 ✅ (13 fixtures, real LLM, €1.80) → Step 1 ✅ (code audit, 6 bugs fixed, €0) → Step 2 (deterministic sweep, 2519 books, €0) → Step 3 (LLM probes, 30 books, €5-10) → Step 4 (calibration, 150 books, €20-30) → Step 5 (full collection, 2519 books, €40-50).

Each step has a GO/NO-GO gate. No phase starts without the previous gate passing. Fixes happen BETWEEN phases, not during. Run → review → fix → next phase.

---

## 30. WHAT "ENGINE COMPLETE" MEANS

An engine is complete when: (1) it handles every format/input type in its SPEC, (2) every error path produces a structured error code, (3) it has been tested on real data (not just synthetic fixtures), (4) the owner has spot-checked representative outputs, (5) all GO/NO-GO gates have passed, (6) its output has been verified as consumable by the next engine downstream, and (7) PHASE_X_LESSONS.md documents everything learned.

An engine is NOT complete just because: it runs without crashing on test fixtures, all unit tests pass, or it produced output for the full collection.

---

## 31. DOWNSTREAM ENGINE AWARENESS

Every engine's output is the next engine's input. The source engine's SourceMetadata is consumed by the normalization engine. The normalization engine's manifest.json + content.jsonl is consumed by passaging. And so on through synthesis. Changing an output field name, type, or semantics in one engine breaks every engine downstream. Before modifying any output schema, verify the downstream engine's input contract still matches.

---

## 32. CONTEXT WINDOW MANAGEMENT FOR CLAUDE CHAT

Claude Chat (architect) has ~200K tokens. NEVER read VISION.md whole (~47K tokens). Use scripts/extract_vision_sections.py for specific sections. One SPEC per session. Stop clean at 70% context usage — finish the current section, write NEXT.md with detail, commit, stop. A clean handoff at 70% is better than a rushed completion at 95%.

---

## 33. KNOWN COSMETIC ISSUES (DO NOT RE-DISCOVER)

Three non-blocking issues from Step 1 audit that are documented but NOT yet fixed:
- Duplicate gate checkpoint created when genre confidence < 0.50 (engine.py:532 and :587 both fire)
- Gate checkpoint diagnostic values are empty strings for confidence_threshold errors (dict.get doesn't resolve dotted paths)
- structural_format defaults to "prose" instead of "mixed", genre chain silently drops on invalid relation_type, staging cleanup swallows move failures

These are known. Do not re-discover them. They will be fixed when relevant.
