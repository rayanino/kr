# Excerpt Viewer — Design Spec

**Date:** 2026-03-31
**Purpose:** Minimal, clean viewer for ExcerptRecord data from the excerpting pipeline.
**Location:** `tools/excerpt_viewer.html`
**Dependencies:** None (single self-contained HTML file with embedded CSS/JS)

## Problem

The excerpting pipeline produces `excerpts.jsonl` files (Arabic scholarly teaching units with 33 metadata fields). There is no way to visually inspect these excerpts for quality assessment. The owner needs to review them one by one, seeing all fields, to form an honest opinion on pipeline quality.

## Design Decisions

### Delivery
- Single `.html` file in `tools/`
- Zero install, zero build step
- Open in any browser, drag `excerpts.jsonl` onto it
- Does not pollute engine code or test infrastructure

### Core Principle: Two Zones

The viewer has two visually distinct zones:

**Zone 1 — "Your Library Excerpt"** (warm, scholarly, prominent)
What would actually exist in your library if the engine ran today.
This is YOUR knowledge. The viewer renders it as the finished product.

**Zone 2 — "Pipeline Diagnostics"** (muted, clearly labeled, collapsible)
How the machine produced this. Helps you judge whether Zone 1 is trustworthy.
Confidence scores, consensus decisions, gate flags, internal IDs.

The visual break between zones must be unmistakable — different background,
a clear divider labeled "Pipeline Diagnostics", and a different type treatment.

### Layout

