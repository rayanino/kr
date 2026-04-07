# KR's memory system will fail silently before July

The persistent memory architecture powering KR (خزانة ريان) has **three critical infrastructure failures** that will compound during the April 9–July 1 autonomous Codex overnight runs: a **200-line hard ceiling** that silently drops memories, a **6.3% per-turn retrieval rate** across 79 files, and a **complete memory blackout** for 5 of 6 AI coworkers. This audit identifies the exact failure thresholds, presents benchmark evidence for each failure mode, and proposes a concrete architecture that fixes them.

The current system — 79 flat markdown files indexed by MEMORY.md with one-line descriptions — works today because the project is within its scaling envelope. But evidence from leaked Claude Code internals, multi-agent failure taxonomies, and retrieval benchmarks demonstrates that the system is approaching multiple hard limits simultaneously. The overnight Codex runs will accelerate every failure mode because Codex CLI cannot read Claude Code's memory files at all.

---

## The 200-line cliff and silent data loss

Claude Code's auto-memory system enforces a **hard cap of 200 lines or 25KB** on the MEMORY.md index file. Beyond this threshold, the system silently truncates — oldest entries fall off the bottom with no warning to the user or the model. Analysis of Claude Code v2.1.88's source (published by mem0.ai and independently confirmed by Milvus) reveals that Claude Code simply loads the first 200 lines and ignores everything else. The model receives no signal that memories have been dropped.

With 79 memory files requiring one index line each, the system currently occupies approximately **79 of 200 available lines**. This leaves 121 lines of headroom — which sounds comfortable until you account for section headers, blank lines, category labels, and the auto-memory entries Claude Code generates during sessions. At KR's current development velocity with 2,099+ tests and 7 engines under active development, the index will likely reach capacity within **8–12 weeks** of intensive development, placing the failure squarely within the April–July autonomous operation window.

When the cliff is hit, the failure is catastrophic precisely because it is invisible. Claude Code will load a fresh context with no awareness that memories exist beyond line 200. It will not hallucinate — it will simply make decisions that contradict forgotten conventions. The model has no mechanism to detect or report that truncation has occurred.

Even within the 200-line window, retrieval quality degrades due to the **"lost in the middle" phenomenon**. Liu et al.'s peer-reviewed research (TACL 2024, 1,000+ citations) demonstrated that LLMs show a U-shaped accuracy curve: **accuracy drops 20–50% for information positioned in the middle of the context** compared to the beginning or end. For a 150-line MEMORY.md, items at positions 50–100 receive systematically less model attention. This creates a reliability gradient where recently added and very old (top-of-file) memories are prioritized over mid-file entries regardless of their importance.

Claude Code's retrieval mechanism compounds this problem. Every conversational turn, a separate API call to Claude Sonnet scans all memory files, reads their one-line descriptions (~150 characters each), and selects **at most 5 files** to load. This is not embedding-based search — it is an LLM reading a list and making a judgment call. With 79 files, this creates a **6.3% retrieval ceiling per turn**. For complex tasks that span multiple knowledge domains (as Arabic NLP pipeline work frequently does), the system systematically undersurfaces relevant context.

The search capability is **grep-only** — literal keyword matching. If a memory about Docker port conflicts is stored with the description "docker-compose mapping," a query about "port conflicts" will return nothing. There is no semantic bridging, no synonym handling, no fuzzy matching. For a domain like Islamic scholarly text processing, where the same concept may be described in Arabic, transliterated Arabic, and English technical terms, this vocabulary mismatch is particularly severe.

---

## Retrieval accuracy falls far short of what the project requires

Benchmarks from multiple independent sources converge on a clear finding: flat-file retrieval with LLM-based selection achieves **significantly lower accuracy** than structured alternatives, and the gap widens dramatically for complex queries.

The Letta Context-Bench (2026) tested LLM agents on multi-step information retrieval from files. The best-performing model (Claude Sonnet 4.5) achieved only **74% accuracy** at $24.58 per run. Open-weight models scored 55–57%. These numbers represent a ceiling for the kind of "read an index, pick relevant files" retrieval that KR's memory system uses. Separately, ContextBench for coding agents (arXiv:2602.05892) found across 1,136 tasks and 66 repositories that "sophisticated agent scaffolding yields only marginal gains in context retrieval" and that "LLMs consistently favor recall over precision, introducing substantial noise."

