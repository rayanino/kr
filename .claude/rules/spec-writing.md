---
globs: ["engines/*/SPEC.md", "shared/*/SPEC.md"]
---
- Every behavioral rule in §4 must have at least one concrete testable example with real Arabic text.
- Every rule must be precise enough to write a function signature (inputs with types, output with type).
- Mark open questions explicitly as `[OPEN: ...]` — never embed uncertainty as if it were a decision.
- Cross-reference `reference/archive/VISION.md` sections as `(§N.N)` and decisions as `(D-NNN)`.
- After modifying any SPEC, run: `python3 scripts/check_spec_quality.py <path>`.
- Verify contract compatibility: upstream §3 (Output) must match this engine's §2 (Input).
- When deviating from a SPEC threshold, constant, or behavioral rule during implementation, document it as an L-XXX entry in the engine's `KNOWN_LIMITATIONS.md` with: (a) SPEC reference, (b) calibration data that justified the deviation, (c) affected range, (d) fix point. Silent deviations are the most dangerous class of error in this project.
