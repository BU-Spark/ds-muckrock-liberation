# component_master

Component-level FOIA data, FY2008-2025, from the foia.gov XML annual reports, with data the XML is missing filled from the foia.gov API.

- `component_master_no_03_06_11.csv` (8,088 rows, 253 columns): one row per fiscal year x agency x component, plus one "Agency Overall" row per agency per year (1,923). 9 ID columns and 244 data columns covering 31 of the 32 data types. Column names start with the data type number (01-32).
  - 06 (Exemption 3 statutes) is not in this table at all; it is in `exemption_statutes_06.csv`. This table only has the total number of times Exemption 3 was used (05 and 09, `Ex. 3` columns).
  - For 03 and 11 ("Other" reasons) only the total column is kept; the reasons are in `other_reasons_03_11.csv`.
- `other_reasons_03_11.csv` (13,700 rows, 13 columns): the 03 and 11 "Other" reasons, one row per fiscal year x agency x component x reason. The same 9 ID columns as the master table, plus Data Type No., Data Type (the foia.gov name, e.g. `Requests - Dis. - "Other" Reasons`), Reason, Quantity. Only reported values are included.
- `exemption_statutes_06.csv` (16,632 rows, 13 columns): 06 Exemption 3 statutes, one row per fiscal year x agency x component x statute. The same 9 ID columns as the master table, plus Statute, Type of Information Withheld, Case Citation, Number of Times Relied Upon.
- `clean_text_03_06_11.py`: the text cleaning used for the text columns of the 03/11 and 06 files (see below).

Values are copied as reported: blank, 0 and N/A are not changed (the text columns of the 03/11 and 06 files only get the formatting clean-up described below).

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

## Text cleaning (03/11 and 06)
The text columns (`Reason` in the 03/11 file; `Statute`, `Type of Information Withheld`, `Case Citation` in the 06 file) are cleaned with `clean_text_03_06_11.clean_text()`, because the same text is written differently depending on the source (foia.gov API, XML annual reports, or the foia.gov CSV export): HTML codes such as `&quot;`, curly vs straight quotes, line breaks, and spellings of N/A. Only formatting changes; counts and ID columns are not touched.

## 06 Exemption 3 statutes
- An agency sometimes lists the same statute more than once; every entry is kept (the foia.gov CSV export shows only one of them).
- Statute names are written in many ways (1,587 different texts; 30 for 26 U.S.C. § 6103). Group them before ranking statutes.
- Commerce FY2025: the "DOC" (Departmental Offices) row is not a separate office. In this file it repeats the other components (same statutes, same counts, 138 in all), and the Agency Overall row adds both, so every count is doubled (276; the correct total is 138). The DOC row is flagged in `Exclude From Component Sum`; for Commerce FY2025, add up the components instead of using Agency Overall.

## Columns to know

### ID columns (the first 9 columns of every file)

| Column | Meaning |
|---|---|
| `Fiscal Year` | 2008-2025. |
| `Agency` | Agency name, spelled as in the agency-level table (128 agencies). |
| `Agency Abbreviation` | As written in the report (EXIM appears as both "EXIM" and "EXIM Bank"). |
| `Component` | Component abbreviation as written in that year's report; "Agency Overall" for the agency total. Abbreviations can change between years (e.g. DoD's ARMY became DA in FY2025). |
| `Component Name` | Full component name. Use it, not the abbreviation, to follow a component across years. |
| `Row Type` | What kind of row it is (see below). |
| `Org Ref ID` | The organization ID inside the XML report (ORG0 = the agency itself). Numbered separately in each report, so it does not match across years; it tells apart two components with the same abbreviation in one year (e.g. USPS FY2019 has two "PS"). "API-HQ" and "API-OIG" mark 2 rows (EXIM FY2024) taken from the foia.gov API. |
| `Exclude From Component Sum` | `yes` = leave this row out when adding up components (see below). |
| `Exclude Reason` | Why the row is excluded (only Commerce FY2025 "DOC"). |

### `Row Type`: what kind of row it is

| Row Type | Meaning |
|---|---|
| `agency_overall` | The whole agency's total (one row per agency per year). |
| `component` | One office inside the agency. |
| `duplicate_entry` | A second entry for an office that the agency reported twice (5 rows). |

**Use the Agency Overall row or the component rows, never both.** The components add up to the agency total (except where part of the data is not linked to any component, see "Not included"). Example, DHS FY2024 backlog: the 15 components add up to 141,420, and the Agency Overall row is also 141,420. Adding all 16 rows would give 282,840, twice the real number.

**`duplicate_entry` rows:** in 5 cases the agency's report lists the same office twice in one table. In 4 of them the two entries have different numbers. Example: NARA FY2025, 03 "Other" reasons: one entry says 23, the other says 97. We can't tell which one is right, so the first entry is the normal `component` row and the second is kept as its own row (only that table's columns are filled). In the fifth case (VA FY2022, ODASB, 05 exemptions) the second entry is empty, so that row has no data. Leave these rows out of totals unless you have checked them.

### `Exclude From Component Sum`: skip this row when adding up components

Only one row has `yes`: Commerce FY2025 "DOC" (Departmental Offices). It looks like an office, but it is really a copy of a total:
- In the master table it copies the Agency Overall. Requests received: Agency Overall 5,368, DOC 5,368, the other components together 5,368.
- In the 06 table it copies the other components added together (see above).

If you add it to the other components, the Commerce numbers come out twice as large.

## Not included
**Data the XML does not assign to any component.** In some reports, part of the numbers is not linked to any office. It is counted in the Agency Overall row, but there is no component row for it. Example, USPS FY2024 requests received: Agency Overall 4,429; components OIG 883 + PIS 666 = 1,549; the other 2,880 are not linked to an office in the XML (the foia.gov CSV export shows them under "PS"). This happens in 79 agency-years, so for those agencies the components add up to less than the Agency Overall.

## Known source issue
**FY2025, 11 (appeals "Other" reasons): the Agency Overall total is 0 for 8 agencies whose components report values.** Justice 1,045, Veterans Affairs 192, EEOC 76, Labor 52, Energy 45, Defense 14, Agriculture 4, Commerce 1. The numbers are kept as the agencies reported them; for these 8, add up the components instead of using Agency Overall.
