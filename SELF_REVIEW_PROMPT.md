Halt. Do not respond yet.

You just produced a substantial output. Before I accept it, you will verify it using the process below. This is non-negotiable — every evaluation session requires this.

<review_mandate>
Your output contains claims. Some of them are wrong. Your job is to find which ones, fix them, and tell me what you found. If you complete this review and report "nothing to fix," you almost certainly didn't look hard enough — surface-level outputs always contain errors that only adversarial verification catches.

The standard: this output will be consumed by downstream pipeline phases and by the owner's domain judgment. An undetected error here becomes a wrong belief in the library. Treat every factual claim, every verdict, every "VERIFIED" as guilty until proven innocent.
</review_mandate>

<review_protocol>

PHASE 1 — REQUIREMENT COMPLIANCE
Re-read the original task document. For every explicit instruction, checklist item, or "MUST" requirement, confirm you actually did it. Don't assess from memory — open the files and check. Common failures: skipped steps in the per-book workflow, missing methodology fixes (FIX 1–6), missing framework-required sections (confidence calibration, consistency self-check), invented categories not in the spec.

PHASE 2 — ADVERSARIAL CLAIM VERIFICATION  
Pick the 5 claims in your output most likely to be wrong — not the ones you're most confident about, the ones with the highest *expected damage if wrong*. For each one:
- State the claim explicitly
- Search the web or read the pipeline data to verify it independently
- If the evidence contradicts your claim, fix it immediately — do not rationalize
- If the evidence is ambiguous, mark it as uncertain rather than asserting confidence

Use tools. Run scripts. Fetch pages. Read JSON files. Introspection catches nothing that tool-grounded verification doesn't catch faster and more reliably.

PHASE 3 — DOMAIN ATTACK
You are evaluating Islamic scholarly texts. Assume your domain knowledge contains errors. For every book where you made a domain claim (genre classification, science scope, author identification, multi-layer structure, death date), find at least one piece of external evidence that either confirms or challenges it. The Islamic sciences have precise technical meanings — verify you used terms correctly (e.g., "sirah" means prophetic biography, not general biography; "tarajim" means biographical dictionary; "tabaqat" means generational classes).

PHASE 4 — CROSS-BOOK CONSISTENCY
Review all verdicts together as a batch. Ask:
- Did I apply the same standard to book 1 and book 8?  
- Did I flag something for one book but let the same issue pass for another?
- Are my source independence counts honest (Shamela ecosystem excluded)?
- Is there a pattern I should have caught but didn't?

PHASE 5 — FIX AND REPORT
Apply all corrections directly to the output file. Then append a structured summary:

**Self-review findings:**  
**Claims verified by tool:** [list what you checked and how]  
**Errors found and fixed:** [specific corrections, not cosmetic]  
**Remaining uncertainty:** [anything you couldn't resolve]  
</review_protocol>

<constraints>
- You MUST use tools (web search, file reads, script execution) during this review. A review that only "thinks harder" is not a review.
- Do NOT fabricate issues to appear thorough. Real fixes only. If the output is genuinely clean, say so and list exactly what you verified to reach that conclusion.
- Do NOT acknowledge the gap without closing it. "Should have searched more" without searching more is a failure. Go search.
- Time is unlimited. Depth is the only metric. Take as many tool calls as needed.
</constraints>
