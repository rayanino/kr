# Overnight Codex Report — 2026-03-30

- Status: **STOPPED**
- Apply mode: `queue_only`
- Launch head: `049e167b`
- Tasks: 3 completed, 4 failed, 1 queued, 0 skipped

## Launch Notes
- Main repo was dirty at launch; auto-apply disabled.

## Completed
- `ki-layer-merge-excerpting`: Probe excerpting layer merge logic for structural attribution bugs
- `review-recent-excerpting`: Review recent committed excerpting changes
- `val-contracts`: Validate cross-engine contracts and metadata flow

## Queued Patches
- `ki-text-integrity-excerpting`: Probe excerpting writer for byte-preservation regressions -> `overnight_codex/queue/ki-text-integrity-excerpting.patch` (launch policy is queue_only)

## Issues
- `harden-recent-excerpting` (failed): Guarded task touched files outside allowlist: ['engines/excerpting/contracts.py']; pytest failed for excerpting: .py:226: in test_mismatched_count_accepted
    result = EnrichmentResult.model_validate(data)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for EnrichmentResult
E     Value error, total_units 5 != len(enrichments) 1 [type=value_error, input_value={'enrichments': [{'unit_i...one}], 'total_units': 5}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.12/v/value_error
=========================== short test summary info ===========================
FAILED engines/excerpting/tests/test_pydantic_robustness.py::TestEnrichmentResultMismatch::test_mismatched_count_accepted
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 698 passed in 66.60s (0:01:06)

- `creative-innovation-local_architecture_challenge-excerpting` (failed): Failed to create worktree for creative-innovation-local_architecture_challenge-excerpting: Preparing worktree (new branch 'overnight-codex-creative-innovation-local_architecture_challenge-excerpting-1774851809')
Updating files:   4% (571/12861)
Updating files:   5% (644/12861)
Updating files:   6% (772/12861)
Updating files:   7% (901/12861)
Updating files:   8% (1029/12861)
Updating files:   9% (1158/12861)
Updating files:  10% (1287/12861)
Updating files:  11% (1415/12861)
Updating fi
- `creative-innovation-local_cost_efficiency-excerpting` (failed): Failed to create worktree for creative-innovation-local_cost_efficiency-excerpting: Preparing worktree (new branch 'overnight-codex-creative-innovation-local_cost_efficiency-excerpting-1774851817')
Updating files:  12% (1667/12861)
Updating files:  13% (1672/12861)
Updating files:  13% (1774/12861)
Updating files:  14% (1801/12861)
Updating files:  14% (1844/12861)
Updating files:  14% (1915/12861)
Updating files:  15% (1930/12861)
Updating files:  15% (1988/12861)
Updating files
- `creative-innovation-local_failure_mode_review-excerpting` (failed): Failed to create worktree for creative-innovation-local_failure_mode_review-excerpting: Preparing worktree (new branch 'overnight-codex-creative-innovation-local_failure_mode_review-excerpting-1774851832')
Updating files:  10% (1410/12861)
Updating files:  11% (1415/12861)
Updating files:  12% (1544/12861)
Updating files:  13% (1672/12861)
Updating files:  14% (1801/12861)
Updating files:  15% (1930/12861)
Updating files:  16% (2058/12861)
Updating files:  17% (2187/12861)
Updating f
