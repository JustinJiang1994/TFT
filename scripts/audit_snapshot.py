#!/usr/bin/env python3
"""Compare an archived refresh with the released cohort, without replacing live data."""
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / 'data/refresh/2026-10-13'
def read(p): return json.loads(p.read_text())
def tier(avg): return 'S' if avg < 4.25 else 'A' if avg < 4.5 else 'B或以下'
selected = read(ROOT/'data/comps/selected.json')
old = read(ROOT/'data/comps/data.json')['results']['data']['cluster_details']
new = read(SNAP/'metatft-comps.json')['results']['data']['cluster_details']
stats = read(SNAP/'metatft-stats.json')
assert stats['cluster_id'] == 426 and stats['tft_set'] == 'TFTSet18' and stats['queue_id'] == 1100
by_id = {str(r['cluster']):r for r in stats['results']}
rows = []
for c in selected:
    cid=c['id']; r=by_id[cid]; places=r['places'][:8]; count=sum(places)
    assert count == r['count'] and count > 0
    avg=sum((i+1)*n for i,n in enumerate(places))/count
    before=read(ROOT/f'data/comps/{cid}.json')['results']; after=read(SNAP/f'details/{cid}.json')['results']
    rows.append(dict(id=cid,name=c['name'],old_tier=c['tier'],new_tier=tier(avg),old_avg=c['avg'],new_avg=avg,delta=avg-c['avg'],count=count,top4=sum(places[:4])/count,win=places[0]/count,board_changed=old[cid]['units_string']!=new[cid]['units_string'],changed_detail_fields=[k for k in sorted(set(before)|set(after)) if before.get(k)!=after.get(k)]))
# Explicitly reviewed relationships only. Similar boards alone do not establish equivalence.
links=[('426003','121','棋子集合一致，主C一致；可对照当前表现，统计口径不同，禁止计算平台间升降'),('426014','122','相关玩法；主C一致，对方终局多阿狸、拉露恩，不能直接替换评级'),('426012','116','相关玩法；主C一致，对方多厄斐琉斯及生成单位，分支仍需核对'),('426010','111','相关玩法；主C一致，其他棋子不同，不能直接替换评级'),('426001','114','相关玩法；对方多黛安娜，携带者标记缺失，需核对迅射转门槛'),('426002','105','相关玩法；主C一致，前排和终局名单不同，需核对永森转分支')]
jcc={r['compId']:r for r in read(SNAP/'jcc-rows.json')}
comparisons=[]
for cid,jid,note in links:
    r=jcc[jid]; c=next(x for x in selected if x['id']==cid)
    comparisons.append(dict(id=cid,name=c['name'],source_id=jid,source_name=r['name'],tier=r['tier'],avg=r['avgPlacement'],count=r['sampleCount'],note=note,auto_replace=False))
audit={'checked_at':datetime.now(timezone.utc).isoformat(),'scope':'既定21套；原始全榜只用于核对，不新增阵容或参与版本定调','tft':{'patch':'18.4b（沿用当前同补丁，公开榜单接口未返回补丁字段）','set':stats['tft_set'],'queue':1100,'cluster_id':426,'rank':'CHALLENGER,DIAMOND,EMERALD,GRANDMASTER,MASTER,PLATINUM','days':3,'updated':stats['updated'],'comparison':'同平台滚动3日快照重叠，不是版本前后独立样本','rows':rows},'jcc':{'source':'https://www.dataj.cc/comp','official':False,'patch':'18.3','set':18,'min_sample':50,'rank':None,'time_window':None,'source_rows':len(jcc),'relationships':comparisons,'unverified_cohort_ids':[c['id'] for c in selected if c['id'] not in {x[0] for x in links}]},'deployment':'候选快照，未覆盖线上历史统计、装备评级或补牌索引','sha256':{str(p.relative_to(SNAP)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SNAP.rglob('*')) if p.is_file() and p.name!='audit.json'}}
(SNAP/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
lines=['# 2026-10-13 数据刷新与迭代核查','',audit['deployment'],'','## TFT同口径快照','',f"已核对21套、抓取21套详情；评级变化{sum(r['old_tier']!=r['new_tier'] for r in rows)}套，代表棋盘变化{sum(r['board_changed'] for r in rows)}套。白金以上、近3日、排位1100；滚动窗口重叠，不能据此声称补丁加强或异军突起。",'','| 阵容 | 原评级→现评级 | 原均名→现均名 | 最新样本 |','|---|---|---|---|']
for r in rows:lines.append(f"| {r['name']} | {r['old_tier']}→{r['new_tier']} | {r['old_avg']:.3f}→{r['new_avg']:.3f} | {r['count']:,} |")
lines+=['','## 金铲铲对应关系核查','','来源为非官方金铲铲大数据18.3榜单。未提供可核实的段位、统计时间窗；不得与MetaTFT均名做差。这里只列现有阵容的核对线索，不扩充阵容池。','','| 现有阵容 | 来源玩法 | 来源评级/均名/样本 | 对应关系 |','|---|---|---|---|']
for r in comparisons:lines.append(f"| {r['name']} | {r['source_name']} | {r['tier']} / {r['avg']:.2f} / {r['count']:,} | {r['note']} |")
lines+=['','其余15套尚未确认可用对应关系。特别是永森95虽与德莱文阵容棋子名单一致，来源主C却是伊泽瑞尔；狂战士沃里克与献祭三狼也不能仅凭主C同名合并。','','## 已落实与后续优先级','','- 已落实：隔离新快照、保存平台/筛选/抓取时间/来源更新时间/完整性记录；第一章修正“加强就更值得试”的表述。','- P0：金铲铲准确分支映射及段位/时间窗验证完成前，禁止自动覆盖TFT评级。','- P1：装备、海克斯、各等级过渡和补牌索引必须同一批更新；本次详情字段已变化，尚未重建衍生索引，因此新快照不接入助手。','- P2：补齐同平台前后补丁快照后再提供“崛起/衰退”；当前差值只作为数据漂移核查。','','## 来源','','- https://www.metatft.com/comps','- https://www.dataj.cc/comp','- 原始抓取见 data/refresh/2026-10-13/；audit.json含21套差异、对应关系和校验和。']
(ROOT/'DATA_REFRESH_2026-10-13.md').write_text('\n'.join(lines)+'\n')
print('Audit complete:',len(rows),'comps;',len(comparisons),'reviewed JCC relationships')
