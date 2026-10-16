from pathlib import Path
import json,html,datetime
P=Path(__file__).resolve().parent;ROOT=P.parents[1];S=ROOT/'games/jcc/set18/18.4/snapshots/20261016T053609Z/data/raw';OUT=ROOT/'guides/金铲铲18.4版本攻略.html'
def load(p):return json.loads(p.read_text())
def e(x):return html.escape(str(x))
cat=load(S/'catalog.json')['data'];rank=load(S/'rank.json')['data'];eq={str(x['id']):x['name'] for x in cat['equip']};hexmap={str(x['id']):x for x in cat['hex']};stats=load(P/'hex-stats.json');wisps={x['title']:x for x in load(P/'datatft-catalog.json')['charms18']}
def table(headers,rows):return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def para(s):return '<p>'+s+'</p>'
def box(s):return '<p class="note">'+s+'</p>'
# Every board is an explicit proposed operating example, not a claimed best observed lineup.
R={
'野怪鸡哥':{3:['绯红树怪','苍蓝哨戒','峡谷迅捷蟹'],4:['绯红树怪','苍蓝哨戒','峡谷迅捷蟹','约里克'],5:['绯红树怪','苍蓝哨戒','峡谷迅捷蟹','远古石甲虫','暗影狼'],6:['绯红树怪','苍蓝哨戒','峡谷迅捷蟹','远古石甲虫','暗影狼','深红锋喙鸟'],7:['苍蓝哨戒','峡谷迅捷蟹','暗影狼','远古石甲虫','深红锋喙鸟','苍蓝雕纹魔像','绯红印记树怪'],8:['苍蓝哨戒','峡谷迅捷蟹','暗影狼','远古石甲虫','深红锋喙鸟','苍蓝雕纹魔像','绯红印记树怪','瑟提'],9:['苍蓝哨戒','峡谷迅捷蟹','远古石甲虫','深红锋喙鸟','苍蓝雕纹魔像','塔里克','纳尔','远古巨龙']},
'卡丽蜜儿':{3:['奥恩','阿卡丽','韦鲁斯'],4:['奥恩','蕾欧娜','阿卡丽','韦鲁斯'],5:['奥恩','蕾欧娜','卡蜜尔','阿卡丽','韦鲁斯'],6:['奥恩','蕾欧娜','卡蜜尔','阿卡丽','韦鲁斯','凯尔'],7:['奥恩','蕾欧娜','卡蜜尔','阿卡丽','韦鲁斯','凯尔','瑟庄妮'],8:['奥恩','蕾欧娜','卡蜜尔','阿卡丽','韦鲁斯','凯尔','瑟庄妮','阿木木'],9:['奥恩','蕾欧娜','卡蜜尔','阿卡丽','韦鲁斯','凯尔','瑟庄妮','阿木木','艾翁']},
'狼人':{4:['雷克塞','阿利斯塔','暗影狼','沃里克'],5:['雷克塞','阿利斯塔','暗影狼','沃里克','卡蜜尔'],6:['雷克塞','阿利斯塔','暗影狼','沃里克','卡蜜尔','黛安娜'],7:['雷克塞','阿利斯塔','暗影狼','沃里克','黛安娜','苍蓝雕纹魔像','绯红印记树怪'],8:['雷克塞','阿利斯塔','暗影狼','沃里克','黛安娜','苍蓝雕纹魔像','绯红印记树怪','卡兹克']},
'主宰女警':{6:['洛','绯红树怪','峡谷迅捷蟹','瑟庄妮','凯特琳','蔚'],7:['洛','绯红树怪','峡谷迅捷蟹','瑟庄妮','凯特琳','蔚','希维尔'],8:['洛','峡谷迅捷蟹','瑟庄妮','约里克','凯特琳','蔚','阿木木','希维尔'],9:['洛','峡谷迅捷蟹','瑟庄妮','约里克','凯特琳','蔚','阿木木','希维尔','艾翁']},
'射箭韦鲁斯':{5:['蕾欧娜','韦鲁斯','瑟庄妮','慎','凯尔'],6:['蕾欧娜','韦鲁斯','瑟庄妮','慎','凯尔','黛安娜'],7:['蕾欧娜','韦鲁斯','瑟庄妮','慎','凯尔','黛安娜','厄斐琉斯'],8:['蕾欧娜','韦鲁斯','瑟庄妮','慎','凯尔','黛安娜','厄斐琉斯','拉露恩']},
'裁决螳螂':{7:['奥恩','赫卡里姆','费德提克','卡兹克','黛安娜','伊泽瑞尔','索拉卡'],8:['奥恩','赫卡里姆','费德提克','卡兹克','黛安娜','伊泽瑞尔','索拉卡','凯南']},
'森林月男':{5:['奥恩','蕾欧娜','霞','乐芙兰','凯尔'],6:['奥恩','蕾欧娜','霞','乐芙兰','凯尔','瑟庄妮'],7:['奥恩','蕾欧娜','霞','乐芙兰','凯尔','瑟庄妮','赫卡里姆'],8:['奥恩','霞','阿利斯塔','赫卡里姆','莉莉娅','伊泽瑞尔','厄斐琉斯','纳尔'],9:['奥恩','霞','阿利斯塔','赫卡里姆','莉莉娅','伊泽瑞尔','厄斐琉斯','纳尔','凯南']}}
for name,levels in R.items():
 for lv,board in levels.items():assert len(set(board))==len(board) and sum(2 if x=='远古巨龙' else 1 for x in board)==lv,(name,lv)
