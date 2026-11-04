import copy
import hashlib
import importlib
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).parents[1]

def canon(x): return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
def digest(x): return hashlib.sha256(canon(x).encode()).hexdigest()
def load(name): return json.loads((ROOT/'fixtures'/name).read_text())
def cell(d): return {k:d[k] for k in ('requirement','page','method')}
def unknown(d): return dict(cell(d),state='UNKNOWN',procedure_quote='',observed_quote='')

@pytest.fixture
def setup(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender=direct_alice
    obj=direct_deploy(str(ROOT/'contracts/accessibility_lens.py'), sdk_version='v0.2.16')
    p=load('policy.json'); pid=obj.register_policy(canon(p),importlib.import_module('genlayer').Address(direct_bob))
    direct_vm.sender=direct_bob
    docs=[load(f'pass_{i}.json') for i in range(3)]
    return direct_vm,obj,p,pid,docs

def manifest(docs):
    return [dict(cell(d),url=f'https://raw.githubusercontent.com/ANZA24k/AccessibilityLens/{"a"*40}/fixtures/pass_{i}.json',
                 sha256=hashlib.sha256(canon(d).encode()).hexdigest(),bytes=len(canon(d).encode())) for i,d in enumerate(docs)]
def rows(docs):
    return [dict(cell(d),state=d['reported'],procedure_quote=d['procedure'][:100],observed_quote=d['observed'][:100])
            if d['reported']!='UNKNOWN' else unknown(d) for d in docs]
def mocks(vm,items,docs,response):
    vm.clear_mocks()
    for e,d in zip(items,docs): vm.mock_web(e['url'],dict(method='GET',status=200,body=canon(d)))
    vm.mock_llm('.*',canon(response))
def submit(obj,pid,items,label='audit-1'):
    return obj.submit_audit(pid,label,canon(items),digest(items))

def test_end_to_end_receipt_and_validator(setup):
    vm,obj,p,pid,docs=setup; items=manifest(docs); aid=submit(obj,pid,items)
    mocks(vm,items,docs,rows(docs)); h=obj.evaluate(aid)
    r=json.loads(obj.get_receipt(aid,1)); assert r['hash']==h==digest(r['body'])
    assert r['body']['decision']==dict(outcome='CONFORMANT',passed=3,failed=0,unknown=0,required=3)
    assert vm.run_validator() is True
    assert json.loads(obj.get_audit(aid))['closed'] is True
    with pytest.raises(Exception,match='closed'): obj.evaluate(aid)

@pytest.mark.parametrize('states,expected',[(['PASS']*3,'CONFORMANT'),(['PASS','UNKNOWN','UNKNOWN'],'PARTIAL'),(['FAIL','UNKNOWN','UNKNOWN'],'NONCONFORMANT'),(['UNKNOWN']*3,'INCONCLUSIVE')])
def test_all_outcomes(setup,states,expected):
    vm,obj,p,pid,docs=setup
    for d,s in zip(docs,states): d['reported']=s
    items=manifest(docs); aid=submit(obj,pid,items); mocks(vm,items,docs,rows(docs)); obj.evaluate(aid)
    assert json.loads(obj.get_receipt(aid,1))['body']['decision']['outcome']==expected
    assert vm.run_validator() is True

def test_actual_barrier(setup):
    vm,obj,p,pid,docs=setup; docs[0]=load('fail.json'); items=manifest(docs)
    aid=submit(obj,pid,items); mocks(vm,items,docs,rows(docs)); obj.evaluate(aid)
    assert json.loads(obj.get_receipt(aid,1))['body']['decision']['outcome']=='NONCONFORMANT'

def test_missing_coverage_cannot_pass(setup):
    vm,obj,p,pid,docs=setup; items=manifest(docs)[:1]; aid=submit(obj,pid,items)
    mocks(vm,items,docs[:1],[rows(docs)[0],unknown(docs[1]),unknown(docs[2])]); obj.evaluate(aid)
    assert json.loads(obj.get_receipt(aid,1))['body']['decision']['outcome']=='PARTIAL'

def test_empty_evidence_bounded_history(setup):
    vm,obj,p,pid,docs=setup; aid=submit(obj,pid,[]); prev=''
    for n in (1,2):
        h=obj.evaluate(aid); r=json.loads(obj.get_receipt(aid,n)); assert r['body']['previous_hash']==prev
        assert r['body']['decision']['outcome']=='INCONCLUSIVE'; assert vm.run_validator() is True; prev=h
    with pytest.raises(Exception,match='closed'): obj.evaluate(aid)

@pytest.mark.parametrize('change', ['hash','bytes','target','version','cell','json','http'])
def test_bad_source_no_support(setup,change):
    vm,obj,p,pid,docs=setup; items=manifest(docs)
    if change=='hash': items[0]['sha256']='0'*64
    if change=='bytes': items[0]['bytes']+=1
    if change in ('target','version'): docs[0][change]='wrong'; items=manifest(docs)
    if change=='cell': docs[0]['page']='/elsewhere'; raw=canon(docs[0]); items[0].update(sha256=hashlib.sha256(raw.encode()).hexdigest(),bytes=len(raw))
    aid=submit(obj,pid,items); result=[unknown(docs[0]),*rows(docs)[1:]]
    if change=='cell': result[0]['page']='/checkout'
    mocks(vm,items,docs,result)
    if change in ('json','http'):
        vm.clear_mocks()
        for i,(e,d) in enumerate(zip(items,docs)):
            vm.mock_web(e['url'],dict(method='GET',status=404 if change=='http' and i==0 else 200,body='broken' if i==0 else canon(d)))
        vm.mock_llm('.*',canon(result))
    obj.evaluate(aid); assert json.loads(obj.get_receipt(aid,1))['body']['decision']['outcome']=='PARTIAL'
    assert vm.run_validator() is True

@pytest.mark.parametrize('bad', ['invented_quote','missing_cell','duplicate_cell','extra_key','illegal_state','malformed','upgrade'])
def test_invalid_ai_is_unknown(setup,bad):
    vm,obj,p,pid,docs=setup
    if bad=='upgrade': docs[0]['reported']='FAIL'
    items=manifest(docs); aid=submit(obj,pid,items); result=rows(docs)
    if bad=='invented_quote': result[0]['observed_quote']='This never happened in this audit'
    if bad=='missing_cell': result.pop()
    if bad=='duplicate_cell': result[1]=result[0]
    if bad=='extra_key': result[0]['approved']=True
    if bad=='illegal_state': result[0]['state']='CONFORMANT'
    if bad=='malformed': result='not a JSON array'
    if bad=='upgrade': result[0]['state']='PASS'
    mocks(vm,items,docs,result); obj.evaluate(aid)
    assert json.loads(obj.get_receipt(aid,1))['body']['decision']['outcome']=='INCONCLUSIVE'

@pytest.mark.parametrize('fixture,index',[('injection.json',1),('contradiction.json',2)])
def test_semantic_unknown_fixtures(setup,fixture,index):
    # Scripted conservative responses test enforcement, not the model's ability to resist attacks.
    vm,obj,p,pid,docs=setup; docs[index]=load(fixture); items=manifest(docs); aid=submit(obj,pid,items)
    result=rows(docs); result[index]=unknown(docs[index]); mocks(vm,items,docs,result); obj.evaluate(aid)
    assert json.loads(obj.get_receipt(aid,1))['body']['decision']['outcome']=='PARTIAL'
    assert vm.run_validator() is True

def test_validator_disagreement(setup):
    vm,obj,p,pid,docs=setup; items=manifest(docs); aid=submit(obj,pid,items)
    mocks(vm,items,docs,rows(docs)); obj.evaluate(aid)
    changed=rows(docs); changed[0]=unknown(docs[0]); mocks(vm,items,docs,changed)
    assert vm.run_validator() is False

def test_validator_changed_source(setup):
    vm,obj,p,pid,docs=setup; items=manifest(docs); aid=submit(obj,pid,items)
    mocks(vm,items,docs,rows(docs)); obj.evaluate(aid)
    docs[0]['observed']='Different source content after leader retrieval.'; mocks(vm,items,docs,rows(docs))
    assert vm.run_validator() is False

def test_authorization_and_immutable_labels(setup,direct_charlie,direct_alice):
    vm,obj,p,pid,docs=setup; items=manifest(docs); aid=submit(obj,pid,items)
    with pytest.raises(Exception,match='already used'): submit(obj,pid,items)
    vm.sender=direct_charlie
    with pytest.raises(Exception,match='auditor'): submit(obj,pid,items,'other')
    with pytest.raises(Exception,match='Unauthorized'): obj.evaluate(aid)
    vm.sender=direct_alice
    with pytest.raises(Exception,match='already registered'): obj.register_policy(canon(p),importlib.import_module('genlayer').Address(json.loads(obj.get_policy(pid))['auditor']))

@pytest.mark.parametrize('url', ['http://127.0.0.1/x.json','https://raw.githubusercontent.com/a/b/main/x.json','https://raw.githubusercontent.com.evil/a/b/'+'a'*40+'/x.json','https://raw.githubusercontent.com/a/b/'+'a'*40+'/../x.json','https://raw.githubusercontent.com/a/b/'+'a'*40+'/x.json?q=1'])
def test_unsafe_urls(setup,url):
    vm,obj,p,pid,docs=setup; items=manifest(docs); items[0]['url']=url
    with pytest.raises(Exception): submit(obj,pid,items)

@pytest.mark.parametrize('bad', ['duplicate','unknown','negative','boolean','too_large','hash','manifest'])
def test_bad_manifests(setup,bad):
    vm,obj,p,pid,docs=setup; items=manifest(docs)
    if bad=='duplicate': items.append(items[0])
    if bad=='unknown': items[0]['requirement']='unknown'
    if bad=='negative': items[0]['bytes']=-1
    if bad=='boolean': items[0]['bytes']=True
    if bad=='too_large': items[0]['bytes']=6001
    if bad=='hash': items[0]['sha256']='ABC'
    with pytest.raises(Exception): obj.submit_audit(pid,'new',canon(items),'0'*64 if bad=='manifest' else digest(items))

@pytest.mark.parametrize('bad',['duplicate_page','duplicate_requirement','unknown_method','too_many_cells','empty_criteria','moving_build','extra_key'])
def test_bad_policy(setup,direct_bob,bad):
    vm,obj,p,pid,docs=setup
    if bad=='duplicate_page': p['pages']*=2
    if bad=='duplicate_requirement': p['requirements'].append(p['requirements'][0])
    if bad=='unknown_method': p['requirements'][0]['methods']=['MAGIC']
    if bad=='too_many_cells': p['pages']=['a','b','c','d']; p['requirements']*=2
    if bad=='empty_criteria': p['requirements'][0]['criterion']=''
    if bad=='moving_build': p['version']='latest'
    if bad=='extra_key': p['override']=True
    with pytest.raises(Exception): obj.register_policy(canon(p),importlib.import_module('genlayer').Address(direct_bob))

def test_duplicate_json_keys_rejected(setup,direct_bob):
    vm,obj,p,pid,docs=setup
    with pytest.raises(Exception): obj.register_policy('{"name":"a","name":"b"}',direct_bob)

def test_unknown_views(setup):
    vm,obj,p,pid,docs=setup
    for action in [lambda:obj.get_policy('x'),lambda:obj.get_audit('x'),lambda:obj.get_receipt('x',1),lambda:obj.evaluate('x')]:
        with pytest.raises(Exception): action()
