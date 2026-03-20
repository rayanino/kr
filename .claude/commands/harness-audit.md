---
description: Validate .claude/ configuration for internal consistency. Finds orphaned hooks, missing frontmatter, broken references, and other config drift.
allowed-tools: Bash(python *), Bash(python3 *)
---
Run the harness audit script and report findings:

```bash
python3 scripts/audit_claude_config.py
```

If issues are found, review each one and recommend fixes:
- **ORPHAN** findings: suggest registering the file in settings.json or removing it.
- **MISSING** findings: suggest creating the missing file or fixing the reference.
- **FRONTMATTER** findings: suggest adding the required fields to the agent definition.
- **REF** findings: suggest updating the path reference or removing the stale reference.
- **SKILL** findings: suggest adding a SKILL.md or restructuring the directory.
