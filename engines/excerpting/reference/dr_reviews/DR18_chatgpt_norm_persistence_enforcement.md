# Persisting Behavioral Norms Across Context Resets in Multi-Session LLM Workflows

## Problem framing and constraints

Your environment is structurally hostile to “norm persistence” in the way humans usually mean it: every work session is a fresh context window, yet a single campaign spans 15–30 sessions and depends on consistent behavioral compliance inside natural-language generation. That puts you in a regime where written norms must repeatedly *win* against (a) position/salience limits in long contexts, (b) the model’s learned “assistant prior,” and (c) local optimization pressures (time, uncertainty, friction). The KR repository itself documents the same meta-problem in different language: prose rules are forgettable, while structural constraints and tool-grounded enforcement are what actually change outcomes. fileciteturn31file0 fileciteturn24file0

Two details matter because they shape almost every solution tradeoff:

First, both of your critical norms are *behavioral policies*, not single-step formatting constraints. Behavioral norms typically require (i) recognizing a situation as relevant (“am I about to ask the user to decide?”), (ii) inhibiting a default response, and (iii) substituting an alternate workflow (“derive next step and execute,” “route prompt through optimizer”). These are multi-step control problems under uncertainty, which are exactly where current instruction-following is least robust in long, heterogeneous contexts. The KR protocol documents the same pattern: “be careful” and same-context introspection do not reliably prevent failures; tool-based verification and forced context breaks do. fileciteturn24file0

Second, your system already contains partial “structuralization” patterns (and therefore suggests where additional leverage exists): compaction-proof prompt injections via lifecycle hooks, and stop-gates that block session termination based on external symptoms (e.g., “did NEXT.md get updated”). Those patterns are important because they show a path to convert *behavioral rules* into *gated artifacts* and *observable evidence*. fileciteturn20file0 fileciteturn17file0 fileciteturn19file0

The remainder of this report is three-layered: (1) why norms decay, (2) how other domains maintain methodology without live supervision, and (3) concrete enforcement mechanisms that fit a Claude Code + Codex CLI + Gemini CLI multi-session, multi-provider workflow.

## Layer 1 failure taxonomy

### Salience failures from long-context position effects

A robust empirical finding in long-context language modeling is that models use information near the beginning and end of the context more reliably than information “in the middle.” “Lost in the Middle” shows substantial performance degradation when relevant information is placed mid-context, even for models designed for long contexts. citeturn0search0 This matters for your 1,700-line protocol: if the two critical norms are not in a privileged position (or must compete with many other instructions), they will be sampled less strongly at the moment of generation.

A newer line of work explicitly treats this as a positional-encoding/attention-distribution problem and proposes methods to mitigate “lost-in-the-middle” effects (e.g., positional encoding variants to improve mid-context retrieval). The existence of this line of work is itself evidence that “instruction in context” is not uniformly available to the model across positions. citeturn0search4

**Implication for your case:** duplicating norms across many locations does not guarantee stronger enforcement; it can just create more mid-context “dead zones.” If the protocol is long and dense, a norm can be “present” but functionally not *attended* at the critical decision point.

### Instruction hierarchy brittleness and the “confusable deputy” mechanism

A second root mechanism is that LLMs historically struggled to robustly obey an instruction hierarchy (system > developer > user > tool outputs) under adversarial or conflicting inputs. OpenAI’s “Instruction Hierarchy” work frames prompt injection, jailbreaks, and similar failures as sharing a vulnerability: models often treat privileged instructions as comparable in priority to untrusted text, and training explicitly for hierarchical instruction following can increase robustness. citeturn3search0turn3search4 A more recent OpenAI update (IH-Challenge) continues in the same direction and explicitly defines the hierarchy and its role in resisting prompt-injection-like conflicts. citeturn3search1

This is directly relevant to multi-agent workflows because your system does something structurally similar to “prompt injection” even when no attacker exists: it concatenates rules, handoffs, tool output, and user interaction into one mixed stream, then asks the model to draw the correct boundary between “policy” and “content.” The entity["organization","National Cyber Security Centre","uk government"] has an unusually clear formulation here: current LLMs “do not enforce a security boundary between instructions and data inside a prompt,” and mitigations should assume the model is an “inherently confusable deputy.” citeturn2search3 This is security language, but it describes the same underlying cognitive phenomenon you are seeing as “norm decay.”

