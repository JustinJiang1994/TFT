// Lightweight DOM harness: executes the shipped script and its actual click handlers.
// This verifies wiring/rendered text, not browser layout.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),html=fs.readFileSync(path.join(root,'games/assistant/index.html'),'utf8');
const elements=new Map();
for(const [,id] of html.matchAll(/\bid="([^"]+)"/g))elements.set(id,{id,value:'',innerHTML:'',textContent:'',handlers:{},addEventListener(type,fn){this.handlers[type]=fn;}});
elements.get('data').textContent=html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1];elements.get('augment-rarity').value='all';
const context=vm.createContext({document:{getElementById:id=>{assert(elements.has(id),'missing element '+id);return elements.get(id);}},localStorage:{getItem:()=>null,setItem(){}},console});
for(const script of ['knowledge-engine.js','unified-assistant.js'])vm.runInContext(fs.readFileSync(path.join(root,'tools/templates',script),'utf8'),context);
const U=require('../../templates/unified-assistant.js'),K=JSON.parse(elements.get('data').textContent),groups=U.augmentGroups(K,{version:'all'});
assert(elements.get('results').innerHTML.includes('先选一个'));
assert.equal((elements.get('augment-list').innerHTML.match(/class="hex"/g)||[]).length,groups.length);
const choose=key=>elements.get('augment-list').handlers.click({target:{closest:()=>({dataset:{hex:key}})}});
choose(groups[0].key);assert.equal((elements.get('results').innerHTML.match(/<article /g)||[]).length,groups[0].comps.length);assert(!elements.get('results').innerHTML.includes('查看阵容来源'));
choose(groups[1].key);assert.equal((elements.get('results').innerHTML.match(/<article /g)||[]).length,groups[0].comps.filter(id=>groups[1].comps.includes(id)).length);
choose(groups[0].key);assert.equal((elements.get('results').innerHTML.match(/<article /g)||[]).length,groups[1].comps.length);
elements.get('clear-hex').handlers.click();assert(elements.get('results').innerHTML.includes('先选一个'));
elements.get('show-all').handlers.click();assert.equal((elements.get('results').innerHTML.match(/<article /g)||[]).length,37);
elements.get('version').value=K.versions[1].id;elements.get('version').handlers.change();assert.equal((elements.get('results').innerHTML.match(/<article /g)||[]).length,22);
elements.get('augment-query').value='不存在的海克斯';elements.get('augment-query').handlers.input();assert(elements.get('augment-list').innerHTML.includes('没有对应'));
elements.get('reset').handlers.click();assert(elements.get('results').innerHTML.includes('先选一个'));assert.equal(elements.get('augment-query').value,'');
console.log('PASS: generated page boots, renders recommendation buttons, click/toggle/multi-select, clear, all comps, version change, search and reset handlers. No visual browser assertion.');

choose(groups[0].key);elements.get('flow-next').handlers.click();assert.equal(elements.get('planning-input').hidden,false);
const candidate=K.comps.find(c=>groups[0].comps.includes(c.id));
const picked=candidate.units[0];
elements.get('units').handlers.change({target:{matches:()=>true,checked:true,value:picked}});
assert(elements.get('plans').innerHTML.includes(K.units[picked].name));assert(elements.get('plans').innerHTML.includes('备战席'));
choose(groups[1].key);choose(groups[1].key);assert(elements.get('plans').innerHTML.includes(K.units[picked].name),'changing augments retains hand');
elements.get('current').value='4';elements.get('current').handlers.change();assert(elements.get('plans').innerHTML.includes('/4 人'));
elements.get('clear').handlers.click();assert(elements.get('plans').innerHTML.includes('勾选场上和备战席'));
console.log('PASS: planner step, hand input, augment changes retain hand, level changes and clear.');

elements.get('reset').handlers.click();
assert.equal((elements.get('units').innerHTML.match(/type="checkbox"/g)||[]).length,U.unitGroups(K,{version:'all'}).length);
assert(!elements.get('units').innerHTML.includes('<summary>'));
const common=U.unitGroups(K,{version:'all'}).find(g=>new Set(g.ids.map(i=>K.units[i].version)).size>1);
elements.get('units').handlers.change({target:{matches:()=>true,checked:true,value:common.ids[0]}});

console.log('PASS: unified cost grid.');

