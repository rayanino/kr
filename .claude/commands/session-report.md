Generate a session feedback report comparing plan predictions with actual deliverables.

Arguments: $ARGUMENTS should be `<plan_file> <engine_name>`

Example: `/session-report .claude/plans/my-plan.md normalization`

Steps:
1. Run: `python3 scripts/session_feedback_report.py $ARGUMENTS`
2. Review the generated report for significant prediction misses (>50% delta)
3. Summarize key calibration insights for future plans (test count multipliers, line estimates)
4. If code reviewer output is available, categorize findings by severity (HIGH/MEDIUM/LOW)
