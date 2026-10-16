from pathlib import Path
from html import escape as E
import json,shutil
from hex_priority import classify
from compact_tabs import compact
from guide_icons import decorate
from hex_icons import decorate_hex
from entity_details import add_entity_details
from hex_filter import add_filter
from fixed_cores import split_fixed
P=Path(__file__).resolve().parent;ROOT=P.parents[2];OLD=ROOT/'games/jcc/set18/18.4/snapshots/20261016T053609Z/data/raw';OUT=ROOT/'guides/金铲铲18.4版本攻略.html'
def read(p):return json.loads(p.read_text())
cat=read(P/'catalog.json')['data'];eq={str(x['id']):x for x in cat['equip']};hx={str(x['id']):x for x in cat['hex']};rows=[x for x in read(P/'rank.json')['data'] if x['tier'] in ['S','A']]
TANK={'104':['远古石甲虫'],'100':['伊莉丝','赫卡里姆'],'110':['瑟庄妮'],'87':['阿利斯塔'],'112':['阿木木'],'99':['苍蓝雕纹魔像','远古石甲虫'],'107':['远古石甲虫','苍蓝雕纹魔像'],'106':['峡谷迅捷蟹','瑟庄妮'],'113':['苍蓝雕纹魔像'],'115':['奥恩'],'114':['阿木木','苍蓝雕纹魔像'],'105':['莉莉娅'],'89':['茂凯','苍蓝雕纹魔像'],'116':['赫卡里姆']}
extra={'114':['厄斐琉斯','苍蓝雕纹魔像']}
CSS='''*{box-sizing:border-box}html{scroll-padding-top:16px}body{margin:0;background:#f5f4ef;color:#263446;font:16px/1.65 system-ui,-apple-system,"PingFang SC",sans-serif}main{max-width:1000px;margin:auto;padding:24px 16px 60px}h1{font-size:28px;margin:8px 0}h2{font-size:23px;margin:0}h3{font-size:18px;margin:0 0 8px}p{margin:8px 0}a{color:#176d67}.intro,.meta{font-size:13px;color:#5f6a71}.nav{display:flex;flex-wrap:wrap;gap:7px;margin:16px 0}.nav a{padding:8px 10px;min-height:44px;background:#e6eeea;border-radius:5px;text-decoration:none;font-size:14px}.comp{background:#fff;border:1px solid #d7e0dc;border-radius:9px;margin:20px 0;padding:20px}.rating{display:inline-block;background:#f2dfbb;color:#745016;padding:2px 10px;border-radius:4px;margin-right:8px}.rating.a{background:#dceee8;color:#176d67}.gate{font-size:14px;color:#885915}.hex{display:inline-block;padding:3px 7px;background:#eef3f0;border-radius:4px;margin:3px 3px 3px 0;font-size:14px}.hex-group{margin:12px 0;padding:10px 12px;background:#f5f7f5;border-radius:5px}.hex-entry{margin:6px 0}.hex-entry .meta{display:block;margin-left:7px}.heroes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:16px}.hero{border-top:2px solid #c6d9d0;padding:12px 0;min-width:0}.role{font-size:13px;color:#64766d;font-weight:400}.combo{margin:9px 0;padding:8px 10px;background:#f5f7f5;border-radius:5px}.combo b{display:block;font-size:14px;color:#176d67}.items{font-size:15px}.priority{font-size:14px;color:#176d67}.foot{font-size:13px;color:#66746c}details{margin-top:10px}summary{min-height:44px;padding:10px 0;cursor:pointer;font-size:14px;color:#176d67}@media(max-width:650px){main{padding:16px 12px 40px}.comp{padding:15px}.heroes{grid-template-columns:1fr;gap:0}h1{font-size:24px}h2{font-size:21px}}@media print{body{background:white}.nav{display:none}.hero{break-inside:avoid}.comp{break-before:auto}.heroes{display:block}}
'''
parts=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>金铲铲18.4｜阵容评级与核心配装</title><style>'+CSS+'</style></head><body><main id="top"><header><p class="meta">金铲铲国服 · 18.4 · 2026-10-16资料</p><h1>阵容评级与核心配装</h1><p>只查四项：评级、推荐海克斯、成型核心、装备组合优先级。</p><p class="intro">装备先看样本：≥100的组合优先，其内按来源S/A、默认推荐、统计备选排序；低于100的组合后置。100是本文保守展示门槛，不是显著性检验；若全部样本不足，首套明确标为暂选。三件套中的“＋”不表示合成先后。主C与主坦先拿装备，再考虑副C。</p><p class="intro">海克斯分档为机制建议，不是来源胜率排名；“必拿”仅指该分支的必要条件，无必要条件就写“无”。优先拿仍须满足旁注，且只在实际可选品质和回合内比较。</p><nav class="nav">'+''.join(f'<a href="#c{r["compId"]}">{r["tier"]} · {E(r["name"])}</a>' for r in rows)+'</nav></header>']
audit=[]
hex_audit={}
for r in rows:
 cid=r['compId'];d=read(P/(cid+'.json'))['data'];cond=[];allowed=set()
 for c in d.get('conditions',[]):
  val=str(c['value']);cond.append((eq if c['type']=='equip' else hx).get(val,{}).get('name',val))
  if c['type']=='equip':allowed.add(val)
 if cid=='116':cond.append('卡兹克已进化裁决')
 hs=[h for h in d['heroes'] if h['heroType']==0 and (h['isCore'] or h['isCarry'] or h['isSubCarry'] or h['heroName'] in extra.get(cid,[]))]
 def role(h):
  if h['isCarry'] or (cid=='114' and h['heroName']=='厄斐琉斯'):return '主C'
  if h['heroName'] in TANK.get(cid,[]):return '主坦／前排核心'
  if h['isSubCarry']:return '副C'
  if any(str(x['heroId'])==str(h['heroId']) for x in d.get('equips',[])):return '副输出／功能携装'
  return '羁绊／功能核心'
 hs.sort(key=lambda h:{'主C':0,'主坦／前排核心':1,'副C':2,'副输出／功能携装':3,'羁绊／功能核心':4}[role(h)])
 parts.append(f'<section class="comp" id="c{cid}"><h2><span class="rating {"a" if r["tier"]=="A" else ""}">{r["tier"]}</span>{E(r["name"])}</h2><p class="gate">'+E('前提：'+'；'.join(cond) if cond else '无额外转职／专属强化条件')+'</p><p><b>最终成型核心：</b>'+E('、'.join(h['heroName'] for h in hs))+'</p>')
 rec=read(OLD/f'comps/{cid}/recommended-hexes.json')['data'].get('hexes',[])
 groups=classify(cid,rec,d.get('conditions',[]));hex_audit[cid]=groups
 parts.append('<p><b>推荐海克斯：</b></p>')
 for group,entries in groups.items():
  parts.append('<div class="hex-group"><b>'+group+'</b>')
  if not entries:parts.append('<span class="meta"> 无；该阵不依赖某个指定海克斯。</span>')
  for x in entries:
   parts.append('<div class="hex-entry"><span class="hex">'+E(x['name'])+'</span><span class="meta">'+E(x['reason'] or '按当前装备、经济与阵容缺口选取。')+'</span></div>')
  parts.append('</div>')
 if cid=='114':parts.append('<p class="gate">此分支海克斯最高仅13次选取；分档仅作机制建议，不按小样本频次硬排。</p>')
 parts.append('<div class="heroes">')
 for h in hs:
  hid=str(h['heroId']);default=[str(x['equipId']) for x in d.get('equips',[]) if str(x['heroId'])==hid];path=OLD/f'comps/{cid}/hero-equips/{hid}.json';raw=read(path)['data'].get('hero3Equips',[]) if path.exists() else []
  def permitted(x):
   ids=list(map(str,x['equipIds']))
   if len(ids)!=3:return False
   if not all(eq.get(i,{}).get('type')=='成型装备' or i in allowed for i in ids):return False
   # Source-designated emblem holders must keep their emblem in every proposed set.
   required=set(default)&allowed
   return required.issubset(ids)
  eligible=[x for x in raw if permitted(x)]
  best=sorted([x for x in eligible if x.get('tier') in ['S','A']],key=lambda x:({'S':0,'A':1}[x['tier']],x['avgPlacement'],-x['sampleCount']))
  choices=[];seen=set()
  def add(ids,label,stats=None):
   key=tuple(sorted(map(str,ids)))
   if key in seen:return
   seen.add(key);choices.append((list(map(str,ids)),label,stats))
  functional=role(h)=='羁绊／功能核心'
  if not functional:
   for x in best:add(x['equipIds'],'来源'+x['tier']+'级组合',x)
   if len(default)==3:add(default,'来源默认组合',next((x for x in raw if sorted(map(str,x['equipIds']))==sorted(default)),None))
   # At most two fallback combinations; no truncation of source S/A sets.
   fallback=sorted([x for x in eligible if x['sampleCount']>=10],key=lambda x:(0 if x['sampleCount']>=100 else 1,'SABCD'.find(x['tier']) if x.get('tier') in list('SABCD') else 5,x['avgPlacement'],-x['sampleCount']))
   count=0
   for x in fallback:
    if tuple(sorted(map(str,x['equipIds']))) in seen:continue
    add(x['equipIds'],'统计备选'+(' · 来源'+x['tier'] if x.get('tier') else ' · 未评级'),x);count+=1
    if count==2:break
  def confidence_order(choice):
   ids,label,st=choice
   n=st['sampleCount'] if st else 0
   category=0 if label.startswith('来源S') else 1 if label.startswith('来源A') else 2 if label=='来源默认组合' else 3
   if n>=100:return (0,category,st['avgPlacement'],-n)
   if st is None and label=='来源默认组合':return (1,0,0,0)
   return (2,-n,category,st['avgPlacement'] if st else 99)
  choices.sort(key=confidence_order)
  parts.append('<article class="hero"><h3>'+E(h['heroName'])+' <span class="role">'+role(h)+'</span></h3>')
  if not choices:parts.append('<p class="meta">'+('不优先分配成装，保留其羁绊／技能作用。' if functional else '本分支没有足够的推荐三件套证据，暂不编造配装排名。')+'</p>')
  for i,(ids,label,st) in enumerate(choices,1):
   special=[eq[z]['name'] for z in ids if z in allowed]
   parts.append('<div class="combo"><b>'+('最推荐' if i==1 and st and st['sampleCount']>=100 else '暂选首套（缺高样本）' if i==1 else '备选'+str(i-1))+' · '+E(label)+'</b><div class="items">'+E(' ＋ '.join(eq[z]['name'] for z in ids))+'</div>')
   if special:parts.append('<p class="gate">仅在本棋子持有'+E('、'.join(special))+'时可用；占一个装备槽。</p>')
   if st:parts.append('<span class="meta">均名'+str(st['avgPlacement'])+' · 样本'+str(st['sampleCount'])+(' · 小样本，仅供参考' if st['sampleCount']<100 else '')+'</span>')
   else:parts.append('<span class="meta">来源推荐，未匹配到组合统计</span>')
   parts.append('</div>')
  parts.append('</article>');audit.append({'comp':cid,'hero':hid,'role':role(h),'sourceSA':len(best),'choices':[{'ids':a,'label':b,'sample':c['sampleCount'] if c else None} for a,b,c in choices]})
 parts.append('</div><details><summary>评级与配装口径</summary><p class="foot">来源终局样本'+str(r['sampleCount'])+'；海克斯保留接口全部推荐，按必要条件与机制适配分档，选取频次不当胜率。核心采用来源核心标记并核对携装职责；5迅射月男补正来源漏标的月男与大蓝。普通成装与本分支转职纳入配装；神器、光明及无关转职不混排。统计备选只取样本≥10的前两套，不等于全部可用装备。装备统计未统一星级，不能直接推断同星级强弱。</p><a href="https://www.dataj.cc/comp/'+cid+'">查看阵容来源</a></details></section>')
parts.append('<footer class="foot">14套S/A · 同日金铲铲18.4快照 · 来源S/A组合完整保留。评级带条件的阵容必须满足上方前提。旧攻略已归档。</footer></main></body></html>')
for dest in [OUT,OUT.with_name('金铲铲18.4手机版速查.html')]:
 backup=dest.with_name(dest.stem+'-旧版-简表重做前.html')
 if dest.exists() and not backup.exists():shutil.copy2(dest,backup)
 dest.write_text(add_filter(split_fixed(add_entity_details(decorate_hex(decorate(compact(''.join(parts),rows)))))))
(P/'hex-priority-audit.json').write_text(json.dumps(hex_audit,ensure_ascii=False,indent=2))
(P/'core-list-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps({'comps':len(rows),'core_units':len(audit),'combinations':sum(len(x['choices']) for x in audit),'output':str(OUT)},ensure_ascii=False))
