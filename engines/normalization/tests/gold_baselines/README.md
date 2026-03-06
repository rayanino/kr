# Gold Baselines for Normalization Testing

Gold baselines are manually verified normalization outputs used for regression testing.
See SPEC §10 for requirements.

## Required Baselines (SPEC §10)

### 1. shamela_ibn_aqil (single-volume sharh)
- **Source fixture:** `fixtures/shamela_ibn_aqil.htm`
- **What to verify:** Content preservation, footnote separation, structure discovery,
  bold-matn layer detection, verse detection, Quran citation flagging, diacritics.
- **Status:** Fixture created. Gold baseline needs manual verification after first
  successful normalization run.

### 2. shamela_multi_volume (multi-volume source)
- **Source fixture:** [NEEDED] A Shamela export with multiple .htm files.
- **What to verify:** Cross-volume unit_index continuity, volume metadata.
- **Status:** Fixture not yet created.

### 3. shamela_vocalized (heavily diacritized text)
- **Source fixture:** alfiyyah_versified (available in tests/fixtures/)
- **What to verify:** Character-level diacritics preservation (§5 check 8).
- **Status:** Fixture exists but not in Shamela format. Conversion needed.

## Creating a Gold Baseline

1. Run the Shamela normalizer on the fixture.
2. Manually verify EVERY field of the output against the source.
3. Save the verified output as the gold baseline JSON file.
4. Record who verified it and when.

Gold baselines are NOT auto-generated. They represent human-verified truth.
