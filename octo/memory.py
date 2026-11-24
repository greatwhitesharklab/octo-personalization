"""Pluggable memory layer.

MemoryBackend interface; implementations:
- RagBackend (self-contained): same base model, facts retrieved by hidden-state mean embedding +
  cosine, injected as TEXT into the prompt. No K/V injection. Runs on CPU with transformers only.
- BkvBackend (optional): wraps the sibling `huamao_bkv` engine (full-fact K/V injection + shared
  residual adapter); memory goes into attention K/V, not prompt text. Available only if huamao_bkv
  is installed (see https://github.com/greatwhitesharklab/huamao-memory-bench).

Per-user isolation: hydrate resets then re-loads that user's facts.
"""
from __future__ import annotations
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .schema import Fact, UserRecord, scene_system
from .prompt import prompt_parts, chat_wrap, build_system


class MemoryBackend:
    name = 'base'

    def hydrate(self, record: UserRecord):
        raise NotImplementedError

    def write(self, fact: Fact):
        raise NotImplementedError

    def recall(self, query: str, topk: int = 3):
        raise NotImplementedError

    def respond(self, record: UserRecord, user_msg: str, topk: int = 3,
                max_new: int = 80, force: bool = False) -> str:
        raise NotImplementedError

    def forget(self):
        raise NotImplementedError

    def _history_text(self, record: UserRecord, k: int = 6) -> str:
        turns = record.turns[-k:]
        return '\n'.join(f'{"客户" if t.role == "user" else "助手"}：{t.text}' for t in turns)


class RagBackend(MemoryBackend):
    """Text-retrieval baseline: hidden-state mean embedding + cosine; facts injected as prompt text."""
    name = 'rag'

    def __init__(self, model_path, device='cpu', dtype='bfloat16'):
        dt = getattr(torch, dtype)
        self.tok = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            str(model_path), local_files_only=True, dtype=dt,
            attn_implementation='sdpa').to(device)
        self.model.eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        self.device = device
        self._facts: list[Fact] = []
        self._emb: list[torch.Tensor] = []

    @torch.no_grad()
    def _embed(self, text: str) -> torch.Tensor:
        ids = self.tok(text, add_special_tokens=False, return_tensors='pt').input_ids.to(self.device)
        out = self.model(ids, output_hidden_states=True)
        h = out.hidden_states[-1][0].float().mean(0)
        return torch.nn.functional.normalize(h, dim=-1)

    def hydrate(self, record: UserRecord):
        self._facts, self._emb = [], []
        for f in record.facts:
            self.write(f)

    def write(self, fact: Fact):
        self._facts.append(fact)
        self._emb.append(self._embed(fact.doc))
        return True

    def recall(self, query: str, topk: int = 3):
        if not self._facts:
            return []
        q = self._embed(query)
        sims = [float(q @ e) for e in self._emb]
        order = sorted(range(len(sims)), key=lambda i: -sims[i])[:topk]
        return [(self._facts[i], sims[i]) for i in order]

    @torch.no_grad()
    def respond(self, record: UserRecord, user_msg: str, topk: int = 3,
                max_new: int = 80, force: bool = False) -> str:
        hits = self.recall(user_msg, topk)
        facts_text = '\n'.join(f'- {f.doc}' for f, _ in hits)
        system = build_system(scene_system(record.scene), record.persona.render(), force=force)
        sys, user = prompt_parts(system, '', self._history_text(record), user_msg, facts_text=facts_text)
        prompt = chat_wrap(self.tok, sys, user)
        ids = self.tok(prompt, add_special_tokens=False, return_tensors='pt').input_ids.to(self.device)
        gen = self.model.generate(ids, max_new_tokens=max_new, do_sample=False,
                                  repetition_penalty=1.3, pad_token_id=self.tok.eos_token_id)
        return self.tok.decode(gen[0][ids.shape[1]:], skip_special_tokens=True).strip()

    def forget(self):
        self._facts, self._emb = [], []


def make_backend(name: str, model_path, device='cpu', dtype='bfloat16', **kw):
    if name == 'rag':
        return RagBackend(model_path, device=device, dtype=dtype)
    if name == 'bkv':
        try:
            from huamao_bkv import FullFactBKV   # sibling repo, optional
        except ImportError as e:
            raise ImportError('bkv backend requires huamao_bkv '
                              '(github.com/greatwhitesharklab/huamao-memory-bench)') from e
        return BkvBackend(model_path, device=device, dtype=dtype, **kw)
    raise ValueError(f'unknown backend {name}')


class BkvBackend(MemoryBackend):
    """Native K/V memory via huamao_bkv (optional). Facts injected as attention K/V, not text."""
    name = 'bkv'

    def __init__(self, model_path, device='cpu', dtype='bfloat16', adapter_path=None,
                 layers=(11, 15, 19, 23), ret_layer=11, ret_head=2):
        from huamao_bkv import FullFactBKV
        assert adapter_path, 'bkv requires a shared adapter'
        self.b = FullFactBKV(model_path, adapter_path, layers=layers, ret_layer=ret_layer,
                             ret_head=ret_head, dtype=dtype, device=device, overwrite_conflicts=False)
        self._facts: list[Fact] = []

    def hydrate(self, record: UserRecord):
        self.b.reset(); self._facts = []
        for f in record.facts:
            self.write(f)

    def write(self, fact: Fact):
        if self.b.add_fact(fact.entity, fact.attribute, fact.value, doc=fact.doc):
            self._facts.append(fact)
            return True
        return False

    def recall(self, query: str, topk: int = 3):
        hits = self.b.recall(query, topk=topk, mode='ent_mean')
        out = []
        for meta, score in hits:
            for f in self._facts:
                if (f.entity, f.attribute, f.value) == tuple(meta):
                    out.append((f, score)); break
        return out

    def respond(self, record: UserRecord, user_msg: str, topk: int = 3,
                max_new: int = 80, force: bool = False) -> str:
        system = build_system(scene_system(record.scene), record.persona.render(), force=force)
        sys, user = prompt_parts(system, '', self._history_text(record), user_msg)
        prompt = chat_wrap(self.b.tok, sys, user)
        hits = self.recall(user_msg, topk)
        idxs = [i for i, f in enumerate(self._facts) if f in [h[0] for h in hits]]
        return self.b.generate(prompt, recall_idxs=idxs or None, max_new=max_new)

    def forget(self):
        self.b.reset(); self._facts = []
