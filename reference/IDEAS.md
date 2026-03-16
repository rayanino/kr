# Project Ideas

Design thoughts, feature concepts, and architectural ideas for KR.
When an idea matures, it gets formalized into the relevant engine's SPEC.
For external tools and resources, see `RESOURCE_INBOX.md`.

**Format:** Title + 1-3 sentences. Add `(§N.N)` to reference VISION.md sections.

---

## General / Cross-Engine

* I just learned about RAG libraries. Is it still meaningfull to continue developing this application the way we visualized it (7 engines, ...)? Or would RAG libraries - or any other technology - help achieve the goal (taxonomy library with excerpts at leaf nodes)? I do not want to compromise on quality.

<!-- Pipeline-wide ideas, tooling, workflow, architecture -->

## Source Engine

## Normalization Engine

- **Multi-language input support:** The engine should accept Arabic as primary input but also handle English text. Most significant input will be Arabic, but English sources are to be expected.

- **Source format hunting:** Before running OCR on a difficult format (e.g., Arabic PDF without selectable text), check if the same book exists elsewhere in a better format (HTML, plain text, EPUB). This should be an early phase in the normalization pipeline — cheaper and more accurate than OCR when a clean source exists.

## Passaging Engine

## Atomization Engine

## Excerpting Engine

## Taxonomy Engine

## Synthesis Engine

## Scholar Interface
