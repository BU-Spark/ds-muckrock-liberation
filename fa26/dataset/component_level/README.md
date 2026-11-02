# component_level

Component-level FOIA data, FY2008-2025, built from the foia.gov API annual reports (the data behind foia.gov, downloaded October 18-19, 2026). The XML annual reports are no longer used.

- `component_master_no_03_06_11.csv` (8,139 rows, 252 columns): one row per fiscal year x agency x component, plus one "Agency Overall" row per agency per year (1,923). 8 ID columns and 244 data columns covering 31 of the 32 data types. Column names start with the data type number (01-32).
  - 06 (Exemption 3 statutes) is not in this table at all; it is in `exemption_statutes_06.csv`. This table only has the total number of times Exemption 3 was used (05 and 09, `Ex. 3` columns).
  - For 03 and 11 ("Other" reasons) only the total column is kept; the reasons are in `other_reasons_03_11.csv`.
- `other_reasons_03_11.csv` (13,903 rows, 12 columns): the 03 and 11 "Other" reasons, one row per fiscal year x agency x component x reason. The same 8 ID columns as the master table, plus Data Type No., Data Type (the foia.gov name, e.g. `Requests - Dis. - "Other" Reasons`), Reason, Quantity.
- `exemption_statutes_06.csv` (16,532 rows, 12 columns): 06 Exemption 3 statutes, one row per fiscal year x agency x component x statute. The same 8 ID columns as the master table, plus Statute, Type of Information Withheld, Case Citation, Number of Times Relied Upon.
- `../../scripts/clean_text_03_06_11.py`: the text cleaning used for the text columns of the 03/11 and 06 files (see below).

Values are copied from the API as they are: blank, 0, N/A and "<1" are not changed. Only spaces around a value are removed (e.g. "814 " -> "814"), and the text columns of the 03/11 and 06 files get the formatting clean-up described below.

## Data types and column prefixes
Columns in the master table start with the data type number and a short name (e.g. `26_Backlog__BackloggedRequestQuantity`). The foia.gov name of each data type:

| No. | Column prefix in the master table | foia.gov data type |
|---|---|---|
| 01 | `01_Requests__` | Requests |
| 02 | `02_Disposition__` | Requests - Disposition (Dis.) |
| 03 | `03_DispositionOtherReasons__` | Requests - Dis. - "Other" Reasons |
| 04 | `04_ExpeditedProcessing__` | Requests - Expedited Processing |
| 05 | `05_Exemptions__` | Exemptions |
| 06 | (not in the master table; see `exemption_statutes_06.csv`) | Exemptions - Exemption 3 Statutes |
| 07 | `07_Appeals__` | Appeals |
| 08 | `08_AppealsDisposition__` | Appeals - Disposition (Dis.) |
| 09 | `09_AppealsExemptions__` | Appeals - Dis. - Use of Exemptions |
| 10 | `10_AppealsOtherThanExemptions__` | Appeals - Dis. - Other Than Exs. |
| 11 | `11_AppealsOtherReasons__` | Appeals - Dis. - "Other" Reasons |
| 12 | `12_AppealsResponseTime__` | Appeals - Response Time |
| 13 | `13_AppealsTenOldest__` | Appeals - Ten Oldest Pending |
| 14 | `14_ProcessingTime__` | Processing Time |
| 15 | `15_ProcessingTimeGranted__` | Processing Time - Requests Granted |
| 16 | `16_SimpleRequests__` | Processing Time - Simple Requests |
| 17 | `17_ComplexRequests__` | Processing Time - Complex Requests |
| 18 | `18_ExpeditedRequests__` | Processing Time - Expedited Requests |
| 19 | `19_PendingRequests__` | Processing Time - Pending Requests |
| 20 | `20_TenOldestRequests__` | Processing Time - Ten Oldest Requests |
| 21 | `21_FeeWaiver__` | Fee Waiver |
| 22 | `22_Personnel__` | FOIA Personnel |
| 23 | `23_Costs__` | FOIA Costs |
| 24 | `24_Exclusions__` | Exclusions |
| 25 | `25_ProactiveDisclosures__` | Proactive Disclosures |
| 26 | `26_Backlog__` | Backlog |
| 27 | `27_Consultations__` | Consultations |
| 28 | `28_ConsultationsTenOldest__` | Consultations - Ten Oldest |
| 29 | `29_Comparisons__` | Comparisons |
| 30 | `30_ComparisonsRequestsBacklogged__` | Comparisons - Requests Backlogged |
| 31 | `31_ComparisonsAppeals__` | Comparisons - Administrative Appeals |
| 32 | `32_ComparisonsAppealsBacklogged__` | Comparisons - Appeals Backlogged |