intro={3:('只搭底盘，不为一星牌锁阵容','3人口没有独立强度统计，下列是从4人口底盘归纳的开局。优先现成两星输出与能扛的前排；2-1是否升4看质量与经济。'),4:('野怪优先观察，近战盘看两星质量','野怪＋约里克/洛有较好的4人口来源表现。卡丽蜜儿与狼人并非全一星就能统治前期，别把终局评级当开局战力。'),5:('决定一费追三，或继续升级','护卫地狱火全两星有较强样本；野怪应补石甲虫与实际质量。只有本体、装备、同行和血量同时支持时才投入一费追三。'),6:('狼人、女警发力，运营路线补质量','狼人核心两星后的中期表现突出；女警是物理打工与二费追三候选。三费路线在此以稳血为主，不盲目追所有低费三星。'),7:('三费追三与上8运营分流','鸡哥、螳螂路线按本体数量决定是否追三；已成型的一二费核心继续保留。部分7人口来源样本是最终停留棋盘，不能用其均名衡量3阶段即时强度。'),8:('补齐四费前排，保留已成型核心','优先让装备携带者与主坦到位。新四费只有一星时，不自动比现有两星或三星强。上9前先确保下一轮不会大幅掉血。'),9:('顺着现有体系提高上限','野怪可以接巨龙，低费阵容可只补功能五费。九五需要经济、高费来牌与可承受的换阵时间；上9不等于必须拆掉整盘。')}
quality={'野怪鸡哥':'前期小红/小蓝两星；中期鸡哥、石甲虫两星起步，来牌顺再追三；四费前排补两星。','卡丽蜜儿':'5人口先争取核心两星；主C阿卡丽/卡蜜尔按装备与本体选重点，奥恩补坦度。来源终局含多张三星，不应要求每局全追。','狼人':'6人口沃里克、牛头、暗影狼两星是发力基础；走终局再追沃里克及关键前排三星。','主宰女警':'女警与河蟹、瑟庄妮两星先稳血；走赌阵时优先女警三星，前排根据数量追。','射箭韦鲁斯':'韦鲁斯三星是主要目标；慎、瑟庄妮、凯尔按本体追，不必等全三星才升级。','裁决螳螂':'螳螂两星先稳血，终局通常依赖三星；人马是前排重点。','森林月男':'前期霞/妖姬两星打工；后期月男与莉莉娅质量到位再换，不追与运营方向冲突的低费三星。'}
ids={'野怪鸡哥':'99','卡丽蜜儿':'115','狼人':'87','主宰女警':'106','射箭韦鲁斯':'110','裁决螳螂':'116','森林月男':'105'}
gear={
'野怪鸡哥':'鸡哥：鬼索的狂暴之刃＋海妖之怒＋锐利之刃；石甲虫：狂徒铠甲＋石像鬼石板甲＋振奋盔甲。前期物理装由小红临时携带属于打工建议，不代表小红终局最佳配装。',
'卡丽蜜儿':'阿卡丽：夜之锋刃＋珠光护手＋正义之手；卡蜜尔：无尽之刃＋斯特拉克的挑战护手＋水银；奥恩：振奋盔甲＋石像鬼石板甲＋狂徒铠甲。先装备一个主C与一个主坦，再补副C。',
'狼人':'沃里克：水银＋汲取剑＋无尽之刃；牛头：石像鬼石板甲＋薄暮法袍＋狂徒铠甲。狼人未到场时可临时交给适配近战打工牌，转交需要卖牌或已有拆卸工具。',
'主宰女警':'凯特琳：锐利之刃＋海妖之怒＋鬼索的狂暴之刃；河蟹：狂徒铠甲＋石像鬼石板甲＋振奋盔甲；希维尔补最后的轻语、朔极之矛等功能输出。',
'射箭韦鲁斯':'韦鲁斯：无尽之刃＋朔极之矛＋锐利之刃；凯尔：鬼索的狂暴之刃＋珠光护手＋巨人捕手；瑟庄妮：振奋盔甲＋石像鬼石板甲＋狂徒铠甲。',
'裁决螳螂':'螳螂来源示例：夜之锋刃＋班克斯的魔法帽＋正义之手；词库将班克斯的魔法帽列为两根无用大棒合成的成型装备。先满足生存、续航与输出缺口，替代三件套强度本次未逐项核验。人马：振奋盔甲＋石像鬼石板甲＋狂徒铠甲。',
'森林月男':'厄斐琉斯：海妖之怒＋鬼索的狂暴之刃＋无尽之刃；莉莉娅：狂徒铠甲＋石像鬼石板甲＋圣盾使的誓约。前期霞临时拿物理装备，待月男质量就位后通过卖打工卡/已有拆卸工具转移；要保留森林霞时预留替补霞。'}
hexnotes={'野怪鸡哥':'欧米茄之怪：野怪体系；纵深Ⅰ/Ⅱ/Ⅲ：看共享羁绊单位；飞升：前排能撑到触发；加冕礼：额外人口与质量空间。','卡丽蜜儿':'宝宝学院：2-1且决定低费路线时；别再错过：3-2/4-2补一费本体，接近追三时更有意义；装备类补主C缺口。','狼人':'挑战者的优雅、便携锻炉：看实际装备适配；团队建设：补追牌资源。不要因为拿到锻炉就无视来牌硬玩狼人。','主宰女警':'飞升、双城赢家、大百宝袋是来源推荐候选；先看前排与装备缺口，不按名称无脑拿。','射箭韦鲁斯':'嘀嘀街区在2-1支持搜牌路线；后续大百宝袋、专属定制按装备需求选。','裁决螳螂':'便携锻炉、团队建设、大百宝袋、飞升在来源推荐中；神器选择需实际适配，不能保证锻炉给到理想装备。','森林月男':'自然庇护所、蔓延之根及其变体属于森林方向候选；飞升、双城赢家用于战力。需要羁绊门槛的强化先核对当前棋盘。'}
levelwisps={3:['休战','找个朋友','有丝分裂'],4:['找个朋友','树皮护甲','休战','有丝分裂'],5:['有丝分裂','星落','巨大化','石化术'],6:['蜂鸟','石化术','星落','衣衫褴褛','日炎巫术','搜查队'],7:['搜查队','顺流而下','余震','约德尔之灵'],8:['余震','约德尔之灵','活体商店','地动山摇','折磨'],9:['地动山摇','折磨','幻影纹章','英雄登场','自然之怒']}
wwhy={'休战':'补经济，先比较本回合是否更需要战力。','找个朋友':'缺前排、想保连胜；词库注明连胜条件。','树皮护甲':'保连胜，战斗前段护盾收益高。','有丝分裂':'补一费关键对子或追三，不能为复制器强行转赌阵。','星落':'本来就要D牌且有钱买牌时使用。','巨大化':'缺前排坦度时的低成本补强。','石化术':'注意第一个阵亡的是谁，让合适的前排先承伤。','蜂鸟':'确认攻速最高单位是希望强化的主C。','衣衫褴褛':'阵容缺破甲/破魔时优先，已有同类效果则收益下降。','日炎巫术':'针对回复；已能稳定施加重伤时减少重复投入。','搜查队':'找四费；买到第一张四费后效果结束。','顺流而下':'上回合上场目标明确，留够刷新与买牌钱。','余震':'要能撑到8秒触发，适合补群控。','约德尔之灵':'针对普攻输出，不等于抵挡一切伤害。','活体商店':'操作时间与买牌资金充足时用；低血量先比较即时战力。','地动山摇':'战斗较长时多次控制，价格两来源不一致。','折磨':'缺重伤、缓速和双破抗时有价值，已有功能避免重复。','幻影纹章':'先检查是否能跨过关键羁绊档位，再决定购买。','英雄登场':'仅6阶段以后候选；提前把有用的强卡放备战席最左，考虑延迟入场。','自然之怒':'仅6阶段以后候选；会处理双方未带装备单位，先核对自身损失与出现条件。'}
parts=['''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>金铲铲18.4版本攻略｜按等级过渡与成型</title><style>
:root{--ink:#233246;--teal:#156d69;--gold:#9d6f19;--line:#d9e0e4}*{box-sizing:border-box}body{margin:0;background:#f7f5ef;color:var(--ink);font:16px/1.8 system-ui,-apple-system,"PingFang SC",sans-serif}main{max-width:1120px;margin:auto;padding:42px 32px 80px}header{border-top:6px solid var(--teal);padding:28px 0}h1{font-size:38px;line-height:1.3;margin:10px 0}h2{font-size:27px;border-bottom:2px solid var(--teal);padding-bottom:10px;margin-top:55px}h3{color:var(--teal);margin:25px 0 10px}a{color:var(--teal)}.eyebrow{font-size:13px;letter-spacing:2px;color:var(--gold)}.lead{font-size:19px;max-width:880px}.note{background:#eee8d8;border-left:4px solid #ad8543;padding:14px 18px}.muted{font-size:14px;color:#5d6b77}nav{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0}nav a{background:#e5edeb;padding:5px 12px;text-decoration:none}.card{background:white;border:1px solid var(--line);padding:18px 22px;margin:18px 0;border-radius:8px}.board{font-weight:650;line-height:2}.tag{font-size:12px;color:var(--gold);font-weight:500;margin-left:10px}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}th{background:#e7eeec}.table-wrap{overflow-x:auto}li{margin:7px 0}.swap{background:#f1f5f5;padding:10px 14px}.source{font-size:13px;color:#5d6b77}footer{margin-top:50px;border-top:1px solid var(--line);padding-top:20px}@media(max-width:650px){main{padding:24px 16px}h1{font-size:29px}.card{padding:14px}td,th{padding:8px}}@media print{body{background:white;font-size:10pt}main{padding:0;max-width:none}nav{display:none}h1{font-size:25pt}h2{font-size:18pt;break-before:page}h3{break-after:avoid}.card{break-inside:avoid}a{color:inherit;text-decoration:none}table{font-size:9pt}header{border-top:0}.note{background:#f1f1f1}.table-wrap{overflow:visible}}
</style></head><body><main><header><div class="eyebrow">金铲铲国服 · 自然之力 · 2026年10月16日资料</div><h1>18.4 版本攻略<br>从开局底盘，到后期成型</h1><p class="lead">按3—9人口查阵容，沿同一条路线看换牌；装备、海克斯与仙灵都围绕当前棋盘的缺口选择。</p></header>''']
parts.append('<nav>'+''.join(f'<a href="#lv{lv}">{lv}人口</a>' for lv in range(3,10))+'<a href="#low">小红/小蓝分支</a><a href="#hex">海克斯回合表</a><a href="#appendix">全S/A装备与强化</a><a href="#sources">来源</a></nav>')
parts.append(box('本攻略固定使用18.4快照。来源版本统计19,960局；38套阵容中10套S、4套A。4—6人口数据是棋盘胜率，7—9人口多为终局样本；不把不同回合、装备与海克斯下的数据混成统一等级榜。阵容与装备来自来源示例；逐级换牌、装备优先级、仙灵用途为运营建议。'))
parts.append('<h2>本版先练哪些路线</h2>'+table(['路线','适合的来牌/装备','投入等级','升级目标'],[
['野怪鸡哥','野怪开局、攻速物理装、鸡哥/石甲虫来得顺','7级评估三费追三','8级四费野怪，9级巨龙'],['野怪小红/小蓝','一费本体多，分别匹配技能物理/法系装备','5级评估一费追三','保留三星主C补高费野怪'],['卡丽蜜儿/射箭韦鲁斯','一费两星多，近战/射手装备方向清晰','5级追主C；二费配套另看数量','6—8级补羁绊与坦度'],['狼人/主宰女警','二费本体顺，分别匹配近战/攻速物理装备','6级评估二费追三','7—8级补四费副C和前排'],['森林月男','森林过渡顺，物理装备、经济足','8级找四费质量','9级补高费功能'],['裁决螳螂','三费本体顺，近战装备合适','7级评估三费追三','8级补质量与前排']]))
parts.append(para('前期物理打工盘在本次候选中选择较多；法系来牌可关注小蓝与森林打工，但不能因此断言全版本物理普遍胜过法系。低费追三路线有清晰发力点，九五则依赖资源。建议一费在5级、二费在6级、三费在7级评估追三；这是搜牌建议，不是来源统计给出的固定最优回合。'))
parts.append(box('海克斯按2-1、3-2、4-2出现，仙灵按回合及条件出现，都不由等级直接决定。下方每级的仙灵表列明时间窗：停5级到4阶段时，应看4阶段仙灵，不能沿用2阶段清单。'))
for lv in range(3,10):
 title,desc=intro[lv];parts.append(f'<section id="lv{lv}"><h2>{lv}人口｜{title}</h2><p>{desc}</p>')
 for name,levels in R.items():
  if lv not in levels:continue
  board=levels[lv];prev=levels.get(lv-1)
  if prev:
   keep=[x for x in board if x in prev];off=[x for x in prev if x not in board];on=[x for x in board if x not in prev]
   swap=f'<b>从{lv-1}级过渡：</b>保留{e("、".join(keep))}；换下{e("、".join(off) or "无")}；补进{e("、".join(on) or "无")}。'
  else:swap='<b>进入这条路线：</b>这是本攻略此路线的首个完整棋盘，不代表必须从上一条阵容整套换入；先保留已有两星前排和装备携带者，再补齐核心。'
  if name=='野怪鸡哥' and lv==7:swap+=' 若小红已三星或是主要装备携带者，不按此表卖掉，转看小红/小蓝分支；若大蓝大红仍一星且场面变弱，暂缓替换。'
  if name=='野怪鸡哥' and lv==9:swap+=' 巨龙占2人口，此次是换下3张、加入4人口，不是逐张一对一替换。巨龙未到时保留8级盘加功能前排。'
  if name=='森林月男' and lv==8:swap+=' 这是整组换阵：月男与莉莉娅至少具备可接班的质量、装备能转交时再执行；纳尔未到可暂留乐芙兰，但不声称羁绊完全等价。'
  if name=='狼人' and lv==7:swap+=' 若大蓝、大红未到或只有一星导致战力下降，先保留卡蜜尔，再补一张有用战力牌。'
  parts.append(f'<article class="card"><h3>{name}<span class="tag">运营示例 · 非唯一最优棋盘</span></h3><p class="board">{e(" ＋ ".join(board))}</p><p class="swap">{swap}</p><p><b>质量门槛：</b>{quality[name]}</p><p><b>核心装备：</b>{gear[name]}</p><p><b>海克斯方向：</b>{hexnotes[name]} 出现回合见文末核对表。</p></article>')
 if lv==9:parts.append('<article class="card"><h3>巨龙九五｜资源好时的另一终局</h3><p class="board">苍蓝雕纹魔像＋阿木木＋茂凯＋塔里克＋凯南＋德莱文＋艾翁＋远古巨龙（8单位，9人口）</p><p>若从上方9级野怪盘改成这盘：保留大蓝、塔里克、巨龙；换下小蓝、河蟹、石甲虫、鸡哥、纳尔；加入阿木木、茂凯、凯南、德莱文、艾翁。<b>这是大幅换阵，不推荐为了照表卖掉三星鸡哥或石甲虫</b>；只有新牌与装备分配实际更强时才执行。</p><p>巨龙来源装备：无尽之刃＋强袭者的链枷＋最后的轻语；德莱文：鬼索的狂暴之刃＋海妖之怒＋海妖之怒；茂凯：狂徒铠甲＋石像鬼石板甲＋振奋盔甲。重复装备是来源示例，不是要求强等两件。</p><p>升级咯！与金鳞精粹属于2-1就开始规划的经济候选，不是到了9级才选择。后期优先已获得的战力与装备收益。</p></article>')
 wr=[]
 for name in levelwisps[lv]:
  w=wisps[name];wr.append([e(name),e('；'.join(w.get('rounds',[]))),e(wwhy[name]),e('；'.join(w.get('requires',[])) or '词库未列额外条件')])
 parts.append('<h3>这个等级常见局势下的仙灵候选</h3>'+table(['仙灵','词库出现回合','何时选','额外前置'],wr))
 parts.append('</section>')
