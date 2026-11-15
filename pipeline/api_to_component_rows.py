"""把 foia.gov API 年报（JSON）转成与 component_v3/raw 同格式的行，用来补 XML zip 里没有的机构·年份。

为什么需要：foia.gov 的 XML 整年 zip 是手工打包的快照，漏了 10 个机构·年份（文件缺失、存成网页错误页、或装了别家的年报），
而 API（网站当前数据库）里这些年报都有。

字段对应：
- 部门行：API 段字段 → XML 列，用 API vs XML 全量对照学到并核对过的 field_map.csv（checks/api_vs_xml_1019/）
- 机构合计行（多部门机构）：report_data_map.json 的 overall_field → 段字段 → XML 列
- 单一机构（只有一个部门）：那一条就是 Agency Overall（与 XML 的 ORG0 行对应）
- "其他理由"按理由文字展开成 OtherDenialReasonQuantity[文字]；法条每条一行

用法：
    python api_to_component_rows.py check <api 目录> <component_v3 目录> <field_map.csv> <report_data_map.json> <输出目录>
        —— 转换 XML 里已有的机构·年份，与 raw 逐格比，验证转换规则
    python api_to_component_rows.py fill  <api 目录> <component_v3 目录> <field_map.csv> <report_data_map.json>
        —— 转换 coverage.csv 里 in_xml = no 的机构·年份，写到 component_v3/raw_api/
    python api_to_component_rows.py statutes <api 目录> <component_v3 目录> <field_map.csv> <report_data_map.json> AGENCY|YEAR ...
        —— 只转这些机构·年份的法条表，写到 component_v3/raw_api_statutes/（build 时替换 XML 的法条行）
"""
import csv
import glob
import gzip
import json
import os
import re
import sys
from collections import Counter, defaultdict

# API 段 → XML Section（与 compare_api_vs_xml.py 相同）
SEG = {
    "field_foia_requests_va": "ProcessedRequestSection",
    "field_foia_requests_vb1": "RequestDispositionSection",
    "field_foia_requests_vb2": "RequestDenialOtherReasonSection",
    "field_foia_requests_vb3": "RequestDispositionAppliedExemptionsSection",
    "field_statute_iv": "Exemption3StatuteSection",
    "field_admin_app_via": "ProcessedAppealSection",
    "field_admin_app_vib": "AppealDispositionSection",
    "field_admin_app_vic1": "AppealDispositionAppliedExemptionsSection",
    "field_admin_app_vic2": "AppealNonExemptionDenialSection",
    "field_admin_app_vic3": "AppealDenialOtherReasonSection",
    "field_admin_app_vic4": "AppealResponseTimeSection",
    "field_admin_app_vic5": "OldestPendingAppealSection",
    "field_proc_req_viia": "ProcessedResponseTimeSection",
    "field_proc_req_viib": "InformationGrantedResponseTimeSection",
    "field_proc_req_viic1": "SimpleResponseTimeIncrementsSection",
    "field_proc_req_viic2": "ComplexResponseTimeIncrementsSection",
    "field_proc_req_viic3": "ExpeditedResponseTimeIncrementsSection",
    "field_pending_requests_vii_d_": "PendingPerfectedRequestsSection",
    "field_admin_app_viie": "OldestPendingRequestSection",
    "field_req_viiia": "ExpeditedProcessingSection",
    "field_req_viiib": "FeeWaiverSection",
    "field_foia_pers_costs_ix": "PersonnelAndCostSection",
    "field_fees_x": "FeesCollectedSection",
    "field_sub_xia": "SubsectionUsedSection",
    "field_sub_xib": "SubsectionPostSection",
    "field_foia_xiia": "BacklogSection",
    "field_foia_xiib": "ProcessedConsultationSection",
    "field_foia_xiic": "OldestPendingConsultationSection",
    "field_foia_xiid1": "ProcessedRequestComparisonSection",
    "field_foia_xiid2": "BackloggedRequestComparisonSection",
    "field_foia_xiie1": "ProcessedAppealComparisonSection",
    "field_foia_xiie2": "BackloggedAppealComparisonSection",
}

