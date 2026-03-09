#!/usr/bin/env python3
"""Extract metadata and text samples from all fixtures for Step 2 LLM testing.

Run: python3 scripts/extract_fixtures.py
Output: tests/fixtures/EXTRACTED_DATA.json

This produces the exact data that would be passed to the LLM inference prompt
(§4.A.4 of SPEC_CORE.md). Each fixture entry contains:
  - extracted_metadata: what the format-specific extractor produces
  - text_sample: first 2000 chars of body text
  - prompt_context: pre-formatted metadata string for the LLM prompt
"""

import hashlib
import json
import os
import re
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def strip_tags(s: str) -> str:
    return re.sub(r'<[^>]+>', '', s).strip()


FIELD_MAP = {
    'الكتاب': 'title_full', 'اسم الكتاب': 'title_full',
    'المؤلف': 'author_name_raw', 'المحقق': 'muhaqiq_name_raw',
    'تحقيق': 'muhaqiq_name_raw', 'دراسة وتحقيق': 'muhaqiq_name_raw',
    'تحقيق ودراسة': 'muhaqiq_name_raw', 'تحقيق وتعليق': 'muhaqiq_name_raw',
    'راجعه': 'muhaqiq_name_raw', 'راجعه ودققه': 'muhaqiq_name_raw',
    'الناشر': 'publisher', 'الطبعة': 'edition_raw',
    'عدد الأجزاء': 'volume_count_raw', 'عدد الصفحات': 'page_count_raw',
    'عدد صفحات (الكتاب الورقي)': 'page_count_raw',
    'عام النشر': 'publication_year_raw',
    'تاريخ النشر بالشاملة': 'shamela_publish_date',
    'مصدر الكتاب': 'source_note', 'تنبيه': 'editorial_note',
    'إعداد': 'author_name_raw', 'إشراف': 'supervisor', 'رسالة': 'thesis_info',
}


def extract_shamela(fixture_path: str) -> dict:
    """Full extraction from a Shamela fixture directory."""
    htm_files = sorted([f for f in os.listdir(fixture_path) if f.endswith('.htm')])
    if not htm_files:
        return {"error": "no .htm files"}
    
    numbered = [f for f in htm_files if re.match(r'^\d+', f.split('.')[0])]
    muqaddima = next((f for f in htm_files if 'المقدمة' in f), None)
    first_file = numbered[0] if numbered else htm_files[0]
    is_multi = len(numbered) > 1 or (len(numbered) == 1 and muqaddima is not None)
    vol_count = len(numbered) if numbered else 1
    
    filepath = os.path.join(fixture_path, first_file)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {
        'source_format': 'shamela_html',
        'is_multi_volume': is_multi,
        'volume_count': vol_count,
        'has_muqaddima': muqaddima is not None,
    }
    
    # Card extraction
    card_match = re.search(r"<div class='PageText'>(.*?)</div>", content, re.DOTALL)
    if not card_match:
        return {"error": "no PageText div"}
    card = card_match.group(1)
    
    # Header
    header_match = re.match(
        r"\s*<span class='title'>(.*?)(?:&nbsp;)+\s*</span>"
        r"\s*(?:<span class='footnote'>\((.*?)\)</span>)?",
        card
    )
    if header_match:
        result['display_title'] = strip_tags(header_match.group(1)).strip()
        if header_match.group(2):
            result['author_short'] = header_match.group(2).strip()
    
    # Category
    cat_match = re.search(
        r"<span class='title'>القسم.*?</span>\s*(.*?)(?:<hr|<p>)", card, re.DOTALL
    )
    if cat_match:
        result['shamela_category'] = strip_tags(cat_match.group(1)).strip()
    
    # Bibliographic fields
    for m in re.finditer(
        r"<span class='title'>(.*?)(?:<font[^>]*>)?:(?:</font>)?</span>\s*(.*?)(?:<p>|<hr|$)",
        card, re.DOTALL
    ):
        label = strip_tags(m.group(1)).strip()
        value = strip_tags(m.group(2)).strip()
        if label in FIELD_MAP and value:
            internal = FIELD_MAP[label]
            if internal not in result or label in ('الكتاب', 'المؤلف', 'المحقق'):
                result[internal] = value
    
    # Death date
    if 'author_name_raw' in result:
        death_match = re.search(
            r'\(.*?(?:المتوفى|ت)\s*:?\s*(\d+)\s*هـ\)?', result['author_name_raw']
        )
        if death_match:
            result['author_death_hijri'] = int(death_match.group(1))
        else:
            range_match = re.search(r'\((\d+)\s*-\s*(\d+)\s*هـ\)', result['author_name_raw'])
            if range_match:
                result['author_birth_hijri'] = int(range_match.group(1))
                result['author_death_hijri'] = int(range_match.group(2))
    
    # Page count (digital body pages)
    body_pages = len(re.findall(r"<div class='PageText'>", content)) - 1
    result['page_count'] = body_pages
    
    # Text sample (split-based extraction to handle nested PageHead div)
    body_text_parts = []
    page_segments = re.split(r"<div class='PageText'>", content)
    for i, seg in enumerate(page_segments):
        if i <= 1:
            continue
        after_pagehead = seg.split("</div>", 1)
        if len(after_pagehead) < 2:
            continue
        body_html = after_pagehead[1].split("</div>")[0]
        body_html = re.sub(r"<hr[^>]*>.*$", '', body_html, flags=re.DOTALL)
        body = strip_tags(body_html).strip()
        if body:
            body_text_parts.append(body)
        if sum(len(p) for p in body_text_parts) > 2000:
            break
    result['text_sample'] = '\n'.join(body_text_parts)[:2000]
    
    # SHA-256
    with open(filepath, 'rb') as f:
        result['file_hash'] = hashlib.sha256(f.read()).hexdigest()
    result['source_id'] = f"src_{result['file_hash'][:8]}"
    
    return result


