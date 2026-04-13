# Session 5 Test Plan

## Testing Dimensions

### 5a Deterministic Tests (no LLM, no network)

These tests verify pure logic: scoring algorithms, threshold behavior, validation checks, registry CRUD, atomic write safety, config loading.

**Scholar Authority (shared/scholar_authority/tests/test_scholar_authority.py):**

1. `test_lookup_exact_match` — Exact canonical_name_ar match → auto_link, score 1.0
2. `test_lookup_known_as_match` — Match via known_as → auto_link
3. `test_lookup_name_variant_match` — Match via name_variants → auto_link
4. `test_lookup_short_vs_long_name_a3_1` — "النووي" vs full name → score >= 0.85 → auto_link (A3-1 fix)
5. `test_lookup_ambiguous_name_gates` — "ابن حجر" without death date → 0.50-0.85 → human_gate
6. `test_lookup_disambiguated_by_death_date` — "ابن حجر" + death_date 852 → auto_link to al-Asqalani
7. `test_lookup_no_match` — Completely different name → < 0.50 → new_record
8. `test_lookup_empty_registry` — Empty registry → new_record
9. `test_register_assigns_sequential_id` — First register → sch_00001, second → sch_00002
10. `test_register_validates_pydantic` — Invalid record → validation error
11. `test_register_requires_canonical_name` — Empty canonical_name_ar → error
12. `test_update_appends_sources_encountered` — New source_id added to list
13. `test_update_death_date_drift_gates` — Existing 769, proposed 780 (diff > 5) → gate
14. `test_update_death_date_small_diff_ok` — Existing 769, proposed 772 (diff ≤ 5) → ok
15. `test_update_school_change_gates` — Changing school affiliation → gate
16. `test_update_name_change_blocked` — Modifying canonical_name_ar → blocked, added to known_as
17. `test_update_self_reference_rejected` — Adding self as teacher → rejected
18. `test_update_temporal_inconsistency_gates` — Teacher death > student death + 30 → gate
19. `test_update_preserves_revision_history` — Old values saved in revision_history
20. `test_record_completeness_calculation` — Verify 24-field fraction calculation

**Trust Evaluator (engines/source/tests/test_trust_evaluator.py):**

21. `test_fixture_01_verified` — Classical, no muhaqiq → verified (ground truth)
22. `test_fixture_03_flagged` — Modern, no muhaqiq → flagged
23. `test_fixture_11_verified` — Classical + muhaqiq → verified
24. `test_fixture_12_flagged` — Modern, non-scholarly → flagged
25. `test_all_13_fixtures_match_ground_truth` — Parametrized test over all 13
26. `test_author_standing_classical` — death ≤ 1000 + known → 0.90
27. `test_author_standing_unknown` — New record → 0.30
28. `test_tahqiq_recognized_muhaqiq` — Name in config → 0.90
29. `test_tahqiq_no_muhaqiq_modern` — Modern, no muhaqiq → 0.30
30. `test_publisher_known_with_variant` — "دار التراث - القاهرة" matches "دار التراث" → 0.75
31. `test_publisher_unknown` — Unknown publisher → 0.40
32. `test_critical_low_flag` — author < 0.30 AND muhaqiq < 0.40 → flagged regardless
33. `test_threshold_boundary` — Score exactly 0.65 → verified; 0.649 → flagged

**Validation (engines/source/tests/test_validation.py):**

