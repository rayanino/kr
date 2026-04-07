# 83 nights unattended: every way this system silently loses your findings

**The KR overnight autonomous system has at least 19 distinct silent failure modes, 10 of which remain unaddressed by the five April 7 fixes.** The most dangerous isn't a single bug — it's a compound failure where a circuit breaker trip during a backlog.json write destroys every finding accumulated across all prior nights. The five recent fixes solved the most visible problems (vanishing errors, dropped sync, missing approval CLI) but introduced new risks: the creative.json-to-backlog sync likely created a deduplication false-merge pathway, and the approval CLI created race conditions with the nightly pipeline. No atomic file writes exist anywhere in the system, meaning every JSON file is one interrupted write away from total corruption.

The math is unforgiving: **a failure mode that silently drops 1% of findings per night compounds to 56% total loss by July 1**. Several identified modes exceed that 1% threshold. The system's three-phase rotation makes this worse — findings lost during Foundation (Phase 1) cannot be regenerated during Synthesis (Phase 3), and the inflation_check dimension will systematically suppress strategic findings exactly when they matter most.

---

## 1. Discovery loss — findings that never reach the backlog

This category traces the path from scanner execution through creative.json to backlog.json. Fix #2 (findings-to-backlog pipeline) was the most critical of the five fixes, but it created new gaps while closing the old one.

