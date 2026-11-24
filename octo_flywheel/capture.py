"""Interaction capture: log every turn with referenced facts + outcome signal.

This is the data intake of the flywheel. The accumulated interaction log IS the moat asset
(not the code). Outcome is a placeholder signal here (simulated); a real product fills it with
actual customer behavior (replied / engaged / repaid).
"""
from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict


@dataclass
class Interaction:
    turn: int
    user_msg: str
    reply: str
    referenced: list = field(default_factory=list)   # salient fact-words the reply used
    outcome: float = 0.0                              # placeholder signal in [-1, 1]


class InteractionLog:
    """Per-user append-only interaction log (auditable)."""
    def __init__(self, root):
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, uid):
        safe = ''.join(c for c in uid if c.isalnum() or c in '-_')
        return self.root / f'{safe}.jsonl'

    def append(self, uid, interaction: Interaction):
        with self._path(uid).open('a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(interaction), ensure_ascii=False) + '\n')

    def read(self, uid):
        p = self._path(uid)
        if not p.exists():
            return []
        return [Interaction(**json.loads(l)) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]

    def delete(self, uid):
        p = self._path(uid)
        if p.exists():
            p.unlink(); return True
        return False