Knowledge graph-based retrieval dramatically outperforms flat-file approaches. The evidence is consistent across multiple benchmarks:

- **Writer's RobustQA benchmark** (50,000 questions, 32 million documents): Knowledge graph retrieval achieved **86.31%** accuracy versus **75.89%** for the best vector-based system and **32.74%** for the worst
- **AIMultiple benchmark** (905 queries across 3,904 reviews): Graph RAG scored **82%** versus **15%** for vector RAG on brand-level queries
- **Diffbot KG-LM benchmark**: GraphRAG performed **3.4× better** than vector RAG, with vector RAG scoring **0%** on schema-bound queries like KPIs and forecasts
- **Multi-hop reasoning** (University of Texas research): Vector RAG dropped to **40–55%** accuracy on multi-hop queries while knowledge graph RAG maintained **70–85%**
- **Neo4j-cited meta-analysis**: Knowledge graphs improve LLM accuracy by **54.2% on average**

These benchmarks are vendor-published and should be interpreted with appropriate skepticism — each vendor has commercial interests. However, the directionality is consistent across all sources, and the magnitude of improvement (2–5× for complex queries) is too large to dismiss. The fundamental advantage is structural: knowledge graphs encode typed relationships between entities, enabling deterministic traversal of connections that flat text cannot represent.

For KR specifically, the domain involves inherently graph-structured data — isnad chains (transmission networks with 2,000+ narrator nodes), matn/sharh/hashiyah hierarchies (directed acyclic graphs of textual commentary), and pipeline dependency chains across 7 NLP engines. Flat-file memory fundamentally cannot represent these structures, forcing the model to reconstruct relationships from prose descriptions every session.

---

## Five agents operate blind while one holds all the context

The most urgent architectural failure is not scaling or retrieval — it is the **complete memory asymmetry** across KR's 6 AI coworkers. Claude Code has access to 79 accumulated memory files. Codex CLI, Gemini CLI, ChatGPT DR, Claude DR, and Gemini DR have access to **none of them**.

Research on multi-agent failure modes quantifies this risk precisely. The MAST taxonomy (Cemri et al.), analyzing 1,600+ execution traces across AutoGen, CrewAI, and LangGraph, found that **36.9% of multi-agent failures stem from inter-agent misalignment** — agents operating on inconsistent views of shared state. This is exactly the failure mode KR's architecture creates. Drew Breunig's failure taxonomy identifies four context failure modes (overload, distraction, contamination, drift) and notes that in multi-agent systems, "each failure mode becomes contagious" — one agent's context failures propagate to others through shared code.

No existing multi-agent framework solves this natively for heterogeneous tool environments. CrewAI, AutoGen, and LangGraph all assume agents run within the same framework with shared memory stores. They address intra-framework coordination, not cross-tool memory sharing between Claude Code and Codex CLI. The architectural paper "Multi-Agent Memory from a Computer Architecture Perspective" (March 2026) explicitly identifies two missing protocols: an **agent cache sharing protocol** and an **agent memory access protocol** with consistency guarantees.

The memory systems of the two primary tools are fundamentally incompatible:

| Feature | Claude Code | Codex CLI |
|---|---|---|
| **Instruction files** | CLAUDE.md hierarchy | AGENTS.md hierarchy |
| **Memory storage** | `.claude/projects/*/memory/` (markdown) | `~/.codex/memory/` (markdown + SQLite) |
| **Memory cap** | 200 lines / 25KB | 32 KiB (AGENTS.md) |
| **Auto-memory** | Auto Dream (24hr+ trigger) | Two-phase pipeline (post-rollout extraction + consolidation) |
| **Search** | Grep-only | Memory-internal |
| **Cross-tool reading** | Does NOT read AGENTS.md | Does NOT read CLAUDE.md |
| **MCP support** | JSON config (.mcp.json) | TOML config (config.toml) |

Critically, **CLAUDE.md is not read by Codex CLI, and AGENTS.md is not read by Claude Code** (unless explicitly configured). Conventions stored in one system are invisible to the other. The AGENTS.md format, stewarded by the Agentic AI Foundation under the Linux Foundation, is supported across 60,000+ open-source projects and 10+ tools — making it the closest thing to a universal standard. But KR's accumulated project knowledge currently lives in Claude Code's proprietary memory format.

