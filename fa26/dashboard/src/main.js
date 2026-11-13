import Chart from "chart.js/auto";
import { configured, getJson, getRowsCsv } from "./db.js";


const C = {b950:"#21304a",b800:"#355a98",b700:"#3a6ebb",b600:"#4582cc",b400:"#78b7e2",b300:"#a4d0ec",b200:"#c9e2f4",b100:"#e1eef8",
  red:"#bc5046",red3:"#edb9b4",gold:"#d4a92c",green:"#0d8e50",green3:"#75e0a4",purple:"#a849b0",purple3:"#e6bbec",gray:"#9aa3ae",muted:"#5b6676"};
const YEARS = Array.from({length:18},(_,i)=>2008+i);
const EX = ["1","2","3","4","5","6","7(A)","7(B)","7(C)","7(D)","7(E)","7(F)","8","9"];
const BK = ["1-20","21-60","61-100","101-200","201-400","401+"];
const NX = [["NoRecords","No records"],["Referred","Referred"],["Withdrawn","Withdrawn"],["FeeRelated","Fee-related"],["NotDescribed","Not described"],["ImproperRequest","Improper"],["NotAgency","Not agency record"],["Duplicate","Duplicate"],["InLitigation","In litigation"],["ExpeditedDenial","Expedited denial"],["Other","Other"]];
const TOP10 = ["Department of Homeland Security","Department of Justice","Department of Veterans Affairs","Department of Defense","Department of Health and Human Services","U.S. Department of State","National Archives and Records Administration","Department of Agriculture","Department of Transportation","Equal Employment Opportunity Commission"];

