import json,re
from pathlib import Path
from html import escape as E,unescape
P=Path(__file__).resolve().parent
CSS='''
.hex-compact .hex-button{font:inherit;font-size:13px;line-height:20px;display:inline-flex;align-items:center;gap:3px;vertical-align:middle;border:0;border-radius:4px;background:#eef3f0;color:#263446;padding:3px 5px;margin:2px 2px 2px 0;cursor:pointer;text-align:left;max-width:100%}.hex-button img{width:16px;height:16px;object-fit:contain;flex:none}.hex-button:focus-visible{outline:2px solid #176d67;outline-offset:1px}.hex-button:hover{background:#dceae3}.hex-dialog{border:0;border-radius:12px;padding:18px;width:calc(100% - 28px);max-width:460px;max-height:80dvh;overflow:auto;background:#fff;color:#263446;box-shadow:0 14px 60px #0003}.hex-dialog::backdrop{background:#182d3c66}.hex-dialog header{display:flex;align-items:center;gap:8px;padding-right:38px;position:relative}.hex-dialog header img{width:28px;height:28px;object-fit:contain}.hex-dialog h2{font-size:19px;margin:0}.hex-dialog .close{position:absolute;right:-6px;top:-8px;min-width:44px;min-height:44px;border:0;border-radius:6px;background:#edf3ef;color:#176d67;font-size:23px;cursor:pointer}.hex-dialog h3{font-size:14px;margin:16px 0 5px;color:#176d67}.hex-dialog p{font-size:15px;line-height:1.7;margin:4px 0;white-space:pre-line}.hex-dialog .context{font-size:13px;color:#647168;margin-top:9px}.hex-dialog .source{font-size:12px;color:#647168;margin-top:14px}@media(max-width:650px){.hex-dialog{margin:auto auto max(12px,env(safe-area-inset-bottom));max-height:78dvh}}@media print{.hex-dialog{display:none}}
'''
JS='''
(()=>{const data=JSON.parse(document.getElementById('hex-data').textContent),d=document.getElementById('hex-dialog');let opener;
document.querySelectorAll('.hex-button').forEach(b=>b.addEventListener('click',()=>{const x=data[b.dataset.hex];opener=b;document.getElementById('hex-title').textContent=x.name;document.getElementById('hex-dialog-icon').src=x.icon;document.getElementById('hex-context').textContent=x.comp+' · '+x.group+' · '+x.grade;document.getElementById('hex-effect').textContent=x.effect;document.getElementById('hex-reason').textContent=x.reason;d.showModal();}));
d.querySelector('.close').addEventListener('click',()=>d.close());d.addEventListener('click',e=>{const r=d.getBoundingClientRect();if(e.target===d&&(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom))d.close()});d.addEventListener('close',()=>{if(opener)opener.focus({preventScroll:true})});})();
'''
def decorate_hex(html):
 cat=json.loads((P/'catalog.json').read_text())['data']['hex']
 # Audit is written after the page build; derive from the live source and same classifier.
 from hex_priority import classify
 byname={}
 for h in cat:byname.setdefault(h['name'],h)
 byid={str(h['id']):h for h in cat};rank=json.loads((P/'rank.json').read_text())['data'];names={r['compId']:r['name'] for r in rank}
 old=P.parents[2]/'games/jcc/set18/18.4/snapshots/20261016T053609Z/data/raw/comps';data={}
 def panel(m):
  cid,body=m.group(1),m.group(2);detail=json.loads((P/(cid+'.json')).read_text())['data'];rec=json.loads((old/cid/'recommended-hexes.json').read_text())['data']['hexes'];groups=classify(cid,rec,detail.get('conditions',[]));mapping={}
  for group,xs in groups.items():
   for x in xs:
    h=byid.get(str(x['id']))
    if not h or h['name']!=x['name']:h=byname[x['name']]
    h=dict(h)
    if x['name']=='太阳的抉择':h['icon']='https://static.datatft.com/images/hex2/DA_18_SolarTraitAugment_1_.png'
    key=cid+'-'+str(x['id']);effect=h.get('descText','').strip();assert effect and h.get('icon'),x['name']
    data[key]={'name':x['name'],'icon':h['icon'],'effect':effect,'comp':names[cid],'group':group,'grade':{1:'白银',2:'黄金',3:'棱彩'}.get(h.get('level'),'品质未标'),'reason':x['reason'] or '来源推荐候选；根据当前装备、经济和阵容缺口选择，不属于无条件必选。'};mapping[x['name']]=key
  def chip(mm):
   name=unescape(mm.group(1));key=mapping[name];x=data[key]
   return '<button type="button" class="hex-button" data-hex="'+key+'" aria-haspopup="dialog" aria-controls="hex-dialog" aria-label="'+E(name+'：查看效果和推荐理由',quote=True)+'"><img src="'+E(x['icon'],quote=True)+'" width="16" height="16" alt="" decoding="async" referrerpolicy="no-referrer"><span>'+mm.group(1)+'</span></button>'
  body=re.sub(r'<span class="hex">(.*?)</span>',chip,body)
  return m.group(0).replace(m.group(2),body,1)
 html=re.sub(r'<section class="comp" id="c(\d+)"[^>]*>(.*?)</section>',panel,html,flags=re.S)
 assert len(data)==140
 modal='<dialog class="hex-dialog" id="hex-dialog" aria-labelledby="hex-title"><header><img id="hex-dialog-icon" alt="" referrerpolicy="no-referrer"><h2 id="hex-title"></h2><button class="close" type="button" aria-label="关闭海克斯详情">×</button></header><p class="context" id="hex-context"></p><h3>效果</h3><p id="hex-effect"></p><h3>推荐理由与适用条件</h3><p id="hex-reason"></p><p class="source">效果沿用2026-10-16词库；优先级与理由为本攻略机制建议。</p></dialog>'
 html=html.replace('“必拿”仅指分支前提；优先拿需符合局面。','点海克斯看效果与理由；“必拿”仅指分支前提。')
 html=html.replace('</style>',CSS+'</style>',1)
 return html.replace('</body>',modal+'<script type="application/json" id="hex-data">'+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+'</script><script>'+JS+'</script></body>')
