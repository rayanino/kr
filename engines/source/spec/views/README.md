# Source Spec Atom Overview

## Summary
| Metric | Value |
| --- | --- |
| Total atoms | 75 |

## By Type
| Type | Count |
| --- | --- |
| constraint | 5 |
| decision | 14 |
| feedback | 16 |
| invariant | 8 |
| question | 6 |
| requirement | 26 |

## By Status
| Status | Count |
| --- | --- |
| confirmed | 19 |
| deferred | 3 |
| draft | 2 |
| proposed | 49 |
| superseded | 2 |

## By Topic
| Topic | Count |
| --- | --- |
| acquisition | 10 |
| agent_ergonomics | 7 |
| consensus | 7 |
| freezing | 1 |
| handoff | 8 |
| identity | 2 |
| metadata | 30 |
| trust | 10 |

## Atom Index
| ID | Type | Layer | Step | Title | Status | Priority | Topic | File |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CON-SRC-0001 | constraint | contracts | — | Shamela HTML and PDF are production formats | confirmed | high | acquisition | 20-contracts/constraints/CON-SRC-0001.yaml |
| CON-SRC-0002 | constraint | contracts | — | Hadith literature dominates source-engine benchmark quality | confirmed | high | metadata | 20-contracts/constraints/CON-SRC-0002.yaml |
| CON-SRC-0003 | constraint | contracts | — | No existing pipeline contract is binding on the rebuild | confirmed | critical | handoff | 20-contracts/constraints/CON-SRC-0003.yaml |
| CON-SRC-0004 | constraint | contracts | — | Complete SourceMetadata output schema | proposed | critical | handoff | 20-contracts/constraints/CON-SRC-0004.yaml |
| CON-SRC-0005 | constraint | contracts | — | Normalization handoff bundle includes a bridge input contract | proposed | high | handoff | 20-contracts/constraints/CON-SRC-0005.yaml |
| DEC-SRC-0001 | decision | architecture | — | Owner hints are cross-validation, not primary data | proposed | critical | acquisition | 30-architecture/decisions/DEC-SRC-0001.yaml |
| DEC-SRC-0002 | decision | architecture | — | Science scope uses dynamic registry | proposed | high | metadata | 30-architecture/decisions/DEC-SRC-0002.yaml |
| DEC-SRC-0003 | decision | architecture | — | Level detection strategy | deferred | medium | metadata | 30-architecture/decisions/DEC-SRC-0003.yaml |
| DEC-SRC-0004 | decision | architecture | — | Replace trust algorithm with agent teams | proposed | critical | trust | 30-architecture/decisions/DEC-SRC-0004.yaml |
| DEC-SRC-0005 | decision | architecture | — | Muhaqiq standing is metadata only | proposed | high | trust | 30-architecture/decisions/DEC-SRC-0005.yaml |
| DEC-SRC-0006 | decision | architecture | — | Agents resolve disagreements autonomously | proposed | critical | consensus | 30-architecture/decisions/DEC-SRC-0006.yaml |
| DEC-SRC-0007 | decision | architecture | — | Disputed metadata as multi-position evidence | proposed | high | metadata | 30-architecture/decisions/DEC-SRC-0007.yaml |
| DEC-SRC-0008 | decision | architecture | — | Agent infrastructure is built within source-engine scope first | proposed | medium | agent_ergonomics | 30-architecture/decisions/DEC-SRC-0008.yaml |
| DEC-SRC-0009 | decision | architecture | — | Research strategy uses specialized sources | proposed | high | agent_ergonomics | 30-architecture/decisions/DEC-SRC-0009.yaml |
| DEC-SRC-0010 | decision | architecture | — | Source hints multi-layer routing and normalization confirms it | proposed | medium | metadata | 30-architecture/decisions/DEC-SRC-0010.yaml |
| DEC-SRC-0011 | decision | architecture | — | Agent self-resolution replaces human_gate | proposed | high | consensus | 30-architecture/decisions/DEC-SRC-0011.yaml |
| DEC-SRC-0012 | decision | architecture | — | Multi-position metadata ordered by confidence | proposed | high | metadata | 30-architecture/decisions/DEC-SRC-0012.yaml |
| DEC-SRC-0014 | decision | architecture | — | Separate raw-upload tracking from official source admission | proposed | critical | handoff | 30-architecture/decisions/DEC-SRC-0014.yaml |
| DEC-SRC-0015 | decision | architecture | — | Normalization consumes a bridge input model, not raw SourceMetadata | proposed | high | handoff | 30-architecture/decisions/DEC-SRC-0015.yaml |
| INV-SRC-0001 | invariant | quality | — | Owner hints never bias inference | proposed | critical | acquisition | 40-quality/invariants/INV-SRC-0001.yaml |
| INV-SRC-0002 | invariant | quality | — | Author attribution role separation is mandatory | proposed | critical | metadata | 40-quality/invariants/INV-SRC-0002.yaml |
| INV-SRC-0003 | invariant | quality | — | Library never refuses knowledge | proposed | critical | metadata | 40-quality/invariants/INV-SRC-0003.yaml |
| INV-SRC-0004 | invariant | quality | — | Truth-seeking over consensus-forcing | proposed | high | consensus | 40-quality/invariants/INV-SRC-0004.yaml |
| INV-SRC-0005 | invariant | quality | — | Muhaqiq never gates trust decisions | proposed | high | trust | 40-quality/invariants/INV-SRC-0005.yaml |
| INV-SRC-0006 | invariant | quality | — | Isnad atomic preservation | proposed | high | metadata | 40-quality/invariants/INV-SRC-0006.yaml |
| INV-SRC-0007 | invariant | quality | — | Scholar registry minimum population | proposed | critical | metadata | 40-quality/invariants/INV-SRC-0007.yaml |
| INV-SRC-0008 | invariant | quality | — | PDF-derived text is never silently trusted at source handoff | proposed | critical | trust | 40-quality/invariants/INV-SRC-0008.yaml |
| OF-SRC-0001 | feedback | evidence | — | Collection unchanged for source intake | confirmed | high | acquisition | 60-evidence/owner-feedback/OF-SRC-0001.yaml |
| OF-SRC-0002 | feedback | evidence | — | Drop-and-go intake with optional hints | confirmed | critical | acquisition | 60-evidence/owner-feedback/OF-SRC-0002.yaml |
| OF-SRC-0003 | feedback | evidence | — | Minimize owner review load | confirmed | critical | trust | 60-evidence/owner-feedback/OF-SRC-0003.yaml |
| OF-SRC-0004 | feedback | evidence | — | Author attribution errors are catastrophic | confirmed | critical | metadata | 60-evidence/owner-feedback/OF-SRC-0004.yaml |
| OF-SRC-0005 | feedback | evidence | — | Science hints follow the same cross-validation rule | confirmed | high | metadata | 60-evidence/owner-feedback/OF-SRC-0005.yaml |
| OF-SRC-0006 | feedback | evidence | — | Science registry must keep growing | confirmed | high | metadata | 60-evidence/owner-feedback/OF-SRC-0006.yaml |
| OF-SRC-0007 | feedback | evidence | — | Preserve and infer level metadata from content | confirmed | medium | metadata | 60-evidence/owner-feedback/OF-SRC-0007.yaml |
| OF-SRC-0008 | feedback | evidence | — | Multi-layer detection ownership is unresolved | confirmed | medium | metadata | 60-evidence/owner-feedback/OF-SRC-0008.yaml |
| OF-SRC-0009 | feedback | evidence | — | Replace numeric trust scoring with agent teams | confirmed | critical | trust | 60-evidence/owner-feedback/OF-SRC-0009.yaml |
| OF-SRC-0010 | feedback | evidence | — | Muhaqiq standing is informational only | confirmed | high | trust | 60-evidence/owner-feedback/OF-SRC-0010.yaml |
| OF-SRC-0011 | feedback | evidence | — | Agents resolve disagreements without human gate | confirmed | critical | consensus | 60-evidence/owner-feedback/OF-SRC-0011.yaml |
| OF-SRC-0012 | feedback | evidence | — | Hadith classification is the primary benchmark surface | confirmed | high | metadata | 60-evidence/owner-feedback/OF-SRC-0012.yaml |
| OF-SRC-0013 | feedback | evidence | — | Disagreement may itself be the true answer | confirmed | high | consensus | 60-evidence/owner-feedback/OF-SRC-0013.yaml |
| OF-SRC-0014 | feedback | evidence | — | Legacy contracts do not cap the rebuild | confirmed | critical | handoff | 60-evidence/owner-feedback/OF-SRC-0014.yaml |
| OF-SRC-0015 | feedback | evidence | — | Build source-engine teams inside the source-engine scope first | confirmed | medium | handoff | 60-evidence/owner-feedback/OF-SRC-0015.yaml |
| OF-SRC-0016 | feedback | evidence | — | Research must use specialized source channels | confirmed | high | agent_ergonomics | 60-evidence/owner-feedback/OF-SRC-0016.yaml |
| OQ-SRC-0001 | question | questions | — | Level detection ownership | deferred | medium | metadata | 50-questions/OQ-SRC-0001.yaml |
| OQ-SRC-0003 | question | questions | — | Agent-team architecture design | draft | critical | agent_ergonomics | 50-questions/OQ-SRC-0003.yaml |
| OQ-SRC-0004 | question | questions | — | Formal replacement for human_gate | superseded | high | consensus | 50-questions/OQ-SRC-0004.yaml |
| OQ-SRC-0005 | question | questions | — | Agent monitoring scope | deferred | medium | agent_ergonomics | 50-questions/OQ-SRC-0005.yaml |
| OQ-SRC-0006 | question | questions | — | Ordering and display semantics for multi-position metadata | superseded | high | metadata | 50-questions/OQ-SRC-0006.yaml |
| OQ-SRC-0007 | question | questions | — | Specialized research source inventory | draft | medium | agent_ergonomics | 50-questions/OQ-SRC-0007.yaml |
| REQ-SRC-0001 | requirement | pipeline | upload_receipt | Upload receipt and raw submission registration | proposed | critical | acquisition | 10-pipeline/10-upload-receipt/REQ-SRC-0001.yaml |
| REQ-SRC-0002 | requirement | pipeline | metadata_deliberation | Optional owner hints as cross-validation | proposed | high | acquisition | 10-pipeline/50-metadata-deliberation/REQ-SRC-0002.yaml |
| REQ-SRC-0003 | requirement | pipeline | metadata_deliberation | Metadata deliberation stays owner-light | proposed | critical | trust | 10-pipeline/50-metadata-deliberation/REQ-SRC-0003.yaml |
| REQ-SRC-0004 | requirement | pipeline | metadata_deliberation | Multi-model consensus for author attribution | proposed | critical | metadata | 10-pipeline/50-metadata-deliberation/REQ-SRC-0004.yaml |
| REQ-SRC-0005 | requirement | pipeline | metadata_deliberation | Optional science hint | proposed | medium | metadata | 10-pipeline/50-metadata-deliberation/REQ-SRC-0005.yaml |
| REQ-SRC-0006 | requirement | pipeline | metadata_deliberation | Growable science registry without owner gate | proposed | high | metadata | 10-pipeline/50-metadata-deliberation/REQ-SRC-0006.yaml |
| REQ-SRC-0007 | requirement | pipeline | source_admission_and_normalization_handoff | Level field preservation across source-engine handoff | proposed | medium | metadata | 10-pipeline/60-source-admission-and-normalization-handoff/REQ-SRC-0007.yaml |
| REQ-SRC-0008 | requirement | pipeline | metadata_deliberation | Agent-team trust evaluation | proposed | critical | trust | 10-pipeline/50-metadata-deliberation/REQ-SRC-0008.yaml |
| REQ-SRC-0009 | requirement | pipeline | metadata_deliberation | Agent self-resolution of disagreements | proposed | critical | consensus | 10-pipeline/50-metadata-deliberation/REQ-SRC-0009.yaml |
| REQ-SRC-0010 | requirement | pipeline | metadata_deliberation | Graduated muhaqiq standing | proposed | medium | metadata | 10-pipeline/50-metadata-deliberation/REQ-SRC-0010.yaml |
| REQ-SRC-0011 | requirement | pipeline | metadata_deliberation | Fine-grained hadith classification | proposed | high | metadata | 10-pipeline/50-metadata-deliberation/REQ-SRC-0011.yaml |
| REQ-SRC-0012 | requirement | pipeline | metadata_deliberation | Multi-position metadata for disputed fields | proposed | high | metadata | 10-pipeline/50-metadata-deliberation/REQ-SRC-0012.yaml |
| REQ-SRC-0013 | requirement | pipeline | metadata_deliberation | Specialized research agents | proposed | high | agent_ergonomics | 10-pipeline/50-metadata-deliberation/REQ-SRC-0013.yaml |
| REQ-SRC-0014 | requirement | pipeline | metadata_deliberation | Copyist and author disambiguation | proposed | critical | metadata | 10-pipeline/50-metadata-deliberation/REQ-SRC-0014.yaml |
| REQ-SRC-0015 | requirement | pipeline | metadata_deliberation | Honorific-aware name matching | proposed | high | metadata | 10-pipeline/50-metadata-deliberation/REQ-SRC-0015.yaml |
| REQ-SRC-0016 | requirement | pipeline | metadata_deliberation | Multi-science assignment | proposed | high | metadata | 10-pipeline/50-metadata-deliberation/REQ-SRC-0016.yaml |
| REQ-SRC-0017 | requirement | pipeline | container_classification | Multipart Shamela container classification | proposed | critical | acquisition | 10-pipeline/30-container-classification/REQ-SRC-0017.yaml |
| REQ-SRC-0018 | requirement | pipeline | freeze_and_manifest | Freeze and manifest verification | proposed | critical | freezing | 10-pipeline/20-freeze-and-manifest/REQ-SRC-0018.yaml |
| REQ-SRC-0019 | requirement | pipeline | intake_analysis | Intake dossier and source-work identification | proposed | critical | identity | 10-pipeline/40-intake-analysis/REQ-SRC-0019.yaml |
| REQ-SRC-0020 | requirement | pipeline | container_classification | Plain text container classification | proposed | medium | acquisition | 10-pipeline/30-container-classification/REQ-SRC-0020.yaml |
| REQ-SRC-0021 | requirement | pipeline | intake_analysis | PDF intake analysis and text-layer quality classification | proposed | critical | acquisition | 10-pipeline/40-intake-analysis/REQ-SRC-0021.yaml |
| REQ-SRC-0022 | requirement | pipeline | source_admission_and_normalization_handoff | PDF handoff preserves intake verdicts | proposed | critical | trust | 10-pipeline/60-source-admission-and-normalization-handoff/REQ-SRC-0022.yaml |
| REQ-SRC-0023 | requirement | pipeline | intake_analysis | PDF text-layer evidence is diagnostic only | proposed | critical | metadata | 10-pipeline/40-intake-analysis/REQ-SRC-0023.yaml |
| REQ-SRC-0024 | requirement | pipeline | intake_analysis | PDF page-geometry hints for normalization | proposed | high | metadata | 10-pipeline/40-intake-analysis/REQ-SRC-0024.yaml |
| REQ-SRC-0025 | requirement | pipeline | source_admission_and_normalization_handoff | Two-stage source admission and normalization handoff packaging | proposed | critical | handoff | 10-pipeline/60-source-admission-and-normalization-handoff/REQ-SRC-0025.yaml |
| REQ-SRC-0026 | requirement | pipeline | metadata_deliberation | Authoritative work identity and collection linkage output | proposed | critical | identity | 10-pipeline/50-metadata-deliberation/REQ-SRC-0026.yaml |
