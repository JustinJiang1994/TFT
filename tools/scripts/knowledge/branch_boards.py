"""Build evidence-backed final boards; never infer a missing emblem variant."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'research/2026-10-15-dual-source/tft'
def build_branches(unit,item):
    archive=BASE/'augment-verification/pro-comps-directory.json'
    guides=json.loads(archive.read_text())['refs']
    def walk(x):
        if isinstance(x,dict):
            yield x
            for v in x.values(): yield from walk(v)
        elif isinstance(x,list):
            for v in x:yield from walk(v)
    def meta(gid,title,level):
        g=next(g for g in guides if g['content_id']==gid)
        b=next(v for v in walk(g['content']) if 'unit_positions'in v and v.get('title',v.get('default_variation_name'))==title)
        members=[dict(id=unit(u['apiName']),items=[item(i['apiName']) for i in u.get('items',[])],stars=u.get('tier'),position=int(pos)) for pos,u in b['unit_positions'].items() if u.get('type')=='unit']
        titles_zh={'Lvl 8 Varus':'8级迅捷射手 · 韦鲁斯', 'Lvl 8 Rapidfire-Emblem':'8级迅捷射手 · 有转职', 'Lvl 8 Nidalee':'8级奈德丽 · 无转职替代', 'Lvl 8 w/ Malphite':'8级希维尔 · 搭配墨菲特', 'Lvl 7 w/ Brawler-Emblem':'7级易 · 斗士转职', 'Lvl 7 Yi only':'7级易 · 常规配装'}
        return dict(title=titles_zh.get(title,title),source_title=title,level=level,members=members,units=[u['id'] for u in members],source='https://www.metatft.com/pro-comps?comp='+gid,evidence_file=str(archive.relative_to(ROOT)),source_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),note='10月15日归档作者棋盘；作者未显式标注18.4b。星级为攻略目标，不是当前星级。',relation='same-route')
    def documented(title,ids,level,slug,emblem=None,relation='same-route'):
        members=[dict(id=unit(i),items=[item(emblem[1])] if emblem and i==emblem[0] else [],stars=None,position=None) for i in ids]
        evidence=BASE/'emblem-verification/web-evidence.json'
        return dict(title=title,level=level,members=members,units=[m['id'] for m in members],source='https://www.pivottft.com/comps/'+slug+'/',evidence_file=str(evidence.relative_to(ROOT)),source_sha256=hashlib.sha256(evidence.read_bytes()).hexdigest(),note='18.4b攻略名单；这里只录已确认的棋子与纹章携带，站位及其余装备未补造。',relation=relation)
    yi='8c51379e-a96a-4767-bf58-8b90bc75925b';ap='034d3180-d2d7-41af-837a-74aa2a6803e2'
    no=meta(ap,'Lvl 8 Nidalee',8);no['relation']='alternative';no['note']+=' 这是奈德丽月男替代路线，原转职分支的海克斯关系和S/A统计不自动继承。'
    boards={'426001':dict(with_emblem=meta(ap,'Lvl 8 Rapidfire-Emblem',8),without_emblem=no),
            '426029':dict(with_emblem=meta(yi,'Lvl 7 w/ Brawler-Emblem',7),without_emblem=meta(yi,'Lvl 7 Yi only',7)),
            '426021':dict(without_emblem=meta('a483ad08-cc76-45f6-b0f8-62ba33030899','Lvl 8 Varus',8)),
            '426016':dict(without_emblem=meta('1a6f5d18-c41f-47cb-ada6-572ae7449fce','Lvl 8 w/ Malphite',8))}
    defender=['DA_18_Cassiopeia','DA_18_Lillia','DA_18_Ornn','DA_18_Rammus','DA_18_Rengar','DA_18_Shen','DA_Fiddlesticks18']
    boards['426000']=dict(with_emblem=documented('6护卫雷恩加尔',defender,7,'defender-rengar-reroll',('DA_18_Rengar','DA_18_EmblemDefender')),
      without_emblem=documented('无转职：蛇女护卫替代路线',[i if i!='DA_18_Rengar' else 'DA_18_Leona' for i in defender],7,'defender-rengar-reroll',relation='alternative'))
    forest=['DA_18_Ornn','DA_18_Alistar','DA_18_Hecarim','DA_18_Lillia','DA_18_LeBlanc','DA_18_Xayah','DA_18_Ezreal','DA_18_Aphelios']
    boards['426002']=dict(with_emblem=documented('8级森林月男 · 有转职',forest,8,'elderwood-aphelios',('DA_18_Aphelios','DA_18_EmblemElderwood')),without_emblem=documented('8级森林月男 · 无转职低档位',forest,8,'elderwood-aphelios'))
    rengar=['DA_18_MasterYi_AD','DA_18_Rengar','DA_18_Sett','DA_18_Yorick','DA_Krug18','DA_Nidalee18_AP','DA_Vi18']
    boards['426022']=dict(without_emblem=documented('7级易＋雷恩加尔 · 常规配装棋盘',rengar,7,'rengar-master-yi-reroll'))
    for cid,b in boards.items():
        for key,v in b.items():
            assert len(v['units'])==v['level'] and len(set(v['units']))==len(v['units'])
            v['key']=key
    return boards
