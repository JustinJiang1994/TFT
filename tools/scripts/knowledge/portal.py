"""Platform-first entrypoints and stable compatibility redirects."""
from pathlib import Path
import html,json,os
ROOT=Path(__file__).resolve().parents[3]
def redirect(path,target):
 path.parent.mkdir(parents=True,exist_ok=True)
 # Preserve fragment for old composition bookmarks. Query is not used by the guide.
 path.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>阵容罗盘 · 跳转</title><p><a href="'+html.escape(target)+'">打开对应平台与版本</a></p><script>location.replace('+json.dumps(target)+'+location.hash);</script></html>')
def page(title,body):
 return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><body style="font:17px/1.8 system-ui;color:#183b43;background:#f5f7f7;max-width:960px;margin:40px auto;padding:24px"><h1>'+title+'</h1>'+body+'</body></html>'
def home(active_by_platform):
 j=active_by_platform.get('jcc');t=active_by_platform.get('tft')
 if not j:return page('阵容罗盘','<p>尚未发布金铲铲版本。</p>')
 data=ROOT/Path(j['path']).parent.parent/'data'/'knowledge.json'
 k=json.loads(data.read_text()) if data.exists() else {'comps':[]}
 comps=k['comps'];guide=html.escape(j['path']);assistant=html.escape(j.get('assistant',str(Path(j['path']).with_name('assistant.html'))))
 e=html.escape
 routes={}
 for c in comps:routes.setdefault(c['route'],[]).append(c)
 route_cards=''.join('<article class="route"><h3>'+e(route)+'</h3><p>'+str(len(cs))+' 套候选</p><div class="links">'+''.join('<a href="'+guide+'#comp-'+str(c['id'])+'"><span class="tier '+e(c['tier'])+'">'+e(c['tier'])+'</span>'+e(c['name'])+'</a>' for c in cs)+'</div></article>' for route,cs in routes.items())
 ref=('<p>已保存 TFT S'+str(t['set'])+' / '+e(t['patch'])+' · '+str(t['comps'])+'套历史攻略。与金铲铲当前收录补丁不同，尚未逐项核对可迁移性。</p><a class="button secondary" href="games/tft/current.html">浏览 TFT 参考手册 ↗</a> <a href="games/tft/index.html">历史版本</a>') if t else '<p>暂无已保存的 TFT 参考资料。</p>'
 return '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>阵容罗盘 · 金铲铲对局指南</title><style>
 *{box-sizing:border-box}body{margin:0;background:#f4f5f1;color:#20383d;font:16px/1.75 system-ui,-apple-system,sans-serif}a{color:#216f78;text-decoration:none}a:hover{text-decoration:underline}a:focus-visible{outline:3px solid #c28d35;outline-offset:4px}main{max-width:1160px;margin:auto;padding:24px}nav{display:flex;gap:22px;align-items:center;flex-wrap:wrap;margin-bottom:28px}nav strong{margin-right:auto;font-size:20px}.hero{background:#193e46;color:#fff;border-radius:24px;padding:42px}.eyebrow{letter-spacing:.12em;font-size:13px;color:#b9d9d8}h1{font-size:clamp(30px,5vw,48px);line-height:1.25;margin:18px 0}h2{font-size:25px;margin:0}h3{margin:0;font-size:19px}.hero p{color:#d1e4e4;max-width:720px}.actions{display:flex;gap:14px;flex-wrap:wrap;margin-top:26px}.button{display:inline-block;border-radius:10px;padding:12px 20px;background:#216c65;color:white;font-weight:650}.hero .button{background:#e5b85b;color:#18383d}.button.secondary{background:#e8f1ee;color:#216559}.hero .secondary{background:#2e5259;color:white;border:1px solid #638086}.meta{display:flex;gap:20px;flex-wrap:wrap;font-size:14px;margin-top:24px;color:#c7dddd}.section{margin-top:36px}.intro{color:#647b7e;margin:8px 0 20px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.card,.route{background:white;border:1px solid #dbe4e1;border-radius:16px;padding:24px}.card .step{color:#497e77;font-weight:700;font-size:13px}.card h3{margin:9px 0}.card p{color:#63797c}.route p{color:#7b8987;font-size:14px;margin:4px 0 15px}.links{display:grid;gap:10px}.links a{display:flex;align-items:center;gap:8px}.tier{font-size:12px;border-radius:5px;color:white;padding:1px 7px;flex:none}.tier.S{background:#b35b24}.tier.A{background:#277481}.reference{display:grid;grid-template-columns:1fr 1.3fr;gap:24px;background:#eceff4;border:1px solid #d7dfe7;border-radius:18px;padding:28px}.reference p{color:#5f707c}.reference .tag{display:inline-block;background:#e0deed;color:#62557c;padding:3px 10px;border-radius:7px;font-size:13px}.rules{background:white;border-radius:12px;padding:20px}.rules p{margin:8px 0}.footer{color:#748589;font-size:13px;margin:28px 0}.snapshot{background:#e9eeeb;border-radius:12px;padding:15px 20px;margin-top:18px;color:#5d7775}@media(max-width:760px){main{padding:16px}.hero{padding:26px}.grid,.reference{grid-template-columns:1fr}.meta{gap:8px 16px}nav{gap:14px}.card,.route{padding:20px}}
 </style></head><body><main><nav><strong>阵容罗盘</strong><a href="#play">开始对局</a><a href="#routes">阵容路线</a><a href="#reference">TFT 参考</a><a href="games/jcc/index.html">版本记录</a></nav>
 <header class="hero"><div class="eyebrow">金铲铲之战 · 对局指南</div><h1>用手里的牌，找到下一步。</h1><p>先选等级、棋子、海克斯与转职，看当前怎么过渡，再看升级后补什么。阵容强度与统计以金铲铲数据为准。</p><div class="actions"><a class="button" href="'''+assistant+'''">进入金铲铲对局助手 →</a><a class="button secondary" href="'''+guide+'''">阅读本版攻略</a></div><div class="meta"><span>已收录 S'''+str(j['set'])+' / '+e(j['patch'])+'''</span><span>'''+str(j['comps'])+''' 套 S/A 阵容</span><span>快照 '''+e(k.get('release',{}).get('fetched_at','')[:10])+'''</span></div></header>
 <section id="play" class="section"><h2>按你现在的问题查</h2><p class="intro">对局时用助手，准备开局时读攻略。</p><div class="grid"><article class="card"><span class="step">01 · 先看环境</span><h3>这个版本怎么玩？</h3><p>查看阵容分布、运营路线，以及相比上一版的变化。</p><a href="'''+guide+'''#overview">查看版本定调 →</a></article><article class="card"><span class="step">02 · 找到下一步</span><h3>我现在可以补什么？</h3><p>已有棋子多选，分别查看当前过渡与目标等级组合，比较前四率和均名。</p><a href="'''+assistant+'''">打开对局助手 →</a></article><article class="card"><span class="step">03 · 准备成型</span><h3>装备、海克斯怎么选？</h3><p>按阵容查看主C、主坦出装、已有装备补全，以及银金彩推荐海克斯。</p><a href="'''+guide+'''#compositions">查看阵容详细攻略 →</a></article></div></section>
 <section id="routes" class="section"><h2>按运营路线找阵容</h2><p class="intro">追三星等级与成型后升人口分开看；查看9级棋盘不等于要速9。</p><div class="grid">'''+route_cards+'''</div></section>
 <section id="reference" class="section reference"><div><span class="tag">补充资料 · TFT 参考</span><h2>缺少资料时，再看另一种思路。</h2>'''+ref+'''</div><div class="rules"><p><strong>金铲铲主数据</strong><br>阵容评级、均名、前四率、推荐装备与海克斯均使用金铲铲来源。</p><p><strong>TFT 补充参考</strong><br>用于了解阵容思路、替代搭配与运营。迁移前核对同赛季棋子、羁绊与装备机制，参考内容单独标注。</p><p><strong>有冲突，优先金铲铲</strong><br>不把 TFT 统计合并进金铲铲排名，也不将 TFT 的 S 级装备标成金铲铲 S 级。</p></div></section>
 <div class="snapshot">这里展示的是已保存的数据快照，不是实时榜单。更新以金铲铲为主；需要补充时定向查询 TFT。</div><footer class="footer">金铲铲来源：金铲铲大数据（非官方） · TFT 历史来源：MetaTFT。具体统计范围与缺失项见各版本手册。</footer></main></body></html>'''

def publish_portals():
 active_by_platform={}
 for platform,label in [('jcc','金铲铲之战'),('tft','TFT · 云顶之弈')]:
  folder=ROOT/'games'/platform;cp=folder/'releases.json'
  if not cp.exists():continue
  c=json.loads(cp.read_text());rows=[];active=next(x for x in c['releases'] if x['id']==c['active']);active_by_platform[platform]=active
  for x in reversed(c['releases']):
   rel=os.path.relpath(ROOT/x['path'],folder);a=x.get('assistant',str(Path(x['path']).with_name('assistant.html')))
   rows.append('<li><strong>S'+str(x['set'])+' / '+html.escape(x['patch'])+'</strong> · '+str(x['comps'])+'套 · '+html.escape(x['snapshot'])+('（当前入口）' if x['id']==c['active'] else '')+'<br><a href="'+rel+'">版本手册</a> · <a href="'+os.path.relpath(ROOT/a,folder)+'">对局助手</a></li>')
  (folder/'index.html').write_text(page(label+' · 版本目录','<p><a href="../../index.html">返回首页</a></p><ul>'+''.join(rows)+'</ul>'))
  redirect(folder/'current.html',os.path.relpath(ROOT/active['path'],folder));redirect(folder/'assistant.html',os.path.relpath(ROOT/active.get('assistant',str(Path(active['path']).with_name('assistant.html'))),folder))
 (ROOT/'index.html').write_text(home(active_by_platform))
if __name__=='__main__':publish_portals()
