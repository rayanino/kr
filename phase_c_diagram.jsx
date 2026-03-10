import { useState } from "react";

const phases = [
  {
    id: "prereqs",
    title: "PHASE 1: Pre-Requisites",
    color: "#3b82f6",
    bgColor: "#1e3a5f",
    borderColor: "#2563eb",
    icon: "🔧",
    duration: "~30 min",
    cost: "€0",
    steps: [
      {
        id: "0a",
        title: "Fix build_prompt_context",
        file: "metadata_inference.py",
        detail: "Fix muhaqiq_name → muhaqiq_name_raw, edition → edition_raw. Add 5 new fields (compiler, commentator, riwayah, edition years).",
        why: "54% of books have muhaqiq data the LLM NEVER sees",
        test: "Run build_prompt_context on fixture 02 → must show 'Muhaqiq/Editor:'",
        blocker: true,
      },
      {
        id: "0b",
        title: "Update SYSTEM_MESSAGE",
        file: "inference_v1.py",
        detail: "Add compiler vs author guidance, commentator → multi-layer evidence, riwayah → distinct works.",
        why: "LLM may confuse compiler (ابن قاسم) with author (ابن تيمية)",
        test: "3-book test checks for regressions. REVERT if genre/author results change unexpectedly.",
        blocker: false,
        revertible: true,
      },
      {
        id: "1",
        title: "Add temperature=0",
        file: "consensus.py → _call_model",
        detail: "Add temperature=0 to client.create() call.",
        why: "Deterministic output, less token waste, reproducible results",
        test: "Verify Instructor passes temperature through in API logs",
        blocker: false,
      },
      {
        id: "2",
        title: "Expose ConsensusResult",
        file: "metadata_inference.py",
        detail: "Add _full_consensus_result field to MetadataInferenceResult. Save it after evaluate() call.",
        why: "Phase C script needs per-model LLM responses for diagnostics",
        test: "Existing 768+ tests still pass",
        blocker: false,
      },
      {
        id: "3",
        title: "Format B test fixture",
        file: "tests/fixtures/shamela_real/13_format_b/",
        detail: "Create synthetic .htm with Format B metadata card. Add ground truth + unit test.",
        why: "Bug fix for 64 books has no regression test",
        test: "New test passes, existing tests pass",
        blocker: false,
      },
      {
        id: "4",
        title: "Create COST_LOG.json",
        file: "tests/results/source_engine/COST_LOG.json",
        detail: "Initialize with Phase 0 (€1.80 complete) and Phase A (€0 complete).",
        why: "Budget tracking — script refuses to start if over budget",
        test: "File exists, valid JSON",
        blocker: false,
      },
    ],
    gate: "ALL 768+ existing tests pass after each pre-req",
  },
  {
    id: "script",
    title: "PHASE 2: Write run_phase_c.py",
    color: "#8b5cf6",
    bgColor: "#2d1b69",
    borderColor: "#7c3aed",
    icon: "📝",
    duration: "~1 hour",
    cost: "€0",
    steps: [
      {
        id: "s1",
        title: "CLI argument parsing",
        detail: "--books, --book, --resume, --force, --dry-run, --output-dir, --budget-eur. Env var checks for ANTHROPIC_API_KEY + OPENROUTER_API_KEY.",
      },
      {
        id: "s2",
        title: "Book resolution",
        detail: "Read phase_c_books.txt, resolve each name against COLLECTION_DIR, verify all 73 directories exist before processing.",
      },
      {
        id: "s3",
        title: "Monkey-patch setup",
        detail: "Patch engine_mod.infer_metadata with _capturing_infer. Module-level global _captured_inference with proper global declaration.",
      },
      {
        id: "s4",
        title: "process_book() function",
        detail: "Create temp library → configure human_gate → detect_format + extract → save extraction.json → save prompt_sent.json → acquire_source → save all results",
      },
      {
        id: "s5",
        title: "Error handling",
        detail: "Catch SourceEngineError(LOW_CONFIDENCE) → status: gate_abort. Catch all other exceptions → status: error. First book API fail → abort. 3 consecutive API fails → abort.",
      },
      {
        id: "s6",
        title: "Budget protection",
        detail: "Pre-flight estimate, per-book tracking via API usage headers, rolling check every 5 books, COST_LOG update per book, hard ceiling.",
      },
      {
        id: "s7",
        title: "Sanity checks",
        detail: "6 deterministic checks per book: multi_layer_no_layers, author_blank, death_date_mismatch, genre_title_mismatch, muhaqiq_not_in_context, high_conf_sparse.",
      },
      {
        id: "s8",
        title: "Summary generation",
        detail: "PHASE_C_MANIFEST.json + PHASE_C_SUMMARY.json with edition_groups and sanity_check_summary after all books complete.",
      },
    ],
    gate: "Script runs without import errors, --dry-run works",
  },
  {
    id: "test3",
    title: "PHASE 3: 3-Book Test Gate",
    color: "#f59e0b",
    bgColor: "#4a3500",
    borderColor: "#d97706",
    icon: "🧪",
    duration: "~5 min",
    cost: "~€0.45",
    steps: [
      {
        id: "t1",
        title: "Book 1: أحكام الاضطباع والرمل في الطواف",
        detail: "Fixture 03_fiqh. Has ground truth. Tests: full pipeline, ground_truth_comparison.json generated, all output files present.",
        expect: "status: success, ground truth match",
      },
      {
        id: "t2",
        title: "Book 2: الأربعون النووية",
        detail: "Famous matn, no ground truth. Clean run expected. Tests: LLM produces sensible genre (matn), author (النووي d.676), correct confidence levels.",
        expect: "status: success, genre=matn",
      },
      {
        id: "t3",
        title: "Book 3: الفقه الأكبر",
        detail: "Disputed attribution. Tests: pipeline triggers validation gate (LOW_CONFIDENCE), script catches it correctly, LLM responses still captured.",
        expect: "status: gate_abort, llm_responses/ present",
      },
    ],
    gate: "ALL 14 items in 3-Book Test Checklist pass",
    gateItems: [
      "extraction.json has all fields incl. _ debug fields",
      "prompt_sent.json saved BEFORE API call",
      "prompt_sent.json shows muhaqiq_name_raw in fields_present (when applicable)",
      "llm_responses/ has full per-model InferenceOutput",
      "consensus.json has agreement details",
      "result.json has complete SourceMetadata",
      "ground_truth_comparison.json for book 1",
      "COST_LOG.json updated per book",
      "Resume skips all 3 books",
      "Force re-runs all 3 books",
      "Cost per book €0.07–0.15",
      "API failure → extraction.json + prompt_sent.json still present",
      "Book 3 → gate_abort (not error) + llm_responses saved",
      "Resume skips gate_abort book",
    ],
  },
  {
    id: "full",
    title: "PHASE 4: Full 73-Book Run",
    color: "#10b981",
    bgColor: "#064e3b",
    borderColor: "#059669",
    icon: "🚀",
    duration: "~15 min",
    cost: "~€11",
    steps: [
      {
        id: "f1",
        title: "Run with --resume",
        detail: "Skips the 3 books already processed in the test phase. Processes remaining 70 books sequentially.",
      },
      {
        id: "f2",
        title: "Monitor progress",
        detail: "Watch for: API errors (3 consecutive = abort), budget warnings (every 5 books), rate limit pauses.",
      },
      {
        id: "f3",
        title: "Per-book output",
        detail: "Each book produces: extraction.json, prompt_sent.json, llm_responses/, consensus.json, result.json, sanity_checks.json. Ground truth comparison for 12 fixture books.",
      },
      {
        id: "f4",
        title: "Generate summaries",
        detail: "PHASE_C_MANIFEST.json (73 books), PHASE_C_SUMMARY.json (aggregate stats + edition_groups + sanity_check_summary).",
      },
    ],
    gate: "0 crashes, all 73 books have result.json",
  },
  {
    id: "commit",
    title: "PHASE 5: Commit & Done",
    color: "#ec4899",
    bgColor: "#4a1942",
    borderColor: "#db2777",
    icon: "✅",
    duration: "~5 min",
    cost: "€0",
    steps: [
      {
        id: "c1",
        title: "Verify test suite",
        detail: "All 768+ existing tests still pass. No regressions from pre-req changes.",
      },
      {
        id: "c2",
        title: "Commit all changes",
        detail: "Pre-req code changes + scripts/run_phase_c.py + COST_LOG.json + all 73-book results in tests/results/source_engine/phase_c/",
      },
      {
        id: "c3",
        title: "Update COST_LOG.json",
        detail: "Phase C: books=73, cost_eur=actual, status=complete. Total updated.",
      },
    ],
    gate: "Everything committed and pushed",
  },
];

