import pathlib,urllib.request,json,time,hashlib,secrets,datetime
ROOT=pathlib.Path(__file__).resolve().parent
logs=[]
def fetch(name,url,body=None):
 headers={'User-Agent':'Mozilla/5.0','Origin':'https://jcc.datatft.com','Referer':'https://jcc.datatft.com/'}
 if body is not None:
  t=str(int(time.time()*1000));nonce=secrets.token_hex(8);did='did_public_snapshot'
  headers.update({'Content-Type':'application/json','t':t,'did':did,'nonce':nonce,'signature':hashlib.md5((t+nonce+did+'koTefnFEdaYDuLFmXyzt').encode()).hexdigest(),'Browser-Language':'ZH-CN','Accept-Language':'CN','App-Platform':'jcc'})
 rec={'file':'raw/'+name,'url':url,'body':body,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  req=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,headers=headers)
  with urllib.request.urlopen(req,timeout=45) as r:raw=r.read()
  d=json.loads(raw);p=ROOT/'raw'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  rec.update(ok=not (isinstance(d,dict) and ('code' in d or d.get('success') is False)) or d.get('code')==1,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
  print(name,rec['ok'],str(d)[:180],flush=True)
  return d
 except Exception as e:rec.update(ok=False,error=str(e));print(name,str(e),flush=True)
 finally:
  logs.append(rec);(ROOT/'manifest.json').write_text(json.dumps({'source':'https://jcc.datatft.com','platform':'jcc','requests':logs},ensure_ascii=False,indent=2))
def api(name,path,body):return fetch(name,'https://api.datatft.com'+path,body)
if __name__=='__main__':
 fetch('catalog-s18.json','https://jcc.datatft.com/assets/h5-data-cn-18-C8KhxreH.json')
 api('team-list.json','/team/list',{'version':'jcc_18.3','season':'18','tier':'grandmaster','time':5})
 api('team-comps.json','/team/comps',{'season':'18'})
 api('home.json','/team/home',{'version':'jcc_18.3','season':'18','tier':'grandmaster','time':5,'gamePlatform':2})
 for typ in ['hero','equip','trait']:
  api('stats-'+typ+'.json','/data/explore/list',{'version':'jcc_18.3','tier':'grandmaster','filterTargetType':typ})
