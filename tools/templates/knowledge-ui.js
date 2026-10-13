(function(){
'use strict';
const K=JSON.parse(document.getElementById('knowledge-data').textContent),E=KnowledgeEngine;
const $=id=>document.getElementById(id),esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const unit=id=>K.units[id]?.name||id,item=id=>K.items[id]?.name||id,names=ids=>ids.map(unit).join('、')||'无';
const badge=t=>`<span class="tier ${esc(t)}">${esc(t)}</span>`;
const num=n=>Number(n||0).toLocaleString('zh-CN');
function connectHash(){let el=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(!el)return;let p=el;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}el.hidden=false;el.scrollIntoView({block:'start'});}
window.addEventListener('hashchange',connectHash);
function setupEquipment(container){
 const gearKey=`jcc-gear:${K.release.set}:${K.release.patch}`;let gear={};try{gear=JSON.parse(localStorage.getItem(gearKey)||'{}')}catch{}
 container.querySelectorAll('.unit-equipment').forEach(box=>{
  const c=K.comps.find(x=>x.id===box.dataset.comp),h=c.heroes.find(x=>x.id===box.dataset.unit),key=c.id+':'+h.id;
  if(!gear[key]||typeof gear[key]!=='object')gear[key]={};
  const allOptions=[...h.combinations,...(h.recommended_combination?[h.recommended_combination]:[])];const freq={};allOptions.forEach(b=>new Set(b.items).forEach(i=>freq[i]=(freq[i]||0)+1));const options=Object.keys(freq).sort((a,b)=>freq[b]-freq[a]||item(a).localeCompare(item(b),'zh-CN'));
  Object.keys(gear[key]).filter(i=>!options.includes(i)).forEach(i=>delete gear[key][i]);
  let scope=h.combinations.length?'sa':'recommended';box.querySelector('.equipment-picker').innerHTML=options.length?`<label>候选范围 <select data-gear-scope><option value="sa" ${scope==='sa'?'selected':''}>S/A统计组合</option><option value="recommended" ${scope==='recommended'?'selected':''}>来源推荐三件套</option></select></label><div class="equipment-choice">${options.map(i=>`<label>${esc(item(i))} · ${freq[i]}次<select data-item="${esc(i)}" aria-label="${esc(h.name+'已有'+item(i))}">${[0,1,2,3].map(n=>`<option value="${n}" ${Number(gear[key][i]||0)===n?'selected':''}>${n}件</option>`).join('')}</select></label>`).join('')}</div><button data-clear-equipment>清空该棋子装备</button>`:'<p class="muted">来源未返回可用S/A三件套，暂不生成补全建议。</p>';
  function update(){const owned=Object.entries(gear[key]).flatMap(([i,n])=>Array(Number(n)).fill(i)),target=box.querySelector('.equipment-results');if(owned.length>3){target.innerHTML='<p class="warn">已选超过3件，请减少数量。</p>';return;}
   const pool=scope==='sa'?h.combinations:(h.recommended_combination?[h.recommended_combination]:[]);const matches=E.equipment(pool,owned).sort((a,b)=>(a.tier==='S'?0:1)-(b.tier==='S'?0:1)||(a.avg??Infinity)-(b.avg??Infinity));const format=b=>`<div class="scheme">${badge(b.tier||'未评级')}均名 ${b.avg==null?'未提供':Number(b.avg).toFixed(2)} · 样本 ${b.count==null?'未提供':num(b.count)}<p class="positive"><strong>${b.missing.length?'还缺：'+esc(b.missing.map(item).join(' + ')):'这套已凑齐'}</strong></p><small>完整组合：${esc(b.items.map(item).join(' + '))}</small></div>`;
   target.innerHTML=`<p><strong>已选${owned.length}/3件 · ${matches.length}组兼容${scope==='sa'?'S/A统计':'来源推荐'}组合</strong></p>`+(matches.length?matches.slice(0,3).map(format).join('')+(matches.length>3?`<details><summary>其余${matches.length-3}组兼容组合</summary>${matches.slice(3).map(format).join('')}</details>`:''):'<p class="muted">来源返回组合中没有匹配项；可减少已选装备重新查找。</p>');
  }
  box.addEventListener('change',e=>{if(e.target.matches('[data-gear-scope]')){scope=e.target.value;update();return;}if(!e.target.matches('select[data-item]'))return;gear[key][e.target.dataset.item]=Number(e.target.value);try{localStorage.setItem(gearKey,JSON.stringify(gear))}catch{}update();});
  box.addEventListener('click',e=>{if(!e.target.closest('[data-clear-equipment]'))return;gear[key]={};box.querySelectorAll('select[data-item]').forEach(x=>x.value='0');try{localStorage.setItem(gearKey,JSON.stringify(gear))}catch{}update();});update();
 });
}
if(document.body.dataset.mode==='guide'){
 const apply=()=>{const q=$('guide-search').value.trim().toLowerCase(),g=$('guide-group').value;K.comps.forEach(c=>{const text=c.name+c.heroes.map(h=>h.name).join('');$(`comp-${c.id}`).hidden=!(text.toLowerCase().includes(q)&&(g==='全部'||c.group===g));});};
 $('guide-search').addEventListener('input',apply);$('guide-group').addEventListener('change',apply);
 setupEquipment(document);
 document.addEventListener('click',e=>{const link=e.target.closest('a[href^="#comp-"]');if(!link)return;$('guide-search').value='';$('guide-group').value='全部';apply();});
 if(location.hash)setTimeout(connectHash,30);return;
}
const key=`jcc-assistant:${K.release.set}:${K.release.patch}`,defaults={owned:[],augments:[],emblems:[],emblemOnly:false,current:6,target:8,group:'全部',left:'units',right:'current',added:{},disclosures:{}};
let state=structuredClone(defaults);try{Object.assign(state,JSON.parse(localStorage.getItem(key)||'{}'))}catch{}
for(const v of ['owned','augments','emblems'])if(!Array.isArray(state[v]))state[v]=[];
if(!state.added||typeof state.added!=='object'||Array.isArray(state.added))state.added={};
if(!state.disclosures||typeof state.disclosures!=='object'||Array.isArray(state.disclosures))state.disclosures={};
const stageLevels=E.unique(K.comps.flatMap(c=>c.stages.map(b=>b.level))).sort((a,b)=>a-b);if(!stageLevels.includes(Number(state.current)))state.current=stageLevels[0];
if(!['units','emblems','augments'].includes(state.left))state.left='units';if(!['current','future'].includes(state.right))state.right='current';
const validGroups=['全部',...E.unique(K.comps.map(c=>c.group))];if(!validGroups.includes(state.group))state.group='全部';
function save(){try{localStorage.setItem(key,JSON.stringify(state));}catch{}}
function disclosure(key,defaultOpen){const open=typeof state.disclosures[key]==='boolean'?state.disclosures[key]:defaultOpen;return `data-disclosure="${esc(key)}" ${open?'open':''}`;}
// Store only user activation, so automatically closed candidates may open when they become the sole result.
document.addEventListener('click',e=>{const summary=e.target.closest('summary');if(!summary)return;const details=summary.parentElement;if(!details.matches('details[data-disclosure]'))return;state.disclosures[details.dataset.disclosure]=!details.open;save();});
function checked(id,values){return values.includes(id)?'checked':''}
function choices(ids,values,kind,extra=()=>'',label=id=>unit(id)){return `<div class="checkgrid">${ids.map(id=>`<label class="${values.includes(id)?'owned':''}"><input type="checkbox" data-kind="${kind}" value="${esc(id)}" ${checked(id,values)}><span>${esc(label(id))}${extra(id)}</span></label>`).join('')}</div>`;}
function renderLevels(){
 $('current-level').innerHTML=stageLevels.map(n=>`<option value="${n}" ${Number(state.current)===n?'selected':''}>${n}级</option>`).join('');
 const next=stageLevels.filter(n=>n>Number(state.current));if(!next.includes(Number(state.target)))state.target=next[0]??null;
 $('target-level').innerHTML=next.length?next.map(n=>`<option value="${n}" ${Number(state.target)===n?'selected':''}>${n}级</option>`).join(''):'<option>已是最高等级</option>'; $('target-level').disabled=!next.length;
 $('output-group').value=state.group;
}
function renderUnits(){
 const stageUnits=E.unique(K.comps.flatMap(c=>c.stages.filter(b=>b.level===Number(state.current)).flatMap(b=>b.units))),all=E.unique([...stageUnits,...state.owned]);
 const grouped={};all.forEach(i=>(grouped[K.units[i]?.cost||0]??=[]).push(i));
 $('unit-choices').innerHTML=Object.keys(grouped).sort((a,b)=>a-b).map(cost=>`<details class="cost${cost}" data-cost="${cost}" ${disclosure('cost:'+cost,true)}><summary>${cost==='0'?'未收录':cost+'费'} · ${grouped[cost].length}名</summary>${choices(grouped[cost].sort((a,b)=>unit(a).localeCompare(unit(b),'zh-CN')),state.owned,'owned',i=>stageUnits.includes(i)?'':'<small>本级未收录，已保留选择</small>')}</details>`).join('');
}
function renderEmblems(){const ids=E.unique(K.comps.flatMap(c=>[...c.optional_emblems,...c.conditions.filter(x=>x.kind==='item').map(x=>x.id)]));$('emblem-choices').innerHTML=choices(ids,state.emblems,'emblems',id=>`<small>${K.comps.filter(c=>c.conditions.some(x=>x.kind==='item'&&x.id===id)).length?'有必需分支':'推荐出装有记录；非必需'}</small>`,item);$('emblem-only').checked=state.emblemOnly;}
function renderAugments(){const ids=E.unique([...Object.keys(K.indices.augments),...K.comps.flatMap(c=>c.conditions.filter(x=>x.kind==='augment').map(x=>x.id))]);const q=$('augment-search').value.trim();const filtered=ids.filter(i=>(K.augments[i]?.name||i).includes(q));
 $('augment-choices').innerHTML=[1,2,3,0].map(n=>{const group=filtered.filter(i=>(K.augments[i]?.rarity||0)===n);return group.length?`<h3>${({1:'银色',2:'金色',3:'棱彩',0:'未标阶位'})[n]}</h3>${choices(group,state.augments,'augments',id=>`<small>${K.indices.augments[id]?.length||0}套来源推荐${K.comps.some(c=>c.conditions.some(x=>x.kind==='augment'&&x.id===id))?' · 含必需分支':''}</small>`,i=>K.augments[i]?.name||i)}`:''}).join('')||'<p class="empty">没有对应海克斯。</p>';
}
const guide=document.body.dataset.guide||'index.html';
function gearSummary(c){
 const heroes=c.heroes.filter(h=>/主C|副C|主坦|副坦/.test(h.role)).sort((a,b)=>Number(!/主C|主坦/.test(a.role))-Number(!/主C|主坦/.test(b.role)));
 const freq={};heroes.forEach(h=>new Set(h.items).forEach(i=>{(freq[i]??=[]).push(h.name);}));
 const demand=Object.entries(freq).sort((a,b)=>b[1].length-a[1].length).map(([i,who])=>`${item(i)} ${who.length}名（${who.join('、')}）`).join('；');
 const rows=builds=>builds.length?`<div class="table-wrap"><table><thead><tr><th>评级</th><th>装备</th><th>均名</th><th>样本</th></tr></thead><tbody>${builds.slice().sort((a,b)=>(a.tier==='S'?0:1)-(b.tier==='S'?0:1)||(a.avg??Infinity)-(b.avg??Infinity)).map(b=>`<tr><td>${badge(b.tier)}</td><td>${esc(b.items.map(item).join(' + '))}</td><td>${b.avg==null?'未提供':Number(b.avg).toFixed(2)}</td><td>${num(b.count)}</td></tr>`).join('')}</tbody></table></div>`:'<p class="muted">来源未返回S/A记录。</p>';
 return `<details ${disclosure('gear:'+c.id,false)}><summary>装备建议 · 主C与主坦优先</summary><p>先凑主C与主坦，再给副C、副坦分配；主坦候选按场上质量选择，不要求同时做满。</p><details><summary>全队推荐装备需求</summary><p>${esc(demand||'来源未列')}</p><small>按来源推荐出装覆盖的携带者数排序，不是S/A组合频次或必做件数。</small></details>${heroes.map(h=>`<details class="unit-equipment" data-comp="${c.id}" data-unit="${h.id}" ${disclosure('gear-unit:'+c.id+':'+h.id,/主C|主坦/.test(h.role))}><summary>${esc(h.name)} · ${esc(h.role)} · ${h.stars||'—'}星</summary><p><strong>来源推荐：</strong>${esc(h.items.map(item).join(' + ')||'未提供')}</p><small>${esc(h.role_evidence||'')}；转职出装仅适用于对应分支。</small><p>${h.combinations.length?'可查询 '+h.combinations.length+' 组S/A三件套，先S后A，同级均名升序。':'本次来源没有返回S/A三件套；下方按来源推荐补全，不赋予S/A评级。'}</p><p>选择该棋子已穿戴并准备保留的装备（最多3件，支持重复件）：</p><div class="equipment-picker"></div><div class="equipment-results" aria-live="polite"></div><details><summary>S/A单件装备 · ${h.single_items.length}项</summary>${rows(h.single_items)}</details><details><summary>全部S/A三件套 · ${h.combinations.length}组</summary>${rows(h.combinations)}</details></details>`).join('')}<p class="source-line">沿用本版金铲铲该阵容的数据；单件评级与三件套评级不同。选择会保存，刷新或切换方向后保留。</p></details>`;
}
function compLink(c){return `<a href="${esc(guide)}#comp-${c.id}">${badge(c.tier)}${esc(c.name)} ↗</a>`;}
function currentResults(){const byBoard=new Map(),missing=[];
 K.comps.forEach(c=>{if(!E.passes(c,state))return;const rows=E.boards(c,state.current,state.owned);if(E.gaps(c,state).length){if(rows.length)missing.push(c);return;}
 rows.forEach(b=>{const id=b.units.slice().sort().join(',');if(!byBoard.has(id))byBoard.set(id,b);});});
 const arr=[...byBoard.values()].sort((a,b)=>a.units.filter(x=>!state.owned.includes(x)).length-b.units.filter(x=>!state.owned.includes(x)).length);
 function format(b){const ids=K.indices.boards[state.current+':'+b.units.slice().sort().join(',')]||[];const links=ids.map(id=>{const c=K.comps.find(c=>c.id===id),missing=E.gaps(c,state);const eligible=E.passes(c,state)&&!missing.length;return `<div class="note">${compLink(c)}<small style="display:block">${eligible?'符合当前筛选':missing.length?'待补：'+esc(missing.map(x=>x.name).join('、')):'有该棋盘记录；未通过当前条件筛选'}</small>${gearSummary(c)}</div>`;}).join('');
 return `<div class="scheme"><strong>补入：${esc(names(b.units.filter(x=>!state.owned.includes(x))))}</strong><p>完整棋盘：${esc(names(b.units))}</p><details ${disclosure('board:'+state.current+':'+b.units.slice().sort().join(','),true)}><summary>可通向的最终阵容 · ${ids.length}套</summary>${links}</details></div>`;}
 $('current-results').innerHTML=`<h3>${state.current}级 · ${arr.length}种当前过渡</h3>`+(arr.length?arr.slice(0,3).map(format).join('')+(arr.length>3?`<details><summary>其他${arr.length-3}种过渡方案</summary>${arr.slice(3).map(format).join('')}</details>`:''):'<p class="empty">该等级返回棋盘中没有同时包含所选棋子的组合。选择会保留，可取消部分打工牌或查看后续等级。</p>')+missingConditions(missing)+'<p class="source-line">同一完整棋盘反查全部本版终局，不因筛选隐藏归属。来源每级只返回有限组，零匹配不代表无法过渡。</p>';
 return arr.length;
}
function missingConditions(cs){return cs.length?`<details><summary>待补入场条件 · ${cs.length}套</summary>${cs.map(c=>`<p>${compLink(c)}<br>还缺：${esc(E.gaps(c,state).map(x=>x.name).join('、'))}</p>`).join('')}</details>`:'';}
function fillHTML(c,rows){const pkey=c.id+':'+state.target,added=Array.isArray(state.added[pkey])?state.added[pkey]:[],calc=E.fill(rows,state.owned,added);
 const freq=calc.frequency.map(([id,n])=>`<label><input type="checkbox" data-add="${id}"><span>${esc(unit(id))} <strong>${n}/${calc.matches.length}</strong></span></label>`).join('');
 const scheme=b=>{const kept=b.units.filter(x=>calc.owned.includes(x)),left=b.units.filter(x=>!calc.owned.includes(x));return `<div class="scheme"><strong class="positive">${left.length?'还需补入：'+esc(names(left)):'完整组合已凑齐'}</strong><p>使用已有：${esc(names(kept))}</p><p><strong>前四率 ${b.top4==null?'未提供':Number(b.top4).toFixed(2)+'%'} · 平均排名 ${b.avg==null?'未提供':Number(b.avg).toFixed(2)}</strong> · 样本 ${num(b.count)}</p><small>完整${b.level}级棋盘：${esc(names(b.units))}</small></div>`;};
 return `<div class="fill-panel" data-comp="${c.id}" data-level="${state.target}"><p><strong>可用组合：${calc.matches.length}/${rows.length}</strong> · 已补${added.length}名</p><div class="freq-list">${added.map(i=>`<label class="owned"><input type="checkbox" data-add="${i}" checked>${esc(unit(i))}（已补）</label>`).join('')}</div><p>下一步可补（每组每棋子计一次，按频次排序）：</p><div class="freq-list">${freq||'<span class="muted">暂无缺件</span>'}</div><button data-clear-add>清空本方向补牌</button><p class="source-line">组合按前四率降序、同前四率按平均排名升序；缺失值排后。统计对应来源棋盘与星级配置，不代表补牌的因果收益。</p>${calc.matches.length?calc.matches.slice(0,3).map(scheme).join('')+(calc.matches.length>3?`<details><summary>其余${calc.matches.length-3}套完整组合</summary>${calc.matches.slice(3).map(scheme).join('')}</details>`:''):'<p class="warn">已补棋子没有共同出现的记录，请取消一项；不会拼接互不兼容的高频棋子。</p>'}</div>`;
}
function futureResults(){const ok=[],missing=[];
 K.comps.forEach(c=>{if(!E.passes(c,state)||state.target==null)return;const rows=E.boards(c,state.target,state.owned);if(!rows.length)return;if(E.gaps(c,state).length){missing.push(c);return;}ok.push({c,rows});});
 $('future-results').innerHTML=`<h3>${state.target??'—'}级 · ${ok.length}个后续方向</h3>`+(ok.length?ok.map(({c,rows})=>{const added=state.added[c.id+':'+state.target]||[],f=E.fill(rows,state.owned,added),short=f.frequency.slice(0,4).map(([i,n])=>`${unit(i)} ${n}/${f.matches.length}`).join('、');return `<details data-comp="${c.id}" ${disclosure('future:'+c.id,ok.length===1)}><summary>${badge(c.tier)}${esc(c.name)} · ${rows.length}种匹配</summary><p>${compLink(c)}</p><div class="note"><strong>终局保留核心：</strong>${esc(names(c.retained_core))}<br><small>${esc(c.core_evidence)}</small></div>${gearSummary(c)}${fillHTML(c,rows)}</details><p class="compact muted">${esc(c.name)}优先观察：${esc(short||'当前选择已凑齐或无兼容记录')}</p>`;}).join(''):'<p class="empty">目标等级没有同时包含所选棋子的已返回组合。可以查看其他等级或取消部分打工牌；不会用当前等级的结果限制未来方向。</p>')+missingConditions(missing)+'<p class="source-line">后续按目标等级独立匹配；不同等级记录不是同一局的转型路径。频次不代表胜率。</p>';
 return ok.length;
}
function renderResults(){const pos=$('results-scroll').scrollTop;const a=currentResults(),b=futureResults();setupEquipment($('current-results'));setupEquipment($('future-results'));$('selection-summary').textContent=`已选${state.owned.length}名棋子 · ${state.augments.length}个海克斯 · ${state.emblems.length}个转职 ｜ 当前过渡${a}种 / 后续方向${b}个`;$('results-scroll').scrollTop=pos;save();}
function tabs(){document.querySelectorAll('[data-left]').forEach(x=>x.setAttribute('aria-selected',x.dataset.left===state.left));document.querySelectorAll('[data-right]').forEach(x=>x.setAttribute('aria-selected',x.dataset.right===state.right));for(const x of ['units','emblems','augments'])$(x+'-pane').hidden=x!==state.left;for(const x of ['current','future'])$(x+'-results').hidden=x!==state.right;save();}
function changeSelection(kind,id,on){state[kind]=on?E.unique([...state[kind],id]):state[kind].filter(x=>x!==id);}
$('current-level').addEventListener('change',e=>{state.current=Number(e.target.value);renderLevels();renderUnits();renderResults();});$('target-level').addEventListener('change',e=>{state.target=Number(e.target.value);renderResults();});$('output-group').addEventListener('change',e=>{state.group=e.target.value;renderResults();});
$('augment-search').addEventListener('input',renderAugments);$('emblem-only').addEventListener('change',e=>{state.emblemOnly=e.target.checked;renderResults();});
document.addEventListener('change',e=>{const el=e.target;if(el.matches('input[data-kind]')){changeSelection(el.dataset.kind,el.value,el.checked);el.closest('label').classList.toggle('owned',el.checked);renderResults();}if(el.matches('input[data-add]')){const panel=el.closest('.fill-panel'),cid=panel.dataset.comp,pkey=cid+':'+panel.dataset.level,a=state.added[pkey]||[];state.added[pkey]=el.checked?E.unique([...a,el.dataset.add]):a.filter(i=>i!==el.dataset.add);const c=K.comps.find(c=>c.id===cid),rows=E.boards(c,Number(panel.dataset.level),state.owned);panel.outerHTML=fillHTML(c,rows);save();}});
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.left){state.left=b.dataset.left;tabs();}if(b.dataset.right){state.right=b.dataset.right;tabs();}if(b.id==='clear-units'){state.owned=[];renderUnits();renderResults();}if(b.id==='clear-emblems'){state.emblems=[];renderEmblems();renderResults();}if(b.id==='clear-augments'){state.augments=[];renderAugments();renderResults();}if(b.hasAttribute('data-clear-add')){const panel=b.closest('.fill-panel'),c=K.comps.find(c=>c.id===panel.dataset.comp);state.added[c.id+':'+panel.dataset.level]=[];panel.outerHTML=fillHTML(c,E.boards(c,Number(panel.dataset.level),state.owned));save();}});
renderLevels();renderUnits();renderEmblems();renderAugments();renderResults();tabs();
})();
