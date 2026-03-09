---
globs: ["**/*"]
---
## Session Discipline for KR Autonomous Development

- **One engine per session.** Start fresh context for each engine, each SPEC section, each implementation block. Cross-engine work causes context pollution.
- **After any compaction:** immediately re-read the active engine's `CLAUDE.md` AND the relevant `SPEC_CORE.md` section being implemented. Compacted context loses D-023 metadata semantics, Arabic handling nuances, and specific behavioral rules.
- **Before implementing:** always read the SPEC section being implemented from the file, not from memory. SPEC rules are precise — paraphrased versions introduce subtle errors.
- **Use `/smart-compact` proactively** when context exceeds ~60% rather than waiting for auto-compaction at 80%. Controlled compaction preserves more critical context.
- **Use `/catchup` at session start** to reload context from git + NEXT.md rather than relying on any prior conversational state.
- **Compaction-fragile items** that MUST be re-verified after any compaction:
  - D-023 metadata pass-through semantics (never delete upstream fields)
  - Arabic text handling rules (diacritics, normalization, encoding)
  - Enum values and their precise definitions (Genre, StructuralFormat, etc.)
  - Multi-model consensus requirements (D-041 — never single LLM for content decisions)