// kind: line (trend) | stack (shares per year) | bar (categories, summed over the period) | statutes
const SECTIONS = [
 {id:"req", name:"Requests", desc:"How many requests come in, get processed, and how they end", types:[
  {n:"01",t:"Requests",s:"Received, processed and pending at year end",k:"line",m:[["req_recv","Received",C.b600],["req_proc","Processed",C.b950],["req_pend","Pending at year end",C.red]]},
  {n:"02",t:"How requests end",s:"Share of processed requests by outcome",k:"stack",m:[["d_full","Full grant",C.b800],["d_part","Partial grant",C.b400],["d_deny","Full denial",C.red],["d_norec","No records",C.gold],["d_other","Other reasons",C.b200]]},
  {n:"03",t:"\"Other\" reasons",s:"Requests closed for an \"other\" reason (reasons are listed in a separate table)",k:"line",m:[["o3","Closed for other reasons",C.purple]]},
  {n:"04",t:"Expedited processing",s:"Requests asking for faster processing",k:"line",m:[["ex_grant","Granted",C.b600],["ex_deny","Denied",C.red]]},
  {n:"29",t:"Revisions",s:"Requests received: as first reported vs this year's report",k:"line",dash:1,m:[["c29_rl","Last year's report",C.gray],["c29_rc","Current report",C.b600]]},
 ]},
 {id:"time", name:"Processing time", desc:"How long agencies take, by track", types:[
  {n:"14",t:"Median days to respond",s:"All processed requests, by track",k:"line",days:1,m:[["t14_s","Simple",C.b600],["t14_c","Complex",C.red],["t14_e","Expedited",C.gold]]},
  {n:"15",t:"Median days, granted",s:"Only requests where records were released",k:"line",days:1,m:[["t15_s","Simple",C.b600],["t15_c","Complex",C.red],["t15_e","Expedited",C.gold]]},
  {n:"16",t:"Simple: days to respond",s:"Simple requests processed in each day range (total over the period)",k:"bar",m:BK.map(b=>["b16_"+b,b+" days",C.b600])},
  {n:"17",t:"Complex: days to respond",s:"Complex requests processed in each day range (total over the period)",k:"bar",m:BK.map(b=>["b17_"+b,b+" days",C.red])},
  {n:"18",t:"Expedited: days to respond",s:"Expedited requests processed in each day range (total over the period)",k:"bar",m:BK.map(b=>["b18_"+b,b+" days",C.gold])},
  {n:"19",t:"Pending requests",s:"Requests still open at year end, by track",k:"line",m:[["p19_s","Simple",C.b600],["p19_c","Complex",C.red],["p19_e","Expedited",C.gold]]},
  {n:"20",t:"Oldest pending request",s:"Days the oldest open request has been waiting",k:"line",days:1,m:[["a20_old","Oldest request (days)",C.b950]]},
 ]},
 {id:"ex", name:"Exemptions", desc:"Why information is withheld", types:[
  {n:"05",t:"Exemptions used",s:"Times each FOIA exemption was applied (total over the period)",k:"bar",m:EX.map(e=>["x5_"+e,"Ex. "+e,C.purple])},
  {n:"06",t:"Exemption 3 statutes",s:"Statutes the agency relied on most (last year of the period)",k:"statutes"},
  {n:"24",t:"Exclusions",s:"Times subsection (c) exclusions were used",k:"line",m:[["excl","Times used",C.purple]]},
 ]},
 {id:"app", name:"Appeals", desc:"What happens when requesters push back", types:[
  {n:"07",t:"Appeals",s:"Received, processed and pending at year end",k:"line",m:[["ap_recv","Received",C.b600],["ap_proc","Processed",C.b950],["ap_pend","Pending at year end",C.red]]},
  {n:"08",t:"How appeals end",s:"Share of processed appeals by outcome",k:"stack",m:[["ad_aff","Upheld",C.b800],["ad_part","Partly reversed",C.b400],["ad_rev","Fully reversed",C.green],["ad_oth","Closed other",C.b200]]},
  {n:"09",t:"Exemptions on appeal",s:"Exemptions applied when denials were upheld (total over the period)",k:"bar",m:EX.map(e=>["x9_"+e,"Ex. "+e,C.purple])},
  {n:"10",t:"Other denial reasons",s:"Non-exemption reasons for denial on appeal (total over the period)",k:"bar",m:NX.map(([k,l])=>["n10_"+k,l,C.b600])},
  {n:"11",t:"\"Other\" appeal reasons",s:"Appeals closed for an \"other\" reason",k:"line",m:[["o11","Closed for other reasons",C.purple]]},
  {n:"12",t:"Days to decide",s:"Days to decide an appeal",k:"line",days:1,m:[["ar_med","Median",C.b600],["ar_avg","Average",C.b300]]},
  {n:"13",t:"Oldest pending appeal",s:"Days the oldest open appeal has been waiting",k:"line",days:1,m:[["a13_old","Oldest appeal (days)",C.b950]]},
  {n:"31",t:"Revisions",s:"Appeals received: as first reported vs this year's report",k:"line",dash:1,m:[["c31_rl","Last year's report",C.gray],["c31_rc","Current report",C.b600]]},
 ]},
 {id:"back", name:"Backlog", desc:"What is left over past the legal deadline, and work from other agencies", types:[
  {n:"26",t:"Backlog",s:"Requests and appeals past the deadline at year end",k:"line",m:[["bl_req","Backlogged requests",C.red],["bl_app","Backlogged appeals",C.purple]]},
  {n:"30",t:"Request backlog vs last year",s:"Last year's backlog vs this year's",k:"line",dash:1,m:[["c30_l","Last year",C.gray],["c30_c","This year",C.red]]},
  {n:"32",t:"Appeal backlog vs last year",s:"Last year's appeal backlog vs this year's",k:"line",dash:1,m:[["c32_l","Last year",C.gray],["c32_c","This year",C.purple]]},
  {n:"27",t:"Consultations",s:"Requests other agencies sent here for review",k:"line",m:[["co_recv","Received",C.b600],["co_proc","Processed",C.b950],["co_pend","Pending",C.red]]},
  {n:"28",t:"Oldest consultation",s:"Days the oldest open consultation has been waiting",k:"line",days:1,m:[["a28_old","Oldest (days)",C.b950]]},
 ]},
 {id:"res", name:"Staff & costs", desc:"Resources behind FOIA, fee waivers and proactive posting", types:[
  {n:"22",t:"FOIA staff",s:"Full-time FOIA staff (FTE)",k:"line",m:[["staff","Total staff (FTE)",C.b600],["staff_ft","Full-time employees",C.b300]]},
  {n:"23",t:"FOIA costs",s:"Total and litigation costs, and fees collected ($)",k:"line",money:1,m:[["cost","Total cost",C.b600],["cost_lit","Litigation cost",C.red],["fees","Fees collected",C.green]]},
  {n:"21",t:"Fee waivers",s:"Requests to waive fees",k:"line",m:[["fw_grant","Granted",C.b600],["fw_deny","Denied",C.red]]},
  {n:"25",t:"Proactive disclosures",s:"Records posted online without a request",k:"line",m:[["pd_foia","By FOIA office",C.b600],["pd_prog","By program offices",C.b300]]},
 ]},
];

