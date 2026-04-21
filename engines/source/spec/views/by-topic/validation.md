# Source Spec Atoms by Topic: validation

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0012 | constraint | Error severity taxonomy | confirmed | high |

### CON-SRC-0012 — Error severity taxonomy
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Established on 2026-04-21 per Phase 5b item 13 closing Codex CLI's Phase 5a reviewer-wave finding S7 ("schema enum {fatal, blocking, warning} has no operational definition anywhere"). The JSON Schema at engines/source/spec/schema.json $defs/severity pins the three permitted values but provides no semantic guidance. With 75+ behavior.error_conditions severity assignments across the atom corpus (24 fatal, 21 blocking, 30 warning as of this atom's creation date), the absence of operational semantics means each atom author has been free to interpret the values differently, silently corrupting the pipeline's error-recovery contract. This atom fixes the semantics once and authoritatively.
- Rule: Every behavior.error_conditions[].severity value in any source- engine spec atom carries a defined operational semantic. "fatal" means unrecoverable data corruption — the condition indicates that scholarly metadata or primary text has been damaged in a way that cannot be reconstructed from the inputs available to the pipeline, and no downstream engine may proceed with the affected record. "blocking" means recoverable rejection — the condition prevents the current operation from completing but a specific correction path exists (owner resubmits with a valid override, upstream re-emits missing evidence, transient dependency recovers). "warning" means advisory — the condition is logged and the operation continues; suitable for observability signals that must not halt the pipeline. These three values are mutually exclusive and collectively exhaustive for the severity enum.
