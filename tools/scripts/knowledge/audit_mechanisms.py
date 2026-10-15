#!/usr/bin/env python3
"""Evidence-bounded sidecar for six reading pairs; does not mutate either game dataset."""
import collections
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
JCC = ROOT / 'games/jcc/set18/18.3/snapshots/20261013T083011Z/data'
TFT = ROOT / 'games/tft/set18/18.4b/data/comps'
OUT = ROOT / 'research/2026-10-15-dual-source/mechanisms'
OFFICIAL = 'https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-4/'

# Editorial conclusions are deliberately scoped to the preserved reading pairs.
NOTES = {
 '87': {
  'tft_id': '426023', 'focus': ['沃里克', '暗影狼'],
  'mechanics': '两份词库都描述沃里克撕咬造成物理伤害、治疗自身并积累攻速；黑荆棘按祭品定位、星级和费用给属性。TFT原始词库的治疗数值已被官方B补丁推翻。',
  'can_reference': ['可参考6级追沃里克三星的路线分类；金铲铲本身已有该路线支持，不代表应照搬同一搜牌回合。', '这组主C三件套没有同名交集；继续使用金铲铲来源的无尽之刃、汲取剑、水银，不把TFT三件套自动列为金铲铲替代。'],
  'do_not_copy': ['金铲铲归档给伊莉丝防装，暗影狼没有推荐装备；TFT给墨菲特防装、暗影狼三件输出装。不能把金铲铲祭品思路直接换成TFT的承装暗影狼，也不能仅凭标题认定某张牌必定被献祭。', 'TFT朔极之矛、斯特拉克的挑战护手、泰坦的坚决，不能直接替换金铲铲的续航与控制免疫配置。'],
  'checks': ['warwick', 'murkwolf'],
 },
 '116': {
  'tft_id': '426012', 'focus': ['卡兹克', '赫卡里姆'],
  'mechanics': '卡兹克基础羁绊在两份词库中都是宿敌；裁决使来自进化选择，不能因为阵容名叫裁决螳螂就把他当作天然裁决使。技能描述是跳向远处敌人、对孤立目标获得额外效果。',
  'can_reference': ['卡兹克的正义之手在双方推荐中均出现；可参考输出与续航结合的承装方向。金铲铲仍保留夜之锋刃、班克斯的魔法帽。', '赫卡里姆的石像鬼石板甲、振奋盔甲、狂徒铠甲是双方完全相同的来源推荐三件套，可作为有金铲铲依据的防装组合；并不由此获得跨平台S/A装备评级。'],
  'do_not_copy': ['要先完成正确的裁决使进化，再参考这条路线；不能把基础宿敌直接算进裁决使人数。', '金铲铲副C标记是索拉卡，TFT历史出装记录还给伊泽瑞尔、黛安娜装备；不能按TFT记录转移金铲铲副C的装备优先级。', 'TFT纳什之牙不能无条件取代金铲铲夜之锋刃；前者属于回蓝方向，后者是低血量脱离选取与恢复。班克斯的魔法帽与灭世者的死亡之帽暂不自动合并ID。'],
  'checks': ['executioner', 'hecarim', 'visage'],
 },
 '105': {
  'tft_id': '426002', 'focus': ['厄斐琉斯', '莉莉娅', '伊泽瑞尔'],
  'mechanics': '双方词库将厄斐琉斯列为月蚀骑士、迅捷射手；永恒之森由纹章和队友构成。森林植物依赖羁绊与星级，不能把植物当作普通可购买棋子或额外人口。',
  'can_reference': ['厄斐琉斯的鬼索的狂暴之刃＋海妖之怒、伊泽瑞尔的朔极之矛，均有双方推荐支持。可参考持续攻击叠加和回蓝方向。', '金铲铲明确要求永恒之森纹章，开局条件仍以这一要求为准。'],
  'do_not_copy': ['金铲铲归档月男三件是海妖、鬼索、无尽；TFT历史记录是森林纹章、鬼索、海妖。不能因为纹章条件相同，就把金铲铲无尽固定换成纹章。', '金铲铲还列拉露恩、索拉卡；TFT历史棋盘列赫卡里姆、乐芙兰。换人会改变羁绊与承装位置，不是无成本替换。', '金铲铲推荐装备表没有指定森林纹章携带者，不能从TFT月男或莉莉娅的纹章记录反填一个“已确认国服携带者”。'],
  'checks': ['elderwood_emblem', 'lunar', 'aphelios_tooltip'],
 },
 '114': {
  'tft_id': '426001', 'focus': ['厄斐琉斯', '绯红印记树怪', '阿木木'],
  'mechanics': '迅捷射手描述为队伍攻速加成及射手攻击叠层；迅射纹章还给普攻附加最大生命值真实伤害。两份词库文本方向相符，但缺少锁定正式服的完整物品机制核验。',
  'can_reference': ['绯红印记树怪的迅捷射手纹章＋夜之锋刃、阿木木的石像鬼石板甲＋狂徒铠甲、月男的无尽之刃，均在双方推荐出现。按金铲铲棋盘与转职条件保留这些搭配。'],
  'do_not_copy': ['绯红印记树怪是4费，不能与1费绯红树怪混用；本次按名字与费用共同核对。', '金铲铲阿木木是双石像鬼＋狂徒，TFT是棘刺背心＋石像鬼＋狂徒；共同两件不等于整套相同，重复件数量必须保留。', 'TFT月男的强袭者的链枷不能自动替换金铲铲海妖之怒；两者在本组分别属于不同来源推荐。'],
  'checks': ['brambleback', 'aphelios_tooltip'],
 },
 '113': {
  'tft_id': '426008', 'focus': ['拉露恩', '苍蓝雕纹魔像'],
  'mechanics': '拉露恩词库描述为多目标魔法碎片和满月全体分摊伤害；月蚀给邻格增益，重装在开战与低血量时给护盾。可参考法系回蓝、技能暴击及保护前排的职责分配。',
  'can_reference': ['拉露恩的珠光护手＋朔极之矛、苍蓝雕纹魔像的圣盾使的誓约，均有金铲铲与TFT历史推荐支持。'],
  'do_not_copy': ['金铲铲拉露恩第三件为纳什之牙，TFT为大天使之杖；不能把两者视为同一种回蓝件。纳什描述还有“暴击额外4”与“提升至4”的口径差异，不能直接做法力收益计算。', '金铲铲苍蓝雕纹魔像配狂徒、石像鬼、誓约；TFT历史为三件誓约。只确认共同推荐单件，不推荐直接照搬三誓约。', '金铲铲用远古巨龙、纳尔等副输出，TFT用莫甘娜等；9级上限与Fast 9的操作含义也不相同。'],
  'checks': ['lunar', 'nashor'],
 },
 '112': {
  'tft_id': '426016', 'focus': ['希维尔'],
  'mechanics': '希维尔基础羁绊在词库中为野兽之灵、猎人，并非天然地狱火。金铲铲通过地狱火纹章走燃烧与商店机制；TFT历史猎人分组不能替代这条条件路线。',
  'can_reference': ['希维尔的红霸符是两端共同推荐；可参考攻击/技能施加灼烧与重伤的用途。金铲铲仍使用红霸符、地狱火纹章、朔极之矛。'],
  'do_not_copy': ['不能把TFT无尽、红霸符、强袭者的链枷当作金铲铲地狱火95的无转职版；移除地狱火纹章会改变羁绊条件。', '地狱火与红霸符的灼烧叠加描述，不等于重伤也叠加，更不证明红霸符是必做的最优解。', '10月12日TFT special为空；10月15日该分组被前端规则判为条件类，原因是猎人纹章使用率达到50%。两个时点不能混合，更不能宣称这套在TFT无条件可玩。'],
  'checks': ['sivir', 'inferno_unverified'],
 },
}

