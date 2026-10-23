# FOIA Data Types 17–24: Column-by-Column Guide

This guide covers only the eight merged source CSVs numbered 17–24 in `output/by_data_type/`. It does not use EDA summary tables to define fields. Column names and order come directly from each CSV header.

## Shared interpretation

- Every file covers FY2008–FY2025 and contains 1,921 agency-year rows representing 128 agency names. Not every agency has a row in every year. `Agency` and `Fiscal Year` identify a row.
- In types 17–20, the processing and pending durations are **working days** and apply to perfected requests. Values in the day-band columns of types 17–18 are **request counts**. The official fee-waiver field instructions for type 21 say 'days' without explicitly specifying working or calendar days.
- CSV values are initially read as strings; the variable types below are semantic analysis types. A `numerical` field may contain `<1`, `N/A`, or other nonnumeric source values in types 19 and 21. Type 20 date fields may contain `N/A`, `0`, or blanks. Neither `<1` nor a blank should automatically be converted to zero.
- `missing tables` is produced by the year-by-year merge script. It lists **whole source tables missing for that fiscal year**, not missing fields unique to the agency row.
- In type 20, `.1`–`.9` distinguish repeated source headers named `Date`. These dates correspond to the ninth-oldest through oldest pending requests, and rank is based on working days pending.
- In type 23, interpret `Percentage of Total Costs` as **fees collected / processing costs × 100**. DOJ training materials and most rows in these CSVs support that direction. The latest handbook's wording of the Section X formula conflicts with its illustration/training materials, and some source CSV values are inconsistent with the formula; retain source values and review anomalies separately.
- This guide uses the current DOJ handbook to explain a historical series. Reporting templates or definitions may have varied across FY2008–FY2025; check the original report for a specific year when precise longitudinal comparability matters.

## Datasets and columns

### 17 | Complex requests: processing-time distribution