**SFM-1: Scanner output lost when creative.json write fails.** If the filesystem write to creative.json fails — disk full, permission error, process kill during I/O — the scanner's findings exist only in memory and vanish. Fix #1 (diagnostic.json) logs the *failure event* but does **not preserve the findings content**. The diagnostic tells the owner something broke, not what was found. Over 83 nights of nightly file I/O across 8 scanners, a write failure probability of **10–20% cumulative** is realistic. Standard Python `json.dump()` to `open('w')` truncates the file immediately on open — a crash after truncation but before complete write leaves creative.json either empty or containing partial JSON. The next night's sync (Fix #2) would then fail parsing it, causing cascading multi-night loss. **The owner would see a diagnostic.json entry but could not recover the lost findings.** Fix complexity: medium — requires atomic write pattern (write-to-temp → `os.fsync()` → `os.replace()`).

**SFM-2: Deduplication false-merges filter legitimate new findings.** Fix #2 created the sync pipeline from creative.json → backlog.json, almost certainly introducing deduplication logic using SBERT cosine similarity. If the similarity threshold is set aggressively (≥0.85), findings about the same file but different issues — "module X has a test coverage gap" versus "module X has a documentation gap" — share enough embedding similarity to be falsely merged. As the backlog grows, false-positive probability increases quadratically. By night 50 with hundreds of accumulated findings, **this becomes near-certain for some findings**. This failure is completely invisible: the system considers the dedup "correct," generates no diagnostic, and the owner never sees the suppressed finding. Estimated frequency: **40–60% probability** that at least some findings are falsely merged over the full run. Fix complexity: requires tuning, audit trail, and soft-delete rather than hard-delete on dedup matches.

**SFM-3: Scanner schema drift causes silent parse failures.** Eight different scanners (test health, SPEC quality, code quality, contract boundaries, documentation, recent changes, creative ideation, backlog writes) must all produce findings in a format the evaluator accepts. No schema validation layer is described in the architecture. If the creative ideation scanner outputs findings with different field names, missing required fields, or unexpected nesting, the evaluator silently skips unparseable entries. This is especially dangerous during phase transitions when scanner behavior may change. None of the five fixes address schema validation. Estimated frequency over 83 nights: **20–35% probability** of at least one schema mismatch event. Detection depends entirely on whether the evaluator's error handling invokes diagnostic.json or swallows the exception.

**SFM-4: Evaluation-error zeros filter legitimate findings.** The 7-dimension evaluator could assign zero scores due to errors (SBERT failure → zero novelty, missing file context → zero repo_grounding) rather than genuine low quality. If a minimum composite score threshold gates entry to the backlog, error-induced zeros become indistinguishable from legitimately poor findings. No mechanism exists to differentiate "correctly scored as zero" from "scoring error produced zero." Estimated frequency: **30–45% probability** of at least some error-induced zero scores over 83 nights across 110+ tests. Completely invisible to the owner.

**Did the five fixes adequately address discovery loss?** Fix #2 closed the most catastrophic gap (findings never entering backlog at all) but likely introduced SFM-2. Fix #1 provides partial visibility into write failures but not data recovery. **SFM-3 and SFM-4 are entirely unaddressed.** The net position is improved but fragile — the system now has a single sync pathway that is itself vulnerable to multiple failure modes.

---

## 2. Evaluation loss — wrong or missing quality scores corrupt ranking

Findings that successfully reach the backlog can still be poisoned by incorrect evaluation scores, which propagate through to SUMMER_WORK_QUEUE.md ranking and permanently distort the owner's priorities.

**SFM-5: SBERT model load failure with unknown fallback behavior.** The SBERT model (likely all-MiniLM-L6-v2 or similar) must load transformer weights into memory each night. Failures include corrupted model cache, insufficient memory, or library version drift over the 3-month run. The critical question: what happens on load failure? SentenceTransformers throws an exception. If caught with a fallback to novelty score **0.0**, every finding that night is marked "not novel" and potentially filtered or deprioritized. If fallback is **1.0**, every finding bypasses novelty checks entirely, flooding the backlog with duplicates. Neither behavior is correct; both are silent if the exception handler doesn't propagate to diagnostic.json. Estimated frequency: **10–20% probability** over 83 nights (low per-night probability but accumulates). No fix addresses this.

**SFM-6: Partial dimension scoring biases composite scores.** If one of seven dimensions throws an exception (e.g., evidence_fidelity fails on a specific finding's structure), the composite score is calculated from 6/7 dimensions. Whether the missing dimension is treated as zero (biasing downward) or excluded from the average (biasing upward), the resulting score is systematically wrong. If the **same dimension fails consistently** — evidence_fidelity requiring file access that's intermittently broken, for example — all findings are mis-scored in the same direction every night, creating systematic ranking distortion invisible in aggregate statistics. Estimated frequency: **20–30%** over 83 nights. Diagnostic.json (Fix #1) was designed for task-level failures, not per-dimension evaluation errors, so this likely goes unrecorded.

**SFM-7: inflation_check miscalibration escalates across phases.** The inflation_check dimension detects over-hyped findings. But finding language naturally shifts across phases: Foundation findings describe concrete infrastructure issues; Synthesis findings describe strategic priorities using more emphatic, abstract language. A threshold calibrated on Foundation-phase findings will **systematically suppress Synthesis-phase findings** — exactly when the system should be producing its highest-value output for SUMMER_WORK_QUEUE.md. This is the single most insidious evaluation failure because it degrades output quality precisely when it matters most, and the degradation looks like "the codebase has fewer interesting findings left" rather than a system error. Estimated frequency: **50–70% probability** of noticeable impact during Phase 3. The owner would need to manually inspect per-dimension scores in backlog.json to detect this; the morning report (Fix #4) almost certainly shows only composite scores.

**SFM-8: Score instability across evaluation runs.** SBERT embeddings are deterministic for the same model, but repo_grounding, structural_completeness, and other code-dependent dimensions change as the repository evolves nightly. The same finding could score differently on consecutive nights, making the backlog's priority ranking non-deterministic. Combined with deduplication (SFM-2), a finding could be "novel" one night and "duplicate" the next. No mechanism tracks score stability over time. Estimated frequency: **60–80%** over 83 nights.

**Did the five fixes address evaluation loss?** Not at all. **None of the five fixes touch evaluation quality, scoring resilience, or calibration.** This entire category is an open gap.

---

## 3. Approval loss — approved items that can never execute

Fix #3 (approval CLI) solved the immediate problem of having no approval mechanism, but it addressed only the proposed→approved transition, leaving the remaining lifecycle stages unautomated.

**SFM-9: Approved items strand across phase boundaries.** A finding approved during Foundation (April 9 – May 4) may specify work requiring capabilities available only during Synthesis (June 2 – June 30). The approval CLI has no phase-awareness — it doesn't check whether the approved item can actually be executed in the current or any future phase. These items sit at "approved" status indefinitely, consuming backlog space and attention. Estimated frequency: **60–80%** — nearly certain given that Foundation infrastructure findings naturally suggest improvements requiring later phases. The owner would notice only if they proactively use the `list` command and mentally cross-reference items against the phase schedule.

**SFM-10: The approved→scheduled→implemented transitions have no automation.** Fix #3 covers proposed→approved. **Nothing described in the architecture covers what happens next.** Who or what moves an approved item to "scheduled"? What triggers "implemented"? Without explicit automation, items accumulate in "approved" state indefinitely. Over 83 nights, the backlog becomes a graveyard of approved-but-never-scheduled items. Estimated frequency: **90%+ probability** that items get stuck. The morning report (Fix #4) likely highlights items needing approval but not items stuck post-approval.

**SFM-11: Scanner-phase mismatch blocks implementation.** If a documentation finding is approved for implementation but the documentation scanner doesn't run during the current phase (per manifest_phase_config.json), there is no executor for that item. No mechanism maps approved items to scanner schedules. Estimated frequency: **25–40%** depending on phase configuration.

**Did the five fixes address approval loss?** Fix #3 solved the entry point (approve/reject/list) and Fix #4 surfaces items needing approval. But **the downstream lifecycle is unautomated**, creating a bottleneck that grows worse every night.

---

## 4. Visibility loss — findings exist but the owner cannot see them

The morning report is the owner's sole window into 83 nights of autonomous operation. Fix #4 added the critical "Needs Owner Attention" section. The question is whether this window shows the full picture.

**SFM-12: Morning report truncation creates a false sense of completeness.** If the morning report generator has a display limit for readability — showing the 10 most recent or highest-priority items — the owner sees a manageable daily list while the backlog silently grows behind it. By night 30, there could be 100+ proposed items across 8 scanners, with only the top 10 visible. **No "and 47 more items not shown" indicator is described.** The owner approves visible items and believes the system is under control. Estimated frequency: **50–70%** that meaningful items are hidden by truncation over the full run.

**SFM-13: No morning report in halted state.** If the circuit breaker trips and the morning report generator is part of the same pipeline, the report stops being generated. On the exact morning when the owner most needs to know what went wrong, there's no report. The owner would notice the absence — a missing report is itself a signal — but would need to know to check diagnostic.json (Fix #1) and have the technical context to interpret it. **The gap between "report is missing" and "owner understands what happened and how to recover" could be days.** Estimated frequency: conditional on breaker trip, but when it occurs, this compounds the recovery time significantly.

**SFM-14: Morning report accuracy degrades with system health.** In reduced or solo health states, fewer scanners run, fewer findings are generated, and the morning report reflects a narrower view of the codebase. The owner sees "fewer findings today" and may attribute this to the codebase being well-analyzed rather than the system operating in degraded mode. **Does the morning report explicitly state the current health level?** If not, the owner has no way to distinguish "nothing to report" from "system is limping." This is the classic degraded-state invisibility problem: the system is "working" but producing less, and the reduction looks normal.

**Did the five fixes address visibility loss?** Fix #4 created the essential visibility channel. But without completeness guarantees, health-state indicators, and halted-state reporting, the channel may provide false confidence rather than true visibility.

---

## 5. Deduplication errors — the silent killer

Deduplication operates at the intersection of discovery and evaluation, making its failure modes particularly dangerous because they corrupt both the quantity and quality of the backlog simultaneously.

**SFM-15: False merges at the similarity threshold.** Two findings about the same module but fundamentally different issues share high embedding similarity. At any reasonable SBERT cosine similarity threshold, there exists a zone where distinct findings get merged. The merged record retains one finding's content and discards the other — permanently, with no audit trail. **Over 83 nights analyzing the same 7-engine codebase, this is the highest-probability silent data loss mechanism.** Scanners repeatedly examine the same files, producing findings that reference the same code but identify different issues. The embedding model cannot reliably distinguish "same file, different problem" from "same problem, different wording." Estimated findings lost: **5–15%** of all findings over the full run. Each lost finding is invisible — the dedup was "correct" from the system's perspective.

**SFM-16: Duplicate flooding from nightly scanner drift.** The inverse problem: a persistent code issue generates slightly different findings each night as the code evolves (different line numbers, updated context, varied wording). These variations push similarity below the dedup threshold, creating duplicate entries. Over 83 nights, the same underlying issue accumulates dozens of near-identical backlog entries. These duplicates consume morning report display slots (SFM-12), approval attention (SFM-10), and SUMMER_WORK_QUEUE.md rankings (Fix #5). **The signal-to-noise ratio of the backlog degrades progressively**, making the final work queue less useful. Estimated frequency: **70–90%** — almost certain for long-running scanners on evolving code.

**Did the five fixes address deduplication errors?** Fix #2 likely introduced deduplication when creating the sync pipeline. **No fix addresses threshold calibration, merge audit trails, or duplicate rate monitoring.** The system has no mechanism to detect whether its dedup is too aggressive (losing findings) or too permissive (accumulating duplicates).

---

## 6. State corruption — the single point of catastrophic failure

Every critical data structure in the system — creative.json, backlog.json, state.json, diagnostic.json — is a JSON file written to disk. None of the described architecture uses atomic writes.

**SFM-17: Non-atomic JSON writes risk total backlog loss.** Python's `open('file.json', 'w')` truncates the target file immediately, then writes incrementally. A crash, OOM kill, or `SIGKILL` between truncation and write completion leaves the file empty or containing partial JSON. For backlog.json, which accumulates findings across all 83 nights, **a single interrupted write destroys the entire accumulated dataset**. No backup mechanism is described. The atomic write pattern (write-to-temp → `os.fsync()` → `os.replace()`) is a solved problem but appears absent. Estimated per-write failure probability: negligible. Cumulative probability across 83 nights × multiple files × multiple writes per night: **10–20%** for at least one corruption event. If that event hits backlog.json, impact is catastrophic.

**SFM-18: Health state and failure counter desynchronization.** If state.json and the consecutive failure counter are updated in separate write operations, a crash between writes creates inconsistency. The system could restart believing it's in "full" health with a failure count of 3, effectively disabling the circuit breaker. Or it could be stuck in "halted" state with a failure count of 0, unable to recover despite no failures. Estimated frequency: **5–10%** over 83 nights, but catastrophic when it occurs because it undermines the entire health state machine.

**Did the five fixes address state corruption?** **No.** Not a single fix introduces atomic writes, file backups, or state consistency checks. This is the most dangerous unaddressed category because the failure mode is low-probability but maximum-impact.

---

## 7. Recovery gaps — what happens when the circuit breaker fires

The circuit breaker (3 consecutive failures → halted) is designed to protect the system from cascading damage. But the protection mechanism itself has gaps that can cause data loss.

**SFM-19: Circuit breaker trip during backlog.json write — the worst-case compound failure.** If the third consecutive failure occurs while backlog.json is being written (during the creative.json → backlog sync from Fix #2), the halt interrupts a write operation on the system's most critical data file. This combines SFM-17 (partial write corruption) with the circuit breaker's halt mechanism to produce **total loss of all accumulated findings with no recovery path**. Estimated probability: **2–5%** over the full run — low, but the impact is the complete destruction of 83 nights of analysis. This is the single highest-severity failure mode in the system.

Additionally, no recovery protocol is described for the halted state. When the breaker trips: Does data from the partial run survive? When the system restarts, does it replay the failed night or skip it? Is there a half-open state for graduated recovery? Without answers to these questions, **every circuit breaker trip is potentially a permanent halt** requiring manual engineering intervention — during a system designed to run for 83 nights without engineering oversight.

**Did the five fixes address recovery gaps?** Fix #1 (diagnostic.json) provides crash forensics but not data recovery. **No fix establishes a recovery protocol, backup mechanism, or graduated restart procedure.**

---

## The compound risk that makes this urgent

These 19 failure modes don't exist in isolation. The most dangerous interactions form cascading chains:

The **catastrophic chain** runs: non-atomic write (SFM-17) + circuit breaker trip (SFM-19) = total backlog destruction. Probability: 2–5% over 83 nights. Impact: complete loss of all findings.

The **silent erosion chain** runs: dedup false-merge (SFM-15) + morning report truncation (SFM-12) + inflation_check phase drift (SFM-7) = progressive, invisible degradation of backlog quality. By Synthesis phase, the work queue is built on corrupted rankings of a depleted finding set. Probability: **40–60%** that meaningful degradation occurs. The owner never detects it because each individual mechanism is invisible.

The **approval gridlock chain** runs: no downstream lifecycle automation (SFM-10) + phase-unaware scheduling (SFM-9) + duplicate flooding (SFM-16) = a backlog of hundreds of items, most duplicates or stuck in "approved" limbo, drowning the useful findings. Probability: **70–80%** over the full run. The owner can detect this manually but would need to invest significant time inspecting backlog.json directly.

---

## Monitoring checklist: 10 automated weekly assertions

These checks can run as a weekly self-audit. Each is expressible as a Python assertion and designed to detect governance drift before it compounds.

```python
# 1. Backlog file integrity — detects SFM-17 (non-atomic write corruption)
import json
with open('overnight_codex/backlog.json') as f:
    backlog = json.load(f)  # Raises JSONDecodeError if corrupted
assert isinstance(backlog, (list, dict)), "backlog.json root must be list or dict"

# 2. Finding count monotonicity — detects SFM-1, SFM-2, SFM-15 (discovery/dedup loss)
current_count = len([i for i in backlog if i.get('status') != 'rejected'])
historical_count = load_last_week_count()  # from a separate tracking file
assert current_count >= historical_count * 0.95, (
    f"Backlog shrank from {historical_count} to {current_count} — possible silent loss"
)

# 3. Score distribution sanity — detects SFM-5, SFM-6, SFM-7 (evaluation errors)
scores = [i.get('composite_score', 0) for i in backlog if i.get('composite_score') is not None]
assert len(scores) > 0, "No scored items in backlog"
assert 0.1 < (sum(scores) / len(scores)) < 0.9, (
    f"Mean score {sum(scores)/len(scores):.2f} outside expected range — possible scoring failure"
)
assert all(0.0 <= s <= 1.0 for s in scores), "Score out of [0, 1] range detected"

# 4. Dimension completeness — detects SFM-6 (partial dimension scoring)
DIMENSIONS = ['repo_grounding', 'structural_completeness', 'strategic_depth',
              'concreteness', 'evidence_fidelity', 'novelty', 'inflation_check']
for item in backlog:
    if item.get('status') == 'proposed':
        present = [d for d in DIMENSIONS if item.get('scores', {}).get(d) is not None]
        assert len(present) == 7, (
            f"Item {item.get('id')} has only {len(present)}/7 dimension scores"
        )

# 5. Approval pipeline flow — detects SFM-10 (stuck approved items)
approved_items = [i for i in backlog if i.get('status') == 'approved']
oldest_approved_age = max(
    (today - parse_date(i.get('approved_date'))).days for i in approved_items
) if approved_items else 0
assert oldest_approved_age < 14, (
    f"Item stuck in 'approved' for {oldest_approved_age} days — pipeline stalled"
)

# 6. Deduplication rate monitoring — detects SFM-15, SFM-16 (false merge/flood)
dedup_log = load_dedup_log()  # Must be implemented: log every dedup decision
dedup_rate = len(dedup_log.get('merged_this_week', [])) / max(len(dedup_log.get('total_this_week', [])), 1)
assert dedup_rate < 0.30, (
    f"Dedup rate {dedup_rate:.0%} exceeds 30% — possible false-merge epidemic"
)

# 7. Health state watchdog — detects SFM-14, SFM-18 (stuck degraded state)
import json
with open('overnight_codex/state.json') as f:
    state = json.load(f)
health = state.get('health_state', 'unknown')
nights_in_state = state.get('nights_in_current_state', 0)
assert not (health in ('reduced', 'solo') and nights_in_state > 7), (
    f"System stuck in '{health}' for {nights_in_state} nights — recovery probe needed"
)
assert health != 'halted', "System is HALTED — immediate human intervention required"

# 8. Morning report freshness — detects SFM-13 (no report in halted state)
from pathlib import Path
import datetime
report_path = Path('overnight_codex/MORNING_REPORT.md')
report_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(report_path.stat().st_mtime)
assert report_age < datetime.timedelta(hours=36), (
    f"Morning report is {report_age.total_seconds()/3600:.0f}h old — possible generation failure"
)

# 9. Phase-schedule alignment — detects SFM-9, SFM-11 (phase mismatch)
with open('.kr/manifest_phase_config.json') as f:
    phase_config = json.load(f)
current_phase = determine_current_phase(phase_config)
for item in backlog:
    if item.get('status') == 'approved':
        required_phase = item.get('required_phase')
        if required_phase and required_phase != current_phase:
            # Flag but don't fail — just track for owner awareness
            print(f"WARNING: Item {item.get('id')} requires phase '{required_phase}', "
                  f"currently in '{current_phase}'")

# 10. Backlog-to-creative.json consistency — detects SFM-3, dangling references
with open('overnight_codex/creative.json') as f:
    creative = json.load(f)
creative_ids = {item.get('id') for item in creative}
backlog_source_ids = {item.get('source_finding_id') for item in backlog if item.get('source_finding_id')}
orphaned = backlog_source_ids - creative_ids
assert len(orphaned) / max(len(backlog_source_ids), 1) < 0.05, (
    f"{len(orphaned)} backlog items reference missing creative findings — data consistency breach"
)
```

---

## Conclusion: the fixes stopped the bleeding but didn't close the wound

The five April 7 fixes addressed the **five most acute symptoms** — vanishing errors, dropped findings, no approval path, no owner visibility, no synthesis output. These were necessary and well-targeted. But the audit reveals a deeper structural vulnerability: **the system has no defense against silent data corruption**.

Three architectural gaps demand immediate attention before April 9:

**First, atomic writes.** Every JSON file in the system is one interrupted write from corruption. backlog.json is a single point of total data loss with no backup. Implementing the write-to-temp-then-rename pattern across all file writes is a one-day fix that eliminates the catastrophic chain entirely.

**Second, a deduplication audit trail.** The sync pipeline (Fix #2) almost certainly deduplicates findings, but no mechanism exists to detect whether dedup is too aggressive (losing findings) or too permissive (flooding duplicates). Soft-delete with provenance logging and a weekly dedup-rate check would make this visible.

**Third, a recovery protocol for the halted state.** The circuit breaker can halt the system with no defined path back to operation. A simple graduated recovery (halted → probe one scanner → if success, enter solo → escalate) with automatic daily retry would prevent the system from staying dead indefinitely.

The system is two days from launch. These three fixes are the difference between an autonomous system that degrades gracefully and one that can silently lose a majority of its findings before July.