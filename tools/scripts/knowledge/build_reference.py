#!/usr/bin/env python3
"""Build an isolated, dated TFT reference from archived evidence; never publish rankings."""
import hashlib
import html
import json
import os
from pathlib import Path
from verify_metatft import verify
from audit_mechanisms import audit, OUT as MECHANISMS, OFFICIAL

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'games/tft/reference/2026-10-15'
JCC = ROOT / 'games/jcc/set18/18.3/snapshots/20261013T083011Z/data/knowledge.json'
TFT = ROOT / 'games/tft/set18/18.4b/data/comps'
RESEARCH = ROOT / 'research/2026-10-15-dual-source/tft'
# Editorial reading pairs, not validated cross-platform composition mappings.
PAIRS = [
    ('87', '426023', '沃里克路线', '金铲铲名为献祭三狼，TFT名为狂战士沃里克；同名携带者和6级路线不足以证明献祭条件、技能或成型棋盘相同。'),
    ('116', '426012', '卡兹克路线', '两份归档均有7级路线；可比较追三星目标和承装位，但不能据此认定装备数值或副C职责相同。'),
    ('105', '426002', '森林厄斐琉斯路线', '两端归档都明确列出永恒之森纹章条件；可比较各自的承装位，但同名纹章不证明效果相同，也不能当成无转职替代。'),
    ('114', '426001', '迅射厄斐琉斯路线', '两端归档都明确列出迅捷射手纹章条件；两个平台的推荐装备和转职承装位仍需分别阅读。'),
    ('113', '426008', '拉露恩高人口路线', '金铲铲的9级上限标签与TFT的Fast 9不是相同定义；终局9级不证明应该速9。'),
    ('112', '426016', '希维尔路线', '金铲铲地狱火95明确要求地狱火纹章；TFT猎人希维尔的special字段为空。两者门槛不能互相替代，空字段也不证明TFT无条件。'),
]

def load(path):
    return json.loads(path.read_text())

def link(path, label):
    return '<a href="' + html.escape(os.path.relpath(path, OUT)) + '">' + html.escape(label) + '</a>'

def text(value):
    return html.escape(str(value))

