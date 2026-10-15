(function(root){
'use strict';
function scoped(K,s){return K.comps.filter(c=>s.version==='all'||c.version===s.version);}
function boardRows(c,s){return c.boards.filter(b=>b.level===Number(s.mode==='future'?s.target:s.current)&&s.owned.every(i=>b.units.includes(i)));}
function augmentKey(a){return JSON.stringify([a.name,Number(a.rarity)||0]);}
function augmentGroups(K,s){const groups=new Map();for(const c of scoped(K,s))for(const a of c.augments){const key=augmentKey(a);if(!groups.has(key))groups.set(key,{key,name:a.name,rarity:Number(a.rarity)||0,comps:[]});const g=groups.get(key);if(!g.comps.includes(c.id))g.comps.push(c.id);}return [...groups.values()].sort((a,b)=>b.comps.length-a.comps.length||a.name.localeCompare(b.name,'zh-CN'));}
function select(K,s){return scoped(K,s).filter(c=>(s.augments||[]).every(key=>c.augments.some(a=>augmentKey(a)===key))&&(s.tier==='all'||c.tier===s.tier)&&(!s.search||(c.name+c.units.map(i=>K.units[i].name).join(' ')).toLowerCase().includes(s.search.toLowerCase()))&&(!s.emblem||[...c.emblems,...c.conditions.filter(x=>x.kind==='item').map(x=>x.name)].includes(s.emblem))&&(!s.augment||c.augments.some(a=>c.version+':'+a.id===s.augment))&&(s.mode==='all'?s.owned.every(i=>c.units.includes(i)):boardRows(c,s).length>0));}
function changeVersion(s,version){return {...s,version,owned:[],profiles:{},bag:[],ownedEmblems:[],emblem:'',augment:'',augments:[]};}
// Hand is an available pool. It never filters out an augment's final directions.
function directions(K,s){return select(K,{...s,owned:[],mode:'all'}).map(c=>activeComp(K,c,s));}
function emblemFit(K,c,s){
 const chosen=[...new Set(s.ownedEmblems||[])],counts=naturalTraits(K,c.units),slots=new Map(c.units.map(id=>[id,0]));
 const rows=chosen.map(name=>{const trait=name.replace(/纹章$/, ''),t=counts.find(t=>t.name===trait),entry=Object.entries(K.trait_catalog||{}).find(([id,x])=>id.startsWith(c.version+':')&&x.name===trait);
  const holder=entry&&c.units.find(id=>!(K.units[id]?.traits||[]).includes(entry[0])&&slots.get(id)<3&&K.units[id]?.purchasable!==false&&!K.units[id]?.special);
  if(holder)slots.set(holder,slots.get(holder)+1);
  const before=t?.count||0,after=before+(holder?1:0),verified=!!entry?.[1].verified,thresholds=verified?entry[1].thresholds||[]:[],old=Math.max(0,...thresholds.filter(n=>n<=before)),active=Math.max(0,...thresholds.filter(n=>n<=after));
  return {name,trait,before,after,holder,verified,old,active,gain:active>old};});
 const score=rows.length?rows.reduce((n,r)=>n+(r.holder&&r.before>0?(r.gain?1:0.5):0),0)/rows.length:0;
 return {rows,score};
}
function transitionCoach(K,cs,s){
 const level=Number(s.current),out=[];
 for(const raw of cs){const c=activeComp(K,raw,s);if(!recommendationEligible(K,c,s))continue;
  const boards=c.active_final?c.boards:(c.transition_boards||c.boards);
  const options=plan(K,{...c,boards},s);if(!options.length||!options[0].units.length)continue;
  const current=options[0],held=new Set((s.owned||[]).filter(id=>K.units[id]?.version===c.version));
  current.bench=current.bench.filter(id=>!current.units.some(u=>K.units[u].name===K.units[id].name));
  const same=(a,b)=>a.length===b.length&&a.every(id=>b.includes(id));
  const evidence=boards.filter(b=>b.level===level&&same(b.units,current.units));
  const finalCore=formationProfile(K,c).core,protectedIds=current.units.filter(id=>finalCore.includes(id));
  const seen=new Set(),next=[];
  for(const b of boards.filter(b=>b.level===level+1)){
   const ids=[...new Set(b.units)],key=[...ids].sort().join('|');if(seen.has(key))continue;seen.add(key);
   if(ids.some(id=>!K.units[id]||K.units[id].purchasable===false||K.units[id].special)||ids.length>level+1||!protectedIds.every(id=>ids.includes(id)))continue;
   const diff=boardDifference(current.units,ids),find=ids.filter(id=>!held.has(id)),fromBench=diff.add.filter(id=>held.has(id));
   next.push({units:ids,find,fromBench,add:diff.add,remove:diff.remove,keep:diff.keep,core:ids.filter(id=>finalCore.includes(id)),source:b.source,count:b.count,stars:b.stars||{},level:b.level});
  }
  next.sort((a,b)=>a.find.length-b.find.length||a.remove.length-b.remove.length||b.core.length-a.core.length||(b.count||0)-(a.count||0));
  const matching=boards.filter(b=>b.level===level),matchPool=matching.length?matching:boards.filter(b=>b.level===level+1);
  const matches=matchPool.map(b=>({board:b,hits:b.units.filter(id=>held.has(id)).length})).sort((a,b)=>b.hits/b.board.units.length-a.hits/a.board.units.length||b.hits-a.hits);
  const match=matches[0],similarity=match?match.hits/match.board.units.length:0;
  out.push({c,current,evidence,next,match,similarity,emblem:emblemFit(K,c,s),core:protectedIds,missingSlots:Math.max(0,level-current.units.length)});
 }
 return out.sort((a,b)=>(s.ownedEmblems?.length?(0.6*b.similarity+0.4*b.emblem.score)-(0.6*a.similarity+0.4*a.emblem.score):b.similarity-a.similarity)||(b.match?.hits||0)-(a.match?.hits||0)||(a.next[0]?.find.length??99)-(b.next[0]?.find.length??99)||b.current.score-a.current.score);
}
function naturalTraits(K,ids){const counts=new Map();for(const id of [...new Set(ids)])for(const t of new Set(K.units[id]?.traits||[]))counts.set(t,(counts.get(t)||0)+1);return [...counts].map(([id,count])=>{const t=K.trait_catalog?.[id]||{name:id,thresholds:[]};return {id,name:t.name,count,active:Math.max(0,...t.thresholds.filter(n=>n<=count)),verified:t.verified};}).sort((a,b)=>b.active-a.active||b.count-a.count);}
function unitRole(c,id){const h=c.heroes.find(h=>h.id===id);if(h?.core)return {label:'后期核心 · '+h.role,evidence:h.evidence};if(c.units.includes(id))return {label:'终局成员 · 核心职责未确认',evidence:'本方向代表棋盘成员，不等于主C'};if(c.boards.some(b=>b.level>=8&&b.units.includes(id)))return {label:'后期变体成员',evidence:'出现在本方向8级以上来源棋盘'};return {label:'打工牌（相对本方向）',evidence:'未出现在已收录终局棋盘；不代表应立即卖掉'};}
function coreAnnotations(K,cs){
 const map={};
 for(const c of cs){const fixed=formationProfile(K,c).core;
  for(const id of c.units){const h=c.heroes.find(h=>h.id===id),role=h?.role||'',tags=[];
   if(h?.core&&!role.includes('候选')){if(/C|输出/.test(role))tags.push({kind:'carry',label:role});else if(role.includes('坦'))tags.push({kind:'tank',label:role});}
   if(fixed.includes(id))tags.push({kind:'fixed',label:'成型固定核心'});
   if(tags.length)(map[id]??=[]).push({comp:c.name,version:c.version,tags});
  }
 }
 return map;
}
function unitGroups(K,s){const gs=new Map();for(const [id,u] of Object.entries(K.units)){if(u.purchasable===false||!(u.cost>0)||(s.version!=='all'&&u.version!==s.version))continue;const key=JSON.stringify([u.name,u.cost]);if(!gs.has(key))gs.set(key,{name:u.name,cost:u.cost,ids:[]});gs.get(key).ids.push(id);}return [...gs.values()].sort((a,b)=>a.cost-b.cost||a.name.localeCompare(b.name,'zh-CN'));}
function handGroup(K,s,id){return unitGroups(K,s).find(g=>g.ids.includes(id));}
function chooseUnit(K,s,id,checked){const g=handGroup(K,s,id);if(!g)return;s.owned=checked?[...new Set([...s.owned,...g.ids])]:s.owned.filter(i=>!g.ids.includes(i));}
function setSharedProfile(K,s,id,field,value){const g=handGroup(K,s,id);if(!g)return;for(const uid of g.ids){const p=s.profiles[uid]||{stars:1,items:[]};if(field==='stars')p.stars=Number(value);else {p.items=[...(p.items||[])];const mapped=Object.keys(K.items).filter(i=>K.items[i].version===K.units[uid].version&&K.items[i].name===K.items[value]?.name);p.items[Number(field)]=mapped.includes(value)?value:mapped.length===1?mapped[0]:'';}s.profiles[uid]=p;}}
function profile(K,s,id){const p=s.profiles?.[id]||{};return {stars:[1,2,3,4].includes(Number(p.stars))?Number(p.stars):1,items:(Array.isArray(p.items)?p.items:[]).slice(0,3).filter(i=>K.items[i]?.version===K.units[id]?.version)};}
function containsItems(build,items){const rest=[...build];return items.every(i=>{const n=rest.indexOf(i);if(n<0)return false;rest.splice(n,1);return true;});}
function evidenceBuild(K,version,unit,items,onlyComp=null){return (onlyComp?[onlyComp]:K.comps.filter(c=>c.version===version)).flatMap(c=>c.builds.map(b=>({...b,comp:c.name,url:c.source}))).find(b=>b.unit===unit&&containsItems(b.items,items));}
function combatQuality(K,s,id){const p=profile(K,s,id),v=K.units[id].version,fit=p.items.length&&evidenceBuild(K,v,id,p.items);return {value:(p.stars-1)*12+Math.min(5,K.units[id].cost||0)*2+(fit?p.items.length*5:0),stars:p.stars,items:p.items,fit:!!fit};}
function transfers(K,c,s,onBoard){
 const equipped=s.owned.filter(i=>K.units[i]?.version===c.version).flatMap(unit=>profile(K,s,unit).items.map((item,slot)=>({unit,item,slot})));
 const bag=(s.bag||[]).filter(item=>K.items[item]?.version===c.version).map((item,slot)=>({unit:null,item,slot}));
 const assigned=new Map(onBoard.map(i=>[i,[...profile(K,s,i).items]]));
 return [...equipped,...bag].map(x=>{let holder=x.unit,proof=null;
  if(!holder){const eligible=onBoard.filter(i=>assigned.get(i).length<3&&evidenceBuild(K,c.version,i,[...assigned.get(i),x.item])).sort((a,b)=>combatQuality(K,s,b).value-combatQuality(K,s,a).value);holder=eligible[0]||null;if(holder)assigned.get(holder).push(x.item);}
  if(holder)proof=evidenceBuild(K,c.version,holder,x.unit?profile(K,s,holder).items:assigned.get(holder));
  const targets=c.heroes.filter(h=>h.core).map(h=>({unit:h.id,proof:evidenceBuild(K,c.version,h.id,[x.item],c)})).filter(t=>t.proof);
  return {...x,holder,proof,targets,onBoard:holder?onBoard.includes(holder):false};
 });
}

function ownedEmblemNames(K,c,s){const equipped=(s.owned||[]).filter(i=>K.units[i]?.version===c.version).flatMap(i=>profile(K,s,i).items);return new Set([...(s.ownedEmblems||[]),...[...(s.bag||[]),...equipped].filter(i=>K.items[i]?.version===c.version).map(i=>K.items[i].name)]);}
function boardDifference(from,to){return {add:to.filter(i=>!from.includes(i)),remove:from.filter(i=>!to.includes(i)),keep:to.filter(i=>from.includes(i))};}
function activeComp(K,c,s){
 if(c.active_final||!c.final_branches)return c;
 const owned=ownedEmblemNames(K,c,s),has=(c.emblems||[]).length>0&&c.emblems.every(n=>owned.has(n));
 const key=has?'with_emblem':'without_emblem',b=c.final_branches[key]||(has?c.final_branches.without_emblem:null);
 if(!b)return {...c,branch_gap:true};
 const fallback=has&&b.key!=='with_emblem';
 const sourceBoard={level:b.level,units:b.units,stars:Object.fromEntries(b.members.filter(m=>m.stars).map(m=>[m.id,m.stars])),avg:null,top4:null,count:null,source:b.source};
 return {...c,name:b.relation==='alternative'?b.title:c.name,augments:b.relation==='alternative'?[]:c.augments,active_final:b,branch_fallback:fallback,original_units:c.units,original_tier:c.tier,units:b.units,traits:[],tier:'未单评',avg:null,top4:null,count:null,
  conditions:c.conditions.filter(x=>!(x.kind==='item'&&c.emblems.includes(x.name)&&b.key==='without_emblem')),
  heroes:b.heroes?b.heroes.map(h=>({...h,stars:b.members.find(m=>m.id===h.id)?.stars})):b.members.map(m=>({...(!b.relation||b.relation!=='alternative'?c.heroes.find(h=>h.id===m.id)||{}:{}),id:m.id,role:(!b.relation||b.relation!=='alternative'?c.heroes.find(h=>h.id===m.id)?.role:null)||'本变体职责未核实',stars:m.stars})),
  builds:b.members.filter(m=>m.items.length).map(m=>({unit:m.id,items:m.items,avg:null,count:null,tier:null,source:'当前变体攻略配装（未提供的部件不补造）'})),
  boards:[sourceBoard],cohort:'当前展示攻略变体，未单独统计评级/均名；原方向榜单评级 '+c.tier+' 不自动转用于此变体。'};
}

function recommendationEligible(K,c,s){c=activeComp(K,c,s);const gate=eligibility(K,c,s);return c.active_final?.relation!=='alternative'&&!c.branch_gap&&!gate.pending.length&&gate.ready;}
function excludedPrerequisites(K,cs,s){
 return cs.filter(c=>!recommendationEligible(K,c,s)).map(c=>{const original=K.comps.find(x=>x.id===c.id)||c;return {c:original,missing:eligibility(K,original,s).missing};}).filter(x=>x.missing.length);
}
function eligibility(K,c,s){
 const equipped=(s.owned||[]).filter(i=>K.units[i]?.version===c.version).flatMap(i=>profile(K,s,i).items);
 const names=new Set([...(s.ownedEmblems||[]),...[...(s.bag||[]),...equipped].filter(i=>K.items[i]?.version===c.version).map(i=>K.items[i].name)]);
 const missing=(c.conditions||[]).filter(x=>x.required).filter(x=>x.kind==='item'?!names.has(x.name):x.kind==='augment'?!(c.augments||[]).some(a=>String(a.id)===String(x.id)&&(s.augments||[]).includes(augmentKey(a))):true);
 const pending=c.situational&&(!c.emblem_policy||c.emblem_policy.status==='unknown')?(c.emblems||[]).filter(n=>!names.has(n)):[];
 return {ready:!missing.length,missing,pending};
}

function plan(K,c,s){
 c=activeComp(K,c,s);
 if(!recommendationEligible(K,c,s))return [];
 const level=Number(s.current),owned=[...new Set(s.owned)].filter(i=>K.units[i]?.version===c.version);
 const eligible=owned.filter(i=>!K.units[i].special&&K.units[i].purchasable!==false);
 const qualities=new Map(eligible.map(i=>[i,combatQuality(K,s,i).value]));
 const source=c.boards.filter(b=>b.level===level),families=ids=>ids.map(i=>K.units[i].family||i);
 function evaluate(ids){const ts=naturalTraits(K,ids),overlap=source.length?Math.max(...source.map(b=>ids.filter(i=>b.units.includes(i)).length)):0;
  return {units:ids,traits:ts,quality:ids.reduce((n,i)=>n+qualities.get(i),0),score:ids.reduce((n,i)=>n+qualities.get(i),0)+ts.reduce((n,t)=>n+(t.active?4:0)+Math.max(0,t.count-1),0)+overlap*2+ids.filter(i=>c.heroes.some(h=>h.id===i&&h.core)).length,overlap};}
 // Bounded beam search; quality weights are heuristics, not simulated damage or win rate.
 let beam=[evaluate([])];for(const id of eligible){const next=[...beam];for(const b of beam)if(b.units.length<level&&!families(b.units).includes(K.units[id].family||id))next.push(evaluate([...b.units,id]));const buckets=new Map();for(const b of next){const n=b.units.length;if(!buckets.has(n))buckets.set(n,[]);buckets.get(n).push(b);}beam=[...buckets.values()].flatMap(bs=>bs.sort((a,b)=>b.score-a.score||a.units.join().localeCompare(b.units.join())).slice(0,64));}
 const size=Math.max(0,...beam.map(b=>b.units.length));return beam.filter(b=>b.units.length===size&&size>0).sort((a,b)=>b.score-a.score).slice(0,2).map(b=>({...b,bench:owned.filter(i=>!b.units.includes(i)),excluded:owned.filter(i=>!eligible.includes(i)),source:source.find(r=>r.units.length===b.units.length&&r.units.every(i=>b.units.includes(i)))||null,core:owned.filter(i=>c.heroes.some(h=>h.id===i&&h.core))}));
}

function recipeParts(K,id,seen=[]){const x=K.items[id];if(!x||seen.includes(id))return null;if(x.component)return [id];if(x.craftable===false||x.recipe?.length!==2)return null;const parts=x.recipe.map(i=>K.items[i]?.version===x.version?recipeParts(K,i,[...seen,id]):null);return parts.some(p=>p===null)?null:parts.flat();}
function componentSummary(K,rows){const counts=new Map(),special=[];for(const row of rows)for(const id of row?.build?.items||[]){const parts=recipeParts(K,id);if(parts===null)special.push({unit:row.unit,item:id});else for(const p of parts)counts.set(p,(counts.get(p)||0)+1);}return {counts:[...counts].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])),special};}
function recommendedBuilds(c,unit){
 const local=c.builds.filter(b=>b.unit===unit&&b.items?.length),cross=(c.cross_game_builds||[]).filter(b=>b.unit===unit),all=local.some(b=>b.items.length===3)?local:cross.length?cross:local;
 const ranked=[...new Map(all.filter(b=>['S','A'].includes(b.tier)&&b.items.length===3).map(b=>[[...b.items].sort().join('|')+'|'+b.tier,b])).values()].sort((a,b)=>a.tier.localeCompare(b.tier)||(b.count||0)-(a.count||0));
 if(ranked.length)return ranked;
 const fallback=[...all].sort((a,b)=>Number(!!b.recommended)-Number(!!a.recommended)||Number(b.items.length===3)-Number(a.items.length===3)||(b.count||0)-(a.count||0))[0];
 return fallback?[fallback]:[];
}
function componentPlan(K,c){
 const candidates=c.units.map(unit=>{const h=c.heroes.find(h=>h.id===unit)||{},tag=K.units[unit]?.role_tags||[];
  const cross=(c.cross_game_builds||[]).find(b=>b.unit===unit);
  const tank=(h.role||'').includes('坦')||!!cross?.donor_role.includes('坦')||tag.includes('Role.Tank');
  const carry=!tank&&((h.role||'').includes('C')||!!cross&&(/C|输出/.test(cross.donor_role))||tag.some(t=>t==='Role.Attack'||t.startsWith('Role.Attack.')||t==='Role.Magic'||t.startsWith('Role.Magic.')));
  const local=c.builds.filter(b=>b.unit===unit),builds=(local.some(b=>b.items.length===3)?local:cross?[cross]:local).slice().sort((a,b)=>Number(!!b.recommended)-Number(!!a.recommended)||Number(b.items.length===3)-Number(a.items.length===3)||Number(b.items.every(i=>recipeParts(K,i)!==null))-Number(a.items.every(i=>recipeParts(K,i)!==null))||(b.count||0)-(a.count||0));
  return {unit,hero:h,tank,carry,build:builds[0]};}).filter(x=>x.build);
 const used=new Set();const rows=['主C','主坦','副C','副坦'].map(role=>{const tank=role.includes('坦');const options=candidates.filter(x=>!used.has(x.unit)&&(tank?x.tank:x.carry)).sort((a,b)=>Number((b.hero.role||'').includes(role))-Number((a.hero.role||'').includes(role))||Number(!!b.hero.core)-Number(!!a.hero.core)||(b.build.count||0)-(a.build.count||0));const pick=options[0];if(!pick)return {role,missing:true};used.add(pick.unit);return {...pick,role,candidate:pick.hero.role!==role};});
 return {rows,primary:componentSummary(K,rows.slice(0,2)),total:componentSummary(K,rows),missing:rows.filter(r=>r.missing||r.build.items.length!==3).length};
}

