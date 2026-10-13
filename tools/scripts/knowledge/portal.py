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
def publish_portals():
 sections=[]
 for platform,label in [('jcc','金铲铲之战'),('tft','TFT · 云顶之弈')]:
  folder=ROOT/'games'/platform;cp=folder/'releases.json'
  if not cp.exists():continue
  c=json.loads(cp.read_text());rows=[];active=next(x for x in c['releases'] if x['id']==c['active'])
  for x in reversed(c['releases']):
   rel=os.path.relpath(ROOT/x['path'],folder);a=x.get('assistant',str(Path(x['path']).with_name('assistant.html')))
   rows.append('<li><strong>S'+str(x['set'])+' / '+html.escape(x['patch'])+'</strong> · '+str(x['comps'])+'套 · '+html.escape(x['snapshot'])+('（当前入口）' if x['id']==c['active'] else '')+'<br><a href="'+rel+'">版本手册</a> · <a href="'+os.path.relpath(ROOT/a,folder)+'">对局助手</a></li>')
  (folder/'index.html').write_text(page(label+' · 版本目录','<p><a href="../../index.html">返回平台选择</a></p><ul>'+''.join(rows)+'</ul>'))
  redirect(folder/'current.html',os.path.relpath(ROOT/active['path'],folder));redirect(folder/'assistant.html',os.path.relpath(ROOT/active.get('assistant',str(Path(active['path']).with_name('assistant.html'))),folder))
  sections.append('<section style="background:white;border:1px solid #cddddd;border-radius:16px;padding:24px;margin:20px 0"><h2>'+label+'</h2><p>当前收录：S'+str(active['set'])+' / '+html.escape(active['patch'])+' · '+str(active['comps'])+'套</p><a href="games/'+platform+'/current.html">打开手册</a> · <a href="games/'+platform+'/assistant.html">对局助手</a> · <a href="games/'+platform+'/index.html">全部版本</a></section>')
 (ROOT/'index.html').write_text(page('阵容罗盘 · 选择游戏平台','<p>金铲铲与TFT分别使用各自来源，按赛季、补丁与快照保存。请选择对应平台。</p>'+''.join(sections)))
if __name__=='__main__':publish_portals()
