# DR18 Verification Notes

**Source:** DR18 Claude DR — Owner Decision Map (523 lines, 31 decision points)
**Verified by:** CC (3 parallel explore agents against actual codebase)
**Date:** 2026-04-07

## Verification Summary

- **26/31 claims CONFIRMED** with file:line evidence
- **2/31 claims WRONG** — corrections below
- **3/31 claims PARTIALLY CONFIRMED** — nuances noted
- **11 GAPS FOUND** — decisions DR18 missed (see DR18_gap_analysis.md)

## Corrections

### CORRECTION 1: SRC-D-001 (Muhaqiq List) — NOT Hardcoded

**DR18 says:** "hardcoded muhaqiq list that determines trust_tier"
**Actual:** The list is **configurable** via `library/config/muhaqiq_lists.json`. Per `engines/source/SPEC.md:947`: "The recognized muhaqiqs list (§4.A.8) and the watchlist of commercial editors are both configurable. Initial watchlist entries are derived from domain knowledge sources. The owner can add or remove entries."

**Impact on data collection:** The MECHANISM already exists. Owner still needs to review the initial list, but the capture method is simpler than DR18 implies — it's editing a JSON file, not a SPEC change.

### CORRECTION 2: TAX-D-003 (Sarf Priority) — No Evidence

**DR18 says:** "sarf is highest priority after nahw"
**Actual:** `taxonomy_registry.yaml` has NO priority field. All 5 science trees (nahw, sarf, balagha, imlaa, aqidah) are status "active." The ordering in the YAML appears to be by creation date, not priority.

**Impact on data collection:** This MUST be explicitly asked of the owner — DR18 assumed an answer that doesn't exist. Added to Session A (Science & Scope) in the collection plan.

## Nuances (Partially Confirmed)

### SRC-D-002: Publisher List
DR18 is correct that examples exist but no formal list. However, the SPEC also mentions a configurable watchlist mechanism (same as muhaqiq list) at SPEC.md:947. The infrastructure exists; the data doesn't.

### EXC-D-010: Flag Budget Threshold
DR18 says "configurable threshold mentioned but not set." Partially true — FP-21 at SPEC.md:81 gives an **example value** (>15%) with "e.g." qualifier. It's a suggestion, not a default. Owner needs to confirm or adjust.

### TAX-D-001: Tree States
DR18 says various stages for 4 trees. Verified: ALL 5 trees have "active" status in `taxonomy_registry.yaml`. Nahw is v2.0 (183 leaves), others are v0.x or v1.0. The "various stages" is about maturity, not availability.

## Additional Source Contract Fields DR18 Missed

Found in `engines/source/contracts.py`:
- `OWNER_OVERRIDE = "owner_override"` — TrustTier enum value (line 74)
- `preferred_source_id: Optional[str]` — WorkRegistryEntry (line 688)
- `preferred_edition_recommendation: Optional[str]` — SourceMetadata (line 549)
- `owner_authored_type: Optional[OwnerAuthoredType]` — SourceMetadata (line 836)

These represent 4 additional owner-touchpoint fields that DR18 did not map.

## SCIENCE.md Status

DR18 references SCIENCE.md files as owner decision points (SYN-D-001). Actual files at `library/sciences/*/SCIENCE.md` are **placeholders only**: "Status: Placeholder — full Level 3 documentation to be written during Phase 2." School lists are deferred to Stage 2 per `engines/taxonomy/SPEC.md:450`.
