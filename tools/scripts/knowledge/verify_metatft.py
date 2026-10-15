#!/usr/bin/env python3
"""Reproduce all tiers from the immutable Oct 15 capture, with separate patch evidence."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CAPTURE = ROOT / 'research/2026-10-15-dual-source/tft'


def load(path):
    return json.loads(path.read_text())


def item_type(item):
    api = item.get('apiName', '')
    tags = item.get('tags', [])
    composition = item.get('composition') or []
    for tag, kind in [('Emblem', 'emblem'), ('Artifact', 'artifact'), ('Support', 'support')]:
        if tag in tags:
            return kind
    if 'Trait' in tags or 'TFT11_Storyweaver' in api or 'TFT11_Item_Inkshadow' in api:
        return 'trait'
    if 'Emblem' in api or 'TFT_Item_Spatula' in composition or 'TFT_Item_FryingPan' in composition:
        return 'emblem'
    return None


def verify():
    verification = CAPTURE / 'verification'
    for base, manifest in [(CAPTURE, load(CAPTURE / 'manifest.json')), (verification, load(verification / 'manifest.json'))]:
        for r in manifest['requests']:
            assert r.get('ok', True)
            assert hashlib.sha256((base / r['file']).read_bytes()).hexdigest() == r['sha256'], r['file']
    source = (verification / 'main-Cukhk3-v.js').read_text()
    assert 'p<4.25?h="S":p<4.5?h="A"' in source
    assert 'z4t=.5' in source and 'n.pcnt>=z4t?foe(t[n.itemNames])==="emblem"' in source
    current = load(verification / 'stats-current-check.json')
    explicit = load(verification / 'stats-explicit-18.4b.json')
    assert current['results'] == explicit['results']
    filters = load(verification / 'games.json')
    patch = filters['current_patch']
    assert (patch['patch'], patch['b_patch_version']) == ('18.4', 'b')
    assert filters['patch']['patch_data'][0] == patch
    raw = load(CAPTURE / 'raw/comps.json')
    stats = load(CAPTURE / 'raw/stats.json')
    assert all(d['tft_set'] == 'TFTSet18' and d['queue_id'] == 1100 and d['cluster_id'] == 426 for d in [raw, stats, current, explicit])
    comps = raw['results']['data']['cluster_details']
    stat_rows = [r for r in stats['results'] if r['cluster'] in comps]
    assert len(stat_rows) == len({r['cluster'] for r in stat_rows}) == len(comps) == 60
    lookup = load(CAPTURE / 'raw/lookup-zh_cn.json')
    names, items = {}, {}
    for kind in ['units', 'traits', 'items', 'augments']:
        for x in lookup[kind]:
            for key in [x['apiName'], *x.get('assetNames', [])]:
                assert key not in names or names[key] == x['name'], key
                names[key] = x['name']
            if kind == 'items':
                items[x['apiName']] = x
    missing = set()
    def name(key):
        if key not in names:
            missing.add(key)
        return names.get(key, key)
    rows = []
    for stat in stat_rows:
        cid = stat['cluster']
        c = comps[cid]
        places = stat['places']
        assert len(places) == 9 and all(isinstance(n, int) and n >= 0 for n in places)
        count = sum(places[:8])
        assert count == places[8] == stat['count'] and count > 0
        score = sum((i + 1) * n for i, n in enumerate(places[:8]))
        # Integer comparisons avoid rounding values across the tier boundary.
        tier = 'S' if score * 4 < count * 17 else 'A' if score * 2 < count * 9 else 'B' if score * 4 < count * 19 else 'C' if score < count * 5 else 'D'
        special = []
        for item in c['top_itemNames']:
            assert item['itemNames'] in items, item['itemNames']
            if item['pcnt'] >= .5 and item_type(items[item['itemNames']]) == 'emblem':
                special.append({'id': item['itemNames'], 'name': name(item['itemNames']), 'fraction': item['pcnt']})
        augment_named = 'Augment' in c['name_string']
        rows.append({'id': cid, 'name': ' / '.join(name(x['name']) for x in c['name']),
                     'tier': tier, 'avg': score / count, 'count': count,
                     'top4': sum(places[:4]) / count, 'win': places[0] / count,
                     'placements': places[:8], 'route_source': c['levelling'],
                     'situational': bool(special or augment_named), 'emblems': special,
                     'augment_named': augment_named,
                     'source_name': c['name_string'], 'units': [name(u.strip()) for u in c['units_string'].split(',')],
                     'detail_path': 'raw/comps/' + cid + '.json'})
    rows.sort(key=lambda x: (x['avg'], x['id']))
    assert not missing, sorted(missing)
    selected = [r for r in rows if r['tier'] in ['S', 'A']]
    old = load(ROOT / 'games/tft/set18/18.4b/data/comps/selected.json')
    old_ids = {r['id'] for r in old}
    ids = {r['id'] for r in selected}
    result = {
        'platform': 'tft', 'set': 'TFTSet18', 'patch': '18.4b',
        'patch_status': '来源补丁标签已核实；原始current归档通过同日配置和后续双查询交叉支持，不是原始响应内嵌补丁字段',
        'patch_evidence': {'config_current_patch': patch, 'config_updated': filters['updated'],
                           'current_check_updated': current['updated'], 'explicit_check_updated': explicit['updated'],
                           'check_results_identical': True},
        'capture_filters': load(CAPTURE / 'manifest.json')['stats_request_filters'],
        'stats_updated_beijing': datetime.datetime.fromtimestamp(stats['updated']/1000, datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'comps_updated': raw['updated'], 'stats_updated': stats['updated'],
        'grade_rule': {'S': 'avg < 4.25', 'A': '4.25 <= avg < 4.5', 'adjustments': '不使用装备、强化、城邦或指定变体的个性化均名修正'},
        'cohort': '所有60个返回分组；含默认隐藏的条件阵容；不加最低出场率过滤',
        'excluded_stat_records': [r for r in stats['results'] if r['cluster'] not in comps],
        'counts': {'all': len(rows), 'selected': len(selected), 'tiers': dict(collections.Counter(r['tier'] for r in selected)),
                   'default': sum(not r['situational'] for r in selected), 'situational': sum(r['situational'] for r in selected)},
        'historical_id_difference': {'added': sorted(ids-old_ids), 'removed': sorted(old_ids-ids),
                                     'caution': '仅分组ID集合差异；标签与棋盘可能漂移，不作补丁增强或同阵容强度变化结论'},
        'name_mapping': '当日中文词库apiName及assetNames别名；只取名称，不采用pbe技能数值',
        'unmapped_names': sorted(missing), 'all_comps': rows, 'selected': selected,
        'limits': ['条件分类使用comps_data默认人群中的top_itemNames比例，不是指定段位3天统计',
                   '条件分类不保证穷尽入场门槛；未标条件不等于无条件适配',
                   '来源updated与实际统计窗口起止不是同一字段；未提供精确窗口起止',
                   'TFT评级和出装不覆盖金铲铲结论']}
    (verification / 'verified-sa.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return result


if __name__ == '__main__':
    result = verify()
    print(json.dumps(result['counts'], ensure_ascii=False))
