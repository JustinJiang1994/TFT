import json,pathlib,html,datetime,hashlib
P=pathlib.Path(__file__).resolve().parent
S=P.parents[1]/'games/jcc/set18/18.4/snapshots/20261016T053609Z/data'
def read(p): return json.loads(p.read_text())
def esc(x):return html.escape(str(x))
rank=read(S/'raw/rank.json')['data']; cat=read(S/'raw/catalog.json')['data']; hx=read(P/'hex-stats.json'); dc=read(P/'datatft-catalog.json'); charms=dc['charms18']
selected=[r for r in rank if r['tier'] in ['S','A']]
hexmap={str(x['id']):x for x in cat['hex']}; eq={str(x['id']):x['name'] for x in cat['equip']}
stages={s:sorted([dict(z,name=x['name'],hexId=x['hexId'],quality=hexmap.get(str(x['hexId']),{}).get('level')) for x in hx for z in x['roundStats'] if z['roundLabel']==s],key=lambda z:z['avgPlacement']) for s in ['2-1','3-2','4-2']}
notes={
'99':'三费鸡哥与石甲虫来得顺、装备合适时考虑追三；不要因为榜单领先就在同行很多时强追。',
'104':'先看一费绯红树怪与苍蓝哨戒数量；已经升人口且缺本体时，不回头硬赌一费。',
'107':'一费苍蓝哨戒来得多可进入候选；与小红路线共享野怪卡，但主C装备与追牌投入不同。',
'87':'沃里克、暗影狼等二费卡多且能供给近战装备时考虑；无本体不因前四率高而强玩。',
'115':'阿卡丽、卡蜜尔等一费多，且近战装备合适时考虑。',
'110':'低费韦鲁斯来牌与射手装同时匹配时考虑；271条样本，仍需观察。',
'100':'148条样本，只作候选，不因为均名漂亮当成最稳答案。',
'114':'仅57条样本，评级可信度有限；先满足羁绊条件。',
'112':'九五阵容需要血量、经济和高费质量支持；成型样本表现不代表强行上9的收益。',
'113':'九五是经济好时的上限方向，不能当低血量救命公式。',
'89':'先稳定当前棋盘，再评估上9；数据不能证明从任意开局冲9都强。',
'105':'月男与森林牌、装备及羁绊门槛同时匹配时考虑，勿把所有物理装备局都锁成月男。',
'106':'根据女警数量、前排质量和装备选择；与重装分支比较后再投入追牌。',
'116':'螳螂来牌及近战装备匹配时考虑；裁决是候选方向，不因旧版攻略就提前锁定。'}
plans=[('2阶段：保经济或保连胜',[
('休战','免费补经济，且不占用本回合更重要的战力选择时拿。'),('找个朋友','已有连胜、缺前排时优先看；词库有连胜出现条件。'),('树皮护甲','保连胜、预计战斗前段能分胜负时有用。'),('有丝分裂','补关键一费对子或追三；不要为复制器强行赌牌。'),('肥料','预计能击杀多个敌人且走升级路线时考虑；追一费不盲拿经验。')]),
('3阶段：补即时质量与搜牌效率',[
('巨大化','前排扛不住时，低成本补坦度。'),('石化术','围绕第一名阵亡前排安排站位，给后排争取时间。'),('蜂鸟','攻速收益能给到主C时选。'),('星落','本来就要D牌且有钱买卡时用；为仙灵额外乱D会亏。'),('搜查队','3-5之后找四费过渡/核心，买到第一张即结束效果。'),('衣衫褴褛','3-5之后补缺少的破甲/破魔。'),('日炎巫术','3-5之后针对回复阵容；已有稳定重伤不重复投资。')]),
('4阶段：稳血优先，按缺口购买',[
('余震','4-2之后，前排能撑到8秒时的群控选择。'),('约德尔之灵','4-2之后，针对依赖普攻的对手；不能当万能免伤。'),('鬼鬼祟祟','4-2之后近战核心切入/存活工具；两来源对目标数和强化目标存在差异。'),('回归的好友','D完钱少、缺前排时看免费假人；4-1还是4-2开始有来源分歧。'),('树丛铠甲','低金币时补主坦双抗；开始回合有分歧。'),('法力细雨','能撑到8秒且缺启动时考虑；开始回合有分歧。'),('顺流而下','上回合上场目标明确、还留有买卡与刷新资金时用。'),('活体商店','预留买卡钱且操作时间充足才买；低血量不为刷商店放弃即时战力。')]),
('5阶段：针对对手补战力',[
('地动山摇','拉长战斗时反复控制；两词库费用不同，按商店实际价格判断。'),('余震','便宜的群控候选；确保能等到触发。'),('约德尔之灵','到5-7仍可作为对抗普攻输出的选择。'),('射手标记','射手承担主要输出时考虑。'),('折磨','缺重伤和双破抗时补齐功能；已有相同效果则收益下降。'),('幻影纹章','确实能跨过关键羁绊档位时选，先检查谁携带。')]),
('6阶段及以后：只看下一场能否赢',[
('英雄登场','备战席最左放能改变战局的强卡，考虑8秒入场延迟；两词库价格不同。'),('自然之怒','双边所有未带装备单位都会被击杀；先检查自身挂件损失与出现条件。'),('地动山摇','长战斗持续群控。'),('余震','低成本控场。')])]
# Save structured evidence, preserving disagreements rather than merging silently.
bundle={'retrieved_date':'2026-10-16','platform':'jcc','patch':'18.4','rank':rank,'hex_by_round':stages,'charms_datatft':charms,'charms_dataj':cat['adventure'],'source_notes':['阵容与海克斯为DataJ 18.4统计；来源版本总样本19960，段位和时间窗接口未明确。','仙灵为当前下载的赛季词库，无逐阶段胜率；DataTFT tier为数据字段，不用作强度评级。','DataJ部分仙灵和强化效果尚未同步18.4；不将赛季词库日期等同补丁版本。','公告转载新增免费仙灵从4-1出现，DataTFT标4-2；不合并为已证实回合。','DataJ与DataTFT的后排之星、地动山摇、英雄登场等价格及鬼鬼祟祟目标存在差异，现场以游戏内为准。'],'recommendations_basis':'对来源机制的实战推断，不是因果效果或胜率榜'}
(P/'research-data.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2))
parts=['''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>18.4 金铲铲实战候选 · 2026-10-16</title><style>body{margin:0;background:#101924;color:#e5edf6;font:16px/1.65 system-ui}main{max-width:1120px;margin:auto;padding:30px 20px}h1{font-size:32px}h2{margin-top:40px;color:#78dfcb}h3{color:#bdd6ff}a{color:#8ccaff}p.note{background:#29313d;padding:16px;border-left:4px solid #e3b967}table{width:100%;border-collapse:collapse;font-size:14px}td,th{text-align:left;padding:9px;border-bottom:1px solid #344454;vertical-align:top}.scroll{overflow:auto}details{background:#182534;border:1px solid #314659;padding:12px;margin:10px 0;border-radius:10px}summary{cursor:pointer;font-weight:700}input{padding:12px;width:min(90%,560px);background:#233247;color:white;border:1px solid #60758f;border-radius:8px}.muted{color:#b2c0d0}nav{display:flex;gap:20px;flex-wrap:wrap}li{margin:8px 0}</style><main><p class="muted">金铲铲国服 · 自然之力 · 18.4 · 抓取 2026-10-16</p><h1>按来牌选择，按局势买仙灵</h1><p>38套完整榜单 · 14套S/A详情 · 234项有统计海克斯 · 181项DataTFT仙灵记录</p><nav><a href="#comps">强势阵容</a><a href="#hex">分阶段海克斯</a><a href="#wisp">各阶段仙灵</a><a href="#evidence">来源与缺口</a></nav><p class="note">18.4刚更新：来源版本总样本19,960，许多阵容只有数百条。评级与均名是已发生对局的表现，不等于任意开局强玩收益。以下“何时选”均为实战建议；仙灵没有可验证的逐阶段胜率榜。</p><h2>先用三个问题决定下一步</h2><ol><li>当前两星牌和可合成装备能否稳住？能就保留两三个终局候选；不能先补即时质量。</li><li>追牌投入之前，看本体数量、同行、血量和装备。已大量投入追三后，转阵有实际成本。</li><li>买仙灵后是否还够升级、D牌和买目标卡？缺血优先当回合战力；经济仙灵只在能兑现时拿。</li></ol><h2 id="comps">14套S/A：全部保留，低样本单独提示</h2>''']
def table(headers,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
parts.append(table(['阵容','评级','均名','前四','登顶','样本'],[[f'<a href="https://www.dataj.cc/comp/{r["compId"]}">{esc(r["name"])}</a>',r['tier'],r['avgPlacement'],str(r['top4Rate'])+'%',str(r['topRate'])+'%',str(r['sampleCount'])+(' · 低样本' if r['sampleCount']<1000 else '')] for r in selected]))
for r in selected:
 cid=r['compId'];d=read(S/f'raw/comps/{cid}/detail.json')['data']; rec=read(S/f'raw/comps/{cid}/recommended-hexes.json')['data'].get('hexes',[])
 rows=[]
 for h in d['heroes']:
  items=[eq.get(str(e['equipId']),str(e['equipId'])) for e in d.get('equips',[]) if str(e['heroId'])==str(h['heroId'])]
  rows.append([esc(h['heroName']),h['price'],str(h.get('heroStarNum') or '未标'),esc('、'.join(items) or '—')])
 parts.append(f'<details><summary>{esc(r["name"])} · {r["sampleCount"]}条样本</summary><p>{notes[cid]}</p>'+table(['来源示例棋子','费用','目标星级','来源装备'],rows)+'<p>来源推荐海克斯（选择频次，不是效果排名）：'+esc('、'.join(x['name'] for x in rec))+'</p><p class="muted">棋子列表是来源终局示例，不要求过渡期照抄；转职及人口需求请同时核对来源详情。</p></details>')
parts.append('<h2 id="hex">海克斯：按选择阶段比较</h2><p>下表每阶段取样本≥200中均名靠前的8项，白银/黄金/棱彩分别标注，不能视为同一轮可互换选项。完整234项与所有阶段记录保留在下方；未达200不代表弱。</p>')
for stage,rows in stages.items():
 parts.append('<h3>'+stage+'</h3>'+table(['名称','品质','均名','前四','该阶段样本'],[[esc(x['name']),{1:'白银',2:'黄金',3:'棱彩'}.get(x['quality'],'待核'),x['avgPlacement'],str(x['top4Rate'])+'%',x['sampleCount']] for x in rows if x['sampleCount']>=200][:8]))
parts.append('<p class="note">欧米茄之怪适合野怪体系；宝宝学院偏向一费阵容；金鳞精粹需要经济装备的兑现时间。纵深看实际共享羁绊的单位数量；飞升与灵魂唤醒需要队伍存活到触发时间。别再错过适合补一费本体，不能当通用战力。海克斯效果词库存在旧值，表中排名只取18.4统计。</p><details><summary>完整海克斯分阶段统计</summary>'+table(['名称','阶段','品质','均名','前四','样本'],[[esc(x['name']),s,{1:'白银',2:'黄金',3:'棱彩'}.get(x['quality'],'待核'),x['avgPlacement'],str(x['top4Rate'])+'%',x['sampleCount']] for s,rows in stages.items() for x in rows])+'</details><h2 id="wisp">各阶段仙灵：按用途选，不设无条件必拿</h2><p>以下为机制推断。名称、时间窗、前置条件来自当前DataTFT词库；两来源及公告冲突处明确提示。普通版与莲华强化版不可混用。</p>')
cm={x['title']:x for x in charms}
for title,entries in plans:
 parts.append('<h3>'+title+'</h3>')
 for name,why in entries:
  x=cm[name]
  parts.append(f'<details open><summary>{esc(name)} · {x["cost"]}金币（DataTFT词库）</summary><p>{esc(why)}</p><p>普通版：{esc(x["effect"])}</p><p class="muted">词库出现窗口：{esc("、".join(x.get("rounds",[])))}；前置：{esc("；".join(x.get("requires",[])) or "来源未列出额外条件")}。</p></details>')
parts.append('<h3>完整仙灵词库 · 181项</h3><p>保留来源原文，不把其中tier当作强势评级。部分字段尚有平台/补丁差异。</p><input id="search" placeholder="搜索仙灵、效果或出现条件"><div id="allcharms">')
for x in charms:
 parts.append('<details><summary>'+esc(x['title'])+' · '+str(x['cost'])+'金币</summary><p>'+esc(x['effect'])+'</p><p>回合：'+esc('、'.join(x.get('rounds',[])))+'</p><p>条件：'+esc('；'.join(x.get('requires',[])) or '未列出')+'</p><p>莲华强化：'+esc(str(x.get('upgrade',{})))+'</p></details>')
parts.append('''</div><h2 id="evidence">来源与覆盖</h2><ul><li><a href="https://www.dataj.cc/comp">DataJ阵容榜</a>：38套，10套S、4套A；216项请求成功，0失败。完整快照保留各阵容装备、强化、过渡等原始数据。</li><li><a href="https://www.dataj.cc/hex">DataJ海克斯页</a>：18.4服务器内嵌234项统计；与词库268项不同，不宣称每个强化都有统计。部分总样本与各阶段合计不一致，保留原值。</li><li><a href="https://jcc.datatft.com/">DataTFT当前金铲铲站</a>：181项仙灵，包含前置条件及强化版；这是当前发布的赛季词库，并非带补丁过滤的胜率接口。</li><li><a href="https://www.taptap.cn/moment/859501804386257393?group_id=213275">18.4官方公告入口</a>；<a href="https://app.ali213.net/news/226461.html">公告文字转载</a>用于核对新增仙灵及变化。</li><li>DataJ仙灵词库170项，仍有旧数值；DataTFT的后排之星、地动山摇、英雄登场价格与之不同。鬼鬼祟祟目标数/强化目标也有差异，不能确认每个字段都适用当前国服。</li><li>新增免费仙灵：公告转载写4-1至5-7，DataTFT写4-2至5-7；DataTFT额外标金币少于10。摸些蘑菇在DataTFT名为蘑菇空间。保留差异，不宣称精确刷新已证实。</li><li>没有仙灵按阶段的样本、均名和胜率；本报告的阶段推荐属于机制判断。来源未给出完整段位、统计时窗与队列过滤条件。</li></ul><p><a href="research-data.json">下载结构化研究数据</a> · <a href="coverage.json">覆盖与校验记录</a></p></main><script>document.getElementById('search').addEventListener('input',e=>{const q=e.target.value.trim().toLowerCase();for(const d of document.querySelectorAll('#allcharms details'))d.hidden=!d.textContent.toLowerCase().includes(q)})</script></html>''')
(P/'index.html').write_text(''.join(parts))
coverage={'platform':'jcc','patch':'18.4','date':'2026-10-16','rank_count':len(rank),'selected_count':len(selected),'hex_statistics_count':len(hx),'hex_catalog_count':len(cat['hex']),'charm_datatft_count':len(charms),'charm_dataj_count':len(cat['adventure']),'snapshot':str(S),'sources':[{'url':'https://www.dataj.cc/hex','file':'hex-page.html'},{'url':'https://jcc.datatft.com/assets/h5-data-cn-18-EaDL5Kor.json','file':'datatft-catalog.json'}],'gaps':bundle['source_notes']}
for item in coverage['sources']:item['sha256']=hashlib.sha256((P/item['file']).read_bytes()).hexdigest()
(P/'coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in coverage.items() if k.endswith('count')},ensure_ascii=False))