# Official facts override only the TFT reference layer, never JCC catalog values.
CHECKS = {
 'warwick': ('沃里克：旧词库差异已被官方补丁解释', '金铲铲归档技能伤害为230/345/535，治疗25%；TFT官方B补丁改为相同的前三星伤害及25%治疗。PBE词库的215/325/500、20%属于旧值，不能当作实装差异。', 'official_match', '2 COST UNIT'),
 'murkwolf': ('暗影狼：强化攻击旧值已过时', '金铲铲归档强化攻击为65/100/160；TFT官方B补丁也改为65/100/160。仅该字段相符，不证明献祭用途或整套装备相同。', 'official_match', '2 COST UNIT'),
 'executioner': ('裁决使：官方补丁与金铲铲归档不同', '金铲铲词库3/4裁决的额外真实伤害写30%/40%；TFT官方18.4改为25%/35%。因此不能跨平台沿用相同增伤估算；未确认金铲铲当前客户端值。', 'official_vs_jcc_snapshot', 'TRAITS'),
 'elderwood_emblem': ('森林纹章：双抗资料差异', '金铲铲词库写35护甲和魔抗；TFT官方18.4将纹章双抗由35改为25。不能把两端纹章当成同等坦度。', 'official_vs_jcc_snapshot', 'EMBLEMS'),
 'lunar': ('月蚀骑士：法强档位资料差异', '金铲铲词库写7/10/14/18%法强；TFT官方18.4改为7/12/16/20%。邻格增益方向可以理解，具体收益不可套用同一数字。', 'official_vs_jcc_snapshot', 'TRAITS'),
 'hecarim': ('赫卡里姆：初始法力资料差异', '金铲铲词库初始/最大法力为30/110；TFT官方18.4改为50/110。相同防装组合不保证相同启动时间。', 'official_vs_jcc_snapshot', 'UNITS: TIER 3'),
 'visage': ('振奋盔甲：伤害减免资料差异', '金铲铲词库基础属性写8%伤害减免；TFT官方18.4改为10%。双方推荐同一件装备，不代表数值完全一致。', 'official_vs_jcc_snapshot', 'ITEMS'),
 'sivir': ('希维尔：物理系数资料差异', '金铲铲词库一/二星初始伤害的物理项为190/285；TFT官方18.4改为200/300。这里只比较物理项，不把含法术项的总伤害混为同一字段。', 'official_vs_jcc_snapshot', 'UNITS: TIER 4'),
 'brambleback': ('4费绯红印记树怪：TFT官方调整了伤害分配', 'TFT官方18.4将普通技能物理加成由80%改为100%，跳跃伤害由155/235改为135/205。不能仅根据同名棋子或纹章效果推导两端收割强度。', 'official_tft_only', 'UNITS: TIER 4'),
 'aphelios_tooltip': ('厄斐琉斯：动态文本不可直接当伤害计算器', '金铲铲词库的挥击次数被展开为0，TFT词库该项仍含运行时计算。这个0不能读成实战不挥击；本次不确认精确次数或两端技能伤害完全一致。', 'unresolved', None),
 'nashor': ('纳什之牙：文案口径尚未确认', '金铲铲写普攻额外2法力、暴击额外4；TFT词库写暴击提升至4，计算字段为2+2。可能是文本表达差异，不能宣布实装多2法力；保留为待实测。', 'unresolved', None),
 'inferno_unverified': ('地狱火：词库疑点不能升级成实装结论', '金铲铲词库写纹章15%攻速、灼烧持续1秒；TFT PBE词库分别为40%攻速、3秒。本次未找到足以确认这些字段的正式补丁证据，不作跨平台实装差异或替代推荐。', 'unresolved', None),
}

