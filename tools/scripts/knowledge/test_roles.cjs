const assert=require('node:assert/strict'),K=require('../../../games/assistant/data.json'),U=require('../../templates/unified-assistant.js');
const comp=id=>K.comps.find(c=>c.source_id===id), state={version:'all',owned:[],ownedEmblems:[],profiles:{},bag:[]};
const kayle=U.activeComp(K,comp('426021'),state);
for(const n of ['韦鲁斯','凯尔','瑟庄妮'])assert(kayle.heroes.some(h=>K.units[h.id].name===n&&h.core));
assert(kayle.heroes.find(h=>K.units[h.id].name==='瑟庄妮').role_note.includes('三星'));
const without=U.activeComp(K,comp('426001'),state);
assert(without.heroes.some(h=>K.units[h.id].name==='奈德丽'&&h.core));
assert(!without.heroes.some(h=>K.units[h.id].name==='绯红印记树怪'));
const withEmblem=U.activeComp(K,comp('426001'),{...state,ownedEmblems:comp('426001').emblems});
assert(!withEmblem.heroes.some(h=>K.units[h.id].name==='奈德丽'&&h.core));
for(const c of K.comps.filter(c=>c.version.startsWith('tft-'))){for(const hs of [c.heroes,...Object.values(c.final_branches||{}).map(b=>b.heroes)])for(const h of hs){if(h.role_candidate)assert(!h.core);if(h.role_confirmed)assert(h.role_source&&h.role_note);}}
assert(!comp('426037').heroes.some(h=>h.core));assert(!comp('426010').heroes.some(h=>h.core));
console.log('PASS: source roles reach final boards, conditional tank note preserved, alternatives independently sourced, candidates excluded from core scoring, unresolved routes stay gaps.');
