# Phase C Hardening — Prompts for New Chat Session

Three prompts. Each produces a concrete deliverable, not just analysis.

---

## PROMPT 1 — Context Intake + Verified Findings Check

Paste this as the FIRST message in the new chat:

```
The <session_context> and <session_goal> in the system prompt describe a PREVIOUS session. Override them with these updated instructions.

We are hardening the Phase C (Step 3: Targeted LLM Probes) preparation before handing it to Claude Code. Phase C runs the full source engine pipeline with real LLM API calls on 73 books. Every €1 spent on a bad call is €1 wasted.

Clone the repo, then read these files in this exact order. Read them carefully — your job is to find what the previous architect missed.

1. `NEXT.md` — current state
2. `PHASE_C_TASK_SPEC.md` — the implementation spec for Claude Code (31KB, the central document)
3. `PHASE_C_PREFLIGHT_AUDIT.md` — cost model, verified findings, risk register, 2 bugs caught in self-analysis
4. `PHASE_C_FINAL_SELECTION.md` — book selection rationale
5. `engines/source/VALIDATION_PLAN.md` — the governing validation plan
6. `RESULT_PRESERVATION.md` — how every API call's output must be saved
7. `scripts/phase_c_books.txt` — 73 book names
8. `tests/fixtures/phase_c_fixture_mappings.json` — 12 ground-truth mappings

The previous session resolved these questions (do NOT re-research them — spot-check only if something looks wrong):
- Temperature pass-through: YES works for both Anthropic TOOLS mode and OpenRouter JSON mode
- Consensus None handling: select_canonical_result picks higher-confidence model; pipeline continues with human gate flag
- Multi-volume: acquire_source reads first .htm file only; metadata card and text_sample from volume 1
- Instructor mode asymmetry: LOW RISK, both modes produce same Pydantic model; optional field handling may differ slightly; caught by 2-book test

Three OPEN questions for you to resolve:
- Q5: Should there be a --force flag to re-run books that already have "success" results?
- Q6: Agent team architecture — can Claude Code use sub-agents for parallel processing or auto-review?
- Q7: Edition variants (73 books include ~16 that are multiple editions of the same work) — run ALL or pick one per work?

After reading all files, give me:
1. Any errors or contradictions you found between documents
2. Any gaps in the task spec that would cause Claude Code to make wrong decisions
3. Your assessment: is this preparation ready for Claude Code, or does it need more work?

Be direct. If everything looks solid, say so. If you find problems, rank them by severity.
```

---

## PROMPT 2 — Deep Audit + Fixes

Paste after Prompt 1's response:

```
Now do the deep technical audit. Read these source files:

1. `engines/source/prompts/inference_v1.py` — the LLM prompt template
2. `engines/source/src/metadata_inference.py` — prompt construction + inference orchestration
3. `shared/consensus/src/consensus.py` — model dispatch, retry, agreement
4. `engines/source/src/inference_models.py` — the Pydantic schema LLMs must produce
5. `engines/source/src/engine.py` — the 13-step pipeline (focus on Steps 4, 9, 11)
6. `engines/source/src/consensus.py` — author agreement function

Audit for these specific risks to API credits:

<money_protection_audit>
A) PROMPT WASTE: Is there anything in the system message or user message that wastes input tokens without improving output quality? The JSON schema in the user message is ~700 tokens — but Instructor in TOOLS mode ALSO sends a schema via tool definitions. Are we sending the schema TWICE for Anthropic calls? That would be ~700 wasted input tokens per Opus call × 73 books = 51K tokens × $5/M = $0.25 wasted.

B) OUTPUT WASTE: The scholarly_context section asks for 10 subfields (composition_period, tradition_position, known_textual_issues, etc.). For obscure books, the LLM will output "null" or empty arrays for most of these — but still consumes output tokens for the JSON keys. Is scholarly_context worth its token cost for Phase C, or should we ask the LLM to OMIT empty scholarly_context fields?

C) RETRY WASTE: Our retry sends the SAME messages on failure. Instructor's retry sends the error message + previous attempt. Which approach wastes more? If our retry sends identical messages, a deterministic model (temperature=0) will produce the SAME failure. Is our retry loop pointless at temperature=0?

D) The monkey-patch (wrapping engine_mod.infer_metadata) — trace the exact import chain: engine.py line "from engines.source.src.metadata_inference import infer_metadata". Verify that patching engine_mod.infer_metadata will be seen when acquire_source calls infer_metadata. Show the specific code lines.

E) Processing flow: the spec says "detect_format() + extract_metadata() BEFORE acquire_source()". Both operate on the SAME file path. extract_metadata reads the .htm file. Then acquire_source ALSO reads the same .htm file (via its own extract_metadata call internally). Is there a TOCTOU risk if the file changes between the two reads? (Probably not in practice, but document the assumption.)
</money_protection_audit>

For each finding, provide:
- Severity: BLOCKER / WARNING / NOTE
- The specific fix (code change or spec change)
- Whether it should be fixed NOW (pre-handoff) or by Claude Code (during implementation)

Then: update PHASE_C_TASK_SPEC.md with ALL fixes. Update PHASE_C_PREFLIGHT_AUDIT.md with new findings. Commit and push with a descriptive message.
```

---

## PROMPT 3 — Agent Architecture + Final Integration + Handoff

Paste after Prompt 2's response:

```
Final phase. Three tasks:

TASK 1 — Agent Architecture Design:
Claude Code runs Opus 4.6 with ~1M context. The owner suggested agent teams where each agent processes a book, potentially with self-evaluation. Research Claude Code's agent/sub-process capabilities, then design the execution architecture:

- How should Claude Code structure the Phase C run? Options: (a) write a script the owner runs on Windows, (b) Claude Code runs the script itself using project API keys, (c) hybrid — Claude Code tests on 2 books, produces the validated script, owner runs the full 73.
- For the script itself: sequential vs parallel processing? If parallel, what concurrency level is safe given Anthropic rate limits (requests/minute) and OpenRouter limits?
- Auto-review: could a THIRD model (e.g., Haiku — cheap) do a quick sanity check on each book's output before human review? Example checks: "is the genre plausible for this title?", "does the author death date match the extracted death date?", "is multi_layer=true but layers is empty?" This would catch obvious errors automatically.
- Design the auto-review prompt if you think it's worthwhile.

TASK 2 — Final Integration Check:
Re-read PHASE_C_TASK_SPEC.md (as you updated it in Prompt 2). Verify:
- All numbers are consistent (73 books, 5 pre-requisites numbered 0-4, 12 fixture matches, ~€10-12 budget)
- The processing flow is internally consistent (path handling, file save ordering, error recovery)
- The Definition of Done checklist is complete and achievable
- The 2-book test checklist will actually catch the bugs we're worried about

TASK 3 — Produce Final Handoff:
- Update NEXT.md for the Claude Code handoff (not for another Claude Chat session)
- Write a concise CLAUDE_CODE_PHASE_C_BRIEF.md (<100 lines) — the executive summary Claude Code reads first, pointing to the detailed spec
- Commit everything with a clear message

After this prompt, the preparation phase is DONE. Everything should be ready for Claude Code to implement.
```

---

## Usage Notes

- Three prompts total. Each produces committed output, not just analysis.
- Prompt 1 establishes context and checks for gross errors (~10 min).
- Prompt 2 is the deep technical work — the money-protection audit (~20-30 min). This is where the new Claude earns its keep by finding things I missed.
- Prompt 3 designs the execution architecture and produces the final deliverables (~15-20 min).
- Total: ~3 turns, ~1 hour of Claude work. Much tighter than the original 6-prompt plan.
