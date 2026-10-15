import collect,json,time
p=collect.ROOT
collect.logs=json.loads((p/'manifest.json').read_text())['requests']
rank=collect.api('rank.json','/team/rank',{'season':'18'})
rows=json.loads((p/'raw/team-list.json').read_text())['data']['list']
ids={int(r.get('strategyId') or r['id']) for r in rows}
if rank and rank.get('code')==1:
 for r in rank['data'].get('list',[]):
  if r.get('id'):ids.add(int(r['id']))
for cid in sorted(ids):
 collect.api('strategies/'+str(cid)+'.json','/team/strategy',{'id':cid});time.sleep(.15)
collect.fetch('augment-tier-config.json','https://api.datatft.com/augment-tier/config?platform=jcc&season=18')
