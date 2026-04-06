# Batch Lifecycle Protocol Summary (from HARDENING_SESSION_PROTOCOL v5.0 §3A)

## Architecture
Serial Muqabalah (classical Islamic collation framework): A primary agent extracts; a secondary agent (muhhaqqiq) performs side-by-side collation against the original, hunting for gaps.

## 6-Phase Model
Maps to classical Islamic pedagogy:
1. **Mutala'ah** (Reading) — Bundle intake, file inventory
2. **Fahm** (Comprehension) — Per-file atom extraction, MCU identification
3. **Mudhakarah** (Peer Discussion) — Coworker cross-validation
4. **Muraja'ah** (Revision/Collation) — Verification against original source
5. **'Ard** (Presentation) — Owner briefing on findings
6. **Ijazah** (Certification) — Batch finalization with shahadah certificate

## MCU (Minimum Content Unit)
Smallest span of owner source text expressing a single directive, definition, risk, rule-example, severity signal, or meta-instruction. Required fields: mcu_id, file_path, start_line, end_line, verbatim_anchor (min 15 chars), severity, classification.

## MCU Classifications
- MAPPED: Has corresponding MAQ entry
- MISSED (nuqsan): Silently dropped during extraction
- SOFTENED (takhfif): Direction preserved but urgency reduced
- DISTORTED-tashif: Surface corruption, recoverable
- DISTORTED-tahrif: Structural corruption, meaning altered
- SKIPPED-FILE: Entire file not processed

## Verification Standard: Hafiz/Faqih Spectrum
- **Hafiz (word-for-word):** For raw owner text, nonnegotiables, ALL-CAPS directives
- **Faqih (meaning-based):** For structured analysis files, model expansions
- Devotional formulae, jawami' al-kalim ALWAYS require Hafiz standard

## Key Rule
ALL-CAPS, exclamation marks, "PLEASE" = SEMANTIC CONTENT, not formatting. Stripping them is a fatal lahn.
