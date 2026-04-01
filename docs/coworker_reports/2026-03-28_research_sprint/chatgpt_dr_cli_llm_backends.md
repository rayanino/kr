# CLI-Based LLM Backends for Multi-Stage Arabic Scholarly Text Pipelines

## Context from your repo and design intent

Your current pipeline architecture—multiple LLM calls for classification, enrichment, and cross-provider verification over Arabic Islamic scholarly texts—depends today on the entity["company","OpenRouter","llm api router"] API transport and Instructor-style structured outputs with validation-driven retries. fileciteturn11file0L1-L1

In the CLI-backed design you’re considering, the core operational shift is: instead of a “thin” HTTP client that can be fully controlled (sampling options, function/schema enforcement, retries) you would be spawning **agent-capable developer CLIs** (Codex / Claude Code / Gemini CLI) and relying on their headless modes + structured-output features (when available) to approximate what Instructor gives you. fileciteturn11file0L1-L1

Two repo artifacts matter most for schema-first automation:

- Your Pydantic contracts (what you ultimately want the model to emit as machine-validated JSON). fileciteturn12file0L1-L1  
- Your excerpting spec’s retry + consensus architecture (what you currently get “for free” from Instructor’s validation feedback loops and multi-provider reconciliation). fileciteturn13file0L1-L1  

Those two constraints dominate whether “CLI as backend” is viable without a large reliability regression.

## Codex exec as a verification backend

### Codex exec is not a thin wrapper around a single model call

OpenAI describes Codex CLI as a **local software agent** that runs an “agent loop” orchestrating model inference plus tool calls (e.g., shell commands) until it reaches a terminating assistant message. citeturn3view0 This is reinforced in OpenAI’s user-facing help docs: Codex CLI “acts as a lightweight coding agent” that can read, modify, and run code locally. citeturn2search1

The Codex CLI command reference makes this agentic nature concrete: it exposes flags for sandbox policy (`--sandbox`), approvals (`--ask-for-approval`), web search (`--search` / web_search config), and writing JSONL “events” (`--json`)—all signals that the backend is an agent harness, not just a “prompt → completion” wrapper. citeturn25view2turn7view2

**Conclusion:** `codex exec` behaves like a headless entrypoint into the Codex agent harness; it can include agentic turns and tool calls, depending on prompt + configuration, even if your intent is “pure verification.” citeturn3view0turn25view2

### What `--output-schema` actually does

OpenAI’s Codex cookbook explicitly shows using `codex exec ... --output-schema <schema.json>` for “structured outputs” workflows. citeturn2search0

In the Codex CLI options reference, `--output-schema` is documented as:

- A **JSON Schema file** describing the expected final response shape;  
- Codex validates against it as part of its workflow. citeturn7view0

This phrasing matters: it is described as **validation**, not as a guaranteed constrained decoding mode (the kind of “strict schema adherence” you might rely on in API-native structured outputs). citeturn7view0turn2search6

**Practical implication for verification calls:** the agent loop can still happen (tool calls, multi-turn), and the schema check is applied to the terminal output stage; you should assume you still need robust failure handling (retry / fallback / escalation) when validation fails. citeturn3view0turn7view0turn0search6

### Minimizing agent overhead for “text-in / structured-JSON-out” verification

You cannot fully “turn Codex into a raw model call” from `codex exec`, but you can materially reduce agentic surface area and nondeterminism:

**Run in a strict sandbox and stop interactive prompts**

- Use a read-only sandbox (`--sandbox read-only`) so even if a tool call is attempted it cannot mutate the workspace. citeturn7view2turn25view2  
- Set approvals for non-interactive execution (`--ask-for-approval never`) to prevent a headless pipeline hang on approval prompts. citeturn25view2  
- Prefer `--ephemeral` if you don’t want session rollout files persisted to disk (reduces state bleed between runs). citeturn7view2  

**Constrain contextual intake and tool availability**

