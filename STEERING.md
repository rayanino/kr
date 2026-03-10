# KR Steering Document — وثيقة التوجيه

This is the CONCISE project context for Claude Code. It replaces reading VISION.md (47K tokens) or DOMAIN.md (7K tokens) for most tasks.

## Product

**Name:** خزانة ريان (Khizanat Rayan, KR)
**Type:** Personal intelligent Islamic scholarly library
**User:** One person — an Islamic studies student with no technical background
**Core axiom:** The library IS the user's knowledge. Errors propagate into his mind.
**Goal:** Make previously impossible scholarship possible through technology.
**Language:** All scholarly content in Arabic. System messages in English. Entries in Arabic.

## Current Development Phase: Pipeline Engineering

**We are building and proving a 7-engine pipeline. We are NOT populating a library.**

The library gets populated as a side effect of a working pipeline. Until all 7 engines are built and proven correct, the only deliverable is: engines that work. Every session, every task, every decision optimizes for pipeline correctness and robustness — never for throughput, user experience, or library population speed. See `/CLAUDE.md` "Development Priority" section for the full directive.

## Architecture

```
Source → Normalization ─── normalization boundary ───
Passaging → Atomization → Excerpting → Taxonomy → Synthesis
                                                      ↓
                                              Scholar Interface
```

**Phase 1 (source-specific):** Source + Normalization. Above the normalization boundary.
**Phase 2 (source-agnostic):** Passaging through Synthesis. Below the boundary.
**Layer 3:** Scholar Interface — user-facing, consumes all engine outputs.

**Shared components:** consensus (multi-model LLM agreement), validation, human_gate (owner approval), feedback, user_model, scholar_authority.

## Data Flow

```
Raw source (PDF, HTML exports, photos, EPUB, manual text, any scholarly format)
  → Frozen source + metadata.json (source engine)
    → manifest.json + content.jsonl (normalization engine)
      → passages[] (passaging engine)
        → atoms[] within passages (atomization engine)
          → excerpts[] with self-containment (excerpting engine)
            → placed_excerpts[] in taxonomy tree (taxonomy engine)
              → entries[] — scholarly narratives (synthesis engine)
                → Scholar Interface — query, browse, learn
```

## Key Decisions (abbreviated)

- **D-019:** ABD legacy code has zero design authority. SPECs define what to build.
- **D-023:** Metadata is synthesis fuel. Never strip metadata. Pass through everything.
- **D-024:** Three-tier identity: source_id, work_id, canonical_id.
- **D-033:** Fail loud. Low-confidence → flag, not silent default.
- **D-040:** Grounding_type traceability. Every claim tagged: source_grounded | metadata_derived | analytical.

## Technology Stack

- **Python 3.11+** — primary language
- **LiteLLM + Instructor** — multi-model LLM consensus via OpenRouter
- **Pydantic** — data validation and schema enforcement
- **Arabic NLP:** CAMeL Tools, Farasa for morphological analysis
- **OCR:** Mistral OCR primary, Qari-OCR for diacritics
- **Embeddings:** arabic-e5-base or GTE-multilingual-base
- **Vector DB:** Qdrant for semantic search
- **Storage:** JSON files on disk (no database for v1)

## Quality Standard

The target output quality is defined in `reference/ENTRY_EXAMPLE.md`. An entry is a scholarly NARRATIVE that:
- Traces positions across centuries with dates
- Shows teacher-student relationships
- Explains WHY scholars disagreed
- Distinguishes evidence types (Quran, hadith, ijma, qiyas)
- Notes when a scholar changed position
- Identifies which opinion the student should follow (with reasoning)

## Constraints

- **Normalization boundary:** No source-format-specific logic below it.
- **Text integrity:** Primary text bytes are NEVER modified after extraction.
- **Consensus required:** All content decisions (attribution, classification, extraction) use multi-model consensus.
- **Human gates:** All irreversible library changes require owner approval.
- **Priority:** Accuracy > Protection > Intelligence.
