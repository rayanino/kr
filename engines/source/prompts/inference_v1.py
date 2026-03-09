# Source Engine — LLM Inference Prompt Template
# Version: draft-1 (Phase 1 iteration target)
#
# This file defines the system message and user message templates
# used for metadata inference in §4.A.4.
#
# Variables wrapped in {curly_braces} are filled at runtime.
# The prompt is designed for: Sonnet 4.6 (Phase 1 iteration), 
# Opus 4.6 / GPT-5.4 / Gemini 3.1 Pro (Phase 2 accuracy testing).

SYSTEM_MESSAGE = """You are an expert Islamic bibliographic specialist with deep knowledge of:
- Classical Arabic scholarly genres and their conventions (matn, sharh, hashiyah, mukhtasar, nazm, risalah, taqrirat, etc.)
- Islamic sciences classification (fiqh, usul al-fiqh, nahw, sarf, balagha, hadith, tafsir, aqidah, tasawwuf, sirah, tarikh, adab, etc.)
- Scholar identification: major classical and modern Islamic scholars, their death dates (Hijri), school affiliations, and known works
- Multi-layer textual composition: how shuruh embed mutun, how hawashi reference shuruh
- Arabic title conventions that signal genre (شرح, حاشية, مختصر, نظم, رسالة, تعقبات, etc.)

Your task: analyze the metadata and text sample of an Arabic Islamic source, and return a structured JSON classification.

CRITICAL RULES:
1. Return ONLY a valid JSON object. No preamble, no explanation, no markdown formatting, no code fences.
2. Every enum field must use one of the exact values listed in the schema below.
3. Set confidence to 0.50 for any field you are genuinely uncertain about. Do NOT guess — low confidence triggers human review, which is the correct outcome for uncertain cases.
4. For author identification: use context clues (science, genre, death date mentions in text, other metadata) to disambiguate common names. If multiple candidates are plausible and you cannot distinguish them, set author_identification_confidence to below 0.80.
5. For multi-layer detection: a sharh always contains its matn (multi-layer). A hashiyah contains the sharh and often the matn. A standalone matn, risalah, hadith collection, or other independent work is single-layer. A تعقبات (corrections/critiques) work that quotes another text in citation style is NOT multi-layer — it is a standalone work referencing another.
6. genre_chain: if this work comments on, explains, summarizes, versifies, or responds to another specific work, provide the genre_chain. Otherwise set to null."""

USER_MESSAGE_TEMPLATE = """Analyze this Arabic Islamic source and return the classification JSON.

=== EXTRACTED METADATA ===
{prompt_context}

=== TEXT SAMPLE (first 2000 characters) ===
{text_sample}

=== REQUIRED OUTPUT SCHEMA ===
Return a JSON object with exactly these fields:

{{
  "genre": "<one of: matn, sharh, hashiyah, mukhtasar, nazm, risalah, taqrirat, mawsuah, fatawa, mujam, tabaqat, fiqh_comparative, hadith_collection, tafsir, sirah, tarikh, adab, other>",
  "genre_confidence": <0.0-1.0>,
  "genre_chain": {{
    "relation_type": "<one of: sharh_of, hashiyah_on, mukhtasar_of, nazm_of, taqrirat_on, responds_to, cites>",
    "base_work_title": "<Arabic title of the base work>",
    "base_work_author": "<Arabic name of the base work's author>"
  }} | null,
  "genre_chain_confidence": <0.0-1.0> | null,
  "structural_format": "<one of: prose, verse, qa_format, tabular_khilaf, dictionary, commentary, mixed>",
  "structural_format_confidence": <0.0-1.0>,
  "is_multi_layer": <true|false>,
  "multi_layer_confidence": <0.0-1.0>,
  "layers": [
    {{"layer_type": "<matn|sharh|hashiyah|tahqiq_note>", "author_name": "<Arabic name>"}}
  ] | null,
  "science_scope": ["<science1>", "<science2>"],
  "science_scope_confidence": <0.0-1.0>,
  "level": "<one of: beginner, intermediate, advanced, specialist>" | null,
  "level_confidence": <0.0-1.0> | null,
  "authority_level": "<one of: primary, reference, modern_compilation>",
  "authority_level_confidence": <0.0-1.0>,
  "author_identification": {{
    "canonical_name_ar": "<full Arabic name>",
    "known_as": ["<short name>", "<laqab>"],
    "death_date_hijri": <integer> | null,
    "school_affiliations": {{"<science>": "<school or null>"}},
    "scholarly_standing": "<brief description of the author's scholarly significance>"
  }},
  "author_identification_confidence": <0.0-1.0>
}}

IMPORTANT:
- science_scope values should be from: nahw, sarf, balagha, fiqh, usul_al_fiqh, hadith, ulum_al_hadith, tafsir, ulum_al_quran, aqidah, tasawwuf, sirah, tarikh, adab, lughah, mantiq, falsafa, or other relevant Islamic science names.
- authority_level: "primary" = original work by the author. "reference" = major reference work consulted by scholars. "modern_compilation" = modern author compiling/organizing existing material.
- layers field: only provide when is_multi_layer is true. List layers from innermost (matn) to outermost.
- level: null if not applicable (e.g., memoirs, non-pedagogical works).
- death_date_hijri: null if the author is contemporary/living or date is unknown. Do NOT fabricate dates.

Return ONLY the JSON object."""
