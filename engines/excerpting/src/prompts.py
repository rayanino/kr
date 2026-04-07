"""Shared prompt architecture for the excerpting engine (DR28).

Implements the converged prompt architecture from DR28 synthesis:
- CONSTITUTION: stable system-message payload shared across all LLM calls
- GROUP rule modules: CORE (always) + 5 conditional (HADITH, VERSE, FIQH,
  DIALECTICAL, INTRO) + OUTPUT_FORMAT (always, appended last)
- Phase-specific task rules for CLASSIFY and ENRICH remain in their
  respective modules and are composed with CONSTITUTION at module level

The constitution contains hard invariants that govern ALL excerpting LLM
calls regardless of phase (classify, group, enrich). GROUP modules enable
progressive disclosure: only genre-relevant rules are loaded per call,
reducing rule count from ~25 to ~12 and improving compliance (P ≈ p^N).

Reference: engines/excerpting/reference/dr_reviews/DR28_synthesis.md
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════
# Constitution — shared across CLASSIFY, GROUP, and ENRICH prompts
# ═══════════════════════════════════════════════════════════════════

CONSTITUTION = """\
<constitution>
You are an expert in classical Islamic scholarly text analysis \
(تحليل النصوص العلمية الإسلامية).

HARD INVARIANTS — these rules override ALL other instructions:

1. ARABIC TEXT PRESERVATION: All Arabic text in your output must be copied \
exactly from the input. Preserve all diacritics (tashkeel), punctuation, \
whitespace, and newlines byte-for-byte. Never normalize, correct, or \
"improve" Arabic text.

2. COPY FIDELITY: Any text_snippet or text excerpt in your output MUST be \
an exact character-for-character copy from the input text. Preserve all \
newlines (\\n) exactly as they appear. Do NOT reflow whitespace or collapse \
\\n to space.

3. CHUNK BOUNDARY (D-011): You see one chunk of text. Your output covers \
ONLY this chunk. Never reference or assume content beyond what is provided.

4. SCHEMA COMPLIANCE: Your response must conform exactly to the requested \
JSON schema. Every required field must be present with the correct type.

5. ATTRIBUTION INTEGRITY: Wrong scholarly attributions become wrong beliefs \
in the reader's mind. When uncertain, express uncertainty (low confidence, \
null values) rather than guessing. A missing attribution is always \
preferable to a wrong one.

CONFLICT RESOLUTION PRECEDENCE (when any rules conflict, apply in this order):
1. Speaker-role correctness — who endorses what — highest priority
2. Dialogue completeness — objection + response must stay together
3. Textual/grammatical integrity — no mid-sentence Arabic fragments
4. Self-containment — the unit teaches a complete thought
5. Granularity — lowest priority; optimize separately
</constitution>"""


# ═══════════════════════════════════════════════════════════════════
# GROUP rule modules — progressive disclosure (DR28 IU-3)
#
# CORE + OUTPUT_FORMAT are always loaded.
# Conditional modules are loaded based on chunk content flags (IU-4).
# Composition order: CORE → conditional modules → OUTPUT_FORMAT.
# ═══════════════════════════════════════════════════════════════════

GROUP_CORE_RULES = """\
You previously classified segments of this Arabic text by scholarly function.
Now group these classified segments into TEACHING UNITS — self-contained
scholarly segments that each teach one distinct concept, ruling, or argument.
A teaching unit is the smallest segment a student could study and learn
something complete from.

GROUPING RULES:
- GENERAL PRINCIPLE (EE-1): An explained object and its immediately \
following explanation form one teaching unit by default. The explained \
text is context for the explanation — separating them orphans the \
explanation. This applies to: hadith + sharh, verse (matn) + commentary, \
definition + examples, principle + reasoning, ruling + evidence. Split \
only when a different scholarly function boundary begins.
- A position (opinion_statement) + its evidence + any counter-evidence
  + conclusion = one unit
- A definition + its examples = one unit
- A question and its answer belong in the same unit
- A rule_statement + its condition_exception(s) = one unit
- Never group unrelated content (e.g., two different مسائل) into one unit
- structural_transition segments may be grouped with the content they introduce,
  or stand alone if they serve as section markers
- FORGIVING RETENTION: When a small linked sentence (≤15% of the unit, \
maximum ~30 words) would need removal to avoid function mixing, but removing \
it would start the next unit at an unsafe causal continuation (primary causal \
particles: لأن, فإن, ولأنه, فإنه, إذ, لكونه, حيث إن, بناء على ذلك — other conjunctions are \
evaluated normally under C-SC-2), RETAIN the carryover. Apply forgiving \
retention at most once per teaching unit; if the next boundary also triggers \
it, the boundary stands and the causal particle is flagged in \
self_containment_notes. The harm of orphaned causal particles exceeds the \
harm of minor function mixing.
- TITLE RETENTION: Retain the chapter/section title in the teaching unit when: \
(a) a demonstrative (هذا الباب, في هذا الفصل) references it, OR \
(b) the title carries scholarly content the text does not repeat — common \
in hadith collections with fiqhi tarajim where the bāb title IS the author's \
ruling. Title retention is per-unit, not global.

