const assert=require('node:assert/strict'),U=require('../../templates/unified-assistant.js');
const c={id:'c',units:['a','b'],boards:[{level:2,units:['a','b'],source:'options'},{level:3,units:['a','b','x'],source:'options'},{level:3,units:['a','z','x'],source:'options'},{level:3,units:['a','z','x'],source:'options'},{level:4,units:['q'],source:'MetaTFT early_options'}]};
const K={comps:[c],units:{a:{name:'甲'},b:{name:'乙'}}};
let p=U.formationProfile(K,c);assert.equal(p.level,2);assert.equal(p.variants,3);assert.deepEqual(p.core,['a']);assert(!p.estimated);
const single={...c,boards:[c.boards[0],c.boards[0]]};p=U.formationProfile({...K,comps:[single]},single);assert.equal(p.variants,1);assert.deepEqual(p.core,[]);
const active={...c,active_final:{level:2,relation:'same-route'},final_branches:{with:{level:2,units:['a','b'],relation:'same-route'},without:{level:2,units:['a','x'],relation:'same-route'},alt:{level:2,units:['z','x'],relation:'alternative'}}};p=U.formationProfile(K,active);assert.deepEqual(p.core,['a']);assert.equal(p.variants,2);
console.log('PASS: distinct final roster intersection, early-board exclusion, single-board gap and alternative-route isolation.');
const levels=U.levelVariants(K,c);
assert.deepEqual(levels.map(x=>x.level),[2,3,4]);
assert.deepEqual(levels[1].core,['a','x']);
assert.deepEqual(levels[1].finalCore,['a']);
assert.equal(levels[1].options.length,2);
assert.equal(levels[1].options[1].records.length,2);
assert.deepEqual(levels[0].core,[]);
for(const l of levels)for(const b of l.options)assert.deepEqual([...l.core,...b.extra].sort(),[...b.units].sort());
const data=require('../../../games/assistant/data.json');
for(const comp of data.comps)for(const l of U.levelVariants(data,comp)){
 for(const b of l.options)assert.deepEqual([...l.core,...b.extra].sort(),[...b.units].sort());
 assert(l.finalCore.every(id=>l.core.includes(id)&&U.formationProfile(data,comp).core.includes(id)));
}
console.log('PASS: level core intersection, duplicate roster preservation, final-core labels and lossless combinations for every archived composition.');

for(const comp of data.comps){
 const route=U.transitionRoute(data,comp);let prev=null;
 for(const r of route){if(!r.units){prev=null;continue;}
  assert(comp.boards.some(b=>b.level===r.level&&[...new Set(b.units)].sort().join('|')===[...r.units].sort().join('|')));
  if(prev){assert.deepEqual([...prev.units.filter(id=>!r.remove.includes(id)),...r.add].sort(),[...r.units].sort());assert(prev.final.every(id=>r.units.includes(id)));}
  prev=r;
 }
}
console.log('PASS: transition targets exist in source, add/remove reconstruct next board, and final cores remain.');
const wolf=data.comps.find(c=>c.name==='献祭三狼');
const berserk=U.expectedTraits(data,wolf).find(t=>t.name==='狂战士');
assert.equal(berserk.count,3);assert.equal(berserk.active,2);
const defender=data.comps.find(c=>c.source_id==='426000');
const withEmblem={...defender,units:defender.final_branches.with_emblem.units,active_final:defender.final_branches.with_emblem};
const trait=U.expectedTraits(data,withEmblem,withEmblem.units,true).find(t=>t.name==='护卫');
assert.equal(trait.count,trait.natural+1);assert.equal(trait.emblems,1);assert.equal(trait.verified,false);
assert.equal(U.expectedTraits(data,withEmblem,withEmblem.units,false).find(t=>t.name==='护卫').count,trait.natural);
console.log('PASS: trait population versus tier and branch-only emblem counts.');
