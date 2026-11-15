"""Build the Outcomes (S1) storyline: the cover and steps 1-3 (steps 4-10 come from s1_steps_4_10.py).

Numbers come from the notebook's own code (storyline_lib.py). Every number in the text is computed here and asserted
against the S1 notebook before anything is written; the text follows the notebook's sections 1-2.

usage: MPLBACKEND=Agg python storylines/build/build_s1_walk.py <out.json>
"""
import json, sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "notebooks"   # the S1 notebook and storyline_lib.py
sys.path.insert(0, str(LIB))
from storyline_lib import G, c02, FG, PG, NR, FD, YR, series, tot, isD, noD, noDN  # noqa: E402
import s1_steps_4_10  # noqa: E402  (steps 4-10, notebook sections 3-8)

r1 = lambda x: round(float(x), 1)
lst = lambda s: [r1(s[y]) for y in YR]
f = lambda x: f"{x:.1f}"
k = lambda x: f"{round(x, -3):,.0f}"          # "about 109,000"

# ---------- cover: outside DHS and NARA (same three lines as the start-page card) ----------
cover = {"Released in full": lst(series([FG], c02, noDN)), "Partly released": lst(series([PG], c02, noDN)),
         "No records found": lst(series([NR], c02, noDN))}
assert cover["Released in full"] == [50.0,45.5,47.0,47.1,47.3,47.3,42.0,39.7,39.3,38.0,40.1,37.1,36.8,32.9,30.2,29.7,24.3,21.4]
assert cover["Partly released"] == [10.2,13.5,16.0,18.9,18.2,17.9,21.2,22.7,23.0,23.3,23.0,24.4,22.8,23.8,23.1,27.9,31.7,32.3]
assert cover["No records found"] == [14.7,14.2,11.9,12.0,12.5,11.7,12.5,13.4,12.7,13.6,13.6,13.5,13.1,13.5,14.9,13.9,13.2,13.5]

# ---------- step 1: all government, four outcomes (notebook section 1) ----------
s1 = {"Released in full": series([FG], c02), "Partly released": series([PG], c02),
      "No records found": series([NR], c02), "Fully denied on exemptions": series([FD], c02)}
g_fg, g_pg, g_nr, g_fd = (s1[n] for n in s1)
assert (r1(g_fg[2008]), r1(g_fg[2025])) == (41.6, 9.5)
assert (r1(g_pg[2008]), r1(g_pg[2025])) == (17.8, 37.7)
assert (r1(g_nr[2008]), r1(g_nr[2025])) == (15.2, 29.7) and g_nr[2018] < g_nr[2017]
assert (r1(g_fd[2008]), r1(g_fd[2025])) == (3.8, 3.2)
top = {y: max(s1, key=lambda n: s1[n][y]) for y in YR}
assert all(top[y] == "Released in full" for y in YR if y <= 2013) and all(top[y] == "Partly released" for y in YR if y >= 2014)

# ---------- step 2: DHS's weight and its outcomes (notebook section 2, step 1) ----------
disp = lambda y, cond: sum(tot(G, c, y, cond) for c in c02)
nD08, nD25, nO08, nO25 = disp(2008, isD), disp(2025, isD), disp(2008, noD), disp(2025, noD)
assert (nD08, nD25, nO08, nO25) == (109028, 994992, 469113, 640181)
w = {y: 100 * disp(y, isD) / (disp(y, isD) + disp(y, noD)) for y in YR}
assert (r1(w[2008]), r1(w[2019]), r1(w[2025])) == (18.9, 49.0, 60.8) and all(w[y] > 50 for y in YR if y >= 2020) and all(w[y] < 50 for y in YR if y <= 2019)
fg_d, fg_o = series([FG], c02, isD), series([FG], c02, noD)
assert all(fg_d[y] < fg_o[y] for y in YR) and (r1(min(fg_d)), r1(max(fg_d))) == (2.4, 12.1)
assert (r1(fg_d[2008]), r1(fg_d[2025]), r1(fg_o[2008]), r1(fg_o[2025])) == (11.4, 2.4, 48.7, 20.7)
pg_d, pg_o = series([PG], c02, isD), series([PG], c02, noD)
assert (r1(pg_o[2008]), r1(pg_o[2025]), r1(pg_d[2008]), r1(pg_d[2025])) == (10.0, 34.3, 51.3, 40.0)
nr_d, nr_o = series([NR], c02, isD), series([NR], c02, noD)
assert (r1(nr_d[2008]), r1(nr_d[2025]), r1(nr_o[2008]), r1(nr_o[2025])) == (7.9, 40.2, 16.9, 13.4)

