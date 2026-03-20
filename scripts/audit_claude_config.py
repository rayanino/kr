"""Validate .claude/ configuration for internal consistency.

Checks hook paths, agent frontmatter, command references, rule freshness,
skill structure, and orphaned files.

Usage:
    python scripts/audit_claude_config.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def find_project_root() -> Path:
    """Find project root by looking for .claude/ directory."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return cwd


def check_hook_paths(
    project: Path, settings: dict[str, object]
) -> tuple[list[str], set[str]]:
    """Verify every hook command path resolves to an existing file."""
    issues: list[str] = []
    hooks = settings.get("hooks", {})
    referenced_scripts: set[str] = set()

    if not isinstance(hooks, dict):
        return issues, referenced_scripts

    for event_type, hook_list in hooks.items():
        if not isinstance(hook_list, list):
            continue
        for hook_group in hook_list:
            if not isinstance(hook_group, dict):
                continue
            for hook in hook_group.get("hooks", []):
                if not isinstance(hook, dict):
                    continue
                cmd = hook.get("command", "")

                # Pattern: "$CLAUDE_PROJECT_DIR/path/to/file.sh"
                for match in re.findall(
                    r'\$CLAUDE_PROJECT_DIR/([^\s"\';&|]+\.sh)', cmd
                ):
                    referenced_scripts.add(match)
                    full_path = project / match
                    if not full_path.exists():
                        issues.append(
                            f"MISSING: Hook {event_type} references "
                            f"'{match}' but file does not exist"
                        )

                # Pattern: bash "$CLAUDE_PROJECT_DIR/path/to/file.sh"
                for match in re.findall(
                    r'bash\s+"?\$CLAUDE_PROJECT_DIR/([^\s"\';&|]+\.sh)', cmd
                ):
                    if match not in referenced_scripts:
                        referenced_scripts.add(match)
                        full_path = project / match
                        if not full_path.exists():
                            issues.append(
                                f"MISSING: Hook {event_type} references "
                                f"'{match}' but file does not exist"
                            )

    return issues, referenced_scripts


def check_orphaned_hooks(project: Path, referenced: set[str]) -> list[str]:
    """Find .sh files in .claude/hooks/ not referenced in settings.json."""
    issues: list[str] = []
    hooks_dir = project / ".claude" / "hooks"
    if not hooks_dir.is_dir():
        return issues

    for sh_file in sorted(hooks_dir.glob("*.sh")):
        relative = sh_file.relative_to(project).as_posix()
        if relative not in referenced:
            issues.append(
                f"ORPHAN: '{relative}' exists but is not referenced "
                f"in settings.json"
            )

    return issues


VALID_MODELS = {"opus", "sonnet", "haiku"}
REQUIRED_AGENT_FIELDS = {"name", "description", "tools"}