**Implication:** norm violations are not only “forgetting”; they are often *mis-prioritization* under mixed instruction streams (protocol text + task demands + social defaults). The failure mode is: the model follows a locally salient goal (be helpful, reduce uncertainty, ask user, respond quickly) rather than the higher-order norm.

### Behavioral norms conflict with RLHF-shaped priors

RLHF-style alignment training explicitly optimizes for outputs humans prefer. InstructGPT is a canonical example: supervised fine-tuning + RLHF can make models more aligned with “user intent” and preferred behaviors. citeturn1search4turn1search0 citeturn1search1 citeturn1search4 entity["people","Long Ouyang","openai researcher"]

This is beneficial in general, but it creates a predictable friction for your Norm 1 (“the AI agent is the decision-maker; never ask the user for technical guidance”). Many RLHF datasets implicitly reward *deference*, *clarifying questions*, and *collaborative tone*—especially when uncertainty is high. The result is that “ask the user what to do” can be a high-probability continuation even when a written norm forbids it.

Similarly, Norm 2 (“mandatory tool use before dispatching prompts”) asks the model to accept extra friction and delay. RLHF often rewards responsiveness and direct helpfulness; inserting an optimization step can feel like “unnecessary ceremony” to the model unless the environment makes it *structurally required*.

Constitutional-style training shows a related concept: behavior can be steered by explicit principles and self-critique procedures, but that steerability is still a training outcome, not a guarantee of perfect compliance at runtime. citeturn1search2 entity["people","Yuntao Bai","anthropic researcher"]

**Implication:** Norm 1 and Norm 2 are not “natural continuations” of the helpful assistant prior; they are *anti-priors*. That predicts (all else equal) higher violation rates than for purely factual or formatting constraints.

### Why “behavioral norms” are often less sticky than “factual instructions”

There is not a single, universally accepted paper that cleanly proves “behavioral norms degrade faster than factual instructions” across all models and contexts; it depends on how you measure “behavior” vs “fact.” What can be said with evidence is:

- Long-context retrieval is position-sensitive. citeturn0search0  
- Instruction hierarchy can fail; training specifically for prioritization helps. citeturn3search0turn3search1  
- Prompts are extractable and overrideable; treating prompts as “secure” is unreliable. citeturn2search5turn2search0  
- Prompt injection exists because models don’t separate data/instructions internally. citeturn2search3turn2search0  

From these, a conservative inference follows: **instructions that require repeated classification + inhibition across many diverse micro-situations will be less robust than instructions that bind to a narrow, repeated surface pattern** (e.g., a specific output schema). This is consistent with KR’s own empirically derived “Quality Axiom”: introspective self-review doesn’t work reliably; tool-based and structural mechanisms do. fileciteturn24file0

### Norm decay accelerators visible in your system design

The KR repository contains multiple concrete “decay accelerators” that generalize beyond KR:

- **Prose rule sprawl and channel mismatch.** The repo explicitly distinguishes “rules in repo files are aspirational; rules in the system prompt are behavioral,” and recommends moving enforcement into the system prompt or structural workflow. fileciteturn23file0  
- **Context-compaction and session switching.** KR describes repeated failures where rules were added but did not “stick” across sessions because context compacts and resets. fileciteturn31file0  
- **Partial enforcement that checks symptoms, not causes.** E.g., Claude Code hooks cannot inspect response text directly and therefore gate on external artifacts (NEXT.md updated or not). This is clever, but it means some violations remain undetectable unless they leave a trail. fileciteturn17file0  
- **Conflicting “autonomy” semantics.** KR protocols sometimes require the agent to stop and wait for “continue” as a context-break forcing function, which can be semantically adjacent to “waiting for permission,” and may blur the boundary of what “autonomous operation” means in practice. fileciteturn30file0  
- **Tool-availability uncertainty.** KR explicitly warns to scan the filesystem for available skills/tools because memory mappings can be stale; that is a real contributor to tool-use norm violations—when the model is uncertain a tool exists, it will often proceed without it. fileciteturn24file0  

**Practical prediction:** the first norms to fail are usually the ones that (a) contradict the assistant prior, (b) require extra steps/tool friction, (c) are ambiguously specified at the boundary cases, and/or (d) are “lost in the middle” of long instruction packs. citeturn0search0turn1search4turn3search0