parts.append('''<section id="low"><h2>野怪小红／小蓝：不要把成熟一费核心误卖给鸡哥</h2><p>小红：无尽之刃＋朔极之矛＋最后的轻语。小蓝：珠光护手＋大天使之杖＋大天使之杖。石甲虫：狂徒铠甲＋石像鬼石板甲＋振奋盔甲。双大天使是来源配装示例，不代表必须扣装备等第二件。</p><p>两条路线共享4—5级野怪底盘；根据一费数量与装备选择主C。本体不顺就保留两星打工并升级，投入追三后不再当作能无成本摇摆。</p>''')
low={5:['绯红树怪','苍蓝哨戒','峡谷迅捷蟹','暗影狼','远古石甲虫'],6:['绯红树怪','苍蓝哨戒','峡谷迅捷蟹','暗影狼','远古石甲虫','魔沼蛙'],7:['绯红树怪','苍蓝哨戒','峡谷迅捷蟹','魔沼蛙','远古石甲虫','深红锋喙鸟','苍蓝雕纹魔像'],8:['绯红树怪','苍蓝哨戒','峡谷迅捷蟹','远古石甲虫','苍蓝雕纹魔像','瑟提','远古巨龙'],9:['绯红树怪','苍蓝哨戒','峡谷迅捷蟹','远古石甲虫','苍蓝雕纹魔像','纳尔','塔里克','远古巨龙']}
rows=[]
for lv,b in low.items():
 assert sum(2 if x=='远古巨龙' else 1 for x in b)==lv
 prev=low.get(lv-1);change='沿用5级野怪底盘，先决定追一费还是升级' if not prev else '换下：'+('、'.join(x for x in prev if x not in b) or '无')+'；补进：'+'、'.join(x for x in b if x not in prev)
 rows.append([lv,e('、'.join(b)),e(change)])