const perBookFlow = [
  { id: "pb1", label: "Create temp library", group: "pre", cost: false },
  { id: "pb2", label: "Configure human_gate\n(auto_approve=True)", group: "pre", cost: false },
  { id: "pb3", label: "detect_format()", group: "pre", cost: false },
  { id: "pb4", label: "extract_metadata()", group: "pre", cost: false },
  { id: "pb5", label: "💾 SAVE extraction.json", group: "save", cost: false },
  { id: "pb6", label: "build_prompt_context()", group: "pre", cost: false },
  { id: "pb7", label: "💾 SAVE prompt_sent.json", group: "save", cost: false },
  { id: "pb8", label: "Reset _captured_inference", group: "pipeline", cost: false },
  { id: "pb9", label: "acquire_source()\n(Steps 1-13)", group: "pipeline", cost: true },
  { id: "pb10", label: "💾 SAVE llm_responses/", group: "save", cost: false },
  { id: "pb11", label: "💾 SAVE consensus.json", group: "save", cost: false },
  { id: "pb12", label: "💾 SAVE result.json", group: "save", cost: false },
  { id: "pb13", label: "Ground truth comparison\n(if fixture match)", group: "post", cost: false },
  { id: "pb14", label: "Run 6 sanity checks", group: "post", cost: false },
  { id: "pb15", label: "💾 SAVE sanity_checks.json", group: "save", cost: false },
  { id: "pb16", label: "Update COST_LOG.json", group: "post", cost: false },
];