function componentName(n){return n==='暴风之剑'||n==='暴风大剑'?'大剑':n==='无用大棒'?'法杖':n==='反曲之弓'?'反曲弓':n;}
function stockOptions(K){return [...new Set(Object.values(K.items).filter(i=>i.component).map(i=>componentName(i.name)))];}
function cleanStock(K,stock){return Object.fromEntries(stockOptions(K).map(n=>[n,Math.max(0,Math.min(99,Math.floor(Number(stock?.[n])||0)))]));}
function matchMaterials(K,summary,stock){const need={};for(const [id,n] of summary.counts){const name=componentName(K.items[id].name);need[name]=(need[name]||0)+n;}const missing={},unused={};let matched=0,total=0;for(const [n,q] of Object.entries(need)){matched+=Math.min(q,stock[n]||0);total+=q;if(q>(stock[n]||0))missing[n]=q-(stock[n]||0);}for(const [n,q] of Object.entries(stock))if(q>(need[n]||0))unused[n]=q-(need[n]||0);return {need,missing,unused,matched,total,ratio:total?matched/total:0};}
function materialFit(K,c,s){const p=componentPlan(K,c),stock=cleanStock(K,s.componentStock),primary=matchMaterials(K,p.primary,stock),total=matchMaterials(K,p.total,stock);
 const primaryComplete=p.rows.slice(0,2).every(r=>!r.missing&&r.build.items.length===3)&&!p.primary.special.length;
 const complete=primaryComplete&&!p.missing&&!p.total.special.length;
 const finish={};for(const r of p.rows.slice(0,2))for(const id of r.build?.items||[]){const parts=recipeParts(K,id);if(!parts)continue;const x=matchMaterials(K,{counts:parts.map(i=>[i,1])},stock);if(Object.values(x.missing).reduce((a,b)=>a+b,0)===1){const n=Object.keys(x.missing)[0];(finish[n]||=[]).push({unit:r.unit,item:id});}}
 const priority=Object.keys(primary.missing).sort((a,b)=>Number(!!finish[b])-Number(!!finish[a])||primary.missing[b]-primary.missing[a]||a.localeCompare(b));
 return {c,p,primary,total,finish,priority,confidence:complete?2:primaryComplete?1:0,ready:eligibility(K,c,s).ready,uncertain:eligibility(K,c,s).pending.length>0,alternative:c.active_final?.relation==='alternative'};
}
function rankMaterials(K,cs,s){return cs.map(c=>activeComp(K,c,s)).filter(c=>recommendationEligible(K,c,s)).map(c=>materialFit(K,c,s)).sort((a,b)=>Number(b.ready)-Number(a.ready)||Number(a.alternative)-Number(b.alternative)||Number(a.uncertain)-Number(b.uncertain)||b.confidence-a.confidence||b.primary.ratio-a.primary.ratio||b.total.ratio-a.total.ratio||b.total.matched-a.total.matched||a.c.name.localeCompare(b.c.name,'zh-CN'));}

