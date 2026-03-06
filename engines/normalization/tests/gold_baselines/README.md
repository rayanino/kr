# Gold Baselines

Each gold baseline is a hand-verified expected output for a specific test fixture.
Used to detect regressions: if the normalizer's output changes, the test fails.

## How to Create a Baseline

1. Run the normalizer on the fixture
2. Manually verify the output is correct (check every field)
3. Save as `{fixture_name}_expected.json` in this directory

## Baselines Needed

### 1. Format-agnostic infrastructure
- **Fixture:** Synthetic `ContentUnit` data (no real source needed)
- **Tests:** Validation, writer, dispatcher routing
- **Status:** Can be created during Step 1-3 implementation

### 2. Per-normalizer baselines (created when each normalizer is built)

| Fixture | Format | Status |
|---------|--------|--------|
| `shamela_ibn_aqil.htm` | Shamela HTML | Fixture exists, baseline needed |
| [PDF fixture needed] | PDF text | Fixture + baseline needed |
| [Plain text fixture needed] | Plain text | Fixture + baseline needed |
| [Image fixture needed] | Image scan | Fixture + baseline needed |

**Owner action needed:** Provide sample scholarly sources in at least 2 formats (e.g., a PDF of an Arabic book + the same book as Shamela export). This enables cross-format testing — the same work normalized from different formats should produce semantically equivalent output.