**File:** [`17_processing_time_complex_requests_FY2008-2025_all_agencies.csv`](17_processing_time_complex_requests_FY2008-2025_all_agencies.csv). **Size:** 1,921 rows, 17 columns. **Meaning:** Counts perfected requests completed during the fiscal year by working-day processing-time band in the complex track. Agencies may apply different criteria for classifying a request as complex. [DOJ Annual FOIA Report Handbook, §VII.C.(2)](https://www.justice.gov/oip/media/1418941/dl?inline=).

| Original column name | Meaning | Variable type | Unit | Interpretation notes |
|---|---|---|---|---|
| `Agency` | Name of the federal agency reporting the annual FOIA data. | categorical | agency | An agency identifier, not a numerical measure. |
| `Fiscal Year` | U.S. federal fiscal year covered by the FOIA annual report. | numerical | year | Integer time key; not the date when this CSV was generated. |
| `missing tables` | Semicolon-separated short names of source data-type tables missing from that fiscal year's merge. | text | — | A fiscal-year-wide source-table flag, not a missingness indicator specific to this agency row; blank does not imply all metric values are zero. |
| `days_complex__<1-20 Days` | Number of perfected complex-track requests completed in the fiscal year within less than one through 20 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__21-40 Days` | Number of perfected complex-track requests completed in the fiscal year within 21-40 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__41-60 Days` | Number of perfected complex-track requests completed in the fiscal year within 41-60 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__61-80 Days` | Number of perfected complex-track requests completed in the fiscal year within 61-80 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__81-100 Days` | Number of perfected complex-track requests completed in the fiscal year within 81-100 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__101-120 Days` | Number of perfected complex-track requests completed in the fiscal year within 101-120 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__121-140 Days` | Number of perfected complex-track requests completed in the fiscal year within 121-140 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__141-160 Days` | Number of perfected complex-track requests completed in the fiscal year within 141-160 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__161-180 Days` | Number of perfected complex-track requests completed in the fiscal year within 161-180 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__181-200 Days` | Number of perfected complex-track requests completed in the fiscal year within 181-200 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__201-300 Days` | Number of perfected complex-track requests completed in the fiscal year within 201-300 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__301-400 Days` | Number of perfected complex-track requests completed in the fiscal year within 301-400 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__401+ Days` | Number of perfected complex-track requests completed in the fiscal year within 401 or more working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_complex__Total` | Total perfected complex-track requests completed in the fiscal year, summed across the 13 processing-time bands. | numerical | requests | Not an average or median processing time. |

### 18 | Expedited requests: processing-time distribution

**File:** [`18_processing_time_expedited_requests_FY2008-2025_all_agencies.csv`](18_processing_time_expedited_requests_FY2008-2025_all_agencies.csv). **Size:** 1,921 rows, 17 columns. **Meaning:** Counts completed perfected requests granted expedited processing by working-day processing-time band. These fields do not measure the time taken to decide whether to grant expedited status. [DOJ Annual FOIA Report Handbook, §VII.C.(3)](https://www.justice.gov/oip/media/1418941/dl?inline=).

| Original column name | Meaning | Variable type | Unit | Interpretation notes |
|---|---|---|---|---|
| `Agency` | Name of the federal agency reporting the annual FOIA data. | categorical | agency | An agency identifier, not a numerical measure. |
| `Fiscal Year` | U.S. federal fiscal year covered by the FOIA annual report. | numerical | year | Integer time key; not the date when this CSV was generated. |
| `missing tables` | Semicolon-separated short names of source data-type tables missing from that fiscal year's merge. | text | — | A fiscal-year-wide source-table flag, not a missingness indicator specific to this agency row; blank does not imply all metric values are zero. |
| `days_expedited__<1-20 Days` | Number of perfected expedited-processing requests completed in the fiscal year within less than one through 20 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__21-40 Days` | Number of perfected expedited-processing requests completed in the fiscal year within 21-40 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__41-60 Days` | Number of perfected expedited-processing requests completed in the fiscal year within 41-60 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__61-80 Days` | Number of perfected expedited-processing requests completed in the fiscal year within 61-80 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__81-100 Days` | Number of perfected expedited-processing requests completed in the fiscal year within 81-100 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__101-120 Days` | Number of perfected expedited-processing requests completed in the fiscal year within 101-120 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__121-140 Days` | Number of perfected expedited-processing requests completed in the fiscal year within 121-140 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__141-160 Days` | Number of perfected expedited-processing requests completed in the fiscal year within 141-160 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__161-180 Days` | Number of perfected expedited-processing requests completed in the fiscal year within 161-180 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__181-200 Days` | Number of perfected expedited-processing requests completed in the fiscal year within 181-200 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__201-300 Days` | Number of perfected expedited-processing requests completed in the fiscal year within 201-300 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__301-400 Days` | Number of perfected expedited-processing requests completed in the fiscal year within 301-400 working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__401+ Days` | Number of perfected expedited-processing requests completed in the fiscal year within 401 or more working days. | numerical | requests | The column label gives a working-day interval; the cell value counts requests, not days. |
| `days_expedited__Total` | Total perfected expedited-processing requests completed in the fiscal year, summed across the 13 processing-time bands. | numerical | requests | Not an average or median processing time. |

### 19 | Pending requests: volume and age

**File:** [`19_processing_time_pending_requests_FY2008-2025_all_agencies.csv`](19_processing_time_pending_requests_FY2008-2025_all_agencies.csv). **Size:** 1,921 rows, 12 columns. **Meaning:** Reports the number of perfected requests still open at fiscal-year end and their age, separately for simple, complex, and expedited tracks. [DOJ Annual FOIA Report Handbook, §VII.D](https://www.justice.gov/oip/media/1418941/dl?inline=).

| Original column name | Meaning | Variable type | Unit | Interpretation notes |
|---|---|---|---|---|
| `Agency` | Name of the federal agency reporting the annual FOIA data. | categorical | agency | An agency identifier, not a numerical measure. |
| `Fiscal Year` | U.S. federal fiscal year covered by the FOIA annual report. | numerical | year | Integer time key; not the date when this CSV was generated. |
| `missing tables` | Semicolon-separated short names of source data-type tables missing from that fiscal year's merge. | text | — | A fiscal-year-wide source-table flag, not a missingness indicator specific to this agency row; blank does not imply all metric values are zero. |
| `pending__Simple - Number Pending` | Number of perfected simple-track requests still open at the end of the fiscal year. | numerical | requests | Year-end inventory, not requests completed during the year. |
| `pending__Simple - Median Number of Days` | Median working days pending for perfected simple-track requests still open at fiscal-year end. | numerical | working days | Computed for pending requests in this track, not for completed requests. |
| `pending__Simple - Average Number of Days` | Average working days pending for perfected simple-track requests still open at fiscal-year end. | numerical | working days | Computed for pending requests in this track, not for completed requests. |
| `pending__Complex - Number Pending` | Number of perfected complex-track requests still open at the end of the fiscal year. | numerical | requests | Year-end inventory, not requests completed during the year. |
| `pending__Complex - Median Number of Days` | Median working days pending for perfected complex-track requests still open at fiscal-year end. | numerical | working days | Computed for pending requests in this track, not for completed requests. |
| `pending__Complex - Average Number of Days` | Average working days pending for perfected complex-track requests still open at fiscal-year end. | numerical | working days | Computed for pending requests in this track, not for completed requests. |
| `pending__Expedited Processing - Number Pending` | Number of perfected expedited-track requests still open at the end of the fiscal year. | numerical | requests | Year-end inventory, not requests completed during the year. |
| `pending__Expedited Processing - Median Number of Days` | Median working days pending for perfected expedited-track requests still open at fiscal-year end. | numerical | working days | Computed for pending requests in this track, not for completed requests. |
| `pending__Expedited Processing - Average Number of Days` | Average working days pending for perfected expedited-track requests still open at fiscal-year end. | numerical | working days | Computed for pending requests in this track, not for completed requests. |

### 20 | Ten oldest pending requests

**File:** [`20_processing_time_ten_oldest_requests_FY2008-2025_all_agencies.csv`](20_processing_time_ten_oldest_requests_FY2008-2025_all_agencies.csv). **Size:** 1,921 rows, 23 columns. **Meaning:** Reports the receipt date and working days pending for the tenth-oldest through oldest perfected requests open at fiscal-year end. Rank is based on working days pending rather than receipt date alone. [DOJ Annual FOIA Report Handbook, §VII.E](https://www.justice.gov/oip/media/1418941/dl?inline=).

| Original column name | Meaning | Variable type | Unit | Interpretation notes |
|---|---|---|---|---|
| `Agency` | Name of the federal agency reporting the annual FOIA data. | categorical | agency | An agency identifier, not a numerical measure. |
| `Fiscal Year` | U.S. federal fiscal year covered by the FOIA annual report. | numerical | year | Integer time key; not the date when this CSV was generated. |
| `missing tables` | Semicolon-separated short names of source data-type tables missing from that fiscal year's merge. | text | — | A fiscal-year-wide source-table flag, not a missingness indicator specific to this agency row; blank does not imply all metric values are zero. |
| `pending_ten_oldest__Date` | Receipt date of the tenth-oldest perfected request still pending at fiscal-year end. | text | YYYY-MM-DD | Date through Date.9 map to tenth-oldest through oldest; N/A, 0, and blank are not valid dates. |
| `pending_ten_oldest__10th Oldest Number of Days Pending` | Working days the tenth-oldest perfected request had remained pending since receipt as of fiscal-year end. | numerical | working days | If fewer than ten requests are pending, unused ranks may contain 0; interpret with the matching receipt-date field. |
| `pending_ten_oldest__Date.1` | Receipt date of the ninth-oldest perfected request still pending at fiscal-year end. | text | YYYY-MM-DD | Date through Date.9 map to tenth-oldest through oldest; N/A, 0, and blank are not valid dates. |
| `pending_ten_oldest__9th Oldest Number of Days Pending` | Working days the ninth-oldest perfected request had remained pending since receipt as of fiscal-year end. | numerical | working days | If fewer than ten requests are pending, unused ranks may contain 0; interpret with the matching receipt-date field. |
| `pending_ten_oldest__Date.2` | Receipt date of the eighth-oldest perfected request still pending at fiscal-year end. | text | YYYY-MM-DD | Date through Date.9 map to tenth-oldest through oldest; N/A, 0, and blank are not valid dates. |
| `pending_ten_oldest__8th Oldest Number of Days Pending` | Working days the eighth-oldest perfected request had remained pending since receipt as of fiscal-year end. | numerical | working days | If fewer than ten requests are pending, unused ranks may contain 0; interpret with the matching receipt-date field. |
| `pending_ten_oldest__Date.3` | Receipt date of the seventh-oldest perfected request still pending at fiscal-year end. | text | YYYY-MM-DD | Date through Date.9 map to tenth-oldest through oldest; N/A, 0, and blank are not valid dates. |
| `pending_ten_oldest__7th Oldest Number of Days Pending` | Working days the seventh-oldest perfected request had remained pending since receipt as of fiscal-year end. | numerical | working days | If fewer than ten requests are pending, unused ranks may contain 0; interpret with the matching receipt-date field. |
| `pending_ten_oldest__Date.4` | Receipt date of the sixth-oldest perfected request still pending at fiscal-year end. | text | YYYY-MM-DD | Date through Date.9 map to tenth-oldest through oldest; N/A, 0, and blank are not valid dates. |
| `pending_ten_oldest__6th Oldest Number of Days Pending` | Working days the sixth-oldest perfected request had remained pending since receipt as of fiscal-year end. | numerical | working days | If fewer than ten requests are pending, unused ranks may contain 0; interpret with the matching receipt-date field. |
| `pending_ten_oldest__Date.5` | Receipt date of the fifth-oldest perfected request still pending at fiscal-year end. | text | YYYY-MM-DD | Date through Date.9 map to tenth-oldest through oldest; N/A, 0, and blank are not valid dates. |
| `pending_ten_oldest__5th Oldest Number of Days Pending` | Working days the fifth-oldest perfected request had remained pending since receipt as of fiscal-year end. | numerical | working days | If fewer than ten requests are pending, unused ranks may contain 0; interpret with the matching receipt-date field. |
| `pending_ten_oldest__Date.6` | Receipt date of the fourth-oldest perfected request still pending at fiscal-year end. | text | YYYY-MM-DD | Date through Date.9 map to tenth-oldest through oldest; N/A, 0, and blank are not valid dates. |
| `pending_ten_oldest__4th Oldest Number of Days Pending` | Working days the fourth-oldest perfected request had remained pending since receipt as of fiscal-year end. | numerical | working days | If fewer than ten requests are pending, unused ranks may contain 0; interpret with the matching receipt-date field. |
| `pending_ten_oldest__Date.7` | Receipt date of the third-oldest perfected request still pending at fiscal-year end. | text | YYYY-MM-DD | Date through Date.9 map to tenth-oldest through oldest; N/A, 0, and blank are not valid dates. |
| `pending_ten_oldest__3rd Oldest Number of Days Pending` | Working days the third-oldest perfected request had remained pending since receipt as of fiscal-year end. | numerical | working days | If fewer than ten requests are pending, unused ranks may contain 0; interpret with the matching receipt-date field. |
| `pending_ten_oldest__Date.8` | Receipt date of the second-oldest perfected request still pending at fiscal-year end. | text | YYYY-MM-DD | Date through Date.9 map to tenth-oldest through oldest; N/A, 0, and blank are not valid dates. |
| `pending_ten_oldest__2nd Oldest Number of Days Pending` | Working days the second-oldest perfected request had remained pending since receipt as of fiscal-year end. | numerical | working days | If fewer than ten requests are pending, unused ranks may contain 0; interpret with the matching receipt-date field. |
| `pending_ten_oldest__Date.9` | Receipt date of the oldest perfected request still pending at fiscal-year end. | text | YYYY-MM-DD | Date through Date.9 map to tenth-oldest through oldest; N/A, 0, and blank are not valid dates. |
| `pending_ten_oldest__Oldest Number of Days Pending` | Working days the oldest perfected request had remained pending since receipt as of fiscal-year end. | numerical | working days | If fewer than ten requests are pending, unused ranks may contain 0; interpret with the matching receipt-date field. |

### 21 | Fee-waiver adjudications

**File:** [`21_fee_waiver_FY2008-2025_all_agencies.csv`](21_fee_waiver_FY2008-2025_all_agencies.csv). **Size:** 1,921 rows, 7 columns. **Meaning:** Reports fee-waiver decisions made during the fiscal year and the time taken to make them, including decisions at the initial-request and, where applicable, administrative-appeal stages. [DOJ Annual FOIA Report Handbook, §VIII.B](https://www.justice.gov/oip/media/1418941/dl?inline=).

| Original column name | Meaning | Variable type | Unit | Interpretation notes |
|---|---|---|---|---|
| `Agency` | Name of the federal agency reporting the annual FOIA data. | categorical | agency | An agency identifier, not a numerical measure. |
| `Fiscal Year` | U.S. federal fiscal year covered by the FOIA annual report. | numerical | year | Integer time key; not the date when this CSV was generated. |
| `missing tables` | Semicolon-separated short names of source data-type tables missing from that fiscal year's merge. | text | — | A fiscal-year-wide source-table flag, not a missingness indicator specific to this agency row; blank does not imply all metric values are zero. |
| `fee_waiver__Number Granted` | Number of fee-waiver adjudications resulting in a grant during the fiscal year. | numerical | decisions | Not the count of all FOIA requests granted. |
| `fee_waiver__Number Denied` | Number of fee-waiver adjudications resulting in a denial during the fiscal year. | numerical | decisions | Not the count of all FOIA requests denied. |
| `fee_waiver__Median Number of Days to Adjudicate` | Median time taken to adjudicate a fee-waiver request. | numerical | days | Count begins when fees are determined to be assessed and the waiver request is ripe; it ends with the grant-or-denial decision. |
| `fee_waiver__Average Number of Days to Adjudicate` | Average time taken to adjudicate a fee-waiver request. | numerical | days | Count begins when fees are determined to be assessed and the waiver request is ripe; it ends with the grant-or-denial decision. |

### 22 | FOIA personnel

**File:** [`22_foia_personnel_FY2008-2025_all_agencies.csv`](22_foia_personnel_FY2008-2025_all_agencies.csv). **Size:** 1,921 rows, 6 columns. **Meaning:** Reports employees assigned full time to FOIA work, the full-time equivalent of other staff's FOIA work, and their sum. [DOJ Annual FOIA Report Handbook, §IX](https://www.justice.gov/oip/media/1418941/dl?inline=).

| Original column name | Meaning | Variable type | Unit | Interpretation notes |
|---|---|---|---|---|
| `Agency` | Name of the federal agency reporting the annual FOIA data. | categorical | agency | An agency identifier, not a numerical measure. |
| `Fiscal Year` | U.S. federal fiscal year covered by the FOIA annual report. | numerical | year | Integer time key; not the date when this CSV was generated. |
| `missing tables` | Semicolon-separated short names of source data-type tables missing from that fiscal year's merge. | text | — | A fiscal-year-wide source-table flag, not a missingness indicator specific to this agency row; blank does not imply all metric values are zero. |
| `personnel__Number of "Full-Time FOIA Employees"` | Number of employees who spend 100% of their working time on FOIA duties. | numerical | people | A full-time headcount, normally an integer. |
| `personnel__Number of "Equivalent Full-Time FOIA Employees"` | Full-time equivalent of FOIA work performed by employees who spend less than all their time on FOIA. | numerical | FTE | May be fractional; not the number of individual people. |
| `personnel__Total Number of "Full-Time FOIA Staff"` | Sum of full-time FOIA employees and equivalent full-time FOIA employees. | numerical | FTE | A combined full-time equivalent, not necessarily a headcount of individuals. |

### 23 | FOIA costs and fees

**File:** [`23_foia_costs_FY2008-2025_all_agencies.csv`](23_foia_costs_FY2008-2025_all_agencies.csv). **Size:** 1,921 rows, 8 columns. **Meaning:** Reports processing costs, litigation costs, total costs, fees actually collected from requesters, and collected fees as a percentage of processing costs. [DOJ Annual FOIA Report Handbook, §IX–X](https://www.justice.gov/oip/media/1418941/dl?inline=).

| Original column name | Meaning | Variable type | Unit | Interpretation notes |
|---|---|---|---|---|
| `Agency` | Name of the federal agency reporting the annual FOIA data. | categorical | agency | An agency identifier, not a numerical measure. |
| `Fiscal Year` | U.S. federal fiscal year covered by the FOIA annual report. | numerical | year | Integer time key; not the date when this CSV was generated. |
| `missing tables` | Semicolon-separated short names of source data-type tables missing from that fiscal year's merge. | text | — | A fiscal-year-wide source-table flag, not a missingness indicator specific to this agency row; blank does not imply all metric values are zero. |
| `costs_fees__Processing Costs` | Agency costs of processing initial FOIA requests and administrative appeals, including salaries, overhead, and other related expenses. | numerical | USD | Excludes separately reported FOIA litigation costs. |
| `costs_fees__Litigation-Related Costs` | Agency costs of FOIA litigation, including personnel, overhead, attorney fees, and other litigation expenses. | numerical | USD | Reported separately from request-processing costs. |
| `costs_fees__Total Costs` | Sum of FOIA processing costs and litigation-related costs. | numerical | USD | Defined as Processing Costs + Litigation-Related Costs. |
| `costs_fees__Total Amount of Fees Collected` | Fees actually collected from FOIA requesters for permitted search, review, duplication, and related services. | numerical | USD | Revenue collected from requesters, not an agency expenditure. |
| `costs_fees__Percentage of Total Costs` | Fees collected as a percentage of FOIA request-processing costs. | numerical | % | Generally Fees Collected / Processing Costs × 100; the denominator excludes litigation costs despite the column label. Some historical source values are inconsistent and should be reviewed, not overwritten. |

### 24 | Use of FOIA subsection (c) exclusions

**File:** [`24_exclusions_FY2008-2025_all_agencies.csv`](24_exclusions_FY2008-2025_all_agencies.csv). **Size:** 1,921 rows, 4 columns. **Meaning:** Reports how many times the agency invoked a FOIA subsection (c) exclusion during the fiscal year. These exclusions differ from ordinary FOIA exemptions. [DOJ Annual FOIA Report Handbook, §XI.A](https://www.justice.gov/oip/media/1418941/dl?inline=).

| Original column name | Meaning | Variable type | Unit | Interpretation notes |
|---|---|---|---|---|
| `Agency` | Name of the federal agency reporting the annual FOIA data. | categorical | agency | An agency identifier, not a numerical measure. |
| `Fiscal Year` | U.S. federal fiscal year covered by the FOIA annual report. | numerical | year | Integer time key; not the date when this CSV was generated. |
| `missing tables` | Semicolon-separated short names of source data-type tables missing from that fiscal year's merge. | text | — | A fiscal-year-wide source-table flag, not a missingness indicator specific to this agency row; blank does not imply all metric values are zero. |
| `subsection_c_used__Number of Times Subsection Used` | Number of times the agency invoked a FOIA subsection 552(c) exclusion during the fiscal year. | numerical | uses | A subsection (c) exclusion is distinct from the nine ordinary subsection (b) exemptions. |

## Sources and construction

1. [U.S. Department of Justice Annual FOIA Report Handbook](https://www.justice.gov/oip/media/1418941/dl?inline=), §§VII.C–E, VIII.B, IX–XI: official definitions of request tracks, processing duration, pending requests, fee waivers, personnel, costs, and exclusions.
2. [FOIA.gov annual data and glossary](https://www.foia.gov/data.html): definitions of simple/complex requests, full-time equivalents, and exclusions.
3. [FOIA.gov dataset downloads](https://www.foia.gov/foia-dataset-download.html): annual source archives for FY2008–FY2025.
4. [DOJ annual-report training materials](https://www.justice.gov/oip/page/file/1440151/dl): fee percentage calculated as fees collected divided by processing costs.
5. This repository's `fa26/dataset/merge_by_year/merge_by_year.py`: explains `missing tables` and the prefixes added to source column names. Exact column labels were read from the eight CSV headers.

**Coverage:** 94 file-column definitions across the eight CSVs, including the three shared identifier/metadata fields in each. The searchable version is [`DATA_DICTIONARY_17_24.csv`](DATA_DICTIONARY_17_24.csv).