# ---------- step 3: two-group composition decomposition, FY2008 -> FY2025 (notebook section 2, step 2) ----------
wD0, wD1 = w[2008] / 100, w[2025] / 100
pD0, pD1, pO0, pO1 = fg_d[2008], fg_d[2025], fg_o[2008], fg_o[2025]
total = g_fg[2025] - g_fg[2008]
assert abs(total - (wD1 * pD1 + (1 - wD1) * pO1 - wD0 * pD0 - (1 - wD0) * pO0)) < 1e-9
parts = {  # (one order, the other order)
    "Outside DHS: its share fell": ((1 - wD0) * (pO1 - pO0), (1 - wD1) * (pO1 - pO0)),
    "DHS: handles more of the requests": ((wD1 - wD0) * (pD1 - pO1), (wD1 - wD0) * (pD0 - pO0)),
    "DHS: its own share fell": (wD0 * (pD1 - pD0), wD1 * (pD1 - pD0)),
}
avg = {n: (a + b) / 2 for n, (a, b) in parts.items()}
rng = {n: sorted(-x for x in ab) for n, ab in parts.items()}
assert r1(total) == -32.1 and abs(sum(avg.values()) - total) < 1e-9
assert [r1(-v) for v in avg.values()] == [16.8, 11.7, 3.6]
assert [[r1(x) for x in v] for v in rng.values()] == [[10.9, 22.7], [7.7, 15.7], [1.7, 5.5]]
# each order adds up exactly; the first is the notebook's worked order (22.7 + 7.7 + 1.7)
for i in (0, 1): assert abs(sum(ab[i] for ab in parts.values()) - total) < 1e-9
assert [r1(-ab[0]) for ab in parts.values()] == [22.7, 7.7, 1.7]
sh = [x / -total for x in rng["DHS: handles more of the requests"]]
assert (round(sh[0] * 100), round(sh[1] * 100)) == (24, 49)   # "a quarter to a half"
lo = lambda n: f(rng[n][0]); hi = lambda n: f(rng[n][1]); av = lambda n: f(-avg[n])
O, W_, D = list(parts)