NESTED = {"field_foia_requests_vb2": "field_foia_req_vb2_info", "field_admin_app_vic3": "field_admin_app_vic3_info"}

csv.field_size_limit(10**9)
ID_COLS = ["Agency", "Agency Abbreviation", "Component", "Component Name", "Fiscal Year", "Source File", "Row Type",
           "Duplicate Of Overall", "Data Item ID", "Org Ref ID", "Assoc Index"]
ws = lambda s: re.sub(r"\s+", " ", (s or "")).strip()


def val(v):
    if isinstance(v, dict):
        v = v.get("value")
    return "" if v is None else ws(str(v))


def load_maps(field_map, data_map):
    fmap = {(r["section"], r["api_field"]): r["xml_col"] for r in csv.DictReader(open(field_map, newline=""))}
    overall = {}  # (section, xml_col) -> field_overall_*
    for g in json.load(open(data_map)):
        for f in g["fields"]:
            if not f.get("overall_field") or "." not in f["id"]:
                continue
            seg, fld = f["id"].split(".", 1)
            sec = SEG.get(seg)
            if sec and (sec, fld) in fmap:
                overall[(sec, fmap[(sec, fld)])] = f["overall_field"]
    return fmap, overall


def convert(path, agency_name, fmap, overall):
    """一份 API 年报 → {Section: [row dict]}。"""
    d = json.load(gzip.open(path, "rt", encoding="utf-8"))
    rep, inc = d["data"], {x["id"]: x for x in d.get("included", [])}
    a = rep["attributes"]
    fy = str(a.get("field_foia_annual_report_yr"))
    ag = next((x["attributes"] for x in inc.values() if x["type"] == "agency"), {})
    abbr = ws(ag.get("abbreviation"))
    comps = [inc[c["id"]]["attributes"] for c in (rep["relationships"].get("field_agency_components") or {}).get("data") or []
             if c["id"] in inc]
    single = len(comps) <= 1
    src = "api:" + os.path.basename(path)
    out = defaultdict(list)

    def base(sec, comp, row_type):
        n = len(out[sec]) + 1
        if row_type == "agency_overall":
            cab, cname, org = "Agency Overall", agency_name, "ORG0"
        else:
            cab, cname, org = ws(comp.get("abbreviation")), ws(comp.get("title")), "API-" + ws(comp.get("abbreviation"))
        return {"Agency": agency_name, "Agency Abbreviation": abbr, "Component": cab, "Component Name": cname,
                "Fiscal Year": fy, "Source File": src, "Row Type": row_type, "Duplicate Of Overall": "",
                "Data Item ID": f"API{n}", "Org Ref ID": org, "Assoc Index": str(n)}

    for seg, sec in SEG.items():
        rel = (rep["relationships"].get(seg) or {}).get("data") or []
        rel = rel if isinstance(rel, list) else [rel]
        if seg == "field_statute_iv":
            for p in rel:
                para = inc.get(p["id"])
                if not para:
                    continue
                st = para["attributes"]
                text = {"StatuteDescriptionText": val(st.get("field_statute")),
                        "ReliedUponStatuteInformationWithheldText": val(st.get("field_type_of_info_withheld")),
                        "Case.CaseTitleText": val(st.get("field_case_citation"))}
                for q in (para["relationships"].get("field_agency_component_inf") or {}).get("data") or []:
                    det = inc.get(q["id"])
                    if not det:
                        continue
                    c = inc.get(((det["relationships"].get("field_agency_component") or {}).get("data") or {}).get("id"), {})
                    r = base(sec, c.get("attributes", {}), "agency_overall" if single else "component")
                    r.update(text, ReliedUponStatuteQuantity=val(det["attributes"].get("field_num_relied_by_agency_comp")))
                    out[sec].append(r)
                if not single:
                    r = base(sec, {}, "agency_overall")
                    r.update(text, ReliedUponStatuteQuantity=val(st.get("field_total_num_relied_by_agency")))
                    out[sec].append(r)
            continue
        for p in rel:
            para = inc.get(p["id"])
            if not para:
                continue
            c = inc.get(((para["relationships"].get("field_agency_component") or {}).get("data") or {}).get("id"), {})
            r = base(sec, c.get("attributes", {}), "agency_overall" if single else "component")
            for k, v in para["attributes"].items():
                col = fmap.get((sec, k))
                if col and val(v) != "":
                    r[col] = val(v)
            if seg in NESTED:
                for q in (para["relationships"].get(NESTED[seg]) or {}).get("data") or []:
                    det = inc.get(q["id"])
                    if det:
                        at = det["attributes"]
                        desc = val(at.get("field_desc_oth_reasons"))
                        n = next((val(v) for k, v in at.items() if k.startswith("field_num")), "")
                        col = f"OtherDenialReasonQuantity[{desc}]"
                        r[col] = n if col not in r else str(float(r[col]) + float(n or 0))
            out[sec].append(r)
        if not single and rel:
            r = base(sec, {}, "agency_overall")
            for (s2, col), of in overall.items():
                if s2 == sec and val(a.get(of)) != "":
                    r[col] = val(a.get(of))
            out[sec].append(r)
    return fy, abbr, single, out


