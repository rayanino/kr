# KR Autonomous Period Deep Research: Dashboard, DR Response Ingestion, Long-Gestation Ideation

## Repo-grounded constraints that should dominate every design choice

KR’s autonomous period is explicitly framed as “everything slow now, everything fast later”: the system’s purpose is to eliminate “we need to research this first” blockers before summer, with Deep Research prompts as the highest-priority pillar. fileciteturn2file0L1-L1

The owner interaction model is also unusually strict: you are the client, not a developer; the system should never require you to touch terminal/repo/code, and it should be silent by default (no progress pings) with the browser dashboard as the only interface. fileciteturn2file0L1-L1

State must be persistent and machine-first. The DESIGN doc defines the dashboard as a read-only “view onto persistent state” plus input forms, with data stored as JSON/JSONL under an autonomous knowledge base. fileciteturn2file0L1-L1

There are two “hard” governance constraints in the current branch that materially affect dashboard + pipeline engineering:

- First, `.kr/` is treated as a forbidden edit prefix by the Codex safety layer (`FORBIDDEN_EDIT_PREFIXES` includes `.kr/`), which is why the DESIGN doc amends the planned knowledge-base location from `.kr/autonomous/` to `overnight_codex/autonomous/`. fileciteturn2file0L1-L1 fileciteturn8file0L1-L1  
- Second, the canonical autonomous-doctrine file you referenced is *actually missing on this branch*, and ACTIVE_AUTHORITY explicitly warns to keep operation conservative until that control-plane gap is repaired. fileciteturn24file0L1-L1

Finally, the repo already encodes a strong “local web GUI” preference: `requirements.txt` explicitly includes FastAPI + Uvicorn + Jinja2 + python-multipart as “Web GUI (D-043: FastAPI + HTMX)”, and the archived GUI decision doc (D-043) argues for an HTMX + server-rendered template approach specifically because Claude Code can build it fluently and because it avoids a heavy JS framework at MVP stage. fileciteturn40file0L1-L1 fileciteturn43file0L1-L1

## Dashboard technology decision

### Scored comparison table

Scoring scale: 1 (poor) → 5 (excellent). Weighted total is out of 5.

| Candidate | Agent maintainability (30%) | Zero-config launch (25%) | Interactivity (20%) | Offline/local (15%) | Data binding to repo JSON/JSONL (10%) | Weighted total |
|---|---:|---:|---:|---:|---:|---:|
| Static HTML + vanilla JS (open `index.html`) | 3 | 5 | 2 | 5 | 2 | **3.50** |
| Python local server (FastAPI + HTMX) | 5 | 4 | 5 | 5 | 5 | **4.75** |
| Single-file HTML app (TiddlyWiki-style) | 2 | 5 | 3 | 4 | 1 | **3.15** |
| Other: Streamlit-style local app | 4 | 3 | 4 | 4 | 4 | **3.75** |

### Recommendation

**Recommend: FastAPI + HTMX + Jinja templates, run locally as a tiny read/write web server over the knowledge-base files.**

This is the only option that cleanly satisfies *all* of your required dashboard behaviors **without hidden workflow debt**:

- You don’t just need a “viewer.” You need *input forms* that persist to the repo’s state (ideas/feedback, DR response path submission, queue actions). Static or single-file HTML cannot reliably write to the repo filesystem in a cross-browser, zero-setup way; a local server can. This matches the DESIGN doc’s requirement that the dashboard be input-capable and a view onto stored state. fileciteturn2file0L1-L1  
- The repo already standardized on FastAPI + HTMX as the preferred GUI MVP stack (D-043), and those dependencies are already in `requirements.txt`, which matters for agent-maintained infrastructure: fewer new tools, fewer “LLM fights,” fewer environment surprises. fileciteturn40file0L1-L1 fileciteturn43file0L1-L1  
- A local server gives *natural* data binding: it can read `relay_queue.json`, stream JSONL feeds, render charts from `metrics.json`, and expose deliberate mutation endpoints that append to JSONL or atomically rewrite JSON using existing repo patterns (see `atomic_write()` and JSONL append helpers in the overnight system utilities). fileciteturn8file0L1-L1  
- It also composes directly with existing runtime artifacts you already get “for free” from the overnight orchestrator: `overnight_codex/state.json`, `.heartbeat`, `run_snapshots/*.json`, and `MORNING_REPORT.md` are all stable dashboard inputs because the orchestrator already writes them. fileciteturn3file0L1-L1 fileciteturn8file0L1-L1