ITEM_ROLES = {
 '无尽之刃': '物理加成与技能暴击；不能因裁决使也有技能暴击，就直接推导为无收益或必做。',
 '珠光护手': '法术加成与技能暴击；用于本页拉露恩共同推荐，不外推到所有法系。',
 '朔极之矛': '普攻额外回蓝；不能与法强随时间成长的大天使之杖视为同一功能。',
 '正义之手': '根据生命状态在输出属性与全能吸血之间增强；共同推荐不等于替代所有保命装。',
 '鬼索的狂暴之刃': '按时间叠加攻速；本词库不是旧版本的每次攻击叠攻速描述。',
 '海妖之怒': '通过攻击叠物理加成，达到攻击次数后获得攻速；与鬼索的叠加触发不同。',
 '夜之锋刃': '低血量时脱离选取、清除负面效果并恢复；不能用一般回蓝装直接替代该保护作用。',
 '石像鬼石板甲': '按正在攻击携带者的敌人数获得双抗；相同装备不保证不同站位有相同收益。',
 '狂徒铠甲': '提供生命值及最大生命值增益；不直接替代护甲、魔抗或回蓝。',
 '振奋盔甲': '回复已损失生命值，并提供伤害减免与回蓝属性；伤害减免存在官方TFT补丁与金铲铲归档差异。',
 '圣盾使的誓约': '开战给法力，低血量触发法力与护盾；单件共同推荐不证明三件叠放在金铲铲同样最优。',
 '迅捷射手纹章': '增加迅射羁绊，普攻附带最大生命值真实伤害；同时占据装备栏，不能只按普通攻速装比较。',
 '红霸符': '攻击与技能施加灼烧、重伤；不能把灼烧可叠加推导为重伤可叠加。',
}

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, data):
        self.parts.append(data)