---

## Overnight Codex runs will compound every failure from April to July

The planned autonomous operation from April 9 to July 1 creates a specific, predictable failure cascade. Each overnight Codex session via `codex exec --full-auto` starts effectively as a **"new hire"** — it reads AGENTS.md (if one exists), loads any Codex-specific memories (from its own SQLite store), and reads the codebase. It does not have access to the 79 files of accumulated project wisdom in Claude Code's memory.

Codex CLI's autonomous mode (`codex exec`) is designed for CI-style batch runs. It streams progress to stderr, prints the final message to stdout, and exits non-zero on failure. It supports session resumption via `codex exec resume --last`, but this requires explicit session IDs and is designed for continuation within Codex, not for inheriting Claude Code's decision history.

Codex has its own two-phase memory pipeline, backed by SQLite at `~/.codex/state_<version>.sqlite`. Phase 1 extracts structured memories from completed sessions. Phase 2 consolidates them into `MEMORY.md`, `memory_summary.md`, and `skills/` files. This means Codex will build its own separate memory of the project — potentially contradicting Claude Code's memories without either system detecting the contradiction.

The **decision drift risk** is substantial. Practitioner analysis from Harness.io describes the pattern: "The agent starts strong. It understands the problem, follows instructions... Then, somewhere along the way, things begin to drift. The code still compiles, but the logic gets inconsistent. Small mistakes creep in. Constraints are ignored. Assumptions mutate. Nothing fails loudly. Everything just gets slightly worse." Over 83 nights of autonomous operation, small deviations compound into architectural incoherence. MemU estimates that **context drift causes 65% of enterprise AI agent failures** (a vendor statistic warranting skepticism on the precise figure, though consistent with broader evidence).

The most reliable constraint propagation mechanism across sessions is not memory — it is the **test suite**. KR's 2,099+ tests are the strongest guardrail against overnight drift. If architectural conventions are encoded as tests, any agent that violates them fails CI. But tests can only enforce behaviors that have been explicitly codified. Design patterns, naming conventions, Arabic text processing policies, and architectural rationale are typically not test-encoded.

