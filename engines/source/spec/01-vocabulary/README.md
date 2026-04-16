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
- `edition_group`: the bibliographic realization of a work as produced by a specific publisher and muhaqqiq. Formalizes the existing `matched_edition_group_id` concept. An edition group has an expected volume count and an edition fingerprint (publisher + muhaqqiq + distinguishing signals).
- `edition_holding`: the library's official record of what it holds for a specific edition group. This is the mutable entity that tracks progressive completeness as volumes arrive. An edition holding has a lifecycle state (draft, active_partial, active_complete, active_mixed, superseded, archived) and a coherence state. Sources attach to holdings; holdings evolve; sources remain immutable.
- `volume_holding`: the presence state of a specific volume within an edition holding. Values: missing, present_primary, present_alternate, conflict.
- `supersession`: a typed relationship between edition holdings where a newer or higher-quality holding replaces an older one as the preferred source for downstream processing. Supersession is pointer-based: the old holding retains its sources and downstream artifacts but is hidden from default discovery.
- `preferred_edition`: a pointer from a work to the edition holding that is the default for downstream processing and UI presentation.
- `reconciliation`: the process that runs on every source admission to create or update EditionGroup and EditionHolding entities based on work_output and collection_match_output from metadata deliberation.
- `edition_fingerprint`: the combination of publisher, muhaqqiq, and distinguishing signals (e.g., edition number, publication year) that uniquely identifies an edition group. Two sources share an edition fingerprint when their publisher and muhaqqiq match with high confidence.
- `coherence_state`: the edition-consistency assessment of an edition holding. Values: coherent (all volumes from same edition), mixed (volumes from different editions), unknown.

Naming rules:

- `upload` means owner submission, not accepted source.
- `accepted source` means accepted by the source engine, not by later engines.
- `work identity` and `source identity` are distinct and must never share one field.