parts.append(table(['等级','完整示例','具体变化'],rows)+box('8级巨龙没来，不要先卖魔沼蛙和鸡哥腾格；继续使用7级底盘补一张强牌。只玩小蓝时，小红未追三可以作为后续替换位置；小红已成主C时必须保留其装备和质量。')+para('海克斯：欧米茄之怪、纵深系列、飞升是来源推荐方向；小蓝还可关注炽天使之拥、更要命的帽子。仙灵：前期有丝分裂，3阶段星落，4阶段顺流而下；前排薄时石化术/余震比继续贪牌更直接。所有仙灵以实际回合和出现条件为准。')+'</section>')
parts.append('<section id="hex"><h2>海克斯回合速查：和人口分开看</h2><p>品质由赛季词库映射，回合按18.4页面实际列出的阶段；同名带“+”的变体不能互换。选取理由是机制建议，来源阵容推荐频次不是强化胜率。</p>')
focus={'欧米茄之怪':'野怪成形时选，不为了它临时丢掉更强棋盘。','宝宝学院':'一费路线且能持续利用成长。','嘀嘀街区':'明确搜牌路线；不要拿了却一直存钱不利用。','便携锻炉':'看实际神器与当前携带者适配。','金鳞精粹':'有时间兑现经济装备，适合健康运营。','升级咯！':'计划升级运营，和长期卡等级追低费的方案冲突。','团队建设':'追牌资源能补到关键质量时。','别再错过':'还需要一费本体时，已成型后价值下降。','挑战者的优雅':'狼人来源推荐，结合实际装备与场面。','纵深 I':'共享羁绊的单位足够时。','纵深 II':'共享羁绊的单位足够时。','纵深 III':'共享羁绊的单位足够时。','飞升':'前排可以撑到触发。','大百宝袋':'即时补装备缺口。'}
hr=[]
for x in stats:
 if x['name'] in focus:hr.append([e(x['name']),{1:'白银',2:'黄金',3:'棱彩'}.get(hexmap.get(str(x['hexId']),{}).get('level'),'待核'),e(' / '.join(x['rounds'])),e(focus[x['name']])])
