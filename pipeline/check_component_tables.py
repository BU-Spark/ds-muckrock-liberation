"""Checks the component-level tables before they are delivered. Exits with 1 if a check fails.

Reads the foia.gov API reports again with its own code (not the build script's), and also uses sources that do
not come through the API:
  - the agency-level table (foia.gov's yearly CSV export) for the Agency Overall rows,
  - foia.gov's component CSV export for FY2024 (foia_downloader_components.py),
  - the agency-level statute table (foia.gov's CSV export) for the 06 Agency Overall rows.

Checks:
  1 structure: 8 ID columns + the 244 data columns, one Agency Overall row per agency-year of the agency table,
    unique row keys, known Row Type values, only Commerce FY2025 DOC excluded
  2 every cell against the API: component / second_entry / no_component rows against the site's records,
    Agency Overall rows against the site's agency totals; every site record has a row
  3 Agency Overall against the agency-level table
  4 components + second_entry + no_component against Agency Overall (summable columns)
  5 FY2024 components against foia.gov's component CSV export
  6 03/11 reasons against the API; reasons added up against the table's total column
  7 06 statutes against the API; Agency Overall against the agency-level statute table
Differences that are known and explained are listed in KNOWN (check -> agency-year -> reason); anything else
fails, and so does a known one that is no longer found.

Usage: python check_component_tables.py <component dir> <agency dir> <api dir> <field_map.csv> <report_data_map.json>
       <data_type_map.csv> <column_mapping.csv> <component CSV dir for 2024> <out dir>
"""
import csv
import glob
import gzip
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api_to_component_rows as conv  # noqa: E402  (SEG, NESTED, val, ws, load_maps only)
from build_component_master import SECTIONS  # noqa: E402
from clean_text_03_06_11 import clean_text  # noqa: E402
from foia_component import summable  # noqa: E402

csv.field_size_limit(10**9)
COMP, AGD, API_DIR, FMAP, DMAP, TYPES, MAPPING, CSV24, OUT = sys.argv[1:10]
os.makedirs(OUT, exist_ok=True)
read = lambda p: list(csv.DictReader(open(p, newline="", encoding="utf-8")))
low = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
NA = {"", "na", "n/a", "n\\a", "n.a", "n.a."}
results = []  # check, agency, fy, row, column, table value, reference value, class


def num(v):
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None


def cls(t, s):
    t, s = (t or "").strip(), (s or "").strip()
    if t == s:
        return "same"
    nt, ns = num(t), num(s)
    if nt is not None and ns is not None and abs(nt - ns) < 1e-6:
        return "same"
    kind = lambda v: "blank" if v == "" else "N/A" if v.lower() in NA else "0" if num(v) == 0 else "value"
    return f"{kind(t)} vs {kind(s)}" if "value" not in (kind(t), kind(s)) else "differ" if kind(t) == kind(s) == "value" else f"{kind(t)} vs {kind(s)}"


def report(check, agency, fy, row, col, t, s, k=None):
    k = k or cls(t, s)
    if k != "same":
        results.append((check, agency, fy, row, col, t, s, k))
    return k


# ---------- the tables ----------
master = read(os.path.join(COMP, "component_master_no_03_06_11.csv"))
reasons = read(os.path.join(COMP, "other_reasons_03_11.csv"))
statutes = read(os.path.join(COMP, "exemption_statutes_06.csv"))
MCOLS = [c for c in master[0] if re.match(r"\d\d_", c)]  # data columns
fmap, overall = conv.load_maps(FMAP, DMAP)
# two agency totals the site's data map lists under other field names than its records use (see the build script)
overall.update({("AppealNonExemptionDenialSection", "NonExemptionDenialQuantity[NotAgency]"): "field_overall_vic2_not_agency_re",
                ("AppealNonExemptionDenialSection", "NonExemptionDenialQuantity[NotDescribed]"): "field_overall_vic2_rec_not_desc"})
HAS = {(sec, col) for (sec, _), col in fmap.items()}
SEC_OF_NO = defaultdict(list)
for sec, no, _ in SECTIONS:
    for n in ([no] if no else ["22", "23"]):
        SEC_OF_NO[n].append(sec)
COL_SF = {}
for c in MCOLS:
    no, field = c.split("_", 1)[0], c.split("__", 1)[1]
    hit = [s for s in SEC_OF_NO[no] if (s, field) in HAS]
    COL_SF[c] = (hit[0], field)
