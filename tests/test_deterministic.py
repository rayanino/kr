"""Deterministic tests for A3 (name matching) and A4 (trust weights).

These tests validate SPEC assumptions without any LLM calls.
Run: python3 tests/test_deterministic.py
"""

import json
import sys
from pathlib import Path

# Add parent so we can import the harness
sys.path.insert(0, str(Path(__file__).parent))
from eval_harness import normalize_arabic_name, normalized_name_similarity


# ═══════════════════════════════════════════════════════════════
# A3: Scholar Name Matching
# ═══════════════════════════════════════════════════════════════
# SPEC thresholds: ≥0.85 → auto-link, 0.50-0.85 → human gate, <0.50 → new record

def test_a3_name_matching():
    """Test name normalization and similarity scoring against known pairs."""
    print("=" * 60)
    print("A3: SCHOLAR NAME MATCHING")
    print("=" * 60)
    
    # ── Normalization tests ──
    print("\n--- Normalization ---")
    norm_tests = [
        ("النَّوَوِيّ", "نووي"),         # Strip diacritics + definite article
        ("أبو عبد الرحمن", "ابو عبد رحمن"),  # Hamza norm + al strip
        ("ابن القَطَّاع الصقلي", "ابن قطاع صقلي"),  # al strip + diacritics
        ("ابن تيمية", "ابن تيميه"),      # taa marbuta → haa
    ]
    for raw, expected in norm_tests:
        result = normalize_arabic_name(raw)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{raw}' → '{result}' (expected: '{expected}')")
        if result != expected:
            print(f"    MISMATCH")
    
    # ── Similarity tests: known pairs with expected thresholds ──
    print("\n--- Similarity Scoring ---")
    print(f"  Thresholds: ≥0.85 auto-link | 0.50-0.85 human_gate | <0.50 new_record\n")
    
    test_pairs = [
        # (name_a, name_b, expected_zone, description)
        # Zone: 'auto' (≥0.85), 'gate' (0.50-0.85), 'new' (<0.50)
        
        # Exact matches (should auto-link)
        ("النووي", "النووي", "auto", "Identical names"),
        ("ابن عقيل", "ابن عقيل", "auto", "Identical - Ibn Aqil"),
        ("جلال الدين السيوطي", "جلال الدين السيوطي", "auto", "Identical - Suyuti"),
        
        # Same person, variant forms (should auto-link or high gate)
        ("أبو زكريا يحيى بن شرف النووي", "النووي", "gate", "Full vs short name - Nawawi"),
        ("ابن القطاع الصقلي", "ابن القَطَّاع الصقلي", "auto", "Diacritics only diff"),
        ("عبد الرحمن بن أبي بكر السيوطي", "جلال الدين السيوطي", "gate", "Different parts of same name"),
        
        # Different scholars, similar names (should be gate or new)
        ("ابن حجر العسقلاني", "ابن حجر الهيتمي", "gate", "Different Ibn Hajar scholars"),
        ("أبو القاسم الزجاجي", "أبو إسحاق الزجاج", "gate", "Zajjaji vs Zajjaj (teacher/student)"),
        
        # Clearly different scholars (should be new)
        ("النووي", "ابن تيمية", "new", "Completely different scholars"),
        ("ابن مالك", "مالك بن أنس", "gate_or_new", "Ibn Malik vs Malik ibn Anas"),
        ("السلمي", "السيوطي", "new", "Different scholars with al-prefix"),
        
        # Real fixture test cases
        ("عبد الرحمن بن إسحاق البغدادي النهاوندي الزجاجي، أبو القاسم",
         "أبو القاسم الزجاجي (ت 337هـ)", "gate", "Fixture 01: full vs short author"),
        ("أبو زكريا يحيى بن شرف النووي (631 - 676 هـ)",
         "النووي (631-676 هـ)", "gate", "Fixture 06: Nawawi full vs short"),
        ("عبد الرحمن بن أبي بكر، جلال الدين السيوطي (ت 911هـ)",
         "جلال الدين السيوطي (ت 911هـ)", "auto", "Fixture 11: Suyuti with patronymic"),
    ]
    
    results = {'pass': 0, 'fail': 0, 'warn': 0}
    
    for name_a, name_b, expected_zone, desc in test_pairs:
        sim = normalized_name_similarity(name_a, name_b)
        
        if sim >= 0.85:
            actual_zone = 'auto'
        elif sim >= 0.50:
            actual_zone = 'gate'
        else:
            actual_zone = 'new'
        
        # Check if actual matches expected
        if expected_zone == 'gate_or_new':
            ok = actual_zone in ('gate', 'new')
        else:
            ok = actual_zone == expected_zone
        
        status = "✓" if ok else "✗"
        if not ok:
            results['fail'] += 1
        else:
            results['pass'] += 1
        
        print(f"  {status} sim={sim:.3f} [{actual_zone:4s}] {desc}")
        if not ok:
            print(f"    Expected zone: {expected_zone}, got: {actual_zone}")
    
    print(f"\n  Results: {results['pass']} pass, {results['fail']} fail")
    
    # ── Critical finding analysis ──
    print("\n--- Critical Findings ---")
    
    # Test the specific concern: can we distinguish ابن حجر العسقلاني from ابن حجر الهيتمي?
    s = normalized_name_similarity("ابن حجر العسقلاني", "ابن حجر الهيتمي")
    print(f"  Ibn Hajar disambiguation: sim={s:.3f} → {'human_gate' if 0.50 <= s < 0.85 else 'auto_link' if s >= 0.85 else 'new_record'}")
    print(f"    {'✓ Correctly routed to human gate' if 0.50 <= s < 0.85 else '✗ PROBLEM: would auto-link or miss'}")
    
    # Test: do full-name variants of the SAME scholar auto-link?
    s2 = normalized_name_similarity(
        "أبو زكريا محيي الدين يحيى بن شرف النووي",
        "النووي"
    )
    print(f"  Nawawi full→short: sim={s2:.3f} → {'human_gate' if 0.50 <= s2 < 0.85 else 'auto_link' if s2 >= 0.85 else 'new_record'}")
    if s2 < 0.50:
        print(f"    ✗ PROBLEM: full vs short name falls below gate threshold!")
        print(f"    → SPEC may need: check against all name_variants, not just canonical")
    elif s2 < 0.85:
        print(f"    ⚠ Falls in human_gate zone — acceptable but not ideal for known scholars")
    
    return results['fail'] == 0


