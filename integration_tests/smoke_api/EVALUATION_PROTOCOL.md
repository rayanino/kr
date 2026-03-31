# Excerpting Engine — Evaluation Protocol

## Run Summary (2026-03-31)

| Package | Excerpts | Errors | Cost | Backend |
|---------|----------|--------|------|---------|
| ibn_aqil_v1 | 19 | 0 | €0.32 | API (OpenRouter) |
| ibn_aqil_v3 | 44 | 0 | €1.08 | API (OpenRouter) |
| taysir | 28 | 3 (EX-V-002) | €0.78 | API (OpenRouter) |
| ext_39_masala | 22 | 0 | €0.34 | API (OpenRouter) |
| ext_46_qa | 20 | 1 (EX-V-002) | €0.41 | API (OpenRouter) |
| **TOTAL** | **133** | **4** | **€2.93** | 33 minutes |

Models: GPT-5.4 (primary), Claude Opus 4.6 (verify), Gemini 2.5 Pro (escalation).

## Evaluation Team

| Reviewer | Role | Tool |
|----------|------|------|
| **Owner** | Human gate — scholarly correctness, Arabic quality | `python tools/review.py integration_tests/smoke_api/` |
| **Claude Code** | Code-level analysis, SPEC compliance, metadata integrity | This session or new CC session |
| **Codex (GPT-5.4)** | Cross-model structural review, pattern detection | `codex exec` with excerpts piped in |
| **Gemini** | Independent Arabic content review, alternative perspective | `gemini -p` with excerpts piped in |
| **Claude Chat** | Deep scholarly review with 200K context — full excerpt set | Upload excerpts.jsonl to claude.ai |
| **ChatGPT Pro** | Independent evaluation, disagreement detection | Upload to ChatGPT |

## Evaluation Dimensions

### 1. Excerpt Quality (Owner + all LLMs)
For each excerpt:
- Is the `primary_text` a valid, self-contained teaching unit?
- Is the `primary_function` correctly classified?
- Is the `self_containment` rating accurate?
- Is the `description_arabic` a faithful gloss?
- Are `quoted_scholars` correctly identified and resolved?
- Is the `school` attribution correct (when present)?

### 2. Structural Integrity (Claude Code)
- D-023: Do excerpts preserve all upstream metadata?
- Are excerpt boundaries correct (no mid-sentence splits)?
- Do `start_word`/`end_word` match `primary_text`?
- Are `segment_indices` consistent with the source chunks?
- Do validation errors (EX-V-002) represent appropriate filtering?

### 3. Consensus Quality (Claude Code + Codex)
- For excerpts with `consensus_metadata`: do enrichment and verifier agree?
- Where they disagree: is the final resolution correct?
- Are gate flags appropriate (not over- or under-triggering)?
- Are `review_flags` meaningful?

### 4. Coverage Analysis (All reviewers)
- Are there teaching units that SHOULD have been extracted but weren't?
- Is the excerpt count reasonable for each source text?
- Are any scholarly functions over/under-represented?

### 5. Arabic Text Fidelity (Owner + Gemini)
- Are diacritics preserved byte-for-byte?
- Are honorifics intact (صلى الله عليه وسلم, رضي الله عنه, etc.)?
- Are Quranic citations properly bounded?
- Does the text render correctly in RTL?

## Owner Review Workflow

1. **Start viewer**: `python tools/review.py integration_tests/smoke_api/`
2. **Review one package at a time** — start with `taysir` (smallest, cleanest)
3. **For each excerpt**: give verdict (Accept / Needs Work / Reject) + comments
4. **Focus on**: is this what you'd want in your library?
5. **Feedback saves to**: `integration_tests/smoke_api/{package}/owner_feedback.jsonl`

## LLM Review Instructions

### For Claude Code (next CC session)
```
Read integration_tests/smoke_api/EVALUATION_PROTOCOL.md first.
Then for each package:
1. Read excerpts.jsonl
2. Read owner_feedback.jsonl (if present)
3. Evaluate each excerpt against the 5 dimensions above
4. Write your findings to integration_tests/smoke_api/{package}/cc_evaluation.md
```

### For Codex
```bash
cat integration_tests/smoke_api/taysir/excerpts.jsonl | codex exec "
Evaluate these Arabic scholarly text excerpts from the KR pipeline.
For each excerpt, assess:
1. Is primary_function correct?
2. Is self_containment accurate?
3. Are quoted_scholars properly resolved?
4. Are there any red flags in the data?
Output a structured JSONL evaluation."
```

### For Gemini
```bash
cat integration_tests/smoke_api/taysir/excerpts.jsonl | gemini -p "
You are reviewing Arabic scholarly text excerpts. For each:
1. Is the Arabic text a coherent teaching unit?
2. Is the scholarly function classification correct?
3. Are scholar names correctly identified?
4. Is the madhab/school attribution accurate?
Give a brief verdict per excerpt." -y --output-format text
```

### For Claude Chat / ChatGPT Pro
Upload `integration_tests/smoke_api/{package}/excerpts.jsonl` and ask:
"These are excerpts from an Arabic scholarly text pipeline. Each is meant to be a self-contained teaching unit. For each, assess: (1) quality of the text boundary, (2) correctness of the scholarly function label, (3) accuracy of scholar identifications, (4) overall: would this be useful in a scholarly library? Give structured feedback."

## Quality Gates (before next run)

Before running a larger/more expensive evaluation:

- [ ] Owner has reviewed at least 1 complete package via the viewer
- [ ] At least 2 LLM reviewers have independently evaluated the same package
- [ ] Disagreements between reviewers have been investigated
- [ ] Any pipeline bugs identified have been fixed
- [ ] EX-V-002 errors have been investigated (are they appropriate drops?)
- [ ] Gate flags reviewed for false positives/negatives
- [ ] Cost projection for the next run documented

## Files

```
integration_tests/smoke_api/
├── SUMMARY.json                    ← run summary
├── EVALUATION_PROTOCOL.md          ← this file
├── ibn_aqil_v1/
│   ├── excerpts.jsonl              ← 19 excerpts
│   ├── owner_feedback.jsonl        ← (after owner review)
│   ├── cc_evaluation.md            ← (after CC review)
│   └── run_metadata.json
├── ibn_aqil_v3/                    ← 44 excerpts
├── taysir/                         ← 28 excerpts
├── ext_39_masala/                  ← 22 excerpts
└── ext_46_qa/                      ← 20 excerpts
```
