"""把 component_v3/analysis 的 31 张表合成一张宽表（06 号法条、未归属行暂不放）。

一行 = 一个年份 × 一个机构 × 一个部门（含 Agency Overall）；列 = 31 张表的全部字段，
列名前加 foia.gov 数据类型编号（01–32）。值原样照抄：空白仍是空白，0 和 N/A 不改。

用法：
    python3 build_component_master.py <component_v3/analysis> <输出目录>
输出：
    component_master.csv   总表
    _columns.csv           每一列来自哪张表、哪个字段
    _coverage.csv          每行 × 31 种数据类型：value / all_na / blank / absent
    _key_collisions.csv    原始 XML 同一张表里同一部门填了两次：内容相同只留一份；不同则第二份单独成行，
                           Level = duplicate_entry（按 Level 筛选就不会重复计算）
"""
import csv
import os
import sys

csv.field_size_limit(10**9)

META = 17  # analysis 表前 17 列是标识列
LEVELS = {"agency_overall", "component"}  # 未归属、重复填报的合计行暂不放

# XML 节 → foia.gov 数据类型编号和短名（编号顺序 = data.html 下拉菜单 = data_type_map.csv）
SECTIONS = [
    ("ProcessedRequestSection", "01", "Requests"),
    ("RequestDispositionSection", "02", "Disposition"),
    ("RequestDenialOtherReasonSection", "03", "DispositionOtherReasons"),
    ("ExpeditedProcessingSection", "04", "ExpeditedProcessing"),
    ("RequestDispositionAppliedExemptionsSection", "05", "Exemptions"),
    ("ProcessedAppealSection", "07", "Appeals"),
    ("AppealDispositionSection", "08", "AppealsDisposition"),
    ("AppealDispositionAppliedExemptionsSection", "09", "AppealsExemptions"),
    ("AppealNonExemptionDenialSection", "10", "AppealsOtherThanExemptions"),
    ("AppealDenialOtherReasonSection", "11", "AppealsOtherReasons"),
    ("AppealResponseTimeSection", "12", "AppealsResponseTime"),
    ("OldestPendingAppealSection", "13", "AppealsTenOldest"),
    ("ProcessedResponseTimeSection", "14", "ProcessingTime"),
    ("InformationGrantedResponseTimeSection", "15", "ProcessingTimeGranted"),
    ("SimpleResponseTimeIncrementsSection", "16", "SimpleRequests"),
    ("ComplexResponseTimeIncrementsSection", "17", "ComplexRequests"),
    ("ExpeditedResponseTimeIncrementsSection", "18", "ExpeditedRequests"),
    ("PendingPerfectedRequestsSection", "19", "PendingRequests"),
    ("OldestPendingRequestSection", "20", "TenOldestRequests"),
    ("FeeWaiverSection", "21", "FeeWaiver"),
    ("PersonnelAndCostSection", None, None),  # 人员列归 22，费用列归 23，见 personnel_or_cost()
    ("FeesCollectedSection", "23", "Costs"),
    ("SubsectionUsedSection", "24", "Exclusions"),
    ("SubsectionPostSection", "25", "ProactiveDisclosures"),
    ("BacklogSection", "26", "Backlog"),
    ("ProcessedConsultationSection", "27", "Consultations"),
    ("OldestPendingConsultationSection", "28", "ConsultationsTenOldest"),
    ("ProcessedRequestComparisonSection", "29", "Comparisons"),
    ("BackloggedRequestComparisonSection", "30", "ComparisonsRequestsBacklogged"),
    ("ProcessedAppealComparisonSection", "31", "ComparisonsAppeals"),
    ("BackloggedAppealComparisonSection", "32", "ComparisonsAppealsBacklogged"),
]
ID_COLS = ["Fiscal Year", "Agency", "Agency Abbreviation", "Component", "Component Name",
           "Level", "Org Ref ID", "Exclude From Component Sum", "Exclude Reason"]


def personnel_or_cost(field):
    if "Cost" in field:
        return "23", "Costs"
    return "22", "Personnel"


def row_key(r):
    # 机构合计每个机构·年份只有一行（API 补的合计行没有 Org Ref ID，不能按 ID 分）；
    # 部门以 Org Ref ID 为准（USPS 2019 两个部门缩写都是 PS）；API 补的部门行没有 ID，用缩写
    if r["Row Level"] == "agency_overall":
        return (r["FY"], r["Agency Std"], "agency_overall", "Agency Overall")
    return (r["FY"], r["Agency Std"], r["Row Level"], r["Org Ref ID"] or r["Component"])


