"""Build the dashboard tables from Tianqi's component-level files and load them into Supabase (Postgres).

Inputs (from fa26/dataset/component_level on the fa26-dev branch):
  component_master_no_03_06_11.csv   one row per agency / component per fiscal year
  exemption_statutes_06.csv          Exemption 3 statutes

Outputs (tables, see schema.sql):
  metrics        one row per dashboard metric: key used by the site, column name, how to combine (sum / avg / max)
  agencies       id, name, abbreviation
  components     agency_id, idx, code, name
  foia_rows      fy, agency_id, comp_idx (-1 = agency overall), one numeric column per metric
  statutes_top   top 3 Exemption 3 statutes per agency and year

Usage:
  # write CSVs only (to check them, or to import by hand in the Supabase table editor)
  python build_tables.py --master ../../dataset/component_level/component_master_no_03_06_11.csv \
                         --statutes ../../dataset/component_level/exemption_statutes_06.csv --csv-out out/

  # write schema.sql (run it once in the Supabase SQL editor)
  python build_tables.py --master ... --statutes ... --schema-out schema.sql

  # load straight into the database (replaces all rows). DATABASE_URL = Supabase "Session pooler" connection string
  DATABASE_URL="postgresql://postgres.xxxx:PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres" \
  python build_tables.py --master ... --statutes ... --load

Requires: pandas, numpy, and psycopg[binary] for --load.
"""
import argparse
import io
import os
import re

import numpy as np
import pandas as pd


def num(s):
    if pd.isna(s):
        return np.nan
    s = str(s).strip().replace(",", "")
    if s == "<1":
        return 0.5
    try:
        return float(s)
    except ValueError:
        return np.nan


# ---------------------------------------------------------------- metric definitions
# key -> (list of source columns, kind). kind: sum (counts add up), avg (days / medians), max (oldest item)
P = {}


def add(k, cols, kind="sum"):
    P[k] = (cols if isinstance(cols, list) else [cols], kind)


R = "01_Requests__ProcessingStatistics"
add("req_recv", R + "ReceivedQuantity"); add("req_proc", R + "ProcessedQuantity"); add("req_pend", R + "PendingAtEndQuantity")
D = "02_Disposition__"
add("d_full", D + "RequestDispositionFullGrantQuantity"); add("d_part", D + "RequestDispositionPartialGrantQuantity")
add("d_deny", D + "RequestDispositionFullExemptionDenialQuantity"); add("d_norec", D + "NonExemptionDenialQuantity[NoRecords]")
add("d_other", [D + f"NonExemptionDenialQuantity[{x}]" for x in
                ["Duplicate", "FeeRelated", "ImproperRequest", "NotAgency", "NotDescribed", "Other", "Referred", "Withdrawn"]])
add("o3", "03_DispositionOtherReasons__ComponentOtherDenialReasonQuantity")
E = "04_ExpeditedProcessing__"
add("ex_grant", E + "RequestGrantedQuantity"); add("ex_deny", E + "RequestDeniedQuantity"); add("ex_med", E + "AdjudicationMedianDaysValue", "avg")
EX = ["1", "2", "3", "4", "5", "6", "7(A)", "7(B)", "7(C)", "7(D)", "7(E)", "7(F)", "8", "9"]
for e in EX:
    add("x5_" + e, f"05_Exemptions__AppliedExemptionQuantity[Ex. {e}]")
A = "07_Appeals__ProcessingStatistics"
add("ap_recv", A + "ReceivedQuantity"); add("ap_proc", A + "ProcessedQuantity"); add("ap_pend", A + "PendingAtEndQuantity")
AD = "08_AppealsDisposition__AppealDisposition"
add("ad_aff", AD + "AffirmedQuantity"); add("ad_part", AD + "PartialQuantity"); add("ad_rev", AD + "ReversedQuantity"); add("ad_oth", AD + "OtherQuantity")
for e in EX:
    add("x9_" + e, f"09_AppealsExemptions__AppliedExemptionQuantity[Ex. {e}]")
