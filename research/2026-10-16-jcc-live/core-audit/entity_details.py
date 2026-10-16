import json,re
from pathlib import Path
from html import escape as E,unescape
P=Path(__file__).resolve().parent
CSS='''
.entity-button{font:inherit;color:inherit;background:none;border:0;padding:0;margin:0;cursor:pointer;text-align:left;vertical-align:baseline;line-height:inherit}.entity-button:focus-visible{outline:2px solid #176d67;outline-offset:2px;border-radius:2px}.entity-button:hover{color:#176d67}.entity-button.equip-name{display:inline-block;white-space:nowrap}.hero h3 .entity-button{font-weight:inherit}.entity-dialog .trait-entry{border-top:1px solid #e1e7e3;padding-top:8px;margin-top:9px}.entity-dialog .trait-entry h3{margin:0 0 5px}.entity-dialog .recipe{display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:15px}.entity-dialog .recipe-piece{display:inline-flex;align-items:center;gap:5px}.entity-dialog .recipe img{width:22px;height:22px}.entity-dialog details>summary{font-size:13px;min-height:36px;padding:8px 0}.entity-dialog .detail-note{font-size:12px;color:#647168}.entity-dialog .trait-entry p{font-size:14px}
'''
JS='''
(()=>{const data=JSON.parse(document.getElementById('entity-data').textContent),d=document.getElementById('entity-dialog'),body=document.getElementById('entity-body');let opener;
function node(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n}
function section(title,text){body.append(node('h3',title),node('p',text))}
document.querySelectorAll('.entity-button').forEach(b=>b.addEventListener('click',()=>{const x=data[b.dataset.entity];opener=b;document.getElementById('entity-title').textContent=x.name;document.getElementById('entity-icon').src=x.icon;body.replaceChildren();
if(x.kind==='hero'){body.append(node('p',x.cost+'费 · '+x.traits.map(t=>t.name).join(' / '),'context'));section('技能 · '+x.skillName,x.skill);if(x.skillValues){const dt=node('details');dt.append(node('summary','技能分星级参数（词库原文）'),node('p',x.skillValues));body.append(dt)}if(x.dynamic)body.append(node('p','“动态值”或属性占位尚未由词库展开；请结合下方技能参数，不视为固定伤害或次数。','detail-note'));body.append(node('h3','羁绊'));for(const t of x.traits){const a=node('div',undefined,'trait-entry');a.append(node('h3',t.name),node('p',t.description));if(t.levels)a.append(node('p',t.levels));body.append(a)}if(x.note)body.append(node('p',x.note,'detail-note'));}
else{body.append(node('p',x.type,'context'));section('属性',x.stats||'词库未提供基础属性');section('效果',x.effect||'词库未提供效果');body.append(node('h3','合成配方'));if(x.recipe.length===2){const r=node('div',undefined,'recipe');x.recipe.forEach((part,i)=>{if(i)r.append(node('span','＋'));const c=node('span',undefined,'recipe-piece'),img=node('img');img.src=part.icon;img.alt='';img.referrerPolicy='no-referrer';c.append(img,node('span',part.name));r.append(c)});body.append(r)}else body.append(node('p','词库未列出常规合成配方，不推断合成材料。'));}
body.append(node('p','沿用2026-10-16的18.4词库；技能数值为基础记录，随星级和属性变化。','source'));d.showModal();}));
d.querySelector('.close').addEventListener('click',()=>d.close());d.addEventListener('click',e=>{const r=d.getBoundingClientRect();if(e.target===d&&(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom))d.close()});d.addEventListener('close',()=>{if(opener)opener.focus({preventScroll:true})});})();
'''
def add_entity_details(html):
 cat=json.loads((P/'catalog.json').read_text())['data'];heroes={};traits={};equips={x['name']:x for x in cat['equip']};eqid={str(x['id']):x for x in cat['equip']}
 for t in cat['trait']:traits.setdefault(str(t['checkId']),t)
 for h in sorted(cat['hero'],key=lambda h:int(h['id'])):
  if h.get('heroType')==0 and h.get('isVisible') and h.get('price',0)>0:heroes.setdefault(h['name'],h)
 data={}
 def button(inner,key,name):return '<button type="button" class="entity-button'+(' equip-name' if key.startswith('equip:') else '')+'" data-entity="'+E(key,quote=True)+'" aria-haspopup="dialog" aria-controls="entity-dialog" aria-label="'+E(name+'：查看'+('技能和羁绊' if key.startswith('hero:') else '效果和合成配方'),quote=True)+'">'+inner+'</button>'
 def hero(m):
  inner,name=m.group(1),unescape(m.group(2));h=heroes[name];key='hero:'+name;ts=[]
  for tid in dict.fromkeys(re.split(r'[|,]',str(h.get('raceId',''))+'|'+str(h.get('jobId','')))):
   if tid not in traits:continue
   t=traits[tid];ts.append({'name':t['name'],'description':t.get('prefix') or t.get('descText') or '词库未列出效果','levels':(t.get('desc2Text') or '').replace('|','\n')})
  data[key]={'kind':'hero','name':name,'icon':h['picture'],'cost':h['price'],'skillName':h.get('skillName','技能'),'skill':re.sub(r'(?<!\d)0(?=\s*[（(])','〔动态值〕',h.get('skillDesc') or '词库未提供技能描述'),'skillValues':(h.get('skillValueDesc') or '').replace('|','\n'),'traits':ts,'dynamic':bool(re.search(r'(?<!\d)0(?!\d)',h.get('skillDesc',''))),'note':'此处列原生羁绊；裁决进化、转职等额外羁绊不自动计入。' if name=='卡兹克' else ''}
  return '<h3>'+button(inner,key,name)+' <span class="role">'
 html=re.sub(r'<h3>(<img class="hero-icon"[^>]*>([^<]+)) <span class="role">',hero,html)
 def equip(m):
  inner,name=m.group(1),unescape(m.group(2));e=equips[name];key='equip:'+name;recipe=[]
  for k in ['synthesis1','synthesis2']:
   q=eqid.get(str(e.get(k,'')))
   if q:recipe.append({'name':q['name'],'icon':q['picture'],'id':str(q['id'])})
  data[key]={'kind':'equip','name':name,'icon':e['picture'],'type':e.get('type','装备'),'stats':e.get('basicDesc',''),'effect':e.get('descText',''),'recipe':recipe}
  return button(inner,key,name)
 html=re.sub(r'<span class="equip-name">(<img class="equip-icon"[^>]*>([^<]+))</span>',equip,html)
 assert sum(x['kind']=='hero' for x in data.values())==37
 for x in data.values():
  if x['kind']=='hero':assert x['traits'],x['name']
 (P/'entity-details-audit.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 modal='<dialog id="entity-dialog" class="hex-dialog entity-dialog" aria-labelledby="entity-title"><header><img id="entity-icon" alt="" referrerpolicy="no-referrer"><h2 id="entity-title"></h2><button class="close" type="button" aria-label="关闭详情">×</button></header><div id="entity-body"></div></dialog>'
 html=html.replace('左右滑动标签切换阵容 · 点开查看备选与理由','左右滑动切阵容 · 点棋子、装备、海克斯看详情')
 return html.replace('</style>',CSS+'</style>',1).replace('</body>',modal+'<script type="application/json" id="entity-data">'+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+'</script><script>'+JS+'</script></body>')