function craftSequence(K,c,s,board,fit){const stock=cleanStock(K,s.componentStock),assigned=new Map((board?.units||[]).map(i=>[i,[]])),steps=[];
 const recipes=fit.p.rows.flatMap((r,priority)=>(r.build?.items||[]).map(item=>({target:r.unit,item,priority})));
 for(const x of recipes){if(steps.length>=3)break;const parts=recipeParts(K,x.item);if(!parts)continue;const need=matchMaterials(K,{counts:parts.map(i=>[i,1])},stock);if(Object.keys(need.missing).length)continue;
 const carriers=(board?.units||[]).filter(i=>assigned.get(i).length<3&&evidenceBuild(K,c.version,i,[...assigned.get(i),x.item])).sort((a,b)=>Number(b===x.target)-Number(a===x.target)||(K.units[b].cost||0)-(K.units[a].cost||0));
 const holder=carriers[0];if(!holder)continue;for(const [n,q] of Object.entries(need.need))stock[n]-=q;assigned.get(holder).push(x.item);steps.push({...x,holder,parts});}
 return {steps,remaining:stock};
}
function combinedRecommendations(K,cs,s){const references=[],ranked=[];
 for(const raw of cs){const c=activeComp(K,raw,s),fit=materialFit(K,c,s);
 const boardOptions=plan(K,c,s).map(board=>({board,craft:craftSequence(K,c,s,board,fit)})).sort((a,b)=>(b.board.score+5*b.craft.steps.length)-(a.board.score+5*a.craft.steps.length));
 const b=boardOptions[0]?.board;
 const owned=new Set((s.owned||[]).filter(i=>K.units[i]?.version===c.version));
 const retained=c.units.filter(i=>owned.has(i)),cores=c.heroes.filter(h=>h.core&&c.units.includes(h.id)).map(h=>h.id),coreHeld=cores.filter(i=>owned.has(i));
 const rosterRatio=retained.length/Math.max(1,c.units.length),coreRatio=cores.length?coreHeld.length/cores.length:0,boardRatio=(b?.units.length||0)/Math.max(1,Number(s.current));
 const score=30*rosterRatio+20*coreRatio+30*fit.primary.ratio+10*fit.total.ratio+10*boardRatio;
 const row={c,fit,board:b,score,retained,cores,coreHeld,missingCore:cores.filter(i=>!owned.has(i)),missingMembers:c.units.filter(i=>!owned.has(i)),craft:boardOptions[0]?.craft||{steps:[],remaining:cleanStock(K,s.componentStock)}};
 if(!recommendationEligible(K,c,s)||!fit.confidence||!b)references.push(row);else ranked.push(row);}
 ranked.sort((a,b)=>(b.score+40*emblemFit(K,b.c,s).score)-(a.score+40*emblemFit(K,a.c,s).score)||b.fit.confidence-a.fit.confidence||a.c.name.localeCompare(b.c.name,'zh-CN'));
 const seen=new Set(),top=[];for(const r of ranked){const signature=JSON.stringify(r.c.units.map(i=>[K.units[i].name,K.units[i].cost]).sort((a,b)=>a[0].localeCompare(b[0])));if(seen.has(signature))continue;seen.add(signature);if(top.length<3)top.push(r);}
 return {top,references,eligible:ranked.length};
}

