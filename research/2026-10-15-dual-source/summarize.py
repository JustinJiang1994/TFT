import pathlib,json,hashlib,collections,datetime
root=pathlib.Path(__file__).resolve().parent;p=root/'tft'
load=lambda f:json.loads(f.read_text())
m=load(p/'manifest.json')
for x in m['requests']:
 assert x['ok'] and hashlib.sha256((p/x['file']).read_bytes()).hexdigest()==x['sha256']
lookup=load(p/'raw/lookup-zh_cn.json'); names={v['apiName']:v['name'] for key in ['units','traits','items','augments'] for v in lookup[key]}
a=load(p/'raw/comps.json')['results']['data']['cluster_details']
stats={str(r['cluster']):r for r in load(p/'raw/stats.json')['results'] if r.get('cluster')}
coverage=collections.Counter();rows=[]
for cid,c in a.items():
 d=load(p/f'raw/comps/{cid}.json')['results'];assert str(d['cluster'])==cid
 for k,v in d.items():
  if v: coverage[k]+=1
 coverage['identified_augment_stats']+=int(any(x.get('aug') for x in d.get('augments',[])))
 coverage['early_board_records']+=sum(len(v) for v in d.get('early_options',{}).values())
 coverage['final_board_records']+=sum(len(v) for v in d.get('options',{}).values())
 r={'id':cid,'name_zh':' / '.join(names.get(x['name'],x['name']) for x in c['name']),'unit_ids':[x.strip() for x in c['units_string'].split(',')],'source_overall_default':c.get('overall'),'stats_filtered':None,'detail_file':f'raw/comps/{cid}.json'}
 s=stats.get(cid);places=s.get('places',[])[:8] if s else []
 if len(places)==8 and sum(places)>0:
  n=sum(places);r['stats_filtered']={'count':n,'avg_placement':sum((i+1)*v for i,v in enumerate(places))/n,'top4_rate':sum(places[:4])/n,'win_rate':places[0]/n,'placement_counts':places}
 rows.append(r)
(p/'comps-index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
m['lookup_metadata']=lookup['_metadata'];m['limits']+=['Chinese latest lookup metadata says patch=pbe; do not present its numbers as verified live-server values','Augment statistics use empty augment ids; pro guide recommendations are distinct from measured augment win rates']
(p/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
jcc=pathlib.Path(__file__).resolve().parents[2]/'games/jcc/set18/18.3/snapshots/20261015T020123Z/data'
j=load(jcc/'inventory.json')
out={'collected_date_local':'2026-10-15','jcc':{'data_path':str(jcc),'rank_count':j['rank_count'],'detail_count':j['detailed_comp_count'],'board_records':j['board_records'],'patch':j['patch'],'successful_requests':j['successful_requests']},'tft':{'source':'https://www.metatft.com/comps','set':m['set'],'patch':m['patch'],'rank_count':len(rows),'detail_count':len(rows),'successful_requests':len(m['requests']),'catalog_raw_counts':{k:len(lookup[k]) for k in ['units','traits','items','augments']},'coverage':dict(coverage),'lookup_metadata':lookup['_metadata'],'stats_filters':m['stats_request_filters'],'integrity_verified':True},'design_notes':['两端可共用产品结构，保留独立平台、版本、统计口径和评级字段','未核验阵容对应关系，不能从双端抓取成功推断强度一致','MetaTFT current是动态补丁别名；词库标记pbe，具体正式服补丁及技能数值仍需核对','金铲铲全榜38套，详情仅S/A 15套；MetaTFT详情覆盖返回的60个分组','原始详情保留完整返回字段；未提取高手攻略推荐，不把空强化ID当成有效统计']}
(root/'inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False))
