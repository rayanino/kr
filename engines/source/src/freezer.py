"""Source Freezing — SPEC §4.A.2 Step 6

1. Compute staging hash for each file
2. Copy to library/sources/{source_id}/frozen/
3. Compute frozen hash, verify matches staging hash
4. Set read-only (chmod 0444)
5. Move staging to .processed/

Errors:
- SRC_FREEZE_COPY_CORRUPT: staging hash != frozen hash
- SRC_FREEZE_PERMISSION_FAILED: cannot chmod
- SRC_STAGING_MODIFIED: TOCTOU detection via timestamp comparison

Staging lock: .kr_processing lock file between format detection and freezing.
"""