function formationProfile(K,c){
 const original=K.comps.find(x=>x.id===c.id)||c;
 const population=c.units.reduce((n,id)=>n+(K.units[id]?.name==='远古巨龙'?2:1),0);
 const exact=original.boards.filter(b=>!b.source?.includes('early_options')&&c.units.every(id=>b.units.includes(id)));
 const level=c.active_final?.level||(exact.length?Math.min(...exact.map(b=>b.level)):population);
 const estimated=!c.active_final&&!exact.length;
 let boards=original.boards.filter(b=>b.level>=level&&!b.source?.includes('early_options'));
 if(c.active_final){boards=Object.values(c.final_branches||{}).filter(b=>b.relation===c.active_final.relation);if(c.active_final.relation==='alternative')boards=[c.active_final];}
 const unique=[...new Map(boards.map(b=>[[...b.units].sort().join('|'),b])).values()];
 const core=unique.length>1?unique[0].units.filter(id=>unique.every(b=>b.units.includes(id))):[];
 return {level,estimated,core,variants:unique.length,levels:[...new Set(boards.map(b=>b.level))].sort((a,b)=>a-b)};
}
function levelVariants(K,c){
 const final=formationProfile(K,c);
 return [...new Set(c.boards.map(b=>b.level))].sort((a,b)=>a-b).map(level=>{
  const groups=new Map();for(const b of c.boards.filter(b=>b.level===level)){const key=[...new Set(b.units)].sort().join('|');if(!groups.has(key))groups.set(key,{units:[...new Set(b.units)],records:[]});groups.get(key).records.push(b);}
  const options=[...groups.values()],core=options.length>1?options[0].units.filter(id=>options.every(b=>b.units.includes(id))):[];
  return {level,core,finalKnown:final.variants>1,finalCore:core.filter(id=>final.core.includes(id)),options:options.map(b=>({...b,extra:b.units.filter(id=>!core.includes(id))}))};
 });
}
function expectedTraits(K,c,ids=c.units,includeEmblems=false){
 const rows=naturalTraits(K,ids).map(t=>({...t,natural:t.count,emblems:0}));
 if(includeEmblems)for(const m of c.active_final?.members||[]){
  if(!ids.includes(m.id))continue;
  for(const item of new Set(m.items||[])){
   const label=K.items[item]?.name||'',traitName=label.endsWith('纹章')?label.slice(0,-2):null;
   if(!traitName)continue;
   const entry=Object.entries(K.trait_catalog).find(([id,t])=>t.name===traitName&&id.startsWith(m.id.split(':')[0]+':'));
   if(!entry||(K.units[m.id]?.traits||[]).includes(entry[0]))continue;
   let row=rows.find(t=>t.id===entry[0]);if(!row){row={id:entry[0],name:traitName,count:0,natural:0,emblems:0,verified:entry[1].verified};rows.push(row);}
   row.count++;row.emblems++;
  }
 }
 for(const row of rows)row.active=Math.max(0,...(K.trait_catalog[row.id]?.thresholds||[]).filter(n=>n<=row.count));
 return rows.sort((a,b)=>b.count-a.count);
}
function transitionRoute(K,c){
 const final=formationProfile(K,c).core,levels=levelVariants(K,c);let previous=null;
 return levels.map(l=>{
  const eligible=l.options.filter(b=>!previous||previous.units.filter(id=>final.includes(id)).every(id=>b.units.includes(id)));
  if(!eligible.length){previous=null;return {level:l.level,gap:true};}
  const score=b=>b.units.filter(id=>final.includes(id)).length*100-(previous?previous.units.filter(id=>!b.units.includes(id)).length*10:0);
  const chosen=[...eligible].sort((a,b)=>score(b)-score(a))[0];
  const row={level:l.level,from:previous?.level,units:chosen.units,add:chosen.units.filter(id=>!previous?.units.includes(id)),remove:previous?previous.units.filter(id=>!chosen.units.includes(id)):[],keep:previous?previous.units.filter(id=>chosen.units.includes(id)):[],final:chosen.units.filter(id=>final.includes(id)),gap:!!previous&&l.level!==previous.level+1};
  previous={level:l.level,units:chosen.units};return row;
 });
}
const api={coreAnnotations,emblemFit,transitionCoach,excludedPrerequisites,recommendationEligible,recommendedBuilds,expectedTraits,transitionRoute,levelVariants,formationProfile,craftSequence,combinedRecommendations,componentName,stockOptions,cleanStock,matchMaterials,materialFit,rankMaterials,recipeParts,componentSummary,componentPlan,activeComp,boardDifference,ownedEmblemNames,eligibility,unitGroups,chooseUnit,setSharedProfile,profile,containsItems,combatQuality,evidenceBuild,transfers,directions,naturalTraits,unitRole,plan,scoped,boardRows,select,changeVersion,augmentKey,augmentGroups};if(typeof module!=='undefined')module.exports=api;
if(typeof document==='undefined')return;
const K=JSON.parse(document.getElementById('data').textContent),E=root.KnowledgeEngine,$=id=>document.getElementById(id),esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// Keep the scrollable picker below the sticky navigation even when summaries wrap.
if(typeof ResizeObserver!=='undefined')new ResizeObserver(entries=>{
 const height=entries[0]?.target.getBoundingClientRect().height;
 if(height)document.documentElement.style.setProperty('--flow-header-height',height+'px');
}).observe($('flow-header'));
const defaults={coach:false,step:0,version:'all',mode:'all',current:4,target:8,tier:'all',search:'',owned:[],profiles:{},bag:[],ownedEmblems:[],emblem:'',augment:'',augments:[],showAll:false};let s={...defaults};
const key='dual-assistant-planner-v3';try{Object.assign(s,JSON.parse(localStorage.getItem(key)||'{}'));}catch{}
// Retired toolbar filters must not invisibly constrain a restored session.
Object.assign(s,{version:'all',mode:'all',tier:'all',search:'',emblem:'',augment:''});
if(!Array.isArray(s.augments))s.augments=[];s.augments=s.augments.filter(k=>augmentGroups(K,s).some(g=>g.key===k));
if(!Array.isArray(s.ownedEmblems))s.ownedEmblems=[];
// Removed quality inputs: discard their persisted values so hidden settings cannot affect recommendations.
s.profiles={};s.bag=[];s.componentStock={};
if(!Array.isArray(s.owned))s.owned=[];s.owned=s.owned.filter(i=>K.units[i]&&(s.version==='all'||K.units[i].version===s.version));
if(!['all','current','future'].includes(s.mode))s.mode='all';if(!['all','S','A'].includes(s.tier))s.tier='all';
const name=i=>K.units[i]?.name||i,items=ids=>ids.map(i=>K.items[i]?.name||i).join(' + '),names=ids=>ids.map(name).join('、'),version=c=>K.versions.find(v=>v.id===c.version),num=n=>n==null?'未提供':Number(n).toLocaleString('zh-CN'),decimal=n=>n==null?'未提供':Number(n).toFixed(2);
function save(){try{localStorage.setItem(key,JSON.stringify(s));}catch{}}
$('version').innerHTML+=K.versions.map(v=>`<option value="${esc(v.id)}">${esc(v.label)}</option>`).join('');
function stockControls(){$('component-stock').innerHTML=stockOptions(K).map(n=>`<label>${esc(n)}<input type="number" min="0" max="99" step="1" value="${s.componentStock?.[n]||0}" data-component="${esc(n)}" aria-label="已有${esc(n)}数量"></label>`).join('');}
function renderUnitChoices(){
 const cs=directions(K,s).filter(c=>recommendationEligible(K,c,s)),annotations=coreAnnotations(K,cs),gs=unitGroups(K,s);
 const tagNames={carry:'输出核心',tank:'主坦核心',fixed:'固定核心'};
 $('units').innerHTML='<div class="core-legend"><span class="unit-core carry">输出核心</span><span class="unit-core tank">主坦核心</span><span class="unit-core fixed">固定核心</span></div><p class="muted">按当前可推荐方向标注；固定核心指已收录成型变体共同保留。未标色不等于不能用，候选职责不标为已确认。</p>'+E.unique(gs.map(g=>g.cost)).map(cost=>`<fieldset><legend>${cost}费</legend><div class="choices">${gs.filter(g=>g.cost===cost).map(g=>{const records=g.ids.flatMap(id=>annotations[id]||[]),kinds=[...new Set(records.flatMap(r=>r.tags.map(t=>t.kind)))],hint=records.map(r=>version({version:r.version}).label+' · '+r.comp+'：'+r.tags.map(t=>t.label).join('、')).join('；');return `<label title="${esc(hint)}"><input type="checkbox" value="${esc(g.ids[0])}" ${g.ids.some(i=>s.owned.includes(i))?'checked':''}><span class="unit-picker-name">${esc(g.name)}<span class="unit-core-tags">${kinds.map(k=>'<span class="unit-core '+k+'">'+tagNames[k]+'</span>').join('')}</span></span></label>`;}).join('')}</div></fieldset>`).join('')+'<details class="core-roster-index"><summary>查看各阵容核心名单与版本</summary>'+cs.map(c=>{const entries=c.units.filter(id=>annotations[id]?.some(r=>r.comp===c.name&&r.version===c.version));return '<p><strong>'+esc(c.name)+'</strong> <small>'+esc(version(c).label)+'</small><br>'+ (entries.map(id=>esc(name(id))+'（'+annotations[id].find(r=>r.comp===c.name&&r.version===c.version).tags.map(t=>esc(t.label)).join('、')+'）').join('；')||'暂无已确认核心记录')+'</p>';}).join('')+'</details>';
}
function controls(){
 const cs=scoped(K,s),levels=Array.from({length:10},(_,i)=>i+2);
 if(!levels.includes(Number(s.current)))s.current=levels[0];
 const future=levels.filter(n=>n>Number(s.current));if(!future.includes(Number(s.target)))s.target=future[0]??null;
 for(const [id,ls] of [['current',levels],['target',future]]){$(id).innerHTML=ls.map(n=>`<option value="${n}">${n}级</option>`).join('');$(id).disabled=!ls.length;}
 const em=E.unique([...cs.flatMap(c=>[...c.emblems,...c.conditions.filter(x=>x.kind==='item').map(x=>x.name)]),...Object.values(K.items).filter(x=>(s.version==='all'||x.version===s.version)&&x.name.endsWith('纹章')).map(x=>x.name)]);
 $('owned-emblems').innerHTML=em.map(n=>`<label><input type="checkbox" value="${esc(n)}" ${s.ownedEmblems.includes(n)?'checked':''}>${esc(n)}</label>`).join('');
 $('emblem').innerHTML='<option value="">不限</option>'+em.map(n=>`<option>${esc(n)}</option>`).join('');
 const aug=new Map();cs.forEach(c=>c.augments.forEach(a=>aug.set(c.version+':'+a.id,version(c).game+' · '+a.name)));
 $('augment').innerHTML='<option value="">不限</option>'+[...aug].map(([id,n])=>`<option value="${esc(id)}">${esc(n)}</option>`).join('');
 if(!em.includes(s.emblem))s.emblem='';if(!aug.has(s.augment))s.augment='';
 for(const id of ['version','mode','current','target','tier','search','emblem','augment'])$(id).value=s[id]??'';
 const ids=Object.keys(K.units).filter(i=>K.units[i].purchasable!==false&&K.units[i].cost>0&&(s.version==='all'||K.units[i].version===s.version));
 renderUnitChoices();
}
function boardHTML(c){
 const rows=c.boards.filter(b=>b.level===Number(s.current)).sort((a,b)=>b.units.filter(i=>s.owned.includes(i)).length-a.units.filter(i=>s.owned.includes(i)).length);
 return `<h3>${s.current}级来源棋盘对照</h3><p>仅供补牌参考，不要求已有棋子全部上场；来源棋盘不等于当前手牌。</p>`+rows.slice(0,3).map(b=>`<div class="board"><p>完整棋盘：${esc(names(b.units))}</p><p>仍缺：${esc(names(b.units.filter(i=>!s.owned.includes(i)))||'无')}</p><small>${esc(b.source)} · 样本 ${num(b.count)} · 均名 ${decimal(b.avg)}</small></div>`).join('')+(rows.length?'':'<p>本级暂无来源棋盘，手牌建议依据棋子质量与自然羁绊结构。</p>');
}
function gateHTML(c){const g=eligibility(K,c,s),p=c.emblem_policy;
 const badge=c.active_final?.relation==='alternative'?'<strong>当前显示无转职替代棋盘 · 非原分支评级</strong>':g.missing.length?'<strong>前置条件未满足 · 暂不推荐走此方向</strong><p>缺少：'+esc(g.missing.map(x=>x.name).join('、'))+'</p>':p?.status==='unknown'?'<strong>转职必要性未确认 · 可参考，未作硬拦截</strong>':p?.status==='optional'?'<strong>无转职也有对应打法 · 已放行</strong>':'<strong>已满足已记录前置条件</strong>';
 return `<div class="evidence">${badge}${p?`<p>${esc(p.note)}</p>${p.alternative?`<p>${esc(p.alternative)}</p>`:''}<small>核实：TFT 18.4b · 2026-10-15。原评级仍属于来源榜单样本，不单独证明无转职强度。</small><p>${p.sources.map(x=>`<a href="${esc(x.url)}">${esc(x.variant||'攻略依据')}</a>`).join(' · ')} · <a href="../../research/2026-10-15-dual-source/tft/emblem-verification/audit.json">逐套核实记录</a></p>`:g.pending.length?'<p>转职依赖未核实；保留提示，不自动拦截。</p>':''}</div>`;
}
function branchHTML(c){
 if(!c.final_branches)return '';
 const b=c.active_final;if(!b)return '<div class="note">当前转职状态没有已核实的成型棋盘，保留缺口；下方原始棋子仅供来源参考。</div>';
 const other=c.final_branches[b.key==='with_emblem'?'without_emblem':'with_emblem'];
 const tiles=v=>`<div class="choices">${v.members.map(m=>`<div class="board"><strong>${esc(name(m.id))}</strong>${m.stars?` · 目标${m.stars}星`:''}<br><small>${esc(items(m.items)||'配装未列，不代表无需装备')}</small></div>`).join('')}</div>`;
 const diff=other?boardDifference(other.units,b.units):null;
 const pool=s.owned.filter(i=>K.units[i]?.version===c.version),need=b.units.filter(i=>!pool.includes(i));
 return `<section class="evidence"><h3>自动展示：${esc(b.title)} · ${b.level}级成型</h3><p>${b.key==='with_emblem'?'已持有对应转职':c.branch_fallback?'已持有转职，但专属转职棋盘未核实；展示已确认基础棋盘':'未持有对应转职'}。棋子排列仅作名单展示，不指定站位。</p>${b.relation==='alternative'?'<p><strong>这是不同终局的替代参考，原方向的海克斯推荐关系未自动继承。</strong></p>':''}${tiles(b)}${diff?`<p><strong>从另一分支切到当前分支：</strong><br>新增：${esc(names(diff.add)||'无')}<br>换下：${esc(names(diff.remove)||'无')}<br>保留：${esc(names(diff.keep)||'无')}</p>${!diff.add.length&&!diff.remove.length?'<p>棋子不必更换；变化在纹章携带与羁绊档位，不能沿用另一分支的强度结论。</p>':''}<details><summary>对照：${esc(other.title)} · ${other.level}级</summary>${tiles(other)}<a href="${esc(other.source)}">另一棋盘依据</a></details>`:'<p>另一转职状态尚无独立核实棋盘，不编造换人方案。</p>'}<p>按已有牌池，成型还缺：${esc(names(need)||'已拥有全部成型棋子')}。已有但不在该终局：${esc(names(pool.filter(i=>!b.units.includes(i)))||'无')}（可继续打工，不是立即卖牌指令）。</p><small>${esc(b.note)}</small> · <a href="${esc(b.source)}">当前棋盘依据</a></section>`;
}
function crossBuildNote(b){return b?.cross_game?`<small class="cross-equipment">TFT 18.4b 参考 · ${esc(b.donor_comp)} · ${esc(b.donor_role)}；跨阵容配装，效果未按金铲铲验证。</small>`:'';}
function componentsHTML(c){
 const p=componentPlan(K,c),top=p.total.counts.filter(([,n])=>n>=2).slice(0,3);
 const combos=r=>recommendedBuilds(c,r.unit);
 const entry=b=>`<p><span class="badge tier">${esc(b.tier?b.tier+'级':'未评级')}</span> ${esc(items(b.items))}${crossBuildNote(b)}<br><small>均名 ${decimal(b.avg)} · 样本 ${num(b.count)}</small></p>`;
 return `<section class="evidence equipment-overview"><h3>装备方向</h3><p><strong>需求较多的散件：</strong>${top.length?top.map(([id,n])=>esc(componentName(K.items[id].name))+' × '+n).join('、'):'暂无明显集中需求'}</p><p class="muted">按四个职责位各选一套来源配装归纳，取需求最多的三种重复散件；替代套装不累加，不是必拿顺序。${p.missing?'有 '+p.missing+' 个位置资料不全，仅为已知配装小计。':''}${p.total.special.length?'另有 '+p.total.special.length+' 件特殊装备或未知配方未折算。':''}</p>${p.rows.map(r=>{
 if(r.missing)return `<div class="board"><h4>${r.role}</h4><p>暂无已确认的推荐配装。</p></div>`;
 const builds=combos(r);
 return `<div class="board"><h4>${r.role}${r.candidate?'候选':''} · ${esc(name(r.unit))}</h4>${r.candidate?'<p class="muted">按来源职责、词库角色与承装记录分配，主副顺序未获作者明确确认。</p>':''}<h5>推荐装备组合</h5>${(builds.length?builds:[r.build]).map(entry).join('')}</div>`;
 }).join('')}<small>装备评级独立于阵容评级。配方按各版本归档记录；TFT词库含PBE元信息。</small></section>`;
}
function flatSections(markup){return markup.replace(/<details[^>]*>/g,'<section class="flat-section">').replace(/<\/details>/g,'</section>').replace(/<summary[^>]*>/g,'<h4>').replace(/<\/summary>/g,'</h4>');}
function levelNavigatorHTML(c,requested=s.current){
 const levels=levelVariants(K,c),route=transitionRoute(K,c);
 if(!levels.length)return '<p>暂无分等级棋盘，无法推导过渡顺序。</p>';
 const level=levels.some(l=>l.level===Number(requested))?Number(requested):levels.reduce((a,b)=>Math.abs(b.level-requested)<Math.abs(a.level-requested)?b:a).level;
 const l=levels.find(l=>l.level===level),r=route.find(r=>r.level===level),next=route.find(r=>r.level>level);
 const change=next?.units&&r?.units&&next.from===level&&next.level===level+1;
 return `<h3>逐级过渡顺序</h3><nav class="level-nodes" aria-label="查看等级">${levels.map(x=>`<button type="button" data-view-level="${x.level}" aria-pressed="${x.level===level}">${x.level}级</button>`).join('')}</nav><div class="level-view"><div class="core-priority">${r?.units?`<p><strong>成型固定核心 · 保留：</strong>${esc(names(r.final))||'本级暂无已确认的成型固定核心'}</p>`: ''}<p class="muted">本级共同核心：${esc(names(l.core))||'已收录组合不足或无共同棋子'}</p></div><h3>${level}级 · 当前上场组合</h3>${r?.units?`<p>${esc(names(r.units))}</p>${expectedTraitsHTML(c,r.units)}`:'<p>此等级无法衔接前一等级并保留成型核心，请参考下方已收录组合。</p>'}${l.options.length>1?`<h4>本级其他可选组合</h4>${l.options.filter(b=>!r?.units||[...b.units].sort().join('|')!==[...r.units].sort().join('|')).map(b=>`<div class="alternative-board"><p>${esc(names(b.units))}</p>${expectedTraitsHTML(c,b.units)}</div>`).join('')}<small>下方换人顺序仅针对“当前上场组合”，其他组合需另行调整。</small>`:''}<div class="next-level-plan"><h3>${next?'升到 '+(level+1)+' 级':'后续升级'}</h3>${change?`<p><strong>补入：</strong>${esc(names(next.add))||'无需补牌'}</p><p><strong>换下：</strong>${esc(names(next.remove))||'无需换人'}</p><p><strong>保留：</strong>${esc(names(next.keep))||'无'}</p><p class="muted">补入棋子到手并能组成目标棋盘后，再替换打工牌；携装棋子先确认装备转移。</p>`:next?'<p>缺少可衔接的下一级棋盘，暂不提供换人指令。可点击其他等级查看目标组合。</p>':'<p>已到本阵容最后一个已收录等级，暂无更高等级记录。</p>'}</div><p class="muted">按已收录棋盘推导，优先保留成型核心、减少换人；不代表实测最优战力。</p></div>`;
}
function expectedTraitsHTML(c,ids=c.units,final=false){
 const rows=expectedTraits(K,c,ids,final),active=rows.filter(t=>t.verified&&t.active>0),unknown=rows.filter(t=>!t.verified),inactive=rows.filter(t=>t.verified&&!t.active);
 const badges=ts=>ts.map(t=>`<span class="badge trait-count"><strong>${esc(t.name)} ${t.count}</strong>${t.verified?'<small>开启 '+t.active+' 档</small>':'<small>人数 · 档位待核实</small>'}${t.emblems?'<small>含纹章 +'+t.emblems+'</small>':''}</span>`).join('');
 return `<div class="expected-traits"><h4>${final?'预期成型羁绊':'当前组合羁绊'}</h4>${badges(active)}${badges(unknown)}${!active.length&&!unknown.length?'<p>暂无达到已核实门槛的羁绊。</p>':''}${inactive.length?'<p class="muted">未开启：'+inactive.map(t=>esc(t.name)+' '+t.count).join(' · ')+'</p>':''}<small>按${final?'当前成型棋盘':'所选等级棋盘'}人数统计${final?'，仅计入该分支明确携带的纹章':'，未计转职'}；人数与开启档位分开显示。</small></div>`;
}
function boardEquipmentHTML(c,id){
 const builds=recommendedBuilds(c,id),b=builds[0];
 if(!b)return '<div class="board-equipment empty-equipment">暂无推荐配装</div>';
 return `<div class="board-equipment" aria-label="推荐装备"><span class="equipment-rating">推荐配装 · ${esc(b.tier?b.tier+'级':'未评级')}</span>${b.cross_game?'<small>TFT 18.4b 参考</small>':''}${b.items.map(item=>`<span class="board-item">${esc(K.items[item]?.name||item)}</span>`).join('')}</div>`;
}
function positioningHTML(c){
 const cells=Array.from({length:28},()=>[]),missing=[];
 for(const id of c.units){const h=c.heroes.find(h=>h.id===id)||{},match=typeof h.position==='string'&&h.position.match(/^([1-4]),([1-7])$/);if(match)cells[(Number(match[1])-1)*7+Number(match[2])-1].push(id);else missing.push(id);}
 const piece=id=>{const u=K.units[id]||{},h=c.heroes.find(h=>h.id===id)||{},cost=u.purchasable!==false&&u.cost>=1&&u.cost<=5?u.cost:'special';return `<div class="board-piece cost-${cost}"><strong>${esc(name(id))}</strong><span>${h.stars?'★'.repeat(h.stars)+' '+h.stars+'星':'星级未确认'}</span><small>${esc(h.role||'定位未确认')}</small>${boardEquipmentHTML(c,id)}</div>`;};
 return `<div class="position-board"><p class="muted">前排 · 靠近对手</p><div class="board-scroll"><div class="hex-board">${Array.from({length:4},(_,r)=>`<div class="hex-row">${cells.slice(r*7,r*7+7).map((ids,col)=>`<div class="hex-cell" aria-label="第${r+1}排第${col+1}格">${ids.map(piece).join('')||'<span class="empty-hex">·</span>'}</div>`).join('')}</div>`).join('')}</div></div><p class="muted">后排 · 己方底线</p></div>${missing.length?'<p class="muted">以下棋子暂无已确认站位，不自动安排格子：</p><div class="unplaced-units">'+missing.map(piece).join('')+'</div>':''}`;
}
function formationBoardHTML(c){
 return `<section class="flat-section"><h3>成型棋盘 · 站位与星级</h3><p class="muted">按归档坐标展示；颜色按费用区分，星级沿用来源目标。站位需结合对手调整。</p>${positioningHTML(c)}${expectedTraitsHTML(c,c.units,true)}</section>`;
}
function fullDirectionHTML(c){
 return `<section class="composition-overview" aria-label="阵容特征"><strong>${esc(c.route)}</strong><span>均名 ${decimal(c.avg)} · 前四 ${decimal(c.top4)}% · 样本 ${num(c.count)}</span></section>${expectedTraitsHTML(c,c.units,true)}<section id="direction-levels" class="flat-section">${levelNavigatorHTML(c)}</section>${gateHTML(c)}${flatSections(branchHTML(c))}${formationBoardHTML(c)}${componentsHTML(c)}<section class="flat-section"><h3>运营路线</h3><p>${esc(c.route)}</p>${c.flow.map(x=>'<p><strong>'+esc(x[0])+'</strong>：'+esc(x[1])+'</p>').join('')||'<p>来源未提供具体搜牌回合。</p>'}</section>${flatSections(recommendationHTML(c))}<p><a href="${esc(c.guide)}">完整阵容攻略</a> · <a href="${esc(c.source)}">数据来源</a></p><small>${esc(c.cohort)}</small>`;
}