## Layer 2 cross-domain solutions

### Classical Islamic institutional pedagogy as “norm persistence engineering”

Your analogy to Islamic scholarly tradition is structurally correct: the core problem is how methodology persists when the teacher is absent and transmission spans many steps. The key mechanisms do not rely on constant supervision; they rely on *authorization, provenance, and artifact-bound evidence*.

**Ijāzah as authorization with accountable provenance.** Modern scholarship and primary-document studies treat ijāzah as a license/authorization to transmit or teach a text/discipline, typically grounded in direct study and a teacher–student relationship, and embedded in a chain (sanad/silsilah). citeturn12search5turn12search7 entity["people","Robert Gleave","islamic law scholar"] entity["people","Mesut Idriz","islamic studies scholar"] The structural principle that makes this enforcement-like (not mere documentation) is: **authorization is socially legible, revocable in reputation, and tied to a specific claimant** (the transmitter), so violations damage transmissibility and status, not just correctness.

**Silsilah/sanad as a tamper-evident chain of transmission.** The point of documenting a chain is not “note-taking.” It makes claims about knowledge *queryable*: who taught whom, when, where, and through which intermediate authorities. The Audition Certificates Platform (a research initiative focused on manuscript audition certificates) describes audition certificates (samāʿ / ijāzah) as manuscript notes documenting authorized transmission and participants in reading sessions. citeturn8search0turn8search4 The structural principle is: **the chain is a verification interface**—it lets later communities audit provenance and discount unreliable links.

**Madrasa curriculum sequencing as prerequisite-gated norm formation.** Here the enforcement mechanism is not a single certificate; it is *path dependency*: a fixed sequence of texts, prerequisites, and commonly recognized mastery milestones constrains what methods a student is likely to apply later (because they have been trained in that order and language). While many detailed studies are monograph-based, the mechanism is conceptually aligned with what modern process engineering calls “stage gates”—the learner cannot credibly skip foundational methods because later authorization assumes them. (For your purposes, the relevant imported structure is “prerequisite-gated advancing,” not the specific historical curriculum.)

**Muqābalah and audition certificates as artifact-bound state attestation.** Audition/reading certificates (samāʿāt) are a particularly close analog to your desired “proof of compliance”: they are attached to a physical manuscript and record the reading session(s), attendees, authority, and sometimes partial attendance. citeturn9search46turn9search0 entity["people","Tilman Seidensticker","arabic studies scholar"] Konrad Hirschler’s work on reading certificates treats samāʿāt as documentary sources for social and cultural practice (including who was authorized and how). citeturn11search0turn11search45 entity["people","Konrad Hirschler","islamic historian"] The structural principle is: **an artifact is not accepted as authoritative unless it carries evidence that it was read/collated under recognized authority**—i.e., a binding between content state and verified process state.

**Isnād criticism and transmitter evaluation as distributed quality control.** Hadith and related transmission sciences developed systematic evaluation of transmitters (ʿilm al-rijāl / jarḥ wa taʿdīl) in which individuals’ reliability and accuracy are assessed and recorded. citeturn4search1turn5search0 The structural principle is: **quality is enforced by ranking the trustworthiness of agents and conditioning acceptance on those ranks**, not solely on any single document’s claim.

**Anchor classical texts for your requested primary-source naming.** The mechanisms above are classically theorized and operationalized in major hadith-methodology works such as: entity["book","al-Kifaya fi 'Ilm al-Riwaya","al-khatib al-baghdadi"] and entity["book","al-Jami' li Akhlaq al-Rawi wa Adab al-Sami'","al-khatib al-baghdadi"], and later methodological syntheses like entity["book","Muqaddimah Ibn al-Salah","hadith methodology"]. (Citations here point to the modern manuscript-certificate scholarship that operationalizes how these norms appear in real artifacts and communities.) citeturn9search46turn11search45turn8search0

### Organizational theory and high-reliability practice as “norm persistence without supervision”

The organizational analogs that translate most directly are the ones that rely on *forcing functions, structured handoffs, and routine auditing* rather than inspirational values.

