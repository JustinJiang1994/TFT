import json,re
from pathlib import Path
from html import escape as E
P=Path(__file__).resolve().parent

def split_fixed(html):
 old=P.parents[2]/'games/jcc/set18/18.4/snapshots/20261016T053609Z/data/raw/comps';records=[]
 def panel(m):
  cid,body=m[1],m[2];detail=json.loads((P/(cid+'.json')).read_text())['data'];base={h['heroName']:str(h['heroId']) for h in detail['heroes'] if h['heroType']==0};carry={str(h['heroId']) for h in detail['heroes'] if h['isCarry'] and h['heroType']==0}
  if cid=='114':carry={base['厄斐琉斯']}
  minlevel=9 if cid in ['89','112','113'] else 8
  groups=json.loads((old/cid/'battle-builds.json').read_text())['data'];sets=[];buildids=[];excluded=[]
  for g in groups:
   if g['peopleNum']<minlevel:continue
   for b in g['builds']:
    ids={str(h['heroBaseId']) for h in b['heroes'] if h['heroType']==0}
    if not carry.issubset(ids):excluded.append(b['id']);continue
    sets.append(ids);buildids.append(b['id'])
  assert sets,cid
  common=set.intersection(*sets);fixed=[];variable=[]
  def heroes(mm):
   for h in re.findall(r'<article class="hero">.*?</article>',mm[1],re.S):
    name=re.search(r'data-entity="hero:([^"]+)"',h)[1]
    if base[name] in common:fixed.append((name,h))
    else:variable.append((name,h.replace('主坦／前排核心','变体前排').replace('羁绊／功能核心','变体功能位')))
   assert fixed,cid
   return '<p class="hex-note"><b>固定核心</b> · 成型变体保留的棋子</p><div class="heroes">'+''.join(h for _,h in fixed)+'</div>'+('<details class="variant-heroes"><summary>变体可替换棋子与配装（'+str(len(variable))+'位）</summary><p class="meta">以下棋子在已收录成型变体中并非每套都保留，不计入固定核心。</p><div class="heroes">'+''.join(h for _,h in variable)+'</div></details>' if variable else '')+'<details class="hex-reasons">'
  body,n=re.subn(r'<div class="heroes">(.*?)</div><details class="hex-reasons">',heroes,body,count=1,flags=re.S);assert n==1,cid
  note='固定核心核对范围：来源已收录的'+str(minlevel)+'人口及以上、保留本阵主C的'+str(len(sets))+'个终局变体；在原核心候选中取共同保留者，不代表已穷尽所有理论变体。'
  if cid=='115':assert {n for n,_ in fixed}=={'阿卡丽','奥恩','卡蜜尔','韦鲁斯','蕾欧娜'}
  body=body.replace('核心采用来源核心标记并核对携装职责；5迅射月男补正来源漏标的月男与大蓝。',note)
  records.append({'comp':cid,'minLevel':minlevel,'buildIds':buildids,'excludedDifferentCarry':excluded,'fixed':[n for n,_ in fixed],'variable':[n for n,_ in variable]})
  return m[0].replace(m[2],body,1)
 html=re.sub(r'<section class="comp" id="c(\d+)"[^>]*>(.*?)</section>',panel,html,flags=re.S)
 (P/'fixed-cores-audit.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));return html
