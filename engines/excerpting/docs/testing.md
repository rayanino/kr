# Test Infrastructure — Excerpting Engine

## Test File Structure

```
engines/excerpting/tests/
├── __init__.py
├── conftest.py                      # ✅ EXISTS (184 lines, 4 factories)
├── test_phase1_tree_walk.py         # §4.2: division tree walking + skip criteria
├── test_phase1_assembly.py          # §4.3: cross-page text joining
├── test_phase1_merge.py             # §4.4: tiny division merging
├── test_phase1_split.py             # §4.5: oversized division splitting
├── test_phase1_layers.py            # §4.6: text layer rebasing
├── test_phase1_metadata.py          # §4.7: flag aggregation, footnotes, renumbering
├── test_phase1_alignment.py         # §4.8: heading alignment filter
├── test_phase1_validation.py        # §4.9: V-P1-1 through V-P1-6
├── test_phase1_integration.py       # Full Phase 1 pipeline end-to-end
├── test_phase2_classify.py          # §5.2 + §5.4.1–2: classification + normalization
├── test_phase2_group.py             # §5.3 + §5.4.3: grouping + verification
├── test_phase3_deterministic.py     # §7.1: 9 deterministic fields
├── test_phase3_enrichment.py        # §7.2: LLM enrichment (mock LLM)
├── test_phase3_consensus.py         # §7.3: consensus + gates (mock LLM)
├── test_phase3_validation.py        # §7.4: V-P3-1 through V-P3-9
├── test_domain_rules.py             # §6: 22 domain rules
├── test_cross_engine.py             # §10.7: upstream/downstream contracts
├── test_adversarial.py              # §10.6: ADV-E-01 through ADV-E-12
└── fixtures/
    └── README.md                    # Fixture requirements (builder creates)
```

## Test Categories by File

### test_phase1_tree_walk.py — §4.2

| Test | SPEC Reference | What It Verifies |
|------|---------------|-----------------|
| test_leaf_identification | §4.2 | Recursive walk collects only leaf nodes (empty children) |
| test_heading_path | §4.2 | heading_path contains root-to-leaf heading_text values |
| test_skip_toc_division | §4.2 | All-TOC divisions skipped with reason code |
| test_skip_index_division | §4.2 | All-index divisions skipped |
| test_skip_blank_division | §4.2 | All-blank divisions skipped |
| test_skip_bibliography | §4.2 | مصادر/مراجع/فهرس headings skipped (word-boundary) |
| test_no_false_positive_masadir | §4.2 | "مصادر الأحكام" NOT skipped (keyword inside phrase) |
| test_skip_empty_range | §4.2 | start > end → EX-A-002, skip |
| test_volume_passthrough | §4.2 | Volume nodes are structural containers, not leaves |
| test_minimal_tree_c8 | §4.2 | <5 leaves after filter → handled by §4.5 |
| test_empty_tree | §4.2 | 0 leaves → EX-A-010, skip entire source |
| test_single_root | §4.2 | Single root with no children → one leaf = one chunk |

### test_phase1_assembly.py — §4.3

| Test | SPEC Reference | What It Verifies |
|------|---------------|-----------------|
| test_separator_mapping | §4.3 | Each boundary_continuity type maps to correct separator |
| test_mid_sentence_word_final | §4.3 | taa marbuta/alif maqsura/tanwin → space inserted |
| test_mid_sentence_connecting | §4.3 | Connecting letter → no separator (word continues) |
| test_skip_toc_in_range | §4.3 | TOC pages skipped during assembly, index recorded |
| test_diacritics_preserved | §4.3 | Arabic diacritics byte-for-byte identical after assembly |
| test_footnote_markers_preserved | §4.3 | ⌜N⌝ markers in text after assembly |
| test_join_points_recorded | §4.3 | JoinPoint per boundary with correct char_offset |
| test_null_boundary | §4.3 | null boundary_continuity → "\n" separator |
| test_constituent_unit_indices | §4.3 | All unit_indices in range recorded (including skipped) |

### test_phase1_merge.py — §4.4

| Test | SPEC Reference | What It Verifies |
|------|---------------|-----------------|
| test_merge_two_tiny | §4.4 | Adjacent <50-word siblings merged with "\n\n" separator |
| test_merge_chain | §4.4 | Recursive: three consecutive tiny → one chunk |
| test_size_guard | §4.4 | Merge blocked if combined > OVERSIZED_DIVISION_WORDS |
| test_only_child | §4.4 | No siblings → process as-is regardless of size |
| test_merge_history | §4.4 | I-AC-6: ≥2 entries, first = div_id |
| test_merge_keeps_div_path | §4.4 | Merged chunk has first division's div_path |
| test_i_ac_7_no_merge_split | §4.4 | Merge and split never both present (I-AC-7) |

### test_phase1_split.py — §4.5

| Test | SPEC Reference | What It Verifies |
|------|---------------|-----------------|
| test_split_at_heading | §4.5 | Heading marker → highest priority split point |
| test_split_at_section_break | §4.5 | Section break split when no heading markers |
| test_split_at_paragraph | §4.5 | Paragraph break nearest midpoint |
| test_split_at_sentence | §4.5 | Sentence boundary as last resort |
| test_recursive_split | §4.5 | 12000-word division → 3+ chunks |
| test_split_info_fields | §4.5 | chunk_id format, chunk_index, total_chunks, split_method |
| test_shared_unit_indices | §4.5 | I-AC-4: all chunks share constituent_unit_indices |
| test_layer_split_points | §4.5 | Layer segments divided at split point, recorded in metadata |
| test_footnote_assignment | §4.5 | Footnotes assigned to chunk containing their ⌜N⌝ marker |