- Run in a dedicated minimal working directory via `--cd` (limits what the agent can read as “project context”). citeturn25view2  
- If you rely on AGENTS.md-style project docs elsewhere, consider reducing or eliminating that ingestion here via config: `project_doc_max_bytes` controls how many bytes are read from `AGENTS.md` when building project instructions. citeturn14view0  
- Disable web search tools at the profile/config layer (`profiles.<name>.web_search = "disabled"` or related tool config), so Codex cannot introduce external facts or variability in a verification pass. citeturn13view1turn14view0  

**Use machine-readable outputs for observability and post-processing**

- Pair `--output-last-message` with `--json` if you want both: (a) structured event streams for auditing (tool calls, timing) and (b) a final artifact file for downstream parsing. citeturn7view2turn7view0  

**When “thin wrapper” behavior is truly required**

If your verification step must be *strictly* “no tools, no agent loop, fixed schema,” Codex CLI is structurally misaligned: it is built as an agent harness. OpenAI’s own guidance on “strict mode” schema adherence lives at the API layer (Structured Outputs strict mode / constrained sampling). citeturn2search6turn3view0  
In that case, the closest equivalent is calling the underlying model/API in a non-agent configuration rather than using `codex exec`. citeturn2search6turn25view2  

## Gemini CLI structured output support in March 2026

### What Gemini CLI currently guarantees

Gemini CLI’s “headless mode” (`gemini -p ... --output-format json`) produces a **fixed wrapper JSON object** with fields such as:

- `response` (string: the model’s natural-language answer),
- `stats` (usage + tools + models),
- `error` (optional). citeturn16search0turn16search6

This is **not** user-defined schema enforcement over the model’s payload; it is a stable CLI envelope for automation and telemetry. citeturn16search0turn16search6

### Evidence that user-provided JSON Schema enforcement is still missing

Multiple Gemini CLI issues explicitly request custom schemas and describe them as currently unsupported:

- Issue proposing a `--output-schema`-style flag for guaranteed JSON matching a user-provided schema (opened July 28, 2025; still open in the captured snapshot). citeturn16search4  
- Newer issue (Nov 19, 2025) stating Gemini CLI “currently supports only the built-in response schema format” documented in the headless docs, and “there is no way to define a custom structured output schema.” citeturn16search1turn16search0  

This aligns with the documentation: the only defined schema is the CLI’s envelope schema; the model content remains an **untyped string** under `response`. citeturn16search0turn16search6

### Known gotcha: “JSON output” vs “JSON in the response field”

A common automation failure mode is “I asked the model to output JSON, but the CLI wrapped it as a string (sometimes inside Markdown fences).” Gemini CLI has an issue where `--output-format json` still returns a JSON object, but the `response` value contained Markdown-fenced JSON (```json … ```), which breaks naive parsing. citeturn16search9

### Release evidence: JSON output improving, but no custom schema feature shipped

Recent Gemini CLI releases show ongoing investment in JSON output correctness/testing (“Optimize json-output tests with mock responses”), but do not indicate the introduction of user-provided output schemas in the release notes excerpt. citeturn26search1  
Together with the still-open feature requests above, the most evidence-supported conclusion is: **as of early 2026, Gemini CLI does not provide custom JSON-schema-enforced model outputs.** citeturn16search1turn16search4turn26search1

### Best alternative for schema enforcement: Gemini API / Python SDK

If you need “Instructor-like” schema enforcement for Gemini outputs, the most direct alternative is the official Google Gen AI SDK path:

- The Gemini API structured output docs instruct setting `response_mime_type="application/json"` and providing `response_json_schema` to generate JSON matching the schema (subset of JSON Schema). citeturn17search15  
- The `google-genai` (Python GenAI SDK) documentation shows `response_json_schema` accepting standard JSON Schema, and also shows `response_schema` accepting Pydantic models (SDK generates schemas). citeturn17search0turn17search1  

This is much closer to Instructor’s core value proposition (schema-first structured outputs) than Gemini CLI’s current headless JSON envelope. citeturn17search0turn16search0turn0search6

