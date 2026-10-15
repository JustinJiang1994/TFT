import json,time,hashlib,secrets,urllib.request,pathlib
P=pathlib.Path(__file__).resolve().parent
did='did_'+secrets.token_hex(4)+'_'+str(int(time.time()*1000))
for name,path,body in [('strategy','/team/strategy',{'id':16294}),('hero','/data/explore/list',{'version':'jcc_18.3','tier':'grandmaster','filterTargetType':'hero'}),('augments','/augment-tier/config?platform=jcc&season=18',None)]:
 t=str(int(time.time()*1000));nonce=secrets.token_hex(8)
 h={'Content-Type':'application/json','User-Agent':'Mozilla/5.0','Origin':'https://jcc.datatft.com','Referer':'https://jcc.datatft.com/','t':t,'did':did,'nonce':nonce,'signature':hashlib.md5((t+nonce+did+'koTefnFEdaYDuLFmXyzt').encode()).hexdigest(),'Browser-Language':'ZH-CN','Accept-Language':'CN','App-Platform':'jcc'}
 req=urllib.request.Request('https://api.datatft.com'+path,headers=h,data=json.dumps(body,separators=(',',':')).encode() if body is not None else None)
 try:
  with urllib.request.urlopen(req,timeout=25) as r:raw=r.read();status=r.status
  (P/(name+'.json')).write_bytes(raw);d=json.loads(raw);print(name,status,d.get('code'),len(raw),flush=True)
 except Exception as e:print(name,str(e),flush=True)