const groupColors = {
  pre: { bg: "#1e3a5f", border: "#3b82f6", label: "Pre-pipeline (€0)" },
  save: { bg: "#1a3d1f", border: "#4ade80", label: "Save to disk" },
  pipeline: { bg: "#4a1942", border: "#ec4899", label: "API calls (€€)" },
  post: { bg: "#3d2e0a", border: "#f59e0b", label: "Post-pipeline (€0)" },
};

function PhaseCard({ phase, expanded, onToggle }) {
  return (
    <div style={{ marginBottom: 16, border: `1px solid ${phase.borderColor}`, borderRadius: 12, background: phase.bgColor, overflow: "hidden" }}>
      <div onClick={onToggle} style={{ padding: "16px 20px", cursor: "pointer", display: "flex", alignItems: "center", gap: 14, userSelect: "none" }}>
        <span style={{ fontSize: 24 }}>{phase.icon}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: "#e4e4e7", fontFamily: "'IBM Plex Sans', sans-serif" }}>{phase.title}</div>
          <div style={{ fontSize: 12, color: "#888", fontFamily: "'IBM Plex Mono', monospace", marginTop: 2 }}>
            {phase.duration} · {phase.cost} · {phase.steps.length} steps
          </div>
        </div>
        <div style={{ color: "#555", fontSize: 16, transition: "transform 0.2s", transform: expanded ? "rotate(180deg)" : "rotate(0)" }}>▾</div>
      </div>

      {expanded && (
        <div style={{ padding: "0 20px 20px", borderTop: `1px solid ${phase.borderColor}44` }}>
          {phase.steps.map((step, i) => (
            <div key={step.id} style={{ display: "flex", gap: 12, padding: "10px 0", borderBottom: i < phase.steps.length - 1 ? "1px solid #ffffff0a" : "none" }}>
              <div style={{ width: 32, height: 32, borderRadius: 6, background: phase.borderColor + "22", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: phase.color, fontFamily: "'IBM Plex Mono', monospace", flexShrink: 0 }}>
                {step.id}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: "#ddd", fontFamily: "'IBM Plex Sans', sans-serif" }}>{step.title}</span>
                  {step.blocker && <span style={{ fontSize: 9, fontWeight: 700, padding: "1px 6px", borderRadius: 3, background: "#dc2626", color: "#fff", letterSpacing: 0.8 }}>BLOCKER</span>}
                  {step.revertible && <span style={{ fontSize: 9, fontWeight: 700, padding: "1px 6px", borderRadius: 3, background: "#d97706", color: "#fff", letterSpacing: 0.8 }}>REVERTIBLE</span>}
                </div>
                {step.file && <div style={{ fontSize: 11, color: "#888", fontFamily: "'IBM Plex Mono', monospace", marginTop: 2 }}>{step.file}</div>}
                <div style={{ fontSize: 12, color: "#aaa", marginTop: 4, lineHeight: 1.5, fontFamily: "'IBM Plex Sans', sans-serif" }}>{step.detail}</div>
                {step.why && <div style={{ fontSize: 11, color: phase.color, marginTop: 4, fontFamily: "'IBM Plex Sans', sans-serif" }}>WHY: {step.why}</div>}
                {step.expect && <div style={{ fontSize: 11, color: "#4ade80", marginTop: 4, fontFamily: "'IBM Plex Mono', monospace" }}>EXPECT: {step.expect}</div>}
                {step.test && <div style={{ fontSize: 11, color: "#888", marginTop: 4, fontFamily: "'IBM Plex Mono', monospace" }}>TEST: {step.test}</div>}
              </div>
            </div>
          ))}

          <div style={{ marginTop: 12, padding: "10px 14px", background: "#0a0a0f", borderRadius: 8, borderLeft: `3px solid ${phase.borderColor}` }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: phase.color, letterSpacing: 1, textTransform: "uppercase", marginBottom: 4, fontFamily: "'IBM Plex Mono', monospace" }}>GO / NO-GO Gate</div>
            <div style={{ fontSize: 12, color: "#ccc", fontFamily: "'IBM Plex Sans', sans-serif" }}>{phase.gate}</div>
          </div>

          {phase.gateItems && (
            <div style={{ marginTop: 8, padding: "10px 14px", background: "#0a0a0f", borderRadius: 8 }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: "#f59e0b", letterSpacing: 1, marginBottom: 6, fontFamily: "'IBM Plex Mono', monospace" }}>14-ITEM CHECKLIST</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "3px 12px" }}>
                {phase.gateItems.map((item, i) => (
                  <div key={i} style={{ fontSize: 10, color: "#999", fontFamily: "'IBM Plex Mono', monospace", padding: "2px 0" }}>
                    ☐ {item}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function PerBookFlow() {
  return (
    <div style={{ margin: "0 0 24px", padding: "20px 24px", background: "#111116", borderRadius: 12, border: "1px solid #222" }}>
      <div style={{ fontSize: 13, color: "#aaa", letterSpacing: 1, textTransform: "uppercase", marginBottom: 6, fontFamily: "'IBM Plex Mono', monospace" }}>Per-Book Processing Flow</div>
      <div style={{ fontSize: 11, color: "#666", marginBottom: 16, fontFamily: "'IBM Plex Sans', sans-serif" }}>This runs 73 times. The red step is the only one that costs money.</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {perBookFlow.map((step, i) => {
          const gc = groupColors[step.group];
          return (
            <div key={step.id} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 24, textAlign: "center", fontSize: 10, color: "#555", fontFamily: "'IBM Plex Mono', monospace" }}>{i + 1}</div>
              <div style={{ flex: 1, padding: "6px 12px", background: gc.bg, borderRadius: 6, borderLeft: `3px solid ${gc.border}`, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span style={{ fontSize: 12, color: step.cost ? "#ec4899" : "#ccc", fontWeight: step.cost ? 700 : 400, fontFamily: "'IBM Plex Mono', monospace", whiteSpace: "pre-line" }}>{step.label}</span>
                {step.cost && <span style={{ fontSize: 9, padding: "1px 6px", borderRadius: 3, background: "#dc2626", color: "#fff", fontWeight: 700, letterSpacing: 0.8 }}>€€€</span>}
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ display: "flex", gap: 16, marginTop: 12, flexWrap: "wrap" }}>
        {Object.entries(groupColors).map(([key, gc]) => (
          <div key={key} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 12, height: 12, borderRadius: 2, background: gc.bg, border: `1px solid ${gc.border}` }} />
            <span style={{ fontSize: 10, color: "#777", fontFamily: "'IBM Plex Mono', monospace" }}>{gc.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ErrorFlows() {
  const flows = [
    { trigger: "API auth fail on book 1", action: "ABORT entire run", status: "error", color: "#dc2626" },
    { trigger: "3 consecutive API fails", action: "ABORT with partial results", status: "error", color: "#dc2626" },
    { trigger: "Both models + fallback fail", action: "Save error, continue to next book", status: "error", color: "#f59e0b" },
    { trigger: "LOW_CONFIDENCE gate (e.g. disputed)", action: "Save gate_abort, continue to next", status: "gate_abort", color: "#8b5cf6" },
    { trigger: "Parse error (Instructor)", action: "Retry with simplified prompt, then error", status: "error", color: "#f59e0b" },
    { trigger: "Budget ceiling hit", action: "STOP, save all processed results", status: "n/a", color: "#dc2626" },
    { trigger: "Script crash mid-run", action: "--resume skips success + gate_abort", status: "n/a", color: "#3b82f6" },
  ];

  return (
    <div style={{ margin: "0 0 24px", padding: "20px 24px", background: "#111116", borderRadius: 12, border: "1px solid #222" }}>
      <div style={{ fontSize: 13, color: "#aaa", letterSpacing: 1, textTransform: "uppercase", marginBottom: 12, fontFamily: "'IBM Plex Mono', monospace" }}>Error & Recovery Flows</div>
      {flows.map((f, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 0", borderBottom: i < flows.length - 1 ? "1px solid #ffffff08" : "none" }}>
          <div style={{ width: 8, height: 8, borderRadius: 4, background: f.color, flexShrink: 0 }} />
          <div style={{ flex: 1, fontSize: 12, color: "#bbb", fontFamily: "'IBM Plex Sans', sans-serif" }}>{f.trigger}</div>
          <div style={{ fontSize: 11, color: "#888", fontFamily: "'IBM Plex Mono', monospace" }}>→ {f.action}</div>
          {f.status !== "n/a" && (
            <div style={{ fontSize: 9, padding: "1px 6px", borderRadius: 3, background: f.color + "22", color: f.color, fontWeight: 600, fontFamily: "'IBM Plex Mono', monospace", flexShrink: 0 }}>{f.status}</div>
          )}
        </div>
      ))}
    </div>
  );
}

export default function PhaseC_Diagram() {
  const [expanded, setExpanded] = useState({ prereqs: true, test3: true });
  const [view, setView] = useState("phases");

  const togglePhase = (id) => setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));

  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0f", color: "#e4e4e7", fontFamily: "'IBM Plex Sans', -apple-system, sans-serif", padding: "24px 20px", maxWidth: 820, margin: "0 auto" }}>
      <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />

      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, margin: "0 0 4px", fontFamily: "'IBM Plex Sans', sans-serif" }}>Phase C — Full Execution Plan</h1>
        <p style={{ fontSize: 13, color: "#777", margin: 0, fontFamily: "'IBM Plex Mono', monospace" }}>
          Claude Code session · 73 books · ~€11 · ~2 hours total
        </p>
      </div>

      <div style={{ display: "flex", gap: 4, marginBottom: 20 }}>
        {["phases", "per-book", "errors"].map((v) => (
          <button key={v} onClick={() => setView(v)} style={{ padding: "6px 14px", borderRadius: 6, border: `1px solid ${view === v ? "#4ade80" : "#333"}`, background: view === v ? "#4ade8015" : "transparent", color: view === v ? "#4ade80" : "#777", fontSize: 12, fontFamily: "'IBM Plex Mono', monospace", cursor: "pointer", fontWeight: view === v ? 600 : 400 }}>
            {v === "phases" ? "5 Phases" : v === "per-book" ? "Per-Book Flow" : "Error Flows"}
          </button>
        ))}
      </div>

      {view === "phases" && (
        <>
          <div style={{ display: "flex", alignItems: "center", gap: 4, marginBottom: 20, overflowX: "auto", paddingBottom: 4 }}>
            {phases.map((p, i) => (
              <div key={p.id} style={{ display: "flex", alignItems: "center", gap: 4, flexShrink: 0 }}>
                <div style={{ padding: "6px 12px", borderRadius: 6, background: p.bgColor, border: `1px solid ${p.borderColor}`, textAlign: "center", minWidth: 70 }}>
                  <div style={{ fontSize: 16 }}>{p.icon}</div>
                  <div style={{ fontSize: 9, color: p.color, fontWeight: 700, fontFamily: "'IBM Plex Mono', monospace", marginTop: 2 }}>{p.cost}</div>
                </div>
                {i < phases.length - 1 && <div style={{ color: i < 2 ? "#555" : i === 2 ? "#f59e0b" : "#4ade80", fontSize: 14 }}>→</div>}
              </div>
            ))}
          </div>
          {phases.map((phase) => (
            <PhaseCard key={phase.id} phase={phase} expanded={!!expanded[phase.id]} onToggle={() => togglePhase(phase.id)} />
          ))}
        </>
      )}

      {view === "per-book" && <PerBookFlow />}
      {view === "errors" && <ErrorFlows />}

      <div style={{ marginTop: 24, padding: "16px 20px", background: "#111116", borderRadius: 12, border: "1px solid #1a5c2e" }}>
        <div style={{ fontSize: 13, color: "#4ade80", fontWeight: 700, fontFamily: "'IBM Plex Mono', monospace", marginBottom: 8 }}>COST PROTECTION SUMMARY</div>
        <div style={{ fontSize: 12, color: "#999", lineHeight: 1.7, fontFamily: "'IBM Plex Sans', sans-serif" }}>
          3-book test gate (€0.45) catches bugs before the full run (€11). Budget hard ceiling at €50.
          Per-book COST_LOG updates survive crashes. Rolling projection check every 5 books.
          Sequential processing means no concurrent API calls — rate limits never hit.
          Pre-pipeline saves (extraction.json + prompt_sent.json) happen BEFORE any API call — zero data loss on failure.
        </div>
      </div>
    </div>
  );
}
