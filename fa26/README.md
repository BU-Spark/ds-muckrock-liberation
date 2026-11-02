# FA26: FOIA annual report data

FOIA annual report data from foia.gov for fiscal years 2008-2025. Every federal agency files one report per year. The report is split into 32 data types (Requests, Exemptions, Appeals, Backlog, ...); `dataset/data_type_map.csv` lists them all.

## Folder layout

```
fa26/
├── scripts/                  code that downloads and builds the data
│   ├── foia_downloader.py        downloads one CSV per data type per year from foia.gov
│   ├── inspect_foia_page.py      helper to fix the downloader if the foia.gov page changes
│   ├── README_foia_downloader.md how to run the downloader
│   ├── merge_by_year.py          builds dataset/agency_level/ from the yearly zips
│   └── clean_text_03_06_11.py    text clean-up used for the component-level text columns
└── dataset/
    ├── data_type_map.csv     the 32 data types: number, foia.gov name, file name, column prefix
    ├── raw_agency_level/     raw downloads: <year>/NN_<data type>.csv, all agencies + components
    ├── supplement/           files used to fill gaps in foia.gov's yearly zips
    ├── agency_level/         cleaned: one row per agency per year (start here)
    └── component_level/      cleaned: one row per agency office (component) per year
```

## Which file to use

| Question | File |
|---|---|
| Agency totals over time | `dataset/agency_level/FOIA_agency_FY2008-2025.csv` |
| One year only | `dataset/agency_level/FY<year>.csv` |
| Numbers for each office inside an agency | `dataset/component_level/component_master_no_03_06_11.csv` |
| Exemption 3 statutes | `dataset/agency_level/exemption_statutes_FY2008-2025.csv` (agency) or `dataset/component_level/exemption_statutes_06.csv` (component) |
| Free-text "Other" denial reasons | `dataset/component_level/other_reasons_03_11.csv` |

Each data folder has its own README with column definitions and known issues.

## How the data was collected

All data is public and comes from foia.gov in four ways:

1. **Report page, by browser automation** (`scripts/foia_downloader.py` → `dataset/raw_agency_level/`). The script uses Playwright to drive Chromium on foia.gov's "Create an Annual Report" page. For each year and data type it selects all agencies, clicks View Report, waits for the page to finish loading its data from api.foia.gov, then clicks Download CSV.
2. **Yearly bulk zips** (input to `scripts/merge_by_year.py` → `dataset/agency_level/`). These are the "All Agency Data set" CSV zips from https://www.foia.gov/foia-dataset-download.html. They are downloaded by hand and not stored in this repo.
3. **Gap fills** (`dataset/supplement/`). Thirteen tables in the zips are blank, incomplete or mislabeled. These were replaced with single-table downloads from the report page (method 1). Agency-years missing from the zips were taken from the foia.gov API.
4. **foia.gov API** (→ `dataset/component_level/`). The component-level tables are built from the API's annual reports (api.foia.gov, the data behind foia.gov's report pages), downloaded October 18-19, 2026. The build script for these tables is not in the repo yet.

## Setup

```bash
pip install pandas playwright
playwright install chromium
```
