# Questionnaire Packet Maintenance

Use this file when changing the questionnaire/evaluation packet itself.

This is maintainer-facing, not owner-facing.

## Goals

Keep the packet:

- internally consistent
- explicit about authority boundaries
- honest about blocked states
- ready for owner review
- ready for later evaluator synthesis

## Core Commands

### 1. Validate the packet after edits

```bash
python scripts/validate_questionnaire_packet.py
```

This checks the current hardened invariants, including:

- 40 total interactions
- 38 active / 2 blocked (`CJ-2`, `CJ-3`)
- heading/title sync between `interactions.json` and `OWNER_QUESTIONNAIRE.md`
- hardened owner-facing wording
- blocked-state handling in runtime surfaces
- doctrine/synthesis guardrails that should not drift

### 2. Build a Gemini upload bundle from the current local checkout

Pre-owner review packet:

```bash
python scripts/build_questionnaire_dr_bundle.py --profile gemini-core --output-dir overnight_codex/gemini_questionnaire_bundle_current
```

Post-owner review packet:

```bash
python scripts/build_questionnaire_dr_bundle.py --profile gemini-post --output-dir overnight_codex/gemini_questionnaire_bundle_post
```

### 3. Summarize questionnaire completion after owner responses exist

```bash
python scripts/summarize_questionnaire_responses.py
```

This generates:

- `evaluation_reports/OWNER_RESPONSE_SUMMARY.md`
- `evaluation_reports/OWNER_RESPONSE_SUMMARY.json`

### 4. Audit response readiness before multi-coworker review

```bash
python scripts/audit_questionnaire_responses.py
```

This generates:

- `evaluation_reports/QUESTIONNAIRE_AUDIT.md`
- `evaluation_reports/QUESTIONNAIRE_AUDIT.json`

### 5. Generate reviewer dispatch packets after responses exist

```bash
python scripts/generate_questionnaire_review_packets.py
```

This generates:

- `evaluation_reports/dispatch_packets/`

## External Reports

Browser research outputs are not local truth automatically.

If external reports influence packet changes:

1. adjudicate them against the current local packet
2. record accepted vs rejected findings
3. preserve the result in:
   - `docs/codex/questionnaire_external_report_adjudication_2026_04_02.md`
   - `evaluation_reports/OWNER_RELAYED_BROWSER_REPORTS_DIGEST_2026_04_02.md`

## Minimum Standards Before Saying The Packet Is Ready

- packet validator passes
- required quality gate passes for changed paths
- blocked states are honest in both docs and runtime
- no owner-facing wording implies owner authority
- no evaluator-facing wording allows owner preference to override invariants
- DR bundle paths and remote/local access assumptions are explicit
