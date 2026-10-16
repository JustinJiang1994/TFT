import re
from html import escape as E
CSS='''
[hidden]{display:none!important}main{max-width:920px;padding:16px 12px 40px}header h1{font-size:23px;margin:2px 0 4px}header .meta{margin:0}.tab-hint{font-size:12px;color:#617167;margin:6px 0}.tab-list{display:grid;grid-template-rows:repeat(2,44px);grid-auto-flow:column;grid-auto-columns:minmax(120px,1fr);gap:6px;overflow-x:auto;padding:4px 0 9px;scrollbar-width:thin;overscroll-behavior-x:contain}.tab-list button{font:inherit;font-size:14px;white-space:nowrap;border:1px solid #c8d8d0;border-radius:6px;padding:8px 10px;background:#edf2ef;color:#285e51;cursor:pointer}.tab-list button[aria-selected="true"]{color:white;background:#176d67;border-color:#176d67;font-weight:650}.tab-list button:focus-visible{outline:3px solid #af8436;outline-offset:2px}.comp{margin:12px 0;padding:14px}.comp h2{font-size:21px}.comp>.gate{font-size:13px;margin:4px 0 8px}.core-line{display:none}.hex-compact{display:grid;grid-template-columns:48px minmax(0,1fr);gap:5px;padding:6px 0;border-bottom:1px solid #e5eae7;font-size:13px}.hex-compact>b{padding-top:3px;white-space:nowrap}.hex-compact .hex{font-size:13px;padding:2px 5px;margin:2px 2px 2px 0}.hex-note{font-size:12px;color:#647168;margin:5px 0}.heroes{gap:10px;margin-top:6px}.hero{padding:8px 0;border-top:1px solid #d9e2dd}.hero h3{font-size:16px;margin:0 0 3px}.role{font-size:12px}.first-set{font-size:14px;line-height:1.65}.first-set .tag{font-size:11px;margin-right:5px;background:#e5eeea;color:#176d67;padding:1px 4px;border-radius:3px}.equip-name{display:inline-block;white-space:nowrap}.hero details{margin-top:2px}.hero summary{font-size:12px;min-height:36px;padding:8px 0}.comp>details{margin-top:4px}.comp>details>summary{font-size:13px;padding:9px 0;min-height:38px}.hero>.meta{font-size:13px;margin:3px 0}.combo{margin:6px 0}.reason-group{margin:10px 0}.reason-group p{font-size:13px;margin:5px 0}.data-note{font-size:12px;color:#647168}@media(max-width:650px){.heroes{grid-template-columns:1fr;gap:0}.tab-list{grid-auto-columns:118px}.comp{padding:12px}.first-set{font-size:14px}}@media print{.tab-list,.tab-hint{display:none}.comp[hidden]{display:block!important}.comp{break-before:page}}
'''
JS='''
(()=>{const tabs=[...document.querySelectorAll('[role="tab"]')],panels=[...document.querySelectorAll('[role="tabpanel"]')];
function show(id,focus=false,update=true){let t=tabs.find(x=>x.dataset.target===id)||tabs[0];tabs.forEach(x=>{const on=x===t;x.setAttribute('aria-selected',String(on));x.tabIndex=on?0:-1});panels.forEach(p=>p.hidden=p.id!==t.dataset.target);if(focus)t.focus();const list=t.parentElement;list.scrollTo({left:Math.max(0,t.offsetLeft-list.offsetLeft-(list.clientWidth-t.offsetWidth)/2),behavior:'auto'});if(update)history.replaceState(null,'','#'+t.dataset.target);}
tabs.forEach((t,i)=>{t.addEventListener('click',()=>show(t.dataset.target));t.addEventListener('keydown',e=>{let n;if(e.key==='ArrowRight'||e.key==='ArrowDown')n=(i+1)%tabs.length;else if(e.key==='ArrowLeft'||e.key==='ArrowUp')n=(i+tabs.length-1)%tabs.length;else if(e.key==='Home')n=0;else if(e.key==='End')n=tabs.length-1;else return;e.preventDefault();show(tabs[n].dataset.target,true)});});addEventListener('hashchange',()=>show(location.hash.slice(1),false,false));show(location.hash.slice(1),false,false);})();
'''
def compact(html,rows):
 intro=''.join(re.findall(r'<p class="intro">.*?</p>',html,re.S))
 header='<header><p class="meta">金铲铲18.4 · 2026-10-16</p><h1>阵容核心速查</h1><p class="tab-hint">左右滑动标签切换阵容 · 点开查看备选与理由</p><div class="tab-list" role="tablist" aria-label="选择阵容">'+''.join(f'<button type="button" role="tab" id="tab{r["compId"]}" aria-controls="c{r["compId"]}" aria-selected="false" tabindex="-1" data-target="c{r["compId"]}">{r["tier"]} · {E(r["name"])}</button>' for r in rows)+'</div></header>'
 html=re.sub(r'<header>.*?</header>',lambda m:header,html,count=1,flags=re.S)
 def comp(m):
  cid,body=m.group(1),m.group(2)
  body=re.sub(r'<p><b>最终成型核心：</b>.*?</p>','',body,flags=re.S)
  groups=re.findall(r'<div class="hex-group">(.*?)</div>(?=<div class="hex-group">|<p class="gate">|<div class="heroes">)',body,re.S)
  # Match full region, then each group bounded by the next group rather than its nested entries.
  start=body.index('<p><b>推荐海克斯：</b></p>');end=body.index('<div class="heroes">')
  region=body[start:end];chunks=re.split(r'<div class="hex-group">',region)[1:]
  compact_groups=[];reason_groups=[]
  for chunk in chunks:
   label=re.search(r'<b>(.*?)</b>',chunk).group(1)
   names=re.findall(r'<span class="hex">(.*?)</span>',chunk)
   compact_groups.append('<div class="hex-compact"><b>'+label+'</b><div>'+(''.join('<span class="hex">'+n+'</span>' for n in names) or '<span class="meta">无指定必拿</span>')+'</div></div>')
   entries=re.findall(r'<span class="hex">(.*?)</span><span class="meta">(.*?)</span>',chunk,re.S)
   reason_groups.append('<div class="reason-group"><b>'+label+'</b>'+''.join('<p><b>'+n+'：</b>'+reason+'</p>' for n,reason in entries)+'</div>')
  caution='<p class="data-note">此分支海克斯最高仅13次选取，分档仅为机制建议。</p>' if cid=='114' else ''
  body=body[:start]+''.join(compact_groups)+'<p class="hex-note">“必拿”仅指分支前提；优先拿需符合局面。</p>'+body[end:]
  def hero(mm):
   content=mm.group(1);allcombos=re.findall(r'<div class="combo">.*?</span></div>',content,re.S)
   if not allcombos:return mm.group(0)
   heading=content[:content.index('<div class="combo">')]
   first=allcombos[0];items=re.search(r'<div class="items">(.*?)</div>',first,re.S).group(1)
   provisional='暂选' if '暂选首套' in first else '首选'
   names=items.split(' ＋ ');items=' ＋ '.join('<span class="equip-name">'+x+'</span>' for x in names)
   gates=''.join(re.findall(r'<p class="gate">.*?</p>',first,re.S))
   return '<article class="hero">'+heading+'<div class="first-set"><span class="tag">'+provisional+'</span>'+items+'</div>'+gates+'<details><summary>备选组合 · 样本与排序依据</summary>'+''.join(allcombos)+'</details></article>'
  body=re.sub(r'<article class="hero">(.*?)</article>',hero,body,flags=re.S)
  body=body.replace('</div><details><summary>评级与配装口径', '</div><details class="hex-reasons"><summary>海克斯推荐理由</summary>'+''.join(reason_groups)+caution+'</details><details><summary>评级与配装口径',1)
  return '<section class="comp" id="c'+cid+'" role="tabpanel" aria-labelledby="tab'+cid+'">'+body+'</section>'
 html=re.sub(r'<section class="comp" id="c(\d+)">(.*?)</section>',comp,html,flags=re.S)
 html=html.replace('</style>',CSS+'</style>',1)
 html=html.replace('<footer class="foot">','<details><summary>配装排序规则</summary>'+intro+'</details><footer class="foot">',1)
 return html.replace('</body>','<script>'+JS+'</script></body>')
