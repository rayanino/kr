"""Generate bughunt and edge case tasks for the weekend sprint.

Reads engine source files and generates detailed bughunt task prompts.
Merges with existing sprint_manifest.json to produce the final manifest.

Usage:
  python scripts/generate_sprint_tasks.py --output overnight/sprint_manifest.json
  python scripts/generate_sprint_tasks.py --dry-run
"""
from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Task templates
# ---------------------------------------------------------------------------

BUGHUNT_PROMPT = """BUGHUNT — {module_name}

Read {file_path} carefully, line by line. You are looking for REAL BUGS, not style issues.
This is the {engine_name} engine, part of the KR Islamic scholarly text pipeline.

PIPELINE CONTEXT (5 engines, NOT 7 — passaging/atomization are STALE):
Source -> Normalization -> Excerpting -> Taxonomy -> Synthesis

CHECK FOR THESE BUG PATTERNS:

1. **None/null handling**: Any code path where None causes AttributeError or TypeError?
   Check EVERY .attribute access, dict[key] lookup, and function call argument.

2. **Arabic string safety**: Any use of .lower(), .upper(), .strip(), .replace() on Arabic text?
   Any regex using \\d (matches Arabic-Indic digits ٠-٩) instead of [0-9]?
   Any \\b word boundary (doesn't work for Arabic clitics)?
   Read .claude/rules/regex-arabic-digits.md and .claude/rules/python-code.md for full rules.

3. **Off-by-one errors**: Any range(), slice [:end], or index [i] that might be wrong by 1?
   Check loop boundaries, string slicing, list indexing.

4. **Silent data loss**: Any except blocks that catch and continue without logging?
   Any conditional returns that silently drop data? Any `or default_value` that hides None?

5. **Type coercion bugs**: Any int()/float() on strings without try/except?
   Any bool() that treats empty string/list as False when it shouldn't?

6. **File I/O safety**: Any open() without encoding='utf-8'?
   Any file write without atomic pattern (write tmp + rename)?

7. **D-023 violations**: Any function that transforms data but drops upstream metadata fields?
   Check: does the function receive a dict/model and return a subset of its fields?

8. **Pydantic traps**: Any Field(None, ...) that should be Field(default=None, ...)?
   Any model_dump() that might strip Arabic text? Any model_validate() without error handling?

9. **Concurrency/race conditions**: Any shared state without locks?
   Any file read-then-write that another process could interfere with?

10. **Logic errors**: Any boolean conditions that could be wrong?
    Any early returns that skip important cleanup? Any fallthrough cases in if/elif chains?

{extra_context}

BEFORE reviewing, read the module's existing test files to understand what is already tested.
Look for patterns in the tests that reveal the developer's assumptions — bugs often hide where
assumptions are wrong.

For EVERY potential bug found:
- Quote the exact code (file path and line number)
- Explain WHY it is a bug (what input triggers it, what goes wrong)
- Describe the IMPACT (data corruption? crash? silent wrong answer?)
- Rate severity: CRITICAL (data corruption/loss) / HIGH (wrong output) / MEDIUM (crash) / LOW (cosmetic)
- Provide a concrete reproducer (specific input that would trigger the bug)
- If the engine is NOT frozen (not excerpting): suggest a fix (code snippet)
- If the engine IS excerpting: do NOT suggest fixes, only document the bug for the day-session team

If you find NO bugs after thorough review, say so explicitly — don't invent false positives.

Write overnight/results/{task_id}/findings.md with all findings.
Write overnight/results/{task_id}/findings.json:
{{"bugs_found": N, "critical": N, "high": N, "medium": N, "low": N, "lines_reviewed": N}}
"""

EDGECASE_PROMPT = """EDGE CASE TESTING — {topic}

You are generating and testing edge cases for Arabic text handling in the KR pipeline.
The pipeline has 5 engines: Source, Normalization, Excerpting, Taxonomy, Synthesis.

{description}

STEPS:
1. Read the relevant source files to understand how the code handles this text pattern
2. Generate 8-15 edge case test inputs (real Arabic text, not transliteration)
3. Write a NEW test file: {test_file}
4. Each test must: construct the edge case input, run it through the relevant function, verify output correctness
5. Run: python -m pytest {test_file} -x -v --tb=short

RULES:
- Use REAL Arabic text: بسم الله الرحمن الرحيم, الحمد لله رب العالمين, etc.
- Include diacritics (تَشْكِيل) in test inputs where relevant
- Test both the happy path AND the failure path for each edge case
- DO NOT modify any existing files — only create the NEW test file
- DO NOT modify any file under engines/*/src/ or shared/*/src/

Write overnight/results/{task_id}/findings.json:
{{"tests_added": N, "tests_passed": N, "tests_failed": N, "edge_cases_covered": N}}
"""