elements.get('reset').handlers.click();elements.get('show-all').handlers.click();
assert(elements.get('results').innerHTML.includes('自动展示：7级易 · 常规配装'));
elements.get('owned-emblems').handlers.change({target:{matches:()=>true,checked:true,value:'斗士纹章'}});
assert(elements.get('results').innerHTML.includes('自动展示：7级易 · 斗士转职'));
elements.get('owned-emblems').handlers.change({target:{matches:()=>true,checked:false,value:'斗士纹章'}});
assert(elements.get('results').innerHTML.includes('自动展示：7级易 · 常规配装'));
console.log('PASS: actual emblem checkbox switches rendered final board in both directions.');
elements.get('component-stock').handlers.input({target:{dataset:{component:'法杖'},value:'2'}});
elements.get('component-stock').handlers.input({target:{dataset:{component:'大剑'},value:'1'}});
assert(elements.get('material-matches').innerHTML.includes('已有散件更适合哪些方向'));
assert(elements.get('material-matches').innerHTML.includes('优先拿'));
elements.get('clear-components').handlers.click();assert(elements.get('material-matches').innerHTML.includes('填写已有基础装备数量'));
console.log('PASS: component quantity input, candidate fit/missing/priority rendering and clear.');
elements.get('units').handlers.change({target:{matches:()=>true,checked:true,value:common.ids[0]}});
assert(elements.get('combined-recommendations').innerHTML.includes('综合推荐'));
assert(elements.get('combined-recommendations').innerHTML.includes('后面补哪些棋子')||elements.get('combined-recommendations').innerHTML.includes('不强凑三套'));
console.log('PASS: combined recommendation summary renders in the shipped UI.');

// Flow nodes are freely selectable, preserve input, and reveal only one working pane.
const move=n=>elements.get('flow-nav').handlers.click({target:{closest:()=>({dataset:{step:String(n)}})}});
move(1);assert.equal(elements.get('flow-units').hidden,false);assert.equal(elements.get('flow-output').hidden,false);
const handBefore=elements.get('units').innerHTML;
move(2);assert.equal(elements.get('flow-items').hidden,false);assert.equal(elements.get('flow-units').hidden,true);
elements.get('component-stock').handlers.input({target:{dataset:{component:'法杖'},value:'2'}});
move(2);assert.equal(elements.get('flow-output').hidden,false);assert.equal(elements.get('planning-input').hidden,false);assert.equal(elements.get('flow-2').ariaCurrent,'step');assert.equal(elements.get('flow-next').hidden,true);assert(!elements.has('flow-3'));
move(0);assert.equal(elements.get('flow-hex').hidden,false);assert.equal(elements.get('flow-output').hidden,false);
assert.equal(elements.get('units').innerHTML,handBefore);assert(elements.get('flow-2').innerHTML.includes('法杖 × 2'));
elements.get('reset').handlers.click();assert.equal(elements.get('flow-0').ariaCurrent,'step');assert(elements.get('flow-2').innerHTML.includes('暂无散件或转职'));
console.log('PASS: three flow nodes, backtracking, retained hand/materials and full reset.');

choose(groups[0].key);assert(elements.get('flow-0').innerHTML.includes(groups[0].name));
elements.get('units').handlers.change({target:{matches:()=>true,checked:true,value:common.ids[0]}});
assert(elements.get('flow-1').innerHTML.includes(K.units[common.ids[0]].name));
elements.get('owned-emblems').handlers.change({target:{matches:()=>true,checked:true,value:'斗士纹章'}});
assert(elements.get('flow-2').innerHTML.includes('斗士纹章'));
for(let i=0;i<3;i++){move(i);assert.equal(elements.get('flow-output').hidden,false);assert.equal(elements.get('flow-inputs').hidden,false);}
console.log('PASS: named condition summaries, live results at every step, persistent recommendations.');
// Recommend real boards and verify compact summaries do not leak the expanded action panels.
elements.get('reset').handlers.click();elements.get('show-all').handlers.click();
const cardComp=K.comps.find(c=>c.source_id==='426021');
for(const id of cardComp.units)elements.get('units').handlers.change({target:{matches:()=>true,checked:true,value:id}});
const cards=elements.get('combined-recommendations').innerHTML;
const summaries=[...cards.matchAll(/<details class="recommendation recommendation-card"><summary class="recommendation-summary">([\s\S]*?)<\/summary>/g)];
assert(summaries.length>0&&summaries.length<=3);
for(const [,summary] of summaries){assert(summary.includes('推荐原因'));assert(summary.includes('缺少核心'));assert(summary.includes('缺少散件'));assert(!summary.includes('class="actions"'));}
assert(cards.includes('主C／主坦核心配装'));assert(cards.includes('缺少散件 · 拿装优先级'));assert(cards.includes('共需 '));assert(cards.includes('已有可用 '));assert(!cards.includes('（已知配装小计，副位仍有缺口）'));
assert(cards.includes('class="recommendation-body"'));assert(cards.includes('现在上场'));assert(cards.includes('装备先合什么'));assert(cards.includes('目标完整棋盘'));
assert(!cards.includes('recommendation-card" open'));
console.log('PASS: top cards start collapsed, reasons/core/material gaps visible, detailed actions and final boards preserved.');

