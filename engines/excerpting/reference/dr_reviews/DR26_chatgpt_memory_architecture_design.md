# Ideal Persistent Memory Architecture for KR

## Understanding the current system

### What KR already has today

KR’s memory system is not “a single component”; it is a **stack** spanning (a) governance docs, (b) session continuity artifacts, (c) a curated memory library, and (d) enforcement hooks that force agents to behave as if memory matters.

**Governance and non-negotiables are explicitly centralized.** `CLAUDE.md` defines the project’s identity (“engineering team, not assistant”), the pipeline-first doctrine, and “Critical Rules” such as result preservation and “ALL data is future training material.” fileciteturn12file0

**Session continuity is formalized and unusually high-rigor.** `NEXT.md` acts like a control-tower runbook: it declares the owner’s role boundaries, enumerates what counts as blocking owner input, and establishes a roadmap and gate structure for ongoing work. It also operationalizes multi-coworker usage and specifies dispatch logs and artifacts. fileciteturn3file0

**Context discipline is codified and coupled to tooling.** `.claude/rules/context-management.md` says “one engine per session,” mandates proactive compaction around ~60%, and instructs agents to use `/catchup` instead of relying on conversational continuity. It also explicitly constrains MCP server usage due to context cost. fileciteturn19file0

**Hooks enforce behavior and persist state.** `.claude/settings.json` is doing real systems work: it blocks destructive commands, enforces pre-push tests, runs lint/type-check/tests after edits, captures state on stop, and runs pre/post-compaction checkpoint logic. fileciteturn4file0

**A persistent session snapshot already exists.** `scripts/session_stop.py` writes `.claude/session_state.json` capturing branch, active engine, recent commits, modified files, a head excerpt from `NEXT.md`, budget summary from a cost log, and warnings like stray `print()` in modified source. This is a strong “current-state” memory layer for recovery. fileciteturn18file0

**Stale reference drift detection is already partially implemented.** There is a staged-file hook that runs a stale-reference checker over `.claude/` Markdown/shell files. fileciteturn20file0 The checker extracts likely file-path references and reports missing targets. fileciteturn21file0

**A curated “Project Memory” index exists, plus typed memory entries.** `MEMORY.md` is a human-designed index of the memory corpus, organized by engine and operational domains, and points to individual memory notes whose frontmatter encodes at least `name/description/type` (e.g., `feedback`, `project`, `user`). fileciteturn0file1 fileciteturn0file5

**Autonomous operation is already treated as a first-class system with explicit constraints.** The “Autonomous Deployment Status” memory file defines a 3‑month autonomous window, daily schedule, CLIs, phase rotation config, and a gating/authority model. fileciteturn0file8

### Structural strengths

KR’s current system has four strengths that matter at scale (and are rarer than they should be in AI-assisted development workflows):

**Strong normative layer, reinforced by automation.** The combination of explicit governance (what the system must do) and hooks (what the system physically can’t do) reduces “norm decay” risk. The settings file explicitly bakes in guardrails (tests before pushing, prompt enforcement, Arabic safety checks, cost guards). fileciteturn4file0

**Clear division between owner authority and technical authority.** This is repeated in `CLAUDE.md`, `NEXT.md`, and memory feedback files: owner is a client and relay; the agent is responsible for architecture and next steps. fileciteturn12file0turn3file0turn0file5 This is essential if you want autonomous overnight operation to converge rather than stall.

**“Result preservation” is treated like an invariant, not an optimization.** The principle that every API call output is sacred and must be persisted is explicitly present as a core rule. fileciteturn12file0turn0file3 That’s aligned with KR’s goal of using all artifacts as future training material. fileciteturn12file0

**Memory isn’t just “notes”; it includes runtime state, dispatch logs, and operational protocols.** `NEXT.md` references a dispatch log path and formal gate checklists, and session_stop persists cost/budget status. fileciteturn3file0turn18file0 This moves KR closer to an “operational memory system” instead of a static wiki.

### Structural weaknesses and likely failure modes as KR scales

The core issue is not “you need semantic search.” KR’s problem is: **the current memory system does not yet have a clean separation between immutable history and curated doctrine**, and it does not yet have enough machine-checkable structure to remain coherent during autonomous expansion.

The most important weaknesses:

