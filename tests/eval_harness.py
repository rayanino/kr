"""Evaluation harness for source engine LLM inference testing.

Scores LLM outputs against GROUND_TRUTH.json using criteria from SCORING_CRITERIA.md.
Run directly to verify scoring logic against known test cases.
"""

import difflib
import io
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ── Name normalization (from SPEC §4.A.1) ──

def normalize_arabic_name(name: str) -> str:
    """Normalize Arabic name for comparison."""
    result = name
    # Strip parenthetical annotations — ground truth includes death dates
    # like "(ت 337هـ)" or "(631-676 هـ)" that are metadata, not name parts.
    result = re.sub(r'\([^)]*\)', '', result)
    # Strip common diacritics (tashkeel)
    diacritics = '\u0610\u0611\u0612\u0613\u0614\u0615\u0616\u0617\u0618\u0619\u061A\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0656\u0657\u0658\u0659\u065A\u065B\u065C\u065D\u065E\u065F\u0670'
    for d in diacritics:
        result = result.replace(d, '')
    # Normalize hamza forms
    result = result.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    # Normalize taa marbuta
    result = result.replace('ة', 'ه')
    # Strip definite article
    result = re.sub(r'\bال[ـ]?', '', result)
    # Collapse whitespace
    result = re.sub(r'\s+', ' ', result).strip()
    return result


def _extract_name_tokens(name: str) -> set:
    """Extract significant tokens from a normalized Arabic scholarly name.

    Removes patronymic particles (بن, ابن) which are structural connectors,
    not identifying components. Keeps kunya, laqab, ism, nasab names, and nisba.
    """
    normalized = normalize_arabic_name(name)
    particles = {'بن', 'ابن'}
    return {t for t in normalized.split() if t not in particles}


def normalized_name_similarity(a: str, b: str) -> float:
    """Compare two Arabic scholarly names by semantic component overlap.

    Handles the common case where the same scholar is referred to by
    different subsets of name components (e.g., nisba-only vs full nasab chain).
    Uses token overlap relative to the shorter name to reward elaboration matches.
    Falls back to substring containment for compound-word mismatches.
    """
    norm_a = normalize_arabic_name(a)
    norm_b = normalize_arabic_name(b)

    if norm_a == norm_b:
        return 1.0
    if not norm_a or not norm_b:
        return 0.0

    tokens_a = _extract_name_tokens(a)
    tokens_b = _extract_name_tokens(b)

    if not tokens_a or not tokens_b:
        return 0.0

    shared = tokens_a & tokens_b

    if not shared:
        # Substring fallback for compound-word mismatches (عبدالله vs عبد له)
        for ta in tokens_a:
            for tb in tokens_b:
                if len(ta) >= 3 and len(tb) >= 3 and (ta in tb or tb in ta):
                    return 0.4
        return 0.0

    min_size = min(len(tokens_a), len(tokens_b))
    overlap = len(shared) / min_size

    # If all of shorter name's tokens found in longer → strict elaboration
    shorter = tokens_a if len(tokens_a) <= len(tokens_b) else tokens_b
    longer = tokens_b if len(tokens_a) <= len(tokens_b) else tokens_a
    if shorter.issubset(longer) and min_size >= 2:
        return max(0.85, overlap)

    return overlap


# ── Genre scoring ──

GENRE_SYNONYMS = {
    frozenset({'sharh', 'hashiyah'}),
    frozenset({'matn', 'nazm'}),
    frozenset({'risalah', 'other'}),
    frozenset({'hadith_collection', 'fiqh_comparative'}),
}

def score_genre(predicted: str, expected: str) -> float:
    if predicted == expected:
        return 1.0
    for syn_set in GENRE_SYNONYMS:
        if predicted in syn_set and expected in syn_set:
            return 0.5
    return 0.0


# ── Science scope scoring ──

def score_science_scope(predicted: List[str], expected: List[str]) -> float:
    pred_set = set(predicted)
    exp_set = set(expected)
    
    if pred_set == exp_set:
        return 1.0
    if not exp_set and not pred_set:
        return 1.0
    if not exp_set and pred_set:
        return 0.0  # Hallucinated scope where none expected
    if exp_set and not pred_set:
        return 0.0  # Missing all scopes
    
    if exp_set.issubset(pred_set):
        return 0.75  # Superset (extra tags)
    if pred_set.issubset(exp_set):
        return 0.5   # Subset (missing some)
    if pred_set & exp_set:
        return 0.25  # Partial overlap
    return 0.0       # Disjoint


# ── Structural format scoring ──

FORMAT_SYNONYMS = {
    frozenset({'prose', 'mixed'}),
    frozenset({'commentary', 'prose'}),
}

def score_structural_format(predicted: str, expected: str) -> float:
    if predicted == expected:
        return 1.0
    for syn_set in FORMAT_SYNONYMS:
        if predicted in syn_set and expected in syn_set:
            return 0.5
    return 0.0


