"""Build the one data file the dashboard reads: data/foia.json.

Rows: one per agency per year (agency level) plus one per component per year (component level).
Columns: every numeric column of the component master table (named as there, e.g.
01_Requests__ProcessingStatisticsReceivedQuantity).

Where the values come from: one table, component_master_no_03_06_11.csv (built from the foia.gov API).
- agency rows: its "agency_overall" rows (one per agency per year).
- component rows: its "component" rows. A "second_entry" row (a
  second entry the agency reported for the same component in one table) is added into its component: summed
  where the column can be added up, otherwise the first entry is kept. Rows marked "Exclude From Component Sum"
  and "no_component" rows (numbers foia.gov links to no component) are left out; the page shows the latter as
  the agency total minus its components.
  Components are told apart by code and name: "Key" is the code, or "code · name" where one agency uses the
  same code for two components (USPS "PS" FY2019-2024).
Labels: foia.gov's own CSV column names, from column_mapping.csv.
Renamed agencies keep one name for every year (RENAMED: "Department of War" -> "Department of Defense"), so a
rename in the reports does not split an agency in two; the page decides how the name is shown.

How values are read: commas removed; blank and N/A spellings -> null (missing, never 0);
"<1" (less than one day) -> 0.5, and its position is listed under "lt1" so the page can show "<1".
Receipt-date columns (text) are left out.

Usage:
    python prep.py --components <component_master_no_03_06_11.csv>
                   [--types <data_type_map.csv>] [--mapping column_mapping.csv] [--out data]
"""
import argparse
import datetime
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA_COL = re.compile(r"\d\d_")  # data columns start with the data type number; the ID columns come first
MISSING = {"", "N/A", "NA", "N.A", "N\\A", "N/A/", "0N/A", "INVALID DATE ENTERED"}  # compared in upper case
SEEN_MISSING = {}  # text read as missing, reported at the end
NOT_ADDABLE = re.compile(r"Days|Median|Average|Highest|Lowest|Percent|OldItem")
# renamed agencies -> one name for every year. Without this, a report filed under the new name would split the agency
# in two: it would drop out of the agencies that reported every year (cohort), lose the next year's restated backlog,
# and its components would not match across the change. The page shows "Department of War (Department of Defense)".
RENAMED = {"Department of War": "Department of Defense"}


def parse(series, col, lt1):
    """Strings -> numbers (None for missing); appends to lt1 the positions where "<1" was."""
    out = []
    for i, v in enumerate(series):
        v = v.strip()
        if v.upper() in MISSING or not re.search(r"\d", v):  # N/A in any spelling ("N/", "n/a", ...)
            out.append(None)
            if v:
                SEEN_MISSING[v] = SEEN_MISSING.get(v, 0) + 1
        elif v == "<1":
            out.append(0.5)
            lt1.append(i)
        else:
            try:
                x = float(v.replace(",", ""))
            except ValueError:
                raise ValueError(f"unexpected value {v!r} in {col}")
            out.append(int(x) if x.is_integer() else round(x, 4))
    return out


def merge_second_entries(c, data_cols):
    """Component rows, with each second_entry row added into the component row it belongs to."""
    keep = c[(c["Row Type"] == "component") & (c["Exclude From Component Sum"] == "")].reset_index(drop=True)
    pos = {k: i for i, k in enumerate(zip(keep["Fiscal Year"], keep["Agency"], keep["Component"], keep["Component Name"]))}
    as_num = lambda v: None if v.strip().upper() in MISSING or not re.search(r"\d", v) or v.strip() == "<1" else float(v.replace(",", ""))
    for _, r in c[c["Row Type"] == "second_entry"].iterrows():
        i = pos.get((r["Fiscal Year"], r["Agency"], r["Component"], r["Component Name"]))
        if i is None:
            continue  # a second entry of numbers linked to no component: left out like the no_component rows
        for col in data_cols:
            v = r[col].strip()
            if not v:
                continue
            first = keep.at[i, col].strip()
            if NOT_ADDABLE.search(col.split("__", 1)[1]):
                if not first:
                    keep.at[i, col] = v
            elif as_num(v) is not None:
                total = (as_num(first) or 0) + as_num(v)
                keep.at[i, col] = str(int(total)) if total.is_integer() else str(round(total, 4))
    names = keep.groupby(["Agency", "Component"])["Component Name"].nunique()
    shared = set(names[names > 1].index)
    keep["Key"] = [f"{code} · {name}" if (a, code) in shared else code
                   for a, code, name in zip(keep["Agency"], keep["Component"], keep["Component Name"])]
    return keep


def label(field):
    """XML field name -> words, e.g. ProcessingStatisticsReceivedQuantity -> Processing Statistics Received Quantity."""
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", field.replace(".", " · "))


