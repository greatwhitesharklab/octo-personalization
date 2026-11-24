"""The flywheel loop: interact -> capture -> write-back -> consolidate -> feedback -> next.

Orchestrates the octo personalization lever with the data-intake plumbing. Each step grows the
per-user memory and outcome-weighted salience, so the next interaction is more personalized.
The accumulated data (memory + interaction log + salience) is the moat asset; this code is plumbing.
"""
from __future__ import annotations
import json
from pathlib import Path
from octo.judge import specificity
from .capture import InteractionLog, Interaction
from .writeback import extract_facts, write_back
from .consolidate import refresh_profile, prune
from .feedback import update_salience


class StateStore:
    """Per-user flywheel state (salience weights + profile summary + interaction count)."""
    def __init__(self, root):
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, uid):
        safe = ''.join(c for c in uid if c.isalnum() or c in '-_')
        return self.root / f'{safe}.json'

    def load(self, uid):
        p = self._path(uid)
        if p.exists():
            return json.loads(p.read_text(encoding='utf-8'))
        return dict(uid=uid, salience={}, profile='', n=0)

    def save(self, uid, state):
        self._path(uid).write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf-8')

    def delete(self, uid):
        p = self._path(uid)
        if p.exists():
            p.unlink(); return True
        return False


class Flywheel:
    def __init__(self, backend, store, log_root, state_root):
        self.backend = backend
        self.store = store
        self.log = InteractionLog(log_root)
        self.states = StateStore(state_root)
        self._uid = None

    def _ensure(self, record):
        if self._uid != record.uid:
            self.backend.hydrate(record)
            self._uid = record.uid

    def step(self, record, user_msg, outcome: float = 0.0, force: bool = True, max_new: int = 90) -> dict:
        self._ensure(record)
        state = self.states.load(record.uid)
        # 1. interact (the lever)
        reply = self.backend.respond(record, user_msg, max_new=max_new, force=force)
        # 2. capture
        referenced = [f.value for f in record.facts if f.value and f.value in reply]
        state['n'] += 1
        self.log.append(record.uid, Interaction(state['n'], user_msg, reply, referenced, outcome))
        # 3. write-back new facts
        new_facts = write_back(record, extract_facts(user_msg), self.backend)
        # 4. consolidate
        state['profile'] = refresh_profile(record)
        prune(record)
        # 5. feedback (outcome-weighted salience)
        update_salience(state['salience'], referenced, outcome)
        # persist
        self.store.save(record)
        self.states.save(record.uid, state)
        kw = [f.value for f in record.facts if f.value]
        spec = specificity(reply, kw)
        return dict(reply=reply, referenced=referenced, new_facts=[f.value for f in new_facts],
                    specificity=spec['rate'], n_facts=len(record.facts), n_interactions=state['n'])

    def forget_user(self, uid):
        """Right to be forgotten across memory + log + state."""
        self.backend.forget(); self._uid = None
        self.store.delete(uid); self.log.delete(uid); self.states.delete(uid)
