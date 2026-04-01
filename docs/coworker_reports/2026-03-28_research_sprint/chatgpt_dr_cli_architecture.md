# Deep research on D-H002 Four-Tool CLI Architecture

## Ground truth from your repo decision D-H002

Decision D-H002 (“Four-Tool CLI Architecture”) establishes a four-provider, role-specialized routing table for your autonomous bug-hunting factory, with deterministic severity classification occurring **before** LLM review and then dispatching to different tools by severity. fileciteturn3file0L1-L1

In D-H002, your factory’s stated intent is to (a) keep the “builder” and “reviewers” on different providers, (b) reserve scarce / expensive reasoning for HIGH+, and (c) keep LOW/MEDIUM high-throughput and cheap. fileciteturn3file0L1-L1

The decision’s routing table (as written) assigns:
- Builder/fixer: Claude Code (Opus 4.6) fileciteturn3file0L1-L1  
- LOW/MEDIUM reviewer: Copilot CLI with GPT-4.1 fileciteturn3file0L1-L1  
- HIGH scholarly reviewer: Codex CLI on a frontier model fileciteturn3file0L1-L1  
- HIGH+ adversarial challenger: Gemini CLI (Gemini 3 Pro) fileciteturn3file0L1-L1  
- CRITICAL escalation: Copilot CLI with Claude Opus 4.5 at a higher multiplier tier fileciteturn3file0L1-L1  

This context matters for your questions because it makes GPT‑4.1’s role explicitly **bounded**: it’s not responsible for HIGH+/scholarly adjudication, but for “edge cases, missing validation, formatting” (your description) and, per D-H003, “edge case handling, defensive code, missing validation” = MEDIUM and “logging, naming, formatting, dead code” = LOW. fileciteturn3file0L1-L1

## GPT-4.1 via Copilot CLI for LOW/MEDIUM review

### Capability fit for routine review

On raw coding capability, GPT‑4.1 is widely characterized (by its publisher) as a strong coding model: OpenAI reports GPT‑4.1 scoring **54.6% on SWE-bench Verified** and highlights improvements in “making fewer extraneous edits” and “following diff formats reliably,” among other engineering-relevant behaviors. citeturn17view0

While SWE-bench is not “code review,” it is evidence of repository-scale software engineering competence under constraints similar to your factory’s environment (multi-file context, tool usage, test-driven completion). citeturn17view0 A routine reviewer for LOW/MEDIUM findings mainly needs (a) basic bug-spotting, (b) validation/rule completeness thinking, (c) reading diffs carefully, and (d) consistent formatting/structure recommendations—abilities that overlap heavily with “instruction following” and “diff reliability.” citeturn17view0

From a Copilot economics standpoint, GitHub’s billing model explicitly treats GPT‑4.1 as an “included model” with **multiplier 0** on paid plans and Copilot Student, which is consistent with your design intent of “use it heavily for bulk review.” citeturn18view0

### Where GPT-4.1 is “strong enough” vs where it’s risky

For the concrete LOW/MEDIUM classes you listed (formatting, missing validation, defensive checks, edge-case coverage), GPT‑4.1 is generally “strong enough” **if** you constrain the work into an auditable checklist and—critically—pair it with deterministic checks (unit tests, property checks, linters) as the primary correctness oracle. The D-H004 direction to integrate property-based testing and mutation testing is aligned with this philosophy (LLM suggests; tests decide). fileciteturn3file0L1-L1

The higher-risk failure mode is not that GPT‑4.1 is “weak,” but that routine review often devolves into **style commentary** unless the prompt forces: (1) explicit “expected vs observed,” (2) minimum reproducible conditions, (3) concrete invariant name, and (4) a patch-level recommendation. The reliability of any reviewer model rises sharply when you (a) pass it the failing test output or invariant violation text and (b) require structured output (see orchestration section). citeturn17view0turn11view0turn12view0

### Recommendation specific to your routing table

Keeping GPT‑4.1 for LOW/MEDIUM is defensible and consistent with D-H002’s “spend frontier review only on HIGH+” allocation. fileciteturn3file0L1-L1 The most robust way to raise assurance without “upgrading the routine reviewer” is to add a **small, systematic audit lane**:

- Sample (for example) 5–10% of LOW/MEDIUM findings nightly and send them to your HIGH+ panel (Codex + Gemini) as a *canary* check, then measure disagreement types. This preserves your cost profile while validating that GPT‑4.1 isn’t systematically under-detecting a recurring class of bug. (This is an architectural control, not a model swap.) fileciteturn3file0L1-L1
- Auto-escalate any LOW/MEDIUM case when GPT‑4.1 outputs uncertainty or when the underlying deterministic checks indicate non-local risk (e.g., touching validation boundaries affecting CRITICAL fields per your deterministic severity rules). fileciteturn3file0L1-L1

## WSL2 invoking Windows-installed CLIs

### Can WSL2 run Windows executables?

Yes: Microsoft’s WSL documentation states that WSL can run Windows tools directly from a Linux shell by invoking `[tool-name].exe`, and that these processes behave much like native Linux executables with support for piping/redirection/backgrounding. citeturn3view0