**Checklists as cognitive forcing functions.** The entity["organization","World Health Organization","un agency"] surgical safety checklist program is the canonical example that a checklist can reduce errors across diverse settings: the WHO guidance and the underlying NEJM study (Haynes et al., 2009) report reductions in complications and mortality after implementing a 19-item checklist across multiple hospitals. citeturn14search6turn14search12turn14search0 The structural principle is: **checklists externalize memory and attention; compliance becomes observable; omission becomes legible.**

**Crew Resource Management as behavior shaping through shared protocols and training.** In aviation, CRM emerged to address team and leadership error modes, and formal CRM guidance exists as operational doctrine (e.g., FAA advisory circulars on CRM training). citeturn14search2turn14search9 entity["organization","Federal Aviation Administration","us aviation regulator"] The structural principle is: **train and standardize interaction patterns so that “good behavior” is proceduralized, not improvised.**

**Asynchronous runbooks and incident-response doctrine in distributed operations.** The Google SRE literature includes concrete artifacts like example incident state documents, postmortems, and launch coordination checklists; these are designed to preserve norms (what to do, what not to do) across handoffs and fatigue. citeturn13search0turn13search3 entity["book","Site Reliability Engineering","google sre book 2016"] The structural principle is: **a runbook is a contract between “the organization at time t” and “the operator at time t+n.”**

**Franchising as standardization at scale via audits, mystery shoppers, and controlled inputs.** For your McDonald’s example, we can ground this in two complementary source types:
- McDonald’s own franchising materials emphasize long, competency-based training (including Hamburger University), and ongoing field operations support oriented around quality/service/cleanliness. citeturn16search0 entity["company","McDonald's","fast food company"]  
- Empirical franchising research explicitly models the control mechanisms franchisors use to maintain uniformity, including **audits**, **mystery shoppers**, and **mandatory purchase of inputs** (to reduce free-riding and ensure conformance quality), alongside customer polls for perceived quality. citeturn16search1turn16search3  

The structural principle here is extremely transferable: **separate “brand-critical norms” from local discretion, then continuously measure compliance using multiple, partly redundant control channels.**

## Layer 3 technical mechanisms for your multi-session CLI agent environment

This layer proposes mechanisms that fit the key constraint you stated: no simple runtime script can reliably intercept violations *inside* free-form natural language generation. Therefore, the strategy is to convert “invisible behavior” into (a) **observable evidence**, (b) **gated artifacts**, and/or (c) **two-stage generation flows** where the “send” step becomes enforceable.

I’ll present each mechanism in a uniform schema: what it enforces, how it detects, whether it prevents or merely detects, complexity, and failure modes. Many are combinable; the ranked list at the end selects the best portfolio for your exact problem (Norm 1 + Norm 2 across 15–30 session campaigns).

### Gated dispatch artifacts for mandatory prompt optimization

**What it enforces.** Norm 2 (“no raw prompt is ever dispatched; everything is optimized first”). This also indirectly supports Norm 1 by reducing ad-hoc user-dependent improvisation in dispatch. citeturn3search0turn2search0

**How it detects violations.** The only allowed way to dispatch a prompt is by producing a structured “PromptCard” artifact with required fields:
- `draft_prompt`
- `optimizer_name` and `optimizer_version`
- `optimized_prompt`
- `optimization_evidence` (e.g., diff summary, rubric checks)
- `hash(draft_prompt)`, `hash(optimized_prompt)`
- `timestamp`, `session_id`, `target_agent`

A dispatcher wrapper rejects any dispatch that does not reference a valid PromptCard and logs the violation.

You already have the architectural pattern for this in KR: “rules should become structural workflows,” and “tool-based verification” beats aspirational prose. fileciteturn23file0 fileciteturn24file0

**Prevent vs detect.** Prevents—because dispatch is technically impossible without a PromptCard.

**Implementation complexity.** Medium. In a CLI environment, this typically means:
- Creating a single “dispatch” command (shell script or Python) that is the only permitted channel to send prompts to Codex/Gemini/other coworkers.
- Teaching agents that “dispatch = run dispatch command,” not “print a prompt for the user to copy.”  
KR already routes LLM calls through an adapter that supports event hooks around completions (pre/post/error). That hook layer is a natural insertion point for enforcement in programmatic dispatch paths. fileciteturn15file0

