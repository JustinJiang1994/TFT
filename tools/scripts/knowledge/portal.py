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
 ref=('<p>已保存 TFT S'+str(t['set'])+' / '+e(t['patch'])+' · '+str(t['comps'])+'套历史攻略。快照 '+e(t['snapshot'])+'。</p><a class="button" href="games/tft/current.html">TFT 历史手册 ↗</a> <a href="games/tft/assistant.html">历史对局助手</a> · <a href="games/tft/index.html">历史版本</a>') if t else '<p>暂无已保存的 TFT 数据。</p>'
 if (ROOT/'games/tft/reference/2026-10-15/index.html').exists():
  ref += '<p><a href="games/tft/reference/2026-10-15/index.html">查看TFT 18.4b完整22套S/A与两端对照 ↗</a><br><small>2026-10-15快照已核实补丁与名单 · 未确认跨平台适配</small></p>'
 return '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>阵容罗盘 · 金铲铲 / TFT</title><style>
 *{box-sizing:border-box}body{margin:0;background:#f4f5f1;color:#20383d;font:16px/1.75 system-ui,-apple-system,sans-serif}a{color:#216f78;text-decoration:none}a:hover{text-decoration:underline}a:focus-visible{outline:3px solid #c28d35;outline-offset:4px}main{max-width:1160px;margin:auto;padding:24px}nav{display:flex;gap:22px;align-items:center;flex-wrap:wrap;margin-bottom:28px}nav strong{margin-right:auto;font-size:20px}.hero{background:#193e46;color:#fff;border-radius:24px;padding:42px}.eyebrow{letter-spacing:.12em;font-size:13px;color:#b9d9d8}h1{font-size:clamp(30px,5vw,48px);line-height:1.25;margin:18px 0}h2{font-size:25px;margin:0}h3{margin:0;font-size:19px}.hero p{color:#d1e4e4;max-width:720px}.actions{display:flex;gap:14px;flex-wrap:wrap;margin-top:26px}.button{display:inline-block;border-radius:10px;padding:12px 20px;background:#216c65;color:white;font-weight:650}.hero .button{background:#e5b85b;color:#18383d}.button.secondary{background:#e8f1ee;color:#216559}.hero .secondary{background:#2e5259;color:white;border:1px solid #638086}.meta{display:flex;gap:20px;flex-wrap:wrap;font-size:14px;margin-top:24px;color:#c7dddd}.section{margin-top:36px}.intro{color:#647b7e;margin:8px 0 20px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.card,.route{background:white;border:1px solid #dbe4e1;border-radius:16px;padding:24px}.card .step{color:#497e77;font-weight:700;font-size:13px}.card h3{margin:9px 0}.card p{color:#63797c}.route p{color:#7b8987;font-size:14px;margin:4px 0 15px}.links{display:grid;gap:10px}.links a{display:flex;align-items:center;gap:8px}.tier{font-size:12px;border-radius:5px;color:white;padding:1px 7px;flex:none}.tier.S{background:#b35b24}.tier.A{background:#277481}.reference{display:grid;grid-template-columns:1fr 1fr;gap:24px;background:#eceff4;border:1px solid #d7dfe7;border-radius:18px;padding:28px}.reference p{color:#5f707c}.reference .tag{display:inline-block;background:#e0deed;color:#62557c;padding:3px 10px;border-radius:7px;font-size:13px}.rules{background:white;border-radius:12px;padding:20px}.rules p{margin:8px 0}.footer{color:#748589;font-size:13px;margin:28px 0}.snapshot{background:#e9eeeb;border-radius:12px;padding:15px 20px;margin-top:18px;color:#5d7775}@media(max-width:760px){main{padding:16px}.hero{padding:26px}.grid,.reference{grid-template-columns:1fr}.meta{gap:8px 16px}nav{gap:14px}.card,.route{padding:20px}}
 </style></head><body><main><nav><strong>阵容罗盘</strong><a href="#play">开始对局</a><a href="#routes">阵容路线</a><a href="#reference">游戏与版本</a><a href="games/jcc/index.html">版本记录</a></nav>
 <header class="hero"><div class="eyebrow">金铲铲之战 / TFT · 双游戏阵容库</div><h1>用手里的牌，找到下一步。</h1><p>两个游戏并列查看，按游戏、赛季、版本与快照日期识别阵容、装备和运营数据。</p><p><a class="button" href="games/assistant/index.html">选海克斯，找最终阵容 →</a></p></header>
 <section id="reference" class="section reference"><div><span class="tag">金铲铲之战</span><h2>S'''+str(j['set'])+''' / '''+e(j['patch'])+'''</h2><p>'''+str(j['comps'])+''' 套 S/A · 已发布快照 '''+e(k.get('release',{}).get('fetched_at','')[:10])+'''</p><p><a class="button" href="'''+assistant+'''">金铲铲对局助手 →</a></p><p><a href="'''+guide+'''">版本手册</a> · <a href="games/jcc/index.html">历史版本</a></p></div><div><span class="tag">TFT · 云顶之弈</span><h2>阵容与版本数据</h2>'''+ref+'''</div></section>
 <section id="play" class="section"><h2>双游戏 · 对局工具</h2><p><a class="button" href="games/assistant/index.html">统一对局助手 · 海克斯推荐与最终阵容 →</a></p><p class="intro">对局时用助手，准备开局时读攻略。</p><div class="grid"><article class="card"><span class="step">01 · 先看环境</span><h3>这个版本怎么玩？</h3><p>查看阵容分布、运营路线，以及相比上一版的变化。</p><a href="'''+guide+'''#overview">查看版本定调 →</a></article><article class="card"><span class="step">02 · 找到下一步</span><h3>我现在可以补什么？</h3><p>已有棋子多选，分别查看当前过渡与目标等级组合，比较前四率和均名。</p><a href="games/assistant/index.html">打开统一对局助手 →</a></article><article class="card"><span class="step">03 · 准备成型</span><h3>装备、海克斯怎么选？</h3><p>按阵容查看主C、主坦出装、已有装备补全，以及银金彩推荐海克斯。</p><a href="'''+guide+'''#compositions">查看阵容详细攻略 →</a></article></div></section>
 <section id="routes" class="section"><h2>金铲铲 · 按运营路线找阵容</h2><p class="intro">追三星等级与成型后升人口分开看；查看9级棋盘不等于要速9。</p><div class="grid">'''+route_cards+'''</div></section>

 <div class="snapshot">这里展示的是已保存的数据快照，不是实时榜单。两个游戏并列收录；统计保留各自的游戏、版本与来源口径，已核实的机制差异在对照页展示。</div><footer class="footer">金铲铲来源：金铲铲大数据（非官方） · TFT 来源：MetaTFT。具体统计范围与缺失项见各版本手册。</footer></main></body></html>'''

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