**A single human-curated index does not scale as the primary discovery mechanism.** `MEMORY.md` is already truncated (“truncates at 200” per your description), and in the provided excerpt we see link-strings that are visually abbreviated (ellipsis) rather than reliably dereferenceable paths. fileciteturn0file1 When you grow from ~79 to 200+ memories, a manually maintained index becomes a bottleneck and a drift source: it will lag reality, and retrieval will silently regress (the worst possible failure mode for KR, which forbids silent defaults). fileciteturn12file0turn0file3

**Critical invariants are already inconsistent across “top of stack” documents.** Two examples visible in the provided corpus:
- `CLAUDE.md` describes a 7-engine pipeline (`source → normalization → passaging → atomization → excerpting → taxonomy → synthesis`). fileciteturn12file0
- `principles.md` describes the prime directive as building a “5-engine pipeline.” fileciteturn0file3  
This is not a cosmetic mismatch: in a multi-agent setting, inconsistency at the invariant layer causes agent divergence, redundant work, and higher defect rates. KR’s current stale-reference checker detects broken file paths, but it does not detect semantic contradictions like this. fileciteturn21file0

**The memory corpus is typed but not yet schema-governed.** Sample memory entries include YAML frontmatter with `name/description/type`, but there is no evidence (in the reviewed files) of enforced required fields like `created_at`, `supersedes`, `scope`, `engine`, `decision_id`, or `source_artifacts`. fileciteturn0file5turn0file7turn0file8turn0file9 Without a schema, autonomous agents will write heterogeneous notes, and retrieval quality will decay long before you reach 200 files.

**No canonical append-only “event log” for decisions and outcomes is evident yet.** `scripts/session_stop.py` writes a snapshot (`session_state.json`) that is overwritten each session. fileciteturn18file0 That is excellent for recovery, but not sufficient for: (a) contradiction tracing, (b) proving why a decision was made, (c) reconstructing a timeline for training data, or (d) auditing overnight output.

**Autonomous overnight operation increases write concurrency and “entropy.”** Your autonomous deployment plan runs daily, multi-cycle, generating queue artifacts and findings. fileciteturn0file8 Without a structured ingestion layer (append-only + validated summaries), “overnight findings” will either (1) remain stranded in logs no one reads, or (2) leak into curated doctrine without enough provenance.

**Cross-agent interoperability is expensive because DR agents have no repo access.** `NEXT.md` explicitly states that DR sessions require fully self-contained prompts (copy/paste of contents), and `CLAUDE.md` mandates frequent DR usage. fileciteturn3file0turn12file0 As sessions scale into the hundreds, manually assembling DR packets becomes a major coordination cost unless memory is structured enough to auto-build “context packs.”

### Where it breaks when scaling engines and autonomy

Scaling pressure points under your stated trajectory (79 → 200+ memories, 5 → 7 engines, human-supervised → overnight autonomous):

**Retrieval breaks first.** Grep can still work at 200 files, but only if filenames, tags, and structure are consistent. Inconsistent memory note structure makes grep brittle, while semantic retrieval requires clean chunking and metadata. KR currently has strong discipline around not relying on stale conversational memory, but not yet a scalable retrieval substrate for large corpora. fileciteturn19file0turn0file1

**Consistency breaks second.** The 5-engine vs 7-engine mismatch is a preview. fileciteturn12file0turn0file3 At 200+ notes, you will get “policy drift” unless contradictions are detectible and resolvable via process.

**Doctrine/decision provenance breaks third.** KR’s ethos requires traceability, immutability of sources, and preservation of outputs. fileciteturn12file0 But without a unified event-sourced log (immutable history) plus materialized summaries (curated doctrine), you can’t reliably answer questions like “what did we decide and when, and based on which evidence?”

## Evaluating MemPalace

### What MemPalace actually is architecturally

MemPalace positions itself as an offline-first “store everything, make it findable” memory stack, organized as a palace hierarchy and backed by ChromaDB for retrieval. citeturn4view0 Its repo explicitly describes:
- A hierarchy: wings (people/projects) → halls (types) → rooms (ideas). citeturn4view0
- A 4-layer memory stack (L0–L3) exposed in its package docs. citeturn6view0
- A ChromaDB-backed semantic search path. citeturn4view0turn6view0
- A temporal SQLite knowledge graph storing entity/triple relationships with `valid_from/valid_to` and time-filtered queries. citeturn11view2turn11view3
- An MCP server exposing tools and an “agent diary” facility. citeturn4view0turn13view3
- Conversation mining support for multiple export formats to a normalized transcript representation. citeturn6view0