## Text cleaning (03, 11 and 06)
The text columns (`Reason` in the 03/11 file; `Statute`, `Type of Information Withheld`, `Case Citation` in the 06 file) are cleaned with `clean_text_03_06_11.clean_text()`: HTML codes such as `&quot;`, curly vs straight quotes, line breaks, and spellings of N/A. Only formatting changes; counts and ID columns are not touched.

## 06 Exemption 3 statutes
- An agency sometimes lists the same statute more than once; every entry is kept.
- Statute names are written in many ways (1,588 different texts; 30 for 26 U.S.C. § 6103). Group them before ranking statutes.
- Commerce FY2025: the "DOC" (Departmental Offices) rows repeat the other components (same statutes, same counts, 138 in all), and the Agency Overall rows add both, so every count is doubled (276; the correct total is 138). The DOC rows are flagged in `Exclude From Component Sum`; for Commerce FY2025, add up the components instead of using Agency Overall.

## Columns to know

### ID columns (the first 8 columns of every file)

| Column | Meaning |
|---|---|
| `Fiscal Year` | 2008-2025. |
| `Agency` | Agency name, spelled as in the agency-level table (128 agencies). |
| `Agency Abbreviation` | As on foia.gov. |
| `Component` | Component abbreviation as foia.gov writes it now, the same in every year (e.g. DoD's Army is `DA` from FY2008 on, its Inspector General `DoW OIG`). Some are written oddly on the site and are kept as they are (e.g. EPA FY2013 and FY2015 `EPA OLD DO NOT USE`). "Agency Overall" for the agency total. |
| `Component Name` | Full component name, as on foia.gov. Two components can share an abbreviation: USPS FY2019-2024 has two "PS", `HQ Postal Service` and `USPS Field Office`, so use the abbreviation and the name together to tell components apart. |
| `Row Type` | What kind of row it is (see below). |
| `Exclude From Component Sum` | `yes` = leave this row out when adding up components (see below). |
| `Exclude Reason` | Why the row is excluded (only Commerce FY2025 "DOC"). |

### `Row Type`: what kind of row it is

| Row Type | Meaning | Rows |
|---|---|---:|
| `agency_overall` | The whole agency's total (one row per agency per year). | 1,923 |
| `component` | One office inside the agency. | 6,191 |
| `second_entry` | A second entry the agency reported for the same office in one table. foia.gov keeps both, and its agency total counts both (e.g. Peace Corps FY2022 costs: OIG 310,000 + second entry 86,900 = Agency Overall 396,900). Only that table's columns are filled. | 10 |
| `no_component` | Numbers foia.gov does not link to any office (e.g. Commerce FY2014, Legal Services Corporation FY2016-2018). | 15 |

**Use the Agency Overall row or the other rows, never both.** The `component`, `second_entry` and `no_component` rows (without the Exclude row) add up to the Agency Overall row, except in the 13 agency-years listed below. Example, DHS FY2024 backlog: the 15 components add up to 141,420, and the Agency Overall row is also 141,420. Adding all 16 rows would give 282,840, twice the real number.

**Agencies that are one organization** (no components, or one component that is the agency itself) have only the Agency Overall row: 1,441 of the 1,923 agency-years. 482 agency-years (32 agencies) have component rows.

**The Agency Overall row** is foia.gov's agency total. Where foia.gov has no total for a one-organization agency, its own entry is used. These totals match the agency-level table except 8 cells where foia.gov's CSV export (which the agency-level table comes from) is blank and the API has the number: Small Business Administration FY2021 fee waiver median and average days (13, 7.98), Council on Environmental Quality FY2023 pending requests median and average days (6 cells).

### `Exclude From Component Sum`: skip this row when adding up components

Only Commerce FY2025 "DOC" (Departmental Offices) has `yes`. It looks like an office, but it is really a copy of a total:
- In the master table it repeats the Agency Overall: the same number in 239 of the 244 columns (it leaves the 03 total blank, and has 0 for 4 exemptions where the total is blank). Requests received: Agency Overall 5,368, DOC 5,368, the other components together 5,368.
- In the 06 table it copies the other components added together (see above).

If you add it to the other components, the Commerce numbers come out twice as large.

## Known source issues
These are in foia.gov's own data; the numbers are kept as reported.
- **Components that do not add up to the agency total** (13 agency-years): Veterans Affairs FY2025 (47 columns, e.g. requests pending at the end of the year), General Services Administration FY2016 (20), Environmental Protection Agency FY2011 (8), Defense FY2025 (3), Commerce FY2025 (2), Agriculture, Labor and EEOC FY2025 (1 each), USPS FY2010, 2013, 2014, 2016 and 2017 (appeals pending at the end of the year).
- **FY2025, 11 (appeals "Other" reasons): no agency total for 8 agencies whose components report values.** Justice 1,045, Veterans Affairs 192, EEOC 76, Labor 52, Energy 45, Defense 14, Agriculture 4, Commerce 1. The Agency Overall cell is blank; add up the components.
- **Energy FY2025, HQ, 11 reasons**: the reasons add up to 49, the total column says 45.
- **How values are written in the source**: N/A is spelled several ways (`N/A`, `n/a`, `N/a`, `NA`, `N\A`, `N.A`); `<1` means less than one day; some decimals have no leading 0 (`.5`). 4 counts are negative (Labor FY2023 OIG, simple requests 21-40 and 41-60 days: -2 and -1; Treasury FY2019 Fiscal Service, complex requests 141-160 days: -1; HHS FY2025 ARPA-H, backlog last year: -2). One date is written `09-15-2025` instead of `2025-09-15` (Consumer Product Safety Commission FY2025, third oldest pending appeal).

## How the tables were checked
- Every cell of every row against the API reports, read a second time by separate code: no differences.
- Agency Overall rows against the agency-level table (`agency_level/FOIA_agency_FY2008-2025.csv`, from foia.gov's CSV export), all 244 columns: 469,204 cells the same, 8 different (listed above).
- FY2024 components against foia.gov's component-level CSV export: 36,466 cells, all the same.
- 06 Agency Overall rows against the agency-level statute table: all 1,919 agency-years with statutes the same.

## Changes from the earlier version (built from the XML)
- All three tables now come from the API. The XML left some blocks of data without an office (e.g. DoD FY2008 Army, USPS "PS" FY2020-2024, DHS CRCL FY2009 and FY2011-2016), so those offices were missing; they are in now. The earlier "Not included" note no longer applies.
- Component abbreviations are foia.gov's current ones, the same in every year (DoD `ARMY` -> `DA`, `NAVY` -> `DON`, `AF` -> `DAF`, `DoD IG` -> `DoW OIG`, ...).
- One-organization agencies (e.g. NARA, NCUA, Amtrak) no longer have a component row that repeated the Agency Overall.
- The `Org Ref ID` column (the organization ID inside the XML report) is removed; tell components apart by `Component` and `Component Name`.
- `duplicate_entry` is now `second_entry`, and it is counted in the agency total (as foia.gov does).
- 0, N/A and blank are written as foia.gov writes them (the XML often wrote them differently), so they now match the agency-level table.
