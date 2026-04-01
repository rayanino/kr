# Fresh adversarial integrity review of CURRENT I-002 bundle in IsIdeas

## Evidence reviewed

Read directly from the current remote default branch (`main`) state, in the required order: `ideas/curriculum-architect/RESEARCH.md`, `DOSSIER.md`, `README.md`, the three preserved external reviews, the Jamia Binoria source preservation note, the modelability session, ADR-012, and the three governed catalog surfaces (`ACTIVE_FOCUS`, `INTEGRITY_BOARD`, `CRITIQUE_REGISTRY`). fileciteturn3file0L1-L1 fileciteturn4file0L1-L1 fileciteturn5file0L1-L1 fileciteturn6file0L1-L1 fileciteturn7file0L1-L1 fileciteturn8file0L1-L1 fileciteturn9file0L1-L1 fileciteturn10file0L1-L1 fileciteturn11file0L1-L1 fileciteturn12file0L1-L1 fileciteturn13file0L1-L1 fileciteturn14file0L1-L1

## Axis verdicts

axis: 1  
verdict: conditional  
confidence: moderate  
reason: The current validator packet and supporting docs consistently frame the Jamia Binoria anchor as *one institution-bound variant* (not universal, not a “correct order”), and the governed surfaces explicitly treat “second source required” as *not yet*. fileciteturn3file0L1-L1 fileciteturn9file0L1-L1 fileciteturn14file0L1-L1 The remaining integrity weakness is evidentiary durability/falsifiability: the “preserved” curriculum anchor is an extracted/condensed representation (not a verbatim capture with durable anchoring), while simultaneously being treated as durable repo truth for downstream modeling decisions. fileciteturn9file0L1-L1  
would_change_if: Strengthens to valid if the preserved anchor is made explicitly “verbatim capture vs. paraphrase” (or otherwise made independently checkable as a capture), such that it cannot quietly become a “source-like” authority artifact merely by being in-repo. fileciteturn9file0L1-L1

axis: 2  
verdict: conditional  
confidence: moderate  
reason: The revised validator packet now states the teacher-guided path may function as the student’s primary local path, and it explicitly asks the evaluator to judge whether the framing subtly demotes the teacher—this is integrity-positive and directly targets the earlier critique. fileciteturn3file0L1-L1 The dossier’s formal model also describes teacher guidance as a separate attributed path that can be locally primary while keeping the published source visible (i.e., it no longer relies on “override” language in its modeled constraints). fileciteturn4file0L1-L1 **However, one supporting truth doc still authorizes a system-owned fallback that undermines the authority boundary:** the modelability session proposes a “structural-only mode” showing “widely-agreed logical dependencies,” which is exactly an unattributed prerequisite claim and is structurally equivalent to “software knows the basics.” fileciteturn10file0L1-L1 This is an authority leak vector even if it is not in the MVP packet, because it remains in the bundle and can re-enter future wording/interpretation/build decisions. fileciteturn12file0L1-L1  
would_change_if: Upgrades to valid if the modelability session deletes (or reverses into a prohibition) the “structural-only mode / widely‑agreed dependencies” concept, making “no system-owned prerequisite edges” a bundle-invariant across packet + dossier + research notes. fileciteturn10file0L1-L1

axis: 3  
verdict: valid  
confidence: high  
reason: The current revised packet/dossier consistently commit to literal preservation of the published order while using neutral source notes / extraction-epistemic notes, explicitly forbidding “fixing” or silently normalizing non-monotonic published ordering. fileciteturn3file0L1-L1 fileciteturn4file0L1-L1 The Jamia Binoria preservation note likewise frames the non-monotonic numbering case as “store as source fact plus a note,” without importing “anomaly” or error-detection semantics into the active modeling rules. fileciteturn9file0L1-L1  
would_change_if: Would downgrade to conditional if “anomaly/surprising/wrong” semantics reappear as first-class labels rather than strictly neutral “source-note / extraction-note” epistemics. fileciteturn3file0L1-L1

axis: 4  
verdict: conditional  
confidence: moderate  
reason: The MVP boundary is now narrow and explicitly recommendation-free (no default path, no ranking/synthesis, no readiness scoring), which is the right integrity posture. fileciteturn3file0L1-L1 fileciteturn4file0L1-L1 The remaining risk is twofold: (a) framing still partially invites a “standalone usefulness” test that can create pressure to smuggle choice-support back in, and (b) the bundle still contains the “structural-only / widely-agreed dependencies” idea, which is a predictable escape hatch when “usefulness without recommendation” feels thin. fileciteturn3file0L1-L1 fileciteturn10file0L1-L1  
would_change_if: Upgrades to valid if Axis 4 is treated as an explicit integrity stress-test (“usefulness only insofar as it does not force system-authored guidance”) *and* the bundle removes the system-owned “widely-agreed dependencies” fallback that would otherwise become the default pressure-release valve. fileciteturn10file0L1-L1

## Overall decision

overall_honest: no  
second_source_required_before_further_work: no  
ready_for_domain_facing_review: no  
blocking_concern: The bundle still contains (in the modelability session) an explicit authorization for a system-owned “structural-only mode” that shows “widely-agreed logical dependencies.” That is an unattributed prerequisite claim, which reintroduces the exact false-authority class the bundle otherwise works hard to exclude. fileciteturn10file0L1-L1  
misuse_risk: The most dangerous likely misuse is a builder (or self-studying student) treating the system as permitted to assert “obvious” universal prerequisites (via the “widely‑agreed dependencies” escape hatch) and then gradually expanding that set—quietly turning the container into a judge while still using “we’re not recommending” disclaimers. fileciteturn10file0L1-L1  
open_note: The governed repo surfaces are internally consistent that the next move is “rerun the external gate,” and the critique registry encodes the same. This is process-coherent, but it does not resolve the remaining bundle-level invariant violation described above. fileciteturn12file0L1-L1 fileciteturn13file0L1-L1 fileciteturn14file0L1-L1

## Repo-grounded summary

- The revised validator packet is materially safer than the earlier preserved critiques describe: it explicitly forbids default/recommendation behavior and explicitly states teacher guidance may be primary for the student while the published source remains visible for comparison. fileciteturn3file0L1-L1  
- The dossier’s authority-boundary model and MVP scope now largely align with “container, not judge,” using neutral note types and editorial groupings rather than authority-loaded taxonomies. fileciteturn4file0L1-L1  
- The non-monotonic-order handling is now framed as literal preservation plus neutral source notes, avoiding “anomaly” framing in the active modeling language. fileciteturn3file0L1-L1 fileciteturn9file0L1-L1  
- The bundle is **not** sealed yet, because the modelability session still proposes a system-owned fallback (“structural-only mode” with “widely-agreed logical dependencies”), which conflicts with the stated invariant that every edge must be attributable to a named source or named teacher path. fileciteturn10file0L1-L1 fileciteturn3file0L1-L1  
- A second curriculum source is still not required *at this stage* (mechanism validation + authority-boundary validation), consistent with the preserved critiques registry; the blocker is coherence/invariants, not breadth. fileciteturn14file0L1-L1  
- The single minimal revision needed before leaving the AI-review loop is to remove (or invert into an explicit prohibition) the “structural-only / widely-agreed dependencies” mode from the modelability session so the full bundle enforces “no system-owned prerequisite edges” as an invariant. fileciteturn10file0L1-L1

## External knowledge notes

- none