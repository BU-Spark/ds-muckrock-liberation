# FOIA Annual Report Dataset — Documentation (FA26)

This folder holds U.S. federal FOIA (Freedom of Information Act) Annual Report data from [foia.gov](https://www.foia.gov/data.html), fiscal years **2008–2025**, in two forms:

| Dataset | Folder | Level of detail | Format | Size |
|---|---|---|---|---|
| **Agency-level CSVs** | `raw_agency_level/` | One row per **agency** per year (agency totals only) | 18 year folders × 32 CSVs (one per data type) | ~9 MB |
| **Component-level tables** | `component_level/` | One row per **agency × component (office)** per year, plus the agency total | 3 combined CSVs covering all years | ~14 MB |

Use the **agency-level** files for quick per-agency or government-wide numbers on a single topic. Use the **component-level** tables when you need office-level detail (e.g. FBI inside DOJ), a single wide table across all data types, or the Exemption 3 statute and "Other" reason details.

The same agency totals are also merged into one table per year (and one for all years) in `agency_level/`, built from foia.gov's yearly zips with gaps filled from `raw_agency_level/` and `agency_level/api_fills/`. See `agency_level/README.md`.

## 1. Background: what is in a FOIA Annual Report?

Every federal agency must file a FOIA Annual Report with the Department of Justice each fiscal year (Oct 1 – Sep 30). On foia.gov the report is organized into **12 main data types**, 6 of which have **sub data types (20 in total)**. Together they make the **32 data types**, and each one is its own file in the agency-level dataset.

### Data type hierarchy (official foia.gov)

| Main data type | Sub data types | No. of sub types |
|---|---|---:|
| Requests | Disposition (Dis.); Dis. – "Other" Reasons; Expedited Processing | 3 |
| Exemptions | Exemption 3 Statutes | 1 |
| Appeals | Disposition (Dis.); Dis. – Use of Exemptions; Dis. – Other Than Exs.; Dis. – "Other" Reasons; Response Time; Ten Oldest Pending | 6 |
| Processing Time | Requests Granted; Simple Requests; Complex Requests; Expedited Requests; Pending Requests; Ten Oldest Requests | 6 |
| Consultations | Ten Oldest | 1 |
| Comparisons | Requests Backlogged; Administrative Appeals; Appeals Backlogged | 3 |
| Fee Waiver | — | 0 |
| FOIA Personnel | — | 0 |
| FOIA Costs | — | 0 |
| Exclusions | — | 0 |
| Proactive Disclosures | — | 0 |
| Backlog | — | 0 |
| **12 main** | | **20 sub** → **32 data types** |

### All 32 data types

Both datasets use the same numbering, which follows the order of the data-type dropdown on foia.gov:

| No. | Main data type | foia.gov data type | What it measures |
|---|---|---|---|
| 01 | Requests | Requests | Requests pending at start, received, processed, pending at end of year |
| 02 | Requests | Requests – Disposition | How processed requests ended: full grant, partial, full denial, no records, withdrawn, etc. |
| 03 | Requests | Requests – Dis. – "Other" Reasons | Count (and, component-level only, reasons) for requests closed as "Other" |
| 04 | Requests | Requests – Expedited Processing | Expedited requests granted/denied, days to adjudicate |
| 05 | Exemptions | Exemptions | Number of times each FOIA exemption (Ex. 1–9, 7(A)–7(F)) was used on requests |
| 06 | Exemptions | Exemptions – Exemption 3 Statutes | Each statute cited under Exemption 3, with case citation, type of info withheld, times used |
| 07 | Appeals | Appeals | Appeals pending at start, received, processed, pending at end |
| 08 | Appeals | Appeals – Disposition | Appeals affirmed, partly reversed, fully reversed, closed for other reasons |
| 09 | Appeals | Appeals – Dis. – Use of Exemptions | Exemptions relied upon in appeal decisions |
| 10 | Appeals | Appeals – Dis. – Other Than Exs. | Non-exemption reasons for appeal outcomes |
| 11 | Appeals | Appeals – Dis. – "Other" Reasons | Count (and, component-level only, reasons) for appeals closed as "Other" |
| 12 | Appeals | Appeals – Response Time | Median / average / lowest / highest days to decide appeals |
| 13 | Appeals | Appeals – Ten Oldest Pending | Dates and days pending of the 10 oldest open appeals |
| 14 | Processing Time | Processing Time | Median / avg / low / high days for simple, complex, expedited requests |
| 15 | Processing Time | Processing Time – Requests Granted | Same as 14, for granted requests only |
| 16 | Processing Time | Processing Time – Simple Requests | Simple requests binned by days to process (<1–20 … 401+) |
| 17 | Processing Time | Processing Time – Complex Requests | Complex requests binned by days to process |
| 18 | Processing Time | Processing Time – Expedited Requests | Expedited requests binned by days to process |
| 19 | Processing Time | Processing Time – Pending Requests | Number pending + median/avg days, by track |
| 20 | Processing Time | Processing Time – Ten Oldest Requests | Dates and days pending of the 10 oldest open requests |
| 21 | Fee Waiver | Fee Waiver | Fee waivers granted/denied, days to adjudicate |
| 22 | FOIA Personnel | FOIA Personnel | Full-time FOIA employees, equivalent FTE, total staff |
| 23 | FOIA Costs | FOIA Costs | Processing costs, litigation costs, total costs, fees collected, fees as % of costs |
| 24 | Exclusions | Exclusions | Times a 5 U.S.C. 552(c) exclusion was used |
| 25 | Proactive Disclosures | Proactive Disclosures | Records posted by the FOIA office and by program offices |
| 26 | Backlog | Backlog | Backlogged requests and appeals at end of year |
| 27 | Consultations | Consultations | Consultations from other agencies: pending, received, processed |
| 28 | Consultations | Consultations – Ten Oldest | 10 oldest pending consultations |
| 29 | Comparisons | Comparisons | Requests received/processed, last year's report vs this year's |
| 30 | Comparisons | Comparisons – Requests Backlogged | Backlogged requests, previous vs current report |
| 31 | Comparisons | Comparisons – Administrative Appeals | Appeals received/processed, last year vs this year |
| 32 | Comparisons | Comparisons – Appeals Backlogged | Backlogged appeals, previous vs current report |

**Key terms**
- **Agency** – a federal department or independent agency (e.g. Department of Justice, EPA).
- **Component** – an office within an agency that processes its own FOIA requests (e.g. FBI within DOJ, Army within DoD). Small agencies usually have none.
- **Agency Overall** – the agency's total. For an agency with components, it is the total across all its components. For an agency **without** components, the Agency Overall row is the only row: the agency's own numbers.
- **Backlog** – requests or appeals still pending past the statutory deadline at year end.

---

## 2. Agency-level CSVs (`raw_agency_level/`)

### Source and collection
Downloaded with `foia_downloader.py` from foia.gov's **Create an Annual Report** page (annual report, "Select All Agencies", one data type, one fiscal year → "Download CSV"). This is foia.gov's own CSV export.

### Layout
- 18 year folders (FY2008–FY2025), each with the same 32 files → **576 CSV files**.
- File name = `<data type no.>_<data type name>.csv`. Sub data types include the main data type in the name (e.g. `08_appeals_disposition_dis.csv` vs `02_requests_disposition_dis.csv`).
- Encoding UTF-8, comma-separated, every value quoted.

### Row grain
- **One row per agency** for that year and data type. Every row's `Component` is `Agency Overall`, because this export has **no component detail**.
- Most files also contain one government-wide total row with `Agency` = **`All agencies`**. Files 12, 13, 14, 15, 20 and 28 (medians, days and oldest-pending data, which can't be summed) don't have it. **Drop the `All agencies` row before aggregating**, or you will double count.
- File 06 (Exemption 3 statutes) is longer: **one row per agency × statute**.

Agencies reported per year are listed in the per-year table in section 3; the counts are the same in both datasets.

### Common columns (every file)

| Column | Type | Meaning |
|---|---|---|
| `Agency` | text | Agency name as written on foia.gov, or `All agencies` for the government-wide total |
| `Component` | text | Always `Agency Overall` in this dataset |
| `Fiscal Year` | integer | 2008–2025 |

### Data columns per file

| File | Data columns (after Agency, Component, Fiscal Year) |
|---|---|
| `01_requests` | Requests Pending as of Start of FY; Received in FY; Processed in FY; Pending as of End of FY |
| `02_requests_disposition_dis` | Full Grants; Partial Grants/Partial Denials; Full Denials Based on Exemptions; No Records; All Records Referred; Request Withdrawn; Fee-Related Reason; Records Not Reasonably Described; Improper FOIA Request for Other Reason; Not Agency Record; Duplicate Request; Other*; Total |
| `03_requests_dis_other_reasons` | Total |
| `04_requests_expedited_processing` | Number Granted; Number Denied; Median / Average Days to Adjudicate; Number Adjudicated Within Ten Calendar Days |
| `05_exemptions` | Ex. 1, Ex. 2, Ex. 3, Ex. 4, Ex. 5, Ex. 6, Ex. 7(A)–7(F), Ex. 8, Ex. 9 |
| `06_exemptions_exemption_3_statutes` | Statute; Case Citation; Type of Information Withheld; Number of Times Relied Upon |
| `07_appeals` | Appeals Pending at Start; Received; Processed; Pending at End |
| `08_appeals_disposition_dis` | Affirmed; Partially Affirmed & Partially Reversed/Remanded; Completely Reversed/Remanded; Closed for Other Reasons; Total |
| `09_appeals_dis_use_of_exemptions` | Ex. 1 … Ex. 9 (same as 05) |
| `10_appeals_dis_other_than_exs` | No Records; Records Referred at Initial Request Level; Request Withdrawn; Fee-Related Reason; Records Not Reasonably Described; Improper Request for Other Reason; Not Agency Record; Duplicate Request or Appeal; Request in Litigation; Appeal Based Solely on Denial of Expedited Processing; Other* |
| `11_appeals_dis_other_reasons` | Total |
| `12_appeals_response_time` | Median / Average / Lowest / Highest Number of Days |
| `13_appeals_ten_oldest_pending` | 10 pairs of `Date` + `Nth Oldest Number of Days Pending` (10th oldest → Oldest). The `Date` header repeats 10 times, so rename columns on load |
| `14_processing_time` | Simple / Complex / Expedited × Median / Average / Lowest / Highest Days (12 cols) |
| `15_processing_time_requests_granted` | Same 12 columns as 14 |
| `16`, `17`, `18` (simple / complex / expedited) | Day bins: <1-20, 21-40, 41-60, 61-80, 81-100, 101-120, 121-140, 141-160, 161-180, 181-200, 201-300, 301-400, 401+; Total |
| `19_processing_time_pending_requests` | Simple / Complex / Expedited × Number Pending, Median Days, Average Days |
| `20_processing_time_ten_oldest_requests` | Same layout as 13 (repeated `Date` header) |
| `21_fee_waiver` | Number Granted; Number Denied; Median / Average Days to Adjudicate |
| `22_foia_personnel` | Full-Time FOIA Employees; Equivalent Full-Time FOIA Employees; Total Full-Time FOIA Staff |
| `23_foia_costs` | Processing Costs; Litigation-Related Costs; Total Costs; Total Amount of Fees Collected; Percentage of Total Costs |
| `24_exclusions` | Number of Times Subsection Used |
| `25_proactive_disclosures` | Records Posted by the FOIA Office; Records Posted by Program Offices |
| `26_backlog` | Backlogged Requests at End of FY; Backlogged Appeals at End of FY |
| `27_consultations` | Consultations Pending at Start; Received; Processed; Pending at End |
| `28_consultations_ten_oldest` | Same layout as 13 (repeated `Date` header) |
| `29_comparisons` / `31_comparisons_administrative_appeals` | Received from Last Year's Report; Received from Current Report; Processed from Last Year's Report; Processed from Current Report |
| `30_comparisons_requests_backlogged` / `32_comparisons_appeals_backlogged` | Backlogged at End of FY from Previous Report; from Current Report |

### Loading example
All values are text. Besides numbers you will see `N/A`, blanks and `<1` (less than one day), so convert with `errors="coerce"`.

```python
import pandas as pd
from pathlib import Path

root = Path("fa26/dataset/raw_agency_level")
frames = [pd.read_csv(p, dtype=str) for p in sorted(root.glob("20*/26_backlog.csv"))]
backlog = pd.concat(frames, ignore_index=True)
backlog = backlog[backlog["Agency"] != "All agencies"]          # drop government-wide total
col = "Number of Backlogged Requests as of End of Fiscal Year"
backlog[col] = pd.to_numeric(backlog[col].str.strip(), errors="coerce")
```

---

## 3. Component-level tables (`component_level/`)

### Source and collection
Built from the **foia.gov API annual reports** (the data behind foia.gov), downloaded October 18–19, 2026. Covers FY2008–FY2025. Values are copied as reported; only surrounding whitespace was trimmed, and the text fields of data types 03, 06 and 11 were cleaned (HTML entities, quote styles, line breaks, N/A spellings). See `component_level/README.md` for the full build notes.

### Master dataset at a glance
- **8,139 rows**: agency totals + components, per year.
- **244 data columns**, grouped by data type.
- Split out into their own tables: the "Other" reasons (03, 11) and the Exemption 3 statutes (06).
- The agency totals match the agency-level table (foia.gov CSV exports, with a few gaps filled from the API).

### Files

| File | Rows | Columns | Grain |
|---|---:|---:|---|
| `component_master_no_03_06_11.csv` | 8,139 | 252 | Fiscal year × agency × component (plus one Agency Overall row per agency-year) |
| `other_reasons_03_11.csv` | 13,903 | 12 | Fiscal year × agency × component × "Other" reason (data types 03 and 11) |
| `exemption_statutes_06.csv` | 16,532 | 12 | Fiscal year × agency × component × Exemption 3 statute (data type 06) |

- **`component_master_no_03_06_11.csv`**: the combined table of all data types in one wide CSV, **leaving out the detail of data types 03, 06 and 11**. 03 and 11 ("Other" reasons) would add many mostly-empty columns, since every agency writes its own reasons, so only their total column is kept here. 06 (Exemption 3 statutes) has a different shape, with one row per statute and text values, so it doesn't fit as columns.
- **`exemption_statutes_06.csv`**: only data type 06 (Exemption 3 statutes), in its own table because its data has a different shape: one row per statute cited.
- **`other_reasons_03_11.csv`**: the itemized "Other" reasons for data types 03 (requests) and 11 (appeals), one row per reason.

### Per-year summary

| Fiscal Year | Data types | Agencies reporting | Agencies with components | Component rows | Agencies added vs prior year | Agencies removed vs prior year |
|---|---:|---:|---:|---:|---:|---:|
| 2008 | 32 | 71 | 21 | 307 | — | — |
| 2009 | 32 | 73 | 22 | 314 | 2 | 0 |
| 2010 | 32 | 97 | 25 | 360 | 24 | 0 |
| 2011 | 32 | 99 | 25 | 360 | 2 | 0 |
| 2012 | 32 | 99 | 26 | 361 | 0 | 0 |
| 2013 | 32 | 99 | 25 | 357 | 1 | 1 |
| 2014 | 32 | 100 | 26 | 352 | 1 | 0 |
| 2015 | 32 | 100 | 26 | 350 | 1 | 1 |
| 2016 | 32 | 115 | 27 | 349 | 15 | 0 |
| 2017 | 32 | 116 | 29 | 356 | 1 | 0 |
| 2018 | 32 | 118 | 29 | 360 | 2 | 0 |
| 2019 | 32 | 118 | 29 | 350 | 0 | 0 |
| 2020 | 32 | 119 | 28 | 348 | 3 | 2 |
| 2021 | 32 | 118 | 29 | 350 | 0 | 1 |
| 2022 | 32 | 120 | 29 | 349 | 2 | 0 |
| 2023 | 32 | 121 | 30 | 352 | 1 | 0 |
| 2024 | 32 | 122 | 28 | 310 | 1 | 0 |
| 2025 | 32 | 118 | 28 | 306 | 1 | 5 |
| **Total** | | **1,923** agency-years | | **6,191** | | |

- **Agencies reporting** = the number of Agency Overall rows that year.
- **Agencies with components** = agencies that also have one or more component rows. All other agencies have **only** the Agency Overall row.
- **Component rows** = rows with `Row Type = component` that year.
- **Data types** = the files foia.gov publishes each year. Data types 24 and 25 are almost entirely blank before FY2017.
- **Agencies added / removed** = whether foia.gov has a report for that agency that year, not whether the agency was created or closed.

### ID columns (first 8 columns of all three files)

| Column | Meaning |
|---|---|
| `Fiscal Year` | 2008–2025 |
| `Agency` | Agency name, spelled as in the agency-level data |
| `Agency Abbreviation` | As on foia.gov (e.g. `DOJ`, `CSB`) |
| `Component` | Component abbreviation in foia.gov's **current** form (e.g. Army = `DA`). Most offices keep one abbreviation in every year, but some appear under two (e.g. Interior's `OSM` became `OSMRE` in FY2020), so check `Component Name` when following one office over time. `Agency Overall` for the agency total |
| `Component Name` | Full component name. In the master table, use `Component` + `Component Name` + `Row Type` as the key within an agency-year, because two components can share an abbreviation and a `second_entry` row repeats the abbreviation and name of its first entry |
| `Row Type` | `agency_overall`, `component`, `second_entry`, or `no_component` (below) |
| `Exclude From Component Sum` | `yes` = leave this row out when summing components |
| `Exclude Reason` | Why the row is excluded |

**Row Type**

| Value | Meaning | Rows (master) |
|---|---|---:|
| `agency_overall` | Agency total, one per agency-year. For an agency without components, this is the only row | 1,923 |
| `component` | One office inside the agency | 6,191 |
| `second_entry` | A second entry in a table; foia.gov counts both in the total | 10 |
| `no_component` | Numbers foia.gov doesn't tie to any office | 15 |

**`Exclude From Component Sum`** is `yes` only for Commerce FY2025 "DOC" (Departmental Offices). That row is a copy of a total, not a real office, so adding it to the other components doubles Commerce's numbers.

### `component_master_no_03_06_11.csv`
8 ID columns + **244 data columns** covering 31 of the 32 data types (all except 06). Data column names follow the pattern `<NN>_<ShortName>__<Field>`, e.g. `26_Backlog__BackloggedRequestQuantity`, `01_Requests__ProcessingStatisticsReceivedQuantity`, `02_Disposition__NonExemptionDenialQuantity[NoRecords]`.

| No. | Column prefix | No. | Column prefix |
|---|---|---|---|
| 01 | `01_Requests__` | 17 | `17_ComplexRequests__` |
| 02 | `02_Disposition__` | 18 | `18_ExpeditedRequests__` |
| 03 | `03_DispositionOtherReasons__` (total only) | 19 | `19_PendingRequests__` |
| 04 | `04_ExpeditedProcessing__` | 20 | `20_TenOldestRequests__` |
| 05 | `05_Exemptions__` | 21 | `21_FeeWaiver__` |
| 06 | *not here; see `exemption_statutes_06.csv`* | 22 | `22_Personnel__` |
| 07 | `07_Appeals__` | 23 | `23_Costs__` |
| 08 | `08_AppealsDisposition__` | 24 | `24_Exclusions__` |
| 09 | `09_AppealsExemptions__` | 25 | `25_ProactiveDisclosures__` |
| 10 | `10_AppealsOtherThanExemptions__` | 26 | `26_Backlog__` |
| 11 | `11_AppealsOtherReasons__` (total only) | 27 | `27_Consultations__` |
| 12 | `12_AppealsResponseTime__` | 28 | `28_ConsultationsTenOldest__` |
| 13 | `13_AppealsTenOldest__` | 29 | `29_Comparisons__` |
| 14 | `14_ProcessingTime__` | 30 | `30_ComparisonsRequestsBacklogged__` |
| 15 | `15_ProcessingTimeGranted__` | 31 | `31_ComparisonsAppeals__` |
| 16 | `16_SimpleRequests__` | 32 | `32_ComparisonsAppealsBacklogged__` |

The total number of times Exemption 3 was used is still in the master table, in the `Ex. 3` columns of 05 and 09.

### `other_reasons_03_11.csv`
ID columns + `Data Type No.` (`03` or `11`), `Data Type` (foia.gov name, e.g. `Requests - Dis. - "Other" Reasons`), `Reason` (cleaned free text), `Quantity`.

### `exemption_statutes_06.csv`
ID columns + `Statute`, `Type of Information Withheld`, `Case Citation`, `Number of Times Relied Upon`.
- The same statute may appear more than once for an agency; all entries are kept.
- The same statute is written in many different ways (e.g. 30 variants of 26 U.S.C. § 6103), so group statute names before ranking them.

### How to aggregate correctly
- **In the master table and the 06 table, use either the `agency_overall` row or the other rows, never both.** Summing all rows doubles the total (e.g. DHS FY2024 backlog: components = 141,420, Agency Overall = 141,420, all rows = 282,840). The 03/11 table has no such overlap: an agency-year has either `agency_overall` rows or other rows, not both.
- When summing components, include `component`, `second_entry` and `no_component` rows, and **leave out rows where `Exclude From Component Sum == "yes"`**.
- Only counts, dollars and FTE can be summed. Medians, averages, days and dates cannot.

```python
import pandas as pd
m = pd.read_csv("fa26/dataset/component_level/component_master_no_03_06_11.csv", dtype=str, keep_default_na=False)

overall = m[m["Row Type"] == "agency_overall"]
parts = m[(m["Row Type"] != "agency_overall") & (m["Exclude From Component Sum"] != "yes")]
```

### What 0, N/A and blank mean

| Value | Meaning |
|---|---|
| `0` | In count columns, the agency reported zero. In days columns and the ten-oldest columns, it usually means there were no such cases, not 0 days (e.g. all 100 rows with an expedited median of 0 have 0 expedited requests). |
| `N/A` | Not applicable, or nothing to calculate (e.g. 4,579 of the 4,801 rows with an N/A expedited median have 0 expedited requests). |
| blank | Usually the component is not in that data type's table, so the whole table is blank for that row (e.g. 31 of DOJ's 32 components in the FY2025 appeals tables, because all its appeals are reported under OIP). Data types 24 and 25 are also almost entirely blank before FY2017. |
| `<1` | Less than one day. |

