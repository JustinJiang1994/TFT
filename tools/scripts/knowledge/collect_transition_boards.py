"""Refresh public per-level responses for the existing 37-composition cohort, separately from releases."""
import json, pathlib, urllib.request, concurrent.futures, datetime, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
def main():
 data=json.loads((ROOT/'games/assistant/data.json').read_text())
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 out=ROOT/'research/transition-refresh'/stamp;out.mkdir(parents=True)
 def fetch(c):
  game='jcc' if c['version'].startswith('jcc') else 'tft'
  url=f"https://www.dataj.cc/api/web/comp/{c['source_id']}/battle-builds?setId=18&gameVersion=18.3" if game=='jcc' else f"https://api-hc.metatft.com/tft-comps-api/comp_details?comp={c['source_id']}&cluster_id=426"
  row={'id':c['id'],'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'explicit JCC 18.3' if game=='jcc' else 'fixed TFT cluster 426; endpoint default filters, patch not embedded'}
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
   with urllib.request.urlopen(req,timeout=18) as r:raw=r.read()
   body=json.loads(raw);path=out/(game+'-'+c['source_id']+'.json');path.write_bytes(raw)
   row.update(ok=True,file=str(path.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest())
  except Exception as e:row.update(ok=False,error=str(e))
  return row
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,data['comps']))
 (out/'manifest.json').write_text(json.dumps({'scope':'Existing cohort; capture only, not automatically merged into published versions','requests':rows},ensure_ascii=False,indent=2))
 print(json.dumps({'manifest':str(out/'manifest.json'),'ok':sum(r['ok'] for r in rows),'failed':sum(not r['ok'] for r in rows)},ensure_ascii=False))
if __name__=='__main__':main()
