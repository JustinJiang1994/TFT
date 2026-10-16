"""Curated single-emblem branches, checked against the local JCC catalog."""
import json,re
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent
# No automatic trait-name matching: each entry has an explicit holder and purpose.
PLANS=[
('104','猎人','绯红印记树怪','让小红的猎人从未激活变为2档；大红也能利用物理加成与击杀叠攻击。'),
('107','重装战士','纳尔','与大蓝开2重装，给纳尔增加前排护盾，延长小蓝输出时间。'),
('99','迅捷射手','绯红印记树怪','鸡哥从未激活迅射变为2迅射；大红普攻也能叠攻速和触发纹章真伤。'),
('100','猎人','蔚','3猎人升4猎人，女警与其他猎人获得更高物理加成；蔚也能利用攻击收益。'),
('106','主宰','崔丝塔娜','5名主宰补到6档，提高全队及主宰减伤；由副输出占槽，保留女警三件套。'),
('110','月蚀骑士','韦鲁斯','2月蚀升3月蚀；同时保留3日蚀，开启日月双蚀。韦鲁斯利用攻速与法强。'),
('87','斗士','沃里克','3斗士补4斗士，提高前排生命；狼人利用额外生命和纹章的生命值普攻伤害。'),
('112','神谕','凯南','与大蓝开2神谕，提供全队回蓝；凯南利用施法回蓝与纹章法强，须另有火转给希维尔。'),
('113','月蚀骑士','纳尔','2月蚀升3月蚀，强化黛安娜、拉露恩及邻格；纳尔利用攻速和法强。'),
('114','月蚀骑士','霞','2月蚀升3月蚀，强化月男与邻格输出；霞获得额外攻速，仍需大红持迅射转。'),
('105','月蚀骑士','霞','3月蚀升4月蚀，月男与霞共享更高攻速、法强；保留莉莉娅的森林转。'),
('105','迅捷射手','伊泽瑞尔','2迅射升3迅射，强化月男与霞的叠攻速；伊泽瑞尔利用普攻叠速，保留森林转。'),
('89','神谕','艾翁','与大蓝开2神谕，提供全队回蓝；艾翁利用更快施法和纹章法强。'),
('116','月蚀骑士','奥恩','与黛安娜开2月蚀；奥恩向邻格提供攻速法强光环，可覆盖螳螂，仍须螳螂裁决进化。'),
]
REQUIRED=[('105','永恒之森','莉莉娅'),('114','迅捷射手','绯红印记树怪'),('112','地狱火','希维尔')]
def build_options():
 cat=json.loads((P/'catalog.json').read_text())['data'];traits={t['name']:t for t in cat['trait']};checks={str(t['checkId']):t['name'] for t in cat['trait']};ht={}
 for h in cat['hero']:
  if int(h['id'])<20000:ht.setdefault(h['name'],{checks[x] for x in re.split('[,|]',str(h['raceId'])+','+str(h['jobId'])) if x in checks})
 boards=json.loads((P/'logic-audit.json').read_text())['boards'];result={}
 for cid,trait,holder,reason in PLANS+[(c,t,h,'本攻略所列成型分支的前提；补到目标羁绊档位。') for c,t,h in REQUIRED]:
  level=9 if cid in ['112','113','89'] else 8
  b=next(b for b in boards if b['comp']==cid and b['level']==level);required=(cid,trait,holder) in REQUIRED
  counts=Counter()
  for hero in b['board']:
   for t in ht[hero]:counts[t]+=2 if hero=='远古巨龙' and t=='峡谷野怪' else 1
  if b['evolve']:counts['裁决使']+=1
  for h,t in b['emblems'].items():
   if not(required and h==holder and t==trait):counts[t]+=1
  assert holder in b['board'] and trait not in ht[holder]
  assert len(b['board'])+('远古巨龙' in b['board'])==level
  before=counts[trait];thresholds=[int(x) for x in traits[trait]['numList'].split('|')];active=lambda n:max([0]+[x for x in thresholds if x<=n]);after=before+1
  assert active(after)>active(before),(cid,trait,before,after)
  result.setdefault(cid,[]).append(dict(name=trait+'纹章',kind='必需转职' if required else '可选提升',holder=holder,level=level,board=b['board'],before=before,after=after,gain=f'{before}→{after}{trait}（激活档位 {active(before)}→{active(after)}）',reason=reason,change='不换牌；使用下列完整参照盘。',cost='占持有者1个装备槽；保留主C关键输出装、前排必要生存装，满装时不要直接覆盖。',evidence=('分支前提来自源榜；莉莉娅持有为机制推演' if cid=='105' else '分支前提及持有者按本攻略记录') if required else '机制推演，非独立胜率结论；仅适用于此参照盘。'))
 (P/'emblem-options-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result
