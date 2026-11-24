"""Octo data contracts + scene templates.

Minimal per-user memory model: Fact (structured historical fact), Persona (tone/character card),
Turn (dialogue turn), UserRecord (one user's full memory). Scene templates give the collection /
marketing system prompt. All synthetic, non-commercial, mechanism-probe use; no real customer data.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
import time


@dataclass
class Fact:
    """One historical fact. entity/attribute form a structured primary key (conflict resolution);
    doc is a natural sentence (model-native encoding, language-agnostic storage)."""
    entity: str
    attribute: str
    value: str
    doc: str = ''
    ts: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.doc:
            self.doc = f'{self.entity}的{self.attribute}是{self.value}。'

    def text(self) -> str:
        return self.doc


@dataclass
class Persona:
    """Per-user persona/tone card. Rendered into a prompt fragment that guides how to talk
    to this person (tone is controlled via context injection, not via K/V)."""
    tone: str = '中性'                 # e.g. 正式/温和/直接/鼓励
    traits: list = field(default_factory=list)
    dos: list = field(default_factory=list)
    donts: list = field(default_factory=list)

    def render(self) -> str:
        if not (self.tone or self.traits or self.dos or self.donts):
            return ''
        parts = [f'【这位客户的沟通画像】语气：{self.tone}。']
        if self.traits:
            parts.append('特点：' + '、'.join(self.traits) + '。')
        if self.dos:
            parts.append('宜：' + '；'.join(self.dos) + '。')
        if self.donts:
            parts.append('忌：' + '；'.join(self.donts) + '。')
        return ''.join(parts)


@dataclass
class Turn:
    role: str                          # 'user' | 'agent'
    text: str


@dataclass
class UserRecord:
    """One user's full memory = historical facts + persona card + dialogue history.
    Serializable / deletable as a whole (right to be forgotten)."""
    uid: str
    name: str = '客户'
    scene: str = 'collection'
    facts: list = field(default_factory=list)     # list[Fact]
    persona: Persona = field(default_factory=Persona)
    turns: list = field(default_factory=list)     # list[Turn]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> 'UserRecord':
        d = dict(d)
        d['facts'] = [Fact(**f) for f in d.get('facts', [])]
        d['persona'] = Persona(**d.get('persona', {}))
        d['turns'] = [Turn(**t) for t in d.get('turns', [])]
        return cls(**d)


SCENES = {
    'collection': (
        '你是信贷机构的还款提醒助手。任务：结合这位客户的历史与沟通画像，礼貌、合规地提醒还款、'
        '协商可行的还款安排。严禁威胁、骚扰、泄露隐私；尊重客户处境。回复简短自然。'
    ),
    'marketing': (
        '你是信贷机构的客户关怀助手。任务：结合这位客户的历史与沟通画像，做个性化的复借/额度关怀，'
        '语气贴合对方。不得夸大、不得误导；客户无需求时不纠缠。回复简短自然。'
    ),
}


def scene_system(scene: str) -> str:
    return SCENES.get(scene, SCENES['collection'])
