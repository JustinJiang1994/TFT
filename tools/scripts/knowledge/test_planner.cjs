const assert=require('node:assert/strict');
const {plan,directions,naturalTraits,unitRole}=require('../../templates/unified-assistant.js');
const K=require('../../../games/assistant/data.json');
const base={version:'all',current:4,mode:'all',tier:'all',search:'',owned:[],augments:[],emblem:'',augment:''};
const c=K.comps.find(c=>c.boards.some(b=>b.level===4)&&c.augments.length);
const a=c.augments[0];const state={...base,augments:[JSON.stringify([a.name,Number(a.rarity)||0])],owned:[...new Set([...c.boards.find(b=>b.level===4).units,...c.units])]};
assert.equal(directions(K,state).length,directions(K,{...state,owned:[]}).length,'extra hand units must not remove directions');
const rows=plan(K,c,state);assert(rows.length);assert.equal(rows[0].units.length,4);assert(rows[0].bench.length>0);
for(const p of rows){assert(p.units.every(i=>state.owned.includes(i)));assert(!p.bench.some(i=>p.units.includes(i)));assert.equal(p.units.length+p.bench.length,state.owned.length);assert(p.units.every(i=>K.units[i].version===c.version));}
assert.deepEqual(plan(K,c,{...state,owned:[]}),[]);
assert.deepEqual(plan(K,c,{...state,owned:Object.keys(K.units).filter(i=>K.units[i].version!==c.version).slice(0,5)}),[]);
const one=rows[0].units[0];assert.deepEqual(naturalTraits(K,[one]),naturalTraits(K,[one,one]));
const core=c.heroes.find(h=>h.core);if(core)assert.match(unitRole(c,core.id).label,/后期核心/);
const fixture={...c,heroes:[],units:[],boards:[]};assert.match(unitRole(fixture,one).label,/打工牌/);
const tft=K.comps.find(c=>c.version.startsWith('tft')&&!c.situational);const ids=Object.keys(K.units).filter(i=>K.units[i].version===tft.version&&!K.units[i].special).slice(0,15);
console.time('15-card pool');const tp=plan(K,tft,{...base,owned:ids});console.timeEnd('15-card pool');assert(tp[0].units.length<=4);assert(tp[0].traits.every(t=>!t.verified&&t.active===0));
const dragon=Object.keys(K.units).find(i=>K.units[i].special&&K.units[i].version===tft.version);if(dragon){const p=plan(K,tft,{...base,owned:[ids[0],dragon]})[0];assert(p.excluded.includes(dragon));assert(!p.units.includes(dragon));}
console.log('PASS: pool subset, bench, direction retention, version isolation, core labels, duplicate handling, TFT uncertainty, special slots.');