SEC_COLS = defaultdict(list)
for c, (sec, f) in COL_SF.items():
    SEC_COLS[sec].append(c)

# ---------- 1. structure ----------
problems = []
ID = ["Fiscal Year", "Agency", "Agency Abbreviation", "Component", "Component Name", "Row Type",
      "Exclude From Component Sum", "Exclude Reason"]
if list(master[0]) != ID + MCOLS or len(MCOLS) != 244:
    problems.append("columns differ from the 8 ID columns + 244 data columns")
for t, name, extra in ((reasons, "03/11", ["Data Type No.", "Data Type", "Reason", "Quantity"]),
                       (statutes, "06", ["Statute", "Type of Information Withheld", "Case Citation", "Number of Times Relied Upon"])):
    if list(t[0]) != ID + extra:
        problems.append(f"{name} columns differ")
agency_rows = read(os.path.join(AGD, "FOIA_agency_FY2008-2025.csv"))
ay_agency = {(r["Agency"], r["Fiscal Year"]) for r in agency_rows}
ov_rows = Counter((r["Agency"], r["Fiscal Year"]) for r in master if r["Row Type"] == "agency_overall")
if set(ov_rows) != ay_agency or max(ov_rows.values()) != 1:
    problems.append(f"Agency Overall rows: {len(ov_rows)} agency-years, agency table {len(ay_agency)}")
keys = Counter((r["Fiscal Year"], r["Agency"], r["Row Type"], r["Component"], r["Component Name"]) for r in master)
if max(keys.values()) != 1:
    problems.append("row key not unique")
rt = Counter(r["Row Type"] for r in master)
if set(rt) - {"agency_overall", "component", "second_entry", "no_component"}:
    problems.append(f"unknown Row Type {rt}")
excl = {(r["Agency"], r["Fiscal Year"], r["Component"]) for t in (master, reasons, statutes) for r in t if r["Exclude From Component Sum"]}
if excl - {("Department of Commerce", "2025", "DOC")}:
    problems.append(f"unexpected exclusions {excl}")
for t, name in ((reasons, "03/11"), (statutes, "06")):
    k = {(r["Fiscal Year"], r["Agency"], r["Row Type"], r["Component"], r["Component Name"]) for r in t}
    if k - set(keys) - {(fy, ag, "agency_overall", "Agency Overall", ag) for ag, fy in ay_agency}:
        problems.append(f"{name} rows with no master row: {list(k - set(keys))[:3]}")


# ---------- the API, read again ----------
def site(path):
    d = json.load(gzip.open(path, "rt", encoding="utf-8"))
    rep, inc = d["data"], {x["id"]: x for x in d.get("included", [])}
    node = lambda rel: (((rel or {}).get("data") or {}).get("id"))
    name = lambda cid: (conv.ws(inc[cid]["attributes"].get("abbreviation")), conv.ws(inc[cid]["attributes"].get("title"))) if cid in inc else ("", "")
    recs, sts = defaultdict(list), []
    for seg, sec in conv.SEG.items():
        rel = (rep["relationships"].get(seg) or {}).get("data") or []
        for i, p in enumerate(rel if isinstance(rel, list) else [rel]):
            para = inc.get(p["id"])
            if not para:
                continue
            at = para["attributes"]
            if seg == "field_statute_iv":
                text = tuple(clean_text(conv.val(at.get(f))) for f in ("field_statute", "field_type_of_info_withheld", "field_case_citation"))
                sts.append((i, "TOTAL", *text, conv.val(at.get("field_total_num_relied_by_agency"))))
                for q in (para["relationships"].get("field_agency_component_inf") or {}).get("data") or []:
                    det = inc.get(q["id"])
                    if det:
                        c = node(det["relationships"].get("field_agency_component"))
                        sts.append((i, name(c) if c in inc else None, *text, conv.val(det["attributes"].get("field_num_relied_by_agency_comp"))))
                continue
            c = node(para["relationships"].get("field_agency_component"))
            vals = {fmap[(sec, k)]: conv.val(v) for k, v in at.items() if (sec, k) in fmap and conv.val(v) != ""}
            rs = []
            for q in (para["relationships"].get(conv.NESTED.get(seg, "")) or {}).get("data") or []:
                det = inc.get(q["id"])
                if det:
                    x = det["attributes"]
                    rs.append((clean_text(conv.val(x.get("field_desc_oth_reasons"))),
                               next((conv.val(v) for k, v in x.items() if k.startswith("field_num")), "")))
            recs[sec].append((name(c) if c in inc else None, vals, rs))
    return rep, recs, sts


