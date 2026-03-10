#!/usr/bin/env python3
"""Phase C Evaluation Helper — Read all data for a single book.

Usage: python3 read_book.py "book_directory_name"

Outputs all relevant fields in the corrected evaluation order:
1. Status + model pair
2. Extraction quality
3. Pipeline values (from correct source per status)
4. Both models' outputs for comparison
5. Consensus
"""
import json
import os
import sys

def read_book(book_dir):
    base = os.path.join(os.path.dirname(__file__), 'tests/results/source_engine/phase_c', book_dir)
    if not os.path.isdir(base):
        print(f"ERROR: Directory not found: {base}")
        sys.exit(1)
    
    # 1. Status + models
    r = json.load(open(os.path.join(base, 'result.json')))
    status = r.get('status')
    llm_files = os.listdir(os.path.join(base, 'llm_responses'))
    model2_file = [f for f in llm_files if f != 'claude_opus_4_6.json'][0]
    
    print(f"{'='*70}")
    print(f"BOOK: {book_dir}")
    print(f"STATUS: {status}")
    print(f"MODELS: claude_opus_4_6 + {model2_file.replace('.json','')}")
    print(f"{'='*70}")
    
    # 2. Extraction quality
    e = json.load(open(os.path.join(base, 'extraction.json')))
    p = json.load(open(os.path.join(base, 'prompt_sent.json')))
    print(f"\n--- EXTRACTION ---")
    print(f"  display_title:   {e.get('display_title')}")
    print(f"  title_full:      {e.get('title_full', 'N/A')}")
    print(f"  author_raw:      {e.get('author_name_raw', 'EMPTY')}")
    print(f"  author_death:    {e.get('author_death_hijri', 'N/A')}")
    print(f"  muhaqiq:         {e.get('muhaqiq_name_raw', 'null')}")
    print(f"  compiler:        {e.get('compiler_name_raw', 'null')}")
    print(f"  shamela_cat:     {e.get('shamela_category', 'N/A')}")
    print(f"  riwayah:         {e.get('riwayah', 'null')}")
    print(f"  quality_issues:  {e.get('_quality_issues', [])}")
    print(f"  page_count:      {e.get('page_count') or e.get('body_page_count', 'N/A')}")
    print(f"  fields_present:  {p.get('metadata_fields_present', [])}")
    print(f"  fields_absent:   {p.get('metadata_fields_absent', [])}")
    
    # 3. Opus output
    opus = json.load(open(os.path.join(base, 'llm_responses', 'claude_opus_4_6.json')))
    op = opus['parsed']
    oai = op['author_identification']
    print(f"\n--- OPUS 4.6 ---")
    print(f"  genre:           {op['genre']} (conf: {op['genre_confidence']})")
    print(f"  author:          {oai['canonical_name_ar']}")
    print(f"  author_conf:     {op['author_identification_confidence']}")
    print(f"  death_hijri:     {oai['death_date_hijri']}")
    print(f"  known_as:        {oai.get('known_as', [])}")
    print(f"  is_multi_layer:  {op['is_multi_layer']} (conf: {op.get('multi_layer_confidence')})")
    if op.get('layers'):
        for layer in op['layers']:
            print(f"    layer: {layer.get('layer_type')} — {layer.get('author_name', '?')}")
    print(f"  science_scope:   {op['science_scope']}")
    print(f"  attribution:     {op['attribution_status']}")
    print(f"  structural_fmt:  {op.get('structural_format', 'N/A')}")
    print(f"  level:           {op.get('level', 'N/A')}")
    print(f"  authority_level: {op.get('authority_level', 'N/A')}")
    
    # 4. Second model output
    m2 = json.load(open(os.path.join(base, 'llm_responses', model2_file)))
    m2p = m2['parsed']
    m2ai = m2p['author_identification']
    m2_label = model2_file.replace('.json','').upper()
    print(f"\n--- {m2_label} ---")
    print(f"  genre:           {m2p['genre']} (conf: {m2p.get('genre_confidence', 'N/A')})")
    print(f"  author:          {m2ai['canonical_name_ar']}")
    print(f"  author_conf:     {m2p.get('author_identification_confidence', 'N/A')}")
    print(f"  death_hijri:     {m2ai.get('death_date_hijri')}")
    print(f"  is_multi_layer:  {m2p['is_multi_layer']}")
    print(f"  science_scope:   {m2p.get('science_scope', 'N/A')}")
    print(f"  attribution:     {m2p.get('attribution_status', 'N/A')}")
    
    # 5. Consensus
    c = json.load(open(os.path.join(base, 'consensus.json')))
    print(f"\n--- CONSENSUS ---")
    print(f"  agreed:          {c['agreed']}")
    print(f"  models:          {c['successful_models']}")
    print(f"  needs_human_gate: {c.get('needs_human_gate', False)}")
    
    # 6. Result.json summary (for success books)
    if status == 'success':
        print(f"\n--- RESULT.JSON (success) ---")
        print(f"  genre:           {r.get('genre')}")
        print(f"  author.name:     {r.get('author', {}).get('name_arabic')}")
        print(f"  author.conf:     {r.get('author', {}).get('confidence')} ← ALWAYS 1.0, IGNORE THIS (BUG-C04)")
        print(f"  is_multi_layer:  {r.get('is_multi_layer')}")
        print(f"  science_scope:   {r.get('science_scope')}")
        print(f"  trust_tier:      {r.get('trust_tier')}")
        print(f"  trust_score:     {r.get('trust_score')}")
        print(f"  attribution:     {r.get('attribution_status')}")
        print(f"  level:           {r.get('level')}")
    else:
        print(f"\n--- RESULT.JSON (gate_abort) ---")
        print(f"  error_code:      {r.get('error_code')}")
        print(f"  gate_errors:     {r.get('gate_errors')}")
    
    # 7. Ground truth comparison (if exists)
    gt_path = os.path.join(base, 'ground_truth_comparison.json')
    if os.path.isfile(gt_path):
        gt = json.load(open(gt_path))
        print(f"\n--- GROUND TRUTH COMPARISON ---")
        print(f"  all_match:       {gt.get('all_match')}")
        print(f"  gt_key:          {gt.get('ground_truth_key')}")
        mismatches = {k: v for k, v in gt.get('comparisons', {}).items() if not v.get('match', True)}
        if mismatches:
            for field, data in mismatches.items():
                print(f"  MISMATCH {field}: expected={data.get('expected')} actual={data.get('actual')}")
    
    # ML disagreement check
    if op['is_multi_layer'] != m2p['is_multi_layer']:
        print(f"\n⚠️  ML DISAGREEMENT: Opus={op['is_multi_layer']}, {m2_label}={m2p['is_multi_layer']}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 read_book.py 'book_directory_name'")
        print("\nAvailable books:")
        base = os.path.join(os.path.dirname(__file__) or '.', 'tests/results/source_engine/phase_c')
        for d in sorted(os.listdir(base)):
            if os.path.isdir(os.path.join(base, d)):
                print(f"  {d}")
        sys.exit(1)
    read_book(sys.argv[1])
