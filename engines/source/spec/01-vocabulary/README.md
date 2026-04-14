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
- `integrity_status`: the source-engine verdict on structural validity and corruption risk at the container level.
- `normalization handoff bundle`: the package emitted by the source engine for normalization to consume.

Naming rules:

- `upload` means owner submission, not accepted source.
- `accepted source` means accepted by the source engine, not by later engines.
- `work identity` and `source identity` are distinct and must never share one field.