index = {r["id"]: r for r in json.load(open(os.path.join(API_DIR, "_index.json")))}
names_by_fy = defaultdict(set)
for ag, fy in ay_agency:
    names_by_fy[fy].add(ag)


def tname(s, fy):
    if s in names_by_fy[fy]:
        return s
    hit = [n for n in names_by_fy[fy] if low(n) == low(s) or low(s).replace("us", "", 1) == low(n)]
    return hit[0] if len(hit) == 1 else None


by_ay = defaultdict(list)
for r in master:
    by_ay[(r["Agency"], r["Fiscal Year"])].append(r)
cells = Counter()
SITE = {}
for path in glob.glob(os.path.join(API_DIR, "*", "*.json.gz")):
    rep, recs, sts = site(path)
    fy = str(rep["attributes"].get("field_foia_annual_report_yr"))
    agency = tname(index[rep["id"]]["agency"], fy)
    if agency is None:
        problems.append(f"API report not in the agency table: {index[rep['id']]['agency']} {fy}")
        continue
    at = rep["attributes"]
    owners = defaultdict(set)
    for sec, rs in recs.items():
        owners[sec] |= {o for o, _, _ in rs}
    owners["06"] |= {s[1] for s in sts if s[1] != "TOTAL"}
    named = {o for v in owners.values() for o in v if o}
    one = not named or (len(named) == 1 and not any(len(v) > 1 for v in owners.values()))
    SITE[(agency, fy)] = (at, recs, sts, one)
    rows = by_ay[(agency, fy)]
    ov = next(r for r in rows if r["Row Type"] == "agency_overall")
    # 2a. Agency Overall vs the site's totals
    for c in MCOLS:
        sec, f = COL_SF[c]
        of = overall.get((sec, f))
        vals = [v.get(f, "") for _, v, _ in recs.get(sec, []) if v.get(f, "") != ""]
        if of and conv.val(at.get(of)) != "":
            ref, how = conv.val(at.get(of)), "site total"
        elif one:
            ref, how = (vals[0] if len(vals) == 1 else (repr(sum(num(v) for v in vals)) if vals and summable(f) and all(num(v) is not None for v in vals) else (vals[0] if vals else ""))), "one-organization record"
        elif of:
            ref, how = "", "site total (blank)"
        else:
            ref = repr(sum(num(v) for v in vals if num(v) is not None)) if any(num(v) is not None for v in vals) and summable(f) else ""
            how = "components added (no site total)"
        cells[("2 Agency Overall vs API", how, report("2 Agency Overall vs API", agency, fy, "Agency Overall", c, ov[c], ref))] += 1
    # 2b. rows vs the site's records
    if one:
        extra = [r for r in rows if r["Row Type"] != "agency_overall"]
        if extra:
            problems.append(f"{agency} {fy}: one organization on the site but {len(extra)} component rows")
        continue
    # key of a non-total row: (code, name, entry 1 or 2, linked to no component)
    rkey = lambda r: (r["Component"], r["Component Name"], 2 if r["Row Type"] == "second_entry" else 1,
                      r["Row Type"] == "no_component" or (r["Row Type"] == "second_entry" and not r["Component"]))
    row_of = {rkey(r): r for r in rows if r["Row Type"] != "agency_overall"}
    filled = set()  # (row key, table) the site has a record for
    for sec, rs in recs.items():
        n = Counter()
        for o, vals, _ in rs:
            n[o] += 1
            k = (*(o or ("", "")), n[o], o is None)
            r = row_of.get(k)
            if r is None:
                problems.append(f"{agency} {fy} {sec}: site record {k} has no row")
                continue
            filled.add((k, sec))
            for c in SEC_COLS.get(sec, []):
                cells[("2 rows vs API", r["Row Type"], report("2 rows vs API", agency, fy, f"{k[0]}|{k[1]}|{r['Row Type']}", c, r[c], vals.get(COL_SF[c][1], "")))] += 1
    in_06 = {(*(s[1] or ("", "")), 1, s[1] is None) for s in sts if s[1] != "TOTAL"}
    for k, r in row_of.items():
        if not any(x[0] == k for x in filled) and k not in in_06:
            problems.append(f"{agency} {fy}: row {k} has no site record")
        for sec, cs in SEC_COLS.items():  # a table the site has no record of for this row must be blank
            if (k, sec) not in filled:
                bad = [c for c in cs if r[c] != ""]
                if bad:
                    problems.append(f"{agency} {fy} {k} {sec}: {len(bad)} values but no site record")