def main(src, out):
    os.makedirs(out, exist_ok=True)
    rows = {}        # key -> {列名: 值}
    columns = []     # (列名, 编号, 短名, 节, 字段)
    type_cols = {}   # 编号 -> [列名]
    collisions = []

    for sec, no, short in SECTIONS:
        with open(os.path.join(src, sec + ".csv"), newline="") as h:
            reader = csv.reader(h)
            hdr = next(reader)
            fields = hdr[META:]
            names = []
            for f in fields:
                n, s = personnel_or_cost(f) if no is None else (no, short)
                name = f"{n}_{s}__{f}"
                names.append(name)
                columns.append((name, n, s, sec, f))
                type_cols.setdefault(n, []).append(name)
            seen = {}
            for vals in reader:
                r = dict(zip(hdr, vals))
                if r["Row Level"] not in LEVELS:
                    continue
                k = row_key(r)
                level = r["Row Level"]
                if k in seen:
                    if seen[k] == vals[META:]:
                        collisions.append([sec, *k, r["Component Name"], r["Row Key"], "identical, dropped"])
                        continue
                    n = sum(1 for x in rows if x[:4] == k) + 1
                    k, level = k + (f"dup{n}",), "duplicate_entry"
                    collisions.append([sec, *k[:4], r["Component Name"], r["Row Key"], "different, own row"])
                else:
                    seen[k] = vals[META:]
                row = rows.setdefault(k, {"Fiscal Year": r["FY"], "Agency": r["Agency Std"],
                                          "Agency Abbreviation": r["Agency Abbreviation"],
                                          "Component": r["Component"], "Component Name": r["Component Name"],
                                          "Level": level, "Org Ref ID": r["Org Ref ID"],
                                          "Exclude From Component Sum": "", "Exclude Reason": ""})
                if not row["Org Ref ID"] and r["Org Ref ID"]:
                    row["Org Ref ID"] = r["Org Ref ID"]
                if not row["Component Name"] and r["Component Name"]:
                    row["Component Name"] = r["Component Name"]
                if r["Exclude From Component Sum"] == "yes":
                    row["Exclude From Component Sum"] = "yes"
                    row["Exclude Reason"] = row["Exclude Reason"] or r["Exclude Reason"]
                for name, v in zip(names, vals[META:]):
                    row[name] = v

    # 机构合计在前，部门按名字排
    order = sorted(rows, key=lambda k: (k[0], rows[k]["Agency"], k[2] != "agency_overall",
                                        rows[k]["Component"], k[3:]))
    header = ID_COLS + [c[0] for c in columns]
    with open(os.path.join(out, "component_master.csv"), "w", newline="") as h:
        w = csv.writer(h)
        w.writerow(header)
        for k in order:
            w.writerow([rows[k].get(c, "") for c in header])

    with open(os.path.join(out, "_columns.csv"), "w", newline="") as h:
        w = csv.writer(h)
        w.writerow(["column", "data_type_no", "data_type", "source_section", "source_field"])
        w.writerows(columns)

    nos = sorted(type_cols)
    with open(os.path.join(out, "_coverage.csv"), "w", newline="") as h:
        w = csv.writer(h)
        w.writerow(ID_COLS[:6] + nos)
        for k in order:
            row, cov = rows[k], []
            for n in nos:
                present = [c for c in type_cols[n] if c in row]
                vals = [row[c].strip() for c in present]
                if not present:
                    cov.append("absent")           # 这张表里没有这个部门的行
                elif all(v == "" for v in vals):
                    cov.append("blank")
                elif all(v == "" or v.upper() == "N/A" for v in vals):
                    cov.append("all_na")
                else:
                    cov.append("value")
            w.writerow([row[c] for c in ID_COLS[:6]] + cov)

    with open(os.path.join(out, "_key_collisions.csv"), "w", newline="") as h:
        w = csv.writer(h)
        w.writerow(["section", "FY", "Agency", "Level", "Org Ref ID or Component", "Component Name", "Row Key", "action"])
        w.writerows(collisions)

    print(f"rows {len(rows)}  columns {len(header)} ({len(columns)} data)  collisions {len(collisions)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
