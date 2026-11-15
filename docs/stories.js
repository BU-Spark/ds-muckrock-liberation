// renamed agencies: current name first, former name in brackets (as in the dashboard's own code)
function fdAgency(a) { return a === "Department of Defense" || a === "Department of War" ? "Department of War (Department of Defense)" : a }
/* ---------- User guide. It sits in the header card, outside the part the dashboard redraws, and shows when the card is
   expanded; the overview's header has the line that opens it. ---------- */
(function () {
  const GUIDE = `<div class="fd-guide" role="region" aria-label="How to use this dashboard">
    <h2>How to use this dashboard</h2>
    <div class="fd-cols">
      <section><h3>What this is</h3>
        <p>Every federal agency files an annual FOIA report. This dashboard puts the reports for FY2008–FY2025 side by side, for agencies
        and for their components: offices inside an agency, such as ICE inside DHS.</p>
        <p>Data: foia.gov annual reports, built 2026-11-02.</p>
        <h3>Three ways in</h3>
        <ol><li><b>Overview</b>, the start page: ten headline numbers, for all agencies or for the agency or component you pick. Click a card to open it: what its number means, what stands out in the years chosen, and a larger chart. The agency, component and years can still be changed while a card is open.</li>
          <li><b>Questions 1–6</b>, on the left: Requests received &amp; processed · Response time · Backlog, staff &amp; cost · Outcomes &amp; exemptions · Appeals · Backlog vs intake. Each opens a chart.</li>
          <li><b>Explore all data</b>: any measure in the reports. Choose a Data type, then a Measure.</li></ol>
        <p class="fd-small">“Home” in the top bar goes back to the overview; so does clicking a selected question again.</p></section>
      <section><h3>Choosing what you see</h3>
        <dl><dt>Agency</dt><dd>“All agencies (government total)”, or one agency.</dd>
          <dt>Component</dt><dd>An office inside the agency you picked.</dd>
          <dt>Fiscal years (top right)</dt><dd>Pick All years, Last 10, Last 5 or the latest year; or click a first year, then a last year. Click one year twice to see only that year. One-year views (distribution, exemptions, tables) use the last year chosen.</dd>
          <dt>Compare with (up to 5)</dt><dd>Adds agencies or components to the same chart; × removes one.</dd>
          <dt>Agencies added up in the total</dt><dd>All reporting agencies (71–122 a year), or only the 70 that reported all 18 years, so a total does not grow just because more agencies report.</dd></dl>
        <p>Each question has two tabs:
          <b>Chart</b> and <b>Tables</b> (the numbers in the chart, related report tables, all agencies in one year). Next to the tables,
          <b>How the comparison is made</b> explains that question's numbers.</p></section>
      <section><h3>Words to know</h3>
        <dl><dt>Processed</dt><dd>Requests an agency closed during the fiscal year.</dd>
          <dt>Released in full, partly released, fully denied on exemptions</dt><dd>How a closed request ended after its records were reviewed. Many end in other ways: no records found, withdrawn, referred and more.</dd>
          <dt>Exemptions</dt><dd>The nine reasons in the law (5 U.S.C. § 552(b)) that let an agency withhold records.</dd>
          <dt>Backlog</dt><dd>Requests still pending at the end of the year beyond the legal time limit: 20 working days from a complete request, plus 10 in unusual circumstances.</dd>
          <dt>Response time</dt><dd>Working days (as the reports count them) from receiving a complete request to closing it.</dd>
          <dt>Appeal</dt><dd>The requester asks the agency to review its decision.</dd></dl></section>
    </div>
    <section class="fd-rules"><h3>Rules used everywhere</h3><div class="fd-rules-body"></div></section>
    <p class="fd-keep"><b>Keep in mind.</b> Agencies fill in these reports themselves, and categories can change from year to year. foia.gov has no FY2008
      figures for 26 agencies; they appear in FY2009–10. The reports show what changed, not why. Student prototype for MuckRock
      (BU Spark! DS 701); not an official MuckRock product.</p>
  </div>`;
  function openGuide(card) { const b = card && card.querySelector(".bslib-full-screen-enter"); if (b) b.click() }
  function fix(qh) {
    qh.dataset.guide = "1";
    const card = qh.closest(".card"); if (!card) return;
    card.classList.add("fd-card");
    if (!card.querySelector(".fd-guide")) (qh.closest(".card-body") || card).insertAdjacentHTML("beforeend", GUIDE);
    const qn = qh.querySelector(".qnum"), name = qn ? qn.textContent.trim() : "";
    if (/^Question [1-6]$/.test(name)) {   // drop "who · years" under the title (the sidebar and the year buttons show both); keep coverage and one-year warnings
      const sel = qh.querySelector(".sel");
      if (sel) { [...sel.childNodes].forEach(n => { if (!(n.nodeType === 1 && n.classList.contains("warn"))) n.remove() });
        const w = sel.querySelector(".warn"); if (w) w.textContent = w.textContent.replace(/^[\s\u00a0]*·\s*/, "");
        if (!sel.textContent.trim()) sel.remove() }
    }
    if (name === "Overview") {   // the start page: the way into the guide
      qh.insertAdjacentHTML("beforeend", `<div class="fd-open"><button type="button" class="fd-link">How to use this dashboard ↗</button></div>`);
      qh.querySelector(".fd-link").addEventListener("click", () => openGuide(card));
    }
  }
  function rules() {
    const src = document.querySelector(".how-rules ul"), dst = document.querySelector(".fd-rules-body");
    if (src && dst && dst.textContent !== src.textContent) dst.replaceChildren(src.cloneNode(true));
  }
  const scan = () => { document.querySelectorAll(".qhead:not([data-guide])").forEach(fix); rules() };
  new MutationObserver(scan).observe(document.documentElement, {childList: true, subtree: true});
  document.addEventListener("DOMContentLoaded", scan);
})();

