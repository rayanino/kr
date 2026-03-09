"""Phase 3: Consensus pair selection analysis.

Loads Phase 2 results from all model runs and computes pairwise
"at least one right" rates to select the best consensus pair.

Usage:
  python tests/consensus_analysis.py
"""

from __future__ import annotations

import io
import json
import sys
from itertools import combinations
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

RESULTS_DIR = Path(__file__).parent / 'results'
FIXTURES_DIR = Path(__file__).parent / 'fixtures'

# Fields we score for consensus (matching eval_harness FIELD_WEIGHTS)
SCORED_FIELDS = ['genre', 'science_scope', 'is_multi_layer', 'structural_format',
                 'level', 'authority_level', 'author_identification']

# Threshold: a field score >= this counts as "right"
RIGHT_THRESHOLD = 0.5


def load_all_results() -> dict[str, dict]:
    """Load and merge all phase2 result files."""
    merged: dict[str, dict] = {}
    for f in sorted(RESULTS_DIR.glob('phase2_*.json')):
        with open(f, encoding='utf-8') as fh:
            data = json.load(fh)
        for model_name, model_data in data.items():
            merged[model_name] = model_data
    # Also load phase1 Sonnet results for comparison
    for f in sorted(RESULTS_DIR.glob('phase1_*.json')):
        with open(f, encoding='utf-8') as fh:
            data = json.load(fh)
        for model_name, model_data in data.items():
            if model_name not in merged:
                merged[model_name] = model_data
    return merged


def get_field_scores(model_data: dict) -> dict[str, dict[str, float]]:
    """Extract per-fixture per-field scores for a model.
    Returns {fixture_id: {field: score}}."""
    result = {}
    for fid, fs in model_data['scores']['fixture_scores'].items():
        if fs.get('error'):
            result[fid] = {f: 0.0 for f in SCORED_FIELDS}
        else:
            result[fid] = {f: fs.get(f, 0.0) for f in SCORED_FIELDS}
    return result


def compute_pair_metrics(
    scores_a: dict[str, dict[str, float]],
    scores_b: dict[str, dict[str, float]],
) -> dict[str, float]:
    """Compute consensus metrics for a pair of models."""
    total_cells = 0
    at_least_one_right = 0
    both_right = 0
    disagree = 0

    fixture_ids = set(scores_a.keys()) & set(scores_b.keys())

    for fid in fixture_ids:
        for field in SCORED_FIELDS:
            a_score = scores_a[fid].get(field, 0.0)
            b_score = scores_b[fid].get(field, 0.0)
            a_right = a_score >= RIGHT_THRESHOLD
            b_right = b_score >= RIGHT_THRESHOLD

            total_cells += 1
            if a_right or b_right:
                at_least_one_right += 1
            if a_right and b_right:
                both_right += 1
            if a_right != b_right:
                disagree += 1

    at_least_one_rate = at_least_one_right / total_cells if total_cells else 0
    complementarity = disagree / total_cells if total_cells else 0
    both_right_rate = both_right / total_cells if total_cells else 0

    # Find worst fixture (lowest "at least one right" rate per fixture)
    worst_fixture = None
    worst_fixture_rate = 1.0
    for fid in fixture_ids:
        fid_right = 0
        fid_total = 0
        for field in SCORED_FIELDS:
            a_right = scores_a[fid].get(field, 0.0) >= RIGHT_THRESHOLD
            b_right = scores_b[fid].get(field, 0.0) >= RIGHT_THRESHOLD
            fid_total += 1
            if a_right or b_right:
                fid_right += 1
        rate = fid_right / fid_total if fid_total else 0
        if rate < worst_fixture_rate:
            worst_fixture_rate = rate
            worst_fixture = fid

    return {
        'at_least_one_rate': round(at_least_one_rate, 4),
        'complementarity': round(complementarity, 4),
        'both_right_rate': round(both_right_rate, 4),
        'worst_fixture': worst_fixture,
        'worst_fixture_rate': round(worst_fixture_rate, 4),
        'total_cells': total_cells,
    }


