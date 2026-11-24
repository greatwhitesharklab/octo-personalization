# EXPERIMENTS — the octo journey (run-271 → run-279)

How the "mechanism moat" hypothesis was progressively **falsified**, step by step. Synthetic-data
mechanism validation throughout; capability claims pending real corpora. Negative results are the point.

## The question

For per-customer personalization (collection / marketing) over a **frozen small model** with external
per-user memory: is there a **defensible mechanism moat** — something competitors can't copy? We tested
three candidates and all three failed. The effective lever turned out to be copyable glue.

## The journey

### run-271 — modern voice control
- **Q:** can we steer a fine-grained lexical "voice"?
- **R:** cross-domain voice control partly works, but fine lexical personality is hard; **prosody steers
  better than lexical signatures**. Tone is controllable but not distinctive.
- **Seed of doubt:** tone is a commodity, not a moat.

### run-272 — empathy / state inference
- **Q:** can the model infer the customer's emotional state to personalize?
- **R:** a 6-state playbook + disambiguation prompt (v2) separates anxiety/distress from
  crying-for-concession and surface anger. 4B anxiety inference **0/3 → 3/3** (total 0.944); 27B 1.000.
- **Lesson:** state inference is **prompt-solvable** — useful, but again not a defensible mechanism.

### run-273 — ReFT style intervention
- **Q:** can a learned subspace intervention steer style without collapsing content?
- **R:** LoReFT (rank-8, layer-19, ~20k params) is **content-preserving**: repeat 0.008 vs additive
  steering α2 0.126/0.159 (which collapses).
- **Lesson:** ReFT is a clean tool — later reused for the orchestration test (run-279), where it failed.

### run-274 — the personalization lever
- **Q:** what actually moves personalization?
- **R:** **rich profile + force-reference** raises JEV-personal **0.304 → 0.500**. The lever is real.
- **⚠️ measure bug found here:** the compliance judge's amount normalization kept units
  (`320元` ≠ `320`), producing **false hallucination flags** and a fabricated "strong personalization ×
  compliance tradeoff". After fixing norm to digits-only, the tradeoff is **marginal, not strong** —
  the strong version was an artifact. **Lesson: validate the measure before trusting the finding.**

### run-275 — competitive landscape
- **Q:** where are the market gaps?
- **R:** five memory thresholds — ① salience retrieval ② force utilization ③ async consolidation
  ④ grounding ⑤ personalization×compliance. Gaps at **②④⑤** (Mem0/Zep/Letta/Memobase/Cognee/LangMem).

### run-276 — Memobase empirical test
- **Q:** does a market leader close ② utilization?
- **R:** **No.** Memobase's native context instruction ("don't proactively mention memory unless asked")
  **suppresses proactive utilization** (② ✗ measured). With force-reference, personal 0.371 → 0.554.
- **Lesson:** the utilization gap is real and unsolved by market tools — but the fix is a prompt lever (glue).

### run-277 — prototype A (glue scaffold)
- **Q:** does a glue scaffold (prompt-force + rule grounding + repair loop) work?
- **R:** P0 personal 0.497 / violations 3; P1 (repair loop) violations 1. Grounding cuts hallucination
  without killing personalization. **But** coo1-type cases expose a ceiling: the model **self-fabricates
  installment math** ("3849.75 / 1283.25") that prompt repair cannot stop.
- **Lesson:** glue works partly; derived-number fabrication is the hard residue → motivates a native test.

### run-278 — native grounding B (K/V injection)
- **Q:** does native K/V fact injection suppress fabrication *by construction*?
- **R (Arm0, no adapter):** K/V readout fails — but this was a **config error**: the shared readout adapter
  was omitted (W62 already showed no-adapter readout ≈ 17.5%). Corrected same day.
- **R (Arm1, with adapter):** on 2 coo cases K2 (K/V+text) had zero fabrication — looked promising.
  **Expansion to anxiety cases falsified it:** K2 confabulates numbers *contradicting* injected facts
  (salary 2000 → "2685"; account 3200 → "14970"). K/V fab-suppression is **case-dependent, not reliable**.
- **Side test:** GTX 1650 fp16 offload ≈ CPU speed (0.87 tok/s; 4GB holds 10/36 modules; GDN reference
  bottleneck + PCIe). **No speedup** — local small-GPU path dead.
- **Lesson:** fact *availability* ≠ faithful *emission*. Decode is reconstructive; native precise grounding
  is unreliable. **Moat candidate #2 falsified.**

### run-279 — orchestration moat test (GPU batch)
- **Q:** does **learned orchestration beat rule glue AND compound with data**? (the moat kill-criterion)
- **R:** three arms on 120 synthetic cases (train 90 / eval 30), ReFT-utilization at 30/60/90:
  - Utilization gap real: A (no orch) **0.076** → B (force rule) **0.238** (~3×).
  - **C (learned ReFT) 0.173 / 0.146 / 0.154 — all BELOW B**, and **flat/decreasing** with more data.
  - C is more compliant (viol 1/0/3 vs B 5) but less personalized — a different tradeoff point, not better.
- **Lesson:** learned orchestration ≤ glue, **no data compounding**. **Moat candidate #3 falsified.**

## The negative-results timeline (how the moat died)

| Candidate moat | Killed by | Verdict |
|---|---|---|
| Unique tone mechanism | run-271/273 | commodity |
| Native precise K/V grounding | run-278 (confabulation) | unreliable |
| Learned orchestration + data flywheel | run-279 (C ≤ B, flat scaling) | ≤ glue, no compounding |

## What survived

- **The personalization lever** (rich profile + force-reference, ~3×) — real, reproducible, but **glue / copyable**.
- **State inference** (prompt-solvable) — useful, not defensible.
- **The honest conclusion:** the defensible advantage is **not a mechanism** but **accumulated customer data
  + product场景 + orchestration know-how** (time-built, not copyable).

## Cross-cutting lessons

1. **Validate the measure first** (run-274 norm bug fabricated a tradeoff).
2. **Small samples lie** (run-278 coo-only "zero fab" was luck; expansion falsified it).
3. **Reuse needs its prerequisites** (run-278 omitted the readout adapter → degenerate result).
4. **Synthetic = mechanism only**; capability claims need real corpora.
5. **A failed mechanism is a result** — publishing the falsifications is the contribution.
