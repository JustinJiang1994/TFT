'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const K=read('games/assistant/data.json'),V=read('research/2026-10-15-dual-source/tft/verification/verified-sa.json');
const U=require('../../templates/unified-assistant.js'),E=require('../../templates/knowledge-engine.js');
const state={version:'all',mode:'all',current:6,target:8,tier:'all',search:'',owned:[],emblem:'',augment:''};
assert.equal(U.select(K,state).length,37);
const [j,t]=K.versions;assert.equal(U.select(K,{...state,version:j.id}).length,15);assert.equal(U.select(K,{...state,version:t.id}).length,22);
const tft=K.comps.filter(c=>c.version===t.id);
assert.deepEqual(tft.map(c=>c.source_id).sort(),V.selected.map(c=>c.id).sort());
assert.equal(U.select(K,{...state,version:t.id,tier:'S'}).length,6);
assert.equal(U.select(K,{...state,version:t.id,tier:'A'}).length,16);
assert.equal(U.select(K,{...state,search:'不存在的阵容'}).length,0);
for(const c of K.comps){
 assert(c.id.startsWith(c.version+':'));assert(c.units.every(i=>K.units[i]?.version===c.version));
 assert(c.boards.every(b=>b.units.every(i=>K.units[i]?.version===c.version)));
 assert(c.builds.every(b=>b.items.every(i=>K.items[i]?.version===c.version)));
}
for(const c of tft){
 const d=read('research/2026-10-15-dual-source/tft/raw/comps/'+c.source_id+'.json').results;
 assert.equal(c.boards.length,Object.values(d.options).flat().length+Object.values(d.early_options).flat().length);
 assert(c.boards.every(b=>b.top4===null));assert(c.builds.every(b=>b.tier===null));
 assert.equal(c.builds.length,d.builds.filter(b=>b.buildName?.length).length);
 const row=c.boards[0],owned=[row.units[0]],s={...state,mode:'current',current:row.level,owned};
 assert(U.select(K,s).some(x=>x.id===c.id));assert(U.select(K,s).every(x=>x.version===t.id));
 assert(U.boardRows(c,s).every(b=>b.units.includes(owned[0])));
}
// Future query is independent of current-level success.
const synthetic={...tft[0],boards:[{level:8,units:['a'],top4:null,avg:4,count:10}]};
assert.equal(U.boardRows(synthetic,{...state,mode:'current',current:6,owned:['a']}).length,0);
assert.equal(U.boardRows(synthetic,{...state,mode:'future',target:8,owned:['a']}).length,1);
const switched=U.changeVersion({...state,owned:['old'],emblem:'old',augment:'old'},t.id);
assert.deepEqual(switched.owned,[]);assert.equal(switched.augment,'');assert.equal(switched.emblem,'');
assert.equal(U.select(K,switched).length,22);
// Same-name units across games do not match each other.
const ju=Object.entries(K.units).find(([id,u])=>u.version===j.id&&Object.values(K.units).some(tu=>tu.version===t.id&&tu.name===u.name));
assert(ju);assert.equal(U.select(K,{...state,version:t.id,owned:[ju[0]]}).length,0);
const pair=tft.flatMap(c=>c.builds).find(b=>new Set(b.items).size<b.items.length);
assert(pair);const repeated=pair.items.find(i=>pair.items.filter(x=>x===i).length>1);
assert.equal(E.equipment([pair],[repeated,repeated])[0].missing.length,pair.items.length-2);
const html=fs.readFileSync(path.join(root,'games/assistant/index.html'),'utf8');assert.equal((html.split('<details id="static">')[1].split('</details>')[0].match(/<li>/g)||[]).length,37);
assert.deepEqual(JSON.parse(html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1]),K);
console.log('PASS: 37 compositions, exact 22 TFT S/A, version/tier/search filters, source-scoped IDs, all board records, independent future matching, version reset, duplicate equipment, embedded data and static fallback.');

const groups=U.augmentGroups(K,state);
assert.equal(new Set(groups.map(g=>g.key)).size,groups.length);
for(const g of groups){
 const hits=U.select(K,{...state,augments:[g.key]});
 assert.deepEqual(hits.map(c=>c.id).sort(),g.comps.slice().sort());
 assert(hits.every(c=>c.augments.some(a=>U.augmentKey(a)===g.key)));
}
const shared=groups.find(g=>new Set(g.comps.map(id=>K.comps.find(c=>c.id===id).version)).size===2);
assert(shared,'must merge at least one same-name/rarity entry across games');
for(const v of K.versions)assert(U.select(K,{...state,version:v.id,augments:[shared.key]}).every(c=>c.version===v.id));
const a=groups[0],b=groups[1];assert.deepEqual(U.select(K,{...state,augments:[a.key,b.key]}).map(c=>c.id).sort(),a.comps.filter(id=>b.comps.includes(id)).sort());
assert.equal(U.select(K,{...state,augments:['not-a-recommendation']}).length,0);
assert.deepEqual(U.changeVersion({...state,augments:[a.key]},t.id).augments,[]);
const audit=read('research/2026-10-15-dual-source/tft/augment-verification/audit.json');
assert.equal(audit.rows.length,22);assert.equal(audit.covered,21);
assert.equal(tft.filter(c=>c.augments.length).length,21);
for(const c of tft)for(const a of c.augments){
 assert.equal(a.avg,null);assert.equal(a.count,null);assert(a.sources.length);
 assert(a.sources.every(p=>(['S','A'].includes(p.tier)||p.recommendation_label)&&['exact','related'].includes(p.match)&&p.author&&p.updated_at&&p.url));
}
assert(tft.filter(c=>!c.augments.length).every(c=>c.augment_gap));
console.log('PASS: '+groups.length+' deduplicated recommendation entries; single/multiple augment intersections, game filters, source evidence, and all 22 coverage statuses.');

const external=read('research/2026-10-15-dual-source/tft/augment-external/audit.json');
assert.equal(external.rows.length,10);assert.equal(external.rows.reduce((n,r)=>n+r.augments.length,0),67);
assert.deepEqual(tft.filter(c=>!c.augments.length).map(c=>c.source_id),['426037']);
for(const row of external.rows){
 const c=tft.find(c=>c.source_id===row.id);assert(c);
 for(const a of row.augments){assert(c.augments.some(x=>x.id===a.id));assert(U.select(K,{...state,augments:[U.augmentKey(a)]}).some(x=>x.id===c.id));}
 assert(row.source.source_sha256);assert(row.source.source_board.length>0);
}
assert(external.rows.some(r=>r.augments.some(a=>a.sources.some(p=>p.global_augment_tier==='C'&&p.tier===null))));
console.log('PASS: 10 externally matched lineups / 67 explicit recommendations; remaining Brambleback gap; global grades distinct from comp recommendations.');
