"""Format-specific atomization strategies (SPEC §4.A.7).

Each strategy adapts atom boundary rules and LLM prompts for a specific
passage structural_format value. The strategy selection router in
prescreen.py maps structural_format → strategy module.
"""
