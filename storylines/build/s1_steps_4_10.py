"""Steps 4-10 of the Outcomes (S1) storyline (notebook sections 3-8), used by build_s1_walk.py.
Every number in the text is computed with the notebook's code and asserted against the notebook before it is used."""
from collections import defaultdict
from storyline_lib import G, c02, FG, PG, NR, FD, YR, tot, bykey, paired, AGK, COK, isD, noD, noDN, vba
from storyline_lib import series as _series

def series(*a):   # the notebook's series(), as a plain {year: share} dict
    return {int(k): float(v) for k, v in _series(*a).items()}

r1 = lambda x: round(float(x), 1); r2 = lambda x: round(float(x), 2)
lst = lambda s: [r1(s[y]) for y in YR]
f = lambda x: f"{x:.1f}"; f2 = lambda x: f"{x:.2f}"
sg = lambda x, d=1: (f"+{x:.{d}f}" if x > 0 else f"−{-x:.{d}f}") if round(x, d) != 0 else f"{0:.{d}f}"
n0 = lambda x: f"{round(x):,}"
OTHER = [c for c in c02 if c not in (FG, PG, NR, FD)]
assert len(OTHER) == 8
isNARA = lambda r: AGK(r) == "NARA"
no_vba = lambda r: noDN(r) and not vba(r)
no_va = lambda r: noDN(r) and AGK(r) != "VA"
isEOIR = lambda r: AGK(r) == "DOJ" and r["Component"] == "EOIR"
disp = lambda y, cond: sum(tot(G, c, y, cond) for c in c02)

def mix(base):
    m = {"Released in full": series([FG], c02, base), "Partly released": series([PG], c02, base),
         "No records found": series([NR], c02, base), "Fully denied on exemptions": series([FD], c02, base)}
    m["Other closures"] = {y: 100 - sum(m[k][y] for k in list(m)) for y in YR}
    return m

def counts(y, cols, base, key=COK):
    n, d = defaultdict(float), defaultdict(float)
    for c in cols:
        for k, v in bykey(y, c, base, key).items(): n[k] += v
    for c in c02:
        for k, v in bykey(y, c, base, key).items(): d[k] += v
    return n, d

def contributions(cols, y0, y1, base, key=COK):
    (a0, d0), (a1, d1) = counts(y0, cols, base, key), counts(y1, cols, base, key)
    T0, T1 = sum(d0.values()), sum(d1.values())
    return {k: 100 * (a1.get(k, 0) / T1 - a0.get(k, 0) / T0) for k in set(a0) | set(a1)}

