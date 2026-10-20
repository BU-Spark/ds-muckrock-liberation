"""
Make one CSV per agency with its FOIA annual report data for FY2008-2025.

Input : agency_presence_2008_2025.csv  (the agency list, one row per agency)
Source: foia.gov bulk CSV files, https://www.foia.gov/downloads/all_agencies_csv_<YEAR>.zip
Output: agency_files/<Agency name>.csv   ONE file per agency:
            columns = agency, table, measure, FY2008, FY2009, ... FY2025
            rows    = every number from the 32 annual report tables (about 240 rows),
                      plus one row per Exemption 3 statute (times relied upon)
        agency_files/_summary.csv        which agencies were done and how many years each

Run (from the folder that has this script and the agency list):
    pip install pandas requests
    python download_agency_files.py --start 65 --end 128

--start / --end are row numbers in the agency list (1 = first agency).
The other person does 1-64, you do 65-128.
"""
import argparse
import io
import re
import zipfile
from pathlib import Path

import pandas as pd
import requests

YEARS = range(2008, 2026)
URL = "https://www.foia.gov/downloads/all_agencies_csv_{year}.zip"
KEYS = ["Agency", "Component", "Fiscal Year"]
MULTI_ROW = "exemption-statutes"   # many rows per agency: one output row per statute


def table_name(file_name):
    """'All Agencies 2008/foia-foia-personnel (9).csv' -> 'foia-personnel'"""
    name = file_name.split("/")[-1]
    name = name.removesuffix(".crdownload").removesuffix(".csv")
    name = re.sub(r" \(\d+\)$", "", name)
    return name.removeprefix("foia-")


def safe_file_name(agency):
    return re.sub(r'[\\/:*?"<>|]', "_", agency).strip()


def get_zip(year, cache):
    """Download the year's zip once and keep it in the cache folder."""
    path = cache / f"all_agencies_csv_{year}.zip"
    if not path.exists():
        print(f"  downloading FY{year} ...")
        r = requests.get(URL.format(year=year), timeout=120)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def read_year(year, cache):
    """Return {table name: DataFrame} for one fiscal year."""
    tables = {}
    with zipfile.ZipFile(get_zip(year, cache)) as z:
        for f in z.namelist():
            if "__MACOSX" in f or not f.endswith((".csv", ".csv.crdownload")):
                continue
            d = pd.read_csv(io.BytesIO(z.read(f)), dtype=str, keep_default_na=False)
            if "Fiscal Year" not in d.columns:
                continue
            # skip a file that belongs to another year (FY2016 has one)
            if not (d["Fiscal Year"].str.strip() == str(year)).all():
                print(f"  FY{year}: skipped {f} (wrong fiscal year inside)")
                continue
            d["Agency"] = d["Agency"].str.strip()
            tables[table_name(f)] = d
    return tables


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agencies", default="agency_presence_2008_2025.csv", help="the agency list")
    ap.add_argument("--start", type=int, default=65, help="first row number to do (1 = first agency)")
    ap.add_argument("--end", type=int, default=128, help="last row number to do")
    ap.add_argument("--out", default="agency_files")
    ap.add_argument("--cache", default="foia_zips", help="where the downloaded zips are kept")
    args = ap.parse_args()

    out, cache = Path(args.out), Path(args.cache)
    out.mkdir(exist_ok=True)
    cache.mkdir(exist_ok=True)

    agencies = pd.read_csv(args.agencies, dtype=str)
    mine = agencies.iloc[args.start - 1: args.end]
    print(f"Agencies {args.start}-{args.end}: {len(mine)} agencies, "
          f"from '{mine.Agency.iloc[0]}' to '{mine.Agency.iloc[-1]}'")

    # an agency can appear under more than one name (e.g. Chemical Safety Board)
    names = {row.Agency: [n.strip() for n in row.Observed_Source_Names.split("|")]
             for row in mine.itertuples()}

    # agency -> list of {table, measure, year, value}
    records = {a: [] for a in names}

    for year in YEARS:
        print(f"FY{year}")
        tables = read_year(year, cache)
        for agency, aliases in names.items():
            for t, d in tables.items():
                sub = d[d["Agency"].isin(aliases)]
                if sub.empty:
                    continue
                if t == MULTI_ROW:
                    # many rows per year: one line per statute, value = times relied upon
                    for _, r in sub.iterrows():
                        statute = str(r.get("Statute", "")).strip()
                        if not statute or statute.upper() == "N/A":
                            continue
                        records[agency].append({"table": t, "measure": statute, "year": year,
                                                "value": r.get("Number of Times Relied Upon", "")})
                    continue
                row = sub.iloc[0]
                for c in sub.columns:
                    if c in KEYS:
                        continue
                    records[agency].append({"table": t, "measure": c, "year": year, "value": row[c]})

    summary = []
    for agency in names:
        file = out / f"{safe_file_name(agency)}.csv"
        recs = records[agency]
        years = sorted({r["year"] for r in recs})
        if recs:
            long = pd.DataFrame(recs)
            # keep the order in which tables and measures first appear
            order = long[["table", "measure"]].drop_duplicates().reset_index(drop=True)
            wide = long.pivot_table(index=["table", "measure"], columns="year", values="value",
                                    aggfunc="first")
            wide = order.merge(wide.reset_index(), on=["table", "measure"], how="left")
            for y in YEARS:                      # one column per year, FY2008 ... FY2025
                if y not in wide.columns:
                    wide[y] = ""
            wide = wide[["table", "measure"] + list(YEARS)]
            wide.columns = ["table", "measure"] + [f"FY{y}" for y in YEARS]
            wide.insert(0, "agency", agency)
            wide.to_csv(file, index=False)
        summary.append({"Agency": agency, "years_found": len(years),
                        "first_year": min(years) if years else "", "last_year": max(years) if years else "",
                        "rows": len(wide) if recs else 0,
                        "file": file.name if recs else "NO DATA FOUND"})
        print(f"  {agency}: {len(years)} years")

    pd.DataFrame(summary).to_csv(out / "_summary.csv", index=False)
    print(f"\nDone. {sum(1 for s in summary if s['years_found'])} files in {out}/  (see _summary.csv)")


if __name__ == "__main__":
    main()
