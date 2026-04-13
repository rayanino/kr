You are a structural code reviewer for the KR excerpting engine. Review the DR40 relationship links implementation for correctness, edge cases, and contract integrity.

BRANCH: excerpting-foundations-hardening-20260404

FILES TO READ (in order):

1. engines/excerpting/contracts.py
   - Lines 79-89: RelationshipType enum (3 values)
   - Lines 418-435: UnitRelationship model
   - Lines 469-474: TeachingUnit.related_units field
   - Lines 592-596: ExcerptRecord.related_units field
   - Lines 1183-1196: I-TU-10 validation

2. engines/excerpting/src/phase3_deterministic.py
   - Lines 174-219: _reindex_related_units function
   - Lines 383-386: subviable exemption (new DR40 change)
   - Lines 295-308: merge_micro_units related_units propagation
   - Lines 460-466: merge_subviable_units related_units propagation

3. engines/excerpting/tests/test_phase3_deterministic.py
   - test_related_units_preserved_despite_subviable
   - test_evidence_split_units_preserved_despite_subviable

REVIEW QUESTIONS:

Q1 — _reindex_related_units edge cases: The function remaps target_unit_index after merges. Check these scenarios:
   (a) What happens when two units with related_units links pointing to each other are BOTH absorbed into the same target? Do the links become self-referential?
   (b) What happens when a chain A→B→C exists and B is absorbed? Does A's link correctly update to C's new index?
   (c) Is the dedup logic correct — does it handle the case where two different relationships to the same target exist (e.g., companion_definition AND evidence_for)?

Q2 — Merge propagation: Both merge_micro_units (line 308) and merge_subviable_units propagation concatenate related_units from micro and target. After concatenation, _reindex_related_units runs. Verify: are there cases where the concatenation creates invalid state BEFORE reindexing catches it?

Q3 — I-TU-10 validation gaps: The validator checks target_unit_index exists and is not self-referential. Missing checks to look for:
   (a) Orphaned links — unit A links to unit B, but B has no reciprocal link back. Is this valid or a bug?
   (b) Relationship type consistency — if A has evidence_for→B, should B have evidence_for→A or is one-way valid?
   (c) Cross-chunk links — can target_unit_index accidentally point to a unit in a different chunk?

Q4 — Subviable + isnad interaction: Line 383-386 now has three conditions: word_count < 25 AND NOT isnad AND NOT related_units. Verify: can a unit have BOTH an isnad marker AND related_units? If so, does the exemption logic handle it correctly (either condition should preserve the unit)?

OUTPUT FORMAT:
For each question, provide:
- VERDICT: PASS (no issues) / ISSUE (describe the bug) / EDGE_CASE (theoretically possible but unlikely)
- EVIDENCE: specific line numbers and code paths
- FIX: if ISSUE, provide the exact code change needed

Do NOT review: Arabic text accuracy, scholarly convention correctness, prompt quality, SPEC compliance, or test coverage breadth. Focus exclusively on structural/contract correctness.
