#!/usr/bin/env python3
"""Generate portable guide + assistant from normalized knowledge, with no network at runtime."""
import argparse,collections,html,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
esc=lambda x:html.escape(str(x))
def render(snapshot,out,root_prefix='',guide_name='index.html',assistant_name='assistant.html'):
 k=json.loads((snapshot/'knowledge.json').read_text());r=k['release'];comps=k['comps'];units=k['units'];items=k['items'];css=(ROOT/'templates/knowledge.css').read_text();engine=(ROOT/'templates/knowledge-engine.js').read_text();client=(ROOT/'templates/knowledge-ui.js').read_text()
 def names(ids,kind='units'):return '、'.join(k[kind].get(str(i),{}).get('name',str(i)) for i in ids) or '暂无'
 def tier(t):return f'<span class="tier {esc(t)}">{esc(t)}</span>'
 def table(headers,rows):return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
 raw_prefix=root_prefix+str(snapshot.relative_to(ROOT))+'/raw/'
 knowledge_link=root_prefix+str(snapshot.relative_to(ROOT))+'/knowledge.json'
 head='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>金铲铲 '+esc(r['patch'])+'｜阵容罗盘</title><style>'+css+'</style>'
 hero=f'<div class="hero"><small>金铲铲之战 · S{r["set"]} · {esc(r["patch"])} · {esc(r["fetched_at"][:10])}抓取</small><h1>这个版本，重新选阵</h1><p>完整扫描来源榜单{r["rank_count"]}套，按来源S/A评级入选{len(comps)}套。每次换版本重新筛选，阵容数量不固定。</p><p>来源：<a href="{r["source"]}/comp">金铲铲大数据（非官方）</a> · <a href="{root_prefix}games/tft/set18/18.4b/index.html">TFT18.4b历史手册</a> · <a href="{root_prefix}versions.html">版本记录</a></p></div>'
 side='<aside class="sidebar"><h3>阵容罗盘</h3><p>金铲铲 '+esc(r['patch'])+'</p><a href="#overview">01 版本怎么打</a><a href="#decide">02 这局能玩什么</a><a href="#compositions">03 阵容详细攻略</a><a href="#coverage">数据与来源</a><hr><strong>当期S/A · '+str(len(comps))+'套</strong>'+''.join(f'<a href="#comp-{c["id"]}">{tier(c["tier"])}{esc(c["name"])}</a>' for c in comps)+'<hr><a href="'+assistant_name+'">打开对局助手 →</a></aside>'
 groups=collections.Counter(c['group'] for c in comps);routes=collections.Counter(c['route'] for c in comps)
 change_rows=[]
 for x in k['changes']:
  title=f'<a href="#comp-{x["id"]}">{esc(x["name"])}</a>' if x['id'] in {c['id'] for c in comps} else esc(x['name'])
  change_rows.append([title,esc(x['status']),esc(str(x['old_tier'] or '—')+' → '+str(x['tier'] or '—')),esc(f'{x["old_avg"]} → {x["avg"]}'),f'{x["delta"]:+.2f}' if x['delta'] is not None else '定义变化／无对照',f'{x["old_count"] or 0:,} → {x["count"] or 0:,}', '低样本，谨慎解释' if x['low_sample'] else ('同ID与定义' if x['same_definition'] else '定义变化，不能直接归因')])
 entered=[x for x in k['changes'] if x['status']=='进入S/A'];exited=[x for x in k['changes'] if x['status']=='退出S/A'];improved=sorted([x for x in k['changes'] if x['delta'] is not None and not x['low_sample'] and x['delta']<-.15],key=lambda x:x['delta'])
 overview='<section id="overview" class="section"><h2>01 版本怎么打</h2><div class="metrics">'+''.join(f'<div class="metric"><strong>{v}</strong>{label}</div>' for label,v in [('当前S级',sum(c['tier']=='S' for c in comps)),('当前A级',sum(c['tier']=='A' for c in comps)),('新进入S/A',len(entered)),('上一版退出S/A',len(exited))])+'</div><div class="card"><h3>与'+esc(r['previous_patch'])+'相比</h3><p><strong>进入强势集合：</strong>'+esc('、'.join(x['name'] for x in entered))+'。</p><p><strong>样本均名改善值得关注：</strong>'+esc('；'.join(f"{x['name']} {x['old_avg']:.2f}→{x['avg']:.2f}" for x in improved[:4]))+'。这里描述来源样本的变化，不把改动公告直接当强度结论。</p><p><strong>退出S/A：</strong>'+esc('、'.join(x['name'] for x in exited) or '无')+'；历史记录仍保留，不再进入本版默认候选。</p><p><strong>这版入选阵容怎么分布：</strong>'+esc('、'.join(f'{g}{n}套' for g,n in groups.items()))+'；'+esc('、'.join(f'{g}{n}套' for g,n in routes.items()))+'。只代表本次S/A集合，不能据此断言物理一定强于法系。运营路线依来源主C费用和目标星级归纳。</p><details><summary>逐套版本变化与样本量</summary>'+table(['阵容','变化','评级','均名','差值（负数改善）','样本量','核对状态'],change_rows)+'</details><p class="source-line">两版同来源、同请求参数，按阵容ID与棋盘/主C/条件核对。来源未公开段位与时间窗；不同版本观察期不相同，不宣称补丁造成了全部变化。低于1,000条样本单独提示。</p></div>'
 # Frequency is descriptive across returned S/A triples; coverage is more comparable than raw counts.
 totals={}
 for c in comps:
  for h in c['heroes']:
   if h['role']=='挂件／功能位':continue
   for i in h['items']:
    if items[i]['type']!='成型装备':continue
    q=totals.setdefault(i,{'comps':set(),'heroes':set(),'n':0});q['comps'].add(c['id']);q['heroes'].add(h['id']);q['n']+=1
 eqrows=[[esc(items[i]['name']),len(v['comps']),len(v['heroes']),v['n']] for i,v in sorted(totals.items(),key=lambda x:(-len(x[1]['comps']),-x[1]['n'],x[0]))]
 overview+='<div class="card"><h3>哪些装备更泛用？</h3><p>先看覆盖阵容数，再看来源推荐出装的装备件数（重复两件计两次）。优先满足主C和主坦；这是需求覆盖，不是装备胜率或必做顺序。本来源S/A三件套较少，不用少量返回组合代表整体需求。</p>'+table(['装备','覆盖阵容','携带棋子','推荐装备件数'],eqrows[:10])+'<details><summary>查看全部普通装备统计</summary>'+table(['装备','覆盖阵容','携带棋子','推荐装备件数'],eqrows[10:])+'</details></div></section>'
 decide=f'<section class="section" id="decide"><h2>02 这局能玩什么</h2><div class="card"><h3>用本版{len(comps)}套阵容筛选</h3><p>选择已有棋子、等级、转职和海克斯，分别看当前过渡和后续补牌。按缺少棋子的出现频次补位，选择会自动保存。</p><a class="back" href="{assistant_name}">打开独立对局助手 →</a></div></section>'
 cards=[]
 for c in comps:
  cid=c['id'];hrows=[]
  for h in c['heroes']:
   hrows.append([esc(h['name']),esc(h['role']),str(h['stars'])+'星' if h['stars'] else '来源未标',esc(' + '.join(items[i]['name'] for i in h['items'])) or '—',esc(h['role_evidence'])])
  positions={h['position']:h for h in c['heroes'] if h['position']};board='<div class="board" aria-label="来源代表站位">'
  for row in range(1,5):
   for col in range(1,8):
    h=positions.get(f'{row},{col}');board+='<div class="cell'+(' occupied' if h else '')+'">'+(f'<strong>{esc(h["name"])}</strong><span>{esc(h["role"])}</span><span>{str(h["stars"])+"星" if h["stars"] else "星级未标"}</span>' if h else '')+'</div>'
  board+='</div>'
  conditions='；'.join(x['name']+'（必需）' for x in c['conditions']) or '来源未列专属入场条件'
  main=esc('、'.join(h['name'] for h in c['heroes'] if '主C' in h['role']) or '待核实');tanks=esc('、'.join(h['name'] for h in c['heroes'] if '主坦' in h['role']) or '来源未独立标记；结合前排承装判断')
  card=f'<article class="comp section" id="comp-{cid}" data-name="{esc(c["name"])}" data-group="{esc(c["group"])}"><h2>{tier(c["tier"])}{esc(c["name"])}</h2><p>{esc(c["group"])} · {esc(c["route"])} · 均名 {c["avg"]:.2f} · 前四 {c["top4"]:.1f}% · 样本 {c["count"]:,}</p>'
  if c['count']<1000:card+='<p class="warn">低样本候选：保留来源S/A评级，暂不据此强推。</p>'
  card+='<p><strong>入场条件：</strong>'+esc(conditions)+'</p><p><strong>主C：</strong>'+main+'　<strong>主坦候选：</strong>'+tanks+'</p><div class="note"><strong>终局保留核心：</strong>'+esc(names(c['retained_core']))+'<br><small>'+esc(c['core_evidence'])+'</small></div><details><summary>棋盘、职责与目标星级</summary>'+board+table(['棋子','职责','目标星级','来源推荐装备','判断依据'],hrows)+'<p class="muted">未标星级不等于只上一星。常规可先上场再追两星；来源“核心”标记与上方严格交集分开。主坦候选依据推荐防装推定。</p></details>'
  card+='<details><summary>一局怎么走 · '+esc(c['route'])+'</summary><div class="flow">'+''.join('<div><strong>'+esc(t)+'</strong><p>'+esc(v)+'</p></div>' for t,v in c['flow'])+'</div><p>停D条件：主C与前排有足够质量、能稳血时停手存钱；持续大掉血则先补质量。经济、同行和来牌会改变时间，不按固定回合盲目D空。</p><small>'+esc(c['flow_evidence'])+'</small></details>'
  card+='<details><summary>装备需求与已有装备补全</summary><p><strong>先主C和主坦，再副C／副坦。</strong>下面按本阵容非挂件棋子推荐出装的普通装备件数排序；重复件单独计数，不按对局样本加权。</p>'+table(['装备','出现次数'],[[esc(items[x['id']]['name']),x['count']] for x in c['equipment_frequency']])
  for h in c['heroes']:
   if h['role']=='挂件／功能位':continue
   builds=h['combinations'];card+=f'<details class="unit-equipment" data-comp="{cid}" data-unit="{h["id"]}"><summary>{esc(h["name"])} · {esc(h["role"])} · S/A三件套{len(builds)}组</summary><p>单件评级与三件套分别计算；先S后A，同级均名升序。若没有S/A统计，可切换来源推荐三件套；推荐出装不保证达到S/A。</p><div class="equipment-picker"></div><div class="equipment-results" aria-live="polite"></div><details><summary>全部返回的S/A三件套</summary>'+table(['评级','三件套','均名','样本'],[[tier(b['tier']),esc(' + '.join(items[i]['name'] for i in b['items'])),f'{b["avg"]:.2f}',f'{b["count"]:,}'] for b in builds])+'</details><details><summary>S/A单件装备</summary>'+table(['评级','装备','均名','样本'],[[tier(b['tier']),esc(names(b['items'],'items')),f'{b["avg"]:.2f}',f'{b["count"]:,}'] for b in h['single_items']])+'</details><p class="muted">'+esc(f'来源返回{h["equipment_coverage"]["returned_triples"]}组三件套；达到200组时可能为接口上限，不代表游戏全部组合。')+'</p></details>'
  card+='</details><details><summary>推荐海克斯 · '+str(len(c['augments']))+'项</summary><p>来源推荐接口按出现率返回；只展示该来源推荐集合，不把全部使用统计都当成推荐。</p>'
  for rarity,label in [(1,'银色'),(2,'金色'),(3,'棱彩'),(None,'未标阶位')]:
   a=[x for x in c['augments'] if x['rarity']==rarity]
   if a:card+='<h3>'+label+'</h3>'+table(['海克斯','出现回合','样本','样本均名'],[[esc(x['name']),esc(' / '.join(x['rounds']) or '未提供'),x['count'],x['avg'] if x['avg'] is not None else '未提供'] for x in a])
  card+='</details><details><summary>各等级实际棋盘与核心</summary>'
  for level in sorted({b['level'] for b in c['stages']}):
   bs=[b for b in c['stages'] if b['level']==level];core=set.intersection(*(set(b['units']) for b in bs))
   card+=f'<details><summary>{level}级 · {len(bs)}组</summary><p><strong>本级共同棋子：</strong>{esc(names(sorted(core)))}</p>'+table(['可购买棋子','自动生成单位','记录样本'],[[esc(names(b['units'])),esc(names(b['generated'])),b['count']] for b in bs])+'</details>'
  card+='</details><p class="source-line"><a href="'+c['source_url']+'">查看来源阵容</a> · <a href="'+raw_prefix+f'comps/{cid}/detail.json">原始详情</a> · <a href="{assistant_name}">返回对局助手</a></p></article>'
  cards.append(card)
 artifacts='<details><summary>神器 → 携带者 → 本版阵容（使用参考）</summary><p>以下是非挂件棋子的神器使用记录，不保证达到S/A；显示原始评级和样本，不把“出现过”当成优先推荐。</p>'
 cmap={c['id']:c for c in comps}
 for iid,refs in k['indices']['artifacts'].items():
  if not refs:continue
  artifacts+='<details><summary>'+esc(items[iid]['name'])+' · '+str(len(refs))+'条关联</summary>'+table(['阵容','携带者','来源装备评级','均名','样本'],[[f'<a href="#comp-{x["comp"]}">{esc(cmap[x["comp"]]["name"])}</a>',esc(names([x['unit']])),esc(x.get('tier') or '未标'),x.get('avg'),x.get('count')] for x in refs])+'</details>'
 artifacts+='</details>'
 coverage='<section class="card section" id="coverage"><h2>数据与来源</h2><p>本版来源榜单'+str(r['rank_count'])+'套，自动入选S/A '+str(len(comps))+'套；分等级棋盘'+str(sum(len(c['stages']) for c in comps))+'组。只用于金铲铲，不混入历史TFT数据。</p><ul>'+''.join('<li>'+esc(x)+'</li>' for x in r['limits'])+'</ul><p>段位、统计时间窗及队列编号：来源未提供。数据词库用于当前版本名称映射，不用于还原上一补丁技能数值。</p><p>未映射字段：'+esc('、'.join(k['quality']['unmapped']) or '无')+'；未映射项不进入推荐过滤器。</p>'+artifacts+'<p><a href="'+knowledge_link+'">完整规范化知识库</a> · <a href="'+root_prefix+str(snapshot.relative_to(ROOT))+'/manifest.json">请求与完整性记录</a></p></section>'
 data='<script id="knowledge-data" type="application/json">'+json.dumps(k,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+'</script>'
 scripts=data+'<script>'+engine+'</script><script>'+client+'</script>'
 guide=head+'<body data-mode="guide"><div class="shell">'+side+'<main class="content">'+hero+overview+decide+'<section id="compositions" class="section"><h2>03 阵容详细攻略</h2><div class="toolbar"><input id="guide-search" type="search" placeholder="搜索阵容或棋子"><select id="guide-group"><option>全部</option>'+''.join('<option>'+esc(x)+'</option>' for x in groups)+'</select></div>'+''.join(cards)+'</section>'+coverage+'</main></div>'+scripts+'</body></html>'
 assistant=head+'<body data-mode="assistant" class="layout-app" data-guide="'+guide_name+'"><header class="app-top"><div style="display:flex;justify-content:space-between;gap:12px"><h1>阵容罗盘 · 金铲铲'+esc(r['patch'])+' · 对局助手</h1><a href="'+guide_name+'">返回版本手册 ↗</a></div><div class="toolbar"><label>当前<select id="current-level"></select></label><label>目标<select id="target-level"></select></label><label>输出<select id="output-group"><option>全部</option>'+''.join('<option>'+esc(x)+'</option>' for x in groups)+'</select></label><small style="color:#d1e1e5">本版'+str(len(comps))+'套 · 换等级保留棋子</small></div><div id="selection-summary" aria-live="polite"></div></header><main class="app-grid"><section class="panel"><nav class="tabs" aria-label="选择条件"><button data-left="units" aria-selected="true">棋子</button><button data-left="emblems" aria-selected="false">转职</button><button data-left="augments" aria-selected="false">海克斯</button></nav><div class="scroll"><div id="units-pane" class="tab-pane"><div class="toolbar"><button id="clear-units">清空棋子</button></div><p class="muted compact">勾选场上与备战席已有棋子，可选部分核心。换等级不会清空；当前与未来分别匹配来源棋盘。</p><div id="unit-choices"></div></div><div id="emblems-pane" class="tab-pane" hidden><button id="clear-emblems">清空转职</button><p class="compact muted">只列本版推荐出装及入场条件出现的纹章。未持有必需纹章的阵容放在待补条件中。</p><label><input id="emblem-only" type="checkbox">只看能使用已选转职的阵容（并集）</label><div id="emblem-choices"></div></div><div id="augments-pane" class="tab-pane" hidden><div class="toolbar"><button id="clear-augments">清空海克斯</button><input id="augment-search" type="search" placeholder="搜索海克斯"></div><p class="compact muted">多选取推荐集合交集；来源明确要求的强化也可选择。未收录不代表无效。</p><div id="augment-choices"></div></div></div></section><section class="panel"><nav class="tabs" aria-label="查看结果"><button data-right="current" aria-selected="true">当前等级怎么过渡</button><button data-right="future" aria-selected="false">升级后补什么</button></nav><div class="scroll" id="results-scroll"><div id="current-results" class="tab-pane"></div><div id="future-results" class="tab-pane" hidden></div></div></section></main><noscript>请使用支持JavaScript的浏览器；完整阵容与数据可在版本手册中阅读。</noscript>'+scripts+'</body></html>'
 out.mkdir(parents=True,exist_ok=True);(out/guide_name).write_text(guide);(out/assistant_name).write_text(assistant)
 print('Rendered',out,len(comps),'comps')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('snapshot',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--root-prefix',default='');p.add_argument('--guide-name',default='index.html');a=p.parse_args();render(a.snapshot.resolve(),a.output,a.root_prefix,a.guide_name)