CONTRACT_EXHAUST_PROMPT = """CONTRACT EXHAUSTION — {engine_name} Engine

You are exhaustively testing every field of every Pydantic model in {contracts_path}.

STEPS:
1. Read {contracts_path} — identify ALL Pydantic models (BaseModel subclasses)
2. For each model, for each field:
   - Test with valid value
   - Test with None (if Optional)
   - Test with boundary values (empty string, 0, -1, maxint, very long string)
   - Test with Arabic text containing diacritics
   - Test with missing field (should it raise ValidationError?)
3. Test model_dump() → model_validate() roundtrip preserves all data (especially Arabic text)
4. Test JSON serialization roundtrip preserves Arabic text byte-for-byte
5. Test cross-model references (e.g., excerpt_id format matches what the next engine expects)

Write a NEW test file: {test_file}
Run: python -m pytest {test_file} -x -v --tb=short

DO NOT modify any existing files.

Write overnight/results/{task_id}/findings.json:
{{"tests_added": N, "models_tested": N, "fields_tested": N, "roundtrip_bugs": N}}
"""

# ---------------------------------------------------------------------------
# Task generators
# ---------------------------------------------------------------------------


def make_task(
    task_id: str, name: str, category: str, prompt: str,
    model: str = "opus", timeout: int = 30, turns: int = 25,
    safety: str = "readonly", bookend: bool = False, priority: int = 5,
) -> dict:
    # Readonly tasks: no Bash (Codex review #2 — prevents accidental writes)
    tools = ["Read", "Glob", "Grep"]
    if category in ("sprint_test", "sprint_script"):
        tools = ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
        safety = "additive"
    return {
        "task_id": task_id, "name": name, "category": category,
        "prompt": prompt, "safety_level": safety, "execution_mode": "cli",
        "model": model, "max_budget_usd": 0, "timeout_minutes": timeout,
        "allowed_tools": tools, "permission_mode": "bypassPermissions",
        "depends_on": [], "priority": priority, "max_turns": turns,
        "codex_flags": [], "bookend": bookend,
    }