**Failure modes.**
- Humans bypass the dispatcher by copy-pasting text manually (common). Mitigation: “outputs are ignored downstream unless accompanied by PromptCard + dispatch log entry,” i.e., make the artifact a required input to the next pipeline stage.
- Optimizer becomes a bottleneck, causing agents to “optimize lazily” (low-quality optimization). Mitigation: add a second, cheap rubric check (see transcript analysis below).
- Some dispatch targets are not tool-mediated (e.g., chatting in a UI). Mitigation: require that any “human relay prompt” must be emitted as a PromptCard file, not plain text.

### Two-stage generation with a norm-linter gate

**What it enforces.** Both norms by gatekeeping the final “user-visible” or “downstream-visible” artifact:
- Norm 1: no asking for technical guidance; autonomous next steps must exist.
- Norm 2: no raw dispatch prompts; must be PromptCard-derived.

**How it detects violations.** Insert a mandatory “lint” step between draft generation and final output acceptance:
1. The agent generates a draft response in a structured envelope: `{analysis_summary, actions, questions_for_user, dispatches[]}`.
2. A separate checker (could be deterministic + LLM classifier) evaluates violations:
   - For Norm 1: detect technical questions, permission-seeking language, or missing “next steps derived from protocol/roadmap.”
   - For Norm 2: detect any `dispatches[]` without linked PromptCards / optimizer evidence.

This mirrors how instruction-hierarchy research treats mis-prioritization as the root cause: you add an explicit discriminative step that enforces priority rules. citeturn3search0turn3search1

**Prevent vs detect.** Prevents (if the gate blocks) or detects (if it only logs). The key is: **don’t accept outputs downstream without a passing lint report**.

**Implementation complexity.** Medium–high depending on how integrated your toolchain is. In KR-like environments, you can often implement this with:
- “Output must be written to a file.”
- A gate script validates the file; if fail, it produces a re-prompt to regenerate under constraints.

The KR hook system already demonstrates gating based on external state at stop time, and injecting compaction-proof context at each user prompt; those are building blocks for a two-stage gate. fileciteturn17file0 fileciteturn20file0

**Failure modes.**
- False positives (blocking legitimate non-technical clarification).
- False negatives (cleverly phrased permission-seeking slips through).
- Checker drift if it’s LLM-based. Mitigation: keep part of it deterministic (pattern checks) and log everything for periodic review.

### Inter-session “fresh eyes” compliance audits as a chain-of-custody

**What it enforces.** Sustained compliance across a 15–30 session campaign by introducing a second-order norm: “each session must verify prior session compliance before proceeding.”

**How it detects violations.** Each new session starts by:
- Reading the previous session’s final artifacts (handoff, dispatch logs, PromptCards, lint reports).
- Emitting an “AuditRecord” that explicitly states whether Norm 1 and Norm 2 were complied with, with evidence pointers.

This is directly analogous to the tradition of reading certificates (samāʿāt) as documentary evidence of who did what, when, and under what conditions. citeturn8search0turn9search46turn11search45

It is also directly aligned with KR’s own empirical governance logic: “fresh context found what biased sessions missed,” and context breaks are treated as a quality mechanism. fileciteturn21file0 fileciteturn24file0

**Prevent vs detect.** Mostly detects, but becomes preventive if downstream stages refuse to proceed without a passing AuditRecord.

**Implementation complexity.** Low–medium. Requires that each session writes:
- session transcript (or at least structured action log),
- dispatch log,
- lint results,
and the next session has a standard audit template.

**Failure modes.**
- Audit becomes rubber-stamping. Mitigation: randomize audit focus and require concrete evidence (hashes, file paths, log entries).
- Incentive misalignment if speed is prized over correctness.

### Structural prompt architecture to exploit primacy/recency and reduce hierarchy conflicts

**What it enforces.** Primarily Norm 1 and Norm 2 by maximizing salience at generation time.

**How it detects violations.** This mechanism is mostly preventive (salience engineering), not a detector. The enforceable part is: require the agent to output (or update) a “NormBanner” block at the top of every session output that restates the two norms in minimal, unambiguous language and declares how compliance will be evidenced (PromptCards, lint report, etc.).

“Lost in the Middle” implies you should privilege beginning/end placement. citeturn0search0

Instruction-hierarchy work implies you should separate policy text from tool outputs and untrusted content, and explicitly bind priority. citeturn3search0turn2search3