### test_phase1_layers.py — §4.6

| Test | SPEC Reference | What It Verifies |
|------|---------------|-----------------|
| test_rebase_single_unit | §4.6 | No offset change for single-unit assembly |
| test_rebase_multi_unit | §4.6 | Cumulative offset includes separator lengths |
| test_merge_adjacent_segments | §4.6 | Same layer_type + author → merged after rebasing |
| test_coverage_invariant | §4.6 | I-AC-2: exact coverage [0, len) after rebasing |
| test_clamping | §4.6 | Segment overflow → clamped + EX-A-004 |
| test_gap_detection | §4.6 | Missing coverage → EX-A-003 |

### test_phase1_metadata.py — §4.7

| Test | SPEC Reference | What It Verifies |
|------|---------------|-----------------|
| test_or_aggregate_flags | §4.7 | Any unit with has_verse=true → chunk has_verse=true |
| test_footnote_dedup | §4.7 | Duplicate ref_marker → keep first, EX-A-005 |
| test_footnote_renumber | §4.7 | Colliding ⌜1⌝ markers → renumbered sequentially |
| test_renumber_updates_text | §4.7 | assembled_text markers updated when renumbering |
| test_renumber_map | §4.7 | old→new mapping in assembly_metadata |
| test_no_renumber_needed | §4.7 | No collisions → renumber_map is None |
| test_physical_pages_order | §4.7 | Pages collected in unit_index order |

### test_phase1_alignment.py — §4.8

| Test | SPEC Reference | What It Verifies |
|------|---------------|-----------------|
| test_aligned_heading | §4.8 | Heading found in first 200 stripped chars → true |
| test_misaligned_heading | §4.8 | Heading NOT found → false + EX-A-006 |
| test_noise_stripped | §4.8 | Diacritics/tatweel ignored in comparison |
| test_not_gate | §4.8 | Misaligned chunk still processed (quality flag only) |

### test_phase1_validation.py — §4.9

| Test | SPEC Reference | What It Verifies |
|------|---------------|-----------------|
| test_v_p1_1_coverage | V-P1-1 | Every leaf → chunk or skip. Missing = fatal. |
| test_v_p1_2_units | V-P1-2 | All content units accounted for. Missing = fatal. |
| test_v_p1_3_no_empty | V-P1-3 | word_count > 0 for all chunks. Warning. |
| test_v_p1_4_no_oversized | V-P1-4 | word_count ≤ OVERSIZED. Warning. |
| test_v_p1_5_layers | V-P1-5 | I-AC-2 for each chunk. Fatal. |
| test_v_p1_6_word_count | V-P1-6 | I-AC-1 for each chunk. Fatal. |

## Fixture Requirements

### Existing regression baselines (DO NOT modify):
- `experiments/architecture_test/divisions/` — 10 divisions from 5 genres
- `experiments/architecture_test/packages/` — NormalizedPackage data per fixture
- `experiments/format_diversity_test/fixtures/` — ibn_aqil (verse-commentary), taysir (prose)

### New fixtures to create (builder builds these in conftest.py):

| Fixture | Purpose | Arabic text source |
|---------|---------|-------------------|
| `_make_tiny_division_pair()` | Two <50-word divisions for merge testing | Extract from real Shamela export |
| `_make_oversized_division()` | >5000-word division for split testing | Concatenate real content units |
| `_make_multi_page_division()` | 5 content units with varied BC types | Real boundary_continuity values |
| `_make_empty_division()` | Division with start > end | Synthetic (structural test) |
| `_make_multi_layer_source()` | matn/sharh with layer boundaries | From ibn_aqil fixtures |
| `_make_footnoted_source()` | Footnotes spanning multiple units with ⌜N⌝ markers | Real Shamela footnotes |
| `_make_simple_package()` | Minimal valid NormalizedPackage (1 div, 2 units) | Synthetic Arabic text |

### conftest.py updates needed:

The existing conftest.py has 4 factories: `_make_assembled_chunk`, `_make_classified_segment`, `_make_teaching_unit`, `_make_excerpt_record`. Session 1 needs additional helpers:

- `_make_content_unit(**overrides)` — ContentUnit factory with sensible defaults
- `_make_division_node(**overrides)` — DivisionNode factory
- `_make_normalized_package(**overrides)` — NormalizedPackage with manifest + content_units
- `_make_division_tree(leaf_count, ...)` — Generate a tree with specified leaf count

These follow the exact pattern from normalization engine conftest.py.

## Test Conventions (from normalization engine)

1. **Factory helpers for all complex types.** Never construct ContentUnit or DivisionNode inline in tests — always use factories.
2. **Real Arabic text for domain tests.** Synthetic text only for structural tests (merge/split logic). Domain rule tests (§6) require authentic Shamela text.
3. **One assertion per test concept.** A test named `test_merge_two_tiny` tests exactly that scenario.
4. **Error code verification.** Each error code test checks: (a) code emitted, (b) message has context, (c) recovery per §8.2.
5. **Regression baselines frozen.** Never modify experiment output files. Tests compare against them.
6. **Catch drift: >200 new impl lines with <10 new tests = problem.**