parts.append(table(['强化','品质','来源出现回合','选取条件'],hr))
parts.append(box('特别纠正：别再错过在本次18.4页面列为3-2／4-2，不能把它写成2-1开局选择。宝宝学院、嘀嘀街区、升级咯！、金鳞精粹列为2-1。'))
parts.append('<h3>新增免费仙灵的处理</h3><p>法力细雨、树丛铠甲、回归的好友可分别补回蓝、主坦双抗与前排。公告转载写4-1开始，DataTFT词库写4-2开始并标金币少于10；因此不把精确起始回合写成已证实。看到时按当前缺口选择，不为刷它们主动把经济压空。鬼鬼祟祟的目标与强化效果、部分仙灵价格也存在来源差异，攻略不据此安排必须成功的操作。</p></section>')
parts.append('<section id="appendix"><h2>当期全部14套S/A：终局装备与海克斯附录</h2><p>以下完整保留入选阵容，便于查看低样本或特殊条件路线。评级照录来源；普通装备、特殊装备和重复装备按来源原名保留。每套最多10项推荐海克斯是接口返回范围，不是游戏内全部适配强化。</p>')
for r in rank:
 if r['tier'] not in ['S','A']:continue
 cid=r['compId'];d=load(S/f'comps/{cid}/detail.json')['data'];rec=load(S/f'comps/{cid}/recommended-hexes.json')['data'].get('hexes',[])
 parts.append(f'<article class="card"><h3>{e(r["name"])} · {r["tier"]}</h3><p class="muted">均名{r["avgPlacement"]}｜前四{r["top4Rate"]}%｜样本{r["sampleCount"]}'+('｜不足1000，谨慎外推' if r['sampleCount']<1000 else '')+'</p>')
 er=[]
 for h in d['heroes']:
  items=[eq.get(str(x['equipId']),str(x['equipId'])) for x in d.get('equips',[]) if str(x['heroId'])==str(h['heroId'])]
  if items:er.append([e(h['heroName']),h.get('heroStarNum') or '未标',e('＋'.join(items))])
 parts.append(table(['携带者','来源目标星级','来源配装'],er))
 parts.append('<p><b>海克斯：</b>'+e('、'.join(x['name'] for x in rec))+'</p>')
 if cid in ['100','114']:parts.append(para('该路线样本较少，附录保留来源候选；本次不将其扩写成经过验证的全等级优先路线。'))
 parts.append(f'<p class="source"><a href="https://www.dataj.cc/comp/{cid}">查看此阵容来源</a></p></article>')
