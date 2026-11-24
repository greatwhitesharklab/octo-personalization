"""octo — per-customer personalization orchestration over external memory for a frozen small LM.

🐙 Give a frozen model a thousand faces. Mechanism library + reproducible personalization benchmark.
Capability claims pending; see docs/en/CLAIMS.md (negative results included).
"""
from .schema import Fact, Persona, Turn, UserRecord, SCENES, scene_system
from .prompt import prompt_parts, chat_wrap, build_system, FORCE, EXAMPLE
from .judge import specificity, compliance_features
from .store import UserStore
from .agent import OctoAgent
from .memory import MemoryBackend, RagBackend, make_backend

__version__ = '0.1.0'
__all__ = ['Fact', 'Persona', 'Turn', 'UserRecord', 'SCENES', 'scene_system',
           'prompt_parts', 'chat_wrap', 'build_system', 'FORCE', 'EXAMPLE',
           'specificity', 'compliance_features', 'UserStore', 'OctoAgent',
           'MemoryBackend', 'RagBackend', 'make_backend']
