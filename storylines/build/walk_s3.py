"""Storyline 3 (appeals) walkthrough, from the final notebook S3-appeals-en (11/12). Series recomputed with storyline_lib and
anchored to the notebook's assertions; every number in the text is checked against the notebook text."""
from collections import defaultdict
from storyline_lib import G, YR, AR, PRO, RV, PA, T8, OT, col, tot, series as _series, isD, noD, AGK, num
from walk_common import check_numbers

r0 = lambda v: int(round(v)); r1 = lambda v: round(float(v), 1); r2 = lambda v: round(float(v), 2)
S = lambda *a: {int(k): float(v) for k, v in _series(*a).items()}
dhs_c = lambda u: (lambda r: AGK(r) == "DHS" and r["Component"] == u)

def build():
    AF, APE = col("08", "Affirmed"), col("07", "PendingAtEnd")
    per = {"All government": S([AR], [PRO]), "DHS": S([AR], [PRO], isD), "Outside DHS": S([AR], [PRO], noD)}
    assert [r2(per["All government"][y]) for y in (2023, 2024, 2025)] == [1.29, 1.34, 1.96] and (r2(min(per["All government"].values())), r2(max(per["All government"].values()))) == (1.29, 1.99)
    rates = {"All agencies": S([RV, PA], [T8]), "DHS": S([RV, PA], [T8], isD), "Outside DHS": S([RV, PA], [T8], noD)}
    assert (r1(min(rates["Outside DHS"].values())), r1(max(rates["Outside DHS"].values()))) == (20.6, 27.3) and [r1(rates["DHS"][y]) for y in (2008, 2024, 2025)] == [26.6, 39.0, 36.7]
    dw = {y: 100 * tot(G, T8, y, isD) / tot(G, T8, y) for y in YR}; assert [r1(dw[y]) for y in (2008, 2025)] == [25.3, 55.0]
    mix = {"Affirmed": S([AF], [T8], isD), "Partly reversed": S([PA], [T8], isD), "Completely reversed": S([RV], [T8], isD), "Other closures": S([OT], [T8], isD)}
    assert [r1(mix["Other closures"][y]) for y in (2023, 2024, 2025)] == [17.8, 36.9, 43.3] and [r1(mix["Affirmed"][y]) for y in (2023, 2024, 2025)] == [33.8, 24.1, 20.0]
    M = [AF, PA, RV]
    merit = {"DHS": S([RV, PA], M, isD), "Outside DHS": S([RV, PA], M, noD), "Outside DHS and DOJ": S([RV, PA], M, lambda r: noD(r) and AGK(r) != "DOJ")}
    assert [r1(merit["DHS"][y]) for y in (2023, 2024, 2025)] == [58.8, 61.8, 64.8]
    agg = defaultdict(lambda: [0.0, 0.0, 0.0])
    for r in G:
        if 2021 <= int(r["Fiscal Year"]) <= 2025:
            a = agg[AGK(r)]; a[0] += num(r[T8]) or 0; a[1] += (num(r[RV]) or 0) + (num(r[PA]) or 0); a[2] += num(r[OT]) or 0
    ags = sorted(((k, v) for k, v in agg.items() if v[0] >= 250), key=lambda kv: -kv[1][0])
    assert len(ags) == 22 and [ags[0][0], r0(ags[0][1][0])] == ["DHS", 41919]
    rv_ = {k: 100 * v[1] / v[0] for k, v in ags}; assert (min(rv_, key=rv_.get), r1(min(rv_.values())), max(rv_, key=rv_.get), r1(max(rv_.values()))) == ("FRB", 2.8, "SSA", 59.4)
    def share_or_none(f): return {y: (100 * (tot(G, RV, y, f) + tot(G, PA, y, f)) / tot(G, T8, y, f) if tot(G, T8, y, f) else None) for y in YR}
    inside = {u: share_or_none(dhs_c(u)) for u in ("USCIS", "CBP", "ICE", "PRIV")}
    assert [round(inside["USCIS"][y]) for y in (2010, 2025)] == [84, 37] and [round(inside["CBP"][y]) for y in (2010, 2025)] == [66, 43]
    vol = {"DHS": {y: tot(G, AR, y, isD) for y in YR}, "Outside DHS": {y: tot(G, AR, y, noD) for y in YR}}
    assert [r0(vol["DHS"][y]) for y in (2023, 2024, 2025)] == [6050, 10557, 20664]
    closed = {y: tot(G, T8, y, isD) for y in YR}; pend = {y: tot(G, APE, y, isD) for y in YR}; oc = {y: tot(G, OT, y, isD) for y in YR}
    assert [r0(closed[y]) for y in (2023, 2025)] == [6124, 12707] and [r0(pend[y]) for y in (2023, 2024, 2025)] == [1054, 2482, 10567] and [r0(oc[y]) for y in (2023, 2025)] == [1090, 5502]
    wo = {"DHS": rates["DHS"], "DHS without USCIS": S([RV, PA], [T8], lambda r: isD(r) and r["Component"] != "USCIS"), "DHS without CBP": S([RV, PA], [T8], lambda r: isD(r) and r["Component"] != "CBP")}
    assert [r1(wo["DHS without USCIS"][y]) for y in (2024, 2025)] == [38.8, 36.8] and [r1(wo["DHS without CBP"][y]) for y in (2024, 2025)] == [32.8, 28.4]
    P = lambda d: [None if d[y] is None else r1(d[y]) for y in YR]; L = lambda d: [r0(d[y]) for y in YR]
    cover_chart = {"title": "Reversed or remanded, share of closed appeals", "series": {"DHS": P(rates["DHS"]), "Outside DHS": P(rates["Outside DHS"])},
                   "colors": {"DHS": "#8c3a91", "Outside DHS": "#4582cc"}}
    walk = {"id": "s3", "name": "Appeals",
      "cover": {"kicker": "Appeals", "title": "Appeals are rare, outcomes vary by agency, and DHS increasingly dominates",
        "body": "Fewer than 2 requests in 100 lead to an appeal. Outside DHS about one quarter of closed appeals are reversed or remanded, from single digits to about 60% across agencies. DHS received 3.4 times as many appeals in FY2025 as two years earlier, and most of the added closures had no decision on the merits.",
        "foot": "Reversed or remanded includes sending the request back for more work; it does not mean the requester received records.", "chart": cover_chart},
      "steps": [
        {"kicker": "All agencies", "title": "Fewer than 2 appeals for every 100 requests processed",
         "sections": [
           {"h": "What we looked at", "p": ["Appeals received in the year (Table 07) per 100 requests processed (Table 01). An appeal may concern a request from an earlier year, so this compares annual volumes, not a per-request probability."]},
           {"h": "What the chart shows", "p": [
             "Government-wide, 1.29–1.99 appeals per 100 requests processed. Even per 100 requests not released in full, it is 1.53–2.93: single digits either way.",
             "Outside DHS the rate fell, from 1.92–2.37 in FY2012–22 to 1.55, 1.58 and 1.78 in FY2023–25; part of this is a larger denominator, not necessarily less willingness to appeal.",
             "The FY2025 jump is almost all DHS: from 1.18 to 2.08 at DHS, only from 1.58 to 1.78 outside DHS."]}],
         "method": "Appeals received ÷ requests processed × 100.",
         "charts": [{"title": "Appeals received per 100 requests processed", "unit": "plain", "digits": 2, "series": {k: [r2(v[y]) for y in YR] for k, v in per.items()},
                     "colors": {"All government": "#9aa3ae", "DHS": "#8c3a91", "Outside DHS": "#4582cc"}, "dashed": ["All government"],
                     "short": {"All government": "all", "DHS": "DHS", "Outside DHS": "outside DHS"}}]},
        {"kicker": "All agencies · DHS", "title": "Outside DHS about one quarter are reversed or remanded; DHS much higher",
         "sections": [
           {"h": "What we looked at", "p": ["Appeals completely or partly reversed or remanded, as a share of all closed appeals (Table 08)."]},
           {"h": "What the charts show", "p": [
             "Government-wide the share ranges from 22.7% to 44.8%, so “about one third” is only a rough summary. Outside DHS it is about one quarter: 20.6%–27.3% each year.",
             "DHS is much higher: 48.2%–75.7% each year in FY2009–23, then 39.0% and 36.7% in FY2024–25. DHS's share of closed appeals rose from 25.3% to 55.0%, so the government-wide figure increasingly reflects DHS."]},
           {"h": "A caution about FY2008", "p": ["DHS's 26.6% that year reflects a large number of closures for other reasons at USCIS, mostly procedural; DHS's range is stated from FY2009."]}],
         "method": "Reversed or remanded = completely + partly reversed or remanded, out of all closed appeals.",
         "charts": [{"title": "Reversed or remanded, share of closed appeals", "series": {k: P(v) for k, v in rates.items()},
                     "colors": {"All agencies": "#9aa3ae", "DHS": "#8c3a91", "Outside DHS": "#4582cc"}, "dashed": ["All agencies"], "short": {"All agencies": "all", "Outside DHS": "outside DHS"}},
                    {"title": "DHS's share of all closed appeals", "series": {"DHS share": P(dw)}, "colors": {"DHS share": "#8c3a91"}, "ref": [{"v": 50, "label": "half"}]}]},
        {"kicker": "DHS", "title": "DHS's recent fall is a change in how appeals are closed, not stricter review",
         "sections": [
           {"h": "What we looked at", "p": ["All four outcomes at DHS each year, then a second denominator: appeals decided on the merits (affirmed + partly + completely reversed)."]},
           {"h": "What the charts show", "p": [
             "DHS's other closures rose from 17.8% in FY2023 to 36.9% and 43.3% in FY2024–25, while affirmances also fell, from 33.8% to 24.1% and 20.0%.",
             "Among appeals decided on the merits, DHS did not fall: 58.8%, 61.8% and 64.8% in FY2023–25."]},
           {"h": "Two denominators, two statements", "p": [
             "Outside DHS: about one quarter of all closed appeals (20.6%–27.3%), and about one third of appeals decided on the merits (28.4%–39.5% in FY2009–25); also without DOJ, 34.6%–46.5%."]}],
         "method": "Table 08's four outcomes add up to 100% of closed appeals.",
         "charts": [{"kind": "stack", "title": "DHS: how closed appeals ended (adds up to 100%)", "segments": {k: P(v) for k, v in mix.items()},
                     "colors": {"Affirmed": "#4582cc", "Partly reversed": "#d4a92c", "Completely reversed": "#8c3a91", "Other closures": "#b8bec7"}},
                    {"title": "Reversed or remanded, share of appeals decided on the merits", "series": {k: P(v) for k, v in merit.items()},
                     "colors": {"DHS": "#8c3a91", "Outside DHS": "#4582cc", "Outside DHS and DOJ": "#21304a"}, "dashed": ["Outside DHS and DOJ"],
                     "short": {"Outside DHS": "outside DHS", "Outside DHS and DOJ": "also without DOJ"}}]},
        {"kicker": "By agency", "title": "From 2.8% to 59.4%: outcomes depend mainly on the agency",
         "sections": [
           {"h": "What we looked at", "p": ["The 22 agencies with at least 250 closed appeals in FY2021–25 combined, ordered by number of closed appeals (not ranked)."]},
           {"h": "What the charts show", "p": [
             "The reversed-or-remanded share ranges from 2.8% (FRB) to 59.4% (SSA), median 24.1%. Other closures range from 6.3% (SEC) to 68.8% (DOL) of the denominator, so the shares are not directly comparable and are not ranked.",
             "DOJ pulls the outside-DHS average down: it is 24.5%–48.0% of closed appeals outside DHS each year, with a share of only 10.9%–20.7%.",
             "Inside DHS, USCIS's share of closed appeals fell from 83% in FY2008 to 25% in FY2025 while CBP's rose from 8% to 58%. PRIV stays low (15% in FY2025)."]}],
         "method": "FY2021–25 totals: reversed or remanded, and other closures, each ÷ closed appeals.",
         "charts": [{"kind": "dots", "title": "FY2021–25, agencies with at least 250 closed appeals (share of closed appeals)", "max": 100,
                     "keys": ["Reversed or remanded", "Other closures"], "rows": [{"name": f"{k} ({r0(v[0]):,})", "v": [r1(100 * v[1] / v[0]), r1(100 * v[2] / v[0])]} for k, v in ags]},
                    {"title": "Inside DHS: reversed or remanded, share of closed appeals", "series": {u: P(v) for u, v in inside.items()},
                     "colors": {"USCIS": "#8c3a91", "CBP": "#4582cc", "ICE": "#d4a92c", "PRIV": "#0b5a36"}}]},
        {"kicker": "DHS", "title": "DHS in FY2024–25: appeals more than tripled, most added closures without a decision on the merits",
         "sections": [
           {"h": "What we looked at", "p": ["Appeals received, closed and pending at DHS. This rests on one or two years of data, and FY2025 has no following-year report to check against, so it is presented as facts and leads."]},
           {"h": "What the chart shows", "p": [
             "DHS received 6,050 appeals in FY2023, 10,557 in FY2024 and 20,664 in FY2025, 64.5% of the government total. It closed 12,707 in FY2025, and its appeals pending at year end rose from 2,482 to 10,567.",
             "DHS closed 6,583 more appeals in FY2025 than in FY2023; 4,412 of them (67%) were closures for other reasons, mainly at CBP (625 to 3,847)."]},
           {"h": "What can and cannot be said", "p": ["Most of the added closures did not reach a review on the merits. It cannot be said that DHS changed its classification or became stricter."]}],
         "method": "Tables 07 and 08. CBP's own reasons (Table 11) are mostly procedural: for example “untimely” (824 in FY2025).",
         "charts": [{"title": "Appeals received", "unit": "count", "series": {k: L(v) for k, v in vol.items()}, "colors": {"DHS": "#8c3a91", "Outside DHS": "#4582cc"}, "short": {"Outside DHS": "outside DHS"}}],
         "tables": [{"title": "DHS appeals", "head": ["", "FY2023", "FY2024", "FY2025"],
                     "rows": [["Received", f"{r0(vol['DHS'][2023]):,}", f"{r0(vol['DHS'][2024]):,}", f"{r0(vol['DHS'][2025]):,}"],
                              ["Closed", f"{r0(closed[2023]):,}", f"{r0(closed[2024]):,}", f"{r0(closed[2025]):,}"],
                              ["  of which other closures", f"{r0(oc[2023]):,}", f"{r0(oc[2024]):,}", f"{r0(oc[2025]):,}"],
                              ["Pending at year end", f"{r0(pend[2023]):,}", f"{r0(pend[2024]):,}", f"{r0(pend[2025]):,}"]]}]},
        {"kicker": "Checks", "title": "No single agency or component drives the main figures",
         "sections": [
           {"h": "What we looked at", "p": ["Each agency or component is removed in turn from all years, and the range of the main figures reported."]},
           {"h": "What we found", "p": [
             "Appeals per 100 requests processed: at most 2.37 across 594 removals.",
             "Reversed or remanded, outside DHS: 19.0% (removing DOS) to 32.9% (removing DOJ's OIP) across 572 removals, so “about one quarter” carries a margin of roughly seven to eight points either way. Among appeals decided on the merits: 26.9%–46.5%.",
             "DHS's high share comes largely from USCIS: without USCIS, DHS is 34.4%–56.8% in FY2009–23, still above outside DHS; in FY2024–25, 38.8% and 36.8%."]}],
         "method": "One unit removed at a time, from all years; agencies without components count once.",
         "charts": [{"title": "DHS: reversed or remanded, without USCIS or CBP", "series": {k: P(v) for k, v in wo.items()},
                     "colors": {"DHS": "#8c3a91", "DHS without USCIS": "#d4a92c", "DHS without CBP": "#21304a"}, "short": {"DHS without USCIS": "without USCIS", "DHS without CBP": "without CBP"}}]},
        {"kicker": "The finding", "title": "Appeals are rare, outcomes vary by agency, and DHS increasingly dominates",
         "sections": [
           {"h": "In one sentence", "p": ["Few requesters appeal; what happens on appeal depends mainly on the agency; and DHS increasingly dominates the appeal stage: in FY2025 it received 3.4 times as many appeals as two years earlier, appeals pending at year end rose about tenfold, and most of the added closures were closed for other reasons, without a decision on the merits."]},
           {"h": "What not to say", "p": [
             "“One third of denials are overturned”: the base is closed appeals, and fewer than 2 in 100 processed requests are appealed.",
             "A ranking of agencies by reversal share: other closures make up 6.3% to 68.8% of the denominator.",
             "That DHS's lower FY2024–25 share means stricter review: among appeals decided on the merits it did not fall.",
             "That the FY2025 surge is settled: it is one year, with no following-year report yet."]},
           {"h": "Leads to follow up", "p": ["CBP's “no component response to adjudicate” (1,155 in FY2025) · DHS partial reversals fell from 27.9% to 4.1% · outside DHS, fewer appeals per 100 processed from FY2023."]}],
         "method": "Annual totals reported by the agencies themselves; reversed or remanded does not mean records were released. Full analysis: Storyline 3 notebook.",
         "charts": [cover_chart]}]}
    check_numbers(walk, "S3-appeals-en", allow=(22, 250, 2008, 2025, 100))
    return walk
