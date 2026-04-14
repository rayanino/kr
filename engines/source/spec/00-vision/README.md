# 00 Vision

Purpose:

- Define why the source engine exists.
- Define what the source engine owns and what it explicitly does not own.
- Define success criteria for the front of the KR pipeline.

Core ownership:

- Accept uploaded materials.
- Freeze them immutably.
- Classify the uploaded container.
- Analyze what was uploaded as a source candidate.
- Deliberate source metadata and admission inside the source-engine boundary.
- Package a downstream normalization handoff without doing normalization itself.

Explicit non-ownership:

- Text extraction from PDFs.
- OCR execution.
- HTML parsing into normalized content.
- Any downstream normalized text production.

Clarification:

- The source engine may sample already-present PDF text layers for diagnostic intake analysis. That diagnostic sampling is allowed because it measures container integrity and routing risk. It is not normalization extraction and must never be emitted as normalized text.

Success criteria:

- The source engine can say what was uploaded, what container it is, what source/work it most likely is, whether it is complete or partial, whether it is structurally valid, and whether it should enter the official source collection.
- The handoff to normalization preserves all upstream intake evidence needed downstream.