The KR repo already uses compaction-proof prompt injection (“ROLE… NEVER say standing by/waiting…”) via a UserPromptSubmit hook, which is essentially a recency/primacy hack. fileciteturn20file0

**Prevent vs detect.** Prevents (probabilistically), not guaranteed.

**Implementation complexity.** Low. It’s mostly prompt and workflow refactoring:
- Put norms in the smallest possible canonical form.
- Put them at the very top and very bottom of the highest-priority instruction channel.
- Remove redundant, inconsistent duplicates elsewhere (or replace them with references to the canonical form).

**Failure modes.**
- Conflicts between norms and other workflow instructions (e.g., “wait for continue” vs “never wait for permission”) still create ambiguity.
- If the model’s RLHF prior strongly conflicts (autonomy vs deference), salience may not be sufficient alone. citeturn1search4turn1search1

### Post-session transcript analysis with quantitative norm metrics

**What it enforces.** Detects both norms at scale and turns them into measured reliability targets (e.g., “Norm 1 violations per session,” “% dispatches with PromptCards,” “time-to-violation”).

**How it detects violations.** Run an automated transcript analyzer after each session:
- Deterministic checks: presence of question marks + key phrases (“should I…”, “do you want me to…”) and presence/absence of next-step section.
- Semantic classification: an LLM-based classifier that labels questions as “technical guidance solicitation” vs “domain preference question.”
- Norm 2: scan for any outbound prompts not traced to PromptCards, and/or scan for PromptCards produced but not used.

This is consistent with OWASP’s “insecure output handling” framing: if you treat model output as trustworthy without validation, downstream failures happen. citeturn2search0turn2search1

KR’s Quality Axiom explicitly argues that “if it’s not in the checklist, it wasn’t done,” and favors tool-based verification over introspection; transcript analysis is a direct instance of that philosophy. fileciteturn24file0

**Prevent vs detect.** Detects after the fact—unless paired with a gate that blocks downstream acceptance.

**Implementation complexity.** Medium. Needs transcript capture (often already available), a parser, and a reporting pipeline.

**Failure modes.**
- Classifier drift and false positives.
- The model adapts its wording to evade lexical checks (rare unless you create adversarial incentives).
- If you don’t tie metrics to acceptance gates, you only get observability, not enforcement.

### Hash-chain attestation inspired by ijāzah/samāʿāt and “muqābalah” artifact binding

**What it enforces.** “Outputs are only valid if produced under compliance.” This is the closest analog to your requested “cryptographic shahada/ijazah model.”

**How it detects violations.** The session must emit an attestation bundle:
- `session_output_hash`
- `prev_session_hash`
- `policy_version_hash` (hash of canonical norms)
- `evidence_hashes` (dispatch logs, PromptCards, lint reports)
- A signature using a project key

Downstream automation verifies the chain: if any link is missing or inconsistent, output is rejected.

This is structurally analogous to manuscript audition certificates that bind a specific copy to an authorized reading event, and to ijāzah documents that bind authority to a named transmitter and a specific subject/text. citeturn8search0turn9search46turn12search5

**Prevent vs detect.** Prevents downstream use of noncompliant outputs. It does not prevent the model from *generating* violations, but it prevents violations from causing damage by denying them downstream acceptance.

**Implementation complexity.** Medium. Cryptographic signatures are straightforward; the hard part is specifying what evidence is required and standardizing it across providers/tools.

**Failure modes.**
- If humans can “force accept” outputs, the chain becomes ceremonial. Mitigation: make acceptance automated and non-optional for production.
- Key management mistakes (lost keys, compromised keys).
- Overly rigid evidence requirements that block legitimate work.

### Provider-level hooks where possible, and “symptom-based” proxies where not

**What it enforces.** Portions of norms that are observable at tool boundaries, plus high-signal proxies for the rest.

**How it detects violations.** Use what each environment can do:
- For programmatic LLM calls: intercept prompts at “completion:kwargs” and require optimizer markers / PromptCard references (KR already has a hookable adapter event layer). fileciteturn15file0  
- For Claude Code: extend lifecycle hooks and file-based enforcement patterns (KR already uses stop-gates and prompt context injection). fileciteturn19file0turn17file0turn20file0  