# Model provider mapping for cross-provider filtering
MODEL_PROVIDERS = {
    'opus-4.6': 'anthropic',
    'sonnet-4.6': 'anthropic',
    'gpt-5.4': 'openai',
    'gemini-3.1-pro': 'google',
    'mistral-large': 'mistral',
    'command-a': 'cohere',
}


def main():
    all_results = load_all_results()
    print(f"Loaded {len(all_results)} models: {list(all_results.keys())}\n")

    # Phase 2 models only (exclude Sonnet from consensus — it's weaker tier)
    phase2_models = [m for m in all_results if m != 'sonnet-4.6']

    # Extract per-field scores for each model
    model_scores = {m: get_field_scores(all_results[m]) for m in phase2_models}

    # Compute all cross-provider pairs
    pairs = []
    for a, b in combinations(phase2_models, 2):
        provider_a = MODEL_PROVIDERS.get(a, a)
        provider_b = MODEL_PROVIDERS.get(b, b)
        if provider_a == provider_b:
            continue  # Skip same-provider pairs
        metrics = compute_pair_metrics(model_scores[a], model_scores[b])
        pairs.append((a, b, metrics))

    # Sort by at_least_one_rate (primary), complementarity (secondary)
    pairs.sort(key=lambda x: (x[2]['at_least_one_rate'], x[2]['complementarity']), reverse=True)

    # Print comparison table
    print("=" * 100)
    print("CONSENSUS PAIR ANALYSIS — Cross-Provider Pairs")
    print("=" * 100)
    print(f"{'Pair':40s} {'≥1 Right':>10s} {'Complem.':>10s} {'Both Right':>12s} {'Worst Fix':>25s} {'Worst Rate':>12s}")
    print("-" * 100)
    for a, b, m in pairs:
        pair_name = f"{a} + {b}"
        print(f"{pair_name:40s} {m['at_least_one_rate']:>10.1%} {m['complementarity']:>10.1%} "
              f"{m['both_right_rate']:>12.1%} {m['worst_fixture']:>25s} {m['worst_fixture_rate']:>12.1%}")

    print()

    # Highlight the best pair
    best_a, best_b, best_m = pairs[0]
    print(f"SELECTED PAIR: {best_a} + {best_b}")
    print(f"  At least one right: {best_m['at_least_one_rate']:.1%}")
    print(f"  Complementarity:    {best_m['complementarity']:.1%}")
    print(f"  Both right:         {best_m['both_right_rate']:.1%}")
    print(f"  Worst fixture:      {best_m['worst_fixture']} ({best_m['worst_fixture_rate']:.1%})")

    # Detailed per-fixture breakdown for selected pair
    print(f"\n{'=' * 80}")
    print(f"DETAILED BREAKDOWN: {best_a} + {best_b}")
    print(f"{'=' * 80}")
    sa = model_scores[best_a]
    sb = model_scores[best_b]
    fixture_ids = sorted(set(sa.keys()) & set(sb.keys()))

    print(f"{'Fixture':25s} {'Field':25s} {best_a:>10s} {best_b:>10s} {'Consensus':>10s}")
    print("-" * 80)
    for fid in fixture_ids:
        for field in SCORED_FIELDS:
            a_val = sa[fid].get(field, 0.0)
            b_val = sb[fid].get(field, 0.0)
            consensus = "AGREE" if (a_val >= RIGHT_THRESHOLD) == (b_val >= RIGHT_THRESHOLD) else "DISAGREE"
            if a_val >= RIGHT_THRESHOLD or b_val >= RIGHT_THRESHOLD:
                status = "OK"
            else:
                status = "MISS"
            print(f"{fid:25s} {field:25s} {a_val:>10.2f} {b_val:>10.2f} {status:>10s}")

    # Save results
    results = {
        'pairs': [
            {'model_a': a, 'model_b': b, 'metrics': m}
            for a, b, m in pairs
        ],
        'selected_pair': {
            'model_a': best_a,
            'model_b': best_b,
            'metrics': best_m,
        },
    }
    results_file = RESULTS_DIR / 'phase3_consensus.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {results_file}")


if __name__ == '__main__':
    main()
