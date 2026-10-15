const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const U=require('../../templates/unified-assistant.js'),K=require('../../../games/assistant/data.json');
const root=path.resolve(__dirname,'../../..');
const base={version:'all',tier:'all',search:'',emblem:'',augment:'',mode:'all',current:4,owned:[],ownedEmblems:[],profiles:{},bag:[],augments:[],componentStock:{'大剑':2}};
const rows=[];
for(const c of K.comps){
 if(c.version.startsWith('jcc')){
  const raw=JSON.parse(fs.readFileSync(path.join(root,'games/jcc/set18/18.3/snapshots/20261013T083011Z/data/raw/comps',c.source_id,'detail.json'))).data.conditions;
  assert.deepEqual(c.conditions.filter(x=>x.required).map(x=>[x.kind,x.id]).sort(),raw.map(x=>[x.type==='equip'?'item':'augment',x.value]).sort(),c.name+' raw conditions');
 }
 const allAugments=c.augments.map(U.augmentKey),required=c.conditions.filter(x=>x.required);
 const full={...base,augments:allAugments,ownedEmblems:required.filter(x=>x.kind==='item').map(x=>x.name)};
 for(const condition of required){
  const missing={...full,ownedEmblems:full.ownedEmblems.filter(n=>n!==condition.name),augments:full.augments.filter(k=>!c.augments.some(a=>String(a.id)===String(condition.id)&&U.augmentKey(a)===k)),owned:c.units};
  assert(!U.recommendationEligible(K,c,missing),c.name+' missing '+condition.name);
  assert.deepEqual(U.plan(K,c,missing),[]);
  assert.deepEqual(U.rankMaterials(K,[c],missing),[]);
  assert.equal(U.combinedRecommendations(K,[c],missing).top.length,0);
  assert(U.recommendationEligible(K,c,full),c.name+' condition fulfilled');
 }
 if(c.emblem_policy?.status==='optional')assert(U.recommendationEligible(K,c,{...base,augments:allAugments}),c.name+' optional emblem');
 if(c.emblem_policy?.status==='unknown'){
  assert(!U.recommendationEligible(K,c,base));
  assert(!U.recommendationEligible(K,c,{...base,ownedEmblems:c.emblems}),'ownership does not resolve missing board evidence');
 }
 rows.push({id:c.id,name:c.name,required:required.map(x=>({kind:x.kind,name:x.name})),emblemPolicy:c.emblem_policy?.status||null,recommendedWithoutPrerequisites:U.recommendationEligible(K,c,base),source:c.source});
}
assert.equal(rows.filter(r=>r.required.some(x=>x.kind==='item')).length,5);
assert.equal(rows.filter(r=>r.required.some(x=>x.kind==='augment')).length,2);
assert.equal(rows.filter(r=>r.emblemPolicy==='optional').length,5);
console.log('PASS: all 37 compositions audited; raw JCC requirements preserved; every hard prerequisite blocks cards, boards, material ranking and top recommendations; 5 optional routes retained; unknown branch excluded.');
if(process.argv.includes('--write-audit'))fs.writeFileSync(path.join(root,'research/2026-10-15-dual-source/prerequisite-audit.json'),JSON.stringify({scope:'Archived project snapshots, not fresh live-meta verification',sources:['games/jcc/set18/18.3/snapshots/20261013T083011Z/data/raw/comps/*/detail.json','research/2026-10-15-dual-source/tft/emblem-verification/audit.json'],rows},null,2)+'\n');