# ── Level scoring ──

LEVEL_ORDER = ['beginner', 'intermediate', 'advanced', 'specialist']

def score_level(predicted: Optional[str], expected: Optional[str]) -> float:
    if expected is None:
        return 1.0 if predicted is None else 0.0
    if predicted is None:
        return 0.0
    if predicted == expected:
        return 1.0
    if predicted in LEVEL_ORDER and expected in LEVEL_ORDER:
        dist = abs(LEVEL_ORDER.index(predicted) - LEVEL_ORDER.index(expected))
        if dist == 1:
            return 0.5
    return 0.0


# ── Authority level scoring ──

def score_authority_level(predicted: str, expected: str) -> float:
    return 1.0 if predicted == expected else 0.0


# ── Multi-layer scoring ──

def score_multi_layer(predicted: bool, expected: bool) -> float:
    return 1.0 if predicted == expected else 0.0


# ── Author identification scoring ──

def score_author_identification(
    predicted_name: str,
    predicted_death: Optional[int],
    expected_name: str,
    expected_death: Optional[int],
) -> Dict[str, float]:
    """Score author identification. Returns sub-scores and weighted total."""
    # Name match (weight 0.50)
    name_score = normalized_name_similarity(predicted_name, expected_name)
    
    # Death date (weight 0.30)
    if expected_death is None and predicted_death is None:
        date_score = 1.0
    elif expected_death is None or predicted_death is None:
        date_score = 0.3
    else:
        diff = abs(predicted_death - expected_death)
        if diff == 0:
            date_score = 1.0
        elif diff <= 10:
            date_score = 0.7
        elif diff <= 50:
            date_score = 0.3
        else:
            date_score = 0.0
    
    # Correct person (weight 0.20) - domain-aware heuristic
    # Death date exact match + any name component overlap → certainly same person
    if date_score == 1.0 and name_score > 0.0:
        person_score = 1.0
    elif name_score >= 0.85:
        person_score = 1.0
    elif name_score >= 0.50 and date_score >= 0.3:
        person_score = 0.5
    else:
        person_score = 0.0
    
    total = name_score * 0.50 + date_score * 0.30 + person_score * 0.20
    
    return {
        'name_score': round(name_score, 3),
        'date_score': round(date_score, 3),
        'person_score': round(person_score, 3),
        'total': round(total, 3),
    }


# ── Aggregate fixture scoring ──

FIELD_WEIGHTS = {
    'genre': 0.15,
    'science_scope': 0.15,
    'is_multi_layer': 0.15,
    'structural_format': 0.10,
    'level': 0.05,
    'authority_level': 0.10,
    'author_identification': 0.30,
}