/* ---------- Fiscal-year buttons in place of the two year dropdowns, and agency and component lists that start with the
   largest ones. The buttons set the hidden dropdowns and the lists are only regrouped, so the dashboard's own inputs stay
   in charge. ---------- */
(function () {
  const DATA = (window.__foiaJson = window.__foiaJson || fetch("data/foia.json").then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(D => { D.ids.Agency = D.ids.Agency.map(fdAgency); return D }));
  const ev = el => el.dispatchEvent(new Event("change", {bubbles: true}));

  // ---- fiscal years: presets and one button per year. Click a year, then another; the same year twice = one year
  const yearBox = () => document.querySelector(".years");
  const yearSel = () => { const w = yearBox(); return w ? [...w.querySelectorAll("select")] : [] };
  function buildYears(card) {
    const [a] = yearSel(); if (!a || card.querySelector(".fd-tl")) return;
    const ys = [...a.options].map(o => +o.value), first = ys[0], last = ys[ys.length - 1];   // the years in the data
    const presets = [["All years", first, last], ["Last 10", Math.max(first, last - 9), last], ["Last 5", Math.max(first, last - 4), last], [`FY${last}`, last, last]];
    const box = document.createElement("div"); box.className = "tl fd-tl";
    box.innerHTML = `<div class="tl-top">${presets.map(([l, x, y]) => `<button type="button" class="tl-p" data-a="${x}" data-b="${y}">${l}</button>`).join("")}<span class="tl-label" aria-live="polite"></span></div>
      <div class="tl-years">${ys.map(y => `<button type="button" class="tl-y" data-y="${y}" title="FY${y}">${String(y).slice(2)}</button>`).join("")}</div>`;
    let anchor = null;   // first click of a range
    const cur = () => { const [x, y] = yearSel().map(s => +s.value); return [Math.min(x, y), Math.max(x, y)] };
    const draw = () => { const [lo, hi] = cur();
      box.querySelectorAll(".tl-y").forEach(c => { const y = +c.dataset.y;
        c.classList.toggle("on", anchor === null && y >= lo && y <= hi); c.classList.toggle("anchor", y === anchor);
        c.classList.toggle("end", anchor === null && (y === lo || y === hi)); c.setAttribute("aria-pressed", y >= lo && y <= hi) });
      box.querySelectorAll(".tl-p").forEach(p => p.classList.toggle("on", anchor === null && +p.dataset.a === lo && +p.dataset.b === hi));
      box.querySelector(".tl-label").textContent = anchor !== null ? `From FY${anchor}: now click the last year` : lo === hi ? `FY${lo}` : `FY${lo}–FY${hi}` };
    const set = (x, y) => { const [sa, sb] = yearSel(); sa.value = String(Math.min(x, y)); sb.value = String(Math.max(x, y)); ev(sb); draw() };   // the dashboard reads both
    box.querySelectorAll(".tl-p").forEach(p => p.onclick = () => { anchor = null; set(+p.dataset.a, +p.dataset.b) });
    box.querySelectorAll(".tl-y").forEach(c => c.onclick = () => { const y = +c.dataset.y;
      if (anchor === null) { anchor = y; draw(); return } const x = anchor; anchor = null; set(x, y) });
    yearSel().forEach(s => s.addEventListener("change", draw));
    card.classList.add("fd-has-tl"); (card.querySelector(".card-body") || card).appendChild(box);
    yearBox().classList.add("fd-hidden");   // the two dropdowns stay in the page, hidden
    draw();
  }

  // ---- lists: the 10 agencies with the most requests in the latest year, and an agency's 5 largest components in the last
  // year chosen (only when it has more than 6), A-Z inside each group. A shorter list, not a ranking.
  function regroup(sel, groups) {
    const keep = sel.value, frag = document.createDocumentFragment();
    for (const [label, opts] of groups) { if (!opts.length) continue;
      if (label == null) { opts.forEach(o => frag.appendChild(o)); continue }
      const g = document.createElement("optgroup"); g.label = label; opts.forEach(o => g.appendChild(o)); frag.appendChild(g) }
    sel.replaceChildren(frag); sel.value = keep; sel.dataset.grouped = "1";
  }
  const formSel = lab => { const l = [...document.querySelectorAll("label")].find(x => x.textContent.trim() === lab); const f = l && l.closest("form"); return f && f.querySelector("select") };
  let TOP = null;
  DATA.then(D => {
    const ids = D.ids, R = D.values["01_Requests__ProcessingStatisticsReceivedQuantity"]; if (!R) return;
    const last = Math.max(...ids.FY), rows = [];
    ids.FY.forEach((y, i) => { if (y === last && ids.level[i] === "agency") rows.push([R[i] || 0, ids.Agency[i]]) });
    rows.sort((a, b) => b[0] - a[0]);
    TOP = {label: `Largest 10 (most requests in FY${last})`, names: new Set(rows.slice(0, 10).map(r => r[1]))};
    scan();
  }).catch(err => console.error("largest agencies:", err));
  function groupAgencies(sel, emptyFirst) {
    if (!TOP || sel.dataset.grouped) return;
    const opts = [...sel.options], head = opts.filter((o, i) => emptyFirst ? o.value === "" : i === 0), rest = opts.filter(o => !head.includes(o));
    regroup(sel, [[null, head], [TOP.label, rest.filter(o => TOP.names.has(o.textContent.trim()))], ["All other agencies", rest.filter(o => !TOP.names.has(o.textContent.trim()))]]);
  }
  function groupComponents(sel) {
    if (sel.disabled || sel.dataset.grouped) return;
    const agSel = formSel("Agency"), agency = agSel && agSel.selectedOptions[0] && agSel.selectedOptions[0].textContent.trim();
    const hi = Math.max(...yearSel().map(s => +s.value)), opts = [...sel.options], head = [opts[0]], rest = opts.slice(1);
    if (!agency || rest.length <= 6) { sel.dataset.grouped = "1"; return }
    DATA.then(D => {
      if (!sel.isConnected || sel.dataset.grouped) return;
      const ids = D.ids, R = D.values["01_Requests__ProcessingStatisticsReceivedQuantity"], recv = new Map();
      ids.FY.forEach((y, i) => { if (y === hi && ids.level[i] === "component" && ids.Agency[i] === agency) recv.set(`${ids.Name[i]} (${ids.Component[i]})`, R[i] || 0) });
      const big = rest.slice().sort((a, b) => (recv.get(b.textContent.trim()) || 0) - (recv.get(a.textContent.trim()) || 0)).slice(0, 5).filter(o => (recv.get(o.textContent.trim()) || 0) > 0);
      if (!big.length) { sel.dataset.grouped = "1"; return }
      regroup(sel, [[null, head], [`Largest 5 (FY${hi})`, rest.filter(o => big.includes(o))], ["All other components", rest.filter(o => !big.includes(o))]]);
    });
  }
  // the same grouping for the component list under "Compare with". That list is rebuilt by the dashboard each time its agency
  // changes (values are entity keys "C|agency|key"); the year can change later, so it is regrouped when the last year changes.
  function groupCmpComponents(sel) {
    const ag = document.querySelector("select.cmp-agency"), agency = ag && ag.value;
    if (!agency || sel.disabled) return;
    const hi = Math.max(...yearSel().map(s => +s.value)), sig = `${agency}|${hi}`, grouped = !!sel.querySelector("optgroup");
    if (grouped && sel.dataset.fdSig === sig) return;                        // grouped for this agency and year
    if (!grouped && (sel.dataset.fdFlat === sig || sel.dataset.fdWait === sig)) return;   // nothing to group, or on its way
    const opts = [...sel.options], head = [opts[0]], rest = opts.slice(1).sort((x, y) => x.textContent.localeCompare(y.textContent));
    const flat = () => { sel.dataset.fdFlat = sig; if (grouped) regroup(sel, [[null, head], [null, rest]]) };
    if (rest.length <= 6) return flat();
    sel.dataset.fdWait = sig;
    DATA.then(D => {
      delete sel.dataset.fdWait;
      if (!sel.isConnected || ag.value !== agency || !opts.every(o => sel.contains(o))) return;   // list rebuilt meanwhile: the next scan does it
      const ids = D.ids, R = D.values["01_Requests__ProcessingStatisticsReceivedQuantity"], recv = new Map();
      ids.FY.forEach((y, i) => { if (y === hi && ids.level[i] === "component" && ids.Agency[i] === agency) recv.set(`C|${agency}|${ids.Key[i]}`, R[i] || 0) });
      const big = rest.slice().sort((x, y) => (recv.get(y.value) || 0) - (recv.get(x.value) || 0)).slice(0, 5).filter(o => (recv.get(o.value) || 0) > 0);
      if (!big.length) return flat();
      delete sel.dataset.fdFlat; sel.dataset.fdSig = sig;
      regroup(sel, [[null, head], [`Largest 5 (FY${hi})`, rest.filter(o => big.includes(o))], ["All other components", rest.filter(o => !big.includes(o))]]);
    });
  }
  function fixNote() {   // the sidebar note names the hidden "To FY" dropdown: say "the last year chosen"
    document.querySelectorAll(".sidebar p, .sidebar .side-note, p").forEach(el => {
      if (el.dataset.fdNote || !el.textContent.includes('"To FY" year')) return;
      const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let n;
      while ((n = w.nextNode())) if (n.nodeValue.includes('"To FY" year')) n.nodeValue = n.nodeValue.replace('the "To FY" year', "the last year chosen");
      el.dataset.fdNote = "1" });
  }
  function scan() {
    fixNote();
    const qh = document.querySelector(".qhead"), card = qh && qh.closest(".card");
    if (card) buildYears(card);
    const a = formSel("Agency"); if (a) groupAgencies(a, false);
    const c = document.querySelector("select.cmp-agency"); if (c) groupAgencies(c, true);
    const k = formSel("Component"); if (k) groupComponents(k);
    const cc = document.querySelector("select.cmp-comp"); if (cc) groupCmpComponents(cc);
  }
  new MutationObserver(scan).observe(document.documentElement, {childList: true, subtree: true});
  document.addEventListener("DOMContentLoaded", scan);
})();

