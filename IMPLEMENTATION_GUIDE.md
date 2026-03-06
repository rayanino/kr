# Claude Code Implementation Guide — دليل التنفيذ

This document tells Claude Code everything it needs to build KR. Written by the Claude Chat architect, for the Claude Code builder.

---

## Environment Setup

### Required API Keys (.env)

```bash
# Multi-model consensus (D-041) — need at least 2 providers
OPENROUTER_API_KEY=        # Primary: single key accesses all models
ANTHROPIC_API_KEY=         # Backup provider
OPENAI_API_KEY=            # Backup provider

# OCR for scanned sources
MISTRAL_API_KEY=           # Mistral OCR API

# Vector search (local by default)
# QDRANT_URL=              # Only if using Qdrant Cloud
# QDRANT_API_KEY=

# Application
KR_LIBRARY_PATH=./library
KR_LOG_LEVEL=INFO
KR_HUMAN_GATE_MODE=queue
KR_GUI_PORT=8000
```

### Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Agent Teams (for parallel engine development)

Claude Code agent teams are enabled. Use them for:
- Building two adjacent engines in parallel (e.g., source + normalization)
- Parallel review: one teammate checks SPEC compliance, another checks Arabic text safety, another checks metadata flow
- Debugging with competing hypotheses

```jsonc
// Already in .claude/settings.json:
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

---

## Tool Stack

### Core Dependencies (requirements.txt)

| Tool | Purpose | Arabic Support |
|------|---------|----------------|
| pydantic v2 | Data validation, schema enforcement | N/A |
| litellm | Multi-model LLM access via OpenRouter | N/A |
| instructor | Structured LLM output | N/A |
| fastapi + uvicorn | Web GUI | N/A |
| jinja2 | HTML templates | RTL layout |
| qdrant-client | Vector search | With Arabic embeddings |

### Arabic Text Processing

| Tool | Purpose | Install |
|------|---------|---------|
| camel-tools | Morphological analysis, dediacritization, NER, dialect ID | `pip install camel-tools` (needs Rust compiler) |
| pyarabic | Arabic text utilities | `pip install pyarabic` |
| openiti | OpenITI corpus tools, Shamela converters | `pip install openiti` |

### OCR Pipeline (for scanned sources)

| Tool | Purpose | Access |
|------|---------|--------|
| Mistral OCR | Primary OCR for embedded-text PDFs | API key |
| QARI-OCR | Diacritized Arabic text (SOTA CER 0.061) | HuggingFace: `riotu-lab/QARI-OCR` (local, 8-bit quantization) |
| Tesseract 5 | Fallback OCR | `apt install tesseract-ocr tesseract-ocr-ara` |

### Document Processing

| Tool | Purpose | Install |
|------|---------|---------|
| docling | PDF/DOCX/HTML → structured JSON | `pip install docling` (Arabic experimental) |
| beautifulsoup4 | HTML parsing (Shamela exports) | `pip install beautifulsoup4` |
| python-docx | Word document processing | `pip install python-docx` |

### Embeddings & Search

| Tool | Purpose | Access |
|------|---------|--------|
| Swan-Large | Arabic embedding SOTA (NAACL 2025) | HuggingFace: `AUBMINDLAB/Swan-Large` |
| Swan-Small | Lightweight alternative (164M params) | HuggingFace: `AUBMINDLAB/Swan-Small` |
| qdrant | Vector database (local) | `pip install qdrant-client` + `docker run qdrant/qdrant` |

---

## Architecture Pattern

KR follows the "interview first, implement second" pattern:
- **Claude Chat** (architect) writes SPECs — the detailed design
- **Claude Code** (builder) implements from SPECs — the construction

The SPEC is authoritative. If the code and SPEC disagree, the SPEC wins. If the SPEC is ambiguous, add `# SPEC-AMBIGUITY: [description]` and note in NEXT.md.

### Implementation Order (from MILESTONES.md)

1. Source engine + Normalization engine (Milestone 1 — proves Phase 1 pipeline)
2. Shared components: consensus, validation, human_gate (Milestone 2 — quality infrastructure)
3. Passaging → Atomization → Excerpting (Milestone 3 — text processing pipeline)
4. Taxonomy → Synthesis (Milestone 4 — knowledge organization)
5. Scholar Interface (Milestone 5 — user-facing layer)

Each milestone produces testable, usable output.

### File Organization Per Engine

```
engines/<name>/
  SPEC.md          # Authoritative specification (written by architect)
  CLAUDE.md        # Engine-specific context for Claude Code (<60 lines)
  contracts.py     # Pydantic models for input/output (if exists)
  src/
    __init__.py
    <name>.py      # Core engine logic
    models.py      # Data models (from contracts.py / SPEC §2-§3)
    errors.py      # Error codes (from SPEC §7)
  tests/
    test_<section>.py  # One test file per §4 subsection
```

---

## Quality Gates

Before committing any code:

1. `python -m pytest engines/<n>/tests/ -v --tb=short` — all tests pass
2. `python3 scripts/check_compliance.py engines/<n>` — SPEC coverage check
3. `python3 scripts/verify_metadata_flow.py` — if data models changed
4. Three Challenges (Hostile Implementer, Skeptical Scholar, Technology Maximalist)

### Knowledge Integrity Rules (inviolable)

1. Frozen sources: bytes never change after SHA-256 hash
2. Primary text: never modified by any engine
3. Every claim: traceable to source excerpt or explicit analytical tag
4. Errors: fail loudly — never silently drop data
5. Human gates: no irreversible library change without owner approval
6. Metadata: flows forward, never deleted (D-023)
7. Content decisions: multi-model consensus, never single LLM call
8. Arabic text: read `.claude/skills/arabic-text/SKILL.md` FIRST