def build():
    verified = verify()
    mechanism_audit = audit()
    mechanics = {r['jcc_id']: r for r in mechanism_audit['pairs']}
    checks = {r['id']: r for r in mechanism_audit['checks']}
    k = load(JCC)
    selected = load(TFT / 'selected.json')
    scope = load(TFT / '来源与统计口径.json')
    manifest = load(RESEARCH / 'manifest.json')
    # Check the new capture itself, not the precomputed inventory's integrity claim.
    for request in manifest['requests']:
        assert request['ok']
        assert hashlib.sha256((RESEARCH / request['file']).read_bytes()).hexdigest() == request['sha256']
    clusters = load(RESEARCH / 'raw/comps.json')['results']['data']['cluster_details']
    assert len(clusters) == manifest['rank_count']
    assert len(selected) == scope['selected_count']
    jc = {c['id']: c for c in k['comps']}
    tc = {c['id']: c for c in selected}
    rows = []
    for jid, tid, topic, limitation in PAIRS:
        j, t = jc[jid], tc[tid]
        assert t['tier'] in ('S', 'A')
        assert t['tier'] == ('S' if t['avg'] < 4.25 else 'A' if t['avg'] < 4.5 else None)
        rows.append({
            'topic': topic, 'status': '阅读线索，未确认跨平台对应或可迁移性',
            'jcc': {'platform': 'jcc', 'id': jid, 'name': j['name'], 'tier': j['tier'],
                    'route': j['route'], 'conditions': j['conditions'],
                    'units': [h['name'] for h in j['heroes']],
                    'stars': [h['name'] for h in j['heroes'] if h['stars'] == 3],
                    'builds': [{'unit': h['name'], 'items': [k['items'][i]['name'] for i in h['items']]}
                               for h in j['heroes'] if h['items']]},
            'tft': {'platform': 'tft', **{key: t[key] for key in ['id', 'name', 'tier', 'econ', 'special', 'units', 'stars', 'builds']}},
            'limitation': limitation,
        })
    paths = [JCC, TFT / 'selected.json', TFT / '来源与统计口径.json', RESEARCH / 'manifest.json', RESEARCH / 'verification/manifest.json', RESEARCH / 'verification/verified-sa.json', MECHANISMS / 'audit.json']
    result = {'as_of': '2026-10-15', 'purpose': '双游戏并列对照；统计按游戏与版本保存',
              'jcc_release': k['release'], 'tft_scope': scope,
              'sources': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
              'pairs': rows, 'verified_tft_20261015': verified,
              'mechanism_audit': mechanism_audit,
              'unpaired_jcc_ids': [c['id'] for c in k['comps'] if c['id'] not in {p[0] for p in PAIRS}]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    body = '<p>' + link(ROOT / 'index.html', '返回首页') + ' · ' + link(ROOT / 'games/jcc/assistant.html', '金铲铲助手') + '</p>'
    body += '<h1>TFT 18.4b 研究与金铲铲对照</h1><p class="notice">整理日期：2026-10-15。以下是已保存来源的对照，不是实时强度榜。金铲铲与TFT并列展示，各条记录标明游戏、版本和快照；机制差异及来源口径随记录保留。</p><p><a href="#verified-sa">10月15日完整S/A与补丁证据</a> · <a href="#historical-pairs">历史6组对照</a></p>'
    body += '<h2>先确认研究范围</h2><ul><li>金铲铲助手当前发布：S18 / 18.3，2026-10-13快照，15套 S/A，评级来自金铲铲大数据；来源未提供段位与统计时间窗。</li><li>TFT历史研究：页面观察标签18.4b，统计更新时间2026-10-12 15:47:54（北京时间），排位队列1100、白金及以上、3天窗口；从60个分组中选出21套（默认16、条件5）。归档记录按公开前端规则复现：均名小于4.25为S，4.25至小于4.5为A。这与金铲铲来源评级是不同口径。</li><li>本页只挑选6组阅读线索，不是完整跨平台映射，也不计算两端均名差或强度高低。</li></ul>'
    body += '<p>依据：' + link(JCC, '金铲铲已发布知识库') + ' · ' + link(TFT / 'selected.json', 'TFT历史21套研究') + ' · ' + link(TFT / '来源与统计口径.json', 'TFT历史筛选口径') + '</p>'
    body += '<h2 id="historical-pairs">6组机制与搭配核查</h2><p>共同搭配比较仍采用金铲铲10月13日已发布推荐与TFT10月12日历史研究；10月15日名单在后文独立列出。<strong>“可参考”只指金铲铲自身也有推荐依据，不代表整套跨平台适配或装备S/A评级。</strong></p>'
    body += '<p class="notice">本轮已核对棋子费用、基础羁绊、推荐出装交集与12项机制疑点。金铲铲词库不支持历史补丁锁定；MetaTFT最新词库复查仍为PBE。能用TFT官方补丁确认的字段另列，剩余差异只称“资料差异”，不冒充两端当前客户端实测。</p><p>依据：' + link(JCC.parent / 'raw/catalog.json', '金铲铲归档词库') + ' · ' + link(RESEARCH / 'raw/lookup-zh_cn.json', 'TFT词库及PBE元数据') + ' · <a href="' + OFFICIAL + '">Riot官方18.4与B补丁</a> · ' + link(MECHANISMS / 'audit.json', '逐项证据、源ID与校验和') + ' · ' + link(MECHANISMS / 'fetch-manifest.json', '本轮在线核查记录') + '</p>'
    if not any(x['changed_ids'] for x in mechanism_audit['jcc_online_catalog_recheck'].values()):
        body += '<p>本轮在线复查的金铲铲词库，在所检查的棋子技能/费用/基础羁绊、羁绊描述、装备描述字段上与归档一致。这能确认来源文本仍一致，不能替代金铲铲客户端或官方补丁验证。</p>'
    for row in rows:
        body += '<section id="pair-' + row['jcc']['id'] + '"><h2>' + text(row['topic']) + '</h2><p>' + text(row['limitation']) + '</p><div class="columns">'
        for platform in ['jcc', 'tft']:
            c = row[platform]
            is_jcc = platform == 'jcc'
            body += '<article><h3>' + ('金铲铲18.3 · 10月13日快照' if is_jcc else 'TFT 18.4b · 10月12日快照') + '</h3><p><strong>' + text(c['name']) + '</strong> · 本平台归档评级 ' + text(c['tier']) + '</p>'
            body += '<p>运营标签：' + text(c['route'] if is_jcc else c['econ']) + '</p>'
            condition = c['conditions'] if is_jcc else c['special']
            body += '<p>来源条件字段：' + text(('、'.join(x['name'] + ('（必需）' if x.get('required') else '（来源条件）') for x in condition) if is_jcc else '、'.join(condition)) if condition else '未列出；不能据此证明无条件') + '</p>'
            body += '<p>三星目标：' + text('、'.join(c['stars']) or '未列出') + '</p><p>棋盘名单：' + text('、'.join(c['units'])) + '</p><details><summary>来源推荐出装（不等于单件或三件套S/A）</summary><ul>'
            body += ''.join('<li>' + text(b['unit'] + '：' + '、'.join(b['items'])) + '</li>' for b in c['builds']) + '</ul></details>'
            target = JCC.parent.parent / 'pages/guide.html' if is_jcc else TFT.parent.parent / 'index.html'
            anchor = '#comp-' + c['id'] if is_jcc else '#c' + c['id']
            body += '<p><a href="' + text(os.path.relpath(target, OUT) + anchor) + '">本平台详细攻略</a> · ' + link(JCC if is_jcc else TFT / 'selected.json', '本栏来源记录') + '</p></article>'
        body += '</div>'
        m = mechanics[row['jcc']['id']]
        body += '<h3>双方共同搭配与游戏差异</h3><p>' + text(m['mechanics']) + '</p><h4>双方来源支持的搭配与路线</h4><ul>'
        body += ''.join('<li>' + text(x) + '</li>' for x in m['can_reference']) + '</ul><h4>不能直接照搬</h4><ul>'
        body += ''.join('<li>' + text(x) + '</li>' for x in m['do_not_copy']) + '</ul>'
        body += '<details><summary>展开棋子、羁绊与推荐装备核对</summary><p>双方共有棋子按名字与费用核对；不是技能数值一致的证明。</p><ul>'
        for u in m['common_units']:
            body += '<li>' + text(u['name'] + '（' + str(u['cost']) + '费）：金铲铲基础羁绊 ' + '、'.join(u['jcc_base_traits']) + '；TFT词库 ' + '、'.join(u['tft_lookup_traits'])) + '</li>'
        body += '</ul><p>仅见于这张金铲铲归档棋盘：' + text('、'.join(m['jcc_only_units']) or '无') + '。仅见于这张TFT历史棋盘：' + text('、'.join(m['tft_only_units']) or '无') + '。这是所列棋盘差异，不是该平台所有可用变体。</p>'
        if m['jcc_summons_excluded']:
            body += '<p>金铲铲来源另列生成单位：' + text('、'.join(m['jcc_summons_excluded'])) + '；已从可购买棋子对照中排除，不能据此计算人口或购牌数。</p>'
        body += '<p>金铲铲归档成型羁绊：' + text('、'.join(str(x['threshold']) + x['name'] for x in m['jcc_traits'])) + '。</p><p>TFT历史分组羁绊：' + text('、'.join(x['name'] for x in m['tft_traits'])) + '。这里只展示来源名称，不把后缀档位索引当作人数；纹章与进化会影响实际人数。</p><ul>'
        for b in m['shared_builds']:
            body += '<li>' + text(b['unit'] + '：共同推荐 ' + '、'.join(b['shared_items']) + ('；三件套及重复数量完全一致。' if b['same_multiset'] else '；只有所列条目相同，完整三件套不同。')) + '</li>'
        if not m['shared_builds']:
            body += '<li>本组同名承装位没有同名推荐装备交集；不自动合并名称不同的装备。</li>'
        body += '</ul></details><h4>具体机制证据与缺口</h4><ul>'
        for key in m['checks']:
            check = checks[key]
            body += '<li><strong>' + text(check['title']) + '</strong>：' + text(check['finding'])
            if check['official_url']:
                body += ' <a href="' + check['official_url'] + '">官方补丁依据</a>'
            body += '</li>'
        body += '</ul></section>'
    body += '<details id="shared-item-mechanics"><summary>13件共同推荐装备：机制用途与替代边界</summary><p>下表归纳两份词库文本中的功能，用来解释已有金铲铲推荐。除上文官方补丁确认的字段外，不宣称两端正式服数值完全相同，也不自动互换ID。</p><ul>'
    for item in mechanism_audit['shared_item_records']:
        body += '<li><strong>' + text(item['name']) + '</strong>：' + text(item['role']) + '<small>（金铲铲ID ' + text(item['jcc_record']['id']) + '；TFT ' + text(item['tft_lookup_record']['apiName']) + '）</small></li>'
    body += '</ul><p>' + link(MECHANISMS / 'audit.json', '完整物品原始描述与曲线字段') + '</p></details>'
    unpaired = [jc[i]['name'] for i in result['unpaired_jcc_ids']]
    body += '<h2>尚未配对的金铲铲阵容</h2><p>' + text('、'.join(unpaired)) + '。本次没有建立阅读配对，不代表TFT中不存在这些玩法。</p>'
    counts = verified['counts']
    evidence = RESEARCH / 'verification'
    body += '<section id="verified-sa"><h2>10月15日完整S/A：TFT 18.4b</h2><p>补丁标签已核实为18.4b：MetaTFT筛选配置current_patch与patch_data首项均为18.4 + b；前端将首项显示为current。随后同条件查询current和明确patch=18.4、b_patch=b，全部返回统计记录一致。原始10:14抓取响应不含具体补丁字段，本结论由同日配置和后续双查询交叉支持；不声称原始响应直接标注18.4b。</p>'
    body += '<p>核查依据：' + link(evidence / 'games.json', '筛选配置（来源更新时间10:40）') + ' · ' + link(evidence / 'stats-current-check.json', 'current复核') + ' · ' + link(evidence / 'stats-explicit-18.4b.json', '明确18.4b复核') + ' · ' + link(evidence / 'frontend-evidence.json', '前端规则摘录及位置') + ' · ' + link(evidence / 'manifest.json', '核查请求URL与哈希') + '</p>'
    body += '<p><strong>下表仍使用原始归档：' + text(verified['stats_updated_beijing']) + '</strong>，排位队列1100、白金及以上、请求3天、未指定地区。后续复核的滚动统计不替换这张表。详情与条件分类来自来源默认人群，不能假定与统计同一人群。</p>'
    body += '<p>逐一核对全部' + str(counts['all']) + '个分组，按未修正均名得到<strong>' + str(counts['selected']) + '套（' + str(counts['tiers']['S']) + ' S、' + str(counts['tiers']['A']) + ' A）</strong>，其中默认类' + str(counts['default']) + '套、条件类' + str(counts['situational']) + '套。S：均名&lt;4.25；A：4.25≤均名&lt;4.5。使用未四舍五入值分级，不套用装备、强化、城邦或指定变体的个性化修正，也不另加最低出场率过滤。完整指接口返回的60个分组，不是所有游戏内组合。</p>'
    body += '<p>条件类复现前端规则：名称字段含Augment，或top_itemNames中纹章使用比例≥50%。这不是已确认的必需门槛；默认类也不保证无条件可玩。名字来自当日中文词库的apiName与assetNames别名，未使用其pbe技能数值。</p>'
    body += '<div class="table-wrap"><table><thead><tr><th>评级</th><th>中文分组名 / ID</th><th>来源运营标签</th><th>类别与纹章使用率</th><th>均名</th><th>前四率</th><th>登顶率</th><th>记录数</th></tr></thead><tbody>'
    route_names = {'Fast 8': '速8', 'Fast 9': '速9', 'Standard': '常规运营'}
    for c in verified['selected']:
        route = route_names.get(c['route_source'], c['route_source'].replace('lvl ', '追牌等级 '))
        condition = '条件类：' + '、'.join(x['name'] + ' ' + format(x['fraction'], '.1%') for x in c['emblems']) if c['situational'] else '默认类'
        body += '<tr><td>' + text(c['tier']) + '</td><td>' + text(c['name']) + '<br><small>' + text(c['id']) + '</small><details><summary>归档棋盘与证据</summary>' + text('、'.join(c['units'])) + '<p>' + link(RESEARCH / c['detail_path'], '原始详情（默认人群）') + '</p></details></td><td>' + text(route) + '</td><td>' + text(condition) + '</td><td>' + format(c['avg'], '.4f') + '</td><td>' + format(c['top4'], '.2%') + '</td><td>' + format(c['win'], '.2%') + '</td><td>' + format(c['count'], ',') + '</td></tr>'
    body += '</tbody></table></div><p>均名＝各名次×记录数之和÷前八项总数；前四率＝前四项÷前八项总数；登顶率＝第一项÷前八项总数。places第9项是总数，不是第9名。空cluster总计与-1未分类记录不当成阵容，也不计入60分组。</p>'
    body += '<p>' + link(RESEARCH / 'raw/stats.json', '原始名次分布') + ' · ' + link(RESEARCH / 'raw/comps.json', '全60分组与条件依据') + ' · ' + link(evidence / 'verified-sa.json', '全部60组计算结果、22套入选及审计') + '</p>'
    body += '<h3>与10月12日研究的差异</h3><p>按分组ID比较，新增426029「魔战士 / 易」，旧21个ID均仍入选。仅说明本次筛选集合变化；标签和棋盘可能漂移，且同为18.4b，不据此宣称补丁增强。10月15日条件分类为8套，与历史记录的5套分开保留，不反向修改旧研究。</p><p>新采集保存60个详情、64次成功请求，本次重新校验全部原始文件SHA-256；中文名称未映射数量为0。金铲铲新采集仍是独立候选快照，未替换当前助手。</p></section>'
    body += '<p>依据：' + link(RESEARCH / 'manifest.json', '新采集请求与哈希') + ' · ' + link(RESEARCH / 'raw/lookup-zh_cn.json', '词库元数据') + ' · ' + link(ROOT / 'games/jcc/releases.json', '金铲铲发布指针') + '</p>'
    body += '<h2>仍无法确认的差异</h2><ul><li>两个平台的技能、羁绊、装备数值和平衡补丁是否相同；本页未给出任何已适配结论。</li><li>同名棋子与相似阵容不证明目标星级、转职门槛或成型路径一致；名称差异也不自动合并。</li><li>TFT详情中的强化统计存在空ID；历史推荐来自高手攻略时，是攻略意见而非当前分支强化胜率。不能补进金铲铲海克斯筛选。</li><li>各等级棋盘是独立样本，不能拼成一条已验证的升级路线；装备使用记录不等于可直接替代。</li></ul>'
    body += '<p>' + link(TFT / '海克斯推荐与依据.json', '历史强化推荐及攻略引用') + ' · ' + link(RESEARCH / 'raw/comps/426023.json', '新沃里克分组完整详情') + ' · ' + link(OUT / 'comparison.json', '结构化对照与来源校验和') + '</p>'
    css = 'body{font:16px/1.75 system-ui;color:#20383d;background:#f4f5f1;max-width:1100px;margin:auto;padding:24px}a{color:#216f78}section,.notice{padding:20px;background:white;border:1px solid #cfded9;border-radius:12px;margin:24px 0}.columns{display:grid;grid-template-columns:1fr 1fr;gap:24px}article{min-width:0}summary{cursor:pointer}h1{line-height:1.3}.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:900px;font-size:14px}th,td{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid #cfded9}td:nth-child(n+5){white-space:nowrap}@media(max-width:720px){.columns{grid-template-columns:1fr}}'
    (OUT / 'index.html').write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TFT历史研究与金铲铲对照</title><style>' + css + '</style></head><body>' + body + '</body></html>')
    print('Built 6 isolated reading pairs; verified', len(manifest['requests']), 'captured requests')

if __name__ == '__main__':
    build()
