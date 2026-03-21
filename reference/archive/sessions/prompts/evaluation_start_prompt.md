Run the normalization engine evaluation. The build is complete — all 7 sessions accepted, 420 tests passing, zero findings in the final review. The repo is clean at commit `3c8f7cd`.

<session_context>
Phase: Step 3 (Evaluate) per `reference/ENGINE_BUILD_BLUEPRINT.md`
Previous: Build done. S7 review ACCEPT at commit `59ba314`. NEXT.md updated at `3c8f7cd`.
State: 420 tests (14 skipped), 37/51 ADV, L-001–L-012, SPEC-NOTE-1–3 pending fix.
Scope: Normalization engine — entirely deterministic, no LLM calls. Evaluation adapts accordingly (Layer 3 = manual structural inspection, not web search verification).
</session_context>

<mandatory_session_start>
Execute in order before any evaluation work:

1. Clone: `git clone https://{token}@github.com/rayanino/kr.git` — read the token from project file `github_token`
2. `cat NEXT.md` — this is your governing directive. It specifies the full methodology: 4 evaluation layers, GO/NO-GO criteria, SPEC maintenance scope, output files, and passaging contract alignment checks. Do NOT improvise — follow it.
3. `git log --oneline -5`
4. Read `reference/ENGINE_BUILD_BLUEPRINT.md` §3 (Step 3: Evaluate) — the evaluation methodology that NEXT.md implements
5. Read `reference/protocols/QUALITY_AXIOM.md`
6. `ls /mnt/skills/user/` — choose skills: `kr-evaluate` + `critical-review` + `thinking-frameworks`
7. Read the remaining files in NEXT.md's "Read First" list before starting Layer 1
</mandatory_session_start>

<task>
The evaluation has 4 layers plus SPEC maintenance. NEXT.md has the full specification for each.

**Layer 1** — Programmatic validation: run normalize_source on all 63 fixtures, collect the metrics schema defined in NEXT.md. Check for zero fatals, warning patterns, and anomalies.

**Layer 2** — Pattern analysis: assess each of L-001 through L-012 for downstream passaging impact (BLOCKING / ACCEPTABLE / DEFERRED). Read the passaging contracts and loader to understand what passaging actually needs.

**Layer 3** — Manual structural inspection: pick 5 diverse fixtures (NEXT.md suggests which), run the pipeline, print real Arabic text, and read it as a human scholar would. Verify diacritics, footnote separation, headings, layer boundaries, and boundary continuity signals. This is the layer that catches what tests can't — semantic quality.

**Layer 4** — GO/NO-GO: aggregate findings, categorize each per kr-evaluate, and deliver the verdict against the GO criteria in NEXT.md.

**SPEC maintenance** — Fix SPEC-NOTE-1 through SPEC-NOTE-3. Details in `reference/SPEC_ERRATA.md`. Do this before or after the evaluation layers, but before the transition gate.

**Outputs:** `engines/normalization/EVALUATION_REPORT.md`, `engines/normalization/LESSONS.md`, updated SPEC.md, updated NEXT.md pointing to the transition gate.
</task>

<guardrails>
- NEXT.md is the authoritative directive. Read it before doing anything. Do not improvise the evaluation methodology.
- Do NOT run the transition gate in this chat. Transition gates go in a separate session — context degradation rules apply. Update NEXT.md to point to the gate, then stop.
- Do NOT skip Layer 3. "420 tests pass" does not mean the engine is ready. The evaluation exists to find what tests don't cover. Print Arabic text. Read it. Check that a scholar would see correct output.
- Do NOT rubber-stamp. The most dangerous moment is when approval feels obvious after 420 passing tests and 7 accepted sessions. That feeling is the signal to look harder, not faster.
- Every finding is categorized per kr-evaluate: CORE GAP / ENGINE BUG / EXTENSION OPPORTUNITY / LESSON LEARNED. Only CORE GAP and ENGINE BUG block the GO verdict.
- After completing the evaluation, run the post-protocol adversarial pass (QUALITY_AXIOM.md standing order 7): "What is this evaluation NOT checking?"
- Take all your time. No rush. Quality is the only metric.
</guardrails>