```
┌── Sticky Top Bar ──────────────────────────────────────┐
│ [◀] Excerpt 3 of 174 [▶]  │  taysir  │  [Overview]    │
└────────────────────────────────────────────────────────────┘

╔══ ZONE 1: YOUR LIBRARY EXCERPT ═══════════════════════════╗
║                                                            ║
║  ── Location ──                                            ║
║  كتاب الطهارة › النية وأحكامها   Vol 1, pp 15-16          ║
║                                                            ║
║  ── Text (RTL, large Arabic font) ──                       ║
║  المعنى الإجمالي:                                          ║
║  هذا حديث عظيم وقاعدة جليلة من قواعد الإسلام هي           ║
║  القياس الصحيح لوزن الأعمال من حيث القَبول وعدمه           ║
║                                                            ║
║  يبين أن قبول العمل وثوابه وردَّه يدور على النية ←gloss    ║
║                                                            ║
║  ┌─ ⚠ PARTIAL ─────────────────────────────────────────┐   ║
║  │ يفتتح بقول «هذا حديث»، وهو إحالة إلى متن سبق خارج │   ║
║  │ Context: المقصود حديث «إنما الأعمال بالنيات»         │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                            ║
║  ── Scholarly Function ──                                  ║
║  [rule_statement]  also: opinion_statement, example         ║
║                                                            ║
║  ── Author & Attribution ──                                ║
║  Layer: sharh (ابن عقيل) — 80% coverage                    ║
║  School: حنبلي                                             ║
║                                                            ║
║  ── Scholars Cited ──                                      ║
║  سيبويه │ عمرو بن عثمان بن قنبر │ quoted_opinion           ║
║  المبرد │ محمد بن يزيد المبرد   │ refuted_position          ║
║                                                            ║
║  ── Topics ──                                              ║
║  [ميزان الأعمال بالنيات]  [قبول العمل بالإخلاص]            ║
║  Variants: النية → [القصد]                                  ║
║                                                            ║
║  ── Evidence ──                                            ║
║  Hadith: إنما الأعمال بالنيات، وإنما لك…                   ║
║  Cross-ref: باب الاستثناء (→ not resolved)                  ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

┌── ZONE 2: PIPELINE DIAGNOSTICS ───────────────────────────┐
│  (muted background, smaller font, collapsible)             │
│                                                            │
│  ▸ Identifiers                                             │
│    excerpt_id: exc_src_test0001_div_..._0_2                │
│    source_id: src_test0001  div_id: div_src_test0001_2_000 │
│    chunk: 0  unit: 2  segments: [11, 12, 13, 14]           │
│    words: 191–306  snippet: المعنى الإجمالي: هذا حديث…     │
│                                                            │
│  ▸ Confidence Scores                                       │
│    attribution: —  school: 0.63                            │
│    scholars: سيبويه 0.99, المبرد 0.98 (llm_enrichment)     │
│                                                            │
│  ▸ Consensus Decisions                                     │
│    self_containment: enrich=PARTIAL verify=PARTIAL ✓ agree  │
│    school_attribution: enrich=حنبلي verify=حنبلي ✓ agree   │
│                                                            │
│  ▸ Flags                                                   │
│    Gates: none  Review: none                               │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Zone 1 Fields (Library Content)

These are what your library would contain. Rendered with scholarly visual weight.

| Section | Fields |
|---------|--------|
| **Location** | `div_path` (breadcrumb), `physical_pages` (Vol/pp) |
| **Text** | `primary_text` (RTL, large), `description_arabic` (gloss below) |
| **Self-Containment** | `self_containment` (pill), `self_containment_notes`, `context_hint` |
| **Function** | `primary_function` (pill), `secondary_functions` (muted pills) |
| **Attribution** | `primary_author_layer` (layer + author + coverage), `school` |
| **Scholars** | `quoted_scholars` (table: mention, resolved name, role) |
| **Topics** | `excerpt_topic` (tags), `terminology_variants` (term → variants) |
| **Evidence** | `evidence_refs`, `takhrij_data`, `cross_references`, `footnotes_relevant` |

### Zone 2 Fields (Pipeline Diagnostics)

These tell you how the engine produced it. Muted, collapsible, clearly separated.

| Section | Fields |
|---------|--------|
| **Identifiers** | `excerpt_id`, `source_id`, `div_id`, `chunk_index`, `unit_index`, `segment_indices`, `start_word`/`end_word`, `text_snippet`, `content_types` |
| **Confidence** | `attribution_confidence`, `school_confidence`, per-scholar `confidence` + `source` |
| **Consensus** | `consensus_metadata.decisions` (full table: enrichment vs verifier vs escalation) |
| **Flags** | `gate_flags` (red), `review_flags` (orange) |

### Zone 3 — Feedback (Human Review for Machine Consumption)

A clearly separated feedback area below Zone 2. The user types freely;
the viewer auto-structures the output for LLM reviewers.

**User input (minimal friction):**
- **Verdict buttons:** `Accept` / `Needs Work` / `Reject` (one click)
- **Comment box:** single textarea, free-form text, no required fields
- **Save & Next:** saves + advances to next excerpt (keyboard: Enter)

**Machine output (auto-structured `feedback.jsonl`):**
Each line is a self-contained review that an LLM can evaluate without
loading the original excerpts.jsonl:

```json
{
  "excerpt_id": "exc_src_test0001_div_..._0_2",
  "timestamp": "2026-03-31T12:34:56Z",
  "verdict": "needs_work",
  "comment": "The school attribution is wrong — clearly Shafi'i not Hanbali...",
  "excerpt_context": {
    "primary_function": "rule_statement",
    "self_containment": "PARTIAL",
    "school": "حنبلي",
    "school_confidence": 0.63,
    "primary_author_layer": {"layer_id": "sharh", "author_id": "unknown"},
    "div_path": ["كتاب الطهارة", "النية وأحكامها"],
    "text_snippet": "المعنى الإجمالي: هذا حديث عظيم...",
    "gate_flags": [],
    "review_flags": [],
    "consensus_summary": "self_containment: agree, school: agree"
  },
  "review_meta": {
    "source_file": "smoke_pre_prod/taysir/excerpts.jsonl",
    "excerpt_position": "3/174",
    "reviewer": "owner"
  }
}
```

**Why `excerpt_context` is auto-captured:** When an LLM reads this feedback
months later, it has everything inline: what the excerpt said, what the owner
said was wrong, and the pipeline's own quality signals. No cross-referencing needed.

**Verdict enum semantics (for LLM consumers):**
- `accept` — excerpt is correct, ready for library
- `needs_work` — something is wrong but fixable (most common)
- `reject` — excerpt should not exist in the library
- `skip` — not reviewed (default state, not saved)

**Storage:** localStorage in the browser (survives page refresh and reload).
"Export Feedback" button downloads `feedback.jsonl`. Feedback persists across
sessions keyed by source filename + excerpt_id.

**Review progress bar:** Shows "Reviewed: 3/174 (2 accept, 1 needs_work)"
in the feedback zone. Clicking the stats jumps to the next unreviewed excerpt.

### Visual Language

| Token | Value | Usage |
|-------|-------|-------|
| Background | `#F7F3EA` | Page |
| Surface | `#FFFDF8` | Cards, sections |
| Text | `#1F1A17` | Primary |
| Muted | `#6B645C` | Labels, IDs |
| Accent | `#2F5D73` | Links, interactive |
| FULL | `#5E7D61` (sage) | Self-containment pill |
| PARTIAL | `#B07A1B` (ochre) | Warning band + pill |
| DEPENDENT | `#A44A3F` (brick) | Warning band + pill |
| Gate flag | `#C0392B` (red) | gate_flags only |

