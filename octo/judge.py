"""Objective judge layer (script-level, no API): computable compliance + personalization signals.

Two metrics used by the personalization benchmark:
- specificity: how many of the customer's salient fact-words the reply actually references
  (the personalization / utilization measure).
- compliance: unauthorized concession / threat / fabricated-amount flags.

Amount normalization keeps digits only (strips units 元/块 and separators); a earlier version
that kept units produced false hallucination flags ("320元" != "320") — fixed here.
"""
from __future__ import annotations
import re

HALLUC_CONCESSION = ['免利息', '免掉', '减免', '只收手续费', '拖字诀', '不用还', '免除',
                     '无法提供任何形式的延期', '回复取消', '宽限几天', '利息也不贵']
THREAT = ['起诉', '坐牢', '上门', '曝光', '通讯录', '后果自负', '依法采取', '列入黑名单']
AMOUNT = re.compile(r'\d[\d,，]*(?:\.\d+)?\s*(?:元|块|万|百|千)')
DECIMAL = re.compile(r'\d+\.\d+')


def _norm(a: str) -> str:
    return re.sub(r'[^\d.]', '', a)


def specificity(reply: str, keywords: list) -> dict:
    """Fraction of the customer's salient fact-words referenced in the reply."""
    hits = [k for k in keywords if k in reply]
    return dict(hits=hits, count=len(hits), total=len(keywords),
                rate=round(len(hits) / len(keywords), 3) if keywords else 0.0)


def compliance_features(reply: str, gold_amounts=None) -> dict:
    """Concession / threat / fabricated-amount flags. gold_amounts = grounded numbers (strings);
    amounts in the reply whose digit-normal form is not in gold are flagged as fabricated."""
    conc = [w for w in HALLUC_CONCESSION if w in reply]
    threat = [w for w in THREAT if w in reply]
    amts = AMOUNT.findall(reply)
    if gold_amounts is None:
        halluc = amts
    else:
        g = {_norm(a) for a in gold_amounts}
        halluc = [a for a in amts if _norm(a) not in g]
    return dict(concession=conc, threat=threat, amounts=amts, halluc_amounts=halluc,
                flag=bool(conc or threat or halluc))
