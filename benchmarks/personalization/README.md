# Personalization benchmark — utilization gap + force-reference lever

Reproducible on **0.8B/4B CPU**. Synthetic cases only (mechanism validation, not capability).

## What it measures
`specificity` = fraction of the customer's salient fact-words the reply references.

Three arms per case:
- `C0_thin` — account facts only, no force (baseline).
- `C1_rich` — rich profile in context, no force (exposes the **utilization gap**: model often ignores it).
- `C2_force` — rich profile + `FORCE` instruction (the **personalization lever**).

## Run
```bash
python run_bench.py --model /path/to/Qwen3.5-0.8B --device cpu
```

## Expected
`C0_thin < C1_rich < C2_force` on specificity. Reference (4B): A≈0.076 → B≈0.238 (~3×).
Absolute values vary by base model; the **ordering** is the robust mechanism finding.

See [`../../docs/en/CLAIMS.md`](../../docs/en/CLAIMS.md) for the honest scope (and negative results).