elements.get('reset').handlers.click();choose(groups[0].key);
const hexCards=elements.get('combined-recommendations').innerHTML;
const eligibleCount=keys=>K.comps.filter(c=>keys.every(k=>c.augments.some(a=>U.augmentKey(a)===k))).map(c=>U.activeComp(K,c,{owned:[],ownedEmblems:[],augments:keys})).filter(c=>U.recommendationEligible(K,c,{owned:[],ownedEmblems:[],augments:keys})).length;
assert.equal((hexCards.match(/recommendation-card hex-direction/g)||[]).length,eligibleCount([groups[0].key]));
assert(hexCards.includes('符合已选海克斯'));assert(!hexCards.includes('把手里的牌告诉我'));
assert.equal(elements.get('flow-output').hidden,false);
choose(groups[1].key);
const intersection=eligibleCount([groups[0].key,groups[1].key]);
assert.equal((elements.get('combined-recommendations').innerHTML.match(/recommendation-card hex-direction/g)||[]).length,intersection);
console.log('PASS: choosing a hex immediately shows every matching direction without hand/items; multiple hexes intersect.');
elements.get('reset').handlers.click();
const wolf=K.comps.find(c=>String(c.source_id)==='87'),firstHex=U.augmentKey(wolf.augments[0]);choose(firstHex);
const nextMarkup=elements.get('combined-recommendations').innerHTML;
assert(nextMarkup.includes('后续可考虑的海克斯'));assert(nextMarkup.includes('不保证后续轮次出现'));
const nextKeys=[...nextMarkup.matchAll(/data-next-hex="([^"]+)"/g)].map(m=>m[1].replaceAll('&quot;','"').replaceAll('&amp;','&'));
assert(!nextKeys.includes(firstHex));
for(const a of wolf.augments.filter(a=>U.augmentKey(a)!==firstHex))assert(nextKeys.includes(U.augmentKey(a)),'full recommendations retained: '+a.name);
assert(nextMarkup.includes('data-direction='));
console.log('PASS: future augment preview/full list, selected augment exclusion, provenance and round-availability limits.');
// Follow-up recommendations use the same intersection as the main picker, without toggling the card.
const selectedKeys=[firstHex];
const addNext=key=>{
 let prevented=false,stopped=false;
 elements.get('combined-recommendations').handlers.click({target:{closest:selector=>selector==='[data-next-hex]'?{dataset:{nextHex:key}}:null},preventDefault(){prevented=true},stopPropagation(){stopped=true}});
 assert(prevented&&stopped);
};
elements.get('units').handlers.change({target:{matches:()=>true,checked:true,value:common.ids[0]}});
elements.get('component-stock').handlers.input({target:{dataset:{component:'法杖'},value:'2'}});
for(const a of wolf.augments.slice(1,3)){
 const key=U.augmentKey(a);addNext(key);selectedKeys.push(key);
 const expected=K.comps.filter(c=>selectedKeys.every(key=>c.augments.some(a=>U.augmentKey(a)===key)));
 assert.equal((elements.get('combined-recommendations').innerHTML.match(/recommendation-card hex-direction/g)||[]).length,eligibleCount(selectedKeys));
 assert(elements.get('selected-augments').innerHTML.includes(a.name));assert(elements.get('flow-0').innerHTML.includes(a.name));
 assert(elements.get('flow-1').innerHTML.includes(K.units[common.ids[0]].name));assert(elements.get('flow-2').innerHTML.includes('法杖 × 2'));
}
const beforeDuplicate=elements.get('selected-augments').innerHTML;addNext(selectedKeys[1]);assert.equal(elements.get('selected-augments').innerHTML,beforeDuplicate);
choose(selectedKeys[2]);assert(!elements.get('selected-augments').innerHTML.includes(wolf.augments[2].name));
assert(elements.get('combined-recommendations').innerHTML.includes('data-next-hex='));
console.log('PASS: second/third augment additions intersect immediately, prevent disclosure toggle, retain inputs, ignore duplicates, and allow removal.');
const fullCard=elements.get('combined-recommendations').innerHTML;
assert(fullCard.includes('固定核心 · 成型变体共同保留'));assert(fullCard.includes('阵容类型'));assert(!fullCard.includes('展开看全'));
const headParts=[...fullCard.matchAll(/<summary class="recommendation-summary">([\s\S]*?)<\/summary>/g)].map(m=>m[1]).join('');
const availableWolf=wolf.augments.filter(a=>[firstHex,selectedKeys[1]].every(key=>key!==U.augmentKey(a)));
for(const a of availableWolf){assert(headParts.includes(a.name));assert(headParts.includes('rarity-'+a.rarity));}
console.log('PASS: formation/core shown and all follow-up augments visible in card summaries with rarity colors.');

