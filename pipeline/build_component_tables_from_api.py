"""Build the three component-level tables from the foia.gov API annual reports.

  component_master_no_03_06_11.csv  one row per fiscal year x agency x component, plus one Agency Overall row;
                                    8 ID columns and 244 data columns
  other_reasons_03_11.csv           03 / 11 "other" reasons, one row per component per reason
  exemption_statutes_06.csv         06 Exemption 3 statutes, one row per component per statute

Values are copied as the API gives them (blank, 0, N/A and "<1" kept); the 03/11 and 06 text gets clean_text()
(formatting only). Column names come from field_map.csv (API field -> column).

Row types:
- agency_overall: the report's agency totals (field_overall_*; two are linked by hand, see OVERALL_EXTRA). A report
  for a single organization gets no component rows; where a total is blank, its own record is used.
- component: every component with a record in the report, including one that appears only in the 06 statutes.
- second_entry: a second record for the same component in one table (foia.gov counts both).
- no_component: a record foia.gov links to no component.
- Commerce FY2025 "DOC" repeats the agency total and is marked Exclude From Component Sum.

Usage: python build_component_tables_from_api.py <api dir> <field_map.csv> <report_data_map.json>
       <FOIA_agency_FY2008-2025.csv> <component_master_no_03_06_11.csv (existing, for the column list)>
       <data_type_map.csv> <out dir>
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
import foia_fields as ff  # noqa: E402
from foia_fields import SECTIONS, clean_text, summable  # noqa: E402

csv.field_size_limit(10**9)
API_DIR, FMAP, DMAP, AGENCY, OLD_MASTER, TYPES, OUT = sys.argv[1:8]
os.makedirs(OUT, exist_ok=True)
ID_COLS = ["Fiscal Year", "Agency", "Agency Abbreviation", "Component", "Component Name", "Row Type",
           "Exclude From Component Sum", "Exclude Reason"]
EXCLUDE = {("Department of Commerce", "2025", "DOC"):
           "DOC / Departmental Offices repeats the Agency Overall numbers; a duplicate total, not a separate component"}
EXCLUDE_06 = "DOC / Departmental Offices is a duplicate total (here it equals the other components combined), not a separate component"
ORDER = {"agency_overall": 0, "component": 1, "second_entry": 2, "no_component": 3}
low = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
log = Counter()


def num(v):
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None


def fmt(x):
    return str(int(x)) if float(x).is_integer() else f"{x:.4f}".rstrip("0").rstrip(".")


# ---------- columns ----------
MCOLS = [c for c in next(csv.reader(open(OLD_MASTER, newline="", encoding="utf-8"))) if re.match(r"\d\d_", c)]  # data columns
assert len(MCOLS) == 244, len(MCOLS)
fmap, overall = ff.load_maps(FMAP, DMAP)
# the site's data map names these two record fields field_not_agency_rec / field_rec_not_reasonably_desc, but the
# records use field_not_agency_record / field_rec_not_desc, so load_maps() cannot link their agency totals
OVERALL_EXTRA = {("AppealNonExemptionDenialSection", "NonExemptionDenialQuantity[NotAgency]"): "field_overall_vic2_not_agency_re",
                 ("AppealNonExemptionDenialSection", "NonExemptionDenialQuantity[NotDescribed]"): "field_overall_vic2_rec_not_desc"}
assert not set(OVERALL_EXTRA) & set(overall)
overall.update(OVERALL_EXTRA)
HAS = {(sec, col) for (sec, _), col in fmap.items()}
SEC_OF_NO = defaultdict(list)
for sec, no, _ in SECTIONS:
    for n in ([no] if no else ["22", "23"]):
        SEC_OF_NO[n].append(sec)
COL_SF = {}
for c in MCOLS:
    no, field = c.split("_", 1)[0], c.split("__", 1)[1]
    hit = [s for s in SEC_OF_NO[no] if (s, field) in HAS]
    assert len(hit) == 1, (c, hit)
    COL_SF[c] = (hit[0], field)
SEC_COLS = defaultdict(list)
for c, (sec, field) in COL_SF.items():
    SEC_COLS[sec].append(c)
TYPE_NAME = {r["No."].zfill(2): r["foia.gov data type"] for r in csv.DictReader(open(TYPES, newline="", encoding="utf-8"))}
REASON_SEC = {"RequestDenialOtherReasonSection": "03", "AppealDenialOtherReasonSection": "11"}

# ---------- agency names: the agency table's spelling ----------
agency_rows = list(csv.DictReader(open(AGENCY, newline="", encoding="utf-8")))
table_names = defaultdict(set)
for r in agency_rows:
    table_names[r["Fiscal Year"]].add(r["Agency"])
index = {r["id"]: r for r in json.load(open(os.path.join(API_DIR, "_index.json")))}


def table_name(site, fy):
    if site in table_names[fy]:
        return site
    hit = [n for n in table_names[fy] if low(n) == low(site) or low(site).replace("us", "", 1) == low(n)]
    assert len(hit) == 1, (site, fy, hit)
    return hit[0]


# ---------- one report ----------
def report(path):
    d = json.load(gzip.open(path, "rt", encoding="utf-8"))
    rep, inc = d["data"], {x["id"]: x for x in d.get("included", [])}
    at = rep["attributes"]
    fy = str(at.get("field_foia_annual_report_yr"))
    agency = table_name(index[rep["id"]]["agency"], fy)
    ag = next((x["attributes"] for x in inc.values() if x["type"] == "agency"), {})
    comp_of = lambda rel: ((rel or {}).get("data") or {}).get("id")
    comps = {}  # component node id -> (code, name)
    recs = defaultdict(list)  # section -> [(node id or None, {column: value}, {reason: qty})]
    statutes = []  # (statute no., node id or None or "TOTAL", statute, info, case, qty); "TOTAL" = the agency total
    for seg, sec in ff.SEG.items():
        rel = (rep["relationships"].get(seg) or {}).get("data") or []
        for pi, p in enumerate(rel if isinstance(rel, list) else [rel]):
            para = inc.get(p["id"])
            if not para:
                continue
            a = para["attributes"]
            if seg == "field_statute_iv":
                text = (ff.val(a.get("field_statute")), ff.val(a.get("field_type_of_info_withheld")),
                        ff.val(a.get("field_case_citation")))
                statutes.append((pi, "TOTAL", *text, ff.val(a.get("field_total_num_relied_by_agency"))))
                for q in (para["relationships"].get("field_agency_component_inf") or {}).get("data") or []:
                    det = inc.get(q["id"])
                    if det:
                        cid = comp_of(det["relationships"].get("field_agency_component"))
                        if cid in inc:
                            comps[cid] = (ff.ws(inc[cid]["attributes"].get("abbreviation")), ff.ws(inc[cid]["attributes"].get("title")))
                        statutes.append((pi, cid if cid in inc else None, *text,
                                         ff.val(det["attributes"].get("field_num_relied_by_agency_comp"))))
                continue
            cid = comp_of(para["relationships"].get("field_agency_component"))
            if cid in inc:
                comps[cid] = (ff.ws(inc[cid]["attributes"].get("abbreviation")), ff.ws(inc[cid]["attributes"].get("title")))
            vals = {}
            for k, v in a.items():
                col = fmap.get((sec, k))
                if col and ff.val(v) != "":
                    vals[col] = ff.val(v)
            reasons = []
            for q in (para["relationships"].get(ff.NESTED.get(seg, "")) or {}).get("data") or []:
                det = inc.get(q["id"])
                if det:
                    x = det["attributes"]
                    reasons.append((ff.val(x.get("field_desc_oth_reasons")),
                                    next((ff.val(v) for k, v in x.items() if k.startswith("field_num")), "")))
            recs[sec].append((cid if cid in inc else None, vals, reasons))
    return fy, agency, ff.ws(ag.get("abbreviation")), at, comps, recs, statutes


def agency_total(at, recs, one_org, sec, field):
    of = overall.get((sec, field))
    if of and ff.val(at.get(of)) != "":
        return ff.val(at.get(of))
    rows = [v.get(field, "") for _, v, _ in recs.get(sec, [])]
    rows = [v for v in rows if v != ""]
    if one_org:
        if len(rows) > 1:
            log["one-organization report with 2 records in a table"] += 1
            if summable(field) and all(num(v) is not None for v in rows):
                return fmt(sum(num(v) for v in rows))
        return rows[0] if rows else ""
    if of:
        return ""
    vals = [num(v) for v in rows]
    vals = [v for v in vals if v is not None]
    return fmt(sum(vals)) if vals and summable(field) else ""


master, reasons_out, statutes_out = [], [], []
for path in sorted(glob.glob(os.path.join(API_DIR, "*", "*.json.gz"))):
    fy, agency, abbr, at, comps, recs, statutes = report(path)
    owners = defaultdict(set)  # table -> components with a record in it (None = no component)
    for sec, rs in recs.items():
        owners[sec] |= {cid for cid, _, _ in rs}
    owners["Exemption3StatuteSection"] |= {s[1] for s in statutes if s[1] != "TOTAL"}
    named = {c for v in owners.values() for c in v if c}
    # one organization: no component, or one component and no table where it sits next to unlinked records
    one_org = not named or (len(named) == 1 and not any(len(v) > 1 for v in owners.values()))
    base = lambda code, name, rt, excl="": {"Fiscal Year": fy, "Agency": agency, "Agency Abbreviation": abbr,
                                           "Component": code, "Component Name": name, "Row Type": rt,
                                           "Exclude From Component Sum": "yes" if excl else "", "Exclude Reason": excl}
    ov = base("Agency Overall", agency, "agency_overall")
    for c in MCOLS:
        sec, field = COL_SF[c]
        ov[c] = agency_total(at, recs, one_org, sec, field)
    rows = [ov]
    if not one_org:
        made = {}  # (node, entry) -> row
        for sec, rs in recs.items():
            seen = Counter()
            for cid, vals, _ in rs:
                seen[cid] += 1
                k = seen[cid]
                assert k <= 2, (agency, fy, sec, cid)
                if (cid, k) not in made:
                    code, name = comps[cid] if cid else ("", "")
                    rt = "second_entry" if k == 2 else "component" if cid else "no_component"
                    made[(cid, k)] = base(code, name, rt, EXCLUDE.get((agency, fy, code), "") if cid else "")
                    made[(cid, k)].update({c: "" for c in MCOLS})
                    if k == 2:
                        log[f"second_entry rows ({'component' if cid else 'no component'})"] += 1
                for c in SEC_COLS.get(sec, []):
                    made[(cid, k)][c] = vals.get(COL_SF[c][1], "")
        for cid in {s[1] for s in statutes if s[1] != "TOTAL"}:  # components with statutes only
            if (cid, 1) not in made:
                code, name = comps[cid] if cid else ("", "")
                made[(cid, 1)] = base(code, name, "component" if cid else "no_component",
                                      EXCLUDE.get((agency, fy, code), "") if cid else "")
                made[(cid, 1)].update({c: "" for c in MCOLS})
                log["rows for components that have statutes only"] += 1
        rows += list(made.values())
    master += rows
    # 03 / 11 reasons
    for sec, no in REASON_SEC.items():
        seen = Counter()
        for cid, vals, reasons in recs.get(sec, []):
            seen[cid] += 1
            if one_org:
                r0 = base("Agency Overall", agency, "agency_overall")
            else:
                code, name = comps[cid] if cid else ("", "")
                rt = "second_entry" if seen[cid] == 2 else "component" if cid else "no_component"
                r0 = base(code, name, rt, EXCLUDE.get((agency, fy, code), "") if cid else "")
            for text, q in reasons:
                reasons_out.append({**r0, "Data Type No.": no, "Data Type": TYPE_NAME[no], "Reason": clean_text(text), "Quantity": q})
    # 06 statutes
    has_total = {s[0] for s in statutes if s[1] == "TOTAL" and s[5] != ""}
    for pi, cid, st, info, case, q in statutes:
        if cid == "TOTAL":
            if one_org and q == "":
                continue  # one organization, no total written: its own entry below is the total
            r0 = base("Agency Overall", agency, "agency_overall")
        elif one_org:
            if pi in has_total:
                continue  # the agency total of this statute is already there
            r0 = base("Agency Overall", agency, "agency_overall")
        else:
            code, name = comps[cid] if cid else ("", "")
            r0 = base(code, name, "component" if cid else "no_component",
                      EXCLUDE_06 if (agency, fy, code) in EXCLUDE else "")
        statutes_out.append({**r0, "Statute": clean_text(st), "Type of Information Withheld": clean_text(info),
                             "Case Citation": clean_text(case), "Number of Times Relied Upon": q})

key = lambda r: (r["Fiscal Year"], r["Agency"], ORDER[r["Row Type"]], r["Component"], r["Component Name"])
master.sort(key=key)
k = Counter((r["Fiscal Year"], r["Agency"], r["Row Type"], r["Component"], r["Component Name"]) for r in master)
assert max(k.values()) == 1, [x for x, n in k.items() if n > 1][:5]
reasons_out.sort(key=lambda r: key(r) + (r["Data Type No."],))
statutes_out.sort(key=key)


def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


write("component_master_no_03_06_11.csv", ID_COLS + MCOLS, master)
write("other_reasons_03_11.csv", ID_COLS + ["Data Type No.", "Data Type", "Reason", "Quantity"], reasons_out)
write("exemption_statutes_06.csv", ID_COLS + ["Statute", "Type of Information Withheld", "Case Citation",
                                              "Number of Times Relied Upon"], statutes_out)
print("master", len(master), Counter(r["Row Type"] for r in master), "| reasons", len(reasons_out),
      "| statutes", len(statutes_out), "| agency-years", len({(r["Fiscal Year"], r["Agency"]) for r in master}))
print(dict(log))
