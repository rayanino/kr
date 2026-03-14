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
- Schema double-send: In TOOLS mode, Instructor sends schema as tool definition AND our user message has it as text. Redundant (~$0.26 waste on 73 books) but harmless. NOT fixing for Phase C.
- Retry at temperature=0: Retry uses simplified_messages (different input), so not pointless. Also handles API failures (timeout, 429) which are non-deterministic.

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
A) PROMPT WASTE: In TOOLS mode (Anthropic), Instructor sends the Pydantic schema as a tool definition. Our user message ALSO contains the JSON schema as text (~700 tokens). Previous session confirmed this is redundant but harmless ($0.26 for 73 books). HOWEVER: verify this by checking what Instructor actually sends in TOOLS mode — does `client.create(response_model=InferenceOutput)` inject a tool with the full schema? If so, could we remove the schema text from the user message for Anthropic calls only? Or is the user-message schema still useful as GUIDANCE even in TOOLS mode?

B) OUTPUT WASTE: The scholarly_context section asks for 10 subfields (composition_period, tradition_position, known_textual_issues, etc.). For obscure books, the LLM will output "null" or empty arrays for most of these — but still consumes output tokens for the JSON keys. Estimate: how many output tokens does an all-null scholarly_context cost? Is it worth keeping for Phase C, or should we tell the LLM to omit scholarly_context entirely when context_richness would be "minimal"?

C) The monkey-patch (wrapping engine_mod.infer_metadata) — trace the exact import chain. engine.py has `from engines.source.src.metadata_inference import infer_metadata` near the top. When Phase C patches `engine_mod.infer_metadata = _capturing_wrapper`, does acquire_source's internal call to `infer_metadata(...)` see the wrapper or the original? Show the specific lines of engine.py where infer_metadata is called.

D) Processing flow: the spec says "detect_format() + extract_metadata() BEFORE acquire_source()". Both read the same .htm file. Is there a practical risk if the owner modifies files mid-run? (Probably not, but document the assumption.)

E) Pre-Req 0 says to add `compiler_name_raw`, `commentator_name_raw`, and `riwayah` to the prompt context. But does the LLM prompt template mention these fields anywhere in its instructions? If the prompt says nothing about compiler/commentator/riwayah, the LLM might ignore them. Should the system message be updated to tell the LLM these fields exist?
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
- Prompt 2 is the deep technical work — the money-protection audit (~20-30 min). This is where the new Claude earns its keep by finding things the previous session missed.
- Prompt 3 designs the execution architecture and produces the final deliverables (~15-20 min).
- Total: ~3 turns, ~1 hour of Claude work.