missing_reports = ay_agency - set(SITE)
if missing_reports:
    problems.append(f"agency-years with no API report: {sorted(missing_reports)[:5]}")

# ---------- 3. Agency Overall vs the agency-level table ----------
types = {r["No."].zfill(2): r for r in read(TYPES)}
AG_COL = {}
for no, t in types.items():
    for m in read(MAPPING):
        if m["table"] == "foia-" + t["Official file name (foia-*.csv)"] and no != "06":
            f = m["xml_col"]
            hit = [s for s in SEC_OF_NO[no] if (s, f) in HAS]
            col = [c for c in MCOLS if COL_SF[c] == (hit[0], f)] if hit else []
            name = t["Column prefix in FOIA_agency_FY2008-2025.csv"] + m["csv_col"]
            if col and name in agency_rows[0]:  # the ten-oldest dates are named Date, Date.1 ... in the agency table
                AG_COL[name] = col[0]
# ten-oldest dates: the agency table names them Date, Date.1 ... Date.9, each just before its "Nth Oldest" days column
ORD = {"Oldest": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5, "6th": 6, "7th": 7, "8th": 8, "9th": 9, "10th": 10}
TEN = {"appeals_ten_oldest": "13_AppealsTenOldest__", "pending_ten_oldest": "20_TenOldestRequests__",
       "consultations_ten_oldest": "28_ConsultationsTenOldest__"}
hdr = list(agency_rows[0])
for i, a in enumerate(hdr):
    if re.search(r"__Date(\.\d)?$", a):
        p, nxt = a.split("__")[0], hdr[i + 1]
        word = nxt.split("__")[1].split(" ")[0]
        assert nxt.startswith(p + "__") and "Days Pending" in nxt and word in ORD, (a, nxt)
        AG_COL[a] = f"{TEN[p]}OldItem{ORD[word]}.OldItemReceiptDate"
data_cols = [a for a in hdr if "__" in a]
if set(AG_COL) != set(data_cols):
    problems.append(f"agency-table columns not compared: {sorted(set(data_cols) - set(AG_COL))[:5]}")
for r in agency_rows:
    ov = next(x for x in by_ay[(r["Agency"], r["Fiscal Year"])] if x["Row Type"] == "agency_overall")
    for a, c in AG_COL.items():
        cells[("3 Agency Overall vs agency table", "", report("3 Agency Overall vs agency table", r["Agency"], r["Fiscal Year"], "Agency Overall", c, ov[c], r[a]))] += 1

# ---------- 4. parts vs Agency Overall ----------
sums = []
for (agency, fy), rows in by_ay.items():
    ov = next(r for r in rows if r["Row Type"] == "agency_overall")
    parts = [r for r in rows if r["Row Type"] != "agency_overall" and not r["Exclude From Component Sum"]]
    if not parts:
        continue
    for c in MCOLS:
        if not summable(COL_SF[c][1]):
            continue
        v = [num(r[c]) for r in parts if num(r[c]) is not None]
        t = num(ov[c])
        if v and t is not None and abs(sum(v) - t) > 0.011:
            sums.append((agency, fy, c, sum(v), t))
cells[("4 parts vs Agency Overall", "agency-years", "differ")] = len({(a, f) for a, f, *_ in sums})