/* ---------- "Clear all": resets Agency, Component and Compare with to how the page opens, in one step. Years, the question
   and "Agencies added up in the total" are not touched. ---------- */
(function () {
  const formSel = lab => { const l = [...document.querySelectorAll("label")].find(x => x.textContent.trim() === lab); const f = l && l.closest("form"); return f && f.querySelector("select") };
  const fire = (el, ...types) => types.forEach(t => el.dispatchEvent(new Event(t, {bubbles: true})));
  const cmpBox = () => document.querySelector("div.cmp");
  const dirty = () => { const ag = formSel("Agency"), c = cmpBox();
    return !!(ag && ag.options.length && ag.value !== ag.options[0].value) || !!(c && Array.isArray(c.value) && c.value.length) };
  function reset() {
    const c = cmpBox();
    if (c) {   // Compare with: back to an empty list and the two lists' first state
      const as = c.querySelector("select.cmp-agency"), cs = c.querySelector("select.cmp-comp");
      if (as) as.value = "";
      if (cs) { cs.replaceChildren(new Option("Whole agency (all components)", "")); cs.disabled = true }
      const chips = c.querySelector(".chips"); if (chips) chips.replaceChildren();
      const hint = c.querySelector(".side-note"); if (hint) hint.textContent = "Choosing adds it to the comparison; × removes it.";
      if (Array.isArray(c.value) && c.value.length) { c.value = []; fire(c, "input") }
    }
    const ag = formSel("Agency");   // Agency: the government total; the dashboard then resets Component itself
    if (ag && ag.value !== ag.options[0].value) { ag.value = ag.options[0].value; fire(ag, "input", "change") }
    setTimeout(update, 50);
  }
  let btn = null;
  const update = () => { if (btn) btn.disabled = !dirty() };
  function place() {
    const ag = formSel("Agency"), form = ag && ag.closest("form");
    if (!form || form.querySelector(".fd-clear")) return;
    form.classList.add("fd-agform");
    btn = document.createElement("button"); btn.type = "button"; btn.className = "fd-clear"; btn.textContent = "Clear all";
    btn.title = "Reset agency, component and compare choices"; btn.addEventListener("click", reset);
    form.appendChild(btn); update();
  }
  new MutationObserver(() => { place(); update() }).observe(document.documentElement, {childList: true, subtree: true});
  document.addEventListener("input", () => setTimeout(update, 0), true);
  document.addEventListener("change", () => setTimeout(update, 0), true);
  document.addEventListener("click", () => setTimeout(update, 0), true);   // the × on a compare chip
})();

