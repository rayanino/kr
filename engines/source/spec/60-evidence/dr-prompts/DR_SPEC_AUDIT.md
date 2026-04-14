# DR Prompt — Comprehensive Source Engine Spec Audit

**Target:** Claude DR (has repo access)
**Purpose:** Cold-read the complete source engine spec (85+ atoms) and find what the CC team, 3 coworker reviews, and 2 prior DRs all missed.

---

## Prompt for the owner to paste into Claude DR:

Read the source engine specification for the KR (خزانة ريان) project — a personal Islamic scholarly library pipeline. The spec lives at `engines/source/spec/` in the repository at https://github.com/[owner's repo URL] on branch `clean-start`.

**Read these files in order:**
1. `engines/source/spec/README.md` — reader spine
2. `engines/source/spec/INDEX.yaml` — full atom inventory (85+ atoms)
3. `engines/source/spec/00-vision/README.md` — what the engine owns
4. `engines/source/spec/01-vocabulary/README.md` — canonical terms
5. `engines/source/spec/10-pipeline/README.md` — 6 pipeline steps
6. Read every YAML atom in `engines/source/spec/10-pipeline/` (all 6 subdirectories)
7. Read every YAML atom in `engines/source/spec/20-contracts/constraints/`
8. Read every YAML atom in `engines/source/spec/30-architecture/decisions/`
9. Read every YAML atom in `engines/source/spec/40-quality/invariants/`
10. Read `engines/source/CLAUDE.md` — engine state and agent protocol
11. Read `engines/source/reference/archive/v1/source_engine/LESSONS.md` — v1 failures

**Context:** This spec was built through: owner interviews (16 questions), 2 Deep Research reports (ChatGPT on agent-team architecture, Gemini on research source inventory), and 3 independent coworker reviews (adversary, contract architect, domain validator). It defines a 6-step pipeline: upload receipt → freeze → container classification → intake analysis → metadata deliberation → source admission & normalization handoff. The engine uses agent teams (not single LLM calls) orchestrated by a deterministic workflow executor (not an LLM supervisor). Every output preserves full evidence chains (zero knowledge loss principle — INV-SRC-0009).

**Your task:** Perform a comprehensive, adversarial audit of the complete spec. Find things that ALL prior reviewers missed. Focus on:

1. **Contradictions between atoms** — postconditions that conflict, error conditions that create deadlocks, acceptance criteria that test impossible states.

2. **Missing behavioral atoms** — mandatory output fields with no producing requirement, pipeline steps that assume data exists but no atom creates it.

3. **Arabic scholarly edge cases** — Islamic naming, genre, transmission, or textual patterns that the spec handles incorrectly or ignores. The owner's collection is 97 PDFs + Shamela HTML exports covering hadith, fiqh, tafsir, aqidah, nahw, and more.

4. **Agent-team failure modes** — What happens when agents hallucinate? When research sources are unavailable? When the 3-round disagreement protocol fails to converge on edge cases? What are the failure modes the spec doesn't account for?

5. **Data model gaps** — Fields referenced in postconditions but never defined. Enums used without exhaustive value lists. Cross-atom dependencies that would break if atoms are consumed independently.

6. **The "Zero Knowledge Loss" principle (INV-SRC-0009)** — Does every output surface actually preserve full evidence chains? Or are there atoms that implicitly compress/drop information?

7. **PDF handling** — The owner has 97 real PDFs (from hadith collections to tafsir to small risalahs). The spec routes all PDFs through OCR-primary. Are there edge cases this misses? What about PDFs with mixed pages (some scanned, some text)?

Report findings as: finding ID, severity (CRITICAL/HIGH/MEDIUM/LOW), title, which atoms are affected, what the gap is, and a concrete fix recommendation.