def audit():
    read = lambda p: json.loads(p.read_text())
    k = read(JCC/'knowledge.json')
    j = read(JCC/'raw/catalog.json')['data']
    lookup_path = ROOT/'research/2026-10-15-dual-source/tft/raw/lookup-zh_cn.json'
    t = read(lookup_path)
    old = {c['id']: c for c in read(TFT/'selected.json')}
    old_comps = read(TFT/'data.json')['results']['data']['cluster_details']
    manifests = read(OUT/'fetch-manifest.json')
    for req in manifests:
        if req['ok']:
            assert hashlib.sha256((OUT/req['file']).read_bytes()).hexdigest() == req['sha256']
    assert read(OUT/'tft-lookup-recheck.json')['_metadata']['patch'] == 'pbe'
    rechecked = read(OUT/'jcc-catalog-recheck.json')['data']
    catalog_recheck = {}
    for kind, fields in [('hero', ['name', 'price', 'skillDesc', 'skillValueDesc', 'initMp', 'maxMp', 'raceId', 'jobId']),
                         ('trait', ['name', 'num', 'prefix', 'desc2Text']),
                         ('equip', ['name', 'basicDesc', 'descText'])]:
        newer = {x['id']: x for x in rechecked[kind]}
        changed = [x['id'] for x in j[kind] if x['id'] not in newer or any(x.get(f) != newer[x['id']].get(f) for f in fields)]
        catalog_recheck[kind] = {'fields': fields, 'compared_records': len(j[kind]), 'changed_ids': changed}
    parser = Text(); parser.feed((OUT/'tft-official-18.4.html').read_text())
    official_text = ' '.join(' '.join(parser.parts).split())
    for term in ['Warwick Spell Healing', 'Elderwood Emblem', 'Bleed Damage', '50/110', '200/300', 'Spirit Visage']:
        assert term in official_text, term
    jheroes = {h['id']: h for h in j['hero']}
    jtraits = {x['id']: x for x in j['trait']}
    jtrait_checks = {x['checkId']: x['name'] for x in j['trait']}
    t_units = {x['name']: x for x in t['units']}
    t_aliases = {alias: x for x in t['units'] for alias in [x['apiName'], *x.get('assetNames', [])]}
    t_traits = {x['apiName']: x for x in t['traits']}
    t_items = {x['name']: x for x in t['items']}
    jitems = {x['id']: x for x in j['equip']}
    def j_base(h):
        return jheroes['1'+h['id']]
    # Verify field-level comparisons against archived JCC rather than trusting prose.
    assert '25%' in jheroes['12508']['skillDesc']
    assert '30%' in jtraits['83890101']['desc2Text'] and '40%' in jtraits['83890101']['desc2Text']
    assert '35护甲' in jitems['41801']['basicDesc']
    assert jheroes['13500']['initMp'] == 30 and jheroes['13500']['maxMp'] == 110
    assert '8%' in jitems['2025']['basicDesc']
    assert '190/285' in jheroes['14510']['skillValueDesc']
    rows = []
    for c in k['comps']:
        if c['id'] not in NOTES: continue
        note = NOTES[c['id']]; tc = old[note['tft_id']]
        regular = [h for h in c['heroes'] if h['purchasable']]
        jnames = {h['name'] for h in regular}; tnames = set(tc['units'])
        shared = sorted(jnames & tnames)
        units = []
        for name in shared:
            h = next(h for h in regular if h['name'] == name); jb = j_base(h); tb = t_units[name]
            assert h['cost'] == jb['price'] == tb['cost'], name
            jbase = sorted({jtrait_checks[i] for key in ['raceId', 'jobId'] for i in jb[key].split('|') if i != '0'})
            units.append({'name': name, 'jcc_id': h['id'], 'jcc_catalog_id': jb['id'], 'tft_id': tb['apiName'], 'cost': h['cost'],
                          'jcc_base_traits': jbase, 'tft_lookup_traits': tb['traits'],
                          'status': '名称和费用核对；基础羁绊为词库记录，非正式服全量机制等同证明'})
        shared_builds = []
        for h in regular:
            for b in tc['builds']:
                if b['unit'] != h['name'] or not h['items']: continue
                ji = [k['items'][i]['name'] for i in h['items']]
                common = list((collections.Counter(ji) & collections.Counter(b['items'])).elements())
                if common:
                    shared_builds.append({'unit': h['name'], 'shared_items': common, 'jcc_items': ji, 'tft_items': b['items'],
                                          'same_multiset': collections.Counter(ji) == collections.Counter(b['items']),
                                          'status': '双方来源推荐交集，不授予跨平台装备评级'})
        jt = [{'name': x['name'], 'threshold': jtraits[x['id']]['num'], 'source_id': x['id']} for x in c['traits']]
        tt = []
        for s in old_comps[tc['id']]['traits_string'].split(','):
            base, tier = s.strip().rsplit('_', 1)
            tr = t_traits[base]
            tt.append({'name': tr['name'], 'source': s.strip(), 'source_tier_index': int(tier)})
        # TFT suffix is a source tier index, never interpret it as unit count.
        rows.append({'jcc_id': c['id'], 'tft_id': tc['id'], **note,
                     'common_units': units, 'jcc_only_units': sorted(jnames-tnames), 'tft_only_units': sorted(tnames-jnames),
                     'jcc_summons_excluded': [h['name'] for h in c['heroes'] if not h['purchasable']],
                     'jcc_traits': jt, 'tft_traits': tt, 'shared_builds': shared_builds})
    checks = [{'id': key, 'title': v[0], 'finding': v[1], 'status': v[2], 'official_section': v[3], 'official_url': OFFICIAL if v[3] else None} for key, v in CHECKS.items()]
    # Include full raw records for the shared named items, preserving multipliers/placeholders.
    shared_names = {name for row in rows for b in row['shared_builds'] for name in b['shared_items']}
    item_records = []
    for name in sorted(shared_names):
        js = [x for x in j['equip'] if x['name'] == name]
        assert len(js) == 1 and name in t_items, name
        item_records.append({'name': name, 'role': ITEM_ROLES[name], 'jcc_record': js[0], 'tft_lookup_record': t_items[name],
                             'status': '仅词库文本核对，PBE数值不得自动作为正式服值'})
    sources = [JCC/'knowledge.json', JCC/'raw/catalog.json', TFT/'selected.json', TFT/'data.json', lookup_path, OUT/'fetch-manifest.json', OUT/'tft-official-18.4.html']
    result = {'scope': '金铲铲10月13日已发布18.3归档，对照原6组TFT10月12日历史推荐；10月15日词库及官方18.4/B补丁用于核查',
              'policy': '两个游戏并列；共同搭配需双方来源支持；各游戏独有搭配及机制差异分别标注，不推定整套机制完全相同',
              'limits': ['金铲铲gamedata接口无补丁参数，内部版本字段混杂，不能把词库归档当成锁定18.3的正式服机制包',
                         'MetaTFT latest词库复查仍标记pbe；官网18.4b统计标签不证明该词库就是18.4b机制',
                         '官方TFT补丁支持列出的变更字段；不能据此证明金铲铲已同步更新',
                         '未找到可锁定这些字段的金铲铲官方补丁证据；保留资料差异与待确认边界',
                         'TFT机制表请求返回403；未用其他地址冒充成功结果'],
              'sources': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],
              'pairs': rows, 'checks': checks, 'shared_item_records': item_records,
              'jcc_online_catalog_recheck': catalog_recheck,
              'fully_verified_cross_platform_mechanics': False}
    (OUT/'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return result

if __name__ == '__main__':
    report = audit()
    print('Audited', len(report['pairs']), 'pairs;', len(report['checks']), 'field checks;', len(report['shared_item_records']), 'shared named items')