// ---------------- data ----------------
let META, KI, ROWS=[], TOPI=[], ROW_BY_ID=new Map();
const LOADED=new Set(); const STATUTES={};
// ag: -2 = top 10 (each agency separately), -1 = all agencies, >=0 one agency
const S = {ag:-2, cp:-1, y0:2015, y1:2025, pending:false, sec:"req", type:{}, mIdx:0};
let chart=null, compsChart=null, renderToken=0;
const BASE_KEYS=["req_recv","req_proc","bl_req","t14_c"];

async function load(){
  if(!configured) throw new Error("Supabase is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY (see README).");
  const [metrics, agencies, comps] = await Promise.all([
    getJson("metrics","key,col,kind","ord"), getJson("agencies","id,name,abbr","id"), getJson("components","agency_id,idx,code,name","agency_id,idx")]);
  META = {keys:metrics.map(m=>m.key), col:{}, kind:{}, agencies:[], abbr:[], components:{}};
  metrics.forEach(m=>{META.col[m.key]=m.col; META.kind[m.key]=m.kind;});
  agencies.forEach(a=>{META.agencies[a.id]=a.name; META.abbr[a.id]=a.abbr||"";});
  comps.forEach(c=>{(META.components[c.agency_id] ||= [])[c.idx]=[c.code||"", c.name||""];});
  KI = Object.fromEntries(META.keys.map((k,i)=>[k,i]));
  const {header, rows} = await getRowsCsv(["fy","agency_id","comp_idx"]);
  const iy=header.indexOf("fy"), ia=header.indexOf("agency_id"), ic=header.indexOf("comp_idx");
  for(const p of rows){ const r={id:+p[0],fy:+p[iy],a:+p[ia],c:+p[ic],v:new Float64Array(META.keys.length).fill(NaN)}; ROWS.push(r); ROW_BY_ID.set(r.id,r); }
  await ensure(BASE_KEYS);
  TOPI = TOP10.map(n=>META.agencies.indexOf(n)).filter(i=>i>=0);
  SECTIONS.forEach(s=>S.type[s.id]=s.types[0].n);
}
// Fetch the metric columns a view needs, once each.
async function ensure(keys){
  const need=[...new Set(keys)].filter(k=>k in KI && !LOADED.has(k));
  if(!need.length) return;
  const {header, rows} = await getRowsCsv(need.map(k=>META.col[k]));
  const idx=need.map(k=>[KI[k], header.indexOf(META.col[k])]);
  for(const p of rows){ const r=ROW_BY_ID.get(+p[0]); if(!r) continue;
    for(const [ki,hi] of idx){ const x=p[hi]; r.v[ki]= (x===""||x==null)?NaN:+x; } }
  need.forEach(k=>LOADED.add(k));
}
async function loadStatutes(ag){
  if(STATUTES[ag]) return STATUTES[ag];
  const rows=await getJson(`statutes_top`,"fy,rank,statute,times",`fy,rank&agency_id=eq.${ag}`);
  const m={}; rows.forEach(r=>{(m[r.fy] ||= []).push([r.statute, r.times]);});
  return (STATUTES[ag]=m);
}
const median = a => {a=a.filter(x=>!isNaN(x)).sort((x,y)=>x-y); if(!a.length) return NaN; const m=a.length>>1; return a.length%2?a[m]:(a[m-1]+a[m])/2;};
const PY = () => YEARS.filter(y=>y>=S.y0&&y<=S.y1);
function rowsFor(fy, ag=S.ag, cp=S.cp){
  if(ag===-1) return ROWS.filter(r=>r.fy===fy&&r.c===-1);
  if(ag===-2) return ROWS.filter(r=>r.fy===fy&&r.c===-1&&TOPI.includes(r.a));
  if(cp<0) return ROWS.filter(r=>r.fy===fy&&r.a===ag&&r.c===-1);
  return ROWS.filter(r=>r.fy===fy&&r.a===ag&&r.c===cp);
}
function agg(rs,k){ const i=KI[k], vals=rs.map(r=>r.v[i]).filter(x=>!isNaN(x)); if(!vals.length) return NaN;
  if(rs.length===1) return vals[0]; const kind=META.kind[k];
  if(kind==="avg") return median(vals); if(kind==="max") return Math.max(...vals); return vals.reduce((s,x)=>s+x,0); }
