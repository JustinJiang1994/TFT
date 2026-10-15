"""Supplement absent JCC complete builds with explicitly labeled TFT references."""
def supplement(comps, units, items):
    tft=[c for c in comps if c['version'].startswith('tft')]
    for c in comps:
        if not c['version'].startswith('jcc'): continue
        c['cross_game_builds']=[]
        names={units[i]['name'] for i in c['units']}
        for uid in dict.fromkeys(c['units']):
            if any(b['unit']==uid and len(b['items'])==3 for b in c['builds']): continue
            target=units[uid]
            h=next((h for h in c['heroes'] if h['id']==uid),{})
            options=[]
            for donor in tft:
                overlap=len(names & {units[i]['name'] for i in donor['units']})
                if overlap<3: continue
                for dh in donor['heroes']:
                    du=units[dh['id']]
                    if du['name']!=target['name'] or du.get('cost')!=target.get('cost'): continue
                    role=dh.get('role','')
                    tank='坦' in role;carry='C' in role or '输出' in role
                    if not (tank or carry) or '转职' in role: continue
                    if '坦' in h.get('role','') and not tank: continue
                    if 'C' in h.get('role','') and not carry: continue
                    for b in donor['builds']:
                        if b['unit']!=dh['id'] or len(b['items'])!=3: continue
                        mapped=[]
                        for iid in b['items']:
                            src=items[iid]
                            matches=[i for i,x in items.items() if x['version']==c['version'] and x['name']==src['name']]
                            if len(matches)!=1: break
                            dest=items[matches[0]]
                            # Only equivalent named two-component recipes are budgeted.
                            if not src.get('craftable') or not dest.get('craftable'): break
                            if len(src.get('recipe',[]))!=2 or len(dest.get('recipe',[]))!=2: break
                            if sorted(items[i]['name'] for i in src['recipe'])!=sorted(items[i]['name'] for i in dest['recipe']): break
                            mapped.append(matches[0])
                        if len(mapped)!=3: continue
                        options.append((overlap,b.get('count') or 0,dict(unit=uid,items=mapped,tier=b.get('tier'),avg=None,count=None,source='TFT 18.4b 跨游戏配装参考',cross_game=True,donor_role=role,donor_comp=donor['name'],donor_id=donor['id'],donor_unit=dh['id'],donor_items=b['items'],donor_avg=b.get('avg'),donor_count=b.get('count'),donor_source=donor.get('raw',donor['source']),overlap=overlap)))
            if options:
                options.sort(key=lambda x:(x[0],x[1]),reverse=True)
                c['cross_game_builds'].append(options[0][2])
