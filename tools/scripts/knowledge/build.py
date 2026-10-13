#!/usr/bin/env python3
"""Normalize one immutable JCC snapshot. Never import TFT content into JCC records."""
import argparse,collections,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def read(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
def payload(p,default=None):return read(p)['data'] if p.exists() else default
def signature(r):return tuple(sorted(map(str,r['equipIds'])))
def normalize(snapshot):
 m=read(snapshot/'manifest.json');raw=snapshot/'raw';ranking=payload(raw/'rank.json');previous=payload(raw/'previous-rank.json',[]);cat=payload(raw/'catalog.json');assert cat
 items={str(x['id']):x for x in cat['equip']};hexes={str(x['id']):x for x in cat['hex']}
 units={}
 for h in cat['hero']:
  if str(h['id']).startswith('1'):units[str(h['id'])[1:]]={'id':str(h['id'])[1:],'name':h['name'],'cost':h['price'],'purchasable':h['price']>0 and h['heroType']==0,'skill':h.get('skillDesc','')}
 missing=[];records=[];selected=[r for r in ranking if r['tier'] in m['cohort_policy']['tiers']]
 assert {x['compId'] for x in selected}==set(m['selected_ids'])
 def unit(uid,fallback=None):
  uid=str(uid)
  if uid not in units:
   missing.append('unit:'+uid);units[uid]={'id':uid,'name':fallback or '未映射棋子 '+uid,'cost':0,'purchasable':False,'skill':''}
  return units[uid]
 def item(i):
  i=str(i)
  if i not in items:missing.append('item:'+i);return {'id':i,'name':'未映射装备 '+i,'type':'未知'}
  return items[i]
 def name(i):return item(i)['name']
 tank_terms=['石像鬼','狂徒','振奋','棘刺','龙爪','救赎','坚定之心','日炎','薄暮','适应性头盔','冕卫','冰霜之心','圣盾','永恒烈焰']
 for rank in selected:
  cid=rank['compId'];folder=raw/'comps'/cid;d=payload(folder/'detail.json');assert d and d['compId']==cid
  conditions=[]
  for c in d['conditions']:
   value=str(c['value']);n=(hexes.get(value,{}).get('name') if c['type']=='hex' else items.get(value,{}).get('name'))
   if not n:missing.append('condition:'+value)
   conditions.append({'kind':'augment' if c['type']=='hex' else 'item','id':value,'name':n or value,'required':True,'evidence':'来源明确条件'})
  builds=collections.defaultdict(list)
  for e in d['equips']:builds[str(e['heroId'])].append(str(e['equipId']))
  heroes=[]
  for h in d['heroes']:
   uid=str(h['heroId']);u=unit(uid,h['heroName']);rec=builds[uid];r=dict(id=uid,name=h['heroName'],cost=h['price'],purchasable=u['purchasable'],stars=h['heroStarNum'],source_core=h['isCore'],role='挂件／功能位',role_evidence='未标记输出职责且无承装证据',items=rec,position=h.get('position'))
   if h['isCarry']:r.update(role='主C',role_evidence='来源主C标记')
   elif h['isSubCarry']:r.update(role='副C',role_evidence='来源副C标记')
   elif sum(any(t in name(i) for t in tank_terms) for i in rec)>=2:r.update(role='主坦候选',role_evidence='推荐防装推定；来源没有主坦字段')
   elif rec:r.update(role='承装功能位',role_evidence='来源有推荐装备；具体职责待核实')
   eq=payload(folder/'hero-equips'/f'{uid}.json',{}) or {};single=eq.get('heroEquips',[]);triples=eq.get('hero3Equips',[])
   def clean(rows,n):
    seen={};out=[]
    for x in rows:
     if x.get('tier') not in ('S','A') or len(x['equipIds'])!=n:continue
     key=signature(x)
     if key in seen:continue
     seen[key]=True
     for e in x.get('equips',[]):
      if str(e['id']) not in items:items[str(e['id'])]={'id':str(e['id']),'name':e['name'],'type':'未知'}
     out.append({'items':list(map(str,x['equipIds'])),'tier':x['tier'],'avg':x['avgPlacement'],'count':x['sampleCount']})
    return sorted(out,key=lambda x:(x['tier']!='S',x['avg'] is None,x['avg'] or 99,-x['count']))
   r['single_items']=clean(single,1);r['combinations']=clean(triples,3)
   exact=next((x for x in triples if signature(x)==tuple(sorted(rec))),None) if len(rec)==3 else None
   r['recommended_combination']={'items':rec,'tier':exact.get('tier') if exact else None,'avg':exact.get('avgPlacement') if exact else None,'count':exact.get('sampleCount') if exact else None,'evidence':'来源阵容推荐出装，不保证达到S/A'} if len(rec)==3 else None
   r['artifact_records']=[{'id':str(x['equipIds'][0]),'tier':x.get('tier'),'avg':x.get('avgPlacement'),'count':x.get('sampleCount')} for x in single if len(x['equipIds'])==1 and item(x['equipIds'][0]).get('type')=='神器装备']
   r['equipment_coverage']={'returned_single':len(single),'returned_triples':len(triples),'possible_limit':len(triples)>=200}
   if u['purchasable'] and not (folder/'hero-equips'/f'{uid}.json').exists():missing.append(f'equipment:{cid}:{uid}')
   heroes.append(r)
  # No fabricated source role: fallback is explicitly labelled as a recommendation.
  if not any(h['role']=='主C' for h in heroes):
   candidates=[h for h in heroes if h['items'] and h['role']!='主坦候选']
   if candidates:
    candidates.sort(key=lambda h:list(builds).index(h['id']))
    candidates[0].update(role='主C候选',role_evidence='来源配装主位推定；来源未标主C')
  carriers=[h for h in heroes if h['role'] in ('主C','主C候选')]
  desc=' '.join(unit(h['id'])['skill'] for h in carriers)
  physical='物理伤害' in desc;magic='魔法伤害' in desc
  group='混合' if physical and magic else '物理' if physical else '法系' if magic else '待核对'
  stages=[]
  for stage in payload(folder/'battle-builds.json',[]) or []:
   seen=set()
   for b in stage['builds']:
    ids=[str(h['heroBaseId']) for h in b['heroes']];buy=sorted({x for x in ids if unit(x)['purchasable']});key=tuple(buy)
    if key in seen:continue
    seen.add(key);stages.append({'level':stage['peopleNum'],'units':buy,'generated':sorted(set(ids)-set(buy)),'stars':{str(h['heroBaseId']):h.get('heroStarNum') for h in b['heroes']},'count':b['sampleCount'],'source_patch':b.get('gameVersion'),'source_id':b['id']})
  assert all(b['source_patch']==m['patch'] for b in stages),'mixed-patch stage records'
  final=[set(b['units']) for b in stages if b['level']>=8];core=sorted(set.intersection(*final)) if final else []
  rec_hex=payload(folder/'recommended-hexes.json',{}) or {};full_hex=payload(folder/'hexes.json',{}) or {};full_by={str(x['hexId']):x for x in full_hex.get('hexes',[])};aug=[]
  for x in rec_hex.get('hexes',[]):
   hid=str(x['id']);base=hexes.get(hid,{});stat=full_by.get(hid,{})
   if not base:missing.append('augment:'+hid)
   aug.append({'id':hid,'name':x['name'],'rarity':base.get('level',stat.get('level')),'count':x.get('pickCount'),'rounds':stat.get('rounds',[]),'avg':stat.get('avgPlacement'),'evidence':'来源推荐接口（按出现率；不代表因果强度）'})
  optional=sorted({i for h in heroes for i in h['items'] if item(i).get('type')=='转职纹章'}-{c['id'] for c in conditions if c['kind']=='item'})
  cost=carriers[0]['cost'] if carriers else None;star=carriers[0]['stars'] if carriers else None
  route=(f'{cost+4}级追三星' if cost in (1,2,3) and star==3 else '9级上限' if cost==5 else '8级找两星')
  if route=='5级追三星':flow=[['2阶段','不主动升人口，留目标牌'],['3-1前后','5级搜低费核心；稳血后留利息'],['核心三星后','升6／7补羁绊'],['后期','上8／9补高费上限']]
  elif route=='6级追三星':flow=[['2-1／2-5','升4／5，保留目标牌'],['3-2前后','升6；先补主C与前排两星'],['稳血后','留50金币慢D目标三星'],['核心成型后','升7／8补强']]
  elif route=='7级追三星':flow=[['2-1／2-5','升4／5，保留目标牌'],['3-2／3-5至4-1','升6再升7，视经济调整'],['7级','先D到主C、前排两星稳血'],['稳血后','慢D三星，成型后升8']]
  else:flow=[['2阶段','升4／5，用两星棋子过渡'],['3阶段','升6／7，留钱并保血'],['4-2前后','升8找主C、前排两星'],['稳血且经济足','升9补高费；不强行卖掉战力']]
  freq=collections.Counter()
  for h in heroes:
   if h['role']=='挂件／功能位':continue
   freq.update(i for i in h['items'] if item(i).get('type')=='成型装备')
  records.append({'id':cid,'key':f'jcc:s{m["set"]}:{m["patch"]}:{cid}','name':d['name'],'tier':rank['tier'],'avg':rank['avgPlacement'],'count':rank['sampleCount'],'top4':rank['top4Rate'],'win':rank['topRate'],'group':group,'group_evidence':'主C技能伤害类型归纳，双修需结合装备','heroes':heroes,'traits':d['traits'],'conditions':conditions,'optional_emblems':optional,'augments':aug,'stages':stages,'retained_core':core,'core_evidence':f'来源{len(final)}条8级以上棋盘的可购买棋子交集；不是全部打法永久核心','route':route,'flow':flow,'flow_evidence':'依据主C费用与来源目标星级整理的运营建议，非搜牌回合统计','equipment_frequency':[{'id':i,'count':n} for i,n in freq.most_common()],'source_url':BASE_COMP+cid,'coverage':{'stages':len(stages),'recommended_augments':len(aug),'full_augments':len(full_hex.get('hexes',[])),'role_inferred':any('推定' in h['role_evidence'] for h in heroes)}})
 # Stable source IDs, same query parameters. Role/roster drift blocks numeric attribution.
 previous_by={r['compId']:r for r in previous};current_by={r['compId']:r for r in ranking};changes=[]
 def board_sig(r):return sorted((str(h['heroId']),bool(h['isCarry']),bool(h['isSubCarry']),h['heroStarNum']) for h in r['heroes'])
 def condition_sig(r):return sorted((x['type'],str(x['value'])) for x in r['conditions'])
 for r in ranking:
  prev=previous_by.get(r['compId']);status='无上版记录' if not prev else '持续强势' if r['tier'] in ('S','A') and prev['tier'] in ('S','A') else '进入S/A' if r['tier'] in ('S','A') else '退出S/A' if prev['tier'] in ('S','A') else '未入选'
  if status=='未入选':continue
  comparable=bool(prev and board_sig(prev)==board_sig(r) and condition_sig(prev)==condition_sig(r))
  changes.append({'id':r['compId'],'name':r['name'],'status':status,'old_tier':prev['tier'] if prev else None,'tier':r['tier'],'old_avg':prev['avgPlacement'] if prev else None,'avg':r['avgPlacement'],'delta':round(r['avgPlacement']-prev['avgPlacement'],4) if comparable else None,'old_count':prev['sampleCount'] if prev else None,'count':r['sampleCount'],'same_definition':comparable,'low_sample':min(r['sampleCount'],prev['sampleCount'] if prev else 0)<1000})
 for prev in previous:
  if prev['compId'] not in current_by and prev['tier'] in ('S','A'):changes.append({'id':prev['compId'],'name':prev['name'],'status':'当前无记录','old_tier':prev['tier'],'tier':None,'old_avg':prev['avgPlacement'],'avg':None,'delta':None,'old_count':prev['sampleCount'],'count':None,'same_definition':False,'low_sample':True})
 indices={'augments':{},'items':{},'artifacts':{},'units':{},'boards':{}}
 for c in records:
  for a in c['augments']:indices['augments'].setdefault(a['id'],[]).append(c['id'])
  for h in c['heroes']:
   if h['purchasable']:indices['units'].setdefault(h['id'],[]).append(c['id'])
   for i in set(h['items']):indices['items'].setdefault(i,[]).append(c['id'])
   if h['role']!='挂件／功能位':
    for artifact in h['artifact_records']:
     indices['artifacts'].setdefault(artifact['id'],[]).append({'comp':c['id'],'unit':h['id'],**{k:artifact[k] for k in ('tier','avg','count')}})
  for b in c['stages']:indices['boards'].setdefault(str(b['level'])+':'+','.join(b['units']),[]).append(c['id'])
 for key in ('augments','units','items','boards'):indices[key]={k:sorted(set(v)) for k,v in indices[key].items()}
 indices['artifacts']={k:list({(x['comp'],x['unit']):x for x in v}.values()) for k,v in indices['artifacts'].items()}
 normalized={'schema_version':1,'release':{'platform':m['platform'],'set':m['set'],'patch':m['patch'],'previous_patch':m['previous_patch'],'snapshot':m['snapshot'],'fetched_at':m['fetched_at'],'source':m['source'],'rank_count':len(ranking),'comp_count':len(records),'source_battles':m['source_version']['battleCount'],'filters':m['filters'],'limits':m['source_limits'],'status':'来源返回范围内完成；统计口径及返回上限见说明'},'comps':records,'changes':changes,'units':{k:{a:b for a,b in v.items() if a!='skill'} for k,v in units.items()},'items':{k:{a:v.get(a) for a in ('id','name','type')} for k,v in items.items()},'augments':{k:{'id':k,'name':v['name'],'rarity':v.get('level')} for k,v in hexes.items()},'indices':indices,'quality':{'unmapped':sorted(set(missing)),'failed_requests':[r for r in m['requests'] if not r['ok']],'previous_comparison':'同来源、同查询、同ID及定义核对；段位、时间窗未公开，均名差仅描述来源样本，不证明补丁因果','catalog_note':'词库原始season字段与页面set标签有差异，以请求setId及榜单页面为准，未改写原始字段'}}
 dump(snapshot/'knowledge.json',normalized)
 print(json.dumps({'comps':len(records),'stages':sum(len(c['stages']) for c in records),'unmapped':normalized['quality']['unmapped'],'snapshot':str(snapshot.relative_to(ROOT))},ensure_ascii=False))
 return normalized
BASE_COMP='https://www.dataj.cc/comp/'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('snapshot',type=Path);a=p.parse_args();normalize(a.snapshot.resolve())
