"""Registry management (SPEC §3, §4.A.2 Step 7).

Atomic writes via write-ahead log pattern:
1. Write pending_registration_{source_id}.json
2. Apply changes to each registry
3. Delete pending file

Startup: check for orphaned pending files → complete or rollback.
"""
