"""Read-only parsing of archived public guides; exact roster checks before enrichment."""
import datetime,hashlib,html,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parents[3]/'research/2026-10-15-dual-source/tft'
ACADEMY={'426007':'set-18-riftbeast-reroll','426002':'set-18-aphelios-vanguards-copy','426008':'set-18-ap-95','426006':'set-18-sprykin-teemo-copy','426012':'set-18-lunarwood-khazix','426009':'set-18-cashout-morgana','426023':'set-18-warwick-rr'}
PIVOT={'426000':'defender-rengar-reroll','426027':'coven-morgana','426013':'invoker-teemo-reroll'}
def load(p):return json.loads(p.read_text())
def academy_data(s):
    # Only a literal data array is parsed. No downloaded JavaScript is executed.
    start=s.index('data: [{type:"data"')+6;quoted=False;escaped=False;depth=0;end=None
    for i in range(start,len(s)):
        c=s[i]
        if quoted:
            if escaped:escaped=False
            elif c=='\\':escaped=True
            elif c=='"':quoted=False
        elif c=='"':quoted=True
        elif c in '[{':depth+=1
        elif c in ']}':
            depth-=1
            if depth==0:end=i+1;break
    assert end
    parts=re.split(r'("(?:\\.|[^"\\])*")',s[start:end])
    for i in range(0,len(parts),2):
        parts[i]=re.sub(r'\b([A-Za-z_$][\w$]*)\s*:',r'"\1":',parts[i]);parts[i]=re.sub(r'\bundefined\b','null',parts[i])
    return json.loads(''.join(parts))