This interop can be enabled/disabled per distribution via `/etc/wsl.conf` under `[interop]`, including whether Windows PATH entries are appended into WSL’s `$PATH`. citeturn4view0 At the implementation level, WSL interop uses a binfmt handler and a Linux-side `/init` entrypoint to create Windows processes via an interop server bridge. citeturn2search7

### Do the CLIs need to be installed inside WSL2?

Strictly speaking: no—if interop is enabled and the Windows executables are reachable (via appended Windows PATH or explicit paths), WSL2 can invoke them. citeturn3view0turn4view0

Practically: for at least one of your four tools, installing inside WSL is often the “least surprising” route. OpenAI’s Codex CLI documentation states that Codex “officially supports macOS and Linux” and that “Windows support is experimental and may require WSL.” citeturn15search1 If you want to minimize interop edge cases, running Codex CLI as a Linux tool *inside* WSL aligns with its official support stance. citeturn15search1

### Known issues and gotchas that matter for your factory

File placement and performance: Microsoft recommends storing project files in the WSL filesystem when working from a Linux command line for best performance (rather than working on `/mnt/c/...`). citeturn3view0 If your orchestrator runs in Ubuntu-on-WSL2 and your repo sits under `/home/...`, but you invoke Windows-side CLIs, you can end up with cross-filesystem access patterns that are slower and sometimes path-confusing. citeturn3view0

Path semantics: Microsoft notes that “parameters are passed to the Windows binary unmodified,” and demonstrates Windows tools expecting Windows-style paths like `C:\temp\foo.txt`. citeturn3view0 This is one of the most common sources of “works manually, fails under automation”: your Python orchestrator running on Linux tends to produce Linux paths; Windows CLIs may interpret them literally unless you translate them. citeturn3view0 WSLENV exists specifically to help translate environment variables (including path lists) between WSL and Windows execution contexts. citeturn3view0

Interop configuration drift: if `[interop] enabled=false` or `appendWindowsPath=false` is set (intentionally or accidentally), Windows tool invocation from WSL will stop working, and the failure mode often looks like “command not found.” citeturn4view0

A tool-specific point for Codex CLI: if your workflow depends on integration tests that call external services, OpenAI’s Codex CLI documentation warns that network can be disabled during execution (and that tests calling external services can fail). citeturn15search2 This typically shows up as “flaky only in agent mode” unless sandbox/network settings are standardized in your orchestration. citeturn15search2

## Orchestrating four CLI agents from Python with less fragility

Your pain points (“output parsing, error handling, timeout management”) are the classic failure modes of shelling out. The best 2026 pattern is not “stop using subprocesses,” but: **stop depending on human-readable output and stop treating processes as opaque.**

### Prefer machine-readable outputs and streaming event protocols

Three of your four tool families now document explicit structured output modes suitable for automation:

- Copilot CLI supports `--output-format=json`, producing JSONL (“one JSON object per line”), and supports `--prompt` (`-p`) to run programmatically and exit; `--silent` helps isolate just model output without usage statistics. citeturn11view0  
- Claude Code supports `--print` (`-p`) plus `--output-format` (`text`, `json`, `stream-json`), plus `--input-format` stream options; it also supports `--json-schema` to request validated JSON matching a JSON Schema, and a `--max-budget-usd` guardrail for print-mode runs. citeturn12view0  
- Gemini CLI headless mode supports explicit JSON output with a documented schema including a `response` plus `stats` containing per-model usage metrics, and it documents stable exit codes for automation workflows. citeturn13search7turn13search6  

Codex also has an official direction toward programmatic integration beyond “run a command and parse text”: OpenAI describes the Codex App Server as a bidirectional JSON-RPC API used across Codex surfaces, and explicitly calls out “Codex Exec” as a scriptable CLI mode intended for automation/pipelines with structured output and clear success/failure signaling. citeturn15search5

Net effect: you can unify your orchestrator around an internal “AgentResult” schema that every tool must produce (or be converted into), making subprocess boundaries far less fragile. citeturn11view0turn12view0turn13search7turn15search5

### Use structured concurrency + cancellation semantics rather than ad hoc timeouts

At the Python runtime level in 2026, the standard library provides async subprocess primitives (`asyncio.create_subprocess_exec` / `.communicate()`), and `asyncio.timeout()` gives a first-class timeout context manager that converts cancellation into a `TimeoutError`. citeturn2search5turn2search8

If you want a higher-level, cross-backend abstraction (and more disciplined cancellation), AnyIO provides task groups and explicit timeout/cancel-scope semantics and also includes subprocess helpers (`run_process()` / `open_process()`). citeturn2search1turn6search9

A concrete “subprocess but less fragile” pattern that’s directly targeted at your problem is Prefect’s `prefect.utilities.processutils`, which wraps AnyIO process handling with features like: Windows command joining support, termination on exception during yield, and forced cleanup during cancellation. citeturn6search21

### What “better than subprocess” realistically means for your system