def generate_bughunt_tasks() -> list[dict]:
    """Generate bughunt tasks for each engine source module."""
    tasks = []

    # Source engine modules (can hunt bugs AND suggest fixes)
    source_modules = [
        ("trust_evaluator", "engines/source/src/trust_evaluator.py",
         "Focus on the 5-factor weighted trust calculation. Check weight arithmetic, None handling for missing factors, boundary values (0.0, 1.0). The weights are: author_standing=0.30, tahqiq_quality=0.25, publisher=0.15, source_authority=0.15, text_fidelity=0.15."),
        ("deduplication", "engines/source/src/deduplication.py",
         "Focus on composite key matching. Check Arabic title comparison (are diacritics handled?). Check what happens with empty/None fields in the composite key."),
        ("freezer", "engines/source/src/freezer.py",
         "Focus on TOCTOU protection (SHA-256 verify after write). Check file permission handling, atomic write pattern, encoding on Windows paths."),
        ("metadata_inference", "engines/source/src/metadata_inference.py",
         "Focus on LLM response parsing. Check JSON parsing error handling, what happens with truncated responses, Arabic text extraction from LLM output."),
        ("consensus", "engines/source/src/consensus.py",
         "Focus on multi-model consensus logic. Check agreement calculation, what happens when one model returns None, temperature settings."),
        ("validation", "engines/source/src/validation.py",
         "Focus on validation rules. Check threshold comparisons (>, >=, off-by-one), error code generation, what happens with edge-case page counts (0, 1, maxint)."),
        ("shamela_extractor", "engines/source/src/extractors/shamela.py",
         "Focus on HTML parsing. Check for unclosed tags, malformed HTML, encoding detection, Arabic text extraction from HTML entities."),
        ("format_detection", "engines/source/src/format_detection.py",
         "Focus on file type detection. Check edge cases: empty files, files with wrong extensions, binary files, files with BOM markers."),
        ("scholar_authority", "engines/source/src/scholar_authority.py",
         "Focus on name matching and registry operations. Check Arabic name comparison, death date parsing, school attribution logic."),
        ("work_registry", "engines/source/src/work_registry.py",
         "Focus on work registration and lookup. Check ID generation uniqueness, concurrent access patterns, update conflict handling."),
    ]

    for module_name, file_path, extra_context in source_modules:
        tasks.append(make_task(
            f"bughunt-source-{module_name.replace('_', '-')}",
            f"Bughunt: source engine {module_name}",
            "sprint_analysis",
            BUGHUNT_PROMPT.format(
                module_name=module_name, file_path=file_path,
                engine_name="Source", extra_context=extra_context,
                task_id=f"bughunt-source-{module_name.replace('_', '-')}",
            ),
            timeout=30, priority=3,
        ))

    # Normalization engine modules
    norm_modules = [
        ("shamela", "engines/normalization/src/normalizers/shamela.py",
         "Focus on the 6-pass HTML normalization pipeline. Check: HTML entity handling, tag stripping order, footnote detection, page boundary handling. This is the most critical normalizer."),
        ("structure_discovery", "engines/normalization/src/structure_discovery.py",
         "Focus on 4-tier heading detection. Check: heading level assignment, same-page heading ordering (L-003 known issue), Arabic text in heading extraction."),
        ("layer_detector", "engines/normalization/src/layer_detector.py",
         "Focus on typographic layer detection (bold, brackets, transitions). Check: bold threshold (50 vs SPEC 80, L-005), bracket matching, Arabic transition phrase detection."),
        ("boundary_continuity", "engines/normalization/src/boundary_continuity.py",
         "Focus on mid-sentence division_break signals. Check: sentence boundary detection with Arabic text, conditional reasoning markers (L-008), guillemet hadith distance (L-009)."),
        ("content_flagger", "engines/normalization/src/content_flagger.py",
         "Focus on boolean content flags per page. Check: flag combination validity, edge cases with empty pages, pages with only footnotes."),
        ("writer", "engines/normalization/src/writer.py",
         "Focus on atomic write pattern (temp dir → rename → cleanup). Check: partial write recovery (L-011), encoding handling, orphan state detection."),
        ("plain_text", "engines/normalization/src/normalizers/plain_text.py",
         "Focus on paragraph splitting for non-HTML sources. Check: line ending handling (\\r\\n vs \\n), empty paragraph handling, Arabic paragraph detection."),
        ("validation", "engines/normalization/src/validation.py",
         "Focus on 10 self-validation checks. Check: threshold comparisons, error severity assignment, what happens when validation itself throws."),
        ("dispatcher", "engines/normalization/src/dispatcher.py",
         "Focus on format routing (§4.A.1). Check: unknown format handling, fallback behavior, error propagation from normalizers."),
        ("errors", "engines/normalization/src/errors.py",
         "Focus on error code definitions and severity mapping. Check: NORM_* code uniqueness, severity consistency, missing error paths."),
        ("content_census", "engines/normalization/src/content_census.py",
         "Focus on content census implementation. Check if this is implemented or stub, any statistical calculations, Arabic word counting."),
        ("base_normalizer", "engines/normalization/src/normalizers/base.py",
         "Focus on the base normalizer interface. Check: contract compliance, method signatures, default behavior for unimplemented methods."),
    ]

    for module_name, file_path, extra_context in norm_modules:
        tasks.append(make_task(
            f"bughunt-norm-{module_name.replace('_', '-')}",
            f"Bughunt: normalization engine {module_name}",
            "sprint_analysis",
            BUGHUNT_PROMPT.format(
                module_name=module_name, file_path=file_path,
                engine_name="Normalization", extra_context=extra_context,
                task_id=f"bughunt-norm-{module_name.replace('_', '-')}",
            ),
            timeout=30, priority=3,
        ))

    # Excerpting engine modules (readonly — under CLI transformation)
    exc_modules = [
        ("phase1_assembly", "engines/excerpting/src/phase1_assembly.py",
         "CRITICAL: This module is under active CLI backend reformation. Find bugs but DO NOT suggest modifications to this file. Focus on: chunk assembly logic, split handling, layer rebasing, offset calculations."),
        ("phase2_classify", "engines/excerpting/src/phase2_classify.py",
         "CRITICAL: Do NOT modify. Focus on: LLM classification logic, 16-type taxonomy, confidence thresholds, Arabic text in classification prompts."),
        ("phase2_group", "engines/excerpting/src/phase2_group.py",
         "CRITICAL: Do NOT modify. Focus on: teaching unit grouping, topic coherence calculation, group size constraints."),
        ("phase3_deterministic", "engines/excerpting/src/phase3_deterministic.py",
         "CRITICAL: Do NOT modify. Focus on: 9 F-DET fields, layer attribution (LA rules), evidence detection, quoted scholars computation. Previous bugs found here: LA-4 vs LA-3 firing incorrectly (fixed in probe-la-none-authors)."),
        ("phase3_enrichment", "engines/excerpting/src/phase3_enrichment.py",
         "CRITICAL: Do NOT modify. Focus on: LLM enrichment prompts, response parsing, token budget management (dynamic scaling at 1500 words)."),
        ("phase3_consensus", "engines/excerpting/src/phase3_consensus.py",
         "CRITICAL: Do NOT modify. Focus on: cross-model verification, generator!=verifier enforcement (T-5), disagreement resolution."),
        ("phase3_validation", "engines/excerpting/src/phase3_validation.py",
         "CRITICAL: Do NOT modify. Focus on: output validation rules, error code assignment, human gate triggers."),
        ("writer", "engines/excerpting/src/writer.py",
         "CRITICAL: Do NOT modify. Focus on: JSONL serialization, Arabic text byte-for-byte preservation, gate queue formatting."),
    ]

    for module_name, file_path, extra_context in exc_modules:
        tasks.append(make_task(
            f"bughunt-exc-{module_name.replace('_', '-')}",
            f"Bughunt: excerpting engine {module_name}",
            "sprint_analysis",
            BUGHUNT_PROMPT.format(
                module_name=module_name, file_path=file_path,
                engine_name="Excerpting", extra_context=extra_context,
                task_id=f"bughunt-exc-{module_name.replace('_', '-')}",
            ),
            timeout=30, priority=3,
        ))

    return tasks


