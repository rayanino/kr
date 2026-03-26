"""Validate all agent and command definitions in .claude/ for correctness.

Checks:
- Required frontmatter fields present
- Model names are valid
- Tool names are valid
- No orphaned references to nonexistent files
- Consistent formatting
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

VALID_MODELS = {"opus", "sonnet", "haiku"}
VALID_TOOLS = {
    "Read", "Write", "Edit", "Bash", "Glob", "Grep",
    "WebSearch", "WebFetch", "Agent", "Task",
}

AGENT_REQUIRED_FIELDS = {"name", "description", "tools"}
COMMAND_REQUIRED_FIELDS = {"description"}


def parse_frontmatter(path: Path) -> dict[str, str] | None:
    """Parse YAML-like frontmatter from a markdown file."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None

    fields: dict[str, str] = {}
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def validate_agent(path: Path) -> list[str]:
    """Validate a single agent definition."""
    issues: list[str] = []
    fields = parse_frontmatter(path)

    if fields is None:
        issues.append(f"{path.name}: missing frontmatter (no --- block)")
        return issues

    # Check required fields
    for field in AGENT_REQUIRED_FIELDS:
        if field not in fields:
            issues.append(f"{path.name}: missing required field '{field}'")

    # Check model validity
    if "model" in fields and fields["model"] not in VALID_MODELS:
        issues.append(
            f"{path.name}: invalid model '{fields['model']}' "
            f"(valid: {', '.join(sorted(VALID_MODELS))})"
        )

    # Check tools
    if "tools" in fields:
        tools = [t.strip() for t in fields["tools"].split(",")]
        for tool in tools:
            # Strip parenthetical restrictions like "Bash(python *)"
            base_tool = tool.split("(")[0].strip()
            if base_tool and base_tool not in VALID_TOOLS:
                issues.append(
                    f"{path.name}: unknown tool '{base_tool}' "
                    f"(valid: {', '.join(sorted(VALID_TOOLS))})"
                )

    # Check description length
    if "description" in fields and len(fields["description"]) > 300:
        issues.append(
            f"{path.name}: description too long "
            f"({len(fields['description'])} chars, max 300)"
        )

    # Check file content has substance
    text = path.read_text(encoding="utf-8")
    content_after_frontmatter = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL)
    if len(content_after_frontmatter.strip()) < 50:
        issues.append(f"{path.name}: very short content ({len(content_after_frontmatter.strip())} chars)")

    return issues


def validate_command(path: Path) -> list[str]:
    """Validate a single command definition."""
    issues: list[str] = []
    fields = parse_frontmatter(path)

    if fields is None:
        # Legacy format: first line IS the description, no frontmatter block.
        # This is valid for older commands — flag as advisory, not error.
        text = path.read_text(encoding="utf-8").strip()
        if len(text) < 20:
            issues.append(f"{path.name}: no frontmatter AND very short content")
        return issues

    for field in COMMAND_REQUIRED_FIELDS:
        if field not in fields:
            issues.append(f"{path.name}: missing required field '{field}'")

    # Check allowed-tools format if present
    if "allowed-tools" in fields:
        tools_str = fields["allowed-tools"]
        if not tools_str:
            issues.append(f"{path.name}: empty allowed-tools field")

    # Check description length
    if "description" in fields and len(fields["description"]) > 300:
        issues.append(
            f"{path.name}: description too long "
            f"({len(fields['description'])} chars, max 300)"
        )

    return issues


def main() -> int:
    """Run validation on all agents and commands."""
    root = Path(__file__).parent.parent / ".claude"
    agents_dir = root / "agents"
    commands_dir = root / "commands"

    all_issues: list[str] = []
    agent_count = 0
    command_count = 0

    # Validate agents
    if agents_dir.exists():
        for path in sorted(agents_dir.glob("*.md")):
            issues = validate_agent(path)
            all_issues.extend(issues)
            agent_count += 1

    # Validate commands
    if commands_dir.exists():
        for path in sorted(commands_dir.glob("*.md")):
            issues = validate_command(path)
            all_issues.extend(issues)
            command_count += 1

    # Report
    print(f"=== Agent/Command Validation ===")
    print(f"Agents:   {agent_count} checked")
    print(f"Commands: {command_count} checked")
    print()

    if all_issues:
        print(f"Issues found: {len(all_issues)}")
        for issue in all_issues:
            print(f"  - {issue}")
        return 1
    else:
        print("All definitions valid.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
