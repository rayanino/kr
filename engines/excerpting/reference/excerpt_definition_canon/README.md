# Excerpt Definition Canon

## Status

This directory is the **current authoritative excerpt-definition canon** for the excerpting engine as of `2026-04-03`.

It is authoritative for:

- what currently counts as an excerpt candidate
- the current distinction between acceptable excerpts and directly study-ready excerpts
- the current controlled vocabulary around self-containment, context, boundary, function, rule/proof, relation integrity, and related dimensions
- the current list of accepted, provisional, emerging, and unresolved doctrine extracted from owner-reviewed cases

It is **not** a claim that excerpt-definition doctrine is fully finished. The canon itself records unresolved and underdefined areas. Treat those bounds as binding.

## Read Order

1. `01_dossier.md` — human canonical artifact
2. `11_hard_judgment.md` — what is still weak or unsafe to freeze
3. `02_terms.yaml` — controlled vocabulary
4. `03_principles.jsonl` through `10_coverage.yaml` — machine-readable doctrine registers
5. `00_manifest.yaml` — bundle metadata and current scope

## Authority Rule

- This directory supersedes the old "single source of truth" claim in `engines/excerpting/reference/ABD_EXCERPT_DEFINITION.md`.
- `ABD_EXCERPT_DEFINITION.md` remains a historical reference artifact, not the live authority for excerpt-definition doctrine.
- The preserved collection snapshot at `engines/excerpting/chatgpt_f1_collection/canon/excerpt_definition/` is provenance, not the active doctrine lane.

## Provenance

This canon was promoted from the validated ChatGPT F1 bundle after:

- owner-reviewed case extraction and canon backfill
- byte-level comparison against the ZIP bundle at `C:\\Users\\Rayane\\Downloads\\canon_excerpt_definition_bundle.zip`
- normalization of two harmless leading-blank-line artifacts in the collection copy

The files in this directory are currently byte-identical to the validated 12-file bundle content.

Companion provenance/evidence artifacts live at:

- `engines/excerpting/chatgpt_f1_collection/README.md`
- `engines/excerpting/chatgpt_f1_collection/manifest.yaml`

Important: as of this promotion, the processed canon is preserved and promoted, but the owner's first raw wording has **not yet been anchored in a repo-visible artifact**. Do not confuse the promoted canon with the full raw owner evidence stack.

## Closure Boundary

This promotion closes the **raw collection / backfill preservation phase** of F1.

It does **not** mean every excerpt-definition question is final. The live unresolved surface is recorded in:

- `04_unresolved.jsonl`
- `10_coverage.yaml`
- `11_hard_judgment.md`