def generate_edgecase_tasks() -> list[dict]:
    """Generate Arabic text edge case testing tasks."""
    edge_cases = [
        ("hamza-variants", "Hamza variant handling (أ إ آ ؤ ئ ء)",
         "Test how the pipeline handles the 7 hamza forms:\n- أ (alef with hamza above)\n- إ (alef with hamza below)\n- آ (alef with madda)\n- ؤ (waw with hamza)\n- ئ (yaa with hamza)\n- ء (standalone hamza)\n- ٱ (alef wasla)\n\nGenerate texts where hamza form matters for meaning (e.g., أكل vs إكل). Test normalization, comparison, search. Read engines/source/src/text_utils.py and engines/normalization/src/ for hamza handling.",
         "engines/source/tests/test_edgecase_hamza.py"),
        ("taa-marbuta", "Taa marbuta vs haa confusion (ة vs ه)",
         "Test the ة/ه distinction:\n- Words ending in ة (e.g., مدرسة, حقيقة, صلاة)\n- Words ending in ه (e.g., كتابه, منه, وجه)\n- Words where confusion changes meaning (e.g., صلاة prayer vs صلاه his prayer)\n\nTest: comparison functions, deduplication, scholar name matching.",
         "engines/source/tests/test_edgecase_taa_marbuta.py"),
        ("alef-variations", "Alef normalization (ا أ إ آ ٱ)",
         "Test alef form variations in Arabic text:\n- ا (plain alef) vs أ (alef hamza above) vs إ (alef hamza below) vs آ (alef madda) vs ٱ (alef wasla)\n- Common words with alef variants: الإسلام/الاسلام, أحمد/احمد\n- Test whether normalization is applied and if so, whether it preserves the distinction when needed.",
         "engines/source/tests/test_edgecase_alef.py"),
        ("shadda-stacking", "Shadda with other diacritics (double stacking)",
         "Test shadda (شّ) combined with other diacritics:\n- شَّ (shadda + fathah)\n- شُّ (shadda + dammah)\n- شِّ (shadda + kasrah)\n- شًّ (shadda + fathatan — rare but valid)\n- Does the code handle the Unicode ordering correctly? Shadda should come before the vowel diacritic.",
         "engines/source/tests/test_edgecase_shadda.py"),
        ("tatweel-positions", "Tatweel/kashida (ـ) in various positions",
         "Test tatweel character (U+0640) handling:\n- Inside words: كـتاب vs كتاب\n- Between words: كتاب ـ الله\n- Multiple consecutive: كــــتاب\n- At word boundaries\n- Test whether tatweel is stripped, preserved, or ignored in comparison/dedup.",
         "engines/source/tests/test_edgecase_tatweel.py"),
        ("mixed-bidi", "Mixed Arabic/Latin bidirectional text",
         "Test bidirectional text handling:\n- Arabic with embedded Latin: قال النبي (peace be upon him)\n- Latin with embedded Arabic: The word كتاب means book\n- Numbers in Arabic context: سنة 1445 هجرية\n- URLs in Arabic text: انظر https://example.com\n- Parentheses: (قال الشافعي) vs (Imam Shafi'i)",
         "engines/source/tests/test_edgecase_bidi.py"),
        ("arabic-digits", "Arabic-Indic digits (٠١٢٣٤٥٦٧٨٩) vs Western (0-9)",
         "Test digit handling:\n- Arabic-Indic: ٠١٢٣٤٥٦٧٨٩ (U+0660-0669)\n- Eastern Arabic-Indic: ۰۱۲۳۴۵۶۷۸۹ (U+06F0-06F9)\n- Western: 0123456789\n- Mixed: page ٢٣ vs page 23\n- Test regex patterns: does \\d match Arabic-Indic digits? (It should NOT in most KR contexts)\n- Read .claude/rules/regex-arabic-digits.md",
         "engines/source/tests/test_edgecase_digits.py"),
        ("diacritic-combinations", "Full tashkeel diacritic combinations",
         "Test all diacritics:\n- فَتْحَة (fathah) U+064E\n- ضَمَّة (dammah) U+064F\n- كَسْرَة (kasrah) U+0650\n- سُكُون (sukun) U+0652\n- شَدَّة (shadda) U+0651\n- تَنْوِين فَتْح (fathatan) U+064B\n- تَنْوِين ضَمّ (dammatan) U+064C\n- تَنْوِين كَسْر (kasratan) U+064D\n\nTest: text with full tashkeel survives serialization roundtrip, comparison with/without diacritics, diacritic stripping.",
         "engines/source/tests/test_edgecase_diacritics.py"),
        ("zero-width-chars", "Zero-width characters in Arabic text",
         "Test invisible characters per .claude/rules/input-sanitization.md:\n- U+200B (zero-width space) — should be stripped\n- U+200C (ZWNJ) — valid in Persian, strip in Arabic\n- U+200D (ZWJ) — valid in Arabic ligatures (لا)\n- U+200E/F (LTR/RTL marks) — should be stripped\n- U+FEFF (BOM) — should be stripped\n- U+2060 (word joiner) — should be stripped\n\nTest: insertion between Arabic letters, at word boundaries, in metadata fields.",
         "engines/source/tests/test_edgecase_zero_width.py"),
        ("presentation-forms", "Arabic presentation forms vs standard forms",
         "Test Unicode presentation forms:\n- Presentation Forms-A (U+FB50-U+FDFF): ﻻ ﷲ ﷺ\n- Presentation Forms-B (U+FE70-U+FEFF): ﺎ ﺏ ﺕ\n- These are visual variants of standard Arabic characters\n- Does the code normalize them? Should it?\n- Test: comparison between presentation form and standard form, serialization roundtrip.",
         "engines/source/tests/test_edgecase_presentation.py"),
        ("lam-alef-ligature", "Lam-alef ligature (لا) handling",
         "Test the lam-alef ligature:\n- لا (lam + alef) — mandatory ligature in Arabic\n- Does string length count it as 1 or 2 characters?\n- Does slicing mid-ligature cause corruption?\n- U+FEFB (ligature form) vs U+0644 U+0627 (component form)\n- Test in: text slicing, excerpt boundary detection, word counting.",
         "engines/source/tests/test_edgecase_lam_alef.py"),
        ("quran-marks", "Quran-specific marks and symbols",
         "Test Quranic text markers:\n- ﴿ ﴾ (ornate brackets for Quran quotes)\n- ۩ (sajda mark)\n- ۞ (rub el hizb)\n- ۝ (end of ayah)\n- ﷽ (bismillah ligature)\n- ﷺ (sallallahu alayhi wasallam)\n- Test: detection, preservation, distinction from non-Quranic text.",
         "engines/source/tests/test_edgecase_quran_marks.py"),
    ]

    tasks = []
    for topic_id, topic, description, test_file in edge_cases:
        tasks.append(make_task(
            f"edgecase-{topic_id}",
            f"Edge case testing: {topic}",
            "sprint_test",
            EDGECASE_PROMPT.format(
                topic=topic, description=description,
                test_file=test_file, task_id=f"edgecase-{topic_id}",
            ),
            timeout=35, priority=4, turns=30,
        ))

    return tasks


