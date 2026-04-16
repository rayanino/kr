# 60-evidence/dr-reports/

Purpose: structured records of Deep Research (DR) reports commissioned on source-engine questions. One file per (question, provider, date) tuple.

Naming: `dr-{provider}-{question-slug}-{YYYYMMDD}.yaml`

Providers: `chatgpt`, `claude`, `gemini` (DR-capable tiers).

## Why these live here, not in `dr-prompts/`

`dr-prompts/` captures what we **sent**. `dr-reports/` captures what **came back**.

The raw DR markdown/text archives live in the owner's Downloads folder and are NOT committed to the repo per Rule 17 (no repo pollution). These YAML files are the structured, permanent, repo-side record:

- Paragraph-level inventory of every claim in the DR
- Implementation target per paragraph (source-engine atom, cross-engine commitment, informational-only, or explicitly rejected)
- Binding source-engine commitments extracted from the DR
- Cross-engine commitments deferred to future engine specs
- Rejection log (claims judged wrong or out-of-scope)
- Cross-check status (whether a twin DR or coworker review has been reconciled)

## Integration discipline

Every paragraph of a DR MUST land in one of:

1. A source-engine atom amendment or new atom
2. A cross-engine commitment logged for future specs
3. An informational observation (explicit, not hidden)
4. A rejection (with documented rationale)

A DR where any paragraph is unaccounted-for is not integrated. The owner's standard is explicit: no paragraph stays unused.
