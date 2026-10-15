const assert=require('node:assert/strict'),K=require('../../../games/assistant/data.json');
const {eligibility,plan,augmentKey}=require('../../templates/unified-assistant.js');
const state={owned:[],bag:[],profiles:{},ownedEmblems:[],augments:[],current:4};
const cs=K.comps.filter(c=>c.conditions.some(x=>x.required&&x.kind==='item'));assert.equal(cs.length,5);
for(const c of cs){const n=c.conditions.find(x=>x.kind==='item').name;assert(!eligibility(K,c,state).ready);assert.deepEqual(plan(K,c,state),[]);assert(!eligibility(K,c,{...state,emblem:n}).ready,'search filter is not ownership');assert(eligibility(K,c,{...state,ownedEmblems:[n]}).ready);const item=Object.keys(K.items).find(i=>K.items[i].version===c.version&&K.items[i].name===n);assert(eligibility(K,c,{...state,bag:[item]}).ready);const foreign=Object.keys(K.items).find(i=>K.items[i].version!==c.version&&K.items[i].name===n);if(foreign)assert(!eligibility(K,c,{...state,bag:[foreign]}).ready);}
for(const c of K.comps.filter(c=>c.conditions.some(x=>x.kind==='augment'))){assert(!eligibility(K,c,state).ready);const a=c.augments.find(a=>c.conditions.some(x=>String(x.id)===String(a.id)));if(a)assert(eligibility(K,c,{...state,augments:[augmentKey(a)]}).ready);}
const t=K.comps.find(c=>c.emblem_policy?.status==='unknown');assert.equal(eligibility(K,t,state).missing.length,0);assert(eligibility(K,t,state).pending.length);assert(eligibility(K,t,state).ready);
const optional=K.comps.filter(c=>c.emblem_policy?.status==='optional');assert.equal(optional.length,5);for(const c of optional)assert(eligibility(K,c,state).ready);
const required=K.comps.filter(c=>c.emblem_policy?.status==='required');assert.equal(required.length,2);for(const c of required)assert(!eligibility(K,c,state).ready);
console.log('PASS: hard emblem gates, ownership vs filters, inventory recognition, version isolation, augment prerequisite and uncertain TFT branches.');
