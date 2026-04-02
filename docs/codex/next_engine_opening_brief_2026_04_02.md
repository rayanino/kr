# Next Engine Opening Brief — 2026-04-02

Use this when the next serious engine-fix session opens.

## Do Not Start With

- another paid smoke/full run
- `taysir`-dependent owner-review tasks
- protected control-plane files

## Start Here

1. [smoke_api_v2_priority_findings_2026_04_02.md](/home/rayane/kr-codex/docs/codex/smoke_api_v2_priority_findings_2026_04_02.md)
2. [ex_v002_repair_map_2026_04_02.md](/home/rayane/kr-codex/docs/codex/ex_v002_repair_map_2026_04_02.md)
3. [ex_v002_drop_packet_2026_04_02.md](/home/rayane/kr-codex/docs/codex/ex_v002_drop_packet_2026_04_02.md)
4. [ex_c003_repair_map_2026_04_02.md](/home/rayane/kr-codex/docs/codex/ex_c003_repair_map_2026_04_02.md)
5. [ex_c003_phase2a_failure_packet_2026_04_02.md](/home/rayane/kr-codex/docs/codex/ex_c003_phase2a_failure_packet_2026_04_02.md)
6. [taysir_timeout_repair_map_2026_04_02.md](/home/rayane/kr-codex/docs/codex/taysir_timeout_repair_map_2026_04_02.md)
7. [taysir_scale_collapse_packet_2026_04_02.md](/home/rayane/kr-codex/docs/codex/taysir_scale_collapse_packet_2026_04_02.md)

## Execution Order

### Lane 1: `EX-V-002` post-grouping validation drops

Open first:

- `engines/excerpting/src/phase3_validation.py`
- `engines/excerpting/src/phase3_deterministic.py`
- `engines/excerpting/src/phase3_orchestrator.py`
- `engines/excerpting/tests/test_phase3_validation.py`
- `engines/excerpting/tests/test_state_machine_edge.py`

Question to answer:

- Are short structural units and slight snippet/prefix drift being dropped
  incorrectly at V-P3-2?

### Lane 2: `EX-C-003` Phase 2a chunk failures

Open first:

- `engines/excerpting/src/phase2_classify.py`
- `engines/excerpting/tests/test_phase2_classify.py`
- `engines/excerpting/tests/test_phase2_hardening.py`
- `engines/excerpting/tests/test_error_recovery.py`
- `tests/test_excerpting_integration_runners.py`

Question to answer:

- Which failures are true classification/anchor failures, and which are
  runner/resume bookkeeping inconsistencies?

### Lane 3: `taysir` timeout / incomplete finalization

Open first:

- `scripts/run_full_integration.py`
- `scripts/run_integration_test.py`
- `engines/excerpting/src/phase3_consensus.py`
- `docs/codex/taysir_timeout_analysis_2026_04_02.md`
- `docs/codex/taysir_verify_tail_analysis_2026_04_02.md`

Question to answer:

- What needs to change so a long-running package can either finish or at least
  land enough partial artifacts before timeout?

## Guardrails

- Keep using the WSL checkout.
- Keep the smoke-test budget protected; use the mock chunk-limit probe before
  any future paid run.
- Treat `.kr/HANDOFF.md` as stale on `L-001`; use
  `docs/codex/protected_state_divergence_2026_04_02.md` instead.
