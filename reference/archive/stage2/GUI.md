# GUI Architecture — واجهة المستخدم

KR is not a CLI-only tool. The owner interacts with it through a web-based GUI optimized for Arabic scholarly content.

---

## Technology Decision (D-043)

**Backend:** FastAPI
- Natural fit with Pydantic models (already in contracts.py)
- Async support for LLM calls
- Automatic API documentation (OpenAPI/Swagger)
- Claude Code works with it fluently

**Frontend (MVP):** HTML + Tailwind CSS + HTMX
- No JavaScript framework needed for MVP
- Tailwind has native RTL support (`dir="rtl"`, `rtl:` prefix classes)
- HTMX enables interactive features without writing JS (partial page updates, search-as-you-type)
- Claude Code can build this entirely in Python + HTML templates
- Upgradeable to React/Next.js when complex features demand it

**Frontend (Future):** React or Reflex
- For complex features: taxonomy tree navigation, debate simulation, interactive knowledge maps
- Reflex (Python → React compilation) is the preferred path to keep Claude Code in Python
- Decision deferred until MVP is validated

**Arabic Typography:**
- Amiri font (Naskh style) for body text — the scholarly standard
- Noto Naskh Arabic as fallback
- `direction: rtl` on all Arabic content containers
- Mixed-direction support for Arabic text with embedded Latin (transliterations, references)

**Why not Streamlit/Gradio?**
- Streamlit: Poor RTL support, reruns entire script on interaction, doesn't scale for complex scholarly UIs
- Gradio: ML-demo focused, wrong paradigm for a knowledge library

---

## MVP Interface Screens

The minimum viable GUI that makes the library usable by a human:

### Screen 1: Library Dashboard (الرئيسية)
- Source count, entry count, science coverage summary
- Recent additions
- Quick search bar
- Pending human gate checkpoints (if any)

### Screen 2: Source Browser (المصادر)
- List of all sources with metadata (title, author, trust tier)
- Filter by science, school, trust tier
- Click source → source detail page (metadata, processing status, frozen file info)

### Screen 3: Entry Reader (القراءة)
- Browse taxonomy tree (expandable hierarchy)
- Click leaf → show entry (the scholarly narrative)
- Entry displays: Arabic text with school attributions, evidence citations, temporal narrative
- Each claim has a traceable link to its source excerpt

### Screen 4: Search (البحث)
- Full-text search across entries and excerpts
- Arabic-aware search (diacritics-insensitive, root-based matching if available)
- Results show: matched text with context, source, taxonomy location

### Screen 5: Human Gate (بوابة المراجعة)
- List pending checkpoints requiring owner approval
- Each checkpoint shows: what decision was made, confidence, options, context
- Approve / reject / modify buttons

---

## File Structure

```
interface/
├── scholar/
│   ├── SPEC.md          # Already exists — scholar interface specification
│   ├── CLAUDE.md        # Already exists
│   ├── contracts.py     # API endpoint contracts (Pydantic request/response models)
│   ├── src/
│   │   ├── app.py       # FastAPI application
│   │   ├── api/         # API route handlers
│   │   │   ├── sources.py
│   │   │   ├── entries.py
│   │   │   ├── search.py
│   │   │   ├── taxonomy.py
│   │   │   └── human_gate.py
│   │   └── templates/   # Jinja2 HTML templates
│   │       ├── base.html        # Base template with RTL, Tailwind, Amiri font
│   │       ├── dashboard.html
│   │       ├── sources.html
│   │       ├── entry.html
│   │       ├── search.html
│   │       └── human_gate.html
│   └── tests/
│       └── test_api.py
```

---

## RTL Layout Rules

All templates follow these rules for Arabic content:

```html
<!-- Base template sets document direction -->
<html lang="ar" dir="rtl">

<!-- Arabic text containers -->
<div class="font-amiri text-right leading-relaxed" dir="rtl">
  <!-- Arabic scholarly content here -->
</div>

<!-- Mixed content (Arabic + Latin references) -->
<div dir="rtl">
  <span dir="rtl">قال ابن قدامة في المغني</span>
  <span dir="ltr" class="text-sm text-gray-500">(vol. 3, p. 142)</span>
</div>

<!-- Metadata in English or transliterated -->
<div dir="ltr" class="text-sm">
  Source: wrk_ibn_qudamah_mughni | Trust: verified (0.82)
</div>
```

---

## Implementation Priority

The GUI is built AFTER the pipeline engines, not before. But the technology decisions and file structure are part of the preparatory phase so Claude Code knows what to target.

Implementation order:
1. Engines and shared components (Milestones 1-3)
2. API endpoints for library data (read-only, no processing)
3. HTML templates for MVP screens
4. Human gate interface (needed for pipeline operation)
5. Search interface (needs embeddings from scholar interface SPEC)
6. Advanced interactive features (taxonomy visualization, debate simulation)
