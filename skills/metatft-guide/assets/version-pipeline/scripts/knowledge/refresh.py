#!/usr/bin/env python3
"""Collect → normalize → validate → render; publish only with explicit --publish."""
import argparse,importlib.util,json,shutil,subprocess,sys,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(name):
 spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py'));mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def write_json(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path);p.add_argument('--set',type=int);p.add_argument('--patch');p.add_argument('--publish',action='store_true');a=p.parse_args()
 if a.snapshot:snapshot=a.snapshot.resolve()
 else:
  cmd=[sys.executable,str(Path(__file__).with_name('collect.py'))]
  if a.set:cmd+=['--set',str(a.set)]
  if a.patch:cmd+=['--patch',a.patch]
  result=json.loads(subprocess.check_output(cmd,text=True));snapshot=ROOT/result['snapshot']
 manifest=json.loads((snapshot/'manifest.json').read_text());rid=f'jcc-s{manifest["set"]}-{manifest["patch"]}-{manifest["snapshot"]}'
 catalog_path=ROOT/'games/jcc/releases.json';catalog=json.loads(catalog_path.read_text()) if catalog_path.exists() else {'schema_version':1,'active':None,'releases':[]}
 assert rid not in {x['id'] for x in catalog['releases']},'This snapshot is already published; collect a new snapshot to revise it'
 k=load('build').normalize(snapshot);load('validate').validate(snapshot)
 target=snapshot.parent/'pages';prefix=__import__('os').path.relpath(ROOT,target)+'/'
 load('render').render(snapshot,target,prefix,'guide.html')
 if not a.publish:print('Staged:',target/'guide.html');return
 catalog['releases'].append({'id':rid,'platform':'jcc','set':manifest['set'],'patch':manifest['patch'],'previous_patch':manifest['previous_patch'],'snapshot':manifest['snapshot'],'comps':len(k['comps']),'path':str(target.relative_to(ROOT))+'/guide.html','knowledge':str(snapshot.relative_to(ROOT))+'/knowledge.json'})
 catalog['active']=rid;write_json(catalog_path,catalog)
 load('portal').publish_portals()
 print('Published:',rid)
if __name__=='__main__':main()
