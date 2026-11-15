"""Storyline 4 (backlog) walkthrough, from the final notebook S4-backlog-outside-immigration-en (11/12). Series recomputed with
storyline_lib and anchored to the notebook's assertions; every number in the text is checked against the notebook text."""
from collections import defaultdict
from storyline_lib import G, YR, REC, PRO, BLR, col, tot, bykey, series as _series, ni, vba, AGK, backlog_revisions
from walk_common import check_numbers

r0 = lambda v: int(round(v)); r1 = lambda v: round(float(v), 1)
S = lambda *a: {int(k): float(v) for k, v in _series(*a).items()}
imm = lambda r: not ni(r)
isNARA = lambda r: AGK(r) == "NARA"; isPRIV = lambda r: AGK(r) == "DHS" and r["Component"] == "PRIV"

def build():
    PEND = col("01", "PendingAtEnd")
    counts = {y: tot(G, BLR, y) for y in YR}; assert r0(counts[2025]) == 339756
    scopes = {"All agencies": S([BLR], [REC]), "Four units": S([BLR], [REC], imm), "Outside the four units": S([BLR], [REC], ni)}
    m = lambda s, a, b: sum(s[y] for y in range(a, b + 1)) / (b - a + 1)
    assert [[r1(m(s, 2014, 2019)), r1(m(s, 2020, 2025))] for s in scopes.values()] == [[15.7, 18.8], [14.2, 12.8], [16.9, 26.0]]
    out = scopes["Outside the four units"]
    assert [r1(out[y]) for y in YR] == [12.9, 14.5, 13.1, 9.4, 10.6, 10.5, 15.2, 18.0, 16.9, 15.8, 17.1, 18.7, 27.6, 25.9, 27.8, 23.2, 21.9, 29.9]
    stages = [(2008, 2010), (2011, 2013), (2014, 2019), (2020, 2025)]
    assert [r1(m(out, a, b)) for a, b in stages] == [13.5, 10.1, 16.9, 26.0]
    nodos = S([BLR], [REC], lambda r: ni(r) and AGK(r) != "DOS"); assert [r1(nodos[y]) for y in (2019, 2020)] == [16.5, 24.5]
    def pooled_by_agency(a, b):
        bl, rc, n = defaultdict(float), defaultdict(float), defaultdict(int)
        for y in range(a, b + 1):
            r_y, b_y = bykey(y, REC, ni, AGK), bykey(y, BLR, ni, AGK)
            for k, v in r_y.items(): rc[k] += v; bl[k] += b_y.get(k, 0); n[k] += 1
        return {k: (100 * bl[k] / rc[k], rc[k]) for k in rc if n[k] == b - a + 1 and rc[k] > 0}
    p0, p1 = pooled_by_agency(2014, 2019), pooled_by_agency(2020, 2025)
    br = []
    for th in (0, 600, 6000, 60000):
        ks = [k for k in p0 if k in p1 and p0[k][1] >= th and p1[k][1] >= th]; br.append((th, len(ks), sum(p1[k][0] > p0[k][0] for k in ks)))
    assert [[n, u] for _, n, u in br] == [[96, 69], [56, 42], [28, 24], [14, 11]]
    top = sorted([k for k in p0 if k in p1], key=lambda k: -p1[k][1])[:14]
    nm = {"DHS": "DHS (other components)", "DOJ": "DOJ (excl. EOIR)"}
    assert [r1(p0["DOS"][0]), r1(p1["DOS"][0])] == [90.4, 116.2] and {k for k in top if p1[k][0] < p0[k][0]} == {"DHS", "VA", "EEOC"}
    pops = {"Outside the four units": ni, "Also without VBA and DHS PRIV": lambda r: ni(r) and not vba(r) and not isPRIV(r),
            "Also without VBA, DHS PRIV, DOS and NARA": lambda r: ni(r) and not vba(r) and not isPRIV(r) and AGK(r) not in ("DOS", "NARA")}
    alt = {k: S([BLR], [REC], f) for k, f in pops.items()}
    assert r1(min(alt["Also without VBA and DHS PRIV"][y] for y in range(2020, 2026))) == 27.6 and r1(m(alt["Also without VBA and DHS PRIV"], 2020, 2025) - m(alt["Also without VBA and DHS PRIV"], 2014, 2019)) == 14.1
    d = lambda f: tot(G, REC, 2020, f) - tot(G, REC, 2019, f)
    drop = [d(ni), d(isNARA), d(isPRIV)]; assert [r0(x) for x in drop] == [-77712, -41728, -18903]
    PERF = [c for c in G[0] if c[:3] in ("16_", "17_", "18_") and "TimeIncrementProcessedQuantity[" in c]
    second = {"Backlog ÷ receipts": out, "Pending at year end ÷ receipts": S([PEND], [REC], ni), "Backlog ÷ processed": S([BLR], [PRO], ni), "Backlog ÷ perfected processed": S([BLR], PERF, ni)}
    assert [r1(second["Pending at year end ÷ receipts"][y]) for y in (2013, 2019, 2020, 2025)] == [15.0, 25.1, 35.1, 37.8]
    bp = second["Backlog ÷ perfected processed"]; assert [r1(m(bp, 2014, 2019)), r1(m(bp, 2020, 2025))] == [18.2, 30.0]
    _, revised = backlog_revisions()
    rv = {c: {int(y): float(v) for y, v in revised[c].items()} for c in revised.columns}
    assert [[r1(rv[c][y]) for c in revised.columns] for y in (2015, 2021, 2023)] == [[18.0, 14.9, 15.0], [25.9, 27.5, 27.4], [23.2, 25.1, 24.7]]
    cbp = lambda r: AGK(r) == "DHS" and r["Component"] == "CBP"; dosm = lambda r: AGK(r) == "DOS" and r["Component"] == "DOS - Main"
    where = [("DHS CBP", tot(G, BLR, 2025, cbp)), ("DHS PRIV", tot(G, BLR, 2025, isPRIV)), ("DOS Main", tot(G, BLR, 2025, dosm))]
    assert [r0(v) for _, v in where] == [96303, 48433, 22678]
    P = lambda s: [r1(s[y]) for y in YR]
    segs = [{"from": a, "to": b, "v": r1(m(out, a, b))} for a, b in stages[1:]]
    cover_chart = {"title": "Backlog ÷ receipts", "series": {"Outside the four units": P(out), "All agencies": P(scopes["All agencies"])},
                   "colors": {"Outside the four units": "#4582cc", "All agencies": "#8a8f98"}, "dashed": ["All agencies"],
                   "short": {"Outside the four units": "outside", "All agencies": "all"}, "segs": segs}
    walk = {"id": "s4", "name": "Backlog",
      "cover": {"kicker": "Backlog", "title": "Outside four immigration-related units, backlog has risen in stages",
        "body": "Outside USCIS, CBP, ICE and EOIR, year-end backlog relative to annual receipts climbed from about 10% in FY2011–13 to 26.0% in FY2020–25. The FY2020–25 average is 9.1 points above FY2014–19, and at least 8.0 after removing any single unit. 69 of 96 agencies rose.",
        "foot": "Year-end backlog (Table 26) ÷ requests received that year (Table 01). Dotted lines: period averages. The government-wide ratio (dashed) rose only about 3 points.", "chart": cover_chart},
      "steps": [
        {"kicker": "All agencies", "title": "Backlog counts rise, but the ratio goes up and down",
         "sections": [
           {"h": "What we looked at", "p": ["Backlog is requests still open at year end past the legal deadline (Table 26). The ratio sets that year-end stock beside the year's receipts; it is not the chance that a request became backlogged."]},
           {"h": "What the charts show", "p": ["The government-wide backlog count rises overall (339,756 in FY2025), but backlog ÷ receipts goes up and down. A unit with very large receipts weighs heavily in the denominator, so the next step separates units."]}],
         "method": "Backlog: Table 26. Receipts: requests received, Table 01.",
         "charts": [{"title": "Backlogged requests, all agencies", "unit": "count", "series": {"Backlog": [r0(counts[y]) for y in YR]}, "colors": {"Backlog": "#21304a"}},
                    {"title": "Backlog ÷ receipts, all agencies", "series": {"All agencies": P(scopes["All agencies"])}, "colors": {"All agencies": "#4582cc"}}]},
        {"kicker": "All agencies · four units", "title": "Why the government-wide ratio barely moves",
         "sections": [
           {"h": "What we looked at", "p": ["The four units (USCIS, CBP, ICE and EOIR) receive a growing share of requests: 19.7% in FY2008, 47.3% in FY2019 and 56.4% in FY2025. Their backlog follows a different path."]},
           {"h": "What the chart shows", "p": [
             "Six-year averages: all agencies 15.7% to 18.8% (+3.1 points); the four units 14.2% to 12.8% (−1.4); outside the four units 16.9% to 26.0% (+9.1)."]},
           {"h": "Why the total rose only about 3 points", "p": [
             "Outside the four units the ratio rose 9.08 points, but those units hold only 50.1% of receipts, so they add +4.55; the four units' own ratio fell slightly (−0.39); their growing share of receipts pulled the total down by 0.92; total +3.24 (table). From here on, look outside the four units."]}],
         "method": "Six-year totals of backlog and receipts are divided for the split, so it differs slightly from the yearly averages.",
         "charts": [{"title": "Backlog ÷ receipts", "series": {k: P(v) for k, v in scopes.items()}, "colors": {"All agencies": "#9aa3ae", "Four units": "#8c3a91", "Outside the four units": "#4582cc"},
                     "dashed": ["All agencies"], "short": {"All agencies": "all", "Four units": "four units", "Outside the four units": "outside"}}],
         "tables": [{"title": "FY2014–19 to FY2020–25: where the +3.24 points come from", "head": ["Part", "Points"],
                     "rows": [["The rest: own change × its share of receipts", "+4.55"], ["The four units: own change × their share", "−0.39"], ["The four units' growing share of receipts", "−0.92"], ["Total", "+3.24"]]}]},
        {"kicker": "Outside the four units", "title": "A rise in stages since FY2013, steepest in FY2020",
         "sections": [
           {"h": "What we looked at", "p": ["Backlog ÷ receipts outside the four units, with each period's average (dotted lines), and a second line without DOS, which added the most backlog."]},
           {"h": "What the chart shows", "p": [
             "Averages: 13.5% in FY2008–10, 10.1% in FY2011–13, 16.9% in FY2014–19 and 26.0% in FY2020–25. It climbed in stages, with five down years out of twelve; the largest single-year rises are FY2020 (+8.9), FY2025 (+8.0) and FY2014 (+4.7).",
             "From FY2013 to FY2019 it had already risen 8.2 points, so FY2020 is not presented as a break. Without DOS the ratio still rises from 16.5% in FY2019 to 24.5% in FY2020 and stays higher."]},
           {"h": "A caution about FY2008–09", "p": ["27 agencies have receipts in FY2010 but none in FY2008, so the rise is safer to state from FY2011–13."]}],
         "method": "Averages of the yearly ratios.",
         "charts": [{"title": "Backlog ÷ receipts outside the four units", "series": {"Outside the four units": P(out), "Also without DOS": P(nodos)},
                     "colors": {"Outside the four units": "#4582cc", "Also without DOS": "#21304a"}, "dashed": ["Also without DOS"], "short": {"Outside the four units": "outside", "Also without DOS": "without DOS"}, "segs": segs}]},
        {"kicker": "By agency", "title": "Broad: 69 of 96 agencies rose, mainly within agencies",
         "sections": [
           {"h": "What we looked at", "p": ["The 96 agencies with data in every year FY2014–25 (99.8% of FY2020–25 receipts outside the four units); six-year totals of backlog and receipts, FY2014–19 against FY2020–25."]},
           {"h": "What the chart shows", "p": [
             "69 of 96 agencies rose (72%), 24 of the 28 with at least 6,000 receipts in each window (86%). Split by agency, the within-agency change is +9.20 on average of the +9.03 total.",
             "The large traditional departments all rose: DoD 18.2% to 34.4%, DOJ (excluding EOIR) 29.8% to 49.9%, HHS 15.9% to 27.7%, DOT 19.9% to 37.6%, DOS 90.4% to 116.2%. DOS's backlog now exceeds a year of its receipts.",
             "Three large ones fell: DHS's other components (a mix effect from PRIV and CISA), VA (mainly VBA: 36.9% to 3.1%) and EEOC."]}],
         "method": "Hollow dot: FY2014–19; filled dot: FY2020–25. DHS and DOJ here exclude the four units.",
         "charts": [{"kind": "dumbbell", "title": "The 14 agencies with the most receipts outside the four units (backlog ÷ receipts)", "keys": ["FY2014–19", "FY2020–25"],
                     "rows": [{"name": nm.get(k, k), "v": [r1(p0[k][0]), r1(p1[k][0])]} for k in top]}],
         "tables": [{"title": "Agencies whose ratio rose", "head": ["Minimum receipts in each six-year window", "Agencies compared", "Ratio higher in FY2020–25"],
                     "rows": [[f"{th:,}", str(n), str(u)] for th, n, u in br]}]},
        {"kicker": "Outside the four units", "title": "The FY2020 jump and the FY2023–24 dip come from a few units' receipts",
         "sections": [
           {"h": "The FY2020 jump", "p": [
             "Receipts fell from 452,915 to 375,203 (−17.2%) while backlog rose from 84,549 to 103,458 (+22.4%). Of the 77,712 drop in receipts, NARA accounts for 41,728 and DHS PRIV for 18,903, 78% together; the rise in backlog is spread out (DHS's other components +4,247, DoD +2,802, DOS +2,692, DOJ +2,607)."]},
           {"h": "The FY2023–24 dip", "p": [
             "VBA and PRIV received many more requests while carrying little backlog, which enlarged the denominator. Without these two units the ratio is 27.6% or higher in every year from FY2020, with no dip; the FY2020–25 average is 14.1 points above FY2014–19."]},
           {"h": "A sensitivity check only", "p": ["The main population does not change: choosing units to remove after seeing the results would be choosing data for the conclusion. The check shows that the 9.1 points is conservative."]}],
         "method": "Same ratio, with units whose receipts swing sharply left out.",
         "charts": [{"title": "Backlog ÷ receipts, removing units with large swings in receipts", "series": {k: P(v) for k, v in alt.items()},
                     "colors": {"Outside the four units": "#4582cc", "Also without VBA and DHS PRIV": "#8c3a91", "Also without VBA, DHS PRIV, DOS and NARA": "#21304a"},
                     "short": {"Outside the four units": "outside", "Also without VBA and DHS PRIV": "w/o VBA, PRIV", "Also without VBA, DHS PRIV, DOS and NARA": "also w/o DOS, NARA"}}]},
        {"kicker": "Outside the four units", "title": "A second measure agrees, and the backlog definition has not drifted",
         "sections": [
           {"h": "What we looked at", "p": ["Requests pending at year end (Table 01) count every open request regardless of the deadline, so they avoid differences in how agencies apply deadlines."]},
           {"h": "What the chart shows", "p": [
             "Pending at year end ÷ receipts moves the same way: 15.0% in FY2013, 25.1% in FY2019, 35.1% in FY2020 and 37.8% in FY2025. Backlog as a share of pending stays between 69.4% and 81.2% in all 18 years, so the rise is not a change in how backlog is counted.",
             "On a denominator of perfected requests only, the increase is larger: 18.2% to 30.0%, 11.8 points. The 9.1 points is therefore conservative."]}],
         "method": "Perfected requests processed: Tables 16–18. Only perfected requests can be backlogged.",
         "charts": [{"title": "Outside the four units: four ratios", "series": {k: P(v) for k, v in second.items()},
                     "colors": {"Backlog ÷ receipts": "#4582cc", "Pending at year end ÷ receipts": "#8c3a91", "Backlog ÷ processed": "#d4a92c", "Backlog ÷ perfected processed": "#0b5a36"},
                     "short": {"Backlog ÷ receipts": "backlog/receipts", "Pending at year end ÷ receipts": "pending/receipts", "Backlog ÷ processed": "backlog/processed", "Backlog ÷ perfected processed": "backlog/perfected"}}]},
        {"kicker": "Checks", "title": "9.1 points higher, at least 8.0 after removing any single unit",
         "sections": [
           {"h": "What we found", "p": [
             "The FY2020–25 average is 9.1 points above FY2014–19 (16.9% to 26.0%, about 1.5 times). After removing any single unit (590 removals) it is at least 8.0; without FY2025 it is 8.3, and at least 7.0.",
             "“Every year from FY2020 is above every earlier year” has a margin of only 0.8 points at its tightest (removing NARA), so the finding uses the average difference instead."]},
           {"h": "When the following year's report differs", "p": [
             "The next year's report repeats the prior year's backlog and receipts; by rule they should be identical. Seven matched backlog figures differ by 500 or more. Using them instead, the gap is 10.01 (backlog replaced) or 9.82 (backlog and receipts replaced): slightly larger. In three cases the replacement equals the unit's pending requests at the start of the next year, so these are only a reference."]}],
         "method": "One unit removed at a time, from all years; agencies without components count once.",
         "charts": [{"title": "Backlog ÷ receipts outside the four units, with following-year figures", "series": {"As reported": P(rv["Original"]), "Backlog replaced": P(rv["Revised backlog"]), "Backlog and receipts replaced": P(rv["Revised backlog and receipts"])},
                     "colors": {"As reported": "#4582cc", "Backlog replaced": "#d4a92c", "Backlog and receipts replaced": "#8c3a91"}, "dashed": ["Backlog and receipts replaced"],
                     "short": {"As reported": "as reported", "Backlog replaced": "backlog repl.", "Backlog and receipts replaced": "both repl."}}]},
        {"kicker": "All agencies", "title": "Almost half of the FY2025 backlog is at three units",
         "sections": [
           {"h": "What the chart shows", "p": [
             "Government-wide backlog in FY2025 is 339,756: CBP 96,303 (28.3%), PRIV 48,433 (14.3%) and DOS Main 22,678 (6.7%), together 49.3%. Outside the four units holds 65.6% of the backlog and 43.6% of receipts."]},
           {"h": "Why the four units are not the main story", "p": [
             "Their own ratio swings widely (65.7% in FY2008, 8.8% in FY2019). CBP's backlog went from 21,444 in FY2023 to 110,271 in FY2024; USCIS's from 20,344 in FY2020 to 1,599 in FY2021."]},
           {"h": "FY2025 on its own", "p": ["Backlog outside the four units rose by 87,290 in one year, 44,359 of it at PRIV; FY2025 has no following-year report to check against yet."]}],
         "method": "FY2025 year-end backlog (Table 26).",
         "charts": [{"kind": "dbars", "fmt": "count", "title": "Backlogged requests, FY2025", "bars": [{"name": k, "v": r0(v)} for k, v in where] + [{"name": "All other units", "v": r0(counts[2025] - sum(v for _, v in where))}]}]},
        {"kicker": "The finding", "title": "Outside four immigration-related units, backlog has risen in stages",
         "sections": [
           {"h": "In one sentence", "p": ["Outside USCIS, CBP, ICE and EOIR, year-end backlog relative to annual receipts climbed from about 10% in FY2011–13 to 26.0% in FY2020–25; the FY2020–25 average is 9.1 points above FY2014–19, and at least 8.0 after removing any single unit. The rise is mainly within agencies and broad. The government-wide ratio rose only about 3 points because the four units have low ratios and a growing share of receipts."]},
           {"h": "What not to say", "p": [
             "That backlog pressure is flat government-wide, without the split.",
             "That FY2020 was a break caused by a single event: the ratio had already risen 8.2 points from FY2013 to FY2019.",
             "That the lower FY2023–24 values mean relief: they reflect larger receipts at VBA and PRIV.",
             "That this population is “non-immigration requests”: it is a grouping of units, not of request topics."]},
           {"h": "Leads to follow up", "p": ["DOS: 90.4% to 116.2%, more than a year of receipts · DOJ (excluding EOIR): 29.8% to 49.9% · PRIV's FY2025 backlog, 4,074 to 48,433."]}],
         "method": "Annual totals reported by the agencies themselves; the reports do not show causes. Full analysis: Storyline 4 notebook.",
         "charts": [cover_chart]}]}
    check_numbers(walk, "S4-backlog-outside-immigration-en", allow=(14, 2025, 2008, 600, 60000))
    return walk