### Typography

- Arabic text: `"Amiri", "Noto Naskh Arabic", "Scheherazade New", "Traditional Arabic", serif`
  - Size: 1.45rem, line-height: 1.9, `dir="rtl"`, `lang="ar"`
- UI/metadata: `"Segoe UI", "SF Pro Text", "Inter", system-ui, sans-serif`
  - Size: 0.875rem for labels, 1rem for values
- Mixed content: wrap Latin/numbers in `<bdi>` or `<span dir="ltr">`

### File Loading

1. **Empty state:** Full-page drop zone with instructions
2. **Drag-and-drop** excerpts.jsonl onto page
3. **File picker** button as fallback
4. Parse: strict UTF-8, JSONL line-by-line, fail loud on first bad line (show line number)
5. No Arabic normalization, no whitespace trimming
6. **URL state:** `#i=37` to bookmark position, localStorage resume

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `←` / `→` | Previous / Next excerpt |
| `Home` / `End` | First / Last |
| `g` | Go to index (prompt) |
| `o` | Toggle overview drawer |
| `f` | Open file picker |
| `1`-`8` | Jump to section |
| `?` | Show shortcuts |

### Overview Drawer (collapsible)

- Total excerpts, current position
- Self-containment distribution (FULL / PARTIAL / DEPENDENT counts)
- Excerpts with gate_flags (count + list)
- Excerpts with review_flags (count + list)
- Top primary_function distribution (bar chart or counts)
- Click any stat to jump to first matching excerpt

### Empty Fields

Show explicit `—` placeholder for every null/empty field. The viewer must prove nothing was dropped — the owner needs to see that a field is empty, not wonder if the viewer omitted it.

## Non-Goals

- No editing of excerpt data (feedback is separate from the excerpt itself)
- No remote URL loading (CORS + file:// is brittle)
- No dark mode in v1
- No gate_queue.jsonl support in v1 (excerpts.jsonl only)
- No campaign-level analysis (that's scripts/excerpting_eval/)

## File Location

`tools/excerpt_viewer.html` — outside the engine tree, doesn't affect tests or pipeline.

## Verification

1. Open `tools/excerpt_viewer.html` in Chrome/Edge/Firefox
2. Drag `integration_tests/compare_codex_v2/taysir/excerpts.jsonl` onto it
3. Verify: 10 excerpts load, Arabic renders RTL with diacritics, all 33 fields visible
4. Navigate with arrow keys, check PARTIAL/DEPENDENT warning bands
5. Open Overview drawer, verify stats match SUMMARY.json
6. Drag a different file (ibn_aqil_v3) — verify clean reload