NX = ["NoRecords", "Referred", "Withdrawn", "FeeRelated", "NotDescribed", "ImproperRequest", "NotAgency", "Duplicate", "InLitigation",
      "ExpeditedDenial", "Other"]
for x in NX:
    add("n10_" + x, f"10_AppealsOtherThanExemptions__NonExemptionDenialQuantity[{x}]")
add("o11", "11_AppealsOtherReasons__ComponentOtherDenialReasonQuantity")
add("ar_med", "12_AppealsResponseTime__ResponseTimeMedianDaysValue", "avg")
add("ar_avg", "12_AppealsResponseTime__ResponseTimeAverageDaysValue", "avg")
for t, k in [("Simple", "s"), ("Complex", "c"), ("Expedited", "e")]:
    add(f"t14_{k}", f"14_ProcessingTime__{t}ResponseTime.ResponseTimeMedianDaysValue", "avg")
    add(f"t15_{k}", f"15_ProcessingTimeGranted__{t}ResponseTime.ResponseTimeMedianDaysValue", "avg")
    add(f"p19_{k}", f"19_PendingRequests__{t}PendingRequestStatistics.PendingRequestQuantity")
BUCK = {"1-20": ["1-20"], "21-60": ["21-40", "41-60"], "61-100": ["61-80", "81-100"],
        "101-200": ["101-120", "121-140", "141-160", "161-180", "181-200"], "201-400": ["201-300", "301-400"], "401+": ["401+"]}
for n, pre in [("16", "16_SimpleRequests__"), ("17", "17_ComplexRequests__"), ("18", "18_ExpeditedRequests__")]:
    for b, parts in BUCK.items():
        add(f"b{n}_{b}", [f"{pre}TimeIncrementProcessedQuantity[{p}]" for p in parts])
add("fw_grant", "21_FeeWaiver__RequestGrantedQuantity"); add("fw_deny", "21_FeeWaiver__RequestDeniedQuantity")
add("fw_med", "21_FeeWaiver__AdjudicationMedianDaysValue", "avg")
add("staff", "22_Personnel__TotalFullTimeStaffQuantity"); add("staff_ft", "22_Personnel__FullTimeEmployeeQuantity")
add("cost", "23_Costs__TotalCostAmount"); add("cost_lit", "23_Costs__LitigationCostAmount"); add("fees", "23_Costs__FeesCollectedAmount")
add("excl", "24_Exclusions__TimesUsedQuantity")
add("pd_foia", "25_ProactiveDisclosures__PostedbyFOIAQuantity"); add("pd_prog", "25_ProactiveDisclosures__PostedbyProgramQuantity")
add("bl_req", "26_Backlog__BackloggedRequestQuantity"); add("bl_app", "26_Backlog__BackloggedAppealQuantity")
C = "27_Consultations__ProcessingStatistics"
add("co_recv", C + "ReceivedQuantity"); add("co_proc", C + "ProcessedQuantity"); add("co_pend", C + "PendingAtEndQuantity")
add("c29_rl", "29_Comparisons__ItemsReceivedLastYearQuantity"); add("c29_rc", "29_Comparisons__ItemsReceivedCurrentYearQuantity")
add("c30_l", "30_ComparisonsRequestsBacklogged__BacklogLastYearQuantity"); add("c30_c", "30_ComparisonsRequestsBacklogged__BacklogCurrentYearQuantity")
add("c31_rl", "31_ComparisonsAppeals__ItemsReceivedLastYearQuantity"); add("c31_rc", "31_ComparisonsAppeals__ItemsReceivedCurrentYearQuantity")
add("c32_l", "32_ComparisonsAppealsBacklogged__BacklogLastYearQuantity"); add("c32_c", "32_ComparisonsAppealsBacklogged__BacklogCurrentYearQuantity")
# ten oldest items: the oldest is the max over the ten slots
for k, pre in [("a13_old", "13_AppealsTenOldest__"), ("a20_old", "20_TenOldestRequests__"), ("a28_old", "28_ConsultationsTenOldest__")]:
    add(k, [f"{pre}OldItem{i}.OldItemPendingDaysQuantity" for i in range(1, 11)], "max")