# ---------- 5. FY2024 components vs foia.gov's component CSV ----------
by_file = {t["Official file name (foia-*.csv)"]: no for no, t in types.items()}
maps = read(MAPPING)
for p in sorted(glob.glob(os.path.join(CSV24, "*.csv"))):
    no = os.path.basename(p)[:2]
    t = types[no]
    lab = {m["csv_col"]: m["xml_col"] for m in maps if m["table"] == "foia-" + t["Official file name (foia-*.csv)"]}
    for r in read(p):
        if r["Fiscal Year"] != "2024":
            continue
        agency = tname(r["Agency"], "2024")
        rows = by_ay.get((agency, "2024"), [])
        if r["Component"] == "Agency Overall":
            cand = [x for x in rows if x["Row Type"] == "agency_overall"]
        else:
            cand = [x for x in rows if x["Component"] == r["Component"] and x["Row Type"] == "component"] or \
                   ([x for x in rows if x["Row Type"] == "agency_overall"] if SITE[(agency, "2024")][3] else [])
        if not cand:
            problems.append(f"FY2024 CSV row with no table row: {r['Agency']} / {r['Component']} ({os.path.basename(p)})")
            continue
        pairs = [(h, lab[h]) for h in r if h in lab]
        pairs = [(h, [m for m in MCOLS if m.split('_', 1)[0] == no and m.split('__', 1)[1] == f]) for h, f in pairs]
        best = max(cand, key=lambda x: sum(cls(x[cs[0]], r[h]) == "same" for h, cs in pairs if cs))
        for h, cs in pairs:
            if cs:
                cells[("5 FY2024 vs component CSV", "", report("5 FY2024 vs component CSV", agency, "2024",
                                                                 f"{best['Component']}|{best['Component Name']}", cs[0], best[cs[0]], r[h]))] += 1

# ---------- 6. 03/11 reasons ----------
REASON_SEC = {"03": "RequestDenialOtherReasonSection", "11": "AppealDenialOtherReasonSection"}
mine = defaultdict(Counter)
for r in reasons:
    mine[(r["Agency"], r["Fiscal Year"], r["Data Type No."], r["Row Type"], r["Component"], r["Component Name"])][(r["Reason"], r["Quantity"])] += 1
theirs = defaultdict(Counter)
for (agency, fy), (at, recs, sts, one) in SITE.items():
    for no, sec in REASON_SEC.items():
        n = Counter()
        for o, _, rs in recs.get(sec, []):
            n[o] += 1
            if one:
                k = ("agency_overall", "Agency Overall", agency)
            else:
                k = ("second_entry" if n[o] == 2 else "component" if o else "no_component", *(o or ("", "")))
            for x in rs:
                theirs[(agency, fy, no, *k)][x] += 1
for k in set(mine) | set(theirs):
    cells[("6 03/11 vs API", "", report("6 03/11 vs API", k[0], k[1], "|".join(k[2:]), "reasons", str(sorted(mine[k].items())), str(sorted(theirs[k].items())),
                                       "same" if mine[k] == theirs[k] else "differ"))] += 1
tot = {"03": "03_DispositionOtherReasons__ComponentOtherDenialReasonQuantity", "11": "11_AppealsOtherReasons__ComponentOtherDenialReasonQuantity"}
rsum = defaultdict(float)
for r in reasons:
    rsum[(r["Agency"], r["Fiscal Year"], r["Data Type No."], r["Row Type"], r["Component"], r["Component Name"])] += num(r["Quantity"]) or 0
reason_total_diffs = []
for r in master:
    for no, c in tot.items():
        k = (r["Agency"], r["Fiscal Year"], no, r["Row Type"], r["Component"], r["Component Name"])
        if k in rsum and num(r[c]) is not None and abs(rsum[k] - num(r[c])) > 1e-6:
            reason_total_diffs.append((*k, rsum[k], r[c]))

# ---------- 7. 06 statutes ----------
mine = defaultdict(Counter)
for r in statutes:
    mine[(r["Agency"], r["Fiscal Year"], r["Row Type"], r["Component"], r["Component Name"])][
        (r["Statute"], r["Type of Information Withheld"], r["Case Citation"], r["Number of Times Relied Upon"])] += 1
theirs = defaultdict(Counter)
for (agency, fy), (at, recs, sts, one) in SITE.items():
    total_of = {s[0] for s in sts if s[1] == "TOTAL" and s[5] != ""}
    for i, o, st, info, case, q in sts:
        if o == "TOTAL":
            if one and q == "":
                continue
            k = ("agency_overall", "Agency Overall", agency)
        elif one:
            if i in total_of:
                continue
            k = ("agency_overall", "Agency Overall", agency)
        else:
            k = ("component" if o else "no_component", *(o or ("", "")))
        theirs[(agency, fy, *k)][(st, info, case, q)] += 1
for k in set(mine) | set(theirs):
    cells[("7 06 vs API", "", report("7 06 vs API", k[0], k[1], "|".join(k[2:]), "statutes", str(sum(mine[k].values())),
                                     str(sum(theirs[k].values())), "same" if mine[k] == theirs[k] else "differ"))] += 1
