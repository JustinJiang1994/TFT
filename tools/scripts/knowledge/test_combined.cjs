const assert=require('node:assert/strict'),U=require('../../templates/unified-assistant.js');
const units=Object.fromEntries(['a','b','c','d'].map(i=>[i,{name:i,cost:1,version:'v',family:i,traits:[],purchasable:true}]));
const items={rod:{name:'无用大棒',component:true,version:'v'},sword:{name:'暴风大剑',component:true,version:'v'},hat:{name:'法装',recipe:['rod','rod'],version:'v'},blade:{name:'物装',recipe:['sword','sword'],version:'v'}};
function comp(id,ids,item){return {id,name:id,version:'v',units:ids,heroes:ids.map((id,i)=>({id,role:i?'主坦':'主C',core:true})),boards:[],builds:ids.map(unit=>({unit,items:[item,item,item],count:10})),conditions:[],augments:[],emblems:[]};}
const a=comp('A',['a','b'],'hat'),b=comp('B',['c','d'],'blade'),K={units,items,comps:[a,b]};
const base={current:4,owned:['a','b','c','d'],ownedEmblems:[],bag:[],componentStock:{'法杖':2}};
assert.equal(U.combinedRecommendations(K,K.comps,base).top[0].c.id,'A');
assert.equal(U.combinedRecommendations(K,K.comps,{...base,componentStock:{'大剑':2}}).top[0].c.id,'B');
assert.equal(U.combinedRecommendations(K,K.comps,{...base,owned:['c','d'],componentStock:{}}).top[0].c.id,'B');
assert.equal(U.combinedRecommendations(K,K.comps,{...base,owned:['a','b'],componentStock:{}}).top[0].c.id,'A');
const r=U.combinedRecommendations(K,K.comps,base).top[0];assert.equal(r.craft.steps.length,1);assert.equal(r.craft.remaining['法杖'],0);assert(r.craft.steps.every(x=>r.board.units.includes(x.holder)));
const blocked={...a,id:'blocked',conditions:[{required:true,kind:'item',name:'required'}]};assert.equal(U.combinedRecommendations(K,[blocked],base).top.length,0);
const partial={...a,id:'partial',builds:[]};assert.equal(U.combinedRecommendations(K,[partial],base).top.length,0);
assert.equal(U.combinedRecommendations(K,[a,{...a,id:'duplicate'},b],base).top.length,2);
assert.equal(U.combinedRecommendations(K,[],base).top.length,0);
assert.equal(U.combinedRecommendations(K,K.comps,{...base,owned:[]}).top.length,0);
console.log('PASS: hand and materials independently change rankings, sequential crafting respects inventory, legal on-board holders, prerequisites/coverage gates, roster deduplication and empty states.');
