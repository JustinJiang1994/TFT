#!/usr/bin/env python3
"""Archive a complete public DataJCC ranking and details for its current S/A cohort."""
import argparse, concurrent.futures, datetime as dt, hashlib, json, re, time, urllib.request, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE='https://www.dataj.cc'
def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
def request(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'TFT-guide-version-collector/1.0'}),timeout=40) as r:return r.read()
        except Exception:
            if attempt==2:raise
            time.sleep(attempt+1)
def api_url(path,**query):return BASE+'/api/web'+path+('?' + urllib.parse.urlencode(query) if query else '')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--set',type=int);ap.add_argument('--patch');args=ap.parse_args()
    html=request(BASE+'/comp').decode();flight=''
    for x in re.findall(r'self\.__next_f\.push\((.*?)\)</script>',html):
        try:
            a=json.loads(x)
            if len(a)>1 and isinstance(a[1],str):flight+=a[1]
        except (ValueError,TypeError):pass
    set_id=args.set or int(re.search(r'"initialSetId":(\d+)',flight)[1])
    versions_body=request(api_url('/gamedata/gameVersion',setId=set_id));versions=json.loads(versions_body)['data'];versions=sorted(versions,key=lambda x:x['startTime'],reverse=True)
    patch=args.patch or versions[0]['gameVersion'];idx=next(i for i,v in enumerate(versions) if v['gameVersion']==patch);previous=versions[idx+1]['gameVersion'] if idx+1<len(versions) else None
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=ROOT/'games/jcc'/f'set{set_id}'/patch/'snapshots'/stamp/'data';out.mkdir(parents=True,exist_ok=False)
    (out/'raw').mkdir();(out/'raw/list.html').write_text(html);(out/'raw/versions.json').write_bytes(versions_body)
    logs=[]
    def fetch(job):
        name,url=job;t0=dt.datetime.now(dt.timezone.utc).isoformat()
        try:
            raw=request(url);data=json.loads(raw)
            if data.get('success') is not True or 'data' not in data:raise ValueError('API did not confirm success')
            p=out/'raw'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            log={'file':str(p.relative_to(out)),'url':url,'retrieved_at':t0,'ok':True,'sha256':hashlib.sha256(raw).hexdigest()};logs.append(log);return data['data']
        except Exception as e:logs.append({'file':'raw/'+name,'url':url,'retrieved_at':t0,'ok':False,'error':str(e)});return None
    query=dict(setId=set_id,gameVersion=patch)
    rows=fetch(('rank.json',api_url('/comp/rank',**query,minSample=1)))
    if not isinstance(rows,list) or not rows:raise RuntimeError('Missing complete ranking; no release generated')
    assert len({r['compId'] for r in rows})==len(rows)
    selected=[r for r in rows if r.get('tier') in ('S','A')]
    if not selected:raise RuntimeError('No S/A cohort; review source schema')
    jobs=[('catalog.json',api_url('/gamedata',setId=set_id))]
    if previous:jobs.append(('previous-rank.json',api_url('/comp/rank',setId=set_id,gameVersion=previous,minSample=1)))
    endpoints={'detail':'','heroes':'/heroes','equips':'/equips','hexes':'/hexes','recommended-hexes':'/recommended-hexes','battle-builds':'/battle-builds','trend':'/trend'}
    for r in selected:
        cid=r['compId']
        for key,suffix in endpoints.items():jobs.append((f'comps/{cid}/{key}.json',api_url('/comp/'+cid+suffix,**({} if key=='trend' else query))))
        for h in r['heroes']:
            if h.get('price',0)>0:jobs.append((f'comps/{cid}/hero-equips/{h["heroId"]}.json',api_url('/comp/'+cid+'/hero-equips',**query,heroId=h['heroId'])))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,jobs))
    manifest={'schema_version':1,'platform':'jcc','set':set_id,'patch':patch,'previous_patch':previous,'snapshot':stamp,'fetched_at':dt.datetime.now(dt.timezone.utc).isoformat(),'source':BASE,'official':False,'source_version':versions[idx],'cohort_policy':{'tiers':['S','A'],'min_source_sample':1,'low_sample_warning':1000,'fixed_count':False},'filters':{'rank':None,'time_window':None,'mode':'来源默认模式；接口未提供队列字段'},'rank_count':len(rows),'selected_ids':[r['compId'] for r in selected],'requests':sorted(logs,key=lambda x:x['file']),'source_limits':['battle-builds接口每等级通常返回3组，非全量游戏组合；limit=100测试未增加返回数','hero3Equips存在200组返回上限；保留全部返回记录，不声称穷尽所有配装','推荐强化接口最多10项，属于来源推荐集合；全量使用统计单独归档','catalog按赛季获取，未提供历史补丁参数，不用于历史技能数值对比']}
    dump(out/'manifest.json',manifest)
    print(json.dumps({'snapshot':str(out.relative_to(ROOT)),'rank':len(rows),'selected':len(selected),'fetched':sum(x['ok'] for x in logs),'failed':[x for x in logs if not x['ok']]},ensure_ascii=False))
if __name__=='__main__':main()
