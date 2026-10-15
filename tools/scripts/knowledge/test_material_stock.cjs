const assert=require('node:assert/strict'),K=require('../../../games/assistant/data.json'),U=require('../../templates/unified-assistant.js');
assert.equal(U.componentName('暴风之剑'),U.componentName('暴风大剑'));
const rod=Object.keys(K.items).find(i=>K.items[i].component&&K.items[i].name==='无用大棒');
const sword=Object.keys(K.items).find(i=>K.items[i].component&&K.items[i].name==='暴风之剑');
const stock=U.cleanStock(K,{'法杖':2,'大剑':1,'拳套':-4,'锁子甲':1.9});assert.equal(stock.拳套,0);assert.equal(stock.锁子甲,1);
const x=U.matchMaterials(K,{counts:[[rod,3],[sword,2]]},stock);assert.equal(x.matched,3);assert.deepEqual(x.missing,{'法杖':1,'大剑':1});
assert.deepEqual(U.matchMaterials(K,{counts:[]},stock).ratio,0);
const s={version:'all',owned:[],ownedEmblems:[],bag:[],componentStock:{'法杖':2,'大剑':1}};
const cs=K.comps.map(c=>U.activeComp(K,c,s)),rows=U.rankMaterials(K,cs,s);
for(const r of rows){assert(r.primary.matched<=3);assert(r.total.matched<=3);assert(r.primary.matched<=r.primary.total);for(const [n,opts] of Object.entries(r.finish))for(const x of opts){const parts=U.recipeParts(K,x.item);const gap=U.matchMaterials(K,{counts:parts.map(i=>[i,1])},U.cleanStock(K,s.componentStock));assert.equal(Object.values(gap.missing).reduce((a,b)=>a+b,0),1);assert.equal(gap.missing[n],1);}}
const regular=rows.filter(r=>r.ready&&!r.alternative&&!r.uncertain);for(let i=1;i<regular.length;i++)assert(regular[i-1].confidence>=regular[i].confidence);
assert.deepEqual(U.rankMaterials(K,[],s),[]);
console.log('PASS: count matching, aliases, input normalization, inventory reuse prevention in totals, incomplete evidence ordering, single-piece completion priority and empty candidates.');
