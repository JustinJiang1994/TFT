(function(root){
'use strict';
const unique=a=>[...new Set(a)];
const includes=(units,owned)=>owned.every(x=>units.includes(x));
function gaps(comp,state){return comp.conditions.filter(x=>!(x.kind==='augment'?state.augments:state.emblems).includes(x.id));}
function passes(comp,state){return (state.group==='全部'||comp.group===state.group)&&state.augments.every(id=>comp.augments.some(a=>a.id===id)||comp.conditions.some(a=>a.kind==='augment'&&a.id===id))&&(!state.emblemOnly||!state.emblems.length||state.emblems.some(id=>comp.optional_emblems.includes(id)||comp.conditions.some(a=>a.kind==='item'&&a.id===id)));}
function boards(comp,level,owned){const seen=new Set();return comp.stages.filter(b=>b.level===Number(level)&&includes(b.units,owned)).filter(b=>{const k=[...b.units].sort().join(',');if(seen.has(k))return false;seen.add(k);return true;});}
function fill(rows,base,added){const owned=unique([...base,...added]);const matches=rows.filter(b=>includes(b.units,owned));const count={};matches.forEach(b=>unique(b.units).filter(u=>!owned.includes(u)).forEach(u=>count[u]=(count[u]||0)+1));return {owned,matches,frequency:Object.entries(count).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))};}
function equipment(rows,owned){const n={};owned.forEach(x=>n[x]=(n[x]||0)+1);return rows.filter(r=>{const count={};r.items.forEach(x=>count[x]=(count[x]||0)+1);return Object.entries(n).every(([i,k])=>(count[i]||0)>=k);}).map(r=>{const left=[...r.items];owned.forEach(x=>left.splice(left.indexOf(x),1));return {...r,missing:left};});}
const api={unique,includes,gaps,passes,boards,fill,equipment};root.KnowledgeEngine=api;if(typeof module!=='undefined')module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
