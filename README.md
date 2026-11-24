# octo — per-customer personalization over external memory for a frozen small LM

**English** | [中文](README.zh.md)

> 🐙 **Give a frozen model a thousand faces.** *Same small model, a different voice for every customer.*
> *(mechanism library + reproducible benchmark; capability claims pending — see [CLAIMS](docs/en/CLAIMS.md))*

**octo (千人千面, "a thousand faces")**: orchestrate **per-customer memory + persona** outside a frozen
small language model so its replies are personalized to each customer's situation — without fine-tuning
per-user weights. Memory lives in an external, auditable, deletable per-user store; the model stays shared.

> **Status: mechanism library + reproducible personalization benchmark. Capability claims pending.**
> Read [`CLAIMS.md`](docs/en/CLAIMS.md) before citing any number — **negative results are listed there too**,
> and they are the main contribution.

## The honest finding

We tested three "clever-mechanism moat" hypotheses and **all three failed**:

| Hypothesis | Result |
|---|---|
| Unique tone mechanism is a moat | ❌ commodity |
| Native K/V memory grounds precise facts | ❌ unreliable — model confabulates numbers contradicting injected facts |
| Learned orchestration beats rules + compounds with data | ❌ a trained ReFT intervention scored **below** a one-line force-reference rule, flat with more data |

What **does** work is simple: **rich customer profile + a force-reference instruction** roughly triples
personalization (specificity 0.076 → 0.238). That lever is **glue — copyable**. So the defensible advantage
is **not a mechanism** but **accumulated customer data + product场景 + orchestration know-how**.

This repo releases the mechanism + the reproducible benchmark + the honest boundaries, in the spirit of
negative-results-as-contribution.

## What's in the box
- `octo/` — the orchestration library:
  - `schema.py` — `Fact` / `Persona` / `UserRecord` data contracts; collection/marketing scene templates.
  - `prompt.py` — prompt assembly + the **force-reference lever** (`FORCE`).
  - `memory.py` — pluggable backend: `RagBackend` (text retrieval, self-contained, CPU) and optional
    `BkvBackend` (native K/V via the sibling [`huamao_bkv`](https://github.com/greatwhitesharklab/huamao-memory-bench)).
  - `judge.py` — objective **specificity** (personalization) + **compliance** signals.
  - `store.py` — per-user JSON store with **right-to-be-forgotten** deletion.
  - `agent.py` — `OctoAgent`: hydrate → recall + persona → reply → write-back.
- `benchmarks/personalization/` — reproducible **utilization-gap + force-lever** benchmark, **0.8B/4B CPU**.
- `tests/` — offline unit tests (no model weights / GPU needed).
- [`docs/en/CLAIMS.md`](docs/en/CLAIMS.md) — demonstrated / falsified / pending, with negative results.
- [`docs/en/EXPERIMENTS.md`](docs/en/EXPERIMENTS.md) — the full run-271→279 journey: how the moat hypothesis was falsified step by step.

## Quickstart
```bash
pip install -e .
# offline tests (no model needed)
python -m pytest tests/ -q
# personalization benchmark (download Qwen3.5-0.8B or 4B first; Apache-2.0)
python benchmarks/personalization/run_bench.py --model /path/to/Qwen3.5-0.8B --device cpu
```
Expected: specificity `C0_thin < C1_rich < C2_force`. The *ordering* is the robust finding; absolute
numbers vary by base model.

## Data flywheel (`octo_flywheel/`)

The lever is copyable; so is the flywheel plumbing. **The moat is the per-customer data you accumulate**
(memory + interaction log + outcome-weighted salience), compounding with every interaction — that stays yours.

```
interact (lever) -> capture -> write-back (overwrite) -> consolidate -> feedback (outcome-weighted
salience) -> next ↺   (more use -> richer memory -> better personalization -> more data)
```
- `octo_flywheel/` — capture / writeback / consolidate / feedback / `Flywheel.step()` + right-to-be-forgotten.
- `demo/flywheel_demo.py` — compounding demo (referenced-fact count grows over turns).
- The "learning" is plain outcome-weighted statistics; extractors + outcome signal are placeholders
  (a real product fills them with an LLM extractor + actual customer behavior).

## Relation to sibling projects
- 🐱 [huamao-memory-bench](https://github.com/greatwhitesharklab/huamao-memory-bench) — native writable K/V
  memory engine (the optional `BkvBackend` here wraps it).
- 🦫 [kapi-interactive-review](https://github.com/greatwhitesharklab/kapi-interactive-review) — interactive review.

## Scope & honesty
- All data here is **synthetic and non-commercial**. No real customer data, keys, or model weights are distributed.
- Mechanism validation only; **capability claims require real corpora** (pending).
- Base model (Qwen3.5) is Apache-2.0; weights are **not** redistributed — download them yourself.

## License
Apache-2.0. See [LICENSE](LICENSE).