def generate_contract_tasks() -> list[dict]:
    """Generate contract exhaustion test tasks."""
    engines = [
        ("source", "engines/source/contracts.py", "engines/source/tests/test_contracts_exhaust.py"),
        ("normalization", "engines/normalization/contracts.py", "engines/normalization/tests/test_contracts_exhaust.py"),
        # excerpting removed — under CLI transformation (Codex review #6)
        ("taxonomy", "engines/taxonomy/contracts.py", "engines/taxonomy/tests/test_contracts_exhaust.py"),
        ("synthesis", "engines/synthesis/contracts.py", "engines/synthesis/tests/test_contracts_exhaust.py"),
    ]

    # Shared modules: point at the actual Pydantic models they import from
    # engines/source/contracts.py (Codex review #10 — these files use dataclasses,
    # not BaseModel, so test their behavior not their schema)
    shared = [
        ("shared-consensus", "shared/consensus/src/consensus.py", "shared/consensus/tests/test_behavior_exhaust.py"),
        ("shared-human-gate", "shared/human_gate/src/human_gate.py", "shared/human_gate/tests/test_behavior_exhaust.py"),
        ("shared-scholar-authority", "shared/scholar_authority/src/scholar_authority.py", "shared/scholar_authority/tests/test_behavior_exhaust.py"),
    ]

    tasks = []
    for engine_id, contracts_path, test_file in engines + shared:
        tasks.append(make_task(
            f"exhaust-{engine_id}",
            f"Contract exhaustion: {engine_id}",
            "sprint_test",
            CONTRACT_EXHAUST_PROMPT.format(
                engine_name=engine_id.replace("-", " ").title(),
                contracts_path=contracts_path,
                test_file=test_file,
                task_id=f"exhaust-{engine_id}",
            ),
            timeout=35, priority=4, turns=30,
        ))

    return tasks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Generate sprint tasks")
    parser.add_argument("--output", default="overnight/sprint_manifest.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--merge", help="Existing manifest to merge with")
    args = parser.parse_args()

    # Generate new tasks
    bughunt = generate_bughunt_tasks()
    edgecase = generate_edgecase_tasks()
    contract = generate_contract_tasks()

    new_tasks = bughunt + edgecase + contract
    print(f"Generated {len(new_tasks)} new tasks:")
    print(f"  Bughunt: {len(bughunt)}")
    print(f"  Edge case: {len(edgecase)}")
    print(f"  Contract: {len(contract)}")

    # Merge with existing manifest if specified
    if args.merge:
        merge_path = PROJECT_DIR / args.merge
        with open(merge_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing_tasks = existing["tasks"]
        existing_ids = {t["task_id"] for t in existing_tasks}

        # Only add tasks with new IDs
        added = [t for t in new_tasks if t["task_id"] not in existing_ids]
        all_tasks = existing_tasks + added
        print(f"  Merged: {len(existing_tasks)} existing + {len(added)} new = {len(all_tasks)} total")
    else:
        all_tasks = new_tasks
        print(f"  Total: {len(all_tasks)}")

    # Validate no duplicate IDs
    ids = [t["task_id"] for t in all_tasks]
    dupes = [x for x in ids if ids.count(x) > 1]
    if dupes:
        print(f"WARNING: Duplicate task IDs: {set(dupes)}")

    if args.dry_run:
        print("\n=== DRY RUN ===")
        for i, t in enumerate(all_tasks, 1):
            print(f"  {i:3d}. [{t['priority']}] {t['category']:16s} {t['task_id']}")
        return

    # Write output
    output_path = PROJECT_DIR / args.output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"tasks": all_tasks}, f, indent=2, ensure_ascii=False)
    print(f"\nWritten to {output_path}")


if __name__ == "__main__":
    main()
