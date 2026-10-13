#!/usr/bin/env python3
"""Collect → normalize → validate → render; publish only with explicit --publish."""
import argparse,importlib.util,json,shutil,subprocess,sys,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(name):
 spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py'));mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def write_json(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
def historical_copy():
 mapping={'index.html':'tft-18.4b.html','assistant.html':'assistant-tft-18.4b.html','equipment.html':'equipment-tft-18.4b.html'}
 if (ROOT/'index.html').exists() and not (ROOT/'tft-18.4b.html').exists():
  for old,new in mapping.items():
   s=(ROOT/old).read_text()
   for a,b in mapping.items():s=s.replace(a,b)
   (ROOT/new).write_text(s)
  v=ROOT/'versions.html'
  if v.exists():
   s=v.read_text()
   for a,b in mapping.items():s=s.replace(a,b)
   (ROOT/'version-review-2026-10-13.html').write_text(s)
def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path);p.add_argument('--set',type=int);p.add_argument('--patch');p.add_argument('--publish',action='store_true');a=p.parse_args()
 if a.snapshot:snapshot=a.snapshot.resolve()
 else:
  cmd=[sys.executable,str(Path(__file__).with_name('collect.py'))]
  if a.set:cmd+=['--set',str(a.set)]
  if a.patch:cmd+=['--patch',a.patch]
  result=json.loads(subprocess.check_output(cmd,text=True));snapshot=ROOT/result['snapshot']
 manifest=json.loads((snapshot/'manifest.json').read_text());rid=f'jcc-s{manifest["set"]}-{manifest["patch"]}-{manifest["snapshot"]}'
 catalog_path=ROOT/'data/knowledge/releases.json';catalog=json.loads(catalog_path.read_text()) if catalog_path.exists() else {'schema_version':1,'active':None,'releases':[]}
 assert rid not in {x['id'] for x in catalog['releases']},'This snapshot is already published; collect a new snapshot to revise it'
 k=load('build').normalize(snapshot);load('validate').validate(snapshot)
 target=ROOT/'releases'/rid;load('render').render(snapshot,target,'../../','guide.html')
 if not a.publish:print('Staged:',target/'guide.html');return
 historical_copy()
 # Generate root entrypoints only after data validation and both versioned pages succeed.
 load('render').render(snapshot,ROOT)
 catalog['releases'].append({'id':rid,'platform':'jcc','set':manifest['set'],'patch':manifest['patch'],'previous_patch':manifest['previous_patch'],'snapshot':manifest['snapshot'],'comps':len(k['comps']),'path':str(target.relative_to(ROOT))+'/guide.html','knowledge':str(snapshot.relative_to(ROOT))+'/knowledge.json'})
 catalog['active']=rid;write_json(catalog_path,catalog)
 links=''.join(f'<li><a href="{html.escape(x["path"])}">金铲铲 S{x["set"]} · {html.escape(x["patch"])} · {x["comps"]}套 · {html.escape(x["snapshot"])}</a>{"（当前）" if x["id"]==rid else ""}</li>' for x in reversed(catalog['releases']))
 (ROOT/'versions.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>版本记录</title><body style="font:18px/1.8 system-ui;max-width:950px;margin:40px auto;padding:20px"><h1>版本记录</h1><p>每版完整获取榜单，重新选择S/A；历史页面与数据不覆盖。</p><ul>'+links+'</ul><h2>历史TFT参考</h2><p><a href="tft-18.4b.html">TFT18.4b · 原21套手册</a> · <a href="assistant-tft-18.4b.html">旧版助手</a> · <a href="equipment-tft-18.4b.html">旧版装备速查</a></p><p><a href="index.html">返回当前版本</a> · <a href="assistant.html">打开当前助手</a></p></body></html>')
 print('Published:',rid)
if __name__=='__main__':main()
