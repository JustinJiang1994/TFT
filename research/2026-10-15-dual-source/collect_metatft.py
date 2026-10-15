import concurrent.futures, datetime, hashlib, json, pathlib, time, urllib.request, urllib.parse
ROOT=pathlib.Path(__file__).resolve().parent/'tft'
BASE='https://api-hc.metatft.com/tft-comps-api/'
logs=[]
def fetch(job):
 name,url=job
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as r: raw=r.read()
   d=json.loads(raw)
   if not isinstance(d,(dict,list)) or (isinstance(d,dict) and ('error' in d or d.get('success') is False)): raise ValueError('API error')
   p=ROOT/'raw'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
   logs.append({'file':'raw/'+name,'url':url,'ok':True,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
   return d
  except Exception as e:
   if attempt==2: logs.append({'file':'raw/'+name,'url':url,'ok':False,'error':str(e)});return None
   time.sleep(1+attempt)
d=fetch(('comps.json',BASE+'comps_data?queue=1100'))
if not d: raise SystemExit('Ranking unavailable')
a=d['results']['data'];cluster=a['cluster_id'];setname=a['tft_set']
filters={'queue':1100,'patch':'current','days':3,'rank':'CHALLENGER,DIAMOND,EMERALD,GRANDMASTER,MASTER,PLATINUM','cluster_id':cluster}
jobs=[('stats.json',BASE+'comps_stats?'+urllib.parse.urlencode(filters)),('lookup-zh_cn.json',f'https://data.metatft.com/lookups/{setname}_latest_zh_cn.json'),('lookup-en_us.json',f'https://data.metatft.com/lookups/{setname}_latest_en_us.json')]
for cid in a['cluster_details']:jobs.append((f'comps/{cid}.json',BASE+'comp_details?'+urllib.parse.urlencode({'comp':cid,'cluster_id':cluster})))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,jobs))
m={'platform':'tft','source':'https://www.metatft.com/comps','official':False,'set':setname,'cluster_id':cluster,'source_updated':d.get('updated'),'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rank_count':len(a['cluster_details']),'cohort':'all clusters returned, no tier cutoff','stats_request_filters':filters,'detail_filters':'source defaults; details endpoint has no explicit rank or days parameters','patch':'current alias; exact patch not yet verified','requests':sorted(logs,key=lambda x:x['file']),'limits':['Separate endpoint populations must not be assumed identical','All returned clusters is not all possible in-game compositions','No cross-platform strength equivalence inferred']}
(ROOT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
print(json.dumps({'rank_count':m['rank_count'],'ok':sum(x['ok'] for x in logs),'failed':[x for x in logs if not x['ok']]},ensure_ascii=False))
