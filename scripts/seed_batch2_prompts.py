"""Seed the DR relay queue with Batch 2 prompts from dr_relay_queue_batch_2.md.

One-time script. Run once to populate the knowledge_base/dr_prompts/ JSONL.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from scripts.autonomous_schemas import (
    DRPrompt,
    DRTarget,
    Priority,
    ResearchCategory,
    append_jsonl,
)

KB = project_root / "overnight_codex" / "autonomous" / "knowledge_base"
PROMPTS_FILE = KB / "dr_prompts" / "batch_2.jsonl"

BATCH_2: list[dict] = [
    {
        "prompt_id": "RQ-B2-001",
        "target": DRTarget.GEMINI,
        "category": ResearchCategory.SCHOLARLY_DOMAIN,
        "priority": Priority.HIGH,
        "topic": "Aqidah Tree: حجية فهم السلف vs إجماع السلف",
        "unblocks": "Aqidah tree v2.0 installation (5 of 7 pending decisions)",
        "file_bundle": "library/sciences/aqidah/tree_history/aqidah_v0_2.yaml",
        "estimated_minutes": 25,
        "prompt_text": (
            "You are an expert in aqidah (Islamic creed) and the methodology of Salafi and traditional Sunni theology. "
            "I am building a taxonomy tree for aqidah to classify scholarly excerpts.\n\n"
            "QUESTION: Is حجية فهم السلف (the authoritativeness of the Salaf's understanding) distinct enough from "
            "إجماع السلف (consensus of the Salaf) to warrant a separate leaf node in the tree?\n\n"
            "CONTEXT:\n"
            "- إجماع السلف is a recognized concept in usul al-fiqh (the consensus of the early Muslim generations as a binding proof)\n"
            "- حجية فهم السلف is used in contemporary aqidah discourse, especially by Salafi scholars, to argue that the Companions' "
            "understanding of creedal matters is authoritative beyond mere consensus\n"
            "- The question is whether these are two names for the same concept, or whether حجية فهم السلف captures something that "
            "إجماع does not\n\n"
            "WHAT I NEED:\n"
            "1. Are these the same concept with different names, or genuinely distinct?\n"
            "2. If distinct: what scholarly content would fall under حجية فهم السلف that would NOT fall under إجماع السلف? "
            "Give real examples from classical aqidah texts.\n"
            "3. If the same: which term is the canonical one to use as the leaf name?\n"
            "4. Key classical and contemporary sources that discuss this distinction (with Arabic titles and author names)."
        ),
    },
    {
        "prompt_id": "RQ-B2-002",
        "target": DRTarget.GEMINI,
        "category": ResearchCategory.SCHOLARLY_DOMAIN,
        "priority": Priority.MEDIUM,
        "topic": "Aqidah Tree: الأسماء والصفات Proportionality",
        "unblocks": "Aqidah tree v2.0 leaf count calibration",
        "file_bundle": "library/sciences/aqidah/tree_history/aqidah_v0_2.yaml",
        "estimated_minutes": 20,
        "prompt_text": (
            "You are an expert in aqidah taxonomy. I am calibrating the leaf count for the الأسماء والصفات "
            "(Divine Names and Attributes) branch of an aqidah taxonomy tree.\n\n"
            "QUESTION: The current draft has 20 leaves under الأسماء والصفات. Is this proportionally correct "
            "relative to the other aqidah branches, or is it over/under-represented?\n\n"
            "CONTEXT:\n"
            "- The full aqidah tree currently has 30 leaves total (v0.2)\n"
            "- Post-cold-read audit draft has 141 leaves\n"
            "- الأسماء والصفات is the largest single topic in most aqidah textbooks, but the tree covers ALL of aqidah: "
            "الإيمان, القدر, النبوة, السمعيات, الفرق, etc.\n"
            "- The benchmark: nahw tree has 183 leaves with careful proportionality\n\n"
            "WHAT I NEED:\n"
            "1. In canonical aqidah textbooks (العقيدة الطحاوية, لمعة الاعتقاد, الواسطية, شرح الأصفهانية), "
            "approximately what percentage of content is devoted to الأسماء والصفات vs other topics?\n"
            "2. Based on that, should 20/141 leaves (14%) be adjusted? If so, to what range?\n"
            "3. Are there sub-topics within الأسماء والصفات that could be collapsed (too granular) or that are missing?"
        ),
    },
    {
        "prompt_id": "RQ-B2-003",
        "target": DRTarget.GEMINI,
        "category": ResearchCategory.SCHOLARLY_DOMAIN,
        "priority": Priority.MEDIUM,
        "topic": "Aqidah Tree: الكهانة/العرافة vs السحر",
        "unblocks": "Aqidah tree pending decision #3",
        "file_bundle": "library/sciences/aqidah/tree_history/aqidah_v0_2.yaml",
        "estimated_minutes": 20,
        "prompt_text": (
            "You are an expert in aqidah and Islamic legal methodology. I am building a taxonomy tree and need to decide "
            "whether الكهانة والعرافة (divination/fortune-telling) and السحر (sorcery/magic) should be separate leaf nodes or combined.\n\n"
            "QUESTION: Are الكهانة/العرافة and السحر distinct enough in scholarly treatment to warrant separate taxonomy leaves?\n\n"
            "WHAT I NEED:\n"
            "1. In classical aqidah texts across traditions — كتاب التوحيد (Muhammad ibn Abd al-Wahhab), إحياء علوم الدين "
            "(al-Ghazali, Book of التوبة on السحر), تفسير القرطبي (on the verse of Harut and Marut), المغني (Ibn Qudamah, "
            "كتاب الردة section on السحر) — are الكهانة and السحر treated in separate chapters or as part of one discussion?\n"
            "2. What is the key scholarly distinction? (e.g., السحر involves actual effect vs الكهانة is knowledge claim?)\n"
            "3. Do fiqh texts (أحكام السحر, أحكام الكهانة) treat them separately with different rulings?\n"
            "4. Recommendation: one leaf or two? With reasoning from the scholarly literature across multiple traditions."
        ),
    },
    {
        "prompt_id": "RQ-B2-004",
        "target": DRTarget.GEMINI,
        "category": ResearchCategory.SCHOLARLY_DOMAIN,
        "priority": Priority.LOW,
        "topic": "Aqidah Tree: أعمال القلوب Leaf Count",
        "unblocks": "Aqidah tree calibration",
        "file_bundle": "library/sciences/aqidah/tree_history/aqidah_v0_2.yaml",
        "estimated_minutes": 20,
        "prompt_text": (
            "You are an expert in aqidah and Islamic spirituality (tasawwuf/tazkiyah). The current aqidah tree draft has "
            "6 leaves under أعمال القلوب (actions of the heart): التوكل, الخوف, الرجاء, المحبة, الإخلاص, الصبر.\n\n"
            "QUESTION: Is 6 leaves appropriate for أعمال القلوب within an aqidah context (as opposed to a tazkiyah/tasawwuf context)?\n\n"
            "WHAT I NEED:\n"
            "1. In aqidah-specific texts (not tasawwuf), how many أعمال القلوب are typically discussed?\n"
            "2. Should some of these 6 be merged (e.g., الخوف والرجاء are often paired)?\n"
            "3. Are any critical ones missing that aqidah texts specifically address (e.g., الشكر, الإنابة, الخشية as distinct from الخوف)?\n"
            "4. The key distinction: aqidah discusses these as matters of creed (إيمان), not as spiritual stations (مقامات). "
            "Does this affect which ones deserve leaves?"
        ),
    },
    {
        "prompt_id": "RQ-B2-005",
        "target": DRTarget.GEMINI,
        "category": ResearchCategory.SCHOLARLY_DOMAIN,
        "priority": Priority.LOW,
        "topic": "Aqidah Tree: الطائفة المنصورة",
        "unblocks": "Aqidah tree pending decision #5",
        "file_bundle": "library/sciences/aqidah/tree_history/aqidah_v0_2.yaml",
        "estimated_minutes": 15,
        "prompt_text": (
            "You are an expert in aqidah. I need to decide whether الطائفة المنصورة (the Victorious Sect / Saved Sect) "
            "deserves its own leaf in an aqidah taxonomy tree.\n\n"
            "QUESTION: Is الطائفة المنصورة a distinct enough aqidah concept to warrant a dedicated leaf node?\n\n"
            "CONTEXT:\n"
            "- The hadith \"لا تزال طائفة من أمتي ظاهرين على الحق\" is a foundational aqidah text\n"
            "- This topic often overlaps with الفرق والمذاهب (sects and schools) and أهل السنة والجماعة (Ahl al-Sunnah)\n"
            "- Some aqidah texts treat it as a major standalone topic; others embed it within the الفرق discussion\n\n"
            "WHAT I NEED:\n"
            "1. In major aqidah textbooks, is الطائفة المنصورة given its own chapter/section, or is it always embedded within الفرق?\n"
            "2. What unique scholarly content would fall under this leaf that doesn't belong under الفرق?\n"
            "3. Recommendation: standalone leaf, sub-leaf under الفرق, or merge? With textual evidence."
        ),
    },
    {
        "prompt_id": "RQ-B2-006",
        "target": DRTarget.GEMINI,
        "category": ResearchCategory.SCHOLARLY_DOMAIN,
        "priority": Priority.MEDIUM,
        "topic": "Sarf Tree: نشأة علم الصرف وتطوره",
        "unblocks": "Sarf tree v2.1 pending decision #1",
        "file_bundle": "library/sciences/sarf/tree_history/sarf_v1_0.yaml",
        "estimated_minutes": 20,
        "prompt_text": (
            "You are an expert in Arabic morphology (علم الصرف) and the history of Arabic linguistic sciences. "
            "I am building a taxonomy tree for sarf.\n\n"
            "QUESTION: Does نشأة علم الصرف وتطوره (the origin and development of the science of sarf) deserve its own "
            "leaf node in a sarf taxonomy tree?\n\n"
            "CONTEXT:\n"
            "- Many sarf textbooks begin with a مقدمة that discusses the history of the science\n"
            "- This content is about the science itself (meta-level), not about morphological rules\n"
            "- It includes: who founded the science, key works, methodology development, relationship to nahw\n\n"
            "WHAT I NEED:\n"
            "1. In the major sarf textbooks (شرح الملوكي for Ibn Ya'ish, المنصف for Ibn Jinni, شذا العرف for al-Hamlawi), "
            "is this treated as a standalone topic or just an introductory paragraph?\n"
            "2. Would a scholar studying sarf systematically need a dedicated entry for this topic, or is it always introductory context?\n"
            "3. Recommendation: leaf, introductory note (not a leaf), or sub-leaf under مقدمات? With evidence."
        ),
    },
    {
        "prompt_id": "RQ-B2-007",
        "target": DRTarget.GEMINI,
        "category": ResearchCategory.SCHOLARLY_DOMAIN,
        "priority": Priority.HIGH,
        "topic": "Sarf Tree: تصريف الأفعال vs أزمنة الفعل",
        "unblocks": "Sarf tree v2.1 pending decision #2 (affects tree structure)",
        "file_bundle": "library/sciences/sarf/tree_history/sarf_v1_0.yaml",
        "estimated_minutes": 25,
        "prompt_text": (
            "You are an expert in Arabic morphology (علم الصرف). I need to determine whether two closely related sarf topics "
            "are genuinely distinct or should be merged.\n\n"
            "QUESTION: Is تصريف الأفعال بعضها من بعض (deriving verbs from one another — e.g., form I→II→III) distinct from "
            "أزمنة الفعل (verb tenses — past/present/imperative)?\n\n"
            "CONTEXT:\n"
            "- تصريف الأفعال covers: الأبواب (verb forms I-X), derivation patterns, how to derive one form from another\n"
            "- أزمنة الفعل covers: الماضي, المضارع, الأمر, and how the same root appears in different tenses\n"
            "- These are related but potentially different axes: تصريف = horizontal (across forms), أزمنة = vertical (across tenses)\n\n"
            "WHAT I NEED:\n"
            "1. In classical sarf texts, are these treated as one topic or two? Cite specific chapters.\n"
            "2. Could a scholarly excerpt about تصريف الأبواب be cleanly classified under one of these two leaves? "
            "Or does it always require both?\n"
            "3. Recommendation: two separate leaves, merge into one, or restructure as parent/children?"
        ),
    },
    {
        "prompt_id": "RQ-B2-008",
        "target": DRTarget.GEMINI,
        "category": ResearchCategory.SCHOLARLY_DOMAIN,
        "priority": Priority.LOW,
        "topic": "Sarf Tree: Standalone الحذف",
        "unblocks": "Sarf tree v2.1 pending decision #3",
        "file_bundle": "library/sciences/sarf/tree_history/sarf_v1_0.yaml",
        "estimated_minutes": 20,
        "prompt_text": (
            "You are an expert in Arabic morphology. I need to determine whether الحذف (elision/deletion in morphology) "
            "is substantial enough as a standalone concept to deserve its own leaf in a sarf taxonomy tree.\n\n"
            "QUESTION: Is الحذف in sarf a standalone topic or is it always discussed as part of other morphological rules?\n\n"
            "CONTEXT:\n"
            "- الحذف appears in multiple sarf contexts: حذف حرف العلة (weak letter deletion), حذف همزة الوصل, حذف نون التوكيد, etc.\n"
            "- Some texts treat الحذف as a unified topic; others discuss each type of deletion within the relevant morphological context\n\n"
            "WHAT I NEED:\n"
            "1. Do any classical sarf texts have a dedicated chapter for الحذف as a unified concept?\n"
            "2. If a student wanted to study \"all deletion rules in sarf,\" would they find a single place to look, "
            "or must they visit 5+ different sections?\n"
            "3. Recommendation: standalone leaf that collects all deletion rules, or distribute deletion across the relevant morphological topics?"
        ),
    },
    {
        "prompt_id": "RQ-B2-009",
        "target": DRTarget.GEMINI,
        "category": ResearchCategory.SCHOLARLY_DOMAIN,
        "priority": Priority.HIGH,
        "topic": "Balagha Tree: المجاز العقلي Dual Placement",
        "unblocks": "Balagha tree architecture (affects branch structure)",
        "file_bundle": "library/sciences/balagha/tree_history/balagha_v1_0.yaml",
        "estimated_minutes": 25,
        "prompt_text": (
            "You are an expert in Arabic rhetoric (علم البلاغة) and the competing organizational frameworks of the classical "
            "rhetoricians. I need to resolve a placement conflict in my balagha taxonomy tree.\n\n"
            "QUESTION: Should المجاز العقلي (intellectual/rational metaphor) be placed under:\n"
            "- (A) البيان > المجاز (al-Sakkaki's framework — places it with other forms of metaphor), OR\n"
            "- (B) المعاني > أحوال الإسناد (al-Qazwini's framework — places it under sentence-level meaning because it "
            "involves attribution of an action to other than its true agent)\n\n"
            "CONTEXT:\n"
            "- السكاكي (d. 626 AH) in مفتاح العلوم treats المجاز العقلي alongside المجاز اللغوي under البيان\n"
            "- القزويني (d. 739 AH) in التلخيص moves it to المعاني because the metaphor operates at the sentence level "
            "(إسناد الفعل إلى غير فاعله الحقيقي)\n"
            "- Most later textbooks follow القزويني, but الإسناد المجازي is still discussed in بيان sections of some modern curricula\n\n"
            "WHAT I NEED:\n"
            "1. Which framework do the majority of classical and modern balagha textbooks follow for المجاز العقلي?\n"
            "2. In a tree designed for student study (not historical accuracy), which placement produces fewer cross-reference complications?\n"
            "3. If placed under المعاني, does the البيان section need a cross-reference leaf or note?\n"
            "4. Concrete recommendation with scholarly justification."
        ),
    },
    {
        "prompt_id": "RQ-B2-010",
        "target": DRTarget.GEMINI,
        "category": ResearchCategory.CROSS_CUTTING,
        "priority": Priority.HIGH,
        "topic": "Cross-Science: Sarf/Nahw Boundary Rulings",
        "unblocks": "Cross-science routing rules for sarf/nahw overlap",
        "file_bundle": "library/sciences/sarf/tree_history/sarf_v1_0.yaml + reference/research/nahw_v2_0_final.yaml",
        "estimated_minutes": 30,
        "prompt_text": (
            "You are an expert in Arabic grammar (nahw) and morphology (sarf) and the historical boundary between these two sciences. "
            "I am building separate taxonomy trees for nahw and sarf and need formal boundary rulings for overlapping topics.\n\n"
            "QUESTION: What are the formal scholarly rules for drawing the boundary between nahw and sarf content?\n\n"
            "CONTEXT:\n"
            "- Classical scholars disagree on the boundary. Some define sarf as dealing with word-internal structure (بنية الكلمة) "
            "and nahw as dealing with word-final markers (إعراب) and sentence structure.\n"
            "- Several topics exist in BOTH trees currently: e.g., المبني والمعرب (built/declined), التعريف والتنكير, الاشتقاق\n"
            "- My nahw tree has 183 leaves (v2.0, validated). My sarf tree has 226 leaves (v1.0, unvalidated).\n\n"
            "WHAT I NEED:\n"
            "1. What is the classical scholarly definition of the boundary? (Cite Ibn Jinni's الخصائص, Sibawayh's الكتاب, "
            "or other foundational sources)\n"
            "2. For the following overlap topics, which tree should own them and why:\n"
            "   - المبني والمعرب\n"
            "   - التعريف والتنكير\n"
            "   - الاشتقاق\n"
            "   - التثنية والجمع (dual and plural formation — morphological change vs syntactic role)\n"
            "   - النسب (attribution — morphological suffix vs syntactic usage)\n"
            "3. Should overlap topics exist in BOTH trees (with cross-references) or in ONE tree (with the other tree pointing to it)?\n"
            "4. A general rule I can apply to future overlap cases."
        ),
    },
]


def main() -> None:
    """Write all Batch 2 prompts to JSONL."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing file (destroys status updates)")
    args = parser.parse_args()

    PROMPTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    if PROMPTS_FILE.exists() and not args.overwrite:
        print(f"File already exists: {PROMPTS_FILE}")
        print("Use --overwrite to replace (destroys relayed/processed status).")
        return

    if PROMPTS_FILE.exists():
        PROMPTS_FILE.unlink()

    for data in BATCH_2:
        prompt = DRPrompt(batch="batch_2", **data)
        append_jsonl(PROMPTS_FILE, prompt)

    print(f"Wrote {len(BATCH_2)} prompts to {PROMPTS_FILE}")


if __name__ == "__main__":
    main()