ag06 = defaultdict(Counter)
for r in read(os.path.join(AGD, "exemption_statutes_FY2008-2025.csv")):
    ag06[(r["Agency"], r["Fiscal Year"])][(clean_text(r["Statute"]), num(r["Number of Times Relied Upon"]) or 0)] += 1
mine06 = defaultdict(Counter)
for r in statutes:
    if r["Row Type"] == "agency_overall":
        mine06[(r["Agency"], r["Fiscal Year"])][(r["Statute"], num(r["Number of Times Relied Upon"]) or 0)] += 1
for k in set(ag06) | set(mine06):
    a = Counter({x: n for x, n in ag06[k].items() if x[1]})
    b = Counter({x: n for x, n in mine06[k].items() if x[1]})
    cells[("7 06 Agency Overall vs agency statute table", "", report("7 06 Agency Overall vs agency statute table", k[0], k[1], "Agency Overall",
                                                                      "statutes", str(sum(x[1] * n for x, n in b.items())), str(sum(x[1] * n for x, n in a.items())),
                                                                      "same" if a == b else "differ"))] += 1

# ---------- known differences: each must still be there, nothing else may be ----------
SITE_CSV_BLANK = "foia.gov's CSV export (the agency-level table) leaves this blank; the API report has the value"
KNOWN = {
    "3 Agency Overall vs agency table": {("Small Business Administration", "2021"): SITE_CSV_BLANK,
                                         ("Council on Environmental Quality", "2023"): SITE_CSV_BLANK},
    "4 parts vs Agency Overall": {(a, f): "the site's components do not add up to its own agency total" for a, f in [
        ("Department of Agriculture", "2025"), ("Department of Commerce", "2025"), ("Department of Defense", "2025"),
        ("Department of Labor", "2025"), ("Department of Veterans Affairs", "2025"), ("Environmental Protection Agency", "2011"),
        ("Equal Employment Opportunity Commission", "2025"), ("General Services Administration", "2016"),
        ("United States Postal Service", "2010"), ("United States Postal Service", "2013"),
        ("United States Postal Service", "2014"), ("United States Postal Service", "2016"),
        ("United States Postal Service", "2017")]},
    "reason totals": {("Department of Energy", "2025"): "HQ appeal reasons add up to 49, its total says 45 (as on the site)"},
}
found = defaultdict(set)
for check, agency, fy, *_ in results:
    found[check].add((agency, fy))
found["4 parts vs Agency Overall"] = {(a, f) for a, f, *_ in sums}
found["reason totals"] = {(x[0], x[1]) for x in reason_total_diffs}
for check in set(found) | set(KNOWN):
    extra = found[check] - set(KNOWN.get(check, {}))
    gone = set(KNOWN.get(check, {})) - found[check]
    if extra:
        problems.append(f"{check}: not explained: {sorted(extra)[:10]} ({len(extra)})")
    if gone:
        problems.append(f"{check}: listed as known but not found any more: {sorted(gone)}")

# ---------- output ----------
with open(os.path.join(OUT, "differences.csv"), "w", newline="", encoding="utf-8") as h:
    w = csv.writer(h)
    w.writerow(["check", "agency", "fiscal_year", "row", "column", "table_value", "reference_value", "class"])
    w.writerows(results)
with open(os.path.join(OUT, "component_sums.csv"), "w", newline="", encoding="utf-8") as h:
    w = csv.writer(h)
    w.writerow(["agency", "fiscal_year", "column", "parts_added", "agency_overall"])
    w.writerows(sums)
with open(os.path.join(OUT, "reason_totals.csv"), "w", newline="", encoding="utf-8") as h:
    w = csv.writer(h)
    w.writerow(["agency", "fiscal_year", "type", "row_type", "component", "component_name", "reasons_added", "total_column"])
    w.writerows(reason_total_diffs)
with open(os.path.join(OUT, "summary.txt"), "w", encoding="utf-8") as h:
    for x in [f"rows: {dict(rt)} | reasons {len(reasons)} | statutes {len(statutes)}", f"structure problems: {len(problems)}"] + problems[:50]:
        print(x, file=h)
        print(x)
    for k, v in sorted(cells.items()):
        print(k, v, file=h)
        print(k, v)
    print("reason totals that differ:", len(reason_total_diffs), file=h)
    print("reason totals that differ:", len(reason_total_diffs))
sys.exit(1 if problems else 0)