NUMBERED ITEM BOUNDARIES:
- Numbered items (1-, 2-, 3-... or فائدة/مسألة + number) and classical \
textual ordinals (أحدها, والثاني, والثالث, الوجه الأول) are unit \
boundary signals. Default: each numbered or ordinally-marked item is a \
separate unit.
- Two numbered items covering different topics MUST NOT be merged \
(e.g., items about void bequests and burial are separate units).
- Exception: consecutive sub-20-word items in the same ruling cluster \
may be grouped. If uncertain, split.

DECONTEXTUALIZATION PREVENTION (critical):
- A reported position ("قال أبو حنيفة...") and its refutation
  ("ورد عليه بأن...") MUST be in the same unit
- A counter-argument MUST include enough of the original argument to be
  understood on its own
- Evidence cited for a ruling MUST stay with the ruling
- A condition and its exception (rule + إلا clause) belong together
- A verdict/tarjīḥ phrase (والصواب، الراجح، الأصح، المعتمد، الأقوى) that
  selects among competing positions should remain with the alternatives it
  judges when the alternatives are only briefly mentioned. However, when a
  long dispute section extensively lists multiple opinions with evidence,
  the tarjīḥ conclusion MAY be a separate teaching unit (see FP-8).
  Default: keep together unless the dispute section is substantial enough
  to stand alone as a distinct teaching unit.
- Qualifications and disclaimers (لكن، غير أن، إلا أن، على خلاف) MUST
  remain with the statement they qualify. A rule without its qualification
  is actively misleading.
- A question (فإن قيل، سؤال، اعترض) and its answer (قلنا، الجواب، وأجيب)
  MUST be in the same unit — even when multiple question-answer cycles
  appear in sequence

SELF-CONTAINMENT EVALUATION:
For each teaching unit, evaluate self-containment against these criteria:

C-SC-1 (Term Resolution): Every technical term is either defined within the
  unit, is standard terminology any student of the science would know, or is
  flagged as requiring external knowledge.

C-SC-2 (Reference Resolution): Every pronoun, demonstrative, anaphoric
  reference, or IMPLIED dependency resolves within the unit. No dangling
  references to text outside the unit. Watch for:
  - Visible: هذا/هذه/هؤلاء, المذكور/ما تقدم/ما سبق, pronoun suffixes
    (ـه/ـها/ـهم/ـهما), opening conjunctions (لأن/فإن)
  - Invisible (taqdir): implied subjects in قال/ذهب/رأى where the speaker
    is determined from prior context, not stated in this unit
  Note: opening و does NOT always indicate a dangling reference — it may
  simply continue within the same topic. Reason about whether each referent
  (visible or implied) resolves inside the unit. Do not flag blindly.

C-SC-3 (Evidence Completeness): Every evidence citation either includes its
  text, is a universally known citation identifiable by its opening words
  (e.g., حديث "إنما الأعمال بالنيات"), or is flagged.

C-SC-4 (Argument Completeness): The unit's argument, ruling, or teaching is
  complete — not a fragment whose premise or conclusion is elsewhere.

C-SC-5 (Dialogue Completeness): If the unit responds to another scholar's
  position, enough of that position is included to understand the response.

Assign self_containment as:
- FULL: All five criteria met. The unit stands alone.
- PARTIAL: Most criteria met, but some context would help. Populate
  self_containment_notes describing what's missing.
