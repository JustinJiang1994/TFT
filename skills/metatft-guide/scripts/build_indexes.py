#!/usr/bin/env python3
"""Build derived relations without modifying source data or the report."""
import argparse
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.anchors = [], []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        href = attrs.get('href', '')
        if href.startswith('#') and len(href) > 1:
            self.anchors.append(href[1:])

def build(source, output, report=None):
    def read(name):
        return json.loads((source / name).read_text(encoding='utf-8'))
    comps = read('selected.json')
    ids = {str(c['id']) for c in comps}
    if len(ids) != len(comps):
        raise ValueError('Duplicate composition IDs')
    recs = read('海克斯推荐与依据.json')
    inverse = {}
    covered = set()
    pairs = set()
    for row in recs:
        cid = str(row['id'])
        if cid not in ids or cid in covered:
            raise ValueError(f'Unknown or duplicate recommendation comp: {cid}')
        covered.add(cid)
        for a in row['recommendations']:
            key = a['apiName']
            if a['rarity'] not in {'Silver', 'Gold', 'Prismatic', 'Unknown'}:
                raise ValueError(f'Invalid rarity: {key}')
            if (cid, key) in pairs:
                raise ValueError(f'Duplicate recommendation: {cid}/{key}')
            pairs.add((cid, key))
            entry = inverse.setdefault(key, {'name': a['name'], 'rarity': a['rarity'], 'comps': []})
            if (entry['name'], entry['rarity']) != (a['name'], a['rarity']):
                raise ValueError(f'Inconsistent augment identity: {key}')
            entry['comps'].append({'id': cid, 'name': row['name'], 'reason': a.get('reason'),
                                   'condition': a.get('condition'), 'guide': a.get('guide')})
    if covered != ids:
        raise ValueError(f'Missing recommendation rows: {sorted(ids-covered)}')
    routes = read('前期过渡路线与证据.json')['routes']
    route_ids = set()
    for route in routes:
        seen = set()
        for target in route['targets']:
            cid = str(target['id'])
            if cid not in ids or cid in seen:
                raise ValueError(f'Unknown/duplicate route target: {cid}')
            if target.get('level4_sample_count', 0) < 0:
                raise ValueError('Negative route sample count')
            seen.add(cid)
            route_ids.add(cid)
    diffs = []
    if (source / '核心棋子与人口换人对照.json').exists():
        for row in read('核心棋子与人口换人对照.json'):
            if str(row['id']) not in ids:
                raise ValueError('Unknown variant comp')
            vs = sorted(row['variants'], key=lambda v: v['level'])
            if not vs or len({v['level'] for v in vs}) != len(vs):
                raise ValueError('Empty/duplicate variant levels')
            core = [u for u in vs[0]['units'] if all(u in v['units'] for v in vs)]
            changes = []
            for a, b in zip(vs, vs[1:]):
                changes.append({'from': a['level'], 'to': b['level'],
                    'added': [u for u in b['units'] if u not in a['units']],
                    'removed': [u for u in a['units'] if u not in b['units']],
                    'retained': [u for u in a['units'] if u in b['units']]})
            diffs.append({'id': row['id'], 'core_within_listed_variants': core, 'changes': changes})
    html_status = None
    if report:
        parser = Links()
        parser.feed(report.read_text(encoding='utf-8'))
        duplicates = [k for k, n in Counter(parser.ids).items() if n > 1]
        missing = sorted(set(parser.anchors) - set(parser.ids))
        if duplicates or missing:
            raise ValueError(f'HTML duplicate IDs={duplicates}; missing anchors={missing}')
        html_status = {'ids': len(parser.ids), 'anchors': len(parser.anchors), 'valid': True}
    summary = {'comps': len(ids), 'augments': len(inverse), 'recommendation_edges': len(pairs),
        'routes': len(routes), 'route_coverage': len(route_ids), 'uncovered_by_routes': sorted(ids-route_ids),
        'variant_comps': len(diffs), 'html': html_status}
    output.mkdir(parents=True, exist_ok=True)
    for filename, value in [('augment-index.json', inverse), ('variant-diffs.json', diffs), ('validation.json', summary)]:
        (output / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    return summary

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--html', type=Path)
    args = p.parse_args()
    print(json.dumps(build(args.source, args.output, args.html), ensure_ascii=False, indent=2))
