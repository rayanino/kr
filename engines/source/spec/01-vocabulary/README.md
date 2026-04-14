# 01 Vocabulary

Canonical terms:

- `submission`: the owner-provided upload event.
- `raw upload registry`: tracks every submission, including rejected ones.
- `source collection`: tracks only officially accepted sources after source-engine completion.
- `source`: the frozen uploaded artifact as handled by the source engine.
- `work`: the bibliographic work the uploaded source is believed to represent.
- `edition`: a specific realization of a work.
- `container classification`: the structural type of the frozen artifact, such as single HTML, multi-volume HTML, PDF, or plain text.
- `intake dossier`: the evidence bundle produced by intake analysis before final metadata deliberation.
- `completeness_status`: the source-engine verdict on complete, partial, mixed, or indeterminate upload completeness.
- `self_containment_assessment`: the source-engine verdict on whether the uploaded material is usable on its own without losing essential context from missing parts.
- `cross_volume_dependency_assessment`: the source-engine verdict on how strongly the uploaded material depends on absent volumes or surrounding material.
- `integrity_status`: the source-engine verdict on structural validity and corruption risk at the container level.
- `study_quality_risk_flag`: any uncertainty that could materially affect study quality.
- `owner_submission_risk_gate`: a source-engine gate for likely mistaken, incomplete, misleading, or risky submissions from the owner. This is distinct from metadata disagreement handling.
- `normalization handoff bundle`: the package emitted by the source engine for normalization to consume.

Naming rules:

- `upload` means owner submission, not accepted source.
- `accepted source` means accepted by the source engine, not by later engines.
- `work identity` and `source identity` are distinct and must never share one field.