const modal=elements.get('direction-dialog');modal.showModal=()=>{modal.open=true;};modal.close=()=>{modal.open=false;};
const openCard=id=>elements.get('combined-recommendations').handlers.click({preventDefault(){},target:{closest:selector=>selector==='.hex-direction'?{dataset:{direction:id}}:null}});
openCard(wolf.id);assert(modal.open);
const info={innerHTML:elements.get('direction-content').innerHTML};assert(info.innerHTML.includes('逐级过渡顺序'));
elements.get('direction-close').handlers.click();assert(!modal.open);assert(!info.innerHTML.includes('<details'));assert(info.innerHTML.includes('运营路线'));assert(info.innerHTML.includes('本级共同核心'));assert(info.innerHTML.includes('需求较多的散件'));assert(info.innerHTML.includes('推荐装备组合'));assert(info.innerHTML.includes('C级'));assert(!info.innerHTML.includes('S/A 级三件套'));assert(!info.innerHTML.includes('来源配装参考'));assert(!info.innerHTML.includes('先做主C＋主坦：'));
for(const role of ['主C','主坦','副C','副坦'])assert(info.innerHTML.includes(role));
const ungraded=K.comps.find(c=>c.source_id==='426003');
openCard(ungraded.id);const tftInfo={innerHTML:elements.get('direction-content').innerHTML};
assert(tftInfo.innerHTML.includes('推荐装备组合'));assert(!tftInfo.innerHTML.includes('没有该位置的 S/A 级组合'));assert(tftInfo.innerHTML.includes('未评级'));
console.log('PASS: one click loads full flat details; four role builds, concise component trends and unrated-source boundaries.');

assert(!info.innerHTML.includes('已选海克斯与本阵容的关系'));
assert(!info.innerHTML.includes('查看阵容来源'));
assert(info.innerHTML.includes('数据来源'));
console.log('PASS: repeated augment source panel removed; single bottom source link retained.');

openCard(wolf.id);
const levelBox={innerHTML:''};elements.set('direction-levels',levelBox);
for(const level of [4,5,6]){
 elements.get('direction-content').handlers.click({target:{closest:()=>({dataset:{viewLevel:String(level)}})}});
 assert(levelBox.innerHTML.includes(level+'级 · 当前上场组合'));
 assert.equal((levelBox.innerHTML.match(/aria-pressed="true"/g)||[]).length,1);
 assert.equal((levelBox.innerHTML.match(/级 · 当前上场组合/g)||[]).length,1);
 assert(!levelBox.innerHTML.includes('各等级可选组合'));
 assert(levelBox.innerHTML.includes('升到 '+(level+1)+' 级'));
}
const last=Math.max(...wolf.boards.map(b=>b.level));
elements.get('direction-content').handlers.click({target:{closest:()=>({dataset:{viewLevel:String(last)}})}});
assert(levelBox.innerHTML.includes('暂无更高等级记录'));
console.log('PASS: modal level nodes switch a single board panel, next-level guidance and final-level boundary.');
openCard(wolf.id);
const boardMarkup=elements.get('direction-content').innerHTML;
assert.equal((boardMarkup.match(/class="hex-cell"/g)||[]).length,28);
assert(/aria-label="第1排第7格">[\s\S]*?<strong>沃里克<\/strong>/.test(boardMarkup));
assert(boardMarkup.includes('★★★ 3星'));
assert(boardMarkup.includes('成型棋盘 · 站位与星级'));
assert(boardMarkup.slice(boardMarkup.indexOf('成型棋盘 · 站位与星级')).includes('预期成型羁绊'));
console.log('PASS: archived board coordinates, stars and traits rendered together.');

