"""Octo dialogue agent: personalized conversation over a per-user memory base.

Orchestration: hydrate memory per user -> recall + persona -> generate reply -> append turns ->
optional write-back of new facts. Re-hydrate only on user switch (avoid per-turn re-encoding);
forget_user triggers the right to be forgotten.
"""
from __future__ import annotations
from .schema import UserRecord, Turn, Fact
from .memory import MemoryBackend


class OctoAgent:
    def __init__(self, backend: MemoryBackend, store=None):
        self.backend = backend
        self.store = store
        self._uid = None

    def _ensure(self, record: UserRecord):
        if self._uid != record.uid:
            self.backend.hydrate(record)
            self._uid = record.uid

    def chat(self, record: UserRecord, user_msg: str, topk: int = 3,
             max_new: int = 80, force: bool = False, write_back=None) -> str:
        self._ensure(record)
        reply = self.backend.respond(record, user_msg, topk=topk, max_new=max_new, force=force)
        record.turns.append(Turn('user', user_msg))
        record.turns.append(Turn('agent', reply))
        if write_back:
            for f in write_back:
                record.facts.append(f)
                self.backend.write(f)
        if self.store:
            self.store.save(record)
        return reply

    def recall(self, record: UserRecord, query: str, topk: int = 3):
        self._ensure(record)
        return self.backend.recall(query, topk=topk)

    def forget_user(self, uid: str):
        """Right to be forgotten: clear backend cache + delete persisted file."""
        self.backend.forget()
        self._uid = None
        if self.store:
            self.store.delete(uid)
