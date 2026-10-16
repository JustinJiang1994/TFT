from pathlib import Path
from html import escape as E
import runpy,re,json
P=Path(__file__).resolve().parent
v=runpy.run_path(str(P/'build_logic_guide.py'))
full=v['OUT'].read_text(); routes=v['routes']; selected=v['selected']; audit=v['audit']; read=v['read']; eq=v['eq']; OLD=v['OLD']; BASE=v['BASE']; cores=v['cores']
OUT=v['OUT'].with_name('金铲铲18.4手机版速查.html')
from pivot_map import CSS as MAPCSS, SHORT

def names(xs):return '、'.join(SHORT.get(x,x) for x in xs) or '无'
def fold(title,body):return '<details><summary>'+E(title)+'</summary><div class="fold-body">'+body+'</div></details>'
def section(id,title):return '<section id="'+id+'"><h2>'+title+'</h2>'
CSS='''*{box-sizing:border-box}html{scroll-padding-top:70px}body{margin:0;background:#f6f4ef;color:#243247;font:16px/1.65 system-ui,-apple-system,"PingFang SC",sans-serif}main{max-width:900px;margin:auto;padding:18px 14px 64px}h1{font-size:25px;line-height:1.4;margin:10px 0}h2{font-size:22px;margin:26px 0 12px}h3{font-size:18px;margin:0 0 8px}a{color:#176d67}p{margin:8px 0}.meta{font-size:13px;color:#59665e}.sticky{position:sticky;top:0;z-index:5;background:#f6f4eff5;border-bottom:1px solid #d3ddd8;display:flex;justify-content:center;gap:4px;padding:5px 8px}.sticky a{font-size:14px;min-height:44px;display:flex;align-items:center;justify-content:center;flex:1;max-width:150px;text-decoration:none;font-weight:650}.jump{display:flex;gap:7px;flex-wrap:wrap}.jump a{min-height:44px;display:flex;align-items:center;padding:6px 12px;background:#e6efeb;border-radius:6px;text-decoration:none}.card{background:#fff;border:1px solid #d5dedb;border-radius:8px;padding:14px;margin:12px 0;min-width:0}.gate{font-size:14px;color:#805009;border-left:3px solid #b58a40;padding-left:9px}.key{color:#176d67;font-weight:600}.small{font-size:14px}.item{padding:8px 0;border-bottom:1px solid #e2e7e4}.item:last-child{border:0}.item b{display:block}details{border-top:1px solid #dce4df;margin-top:10px}summary{cursor:pointer;min-height:44px;padding:10px 2px;color:#176d67;font-size:15px;font-weight:600}.fold-body{padding:0 0 10px}.fold-body p{font-size:15px}.badge{display:inline-block;background:#edf2ef;padding:4px 8px;border-radius:5px;margin:3px 4px 3px 0;font-size:14px}.swap{font-size:14px;line-height:1.9}.tags{font-size:14px;color:#176d67}.level-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.level-grid>.card{margin:0}.back{display:block;padding:10px 0;min-height:44px;text-align:right}.note{font-size:14px;padding:10px;background:#eee8d9}.table-wrap{overflow:auto}table{border-collapse:collapse;font-size:14px}td,th{padding:8px;border-bottom:1px solid #ddd;vertical-align:top;text-align:left}img{max-width:100%}@media(max-width:650px){.level-grid{grid-template-columns:1fr}}@media print{.sticky,.jump,.back{display:none}details .fold-body{display:block}main{max-width:none}}
'''
parts=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>金铲铲18.4｜手机速查</title><style>'+CSS+MAPCSS+'''#pivot-map h2{font-size:22px}.pm-grid{grid-template-columns:1fr}.pm-detail{font-size:15px}.pm-edge .pm-link{display:none}.pm-edge details{margin-top:8px}.pm-group>p{font-size:14px}.pm-group h3{font-size:18px}.pm-gate{font-size:14px}.pm-summary{font-size:14px}.pm-jumps{display:grid;grid-template-columns:1fr 1fr}.pm-line{grid-template-columns:minmax(0,1fr) 32px minmax(0,1fr)}.pm-detail details .pm-row{font-size:15px}
</style></head><body><nav class="sticky" aria-label="速查目录"><a href="#pivot-map">互转</a><a href="#levels">补牌</a><a href="#builds">装备</a><a href="#hexes">海克斯</a><a href="#wisps">仙灵</a></nav><main><header id="top"><p class="meta">金铲铲国服 · 18.4 · 2026-10-16资料</p><h1>手机版速查</h1><p class="small">来牌看互转，升级看补牌；点击展开换牌理由。</p><a href="金铲铲18.4版本攻略.html">打开完整版攻略 ↗</a><p class="meta">沿用同版资料；理论过渡与互转不代表实测胜率。高费牌没到，不先拆旧盘。</p></header>''']
# Reuse all 23 arrow labels, exact roster changes, and hard prerequisites.
maphtml=re.search(r'<section id="pivot-map".*?</section>',full,re.S).group()
def compact(m):
 body=m.group(1)
 trigger=re.search(r'<p class="pm-trigger">.*?</p>',body,re.S).group()
 keep=re.search(r'<p class="pm-row pm-keep">.*?</p>',body,re.S).group()
 gate=re.search(r'<p class="pm-gate">.*?</p>',body,re.S).group()
 other=body.replace(trigger,'').replace(keep,'').replace(gate,'')
 return '<div class="pm-detail">'+trigger+keep+gate+fold('换下谁／补进谁',other)+'</div>'
maphtml=re.sub(r'<div class="pm-detail">(.*?)</div>',compact,maphtml,flags=re.S)
# Put the corresponding full reasoning directly under each arrow; no second long list.
for e in audit['pivots']:
 i=e['id'];card=re.search(r'<article class="card" id="pivot'+str(i)+r'">(.*?)</article>',full,re.S).group(1)
 card=re.sub(r'^<h3>.*?</h3>','',card,flags=re.S)
 link=re.search(r'<a class="pm-link" href="#pivot'+str(i)+r'">.*?</a>',maphtml,re.S).group()
 maphtml=maphtml.replace(link,'<details id="pivot'+str(i)+'"><summary>装备交接／操作顺序／不转条件</summary><div class="fold-body">'+card+'</div></details>')
parts.append(maphtml)
parts.append(section('levels','各等级｜关键补牌')+'<div class="jump">'+''.join(f'<a href="#lv{x}">{x}级</a>' for x in range(3,10))+'</div><p class="meta">“补进／换下”相对于本路线上一等级示例；跨阵容请看互转。首次展示给起手底盘，不代表强搜高费。</p></section>')
for lv in range(3,10):
 parts.append(section('lv'+str(lv),str(lv)+'级补牌')+'<p class="small">'+v['levelintro'][lv]+'</p><div class="level-grid">')
 for r in selected:
  cid=r['compId'];st=routes[cid].get(lv)
  if not st:continue
  prev=routes[cid].get(lv-1);on=[n for n in st['board'] if not prev or n not in prev['board']];off=[n for n in prev['board'] if n not in st['board']] if prev else []
  parts.append(f'<article class="card" id="r{cid}l{lv}"><h3><a href="#comp{cid}">{E(r["name"])}</a></h3><p class="key">'+('补进：' if prev else '起手底盘：')+E(names(on))+'</p>'+('<p class="small">换下：'+E(names(off))+'</p>' if off else ''))
  if st['emblems']:parts.append('<p class="gate">必须：'+E('；'.join(names([n])+'携'+t+'纹章' for n,t in st['emblems'].items()))+('；莉莉娅持有为推导' if cid=='105' else '')+'</p>')
  if st['evolve']:parts.append('<p class="gate">必须：螳螂已进化裁决</p>')
  parts.append(fold('为什么这样补／完整棋盘', '<p>'+E(st['why'])+'</p><p><b>完整棋盘：</b>'+E(names(st['board']))+'</p><p class="tags">'+E(v['activefmt'](st['active']))+'</p><div class="swap">'+v['delta'](prev,st)+'</div>')+'</article>')
 parts.append('</div><a class="back" href="#levels">↑ 选其他等级</a></section>')
parts.append(section('builds','核心装备｜按阵容直达')+'<div class="jump">'+''.join(f'<a href="#comp{r["compId"]}">{E(r["name"])}</a>' for r in selected)+'</div><p class="meta">来源示例配装；先主C、主坦，再给副C。更换携带者需要实际卖牌或拆卸条件。</p></section>')
for r in selected:
 cid=r['compId'];d=read(P/(cid+'.json'))['data'];anchor,logic,flex,shared=cores[cid]
 parts.append(f'<article class="card" id="comp{cid}"><h3>{E(r["name"])} · {r["tier"]}</h3><p class="gate">'+E(v['condition'](cid))+'</p><p class="small"><b>核心：</b>'+E(anchor)+'</p>')
 for h in d['heroes']:
  items=[eq[str(x['equipId'])]['name'] for x in d.get('equips',[]) if str(x['heroId'])==str(h['heroId'])]
  if items:parts.append('<div class="item"><b>'+E(h['heroName'])+' <span class="meta">'+E(str(h.get('heroStarNum') or '未标'))+'星（来源目标）</span></b><span class="small">'+E(' ＋ '.join(items))+'</span></div>')
 if cid=='105':parts.append('<p class="gate">若按本文方案给莉莉娅森转，必须替掉一件普通装备；不能同时拿三件坦装再加纹章。来源未指定森转持有者。</p>')
 parts.append(f'<p><a href="#hex{cid}">查本阵海克斯 →</a></p><div class="jump">'+''.join(f'<a href="#r{cid}l{x}">{x}级补牌</a>' for x in routes[cid])+'</div>')
 parts.append(fold('阵容理由／可替换位置／来源样本','<p>'+E(logic)+'</p><p>'+E(flex)+'</p><p>'+E(shared)+'</p><p class="meta">来源样本'+str(r['sampleCount'])+'；评级不代表理论过渡强度。</p>')+'</article>')
parts.append(section('hexes','海克斯｜先看用途，再查阵容')+'<div class="jump">'+''.join(f'<a href="#hex{r["compId"]}">{E(r["name"])}</a>' for r in selected)+'</div>')
parts.append('<p class="small">缺即战力选能立即补输出、前排或装备的强化；追三星看搜牌资源；上8/9看升级经济。宝宝学院等专属条件会限制后续互转。</p>')
for r in selected:
 cid=r['compId'];recs=read(OLD/f'comps/{cid}/recommended-hexes.json')['data'].get('hexes',[])
 parts.append(f'<article class="card" id="hex{cid}"><h3>{E(r["name"])}</h3><p class="gate">'+E(v['condition'](cid))+'</p>'+''.join('<span class="badge">'+E(x['name'])+'</span>' for x in recs)+f'<p class="small"><a href="#comp{cid}">核心装备 ↗</a></p></article>')
# Functional shortlist with original quality and round data, not an invented ranking.
func=[]
for x in v['hstats']:
 if x['name'] in v['focus']:
  grade={1:'白银',2:'黄金',3:'棱彩'}.get(v['hx'].get(str(x['hexId']),{}).get('level'),'待核')
  func.append('<div class="item"><b>'+E(x['name'])+' · '+grade+'</b><span class="meta">'+E(' / '.join(x['rounds']))+'</span><p class="small">'+E(v['focus'][x['name']])+'</p></div>')
parts.append(fold('通用强化：品质／出现回合／适用理由',''.join(func))+'<p class="meta">逐阵推荐保留来源全部返回项；推荐频次不是因果强度排名。</p></section>')
parts.append(section('wisps','仙灵法杖｜按阶段与缺口')+'<p class="gate">仙灵池看阶段与回合，不看人口。先检查缺口，避免重复购买已有破抗、重伤功能。</p>')
groups=[('2阶段｜稳开局',['休战','找个朋友','树皮护甲','有丝分裂']),('3阶段｜补战力',['星落','巨大化','石化术','蜂鸟']),('3-5起｜补功能或找四费',['衣衫褴褛','日炎巫术','搜查队']),('4-2起｜战力与运营',['顺流而下','余震','约德尔之灵','活体商店']),('5阶段｜终盘对位',['地动山摇','折磨','幻影纹章']),('后期与特殊条件｜以条目窗口为准',['英雄登场','自然之怒','法力细雨','树丛铠甲','回归的好友'])]
for title,ns in groups:
 parts.append('<h3>'+title+'</h3>')
 for n in ns:
  w=v['wmap'][n]
  parts.append('<article class="card"><h3>'+E(n)+'</h3><p class="meta">词库回合：'+E(' / '.join(w.get('rounds',[])))+'</p><p class="small">'+E(w['effect'])+'</p>')
  if w.get('requires'):parts.append('<p class="gate">'+E('；'.join(w['requires']))+'</p>')
  parts.append('</article>')
parts.append(fold('阶段选择理由／资料冲突',''.join('<p><b>'+str(lv)+'级附近：</b>'+E(v['levelspells'][lv])+'</p>' for lv in [3,6,7,9])+'<p>新增免费仙灵起始回合：公告转载4-1，词库4-2且金币少于10；保留冲突，不为刷取故意花空经济。无逐阶段胜率，推荐为机制判断。</p>')+'</section>')
parts.append('<footer>'+fold('资料范围与完整版','<p>金铲铲18.4，2026-10-16同版资料；14套S/A、23条互转、83个分级棋盘、23个仙灵候选。转职条件与理论推导沿用完整版。</p><a href="金铲铲18.4版本攻略.html">查看完整证据与机制分析</a>')+'<a class="back" href="#top">↑ 回到顶部</a></footer></main><script>function reveal(){const id=decodeURIComponent(location.hash.slice(1));if(!id)return;const el=document.getElementById(id);if(!el)return;for(let p=el;p;p=p.parentElement)if(p.tagName==="DETAILS")p.open=true;requestAnimationFrame(()=>el.scrollIntoView({block:"start"}));}addEventListener("hashchange",reveal);addEventListener("DOMContentLoaded",reveal);</script></body></html>')
OUT.write_text(''.join(parts));print('Mobile:',OUT,OUT.stat().st_size)