## Production patterns for using agent CLIs as LLM backends

### Established integration patterns that do exist

There is a recognizable pattern emerging across coding-agent CLIs: **headless invocation + JSON/JSONL output + sandbox/approval policy**.

- Codex CLI explicitly supports CI-friendly machine-readable output (`--json` events, `--output-last-message` artifact) and security controls (`--sandbox`, approvals). citeturn7view2turn25view2  
- Gemini CLI’s headless mode is documented as ideal for scripting/automation and returns a stable JSON envelope (plus streaming JSON event mode). citeturn16search0turn16search6  
- Claude Code CLI’s print mode supports JSON output and also a `--json-schema` option for validated structured JSON “after agent completes its workflow,” plus tool restriction (`--tools`, including disabling all tools with `""`). citeturn21view0turn21view1  

There are also third-party wrappers that treat these CLIs as subprocess backends:

- A Python SDK that wraps Gemini CLI as a subprocess and adds typed outputs / Pydantic models (illustrates “CLI-as-backend” hardening). citeturn17search2  
- Sandboxed execution patterns for Codex exec (e.g., running `codex exec` inside isolated sandboxes) appear in infrastructure documentation, reflecting the security expectation that agent CLIs may run tools/commands. citeturn1search3  
- Plugins that integrate Codex CLI as an “agent” backend (including surfacing tool calls via JSONL) illustrate the operational model: treat the CLI as an agent runtime, not just a model inference function. citeturn1search10turn7view2  

### High-probability gotchas and anti-patterns for data pipelines

**Implicit context contamination (workspace, config, and “project docs”)**

Agent CLIs intentionally ingest context from disk (repo state, settings layers, project instruction files). For example, Claude Code settings are layered across managed/user/project/local scopes and are meant to shape behavior. citeturn23view0 Codex similarly composes prompts using configuration and project docs such as AGENTS.md (with configurable limits). citeturn3view0turn14view0  
In a production pipeline, this creates a reproducibility risk unless you isolate working directories and pin configurations per job/run. citeturn25view2turn23view0

**Agentic tool use when you expect pure inference**

Gemini CLI, Codex CLI, and Claude Code all expose built-in tool ecosystems (shell/file ops, web fetch/search, MCP). citeturn0search0turn25view2turn21view0  
If a verification backend is expected to be “read-only text reasoning,” leaving tool availability open can add latency, nondeterminism, and failure modes (permission prompts, sandbox denials, unexpected network/tool calls). citeturn25view2turn16search0turn21view0

**Output brittleness when the CLI envelope is structured but the payload isn’t**

Gemini CLI is the clearest example: `--output-format json` guarantees the wrapper object, not schema conformity of the `response` field. Real issues show the response can contain Markdown-fenced JSON, undermining downstream parsers. citeturn16search0turn16search9  
If your pipeline’s correctness depends on Pydantic-level guarantees, CLI envelopes alone are insufficient. citeturn0search6turn16search0

**Version churn and interface drift**

Gemini CLI documents rapid release cadences (preview/stable/nightly) and publishes frequent release notes. citeturn16search2turn26search1 In a production pipeline, uncontrolled CLI upgrades can silently change output formats, default models, tool behavior, or safety constraints—so you typically need version pinning and compatibility tests. citeturn26search1turn7view2

## Replicating Instructor’s retry-with-feedback behavior

### What Instructor does (the behavior you’re replacing)

Instructor’s retry mechanism is explicitly a **validation feedback loop**:

1. capture validation errors,  
2. format as feedback,  
3. append feedback to the prompt context,  
4. ask the LLM to try again, up to `max_retries`. citeturn0search6  

This is functionally “schema repair by iterative prompting,” which is especially important when you do not have strict constrained decoding guarantees. citeturn0search6turn2search6

Your repo’s excerpting spec indicates you already reason about retry and consensus behaviors at the architecture level, so replacing Instructor is not just a transport swap—it changes a reliability primitive. fileciteturn13file0L1-L1

