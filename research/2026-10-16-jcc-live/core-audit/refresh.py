import json,pathlib,urllib.request,datetime,hashlib,concurrent.futures
P=pathlib.Path(__file__).resolve().parent;S=P.parents[2]/'games/jcc/set18/18.4/snapshots/20261016T053609Z/data/raw'
# Current entrypoints, scoped to the same patch; no release updates.
rows=json.loads((P.parent/'research-data.json').read_text())['rank']
jobs=[('catalog','https://www.dataj.cc/api/web/gamedata?setId=18'),('rank','https://www.dataj.cc/api/web/comp/rank?setId=18&gameVersion=18.4&minSample=1')]+[(str(x['compId']),'https://www.dataj.cc/api/web/comp/'+str(x['compId'])+'?setId=18&gameVersion=18.4') for x in rows if x['tier'] in ['S','A']]
def get(j):
 name,url=j;rec={'name':name,'url':url,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as f:b=f.read()
  d=json.loads(b);assert d.get('success') is True and d.get('data') is not None
  (P/(name+'.json')).write_bytes(b);rec.update(ok=True,sha256=hashlib.sha256(b).hexdigest())
 except Exception as ex:rec.update(ok=False,error=str(ex))
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:res=list(pool.map(get,jobs))
(P/'manifest.json').write_text(json.dumps(res,ensure_ascii=False,indent=2));print(json.dumps(res,ensure_ascii=False))
