"""Requests (S0) storyline, from the notebook S0-request-volume-en. Series are recomputed with storyline_lib and anchored to
the notebook's assertions; every number in the text is checked against the notebook text."""
from storyline_lib import G, YR, REC, PRO, tot, bykey, allr, ni, vba, isD, AGK, COK
from walk_common import check_numbers

r0 = lambda v: int(round(v)); r1 = lambda v: round(float(v), 1)
yearly = lambda c, f=allr: {y: tot(G, c, y, f) for y in YR}
imm = lambda r: not ni(r)
unit = lambda a, c: (lambda r: AGK(r) == a and r["Component"] == c)
rest_clean = lambda r: ni(r) and not vba(r) and AGK(r) != "DHS"

def build():
    rec, pro = yearly(REC), yearly(PRO)
    assert [int(rec[y]) for y in (2008, 2019, 2021, 2025)] == [560978, 858952, 838164, 1707413] and [int(pro[y]) for y in (2008, 2025)] == [578141, 1635171]
    rec4, recr = yearly(REC, imm), yearly(REC, ni)
    assert [int(rec4[2008]), int(rec4[2025]), int(recr[2008]), int(recr[2025])] == [110388, 962166, 450590, 745247]
    share4 = {y: 100 * rec4[y] / rec[y] for y in YR}; dshare = {y: 100 * tot(G, REC, y, isD) / rec[y] for y in YR}
    assert [r1(share4[y]) for y in (2008, 2019, 2024, 2025)] == [19.7, 47.3, 58.7, 56.4] and [r1(dshare[y]) for y in (2008, 2025)] == [19.4, 59.7]
    four = {u: yearly(REC, unit(a, u)) for a, u in (("DHS", "USCIS"), ("DHS", "CBP"), ("DOJ", "EOIR"), ("DHS", "ICE"))}
    assert [[int(four[u][y]) for y in (2008, 2019, 2025)] for u in four] == [[78985, 200174, 589972], [13943, 86133, 207034], [13236, 55499, 102922], [4224, 64231, 62238]]
    inc = {u: 100 * (four[u][2025] - four[u][2008]) / (rec4[2025] - rec4[2008]) for u in four}
    assert [r1(v) for v in inc.values()] == [60.0, 22.7, 10.5, 6.8]
    rc = yearly(REC, rest_clean)
    lo, hi = min(rc[y] for y in range(2010, 2020)), max(rc[y] for y in range(2010, 2020))
    assert [int(lo), int(hi), int(rc[2021]), int(rc[2024]), int(rc[2025])] == [394268, 444654, 322865, 417789, 484098]
    cisa, priv = yearly(REC, unit("DHS", "CISA")), yearly(REC, unit("DHS", "PRIV"))
    assert [int(cisa[2018]), int(cisa[2019]), int(priv[2018]), int(priv[2019])] == [37516, 353, 1448, 43024]
    g25 = sorted(bykey(2025, REC, allr, AGK).items(), key=lambda kv: -kv[1]); g08 = bykey(2008, REC, allr, AGK)
    tot25 = sum(v for _, v in g25)
    assert [k for k, _ in g25[:5]] == ["DHS", "DOJ", "VA", "DoD", "HHS"] and r1(100 * g25[0][1] / tot25) == 59.7 and r1(100 * sum(v for _, v in g25[:5]) / tot25) == 84.1
    ratio = {"All government": {y: 100 * pro[y] / rec[y] for y in YR}, "Four units": {y: 100 * tot(G, PRO, y, imm) / rec4[y] for y in YR},
             "Outside the four units": {y: 100 * tot(G, PRO, y, ni) / recr[y] for y in YR}}
    assert [r1(ratio["Four units"][y]) for y in (2009, 2015, 2019, 2025)] == [152.2, 124.2, 105.4, 101.8] and r1(ratio["Outside the four units"][2025]) == 88.0
    plot_ratio = {k: [None if not 80 <= v[y] <= 115 else r1(v[y]) for y in YR] for k, v in ratio.items()}
    assert [(y, k) for k in ratio for i, y in enumerate(YR) if plot_ratio[k][i] is None] == [(2009, "Four units"), (2015, "Four units")]
    PERF = [c for c in G[0] if c[:3] in ("16_", "17_", "18_") and "TimeIncrementProcessedQuantity[" in c]
    perf = {y: 100 * sum(tot(G, c, y) for c in PERF) / pro[y] for y in YR}
    assert [r1(perf[y]) for y in (2022, 2023, 2024, 2025)] == [90.2, 88.9, 77.5, 87.4]
    L = lambda d: [r0(d[y]) for y in YR]; P = lambda d: [r1(d[y]) for y in YR]
    cover_chart = {"title": "Requests received", "unit": "count", "series": {"Four units (USCIS, CBP, ICE, EOIR)": L(rec4), "Outside the four units": L(recr)},
                   "short": {"Four units (USCIS, CBP, ICE, EOIR)": "four units", "Outside the four units": "the rest"}, "colors": {"Four units (USCIS, CBP, ICE, EOIR)": "#8c3a91", "Outside the four units": "#4582cc"}}
    walk = {"id": "s0", "name": "Requests",
      "cover": {"kicker": "Requests", "title": "Requests nearly tripled, mostly at four immigration-related units",
        "body": "Requests received rose from 560,978 in FY2008 to 1,707,413 in FY2025, 3.04 times as many (2.86 times from FY2010). 74.3% of the increase is at USCIS, CBP, ICE and EOIR. Outside these four, requests rose 1.65 times; leaving out VBA and DHS's other components as well, they were roughly flat for a decade and passed their FY2010–19 high only in FY2025.",
        "foot": "Requests received (Table 01). The four units are a grouping of units, not of request topics. FY2008–09: 26 agencies are not yet in the data.", "chart": cover_chart},
      "steps": [
        {"kicker": "All agencies", "title": "Requests received rose from 560,978 to 1,707,413",
         "sections": [
           {"h": "What we looked at", "p": ["Requests received and processed in each year, government-wide (Table 01). Both are counts of requests; one requester can file many."]},
           {"h": "What the chart shows", "p": [
             "Requests received rose from 560,978 in FY2008 to 1,707,413 in FY2025, 3.04 times as many. The growth was uneven: 858,952 in FY2019 and 838,164 in FY2021, then 2.04 times as many four years later.",
             "Processing broadly kept pace: 578,141 in FY2008 and 1,635,171 in FY2025."]},
           {"h": "A caution about FY2008", "p": [
             "26 agencies have no FY2008 data and appear in FY2009–10; in FY2010 they account for 9.3% of government receipts. The FY2008 starting level is therefore low; from FY2010 the multiple is 2.86, hence “nearly tripled”."]}],
         "method": "Requests received include requests that are not yet perfected (complete enough to process); counts are of requests, not requesters.",
         "charts": [{"title": "Requests received and processed, all agencies", "unit": "count", "series": {"Received": L(rec), "Processed": L(pro)}, "colors": {"Received": "#4582cc", "Processed": "#21304a"}}]},
        {"kicker": "All agencies · four units", "title": "74.3% of the increase is at four immigration-related units",
         "sections": [
           {"h": "What we looked at", "p": ["USCIS, CBP and ICE (in DHS) and EOIR (the immigration courts, in DOJ), against all other units. This is a grouping of units, not of request topics."]},
           {"h": "What the charts show", "p": [
             "Requests at the four units rose from 110,388 to 962,166, 8.72 times as many; at the rest, from 450,590 to 745,247, 1.65 times. Of the 1,146,435 requests added over FY2008–25, 74.3% are at the four units (74.4% counted from FY2010).",
             "Their share of all requests rose from 19.7% in FY2008 to 47.3% in FY2019 and 58.7% in FY2024. All of DHS rose from 19.4% to 59.7%."]},
           {"h": "Within the four units", "p": [
             "Mainly USCIS: 78,985 to 589,972, 60.0% of the four units' increase. CBP accounts for 22.7%, EOIR 10.5% and ICE 6.8% (table)."]},
           {"h": "Why it matters", "p": ["Government-wide request volume mainly reflects these four units, which is why the later storylines separate them first."]}],
         "method": "Four units = USCIS, CBP, ICE and EOIR. Shares of all requests received that year.",
         "charts": [{"title": "Requests received", "unit": "count", "series": cover_chart["series"], "short": cover_chart["short"], "colors": cover_chart["colors"]},
                    {"title": "Share of all requests received", "series": {"Four units": P(share4), "All of DHS": P(dshare)}, "colors": {"Four units": "#8c3a91", "All of DHS": "#9aa3ae"}, "dashed": ["All of DHS"]}],
         "tables": [{"title": "The four units, requests received", "head": ["", "FY2008", "FY2019", "FY2025", "Share of the increase"],
                     "rows": [[u, f"{r0(four[u][2008]):,}", f"{r0(four[u][2019]):,}", f"{r0(four[u][2025]):,}", f"{r1(inc[u])}%"] for u in four]}]},
        {"kicker": "Outside the four units", "title": "Everyone else, without VBA and DHS's other components: flat for a decade, a new high only in FY2025",
         "sections": [
           {"h": "What we looked at", "p": [
             "Requests received outside the four units, then a second line that also leaves out VBA and DHS's other components. Those two account for 54.1% of what the rest added in FY2021–25, and requests have moved between DHS components."]},
           {"h": "What the chart shows", "p": [
             "Outside the four units as a whole (first line), requests were already above their earlier high in FY2023.",
             "Without VBA and DHS's other components, receipts were 394,268–444,654 each year in FY2010–19 (dashed lines). FY2020–22 is a low (322,865 in FY2021); FY2024, at 417,789, is back within the earlier range; FY2025, at 484,098, is the highest of the 18 years, 8.9% above the FY2010–19 maximum.",
             "So without those two, through FY2024 this is a recovery; only FY2025 is a new high. Leaving out any one agency, the FY2019–25 rise is still at least 64,000 (removing DOS)."]},
           {"h": "PRIV's FY2019 jump is a transfer", "p": [
             "CISA received 37,516 requests in FY2018 and 353 in FY2019, while DHS's Privacy Office (PRIV) went from 1,448 to 43,024: the same requests, reported under a different component."]}],
         "method": "DHS's other components = every DHS component except USCIS, CBP and ICE. VBA = VA's Veterans Benefits Administration.",
         "charts": [{"title": "Requests received outside the four units", "unit": "count",
                     "series": {"Outside the four units": L(recr), "Also without VBA and DHS's other components": L(rc)},
                     "short": {"Outside the four units": "outside", "Also without VBA and DHS's other components": "also without VBA, DHS"},
                     "colors": {"Outside the four units": "#4582cc", "Also without VBA and DHS's other components": "#21304a"},
                     "ref": [{"v": r0(lo), "label": "FY2010–19 low"}, {"v": r0(hi), "label": "FY2010–19 high"}]}],
         "tables": [{"title": "CISA and PRIV: one stream of requests", "head": ["", "FY2018", "FY2019"],
                     "rows": [["CISA", f"{r0(cisa[2018]):,}", f"{r0(cisa[2019]):,}"], ["PRIV", f"{r0(priv[2018]):,}", f"{r0(priv[2019]):,}"]]}]},
        {"kicker": "By agency", "title": "DHS alone receives 59.7% of all requests",
         "sections": [
           {"h": "What we looked at", "p": ["Agency totals (all components included): the 15 agencies with the most requests received in FY2025."]},
           {"h": "What the chart shows", "p": [
             "117 agencies received requests in FY2025. DHS alone received 59.7% (1,019,496), and the top five (DHS, DOJ, VA, DoD and HHS) 84.1%.",
             "The second agency, DOJ, received 159,743 and the third, VA, 124,414, an order of magnitude below DHS. The top five in FY2008 were the same five, with DHS at only 19.4%."]},
           {"h": "Why it matters", "p": ["“How agencies differ” is first of all a difference between DHS and everyone else."]}],
         "method": "Requests received in FY2025, agency totals.",
         "charts": [{"kind": "dbars", "fmt": "count", "title": "Requests received in FY2025: the 15 largest agencies",
                     "bars": [{"name": k, "v": r0(v)} for k, v in g25[:15]]}]},
        {"kicker": "All agencies · four units", "title": "Outside the four units, FY2025 processing was only 88.0% of receipts",
         "sections": [
           {"h": "What we looked at", "p": ["Requests processed ÷ requests received. Above 100% means more was processed than received. Two of the four units' values, FY2009 and FY2015 (152.2% and 124.2%), are off the scale and left as gaps."]},
           {"h": "What the chart shows", "p": [
             "The four units: 105.4% in FY2019, 93.7% in FY2023, then 99.7% and 101.8% in FY2024–25.",
             "Outside the four units: 99.4% in FY2019, 93.3% in FY2023, 100.1% in FY2024 and only 88.0% in FY2025, the lowest of the 18 years. Receipts are rising faster than processing, the other side of the rising backlog in the Backlog storyline."]},
           {"h": "More of the count is not yet complete", "p": [
             "Counts include requests that are not perfected. Perfected requests were 91.6%–95.7% of processed requests in FY2008–21, and 90.2%, 88.9%, 77.5% and 87.4% in FY2022–25. In FY2024, 59.1% of the difference is at USCIS."]}],
         "method": "Processed and received from Table 01; perfected requests from Tables 16–18, which count perfected requests only.",
         "charts": [{"title": "Requests processed ÷ requests received", "series": plot_ratio, "yMin": 80, "yMax": 115, "ref": [{"v": 100, "label": "100%"}],
                     "colors": {"All government": "#9aa3ae", "Four units": "#8c3a91", "Outside the four units": "#4582cc"}, "dashed": ["All government"],
                     "short": {"All government": "all", "Four units": "four units", "Outside the four units": "outside"}}]},
        {"kicker": "The finding", "title": "Requests nearly tripled, mostly at four immigration-related units",
         "sections": [
           {"h": "In one sentence", "p": [
             "Requests received nearly tripled over FY2008–25 (3.04 times the FY2008 level, 2.86 times FY2010); 74.3% of the increase is at four immigration-related units, whose share of all requests rose from 19.7% to 58.7% in FY2024; elsewhere (without VBA and DHS's other components) requests were roughly flat for a decade, fell to a low in FY2020–22, recovered by FY2024, and were the highest of the 18 years only in FY2025."]},
           {"h": "What not to say", "p": [
             "That requests surged across the board: 74.3% of the increase is at four units.",
             "That the rise elsewhere is a broad multi-year trend: without VBA and DHS's other components, only FY2025 exceeds the FY2010–19 range, and FY2025 has no following-year report yet.",
             "That these are “immigration requests”, or that counts are numbers of requesters. Or any cause: the reports do not show why requests increased."]},
           {"h": "Leads to follow up", "p": [
             "CISA and PRIV, one stream of requests (8,480 in FY2014, 148,873 in FY2025) · VBA's 61,658–100,897 a year from FY2023 · outside the four units, FY2025 processing at 88.0% of receipts."]}],
         "method": "Annual totals reported by the agencies themselves. 26 agencies are missing in FY2008–09; FY2025 has no following-year report yet. Full analysis: Storyline 0 notebook.",
         "charts": [cover_chart]}]}
    check_numbers(walk, "S0-request-volume-en", allow=(15, 2008, 2025))
    return walk
