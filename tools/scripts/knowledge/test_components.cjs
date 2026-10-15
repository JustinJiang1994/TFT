const assert=require('node:assert/strict'),U=require('../../templates/unified-assistant.js'),K=require('../../../games/assistant/data.json');
const rod=Object.keys(K.items).find(i=>i.startsWith('tft')&&K.items[i].name==='无用大棒'),bow=Object.keys(K.items).find(i=>i.startsWith('tft')&&K.items[i].name==='反曲之弓');
const rage=Object.keys(K.items).find(i=>i.startsWith('tft')&&K.items[i].name==='鬼索的狂暴之刃');
assert.deepEqual(U.recipeParts(K,rage).sort(),[rod,bow].sort());
let x=U.componentSummary(K,[{unit:'a',build:{items:[rage,rage]}},{unit:'b',build:{items:[rage]}}]);assert.equal(new Map(x.counts).get(rod),3);assert.equal(new Map(x.counts).get(bow),3);
assert.equal(U.recipeParts({items:{a:{version:'x',recipe:['a']}}},'a'),null);
assert.equal(U.recipeParts({items:{a:{version:'x',recipe:['b']},b:{version:'y',component:true}}},'a'),null);
assert.equal(U.componentSummary(K,[{unit:'a',build:{items:['unknown']}}]).special.length,1);
for(const c of K.comps){const p=U.componentPlan(K,c);const used=p.rows.filter(r=>!r.missing).map(r=>r.unit);assert.equal(used.length,new Set(used).size);assert(used.every(i=>c.units.includes(i)));assert(p.rows.every(r=>r.missing||[...c.builds,...(c.cross_game_builds||[])].includes(r.build)));}
const c=K.comps.find(c=>c.source_id==='426029');const no=U.activeComp(K,c,{owned:[],ownedEmblems:[],bag:[]}),yes=U.activeComp(K,c,{owned:[],ownedEmblems:c.emblems,bag:[]});const p=U.componentPlan(K,no);assert(p.rows.find(r=>r.role==='主C').unit.endsWith('DA_18_MasterYi_AD'));assert.notDeepEqual(U.componentPlan(K,yes).total.counts,p.total.counts);
console.log('PASS: recipe expansion, repeated items across carriers, unknown/special/cyclic recipes, source-only builds, unique carriers, active branch changes totals.');