/* ---------- The view in the page address, and "Copy link to this view". The address records the question, agency, component,
   years, compare list, the two radio choices and the Explore measure; opening such a link sets the same controls again, in
   order, the way a user would. ---------- */
(function () {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const waitFor = async (f, ms = 8000) => { for (let t = 0; t < ms; t += 100) { const v = f(); if (v) return v; await sleep(100) } return null };
  const formOf = lab => { const l = [...document.querySelectorAll("label")].find(x => x.textContent.trim() === lab); return l && l.closest("form") };
  const selOf = lab => { const f = formOf(lab); return f && f.querySelector("select") };
  const fire = (el, ...ts) => ts.forEach(t => el.dispatchEvent(new Event(t, {bubbles: true})));
  const checkedText = lab => { const f = formOf(lab), i = f && f.querySelector("input:checked"); return i ? i.closest("label").textContent.trim() : null };
  let restoring = false, timer = null;
  function read() {
    const p = new URLSearchParams(), qp = document.querySelector(".qpick"), q = qp ? +qp.value : 0;
    if (q) p.set("q", q);
    const ag = selOf("Agency"), total = !ag || ag.value === ag.options[0].value;
    if (!total) p.set("agency", ag.selectedOptions[0].textContent.trim());
    const cs = selOf("Component");
    if (!total && cs && !cs.disabled && cs.value !== cs.options[0].value) p.set("comp", cs.selectedOptions[0].textContent.trim());
    const ys = [...document.querySelectorAll(".years select")];
    if (ys.length === 2) { const v = ys.map(s => +s.value), all = [...ys[0].options].map(o => +o.value), lo = Math.min(...v), hi = Math.max(...v);
      if (lo !== all[0] || hi !== all[all.length - 1]) { p.set("from", lo); p.set("to", hi) } }
    const cmp = document.querySelector("div.cmp"); if (cmp && Array.isArray(cmp.value) && cmp.value.length) p.set("with", cmp.value.join("~"));
    if ((checkedText("Agencies added up in the total") || "").startsWith("Only")) p.set("scope", "same");
    // the reversal-rate base also sets the overview's appeals tile and "Compare with"; pages other than Question 5 hide its control,
    // so there the choice is read from where the dashboard keeps it
    if ((q === 5 ? checkedText("Reversal rate out of") : (window.__memo || {}).base5) === "All processed appeals") p.set("base", "all");
    const od = document.querySelector(".odetail:not([hidden])"); if (!q && od) p.set("card", od.dataset.i);   // the card opened on the overview
    if (q === 7) { const ty = selOf("Data type"), me = selOf("Measure");
      if (ty) p.set("type", ty.selectedOptions[0].textContent.trim().slice(0, 2)); if (me) p.set("m", me.selectedOptions[0].textContent.trim()) }
    return p;
  }
  function sync() { if (restoring) return; const s = read().toString(); history.replaceState(null, "", s ? `?${s}` : location.pathname) }
  const later = () => { clearTimeout(timer); timer = setTimeout(sync, 400) };
  ["input", "change", "click"].forEach(t => document.addEventListener(t, later, true));
  async function restore(p) {
    restoring = true;
    try {
      await waitFor(() => document.querySelector(".qpick") && selOf("Agency") && document.querySelectorAll(".years select").length === 2);
      const ys = [...document.querySelectorAll(".years select")], f = +p.get("from"), t = +p.get("to");
      if (f && t && [...ys[0].options].some(o => +o.value === f) && [...ys[1].options].some(o => +o.value === t)) { ys[0].value = String(f); ys[1].value = String(t); fire(ys[1], "change"); await sleep(400) }
      const agName = fdAgency(p.get("agency")), ag = selOf("Agency");   // links made before a rename still open
      if (agName) { const o = [...ag.options].find(o => o.textContent.trim() === agName);
        if (o) { ag.value = o.value; fire(ag, "input", "change");
          const comp = p.get("comp");
          if (comp) { const cs = await waitFor(() => { const s = selOf("Component"); return s && !s.disabled && [...s.options].some(o => o.textContent.trim() === comp) && s });
            if (cs) { cs.value = [...cs.options].find(o => o.textContent.trim() === comp).value; fire(cs, "input", "change") } }
          await sleep(500) } }
      const keys = (p.get("with") || "").split("~").filter(Boolean).slice(0, 5).map(k => { const x = k.split("|"); x[1] = fdAgency(x[1]); return x.join("|") });
      // in the link's order; a component's agency is added and then replaced by the component, so a whole agency listed before
      // one of its own components drops out there, and is added again at the end (the only case where the order can change)
      const cmpNow = () => { const c = document.querySelector("div.cmp"); return c && Array.isArray(c.value) ? c.value : [] };
      for (const k of [...keys, ...keys.filter(k => k.startsWith("A|"))]) {
        if (cmpNow().includes(k)) continue;
        const [lv, a] = k.split("|"), as = await waitFor(() => document.querySelector("select.cmp-agency"));
        if (!as || ![...as.options].some(o => o.value === a)) continue;
        as.value = a; fire(as, "change"); await sleep(250);
        if (lv === "C") { const cs = await waitFor(() => { const s = document.querySelector("select.cmp-comp"); return s && [...s.options].some(o => o.value === k) && s });
          if (cs) { cs.value = k; fire(cs, "change"); await sleep(250) } }
      }
      if (p.get("scope") === "same") { const f2 = formOf("Agencies added up in the total"), i = f2 && [...f2.querySelectorAll("input")].find(x => x.closest("label").textContent.trim().startsWith("Only")); if (i) { i.click(); await sleep(300) } }
      const q = +p.get("q");
      if (q) { const b = document.querySelector(`.qbtn[data-id="${q}"]`); if (b && +document.querySelector(".qpick").value !== q) b.click();
        if (q === 5 && p.get("base") === "all") { const f3 = await waitFor(() => formOf("Reversal rate out of")); const i = f3 && [...f3.querySelectorAll("input")].find(x => x.closest("label").textContent.trim() === "All processed appeals"); if (i) i.click() }
        if (q === 7) { const ty = p.get("type"), m = p.get("m");
          if (ty) { const s = await waitFor(() => selOf("Data type")); const o = s && [...s.options].find(o => o.textContent.trim().startsWith(ty)); if (o && s.value !== o.value) { s.value = o.value; fire(s, "input", "change"); await sleep(500) } }
          if (m) { const s = await waitFor(() => { const x = selOf("Measure"); return x && [...x.options].some(o => o.textContent.trim() === m) && x }); if (s) { s.value = [...s.options].find(o => o.textContent.trim() === m).value; fire(s, "input", "change") } } } }
      await sleep(600);
    } finally { restoring = false; sync() }
  }
  function button() {   // under the year buttons
    const tl = document.querySelector(".fd-tl"); if (!tl || tl.querySelector(".fd-copy")) return;
    const b = document.createElement("button"); b.type = "button"; b.className = "fd-copy"; b.textContent = "Copy link to this view";
    b.addEventListener("click", async () => { sync();
      try { await navigator.clipboard.writeText(location.href); b.textContent = "Link copied" } catch (e) { b.textContent = "Copy it from the address bar" }
      setTimeout(() => { b.textContent = "Copy link to this view" }, 1800) });
    const row = document.createElement("div"); row.className = "fd-linkrow"; row.appendChild(b); tl.appendChild(row);
  }
  new MutationObserver(button).observe(document.documentElement, {childList: true, subtree: true});
  const start = new URLSearchParams(location.search);
  // set before the dashboard builds its inputs (this file runs first), so the base holds on every page, not only on Question 5
  if (start.get("base") === "all") window.__memo = Object.assign(window.__memo || {}, {base5: "All processed appeals"});
  if (!start.get("q") && +start.get("card") > 0) window.__openCard = +start.get("card") - 1;   // the overview opens this card when it is first drawn
  if ([...start.keys()].length) restore(start);
})();