### Known issues (from `component_level/README.md`)
These problems are in foia.gov's own data. The numbers are kept as reported.

- **Commerce FY2025 "DOC" row (flagged `Exclude From Component Sum = yes`).** In the master table it repeats the Agency Overall row: the same number in 239 of 244 columns (e.g. requests received: 5,368). In the 06 table it copies the other components added together. As a result, the Commerce FY2025 Agency Overall statute counts are doubled (276; the correct total is 138). Add up the components instead.
- **Components that don't add up to the agency total** (13 agency-years): Veterans Affairs FY2025 (47 columns), GSA FY2016 (20), EPA FY2011 (8), Defense FY2025 (3), Commerce FY2025 (2), Agriculture, Labor and EEOC FY2025 (1 each), and USPS FY2010, 2013, 2014, 2016, 2017 (appeals pending at end of year).
- **FY2025, data type 11:** 8 agencies report component values but have a blank Agency Overall cell: Justice 1,045, Veterans Affairs 192, EEOC 76, Labor 52, Energy 45, Defense 14, Agriculture 4, Commerce 1. Add up the components.
- **Energy FY2025 HQ, data type 11:** the reasons add up to 49, but the total column says 45.
- **FY2022, All agencies:** foia.gov's CSV export leaves out USAGM, so its All agencies row shows 928,261 requests received. Adding the Agency Overall rows gives 928,353, because the API includes USAGM's 92 requests.
- **Shared abbreviations:** USPS FY2019–2024 has two `PS` components (`HQ Postal Service` and `USPS Field Office`).
- **Some components are named oddly on foia.gov** and are kept as they are (e.g. EPA FY2013 and FY2015 `EPA OLD DO NOT USE`).
- **Value formats:**
  - N/A is spelled several ways (`N/A`, `n/a`, `N/a`, `NA`, `na`, `N\A`, `N.A`, `N./A`, `N/`). One cell reads `N/S` (CPPBSD FY2025, average days to decide appeals).
  - `<1` means less than one day.
  - Some decimals have no leading 0 (`.5`).
  - 4 counts are negative: Labor FY2023 OIG (2); Treasury FY2019 Fiscal Service; HHS FY2025 ARPA-H.
  - One date is written `09-15-2025` instead of `2025-09-15` (CPSC FY2025, third oldest pending appeal).