data = {
    "built": "2026-11-14",
    "source": "storyline_lib.py on data/component_master_no_03_06_11.csv",
    "years": YR,
    "cover": {"series": cover},
    "steps": [
        {"kicker": "All agencies", "title": f"Across the government, full releases fell from {f(g_fg[2008])}% to {f(g_fg[2025])}%",
         "sections": [
            {"h": "What we looked at", "p": [
                "In the annual reports, every closed request ends in one of 12 ways. Four are drawn here, each as a share of all requests "
                "closed that year: released in full, partly released, no records found, and fully denied on exemptions. The other eight "
                "(such as referred, withdrawn or duplicate) stay in the total."]},
            {"h": "What the chart shows", "p": [
                f"Released in full fell from {f(g_fg[2008])}% in FY2008 to {f(g_fg[2025])}% in FY2025.",
                f"Partly released rose from {f(g_pg[2008])}% to {f(g_pg[2025])}%. It has been the most common of the four in every year since "
                "FY2014; before that, released in full was.",
                f"No records found rose from {f(g_nr[2008])}% to {f(g_nr[2025])}%, with a dip in FY2018 ({f(g_nr[2017])}% to {f(g_nr[2018])}%). "
                f"Fully denied on exemptions stayed small: {f(g_fd[2008])}% to {f(g_fd[2025])}%."]},
            {"h": "What this raises", "p": [
                "The curve is uneven, and one government-wide line can combine very different agencies. Is this a pattern shared across "
                "agencies, or the work of a few agencies with many requests or unusual outcomes? We start with DHS, which closes a very "
                "large number of requests."]}],
         "method": "Share = requests closed that way ÷ all requests closed that year. Government totals add up every agency's reported "
                   "total. FY2008–09: 26 agencies are not yet in the foia.gov data.",
         "charts": [{"title": "Share of all closed requests, all agencies", "series": {n: lst(v) for n, v in s1.items()}}]},

        {"kicker": "All agencies · DHS", "title": f"DHS now closes {round(w[2025] / 10)} in 10 requests, and it rarely releases in full",
         "sections": [
            {"h": "What we looked at", "p": [
                "The same figures, split into DHS and everyone else (“outside DHS”: every other agency and component)."]},
            {"h": "What the charts show", "p": [
                f"DHS closed about {k(nD08)} requests in FY2008, {f(w[2008])}% of all. In FY2025 it closed about {k(nD25)}, more than "
                f"{int(nD25 // nD08)} times as many and {f(w[2025])}% of all. Outside DHS, closed requests grew only from about {k(nO08)} "
                f"to about {k(nO25)}. DHS has closed more than half of all requests every year since FY2020 ({f(w[2019])}% in FY2019).",
                f"In every year DHS released in full less often than the rest of the government: {f(fg_d[2008])}% in FY2008 and "
                f"{f(fg_d[2025])}% in FY2025, never above {f(max(fg_d))}%. Outside DHS the share fell from {f(fg_o[2008])}% to {f(fg_o[2025])}%."]},
            {"h": "Why it matters", "p": [
                "The government-wide share is an average of DHS and outside DHS, weighted by how many requests each closes. Since DHS "
                "passed half, the government-wide line (grey, dashed) sits closer to DHS's.",
                f"So one national line can hide opposite movements. Partly released rose government-wide from {f(g_pg[2008])}% to "
                f"{f(g_pg[2025])}%; outside DHS it rose from {f(pg_o[2008])}% to {f(pg_o[2025])}%, while at DHS it fell from "
                f"{f(pg_d[2008])}% to {f(pg_d[2025])}%."]}],
         "method": "Each share is out of that group's own closed requests. “Outside DHS” includes NARA and every other agency.",
         "charts": [{"title": "DHS's share of all closed requests", "series": {"DHS share": lst(w)}, "ref": [{"v": 50, "label": "half"}]},
                    {"title": "Released in full, share of closed requests",
                     "series": {"Outside DHS": lst(fg_o), "DHS": lst(fg_d), "All agencies": lst(g_fg)}}]},

        {"kicker": "All agencies · DHS", "title": "A quarter to a half of the national drop comes from DHS handling more of the requests",
         "sections": [
            {"h": "The question", "p": [
                f"The government-wide full-release share fell {f(-total)} points ({f(g_fg[2008])}% to {f(g_fg[2025])}%). Two things changed "
                f"at once: the rates (DHS {f(pD0)}% to {f(pD1)}%, outside DHS {f(pO0)}% to {f(pO1)}%) and DHS's share of closed requests "
                f"({f(w[2008])}% to {f(w[2025])}%). How much of the fall is agencies releasing in full less often, and how much is more "
                "requests going to DHS, which rarely releases in full?"]},
            {"h": "How the split works", "p": [
                "Change one thing at a time, as in the example with made-up numbers: first the rates with the request counts held fixed, "
                "then the counts with the rates held fixed. The middle row never happened; it only separates the two changes.",
                "Done in the other order, the parts come out different. The method (a composition decomposition, Kitagawa 1955) takes the "
                "average of the two orders and reports both as a range. In either order the parts add up exactly to the total."]},
            {"h": "What we found", "p": [
                f"About {av(O)} points come from the share outside DHS falling ({lo(O)}–{hi(O)}), about {av(W_)} from DHS handling more of "
                f"the requests ({lo(W_)}–{hi(W_)}), and about {av(D)} from DHS's own share falling ({lo(D)}–{hi(D)}).",
                f"So a quarter to a half of the national drop is the shift toward DHS. But outside DHS the share fell on its own: "
                f"{lo(O)} to {hi(O)} points, whichever order is used."]},
            {"h": "What comes next", "p": [
                f"Inside DHS there is a different change: its no-records share rose from {f(nr_d[2008])}% to {f(nr_d[2025])}% (most of the "
                f"added count is at CBP and USCIS), while outside DHS it did not rise ({f(nr_o[2008])}% to {f(nr_o[2025])}%). That is kept "
                "as a separate lead. The rest of this storyline follows the fall outside DHS: is it driven by individual agencies?"]}],
         "method": "An arithmetic split: it shows how many points each part accounts for, not why. It uses two groups only; step 8 "
                   "splits by agency.",
         "charts": [{"kind": "bars", "title": f"FY2008–25 change in the full-release share: {f(total).replace('-', '−')} points",
                     "bars": [{"name": n, "v": r1(-avg[n]), "lo": r1(rng[n][0]), "hi": r1(rng[n][1])} for n in parts]}],
         "example": {"caption": "The idea, with made-up numbers. A is like DHS (rarely releases in full), B like the rest. First B's rate "
                                "falls (42% to 26%: 16 points from rates); then 40 requests move from B to A (26% to 18%: 8 points from the shift).",
                     "head": ["", "A requests", "A rate", "B requests", "B rate", "Released in full", "Share"],
                     "rows": [["Year 1", "20", "10%", "80", "50%", "2 + 40 = 42", "42%"],
                              ["Hypothetical", "20", "10%", "80", "*30%", "2 + 24 = 26", "26%"],
                              ["Year 2", "*60", "10%", "*40", "30%", "6 + 12 = 18", "18%"]]}},
    ],
}
data["steps"] += s1_steps_4_10.build()
assert len(data["steps"]) == 10
Path(sys.argv[1]).write_text(json.dumps(data, ensure_ascii=False, indent=1))
print("ok:", sys.argv[1], "| total", f(total), "| parts", {n: av(n) for n in parts})
