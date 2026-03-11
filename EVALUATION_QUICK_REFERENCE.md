# Evaluation Quick Reference — Read Before EACH Book

This is a compact checklist. Re-read it before writing each verdict to prevent drift.

## Per-Book Sequence (do not reorder)
1. `python3 read_book.py "book_name"` — read ALL pipeline data
2. Note: status (success/gate_abort), model pair, extraction quality
3. Check extraction.json: author_name_raw text content (death dates embedded?), shamela_category, quality_issues
4. Check prompt_sent.json: fields_present vs fields_absent
5. Compare Opus vs second model on: genre, ML, science_scope, attribution, layers, death_date
6. Note any ML disagreement — consensus does NOT check ML (Correction 7)
7. Web search (BEFORE writing) — at minimum 1 search per book
8. web_fetch at least 1 URL per book
9. Write structured verdict using exact format
10. Mark death date as pass-through (in extraction or raw text) vs genuine inference

## Field Sources (do NOT mix these up)
| Field | SUCCESS books | GATE_ABORT books |
|-------|-------------|-----------------|
| Author name | result.json | llm_responses/ |
| Author confidence | **llm_responses/ ONLY** (result.json = always 1.0, BUG) | llm_responses/ |
| Death date | llm_responses/ (not in result.json) | llm_responses/ |
| Genre | result.json | llm_responses/ |
| Multi-layer | result.json | llm_responses/ |
| Science scope | result.json | llm_responses/ |
| Trust tier | result.json | NOT AVAILABLE — skip |

## Source Independence (Correction 5)
ONE collective source: shamela.ws, ketabonline.com, turath.io, waqfeya.net
VERIFIED requires: 2+ genuinely INDEPENDENT sources (Wikipedia, archive.org, noor-book.com, islamway.net, alukah.net, government sites, academic catalogs, publisher sites)

## What WRONG Looks Like (learn from prior errors)

**ERROR: Accepting imprecise science terms.**
WRONG: "Science VERIFIED — ['tarikh', 'sirah']" for a biographical dictionary.
WHY: 'sirah' means prophetic biography. A biographical dictionary is tarikh/tarajim, not sirah.
RIGHT: "Science PLAUSIBLE — CA's 'sirah' is technically imprecise for this biographical dictionary."

**ERROR: Saying "ML correct" when tahqiq is the only basis.**
WRONG: مسند أحمد "ML=true is correct because it has tahqiq notes."
WHY: Tahqiq notes are editorial apparatus, not a scholarly layer. ML should be false.
RIGHT: "ML FLAG — Opus=true based solely on tahqiq_note layer. CA=false (correct). Known bias."

**ERROR: Writing "correct per SPEC rules" without verifying.**
WRONG: "Trust=flagged is correct per SPEC rules (modern compilation → flagged)."
WHY: You didn't trace through the engine code. Result.json may use different logic.
RIGHT: "Trust=flagged. The mechanism is not traced; noting the value without explaining causation."

**ERROR: Counting Shamela-ecosystem as independent.**
WRONG: "VERIFIED — ketabonline + shamela.ws + archive.org = 3 independent sources."
WHY: ketabonline and shamela.ws are the same ecosystem. Real count: 1 independent + 1 ecosystem.
RIGHT: "archive.org (independent) + Shamela-ecosystem (ketabonline, shamela.ws) = 1 independent. Need 1 more."

**ERROR: Invented verdict categories.**
WRONG: "Verdict: VERIFIED with FLAG" or "Verdict: MOSTLY VERIFIED"
WHY: Only 5 categories exist: VERIFIED, PLAUSIBLE, UNVERIFIABLE, FLAG, ESCALATE.
RIGHT: "Verdict: VERIFIED" with a field-level note in the relevant field.

**ERROR: Internal contradiction after multi-round edits.**
WRONG: Science field says "CA's sirah is questionable" but Notes say "Neither science is wrong."
WHY: Round 3 fixed the Science field but didn't update Notes.
RIGHT: Both sections must say the same thing. Grep for key terms after editing.

## Mid-Session Quality Gate
After book 3 (or 4), STOP. Re-read this checklist. Ask yourself:
- Am I still doing web_fetch, or did I start relying on search snippets?
- Am I still checking both models, or just reading result.json?
- Am I still writing "Death source: pass-through/inferred" or did I stop?
- Is my verdict format still complete, or am I abbreviating?
If any answer is "I drifted," go back and fix the affected books before continuing.
