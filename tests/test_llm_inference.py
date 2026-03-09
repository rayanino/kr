"""Phase 1 & 2 LLM inference test runner.

Sends the inference prompt to LLMs against all 13 fixtures,
parses responses, and scores them via eval_harness.

Usage:
  python3 tests/test_llm_inference.py --phase 1 --dry-run   # Print prompts, no API calls
  python3 tests/test_llm_inference.py --phase 1              # Sonnet 4.6 iteration
  python3 tests/test_llm_inference.py --phase 2              # All strongest-tier models
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from eval_harness import score_model_run

# Import prompt template
sys.path.insert(0, str(Path(__file__).parent.parent / 'engines' / 'source' / 'prompts'))
from inference_v1 import SYSTEM_MESSAGE, USER_MESSAGE_TEMPLATE


FIXTURES_DIR = Path(__file__).parent / 'fixtures'
RESULTS_DIR = Path(__file__).parent / 'results'


def load_fixtures():
    extracted = json.load(open(FIXTURES_DIR / 'EXTRACTED_DATA.json'))
    ground_truth = json.load(open(FIXTURES_DIR / 'GROUND_TRUTH.json'))
    return extracted, ground_truth


def format_prompt(fixture_data: dict) -> str:
    """Format the user message for a single fixture."""
    return USER_MESSAGE_TEMPLATE.format(
        prompt_context=fixture_data['prompt_context'],
        text_sample=fixture_data['text_sample'],
    )


# ── API callers ──

def call_anthropic(system_msg: str, user_msg: str, model: str, api_key: str) -> dict:
    """Call Anthropic API. Returns parsed JSON or error dict."""
    import httpx
    
    response = httpx.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json',
        },
        json={
            'model': model,
            'max_tokens': 2000,
            'system': system_msg,
            'messages': [{'role': 'user', 'content': user_msg}],
        },
        timeout=60.0,
    )
    
    if response.status_code != 200:
        return {'_parse_error': True, '_raw': response.text, '_status': response.status_code}
    
    data = response.json()
    text = data['content'][0]['text'].strip()
    return _parse_llm_json(text)


def call_openrouter(system_msg: str, user_msg: str, model: str, api_key: str) -> dict:
    """Call OpenRouter API. Returns parsed JSON or error dict."""
    import httpx
    
    response = httpx.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        json={
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': user_msg},
            ],
            'max_tokens': 2000,
        },
        timeout=90.0,
    )
    
    if response.status_code != 200:
        return {'_parse_error': True, '_raw': response.text, '_status': response.status_code}
    
    data = response.json()
    text = data['choices'][0]['message']['content'].strip()
    return _parse_llm_json(text)


def _parse_llm_json(text: str) -> dict:
    """Parse LLM response text as JSON. Returns parsed dict or error dict."""
    # Strip markdown code fences if present
    clean = text
    if clean.startswith('```'):
        clean = clean.split('\n', 1)[1] if '\n' in clean else clean[3:]
    if clean.endswith('```'):
        clean = clean.rsplit('```', 1)[0]
    clean = clean.strip()
    
    try:
        parsed = json.loads(clean)
        # Extract fields into flat structure for scoring
        result = {
            'genre': parsed.get('genre'),
            'science_scope': parsed.get('science_scope', []),
            'is_multi_layer': parsed.get('is_multi_layer', False),
            'structural_format': parsed.get('structural_format'),
            'level': parsed.get('level'),
            'authority_level': parsed.get('authority_level'),
            'author_name': parsed.get('author_identification', {}).get('canonical_name_ar', ''),
            'author_death_hijri': parsed.get('author_identification', {}).get('death_date_hijri'),
            # Preserve full response for detailed analysis
            '_full_response': parsed,
        }
        
        # Check enum compliance
        violations = []
        VALID_GENRES = {'matn','sharh','hashiyah','mukhtasar','nazm','risalah','taqrirat','mawsuah','fatawa','mujam','tabaqat','fiqh_comparative','hadith_collection','tafsir','sirah','tarikh','adab','other'}
        VALID_FORMATS = {'prose','verse','qa_format','tabular_khilaf','dictionary','commentary','mixed'}
        VALID_AUTHORITY = {'primary','reference','modern_compilation'}
        VALID_LEVELS = {'beginner','intermediate','advanced','specialist', None}
        
        if result['genre'] not in VALID_GENRES:
            violations.append(f"genre={result['genre']}")
        if result['structural_format'] not in VALID_FORMATS:
            violations.append(f"structural_format={result['structural_format']}")
        if result['authority_level'] not in VALID_AUTHORITY:
            violations.append(f"authority_level={result['authority_level']}")
        if result['level'] not in VALID_LEVELS:
            violations.append(f"level={result['level']}")
        
        if violations:
            result['_enum_violations'] = violations
        
        return result
        
    except json.JSONDecodeError as e:
        return {'_parse_error': True, '_raw': text[:500], '_error': str(e)}


# ── Model configurations ──

PHASE1_MODELS = {
    'sonnet-4.6': {
        'caller': 'anthropic',
        'model_id': 'claude-sonnet-4-6-20250514',
        'key_file': 'anthropic_api_key',
    },
}

PHASE2_MODELS = {
    'opus-4.6': {
        'caller': 'anthropic',
        'model_id': 'claude-opus-4-6-20250528',
        'key_file': 'anthropic_api_key',
    },
    'gpt-5.4': {
        'caller': 'openrouter',
        'model_id': 'openai/gpt-5.4',
        'key_file': 'openrouter_api_key',
    },
    'gemini-3.1-pro': {
        'caller': 'openrouter',
        'model_id': 'google/gemini-3.1-pro-preview',
        'key_file': 'openrouter_api_key',
    },
    'mistral-large': {
        'caller': 'openrouter',
        'model_id': 'mistralai/mistral-large-2512',
        'key_file': 'openrouter_api_key',
    },
    'command-a': {
        'caller': 'openrouter',
        'model_id': 'cohere/command-a',
        'key_file': 'openrouter_api_key',
    },
}


def load_api_key(key_file: str) -> str:
    """Load API key from project knowledge files."""
    key_path = Path('/mnt/project') / key_file
    if key_path.exists():
        return key_path.read_text().strip()
    # Fallback: try repo root
    key_path = Path(__file__).parent.parent / key_file
    if key_path.exists():
        return key_path.read_text().strip()
    raise FileNotFoundError(f"API key file not found: {key_file}")


def run_model(model_name: str, model_config: dict, fixtures: dict, dry_run: bool = False) -> dict:
    """Run a single model against all fixtures. Returns predictions dict."""
    predictions = {}
    
    if not dry_run:
        api_key = load_api_key(model_config['key_file'])
        caller = call_anthropic if model_config['caller'] == 'anthropic' else call_openrouter
    
    for fixture_id, fixture_data in fixtures.items():
        user_msg = format_prompt(fixture_data)
        
        if dry_run:
            print(f"  [{fixture_id}] Prompt length: {len(SYSTEM_MESSAGE) + len(user_msg)} chars")
            predictions[fixture_id] = {'_dry_run': True}
            continue
        
        print(f"  [{fixture_id}] Calling {model_name}...", end=' ', flush=True)
        start = time.time()
        
        try:
            result = caller(SYSTEM_MESSAGE, user_msg, model_config['model_id'], api_key)
            elapsed = time.time() - start
            
            if result.get('_parse_error'):
                print(f"PARSE ERROR ({elapsed:.1f}s)")
            elif result.get('_enum_violations'):
                print(f"OK with enum violations: {result['_enum_violations']} ({elapsed:.1f}s)")
            else:
                print(f"OK ({elapsed:.1f}s)")
            
            predictions[fixture_id] = result
            
        except Exception as e:
            print(f"EXCEPTION: {e}")
            predictions[fixture_id] = {'_parse_error': True, '_error': str(e)}
        
        # Rate limiting: 1 second between calls
        time.sleep(1.0)
    
    return predictions


def main():
    parser = argparse.ArgumentParser(description='LLM inference testing')
    parser.add_argument('--phase', type=int, choices=[1, 2], default=1)
    parser.add_argument('--dry-run', action='store_true', help='Print prompts without API calls')
    parser.add_argument('--model', type=str, help='Run only this model (by name)')
    parser.add_argument('--fixture', type=str, help='Run only this fixture')
    args = parser.parse_args()
    
    extracted, ground_truth = load_fixtures()
    
    # Filter fixtures if requested
    if args.fixture:
        extracted = {k: v for k, v in extracted.items() if k == args.fixture}
        ground_truth = {k: v for k, v in ground_truth.items() if k == args.fixture}
    
    models = PHASE1_MODELS if args.phase == 1 else PHASE2_MODELS
    if args.model:
        models = {k: v for k, v in models.items() if k == args.model}
    
    if args.dry_run:
        print("=== DRY RUN — No API calls ===\n")
        print(f"System message: {len(SYSTEM_MESSAGE)} chars\n")
        for fixture_id, fixture_data in extracted.items():
            user_msg = format_prompt(fixture_data)
            print(f"[{fixture_id}] User message: {len(user_msg)} chars "
                  f"(context={len(fixture_data['prompt_context'])}, "
                  f"sample={len(fixture_data['text_sample'])})")
        
        print(f"\nTotal fixtures: {len(extracted)}")
        print(f"Models to test: {list(models.keys())}")
        print(f"Estimated API calls: {len(extracted) * len(models)}")
        
        # Print one full prompt as example
        example_id = list(extracted.keys())[0]
        print(f"\n=== Example prompt for {example_id} ===")
        print(f"--- SYSTEM ---\n{SYSTEM_MESSAGE[:500]}...\n")
        print(f"--- USER ---\n{format_prompt(extracted[example_id])[:1000]}...\n")
        return
    
    # Ensure results directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    all_results = {}
    
    for model_name, model_config in models.items():
        print(f"\n{'='*60}")
        print(f"Model: {model_name} ({model_config['model_id']})")
        print(f"{'='*60}")
        
        predictions = run_model(model_name, model_config, extracted, dry_run=args.dry_run)
        scores = score_model_run(predictions, ground_truth)
        
        all_results[model_name] = {
            'predictions': predictions,
            'scores': scores,
        }
        
        # Print summary
        print(f"\n--- {model_name} Summary ---")
        print(f"  JSON parse rate:       {scores['json_parse_rate']:.0%}")
        print(f"  Enum violations:       {scores['enum_violation_count']}")
        print(f"  Multi-layer accuracy:  {scores['multi_layer_accuracy']:.0%}")
        print(f"  Model aggregate score: {scores['model_aggregate']:.3f}")
        
        if scores['json_parse_failures']:
            print(f"  Parse failures: {scores['json_parse_failures']}")
        
        # Per-fixture breakdown
        print(f"\n  Per-fixture scores:")
        for fid, fs in scores['fixture_scores'].items():
            agg = fs.get('aggregate', 0.0)
            genre = fs.get('genre', '-')
            scope = fs.get('science_scope', '-')
            multi = fs.get('is_multi_layer', '-')
            auth = fs.get('author_identification', '-')
            print(f"    {fid:25s} agg={agg:.3f}  genre={genre:.1f} scope={scope:.2f} multi={multi:.1f} auth={auth:.3f}")
    
    # Save results
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    phase_label = f"phase{args.phase}"
    results_file = RESULTS_DIR / f'{phase_label}_{timestamp}.json'
    
    # Serialize (remove non-serializable items)
    serializable = {}
    for model_name, data in all_results.items():
        serializable[model_name] = {
            'scores': data['scores'],
            'predictions': {
                fid: {k: v for k, v in pred.items() if k != '_full_response'}
                for fid, pred in data['predictions'].items()
            },
        }
    
    json.dump(serializable, open(results_file, 'w'), ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {results_file}")


if __name__ == '__main__':
    main()
