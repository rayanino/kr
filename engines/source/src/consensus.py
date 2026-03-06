"""Multi-Model Consensus — SPEC §6

Used for two decisions only:
1. Author identification → both models must agree on canonical_id
2. Work matching → both models must agree on work_id

If one model fails:
- Author ID: human gate (too high cascade risk)
- Work matching: accept single model + needs_review flag

Configuration: 2 models from different providers (e.g., Claude + GPT).
"""
