#!/usr/bin/env python3
"""Trace creator S/A recommendations to archived roster variants, never empty stats."""
import json,hashlib
from pathlib import Path
from external_augments import external
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'research/2026-10-15-dual-source/tft'
def load(p):return json.loads(p.read_text())
def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)
def audit():
    live=BASE/'augment-verification';manifest=load(live/'manifest.json')
    for r in manifest['requests']:assert hashlib.sha256((live/r['file']).read_bytes()).hexdigest()==r['sha256']
    selected=load(BASE/'verification/verified-sa.json')['selected'];clusters=load(BASE/'raw/comps.json')['results']['data']['cluster_details']
    lookup=load(BASE/'raw/lookup-zh_cn.json');aug={a['apiName']:a for a in lookup['augments']}
    # These are the two Elderwood generated plants, not board slots. No other unit is discarded.
    generated={'DA_Elderwood18_StonebarkTree','DA_Elderwood18_Lifeblossom'}
    related={'426010':'同为阿狸主输出、莫甘娜副输出的速8分支；代表棋盘有塔里克/克格莫差异，属于相关攻略参考。',
             '426022':'同为易和雷恩加尔7级追三星分支；攻略人口变体与当前代表棋盘不同，属于相关攻略参考。'}
    rows=[];unmapped=set()
    for c in selected:
        response=load(live/(c['id']+'.json'));assert response['cluster_id']==426 and response['tft_set']=='TFTSet18' and response['queue_id']==1100
        target=set(clusters[c['id']]['units_string'].replace(' ','').split(','));accepted={};guides=[]
        candidates=list(response['results'].get('proComps',[]))
        known={g['content']['content_id'] for g in candidates}
        for co in load(live/'pro-comps-directory.json')['refs']:
            exact_any=any(({u['apiName'] for u in v['unit_positions'].values() if u.get('type')=='unit'}-generated)==target for v in walk(co['content']) if 'unit_positions' in v)
            if exact_any and co['content_id'] not in known:candidates.append({'content':co});known.add(co['content_id'])
        for g in candidates:
            co=g['content'];body=co['content'];variants=[v for v in walk(body) if 'unit_positions'in v]
            variants=[(v,{u['apiName'] for u in v['unit_positions'].values() if u.get('type')=='unit'}-generated) for v in variants]
            exact=next(((v,us) for v,us in variants if us==target),None)
            best=max(variants,key=lambda vu:len(vu[1]&target)/max(1,len(vu[1]|target))) if variants else ({},set())
            match='exact' if exact else 'related' if c['id'] in related else 'unmatched'
            if match=='related' and ('AHRI' if c['id']=='426010' else 'MASTER YI') not in co['metadata']['title']:match='unmatched'
            variant,us=exact or best
            evidence=dict(author=co['author']['riotid'],title=co['metadata']['title'],updated_at=co['updated_at'],url='https://www.metatft.com/pro-comps?comp='+co['content_id'],guide_id=co['content_id'],match=match,variant=variant.get('title',body.get('default_variation_name','默认棋盘')),missing=sorted(target-us),extra=sorted(us-target),patch_note='作者未显式标注18.4b；这是10月15日详情关联的攻略，不是同补丁胜率统计。',note='扣除两种生成植物后，与攻略某人口变体棋子集合一致；不据此证明装备或机制完全相同。' if exact else related.get(c['id'],'来源关联相近攻略，未确认适配此分支。'))
            found=[]
            for v in walk(body):
                if v.get('type')!='tierlist':continue
                for tier in v.get('tiers',[]):
                    for entry in walk(tier.get('content',[])):
                        if entry.get('type')!='augment':continue
                        aid=entry['apiName']
                        if aid not in aug:unmapped.add(aid);continue
                        found.append((aid,tier['label']))
            guides.append(dict(evidence,recommended_sa=len({i for i,t in found if t in ['S','A']})))
            if match=='unmatched':continue
            for aid,tier in found:
                if tier not in ['S','A']:continue
                a=aug[aid];entry=accepted.setdefault(aid,dict(id=aid,name=a['name'],rarity={'Silver':1,'Gold':2,'Prismatic':3}.get(a['rarity'],0),rounds=a.get('rounds',[]),avg=None,count=None,evidence='作者攻略推荐（非统计排名）',sources=[]))
                proof=dict(evidence,tier=tier)
                if proof not in entry['sources']:entry['sources'].append(proof)
        rows.append(dict(id=c['id'],name=c['name'],augments=list(accepted.values()),guides=guides,status='supported' if accepted else 'missing',gap=None if accepted else '未找到与此分支核实对应的作者S/A海克斯推荐；空统计、相近主C或不同运营攻略不补作推荐。'))
    supplemental=external()
    by_id={r['id']:r for r in rows}
    for r in supplemental['rows']:
        target=by_id[r['id']]
        assert not target['augments'], 'supplement only previously missing recommendations'
        target['augments']=r['augments'];target['status']='supported';target['gap']=None
        target['guides'].append(r['source'])
    for r in supplemental['remaining']:by_id[r['id']]['gap']=r['reason']
    unmapped.update(r['id'] for r in supplemental['unmapped'])
    out=dict(directory_guides_checked=len(load(live/'pro-comps-directory.json')['refs']),rows=rows,unmapped=sorted(unmapped),covered=sum(bool(r['augments']) for r in rows),total=len(rows),rules='MetaTFT取作者S/A海克斯条目；外部攻略取明确推荐条目。不把阵容评级、海克斯全局评级和本阵容推荐混同；相关分支与缺口显式标记。',manifest='augment-verification/manifest.json')
    (live/'audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('TFT augment coverage',out['covered'],'/',len(rows));return out
if __name__=='__main__':audit()