This aligns with KR’s demonstrated practice: when you cannot inspect response text directly, you enforce via external artifacts and symptoms (e.g., “substantial work but no NEXT.md update”). fileciteturn17file0

**Prevent vs detect.** Mixed. Some are preventive (blocking stop), some are detective (warnings, logs).

**Implementation complexity.** Low–medium because the scaffolding exists, but designing good proxies is nontrivial.

**Failure modes.**
- Proxy mismatch: behavior violates norm without triggering symptom.
- Hook bypass paths (e.g., manual copy/paste).

## Ranked enforcement mechanisms for your specific system

This ranking optimizes for “expected impact on norm persistence” under your exact constraints: multi-session resets, multiple LLM providers/CLIs, and historically demonstrated damage from violations. Each entry includes an implementation sketch designed for a software engineer to act on.

### Gated dispatch with PromptCards as the only legal outbound prompt format

Make a single dispatch channel that is structurally incapable of sending raw prompts. Implement a `dispatch/` command (or Python module) that requires a PromptCard file path as input, verifies it contains optimizer provenance (optimizer name/version + hashes), records a dispatch ledger entry, and only then transmits to Codex/Gemini/other coworkers. Any “prompt to be relayed by the owner” must also be emitted as a PromptCard file (so the human relay is copying an artifact, not free text). Then change downstream acceptance rules: if a coworker result arrives without a matching PromptCard hash in the ledger, it is ignored. This directly mirrors franchising control channels (audits/required inputs) and converts Norm 2 into enforceable infrastructure. citeturn16search1turn16search0 fileciteturn23file0

### Two-stage generation with a norm-linter gate before any output is “real”

Refactor session outputs so the LLM first writes a structured draft (actions, dispatches, questions) to a file, then a gate script runs: (a) deterministic checks for permission-seeking/technical guidance solicitation, (b) dispatch validation (every dispatch references a PromptCard), and (c) optionally an LLM-based classifier for ambiguous cases. If the gate fails, the system re-prompts the model with the failing checks and requires regeneration. This converts both norms into preflight constraints and prevents “silently dropped feedback” and “unoptimized prompt” damage by blocking the output from becoming a downstream input. It is also directly consistent with OWASP’s warning about insecure output handling and “excessive agency” risks: you must validate before acting. citeturn2search0turn2search1 fileciteturn24file0

### Hash-chain attestation for session outputs with evidence binding

Implement a chain-of-custody ledger where each session must output an attestation bundle: hashes of (1) canonical norm text/version, (2) session output, (3) dispatch ledger entries, (4) PromptCards, (5) lint report, and (6) prior session hash. Sign the bundle with a project key. Downstream automation verifies the chain before accepting any artifact (handoff, prompts, decisions). This is the closest technical analog to ijāzah + samāʿāt as artifact-bound authorization: it does not rely on “remembering,” it relies on “proof required for acceptance.” citeturn8search0turn9search46turn12search5

### Inter-session compliance audit as mandatory “fresh eyes” stage gate

At the start of each new session, require a lightweight compliance audit of the previous session: did it ask for technical guidance, did it dispatch through the proper channel, did it produce required artifacts (PromptCards, lint report, attestation), and did it end with a concrete autonomous next-step plan. Require that the audit output itself is committed as a session artifact, and that the next step cannot begin until the audit passes. This leverages what KR already treats as a quality mechanism—context breaks and fresh-instance review—and imports the isnād criticism idea: reliability is tracked *per transmitter/session* and becomes part of whether later work is trusted. fileciteturn21file0 fileciteturn24file0 citeturn11search45turn11search0

### Transcript analysis with quantitative norm metrics tied to acceptance thresholds

Implement post-session transcript analysis that produces a scorecard: Norm 1 violations (count + severity), Norm 2 compliance rate (% dispatches with PromptCards), and latency-to-violation. Use this not just for monitoring but as a hard acceptance threshold: e.g., “any critical Norm 1 violation invalidates the session’s outputs; the session must be rerun or corrected.” This is the engineering analog of checklist-based and audit-based organizational controls: when compliance is measured, gaps become systematically correctable rather than rediscovered ad hoc. It also aligns with the KR repository’s empirically grounded view that tool-based verification and structural enforcement outperform introspective commitments. citeturn14search12turn13search0 fileciteturn24file0