### Palace hierarchy versus KR’s current structure

MemPalace’s hierarchy is a **navigation taxonomy** primarily optimized for human intuition and structured retrieval filters. citeturn4view0turn6view0 KR’s current system is closer to a **flat-ish curated notebook set plus an index**, with type hints in frontmatter and topical grouping in the index. fileciteturn0file1turn0file5

What MemPalace gets right (conceptually) that KR should copy, even if not the implementation:
- **Separate “how memory is filed” from “how memory is searched.”** Wings/rooms become query filters rather than relying on filenames. citeturn6view0
- **Explicitly model multi-layer memory (boot layer vs deep search).** KR already has a practical analogue (governance docs + NEXT + session recovery) but not yet as a formal memory compilation pipeline. fileciteturn12file0turn3file0turn18file0

### AAAK compression: useful idea, but MemPalace’s claim is not credible as-is

MemPalace’s README claims AAAK is “lossless,” achieves “30x compression,” and loads “months of context in ~120 tokens.” citeturn4view0

But the implementation in `dialect.py` is explicitly **heuristic extraction** (entities/topics/key sentence/emotion flags) into a “symbolic representation,” and the `decode()` function is described as parsing AAAK back into a “readable summary,” not reconstructing original text. citeturn9view0turn8view3 This is, by construction, **lossy summarization**. For KR, where Arabic text fidelity and provenance preservation are existential requirements, a lossy “dialect” should only ever exist as a derived cache, not as canonical memory. fileciteturn12file0turn0file3

In KR terms: AAAK can be valuable only as a **strictly derivative bootpack** (fast-to-load context seed) whose contents are provably traceable to canonical sources. Anything else conflicts with KR’s “never delete data” and “bytes never change” posture. fileciteturn12file0

### ChromaDB + SQLite semantic search: likely useful, but not in MemPalace’s “one size fits all” form

MemPalace argues that “raw verbatim text with good embeddings” is a surprisingly strong baseline on LongMemEval. citeturn5view0

Two important caveats for KR:
- LongMemEval is a benchmark for long-term interactive chat memory (multi-session reasoning, temporal reasoning, updates, abstention). It does not directly measure KR’s domain-specific needs like Arabic fidelity or SPEC compliance. citeturn0search5turn0search0
- KR is not just conversation memory. It is also codebase state, tests, prompts, Arabic conventions, evaluation traces, and owner feedback—all of which require **typed retrieval** and **provenance**.

That said, KR’s current “prefer grep” posture is rational early on (fewer moving parts; deterministic). fileciteturn19file0 But as the corpus grows to include hundreds of sessions plus preserved raw LLM outputs (which KR explicitly mandates), full-text + semantic indexing becomes high leverage. fileciteturn12file0turn0file3

The MemPalace concept worth adopting is not “ChromaDB specifically,” but:
- **Hybrid retrieval:** lexical for precision + semantic for recall (especially for paraphrased “why” questions).
- **Metadata filtering:** wing/room (or KR equivalents) as structured query constraints. citeturn6view0turn5view0

### MCP server duplication: likely harmful for KR

MemPalace positions MCP as the primary integration channel (adds a server that exposes 19 tools). citeturn4view0turn13view3 KR’s own context management explicitly warns that MCP tools consume context and says to keep enabled MCP servers ≤5, preferring local CLI wrappers for simple operations. fileciteturn19file0

Given KR’s existing hooks + scripts + governance, adding another large MCP server is likely to:
- Increase operational surface area (more failure modes) during autonomous runs.
- Increase context/tool overhead in interactive sessions.
- Duplicate functionality that KR can implement as scripts invoked by bash hooks (consistent with current discipline). fileciteturn4file0turn19file0

### Conversation mining: high value for KR, but the ingestion target should differ

MemPalace supports mining multiple chat export formats into normalized transcripts, and explicitly highlights conversation mining as a core feature. citeturn4view0turn6view0