### Pitfalls when implementing this pattern yourself

**Prompt growth and context-window pressure**

Appending full validation errors can be verbose (nested field paths, long type errors). Each retry expands context, which increases token costs and can change model behavior across retries. This is a known parsing failure domain in structured-output pipelines generally. citeturn0search6turn18search0

**“Fixing the parser” vs “fixing the semantics”**

A repair loop can converge to JSON that passes schema validation but is semantically low-quality (e.g., empty strings, placeholders, “unknown”). Instructor’s retries improve syntactic validity but cannot guarantee domain correctness; you typically need additional semantic checks or cross-model verification (which your pipeline already contemplates). citeturn0search6turn18search0  

**Inconsistent behavior across different backends**

Once you migrate to CLIs, you’ll have heterogeneous guarantees:

- Codex CLI: schema validation flag exists, but it’s part of an agent workflow, not a pure structured-output API call. citeturn7view0turn3view0  
- Claude Code: schema validation exists “after agent completes its workflow.” citeturn21view0  
- Gemini CLI: no custom schema enforcement; you must implement retry/repair externally or switch to the SDK. citeturn16search1turn17search0  

A single “retry strategy” may not port cleanly across all three.

### Open-source implementations of “retry with error feedback” outside Instructor

**LangChain parsers**

LangChain provides retry parsers that explicitly pass the *prompt + completion + error* back to an LLM to repair outputs:

- `RetryWithErrorOutputParser`: “passing the original prompt, the completion, AND the error.” citeturn18search1turn18search6  
- `RetryOutputParser`: similar, but without the detailed raised error. citeturn18search5turn18search10  

**Guardrails reasking**

Guardrails supports validator-driven remediation, including `OnFailAction.REASK`, where the prompt used for reasking includes auto-generated information about which criteria failed. citeturn18search14turn18search13

These are the closest OSS analogs to Instructor’s “validation error appended to prompt” loop, and they can be adapted to “CLI backend” execution if you can reliably capture the failing output and feed the error message back into a subsequent CLI call. citeturn18search1turn18search14turn21view0

## Temperature control and “determinism knobs” in the CLIs

### Claude Code CLI

Claude Code CLI exposes many operational controls in print mode (`--max-turns`, `--output-format`, `--json-schema`, tool restriction via `--tools`, and disabling tools with `--tools ""`). citeturn21view0turn21view1  
However, neither the CLI reference nor the settings documentation exposes a `--temperature` flag or a temperature setting. citeturn21view0turn24view0turn23view0

**What you can do instead:** use `--json-schema` for validated structured output and disable tools (`--tools ""`) to reduce nondeterministic tool behavior; cap agentic depth with `--max-turns`. citeturn21view0turn21view1

### Codex CLI

Codex CLI exposes sandboxing (`--sandbox`), approvals (`--ask-for-approval`), and structured output options (`--output-schema`, `--output-last-message`, `--json`). citeturn7view0turn25view2  
In the Codex CLI docs captured here, temperature is not exposed as a CLI flag; instead, configuration focuses on **reasoning effort** and related agent/runtime parameters (e.g., `model_reasoning_effort`, `model_verbosity`). citeturn10view4turn14view0turn7view0

**What you can do instead:** tune `model_reasoning_effort`, disable web search tools, and run read-only to reduce variability. citeturn10view4turn14view0turn25view2

### Gemini CLI

Gemini CLI’s headless mode documents `--model`, `--output-format`, `--debug`, and approval modes, but does not document a temperature flag in the headless reference. citeturn16search0turn16search6turn16search3  
The configuration guide excerpt similarly does not surface a temperature knob. citeturn19view0turn20view0

**If you require temperature=0:** the evidence-backed path is to use the Gemini API SDK directly (where generation config supports structured outputs with schema, and temperature is typically an API-level parameter), rather than relying on Gemini CLI. citeturn17search15turn17search0turn16search0