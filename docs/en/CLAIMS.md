# CLAIMS — what octo does and does not show

**Read this before citing any number.** Synthetic-data results are *mechanism validation*, not capability
claims. Capability claims require real corpora and are marked ⏳ pending. Negative results are listed
explicitly — they are the main research contribution.

## ✅ Demonstrated (mechanism, synthetic, reproducible on CPU)

- **Utilization gap.** A frozen small model given a customer profile in context often does **not**
  spontaneously use it. On the personalization benchmark, specificity (fraction of the customer's salient
  fact-words referenced) is **0.076** with the profile present but no instruction (arm A).
- **Force-reference lever.** Adding a force-reference instruction to the system prompt raises specificity
  to **0.238** (~3×, arm B). Rich profile + force-reference is an effective, reproducible personalization
  lever. (Earlier JEV-personal metric: 0.304 → 0.500.)
- **Empathy state inference.** A disambiguation prompt (v2) separates anxiety/distress from
  crying-for-concession and surface anger; 4B anxiety inference 0/3 → 3/3.

## ❌ Falsified / negative (do not resurrect)

- **Native precise grounding is unreliable.** Injecting facts as attention K/V does **not** make a frozen
  model emit them faithfully: it confabulates numbers that *contradict* the injected facts
  (e.g. profile salary 2000 → reply "2685"; account 3200 → reply "14970"). Fact *availability* ≠ faithful
  *emission*; decode is reconstructive and lossy. (run-278)
- **Learned orchestration ≤ rule glue, no data compounding.** A trained ReFT utilization intervention
  (rank-8, layer-19) scored specificity **0.173 / 0.146 / 0.154** at 30/60/90 training cases — all **below**
  the force-reference rule (0.238), and **flat/decreasing** with more data. The "learned orchestration beats
  rules and compounds with data" moat hypothesis is **falsified for this mechanism**. (run-279)
- **Tone mechanism is commodity.** Style steering (SAE / ReFT) is not a defensible moat.
- **Strong personalization × compliance tradeoff** was an artifact of an amount-normalization bug
  (units not stripped); after the fix the tradeoff is marginal, not strong.

## ⏳ Pending (capability claims need real corpora)

- Any claim that this improves real collection/marketing outcomes. Synthetic cases validate the mechanism
  only; real-corpus validation (e.g. DuIE/CMeIE or real interaction logs) is required before capability claims.

## Strategic conclusion (evidence-backed)

Three "clever-mechanism moat" paths were tested and failed: tone (commodity), native precise grounding
(unreliable), learned orchestration (≤ glue, no compounding). The effective personalization lever
(force-reference + rich profile) is **glue — copyable**. The defensible advantage is therefore **not a
mechanism** but **accumulated customer data + product场景 + orchestration know-how** (time-built, not copyable).

## Reproduce

```bash
pip install -e .
python benchmarks/personalization/run_bench.py --model <Qwen3.5-0.8B-or-4B-path> --device cpu
```
Expected: C0_thin < C1_rich < C2_force on specificity (the lever). Absolute numbers vary by base model;
the *ordering* (force > rich > thin) is the robust mechanism finding.