For KR, this is one of the biggest “missing leverage points” because:
- KR runs across many modalities (Claude Code, Codex CLI, Gemini CLI, multiple DR windows). fileciteturn3file0turn12file0turn0file8
- DR sessions are especially high ROI per KR’s own doctrine. fileciteturn12file0turn0file1
- “All data is future training material” implies past sessions should be preserved and re-indexable. fileciteturn12file0

So: adopt **the idea of transcript mining**, but ingest into **KR’s own canonical artifact store**, not into an external “palace” database that becomes another source of truth.

### Contradiction detection: solves a real KR problem, but must target KR’s invariants

MemPalace includes a temporal knowledge graph with explicit fact invalidation (`valid_from/valid_to`, `invalidate`, `as_of` queries). citeturn11view1turn11view3 This style of temporal modeling is relevant to KR’s needs: KR’s project doctrine changes over time (protocol versions, prompt rules, engine boundaries), and today you already have invariant inconsistencies such as 5-engine vs 7-engine. fileciteturn12file0turn0file3

However, KR does not need a person-centric fact graph first. It needs **doctrine/decision temporal validity**:
- “Which rule set was active on date X?”
- “Which prompt version and FP set governed the excerpting run that produced these artifacts?”
- “Which owner preferences were confirmed vs tentative at the time?” fileciteturn3file0turn0file7turn0file9

### 96.6% LongMemEval R@5: impressive, but not decisive for KR’s design

MemPalace claims 96.6% LongMemEval R@5 without API calls and 100% with reranking. citeturn4view0turn5view0 LongMemEval itself measures five long-term memory abilities and is positioned as a benchmark for chat assistants’ long-term interactive memory. citeturn0search5turn0search0

For KR:
- This metric is **partially relevant** (KR has multi-session agent continuity and retrieval needs).
- But it’s **not sufficient**. KR’s correctness constraints (Arabic fidelity, SPEC alignment, provenance, human gates) demand additional evaluation dimensions that LongMemEval does not capture. fileciteturn12file0turn0file3turn0file7

### Verdict on what to adopt, ignore, or avoid

Adopt (conceptual, adapted to KR):
- **Conversation mining + normalization into a canonical transcript store** (KR-owned). citeturn6view0turn4view0
- **Temporal validity modeling** for decisions/doctrine (MemPalace’s `valid_from/valid_to` idea, but applied to KR policies and prompts). citeturn11view0turn11view3
- **Multi-layer memory compilation** (boot layer + deep retrieval), but implemented as KR context packs rather than AAAK. citeturn6view0turn4view0

Ignore (low ROI / mismatched to KR constraints):
- AAAK as a canonical representation. The implementation is lossy and conflicts with KR’s preservation posture. citeturn9view0turn8view3 fileciteturn12file0

Avoid (actively harmful to integrate now):
- A large extra MCP server/tool suite that competes with KR’s existing discipline and increases operational surface area. citeturn4view0turn13view3 fileciteturn19file0turn4file0

## Surveying the landscape

### What leading AI coding tools do for “memory”

Across mainstream AI coding tools, “memory” typically means one of two things:

**Persistent prompt context (rules), not externalized knowledge stores.** Cursor’s documentation frames rules as “persistent, reusable context at the prompt level” because models do not retain memory between completions; rule contents are injected at the start of the context. Cursor also lists “Memories” as automatically generated rules based on conversations. citeturn14search5turn14search3

**Local, tool-managed “memories” plus repo-committed “rules.”** Windsurf distinguishes auto-generated “Memories” (stored locally per workspace and not committed) from “Rules” stored in `.windsurf/rules/` or `AGENTS.md` for durable, shareable behavior constraints. citeturn14search0turn14search1

The pattern is consistent: production tools avoid making the repo a dumping ground of raw history; they store lightweight persistent instructions and rely on retrieval from the codebase for the rest.

KR differs because KR explicitly wants:
- Preservation of *all* outputs as future training material. fileciteturn12file0
- Autonomous operation without continuous human curation. fileciteturn0file8  
So KR must go beyond “rules files” into a true memory architecture.

### How retrieval-heavy workflows handle large codebases and tests

Aider’s “repository map” is a good example of a scalable compromise: it sends a concise, symbol-focused map of the whole repo to the model with each request, so the model can understand surrounding structure without reading everything. citeturn14search7

