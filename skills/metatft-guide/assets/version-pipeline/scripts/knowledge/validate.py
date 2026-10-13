#!/usr/bin/env python3
"""Validate cohort selection, provenance, snapshot isolation and generated relations."""
import argparse,hashlib,json
from pathlib import Path
def validate(snapshot):
 k=json.loads((snapshot/'knowledge.json').read_text());m=json.loads((snapshot/'manifest.json').read_text());raw=snapshot/'raw';rank=json.loads((raw/'rank.json').read_text())['data'];ids={c['id'] for c in k['comps']}
 assert ids=={r['compId'] for r in rank if r['tier'] in m['cohort_policy']['tiers']},'S/A cohort incomplete'
 assert len(ids)==len(k['comps'])==k['release']['comp_count']
 assert k['release']['platform']==m['platform']=='jcc' and k['release']['patch']==m['patch']
 assert not k['quality']['failed_requests'],'Fetch incomplete: do not publish a mixed snapshot'
 for req in m['requests']:
  assert hashlib.sha256((snapshot/req['file']).read_bytes()).hexdigest()==req['sha256'],'Raw snapshot changed'
 assert k['comps'],'Empty cohort'
 for c in k['comps']:
  assert c['key'].startswith(f'jcc:s{m["set"]}:{m["patch"]}:')
  assert c['source_url'].endswith('/'+c['id']) and c['source_url'].startswith(m['source'])
  for b in c['stages']:
   assert b['source_patch']==m['patch'];assert len(b['units'])==len(set(b['units']))
   assert all(k['units'][u]['purchasable'] for u in b['units']),'Generated unit entered purchase candidates'
   assert c['id'] in k['indices']['boards'][str(b['level'])+':'+','.join(b['units'])]
  finals=[set(b['units']) for b in c['stages'] if b['level']>=8]
  assert set(c['retained_core'])==(set.intersection(*finals) if finals else set())
  for a in c['augments']:assert c['id'] in k['indices']['augments'][a['id']]
  for h in c['heroes']:
   for b in h['combinations']:
    assert len(b['items'])==3 and b['tier'] in ('S','A') and all(i in k['items'] for i in b['items'])
 for key in ('augments','units','items','boards'):
  assert all(set(v)<=ids and len(v)==len(set(v)) for v in k['indices'][key].values())
 for refs in k['indices']['artifacts'].values():assert refs and all(x['comp'] in ids for x in refs)
 assert all(x['delta'] is None for x in k['changes'] if not x['same_definition'])
 result={'compositions':len(ids),'stage_boards':sum(len(c['stages']) for c in k['comps']),'source_limits':m['source_limits'],'unmapped':k['quality']['unmapped'],'status':'PASS'}
 print(json.dumps(result,ensure_ascii=False));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('snapshot',type=Path);a=p.parse_args();validate(a.snapshot.resolve())