def main(mode, api_dir, v3, field_map, data_map, outdir=None, *_):
    fmap, overall = load_maps(field_map, data_map)
    index = {r["id"]: r for r in json.load(open(f"{api_dir}/_index.json"))}
    cov = list(csv.DictReader(open(f"{v3}/meta/coverage.csv", newline="")))
    files = {}
    for path in glob.glob(f"{api_dir}/*/*.json.gz"):
        rid = json.load(gzip.open(path, "rt", encoding="utf-8"))["data"]["id"]
        files[rid] = path
    alias = {"U.S. Chemical Safety and Hazard Investigation Board": "Chemical Safety and Hazard Investigation Board"}
    by_key = {(alias.get(r["agency"], r["agency"]), r["year"]): files[r["id"]] for r in index.values() if r["id"] in files}

    if mode == "statutes":
        # 法条表与 API 不一致的机构·年份（XML 重复关联被去重、单一机构把分项也写成 Agency Overall 等）：整张法条表改用 API
        targets = [t.split("|") for t in sys.argv[6:]]
        # API 部门缩写是网站现在的写法（DoD 改名后 "DoD IG" 成了 "DoW OIG"）→ 换回同一年 XML 的写法，
        # 用 compare_api_vs_xml.py 在其他表里配好的对（component_pairs.csv，与 field_map.csv 同目录）
        votes = defaultdict(Counter)
        for r in csv.DictReader(open(os.path.join(os.path.dirname(field_map), "component_pairs.csv"), newline="")):
            if r["xml_row_type"] == "component":
                votes[(r["agency"], r["fiscal_year"], r["api_abbr"])][(r["xml_component"], r["xml_component_name"])] += int(r["records"])
        to_xml = {k: c.most_common(1)[0][0] for k, c in votes.items()}
        rows, made, renamed = [], [], Counter()
        for agency, fy in targets:
            path = by_key[(agency, fy)]
            _, abbr, single, out = convert(path, agency, fmap, overall)
            for r in out.get("Exemption3StatuteSection", []):
                if r["Row Type"] == "component":
                    if not r["Component"]:  # 网站上没挂部门的那份数 = XML 的未归属行
                        r.update({"Row Type": "unattributed", "Component": "Unattributed", "Component Name": ""})
                    elif (agency, fy, r["Component"]) in to_xml:
                        new = to_xml[(agency, fy, r["Component"])]
                        renamed[new != (r["Component"], r["Component Name"])] += 1
                        r["Component"], r["Component Name"] = new
                    else:
                        renamed["not found, API name kept"] += 1
                rows.append(r)
            made.append({"agency": agency, "fiscal_year": fy, "source": "api:" + os.path.basename(path),
                         "rows": len(out.get("Exemption3StatuteSection", []))})
        os.makedirs(f"{v3}/raw_api_statutes", exist_ok=True)
        cols = ID_COLS + sorted({k for r in rows for k in r} - set(ID_COLS))
        with open(f"{v3}/raw_api_statutes/Exemption3StatuteSection.csv", "w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
        with open(f"{v3}/meta/api_statute_sources.csv", "w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=list(made[0]))
            w.writeheader()
            w.writerows(made)
        print(len(made), "agency-years,", len(rows), "rows | component names (True = renamed to XML):", dict(renamed))
        return

    if mode == "fill":
        targets = [(r["agency"], r["fiscal_year"][:4]) for r in cov if r["in_xml"] == "no"]
        rows, made = defaultdict(list), []
        for agency, fy in targets:
            path = by_key[(agency, fy)]
            _, abbr, single, out = convert(path, agency, fmap, overall)
            for sec, rs in out.items():
                rows[sec] += rs
            made.append({"agency": agency, "fiscal_year": fy, "agency_abbr": abbr, "source": "api:" + os.path.basename(path),
                         "single_org": single, "sections": len(out), "rows": sum(len(v) for v in out.values())})
        os.makedirs(f"{v3}/raw_api", exist_ok=True)
        for sec, rs in rows.items():
            cols = ID_COLS + sorted({k for r in rs for k in r} - set(ID_COLS))
            with open(f"{v3}/raw_api/{sec}.csv", "w", newline="", encoding="utf-8") as h:
                w = csv.DictWriter(h, fieldnames=cols)
                w.writeheader()
                w.writerows(rs)
        with open(f"{v3}/meta/api_supplement_sources.csv", "w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=list(made[0]))
            w.writeheader()
            w.writerows(made)
        for m in made:
            print(m)
        return

    # check：把 XML 里已有的机构·年份也转一遍，与 raw 比（同机构·年·表·部门的非空单元格）
    raw = defaultdict(dict)
    for f in glob.glob(f"{v3}/raw/*.csv"):
        sec = os.path.basename(f)[:-4]
        if sec == "Exemption3StatuteSection":
            continue
        for r in csv.DictReader(open(f, newline="", encoding="utf-8")):
            if r["Row Type"] not in ("agency_overall", "component"):
                continue
            key = (r["Fiscal Year"][:4], r["Agency Abbreviation"], sec, r["Component"])
            raw[key].update({k: v for k, v in r.items() if k not in ID_COLS and v != ""})
    stats, bad = Counter(), []
    num = lambda v: float(v.replace(",", "")) if re.fullmatch(r"-?[\d,]*\.?\d+", v or "") else None
    for (agency, fy), path in sorted(by_key.items()):
        _, abbr, single, out = convert(path, agency, fmap, overall)
        for sec, rs in out.items():
            if sec == "Exemption3StatuteSection":
                continue
            for r in rs:
                key = (fy, abbr, sec, r["Component"])
                if key not in raw:
                    stats["no matching XML row"] += 1
                    continue
                x = raw[key]
                for col, v in r.items():
                    if col in ID_COLS:
                        continue
                    xv = x.get(col, "")
                    if v == xv or (num(v) is not None and num(v) == num(xv)):
                        stats["same"] += 1
                    elif (v.lower() in ("n/a", "na", "0", "") or num(v) == 0) and (xv.lower() in ("n/a", "na", "0", "") or num(xv) == 0):
                        stats["writing"] += 1
                    else:
                        stats["differ"] += 1
                        bad.append((agency, fy, sec, r["Component"], col, v, xv))
    os.makedirs(outdir, exist_ok=True)
    with open(f"{outdir}/converter_check_diffs.csv", "w", newline="", encoding="utf-8") as h:
        w = csv.writer(h)
        w.writerow(["agency", "fiscal_year", "section", "component", "column", "converted_api", "xml_raw"])
        w.writerows(bad)
    print(dict(stats))


if __name__ == "__main__":
    main(*sys.argv[1:])
