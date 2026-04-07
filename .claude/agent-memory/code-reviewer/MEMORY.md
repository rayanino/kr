# Code Reviewer Memory

## Known Patterns
- D-023 metadata pass-through is the most commonly violated rule
- Arabic .lower()/.upper() violations appear in string comparison code
- Pydantic Field(None) required for Optional fields with defaults (pyright)

## Engine-Specific Notes
- [Excerpting foundations review](excerpting_foundations_review_20260404.md) -- SPEC §5.3.2 code block vs actual code prompt drift is the primary risk pattern
- [D3 SPEC additions review](d3_spec_review_20260407.md) -- §6.18-6.23 + ADV-E-13-22 all clean, atom catalog audit trail is solid

## Recurring Issues
- SPEC code blocks claiming to be the definitive prompt text can drift from actual code -- always diff them
- Prompt content tests that only check for rule name presence (e.g., "C-SC-2" in prompt) miss content drift