const series = (k, ag=S.ag, cp=S.cp) => PY().map(fy=>agg(rowsFor(fy,ag,cp),k));
const periodTotal = (k, ag=S.ag, cp=S.cp) => { const s=series(k,ag,cp).filter(x=>!isNaN(x)); if(!s.length) return NaN;
  return META.kind[k]==="sum" ? s.reduce((a,b)=>a+b,0) : median(s); };
const hasYear = fy => rowsFor(fy).length>0;
const fmt = (x,money)=>{ if(x==null||isNaN(x)) return "–"; const a=Math.abs(x), p=money?"$":"";
  if(a>=1e9) return p+(x/1e9).toFixed(2)+"B"; if(a>=1e6) return p+(x/1e6).toFixed(a>=1e7?1:2)+"M";
  if(a>=1e4) return p+Math.round(x/1e3)+"K"; if(a>=1e3) return p+(x/1e3).toFixed(1)+"K"; return p+(Math.round(x*10)/10).toLocaleString(); };
const agShort = i => META.abbr[i] || META.agencies[i].replace("Department of ","").slice(0,22);

// ---------------- controls ----------------
const $ = id => document.getElementById(id);
function buildControls(){
  const others = META.agencies.map((a,i)=>i).filter(i=>!TOPI.includes(i));
  const opt = i => `<option value="${i}">${META.agencies[i]}${META.abbr[i]?" ("+META.abbr[i]+")":""}</option>`;
  $("ag").innerHTML = `<optgroup label="Overview"><option value="-2">Top 10 priority agencies (compare)</option><option value="-1">All 128 agencies (government total)</option></optgroup>`+
    `<optgroup label="Top 10 priority agencies">${TOPI.map(opt).join("")}</optgroup><optgroup label="All other agencies">${others.map(opt).join("")}</optgroup>`;
  $("ag").onchange=()=>{S.ag=+$("ag").value; S.cp=-1; buildComps(); render();};
  $("cp").onchange=()=>{S.cp=+$("cp").value; render();};
  $("nav").innerHTML=SECTIONS.map(s=>`<button data-s="${s.id}">${s.name}<span>${s.types.length}</span></button>`).join("");
  $("nav").querySelectorAll("button").forEach(b=>b.onclick=()=>{S.sec=b.dataset.s; S.mIdx=0; render();});
  $("measure").onchange=()=>{S.mIdx=+$("measure").value; renderMain();};
  const pre=[["All years",2008,2025],["Last 10 years",2016,2025],["Last 5 years",2021,2025],["FY2025 only",2025,2025]];
  $("presets").innerHTML=pre.map(([l,a,b])=>`<button data-a="${a}" data-b="${b}">${l}</button>`).join("");
  $("presets").querySelectorAll("button").forEach(b=>b.onclick=()=>{S.y0=+b.dataset.a; S.y1=+b.dataset.b; S.pending=false; render();});
  buildComps();
}
function buildComps(){
  const cp=$("cp"), list = S.ag<0?null:META.components[S.ag];
  if(!list){cp.innerHTML=`<option value="-1">${S.ag<0?"Pick one agency first":"Agency reports as one organization"}</option>`; cp.disabled=true;
    $("cpHint").textContent = S.ag<0?"":"No separate components in the data"; return;}
  cp.disabled=false;
  cp.innerHTML='<option value="-1">All components (agency total)</option>'+list.map(([ab,nm],i)=>`<option value="${i}">${ab}${nm&&nm!==ab?" · "+nm:""}</option>`).join("");
  $("cpHint").textContent = list.length+" components · see the bar chart below the main chart";
}
function clickYear(y){
  if(!S.pending){ S.start=y; S.y0=y; S.y1=y; S.pending=true; }
  else { S.y0=Math.min(S.start,y); S.y1=Math.max(S.start,y); S.pending=false; }
  render();
}

