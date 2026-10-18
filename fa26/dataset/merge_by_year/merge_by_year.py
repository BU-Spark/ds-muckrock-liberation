import argparse
import re
from pathlib import Path

import pandas as pd

YEARS = range(2008, 2026)
ALL = "All agencies"
KEYS = ["Agency", "Component", "Fiscal Year"]
MULTI_ROW = {"exemption-statutes"}

# short names for the 32 tables (official file name without "foia-" and the " (N)" suffix)
SHORT = {
    "received-processed-and-pending-foia-requests": "requests",
    "comparison-of-numbers-of-requests-from-previous-year-and-current-year-annual-report": "requests_vs_prev_year",
    "disposition-of-foia-requests-all-processed-requests": "disposition",
    "disposition-of-foia-requests-other-reasons": "disposition_other_reasons",
    "disposition-of-foia-requests-number-of-times-exemptions-applied": "exemptions_applied",
    "exemption-statutes": "exemption_statutes",
    "requests-for-expedited-processing": "expedited",
    "requests-for-fee-waiver": "fee_waiver",
    "processed-requests-response-time-for-all-processed-perfected-requests": "response_time_all",
    "processed-requests-response-time-for-perfected-requests-in-which-information-was-granted": "response_time_granted",
    "processed-requests-response-time-in-day-increments-simple-requests": "days_simple",
    "processed-requests-response-time-in-day-increments-complex-requests": "days_complex",
    "processed-requests-response-time-in-day-increments-requests-granted-expedited-processing": "days_expedited",
    "pending-requests-all-pending-perfected-requests": "pending",
    "pending-requests-ten-oldest-pending-perfected-requests": "pending_ten_oldest",
    "backlogs-of-foia-requests-and-administrative-appeals": "backlog",
    "comparison-of-backlogged-requests-from-previous-year-and-current-year-annual-report": "backlog_requests_vs_prev_year",
    "comparison-of-backlogged-administrative-appeals-from-previous-year-and-current-year-annual-report": "backlog_appeals_vs_prev_year",
    "received-processed-and-pending-administrative-appeals": "appeals",
    "comparison-of-numbers-of-administrative-appeals-from-previous-year-and-current-year-annual-report": "appeals_vs_prev_year",
    "disposition-of-administrative-appeals-all-processed-appeals": "appeals_disposition",
    "reasons-for-denial-on-appeal-number-of-times-exemptions-applied": "appeals_exemptions_applied",
    "reasons-for-denial-on-appeal-reasons-other-than-exemptions": "appeals_non_exemption_reasons",
    "reasons-for-denial-on-appeal-other-reasons": "appeals_other_reasons",
    "response-time-for-administrative-appeals": "appeals_response_time",
    "ten-oldest-administrative-appeals": "appeals_ten_oldest",
    "consultations-on-foia-requests-received-processed-and-pending-consultations": "consultations",
    "consultations-on-foia-requests-ten-oldest-consultations-received-from-other-agencies-pending-at-agency": "consultations_ten_oldest",
    "foia-costs-and-fees-collected-for-processing-requests": "costs_fees",
    "foia-personnel": "personnel",
    "number-of-subsection-a-postings": "subsection_a_postings",
    "number-of-times-subsection-c-used": "subsection_c_used",
}


def table_name(path):
    name = path.name.removesuffix(".crdownload").removesuffix(".csv")
    name = re.sub(r" \(\d+\)$", "", name)
    return name.removeprefix("foia-")


def load_year(folder, year):
    """Return {table: DataFrame} for one year, plus notes about skipped files."""
    tables, notes = {}, []
    for f in sorted(folder.rglob("*")):
        if not f.name.endswith((".csv", ".csv.crdownload")):
            continue
        d = pd.read_csv(f, dtype=str)
        fy = pd.to_numeric(d["Fiscal Year"], errors="coerce")
        if not (fy == year).all():
            notes.append(f"skipped {f.name}: Fiscal Year is {[int(x) for x in sorted(fy.dropna().unique())]}")
            continue
        t = table_name(f)
        if t not in SHORT:
            notes.append(f"unknown table {f.name}")
            continue
        tables[t] = d[d["Agency"] != ALL]
    return tables, notes


def merge_year(tables):
    """Join every one-row-per-agency table side by side on Agency."""
    merged = None
    for t in SHORT:
        if t in MULTI_ROW or t not in tables:
            continue
        d = tables[t]
        if d["Agency"].duplicated().any():
            raise ValueError(f"{t}: more than one row per agency")
        d = d.drop(columns=["Component", "Fiscal Year"]).set_index("Agency")
        d.columns = [f"{SHORT[t]}__{c}" for c in d.columns]
        merged = d if merged is None else merged.join(d, how="outer")
    return merged


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=str(Path.home() / "ds701-spark/data/extracted"),
                        help="folder that contains csv_2008/ ... csv_2025/")
    parser.add_argument("--out", default=str(Path(__file__).parent / "output"))
    args = parser.parse_args()
    data, out = Path(args.data).expanduser(), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    report, statutes, years = [], [], []
    for year in YEARS:
        tables, notes = load_year(data / f"csv_{year}", year)
        merged = merge_year(tables)

        # check: no agency row was duplicated by the joins
        req = tables["received-processed-and-pending-foia-requests"]
        col = "requests__Number of Requests Received in Fiscal Year"
        before = pd.to_numeric(req["Number of Requests Received in Fiscal Year"].str.replace(",", ""), errors="coerce").sum()
        after = pd.to_numeric(merged[col].str.replace(",", ""), errors="coerce").sum()
        assert before == after, f"FY{year}: received total changed {before} -> {after}"

        merged.insert(0, "Fiscal Year", year)
        merged.reset_index().to_csv(out / f"FY{year}.csv", index=False)
        if "exemption-statutes" in tables:
            statutes.append(tables["exemption-statutes"])

        missing = [SHORT[t] for t in SHORT if t not in tables]
        # all-years file: a missing table stays blank (not reported), never 0
        years.append(merged.reset_index().assign(**{"missing tables": "; ".join(missing)}))
        report.append({"Fiscal Year": year, "tables found": len(tables), "agencies": len(merged),
                       "columns": merged.shape[1], "missing tables": "; ".join(missing),
                       "notes": "; ".join(notes), "requests received (check)": int(after)})
        print(f"FY{year}: {len(tables)} tables, {len(merged)} agencies x {merged.shape[1]} columns"
              + (f" | missing: {', '.join(missing)}" if missing else "") + (f" | {'; '.join(notes)}" if notes else ""))

    pd.concat(statutes, ignore_index=True).to_csv(out / "exemption_statutes_FY2008-2025.csv", index=False)

    # stack the 18 years into one file, one row per agency per year
    stacked = pd.concat(years, ignore_index=True)
    stacked = stacked[["Agency", "Fiscal Year", "missing tables"]
                      + [c for c in stacked.columns if c not in ("Agency", "Fiscal Year", "missing tables")]]
    assert len(stacked) == sum(r["agencies"] for r in report)
    assert not stacked.duplicated(["Agency", "Fiscal Year"]).any()
    stacked.to_csv(out / "FOIA_agency_FY2008-2025.csv", index=False)
    print(f"all years: {len(stacked)} rows x {stacked.shape[1]} columns")
    pd.DataFrame(report).to_csv(out / "merge_report.csv", index=False)


if __name__ == "__main__":
    main()