def main(components_csv, types_csv, mapping_csv, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    c = pd.read_csv(components_csv, dtype=str, keep_default_na=False)
    renamed = c["Agency"].isin(RENAMED.keys())
    if renamed.any():
        print("renamed agencies:", {k: int(v) for k, v in c.loc[renamed, "Agency"].value_counts().items()}, "rows ->", RENAMED)
    c["Agency"] = c["Agency"].replace(RENAMED)
    types = pd.read_csv(types_csv, dtype=str, keep_default_na=False)
    mapping = pd.read_csv(mapping_csv, dtype=str, keep_default_na=False)
    by_no = {r["No."].zfill(2): r for _, r in types.iterrows()}
    data_cols = [x for x in c.columns if DATA_COL.match(x)]
    agency = c[c["Row Type"] == "agency_overall"].reset_index(drop=True)
    if agency.duplicated(["Agency", "Fiscal Year"]).any():
        raise ValueError("more than one agency_overall row for an agency-year")
    comp = merge_second_entries(c, data_cols)
    n_a, n_c = len(agency), len(comp)

    # numeric columns of the component master
    columns, values, lt1 = [], {}, {}
    for col in data_cols:
        no, field = col.split("_", 1)[0], col.split("__", 1)[1]
        if field.endswith("ReceiptDate"):
            continue
        t = by_no[no]
        hit = mapping[(mapping.table == "foia-" + t["Official file name (foia-*.csv)"]) & (mapping.xml_col == field)]
        if len(hit) != 1:
            raise ValueError(f"no single foia.gov CSV column name for {col}: {list(hit.csv_col)}")
        a_lt1, c_lt1 = [], []
        values[col] = parse(agency[col], col, a_lt1) + parse(comp[col], col, c_lt1)
        if a_lt1 or c_lt1:
            lt1[col] = a_lt1 + [n_a + i for i in c_lt1]
        # label: foia.gov's own CSV column name (e.g. "Number of Requests Received in Fiscal Year"); field: the XML name
        columns.append({"key": col, "no": no, "type": t["foia.gov data type"], "label": hit.csv_col.iloc[0],
                        "field": label(field), "addable": not NOT_ADDABLE.search(field)})

    fy = [int(x) for x in agency["Fiscal Year"]] + [int(x) for x in comp["Fiscal Year"]]
    ag = list(agency["Agency"]) + list(comp["Agency"])
    code = [""] * n_a + list(comp["Component"])
    key = [""] * n_a + list(comp["Key"])
    name = list(agency["Agency"]) + list(comp["Component Name"])
    level = ["agency"] * n_a + ["component"] * n_c

    # cohort: agencies with an agency row in every year
    years = agency.groupby("Agency")["Fiscal Year"].nunique()
    cohort_set = set(years[years == agency["Fiscal Year"].nunique()].index)
    cohort = [x in cohort_set for x in ag]

    # backlog as restated in the next year's report (table 30, "last year" figure), same agency / component
    last = values["30_ComparisonsRequestsBacklogged__BacklogLastYearQuantity"]
    nxt = {(lv, x, k, f - 1): v for lv, x, k, f, v in zip(level, ag, key, fy, last) if v is not None}
    restated = [nxt.get((lv, x, k, f)) for lv, x, k, f in zip(level, ag, key, fy)]

    blob = {"built": datetime.date.today().isoformat(), "ids": {"FY": fy, "Agency": ag, "Component": code, "Key": key, "Name": name, "level": level, "cohort": cohort},
            "columns": columns, "values": values, "lt1": lt1, "backlog_restated": restated}
    (out / "foia.json").write_text(json.dumps(blob, separators=(",", ":")))
    print(f"rows {n_a + n_c} (agency {n_a}, component {n_c}) | columns {len(columns)} | "
          f"agencies {len(set(ag))}, cohort {len(cohort_set)} | '<1' cells {sum(map(len, lt1.values()))}")
    print(f"foia.json: {(out / 'foia.json').stat().st_size:,} bytes")
    print("read as missing:", dict(sorted(SEEN_MISSING.items(), key=lambda kv: -kv[1])))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build the dashboard's data file.")
    ap.add_argument("--components", required=True, help="fa26/dataset/component_level/component_master_no_03_06_11.csv")
    ap.add_argument("--types", help="fa26/dataset/data_type_map.csv (default: the folder above the component table's folder)")
    ap.add_argument("--mapping", default=str(HERE / "column_mapping.csv"), help="foia.gov CSV column name for each component-table column")
    ap.add_argument("--out", default=str(HERE / "data"), help="output folder (default: data/ next to this script)")
    args = ap.parse_args()
    types = args.types or str(Path(args.components).resolve().parent.parent / "data_type_map.csv")
    main(args.components, types, args.mapping, args.out)
