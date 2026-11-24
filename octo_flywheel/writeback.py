"""Fact write-back: extract new facts from conversation, write to per-user memory with overwrite.

Structured primary key (entity, attribute): latest wins, old value superseded (auditable).
Extraction here is a minimal rule-based placeholder; a real product uses an LLM extractor.
The point of the scaffold is the write-back + overwrite plumbing, not extraction quality.
"""
from __future__ import annotations
import re
from octo.schema import Fact


# Minimal placeholder extractor: a few high-signal patterns (profession / family / hardship).
# Real product replaces this with an LLM fact extractor; the write-back path stays the same.
_PATTERNS = [
    ('职业', r'(货车司机|程序员|护士|教师|个体户|快递员|保洁|装修工|网约车司机|理货员|失业|裁员)'),
    ('家庭', r'(独自带|单亲|女儿|儿子|孩子|丈夫|妻子|家人住院)'),
    ('困难', r'(房租|学费|住院|肾病|淡季|拖欠|周转不开|工资没结)'),
]


def extract_facts(text: str, entity: str = '客户') -> list:
    """Placeholder extraction: surface matched spans as candidate facts (dedup by attribute+value)."""
    out, seen = [], set()
    for attr, pat in _PATTERNS:
        for m in re.finditer(pat, text):
            val = m.group(1)
            key = (attr, val)
            if key not in seen:
                seen.add(key)
                out.append(Fact(entity=entity, attribute=attr, value=val,
                                doc=f'{entity}的{attr}涉及{val}。'))
    return out


def write_back(record, facts: list, backend=None) -> list:
    """Write facts into the record with (entity, attribute) overwrite; optionally re-hydrate backend.
    Returns the list of facts actually written (new or updated)."""
    written = []
    for f in facts:
        idx = next((i for i, x in enumerate(record.facts)
                    if x.entity == f.entity and x.attribute == f.attribute and x.value == f.value), None)
        if idx is None:
            # overwrite same (entity, attribute) slot if a different value exists
            slot = next((i for i, x in enumerate(record.facts)
                         if x.entity == f.entity and x.attribute == f.attribute), None)
            if slot is not None:
                record.facts[slot] = f
            else:
                record.facts.append(f)
            written.append(f)
    if backend is not None and written:
        backend.hydrate(record)
    return written
