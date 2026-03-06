Trace a piece of data through the pipeline to verify consistency.

Usage: Provide a source_id or describe the test data.

Steps:
1. Read `reference/PIPELINE_TRACE.md` for the reference trace format.
2. Starting from the source engine output, trace through each engine boundary:
   source → normalization → passaging → atomization → excerpting → taxonomy → synthesis
3. At each boundary, verify: the producing engine's output matches the consuming engine's input.
4. Track metadata accumulation (D-023): list all metadata fields at each stage.
5. Report any metadata loss, type mismatches, or missing required fields.

This command is for design verification (checking SPECs) before implementation,
and for runtime verification (checking actual data) during/after implementation.
