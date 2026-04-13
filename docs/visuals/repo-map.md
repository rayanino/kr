# KR Repo Map

This table is a plain-language guide to the top level of the KR repository. It is meant to help the owner understand what kind of material lives where.

| Directory | What's in it | Who uses it |
| --- | --- | --- |
| `.agents` | Repo-local helper skills and agent setup files. | Engineering team |
| `.claude` | Claude-side tooling, hooks, commands, and local agent support files. | Engineering team |
| `.codex` | Codex-side config and hooks for this repo. | Engineering team |
| `.deepeval` | Evaluation tool support files. | System/tooling |
| `.git` | Git history and repository internals. | System/tooling |
| `.github` | GitHub workflows such as automation or checks. | Engineering team |
| `.kr` | KR control files: active frontier, handoff, decisions, and runtime state. | Engineering team |
| `.pytest_cache` | Temporary test cache files. | System/tooling |
| `.ruff_cache` | Temporary lint cache files. | System/tooling |
| `.serena` | Local tool memory and project metadata for one assistant workflow. | System/tooling |
| `batch2_gemini` | A workspace for one Gemini deep-research batch. | Engineering team |
| `docs` | Human-readable project docs, plans, reports, and now owner-facing visuals. | Owner and engineering team |
| `engines` | The seven pipeline engines that do the real library work. | Engineering team |
| `eval` | Evaluation helpers and notes for measuring output quality. | Engineering team |
| `experiments` | Short-lived architecture and format experiments used to test ideas before adopting them. | Engineering team |
| `integration_tests` | End-to-end test runs, smoke runs, review sessions, and comparison outputs. | Engineering team |
| `library` | The growing library surface itself: science trees, registries, logs, gates, and sources. | Owner and engineering team |
| `memory` | Saved event logs and memory records from assistant sessions. | System/tooling |
| `migration` | Scripts and checklists for moving or restoring environments. | Engineering team |
| `notes` | Raw working notes, owner ideas, and scratch text. | Engineering team |
| `output` | Generated output samples and test render artifacts. | Engineering team |
| `overnight` | Artifacts from one unattended run system. | Engineering team |
| `overnight_codex` | Codex unattended runtime files, logs, backlog, and autonomous support material. | Engineering team |
| `reference` | Deep reference material: architecture notes, reports, archived decisions, and scholarly guidance. | Engineering team |
| `results` | Stored analysis outputs and validation results. | Engineering team |
| `scripts` | Command-line scripts for running, checking, and analyzing the pipeline. | Engineering team |
| `shamela-export-samples` | Real sample book exports used to understand source formats. | Engineering team |
| `shared` | Shared building blocks used by more than one engine, such as validation, gates, and feedback. | Engineering team |
| `skills` | Reusable KR skills and templates. | Engineering team |
| `tests` | Test fixtures, integration tests, and evaluation support for proving the pipeline works. | Engineering team |
| `tools` | Practical utilities such as review, auditing, and comparison tools. | Owner and engineering team |

## Quick reading guide

- If the owner wants to understand the library itself, start with `library` and `docs`.
- If the owner wants to understand how the pipeline works, start with `docs/visuals`, `engines`, and `shared`.
- If the owner is reviewing results, the most useful places are usually `tools`, `integration_tests`, and `library`.
