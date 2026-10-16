import pathlib,json,urllib.request,concurrent.futures,datetime,hashlib
P=pathlib.Path(__file__).resolve().parent;S=P.parents[1]/'games/jcc/set18/18.4/snapshots/20261016T053609Z/data/raw';O=P/'transitions';O.mkdir(exist_ok=True)
rank=json.loads((S/'rank.json').read_text())['data']
def run(r):
 cid=r['compId'];url=f'https://www.dataj.cc/api/web/comp/{cid}/battle-builds?setId=18&gameVersion=18.4';row={'compId':cid,'name':r['name'],'url':url,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as f:raw=f.read()
  d=json.loads(raw);assert d.get('success') is True and isinstance(d.get('data'),list)
  (O/f'{cid}.json').write_bytes(raw);row.update(ok=True,sha256=hashlib.sha256(raw).hexdigest())
 except Exception as e:row.update(ok=False,error=str(e))
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(run,rank))
(O/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps({'ok':sum(r['ok'] for r in rows),'failures':[r for r in rows if not r['ok']]}))
