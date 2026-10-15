const assert=require('node:assert/strict'),K=require('../../../games/assistant/data.json');
const {activeComp,boardDifference,eligibility,plan}=require('../../templates/unified-assistant.js');
const base={owned:[],profiles:{},bag:[],ownedEmblems:[],augments:[],current:4};
const get=id=>K.comps.find(c=>c.source_id===id&&c.version.startsWith('tft'));
assert.equal(K.comps.filter(c=>Object.keys(c.final_branches||{}).length).length,7);
for(const id of ['426000','426001','426002','426029']){
 const c=get(id),no=activeComp(K,c,base),yes=activeComp(K,c,{...base,ownedEmblems:c.emblems});
 assert.equal(no.active_final.key,'without_emblem');assert.equal(yes.active_final.key,'with_emblem');
 assert.equal(no.units.length,no.active_final.level);assert.equal(yes.units.length,yes.active_final.level);
 assert.equal(no.avg,null);assert.equal(no.tier,'未单评');assert(eligibility(K,no,base).ready);
 assert(no.heroes.every(h=>no.units.includes(h.id)));assert(no.builds.every(b=>no.units.includes(b.unit)));
 const item=Object.keys(K.items).find(i=>K.items[i].version===c.version&&K.items[i].name===c.emblems[0]);
 assert.equal(activeComp(K,c,{...base,bag:[item]}).active_final.key,'with_emblem');
 assert.equal(activeComp(K,c,base).active_final.key,'without_emblem');
}
const c=get('426029'),no=activeComp(K,c,base),yes=activeComp(K,c,{...base,ownedEmblems:c.emblems}),diff=boardDifference(no.units,yes.units);
assert.deepEqual(diff.add.map(i=>K.units[i].name),['阿利斯塔']);assert.deepEqual(diff.remove.map(i=>K.units[i].name),['蔚']);
const f=get('426002');assert.deepEqual(f.final_branches.with_emblem.units,f.final_branches.without_emblem.units);
const alt=activeComp(K,get('426001'),base);assert.equal(alt.active_final.relation,'alternative');assert(!alt.units.some(i=>K.units[i].name==='绯红印记树怪'));assert(alt.units.some(i=>K.units[i].name==='奈德丽'));
assert(activeComp(K,get('426021'),{...base,ownedEmblems:get('426021').emblems}).branch_fallback);
assert(activeComp(K,get('426037'),base).branch_gap);
const hand=alt.units.slice(0,5);const p=plan(K,get('426001'),{...base,owned:hand});assert(p.length);assert.equal(p[0].units.length,4);
console.log('PASS: 4 paired boards, 3 baseline fallbacks, one honest gap; automatic emblem/inventory switch, exact swaps, branch-specific roles/builds and no inherited ratings.');
