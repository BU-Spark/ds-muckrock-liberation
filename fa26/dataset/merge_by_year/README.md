# Merge the 32 tables of each year into one file

Test of the idea from the 10/14 team meeting: one CSV per fiscal year with all 32 tables side by side.

## Output (`output/`)

| File | What it is |
|---|---|
| `FY2008.csv` … `FY2025.csv` | One row per agency, all tables joined side by side (about 245 columns) |
| `exemption_statutes_FY2008-2025.csv` | The exemption-statutes table, all years (kept separate, see below) |
| `merge_report.csv` | Per year: tables found, agencies, columns, missing tables, skipped files |

Column names are `<table>__<original column>`, e.g. `requests__Number of Requests Received in Fiscal Year`.
Values are kept exactly as published (text), including `N/A` and `<1`.

## Results

- Works for all 18 years: 71–122 agencies per year, 234–245 columns.
- Check: the total "requests received" is the same before and after joining, every year
  (e.g. FY2025 DHS = 1,019,496; FY2009 has 73 agencies, same as Jerry's count).

## Things this handles

1. **Column names repeat across tables** (7 tables have a column called `Total`), so every column gets the table name in front.
2. **`All agencies` row is dropped**: it is the sum of all agencies, so keeping it would double count.
3. **exemption-statutes is not joined**: it has one row per statute, up to 43 rows for one agency.
   Joining it would repeat every other number. When I tried, FY2025 total requests went from
   1,707,197 to 29,758,465. So it is saved as its own file.
4. **FY2016 zip contains an FY2018 file**: each file's own `Fiscal Year` column is checked and wrong-year files are skipped.
5. **One FY2017 file ends in `.csv.crdownload`**: it is read too (a `*.csv` search misses it).

## Missing tables (missing in the official data, not a bug)

| Year | Missing |
|---|---|
| FY2013 | backlog_appeals_vs_prev_year, appeals_vs_prev_year |
| FY2016 | backlog_appeals_vs_prev_year |
| FY2020 | appeals_other_reasons; appeals_non_exemption_reasons has only `Total` that year |

Those columns are empty for those years. They should be shown as "no data", not 0.

## Limits

- **Agency level only.** The official CSVs have no components (`Component` is always "Agency Overall").
  Component-level data has to come from the XML files.
- About 245 columns is wide. For charts, it is often easier to use one table stacked across years,
  e.g. `requests` for 2008–2025.
- Agency names are as published each year (renames and merges are not mapped yet).

## Run

```bash
python merge_by_year.py --data <folder with csv_2008/ ... csv_2025/>
```
Input is the official annual CSV zips from https://www.foia.gov/foia-dataset-download.html, unzipped into one folder per year.
