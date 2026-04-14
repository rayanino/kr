# OwnerSubmissionRiskCase

Owned by:

- `60-source-admission-and-normalization-handoff`

Purpose:

- Preserve any source-engine warning that the owner may have submitted something materially misleading for study, even if the source remains readable.

Core fields:

- `gate_status`
- `risk_flags`
- `risk_summary`
- `owner_ack_required`
- `recommended_owner_action`
- `notes_from_owner`

Rules:

- This gate is for owner-submission risk only, not for metadata disagreement resolution.
- A live gate blocks official source-collection admission and normalization handoff until owner acknowledgment is recorded.
