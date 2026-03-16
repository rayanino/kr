#!/usr/bin/env python3
"""Session C verdict-ready data extractor.

For each book, outputs ALL fields needed for the 14-field verdict format,
plus structural analysis (genre disagreement, ML disagreement, layer data,
BUG-03 override detection). Designed to be copy-pasted into verdicts
with zero memory-based transcription.

Usage: python3 session_c_extract.py "book_name"
       python3 session_c_extract.py --all  (all 15 Session C books)
"""

import json, sys, os, glob

PHASE_D_DIR = "tests/results/source_engine/phase_d"

SESSION_C_BOOKS = [
    "أمالي الأذكار في فضل صلاة التسبيح",
    "إعلام الموقعين عن رب العالمين - ط العلمية",
    "الأحاديث الأربعين النووية مع ما زاد عليها ابن رجب وعليها الشرح الموجز المفيد",
    "الأدب المفرد - بأحكام الألباني - ت الزهيري",
    "الإبانة عن أصول الديانة - ت العصيمي",
    "الإبانة عن أصول الديانة - ت فوقية",
    "الرسالة للشافعي",
    "الروضة الندية شرح الدرر البهية ط المعرفة",
    "القسم الثالث من المعجم الأوسط للطبراني",
    "المسائل النحوية في كتاب التوضيح لشرح الجامع الصحيح",
    "النكت على شرح النووي على صحيح مسلم",
    "تفسير ابن كمال باشا",
    "شرح المفصل لابن يعيش",
    "مختصر صحيح مسلم للمنذري ت الألباني",
    "مسند أحمد - ت شاكر - ط دار الحديث",
]


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None