### How the tables were checked
- Every cell was checked against the API reports a second time, by separate code: no differences.
- The Agency Overall rows were compared with the agency-level table across all 244 columns: 469,204 cells match. 8 cells differ, where foia.gov's CSV export is blank but the API has an entry: SBA FY2021 fee waiver median/average days; CEQ FY2023 pending requests median/average days.
- FY2024 components were compared with foia.gov's component-level CSV export (23 data types): 36,466 cells, all match.
- The 06 Agency Overall rows were compared with the agency-level statute table: all 1,919 agency-years with statutes match.

---

## 4. Agency-level vs component-level at a glance

| | Agency-level CSVs | Component-level tables |
|---|---|---|
| Source | foia.gov CSV export (report builder page) | foia.gov API annual reports |
| Years | FY2008–2025 | FY2008–2025 |
| Granularity | Agency totals only | Agency totals + each component |
| Layout | Long: 1 file per year × data type, human-readable headers | Wide: 1 master table (all data types except 06) + 2 long tables |
| Government-wide total row | Yes (`All agencies`, in most files) | No; sum the `agency_overall` rows |
| Data type 06 | Per-year file, raw text | `exemption_statutes_06.csv`, text cleaned |
| 03 / 11 "Other" reasons | Totals only | Totals + itemized reasons |
| Cleaning | None (raw export) | Whitespace trimmed; 03/06/11 text cleaned; values otherwise as reported |
| Best for | Quick per-agency trends on one topic | Office-level analysis, cross-topic joins, statute/reason analysis |

**Joining the two:** match on `Agency` + `Fiscal Year`, and use only the component-level `agency_overall` rows. Check for names that don't match, since an agency's name can be spelled differently in different years.

---

## 5. Recommended handling checklist
1. Read every CSV with `dtype=str`, strip whitespace, then convert numeric columns with `errors="coerce"`; decide explicitly how to treat `N/A`, blank and `<1`.
2. Agency-level: drop `Agency == "All agencies"` before aggregating; rename the repeated `Date` columns in files 13, 20, 28.
3. Component-level: never mix `agency_overall` rows with component rows in one sum; leave out rows marked in `Exclude From Component Sum`.
4. Don't sum medians, averages, days or dates.
5. Group statute names (06) and agency names (across years) before counting.
