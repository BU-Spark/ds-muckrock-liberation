// renamed agencies: the current name first, the former one in brackets (same rule as the dashboard's own code)
function fdAgency(a) { return a === "Department of Defense" || a === "Department of War" ? "Department of War (Department of Defense)" : a }
/* Start page: four findings that were checked.
   Text and numbers come from data/walk_<id>.json (built by storylines/build/build_walks.py). */
// a grey, blurred card that holds a storyline's place; no old text or numbers are kept in it
function storyPlaceholder(kicker) {
  const el = document.createElement("article"); el.className = "story placeholder";
  el.setAttribute("aria-label", `${kicker}: storyline in progress`);
  el.innerHTML = `<div class="kicker">${kicker}</div>
    <div class="veil-wrap">
      <div class="veil" aria-hidden="true">
        <div class="sk tall w80"></div><div class="sk tall w55"></div>
        <div class="sk w95"></div><div class="sk w90"></div><div class="sk w70"></div>
        <svg viewBox="0 0 520 180"><g stroke="#c9ced6" stroke-width="1"><line x1="34" x2="392" y1="10" y2="10"/><line x1="34" x2="392" y1="84" y2="84"/><line x1="34" x2="392" y1="158" y2="158"/></g>
          <path d="M34,122 L80,112 L126,118 L172,96 L218,90 L264,70 L310,76 L356,52 L392,44" fill="none" stroke="#9aa3ae" stroke-width="3"/>
          <path d="M34,58 L80,66 L126,58 L172,74 L218,82 L264,96 L310,92 L356,110 L392,118" fill="none" stroke="#b8bec7" stroke-width="3"/></svg>
        <div class="sk w85"></div><div class="sk w60"></div>
      </div>
      <div class="veil-label"><b>Storyline in progress</b><span>Still being checked. It will appear here when it is ready.</span></div>
    </div>`;
  return el;
}
(function () {
  const YEARS = Array.from({length: 18}, (_, i) => 2008 + i);
  const C = {blue: "#4582cc", purple: "#8c3a91", gold: "#d4a92c", ink: "#333C47", muted: "#6c6b66", grid: "#e9ecf1"};

  const STORIES = [
    {placeholder: "Requests"},
    {
      kicker: "Outcomes", q: 4, qlabel: "Outcomes & exemptions", walk: true,
      title: "A shrinking share of requests is released in full",
      body: "Outside DHS and NARA, the share of processed requests released in full fell from 50.0% in FY2008 to 21.4% in FY2025. The fall holds with any single agency or component left out, and it comes mostly from agencies' own shares falling.",
      foot: "Share of all processed requests. Why DHS and NARA are left out, and what lies behind the fall, is in the 10 steps.",
      yMax: 60, unit: "%",
      series: [
        {name: "Released in full", color: C.blue, v: [50.0,45.5,47.0,47.1,47.3,47.3,42.0,39.7,39.3,38.0,40.1,37.1,36.8,32.9,30.2,29.7,24.3,21.4]},
        {name: "Partly released", color: C.purple, v: [10.2,13.5,16.0,18.9,18.2,17.9,21.2,22.7,23.0,23.3,23.0,24.4,22.8,23.8,23.1,27.9,31.7,32.3]},
        {name: "No records found", color: C.gold, v: [14.7,14.2,11.9,12.0,12.5,11.7,12.5,13.4,12.7,13.6,13.6,13.5,13.1,13.5,14.9,13.9,13.2,13.5]}]
    },
    {placeholder: "Appeals"},
    {placeholder: "Backlog"}
  ];

  const W = 520, H = 180, M = {l: 34, r: 128, t: 10, b: 22};
  const x = yr => M.l + (yr - 2008) / 17 * (W - M.l - M.r);
  const svgEl = (tag, attrs) => { const e = document.createElementNS("http://www.w3.org/2000/svg", tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e; };

  function chart(s) {
    const box = document.createElement("div"); box.className = "chart";
    const y = v => M.t + (1 - v / s.yMax) * (H - M.t - M.b);
    const svg = svgEl("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": s.title});
    [0, s.yMax / 2, s.yMax].forEach(t => {
      svg.appendChild(svgEl("line", {x1: M.l, x2: W - M.r, y1: y(t), y2: y(t), stroke: C.grid, "stroke-width": 1}));
      const lab = svgEl("text", {x: M.l - 6, y: y(t) + 3.5, "text-anchor": "end", "font-size": 10, fill: C.muted}); lab.textContent = t + s.unit; svg.appendChild(lab);
    });
    [2008, 2012, 2016, 2020, 2025].forEach(yr => {
      const lab = svgEl("text", {x: x(yr), y: H - 6, "text-anchor": "middle", "font-size": 10, fill: C.muted}); lab.textContent = yr; svg.appendChild(lab);
    });
    (s.avgs || []).forEach(a => {
      const vals = s.series[0].v.slice(a.from - 2008, a.to - 2008 + 1); const m = vals.reduce((p, c) => p + c, 0) / vals.length;
      svg.appendChild(svgEl("line", {x1: x(a.from), x2: x(a.to), y1: y(m), y2: y(m), stroke: C.muted, "stroke-width": 1.5, "stroke-dasharray": "4 3"}));
    });
    s.series.forEach(se => {
      const d = se.v.map((v, i) => `${i ? "L" : "M"}${x(YEARS[i]).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
      svg.appendChild(svgEl("path", {d, fill: "none", stroke: se.color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round"}));
    });
    // end labels (text in ink, colored dot carries identity), nudged apart
    const ends = s.series.map(se => ({se, yy: y(se.v[17])})).sort((a, b) => a.yy - b.yy);
    for (let i = 1; i < ends.length; i++) if (ends[i].yy - ends[i - 1].yy < 13) ends[i].yy = ends[i - 1].yy + 13;
    ends.forEach(({se, yy}) => {
      svg.appendChild(svgEl("circle", {cx: x(2025), cy: y(se.v[17]), r: 3, fill: se.color}));
      const t = svgEl("text", {x: x(2025) + 8, y: yy + 3.5, "font-size": 10.5, fill: C.ink});
      t.textContent = `${se.v[17]}${s.unit} ${s.series.length > 1 ? short(se.name) : ""}`; svg.appendChild(t);
    });
    // hover: crosshair + tooltip
    const cross = svgEl("line", {y1: M.t, y2: H - M.b, stroke: "#9aa3ae", "stroke-width": 1, visibility: "hidden"}); svg.appendChild(cross);
    const hit = svgEl("rect", {x: M.l, y: 0, width: W - M.l - M.r, height: H, fill: "transparent"}); svg.appendChild(hit);
    const tip = document.createElement("div"); tip.className = "tip";
    hit.addEventListener("mousemove", ev => {
      const r = svg.getBoundingClientRect(); const px = (ev.clientX - r.left) / r.width * W;
      const i = Math.max(0, Math.min(17, Math.round((px - M.l) / (W - M.l - M.r) * 17)));
      cross.setAttribute("x1", x(YEARS[i])); cross.setAttribute("x2", x(YEARS[i])); cross.setAttribute("visibility", "visible");
      tip.innerHTML = `<b>FY${YEARS[i]}</b><br>` + s.series.map(se => `<i style="background:${se.color}"></i>${se.name}: ${se.v[i]}${s.unit}`).join("<br>")
        + (s.extra ? `<br>${s.extra.name}: ${s.extra.fmt(s.extra.v[i])}` : "");
      tip.style.display = "block";
      const left = x(YEARS[i]) / W * r.width; tip.style.left = (left > r.width * 0.55 ? left - tip.offsetWidth - 10 : left + 10) + "px"; tip.style.top = "6px";
    });
    hit.addEventListener("mouseleave", () => { cross.setAttribute("visibility", "hidden"); tip.style.display = "none"; });
    box.appendChild(svg); box.appendChild(tip);
    return box;
  }
  const short = n => ({"Released in full": "in full", "Partly released": "partly", "No records found": "no records",
    "Privacy share of exemption citations": "privacy", "Full denials (of partly released + fully denied)": "full denials",
    "Agencies other than DHS": "not DHS", "DHS": "DHS"})[n] || n;

  function card(s) {
    const el = document.createElement("article"); el.className = "story";
    el.innerHTML = `<div class="kicker">${s.kicker}</div><h3>${s.title}</h3><p class="body">${s.body}</p>`;
    if (s.series.length > 1) el.insertAdjacentHTML("beforeend", `<div class="legend">${s.series.map(se => `<span><i style="background:${se.color}"></i>${se.name}</span>`).join("")}</div>`);
    el.appendChild(chart(s));
    const rows = YEARS.map((yr, i) => `<tr><td>FY${yr}</td>${s.series.map(se => `<td>${se.v[i]}${s.unit}</td>`).join("")}${s.extra ? `<td>${s.extra.fmt(s.extra.v[i])}</td>` : ""}</tr>`).join("");
    el.insertAdjacentHTML("beforeend", `<p class="foot">${s.foot}</p><div class="actions">${s.walk ? `<button type="button" class="walk">How we got here · 10 steps →</button>` : ""}<button type="button" class="go" data-q="${s.q}">Explore: ${s.qlabel} →</button>
      <details><summary>Numbers</summary><table><tr><th>Year</th>${s.series.map(se => `<th>${se.name}</th>`).join("")}${s.extra ? `<th>${s.extra.name}</th>` : ""}</tr>${rows}</table></details></div>`);
    el.querySelector(".go").addEventListener("click", () => { const b = document.querySelector(`.qbtn[data-id="${s.q}"]`); if (b) b.click(); });
    const wb = el.querySelector(".walk"); if (wb) wb.addEventListener("click", () => window.openS1Walk && window.openS1Walk(wb));
    return el;
  }

  function fill(es) {
    es.dataset.stories = "1"; es.classList.add("stories"); es.innerHTML = "";
    es.insertAdjacentHTML("beforeend", `<div class="stories-head"><h2>What the annual reports show</h2>
      <p>Four findings from the agencies' own FOIA reports, FY2008–FY2025, each checked step by step: open “How we got here” on a card to follow the analysis. Pick a question on the left to explore the data yourself.</p></div>`);
    const grid = document.createElement("div"); grid.className = "story-grid"; [["s0", "Requests"], ["s1", "Outcomes"], ["s3", "Appeals"], ["s4", "Backlog"]].forEach(([id, name]) => {
      const ph = storyPlaceholder(name); grid.appendChild(ph);
      if (window.storyCover) window.storyCover(id).then(el => { if (el && ph.isConnected) ph.replaceWith(el) }) }); es.appendChild(grid);
    es.insertAdjacentHTML("beforeend", `<p class="stories-method">How these were counted: government totals add up each agency's reported total (its components plus anything not assigned to one) and match foia.gov's government-wide totals. The reports are filled in by the agencies themselves. They show what changed, not why.</p>`);
  }
  const scan = () => document.querySelectorAll(".empty-state:not([data-stories])").forEach(fill);
  new MutationObserver(scan).observe(document.documentElement, {childList: true, subtree: true});
  document.addEventListener("DOMContentLoaded", scan);
})();

/* ---------- Storyline walkthroughs (2026-11-14): a cover card per storyline on the start page and a dialog of step cards.
   Text and numbers: data/walk_<id>.json, built by storylines/build/build_walks.py from the final
   storyline notebooks; every number is asserted there. ---------- */
(function () {
  const C = {blue: "#4582cc", purple: "#8c3a91", gold: "#d4a92c", green: "#0b5a36", navy: "#21304a", ink: "#333C47", muted: "#6c6b66", grid: "#e9ecf1"};
  const PAL = [C.blue, C.purple, C.gold, C.green, C.navy, "#7d8590"];
  const COLORS = {"Released in full": C.blue, "Partly released": C.purple, "No records found": C.gold, "Fully denied on exemptions": C.green,
    "Other closures": "#7d8590", "DHS share": C.purple, "Outside DHS": C.blue, "DHS": C.purple, "All agencies": "#8a8f98"};
  const SHORT = {"Released in full": "in full", "Partly released": "partly", "No records found": "no records", "Fully denied on exemptions": "denied",
    "Other closures": "other", "Outside DHS": "outside DHS", "DHS": "DHS", "All agencies": "all agencies"};
  const DASHED = new Set(["All agencies"]), NS = "http://www.w3.org/2000/svg";
  const CACHE = {}; let modal = null, cur = null, idx = 0, opener = null, STEPS = 0;
  const load = id => CACHE[id] || (CACHE[id] = fetch(`data/walk_${id}.json`).then(r => { if (!r.ok) throw new Error(r.status); return r.json() }));
  const el = (t, a) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); return e };
  const txt = (svg, a, s) => { const e = el("text", Object.assign({"font-size": 10.5, fill: C.ink}, a)); e.textContent = s; svg.appendChild(e); return e };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"})[c]);
  const num = (v, d = 1) => (v < 0 ? "−" + Math.abs(v).toFixed(d) : (v > 0 ? "+" : "") + v.toFixed(d));
  const p1 = v => v.toFixed(1);
  const compact = v => Math.abs(v) >= 1e6 ? (v / 1e6).toFixed(Math.abs(v) >= 1e7 ? 1 : 2).replace(/\.?0+$/, "") + "M" : Math.abs(v) >= 1e3 ? Math.round(v / 1e3) + "k" : String(Math.round(v));
  const niceTop = m => { if (m <= 0) return 1; const s = Math.pow(10, Math.floor(Math.log10(m))); return Math.ceil(m / s * 2) / 2 * s };
  const colorOf = (ch, k, i) => (ch.colors && ch.colors[k]) || COLORS[k] || PAL[i % PAL.length];
  const dashedOf = (ch, k) => (ch.dashed || []).includes(k) || DASHED.has(k);
  const shortOf = (ch, k) => (ch.short && ch.short[k] != null) ? ch.short[k] : (SHORT[k] || k);
  const unitFmt = ch => ch.unit === "count" ? {axis: compact, end: compact, tip: v => Math.round(v).toLocaleString("en-US")}
    : ch.unit === "plain" ? {axis: v => (+v.toFixed(2)).toString(), end: v => v.toFixed(ch.digits ?? 1), tip: v => v.toFixed(ch.digits ?? 1)}
    : {axis: v => (+v.toFixed(1)) + "%", end: v => p1(v) + "%", tip: v => p1(v) + "%"};
  const wrapBox = (svg, tip) => { const b = document.createElement("div"); b.className = "s1m-chart"; b.appendChild(svg); if (tip) b.appendChild(tip); return b };
  function hover(svg, W, x0, x1, n, onMove) {
    const tip = document.createElement("div"); tip.className = "tip";
    const hit = el("rect", {x: x0, y: 0, width: x1 - x0, height: "100%", fill: "transparent"}); svg.appendChild(hit);
    hit.addEventListener("pointermove", ev => { const r = svg.getBoundingClientRect(), i = Math.max(0, Math.min(n, Math.round(((ev.clientX - r.left) / r.width * W - x0) / (x1 - x0) * n)));
      tip.innerHTML = onMove(i); tip.style.display = "block"; const left = (x0 + i / n * (x1 - x0)) / W * r.width;
      tip.style.left = (left > r.width * 0.5 ? left - tip.offsetWidth - 10 : left + 10) + "px"; tip.style.top = "4px" });
    hit.addEventListener("pointerleave", () => { tip.style.display = "none" });
    return tip;
  }
  const ok = v => v != null && Number.isFinite(v);
  function lines(ch, years, W, ratio) {
    const H = Math.round(W * ratio), M = {l: 40, r: Math.round(W * 0.2), t: 10, b: 24}, names = Object.keys(ch.series), n = years.length - 1, F = unitFmt(ch);
    const vals = [...names.flatMap(k => ch.series[k].filter(ok)), ...(ch.ref || []).map(r => r.v), ...(ch.segs || []).map(s => s.v)];
    const lo = ch.yMin ?? 0, top = ch.yMax ?? (ch.unit ? niceTop(Math.max(...vals)) : [10, 20, 25, 40, 50, 60, 70, 80, 100].find(t => t >= Math.max(...vals)) || Math.ceil(Math.max(...vals) / 10) * 10);
    const x = i => M.l + i / n * (W - M.l - M.r), y = v => M.t + (1 - (v - lo) / (top - lo)) * (H - M.t - M.b);
    const svg = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": ch.title});
    [(lo + top) / 2, top].forEach(t => { svg.appendChild(el("line", {x1: M.l, x2: W - M.r, y1: y(t), y2: y(t), stroke: C.grid})); txt(svg, {x: M.l - 6, y: y(t) + 3.5, "text-anchor": "end", "font-size": 10, fill: C.muted}, F.axis(t)) });
    (ch.ref || []).forEach(rf => { svg.appendChild(el("line", {x1: M.l, x2: W - M.r, y1: y(rf.v), y2: y(rf.v), stroke: C.muted, "stroke-dasharray": "5 4"})); txt(svg, {x: M.l + 4, y: y(rf.v) - 5, "font-size": 10, fill: C.muted}, rf.label) });
    (ch.segs || []).forEach(sg => { const i0 = years.indexOf(sg.from), i1 = years.indexOf(sg.to);
      svg.appendChild(el("line", {x1: x(i0), x2: x(i1), y1: y(sg.v), y2: y(sg.v), stroke: C.navy, "stroke-width": 1.4, "stroke-dasharray": "2 3"}));
      txt(svg, {x: (x(i0) + x(i1)) / 2, y: y(sg.v) - 5, "text-anchor": "middle", "font-size": 9.5, fill: C.navy}, `avg ${F.end(sg.v)}`) });
    svg.appendChild(el("line", {x1: M.l, x2: W - M.r, y1: y(lo), y2: y(lo), stroke: "#8a8f98"})); txt(svg, {x: M.l - 6, y: y(lo) + 3.5, "text-anchor": "end", "font-size": 10, fill: C.muted}, F.axis(lo));
    const tickYears = years.filter(yr => n <= 6 || (n <= 17 ? yr % 2 === 0 : yr % 5 === 0));
    tickYears.forEach(yr => txt(svg, {x: x(years.indexOf(yr)), y: H - 6, "text-anchor": "middle", "font-size": 10, fill: C.muted}, yr));
    names.forEach((k, j) => { const s = ch.series[k], col = colorOf(ch, k, j), dash = dashedOf(ch, k); let seg = [];
      const flush = () => { if (seg.length > 1) svg.appendChild(el("path", {d: seg.map((p, i) => `${i ? "L" : "M"}${p}`).join(" "), fill: "none", stroke: col, "stroke-width": dash ? 1.7 : 2.2, "stroke-dasharray": dash ? "5 4" : "none", "stroke-linejoin": "round", "stroke-linecap": "round"}));
        if (seg.length === 1) { const [a, b] = seg[0].split(","); svg.appendChild(el("circle", {cx: a, cy: b, r: 2.5, fill: col})) } seg = [] };
      s.forEach((v, i) => ok(v) ? seg.push(`${x(i).toFixed(1)},${y(v).toFixed(1)}`) : flush()); flush() });
    const lastOk = s => { for (let i = n; i >= 0; i--) if (ok(s[i])) return i; return -1 };
    const ends = names.map((k, j) => { const i = lastOk(ch.series[k]); return i < 0 ? null : {k, j, i, v: ch.series[k][i], yy: y(ch.series[k][i])} }).filter(Boolean).sort((a, b) => a.yy - b.yy);
    for (let i = 1; i < ends.length; i++) if (ends[i].yy - ends[i - 1].yy < 13) ends[i].yy = ends[i - 1].yy + 13;
    ends.forEach(e => { svg.appendChild(el("circle", {cx: x(e.i), cy: y(e.v), r: 3, fill: colorOf(ch, e.k, e.j)})); const s = names.length > 1 ? shortOf(ch, e.k) : "";
      txt(svg, {x: x(n) + 8, y: e.yy + 3.5}, `${F.end(e.v)}${s ? " " + s : ""}${e.i < n ? ` (FY${years[e.i]})` : ""}`) });
    const tip = hover(svg, W, M.l, W - M.r, n, i => `<b>FY${years[i]}</b><br>` + names.map((k, j) => `<i style="background:${colorOf(ch, k, j)}"></i>${esc(k)}: ${ok(ch.series[k][i]) ? F.tip(ch.series[k][i]) : "–"}`).join("<br>"));
    return wrapBox(svg, tip);
  }
  function stack(ch, years, W, ratio) {
    const H = Math.round(W * ratio), M = {l: 36, r: 10, t: 8, b: 24}, names = Object.keys(ch.segments), n = years.length;
    const bw = (W - M.l - M.r) / n, y = v => M.t + (1 - v / 100) * (H - M.t - M.b);
    const svg = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": ch.title});
    [0, 50, 100].forEach(t => txt(svg, {x: M.l - 6, y: y(t) + 3.5, "text-anchor": "end", "font-size": 10, fill: C.muted}, t + "%"));
    years.forEach((yr, i) => { let acc = 0;
      names.forEach((k, j) => { const v = Math.max(0, ch.segments[k][i] || 0); svg.appendChild(el("rect", {x: M.l + i * bw + bw * 0.1, y: y(acc + v), width: bw * 0.8, height: y(acc) - y(acc + v), fill: colorOf(ch, k, j)})); acc += v });
      if (yr % 2 === 0) txt(svg, {x: M.l + i * bw + bw / 2, y: H - 6, "text-anchor": "middle", "font-size": 10, fill: C.muted}, yr) });
    const tip = hover(svg, W, M.l + bw / 2, W - M.r - bw / 2, n - 1, i => `<b>FY${years[i]}</b><br>` + names.map((k, j) => `<i style="background:${colorOf(ch, k, j)}"></i>${esc(k)}: ${p1(ch.segments[k][i] || 0)}%`).join("<br>"));
    return wrapBox(svg, tip);
  }
  function bars(ch, W) {
    const rowH = 44, M = {l: 250, r: 64, t: 6, b: 26}, H = M.t + rowH * ch.bars.length + M.b;
    const top = [10, 20, 25, 40, 50].find(t => t >= Math.max(...ch.bars.map(b => b.hi))) || 50, x = v => M.l + v / top * (W - M.l - M.r);
    const svg = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": ch.title});
    [0, top / 2, top].forEach(t => { svg.appendChild(el("line", {x1: x(t), x2: x(t), y1: M.t, y2: H - M.b, stroke: t ? C.grid : "#8a8f98"})); txt(svg, {x: x(t), y: H - 8, "text-anchor": "middle", "font-size": 10, fill: C.muted}, `${t} pts`) });
    ch.bars.forEach((b, i) => { const y0 = M.t + i * rowH + 12, c = i ? C.purple : C.blue;
      txt(svg, {x: M.l - 10, y: y0 + 13, "text-anchor": "end", "font-size": 11.5}, b.name);
      svg.appendChild(el("rect", {x: M.l, y: y0, width: x(b.v) - M.l, height: 18, rx: 2, fill: c, opacity: 0.85}));
      svg.appendChild(el("line", {x1: x(b.lo), x2: x(b.hi), y1: y0 + 9, y2: y0 + 9, stroke: C.ink, "stroke-width": 1.2}));
      [b.lo, b.hi].forEach(v => svg.appendChild(el("line", {x1: x(v), x2: x(v), y1: y0 + 4, y2: y0 + 14, stroke: C.ink, "stroke-width": 1.2})));
      txt(svg, {x: x(b.hi) + 6, y: y0 + 13, "font-weight": 600}, p1(b.v)) });
    const box = wrapBox(svg);
    box.insertAdjacentHTML("beforeend", `<table class="s1m-range"><tr><th></th><th>Average</th><th>Range</th></tr>${ch.bars.map(b => `<tr><td>${esc(b.name)}</td><td>${p1(b.v)} pts</td><td>${p1(b.lo)}–${p1(b.hi)}</td></tr>`).join("")}</table>`);
    return box;
  }
  function dbars(ch, W) {
    const cnt = ch.fmt === "count", rowH = cnt ? 22 : 27, M = {l: 190, r: cnt ? 80 : 56, t: 6, b: 8}, H = M.t + rowH * ch.bars.length + M.b, vs = ch.bars.map(b => b.v);
    const lo = Math.min(0, ...vs), hi = Math.max(0, ...vs), pad = (hi - lo) * 0.12, a = lo - (lo < 0 ? pad : 0), z = hi + (hi > 0 ? pad : 0);
    const x = v => M.l + (v - a) / (z - a) * (W - M.l - M.r), lab = v => cnt ? Math.round(v).toLocaleString("en-US") : num(v, ch.digits || 1);
    const svg = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": ch.title});
    ch.bars.forEach((b, i) => { const y0 = M.t + i * rowH + 4, c = COLORS[b.name] || (b.name.startsWith("All other") ? "#b8bec7" : b.v < 0 || cnt ? C.blue : "#9aa3ae");
      txt(svg, {x: M.l - 10, y: y0 + (cnt ? 10 : 12), "text-anchor": "end", "font-size": cnt ? 10.5 : 11.5}, b.name);
      svg.appendChild(el("rect", {x: Math.min(x(0), x(b.v)), y: y0, width: Math.abs(x(b.v) - x(0)), height: cnt ? 13 : 16, rx: 2, fill: c, opacity: 0.9}));
      txt(svg, {x: b.v < 0 ? x(b.v) - 5 : x(b.v) + 5, y: y0 + (cnt ? 10 : 12), "text-anchor": b.v < 0 ? "end" : "start", "font-weight": 600, "font-size": 10.5}, lab(b.v)) });
    svg.appendChild(el("line", {x1: x(0), x2: x(0), y1: M.t, y2: H - M.b, stroke: C.ink, "stroke-width": 1.2}));
    return wrapBox(svg);
  }
  function ranges(ch, W) {
    const rowH = 58, M = {l: 96, r: 24, t: 8, b: 26}, H = M.t + rowH * ch.rows.length + M.b;
    const lo = Math.min(...ch.rows.map(r => r.lo)), a = Math.floor((lo - 4) / 10) * 10, z = 5, x = v => M.l + (v - a) / (z - a) * (W - M.l - M.r);
    const svg = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": ch.title});
    for (let t = a; t <= 0; t += 10) { svg.appendChild(el("line", {x1: x(t), x2: x(t), y1: M.t, y2: H - M.b, stroke: t ? C.grid : C.ink, "stroke-width": t ? 1 : 1.4})); txt(svg, {x: x(t), y: H - 8, "text-anchor": "middle", "font-size": 10, fill: C.muted}, t ? "−" + -t : "0 (no change)") }
    ch.rows.forEach((r, i) => { const y0 = M.t + i * rowH + 14;
      txt(svg, {x: M.l - 12, y: y0 + 4, "text-anchor": "end", "font-size": 11.5, "font-weight": 600}, r.name);
      svg.appendChild(el("line", {x1: x(r.lo), x2: x(r.hi), y1: y0, y2: y0, stroke: "#b9cbe6", "stroke-width": 10, "stroke-linecap": "round"}));
      svg.appendChild(el("circle", {cx: x(r.base), cy: y0, r: 5.5, fill: C.blue, stroke: "#fff", "stroke-width": 1.5}));
      txt(svg, {x: M.l, y: y0 + 24, "text-anchor": "start", "font-size": 10, fill: C.muted}, `${num(r.lo)} to ${num(r.hi)} · no removal ${num(r.base)} · smallest fall ${r.hiLabel}`) });
    const box = wrapBox(svg);
    box.insertAdjacentHTML("afterbegin", `<div class="s1m-legend"><span><i style="background:#b9cbe6;height:8px;width:18px"></i>Range over the 571 removals</span><span><i style="background:${C.blue};height:9px;width:9px;border-radius:50%"></i>No removal</span></div>`);
    return box;
  }
  function rowdots(ch, W, kind) {   // one row per agency: two values on a 0-max % scale ("dots": two markers; "dumbbell": start to end)
    const rowH = kind === "dots" ? 17 : 22, M = {l: 168, r: 44, t: 6, b: 24}, H = M.t + rowH * ch.rows.length + M.b;
    const mx = ch.max || Math.ceil(Math.max(...ch.rows.flatMap(r => r.v)) / 25) * 25, x = v => M.l + v / mx * (W - M.l - M.r);
    const svg = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": ch.title});
    for (let t = 0; t <= mx; t += 25) { svg.appendChild(el("line", {x1: x(t), x2: x(t), y1: M.t, y2: H - M.b, stroke: t ? C.grid : "#8a8f98"})); txt(svg, {x: x(t), y: H - 8, "text-anchor": "middle", "font-size": 10, fill: C.muted}, t + "%") }
    ch.rows.forEach((r, i) => { const yy = M.t + i * rowH + rowH / 2, [a, b] = r.v;
      txt(svg, {x: M.l - 8, y: yy + 3.5, "text-anchor": "end", "font-size": 10.5}, r.name);
      if (kind === "dots") {
        svg.appendChild(el("rect", {x: x(b) - 3.5, y: yy - 3.5, width: 7, height: 7, fill: "#fff", stroke: "#5b5e6b", "stroke-width": 1.3}));
        svg.appendChild(el("circle", {cx: x(a), cy: yy, r: 4, fill: C.purple}));
        txt(svg, {x: W - M.r + 6, y: yy + 3.5, "font-size": 9.5, fill: C.muted}, p1(a) + "%");
      } else {
        const up = b > a, col = up ? C.purple : C.blue;
        svg.appendChild(el("line", {x1: x(a), x2: x(b), y1: yy, y2: yy, stroke: col, "stroke-width": 2.2}));
        svg.appendChild(el("circle", {cx: x(a), cy: yy, r: 4, fill: "#fff", stroke: col, "stroke-width": 1.5}));
        svg.appendChild(el("circle", {cx: x(b), cy: yy, r: 4, fill: col}));
        txt(svg, {x: x(Math.max(a, b)) + 8, y: yy + 3.5, "font-size": 9.5, fill: C.muted}, `${p1(a)} → ${p1(b)}`);
      } });
    const box = wrapBox(svg);
    box.insertAdjacentHTML("afterbegin", kind === "dots"
      ? `<div class="s1m-legend"><span><i style="background:${C.purple};height:9px;width:9px;border-radius:50%"></i>${esc(ch.keys[0])}</span><span><i style="background:#fff;border:1.3px solid #5b5e6b;height:8px;width:8px;border-radius:0"></i>${esc(ch.keys[1])}</span></div>`
      : `<div class="s1m-legend"><span><i style="background:#fff;border:1.5px solid ${C.ink};height:8px;width:8px;border-radius:50%"></i>${esc(ch.keys[0])}</span><span><i style="background:${C.ink};height:9px;width:9px;border-radius:50%"></i>${esc(ch.keys[1])}</span><span><i style="background:${C.purple}"></i>higher</span><span><i style="background:${C.blue}"></i>lower</span></div>`);
    return box;
  }
  const table = tb => `<figure class="s1m-ex"><figcaption>${esc(tb.title)}</figcaption><table><tr>${tb.head.map(h => `<th>${esc(h)}</th>`).join("")}</tr>${tb.rows.map(r => `<tr>${r.map((c, j) => j ? `<td>${esc(c)}</td>` : `<th>${esc(c)}</th>`).join("")}</tr>`).join("")}</table></figure>`;
  function figure(ch, years, W, ratio) {
    const fg = document.createElement("figure"); fg.innerHTML = `<figcaption>${esc(ch.title)}</figcaption>`;
    const kind = ch.kind || "lines", names = kind === "lines" ? Object.keys(ch.series) : kind === "stack" ? Object.keys(ch.segments) : [];
    if (names.length > 1) fg.insertAdjacentHTML("beforeend", `<div class="s1m-legend">${names.map((k, j) => `<span><i style="${dashedOf(ch, k) ? `border-top:2px dashed ${colorOf(ch, k, j)};height:0;background:none` : `background:${colorOf(ch, k, j)}${kind === "stack" ? ";height:9px;width:9px" : ""}`}"></i>${esc(k)}</span>`).join("")}</div>`);
    fg.appendChild(kind === "bars" ? bars(ch, W) : kind === "dbars" ? dbars(ch, W) : kind === "ranges" ? ranges(ch, W) : kind === "dots" || kind === "dumbbell" ? rowdots(ch, W, kind)
      : kind === "stack" ? stack(ch, years, W, ratio) : lines(ch, years, W, ratio));
    return fg;
  }
  function slide(s, i, years) {
    const d = document.createElement("section"); d.className = "s1m-slide"; d.setAttribute("aria-label", `Step ${i + 1} of ${STEPS}`);
    d.innerHTML = `<div class="s1m-cols"><div class="s1m-text"><div class="s1m-kicker">Step ${i + 1} of ${STEPS} · ${esc(s.kicker)}</div><h3>${esc(s.title)}</h3>
      ${s.sections.map(x => `<h4>${esc(x.h)}</h4>${x.p.map(p => `<p>${esc(p)}</p>`).join("")}`).join("")}
      ${s.method ? `<div class="s1m-method"><b>How it was counted.</b> ${esc(s.method)}</div>` : ""}</div><div class="s1m-figs"></div></div>`;
    const figs = d.querySelector(".s1m-figs"), ratio = s.charts.length > 1 ? 0.26 : 0.52;
    s.charts.forEach(ch => figs.appendChild(figure(ch, years, 640, ratio)));
    (s.tables || []).forEach(tb => figs.insertAdjacentHTML("beforeend", table(tb)));
    if (s.example) { const e = s.example, cell = c => c.startsWith("*") ? `<b>${esc(c.slice(1))}</b>` : esc(c);
      figs.insertAdjacentHTML("beforeend", `<figure class="s1m-ex"><figcaption>How the split works</figcaption><p>${esc(e.caption)}</p>
        <table><tr>${e.head.map(h => `<th>${esc(h)}</th>`).join("")}</tr>${e.rows.map(r => `<tr>${r.map((c, j) => j ? `<td>${cell(c)}</td>` : `<th>${esc(c)}</th>`).join("")}</tr>`).join("")}</table>
        <p class="s1m-small">Bold: the one thing that changes from the row above.</p></figure>`) }
    return d;
  }
  function shell() {
    modal = document.createElement("div"); modal.className = "s1m"; modal.hidden = true;
    modal.innerHTML = `<div class="s1m-backdrop"></div>
      <div class="s1m-panel" role="dialog" aria-modal="true" aria-labelledby="s1m-name">
        <header class="s1m-head"><div><div class="s1m-eyebrow"></div><div class="s1m-name" id="s1m-name"></div></div>
          <button type="button" class="s1m-x" aria-label="Close">×</button></header>
        <div class="s1m-dots"></div>
        <div class="s1m-view"><div class="s1m-track"></div><div class="s1m-more" aria-hidden="true">More below ↓</div></div>
        <footer class="s1m-foot"><button type="button" class="s1m-prev">← Back</button><span class="s1m-count" aria-live="polite"></span><button type="button" class="s1m-next">Next →</button></footer>
      </div>`;
    document.body.appendChild(modal);
    modal.querySelector(".s1m-x").addEventListener("click", close);
    modal.querySelector(".s1m-backdrop").addEventListener("click", close);
    modal.querySelector(".s1m-prev").addEventListener("click", () => go(idx - 1));
    modal.querySelector(".s1m-next").addEventListener("click", () => go(idx + 1));
    window.addEventListener("resize", () => { if (!modal.hidden) more() });
    const view = modal.querySelector(".s1m-view"); let sx = null, sy = 0;   // swipe: a mostly horizontal drag of 50px or more
    view.addEventListener("pointerdown", e => { sx = e.clientX; sy = e.clientY });
    view.addEventListener("pointerup", e => { if (sx == null) return; const dx = e.clientX - sx, dy = e.clientY - sy; sx = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > 1.5 * Math.abs(dy)) go(idx + (dx < 0 ? 1 : -1)) });
    view.addEventListener("pointercancel", () => { sx = null });
    document.addEventListener("keydown", e => {   // on the document: a click inside the dialog can move focus to the page
      if (!modal || modal.hidden) return;
      if (e.key === "Escape") close(); else if (e.key === "ArrowRight") go(idx + 1); else if (e.key === "ArrowLeft") go(idx - 1);
      else if (e.key === "Tab") { const f = [...modal.querySelectorAll("button:not([disabled])")].filter(b => !b.closest("[inert]")); const a = f.indexOf(document.activeElement);
        if (a === -1) { e.preventDefault(); f[0].focus() } else if (e.shiftKey && a === 0) { e.preventDefault(); f[f.length - 1].focus() } else if (!e.shiftKey && a === f.length - 1) { e.preventDefault(); f[0].focus() } } });
  }
  function fillFor(w) {
    STEPS = w.steps.length; cur = w.id;
    modal.querySelector(".s1m-eyebrow").textContent = `Storyline · ${w.name}`;
    modal.querySelector(".s1m-name").textContent = `How we got to “${w.cover.title}”`;
    const track = modal.querySelector(".s1m-track"), dots = modal.querySelector(".s1m-dots");
    track.replaceChildren(); dots.replaceChildren(); track.style.transform = "translateX(0)";
    w.steps.forEach((s, i) => { const sl = slide(s, i, w.years); sl.addEventListener("scroll", more, {passive: true}); track.appendChild(sl);
      const b = document.createElement("button"); b.type = "button"; b.className = "s1m-dot"; b.title = b.ariaLabel = `Step ${i + 1}: ${s.title}`;
      b.addEventListener("click", () => go(i)); dots.appendChild(b) });
  }
  function more() { const s = modal.querySelectorAll(".s1m-slide")[idx]; if (s) modal.querySelector(".s1m-view").classList.toggle("more", s.scrollTop + s.clientHeight < s.scrollHeight - 8) }
  function go(i) {
    idx = Math.max(0, Math.min(STEPS - 1, i));
    modal.querySelector(".s1m-track").style.transform = `translateX(${-idx * 100}%)`;
    modal.querySelectorAll(".s1m-dot").forEach((d, j) => j === idx ? d.setAttribute("aria-current", "step") : d.removeAttribute("aria-current"));
    modal.querySelectorAll(".s1m-slide").forEach((s, j) => { s.inert = j !== idx; if (j === idx) s.scrollTop = 0 });
    modal.querySelector(".s1m-count").textContent = `Step ${idx + 1} of ${STEPS}`;
    modal.querySelector(".s1m-prev").disabled = idx === 0; modal.querySelector(".s1m-next").disabled = idx === STEPS - 1;
    requestAnimationFrame(more);
  }
  async function open(id, from) {
    opener = from; let w;
    try { w = await load(id) } catch (err) { console.error(`walkthrough ${id}: could not load data/walk_${id}.json`, err); return }
    if (!modal) shell();
    if (cur !== id) fillFor(w);
    modal.hidden = false; document.documentElement.classList.add("s1m-open"); go(0); modal.querySelector(".s1m-x").focus();
  }
  function close() { modal.hidden = true; document.documentElement.classList.remove("s1m-open"); if (opener && opener.isConnected) opener.focus() }
  // the start-page card of one storyline: its finding, one chart, and the way into the steps
  async function cover(id) {
    const w = await load(id), c = w.cover, el = document.createElement("article"); el.className = "story";
    el.innerHTML = `<div class="kicker">${esc(c.kicker)}</div><h3>${esc(c.title)}</h3><p class="body">${esc(c.body)}</p>`;
    const fg = figure(c.chart, w.years, 520, 0.36); fg.querySelector("figcaption").remove(); el.appendChild(fg);
    const names = Object.keys(c.chart.series), F = unitFmt(c.chart);
    const rows = w.years.map((yr, i) => `<tr><td>FY${yr}</td>${names.map(k => `<td>${ok(c.chart.series[k][i]) ? F.tip(c.chart.series[k][i]) : "–"}</td>`).join("")}</tr>`).join("");
    el.insertAdjacentHTML("beforeend", `<p class="foot">${esc(c.foot || "")}</p><div class="actions"><button type="button" class="walk">How we got here · ${w.steps.length} steps →</button>
      <button type="button" class="go">Explore: ${esc(w.explore.label)} →</button>
      <details><summary>Numbers</summary><table><tr><th>Year</th>${names.map(k => `<th>${esc(k)}</th>`).join("")}</tr>${rows}</table></details></div>`);
    const wb = el.querySelector(".walk"); wb.addEventListener("click", () => open(id, wb));
    el.querySelector(".go").addEventListener("click", () => { const b = document.querySelector(`.qbtn[data-id="${w.explore.q}"]`); if (b) b.click() });
    return el;
  }
  window.openWalk = open;
  window.storyCover = id => cover(id).catch(err => { console.error(`storyline card ${id}:`, err); return null });
})();