This is directly relevant to KR because:
- KR has thousands of tests and multiple engines. fileciteturn0file1turn0file7
- Autonomous agents need a stable way to rebuild “repo understanding” repeatedly without relying on chat history. fileciteturn19file0turn18file0

### What enterprise agent frameworks do for persistence and autonomy

Two production-grade patterns are especially relevant:

**Checkpointed state + thread identity (time-travel and fault tolerance).** LangGraph persistence saves graph state as checkpoints organized into threads, enabling memory across interactions, replay/time-travel debugging, and resumption after failures. citeturn16search0turn16search1 This is closest-in-spirit to what KR needs for overnight operation: autonomous steps must be replayable and auditable.

**Separation between per-thread memory and cross-thread memory stores.** LangGraph’s documentation explicitly motivates a `Store` interface because checkpointers alone don’t share memory across threads (e.g., user facts across conversations). citeturn16search0 This maps cleanly to KR’s multi-session resets: you need both session-local state and cross-session doctrine/policy.

### Mature “agent memory” systems: memory hierarchy and background consolidation

Letta (from the creators of MemGPT) formalizes memory as a hierarchy: in-context “core memory” blocks plus out-of-context recall and archival memory searchable via tools. citeturn15search0turn15search1 This is the OS‑style framing: keep a compact executive summary always visible, and retrieve the rest on demand.

MemGPT (the research origin) explicitly frames the problem as virtual context management inspired by OS memory hierarchies, paging between fast context and external storage. citeturn19search0turn19search6

LangChain’s “Deep Agents” documentation describes filesystem-backed memory, with explicit attention to **background consolidation**, read-only vs writable memory, and concurrent writes across multiple agents in the same deployment. citeturn16search5 This is unusually aligned with KR’s “autonomous overnight” constraint set.

### Temporal knowledge graphs as memory substrates

Zep’s Graphiti positions itself as a temporally-aware knowledge graph framework that maintains historical context and supports query via time + full text + semantic + graph algorithms. citeturn15search4turn15search2 MemPalace’s own knowledge graph is a simpler SQLite triple store with time validity ranges and `as_of` filters. citeturn11view2turn11view3

For KR, temporal modeling is valuable not because you need a fancy KG, but because **doctrine changes over time** and autonomous agents must know which rule set applied at the time an artifact was produced.

### Durable systems patterns that map well onto KR memory

KR’s memory constraints (“never delete,” autonomous operation, auditability) are structurally similar to event-sourcing and gitops patterns:

- Event sourcing: store the full series of actions as an append-only log to enable replay and auditability. citeturn18search9turn18search0
- GitOps: desired state is declarative and versioned in git; automated reconciliation makes the real world match. citeturn18search4turn18search6
- SQLite WAL provides a concrete example of write-ahead logging and checkpointing for durability and concurrency. citeturn17search0

KR should not literally “event source the whole repo,” but the design motifs (append-only history + derived materializations) are exactly right for a persistent memory system that must preserve training data.

## Designing the ideal system

### The design goal in one sentence

The ideal KR memory architecture is a **two-plane system**: an **append-only, provenance-rich historical record** (for audit/training/replay) plus a **curated, schema-governed doctrine layer** (for day-to-day agent guidance), with automated compilation into role-specific context packs.

This fits KR’s explicit invariants: pipeline-first, result preservation, multi-model consensus discipline, and autonomous operation. fileciteturn12file0turn0file3turn0file8

### Current-vs-ideal gap: what is missing (and what already exists)

Below is the most honest way to answer “how far is the current system from ideal”: treat it as maturity across critical dimensions.

| Dimension | Current KR state | What “ideal” requires |
|---|---|---|
| State recovery | Strong: `session_state.json` snapshot + hook-driven recovery patterns exist. fileciteturn18file0turn4file0 | Keep snapshot, but add immutable timeline and machine traceability linking snapshot → events. |
| Doctrine clarity | Strong intent, but inconsistent invariants (5-engine vs 7-engine). fileciteturn12file0turn0file3 | Enforced single source-of-truth for invariants with automated contradiction checks. |
| Historical provenance | Partial: outputs are to be preserved; cost logs and artifacts referenced; but no unified “decision/event log” layer is visible in reviewed files. fileciteturn12file0turn18file0 | Append-only event log capturing decisions, evidence pointers, and outcomes; never overwritten; queryable. |
| Memory structure | Partial: typed notes with minimal frontmatter; human index. fileciteturn0file1turn0file5 | Schema-governed notes with IDs, scope, status, supersession, and artifact pointers; index generated automatically. |
| Retrieval | Disciplined grep-first posture. fileciteturn19file0 | Hybrid: lexical + FTS + optional semantic embeddings, all driven by metadata filters. |
| Autonomous ingestion | Deployment exists; produces findings and queues. fileciteturn0file8 | Mandatory ingestion pipeline: overnight output → raw log → validated summaries → doctrine updates via gates. |

