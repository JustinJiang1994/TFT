"""Apply curated TFT role evidence without changing JCC or inheriting alternative roles."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def apply_roles(comps):
    path=ROOT/'research/2026-10-15-dual-source/tft/role-verification/roles.json'
    evidence=json.loads(path.read_text());audit=[]
    assert hashlib.sha256((ROOT/evidence['archive']).read_bytes()).hexdigest()==evidence['archive_sha256']
    for c in comps:
        if not c['version'].startswith('tft-'):continue
        rows=[r for r in evidence['rows'] if r['comp']==c['source_id']]
        def apply(heroes,records):
            for r in records:
                h=next((h for h in heroes if h['id'].split(':')[-1]==r['unit']),None)
                if h is None:continue
                if h.get('role_confirmed') and not r['confirmed']:continue
                h.update(role=r['role'],core=r['confirmed'],role_confirmed=r['confirmed'],role_candidate=not r['confirmed'],role_source=r['source'],role_note=r['note'],evidence=r['note']+' · '+r['source'])
            return heroes
        apply(c['heroes'],[r for r in rows if not r['branch']])
        for key,b in c.get('final_branches',{}).items():
            # Only same-route evidence may be reused. Alternatives start with no roles.
            heroes=[dict(id=i,role='本变体职责未核实',core=False) for i in b['units']]
            records=[r for r in rows if r['branch']==key or (not r['branch'] and b['relation']!='alternative')]
            b['heroes']=apply(heroes,records)
        for key,heroes in [('default',c['heroes'])]+[(key,b['heroes']) for key,b in c.get('final_branches',{}).items()]:
            audit.append(dict(comp=c['source_id'],name=c['name'],branch=key,confirmed=[h['id'] for h in heroes if h.get('core')],tank_confirmed=any(h.get('role_confirmed') and '坦' in h['role'] for h in heroes),candidates=[h['id'] for h in heroes if h.get('role_candidate')]))
    (path.parent/'audit.json').write_text(json.dumps(dict(evidence_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),rows=audit),ensure_ascii=False,indent=2))