Key limitations for overnight operation include memory locality (Codex's SQLite database is local to `~/.codex/`, absent on CI runners), the AGENTS.md **32 KiB size cap** (which truncates detailed project conventions), and the absence of runtime constraint enforcement — AGENTS.md provides guidance via prompting, not hard enforcement. OpenAI's own documentation warns that full-auto mode is "not recommended for production repos."

---

## Arabic NLP and Islamic text processing demand structured domain memory

KR's domain imposes memory requirements that flat files cannot efficiently serve. The 7-engine Arabic NLP pipeline requires persistent configuration across four categories, each with different durability characteristics and update frequencies.

**Static processing configuration** includes the canonical normalization order (Unicode normalization → Alef/Hamza normalization → diacritics handling → Taa Marbuta), character whitelists/blacklists (OpenITI's `ar_chars`, `ar_nums`, `allowed_chars`), transliteration scheme mappings (Buckwalter, Safe Buckwalter, HSB, betaCode), and per-corpus diacritics policies. The critical rule: Islamic scholarly texts (Quran, hadith, classical fiqh) **require diacritical preservation** while general Arabic NLP strips them. CAMeL Tools provides discrete normalization functions (`normalize_alef_ar`, `normalize_teh_marbuta_ar`, `normalize_alef_maksura_ar`) that must be applied in a specific order and with corpus-specific policies. Applying `normalize_teh_marbuta_ar` (which maps ة to ه) to hadith text destroys meaningful distinctions (صلاة vs صلاه). These policies must persist and be enforced across all 7 engines and all AI coworkers.

**Growing domain knowledge** includes the narrator database (Sahih Muslim alone has **2,092 narrator nodes** and **77,797 sanad-hadith edges** in the Multi-IsnadSet dataset), hadith grading taxonomy (sahih/hasan/da'if/mawdu' with sub-classifications by narrator count and chain characteristics), and the matn/sharh/hashiyah textual hierarchy — a directed acyclic graph where each base text (matn) may have multiple commentaries (shuruh), each of which may have multiple super-commentaries (hawashi), notes (taliqat), and continuations (takmilat). This is inherently graph-structured knowledge that flat files can describe but cannot natively represent.

The leading digital humanities projects in this domain have converged on structured, schema-driven approaches. **OpenITI** uses a custom markup scheme (mARkdown) with a formal URI system (`[DeathDateAH][Shuhra]/[BookTitle]/[VersionID]`), YAML metadata files, and a quality pipeline tracking files through stages from raw to verified. **KITAB** generates massive structured datasets from text reuse detection (650,000 instances across 3,500 books) and explicitly treats "uncertainty, loss, and disagreement as structured information rather than noise." **SemanticHadith** provides a formal RDF ontology (v2.0.1) covering hadith structure, narrators, chains, topics, and grades with a SPARQL endpoint.

KR's flat markdown memory cannot capture the relationships between these entities. A memory file titled "hadith-processing-rules.md" can describe the isnad chain structure in prose, but when a Codex overnight session processes a new text, it cannot traverse the narrator graph to verify chain validity. The domain demands a knowledge graph that encodes narrator credibility ratings, textual genealogy relationships, and processing pipeline configurations as structured, queryable data.

---

## Staleness poisons memory when nothing distinguishes old decisions from current ones

The 79 markdown files contain no temporal metadata — no timestamps on when decisions were made, no markers for whether they are still valid, no mechanism to detect when file 3 contradicts file 67. This is a known failure mode with well-studied solutions that KR has not implemented.

The foundational problem is distinguishing **ephemeral state** (current sprint goals, active bugs, deployment status, framework versions) from **durable principles** (architectural patterns, coding conventions, Arabic normalization rules). Truth Maintenance Systems (TMS) from classical AI formalize this distinction: premises are fundamental beliefs requiring no justification, while derived facts depend on premises and must be re-evaluated when premises change. The AGM theory of belief revision (Alchourrón, Gärdenfors, Makinson, 1985) establishes that revision should preserve as much existing knowledge as possible while incorporating new information — the "minimal change" principle.

Modern implementations of these ideas include Zep's **bi-temporal modeling**, which tracks two timelines: T (when facts were true in reality) and T' (when facts were recorded in the system). Each fact carries four timestamps: `t'_created`, `t'_expired`, `t_valid`, `t_invalid`. This enables precise reasoning about historical state. The **Architecture Decision Record** pattern (Nygard, 2011) provides a simpler but effective approach: decisions are immutable, append-only records that are never deleted but marked "superseded" or "deprecated" with references to replacements.

Without temporal awareness, KR's memory system experiences predictable degradation. Production RAG systems follow a documented trajectory: weeks 1–2 perform well, weeks 3–4 show quality drift on frequently-updated topics, month 4 sees costs climb 40% from workarounds, and month 6 requires a full rebuild. For a system generating new memories during overnight autonomous runs without human curation, this timeline accelerates.

The MCP Memory Server, which exists in KR's configuration but appears unused, does not solve the staleness problem. Its 9-tool API (create_entities, create_relations, add_observations, search_nodes, read_graph, open_nodes, delete_entities, delete_relations, delete_observations) stores entities and relations in a JSONL knowledge graph — a structural improvement over flat files. But it has **no temporal awareness** (no timestamps on anything), **no contradiction detection** (contradictory observations coexist silently), **no versioning** (deleted data is gone permanently), and **no semantic search** (basic string matching only). The GitHub README explicitly states these servers are "meant to serve as educational examples, not as production-ready solutions."

---

## A three-layer architecture that addresses every identified failure

The evidence points to a specific architecture that resolves the scaling cliff, retrieval accuracy, multi-agent coordination, domain structure, staleness, and autonomous operation problems simultaneously. It has three layers, each addressing distinct failure modes.

**Layer 1: AGENTS.md as the universal instruction surface.** Migrate KR's critical conventions from CLAUDE.md to a comprehensive AGENTS.md file at the repository root. AGENTS.md is the cross-tool standard supported by Codex CLI, Claude Code (via configuration), Cursor, Copilot, Amp, Jules, Gemini CLI, Windsurf, Cline, Aider, and Zed. This single change eliminates the memory blackout for Codex CLI overnight sessions. The file should contain: build and test commands, the canonical Arabic normalization pipeline order, coding conventions, architectural decisions, and explicit constraints for autonomous operation ("Do NOT modify engine configurations without running the full test suite"). Keep it under **32 KiB** (Codex's cap) by referencing detailed documentation files rather than inlining everything.

**Layer 2: A shared MCP knowledge graph replacing flat markdown files.** Replace the 79 markdown memory files with a knowledge graph served via MCP, accessible to both Claude Code and Codex CLI. The implementation path:

- Deploy a production-grade MCP memory server (not the reference implementation). Options include `codex-mcp-memory` (PostgreSQL-backed with semantic search), Basic Memory (cross-tool, works with both Claude Code and Codex CLI), or a custom server extending the reference implementation with temporal metadata and semantic search
- Define entity types encoding durability: `Convention` (durable, rarely invalidated), `ArchitectureDecision` (durable, superseded not deleted), `PipelineConfig` (semi-durable, versioned), `ActiveTask` (ephemeral), `NarratorRecord` (domain knowledge, grows), `TextRelationship` (domain knowledge, graph-structured)
- Define relation types: `supersedes` (decision evolution), `depends_on` (component dependencies), `applies_to` (rule scoping), `narrates_from` (isnad chains), `comments_on` (matn/sharh/hashiyah hierarchy), `requires_normalization` (pipeline configuration)
- Add bi-temporal timestamps to all entities and observations: `valid_from`, `valid_until`, `recorded_at`, `recorded_by` (which agent/session created the entry)
- Configure both Claude Code (via `.mcp.json`) and Codex CLI (via `config.toml`) to connect to the same MCP memory server

**Layer 3: Test-driven constraint propagation for autonomous operation.** Encode every convention that must survive overnight runs as an automated test. The 2,099+ test suite is already KR's strongest asset — extend it to cover:

- Arabic normalization pipeline order (test that normalization functions are called in the canonical sequence)
- Diacritics preservation policy (test that Quranic and hadith texts retain tashkeel after processing)
- Architectural invariants (test that no engine directly accesses another engine's internal state)
- File format conventions (test that generated files conform to expected schemas)
- Pre-session context injection: create a script that runs before each `codex exec` invocation, exporting the latest knowledge graph state into a summary appended to AGENTS.md or a session-specific context file
- Post-session review gates: never auto-merge overnight work. Each overnight branch requires human or Claude Code review before merging to main

**Implementation sequence for the April 9 deadline:**

1. **Week 1 (immediate):** Create a comprehensive AGENTS.md from the existing CLAUDE.md and memory files. This is the minimum viable fix — it gives Codex CLI access to core project conventions on day one
2. **Week 2:** Deploy Basic Memory or an equivalent shared MCP memory server. Configure both Claude Code and Codex CLI to connect. Begin migrating high-value memory files into structured entities
3. **Week 3:** Implement the pre-session and post-session scripts for overnight runs. Add convention-encoding tests to the test suite. Define the entity type schema for Arabic NLP domain knowledge
4. **Ongoing:** As overnight sessions run, monitor for decision drift by reviewing diffs against the knowledge graph. Gradually migrate all 79 memory files into structured entities with temporal metadata and typed relations

---

## Conclusion

KR's flat-file memory system is not broken today — it is approaching three hard limits simultaneously. The **200-line index ceiling** will trigger silent data loss within the autonomous operation window. The **5-file-per-turn retrieval limit** means 93.7% of accumulated knowledge is invisible on any given query. And the **complete memory asymmetry** between Claude Code and the other 5 coworkers means overnight Codex sessions operate without any of the project's accumulated wisdom.

The most critical finding is temporal: **these failures will compound during the 83-night autonomous operation period from April 9 to July 1**. Each overnight session builds on the previous session's output without access to the design rationale behind prior decisions. Small deviations accumulate into architectural incoherence that is expensive to reverse.

The evidence strongly favors a three-layer fix: AGENTS.md as a universal instruction surface (eliminating the cross-tool blackout), a shared MCP knowledge graph (replacing flat files with structured, temporally-aware, semantically-searchable memory), and test-driven constraint propagation (encoding conventions as executable invariants). The domain structure of Islamic scholarly texts — isnad chains, commentary hierarchies, narrator credibility networks — is inherently graph-shaped and will benefit disproportionately from knowledge graph representation, with benchmarks showing **2–5× retrieval accuracy improvements** for complex, multi-hop queries. The first layer (AGENTS.md) can be implemented before April 9. The second and third layers should be deployed within the first two weeks of autonomous operation, before the system's memory reaches critical mass.