Net: KR is **ahead** on governance/enforcement and **behind** on structured, provenance-rich persistent memory (especially append-only history and contradiction management at the doctrine level).

### The ideal KR memory stack

#### Storage format

Use **three canonical artifact types**, each with strict roles:

**Type A: Immutable event records (append-only)**
- Format: `JSONL` (one event per line) + optional blob attachments.
- Purpose: canonical historical truth for training/audit/replay.
- Properties: never edited in place; corrections happen via new events that supersede or amend prior events.

**Type B: Curated doctrine and state (schema-governed Markdown)**
- Format: Markdown with YAML frontmatter and strict required keys.
- Purpose: “what agents should do now,” not raw history.
- Properties: editable but versioned in git; any change must reference the event(s) that justified it.

**Type C: Derived indexes (rebuildable)**
- Format: SQLite (FTS5) for full text + metadata; optional embeddings store.
- Purpose: accelerate retrieval across the large corpus.
- Properties: treated as cache; rebuildable from A/B.

This arrangement directly reconciles KR’s “never delete data” doctrine with the operational need to keep day-to-day guidance compact and coherent. fileciteturn12file0

#### Hierarchy and organization

Adopt MemPalace’s “hierarchy for filtering,” but implement it as KR-native directories + tags rather than a separate palace DB:

Proposed repo structure (illustrative):

```text
memory/
  doctrine/
    invariants.md
    user_model.md
    operations/
      autonomy.md
      budgets.md
      dispatch_protocol.md
    engines/
      excerpting_state.md
      taxonomy_state.md
      ...
    decisions/            # ADR-style decision records
      ADR_2026-04-07_autonomy_queue_only.md
  events/
    2026/
      04/
        sessions.jsonl
        dispatch.jsonl
        evaluations.jsonl
  artifacts/
    transcripts/
    dr_reports/
    run_outputs/
  index/
    memory_index.sqlite   # generated
    MEMORY.generated.md   # generated
```

Why this organization is ideal for KR specifically:
- It mirrors how KR actually reasons: invariants → active lane → evidence. fileciteturn3file0turn12file0turn0file7
- It cleanly supports cross-agent access: everything is in-repo and tool-agnostic. fileciteturn0file8turn19file0
- It makes “what changed and why” auditable (ADR + event pointers). citeturn17search2turn18search9

#### Retrieval mechanism

Build retrieval as a **compile step**, not as ad-hoc grepping:

**Step 1: Deterministic prefilter**
- Use metadata filters: `engine`, `type`, `status`, `date range`, `source_kind` (DR/CLI/owner/etc).
- This can be implemented without any embeddings.

**Step 2: Lexical retrieval**
- Use ripgrep-like search (fast, precise) for strict terms (IDs, filenames, FP numbers, SPEC sections). This aligns with current discipline. fileciteturn19file0

**Step 3: Full-text indexed retrieval**
- Use SQLite FTS (rebuildable cache) to search large transcripts and events, with stable performance as the corpus grows. SQLite WAL and checkpointing are a mature durability/concurrency pattern for this kind of workload. citeturn17search0

**Step 4: Optional semantic retrieval**
- Only after the above is stable: add multilingual embeddings for fuzzy “why” questions and paraphrase retrieval (especially across DR transcripts). This is conceptually aligned with LongMemEval-style findings that retrieval quality matters, but must be validated on KR’s own tasks. citeturn0search5turn5view0

#### Write triggers

KR already has strong hook infrastructure. The ideal system extends it with **structured write triggers** while keeping canonical memory centralized.

Key triggers:

**On session stop**
- Keep `session_state.json` snapshot (already exists). fileciteturn18file0
- Append a `session_end` event to `memory/events/YYYY/MM/sessions.jsonl` including:
  - agent identity (CC/Codex/Gemini)
  - branch + commit range
  - active engine + SPEC section
  - decisions made (with links or ADR IDs)
  - artifacts produced (paths + hashes)
  - tests run and results summary
  - budget delta (from cost logs)

The existing stop hook already calls `scripts/session_stop.py`. fileciteturn4file0turn18file0 This is the correct insertion point.

**On coworker dispatch**
- Write a `dispatch` event (prompt hash, target, objective, returned artifact path). `NEXT.md` already declares a dispatch log path; formalize it into the event store. fileciteturn3file0

**On DR ingestion**
- Store DR prompts and responses as transcript artifacts (Type A), then write a “synthesis/decision support” curated note (Type B) that references the raw artifact.

**On autonomous overnight run completion**
- Append an `overnight_cycle_end` event storing:
  - tasks attempted
  - diffs produced
  - failures encountered
  - which outputs are proposed-only vs mergeable
This prevents “overnight findings” from being lost or silently merged.

#### Staleness and contradiction management

The ideal system treats “staleness” as a first-class defect type (like failing tests), because stale doctrine causes agent failure.

Build three automated checks:

**Reference integrity** (already partially present)
- Extend the existing stale reference system beyond `.claude/` to include `memory/doctrine/` and `memory/decisions/`. The current checker scans `.claude/` files only. fileciteturn20file0turn21file0

**Invariant consistency**
- A machine-checkable list of invariants (pipeline stages, engine count, D‑rules like D‑023, etc.) extracted into one canonical file (e.g., `memory/doctrine/invariants.md`).
- A script that asserts: those invariants are not contradicted in other governance files (e.g., detect “5-engine” vs “7-engine”). fileciteturn12file0turn0file3

**Decision supersession correctness**
- Adopt ADR-style statuses (“Accepted”, “Superseded”, etc.) and enforce that superseding decisions link backwards. This aligns with widely used ADR practice: decisions are retained and superseding decisions reference what they override. citeturn17search2turn17search3

If you later add a temporal store, you can model validity ranges in a minimal way similar to MemPalace’s `valid_from/valid_to` and `as_of` filtering, but applied to doctrine items rather than personal facts. citeturn11view0turn11view3

#### Cross-agent access

The ideal system is “lowest common denominator” across:
- Claude Code sessions (hooks + repo file reads/writes). fileciteturn4file0turn19file0
- Codex CLI and Gemini CLI (direct repo access; overnight automation). fileciteturn0file8turn3file0
- DR agents with no repo access (must receive context via copied packs). fileciteturn3file0turn12file0

So the interface should be:
- **CLI-first** (a few `python3 scripts/memory/*.py` commands).
- **Context-pack generator**: outputs a bounded “DR packet” or “agent bootpack” built from doctrine + top relevant events, with strict provenance pointers.

This is consistent with KR’s preference for bash-wrapped tools over MCP bloat. fileciteturn19file0

#### Migration path from the current system

A safe migration must avoid violating KR’s “never delete” and “result preservation” ethos. fileciteturn12file0turn0file3

Migration steps:
1. **Mirror existing memory notes** into `memory/doctrine/legacy/` as-is (no edits), preserving the current system intact as historical artifacts.
2. **Introduce a frontmatter schema** and gradually upgrade only the “active lane” notes first (operations + excerpting + autonomy), because these drive ongoing decisions. fileciteturn3file0turn0file7turn0file8
3. **Generate (don’t hand-edit) the index.** Replace manual `MEMORY.md` as the primary index with an auto-generated `MEMORY.generated.md`. Keep the manual one as legacy until confidence is high. fileciteturn0file1
4. **Add append-only event logs** starting now (no backfill required initially). Optionally backfill later by mining old sessions.

## Implementation roadmap

This roadmap is constrained by KR’s own pipeline-first doctrine: memory work must directly improve correctness, autonomy, and long-term leverage, not become a distraction. fileciteturn12file0turn0file3

### Build natively within KR’s existing `.claude/` infrastructure

