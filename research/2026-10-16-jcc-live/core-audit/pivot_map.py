from html import escape as E
# Compact arrow annotations, keyed to the detailed routes; full rosters come from their audit.
LABELS={
1:'人马＋蜘蛛＋大蓝质量胜过主宰前排',2:'河蟹＋瑟庄妮＋阿木木先两星',
3:'鸡哥＋大红＋大蓝齐，迅射转到手',4:'人马＋莉莉娅等森林壳质量更高',
5:'女警未三，鸡哥两星＋野怪壳齐',6:'女警少、鸡哥顺；备齐整套野怪壳',7:'仅早期：女警多、主宰前排先两星',
8:'小蓝多＋法棒眼泪多，尚未锁装',9:'小红多＋物理散件顺，尚未锁装',
10:'小红未三，鸡哥两星＋另有攻速套',11:'小蓝未三，鸡哥两星＋另有物理套',
12:'可上9，巨龙＋德莱文及高费前排到',13:'可上9，拉露恩＋巨龙＋重装壳到',14:'可上9，巨龙到且另有副C攻速套',
15:'德莱文成型＋新高费壳更强；另有攻速套',16:'拉露恩＋纳尔先两星；另有法装',
17:'韦鲁斯未三，月男两星＋森林壳齐',18:'可上9，火转＋艾希＋凯南到',
19:'韦鲁斯多、日蚀牌顺，未深追近战',20:'仅早期：近战低费多＋宝宝学院',
21:'狼人未三，鸡哥＋野怪壳齐；另有射手装',22:'螳螂未深追，月男两星＋物理套＋森转',
23:'仅未锁定：螳螂多且裁决进化，近战法装齐'}
GROUPS=[
('same','同主C｜优先比较前排质量','女警：三件装备完全保留。月男：海妖/无尽共用，已有鬼索可留；两种纹章不能互换。',[1,2,3,4]),
('items','共用整套／部分装备｜换C前先接好装备','女警⇄鸡哥：锐利＋海妖＋鬼索全共用。鸡哥→德莱文共用鬼索/海妖；小红→巨龙共用无尽/轻语；其余只部分共用。',[5,6,7,12,14,17,18,19,20]),
('late','九五双C分配｜巨龙保留或接管','古纳拉⇄巨龙95保留巨龙；拉露恩与德莱文不共用输出套。小蓝→古纳拉只共用部分法装，巨龙另需物理装。',[13,15,16]),
('shell','仅共用阵容壳｜主装不通用，主要是早期分流','小红、小蓝、鸡哥共用野怪；狼人和螳螂只是部分连接牌共用。已追三星或专属机制投入后，通常保C调辅助。',[8,9,10,11,21,22,23])]
SHORT={'厄斐琉斯':'月男','凯特琳':'女警','深红锋喙鸟':'鸡哥','绯红树怪':'小红','苍蓝哨戒':'小蓝','苍蓝雕纹魔像':'大蓝','绯红印记树怪':'大红','峡谷迅捷蟹':'河蟹','远古石甲虫':'石甲虫','远古巨龙':'巨龙','赫卡里姆':'人马','阿利斯塔':'牛头','伊莉丝':'蜘蛛','沃里克':'狼人','伊泽瑞尔':'EZ','崔丝塔娜':'小炮','卡兹克':'螳螂'}
CSS='''
#pivot-map{margin:26px 0 40px}#pivot-map>h2{margin-top:24px}.pm-legend{font-size:14px;color:#526473}.pm-group{margin:24px 0}.pm-group h3{margin:0;padding:10px 14px;background:#e5efeb;border-left:5px solid #176d67}.pm-group>p{margin:8px 0 12px;font-size:14px}.pm-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.pm-edge{min-width:0;background:#fff;padding:14px;border:1px solid #d5dedb;border-radius:8px;break-inside:avoid}.pm-line{display:grid;grid-template-columns:minmax(0,1fr) 48px minmax(0,1fr);align-items:center;gap:8px}.pm-node{font-size:15px;font-weight:650;text-align:center;background:#edf3f1;padding:8px 4px;border-radius:5px;text-decoration:none}.pm-node small{display:block;font-weight:400;font-size:12px}.pm-arrow{position:relative;border-top:2px solid #176d67;height:0}.pm-arrow:after{content:"";position:absolute;right:-1px;top:-6px;border-left:9px solid #176d67;border-top:5px solid transparent;border-bottom:5px solid transparent}.pm-detail{margin-top:10px;border-left:2px solid #b9ccc5;padding-left:10px;font-size:13px;line-height:1.65}.pm-detail p{margin:3px 0}.pm-trigger{font-weight:600}.pm-gate{color:#814e09}.pm-link{display:block;text-align:right;font-size:12px;margin-top:6px}.pm-group.shell .pm-arrow{border-top-style:dashed}.pm-group.shell h3{border-left-color:#8b7550;background:#f1ece2}.pm-group.shell .pm-arrow:after{border-left-color:#8b7550}.pm-group.shell .pm-arrow{border-color:#8b7550}@media(max-width:800px){.pm-grid{grid-template-columns:1fr}}@media print{#pivot-map>h2{break-before:auto}.pm-group h3{break-after:avoid}.pm-grid{display:block}.pm-edge{margin-bottom:10px}.pm-detail{font-size:9pt}}

.pm-jumps{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 18px}.pm-jumps a{display:flex;align-items:center;min-height:44px;padding:7px 12px;border:1px solid #bdcec7;border-radius:6px;background:#fff;text-decoration:none;font-size:14px;font-weight:600}.pm-group{scroll-margin-top:18px}.pm-unit{display:inline-block;white-space:nowrap;margin-right:7px}.pm-detail{font-size:14px;line-height:1.75}.pm-detail p{margin:5px 0}.pm-keep{background:#eff5f2;padding:5px 7px}.pm-row{display:grid;grid-template-columns:40px minmax(0,1fr);gap:3px}.pm-link{font-size:14px;min-height:44px;display:flex;justify-content:flex-end;align-items:center}.pm-back{display:block;text-align:right;min-height:44px;padding:10px 0;font-size:14px}.pm-detail b{white-space:nowrap}#pivot-map>.pm-legend{margin-bottom:8px}.pm-summary{margin:8px 0;color:#59665e;font-size:14px}.pm-gate{font-weight:550}@media(max-width:800px){.pm-detail{font-size:15px}.pm-node{font-size:16px}.pm-line{grid-template-columns:minmax(0,1fr) 32px minmax(0,1fr)}.pm-group h3{font-size:18px}.pm-group>p{font-size:15px}.pm-edge{padding:12px}.pm-jumps{display:grid;grid-template-columns:1fr 1fr}.pm-jumps a{justify-content:center}.pm-detail{padding-left:8px}.pm-summary{font-size:14px}}@media print{.pm-jumps,.pm-back{display:none}.pm-detail{font-size:10pt}.pm-link{min-height:0}}
'''
def render_map(audit,selected):
 names={r['compId']:r['name'] for r in selected};edges={e['id']:e for e in audit['pivots']}
 assert set(LABELS)==set(edges)=={i for _,_,_,ids in GROUPS for i in ids}
 def units(xs):return '、'.join(SHORT.get(x,x) for x in xs) or '无'
 def chips(xs):return ''.join('<span class="pm-unit">'+E(SHORT.get(x,x))+'</span>' for x in xs) or '无'
 out=['<section id="pivot-map" aria-label="阵容互转总览图"><h2>阵容互转｜快速总览</h2><p class="pm-legend">左 → 右读；双向条件分开列。先看同主C，再看装备能否接手。</p><div class="pm-jumps"><a href="#pm-same">① 同主C换前排</a><a href="#pm-items">② 共用装备换C</a><a href="#pm-late">③ 九五双C分配</a><a href="#pm-shell">④ 仅共用阵容壳</a></div><p class="pm-summary">新C和前排到齐再换；已成三星通常留。虚线：主装不通用。名单对应标注人口的示例盘。</p>']

 for cls,title,desc,ids in GROUPS:
  out.append(f'<div class="pm-group {cls}" id="pm-{cls}"><h3>{E(title)}</h3><p>{E(desc)}</p><div class="pm-grid">')
  for i in ids:
   e=edges[i];gate='转职：无额外要求'
   if e['target_emblems']:gate='需：'+'、'.join(units([n])+'携'+{'永恒之森':'永森转','迅捷射手':'迅射转','地狱火':'地狱火转'}[t] for n,t in e['target_emblems'].items())
   if e['to']=='105':gate+='（持有者为推导）'
   if e['to']=='115':gate='必须：宝宝学院；无此强化不继承来源评级'
   if e['target_evolve']:gate='必须：螳螂已进化裁决；不是原生裁决'
   if e['from'] in ['105','114','112']:gate+='；原转职不可变换'
   out.append(f'<article class="pm-edge" id="map-edge{i}"><div class="pm-line"><a class="pm-node" href="#comp{e["from"]}">{E(names[e["from"]])}<small>示例 {e["from_level"]} 人口</small></a><span class="pm-arrow" aria-label="转向"></span><a class="pm-node" href="#comp{e["to"]}">{E(names[e["to"]])}<small>示例 {e["to_level"]} 人口</small></a></div><div class="pm-detail"><p class="pm-trigger">来牌：{E(LABELS[i])}</p><p class="pm-row pm-keep"><b>保留</b><span>{chips(sorted(e["keep"]))}</span></p><p class="pm-row"><b>换下</b><span>{chips(e["remove"])}</span></p><p class="pm-row"><b>补进</b><span>{chips(e["add"])}</span></p><p class="pm-gate">{E(gate)}</p></div><a class="pm-link" href="#pivot{i}">路线 {i} · 装备交接／不转条件 ↗</a></article>')
  out.append('</div><a class="pm-back" href="#pivot-map">↑ 回总览分组</a></div>')
 out.append('<p class="pm-legend">地狱火95是有火转条件的终局，本图保留“转入”箭头，没有硬造转出路线。小红⇄小蓝的“留整盘、无需换牌”表示换装备与追牌优先级，已选阿尔法需核实能否改选。所有箭头为机制推导，不代表转型胜率。</p></section>')
 return ''.join(out)
