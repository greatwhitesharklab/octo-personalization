"""Reproducible personalization benchmark (CPU, 0.8B/4B).

Demonstrates the utilization gap + the force-reference lever:
  C0_thin  : account facts only, no force        (baseline)
  C1_rich  : rich profile in context, no force   (model often ignores it -> utilization gap)
  C2_force : rich profile + FORCE instruction    (personalization lever, ~3x specificity)

Metric: specificity = fraction of the customer's salient keywords referenced in the reply.
Run:  python run_bench.py --model <path-to-Qwen3.5-0.8B-or-4B> --device cpu
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # repo root
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from octo.prompt import build_system, prompt_parts, chat_wrap
from octo.schema import scene_system
from octo.judge import specificity, compliance_features
from cases import CASES, ACCOUNT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--device', default='cpu')
    ap.add_argument('--max-new', type=int, default=90)
    ap.add_argument('--out', default=str(Path(__file__).resolve().parent / 'results.json'))
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True,
                                                 dtype=torch.bfloat16, attn_implementation='sdpa').to(a.device)
    model.eval()

    @torch.no_grad()
    def gen(facts, force, case):
        system = build_system(scene_system('collection'), f'【沟通画像】语气：{case["tone"]}。', force=force)
        sys, user = prompt_parts(system, '', '', case['msg'], facts_text=facts)
        prompt = chat_wrap(tok, sys, user)
        ids = tok(prompt, add_special_tokens=False, return_tensors='pt').input_ids.to(a.device)
        g = model.generate(ids, max_new_tokens=a.max_new, do_sample=False,
                           repetition_penalty=1.3, pad_token_id=tok.eos_token_id)
        return tok.decode(g[0][ids.shape[1]:], skip_special_tokens=True).strip()

    rows = []
    for ci, c in enumerate(CASES):
        rich = ACCOUNT + '\n' + c['profile']
        for cond, facts, force in [('C0_thin', ACCOUNT, False), ('C1_rich', rich, False), ('C2_force', rich, True)]:
            t = time.time()
            reply = gen(facts, force, c)
            spec = specificity(reply, c['keywords'])
            comp = compliance_features(reply, gold_amounts=['3200', '320', '12', '25'])
            rows.append(dict(uid=c['uid'], cond=cond, reply=reply, specificity=spec['rate'],
                             spec_count=spec['count'], kw_total=spec['total'],
                             compliance_flag=comp['flag'], secs=round(time.time()-t, 1)))
        print(f'[{ci+1}/{len(CASES)}] {c["uid"]} done', flush=True)

    print(f'\n{"cond":10} {"n":>2} {"spec_rate":>9} {"spec_cnt":>8} {"viol":>5}')
    agg = {}
    for cond in ['C0_thin', 'C1_rich', 'C2_force']:
        sub = [r for r in rows if r['cond'] == cond]
        sr = sum(r['specificity'] for r in sub)/len(sub)
        sc = sum(r['spec_count'] for r in sub)/len(sub)
        v = sum(r['compliance_flag'] for r in sub)
        agg[cond] = dict(n=len(sub), spec_rate=round(sr, 3), spec_cnt=round(sc, 2), viol=v)
        print(f'{cond:10} {len(sub):>2} {sr:>9.3f} {sc:>8.2f} {v:>5}')
    Path(a.out).write_text(json.dumps(dict(rows=rows, agg=agg), ensure_ascii=False, indent=1))
    print(f'\nsaved {a.out}')
    print('BENCH_DONE', flush=True)


if __name__ == '__main__':
    main()