def col_name(key):
    """Site key -> Postgres column name (lowercase, a-z0-9_)."""
    return re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")


KEYS = list(P)
COLS = [col_name(k) for k in KEYS]
assert len(set(COLS)) == len(COLS), "column names must be unique"


# ---------------------------------------------------------------- build
def build(master, statutes):
    d = pd.read_csv(master, dtype=str)
    d = d[d["Exclude From Component Sum"].fillna("") != "yes"]
    d = d[d["Row Type"].isin(["agency_overall", "component", "second_entry"])].copy()

    missing = sorted({c for cols, _ in P.values() for c in cols if c not in d.columns})
    if missing:
        print(f"warning: {len(missing)} source columns not in the master file, they load as empty: {missing[:5]} ...")

    vals = {}
    for k, (cols, kind) in P.items():
        present = [c for c in cols if c in d.columns]
        if not present:
            vals[k] = pd.Series(np.nan, index=d.index)
            continue
        m = pd.concat([d[c].map(num) for c in present], axis=1)
        vals[k] = m.max(axis=1, skipna=True) if kind == "max" else m.sum(axis=1, min_count=1)

    agencies = sorted(d.Agency.unique())
    ai = {a: i for i, a in enumerate(agencies)}
    abbr = d.groupby("Agency")["Agency Abbreviation"].agg(lambda s: s.dropna().iloc[-1] if s.notna().any() else "").to_dict()
    ag_df = pd.DataFrame({"id": range(len(agencies)), "name": agencies, "abbr": [abbr.get(a, "") for a in agencies]})

    d["key"] = d["Component"].fillna("") + " | " + d["Component Name"].fillna("")
    comp_rows, ci = [], {}
    for a, g in d[d["Row Type"] != "agency_overall"].groupby("Agency"):
        for i, key in enumerate(g.groupby("key").size().index.tolist()):
            code, name = key.split(" | ", 1)
            ci[(a, key)] = i
            comp_rows.append({"agency_id": ai[a], "idx": i, "code": code, "name": name})
    comp_df = pd.DataFrame(comp_rows, columns=["agency_id", "idx", "code", "name"])

    rows = pd.DataFrame({
        "fy": d["Fiscal Year"].astype(int),
        "agency_id": d.Agency.map(ai),
        "comp_idx": [-1 if rt == "agency_overall" else ci[(a, k)] for rt, a, k in zip(d["Row Type"], d.Agency, d.key)],
    })
    metric_df = pd.DataFrame({c: vals[k].round(2).to_numpy() for k, c in zip(KEYS, COLS)})
    rows = pd.concat([rows.reset_index(drop=True), metric_df], axis=1)
    rows = rows.sort_values(["fy", "agency_id", "comp_idx"]).reset_index(drop=True)

    s = pd.read_csv(statutes, dtype=str)
    s = s[(s["Row Type"] == "agency_overall") & s.Statute.notna() & s.Agency.isin(ai)]
    s["n"] = s["Number of Times Relied Upon"].map(num)
    s["st"] = s.Statute.str.replace(r"\s+", " ", regex=True).str.strip().str.slice(0, 120)
    top = []
    for (fy, a), g in s.groupby(["Fiscal Year", "Agency"]):
        g = g.groupby("st").n.sum(min_count=1).sort_values(ascending=False).head(3)
        for r, (st, n) in enumerate(g.items(), 1):
            top.append({"fy": int(fy), "agency_id": ai[a], "rank": r, "statute": st, "times": None if pd.isna(n) else int(n)})
    st_df = pd.DataFrame(top, columns=["fy", "agency_id", "rank", "statute", "times"])

    met_df = pd.DataFrame({"key": KEYS, "col": COLS, "kind": [P[k][1] for k in KEYS], "ord": range(len(KEYS))})
    return {"metrics": met_df, "agencies": ag_df, "components": comp_df, "foia_rows": rows, "statutes_top": st_df}


