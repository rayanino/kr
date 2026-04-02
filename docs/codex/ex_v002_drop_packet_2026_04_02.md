# `EX-V-002` Drop Packet — 2026-04-02

Purpose: capture the first execution-ready evidence packet for the top-ranked
failure class in `smoke_api_v2`: post-grouping validation drops that remove
already-built units before final excerpt output.

## Scope

Completed packages with explicit `validation_drops.jsonl` evidence:

- `ext_39_masala`: `3` drops
- `ext_46_qa`: `12` drops
- `ibn_aqil_v1`: `2` drops
- `ibn_aqil_v3`: `5` drops

Confirmed minimum total: `22` dropped units in completed packages.

## Evidence Paths

- `integration_tests/smoke_api_v2/ext_39_masala/validation_drops.jsonl`
- `integration_tests/smoke_api_v2/ext_46_qa/validation_drops.jsonl`
- `integration_tests/smoke_api_v2/ibn_aqil_v1/validation_drops.jsonl`
- `integration_tests/smoke_api_v2/ibn_aqil_v3/validation_drops.jsonl`
- `integration_tests/smoke_api_v2/analysis/campaign_summary.md`

## Concrete Dropped Units

### ext_39_masala

- `div_src_test0001_2_000_pre / unit 5`
  - snippet: `6 - ويجب أن يوصي للأقربين الذين لا يرثون منه لقوله تبارك وتعالى...`
- `div_src_test0001_3_005 / unit 4`
  - snippet: `الرابعة: الاستشهاد في ساحة القتال قال الله تعالى...`
- `div_src_test0001_3_011 / unit 0`
  - snippet: `صفة صلاة الجنازة.`

### ext_46_qa

- `div_src_test0001_5_003 / unit 0`
  - snippet: `المسألة الخامسة ... دلالات النحوية ثلاث...`
- `div_src_test0001_5_007 / unit 0`
  - snippet: `المسألة التاسعة ... اختلف: هل بين العربي والعجمي واسطة؟`
- `div_src_test0001_5_009 / unit 1`
  - snippet: `انتهى.`
- `div_src_test0001_3_010 / unit 4`
  - snippet: `الثالثة`
- `div_src_test0001_3_010 / unit 7`
  - snippet: `الرابعة`

### ibn_aqil_v1

- `div_src_test0001_2_002 / unit 17`
  - snippet: `ف قد جمعا … يكسر في الجر وفي النصب معا...`
- `div_src_test0001_2_009_pre / unit 14`
  - snippet: `ذفونها ويبقون الخبر … وبعد إن ولو كثيرا ذا اشتهر...`

### ibn_aqil_v3

- `div_src_test0001_3_005 / unit 0`
  - snippet: `أبنية المصادر`
- `div_src_test0001_3_009 / unit 10`
  - snippet: `ويذكر المخصوص بعد مبتدأ … أو خبر أسم ليس يبدو أبدا...`
- `div_src_test0001_3_010 / unit 6`
  - snippet: `قيل ومن استعمال صيغة أفعل التفضيل قوله تعالى...`
- `div_src_test0001_3_011 / unit 0`
  - snippet: `التوابع / النعت`
- `div_src_test0001_4_006 / unit 0`
  - snippet: `التحذير والإغراء`

## Immediate Reading

The dropped units are not confined to one content type:

- full substantive rules
- section headings / structural transitions
- tiny remnants like `الثالثة`, `الرابعة`, `انتهى`
- larger explanatory units

That suggests the failure seam is likely in post-grouping validation or
writer-side acceptance criteria, not in one narrow scholarly-function family.

## Next Useful Checks

1. Compare these dropped units against `EX-V-002` validation logic and the
   final writer/validation acceptance path.
2. Separate “trivial structural fragment dropped correctly” from “real unit
   dropped incorrectly” before proposing engine changes.
3. Use these exact unit ids as the first regression fixture set when the
   engine lane opens again.