/* ---------- Start-page header and the user guide (sample, branch exploring-storyline-display, 2026-11-14) ----------
   The header card's text is rewritten on the start page, with a third line that opens the guide. The guide sits in the same
   card, outside the part the dashboard redraws, and shows only when the card is expanded (Quarto's full-screen card). */
(function () {
  const GUIDE = `<div class="fd-guide" role="region" aria-label="How to use this dashboard">
    <h2>How to use this dashboard</h2>
    <div class="fd-cols">
      <section><h3>What this is</h3>
        <p>Every federal agency files an annual FOIA report. This dashboard puts the reports for FY2008–FY2025 side by side, for agencies
        and for their components: offices inside an agency, such as ICE inside DHS.</p>
        <p>Data: foia.gov annual reports, built 2026-11-02.</p>
        <h3>Three ways in</h3>
        <ol><li><b>Storylines</b>, on the start page: findings checked across all the years. “How we got here” on a card walks through each step.</li>
          <li><b>Questions 1–6</b>, on the left: Requests received &amp; processed · Response time · Backlog, staff &amp; cost · Outcomes &amp; exemptions · Appeals · Backlog vs intake. Each opens a chart.</li>
          <li><b>Explore all data</b>: any measure in the reports. Choose a Data type, then a Measure.</li></ol>
        <p class="fd-small">Click a selected item again to clear it.</p></section>
      <section><h3>Choosing what you see</h3>
        <dl><dt>Agency</dt><dd>“All agencies (government total)”, or one agency.</dd>
          <dt>Component</dt><dd>An office inside the agency you picked.</dd>
          <dt>Fiscal years (top right, once you pick a question or an agency)</dt><dd>Pick All years, Last 10, Last 5 or the latest year; or click a first year, then a last year. Click one year twice to see only that year. One-year views (distribution, exemptions, tables) use the last year chosen.</dd>
          <dt>Compare with (up to 5)</dt><dd>Adds agencies or components to the same chart; × removes one.</dd>
          <dt>Agencies added up in the total</dt><dd>All reporting agencies (71–122 a year), or only the 70 that reported all 18 years, so a total does not grow just because more agencies report.</dd></dl>
        <p>With an agency chosen and no question, the page shows an <b>Overview</b>: the key measure of each question. Each question has two tabs:
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
    const qn = qh.querySelector(".qnum"), start = !!qn && qn.textContent.trim() === "Federal FOIA Dashboard";
    card.classList.toggle("fd-start", start);   // the start page shows only the storylines, which do not use the years: no year buttons there
    if (!start) {   // questions 1-6: drop "who · years" under the title (the sidebar and the year buttons show both); keep coverage and one-year warnings
      if (/^Question [1-6]$/.test(qn ? qn.textContent.trim() : "")) {
        const sel = qh.querySelector(".sel");
        if (sel) { [...sel.childNodes].forEach(n => { if (!(n.nodeType === 1 && n.classList.contains("warn"))) n.remove() });
          const w = sel.querySelector(".warn"); if (w) w.textContent = w.textContent.replace(/^[\s\u00a0]*·\s*/, "");
          if (!sel.textContent.trim()) sel.remove() }
      }
      return;
    }
    qh.innerHTML = `<span class="qnum">Federal FOIA Dashboard</span>
      <div class="fd-sub">How federal agencies handle FOIA requests, from their own annual reports.</div>
      <div class="fd-open"><button type="button" class="fd-link">How to use this dashboard ↗</button></div>`;
    qh.querySelector(".fd-link").addEventListener("click", () => openGuide(card));
  }
  function rules() {
    const src = document.querySelector(".how-rules ul"), dst = document.querySelector(".fd-rules-body");
    if (src && dst && dst.textContent !== src.textContent) dst.replaceChildren(src.cloneNode(true));
  }
  const scan = () => { document.querySelectorAll(".qhead:not([data-guide])").forEach(fix); rules() };
  new MutationObserver(scan).observe(document.documentElement, {childList: true, subtree: true});
  document.addEventListener("DOMContentLoaded", scan);
})();

/* ---------- From v6 (2026-11-14): fiscal-year buttons replace the two year dropdowns, and the agency and component lists
   start with the largest ones. Only the controls change: the dashboard's own inputs stay in charge. The year buttons set
   the hidden "Fiscal years" dropdowns; the lists keep their options and values and are only regrouped. ---------- */
(function () {
  const DATA = (window.__foiaJson = window.__foiaJson || fetch("data/foia.json").then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(D => { D.ids.Agency = D.ids.Agency.map(fdAgency); return D }));
  const ev = el => el.dispatchEvent(new Event("change", {bubbles: true}));

  // ---- fiscal years: presets and one button per year, as in v6. Click a year, then another; the same year twice = one year
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
  // year chosen (only when it has more than 6), both A-Z inside their group, as in v6. A shorter list, not a ranking.
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
  function fixNote() {   // the sidebar note named the hidden "To FY" dropdown
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

/* ---------- "Clear all" for the agency and component choices (2026-11-14): resets Agency, Component and Compare with to how the
   page opens, in one step. Years, the question and "Agencies added up in the total" are not touched. ---------- */
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

/* ---------- The view in the page address, and "Copy link to this view" (from v3, 2026-11-14). The address records the question,
   agency, component, years, compare list, the two radio choices and the Explore measure; opening such a link sets the same
   controls again, in order, the way a user would. The dashboard's own code is not changed. ---------- */
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
    if (q === 5 && checkedText("Reversal rate out of") === "All processed appeals") p.set("base", "all");
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
  function button() {   // under the year buttons, as in v3
    const tl = document.querySelector(".fd-tl"); if (!tl || tl.querySelector(".fd-copy")) return;
    const b = document.createElement("button"); b.type = "button"; b.className = "fd-copy"; b.textContent = "Copy link to this view";
    b.addEventListener("click", async () => { sync();
      try { await navigator.clipboard.writeText(location.href); b.textContent = "Link copied" } catch (e) { b.textContent = "Copy it from the address bar" }
      setTimeout(() => { b.textContent = "Copy link to this view" }, 1800) });
    const row = document.createElement("div"); row.className = "fd-linkrow"; row.appendChild(b); tl.appendChild(row);
  }
  new MutationObserver(button).observe(document.documentElement, {childList: true, subtree: true});
  const start = new URLSearchParams(location.search);
  if ([...start.keys()].length) restore(start);
})();