def extract_book(book_name):
    book_dir = os.path.join(PHASE_D_DIR, book_name)
    if not os.path.isdir(book_dir):
        print(f"ERROR: Directory not found: {book_dir}")
        return

    result = load_json(os.path.join(book_dir, "result.json"))
    extraction = load_json(os.path.join(book_dir, "extraction.json"))
    consensus = load_json(os.path.join(book_dir, "consensus.json"))
    prompt_sent = load_json(os.path.join(book_dir, "prompt_sent.json"))

    # Load LLM responses
    opus_data = None
    ca_data = None
    llm_dir = os.path.join(book_dir, "llm_responses")
    if os.path.isdir(llm_dir):
        for f in os.listdir(llm_dir):
            path = os.path.join(llm_dir, f)
            data = load_json(path)
            if data:
                parsed = data.get("parsed", {})
                if "claude_opus" in f:
                    opus_data = parsed
                else:
                    ca_data = parsed

    if not result or not opus_data or not ca_data:
        print(f"ERROR: Missing data files for {book_name}")
        return

    # Extract all verdict-relevant fields
    print("=" * 70)
    print(f"BOOK: {book_name}")
    print("=" * 70)

    # --- VERDICT-READY FIELDS ---
    print("\n### COPY-PASTE BLOCK ###")
    print(f"- **Status:** {result.get('status', 'N/A')}")
    print(f"- **Pipeline author:** {result.get('author', {}).get('name_arabic', 'N/A')}")

    # Death date from BOTH models
    opus_death = opus_data.get("author_identification", {}).get("death_date_hijri") if isinstance(opus_data.get("author_identification"), dict) else opus_data.get("death_date_hijri")
    ca_death = ca_data.get("author_identification", {}).get("death_date_hijri") if isinstance(ca_data.get("author_identification"), dict) else ca_data.get("death_date_hijri")
    if opus_death == ca_death:
        death_str = f"d. {opus_death} AH" if opus_death else "no death date"
    else:
        death_str = f"Opus: {opus_death}, CA: {ca_death} — DISAGREEMENT"
    print(f"  Death date: {death_str}")

    # Confidence from LLM responses (NOT result.json)
    opus_conf = opus_data.get("author_identification_confidence", "N/A")
    ca_conf = ca_data.get("author_identification_confidence", "N/A")
    print(f"  Author conf: Opus={opus_conf}, CA={ca_conf}")

    # Genre
    opus_genre = opus_data.get("genre", "N/A")
    opus_genre_conf = opus_data.get("genre_confidence", "N/A")
    ca_genre = ca_data.get("genre", "N/A")
    ca_genre_conf = ca_data.get("genre_confidence", "N/A")
    result_genre = result.get("genre", "N/A")
    genre_match = "AGREE" if opus_genre == ca_genre else "DISAGREE"
    print(f"- **Pipeline genre:** {result_genre}")
    print(f"  Opus: {opus_genre} ({opus_genre_conf}), CA: {ca_genre} ({ca_genre_conf}) → {genre_match}")

    # Multi-layer
    opus_ml = opus_data.get("is_multi_layer", "N/A")
    opus_ml_conf = opus_data.get("is_multi_layer_confidence", "N/A")
    ca_ml = ca_data.get("is_multi_layer", "N/A")
    result_ml = result.get("is_multi_layer", "N/A")
    ml_match = "AGREE" if opus_ml == ca_ml else "DISAGREE"
    print(f"- **Pipeline ML:** {result_ml}")
    print(f"  Opus: {opus_ml} (conf {opus_ml_conf}), CA: {ca_ml} → {ml_match}")

    # Layers (critical for Session C)
    opus_layers = opus_data.get("text_layers", [])
    ca_layers = ca_data.get("text_layers", [])
    result_layers = result.get("text_layers", [])
    print(f"  Pipeline layers: {json.dumps(result_layers, ensure_ascii=False)}")
    if opus_layers:
        print(f"  Opus layers ({len(opus_layers)}):")
        for layer in opus_layers:
            if isinstance(layer, dict):
                print(f"    - {layer.get('layer_type','?')}: {layer.get('author_name','?')}")
            else:
                print(f"    - {layer}")
    if ca_layers:
        print(f"  CA layers ({len(ca_layers)}):")
        for layer in ca_layers:
            if isinstance(layer, dict):
                print(f"    - {layer.get('layer_type','?')}: {layer.get('author_name','?')}")
            else:
                print(f"    - {layer}")

    # Science scope
    result_sci = result.get("science_scope", [])
    opus_sci = opus_data.get("science_scope", [])
    ca_sci = ca_data.get("science_scope", [])
    print(f"- **Pipeline science:** {result_sci}")
    print(f"  Opus: {opus_sci}, CA: {ca_sci}")

    # Trust
    trust_tier = result.get("trust_tier", "N/A")
    trust_score = result.get("trust_score", "N/A")
    print(f"- **Trust tier:** {trust_tier} ({trust_score})")

    # Attribution
    opus_attr = opus_data.get("attribution_status", "N/A")
    ca_attr = ca_data.get("attribution_status", "N/A")
    result_attr = result.get("attribution_status", "N/A")
    print(f"- **Attribution:** {result_attr} (Opus: {opus_attr}, CA: {ca_attr})")

    # --- EXTRACTION DATA ---
    print("\n### EXTRACTION ###")
    if extraction:
        print(f"  author_raw: {extraction.get('author_name_raw', 'EMPTY')}")
        print(f"  muhaqiq: {extraction.get('muhaqiq_name_raw', 'null')}")
        author_death = extraction.get("author_death_hijri", "N/A")
        print(f"  author_death_hijri: {author_death}")
        print(f"  shamela_cat: {extraction.get('shamela_category', 'N/A')}")

    # --- PROMPT SENT ---
    print("\n### PROMPT SENT ###")
    if prompt_sent:
        present = prompt_sent.get("metadata_fields_present", [])
        absent = prompt_sent.get("metadata_fields_absent", [])
        print(f"  fields_present: {present}")
        print(f"  fields_absent: {absent}")

    # --- CONSENSUS ---
    print("\n### CONSENSUS ###")
    if consensus:
        print(f"  agreed: {consensus.get('agreed', 'N/A')}")
        print(f"  human_gate: {consensus.get('needs_human_gate', 'N/A')}")

    # --- STRUCTURAL FLAG ANALYSIS ---
    print("\n### STRUCTURAL FLAGS ###")
    flags = []

    # Genre disagreement
    if opus_genre != ca_genre:
        flags.append(f"GENRE DISAGREE: Opus={opus_genre}, CA={ca_genre}, Pipeline={result_genre}")
        # Check which model won
        if result_genre == opus_genre:
            flags.append("  → Opus genre won")
        elif result_genre == ca_genre:
            flags.append("  → CA genre won")
        else:
            flags.append("  → NEITHER model's genre matches pipeline! ANOMALY")

    # ML disagreement
    if opus_ml != ca_ml:
        flags.append(f"ML DISAGREE: Opus={opus_ml}, CA={ca_ml}, Pipeline={result_ml}")

    # Genre-ML consistency
    ml_genres = {"sharh", "hashiyah", "tafsir"}
    if result_genre in ml_genres and not result_ml:
        flags.append(f"GENRE-ML INCONSISTENCY: genre={result_genre} implies ML=True but Pipeline has ML=False")
    if result_genre == "hashiyah" and result_ml:
        layer_count = len(result_layers) if result_layers else 0
        if layer_count < 3:
            flags.append(f"HASHIYAH LAYER COUNT: genre=hashiyah requires 3 layers but only {layer_count} found")

    # Tahqiq-note check (BUG-03 pattern)
    tahqiq_layers = [l for l in (opus_layers or []) if isinstance(l, dict) and l.get("layer_type") == "tahqiq_note"]
    if tahqiq_layers and opus_ml and not ca_ml:
        flags.append(f"BUG-03 PATTERN: Opus has tahqiq_note layer + ML=True, CA=False → override should fire")
        if not result_ml:
            flags.append("  → Override FIRED correctly (Pipeline ML=False)")
        else:
            flags.append("  → Override DID NOT fire! Pipeline ML=True")

    if not flags:
        print("  No structural flags detected")
    else:
        for f in flags:
            print(f"  ⚠ {f}")

    # Death date source analysis
    print("\n### DEATH DATE SOURCE ###")
    if extraction:
        has_structured = extraction.get("author_death_hijri") not in (None, "N/A", "")
        raw = extraction.get("author_name_raw", "")
        has_in_raw = any(c.isdigit() for c in (raw or "")) and ("ت " in (raw or "") or "(" in (raw or ""))
        if has_structured:
            print("  Source: PASS-THROUGH (structured field in extraction)")
        elif has_in_raw:
            print(f"  Source: EXTRACTED FROM RAW TEXT (author_raw contains: {raw})")
        elif opus_death or ca_death:
            print("  Source: INFERRED (no extraction data, LLM supplied from domain knowledge)")
        else:
            print("  Source: NONE (no death date anywhere)")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 session_c_extract.py 'book_name' | --all")
        sys.exit(1)

    if sys.argv[1] == "--all":
        for book in SESSION_C_BOOKS:
            extract_book(book)
    else:
        extract_book(sys.argv[1])
