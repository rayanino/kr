# Ready-to-paste prompt for new chat session

Paste this as your first message in a new Claude Chat session:

---

Excerpting engine triage fixes are applied (commit 619b4ec8, 551 tests passing). This is a new chat for the formal 3-pass review.

Session start protocol:
1. Clone the repo
2. Read NEXT.md
3. git log --oneline -5
4. Read the handoff at reference/archive/sessions/handoff_triage_to_review.md — it has the complete review plan, file list, probe instructions, and CC audit prompt
5. Read reference/protocols/REVIEW_PROTOCOL.md and reference/protocols/QUALITY_AXIOM.md
6. Scan ls /mnt/skills/user/ and pick all relevant skills

Start Round 1 (Structural): read the full diff (git diff aac490fe..619b4ec8), read all 4 source files and 3 test files in full, run tests, verify each of the 14 fixes was implemented per NEXT.md spec, cross-engine boundary check, SPEC cross-reference for §7.4 and §8.1.

End Round 1 with findings. I'll say "continue" for Round 2.