def check_agent_frontmatter(project: Path) -> list[str]:
    """Verify agent .md files have required frontmatter fields."""
    issues: list[str] = []
    agents_dir = project / ".claude" / "agents"
    if not agents_dir.is_dir():
        return issues

    for md_file in sorted(agents_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8", errors="ignore")

        if not content.startswith("---"):
            issues.append(
                f"FRONTMATTER: '{md_file.name}' missing YAML frontmatter"
            )
            continue

        end = content.find("---", 3)
        if end == -1:
            issues.append(
                f"FRONTMATTER: '{md_file.name}' has unclosed frontmatter"
            )
            continue

        frontmatter = content[3:end]
        fields_found: set[str] = set()
        model_value: str | None = None

        for line in frontmatter.strip().split("\n"):
            if ":" in line:
                key = line.split(":", 1)[0].strip()
                value = line.split(":", 1)[1].strip()
                fields_found.add(key)
                if key == "model":
                    model_value = value

        missing = REQUIRED_AGENT_FIELDS - fields_found
        if missing:
            issues.append(
                f"FRONTMATTER: '{md_file.name}' missing fields: "
                f"{', '.join(sorted(missing))}"
            )

        if model_value and model_value not in VALID_MODELS:
            issues.append(
                f"MODEL: '{md_file.name}' has model='{model_value}' "
                f"-- must be one of: {', '.join(sorted(VALID_MODELS))}"
            )

    return issues


def check_command_references(project: Path) -> list[str]:
    """Check that commands referencing scripts point to existing files."""
    issues: list[str] = []
    commands_dir = project / ".claude" / "commands"
    if not commands_dir.is_dir():
        return issues

    for md_file in sorted(commands_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8", errors="ignore")

        for match in re.findall(
            r"python[3]?\s+(scripts/[^\s`\"']+\.py)", content
        ):
            script_path = project / match
            if not script_path.exists():
                issues.append(
                    f"SCRIPT: Command '{md_file.name}' references "
                    f"'{match}' but file does not exist"
                )

    return issues


def check_rule_files(project: Path) -> list[str]:
    """Verify rule files are non-empty and path references resolve."""
    issues: list[str] = []
    rules_dir = project / ".claude" / "rules"
    if not rules_dir.is_dir():
        return issues

    for md_file in sorted(rules_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8", errors="ignore").strip()
        if not content:
            issues.append(f"EMPTY: Rule '{md_file.name}' is empty")
            continue

        # Check path references in backticks — only those that look
        # like actual file paths (contain / separator), not generic
        # filenames like `contracts.py` or `SPEC.md`.
        for match in re.findall(
            r"`([^`]{3,80})`", content
        ):
            # Must look like a file path with directory separator
            if "/" not in match:
                continue
            # Must end with a known extension
            if not re.search(r"\.(md|py|sh|json)$", match):
                continue
            # Skip URLs, variables, glob patterns, commands
            if match.startswith(("http", "$", "python", "pip")):
                continue
            if any(c in match for c in ("*", "{", "|", "&&", "=")):
                continue
            ref_path = project / match
            if not ref_path.exists():
                issues.append(
                    f"REF: Rule '{md_file.name}' references '{match}' "
                    f"but file does not exist"
                )

    return issues


def check_skill_structure(project: Path) -> list[str]:
    """Verify each skill directory has a SKILL.md."""
    issues: list[str] = []

    skills_dir = project / ".claude" / "skills"
    if skills_dir.is_dir():
        for subdir in sorted(skills_dir.iterdir()):
            if subdir.is_dir():
                if not (subdir / "SKILL.md").exists():
                    issues.append(
                        f"SKILL: '.claude/skills/{subdir.name}' "
                        f"has no SKILL.md"
                    )

    return issues


def main() -> int:
    project = find_project_root()
    settings_path = project / ".claude" / "settings.json"

    if not settings_path.exists():
        print("ERROR: .claude/settings.json not found")
        return 1

    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: Failed to parse settings.json: {e}")
        return 1

    print("=== KR Harness Audit ===\n")

    all_issues: list[str] = []

    # 1. Hook paths
    hook_issues, referenced_scripts = check_hook_paths(project, settings)
    all_issues.extend(hook_issues)

    # 2. Orphaned hooks
    all_issues.extend(check_orphaned_hooks(project, referenced_scripts))

    # 3. Agent frontmatter
    all_issues.extend(check_agent_frontmatter(project))

    # 4. Command references
    all_issues.extend(check_command_references(project))

    # 5. Rule files
    all_issues.extend(check_rule_files(project))

    # 6. Skill structure
    all_issues.extend(check_skill_structure(project))

    if all_issues:
        categories: dict[str, list[str]] = {}
        for issue in all_issues:
            cat = issue.split(":")[0]
            categories.setdefault(cat, []).append(issue)

        for cat, items in sorted(categories.items()):
            print(
                f"[{cat}] ({len(items)} issue{'s' if len(items) != 1 else ''})"
            )
            for item in items:
                print(f"  {item}")
            print()

        print(f"Total: {len(all_issues)} issue(s) found")
        return 1

    print("All clear -- no issues found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