There are two legitimate upgrades beyond subprocess calls:

- For Codex specifically, consider integrating via the Codex App Server JSON-RPC interface (where feasible), which is explicitly designed for “client-friendly, bidirectional” control and avoids TTY/process edge cases. citeturn15search5  
- For the broader four-tool design, the best “next layer up” is a workflow engine when you care about crash recovery, pause/resume, and durable retries (which autonomous nightly hunting workflows often do). Temporal’s public positioning is exactly this: workflows capture state at each step and can resume after failure, and activities have built-in retry/timeout patterns. citeturn8search6turn7search9  

This typically doesn’t replace your orchestrator; it replaces the most failure-prone parts: long-running state machines, retry loops, and ad hoc persistence of “what step did we reach?” citeturn8search6turn7search9

## Quota and usage tracking across four providers

### There is no single “unified quota interface,” but you can unify telemetry

Each provider’s “quota unit” is different (monthly premium-request allowances, daily request caps, API token spend, or subscription-based gating), so you usually need per-provider accounting. citeturn18view0turn1search0turn1search9turn15search2turn14search6

However, you can centralize *how you measure and react* by unifying on a shared telemetry model:
- **request count**, **tokens in/out**, **latency**, **error class**, **selected model**, and an internal **“severity budget”** per provider.

This is increasingly practical because multiple CLIs now expose usage telemetry directly.

### GitHub Copilot

GitHub’s billing docs clarify that for Copilot Student and paid plans, GPT‑4.1 is an included model with multiplier **0** and thus does not consume premium requests (while other models may). citeturn18view0 The same document describes Copilot CLI prompts as consuming premium requests (with multipliers depending on model) and notes counters reset monthly and do not roll over. citeturn18view2

For “approaching limits,” GitHub’s monitoring guidance emphasizes viewing usage in IDEs or in billing settings and notes notifications when you reach the limit; it also describes downloading usage reports and budgeting alerts for overages (where supported). citeturn1search0

For programmatic tracking inside your orchestrator, Copilot CLI’s own “OpenTelemetry monitoring” section documents span attributes including `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, and Copilot-specific fields like `github.copilot.cost` and `github.copilot.aiu` (“AI units consumed”). citeturn11view3 This is unusually useful: it lets your factory estimate consumption and “degrade gracefully” based on *actual measured usage* rather than guessing by prompt size. citeturn11view3

### Gemini CLI

Gemini CLI’s documented license limits include **1500 model requests per user per day** (and per-minute limits) for a standard edition. citeturn1search9 In headless mode, Gemini CLI can return JSON including usage statistics broken down by model, which can feed directly into your quota ledger. citeturn13search6turn13search7

Gemini CLI also documents an OpenTelemetry-based observability system with configuration via settings and environment variables (e.g., enabling/disabling telemetry). citeturn13search10 This suggests a clean convergence path: export Copilot + Gemini telemetry to the same backend, and compute “remaining daily budget” centrally. citeturn11view3turn13search10

### Codex CLI and OpenAI usage

Your D-H002 writeup frames Codex CLI quotas in terms of a “messages per 5hr window” for a frontier model. fileciteturn3file0L1-L1 Official Codex CLI documentation, however, describes authentication via API keys, and the “Sign in with ChatGPT” flow creates an API key and uses promotional API credits for Plus/Pro users (rather than describing ChatGPT-style message windows as the compute unit). citeturn15search2

If your Codex CLI usage is API-key-backed (as the official flow describes), your most robust quota tracking is: (a) rely on OpenAI API rate-limit headers for “remaining requests/tokens,” and (b) enforce internal budgets by tracking tokens/cost per call and reacting before you hit organizational usage limits. citeturn14search6turn15search2

### Claude Code / Anthropic

Claude Code exposes automation-friendly output modes (`json`, `stream-json`) and additionally provides a `--max-budget-usd` guardrail in print mode—this is directly relevant to “degrade gracefully when approaching limits,” because it lets you cap spend per invocation even before you build full provider-side usage polling. citeturn12view0

### A practical quota-tracking strategy for your factory

Given the above, the “best” approach is a layered design:

- A unified internal **Usage Ledger** (append-only) keyed by (provider, model, run_id, finding_id), storing: request counts, token counts (when available), latency, errors, and any cost fields the CLI emits. citeturn11view3turn13search6turn14search6turn12view0  
- Per-provider “quota adapters” that map ledger entries into provider quota units: Copilot premium requests / multipliers, Gemini daily request caps, OpenAI API RPM/TPM and monthly spend, and Claude Code per-run budget caps. citeturn18view0turn1search9turn14search6turn12view0  
- A policy layer that implements the graceful degradation you intended in D-H002 (“route work away from constrained tools”): e.g., skip HIGH+ adversarial challenge when Gemini daily cap is tight; or route borderline HIGH to only one reviewer when OpenAI budget is tight; or force LOW/MEDIUM to GPT‑4.1/“0× included” models when Copilot premium requests are scarce. citeturn3file0L1-L1turn18view0