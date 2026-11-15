# Federal FOIA Dashboard — client meeting, Nov 17

Prototype v4 of the Federal FOIA Dashboard, built by BU Spark! (DS 701) for MuckRock, with everything needed to
rebuild it: the data, the scripts that make the data, and the storyline notebooks.

**Live page:** https://crazythursv50.github.io/client-meeting-1117/

Student prototype; not an official MuckRock product. All numbers come from the agencies' annual FOIA reports on
foia.gov (FY2008–FY2025).

## What is on the page

- **Start page: four storylines** (Requests, Outcomes, Appeals, Backlog). Each card states one finding; "How we got
  here" walks through the analysis step by step. The storylines are fixed: they do not change with the choices on the left.
- **Questions 1–6 and Explore all data.** Choose an agency or component, the fiscal years, and up to five agencies or
  components to compare. Each question has a Chart tab and a Tables tab; the notes next to the tables explain how
  the numbers are made. Tables can be downloaded as CSV, and "Copy link to this view" keeps every choice in the link.
- **How to use this dashboard** (start page) opens the user guide, including the rules used everywhere.
- **Storyline notebooks**, the full analysis behind each storyline:
  [Requests](https://crazythursv50.github.io/client-meeting-1117/notebooks/S0-request-volume-en.html) ·
  [Outcomes](https://crazythursv50.github.io/client-meeting-1117/notebooks/S1-partial-releases-en.html) ·
  [Appeals](https://crazythursv50.github.io/client-meeting-1117/notebooks/S3-appeals-en.html) ·
  [Backlog](https://crazythursv50.github.io/client-meeting-1117/notebooks/S4-backlog-outside-immigration-en.html)

## How the data gets to the page

```
foia.gov API (one JSON per annual report)
  └─ pipeline/download_api_annual.py            1,923 reports, FY2008–FY2025
      └─ pipeline/build_component_tables_from_api.py
          ├─ data/component_master_no_03_06_11.csv   one row per agency or component per year (244 measures)
          ├─ data/other_reasons_03_11.csv            "other" reasons, tables 03 and 11
          └─ data/exemption_statutes_06.csv          Exemption 3 statutes, table 06
              └─ pipeline/check_component_tables.py  every cell checked again before use
                  └─ pipeline/prep.py              -> docs/data/foia.json   (what the page reads)

storylines/notebooks/*.ipynb  (+ storyline_lib.py, reading the same component table)
  └─ storylines/build/build_walks.py            -> docs/data/walk_s0|s1|s3|s4.json   (the storyline cards)
```

The page itself never calls the API: it reads `docs/data/foia.json` and the four `walk_*.json` files.

## Folders

| Folder | What is in it |
|---|---|
| `docs/` | The page (served by GitHub Pages): `index.html`, `stories.js` / `stories.css` (storylines, guide, year buttons, lists, links), `data/`, and the notebooks as HTML |
| `data/` | The three component-level tables built from the API (download of 2026-11-02; a second download on 11-06 gave identical tables), the agency-level table, and the data type map |
| `pipeline/` | API download, table build, checks, and `prep.py` with `column_mapping.csv` (foia.gov's own column names) |
| `storylines/notebooks/` | The four storyline notebooks (English) and `storyline_lib.py` |
| `storylines/build/` | Turns the notebooks into the storyline cards; stops if a number in a card's text is not in the notebook |
| `tools/serve.py` | A local preview server without browser caching |

## Rebuild

Python 3 with pandas and matplotlib. Run from the repository folder.

```bash
# 1. Download the annual reports (free key from api.data.gov in ~/.foia_api_key; about two hours at the rate limit)
python pipeline/download_api_annual.py pipeline/report_data_map.json raw/api

# 2. Build the three component tables (the old component table only gives the column list)
python pipeline/build_component_tables_from_api.py raw/api pipeline/field_map.csv pipeline/report_data_map.json \
  data/FOIA_agency_FY2008-2025.csv data/component_master_no_03_06_11.csv data/data_type_map.csv data/new

# 3. Check them (also uses the team repository's agency_level folder and foia.gov's FY2024 component CSV export)
#    python pipeline/check_component_tables.py data/new <agency_level dir> raw/api pipeline/field_map.csv \
#      pipeline/report_data_map.json data/data_type_map.csv pipeline/column_mapping.csv <FY2024 component CSV dir> checks

# 4. The page's data file
python pipeline/prep.py --components data/component_master_no_03_06_11.csv --types data/data_type_map.csv \
  --mapping pipeline/column_mapping.csv --out docs/data

# 5. The storyline cards (asserts every number against the notebooks)
MPLBACKEND=Agg python storylines/build/build_walks.py docs/data

# Preview
python tools/serve.py 8000 docs      # then open http://127.0.0.1:8000/
```

Steps 4 and 5 on the files in this repository give exactly the `docs/data` files that are here (apart from the
build date in `foia.json`).

## Notes

- **Missing is not zero.** Blank and "N/A" are kept as missing; "<1" (less than a day) is kept as "<1".
- **No double counting.** Government totals add agency totals only; components are never added on top of their agency.
- **Department of War (Department of Defense).** DOJ's FY2025 summary uses the new name; foia.gov's data still says
  Department of Defense. The page shows the current name first and the former one in brackets, and `prep.py` keeps
  both spellings as one agency, so a later rename in the data does not split it in two.
- **Days are working days**, as the annual reports count them; the legal time limit is 20 working days.
- Team repository: https://github.com/BU-Spark/ds-muckrock-liberation
