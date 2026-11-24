"""Offline tests — no model / GPU / network. Uses a mock backend."""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from octo.schema import UserRecord, Fact, Persona
from octo_flywheel import (extract_facts, write_back, refresh_profile, prune,
                           update_salience, rank_facts, Flywheel)


class MockBackend:
    name = 'mock'
    def hydrate(self, record): self.record = record
    def write(self, fact): return True
    def recall(self, q, topk=3): return []
    def forget(self): pass
    def respond(self, record, user_msg, topk=3, max_new=80, force=False):
        # simulate a personalized reply referencing the customer's fact values
        vals = [f.value for f in record.facts if f.value]
        return '了解您的情况：' + '、'.join(vals[:3]) + '，我们商量个方案。'


def test_extract_facts():
    fs = extract_facts('我被裁员了，独自带女儿，房租拖欠')
    vals = {f.value for f in fs}
    assert '裁员' in vals and '女儿' in vals and '房租' in vals


def test_writeback_overwrite():
    r = UserRecord(uid='u', facts=[Fact('客户', '职业', '程序员')])
    write_back(r, [Fact('客户', '职业', '货车司机')])   # same key, new value -> overwrite
    assert len(r.facts) == 1 and r.facts[0].value == '货车司机'
    write_back(r, [Fact('客户', '家庭', '女儿')])       # new key -> append
    assert len(r.facts) == 2


def test_consolidate_profile():
    r = UserRecord(uid='u', name='张伟', facts=[Fact('客户', '职业', '司机'), Fact('客户', '家庭', '女儿')])
    p = refresh_profile(r)
    assert '张伟' in p and '司机' in p and '女儿' in p


def test_prune():
    r = UserRecord(uid='u', facts=[Fact('客户', f'a{i}', str(i)) for i in range(60)])
    assert prune(r, keep=50) == 10 and len(r.facts) == 50


def test_feedback_salience():
    s = {}
    update_salience(s, ['女儿', '裁员'], outcome=1.0)
    update_salience(s, ['女儿'], outcome=1.0)
    assert s['女儿'] > s['裁员']                      # more positive reinforcement -> higher
    assert rank_facts(['裁员', '女儿'], s)[0] == '女儿'


def test_flywheel_loop_and_forget():
    with tempfile.TemporaryDirectory() as d:
        from octo.store import UserStore
        fw = Flywheel(MockBackend(), UserStore(f'{d}/mem'), f'{d}/log', f'{d}/state')
        r = UserRecord(uid='u1', name='张伟', persona=Persona(tone='温和'))
        res1 = fw.step(r, '我被裁员了，独自带女儿')   # cold start: reply first, then write-back
        assert res1['n_facts'] >= 2 and res1['n_interactions'] == 1
        res2 = fw.step(r, '房租也拖欠了')             # turn 2: memory now exists -> reply references it
        assert res2['referenced'] and res2['n_interactions'] == 2
        st = fw.states.load('u1')
        assert st['n'] == 2 and st['profile']
        fw.forget_user('u1')
        assert not fw.states.delete('u1')             # already deleted
        assert fw.log.read('u1') == []
