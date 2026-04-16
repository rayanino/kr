# Source Spec Atoms by Step: container_classification

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| REQ-SRC-0017 | requirement | Multipart Shamela container classification | confirmed | critical |
| REQ-SRC-0020 | requirement | Plain text container classification | confirmed | medium |
| REQ-SRC-0041 | requirement | Format-agnostic multi-volume folder classification | confirmed | critical |

### REQ-SRC-0017 — Multipart Shamela container classification
- Type: requirement
- Layer: pipeline
- Step: container_classification
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-001 and tightened on 2026-04-14 to distinguish container classification from freezing and later metadata deliberation.
- Trigger: Container classification receives a frozen directory candidate whose members include .htm files.
- Postconditions:
  - container_classification.container_type is set to shamela_multi_volume_html when the manifest contains at least two numbered .htm members.
  - container_classification.container_type is set to multipart_with_supplementary when the manifest contains one or more numbered .htm members plus supplementary non-numbered .htm members.
  - container_classification.volume_manifest preserves numbered HTML members in integer-stem order.
  - container_classification.supplementary_members preserves non-numbered HTML members separately from numbered volumes.
  - container_classification.normalization_route is set to html_parse_primary.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/11_multi_small; When container classification executes; Then container_classification.container_type="shamela_multi_volume_html", len(container_classification.volume_manifest)=3, and container_classification.normalization_route="html_parse_primary"..
  - AC-2 [deterministic] Given A frozen directory manifest containing only appendix.htm and introduction.htm; When container classification executes; Then Classification aborts with error_code=SRC-E-EMPTY-DIRECTORY..
  - AC-3 [deterministic] Given A frozen directory manifest containing 001.htm and المقدمة.htm; When container classification executes; Then container_classification.container_type="multipart_with_supplementary", container_classification.volume_manifest[0].member_name="001.htm", and container_classification.supplementary_members[0].member_name="المقدمة.htm"..

### REQ-SRC-0020 — Plain text container classification
- Type: requirement
- Layer: pipeline
- Step: container_classification
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Added from adversary-review.yaml ADV-011 and narrowed on 2026-04-14 so plain-text handling is classified and routed here, while later text interpretation belongs to later steps.
- Trigger: Container classification receives a frozen single-file candidate whose suffix is .txt.
- Postconditions:
  - container_classification.container_type is set to plain_text.
  - container_classification.normalization_route is set to plain_text_parse.
  - container_classification.text_encoding is set to utf-8.
  - intake analysis may later use the first non-empty line as title evidence, but that evidence is not finalized at this step.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/alfiyyah_versified/alfiyyah.txt; When container classification executes; Then container_classification.container_type="plain_text", container_classification.normalization_route="plain_text_parse", and container_classification.text_encoding="utf-8"..

### REQ-SRC-0041 — Format-agnostic multi-volume folder classification
- Type: requirement
- Layer: pipeline
- Step: container_classification
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner correction 2026-04-15 that multi-volume handling should be format-agnostic. Single file = single volume, folder with files = multi-volume, regardless of format. PDF and plain text multi-volume folders were not covered by REQ-SRC-0017 (Shamela-only) or REQ-SRC-0020/0021 (single-file only).
- Trigger: Container classification receives a frozen directory candidate whose members are not .htm files.
- Postconditions:
  - A folder containing multiple .pdf files is classified as container_type=pdf_multi_volume. volume_manifest preserves the PDF files in filename order. normalization_route=pdf_ocr_primary or pdf_text_primary based on per-file text-layer assessment in REQ-SRC-0021.
  - A folder containing multiple .txt files is classified as container_type=plain_text_multi_volume. volume_manifest preserves the text files in filename order. normalization_route=plain_text_parse.
  - A folder containing mixed file formats is classified as container_type=mixed_format_directory with a warning. Each member's format is recorded individually.
  - The format-agnostic principle: single file submission = single-volume source. Folder submission = multi-volume source. The format of the files inside determines the processing route, but the folder-as-multi-volume pattern is universal across all formats.
  - Concatenated multi-volume PDFs (single PDF with internal volume boundaries marked by ToC entries) are detected at intake analysis (REQ-SRC-0019/REQ-SRC-0038), not at container classification. Container classification sees them as a single PDF file.
- Acceptance criteria:
  - AC-1 [deterministic] Given A frozen directory containing 3 PDF files named vol1.pdf, vol2.pdf, vol3.pdf; When container classification executes; Then container_type="pdf_multi_volume" and len(volume_manifest)=3 and volume_manifest is ordered by filename..
  - AC-2 [deterministic] Given A frozen directory containing 2 .txt files; When container classification executes; Then container_type="plain_text_multi_volume" and normalization_route="plain_text_parse"..
  - AC-3 [deterministic] Given A single PDF file submitted (not a folder); When container classification executes; Then container_type="pdf" (single-volume, not pdf_multi_volume)..