# ---------------------------------------------------------------- schema
def schema_sql():
    metric_cols = ",\n".join(f"  {c} double precision" for c in COLS)
    tables = ["metrics", "agencies", "components", "foia_rows", "statutes_top"]
    policies = "\n".join(
        f"alter table public.{t} enable row level security;\n"
        f"drop policy if exists \"public read\" on public.{t};\n"
        f"create policy \"public read\" on public.{t} for select to anon, authenticated using (true);\n"
        f"grant select on public.{t} to anon, authenticated;" for t in tables)
    return f"""-- FOIA dashboard tables (generated by build_tables.py). Run once in the Supabase SQL editor.
-- Everyone can read (the site uses the public anon key); only the loader (database password) can write.

drop table if exists public.statutes_top, public.foia_rows, public.components, public.agencies, public.metrics cascade;

create table public.metrics (
  key  text primary key,      -- key the site uses, e.g. req_recv
  col  text not null unique,  -- column in foia_rows
  kind text not null check (kind in ('sum','avg','max')),
  ord  int  not null
);

create table public.agencies (
  id   int primary key,
  name text not null,
  abbr text
);

create table public.components (
  agency_id int not null references public.agencies(id),
  idx       int not null,
  code      text,
  name      text,
  primary key (agency_id, idx)
);

create table public.foia_rows (
  id        bigint generated always as identity primary key,
  fy        smallint not null,
  agency_id int not null references public.agencies(id),
  comp_idx  int not null,      -- -1 = agency overall row, otherwise components.idx
{metric_cols}
);
create index foia_rows_fy_agency on public.foia_rows (fy, agency_id, comp_idx);

create table public.statutes_top (
  fy        smallint not null,
  agency_id int not null references public.agencies(id),
  rank      smallint not null,
  statute   text not null,
  times     int,
  primary key (fy, agency_id, rank)
);

{policies}
"""


# ---------------------------------------------------------------- load
def load(tables, url):
    import psycopg
    with psycopg.connect(url) as conn, conn.cursor() as cur:
        cur.execute("truncate public.statutes_top, public.foia_rows, public.components, public.agencies, public.metrics")
        for name in ["metrics", "agencies", "components", "foia_rows", "statutes_top"]:
            df = tables[name]
            buf = io.StringIO()
            df.to_csv(buf, index=False, header=False, na_rep="")
            cols = ", ".join(df.columns)
            with cur.copy(f"copy public.{name} ({cols}) from stdin with (format csv, null '')") as cp:
                cp.write(buf.getvalue())
            print(f"loaded {name}: {len(df):,} rows")
        conn.commit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True)
    ap.add_argument("--statutes", required=True)
    ap.add_argument("--csv-out")
    ap.add_argument("--schema-out")
    ap.add_argument("--load", action="store_true", help="load into DATABASE_URL")
    a = ap.parse_args()

    t = build(a.master, a.statutes)
    for k, v in t.items():
        print(f"{k}: {len(v):,} rows x {v.shape[1]} cols")
    if a.schema_out:
        open(a.schema_out, "w").write(schema_sql())
        print("wrote", a.schema_out)
    if a.csv_out:
        os.makedirs(a.csv_out, exist_ok=True)
        for k, v in t.items():
            v.to_csv(os.path.join(a.csv_out, k + ".csv"), index=False)
        print("wrote CSVs to", a.csv_out)
    if a.load:
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise SystemExit("set DATABASE_URL (Supabase > Project Settings > Database > Connection string > Session pooler)")
        load(t, url)


if __name__ == "__main__":
    main()
