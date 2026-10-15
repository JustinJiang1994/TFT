const assert=require('node:assert/strict'),K=require('../../../games/assistant/data.json'),U=require('../../templates/unified-assistant.js');
let count=0;
for(const c of K.comps)for(const b of c.cross_game_builds||[]){
 count++;assert(c.version.startsWith('jcc'));assert(b.cross_game);
 assert(!c.builds.some(x=>x.unit===b.unit&&x.items.length===3));
 const donor=K.comps.find(x=>x.id===b.donor_id);assert(donor.version.startsWith('tft'));
 assert.equal(K.units[b.unit].name,K.units[b.donor_unit].name);assert.equal(K.units[b.unit].cost,K.units[b.donor_unit].cost);
 assert(donor.builds.some(x=>x.unit===b.donor_unit&&JSON.stringify(x.items)===JSON.stringify(b.donor_items)));
 assert.equal(b.avg,null);assert.equal(b.count,null);assert(b.overlap>=3);
 for(let i=0;i<3;i++){
  assert.equal(K.items[b.items[i]].version,c.version);
  assert.equal(K.items[b.items[i]].name,K.items[b.donor_items[i]].name);
  assert.deepEqual(U.recipeParts(K,b.items[i]).map(i=>K.items[i].name).sort(),U.recipeParts(K,b.donor_items[i]).map(i=>K.items[i].name).sort());
 }
 assert(U.recommendedBuilds(c,b.unit)[0].cross_game);
}
assert(count>0);
for(const c of K.comps)for(const h of c.heroes)if(c.builds.some(b=>b.unit===h.id&&b.items.length===3))assert(U.recommendedBuilds(c,h.id).every(b=>!b.cross_game));
console.log('PASS:',count,'TFT references preserve native builds, donor identity/role/provenance and recipe equivalence; no TFT statistics relabeled as JCC.');
