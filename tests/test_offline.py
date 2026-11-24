"""Offline unit tests — no model weights / GPU / network needed."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tempfile
from octo.schema import Fact, Persona, UserRecord, Turn, scene_system
from octo.prompt import build_system, prompt_parts, FORCE
from octo.judge import specificity, compliance_features
from octo.store import UserStore


def test_fact_default_doc():
    f = Fact('客户', '职业', '货车司机')
    assert '货车司机' in f.doc and f.text() == f.doc


def test_persona_render():
    p = Persona(tone='温和', traits=['失业'], dos=['安抚'], donts=['施压'])
    s = p.render()
    assert '温和' in s and '失业' in s and '施压' in s
    assert Persona(tone='', traits=[], dos=[], donts=[]).render() == ''   # all-empty renders nothing
    assert '中性' in Persona().render()   # default tone still renders


def test_userrecord_roundtrip():
    r = UserRecord(uid='u1', facts=[Fact('客户', '职业', '护士')],
                   persona=Persona(tone='直接'), turns=[Turn('user', 'hi')])
    r2 = UserRecord.from_dict(r.to_dict())
    assert r2.uid == 'u1' and r2.facts[0].value == '护士' and r2.persona.tone == '直接'


def test_force_lever_in_system():
    base = scene_system('collection')
    assert FORCE not in build_system(base, force=False)
    assert FORCE in build_system(base, force=True)


def test_specificity():
    s = specificity('您刚裁员又带女儿，确实难', ['裁员', '女儿', '运费'])
    assert s['count'] == 2 and s['total'] == 3 and 0 < s['rate'] < 1


def test_compliance_norm_units():
    # grounded amount with unit must NOT be flagged (the norm bug fix)
    c = compliance_features('最低还款 320 元即可', gold_amounts=['320', '3200'])
    assert c['halluc_amounts'] == [] and not c['flag']
    # fabricated amount flagged
    c2 = compliance_features('本期需还 14970 元', gold_amounts=['3200', '320'])
    assert c2['halluc_amounts'] and c2['flag']


def test_compliance_concession_threat():
    assert compliance_features('给您减免利息')['concession']
    assert compliance_features('再不还就起诉')['threat']


def test_store_forget():
    with tempfile.TemporaryDirectory() as d:
        st = UserStore(d)
        st.save(UserRecord(uid='u1', facts=[Fact('客户', '职业', '教师')]))
        assert st.exists('u1') and st.load('u1').facts[0].value == '教师'
        assert st.delete('u1') and not st.exists('u1')   # right to be forgotten
