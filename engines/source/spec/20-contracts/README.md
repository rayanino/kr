# 20 Contracts

Purpose:

- Define the structured records emitted and consumed by the source engine.

Core contract surfaces:

- `RawUploadRecord`
- `FrozenMemberManifest`
- `ContainerClassification`
- `IntakeDossier`
- `SourceMetadata`
- `NormalizationInput`
- `NormalizationHandoffBundle`

Rules:

- Contracts define shapes and field meanings, not step behavior.
- A field belongs here only if another step or engine must rely on its exact shape.
