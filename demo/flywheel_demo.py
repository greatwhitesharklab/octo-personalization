"""Flywheel compounding demo: more interactions -> richer memory -> more personalized replies.

Simulated multi-turn conversation where the customer progressively reveals facts. Each turn the
flywheel captures, writes back, consolidates, and updates outcome-weighted salience. We track how
the number of customer-specific facts referenced in replies grows as memory accumulates.

Outcome is SIMULATED (placeholder): +1 if the reply referenced customer facts, else -0.5.
Run: python flywheel_demo.py --model <Qwen3.5-0.8B-or-4B> --device cpu
"""
from __future__ import annotations
import argparse, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # repo root (octo + octo_flywheel)
from octo.schema import UserRecord, Persona, Fact
from octo.memory import RagBackend
from octo.store import UserStore
from octo_flywheel import Flywheel, update_salience

# Scripted reveals: each turn the customer exposes more of their situation.
TURNS = [
    '我最近实在没钱，能不能缓缓啊。',
    '我前阵子被电子厂裁员了，现在打零工。',
    '我一个人带着8岁的女儿，她还在读小学。',
    '房租已经拖欠两个月了，女儿学费也还没交。',
    '我上月还了最低额320元，不是不想还，是真周转不开。',
    '我打零工月入不稳，大概2000元，能不能商量个分期？',
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--device', default='cpu')
    ap.add_argument('--uid', default='demo_zhang')
    a = ap.parse_args()
    backend = RagBackend(a.model, device=a.device)
    with tempfile.TemporaryDirectory() as d:
        fw = Flywheel(backend, store=UserStore(f'{d}/mem'),
                      log_root=f'{d}/log', state_root=f'{d}/state')
        rec = UserRecord(uid=a.uid, name='张伟', persona=Persona(tone='温和'))
        print(f'{"turn":>4} {"n_facts":>7} {"referenced":>10} {"spec_cnt":>8}  reply')
        counts = []
        for i, msg in enumerate(TURNS, 1):
            # simulate outcome AFTER seeing reply: peek via a dry step is complex; use prior referenced
            res = fw.step(rec, msg, outcome=0.0)
            # recompute outcome from referenced and re-update salience (simulated engagement)
            outcome = 1.0 if res['referenced'] else -0.5
            st = fw.states.load(a.uid); update_salience(st['salience'], res['referenced'], outcome)
            fw.states.save(a.uid, st)
            counts.append(len(res['referenced']))
            print(f'{i:>4} {res["n_facts"]:>7} {len(res["referenced"]):>10} {res["specificity"]:>8.2f}  {res["reply"][:50]}')
        print(f'\nreferenced-fact count by turn: {counts}')
        early = sum(counts[:2]) / 2; late = sum(counts[-2:]) / 2
        print(f'early avg {early:.1f} -> late avg {late:.1f}  ({"compounding ✓" if late > early else "no growth ✗"})')
        print('DEMO_DONE', flush=True)


if __name__ == '__main__':
    main()
