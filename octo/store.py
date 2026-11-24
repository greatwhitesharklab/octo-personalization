"""Per-user persistence + right to be forgotten.

One JSON file per user (facts + persona + turns). Any K/V cache is a derived quantity,
re-hydrated from facts — so deleting the user file deletes the memory source and responses
stop referencing it (right to be forgotten). Prototype file store; production scale later.
"""
from __future__ import annotations
import json
from pathlib import Path
from .schema import UserRecord


class UserStore:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, uid: str) -> Path:
        safe = ''.join(c for c in uid if c.isalnum() or c in '-_')
        return self.root / f'{safe}.json'

    def save(self, record: UserRecord):
        self._path(record.uid).write_text(
            json.dumps(record.to_dict(), ensure_ascii=False, indent=1), encoding='utf-8')

    def load(self, uid: str) -> UserRecord:
        return UserRecord.from_dict(json.loads(self._path(uid).read_text(encoding='utf-8')))

    def exists(self, uid: str) -> bool:
        return self._path(uid).exists()

    def delete(self, uid: str) -> bool:
        """Right to be forgotten: permanently delete this user's memory file."""
        p = self._path(uid)
        if p.exists():
            p.unlink()
            return True
        return False

    def list_uids(self):
        return sorted(p.stem for p in self.root.glob('*.json'))