def build():
    # ======================= step 4: NARA (section 3) =======================
    nara = mix(isNARA); out_d, out_dn = mix(noD), mix(noDN)
    top = {y: max(nara, key=lambda k: nara[k][y]) for y in YR}
    assert all(top[y] == "No records found" and nara["No records found"][y] >= 78 for y in YR if y <= 2017)
    assert [top[y] for y in (2018, 2019, 2020, 2021)] == ["Released in full", "Released in full", "Partly released", "Released in full"]
    assert [r1(nara["Released in full"][y]) for y in (2018, 2019, 2021)] == [68.1, 71.6, 76.8] and r1(nara["Partly released"][2020]) == 87.1
    assert all(top[y] == "Partly released" for y in (2022, 2023, 2024, 2025))
    assert (r1(min(nara["Partly released"][y] for y in (2022, 2023, 2024, 2025))), r1(max(nara["Partly released"][y] for y in (2022, 2023, 2024, 2025)))) == (60.3, 82.4)
    nw = {y: 100 * disp(y, isNARA) / disp(y, noD) for y in YR}
    assert (r1(min(nw.values())), r1(max(nw.values()))) == (1.8, 15.2)
    fo, fn = out_d["Released in full"], out_dn["Released in full"]
    assert (r1(fo[2017]), r1(fo[2018]), r1(fn[2017]), r1(fn[2018])) == (33.2, 43.4, 38.0, 40.1)
    assert (r1(fo[2008]), r1(fo[2025]), r1(fn[2008]), r1(fn[2025])) == (48.7, 20.7, 50.0, 21.4)
    gap = {y: abs(fo[y] - fn[y]) for y in YR}; gy = max(gap, key=gap.get)
    assert (r1(gap[gy]), gy) == (5.2, 2019)
    step4 = {"kicker": "Outside DHS · NARA", "title": "NARA's outcomes swing from year to year, so it is set aside",
      "sections": [
        {"h": "What we looked at", "p": [
          f"Outside DHS, the full-release share jumps from {f(fo[2017])}% in FY2017 to {f(fo[2018])}% in FY2018. Most of that jump is one "
          "agency, the National Archives (NARA). The bars show how NARA's own requests ended each year."]},
        {"h": "What the charts show", "p": [
          "NARA's most common outcome changes every few years: no records found in FY2008–17 (78% or more each year), released in full in "
          f"FY2018–19 ({f(nara['Released in full'][2018])}% and {f(nara['Released in full'][2019])}%), partly released in FY2020 "
          f"({f(nara['Partly released'][2020])}%), released in full again in FY2021 ({f(nara['Released in full'][2021])}%), and partly released in FY2022–25 (60.3%–82.4%).",
          f"NARA is {f(min(nw.values()))}%–{f(max(nw.values()))}% of the requests closed outside DHS, enough to put swings into that line. "
          f"Without NARA, the FY2017–18 jump is only {f(fn[2017])}% to {f(fn[2018])}%."]},
        {"h": "What setting NARA aside changes", "p": [
          f"Mainly the middle years. The endpoints barely move: released in full goes from {f(fo[2008])}% to {f(fo[2025])}% with NARA and "
          f"from {f(fn[2008])}% to {f(fn[2025])}% without it; the widest gap between the two lines is {f(gap[gy])} points (FY{gy}). "
          "Setting NARA aside does not create the long-run fall."]},
        {"h": "What we do not claim", "p": [
          "The reports do not say why NARA's categories change, and we do not decide whether they are errors. NARA is set aside, not "
          "corrected; its pattern is a lead of its own."]}],
      "method": "From here on, every figure is for agencies outside DHS and NARA, unless it says otherwise.",
      "charts": [{"kind": "stack", "title": "How NARA's requests ended, each year (adds up to 100%)", "segments": {k: lst(v) for k, v in nara.items()}},
                 {"title": "Released in full, share of closed requests",
                  "series": {"Outside DHS": lst(fo), "Outside DHS and NARA": lst(fn)},
                  "colors": {"Outside DHS": "#9aa3ae", "Outside DHS and NARA": "#4582cc"}, "short": {"Outside DHS": "with NARA", "Outside DHS and NARA": "without NARA"}}]}

    # ======================= step 5: outside DHS and NARA (section 4) =======================
    m = out_dn; ch = {k: m[k][2025] - m[k][2008] for k in m}
    assert [r1(m[k][2008]) for k in m] == [50.0, 10.2, 14.7, 4.6, 20.5] and [r1(m[k][2025]) for k in m] == [21.4, 32.3, 13.5, 6.0, 26.8]
    assert [r1(v) for v in ch.values()] == [-28.5, 22.0, -1.2, 1.4, 6.3] and abs(sum(ch.values())) < 1e-9
    fd = m["Fully denied on exemptions"]; assert (r1(min(fd.values())), r1(max(fd.values()))) == (4.6, 9.5)
    assert (r1(min(m["Released in full"][y] for y in range(2009, 2014))), r1(max(m["Released in full"][y] for y in range(2009, 2014)))) == (45.5, 47.3)
    assert r1(m["Released in full"][2010]) == 47.0 and r1(m["Released in full"][2010] - m["Released in full"][2025]) == 25.6
    c18 = contributions([FG], 2017, 2018, noDN)
    assert (r2(c18["USDA/FSA"]), r2(c18["DOJ/EOIR"])) == (2.51, 1.51)
    sub = {lab: series([col], c02, noDN) for lab, col in (("improper", "[ImproperRequest]"), ("duplicate", "[Duplicate]"), ("other", "[Other]"))
           for col in [next(c for c in c02 if col in c)]}
    assert [(r1(s[2008]), r1(s[2025])) for s in sub.values()] == [(3.7, 8.4), (1.9, 4.3), (1.5, 3.9)]
    step5 = {"kicker": "Outside DHS and NARA", "title": "Outside DHS and NARA, full releases fell from 50.0% to 21.4%",
      "sections": [
        {"h": "What we looked at", "p": [
          "The same outcomes, now only for agencies outside DHS and NARA. The eight other ways a request can end (such as referred, "
          "withdrawn, duplicate or improper) are grouped as “other closures”, so the five lines add up to 100% every year."]},
        {"h": "What the chart shows", "p": [
          f"Released in full fell from {f(m['Released in full'][2008])}% in FY2008 to {f(m['Released in full'][2025])}% in FY2025. Partly released "
          f"rose from {f(m['Partly released'][2008])}% to {f(m['Partly released'][2025])}%. No records found barely moved "
          f"({f(m['No records found'][2008])}% to {f(m['No records found'][2025])}%), and full denials on exemptions stayed low ({f(min(fd.values()))}%–{f(max(fd.values()))}% a year).",
          "The fall is not every year. It is flat in FY2009–13 (45.5%–47.3%) and rises 2.1 points in FY2018, when two units that almost "
          f"always release in full closed many more requests (USDA's FSA {sg(c18['USDA/FSA'], 2)} points, DOJ's EOIR {sg(c18['DOJ/EOIR'], 2)}). "
          f"FY2008 has the fewest agencies in the data; counted from FY2010 the fall is {f(m['Released in full'][2010])}% to {f(m['Released in full'][2025])}%."]},
        {"h": "Where the 28.5 points went", "p": [
          f"Partly released rose {f(ch['Partly released'])} points, less than the {f(-ch['Released in full'])}-point fall. Other closures rose "
          f"{f(ch['Other closures'])} points ({f(m['Other closures'][2008])}% to {f(m['Other closures'][2025])}%): improper requests "
          f"{f(sub['improper'][2008])}% to {f(sub['improper'][2025])}%, duplicates {f(sub['duplicate'][2008])}% to {f(sub['duplicate'][2025])}%, "
          f"other reasons {f(sub['other'][2008])}% to {f(sub['other'][2025])}%.",
          "So these are two shifts in yearly totals, not the same requests moving from full to partial release."]},
        {"h": "What this raises", "p": [
          "Partly released stays flat for years and then jumps from FY2023. Is that rise shared, or one unit?"]}],
      "method": "Shares of all requests closed outside DHS and NARA. The changes on the right are in percentage points and add up to zero.",
      "charts": [{"title": "Share of all closed requests, outside DHS and NARA", "series": {k: lst(v) for k, v in m.items()}},
                 {"kind": "dbars", "title": "Change from FY2008 to FY2025, percentage points", "bars": [{"name": k, "v": r1(v)} for k, v in ch.items()]}]}

    # ======================= step 6: VBA (section 5, first part) =======================
    pg, pgv = series([PG], c02, noDN), series([PG], c02, no_vba)
    assert [r1(pg[y]) for y in (2022, 2023, 2024, 2025)] == [23.1, 27.9, 31.7, 32.3]
    assert (r1(min(pg[y] for y in range(2014, 2023))), r1(max(pg[y] for y in range(2014, 2023)))) == (21.2, 24.4)
    c23, c25 = contributions([PG], 2022, 2023, noDN), contributions([PG], 2022, 2025, noDN)
    t23, t25 = sum(c23.values()), sum(c25.values())
    assert (r2(t23), r2(c23["VA/VBA"]), r2(t23 - c23["VA/VBA"])) == (4.77, 8.95, -4.18)
    assert (r2(t25), r2(c25["VA/VBA"]), r2(t25 - c25["VA/VBA"])) == (9.17, 14.73, -5.56)
    vd = {y: disp(y, vba) for y in YR}; vs = {y: 100 * vd[y] / disp(y, noDN) for y in YR}
    assert [vd[y] for y in (2022, 2023, 2024, 2025)] == [7586, 54244, 97415, 99224] and [r1(vs[y]) for y in (2022, 2025)] == [2.1, 16.2]
    vpg, vfg = series([PG], c02, vba), series([FG], c02, vba)
    assert (r1(vpg[2022]), r1(vpg[2025]), r1(vfg[2022]), r1(vfg[2025])) == (31.3, 95.0, 56.0, 1.5)
    fgv = series([FG], c02, no_vba); assert (r1(fgv[2008]), r1(fgv[2025])) == (48.6, 25.3)
    mv = mix(no_vba)
    assert (r1(mv["Released in full"][2017] - mv["Released in full"][2008]), r1(mv["Partly released"][2017] - mv["Partly released"][2008])) == (-10.6, 12.3)
    assert (r1(pg[2025] - pg[2017]), r1(pgv[2017]), r1(pgv[2025]), r1(pgv[2025] - pgv[2017])) == (9.0, 22.9, 20.1, -2.8)
    assert (r1(mv["Other closures"][2025] - mv["Other closures"][2017]), r1(mv["No records found"][2025] - mv["No records found"][2017])) == (14.9, 2.1)
    co = contributions(OTHER, 2017, 2025, no_vba); srt = sorted(co.items(), key=lambda kv: -kv[1])
    assert (srt[0][0], r1(srt[0][1]), srt[1][0], r1(srt[1][1])) == ("DOJ/EOIR", 2.2, "HHS/CMS", 1.6)
    top10 = sum(v for _, v in srt[:10]); assert (r1(top10), r1(sum(co.values()) - top10)) == (8.3, 6.6)
    step6 = {"kicker": "Outside DHS and NARA · VBA", "title": "Since FY2017, the rise in partial releases is one component: VA's VBA",
      "sections": [
        {"h": "What we looked at", "p": [
          f"Partly released stayed at {f(min(pg[y] for y in range(2014, 2023)))}%–{f(max(pg[y] for y in range(2014, 2023)))}% every year in "
          f"FY2014–22, then jumped: {f(pg[2022])}% in FY2022, {f(pg[2023])}% in FY2023, {f(pg[2024])}% in FY2024 and {f(pg[2025])}% in FY2025. "
          "We split the jump by unit: each unit's partial releases as a share of all closed requests, later year minus FY2022. The parts add up exactly."]},
        {"h": "What we found", "p": [
          "Almost all of it is the Veterans Benefits Administration (VBA), part of VA (table). Every other unit together pulled the other way.",
          f"VBA's volume and outcomes changed at the same time. It closed {n0(vd[2022])} requests in FY2022 and {n0(vd[2025])} in FY2025 "
          f"({f(vs[2022])}% to {f(vs[2025])}% of all requests closed outside DHS and NARA), and its partly-released share went from "
          f"{f(vpg[2022])}% to {f(vpg[2025])}% while its full-release share fell from {f(vfg[2022])}% to {f(vfg[2025])}%."]},
        {"h": "The test: remove VBA from all years", "p": [
          f"Released in full still falls, from {f(fgv[2008])}% to {f(fgv[2025])}%, so VBA does not drive that decline.",
          f"Partly released has two periods. In FY2008–17 it still rises {f(mv['Partly released'][2017] - mv['Partly released'][2008])} points "
          f"without VBA. In FY2017–25 it rises {f(pg[2025] - pg[2017])} points with VBA but falls {f(pgv[2017] - pgv[2025])} without it "
          f"({f(pgv[2017])}% to {f(pgv[2025])}%). Of 571 single removals (step 9), only removing VBA or all of VA does this."]},
        {"h": "What replaced full releases, without VBA", "p": [
          f"In FY2017–25, mostly other closures: +{f(mv['Other closures'][2025] - mv['Other closures'][2017])} points (improper requests, "
          f"other reasons, duplicates). The rise is spread across many units: the largest are DOJ's EOIR (+{f(srt[0][1])}) and HHS's CMS "
          f"(+{f(srt[1][1])}); the top ten add +{f(top10)} and all others +{f(sum(co.values()) - top10)}."]}],
      "method": "The reports do not say why VBA changed. We do not decide whether it changed how it handles requests or how it reports them.",
      "charts": [{"title": "Partly released, share of closed requests", "series": {"Outside DHS and NARA": lst(pg), "Also without VBA": lst(pgv)},
                  "colors": {"Outside DHS and NARA": "#8c3a91", "Also without VBA": "#21304a"}, "short": {"Outside DHS and NARA": "with VBA", "Also without VBA": "without VBA"}},
                 {"title": "VBA's own requests: how they ended", "series": {"Partly released": lst(vpg), "Released in full": lst(vfg)},
                  "colors": {"Partly released": "#8c3a91", "Released in full": "#4582cc"}}],
      "tables": [{"title": "Where the jump in partial releases comes from (percentage points)", "head": ["", "Total change", "VBA", "All other units"],
                  "rows": [["FY2022 → FY2023", sg(t23, 2), sg(c23["VA/VBA"], 2), sg(t23 - c23["VA/VBA"], 2)],
                           ["FY2022 → FY2025", sg(t25, 2), sg(c25["VA/VBA"], 2), sg(t25 - c25["VA/VBA"], 2)]]}]}

    # ======================= step 7: requests closed without records (section 5, second part) =======================
    REV = [FG, PG, FD]
    fr_dn, fr_v = series([FG], REV, noDN), series([FG], REV, no_vba)
    rs_v = series(REV, c02, no_vba)
    assert [r1(fr_dn[y]) for y in (2008, 2017, 2025)] == [77.2, 54.4, 35.9] and [r1(fr_v[y]) for y in (2008, 2017, 2025)] == [76.0, 54.7, 48.1]
    assert [r1(rs_v[y]) for y in (2008, 2017, 2025)] == [64.0, 69.6, 52.6]
    def split(y0, y1):
        R0, R1, F0, F1 = (round(x, 2) for x in (rs_v[y0], rs_v[y1], fr_v[y0], fr_v[y1]))   # two-decimal values, as in the notebook
        total = round(fgv[y1], 2) - round(fgv[y0], 2); p1 = (R1 - R0) * (F0 + F1) / 2 / 100
        return total, p1, total - p1
    a = split(2008, 2017); b = split(2017, 2025)
    assert [r2(x) for x in b] == [-12.74, -8.74, -4.00] and (r2(a[1]), r2(a[2])) == (3.68, -14.24)
    nfg = {y: tot(G, FG, y, no_vba) for y in (2017, 2025)}; ndp = {y: disp(y, no_vba) for y in (2017, 2025)}
    assert (nfg[2017], nfg[2025], ndp[2017], ndp[2025]) == (147853, 129974, 388535, 513446)
    step7 = {"kicker": "Outside DHS and NARA · without VBA", "title": "Without VBA, most of the recent fall is requests closed without any records processed",
      "sections": [
        {"h": "What we looked at", "p": [
          "A request whose records were reviewed must end as released in full, partly released or fully denied on exemptions. The other "
          "nine ways, including no records found, are used only when no records were processed.",
          "So a falling full-release share can mean two things: less released in full among reviewed requests, or more requests closed "
          "without any records processed. The share splits exactly into two factors: (reviewed ÷ all closed) × (released in full ÷ reviewed)."]},
        {"h": "What we found", "p": [
          f"Among reviewed requests, the full-release share also fell: outside DHS and NARA {f(fr_dn[2008])}% (FY2008), {f(fr_dn[2017])}% "
          f"(FY2017) and {f(fr_dn[2025])}% (FY2025); without VBA {f(fr_v[2008])}%, {f(fr_v[2017])}% and {f(fr_v[2025])}%.",
          f"FY2008–17, without VBA: the whole fall comes from less released among reviewed requests ({f2(a[2]).replace('-', '−')} points); "
          f"the reviewed share actually rose ({f(rs_v[2008])}% to {f(rs_v[2017])}%).",
          f"FY2017–25, without VBA: the share fell {f2(-b[0])} points. {f2(-b[1])} of them come from the reviewed share falling "
          f"({f(rs_v[2017])}% to {f(rs_v[2025])}%, more requests closed without records processed), and only {f2(-b[2])} from less "
          f"released among reviewed requests ({f(fr_v[2017])}% to {f(fr_v[2025])}%)."]},
        {"h": "A fact that does not depend on the denominator", "p": [
          f"Without VBA, the number of full releases fell from {n0(nfg[2017])} in FY2017 to {n0(nfg[2025])} in FY2025, while closed "
          f"requests rose from {n0(ndp[2017])} to {n0(ndp[2025])}."]}],
      "method": "Part 1 = change in the reviewed share × the two-year average of the other factor; part 2 = the rest, so the two parts add "
                "up exactly. Computed from two-decimal values, as in the notebook.",
      "charts": [{"title": "Released in full, share of requests whose records were reviewed", "series": {"Outside DHS and NARA": lst(fr_dn), "Also without VBA": lst(fr_v)},
                  "colors": {"Outside DHS and NARA": "#4582cc", "Also without VBA": "#21304a"}, "short": {"Outside DHS and NARA": "with VBA", "Also without VBA": "without VBA"}},
                 {"title": "Requests whose records were reviewed, share of all closed (without VBA)", "series": {"Reviewed": lst(rs_v)},
                  "colors": {"Reviewed": "#0b5a36"}}],
      "tables": [{"title": "Splitting the fall in the full-release share, without VBA (percentage points)",
                  "head": ["", "Total change", "From the reviewed share", "From released among reviewed"],
                  "rows": [["FY2008 → FY2017", sg(a[0], 2), sg(a[1], 2), sg(a[2], 2)], ["FY2017 → FY2025", sg(b[0], 2), sg(b[1], 2), sg(b[2], 2)]]}]}

    # ======================= step 8: agencies' own shares (section 6) =======================
    def rates(y, key=AGK):
        n, d = counts(y, [FG], noDN, key); return n, {k: v for k, v in d.items() if v}
    def decompose(y0, y1):
        (a0, d0), (a1, d1) = rates(y0), rates(y1); D0, D1 = sum(d0.values()), sum(d1.values())
        ks = [k for k in d0 if k in d1]; dr = {k: a1.get(k, 0) / d1[k] - a0.get(k, 0) / d0[k] for k in ks}
        ws = sum(d0[k] / D0 * dr[k] for k in ks) * 100; we = sum(d1[k] / D1 * dr[k] for k in ks) * 100
        per = {k: dr[k] * (d0[k] / D0 + d1[k] / D1) / 2 * 100 for k in ks}
        return (sum(a1.values()) / D1 - sum(a0.values()) / D0) * 100, ws, we, (ws + we) / 2, per
    T1, s1_, e1, m1, p1 = decompose(2008, 2017); T2, s2_, e2, m2, p2 = decompose(2017, 2025)
    assert [r2(x) for x in (T1, s1_, e1, m1)] == [-11.97, -14.31, -5.89, -10.10] and [r2(x) for x in (T2, s2_, e2, m2)] == [-16.57, -13.85, -13.13, -13.49]
    A1 = ["VA", "HHS", "SSA", "DOJ", "DOT"]; A2 = ["VA", "DoD", "DOT", "DOJ", "HHS", "USDA"]
    assert [r2(p1[k]) for k in A1] == [-4.26, -3.52, -2.33, 1.71, 0.46] and [r2(p2[k]) for k in A2] == [-2.59, -2.49, -1.13, -1.05, -1.05, -0.85]
    def fell(y0, y1, th, key=AGK):
        (a0, d0), (a1, d1) = rates(y0, key), rates(y1, key)
        ks = [k for k in d0 if k in d1 and d0[k] >= th and d1[k] >= th]; dec = [k for k in ks if a1.get(k, 0) / d1[k] < a0.get(k, 0) / d0[k]]
        return len(dec), len(ks), 100 * sum(d1[k] for k in dec) / sum(d1[k] for k in ks)
    fa = {th: fell(2017, 2025, th) for th in (1, 10, 100, 1000)}
    assert fa[1][:2] == (87, 107) and fa[1000][:2] == (24, 26) and (round(min(v[2] for v in fa.values())), round(max(v[2] for v in fa.values()))) == (96, 97)
    fc1, fc1000 = fell(2017, 2025, 1, COK), fell(2017, 2025, 1000, COK)
    assert fc1[:2] == (278, 340) and fc1000[:2] == (40, 47)
    doj = {y: counts(y, [FG], lambda r: AGK(r) == "DOJ")[0:2] for y in (2008, 2025)}
    def dojsh(y):
        n, d = doj[y]; e = "DOJ/EOIR"; return (100 * d[e] / sum(d.values()), 100 * n[e] / d[e],
                                              100 * (sum(n.values()) - n[e]) / (sum(d.values()) - d[e]), 100 * sum(n.values()) / sum(d.values()))
    j8, j25 = dojsh(2008), dojsh(2025)
    assert [r1(x) for x in j8] == [22.2, 71.3, 23.2, 33.9] and [r1(x) for x in j25] == [63.3, 56.9, 8.8, 39.3]
    step8 = {"kicker": "Outside DHS and NARA · by agency", "title": "The fall comes mostly from agencies' own shares, and most agencies fell",
      "sections": [
        {"h": "What we looked at", "p": [
          "Step 3 split the national fall between DHS and the rest. Here the same split is done agency by agency outside DHS and NARA: did "
          "agencies' own full-release shares fall, or did requests shift toward agencies that release less in full?",
          "Within-agency change = each agency's change in its own share × its weight (its share of all closed requests), added up. The rest "
          "is the remainder: shifts in weight, and agencies with data in only one of the two years."]},
        {"h": "What we found", "p": [
          f"FY2017–25: the share fell {f2(-T2)} points. The within-agency change is {f2(-e2)} to {f2(-s2_)} points depending on which year's "
          f"weights are used ({f2(-m2)} on average), so most of the fall is agencies' own shares.",
          f"FY2008–17: the share fell {f2(-T1)} points; the within-agency change is {f2(-e1)} to {f2(-s1_)} ({f2(-m1)} on average). The range "
          "is wide because VA and HHS both fell and shrank (VA's weight 21.6% to 6.4%, HHS's 14.6% to 8.8%), and 26 agencies are missing from the FY2008 data."]},
        {"h": "Who drove it", "p": [
          "FY2008–17 is concentrated in VA, HHS and SSA. FY2017–25 is broader: VA, DoD, DOT, DOJ, HHS and USDA all fell (charts, average weights)."]},
        {"h": "How many agencies fell", "p": [
          f"FY2017–25: {fa[1][0]} of the {fa[1][1]} agencies with data in both years released in full less often ({round(100 * fa[1][0] / fa[1][1])}%); "
          f"among agencies with 1,000 or more closed requests, {fa[1000][0]} of {fa[1000][1]} ({round(100 * fa[1000][0] / fa[1000][1])}%). "
          f"The agencies that fell handled 96%–97% of these agencies' FY2025 requests, whatever the size cut-off. By component: {fc1[0]} of {fc1[1]} ({round(100 * fc1[0] / fc1[1])}%)."]},
        {"h": "The exception: DOJ", "p": [
          f"DOJ's share rose over FY2008–25 ({f(j8[3])}% to {f(j25[3])}%) although both its parts fell: EOIR {f(j8[1])}% to {f(j25[1])}%, the rest "
          f"of DOJ {f(j8[2])}% to {f(j25[2])}%. EOIR, which releases in full often, grew from {f(j8[0])}% to {f(j25[0])}% of DOJ's requests. "
          "This is a Simpson's paradox: the total moves opposite to every part."]}],
      "method": "Composition decomposition by agency (Kitagawa 1955), with start-year, end-year or average weights. Agency counts compare "
                "each agency's own share in the two years; an agency at the same share in both years is not counted as falling.",
      "charts": [{"kind": "dbars", "digits": 2, "title": "FY2017–25: within-agency change by agency (points, average weights)",
                  "bars": [{"name": k, "v": r2(p2[k])} for k in A2] + [{"name": "All other agencies", "v": r2(m2 - sum(p2[k] for k in A2))}]},
                 {"kind": "dbars", "digits": 2, "title": "FY2008–17: within-agency change by agency (points, average weights)",
                  "bars": [{"name": k, "v": r2(p1[k])} for k in A1] + [{"name": "All other agencies", "v": r2(m1 - sum(p1[k] for k in A1))}]}],
      "tables": [{"title": "Splitting the fall: agencies' own shares and the remainder (points)",
                  "head": ["", "Total", "Within agencies (start-year weights)", "End-year weights", "Average"],
                  "rows": [["FY2008 → FY2017", sg(T1, 2), sg(s1_, 2), sg(e1, 2), sg(m1, 2)], ["FY2017 → FY2025", sg(T2, 2), sg(s2_, 2), sg(e2, 2), sg(m2, 2)]]}]}

    # ======================= step 9: single-unit removal (section 7) =======================
    units_by_ag = defaultdict(set)
    for r in G:
        if noDN(r): units_by_ag[AGK(r)].add(COK(r))
    dup = {("co", next(iter(s))) for s in units_by_ag.values() if len(s) == 1}
    assert len(units_by_ag) == 126 and len(dup) == 95 and sum(len(s) for s in units_by_ag.values() if len(s) > 1) == 445
    def removals(cols):
        res = paired(cols, c02, noDN); base = res.pop("Baseline")
        return base, {k: v for k, v in res.items() if k not in dup}
    bF, rF = removals([FG]); bP, rP = removals([PG]); bN, rN = removals([NR])
    assert len(rF) == 571
    per = {"FY2008–17": (2008, 2017), "FY2017–25": (2017, 2025), "FY2008–25": (2008, 2025)}
    rows = []
    for lab, (y0, y1) in per.items():
        ch_ = {k: s[y1] - s[y0] for k, s in rF.items()}; lo_k, hi_k = min(ch_, key=ch_.get), max(ch_, key=ch_.get)
        assert ch_[hi_k] < 0
        rows.append({"name": lab, "base": r1(bF[y1] - bF[y0]), "lo": r1(ch_[lo_k]), "hi": r1(ch_[hi_k]), "loU": lo_k, "hiU": hi_k})
    assert [(x["base"], x["hi"]) for x in rows] == [(-12.0, -8.0), (-16.6, -12.7), (-28.5, -23.1)]
    assert [x["hiU"] for x in rows] == [("co", "HHS/CMS"), ("co", "VA/VBA"), ("ag", "VA")] and (rows[2]["lo"], rows[2]["loU"]) == (-36.7, ("ag", "DOJ"))
    e_ch = rF[("co", "DOJ/EOIR")][2025] - rF[("co", "DOJ/EOIR")][2008]; assert r1(e_ch) == -34.3
    assert r1(min(s[2008] - s[2024] for s in rF.values())) == 19.6
    pch = {k: s[2017] - s[2008] for k, s in rP.items()}; assert r1(min(pch.values())) == 9.9 and min(pch, key=pch.get) == ("ag", "VA")
    nch = [s[2025] - s[2008] for s in rN.values()]; assert (r1(min(nch)), r1(max(nch)), r1(bN[2025] - bN[2008])) == (-2.9, 1.0, -1.2)
    es = {y: 100 * disp(y, isEOIR) / disp(y, noDN) for y in YR}; assert (r1(es[2008]), r1(es[2023]), r1(es[2025])) == (3.0, 21.9, 15.3)
    cE = contributions([FG], 2022, 2023, no_vba); assert r1(cE["DOJ/EOIR"]) == 7.7
    always = None
    for y in YR:
        _, d = rates(y); ks = set(d); always = ks if always is None else always & ks
    assert len(always) == 67
    inlist = lambda r: noDN(r) and AGK(r) in always
    f67 = series([FG], c02, inlist); assert [r1(f67[y]) for y in (2008, 2017, 2025)] == [50.0, 37.5, 20.7]
    cov = [100 * disp(y, inlist) / disp(y, noDN) for y in range(2010, 2026)]; assert (r1(min(cov)), r1(max(cov))) == (83.5, 90.6)
    nm = {("co", "HHS/CMS"): "without HHS's CMS", ("co", "VA/VBA"): "without VBA", ("ag", "VA"): "without all of VA", ("ag", "DOJ"): "without all of DOJ"}
    lab = lambda k: nm.get(k, "without " + k[1])
    step9 = {"kicker": "Outside DHS and NARA · checks", "title": "Leave out any one of 571 agencies or components, and full releases still fall",
      "sections": [
        {"h": "What we looked at", "p": [
          "Earlier steps followed oddities as they appeared (NARA, the FY2018 rise, VBA, EOIR). This step checks them all at once: remove "
          "one agency or one component from every year (571 removals: 126 agencies and 445 components; an agency with no components counts "
          "once) and recompute each period's change."]},
        {"h": "What we found", "p": [
          f"Released in full falls in every period under every removal. The smallest falls: {f(rows[0]['hi'])} points in FY2008–17 "
          f"({lab(rows[0]['hiU'])}), {f(rows[1]['hi'])} in FY2017–25 ({lab(rows[1]['hiU'])}), {f(rows[2]['hi'])} over FY2008–25 "
          f"({lab(rows[2]['hiU'])}). With FY2024 as the end year, it still falls at least 19.6 points.".replace("-", "−"),
          "Partly released: the FY2008–17 rise holds under every removal (at least +9.9 points). No records found: the FY2008–25 change "
          "stays between −2.9 and +1.0 points, nothing like the fall in full releases."]},
        {"h": "One unit pulls the other way: EOIR", "p": [
          f"The biggest falls come from removing all of DOJ ({f(rows[2]['lo'])} points) or its EOIR, the immigration courts ({f(e_ch)}), "
          f"both larger than the {f(rows[2]['base'])} with no removal. EOIR releases in full often and grew from {f(es[2008])}% of requests "
          f"closed outside DHS and NARA in FY2008 to {f(es[2023])}% in FY2023, which props up the total. The FY2018 rise (EOIR "
          f"{sg(c18['DOJ/EOIR'], 2)} points) and a FY2023 rise when VBA is left out (EOIR +{f(cE['DOJ/EOIR'])}) both came in years when EOIR's volume jumped.".replace("-", "−")]},
        {"h": "A fixed list of agencies", "p": [
          f"Using only the {len(always)} agencies with data in all 18 years: {f(f67[2008])}%, {f(f67[2017])}% and {f(f67[2025])}% in FY2008, "
          f"FY2017 and FY2025, almost the same as 50.0%, 38.0% and 21.4% for all agencies. They hold {f(min(cov))}%–{f(max(cov))}% of "
          "closed requests each year from FY2010. The changing list of agencies does not drive the finding."]}],
      "method": "One unit removed at a time, from all years. VBA and EOIR were also removed together; other combinations of several "
                "units were not tested. These are descriptive checks, not causal identification.",
      "charts": [{"kind": "ranges", "title": "Change in the full-release share after each of the 571 removals (points)",
                  "rows": [{"name": x["name"], "base": x["base"], "lo": x["lo"], "hi": x["hi"], "hiLabel": lab(x["hiU"])} for x in rows]},
                 {"title": "Released in full, share of closed requests", "series": {"All agencies outside DHS and NARA": lst(fn), f"The {len(always)} agencies in all 18 years": lst(f67)},
                  "colors": {"All agencies outside DHS and NARA": "#4582cc", f"The {len(always)} agencies in all 18 years": "#21304a"},
                  "dashed": [f"The {len(always)} agencies in all 18 years"], "short": {"All agencies outside DHS and NARA": "all", f"The {len(always)} agencies in all 18 years": f"{len(always)} agencies"}}]}

    # ======================= step 10: the finding (section 8) =======================
    step10 = {"kicker": "The finding", "title": "A shrinking share of requests is released in full",
      "sections": [
        {"h": "In one sentence", "p": [
          "Outside DHS and NARA, full releases fell from 50.0% of closed requests in FY2008 to 21.4% in FY2025. The fall remains after "
          "removing any single agency or component, and it comes mainly from agencies' own full-release shares falling, not from a shift "
          "in which agencies handle requests."]},
        {"h": "In more detail", "p": [
          "Nationally the share fell 32.1 points; about 11.7 of them only reflect DHS closing more of the requests (step 3).",
          f"It falls in both periods: {f(rows[0]['base'])} points in FY2008–17 and {f(rows[1]['base'])} in FY2017–25, and at least "
          f"{f(-rows[0]['hi'])} and {f(-rows[1]['hi'])} after any single removal (step 9).".replace("-", "−"),
          f"Most agencies fell: in FY2017–25, {fa[1][0]} of {fa[1][1]} agencies released in full less often, and they handled 96%–97% of these agencies' requests (step 8).",
          "What replaced full releases differs by period: partial releases in FY2008–17; in FY2017–25 the rise in partial releases is VBA, "
          "and without VBA most of the fall (8.74 of 12.74 points) is more requests closed without records processed (steps 6–7).",
          "No records found did not rise with it: −1.2 points over FY2008–25 (step 5)."]},
        {"h": "What not to say", "p": [
          "That the whole national decline is agencies releasing less: about 11.7 points reflect DHS's growing weight.",
          "That partial releases have been rising lately, without mentioning VBA.",
          "That the recent fall is all “agencies released less of what they reviewed”: without VBA, most of it is requests closed without records processed.",
          "Any cause. The reports show that agencies' own shares fell, not whether request types, exemption use or reporting practice changed."]},
        {"h": "Leads to follow up separately", "p": [
          "DHS's rising no-records share, mainly CBP and USCIS · NARA's swings between categories · VBA's switch to partial releases from "
          "FY2023 · EOIR's growing weight · the broad rise in other closures without VBA in FY2017–25."]}],
      "method": "Annual totals reported by the agencies themselves; they do not follow individual requests or count pages released. 26 "
                "agencies are missing from the FY2008 data; FY2025 has no later report to compare with yet. Full analysis: Storyline 1 notebook.",
      "charts": [{"title": "Share of closed requests, outside DHS and NARA", "series": {k: lst(m[k]) for k in ("Released in full", "Partly released", "No records found")}}]}
    return [step4, step5, step6, step7, step8, step9, step10]
