"""Resume source-backed public S18 endpoints; never equate HTTP 200 with success."""
import datetime,hashlib,json,pathlib,secrets,time,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'resumed';OUT.mkdir(exist_ok=True)
STATE=OUT/'state.json'
state=json.loads(STATE.read_text()) if STATE.exists() else {'source':'https://jcc.datatft.com/','scope':{'season':'18','version':'jcc_18.3','tier':'grandmaster','time':5},'requests':{},'attempts':[]}
did=state.setdefault('anonymous_device_id','did_'+secrets.token_hex(4)+'_'+str(int(time.time()*1000)))
def save():
 state['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2))
def request(key,path,body,method='POST'):
 old=state['requests'].get(key,{})
 if old.get('ok') and (OUT/old['file']).exists():return json.loads((OUT/old['file']).read_text())['data']
 stamp=str(int(time.time()*1000));nonce=secrets.token_hex(8)
 headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0','Origin':'https://jcc.datatft.com','Referer':'https://jcc.datatft.com/','App-Platform':'jcc','Accept-Language':'CN','Browser-Language':'ZH-CN','did':did,'t':stamp,'nonce':nonce,'signature':hashlib.md5((stamp+nonce+did+'koTefnFEdaYDuLFmXyzt').encode()).hexdigest()}
 url='https://api.datatft.com'+path
 if method=='GET':url+='?'+urllib.parse.urlencode(body)
 rec={'key':key,'url':url,'method':method,'body':body,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ok':False}
 try:
  req=urllib.request.Request(url,headers=headers,data=json.dumps(body,separators=(',',':')).encode() if method=='POST' else None,method=method)
  with urllib.request.urlopen(req,timeout=25) as resp:raw=resp.read();rec['http_status']=resp.status
  d=json.loads(raw);rec['api_code']=d.get('code');rec['ok']=d.get('code')==1 and d.get('data') is not None
  rel=('data/' if rec['ok'] else 'failures/')+key+'.json';p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  rec.update(file=rel,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
  if not rec['ok']:rec['error']='Source API returned non-success'
 except Exception as e:rec['error']=str(e)
 state['requests'][key]=rec;state['attempts'].append(rec.copy());save();print(key,'OK' if rec['ok'] else rec.get('api_code',rec.get('error')),flush=True)
 time.sleep(.5)
 return d['data'] if rec['ok'] else None
scope=state['scope']
rank=request('team-list','/team/list',scope)
rows=(rank or json.loads((ROOT/'raw/team-list.json').read_text())['data'])['list']
for name,path,params,method in [
 ('team-comps','/team/comps',{'season':'18'},'POST'),
 ('team-rank','/team/rank',{'season':'18'},'POST'),
 ('home','/team/home',{**scope,'gamePlatform':2},'POST'),
 *[(f'stats-{k}','/data/explore/list',{'version':'jcc_18.3','tier':'grandmaster','filterTargetType':k},'POST') for k in ['hero','equip','trait']],
 ('augment-config','/augment-tier/config',{'platform':'jcc','season':'18'},'GET')]:request(name,path,params,method)
ids=sorted({int(r.get('strategyId') or r['id']) for r in rows})
for cid in ids:
 if request('strategies/'+str(cid),'/team/strategy',{'id':cid}) is None:
  state['strategy_circuit_breaker']='First failed strategy stops this endpoint family until next cycle';break
required=['team-list','team-comps','team-rank','home','stats-hero','stats-equip','stats-trait','augment-config']+['strategies/'+str(cid) for cid in ids]
state['required_keys']=required;state['pending_keys']=[k for k in required if not state['requests'].get(k,{}).get('ok')]
state['endpoint_coverage_complete']=not state['pending_keys'];state['full_collection_complete']=False
state['completion_note']='Even after endpoint coverage, inspect pagination, returned detail IDs, static equipment tiers, schema and field gaps before declaring full completion.'
save();print(json.dumps({'pending':len(state['pending_keys']),'successful':len(required)-len(state['pending_keys']),'full_collection_complete':False}))