**Add an append-only session/event log that complements `session_state.json`.**  
What to build: extend `scripts/session_stop.py` to also append structured events (JSONL) to `memory/events/...`, including provenance pointers to artifacts, decisions, and tests.  
Why it matters for KR: it turns “state snapshot” into “state + history,” enabling replay, training data extraction, and contradiction resolution. fileciteturn18file0turn12file0  
Replaces/improves: the current overwrite-only nature of `.claude/session_state.json`. fileciteturn18file0  
Complexity: **moderate** (existing hook point exists). fileciteturn4file0  
Priority: **highest** (directly supports overnight autonomy and future training value). fileciteturn0file8turn12file0

**Auto-generate the memory index from frontmatter.**  
What to build: a script that scans memory notes, validates schema, and emits a generated index file.  
Why it matters: removes a growth bottleneck and reduces drift as you scale to 200+. fileciteturn0file1  
Replaces/improves: manual index maintenance and truncated/unreliable link strings. fileciteturn0file1  
Complexity: **moderate**.  
Priority: **high**.

**Invariant consistency checker (doctrine contradiction detection).**  
What to build: a lightweight script that asserts invariants (e.g., pipeline stage list, engine count) match across top documents; fail in CI or at least warn on stop.  
Why it matters: you already have contradictory invariant statements. fileciteturn12file0turn0file3  
Replaces/improves: reliance on human noticing contradictions.  
Complexity: **trivial to moderate**.  
Priority: **high**.

**Extend stale-reference checking beyond `.claude/`.**  
What to build: expand `check_stale_references.py` scope to include `memory/` doctrine and decision docs.  
Why it matters: prevents dead links as doctrine grows. fileciteturn21file0  
Replaces/improves: current check restricted to `.claude/` docs. fileciteturn21file0  
Complexity: **trivial**.  
Priority: **high**.

### Adopt from external tools

**Adopt the MemPalace “conversation mining” concept, not its database.**  
What to adopt: normalize exported transcripts across Claude/ChatGPT/etc into a canonical KR transcript artifact format (JSONL + metadata). MemPalace documents multi-format normalization/ming. citeturn6view0turn4view0  
Why KR-specific: DR is mandated as high ROI, but DR is disconnected from repo access; transcript mining lets you recover insights from hundreds of sessions into a searchable artifact store. fileciteturn12file0turn3file0  
What it replaces: ad-hoc “lost insight” recovery and manual searching of old chat logs.

**Adopt temporal validity modeling for doctrine/decisions (minimal).**  
What to adopt: the `valid_from/valid_to` concept used in MemPalace’s SQLite KG, but apply it to rule/decision validity rather than personal facts. citeturn11view0turn11view3  
Why KR-specific: protocol versions and prompt rule sets change; autonomous runs need to know what was valid when an artifact was produced. fileciteturn3file0turn0file7turn0file8

### Defer until after the pipeline is complete

**Vector DB / embedding search as a primary dependency.**  
Why defer: KR’s current grep-first discipline is aligned with keeping the active lane simple; semantic retrieval becomes valuable once transcript volume explodes, but it is not the first bottleneck if schema and append-only logs are missing. fileciteturn19file0  
Complexity: **significant** (model choice, multilingual embeddings, chunking, eval harness).  
Priority: **medium after pipeline**.

**A full MCP memory server expansion.**  
Why defer/avoid: KR already constrains MCP usage for context reasons and already has hooks/CLI infrastructure; adding tool surfaces increases operational risk during autonomous operation. fileciteturn19file0turn4file0

### Priority order by impact vs effort

1. **Append-only event log via stop hooks** (moderate, highest impact). fileciteturn4file0turn18file0  
2. **Invariant consistency checker** (trivial/moderate, high impact—prevents doctrine divergence). fileciteturn12file0turn0file3  
3. **Schema + auto-generated index** (moderate, unlocks scaling past 200 files). fileciteturn0file1turn0file5  
4. **Extend stale-reference detection to memory/decisions** (trivial, reduces entropy). fileciteturn21file0  
5. **Conversation mining into KR artifacts** (significant but high leverage; start minimal). citeturn6view0turn4view0  
6. **Optional semantic retrieval layer** (significant; defer until corpus size makes grep insufficient).

The single best next move, bottleneck-first: **turn session_stop from “snapshot only” into “snapshot + append-only event log,” then enforce doctrine consistency.** This directly supports autonomous overnight operation, training data preservation, and prevents the failure mode that will otherwise dominate at 200+ memories: silent drift in what “the system believes is true.” fileciteturn18file0turn0file8turn12file0