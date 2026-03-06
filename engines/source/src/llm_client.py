"""LLM Client Abstraction — SPEC §6, §4.A.4

Wraps Anthropic and OpenAI APIs for metadata inference and consensus.
- Single-call: infer(prompt, system) → response
- Consensus: consensus_infer(prompt, system) → (response, agreement, details)

Configured via SourceEngineConfig: model providers, API keys, timeouts.
"""