const pieces=[...boardMarkup.matchAll(/<div class="board-piece [\s\S]*?<\/div><\/div>/g)].map(m=>m[0]);
const warwick=pieces.find(p=>p.includes('<strong>沃里克</strong>'));
assert(warwick.includes('推荐配装 · A级'));
for(const item of ['无尽之刃','正义之手','水银'])assert(warwick.includes(item));
const elise=pieces.find(p=>p.includes('<strong>伊莉丝</strong>'));
assert(elise.includes('推荐配装 · C级'));
assert(elise.includes('石像鬼石板甲'));
console.log('PASS: per-unit board equipment matches recommended combinations and original grades.');

elements.get('reset').handlers.click();
const defender=K.comps.find(c=>c.source_id==='426000');
const painful=defender.augments.find(a=>a.name==='D个痛快！'||a.name==='D个痛快!');assert(painful);
choose(U.augmentKey(painful));
const assertDefender=expected=>assert.equal(elements.get('combined-recommendations').innerHTML.includes('data-direction="'+defender.id+'"'),expected);
assertDefender(false);
elements.get('flow-nav').handlers.click({target:{closest:()=>({dataset:{step:'2'}})}});
elements.get('component-stock').handlers.input({target:{dataset:{component:'大剑'},value:'2'}});
assertDefender(false);
elements.get('owned-emblems').handlers.change({target:{matches:()=>true,value:'护卫纹章',checked:true}});
assertDefender(true);
elements.get('owned-emblems').handlers.change({target:{matches:()=>true,value:'护卫纹章',checked:false}});
assertDefender(false);
console.log('PASS: no defender recommendation without emblem, including component-only state; selecting/removing emblem updates it.');
let excludedMarkup=elements.get('combined-recommendations').innerHTML.split('<details class="excluded-prerequisites">')[1];
assert(excludedMarkup&&excludedMarkup.includes('护卫 / 雷恩加尔')&&excludedMarkup.includes('转职 · 护卫纹章'));
assert(!elements.get('combined-recommendations').innerHTML.includes('class="excluded-prerequisites" open'));
elements.get('owned-emblems').handlers.change({target:{matches:()=>true,value:'护卫纹章',checked:true}});
excludedMarkup=elements.get('combined-recommendations').innerHTML.split('<details class="excluded-prerequisites">')[1]||'';
assert(!excludedMarkup.includes('护卫 / 雷恩加尔'));assertDefender(true);
console.log('PASS: missing prerequisite section starts collapsed and moves unlocked composition into recommendations.');
elements.get('units').handlers.change({target:{matches:()=>true,checked:true,value:common.ids[0]}});
elements.get('component-stock').handlers.input({target:{dataset:{component:'大剑'},value:'2'}});
const hexBeforeClear=elements.get('selected-augments').innerHTML,handBeforeClear=elements.get('flow-1').innerHTML;
elements.get('clear-items').handlers.click();
assert.equal(elements.get('selected-augments').innerHTML,hexBeforeClear);
assert.equal(elements.get('flow-1').innerHTML,handBeforeClear);
assert(!elements.get('flow-2').innerHTML.includes('大剑 × 2'));
assert(!elements.get('flow-2').innerHTML.includes('护卫纹章'));
assert(!elements.get('owned-emblems').innerHTML.includes(' checked'));
assert(!elements.get('component-stock').innerHTML.includes('value="2"'));
assertDefender(false);
assert(html.includes('id="clear-items" class="clear-action"'));
for(const id of ['clear-hex','clear','reset'])assert(html.includes('id="'+id+'" class="clear-action"'));
console.log('PASS: equipment page clear resets stock/emblems, preserves hand/augments and rechecks prerequisites; all clears prominent.');
elements.get('flow-nav').handlers.click({target:{closest:()=>({dataset:{step:'1'}})}});
for(const level of [4,9]){
 elements.get('current').value=String(level);elements.get('current').handlers.change();
 const summaries=[...elements.get('combined-recommendations').innerHTML.matchAll(/<summary class="recommendation-summary">([\s\S]*?)<\/summary>/g)].map(m=>m[1]);
 assert(summaries.length);
 for(const summary of summaries){
  assert(summary.includes('current-board-preview'));
  assert(summary.includes('当前 '+level+' 级 · 推荐上场 1/'+level+' 人'));
  assert(summary.includes('还空 '+(level-1)+' 个位置'));
  assert(summary.includes(K.units[common.ids[0]].name));
 }
}
console.log('PASS: collapsed recommendation cards show level, board members and capacity; changing 4 to 9 updates visible vacancies.');
elements.get('coach-toggle').handlers.click();
for(const level of [3,4]){
 elements.get('current').value=String(level);elements.get('current').handlers.change();
 const body=elements.get('combined-recommendations').innerHTML;
 assert(body.includes('逐级过渡教练'));assert(body.includes('上场 1/'+level+' 人'));assert(body.includes('升到 '+(level+1)+'级'));
}
elements.get('coach-toggle').handlers.click();
assert(!elements.get('combined-recommendations').innerHTML.includes('逐级过渡教练'));
console.log('PASS: coach toggles without losing hand and level changes update current and next level.');