def score_fixture(predicted: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
    """Score a single fixture's LLM output against ground truth."""
    scores = {}
    
    scores['genre'] = score_genre(
        predicted.get('genre', ''), expected['genre'])
    
    scores['science_scope'] = score_science_scope(
        predicted.get('science_scope', []), expected['science_scope'])
    
    scores['is_multi_layer'] = score_multi_layer(
        predicted.get('is_multi_layer', False), expected['is_multi_layer'])
    
    scores['structural_format'] = score_structural_format(
        predicted.get('structural_format', ''), expected['structural_format'])
    
    scores['level'] = score_level(
        predicted.get('level'), expected.get('level'))
    
    scores['authority_level'] = score_authority_level(
        predicted.get('authority_level', ''), expected['authority_level'])
    
    author_scores = score_author_identification(
        predicted.get('author_name', ''),
        predicted.get('author_death_hijri'),
        expected['author_identified'],
        expected.get('author_death_hijri'),
    )
    scores['author_identification'] = author_scores['total']
    scores['author_detail'] = author_scores
    
    # Weighted aggregate
    total = sum(
        scores[f] * FIELD_WEIGHTS[f] 
        for f in FIELD_WEIGHTS 
        if f in scores
    )
    scores['aggregate'] = round(total, 3)
    
    return scores


def score_model_run(
    predictions: Dict[str, Dict[str, Any]], 
    ground_truth: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Score all fixtures for a single model run."""
    fixture_scores = {}
    json_parse_failures = []
    enum_violations = []
    
    for fixture_id, expected in ground_truth.items():
        if fixture_id not in predictions:
            fixture_scores[fixture_id] = {'error': 'missing', 'aggregate': 0.0}
            continue
        
        pred = predictions[fixture_id]
        
        if pred.get('_parse_error'):
            json_parse_failures.append(fixture_id)
            fixture_scores[fixture_id] = {'error': 'json_parse', 'aggregate': 0.0}
            continue
        
        if pred.get('_enum_violations'):
            enum_violations.extend(pred['_enum_violations'])
        
        fixture_scores[fixture_id] = score_fixture(pred, expected)
    
    n = len(ground_truth)
    model_aggregate = sum(
        fs.get('aggregate', 0.0) for fs in fixture_scores.values()
    ) / n if n > 0 else 0.0
    
    return {
        'fixture_scores': fixture_scores,
        'model_aggregate': round(model_aggregate, 3),
        'json_parse_rate': round(1.0 - len(json_parse_failures) / n, 3) if n > 0 else 0.0,
        'json_parse_failures': json_parse_failures,
        'enum_violation_count': len(enum_violations),
        'multi_layer_accuracy': _compute_multi_layer_accuracy(fixture_scores, ground_truth),
    }


def _compute_multi_layer_accuracy(
    fixture_scores: Dict[str, Dict], 
    ground_truth: Dict[str, Dict],
) -> float:
    """Compute boolean accuracy for is_multi_layer across all fixtures."""
    correct = sum(
        1 for fid, fs in fixture_scores.items()
        if fs.get('is_multi_layer') == 1.0
    )
    total = sum(1 for fs in fixture_scores.values() if 'is_multi_layer' in fs)
    return round(correct / total, 3) if total > 0 else 0.0


# ── Self-test ──

def run_self_test():
    """Verify scoring logic with known inputs."""
    print("=== Scoring Harness Self-Test ===\n")
    errors = 0
    
    # Genre scoring
    assert score_genre('risalah', 'risalah') == 1.0
    assert score_genre('sharh', 'hashiyah') == 0.5
    assert score_genre('matn', 'sharh') == 0.0
    assert score_genre('risalah', 'other') == 0.5
    print("✓ Genre scoring")
    
    # Science scope scoring
    assert score_science_scope(['fiqh'], ['fiqh']) == 1.0
    assert score_science_scope(['fiqh', 'hadith'], ['fiqh']) == 0.75
    assert score_science_scope(['fiqh'], ['fiqh', 'hadith']) == 0.5
    assert score_science_scope(['nahw'], ['fiqh']) == 0.0
    assert score_science_scope([], []) == 1.0
    assert score_science_scope(['fiqh'], []) == 0.0
    assert score_science_scope(['fiqh', 'nahw'], ['fiqh', 'hadith']) == 0.25
    print("✓ Science scope scoring")
    
    # Multi-layer scoring  
    assert score_multi_layer(True, True) == 1.0
    assert score_multi_layer(False, True) == 0.0
    print("✓ Multi-layer scoring")
    
    # Level scoring
    assert score_level('intermediate', 'intermediate') == 1.0
    assert score_level('beginner', 'intermediate') == 0.5
    assert score_level('beginner', 'advanced') == 0.0
    assert score_level(None, None) == 1.0
    assert score_level('intermediate', None) == 0.0
    print("✓ Level scoring")
    
    # Name similarity
    s1 = normalized_name_similarity('ابن عقيل', 'ابن عقيل')
    assert s1 == 1.0, f"Exact match expected 1.0, got {s1}"
    
    s2 = normalized_name_similarity('ابن حجر العسقلاني', 'ابن حجر الهيتمي')
    assert 0.3 <= s2 <= 0.7, f"Partial overlap (shared حجر, different nisba) expected 0.3-0.7, got {s2}"
    
    s3 = normalized_name_similarity('النووي', 'ابن تيمية')
    assert s3 < 0.4, f"Different scholars expected <0.4, got {s3}"
    print(f"✓ Name similarity (exact={s1:.2f}, similar={s2:.2f}, different={s3:.2f})")
    
    # Author identification
    auth = score_author_identification(
        'جلال الدين السيوطي', 911,
        'جلال الدين السيوطي (ت 911هـ)', 911,
    )
    assert auth['total'] > 0.8, f"Expected >0.8 for correct ID, got {auth['total']}"
    print(f"✓ Author identification (Suyuti match: {auth['total']:.3f})")
    
    # Fixture aggregate
    perfect = score_fixture(
        {
            'genre': 'risalah',
            'science_scope': ['fiqh'],
            'is_multi_layer': False,
            'structural_format': 'prose',
            'level': 'intermediate',
            'authority_level': 'modern_compilation',
            'author_name': 'عبد الله بن إبراهيم الزاحم',
            'author_death_hijri': None,
        },
        {
            'genre': 'risalah',
            'science_scope': ['fiqh'],
            'is_multi_layer': False,
            'structural_format': 'prose',
            'level': 'intermediate',
            'authority_level': 'modern_compilation',
            'author_identified': 'عبد الله بن إبراهيم الزاحم',
            'author_death_hijri': None,
        },
    )
    assert perfect['aggregate'] > 0.95, f"Perfect match expected >0.95, got {perfect['aggregate']}"
    print(f"✓ Fixture aggregate (perfect: {perfect['aggregate']:.3f})")
    
    print("\n=== All self-tests passed ===")


if __name__ == '__main__':
    run_self_test()