function card(c){const v=version(c);return `<article id="comp-${esc(c.id)}"><small class="version-label">${esc(v.label)}</small> <span class="badge tier">${esc(c.tier)}</span><h2>${esc(c.name)}</h2>${!recommendationEligible(K,c,s)?'<p class="muted"><strong>仅供查阅 · 不进入当前推荐</strong>：前置条件未满足或路线尚未核实。</p>':''}${gateHTML(c)}${branchHTML(c)}${componentsHTML(c)}<p>${esc(c.route)} · 均名 ${decimal(c.avg)} · 前四 ${decimal(c.top4)}% · 样本 ${num(c.count)}</p><p>${esc(names(c.units))}</p><p class="muted">${esc(c.traits.join(' / '))}</p>${recommendationHTML(c)}${c.situational&&!c.emblem_policy?`<p>条件分支标记：${esc(c.emblems.join('、')||'来源命名标记')}；属于使用率／命名规则，不自动视为硬性入场条件。</p>`:''}${c.conditions.length?`<p>来源入场条件：${esc(c.conditions.map(x=>x.name).join('、'))}</p>`:''}<details class="card-detail" data-id="${esc(c.id)}"><summary>查看补牌、装备与运营</summary><div class="detail-body"></div></details><p><a href="${esc(c.guide)}">${v.game==='TFT'?'完整名单与核实依据':'完整阵容攻略'}</a> · <a href="${esc(c.source)}">数据来源</a>${c.raw?` · <a href="${esc(c.raw)}">原始详情</a>`:''}</p><small>${esc(c.cohort)}</small></article>`;}
function gear(c){return `<details><summary>已有装备补全 · ${c.builds.length}条出装记录</summary><p>每条出装保留来源均名与样本；未评级不等于 S/A。重复装备分别计件。统计相关性不代表必做。</p><div class="gear" data-id="${esc(c.id)}"><label>携带者<select class="carrier">${E.unique(c.builds.map(b=>b.unit)).map(i=>`<option value="${esc(i)}">${esc(name(i))}</option>`).join('')}</select></label><div class="gear-choices"></div><div class="gear-result"></div></div></details>`;}
function detail(c){return boardHTML(c)+`<details><summary>棋子职责与星级</summary>${c.heroes.map(h=>`<p>${esc(name(h.id))} · ${esc(h.role)} · ${h.stars?`${h.stars}星（来源标记）`:'星级未标'}</p>`).join('')}</details>`+gear(c)+`<details><summary>运营与海克斯</summary><p>${esc(c.route)}</p><p>${esc(c.flow.map(x=>x.join('：')).join(' → ')||'来源仅提供运营类型，未核实具体搜牌回合。')}</p>${c.augments.map(a=>`<p>${esc(({1:'银色',2:'金色',3:'棱彩'})[a.rarity]||'未标阶位')} · ${esc(a.name)}${a.sources?' · 攻略明确推荐':' · 均名 '+decimal(a.avg)+' · 样本 '+num(a.count)}</p>`).join('')||'<p>本次未接入经核实的推荐关系；不表示没有适配海克斯。</p>'}</details>`;}
function fill(box,c,added=[]){
 const rows=boardRows(c,s),calc=E.fill(rows,s.owned,added),unique=E.unique(calc.matches.map(b=>JSON.stringify([...b.units].sort()))).map(x=>({units:JSON.parse(x)}));const freq=E.fill(unique,s.owned,added).frequency;
 box._added=added;box.querySelector('.add').innerHTML='<option value="">选择棋子</option>'+freq.map(([i,n])=>`<option value="${esc(i)}">${esc(name(i))} · ${n}/${unique.length}种组合</option>`).join('');
 const format=b=>`<div class="board"><strong>还需补入：${esc(names(b.units.filter(i=>!calc.owned.includes(i)))||'已凑齐')}</strong><p>完整棋盘：${esc(b.units.map(i=>name(i)+(b.stars[i]?` ${b.stars[i]}星`:'' )).join('、'))}</p><small>${esc(b.source)} · 均名 ${decimal(b.avg)} · 前四 ${b.top4==null?'未提供':decimal(b.top4)+'%'} · 样本 ${num(b.count)}</small>${b.traits?`<p><small>来源羁绊配置：${esc(b.traits)}</small></p>`:''}</div>`;
 box.querySelector('.filled').innerHTML=`<p>已补：${esc(names(added)||'无')} · ${calc.matches.length}条匹配记录</p>`+calc.matches.slice(0,3).map(format).join('')+(calc.matches.length>3?`<details><summary>其余 ${calc.matches.length-3} 条完整记录</summary>${calc.matches.slice(3).map(format).join('')}</details>`:'')+'<small>按棋盘前四率、均名排序，缺失值排后；补牌频次按不同棋子组合计算。不同等级不是同一局转型链。</small>';
}
function equip(box,c,reset=true){
 const carrier=box.querySelector('.carrier').value,rows=c.builds.filter(b=>b.unit===carrier);
 if(reset)box.querySelector('.gear-choices').innerHTML=E.unique(rows.flatMap(b=>b.items)).map(i=>`<label>${esc(items([i]))}<select data-item="${esc(i)}">${[0,1,2,3].map(n=>`<option value="${n}">${n}件</option>`).join('')}</select></label>`).join('');
 const owned=[...box.querySelectorAll('[data-item]')].flatMap(el=>Array(Number(el.value)).fill(el.dataset.item)),matches=E.equipment(rows,owned);
 box.querySelector('.gear-result').innerHTML=owned.length>3?'<p>已选超过3件，请减少。</p>':`<p>${matches.length}条兼容出装</p><div class="table"><table><tr><th>缺少</th><th>完整出装</th><th>评级</th><th>均名 / 样本</th></tr>${matches.map(b=>`<tr><td>${esc(items(b.missing)||'已凑齐')}</td><td>${esc(items(b.items))}</td><td>${esc(b.tier||'未评级')}</td><td>${decimal(b.avg)} / ${num(b.count)}</td></tr>`).join('')}</table></div>`;
}
function recommendationHTML(c){
 if(c.active_final?.relation==='alternative')return '<p class="muted">当前是替代棋盘，已选海克斯的适配关系仍待确认。</p>';
 const selected=c.augments.filter(a=>s.augments.includes(augmentKey(a)));
 if(!selected.length)return c.augment_gap?`<p class="muted">海克斯推荐待补：${esc(c.augment_gap)}</p>`:'';
 const related=selected.filter(a=>a.sources?.length&&a.sources.every(p=>p.match==='related'));
 return related.length?`<p class="muted">${related.map(a=>esc(a.name)).join('、')}：仅有相关分支推荐，当前棋盘适配仍需核对。</p>`:'';
}
function renderAugments(){
 const q=$('augment-query').value.trim().toLowerCase(),rarity=$('augment-rarity').value;
 const groups=augmentGroups(K,s),visible=groups.filter(a=>(rarity==='all'||String(a.rarity)===rarity)&&a.name.toLowerCase().includes(q));
 $('selected-augments').innerHTML=s.augments.map(key=>`<button class="selected-hex" data-hex="${esc(key)}">${esc(groups.find(g=>g.key===key)?.name||key)} ×</button>`).join('');
 $('augment-list').innerHTML=[1,2,3,0].map(r=>{const rows=visible.filter(g=>g.rarity===r);return rows.length?`<h3>${({1:'银色',2:'金色',3:'棱彩',0:'阶位待确认'})[r]} · ${rows.length}</h3><div class="hex-list">${rows.map(a=>`<button class="hex" data-hex="${esc(a.key)}" aria-pressed="${s.augments.includes(a.key)}"><span>${esc(a.name)}</span><small class="hex-count">${a.comps.length}套方向</small></button>`).join('')}</div>`:'';}).join('')||'<p>没有对应的推荐海克斯。</p>';
}
function planningHTML(cs){
 cs=cs.filter(c=>eligibility(K,c,s).ready);
 if(!cs.length)return '<p class="note">当前候选方向均缺少已确认的必需前置，请查看下方阵容提示。</p>';
 if(!s.owned.length)return '<p class="note">选好等级，勾选场上和备战席已有的棋子。系统会挑选上场组合，其余留在备战席。</p>';
 return '<h2>现在怎么上场</h2><p class="muted">优先坐满可确认的人口，再结合棋子费用、自然羁绊结构、同级来源棋盘重合度与已持有核心排序。这是结构建议，未录入星级与装备，尚未模拟技能、站位和对手，不是实战强度排名；最多展示每个方向2组。转职、召唤物及动态羁绊不计入。</p>'+cs.map(c=>{const ps=plan(K,c,s);return `<article><small>${esc(version(c).label)}</small><h3>走向 ${esc(c.name)}</h3>${c.emblem_policy?gateHTML(c)+branchHTML(c):''}${ps.length?ps.map((p,n)=>`<div class="board"><strong>方案 ${n+1} · 上场 ${p.units.length}/${s.current} 人</strong><p>${p.units.map(i=>`<span class="badge">${esc(name(i))} · ${esc(unitRole(c,i).label)}</span>`).join('')}</p><p>备战席：${esc(names(p.bench)||'无')}</p><p>已持有的后期核心（含备战席）：${esc(names(p.core)||'暂无来源确认的核心')}</p><p>自然羁绊：${p.traits.map(t=>esc(t.name)+' '+t.count+'人'+(t.verified?(t.active?'（达到'+t.active+'人档）':'（未激活）'):'（档位待版本核实）')).join(' / ')||'暂无可确认关系'}</p><small>${p.source?'棋子集合完整对应本级来源棋盘；星级与特殊羁绊配置仍需对照。':'根据已有牌推导的组合；与本方向同级来源棋盘最多重合 '+p.overlap+' 张，并非来源实战棋盘。'}${p.excluded.length?' 特殊棋子暂不自动安排：'+esc(names(p.excluded))+'，占位及形态需手动核对。':''}</small><details><summary>棋子去留依据</summary>${[...p.units,...p.bench].map(i=>`<p>${esc(name(i))}：${esc(unitRole(c,i).label)}。${esc(unitRole(c,i).evidence)}</p>`).join('')}</details></div>`).join(''):'<p>该版本还没有可安排的已有棋子；不会把另一个游戏的同名棋子自动代入。</p>'}<p><a href="${esc(c.source)}">阵容来源</a> · <a href="data.json">棋子、羁绊与职责依据</a></p></article>`;}).join('');
}

