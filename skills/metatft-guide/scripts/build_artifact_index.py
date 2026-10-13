#!/usr/bin/env python3
"""Derive observed artifact/unit/comp relations; counts do not establish optimal builds."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

def build(source, output, min_count=30):
    def read(name):
        return json.loads((source / name).read_text(encoding='utf-8'))
    z = read('zh.json')
    artifacts = {x['apiName']: x for x in z['items']
                 if 'Item.Equippable.Item.Artifact' in x.get('tags', [])}
    units = {key: u for u in z['units'] for key in [u['apiName']] + u.get('assetNames', [])}
    observed, chosen, missing = [], [], []
    seen = set()
    comps = read('selected.json')
    for c in comps:
        rows = []
        for item in read(str(c['id']) + '.json')['results'].get('itemNames', []):
            aid = item['itemNames']
            if aid not in artifacts:
                continue
            for u in item.get('units', []):
                unit = units.get(u['units'])
                if not unit:
                    unit = {'name': u['units'] + '（名称待核对）'}
                key = (str(c['id']), u['units'], aid)
                if key in seen:
                    raise ValueError(f'Duplicate evidence row: {key}')
                seen.add(key)
                if u['count'] < 0:
                    raise ValueError('Negative sample count')
                rows.append(dict(comp_id=str(c['id']), comp_name=c['name'], unit_id=u['units'],
                    unit=unit['name'], artifact_id=aid, artifact=artifacts[aid]['name'],
                    count=u['count'], avg=u.get('avg'), place_change=u.get('place_change'),
                    source=str(c['id']) + '.json#results.itemNames'))
        observed.extend(rows)
        # Preserve every source-returned bearer, including low-count and variant units.
        selected = [dict(row, low_sample=row['count'] < min_count) for row in rows]
        if not selected:
            missing.append(str(c['id']))
        chosen.extend(selected)
    by_artifact = {key: {'name': a['name'], 'candidates': []} for key, a in artifacts.items()}
    by_unit = defaultdict(list)
    for r in chosen:
        by_artifact[r['artifact_id']]['candidates'].append(r)
        by_unit[r['unit_id']].append(r)
    summary = {'comps': len(comps), 'artifact_catalog': len(artifacts),
               'observed_edges': len(observed), 'candidate_edges': len(chosen),
               'unit_count': len(by_unit), 'uncovered_comps': missing,
               'selection': {'mode': 'all_source_records', 'low_sample_label_below': min_count},
               'interpretation': 'Observed usage, not causal strength or optimality ranking'}
    output.mkdir(parents=True, exist_ok=True)
    for name, value in [('artifact-observations.json', observed), ('artifact-candidates.json', chosen),
                        ('artifact-index.json', by_artifact), ('unit-artifacts.json', by_unit),
                        ('artifact-validation.json', summary)]:
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    return summary

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--min-count', type=int, default=30)
    a = p.parse_args()
    if a.min_count < 1:
        p.error('Selection limits must be positive')
    print(json.dumps(build(a.source, a.output, a.min_count), ensure_ascii=False, indent=2))
