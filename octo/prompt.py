"""Prompt orchestration: assemble (system, user) segments + the personalization lever.

The core empirical finding of octo: a frozen model given a customer profile often does NOT
spontaneously use it (the "utilization gap"). A force-reference instruction in the system prompt
roughly triples specificity (personalization). This module exposes that lever explicitly.
"""
from __future__ import annotations

# The personalization lever (run-274 / run-279): force the model to reference a concrete personal detail.
FORCE = ('【个性化硬要求】回复必须具体回应这位客户的独特处境，至少引用其个人情况中的一个具体细节'
         '（如职业/家庭/上次承诺/具体困难），严禁用"非常理解您的困难"这类通用套话开头。')
EXAMPLE = ('【个性化范例】若客户画像为"刚失业独自带孩子"，客户说"没钱能不能缓缓"，应回：'
           '"您刚没了工作，一个人带孩子确实扛得辛苦。咱不逼您一次性还清，先还个最低额保住记录，'
           '剩下的等您零工工资结了再说，您看行吗？"——像这样贴合具体处境，而非通用模板。')


def prompt_parts(system: str, persona_text: str, history_text: str, user_msg: str,
                 facts_text: str = ''):
    """Assemble (system, user). facts_text carries retrieved profile facts (text/RAG path)."""
    sys = system + ('\n\n' + persona_text if persona_text else '')
    seg = []
    if facts_text:
        seg.append('【这位客户的历史记录】\n' + facts_text)
    if history_text:
        seg.append('【近期对话】\n' + history_text)
    seg.append('客户说：' + user_msg)
    seg.append('请结合这位客户的历史与沟通画像，直接给出简短自然的中文回应（不要推理过程）。')
    return sys, '\n\n'.join(seg)


def chat_wrap(tok, system: str, user: str) -> str:
    """Apply chat template with thinking disabled (avoids English thinking preamble)."""
    return tok.apply_chat_template(
        [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
        tokenize=False, add_generation_prompt=True, enable_thinking=False)


def build_system(scene_system: str, persona_text: str = '', force: bool = False,
                 example: bool = False) -> str:
    """Build the system prompt; force/example toggle the personalization lever."""
    system = (FORCE + '\n' + scene_system) if force else scene_system
    if example:
        system = system + '\n' + EXAMPLE
    if persona_text:
        system = system + '\n\n' + persona_text
    return system