# ═══════════════════════════════════════════════════════════════
# A4: Trust Weight Calibration
# ═══════════════════════════════════════════════════════════════
# SPEC weights: author_standing=0.30, tahqiq_quality=0.25, publisher_reputation=0.15,
#               source_authority=0.15, text_fidelity=0.15
# Threshold: ≥0.65 → verified, <0.65 → flagged

def compute_trust_score(
    author_standing: float,
    tahqiq_quality: float,
    publisher_reputation: float,
    source_authority: float,
    text_fidelity: float,
) -> float:
    """Compute trust score per SPEC §4.A.8."""
    return (
        author_standing * 0.30 +
        tahqiq_quality * 0.25 +
        publisher_reputation * 0.15 +
        source_authority * 0.15 +
        text_fidelity * 0.15
    )


def test_a4_trust_weights():
    """Test trust weight calibration against all 13 fixtures."""
    print("\n" + "=" * 60)
    print("A4: TRUST WEIGHT CALIBRATION")
    print("=" * 60)
    
    gt = json.load(open(Path(__file__).parent / 'fixtures' / 'GROUND_TRUTH.json'))
    
    # Factor scoring rules from SPEC §4.A.8:
    # author_standing: classical (≤900AH, known) → 0.90, known scholar → 0.70, unknown → 0.30
    # tahqiq_quality: recognized muhaqiq → 0.90, unknown muhaqiq → 0.50, no muhaqiq pre-modern → 0.40, no muhaqiq modern → 0.30
    # publisher_reputation: known publisher → 0.55-0.80, unknown → 0.40
    # source_authority: primary → 0.85, reference → 0.60, modern_compilation → 0.40
    # text_fidelity: shamela_html → high → 0.90, plain_text → high → 0.90
    
    # For Stage 1 (no recognized muhaqiq list, no known publishers list),
    # we use the SPEC's default scores for unknown/absent.
    
    print(f"\n  Threshold: ≥0.65 → verified, <0.65 → flagged")
    print(f"  Weights: author=0.30, tahqiq=0.25, publisher=0.15, authority=0.15, fidelity=0.15\n")
    
    # Define factor scores for each fixture based on SPEC rules
    fixture_factors = {
        '01_nahw_simple': {
            'author_standing': 0.90,   # Classical scholar (d. 337 AH), known grammarian
            'tahqiq_quality': 0.40,    # No muhaqiq, pre-modern work (≤1300 AH)
            'publisher_reputation': 0.40,  # Unknown publisher  
            'source_authority': 0.85,  # primary
            'text_fidelity': 0.90,     # shamela_html → high
        },
        '02_nahw_muhaqiq': {
            'author_standing': 0.90,   # Classical scholar (d. 515 AH)
            'tahqiq_quality': 0.50,    # Has muhaqiq (أحمد محمد عبد الدايم) but not in recognized list
            'publisher_reputation': 0.40,  # دار الكتب والوثائق القومية — let's assume not in list yet
            'source_authority': 0.85,  # primary
            'text_fidelity': 0.90,     # shamela_html → high
        },
        '03_fiqh': {
            'author_standing': 0.30,   # Unknown contemporary author (no death date, just created)
            'tahqiq_quality': 0.30,    # No muhaqiq, modern work
            'publisher_reputation': 0.40,  # الجامعة الإسلامية — could be known, assume unknown for now
            'source_authority': 0.40,  # modern_compilation
            'text_fidelity': 0.90,     # shamela_html → high
        },
        '04_hadith': {
            'author_standing': 0.90,   # Classical scholar (d. 282 AH)
            'tahqiq_quality': 0.50,    # Has muhaqiq but not recognized
            'publisher_reputation': 0.40,  # مكتبة الرشد — assume unknown
            'source_authority': 0.85,  # primary
            'text_fidelity': 0.90,     # shamela_html → high
        },
        '05_tafsir': {
            'author_standing': 0.30,   # Unknown contemporary author
            'tahqiq_quality': 0.30,    # No muhaqiq, modern work
            'publisher_reputation': 0.40,  # دار الصميعي — unknown
            'source_authority': 0.40,  # modern_compilation
            'text_fidelity': 0.90,     # shamela_html → high
        },
        '06_usul': {
            'author_standing': 0.90,   # النووي — one of most recognized scholars (d. 676 AH)
            'tahqiq_quality': 0.50,    # Has muhaqiq (بسام الجابي) but assume not in recognized list
            'publisher_reputation': 0.40,  # دار الفكر — no known_publishers.json in Stage 1
            'source_authority': 0.85,  # primary
            'text_fidelity': 0.90,     # shamela_html → high
        },
        '07_balagha': {
            'author_standing': 0.30,   # Modern scholar, just created record
            'tahqiq_quality': 0.30,    # No muhaqiq, modern work (author IS the writer)
            'publisher_reputation': 0.40,  # وكالة المطبوعات — unknown
            'source_authority': 0.40,  # modern_compilation
            'text_fidelity': 0.90,     # shamela_html → high
        },
        '08_death_date': {
            'author_standing': 0.90,   # Classical scholar (d. 412 AH)
            'tahqiq_quality': 0.50,    # Has muhaqiq but not recognized
            'publisher_reputation': 0.40,  # دار الصحابة — unknown
            'source_authority': 0.85,  # primary
            'text_fidelity': 0.90,     # shamela_html → high
        },
        '09_alt_title': {
            'author_standing': 0.30,   # Unknown contemporary author
            'tahqiq_quality': 0.30,    # No muhaqiq, modern work
            'publisher_reputation': 0.40,  # وزارة الشئون الإسلامية — could be known
            'source_authority': 0.40,  # modern_compilation
            'text_fidelity': 0.90,     # shamela_html → high
        },
        '10_no_author': {
            'author_standing': 0.30,   # Unknown contemporary author
            'tahqiq_quality': 0.30,    # No muhaqiq, modern work (إعداد not تحقيق)
            'publisher_reputation': 0.40,  # دار ابن خزيمة — unknown
            'source_authority': 0.40,  # modern_compilation
            'text_fidelity': 0.90,     # shamela_html → high
        },
        '11_multi_small': {
            'author_standing': 0.90,   # السيوطي — classical, very well known (d. 911 AH)
            'tahqiq_quality': 0.50,    # Has muhaqiq (عبد الحميد هنداوي) — not in recognized list
            'publisher_reputation': 0.40,  # المكتبة التوفيقية — unknown
            'source_authority': 0.85,  # primary
            'text_fidelity': 0.90,     # shamela_html → high
        },
        '12_multi_muq': {
            'author_standing': 0.30,   # Modern intellectual (d. 1393 AH), not in Islamic scholarly tradition
            'tahqiq_quality': 0.30,    # No muhaqiq (it's a translation, not tahqiq), modern
            'publisher_reputation': 0.40,  # دار الأمة — unknown
            'source_authority': 0.85,  # primary (author's own work)
            'text_fidelity': 0.90,     # shamela_html → high
        },
        'alfiyyah_versified': {
            'author_standing': 0.90,   # ابن مالك — classical (d. 672 AH), extremely well known
            'tahqiq_quality': 0.40,    # No muhaqiq, pre-modern work (≤1300 AH)
            'publisher_reputation': 0.40,  # No publisher (plain text)
            'source_authority': 0.85,  # primary
            'text_fidelity': 0.60,     # plain_text → medium (0.60)
        },
    }
    
    results = {'pass': 0, 'fail': 0}
    
    for fixture_id, factors in fixture_factors.items():
        expected_trust = gt[fixture_id]['expected_trust']
        score = compute_trust_score(**factors)
        predicted_tier = 'verified' if score >= 0.65 else 'flagged'
        
        ok = predicted_tier == expected_trust
        status = "✓" if ok else "✗"
        if ok:
            results['pass'] += 1
        else:
            results['fail'] += 1
        
        print(f"  {status} {fixture_id:25s} score={score:.3f} → {predicted_tier:8s} (expected: {expected_trust})")
        if not ok:
            detail = ", ".join(f"{k}={v:.2f}" for k, v in factors.items())
            print(f"    Factors: {detail}")
    
    print(f"\n  Results: {results['pass']} pass, {results['fail']} fail")
    
    # ── Sensitivity analysis ──
    print("\n--- Sensitivity Analysis ---")
    
    # What if we adjust the threshold?
    for threshold in [0.55, 0.60, 0.65, 0.70, 0.75]:
        matches = 0
        for fixture_id, factors in fixture_factors.items():
            expected = gt[fixture_id]['expected_trust']
            score = compute_trust_score(**factors)
            predicted = 'verified' if score >= threshold else 'flagged'
            if predicted == expected:
                matches += 1
        print(f"  threshold={threshold:.2f}: {matches}/{len(fixture_factors)} correct ({matches/len(fixture_factors)*100:.0f}%)")
    
    return results['fail'] == 0


# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print()
    a3_ok = test_a3_name_matching()
    a4_ok = test_a4_trust_weights()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  A3 (name matching):  {'PASS' if a3_ok else 'FAIL — review findings above'}")
    print(f"  A4 (trust weights):  {'PASS' if a4_ok else 'FAIL — review findings above'}")
    print()
    
    sys.exit(0 if (a3_ok and a4_ok) else 1)
