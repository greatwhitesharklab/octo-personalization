"""Outcome feedback: outcome-weighted salience (simple statistics, NOT a learned mechanism).

The flywheel's compounding engine: facts referenced in interactions that led to good outcomes
get higher salience, so future replies surface them first. This is deliberately plain statistics
(the moat is the accumulated outcome data, not a clever algorithm).
"""
from __future__ import annotations


def update_salience(salience: dict, referenced: list, outcome: float, lr: float = 0.1) -> dict:
    """Increment referenced facts' salience toward the outcome signal (exponential moving average)."""
    for fact in referenced:
        prev = salience.get(fact, 0.0)
        salience[fact] = prev + lr * (outcome - prev)
    return salience


def rank_facts(values: list, salience: dict) -> list:
    """Rank fact values by salience (descending)."""
    return sorted(values, key=lambda v: -salience.get(v, 0.0))
