# merge_by_year

Agency-level FOIA data, FY2008-2025: foia.gov's 32 annual tables merged into one row per agency per year.

## Files
- `output/FOIA_agency_FY2008-2025.csv` (1,923 rows, 247 columns): all 18 years stacked, one row per agency per year (128 agencies). Columns: `Agency`, `Fiscal Year`, `missing tables`, then 244 data columns.
- `output/FY2008.csv` ... `output/FY2025.csv`: the same data, one file per year (`Agency`, `Fiscal Year`, then the 244 data columns).
- `output/exemption_statutes_FY2008-2025.csv` (6,307 rows): 06 Exemption 3 statutes, one row per statute (it does not fit one row per agency, so it is kept separately).
- `output/merge_report.csv`: one row per year: number of tables and agencies, which per-table downloads and API rows were used (`notes`), and total requests received as a check.
- `data_type_map.csv`: the 32 data types: number (01-32, the order on foia.gov's data page), foia.gov name, official file name, and the column prefix used in the merged table (e.g. `requests__`).
- `merge_by_year.py`: the script that builds `output/`.
- `per_table_supplement/`: data used to fill gaps in foia.gov's yearly zips (see below).

## Where the data comes from
1. **foia.gov yearly CSV zips** ("Download the full YYYY All Agency Data set" on https://www.foia.gov/foia-dataset-download.html). These give most of the data.
2. **Single-table downloads** from https://www.foia.gov/data.html (all agencies, one data type, one year), in `per_table_supplement/<year>/`. Used where the table in the yearly zip has a problem (13 files; `output/merge_report.csv` lists them too):

| Year | No. | Data type | Problem with the table in the yearly zip |
|---|---|---|---|
| FY2009 | 24 | Exclusions | blank |
| FY2009 | 25 | Proactive Disclosures | blank |
| FY2012 | 04 | Requests - Expedited Processing | lists only 69 of 99 agencies |
| FY2012 | 05 | Exemptions | lists only 69 of 99 agencies |
| FY2012 | 10 | Appeals - Dis. - Other Than Exs. | lists only 14 of 99 agencies |
| FY2012 | 11 | Appeals - Dis. - "Other" Reasons | lists only 14 of 99 agencies |
| FY2012 | 12 | Appeals - Response Time | lists only 14 of 99 agencies |
| FY2013 | 31 | Comparisons - Administrative Appeals | missing |
| FY2013 | 32 | Comparisons - Appeals Backlogged | missing |
| FY2016 | 32 | Comparisons - Appeals Backlogged | missing |
| FY2020 | 10 | Appeals - Dis. - Other Than Exs. | holds another table's columns (table 11) |
| FY2020 | 11 | Appeals - Dis. - "Other" Reasons | missing |
| FY2020 | 25 | Proactive Disclosures | blank |

The FY2016 zip also holds a second copy of table 01 (`... (1).csv`) whose rows are FY2018 data; the script checks the fiscal year and skips it.
3. **foia.gov API**, for what the zips leave out:
   - `agency_years_from_api.csv`: 2 annual reports that are not in the zips at all (U.S. Agency for Global Media FY2022, Council of the Inspectors General on Integrity and Efficiency FY2025).
   - `exemption_statutes_from_api.csv`: 06 statute rows for 56 agency-years the zips leave out; they replace the zip's rows for those agencies.

## How values are handled
- Values are copied as written: blank, 0 and N/A are not changed.
- The "All agencies" total row of each table is left out.
- Agency names follow the yearly zips. The single-table downloads call one agency "U.S. Chemical Safety and Hazard Investigation Board"; it is renamed to "Chemical Safety and Hazard Investigation Board".
- `missing tables` lists tables still missing for that agency-year after the fills. It is empty in every row: no table is missing.
- Column names are the data type prefix (see `data_type_map.csv`) plus the column name in foia.gov's CSV, e.g. `requests__Number of Requests Received in Fiscal Year`.

## Checks
- Every cell was compared with the foia.gov API: values match (29 cells differ only in spaces around "N/A").
- Requests received add up to the official "All agencies" row in every year except FY2022 (+92) and FY2025 (+237): the two agency-years added from the API are not in that row.
- 24 (Exclusions) and 25 (Proactive Disclosures) are blank for almost all agencies in FY2008-2016; the foia.gov API is blank for those years too.

## How to rebuild `output/`
1. Download the 18 yearly "All Agency Data set" CSV zips from https://www.foia.gov/foia-dataset-download.html and unzip each into a folder named `csv_2008`, `csv_2009`, ... `csv_2025`, all inside one parent folder.
2. Run:
   ```
   pip install pandas
   python merge_by_year.py --data <parent folder>
   ```
   `--supplement` (default `per_table_supplement/`) and `--out` (default `output/`) can also be set.

   Note: in the FY2017 zip, one file is named `foia-received-processed-and-pending-administrative-appeals.csv.crdownload`. That is how foia.gov packed it; the script reads it like the other files.