parts.append('''</section><section id="sources"><h2>使用边界与来源</h2><ul><li>装备先给能实际发挥作用的两星携带者。凑齐推荐三件套只是目标，不是前期空装备等待的理由；先做合适的一件输出和一件前排装，再补完整配置。</li><li>装备不会因为换阵自动转移：卖掉打工牌、使用已有拆卸工具，或满足具体机制条件后才能转交。要保留的羁绊牌预留替补，不卖成熟三星核心取装备。</li><li>每次换牌先核对保留、换下、补进三组；多换多只表示集合变化，不虚构一一对应关系。巨龙占2个人口。</li><li>等级不等于阶段。4—6级来源胜率没有控制具体回合、装备、海克斯和对手；样本可能是棋盘或战斗记录，不作为独立整局数。未将重复出现在多个终局来源的棋盘样本合并。</li><li>7—9级示例具有成型与生存选择偏差。活到9级的好名次不能证明强上9更好；失败时停7级的样本也不能证明那盘在3阶段一定弱。</li><li>逐级清单为可执行的示例路径，非唯一最优；3级、部分中间补位与跨路线衔接为机制建议。没有足够可比数据来称“各等级全服第一阵容”。</li><li>仙灵来自当前赛季词库，未获取逐阶段胜率。部分价格、目标数与回合有冲突，未验证字段不用于精确收益承诺。</li><li>数据平台固定为金铲铲国服；不将TFT评级和胜率混入。</li></ul><p><a href="https://www.dataj.cc/comp">DataJ 18.4阵容榜</a> · <a href="https://www.dataj.cc/hex">海克斯统计</a> · <a href="https://jcc.datatft.com/">DataTFT仙灵词库</a> · <a href="https://www.taptap.cn/moment/859501804386257393?group_id=213275">18.4官方公告入口</a> · <a href="https://app.ali213.net/news/226461.html">公告文字转载</a></p><p>本地证据：<a href="../research/2026-10-16-jcc-live/coverage.json">采集覆盖</a> · <a href="../research/2026-10-16-jcc-live/transitions/manifest.json">全部38套过渡抓取清单</a> · <a href="../research/2026-10-16-jcc-live/research-data.json">原始研究汇总</a></p></section><footer>金铲铲18.4版本攻略 · 2026-10-16 · 静态阅读版，可使用浏览器打印保存为PDF。</footer></main></body></html>''')
if OUT.exists():OUT.with_name(OUT.stem+'-备份-'+datetime.datetime.now().strftime('%H%M%S')+'.html').write_bytes(OUT.read_bytes())
OUT.write_text(''.join(parts))
(P/'guide-lineups.json').write_text(json.dumps({'routes':R,'low_cost_wilds':low,'basis':'Source-backed examples plus explicitly labeled operational inference'},ensure_ascii=False,indent=2))
print(OUT);print('Boards:',sum(len(x) for x in R.values())+len(low),'S/A appendix:',sum(r['tier'] in ['S','A'] for r in rank),'bytes',OUT.stat().st_size)