### Five-file architecture sketch for the recommended dashboard

This is intentionally minimal: one server, one storage layer, one template, one client-side behavior file, one launcher. It is designed to be modified by agents without sprawling a frontend framework.

| File | Responsibility | Reads | Writes |
|---|---|---|---|
| `scripts/autonomous_dashboard/app.py` | FastAPI app, route definitions, HTMX endpoints, “page = composed view model over persistent state” | `overnight_codex/autonomous/**`, plus `overnight_codex/state.json`, `overnight_codex/run_snapshots/**`, `overnight_codex/MORNING_REPORT.md` | none directly (delegates writes to store layer) |
| `scripts/autonomous_dashboard/store.py` | Single source of truth for file IO: atomic JSON writes, JSONL appends, safe concurrent reads, path normalization (Windows/WSL) | same as above | `ideas.jsonl`, `history.jsonl`, `relay_queue.json`, `research_gaps.json`, `dashboard/state.json` (all under `overnight_codex/autonomous/`) |
| `scripts/autonomous_dashboard/view_models.py` | Deterministic “dashboard projections”: queue ordering, deduped findings, metrics aggregates (for charts), health summaries | `relay_queue.json`, `findings.jsonl`, `metrics.json`, `run_snapshots/*.json` | none |
| `scripts/autonomous_dashboard/templates/index.html` | Single page layout with HTMX partials: relay queue, findings feed, owner input form, health, charts containers | view model rendered by server | none |
| `scripts/start_autonomous_dashboard.ps1` | One-command Windows entrypoint: starts server (prefer WSL if that’s the canonical unattended lane), opens browser to `http://localhost:<port>` | n/a | n/a |

**Data flow (tight loop, no magic):** overnight run writes runtime artifacts → prompt generator writes to `overnight_codex/autonomous/relay_queue.json` + JSONL feeds → dashboard server reads and renders → owner actions POST to server → server appends/atomically updates the same JSON/JSONL files → next overnight cycle consumes updated state.

This “projection over files” exactly matches the repo’s existing operational style: the orchestrator persists state to JSON (`state.json`) and writes reports/snapshots that are meant to be read by humans and machines. fileciteturn3file0L1-L1 fileciteturn8file0L1-L1

## DR response processing pipeline design

### Recommendation

Implement the DR response ingestion as a **separate, owner-triggered pipeline** (CLI + dashboard endpoint) whose core is a **Markdown-to-IR block parser** (not regex scraping) plus a deterministic classifier with explicit uncertainty handling.

This matches the DESIGN doc’s Codex feasibility amendment: the orchestrator’s synchronous loop cannot “wait for a human relay step,” so DR response ingestion must be decoupled into its own script (`scripts/process_dr_response.py <path>`). fileciteturn2file0L1-L1

### Pipeline stages and artifacts

**Ingestion**  
Input: absolute/relative path to a `.md` file downloaded from ChatGPT/Claude/Gemini DR.  
Actions: validate existence; read as UTF-8 with replacement; compute `response_sha256`; record tool source (ChatGPT/Claude/Gemini) when provided; store raw text snapshot.  
Persist:
- `overnight_codex/autonomous/knowledge_base/dr_responses/raw/<response_id>.md` (exact raw copy)  
- `overnight_codex/autonomous/knowledge_base/dr_responses/index.jsonl` (one record per response: ids, timestamps, source, hashes, status)

**Parsing**  
Goal: extract “candidate findings” from unpredictable Markdown structures without depending on a fixed template.  
Recommended approach: build a **block-level Markdown IR** via a state-machine tokenizer that recognizes only the stable constructs that matter:

