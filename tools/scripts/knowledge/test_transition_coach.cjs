const assert=require('node:assert/strict');
const A=require('../../templates/unified-assistant.js'),K=require('../../../games/assistant/data.json');
const s={version:'all',current:3,owned:[],augments:[],ownedEmblems:[],profiles:{},bag:[]};
const c=K.comps.find(c=>c.transition_boards?.some(b=>b.level===4)&&A.recommendationEligible(K,c,s));
assert(c);
s.owned=[...new Set(c.transition_boards.filter(b=>b.level===4).flatMap(b=>b.units))].slice(0,5);
assert.equal(s.owned.length,5);
const r=A.transitionCoach(K,[c],s)[0];assert.equal(r.current.units.length,3);assert.equal(r.current.bench.length,2);
assert(r.current.units.every(i=>s.owned.includes(i)));assert(!r.evidence.length);assert(r.next.length);
for(const n of r.next){assert.equal(n.level,4);assert(n.find.every(i=>!s.owned.includes(i)));assert(n.fromBench.every(i=>s.owned.includes(i)&&!r.current.units.includes(i)));assert.deepEqual([...r.current.units.filter(i=>!n.remove.includes(i)),...n.add].sort(),[...n.units].sort());assert(r.core.every(i=>n.units.includes(i)));}
assert.equal(A.transitionCoach(K,[c],{...s,current:4})[0].current.units.length,4);
assert.equal(A.transitionCoach(K,[c],{...s,current:11})[0].next.length,0);
assert.equal(A.transitionCoach(K,[c],{...s,owned:[]}).length,0);
for(const x of K.comps.filter(c=>!A.recommendationEligible(K,c,s)))assert.equal(A.transitionCoach(K,[x],s).length,0);
assert.equal(K.comps.filter(c=>c.transition_boards?.length).length,15);
console.log('PASS: 5-to-3 selection, bench, next source boards, upgrade differences, protected cores, level capacity, gaps and prerequisite gates.');
const ranked=A.transitionCoach(K,K.comps,s);
for(let i=1;i<ranked.length;i++)assert(ranked[i-1].similarity>=ranked[i].similarity);
for(const x of ranked){assert(x.similarity>=0&&x.similarity<=1);assert(!x.current.bench.some(id=>x.current.units.some(u=>K.units[u].name===K.units[id].name)));}
console.log('PASS: source coverage ordering and no duplicate named bench/on-board entries.');
