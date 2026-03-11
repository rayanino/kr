Halt. Do not respond yet.

You just produced a substantial output. Before I accept it, you will verify it using the process below. This is non-negotiable — every evaluation session requires this.

<review_mandate>
Your output contains claims. Some of them are wrong. Your job is to find which ones, fix them, and tell me what you found. If you complete this review and report "nothing to fix," you almost certainly didn't look hard enough — surface-level outputs always contain errors that only adversarial verification catches.

The standard: this output will be consumed by downstream pipeline phases and by the owner's domain judgment. An undetected error here becomes a wrong belief in the library. Treat every factual claim, every verdict, every "VERIFIED" as guilty until proven innocent.
</review_mandate>

<review_protocol>

PHASE 1 — REQUIREMENT COMPLIANCE (re-read ALL governing documents, not just the task)
Open and re-read: the task document, PHASE_C_EVALUATION_FRAMEWORK.md, PHASE_C_ERRATA.md, and NEXT.md. For every explicit instruction, checklist item, or "MUST" requirement across ALL of these, confirm you actually did it — don't assess from memory, open the files and check.

Then ask: **what did I skip?** List every pipeline data file that EXISTS for these books but that you never opened (sanity_checks.json? prompt_sent.json? consensus.json? ground_truth_comparison.json?). Open each one now and check for findings.

<known_failure_patterns>
These are errors that have occurred in prior sessions. Check for EACH ONE explicitly:
- Invented verdict categories not in the 5-level scale (VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE)
- Shamela-ecosystem sources (shamela.ws, ketabonline, turath.io, waqfeya) counted as independent
- Author confidence read from result.json instead of llm_responses/ (always 1.0 — engine bug)
- Confidence calibration section missing (framework requires it)
- Consistency self-check missing or done inline instead of as a separate pass
- web_fetch compliance below target
- Death dates classified as "genuine inference" when actually embedded in author_name_raw text
- Strategic analysis predictions not checked against actual results
- Cross-model field differences on non-consensus-checked fields (authority_level, science_scope, layers) not documented
- Causal claims about engine behavior ("X because Y") asserted without tracing through actual engine data
</known_failure_patterns>

PHASE 2 — ADVERSARIAL CLAIM VERIFICATION
Identify every claim in your output that, if wrong, would damage downstream consumers. This includes: author identifications, death dates, genre classifications, multi-layer determinations, science scope terms, source independence counts, and any "VERIFIED" verdict. For each high-damage claim:
- State it explicitly
- Verify it with a tool (web search, script, file read) — not from memory
- If the evidence contradicts your claim, fix it. Do not rationalize.

Minimum: 8 tool calls during this phase. If you haven't used 8 tools, you haven't checked enough.

PHASE 3 — DOMAIN ATTACK
You are evaluating Islamic scholarly texts. Assume your domain knowledge contains errors. For every book where you made a domain claim (genre, science scope, author, multi-layer, death date, layer structure), find at least one piece of EXTERNAL evidence (web search) that confirms or challenges it.

<domain_precision_checklist>
- "sirah" means prophetic biography (السيرة النبوية), NOT general biography
- "tarajim" means biographical dictionary, "tabaqat" means generational-class biographical work
- "tarikh" means historical chronicle
- A hashiyah has 3 layers (matn → sharh → hashiyah) — verify the actual author of each layer
- Tahqiq notes are editorial apparatus, NOT a scholarly commentary layer
- "fiqh_comparative" means cross-school comparative jurisprudence
- "mukhtasar" means an abridgment of a specific named longer work
- When two models disagree on layer structure, verify which is bibliographically correct via external sources
</domain_precision_checklist>

PHASE 4 — CROSS-BOOK AND CROSS-SESSION CONSISTENCY
Review all verdicts together as a batch. Ask:
- Did I apply the same standard to book 1 and book N?
- Did I flag something for one book but let the same issue pass for another?
- Are my source independence counts honest after excluding Shamela ecosystem?
- Are my verdicts consistent with prior sessions (calibration, Session 1, Session 2)?
- Did I check the strategic analysis predictions against actual Session results?
- Is there a cross-book pattern I should have caught but didn't?

PHASE 5 — FIX AND REPORT
Apply all corrections directly to the output file (str_replace). Then append a structured summary:

**Self-review findings:**
**Tool calls used:** [count and list what you checked]
**Errors found and fixed:** [specific corrections — not cosmetic]
**Known failure patterns checked:** [which patterns from the checklist were relevant, which were clean]
**Remaining uncertainty:** [anything you couldn't resolve]
</review_protocol>

<constraints>
- Minimum 8 tool calls during review. A review with fewer than 8 tools didn't verify enough.
- Do NOT fabricate issues. Real fixes only. If clean, list exactly what you verified.
- Do NOT acknowledge gaps without closing them. "Should have searched more" without searching is failure. Go search.
- Time is unlimited. Depth is the only metric.
</constraints>