const materialText=x=>Object.entries(x).filter(([,n])=>n>0).map(([n,q])=>esc(n)+' × '+q).join('、')||'无';
function materialsHTML(cs){
 if(!Object.values(s.componentStock).some(n=>n>0))return '<p>填写已有基础装备数量后，这里比较海克斯候选阵容的散件适合度。</p>';
 const rows=rankMaterials(K,cs,s);if(!rows.length)return '<p>当前海克斯没有共同候选阵容。</p>';
 const best=rows.find(r=>r.ready&&!r.alternative&&!r.uncertain&&r.confidence>0);
 return `<h2>已有散件更适合哪些方向</h2><p>${best?'当前可比较方案中，材料最匹配：<strong>'+esc(best.c.name)+'</strong>（'+esc(version(best.c).label)+'）。':'暂无配装足够完整且满足前置的直接候选，下面仅列参考小计。'}</p><p class="muted">先分完整四位／主C主坦完整／配装不全，再按主C主坦材料覆盖率、全队覆盖率排序；同档并列同样参考。不把缺位当作省装备。只比较当前配装方案，不代表实战最强或所有替代出装的最优解。</p>${rows.map(r=>`<div class="board"><h3>${esc(r.c.name)} <small>${esc(version(r.c).label)}</small></h3><p>${!r.ready?'缺少必需前置 · 暂不推荐':r.alternative?'替代路线参考 · 已选海克斯关系未核实':r.uncertain?'转职前置待核实 · 暂作参考':r.confidence===2?'四位配装完整':r.confidence===1?'主C＋主坦完整，副位仅小计':'配装不全 · 不参与最适合结论'}</p><p>主C＋主坦可覆盖 ${r.primary.matched}/${r.primary.total} 件散件；还缺：<strong>${materialText(r.primary.missing)}</strong></p><p>当前全队配装可覆盖 ${r.total.matched}/${r.total.total} 件；还缺：${materialText(r.total.missing)}</p><p>暂未用到：${materialText(r.total.unused)}</p><p><strong>优先拿：</strong>${!r.confidence?'主C／主坦配装不完整，先参考已知缺口，暂不指定拿装顺序':r.priority.length?r.priority.map(n=>esc(n)+(r.finish[n]?'（再来1件可为'+r.finish[n].map(x=>esc(name(x.unit))+'合成'+esc(K.items[x.item].name)).join(' / ')+'）':'（补主C／主坦缺口）')).join(' → '):Object.keys(r.total.missing).length?'主C主坦散件已够，接着补：'+materialText(r.total.missing):'已列可合成配装的散件已够'}。</p>${r.p.total.special.length?'<p>另有 '+r.p.total.special.length+' 件不可直接折算的特殊装备／配方缺口，不能据散件判断已齐装。</p>':''}<small>“差1件成装”是单件独立选择，不表示这些装备能同时合成；已有散件不会当作已经取得转职。</small></div>`).join('')}`;
}
function coreTargetsHTML(c){
 const confirmed=c.heroes.filter(h=>h.core&&c.units.includes(h.id)),candidates=c.heroes.filter(h=>h.role_candidate&&c.units.includes(h.id));
 const line=h=>`<p><strong>${esc(h.role)} · ${esc(name(h.id))}</strong> <small>${s.owned.includes(h.id)?'已持有':'待补'}</small>${h.role_note?'<br><small>'+esc(h.role_note)+'</small>':''}</p>`;
 return confirmed.map(line).join('')+(confirmed.length?'':'<p>尚无可无条件套用的已确认核心。</p>')+candidates.map(line).join('')+(!confirmed.some(h=>h.role.includes('坦'))?'<p class="muted">主坦尚无明确结论'+(candidates.length?'，以上候选不计入确认核心。':'，保留缺口。')+'</p>':'');
}
function nextHexes(c){
 const seen=new Set();return c.augments.filter(a=>{const key=augmentKey(a);if(s.augments.includes(key)||seen.has(key))return false;seen.add(key);return true;});
}
function nextHexHTML(c,preview=false){
 if(c.active_final?.relation==='alternative')return preview?'<span class="card-line muted">后续海克斯：替代棋盘关系待核实，暂不沿用原阵容推荐。</span>':'';
 const all=nextHexes(c),rarity=r=>({1:'银色',2:'金色',3:'棱彩'})[r]||'阶位待确认';
 const related=a=>a.sources?.length&&a.sources.every(p=>p.match==='related');
 const badge=a=>`<button type="button" class="badge next-hex rarity-${Number(a.rarity)||0}" data-next-hex="${esc(augmentKey(a))}" aria-label="加入已选海克斯：${esc(a.name)}">${esc(a.name)} <small>${rarity(a.rarity)}${related(a)?' · 分支参考':''}</small><span aria-hidden="true"> ＋</span></button>`;
 if(preview){
  const picks=[1,2,3,0].flatMap(r=>all.filter(a=>a.rarity===r));
  return `<span class="card-line"><span class="card-label">后续可考虑的海克斯</span>${all.length?picks.map(badge).join(''):'暂无其他已收录推荐'}</span>`;
 }
 return `<section class="next-hex-section"><h4>后续可考虑的海克斯 · ${all.length} 个</h4><p class="muted">已排除当前所选。以下是本阵容的单项来源推荐，不代表已验证与当前海克斯同时搭配，也不保证后续轮次出现；排列不代表优先级。</p>${[1,2,3,0].map(r=>{const rows=all.filter(a=>a.rarity===r);return rows.length?`<h5>${rarity(r)}</h5>${rows.map(a=>`<div class="next-hex-row">${badge(a)}${a.sources?.length?a.sources.map(p=>`<a href="${esc(p.url)}">${p.match==='related'?'相关分支依据':'推荐依据'}</a>`).join(' · '):`<a href="${esc(c.source)}">阵容来源</a>`}</div>`).join('')}`:'';}).join('')||'<p>暂无其他已收录推荐；不表示其他海克斯无效。</p>'}</section>`;
}
function hexDirectionsHTML(cs){
 if(!cs.length)return '<div class="note"><h2>暂无共同推荐阵容</h2><p>取消一个海克斯可扩大范围；未收录不代表不能搭配。</p></div>';
 return `<div class="result-head"><h2>${s.augments.length?'符合已选海克斯':'已收录'}的阵容 · ${cs.length} 套</h2><p>点击卡片一次展开全部阵容信息。后续海克斯是单项来源推荐，不代表已验证组合，也不保证后续轮次出现。</p></div>${cs.map(c=>{
 const g=eligibility(K,c,s),selected=c.augments.filter(a=>s.augments.includes(augmentKey(a)));
 const formation=formationProfile(K,c);
 const related=selected.some(a=>a.sources?.length&&a.sources.every(p=>p.match==='related'));
 return `<details class="recommendation recommendation-card hex-direction" data-direction="${esc(c.id)}"><summary class="recommendation-summary"><span class="section-head"><span class="rank">${esc(c.original_tier||c.tier)} · 来源评级</span><small>${esc(version(c).label)}</small></span><span class="recommendation-title">${esc(c.name)}</span><span class="card-line"><span class="card-label">阵容类型</span>${esc(c.route)} · ${formation.level}级${formation.estimated?'成型参考（按代表名单占位估算）':'成型棋盘'}</span><span class="card-line"><span class="card-label">固定核心 · 成型变体共同保留</span>${formation.variants>1?(esc(names(formation.core))||'暂无所有变体共同保留的棋子'):'仅有一套成型棋盘，暂不能确认共同核心'}<small class="core-scope">${formation.variants} 套已收录不同棋盘${formation.levels.length?' · '+formation.levels.join('／')+'级':''}；不等于所有打法的永久核心。</small></span><span class="card-line">${selected.length?'推荐海克斯：'+selected.map(a=>esc(a.name)).join('、'):'暂不限定海克斯'}</span>${emblemFitHTML(c)}${nextHexHTML(c,true)}${related?'<span class="card-line muted">仅有相关分支推荐，需核对差异。</span>':''}${g.missing.length?'<span class="card-line">还需：'+g.missing.map(x=>esc(x.name)).join('、')+'</span>':''}${c.active_final?.relation==='alternative'?'<span class="card-line">当前转职条件对应替代棋盘，原海克斯关系尚未确认。</span>':''}${g.pending.length||c.branch_gap?'<span class="card-line muted">转职或成型分支仍待核实。</span>':''}<span class="card-toggle"><span class="when-closed">查看阵容 ↗</span><span class="when-open">收起 ↑</span></span></summary><div class="recommendation-body direction-info"></div></details>`;
 }).join('')}`;
}
function primaryEquipmentHTML(r){
 const fit=r.fit,roles=fit.p.rows.slice(0,2);
 return `<span class="primary-equipment"><span class="card-label">主C／主坦核心配装</span>${roles.map(row=>`<span class="primary-role"><strong>${esc(row.role)}${row.candidate?'候选':''}${row.unit?' · '+esc(name(row.unit)):''}</strong><span>${row.build?esc(items(row.build.items))+' <small>（'+esc(row.build.tier?row.build.tier+'级':'未评级')+'）</small>'+crossBuildNote(row.build):'配装未确认'}</span></span>`).join('')}<span class="card-label">缺少散件 · 拿装优先级</span>${fit.priority.length?fit.priority.map((n,i)=>`<span class="material-priority"><strong>${i+1}. ${esc(n)} × ${fit.primary.missing[n]}</strong><small>共需 ${fit.primary.need[n]} · 已有可用 ${fit.primary.need[n]-fit.primary.missing[n]}</small>${fit.finish[n]?.length?'<small class="finish-hint">再拿 1 件可合：'+esc([...new Set(fit.finish[n].map(x=>K.items[x.item]?.name||x.item))].join('／'))+'（择一）</small>':''}</span>`).join(''):'<span>已知主C／主坦配装的散件已齐。</span>'}<small class="equipment-rule">仅按上方两套配装合计扣除已有散件，不含副C／副坦；优先补能立即合装的散件，再按缺口数量排序。同一散件不重复抵扣，单件可合提示为独立选择。${roles.some(x=>x.missing||x.build?.items.length!==3)?' 主位配装不全，仅为已知需求。':''}${fit.p.primary.special.length?' 特殊装备或未知配方未折算，不能视为已齐。':''}</small></span>`;
}
function combinedHTML(cs){
 if(!s.owned.length)return '<div class="note"><h2>把手里的牌告诉我</h2><p class="muted">选择当前等级、已有棋子和散件，即可比较最适合的三个方向。暂时没有散件也可以先看。</p></div>';
 const result=combinedRecommendations(K,cs,s);
 return `<div class="result-head"><h2>综合推荐${result.top.length?' · '+result.top.length+' 个方向':''}</h2><p>结合手牌与散件的路线建议，非实战胜率排名。</p></div>${result.top.map((r,i)=>`<details class="recommendation recommendation-card"><summary class="recommendation-summary"><span class="section-head"><span class="rank">推荐 0${i+1}</span><small>${esc(version(r.c).label)}</small></span><span class="recommendation-title">${esc(r.c.active_final?.title||r.c.name)}</span><span class="current-board-preview"><span class="card-label">当前 ${Number(s.current)} 级 · 推荐上场 ${r.board.units.length}/${Number(s.current)} 人</span><span class="preview-units">${r.board.units.map(id=>`<span class="badge">${esc(name(id))}</span>`).join('')||'暂无可上场棋子'}</span>${r.board.units.length<Number(s.current)?`<small>还空 ${Number(s.current)-r.board.units.length} 个位置，请补充已有棋子。</small>`:'<small>已安排满当前人口。</small>'}${r.board.bench.length?`<small>暂留备战席：${esc(names(r.board.bench))}</small>`:''}</span><span class="card-line"><span class="card-label">推荐原因</span>已有 ${r.retained.length}/${r.c.units.length} 名成型成员${r.coreHeld.length?'，含'+esc(names(r.coreHeld)):''}；主C＋主坦散件可覆盖 ${r.fit.primary.matched}/${r.fit.primary.total} 件。</span><span class="card-line"><span class="card-label">缺少核心</span>${esc(names(r.missingCore)||(r.cores.length?'已确认核心均已持有':'核心职责仍有缺口'))}${!r.c.heroes.some(h=>h.core&&h.role.includes('坦')&&!h.role.includes('候选'))?'；主坦待确认':''}</span>${emblemFitHTML(r.c)}${primaryEquipmentHTML(r)}<span class="card-toggle"><span class="when-closed">展开上场、合装与完整棋盘 ↓</span><span class="when-open">收起详情 ↑</span></span></summary><div class="recommendation-body"><div class="actions"><div><h4>现在上场 · ${r.board.units.length}/${s.current} 人</h4><p>${r.board.units.map(id=>`<span class="badge">${esc(name(id))} · ${esc(unitRole(r.c,id).label.replace('终局成员 · 核心职责未确认','终局成员'))}</span>`).join('')}</p>${r.board.bench.length?'<p class="muted">备战席：'+esc(names(r.board.bench))+'</p>':''}</div><div><h4>装备先合什么</h4>${r.craft.steps.length?'<ol>'+r.craft.steps.map(x=>`<li><strong>${esc(K.items[x.item].name)}</strong> <small>${x.parts.map(id=>esc(componentName(K.items[id].name))).join('＋')}</small><br>先给${esc(name(x.holder))}${x.holder===x.target?'，后期保留':'打工 → 后期给'+esc(name(x.target))}</li>`).join('')+'</ol><p class="muted">按顺序扣除散件；合装前确认空位，转装需卸装或出售。</p>':'<p>先留散件，暂无适合当前上场棋子的已确认合装。</p>'}<p>优先考虑：<strong>${r.fit.priority.length?r.fit.priority.slice(0,2).map(n=>esc(n)).join(' / '):'主C主坦散件已够，查看副位缺口'}</strong></p></div><div><h4>后面补哪些棋子</h4>${coreTargetsHTML(r.c)}</div></div><section class="final-board"><h4>羁绊、完整棋盘与缺件</h4><p>天然羁绊：${r.board.traits.map(t=>esc(t.name)+' '+t.count+'人'+(t.verified?(t.active?'（'+t.active+'人档）':'（未激活）'):'（档位待核实）')).join(' / ')||'暂无确认归属'}</p><p>主C＋主坦还缺：${materialText(r.fit.primary.missing)}</p><p>完整拿装参考顺序：${r.fit.priority.map(n=>esc(n)).join(" → ")||"主C主坦散件已够"}</p><p>全队还缺：${materialText(r.fit.total.missing)}</p><p>配装携带者候选还缺：${esc(names(r.fit.p.rows.filter(x=>!x.missing&&!s.owned.includes(x.unit)).map(x=>x.unit))||'无')}</p><p>其他成型缺牌：${esc(names(r.missingMembers.filter(id=>!r.missingCore.includes(id)))||'无')}</p><p>目标完整棋盘：${esc(names(r.c.units))}</p><details><summary>核心职责依据</summary>${r.c.heroes.filter(h=>h.role_source).map(h=>`<p>${esc(name(h.id))}：${esc(h.role_note)} <a href="${esc(h.role_source)}">来源</a></p>`).join('')||'沿用原阵容来源标记。'}</details><a data-guide="${esc(r.c.id)}" href="#comp-${esc(r.c.id)}">查看完整攻略与来源</a></section></div></details>`).join('')||'<p class="note">当前没有同时满足手牌、配装证据和前置要求的直接推荐，不强凑三套。可补充手牌或查看候选攻略。</p>'}${result.top.length&&result.top.length<3?'<p class="muted">可用方向不足三套，未用证据不足的方案补位。</p>':''}<details><summary>推荐依据与待确认方向</summary><p class="muted">成型棋子持有比例30分、来源核心持有比例20分、主C主坦散件覆盖30分、全队散件覆盖10分、当前可上场人数比例10分。核心未核实不补分；相同成型名单只占一个名额。上场方案在搜索返回的至多两组中，按可合成且有携带依据的装备每件加5分比较。未录星级、已穿装备及对手，权重为启发式，不保证最优战力。</p>${result.references.map(r=>`<p>${esc(r.c.name)}：${!r.fit.ready?'缺少必需前置':r.fit.alternative?'替代路线的海克斯关系未核实':r.fit.uncertain||r.c.branch_gap?'转职或成型棋盘仍有缺口':!r.board?'该版本暂无可用手牌':'主C／主坦配装证据不完整'}</p>`).join('')}</details>`;
}
function flowRender(){
 const step=Number.isInteger(s.step)&&s.step>=0&&s.step<=2?s.step:2;s.step=step;
 const hand=unitGroups(K,s).filter(g=>g.ids.some(id=>s.owned.includes(id)));
 const groups=augmentGroups(K,s);
 const hexNames=s.augments.map(key=>groups.find(g=>g.key===key)?.name||key);
 const handNames=hand.map(g=>name(g.ids[0]));
 const stock=Object.entries(s.componentStock).filter(([,n])=>n>0).map(([name,n])=>name+' × '+n);
 const summaries=[hexNames.join('、')||(s.showAll?'暂不限定海克斯':'未选择海克斯'),s.current+'级 · '+(handNames.join('、')||'未选择棋子'),s.ownedEmblems.join('、')||'未选择转职'];
 ['选海克斯','选棋子','选转职'].forEach((title,i)=>{const b=$('flow-'+i);b.innerHTML=`<span class="node-number">${i+1}</span><span><b>${title}</b><small>${esc(summaries[i])}</small></span>`;b.ariaCurrent=i===step?'step':'false';});
 $('flow-hex').hidden=step!==0;$('planning-input').hidden=step!==1&&step!==2;$('flow-units').hidden=step!==1;$('flow-items').hidden=step!==2;$('flow-output').hidden=false;$('flow-inputs').hidden=false;$('flow-workspace').className='flow-workspace';
 $('flow-back').hidden=step===0;$('flow-next').hidden=step===2;$('flow-next').textContent=['下一步：选棋子','下一步：选转职'][step]||'下一步';
}
function goStep(step){s.step=Math.max(0,Math.min(2,step));if(s.step>0&&!s.augments.length)s.showAll=true;render();}
$('flow-nav').addEventListener('click',e=>{const b=e.target.closest('[data-step]');if(b)goStep(Number(b.dataset.step));});
$('flow-next').addEventListener('click',()=>goStep(s.step+1));$('flow-back').addEventListener('click',()=>goStep(s.step-1));
function emblemFitHTML(c){const fit=emblemFit(K,c,s);if(!fit.rows.length)return '';return '<div class="coach-current"><strong>转职适配 · 成型棋盘</strong>'+fit.rows.map(r=>'<p>'+esc(r.name)+'：'+r.before+' → '+r.after+' 人'+(!r.holder?' · 暂无可用携带者':r.verified?(r.gain?' · 开启 '+r.active+' 人档':' · 未跨档'):' · 档位待核实')+'</p>').join('')+'<small>按可携带棋子估算；需调整承装。转职适配是结构评分，不代表实测强度。</small></div>';}
function transitionCoachHTML(cs){
 const rows=transitionCoach(K,cs,s),level=Number(s.current);
 if(!s.owned.length)return '<div class="note"><h2>逐级过渡教练</h2><p>选择当前等级和手上的棋子，例如3级有5张牌，教练会挑出可上场的3张；海克斯可以暂不选。</p></div>';
 if(!rows.length)return '<div class="note"><h2>逐级过渡教练</h2><p>当前没有符合前置条件且有可安排手牌的方向。请补充棋子或调整海克斯条件。</p></div>';
 const card=(r,index)=>{const best=r.next[0];return `<article class="transition-coach-card"><small>方向 ${index+1} · ${esc(version(r.c).label)}</small><h3>${esc(r.c.active_final?.title||r.c.name)}</h3><div class="coach-overview">${s.ownedEmblems.length?'<strong>综合匹配度 '+Math.round((0.6*r.similarity+0.4*r.emblem.score)*100)+'%</strong>':''}<strong>手牌匹配度 ${Math.round(r.similarity*100)}%</strong><span>${r.match?r.match.hits+'/'+r.match.board.units.length+' 张 · 对照'+r.match.board.level+'级棋盘':'暂无相邻等级记录'}</span></div><p class="coach-matched-augments"><strong>已匹配海克斯：</strong>${r.c.augments.filter(a=>s.augments.includes(augmentKey(a))).map(a=>'<span class="badge">'+esc(a.name)+'</span>').join('')||'未选择海克斯'}</p>${emblemFitHTML(r.c)}<p><strong>阵容风格：</strong>${esc(r.c.route||'运营节奏待确认')}</p><p><strong>建议补牌（升到 ${level+1}级）：</strong>${best?(esc(names(best.find))||'所需棋子已在手牌中'):'下一级来源棋盘缺失，暂不指定'}</p><p class="coach-current"><strong>${level}级 · 上场 ${r.current.units.length}/${level} 人：</strong>${esc(names(r.current.units))}${r.missingSlots?' · 还空 '+r.missingSlots+' 人':''}</p><details class="coach-detail"><summary>查看备战席、羁绊与换人方案</summary><p>备战席：${esc(names(r.current.bench))||'无'}</p>${expectedTraitsHTML(r.c,r.current.units)}<p>成型固定核心 · 保留：${esc(names(r.core))||'暂无已确认核心'}</p>${r.next.slice(0,3).map((n,i)=>`<div class="next-level-plan"><strong>升到 ${level+1}级 · 方案 ${i+1}</strong><p>要找：${esc(names(n.find))||'手牌已齐'}</p><p>备战席补入：${esc(names(n.fromBench))||'无'}</p><p>保留：${esc(names(n.keep))||'无'}</p><p>换下：${esc(names(n.remove))||'无需换人'}</p><p>完整组合：${esc(names(n.units))}</p>${expectedTraitsHTML(r.c,n.units)}</div>`).join('')||'<p>没有可衔接并保留成型核心的下一级来源棋盘。</p>'}<small>当前上场按手牌推导；升级补齐后再换人，携装棋子先处理装备。匹配度是手牌覆盖来源棋盘的比例，不是胜率。</small></details></article>`;};
 return `<h2>逐级过渡教练 · ${level} → ${level+1}级</h2><p class="muted">未选转职按手牌匹配度排序；选了转职按手牌60%＋转职适配40%排序。跨过已核实档位优先，其次为补充已有羁绊；本级无记录时参考下一级。先看未来方向与补牌，点击展开换人细节。</p>${rows.slice(0,3).map(card).join('')}${rows.length>3?'<details><summary>其他方向 · '+(rows.length-3)+' 套</summary>'+rows.slice(3).map((r,i)=>card(r,i+3)).join('')+'</details>' :''}`;
}
function excludedPrerequisitesHTML(cs){
 const rows=excludedPrerequisites(K,cs,s);if(!rows.length)return '';
 return `<details class="excluded-prerequisites"><summary>缺少前置条件的阵容 · ${rows.length} 套</summary><p class="muted">这些阵容符合已选海克斯方向，但尚未满足硬性前置。拿到条件后更新左侧选择，会重新参与推荐。</p>${rows.map(({c,missing})=>`<div class="excluded-composition"><div class="section-head"><strong>${esc(c.name)}</strong><small>${esc(version(c).label)}</small></div><p>还缺：${missing.map(x=>`<span class="badge missing-condition">${x.kind==='item'?'转职':x.kind==='augment'?'专属海克斯':'条件'} · ${esc(x.name)}</span>`).join('')}</p><small>以上条件需全部满足；仅供后续规划，不计入当前推荐。</small></div>`).join('')}</details>`;
}
function render(){
 const rows=directions(K,s),eligibleRows=rows.filter(c=>recommendationEligible(K,c,s)).sort((a,b)=>emblemFit(K,b,s).score-emblemFit(K,a,s).score),scope=scoped(K,s),groups=augmentGroups(K,s);
 $('status').textContent=s.augments.length?`已选 ${s.augments.length} 个海克斯 · ${eligibleRows.length} 套可推荐方向 · ${rows.length-eligibleRows.length} 套因前置未满足或路线待核实而排除`:`${groups.length} 个推荐海克斯 · 覆盖 ${scope.filter(c=>c.augments.length).length} / ${scope.length} 套阵容`;
 $('results').innerHTML=!s.augments.length&&!s.showAll?'<div class="note"><h2>先选一个你拿到的海克斯</h2><p>这里会显示它能走向的最终阵容、成型棋子、运营路线和推荐依据。拿到第二个海克斯后可继续点击，找共同方向。</p></div>':rows.map(card).join('')||'<p class="note">没有同时推荐这些海克斯的已收录阵容。可以取消一项查看其他方向；未收录不代表无法搭配。</p>';
 $('combined-recommendations').innerHTML=s.coach?transitionCoachHTML(eligibleRows)+excludedPrerequisitesHTML(rows):(!s.augments.length&&!s.showAll)?'<div class="note"><h2>先选海克斯，再决定往哪走</h2><p class="muted">在第一个节点选择已拿到的海克斯，再补充手牌和散件。选择后这里立即显示匹配阵容，无需先填写手牌。</p></div>':(s.step===0||!s.owned.length?hexDirectionsHTML(eligibleRows):combinedHTML(eligibleRows))+excludedPrerequisitesHTML(rows);
 $('coach-toggle').textContent=s.coach?'返回最终阵容推荐':'打开逐级过渡教练';$('coach-toggle').setAttribute?.('aria-pressed',String(!!s.coach));
 $('hand-count').textContent=unitGroups(K,s).filter(g=>g.ids.some(id=>s.owned.includes(id))).length+' 名';
 $('emblem-count').textContent=s.ownedEmblems.length?s.ownedEmblems.length+' 个':'';
 $('material-matches').innerHTML=(!s.augments.length&&!s.showAll)?'':materialsHTML(eligibleRows);
 $('planning-input').hidden=!s.augments.length&&!s.showAll;
 $('plans').innerHTML=(!s.augments.length&&!s.showAll)?'':planningHTML(eligibleRows);
 renderUnitChoices();renderAugments();flowRender();save();
}
$('coverage').innerHTML=`<p>金铲铲15套有来源推荐；TFT ${K.augment_coverage.tft_covered}/22套接入作者推荐（其中${K.augment_coverage.related_only}套仅有相关分支参考），另${K.augment_coverage.tft_total-K.augment_coverage.tft_covered}套保留缺口。</p><ul>${K.comps.filter(c=>c.augment_gap).map(c=>`<li>${esc(c.name)}：${esc(c.augment_gap)}</li>`).join('')}</ul><p>另有${K.augment_coverage.unmapped.length}个来源条目无法核实中文名与阶位，未进入筛选。</p>`;
const dialog=$('direction-dialog');let dialogComp=null;
function openDirection(id){const original=K.comps.find(c=>c.id===id);if(!original)return;$('direction-title').textContent=original.name;dialogComp=activeComp(K,original,s);$('direction-content').innerHTML=fullDirectionHTML(dialogComp);dialog.showModal();dialog.scrollTop=0;}
$('direction-content').addEventListener('click',e=>{const b=e.target.closest('[data-view-level]');if(!b||!dialogComp)return;const box=$('direction-levels');box.innerHTML=levelNavigatorHTML(dialogComp,Number(b.dataset.viewLevel));box.querySelector?.('[data-view-level="'+b.dataset.viewLevel+'"]')?.focus();});
$('direction-close').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
$('combined-recommendations').addEventListener('click',e=>{
 const next=e.target.closest('[data-next-hex]');
 if(next){
  e.preventDefault();e.stopPropagation();
  const key=next.dataset.nextHex;
  if(s.augments.includes(key)||!augmentGroups(K,s).some(a=>a.key===key))return;
  s.augments=[...s.augments,key];s.mode='all';s.emblem='';s.augment='';s.showAll=false;controls();render();return;
 }
 const direction=e.target.closest('.hex-direction');if(direction){e.preventDefault();openDirection(direction.dataset.direction);return;}
 if(e.target.closest('[data-guide]'))$('all-results').open=true;
});
$('augment-list').addEventListener('click',chooseHex);$('selected-augments').addEventListener('click',chooseHex);
function chooseHex(e){const b=e.target.closest('[data-hex]');if(!b)return;const key=b.dataset.hex;s.augments=s.augments.includes(key)?s.augments.filter(k=>k!==key):[...s.augments,key];s.mode='all';s.emblem='';s.augment='';s.showAll=false;controls();render();}
$('augment-query').addEventListener('input',renderAugments);$('augment-rarity').addEventListener('change',renderAugments);
$('clear-hex').addEventListener('click',()=>{s.augments=[];s.showAll=false;render();});$('show-all').addEventListener('click',()=>{s.augments=[];s.showAll=true;goStep(1);});
$('results').addEventListener('toggle',e=>{if(!e.target.matches('.card-detail')||!e.target.open||e.target.dataset.loaded)return;const c=activeComp(K,K.comps.find(c=>c.id===e.target.dataset.id),s);e.target.querySelector('.detail-body').innerHTML=detail(c);e.target.dataset.loaded='1';const box=e.target.querySelector('.fill');if(box)fill(box,c);equip(e.target.querySelector('.gear'),c);},true);
$('results').addEventListener('change',e=>{let box=e.target.closest('.fill');if(box&&e.target.matches('.add')&&e.target.value)fill(box,K.comps.find(c=>c.id===box.dataset.id),[...box._added,e.target.value]);box=e.target.closest('.gear');if(box)equip(box,activeComp(K,K.comps.find(c=>c.id===box.dataset.id),s),e.target.matches('.carrier'));});
$('results').addEventListener('click',e=>{if(e.target.matches('.clear-add')){const box=e.target.closest('.fill');fill(box,K.comps.find(c=>c.id===box.dataset.id));}});
$('component-stock').addEventListener('input',e=>{const n=e.target.dataset.component;if(!stockOptions(K).includes(n))return;s.componentStock=cleanStock(K,{...s.componentStock,[n]:e.target.value});e.target.value=String(s.componentStock[n]);render();});
$('coach-toggle').addEventListener('click',()=>{s.coach=!s.coach;if(s.coach){s.step=1;s.showAll=true;}render();});
$('clear-items').addEventListener('click',()=>{s.componentStock={};s.ownedEmblems=[];s.bag=[];s.profiles={};stockControls();controls();render();});
$('clear-components').addEventListener('click',()=>{s.componentStock={};stockControls();render();});
$('owned-emblems').addEventListener('change',e=>{if(!e.target.matches('input'))return;s.ownedEmblems=e.target.checked?E.unique([...s.ownedEmblems,e.target.value]):s.ownedEmblems.filter(n=>n!==e.target.value);render();});
$('units').addEventListener('change',e=>{if(e.target.matches('input')){chooseUnit(K,s,e.target.value,e.target.checked);render();}});
for(const id of ['version','mode','current','target','tier','emblem','augment'])$(id).addEventListener('change',()=>{s[id]=$(id).value;if(id==='version')s=changeVersion(s,s.version);if(['version','current'].includes(id))controls();render();});
$('search').addEventListener('input',()=>{s.search=$('search').value;render();});$('clear').addEventListener('click',()=>{s.owned=[];s.profiles={};controls();render();});$('reset').addEventListener('click',()=>{s={...defaults,owned:[],profiles:{},bag:[],ownedEmblems:[],componentStock:{},augments:[]};$('augment-query').value='';$('augment-rarity').value='all';stockControls();controls();render();});
for(const id of [...s.owned]){chooseUnit(K,s,id,true);const saved=s.profiles[id];if(saved){setSharedProfile(K,s,id,'stars',saved.stars||1);for(let n=0;n<3;n++)if(saved.items?.[n])setSharedProfile(K,s,id,String(n),saved.items[n]);}}
stockControls();controls();render();
})(typeof globalThis!=='undefined'?globalThis:this);