def extract_plaintext(filepath: str) -> dict:
    """Full extraction from a plain text fixture."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    result = {
        'source_format': 'plain_text',
        'title_arabic': lines[0] if lines else os.path.basename(filepath),
        'page_count': None,
        'text_sample': text[:2000],
        'is_multi_volume': False,
        'volume_count': 1,
    }
    
    with open(filepath, 'rb') as f:
        result['file_hash'] = hashlib.sha256(f.read()).hexdigest()
    result['source_id'] = f"src_{result['file_hash'][:8]}"
    
    return result


def build_prompt_context(data: dict) -> str:
    """Format extracted metadata as the context string for the LLM prompt."""
    lines = []
    
    title = data.get('title_full', data.get('display_title', data.get('title_arabic', 'Unknown')))
    lines.append(f"Title: {title}")
    
    if 'author_name_raw' in data:
        lines.append(f"Author field: {data['author_name_raw']}")
    elif 'author_short' in data:
        lines.append(f"Author (short): {data['author_short']}")
    else:
        lines.append("Author: NOT FOUND IN METADATA")
    
    if 'muhaqiq_name_raw' in data:
        lines.append(f"Muhaqiq/Editor: {data['muhaqiq_name_raw']}")
    
    if 'publisher' in data:
        lines.append(f"Publisher: {data['publisher']}")
    
    if 'shamela_category' in data:
        lines.append(f"Shamela category: {data['shamela_category']}")
    
    if 'edition_raw' in data:
        lines.append(f"Edition: {data['edition_raw']}")
    
    fmt = data.get('source_format', 'unknown')
    lines.append(f"Source format: {fmt}")
    
    if data.get('is_multi_volume'):
        lines.append(f"Multi-volume: yes ({data.get('volume_count', '?')} volumes)")
    else:
        lines.append("Multi-volume: no")
    
    return '\n'.join(lines)


def main():
    base_shamela = os.path.join(os.path.dirname(__file__), '..', 'tests', 'fixtures', 'shamela_real')
    base_alfiyyah = os.path.join(os.path.dirname(__file__), '..', 'tests', 'fixtures', 'alfiyyah_versified')
    
    all_data = {}
    
    # Shamela fixtures
    for fixture_dir in sorted(os.listdir(base_shamela)):
        fixture_path = os.path.join(base_shamela, fixture_dir)
        if not os.path.isdir(fixture_path):
            continue
        
        data = extract_shamela(fixture_path)
        data['prompt_context'] = build_prompt_context(data)
        all_data[fixture_dir] = data
        print(f"  Extracted {fixture_dir}: {len(data.get('text_sample', ''))} chars text sample")
    
    # Plain text fixture
    alfiyyah_path = os.path.join(base_alfiyyah, 'alfiyyah.txt')
    if os.path.exists(alfiyyah_path):
        data = extract_plaintext(alfiyyah_path)
        data['prompt_context'] = build_prompt_context(data)
        all_data['alfiyyah_versified'] = data
        print(f"  Extracted alfiyyah_versified: {len(data.get('text_sample', ''))} chars text sample")
    
    output_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'fixtures', 'EXTRACTED_DATA.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nWritten: {output_path} ({len(all_data)} fixtures)")


if __name__ == '__main__':
    main()