34. `test_schema_valid_passes` — Valid SourceMetadata dict → no errors
35. `test_schema_missing_required_field` — Missing source_id → fatal
36. `test_referential_integrity_author_missing` — author.canonical_id not in scholars → fatal
37. `test_referential_integrity_work_missing` — work_id not in works → fatal
38. `test_confidence_below_block_threshold` — genre confidence 0.40 → gate
39. `test_confidence_above_block_ok` — genre confidence 0.60 → no gate
40. `test_consistency_nazm_verse` — genre=nazm + format=prose → warning
41. `test_consistency_sharh_commentary_ok` — genre=sharh + format=commentary → ok
42. `test_consistency_sharh_prose_ok` — genre=sharh + format=prose → ok (running prose valid)
43. `test_consistency_hashiyah_not_beginner` — hashiyah + level=beginner → warning
44. `test_consistency_author_science_mismatch_gates` — author known for nahw, scope=fiqh → gate
45. `test_consistency_genre_multi_layer_autocorrect` — sharh + is_multi_layer=false → auto-correct to true
46. `test_multi_layer_true_empty_layers_gates` — is_multi_layer=true + empty layers → gate
47. `test_multi_layer_false_has_layers_autocorrect` — is_multi_layer=false + layers present → auto-correct
48. `test_layer_author_ref_missing_fatal` — TextLayer author not in scholars → fatal
49. `test_d023_passthrough_field_deleted` — Enrichment deletes existing field → fatal
50. `test_d023_passthrough_field_added_ok` — Enrichment adds new field → ok

**Human Gate (shared/human_gate/tests/test_human_gate.py):**

51. `test_create_checkpoint_persists` — Checkpoint appears in pending file
52. `test_create_checkpoint_auto_approve` — Auto-approve mode sets status=auto_approved
53. `test_resolve_approve_moves_to_resolved` — Approved checkpoint moved from pending/ to resolved/
54. `test_resolve_reject_marks_rejected` — Rejected checkpoint has status=rejected
55. `test_get_pending_filters_by_source` — Only returns checkpoints for given source_id
56. `test_get_pending_count` — Accurate count across all sources
57. `test_index_updated_on_create` — index.json maps checkpoint_id → source_id
58. `test_batching_multiple_checkpoints_per_source` — Multiple gates for one source in same file

**Registries (engines/source/tests/test_registries.py):**

59. `test_register_source_creates_all_three_entries` — source, work, scholar entries created
60. `test_register_source_writes_metadata_json` — metadata.json written to library/sources/{source_id}/
61. `test_register_source_pending_file_lifecycle` — pending file created, then deleted after success
62. `test_orphaned_registration_recovery` — Interrupted registration recovered on startup
63. `test_work_relationship_edge_created` — Genre chain → WorkRelationshipEdge
64. `test_placeholder_work_created` — Referenced work not in library → placeholder created
65. `test_atomic_write_survives_crash` — Simulated crash after .bak → registry recoverable

**Config (engines/source/tests/test_config.py):**

66. `test_load_all_config_files` — All 4 config files loaded correctly
67. `test_missing_config_file_defaults` — Missing file → empty default
68. `test_malformed_json_raises` — Bad JSON → clear error
69. `test_arabic_text_preserved` — Muhaqiq names with diacritics survive round-trip
70. `test_publisher_variants_loaded` — Variants list populated correctly

### 5b LLM-Worker Tests (use mocked LLM responses)

None for Session 5. Trust evaluator, validation, registries, and human gate are all deterministic. The LLM calls happen in Session 3's consensus module.

### 5c Integration Tests

71. `test_full_pipeline_fixture_01_trust` — Run extraction + inference (mocked) + trust → verified
72. `test_full_pipeline_fixture_03_trust` — Run extraction + inference (mocked) + trust → flagged
73. `test_validation_blocks_write_on_fatal` — Pipeline stops when validation returns fatal
74. `test_human_gate_created_on_ambiguous_author` — Pipeline creates gate checkpoint

## Fixtures

All 13 existing fixtures are used for trust evaluation testing. The test constructs SourceMetadata-like dicts from extraction output + GROUND_TRUTH.json expected values, bypassing LLM inference (which was tested in Session 3).

## Test File Locations

```
shared/scholar_authority/tests/test_scholar_authority.py  (tests 1-20)
shared/human_gate/tests/test_human_gate.py               (tests 51-58)
engines/source/tests/test_trust_evaluator.py              (tests 21-33)
engines/source/tests/test_validation.py                   (tests 34-50)
engines/source/tests/test_registries.py                   (tests 59-65)
engines/source/tests/test_config.py                       (tests 66-70)
engines/source/tests/test_integration_session5.py         (tests 71-74)
```
