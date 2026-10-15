#!/usr/bin/env python3
"""Join source-scoped releases for the assistant; never rewrite published snapshots."""
import json, html, hashlib
from pathlib import Path
from verify_metatft import verify
from audit_augments import audit
from branch_boards import build_branches
from role_evidence import apply_roles
from cross_game_equipment import supplement
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'games/assistant'
CAP = ROOT / 'research/2026-10-15-dual-source/tft'
def read(p): return json.loads(p.read_text())
def build():
    verified = verify()
    augment_audit = audit()
    augment_rows = {r["id"]: r for r in augment_audit["rows"]}
    registry = read(ROOT/'games/jcc/releases.json')
    active = next(r for r in registry['releases'] if r['id'] == registry['active'])
    jp = ROOT/Path(active['path']).parent.parent/'data/knowledge.json'
    j = read(jp)
    versions = [dict(id=active['id'], game='金铲铲', patch=j['release']['patch'], date=j['release']['fetched_at'][:10], set=18),
                dict(id='tft-s18-18.4b-20261015', game='TFT', patch='18.4b', date='2026-10-15', set=18)]
    units, items, comps = {}, {}, []
    traits = {}
    def label(v): return f"{v['game']} · S{v['set']} {v['patch']} · {v['date']}"
    for v in versions: v['label'] = label(v)
    v = versions[0]; prefix=v['id']+':'
    for kind,target in [('units',units),('items',items)]:
        for i,x in j[kind].items(): target[prefix+i] = dict(name=x['name'],cost=x.get('cost'),version=v['id'])
    catalog = read(jp.parent/'raw/catalog.json')['data']
    for x in catalog['equip']:
        items[prefix+str(x['id'])].update(component=x['type']=='基础装备',craftable=all(str(x.get(k,'0')) not in ['0','None',''] for k in ['synthesis1','synthesis2']),recipe=[prefix+str(x[k]) for k in ['synthesis1','synthesis2'] if str(x.get(k,'0')) not in ['0','None','']],recipe_source='金铲铲该快照catalog合成字段')
    for t in catalog['trait']:
        traits[prefix+t['checkId']] = dict(name=t['name'],thresholds=[int(n) for n in t['numList'].split('|')],verified=True)
    for h in catalog['hero']:
        uid=prefix+str(h['id'])[1:]
        if uid in units:
            units[uid].update(purchasable=j['units'][str(h['id'])[1:]].get('purchasable',False),family=uid,special=h['name']=='远古巨龙',
                traits=[prefix+t for field in ['raceId','jobId'] for t in (h.get(field) or '').split('|') if prefix+t in traits])
    for c in j['comps']:
        boards=[dict(b,units=[prefix+i for i in b['units']],stars={prefix+i:n for i,n in b.get('stars',{}).items()},source='金铲铲分等级棋盘') for b in c['stages']]
        builds=[]
        for h in c['heroes']:
            for b in h['combinations'] + ([h['recommended_combination']] if h.get('recommended_combination') else []):
                builds.append(dict(b,recommended=b is h.get('recommended_combination'),unit=prefix+h['id'],items=[prefix+i for i in b['items']],source=b.get('evidence','金铲铲 S/A 三件套统计')))
        comps.append(dict(id=prefix+c['id'],source_id=c['id'],version=v['id'],name=c['name'],tier=c['tier'],avg=c['avg'],top4=c['top4'],count=c['count'],route=c['route'],group=c['group'],
            units=[prefix+h['id'] for h in c['heroes']],heroes=[dict(id=prefix+h['id'],role=h['role'],stars=h['stars'],position=h.get('position'),core=bool(h.get('source_core') or h['role'] in ['主C','副C']),evidence=('来源核心标记；' if h.get('source_core') else '')+h['role_evidence']) for h in c['heroes']],
            traits=[t['name'] for t in c['traits']],boards=boards,builds=builds,augments=c['augments'],conditions=c['conditions'],
            emblems=[items[prefix+i]['name'] for i in c['optional_emblems']],flow=c['flow'],
            guide='../../'+active['path']+'#comp-'+c['id'],source=c['source_url'],
            cohort='金铲铲大数据（非官方）；段位与统计时间窗未提供。棋盘和装备保留各自记录统计。'))
    lookup=read(CAP/'raw/lookup-zh_cn.json'); aliases={}
    for kind in ['units','traits','items']:
        for x in lookup[kind]:
            for i in [x['apiName'],*x.get('assetNames',[])]: aliases[i]=x
    v=versions[1];prefix=v['id']+':'
    def unit(i):
        x=aliases[i];units[prefix+i]=dict(name=x['name'],cost=x.get('cost'),version=v['id'],family=x['apiName'],purchasable=x.get('cost',0)>0,traits=[prefix+t for t in x.get('traitApiNames',[])],special=x['apiName']=='TFT18_ElderDragon',role_tags=x.get('roleTags',[]));return prefix+i
    def item(i):
        x=aliases[i]
        if prefix+i not in items:
            items[prefix+i]=dict(name=x['name'],version=v['id'],component='Component' in x.get('tags',[]) or 'Item.Equippable.Item.Component' in x.get('tags',[]),craftable='Item.Equippable.Item.Craftable' in x.get('tags',[]),recipe=[],recipe_source='TFT归档词库composition；含PBE元信息，按归档配方参考')
            items[prefix+i]['recipe']=[item(r) for r in x.get('composition',[]) if r in aliases]
        return prefix+i
    for t in lookup['traits']:
        traits[prefix+t['apiName']]=dict(name=t['name'],thresholds=[],verified=False)
    for u in lookup['units']:
        if u.get('cost',0)>0:
            for alias in u.get('assetNames',[]) or [u['apiName']]: unit(alias)
    clusters=read(CAP/'raw/comps.json')['results']['data']['cluster_details']
    for r in verified['selected']:
        c=clusters[r['id']];d=read(CAP/r['detail_path'])['results']; boards=[]
        # Retain every returned record, including trait variants and source overlaps. Never sum samples.
        for field,key in [('early_options','unit_list'),('options','units_list')]:
            for level,rows in d[field].items():
                for b in rows:
                    boards.append(dict(level=int(level),units=[unit(i) for i in b[key].split('&')],stars={},count=b['count'],avg=b.get('avg'),top4=None,
                        source='MetaTFT '+field, traits=' / '.join(aliases[t.rsplit('_',1)[0]]['name'] + '（档位' + t.rsplit('_',1)[1] + '）' for t in b.get('traits_list','').split('&') if t),source_record=b))
        builds=[dict(unit=unit(b['unit']),items=[item(i) for i in b['buildName']],count=b.get('count'),avg=b.get('avg'),tier=None,source='MetaTFT详情默认样本；未赋装备评级') for b in d['builds'] if b.get('buildName')]
        lineup=[i.strip() for i in c['units_string'].split(',')]
        route={'Fast 8':'速8','Fast 9':'速9','Standard':'标准运营'}.get(r['route_source'],r['route_source'].replace('lvl ','追三星等级：'))
        comps.append(dict(id=prefix+r['id'],source_id=r['id'],version=v['id'],name=r['name'],tier=r['tier'],avg=r['avg'],top4=r['top4']*100,count=r['count'],route=route,group='未归类',
            units=[unit(i) for i in lineup],heroes=[dict(id=unit(i),role='职责未核实',stars=3 if i in c['stars'] else None) for i in lineup],
            traits=[aliases[t.strip().rsplit('_',1)[0]]['name'] for t in c['traits_string'].split(',')],boards=boards,builds=builds,augments=augment_rows[r['id']]['augments'],augment_gap=augment_rows[r['id']]['gap'],conditions=[],emblems=[e['name'] for e in r['emblems']],flow=[],situational=r['situational'],
            guide='../tft/reference/2026-10-15/index.html',source='https://www.metatft.com/comps',
            raw='../../'+str((CAP/r['detail_path']).relative_to(ROOT)),
            cohort='评级与均名：排位队列1100、近3天、白金至王者。棋盘与装备：详情接口默认样本，不能与榜单样本合并；棋盘前四率未提供。词库只用于名称，不证明两端机制一致。'))
    for c in comps:
        for h in c['heroes']:
            if h.get('core'): continue
            proofs=[p for a in c['augments'] for p in a.get('sources',[]) if p.get('match')=='exact' and c['version']+':'+p.get('main_champion','')==h['id']]
            if proofs: h.update(core=True,role='攻略主C（对应变体）',evidence=proofs[0]['title']+' · '+proofs[0]['url'])
    emblem_audit=read(CAP/'emblem-verification/audit.json')
    for evidence in emblem_audit['evidence_files']:
        assert hashlib.sha256((CAP/evidence['file']).read_bytes()).hexdigest()==evidence['sha256']
    policies={r['id']:r for r in emblem_audit['rows']}
    assert len(policies)==8
    for c in comps:
        if c['version']!=versions[1]['id'] or not c.get('situational'): continue
        policy=policies[c['source_id']];c['emblem_policy']=policy
        if policy['status']=='required':
            for name in policy['emblems']:
                ids=[i for i,x in items.items() if x['version']==c['version'] and x['name']==name]
                assert ids,name
                c['conditions'].append(dict(kind='item',id=ids[0].split(':')[-1],name=name,required=True,evidence=policy['note']))
    branches=build_branches(unit,item)
    for c in comps:
        if c['version']==versions[1]['id'] and c.get('emblem_policy'):
            c['final_branches']=branches.get(c['source_id'],{})
    apply_roles(comps)
    supplement(comps, units, items)
    result=dict(trait_catalog=traits,versions=versions,comps=comps,units=units,items=items,augment_coverage=dict(tft_covered=augment_audit["covered"],tft_total=22,related_only=sum(bool(r["augments"]) and all(p["match"]=="related" for a in r["augments"] for p in a["sources"]) for r in augment_audit["rows"]),unmapped=augment_audit["unmapped"]),
                provenance=dict(planner='星级、费用、同版本整套装备适配、自然羁绊与棋盘重合度的启发式建议；非战斗模拟或胜率统计，未计站位、对手、转职及动态羁绊。',trait_sources=['games/jcc/set18/18.3/snapshots/20261013T083011Z/data/raw/catalog.json','research/2026-10-15-dual-source/tft/raw/lookup-zh_cn.json'],jcc=str(jp.relative_to(ROOT)),jcc_sha256=hashlib.sha256(jp.read_bytes()).hexdigest(),tft='research/2026-10-15-dual-source/tft/verification/verified-sa.json'))
    assert len(comps)==37 and len({c['id'] for c in comps})==37
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'data.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
    e=html.escape
    static=''.join(f'<li>{e(next(v["label"] for v in versions if v["id"]==c["version"]))} · {e(c["tier"])} · <a href="{e(c["guide"])}">{e(c["name"])}</a> · {e(c["route"])}</li>' for c in comps)
    template=(ROOT/'tools/templates/unified-assistant.html').read_text()
    page=template.replace('__STATIC__',static).replace('__DATA__',json.dumps(result,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')).replace('__ENGINE__',(ROOT/'tools/templates/knowledge-engine.js').read_text()).replace('__CLIENT__',(ROOT/'tools/templates/unified-assistant.js').read_text())
    (OUT/'index.html').write_text(page)
    print('Unified assistant:',len(comps),'comps;',sum(len(c['boards']) for c in comps),'source board records')
    return result
if __name__=='__main__': build()