- headings (`#…####`) tracked as a stack (creates a section path context)  
- unordered/ordered list items (including nested indent levels)  
- code fences (``` blocks)  
- tables (pipe tables, captured as rows)  
- paragraphs (coalesced runs of text)

This is “not brittle regex” because it’s structure-first: you identify blocks by simple lexical markers and maintain parsing state (e.g., “inside code fence”), rather than scraping patterns like “Recommendation:” everywhere. The repo already uses structured fallback conversion from Markdown into JSON for Codex task results (`_payload_from_markdown` extracts sections, parses bullets, then produces a canonical structured payload). That’s proof the codebase accepts “convert Markdown → stable JSON” as a runtime pattern; the DR pipeline is the same idea, but needs a more general block parser because DR output formats vary more. fileciteturn3file0L1-L1

**Classification**  
Each candidate finding gets:
- `finding_type ∈ {architecture_decision, edge_case, scholarly_insight, technology_recommendation, risk, open_question}` (exact set you specified)  
- `confidence ∈ [0.0, 1.0]` plus `rationale` (short, deterministic reasons: keyword hits, section context)  
- `evidence_spans`: pointers back to the parsed IR nodes (heading path + block index), and optionally quoted substrings (short excerpts)

Mechanism: deterministic rules with confidence weighting, driven by two signals:
1) **Section context**: heading path (e.g., under “Risks” or “Open questions”)  
2) **Lexical cues**: “should”, “recommend”, “risk”, “unknown”, “edge case”, “fails when”, “consider”, “tradeoff”, “open question”, etc.

If confidence < threshold (e.g., 0.65), do **not guess**: classify as `open_question` (or `risk` if clearly negative) and mark `needs_review=true`. This aligns with the repo’s doctrine “stagnation over corruption” in evaluator language (binary pass/reject, no provisional) and avoids silently misfiling scholarship-sensitive content. fileciteturn27file0L1-L1

**Cross-referencing against the knowledge base**  
You need deduplication and linkage, not just storage.

Recommended scheme:
- Compute `finding_fingerprint = sha1(normalize_text(finding_text) + finding_type + sorted(referenced_paths))`
- Maintain an index `findings_registry.json` (similar to how the overnight system maintains its own findings registry and tracker) that maps fingerprint → canonical finding record, with occurrence counters and last-seen timestamps. The repo already does this for creative findings (`findings_registry.json` and `FINDINGS_TRACKER.md` are updated by `append_codex_findings.py`); reuse the same conceptual model for DR findings so the dashboard “findings feed” can show “what’s new since yesterday” and “what keeps recurring.” fileciteturn46file0L1-L1  
- For linkage: also maintain `dr_index.json` mapping `prompt_id ↔ response_id ↔ finding_fingerprint[]` (the DESIGN doc calls out a master index for prompt/response status and findings). fileciteturn2file0L1-L1

**Gap update**  
The DESIGN doc expects `research_gaps.json` to be a core artifact. fileciteturn2file0L1-L1  
Recommended mechanics:
- Represent gaps as a dict keyed by `gap_id` (string), with status `open|resolved|superseded`, plus `priority`, `created_at`, `resolved_at`, `source`, and `resolution_evidence` linking to `(response_id, finding_fingerprint)`.  
- Close a gap when you see an `architecture_decision` or `technology_recommendation` finding that explicitly answers it, or when a follow-up prompt is generated that reframes it (mark previous as superseded).  
- Use **atomic JSON writes** so the dashboard never reads a half-written file. The overnight runtime already has `atomic_write()` for precisely this durability problem (with fsync before rename), and uses atomic JSON writes for durable state like `state.json`. fileciteturn8file0L1-L1 fileciteturn3file0L1-L1

**Follow-up generation**  
Follow-ups should be generated only from:
- `open_question` findings with high priority or strong “unblocks X” linkage  
- `risk` findings that imply unknown behavior  
- conflicts: multiple findings that disagree

Each follow-up prompt record should include:
- `target_dr` (ChatGPT DR vs Claude DR vs Gemini DR) using the DESIGN doc’s capability mapping, and strictly respecting its rule: *never paste file contents into ChatGPT/Claude DR prompts; give file paths.* fileciteturn2file0L1-L1  
- `what_it_unblocks` (required field, because the “time economics” framing makes unblock-value the metric that matters) fileciteturn2file0L1-L1  
- `dedup_hash` to avoid re-asking already answered questions  
- `prompt_text` plus an explicit expected output format request

Persist follow-ups into `overnight_codex/autonomous/relay_queue.json` as “pending prompts,” and ensure queue updates are atomic (the DESIGN doc explicitly moved from directory-based queue state to a single JSON file for atomicity). fileciteturn2file0L1-L1

### Error handling that prevents silent corruption

The pipeline should be fail-loud and degrade gracefully:

- Empty file or whitespace-only: ingest record with `status="invalid_empty"`, do not update gaps, do not generate follow-ups, and surface an error card on the dashboard (this matches the repo’s general approach: don’t silently proceed when evidence is missing). fileciteturn2file0L1-L1  
- Malformed encoding: read with replacement but record `encoding_warnings=true` and store raw bytes hash; do not normalize Arabic content (Gemini review amendments in DESIGN.md explicitly warn about Arabic text safety and prohibitions like unsafe normalization/strip patterns). fileciteturn2file0L1-L1  
- Parser failure: persist raw response and emit `parse_error` with traceback summary; classify nothing rather than guessing; optionally generate a single follow-up prompt asking the DR tool to reformat into a more parseable structure (but only if you can do so without wasting relay budget).

## Long-gestation creative idea generation framework integrated with the existing evaluator

### Recommendation

Adopt a closed-loop framework I’ll call **Idea Quarry → DR Validation → Summer-Ready Packaging**, where every idea is forced to be repo-grounded *by construction* (paths + contract symbols + insertion boundary), then validated by 1–3 DR prompts, then only marked “summer-ready” when it meets the DESIGN doc’s readiness bar *and* passes the evaluator’s quality gate.

This is explicitly consistent with how KR already measures “creative output quality”: `overnight_codex_evaluator.py` is a deterministic measurement instrument built around “golden-example” characteristics, with tight anti-hallucination checks (evidence fidelity) and shallow-idea detection patterns. fileciteturn27file0L1-L1 fileciteturn36file0L1-L1

### How the framework executes autonomously without drifting into generic brainstorming

**Idea Quarry (systematic grounding source)**  
Instead of “brainstorm,” the system mines *repo artifacts* that imply long-gestation opportunities:

- Cross-engine boundary stress: the evaluator itself encodes “known boundary patterns” (source→normalization→…→synthesis) as a signal of architectural awareness; ideas must anchor themselves at a boundary, not as an isolated feature. fileciteturn27file0L1-L1  
- Deferred or under-specified areas: DESIGN.md lists (and Gemini review amendments expand) gap scanners beyond simple `[OPEN]` markers—foundational principles, adversarial tests, domain rules, and deferred capabilities are explicitly called out as better idea sources. fileciteturn2file0L1-L1  
- Existing GUI doctrine (D-043) shows that the project already values “upgradeable MVPs” and “no JS framework for MVP” logic; the creative system should propose comparable architecture reframes, not micro-refactors. fileciteturn43file0L1-L1

**Idea Card synthesis (the non-negotiable schema that prevents generic output)**  
Each idea must be produced in a schema that the evaluator can score, meaning it must include these fields (the evaluator’s hard expectations):

- `current_system_limit` (deep enough; evaluator enforces minimum word count) fileciteturn27file0L1-L1  
- `proposed_reframe` (must *not* match shallow patterns like “use library X instead of Y”; evaluator has an expanded shallow-pattern detector) fileciteturn27file0L1-L1  
- `primary_insertion_boundary` (must resolve to real contracts/spec paths or match known boundary patterns) fileciteturn27file0L1-L1  
- `owner_value_statement` (must reference study/learning experience; evaluator explicitly looks for study keywords) fileciteturn27file0L1-L1  
- `benefits[]`, `risks[]`, `secondary_required_changes[]` (and at least some secondary changes must reference real repo paths; evaluator checks that deterministically) fileciteturn27file0L1-L1  
- At least 2–3 contract symbols from the evaluator’s `SYMBOL_REGISTRY` (this is the built-in anti-hallucination mechanism: it checks that claimed symbols exist in real `contracts.py` files) fileciteturn27file0L1-L1

Critically: this schema forces ideas to be “about KR” (contracts, boundaries, file paths, owner study value), not generic platform advice.

**Evaluator integration (do not replace; use as the first gate)**  
Immediately after an Idea Card is generated:

1) Run the evaluator (`evaluate_creative_output`) to compute per-dimension results and pass/reject verdict. The evaluator is explicitly binary (“pass” or “reject,” no provisional) and is designed to prevent “dressed-up cleanup” from being mistaken as strategic ideation. fileciteturn27file0L1-L1  
2) If it fails, the creative engine should *revise the idea*, not ship it: the rejection reasons are already structured per dimension (repo grounding, strategic depth, concreteness, evidence fidelity, inflation). fileciteturn27file0L1-L1  
3) Only “pass” ideas enter the research phase. This is the bottleneck-first move: it prevents wasting DR relays validating low-grade ideas.

**DR validation phase (1–3 DR prompts per idea, targeted by capability)**  
Your DESIGN doc already defines this pattern for owner ideas and for pillar-3 creative lifecycle: ideas trigger DR research before implementation is even considered. fileciteturn2file0L1-L1

For each passed Idea Card, generate:
- 1 prompt to ChatGPT DR: feasibility, architecture, failure modes (repo paths only)  
- 1 prompt to Claude DR: boundary correctness, scholarly integrity risks, edge-case traps (repo paths only)  
- optional 1 prompt to Gemini DR: Islamic methodology/pedagogy framing (requires file bundle; DESIGN doc notes Gemini “no repo access”) fileciteturn2file0L1-L1

This phase is also where you enforce “long-gestation only”: the prompts must explicitly ask for multi-week implications (dependency graph, contract evolution, test strategy, and research tasks), not quick fixes.

**Summer-ready definition (explicit, testable gate)**  
Do not invent a new readiness definition: the DESIGN doc already defines “summer-ready” for creative ideas as requiring multiple DR reports, multiple coworker validations, a concrete implementation sketch, dependency identification, and owner briefing (brief-before, not approval-gate). fileciteturn2file0L1-L1

Operationalizing that into a deterministic gate:

An idea is `summer_ready=true` only when all are present:
- `evaluator_verdict == "pass"` AND `idea_class_evaluator ∈ {"major","benchmark_grade"}` (thresholds are encoded in evaluator logic) fileciteturn27file0L1-L1  
- `dr_reports_count >= 2` with stored response_ids and extracted findings linked back into the idea record  
- `peer_validations >= 2` where “peer major coworkers” are Claude Code and Gemini CLI per coworker policy fileciteturn20file0L1-L1  
- `implementation_sketch` exists and references specific repo paths/contracts  
- `dependencies[]` list exists, with explicit “blocked/unblocked” status

**Where this plugs into the existing overnight machinery**  
You already have a creative task channel in the task generator: it loads creative templates, enforces read-only mode, and caps creative tasks to ~37% of the manifest. fileciteturn7file0L1-L1  
You also already have a runtime mechanism to ingest creative “actionable” findings and track them in a registry. fileciteturn46file0L1-L1

So the clean integration is:

- Templates generate Idea Cards (creative.json) → evaluator scores them → passed cards generate DR prompts into the relay queue → owner relays → response pipeline (from the prior section) ingests DR responses and updates idea status → when summer-ready, write a single “summer packet” artifact per idea.

This reuses the existing operational invariant: tasks produce structured JSON, and host-side scripts persist canonical state and trackers.

## Critical risks and the single best next move

The biggest structural risk visible in the branch is **control-plane incompleteness**: the canonical doctrine file the system is supposed to obey is missing, and ACTIVE_AUTHORITY explicitly says to keep operation conservative until that gap is repaired. fileciteturn24file0L1-L1 This is a real blocker because multiple docs defer exact degraded-mode behavior and promotions to that missing doctrine file. fileciteturn18file0L1-L1 fileciteturn19file0L1-L1

The single best next move (highest leverage, lowest regret) is therefore:

**Restore or replace `docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md` on this branch, and make the dashboard + DR pipeline treat it as read-only policy input (never mutated by the runtime).**

That action unblocks safe automation gates, degraded-mode rules, and stop/rollback behavior that you otherwise have to guess—which the repo itself warns against (“stagnation over corruption,” “do not infer policy from missing doctrine”). fileciteturn24file0L1-L1 fileciteturn27file0L1-L1