"""Consolidation: async refine the profile from accumulated facts (the 'dream' step).

Refresh profile prose from facts, prune superseded/stale entries, surface salient facts.
Scaffold version is deterministic templating; a real product may use an LLM summarizer.
"""
from __future__ import annotations


def refresh_profile(record) -> str:
    """Build a compact profile prose from the current facts (latest values)."""
    by_attr = {}
    for f in record.facts:
        by_attr[f.attribute] = f.value   # last wins
    parts = [f'{record.name}']
    for attr, val in by_attr.items():
        parts.append(f'{attr}：{val}')
    return '；'.join(parts) + '。'


def salient_values(record, salience: dict, topk: int = 8) -> list:
    """Fact values ranked by learned salience (feedback weights), fallback to recency."""
    vals = [(f.value, salience.get(f.value, 0.0), f.ts) for f in record.facts]
    vals.sort(key=lambda x: (-x[1], -x[2]))
    return [v for v, _, _ in vals[:topk]]


def prune(record, keep: int = 50) -> int:
    """Cap memory size (drop oldest low-salience facts). Returns number pruned."""
    if len(record.facts) <= keep:
        return 0
    record.facts.sort(key=lambda f: f.ts)
    dropped = len(record.facts) - keep
    record.facts = record.facts[-keep:]
    return dropped