/* ---------- "Home" in the top bar (and the dashboard's name): back to the overview's cards. The agency, component,
   comparison and years chosen stay as they are; "Clear all" resets those. ---------- */
(function () {
  const openPanel = () => document.querySelector(".odetail:not([hidden])");
  const goHome = e => { if (e) e.preventDefault(); window.__openCard = null;
    const c = openPanel(); if (c) c.querySelector(".od-close").click();
    const on = document.querySelector(".qbtn.on"); if (on) on.click(); window.scrollTo(0, 0) };
  let btn = null;
  const update = () => { if (btn) btn.classList.toggle("fd-at-home", !document.querySelector(".qbtn.on") && !openPanel()) };
  function place() {
    const nav = document.querySelector("nav.navbar"); if (!nav || nav.querySelector(".fd-home")) return;
    btn = document.createElement("button"); btn.type = "button"; btn.className = "fd-home"; btn.title = "Back to the overview";
    btn.innerHTML = '<i class="bi bi-house-door" aria-hidden="true"></i> Home';
    btn.addEventListener("click", goHome); nav.appendChild(btn);
    const name = nav.querySelector(".navbar-title-text > a"); if (name) name.addEventListener("click", goHome);
    update();
  }
  document.addEventListener("DOMContentLoaded", place); place();
  document.addEventListener("click", () => setTimeout(update, 0), true);
  // an opened card on the overview: Escape closes it, the arrow keys step through the cards
  document.addEventListener("keydown", e => {
    const d = openPanel(); if (!d || /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName) || document.querySelector('.card[data-full-screen="true"]')) return;
    const b = d.querySelector(e.key === "Escape" ? ".od-close" : e.key === "ArrowRight" ? ".od-next" : e.key === "ArrowLeft" ? ".od-prev" : "none");
    if (b && !b.disabled) b.click();
  });
})();