- DEPENDENT: Cannot be understood alone. Populate self_containment_notes
  explaining the dependency."""

GROUP_HADITH_RULES = """\
HADITH RULES:
- A hadith + its chain + commentary = one unit (for hadith citations \
within broader discussions — NOT for derived benefits sections).
- DERIVED BENEFITS: Sections opening with "ما يؤخذ من الحديث:" or "فوائد:" \
are derived benefits from the preceding hadith. \
Default: split per numbered item. Each item is a separate teaching unit. \
Exception: consecutive items that are fragments of one immediate ruling \
cluster AND are individually under 20 words may be grouped into one excerpt. \
If uncertain whether items are same-topic or different-topic, SPLIT. \
(This split-on-uncertainty rule is specific to derived benefits and \
numbered items. For general grouping, prefer keeping related content \
together per EE-1 rather than splitting aggressively — overgranulation \
is more harmful than undergranulation, FP-9.)
- The hadith text + gharib + المعنى الإجمالي form the inseparable core \
of a hadith commentary unit. Fawa'id/ما يؤخذ points may be separate.
- Exception: numbered غريب الحديث items within the hadith inseparable core \
(hadith + gharib + المعنى الإجمالي) do NOT split — they stay with the core."""

GROUP_VERSE_RULES = """\
VERSE RULES:
- A Quranic verse (evidence_quran) + the commentary immediately following \
it form one teaching unit per EE-1. The verse provides the textual basis \
for the commentary — separating them makes the commentary \
reference-dependent."""

GROUP_FIQH_RULES = """\
FIQH RULES:
- MULTI-FUNCTION SPLIT: A passage substantively containing introduction + \
ruling + proof-overview + refutation must NOT remain as one unit. Split at \
function boundaries. A chapter-intro sentence that merely touches on the \
ruling may stay via FORGIVING RETENTION; but when each function is \
substantive, they are separate teaching units. Exemption: semantic \
dependencies (تخصيص/شرط/استثناء/تقييد) must stay with عام regardless of \
proportion — splitting عام from مخصص creates false absolutes (FP-5).
- PROOF STRUCTURE: Scholars present proofs in 3 phases: (1) cite the proof, \
(2) explain it, (3) defend/refute objections. Phases 1+2 belong together per \
EE-1 (proof + explanation = one unit). Phase 3 (refutations/ردود) MAY be a \
separate unit when it answers a different question than phases 1+2. \
For dialectical structures (فإن قيل/قلنا), refutation always stays with \
the objection it answers."""

GROUP_DIALECTICAL_RULES = """\
DIALECTICAL RULES:
- Dialectical structures (فإن قيل/قلنا, سؤال/الجواب, اعترض/وأجيب): \
each objection-response pair forms one unit. When multiple cycles appear \
in sequence, each cycle is a separate unit — do not merge different \
objection-response pairs.
- A refutation always stays with the objection it answers (FP-14). \
Never separate a refutation into its own teaching unit without the \
position being refuted."""

GROUP_INTRO_RULES = """\
INTRODUCTION RULES:
- INTRODUCTION SCOPE: Distinguish chapter-specific introductions ("هذا الباب \
يذكر فيه...") from full-topic introductions that define the science or \
subject. A chapter-specific intro applies only to this source's chapter; \
treating it as a universal topic introduction creates scope mismatch.
- MENTION IS NOT EXCERPT: A topic being briefly mentioned in passing does NOT \
make it an excerpt. Only create a teaching unit when the text substantively \
discusses the topic (explains, rules on, or proves something about it). Brief \
mentions in unrelated passages must not generate forced or empty excerpt units."""

GROUP_CRITICAL_REMINDERS = """\
REMEMBER — these override all other considerations:
- text_snippet must be an EXACT character-for-character copy from the input
- An explained object + its explanation = one teaching unit (EE-1)
- A reported position + its refutation MUST be in the same unit
- A question + its answer MUST be in the same unit"""

GROUP_OUTPUT_FORMAT = """\
For each teaching unit, provide:
- unit_index: 0-based position in the sequence
- segment_indices: list of segment_index values composing this unit
  (must be a contiguous ascending sequence, e.g. [3, 4, 5])
- start_word: the start_word of the first constituent segment
- end_word: the end_word of the last constituent segment
- text_snippet: the FIRST 80 CHARACTERS of this unit's text, copied EXACTLY
  from the input — preserve all diacritics, punctuation, and whitespace.
- primary_function: the dominant scholarly function (must be a function present
  in the constituent segments)
- secondary_functions: other functions present in the unit (may be empty)
- description_arabic: a brief Arabic description of what this unit teaches,
  5 to 35 Arabic words. Write it as a student-facing summary.
- self_containment: FULL, PARTIAL, or DEPENDENT
- self_containment_notes: present and non-empty for PARTIAL/DEPENDENT;
  absent or null for FULL

The text format is: {structural_format}"""


# ═══════════════════════════════════════════════════════════════════
# CLASSIFY critical reminders — instruction sandwich (DR28 IU-6)
#
# Restated at the end of the user message to reinforce the most
# compliance-critical rules. Targets the recency bias demonstrated
# in "Lost in the Middle" research.
# ═══════════════════════════════════════════════════════════════════

CLASSIFY_CRITICAL_REMINDERS = """\
REMEMBER — these override all other considerations:
- text_snippet must be an EXACT character-for-character copy from the input
- Classify by scholarly FUNCTION, not by surface language or section labels
- An isnad chain + its matn = one segment (never split)
- Derived rulings (ما يؤخذ من الحديث) are rule_statement, NOT evidence_hadith"""


# ═══════════════════════════════════════════════════════════════════
# ENRICH critical reminders — instruction sandwich (DR28 IU-7)
# ═══════════════════════════════════════════════════════════════════

ENRICH_CRITICAL_REMINDERS = """\
REMEMBER — these override all other considerations:
- Wrong attributions become wrong beliefs. When uncertain: null + low \
confidence, NEVER guess.
- Attribute the POSITION's school, not the AUTHOR's school
- Do NOT invent or infer hadith grades — record ONLY what the text states
- Use "narrator" role for hadith transmission chains (عن، حدثنا), \
not "quoted_opinion\""""
