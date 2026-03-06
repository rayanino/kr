"""Trustworthiness Evaluation — SPEC §4.A.8

Five weighted factors:
- author_standing (0.30)
- tahqiq_quality (0.25)
- publisher_reputation (0.15)
- source_authority (0.15)
- text_fidelity (0.15)

Combined >= 0.65 → verified. < 0.65 → flagged.
Conservative bias: uncertain → flagged (§7.4).
Special cases: owner-authored → verified; Quran/canonical hadith → verified.
"""