def external():
    folder=BASE/'augment-external';manifest=load(folder/'manifest.json');requests={r['file']:r for r in manifest['requests']}
    for r in requests.values():assert hashlib.sha256((folder/r['file']).read_bytes()).hexdigest()==r['sha256']
    lookup=load(BASE/'raw/lookup-zh_cn.json');augs={a['apiName']:a for a in lookup['augments']};english={a['en_name']:a for a in lookup['augments'] if a.get('en_name')}
    units={key:u for u in lookup['units'] for key in [u['apiName'],*u.get('assetNames',[])]}
    clusters=load(BASE/'raw/comps.json')['results']['data']['cluster_details'];out=[];unmapped=[]
    generated={'DA_Elderwood18_StonebarkTree','DA_Elderwood18_Lifeblossom','DA_Elderwood18_Protector'}
    assert all(units[i]['cost']==0 for i in generated)
    def entry(a,proof):return dict(id=a['apiName'],name=a['name'],rarity={'Silver':1,'Gold':2,'Prismatic':3}[a['rarity']],rounds=a.get('rounds',[]),avg=None,count=None,evidence='外部攻略明确推荐（非胜率统计）',sources=[proof])
    for cid,slug in ACADEMY.items():
        file='academy-'+slug+'.html';data=academy_data((folder/file).read_text());patch=next(x['data']['patch']for x in data if x and 'patch'in x.get('data',{}));assert patch=='18.4b'
        g=next(x['data']['queriedGuide']for x in data if x and 'queriedGuide'in x.get('data',{}));assert g['set']==18 and g['compSlug']==slug
        roster={u['apiName']for u in g['finalComp']}-generated
        detail=load(BASE/'raw/comps'/f'{cid}.json')['results'];matches=[dict(level=int(l),record=b)for l,bs in detail['options'].items()for b in bs if set(b['units_list'].split('&'))==roster];assert matches,(cid,slug)
        assert g['mainChampion']['apiName'] in roster
        proof=dict(author='TFT Academy 编辑攻略',title=g['title'],updated_at=g['updated'],url=requests[file]['url'],guide_id=slug,match='exact',tier=None,recommendation_label='本阵容明确推荐（未单独评级）',variant=' / '.join(str(n)+'级'for n in sorted({b['level']for b in matches})),patch_note='页面标注18.4b，攻略赛季18；保留来源更新时间，不赋予海克斯统计胜率。',note='与MetaTFT已收录人口变体的可购买棋子集合完全一致；仅排除词库标为0费的森林召唤物。',source_file=str((folder/file).relative_to(BASE)),source_sha256=requests[file]['sha256'],source_board=sorted(roster),match_levels=sorted({b['level']for b in matches}),main_champion=g['mainChampion']['apiName'])
        rows=[]
        for a in g['augments']:
            if a.get('disabled'):continue
            if a['apiName']not in augs:unmapped.append(dict(comp=cid,id=a['apiName'],source=slug));continue
            conditions={
                ('426002','DA_BlackthornTraitAugment'):'装备提炼需要黑荆棘献祭过渡才能兑现；本终局没有黑荆棘，不代表成型后仍能触发。',
                ('426009','DA_18_CovenTraitAugment'):'女巫使魔用于魔女精粹过渡阶段；该终局不维持魔女羁绊。',
                ('426009','DA_18_CovenTraitAugment_LootToAP'):'黑暗仪式改变魔女精粹兑换；仅在实际走魔女过渡且愿意换取法强时参考，不能当普通经济强化。'}
            extra=conditions.get((cid,a['apiName']))
            rows.append(entry(augs[a['apiName']],dict(proof,note=proof['note']+(' '+extra if extra else ''))))
        out.append(dict(id=cid,augments=rows,source=proof))
    for cid,slug in PIVOT.items():
        file=slug+'.html';s=(folder/file).read_text();assert 'Patch 18.4b'in s and 'Set 18'in s
        section=s.split('Units and items</h2>',1)[1].split('<h3',1)[0]
        names={html.unescape(n)for n in re.findall(r'<a[^>]*href="/set-18/champions/[^\"]+"[^>]*>([^<]+)</a>',section)}
        target={i.strip()for i in clusters[cid]['units_string'].split(',')};assert names=={units[i]['en_name']for i in target},(cid,names)
        date=re.search(r'Updated (\d+ [A-Za-z]+ \d{4})',s).group(1);date=datetime.datetime.strptime(date,'%d %B %Y').date().isoformat()
        title=html.unescape(re.search(r'<h1[^>]*>(.*?)</h1>',s).group(1));proof=dict(author='PivotTFT 编辑团队',title=title,updated_at=date,url=requests[file]['url'],guide_id=slug,match='exact',tier=None,recommendation_label='本阵容 Best augments 明确推荐',variant='代表棋盘',patch_note='来源标注18.4b；编辑推荐，不是实测胜率。站点海克斯全局评级与本阵容推荐分别保留。',note='棋子名单、主C和运营路线与本分支核对；不替换MetaTFT阵容评级或统计。',source_file=str((folder/file).relative_to(BASE)),source_sha256=requests[file]['sha256'],source_board=sorted(target))
        if cid=='426000':proof['note']+=' 来源明确要求雷恩加尔携带护卫纹章；选择其他海克斯并不免除该条件。'
        section=s.split('Best augments</h2>',1)[1].split('</ul>',1)[0];rows=[]
        for li in re.findall(r'<li\b[^>]*>(.*?)</li>',section,re.S):
            name=html.unescape(re.search(r'<a class="cg-aug-name"[^>]*>(.*?)</a>',li).group(1));a=english[name]
            kind=html.unescape(re.search(r'<span class="cg-aug-kind">(.*?)</span>',li).group(1));assert a['rarity']in kind
            grade=re.search(r', ([SABCD]) tier',kind).group(1)
            rows.append(entry(a,dict(proof,global_augment_tier=grade,recommendation_label='本阵容明确推荐；站点全局评级'+grade)))
        assert len(rows)==4
        out.append(dict(id=cid,augments=rows,source=proof))
    gap='已核查MetaTFT、TFT Academy、PivotTFT及LUM.GG。LUM.GG同棋盘明确暂无海克斯建议；TFT Academy的狂战伊莉丝与TFT Flow的野怪树怪为不同核心/羁绊分支，未挪用推荐。'
    lum=(folder/'brambleback-ravager.html').read_text();assert 'No augment suggestions yet' in lum
    result=dict(rows=out,unmapped=unmapped,remaining=[dict(id='426037',reason=gap,url=requests['brambleback-ravager.html']['url'])],rules='仅接入已核对棋盘、核心玩法、赛季和版本的明确推荐。TFT Academy没有单条评级；Pivot全局评级不是阵容内排名，Best augments中的B/C条目仍是明确推荐。')
    (folder/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':
    a=external();print('External coverage',len(a['rows']),'relations',sum(len(r['augments'])for r in a['rows']),'unmapped',a['unmapped'])
