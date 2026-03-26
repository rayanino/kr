---
description: "Run E2E UI tests. Usage: /ui-test [component|full]. Dormant until UI phase."
allowed-tools: ["Bash(npx *)", "Bash(node *)"]
---
Run Playwright E2E tests for the KR scholarly library interface.

NOTE: This command is dormant until the UI phase begins. If no Playwright
config exists (`playwright.config.ts`), report "UI tests not yet configured — this command will activate when the frontend is built" and exit.

If $ARGUMENTS is a component name:
  `npx playwright test --grep "$ARGUMENTS" --reporter=html`

If $ARGUMENTS is "full" or empty:
  `npx playwright test --reporter=html`

After tests complete:
1. Report pass/fail count
2. For failures: show screenshot path and error message
3. Check Arabic rendering: grep test output for RTL/bidi issues
4. Report accessibility violations if any
5. Open HTML report: `npx playwright show-report`

## Arabic-Specific Checks
- Verify `dir="rtl"` is set on Arabic content containers
- Verify diacritics render visibly (not clipped or hidden)
- Verify scholar names display in Arabic script
- Verify search handles Arabic input (tatweel, hamza variants)
