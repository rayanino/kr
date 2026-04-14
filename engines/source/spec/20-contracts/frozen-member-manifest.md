# FrozenMemberManifest

Owned by:

- `20-freeze-and-manifest`

Purpose:

- Preserve the immutable member inventory of the frozen artifact.

Per-member fields:

- `member_name`
- `member_kind`
- `member_size_bytes`
- `member_sha256`

Rules:

- The manifest is built from frozen members, not from later normalized outputs.
- Downstream steps may read it but must not rewrite it.