// ---------------- render ----------------
async function render(){
  const t=curType(), my=++renderToken;
  const keys=[...BASE_KEYS, ...(t.m||[]).map(m=>m[0])];
  if(keys.some(k=>k in KI && !LOADED.has(k))){
    if(chart){chart.destroy(); chart=null;} $("chartbox").innerHTML='<div class="empty">Loading…</div>';
    try{ await ensure(keys); }catch(e){ $("chartbox").innerHTML=`<div class="empty">Could not load this data type: ${e.message}</div>`; console.error(e); return; }
    if(my!==renderToken) return;
  }
  renderNow();
}
function renderNow(){
  const tr=$("track"), w=100/(YEARS.length-1), i0=YEARS.indexOf(S.y0), i1=YEARS.indexOf(S.y1);
  tr.innerHTML=`<div class="rail"></div><div class="fill" style="left:calc(10px + (100% - 20px)*${i0/(YEARS.length-1)});width:calc((100% - 20px)*${(i1-i0)/(YEARS.length-1)})"></div>`+
    YEARS.map(y=>`<button class="yr ${y===S.y0||y===S.y1?"end":(y>S.y0&&y<S.y1?"in":"")} ${hasYear(y)?"":"na"}" data-y="${y}" title="FY${y}"><div class="dot"></div><span>${y}</span></button>`).join("");
  tr.querySelectorAll(".yr").forEach(b=>b.onclick=()=>clickYear(+b.dataset.y));
  $("tlTitle").textContent = S.y0===S.y1 ? `Period: FY${S.y0}` : `Period: FY${S.y0} – FY${S.y1}`;
  $("tlHelp").textContent = S.pending ? `Start: FY${S.y0}. Now click the end year (or the same year for one year)` : "Click a start year, then an end year · or use the buttons";
  $("tlCov").textContent = "Dashed circle = not reported for this selection";
  $("presets").querySelectorAll("button").forEach(b=>b.classList.toggle("on",+b.dataset.a===S.y0&&+b.dataset.b===S.y1));
  const agName = S.ag===-2?"Top 10 priority agencies":S.ag===-1?"All 128 agencies":META.agencies[S.ag];
  const cpName = S.cp<0?"":" › "+META.components[S.ag][S.cp].filter(Boolean).join(" · ");
  $("ctx").innerHTML = `Showing <b>${agName}${cpName}</b> · <b>${S.y0===S.y1?"FY"+S.y0:"FY"+S.y0+"–FY"+S.y1}</b>`;
  $("agHint").textContent = S.ag===-2?"Each agency shown side by side (placeholder list)":S.ag===-1?"Counts are added up across agencies":(META.components[S.ag]?"Has components":"Reports as one organization");
  $("ag").value=S.ag; $("cp").value=S.cp;
  $("nav").querySelectorAll("button").forEach(b=>b.classList.toggle("on", b.dataset.s===S.sec));
  renderKpis(); renderChips(); renderMain(); renderComps();
}
function renderKpis(){
  const items=[["req_recv","Requests received"],["req_proc","Requests processed"],["bl_req","Backlogged requests"],["t14_c","Median days, complex"]];
  $("kpis").innerHTML = items.map(([k,l])=>{ const s=series(k), v=s[s.length-1], p=s[0];
    let d; if(isNaN(v)) d="not reported in FY"+S.y1;
    else if(S.y0===S.y1||isNaN(p)||p===0) d="in FY"+S.y1;
    else {const ch=(v/p-1)*100; d=`<span class="${ch>0?"up":"down"}">${ch>0?"▲":"▼"} ${Math.abs(ch).toFixed(0)}%</span> since FY${S.y0}`;}
    return `<div class="kpi"><div class="l">${l} · FY${S.y1}</div><div class="v">${fmt(v)}${k==="t14_c"&&!isNaN(v)?" days":""}</div><div class="d">${d}</div></div>`;}).join("");
}
function sec(){return SECTIONS.find(s=>s.id===S.sec);}
function curType(){const s=sec(); return s.types.find(t=>t.n===S.type[s.id])||s.types[0];}
function renderChips(){
  const s=sec(); $("secName").textContent=s.name; $("secDesc").textContent=s.desc+" · pick a data type:";
  $("chips").innerHTML=s.types.map(t=>`<button class="chip ${t.n===curType().n?"on":""}" data-n="${t.n}"><b>${t.n}</b>${t.t}</button>`).join("");
  $("chips").querySelectorAll(".chip").forEach(b=>b.onclick=()=>{S.type[s.id]=b.dataset.n; S.mIdx=0; render();});
}
function resetBox(){ if(chart){chart.destroy(); chart=null;} $("chartbox").innerHTML='<canvas id="mainChart"></canvas>'; return $("mainChart"); }
const tick = {color:C.muted,font:{size:12}};
function baseOpts(t, legend){ return {responsive:true,maintainAspectRatio:false,animation:false,
  plugins:{legend:{display:legend,position:"top",align:"start",labels:{boxWidth:12,boxHeight:12,color:C.b950,font:{size:13}}},
   tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${t.k==="stack"?c.raw.toFixed(0)+"%":fmt(c.raw,t.money)}${t.days?" days":""}`}}},
  scales:{x:{grid:{display:false},ticks:tick},y:{grid:{color:C.b100},beginAtZero:true,ticks:{...tick,callback:v=>t.k==="stack"?v+"%":fmt(v,t.money)}}}}; }

function renderMain(){
  const t=curType(); $("mcTitle").innerHTML=`<span class="badge">${t.n}</span>${t.t}`; $("mcSub").textContent=t.s;
  const ms=$("measure"); const cv=resetBox(); let take="";
  const labels=PY().map(String);
  // ---- Top 10 compare mode: one measure, one bar per agency ----
  if(S.ag===-2 && t.k!=="statutes"){
    ms.hidden=false; ms.innerHTML=t.m.map((m,i)=>`<option value="${i}">${m[1]}</option>`).join(""); if(S.mIdx>=t.m.length) S.mIdx=0; ms.value=S.mIdx;
    const [k,l,col]=t.m[S.mIdx]; const sum=META.kind[k]==="sum";
    const arr=TOPI.map(a=>({a,l:agShort(a),v:periodTotal(k,a,-1)})).filter(x=>!isNaN(x.v)).sort((x,y)=>y.v-x.v);
    if(!arr.length){$("chartbox").innerHTML='<div class="empty">Not reported for these agencies in this period</div>'; $("takeaway").textContent=""; return;}
    $("mcSub").textContent = `${l} · ${sum?"total":"median of yearly values"} for FY${S.y0}${S.y0===S.y1?"":"–FY"+S.y1} · click a bar to open the agency`;
    chart=hbar(cv, arr.map(x=>x.l), arr.map(x=>x.v), col===C.b200||col===C.b300?C.b600:col, i=>{S.ag=arr[i].a; S.cp=-1; buildComps(); render();}, t);
    take=`<b>${arr[0].l}</b> is highest (${fmt(arr[0].v,t.money)}${t.days?" days":""}); <b>${arr[arr.length-1].l}</b> is lowest (${fmt(arr[arr.length-1].v,t.money)}${t.days?" days":""}).`;
    $("takeaway").innerHTML=take; return;
  }
  ms.hidden=true;
  if(t.k==="statutes") return statutes();
  const data=t.m.map(([k,l,c])=>({k,l,c,s:series(k)}));
  if(!data.some(d=>d.s.some(x=>!isNaN(x)))){$("chartbox").innerHTML='<div class="empty">Not reported for this selection and period</div>'; $("takeaway").textContent=""; return;}
  if(t.k==="line"){
    const one=labels.length===1;
    chart=new Chart(cv,{type:one?"bar":"line",data:{labels,datasets:data.map((d,j)=>({label:d.l,data:d.s.map(x=>isNaN(x)?null:x),borderColor:d.c,backgroundColor:d.c,
      borderWidth:2.5,borderDash:(t.dash&&j===0)?[6,5]:[],pointRadius:3,pointHoverRadius:6,tension:0,maxBarThickness:60,borderRadius:one?4:0}))},options:baseOpts(t,data.length>1)});
    const d0=data[0], a=d0.s.find(x=>!isNaN(x)), b=[...d0.s].reverse().find(x=>!isNaN(x));
    take = labels.length>1&&!isNaN(a)&&!isNaN(b)&&a!==0 ? `<b>${d0.l}</b>: ${fmt(a,t.money)} → ${fmt(b,t.money)}${t.days?" days":""} (${b>=a?"+":""}${((b/a-1)*100).toFixed(0)}%) over the period.` : `<b>${d0.l}</b>: ${fmt(b,t.money)}${t.days?" days":""} in FY${S.y1}.`;
  } else if(t.k==="stack"){
    const tot=labels.map((_,i)=>data.reduce((s,d)=>s+(isNaN(d.s[i])?0:d.s[i]),0));
    chart=new Chart(cv,{type:"bar",data:{labels,datasets:data.map(d=>({label:d.l,data:d.s.map((x,i)=>tot[i]?100*(isNaN(x)?0:x)/tot[i]:null),backgroundColor:d.c,borderColor:"#fff",borderWidth:1,maxBarThickness:60}))},
      options:(o=>{o.scales.x.stacked=true;o.scales.y.stacked=true;o.scales.y.max=100;return o;})(baseOpts(t,true))});
    const last=tot.length-1; const sh=data.map(d=>({l:d.l,v:tot[last]?100*(isNaN(d.s[last])?0:d.s[last])/tot[last]:0})).sort((a,b)=>b.v-a.v);
    take = `In FY${S.y1}, most common outcome: <b>${sh[0].l}</b> (${sh[0].v.toFixed(0)}%), then ${sh[1].l} (${sh[1].v.toFixed(0)}%).`;
  } else if(t.k==="bar"){
    const vals=data.map(d=>{const s=d.s.filter(x=>!isNaN(x)); return s.length?s.reduce((a,b)=>a+b,0):NaN;});
    if(vals.every(x=>isNaN(x))){$("chartbox").innerHTML='<div class="empty">Not reported in this period</div>'; $("takeaway").textContent=""; return;}
    chart=new Chart(cv,{type:"bar",data:{labels:data.map(d=>d.l),datasets:[{label:S.y0===S.y1?"FY"+S.y0:`FY${S.y0}–${S.y1}`,data:vals.map(x=>isNaN(x)?null:x),backgroundColor:data[0].c,borderRadius:4,maxBarThickness:46}]},
      options:(o=>{o.plugins.legend.display=false; o.scales.x.ticks={...tick,autoSkip:false,maxRotation:45,minRotation:data.length>8?40:0}; return o;})(baseOpts(t,false))});
    const tot=vals.reduce((a,b)=>a+(isNaN(b)?0:b),0), mx=vals.indexOf(Math.max(...vals.filter(x=>!isNaN(x))));
    take = tot? `Largest: <b>${data[mx].l}</b>, ${(100*vals[mx]/tot).toFixed(0)}% of the total (${fmt(tot)}).` : "";
  }
  $("takeaway").innerHTML=take;
}
function hbar(cv, labels, vals, color, onClick, t={}){
  return new Chart(cv,{type:"bar",data:{labels,datasets:[{data:vals,backgroundColor:color,borderRadius:4,maxBarThickness:22}]},
    options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,animation:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>fmt(c.raw,t.money)+(t.days?" days":"")}}},
    scales:{x:{grid:{color:C.b100},beginAtZero:true,ticks:{...tick,callback:v=>fmt(v,t.money)}},y:{grid:{display:false},ticks:{color:C.b950,autoSkip:false,font:{size:13}}}},
    onClick:(e,els)=>{if(els.length&&onClick) onClick(els[0].index);}, onHover:(e,els)=>{e.native.target.style.cursor=els.length?"pointer":"default";}}});
}
function statutes(){
  const box=$("chartbox");
  if(S.ag<0){ box.innerHTML='<div class="empty">Pick one agency to see its Exemption 3 statutes</div>'; $("takeaway").textContent=""; return;}
  if(S.cp>=0){ box.innerHTML='<div class="empty">Statutes are shown at agency level. Pick "All components".</div>'; $("takeaway").textContent=""; return;}
  const ag=S.ag, y=S.y1;
  if(!STATUTES[ag]){ box.innerHTML='<div class="empty">Loading…</div>'; $("takeaway").textContent="";
    loadStatutes(ag).then(()=>{ if(S.ag===ag&&S.y1===y&&curType().k==="statutes") statutes(); })
      .catch(e=>{ box.innerHTML=`<div class="empty">Could not load statutes: ${e.message}</div>`; }); return; }
  const rows=STATUTES[ag][y];
  if(!rows||!rows.length){box.innerHTML=`<div class="empty">No Exemption 3 statutes listed in FY${S.y1}</div>`; $("takeaway").textContent=""; return;}
  box.innerHTML=`<ul class="stat-list">${rows.map(([s,n])=>`<li><span>${s.replace(/</g,"&lt;")}</span><span>${n==null?"–":n.toLocaleString()} times</span></li>`).join("")}</ul>`;
  $("takeaway").textContent=`Top statutes in FY${S.y1}. The full list (one row per statute) is in exemption_statutes_06.csv.`;
}
function renderComps(){
  const box=$("compsBox"); if(compsChart){compsChart.destroy(); compsChart=null;}
  const list=S.ag<0?null:META.components[S.ag];
  if(!list||S.cp>=0){box.hidden=true; return;}
  const m={}; PY().forEach(fy=>ROWS.filter(r=>r.fy===fy&&r.a===S.ag&&r.c>=0).forEach(r=>{const v=r.v[KI.req_recv]; if(!isNaN(v)) m[r.c]=(m[r.c]||0)+v;}));
  const arr=Object.entries(m).map(([c,v])=>({c:+c,v,l:list[+c][0]})).sort((a,b)=>b.v-a.v).slice(0,12);
  box.hidden=false; $("compsTitle").textContent=`Requests received by component, FY${S.y0}${S.y0===S.y1?"":"–FY"+S.y1}`;
  $("compsSub").textContent= arr.length?"Click a bar (or use the Component dropdown) to see one component":"No component data in this period";
  if(arr.length) compsChart=hbar($("compsChart"), arr.map(x=>x.l), arr.map(x=>x.v), C.b600, i=>{S.cp=arr[i].c; render();});
}

load().then(()=>{ $("loading").hidden=true; $("app").hidden=false; buildControls(); render(); })
  .catch(e=>{ $("loading").textContent="Could not load the data: "+e.message; console.error(e); });
