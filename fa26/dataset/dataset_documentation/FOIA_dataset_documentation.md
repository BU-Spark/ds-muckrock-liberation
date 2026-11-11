# FOIA Annual Report Dataset — Documentation (FA26)

The dataset holds U.S. federal FOIA (Freedom of Information Act) Annual
Report data from [foia.gov](https://www.foia.gov/data.html),
fiscal years **2008–2025**:

| **Dataset**              | **Level of detail**                                                         | **Format**              |
|--------------------------|-----------------------------------------------------------------------------|-------------------------|
| **Component-level data** | One row per **agency × component (office)** per year, plus the agency total | CSVs covering all years |

## 1. Background: what is in a FOIA Annual Report?

Every federal agency must file a FOIA Annual Report with the Department
of Justice each fiscal year (Oct 1 – Sep 30). On foia.gov the report is
organized into **12 main data types**, 6 of which have **sub data types
(20 in total)**. Together they make the **32 data types**, and each one
is its own file in the agency-level dataset.

### Data type hierarchy (official foia.gov)

| **Main data type**    | **Sub data types**                                                                                                              | **No. of sub types**           |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| Requests              | Disposition (Dis.); Dis. – "Other" Reasons; Expedited Processing                                                                | 3                              |
| Exemptions            | Exemption 3 Statutes                                                                                                            | 1                              |
| Appeals               | Disposition (Dis.); Dis. – Use of Exemptions; Dis. – Other Than Exs.; Dis. – "Other" Reasons; Response Time; Ten Oldest Pending | 6                              |
| Processing Time       | Requests Granted; Simple Requests; Complex Requests; Expedited Requests; Pending Requests; Ten Oldest Requests                  | 6                              |
| Consultations         | Ten Oldest                                                                                                                      | 1                              |
| Comparisons           | Requests Backlogged; Administrative Appeals; Appeals Backlogged                                                                 | 3                              |
| Fee Waiver            | —                                                                                                                               | 0                              |
| FOIA Personnel        | —                                                                                                                               | 0                              |
| FOIA Costs            | —                                                                                                                               | 0                              |
| Exclusions            | —                                                                                                                               | 0                              |
| Proactive Disclosures | —                                                                                                                               | 0                              |
| Backlog               | —                                                                                                                               | 0                              |
| **12 main**           |                                                                                                                                 | **20 sub** → **32 data types** |

### All 32 data types

The following is the order of the data-type dropdown on foia.gov:

| **No.** | **Main data type**    | **foia.gov data type**                | **What it measures**                                                                        |
|---------|-----------------------|---------------------------------------|---------------------------------------------------------------------------------------------|
| 01      | Requests              | Requests                              | Requests pending at start, received, processed, pending at end of year                      |
| 02      | Requests              | Requests – Disposition                | How processed requests ended: full grant, partial, full denial, no records, withdrawn, etc. |
| 03      | Requests              | Requests – Dis. – "Other" Reasons     | Count (and, component-level only, reasons) for requests closed as "Other"                   |
| 04      | Requests              | Requests – Expedited Processing       | Expedited requests granted/denied, days to adjudicate                                       |
| 05      | Exemptions            | Exemptions                            | Number of times each FOIA exemption (Ex. 1–9, 7(A)–7(F)) was used on requests               |
| 06      | Exemptions            | Exemptions – Exemption 3 Statutes     | Each statute cited under Exemption 3, with case citation, type of info withheld, times used |
| 07      | Appeals               | Appeals                               | Appeals pending at start, received, processed, pending at end                               |
| 08      | Appeals               | Appeals – Disposition                 | Appeals affirmed, partly reversed, fully reversed, closed for other reasons                 |
| 09      | Appeals               | Appeals – Dis. – Use of Exemptions    | Exemptions relied upon in appeal decisions                                                  |
| 10      | Appeals               | Appeals – Dis. – Other Than Exs.      | Non-exemption reasons for appeal outcomes                                                   |
| 11      | Appeals               | Appeals – Dis. – "Other" Reasons      | Count (and, component-level only, reasons) for appeals closed as "Other"                    |
| 12      | Appeals               | Appeals – Response Time               | Median / average / lowest / highest days to decide appeals                                  |
| 13      | Appeals               | Appeals – Ten Oldest Pending          | Dates and days pending of the 10 oldest open appeals                                        |
| 14      | Processing Time       | Processing Time                       | Median / avg / low / high days for simple, complex, expedited requests                      |
| 15      | Processing Time       | Processing Time – Requests Granted    | Same as 14, for granted requests only                                                       |
| 16      | Processing Time       | Processing Time – Simple Requests     | Simple requests binned by days to process (\<1–20 … 401+)                                   |
| 17      | Processing Time       | Processing Time – Complex Requests    | Complex requests binned by days to process                                                  |
| 18      | Processing Time       | Processing Time – Expedited Requests  | Expedited requests binned by days to process                                                |
| 19      | Processing Time       | Processing Time – Pending Requests    | Number pending + median/avg days, by track                                                  |
| 20      | Processing Time       | Processing Time – Ten Oldest Requests | Dates and days pending of the 10 oldest open requests                                       |
| 21      | Fee Waiver            | Fee Waiver                            | Fee waivers granted/denied, days to adjudicate                                              |
| 22      | FOIA Personnel        | FOIA Personnel                        | Full-time FOIA employees, equivalent FTE, total staff                                       |
| 23      | FOIA Costs            | FOIA Costs                            | Processing costs, litigation costs, total costs, fees collected, fees as % of costs         |
| 24      | Exclusions            | Exclusions                            | Times a 5 U.S.C. 552(c) exclusion was used                                                  |
| 25      | Proactive Disclosures | Proactive Disclosures                 | Records posted by the FOIA office and by program offices                                    |
| 26      | Backlog               | Backlog                               | Backlogged requests and appeals at end of year                                              |
| 27      | Consultations         | Consultations                         | Consultations from other agencies: pending, received, processed                             |
| 28      | Consultations         | Consultations – Ten Oldest            | 10 oldest pending consultations                                                             |
| 29      | Comparisons           | Comparisons                           | Requests received/processed, last year's report vs this year's                              |
| 30      | Comparisons           | Comparisons – Requests Backlogged     | Backlogged requests, previous vs current report                                             |
| 31      | Comparisons           | Comparisons – Administrative Appeals  | Appeals received/processed, last year vs this year                                          |
| 32      | Comparisons           | Comparisons – Appeals Backlogged      | Backlogged appeals, previous vs current report                                              |

**Key terms**

- **Agency** – a federal department or independent agency (e.g.
  Department of Justice, EPA).
- **Component** – an office within an agency that processes its own FOIA
  requests (e.g. FBI within DOJ, Army within DoD). Small agencies
  usually have none.
- **Agency Overall** – the agency's total. For an agency with
  components, it is the total across all its components. For an agency
  **without** components, the Agency Overall row is the only row: the
  agency's own numbers.
- **Backlog** – requests or appeals still pending past the statutory
  deadline at year end.

### Data columns per file

| **File**                                                               | **Data columns (after Agency, Component, Fiscal Year)**                                                                                                                                                                                                                                                  |
|------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 01_requests                                                            | Requests Pending as of Start of FY; Received in FY; Processed in FY; Pending as of End of FY                                                                                                                                                                                                             |
| 02_requests_disposition_dis                                            | Full Grants; Partial Grants/Partial Denials; Full Denials Based on Exemptions; No Records; All Records Referred; Request Withdrawn; Fee-Related Reason; Records Not Reasonably Described; Improper FOIA Request for Other Reason; Not Agency Record; Duplicate Request; Other\*; Total                   |
| 03_requests_dis_other_reasons                                          | Total                                                                                                                                                                                                                                                                                                    |
| 04_requests_expedited_processing                                       | Number Granted; Number Denied; Median / Average Days to Adjudicate; Number Adjudicated Within Ten Calendar Days                                                                                                                                                                                          |
| 05_exemptions                                                          | Ex. 1, Ex. 2, Ex. 3, Ex. 4, Ex. 5, Ex. 6, Ex. 7(A)–7(F), Ex. 8, Ex. 9                                                                                                                                                                                                                                    |
| 06_exemptions_exemption_3_statutes                                     | Statute; Case Citation; Type of Information Withheld; Number of Times Relied Upon                                                                                                                                                                                                                        |
| 07_appeals                                                             | Appeals Pending at Start; Received; Processed; Pending at End                                                                                                                                                                                                                                            |
| 08_appeals_disposition_dis                                             | Affirmed; Partially Affirmed & Partially Reversed/Remanded; Completely Reversed/Remanded; Closed for Other Reasons; Total                                                                                                                                                                                |
| 09_appeals_dis_use_of_exemptions                                       | Ex. 1 … Ex. 9 (same as 05)                                                                                                                                                                                                                                                                               |
| 10_appeals_dis_other_than_exs                                          | No Records; Records Referred at Initial Request Level; Request Withdrawn; Fee-Related Reason; Records Not Reasonably Described; Improper Request for Other Reason; Not Agency Record; Duplicate Request or Appeal; Request in Litigation; Appeal Based Solely on Denial of Expedited Processing; Other\* |
| 11_appeals_dis_other_reasons                                           | Total                                                                                                                                                                                                                                                                                                    |
| 12_appeals_response_time                                               | Median / Average / Lowest / Highest Number of Days                                                                                                                                                                                                                                                       |
| 13_appeals_ten_oldest_pending                                          | 10 pairs of Date + Nth Oldest Number of Days Pending (10th oldest → Oldest). The Date header repeats 10 times, so rename columns on load                                                                                                                                                                 |
| 14_processing_time                                                     | Simple / Complex / Expedited × Median / Average / Lowest / Highest Days (12 cols)                                                                                                                                                                                                                        |
| 15_processing_time_requests_granted                                    | Same 12 columns as 14                                                                                                                                                                                                                                                                                    |
| 16, 17, 18 (simple / complex / expedited)                              | Day bins: \<1-20, 21-40, 41-60, 61-80, 81-100, 101-120, 121-140, 141-160, 161-180, 181-200, 201-300, 301-400, 401+; Total                                                                                                                                                                                |
| 19_processing_time_pending_requests                                    | Simple / Complex / Expedited × Number Pending, Median Days, Average Days                                                                                                                                                                                                                                 |
| 20_processing_time_ten_oldest_requests                                 | Same layout as 13 (repeated Date header)                                                                                                                                                                                                                                                                 |
| 21_fee_waiver                                                          | Number Granted; Number Denied; Median / Average Days to Adjudicate                                                                                                                                                                                                                                       |
| 22_foia_personnel                                                      | Full-Time FOIA Employees; Equivalent Full-Time FOIA Employees; Total Full-Time FOIA Staff                                                                                                                                                                                                                |
| 23_foia_costs                                                          | Processing Costs; Litigation-Related Costs; Total Costs; Total Amount of Fees Collected; Percentage of Total Costs                                                                                                                                                                                       |
| 24_exclusions                                                          | Number of Times Subsection Used                                                                                                                                                                                                                                                                          |
| 25_proactive_disclosures                                               | Records Posted by the FOIA Office; Records Posted by Program Offices                                                                                                                                                                                                                                     |
| 26_backlog                                                             | Backlogged Requests at End of FY; Backlogged Appeals at End of FY                                                                                                                                                                                                                                        |
| 27_consultations                                                       | Consultations Pending at Start; Received; Processed; Pending at End                                                                                                                                                                                                                                      |
| 28_consultations_ten_oldest                                            | Same layout as 13 (repeated Date header)                                                                                                                                                                                                                                                                 |
| 29_comparisons / 31_comparisons_administrative_appeals                 | Received from Last Year's Report; Received from Current Report; Processed from Last Year's Report; Processed from Current Report                                                                                                                                                                         |
| 30_comparisons_requests_backlogged / 32_comparisons_appeals_backlogged | Backlogged at End of FY from Previous Report; from Current Report                                                                                                                                                                                                                                        |

## 2. Component-level tables

This section covers the component-level data for FY2008–FY2025. A
component is an office inside an agency, like the FBI inside DOJ. Each
agency with a report on foia.gov has one total row per year, and
agencies with components also have a row for each component.

The data comes from the foia.gov API and was downloaded on October
18–19, 2026. We kept the values as foia.gov reports them. The only
changes were removing extra spaces around values and cleaning up the
formatting of text in data types 03, 06 and 11.

### Files

| **File**                         | **Rows** | **Grain**                                                                      |
|----------------------------------|----------|--------------------------------------------------------------------------------|
| component_master_no_03_06_11.csv | 8,139    | Fiscal year × agency × component (plus one Agency Overall row per agency-year) |
| other_reasons_03_11.csv          | 13,903   | Fiscal year × agency × component × "Other" reason (data types 03 and 11)       |
| exemption_statutes_06.csv        | 16,532   | Fiscal year × agency × component × Exemption 3 statute (data type 06)          |

- **component_master_no_03_06_11.csv**: All data types in one wide
  table. Data types 03 and 11 only have their total column here, and
  06 is not included.
- **exemption_statutes_06.csv**: The Exemption 3 statutes (06), one row
  per statute cited.
- **other_reasons_03_11.csv**: The "Other" reasons for requests (03) and
  appeals (11), one row per reason.
- The master table has 8 ID columns and 244 data columns. Data column
  names start with the data type number, for example
  26_Backlog\_\_BackloggedRequestQuantity.

### Row types

| **Row Type**   | **Meaning**                                                                                                                                                                                        | **Master table rows** |
|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| agency_overall | The agency's total for the year. Agencies that report as one organization only have this row                                                                                                       | 1,923                 |
| component      | One component of the agency                                                                                                                                                                        | 6,191                 |
| second_entry   | A second entry in the same table. foia.gov counts both in the agency total. For example, Peace Corps FY2022 costs are OIG 310,000 plus a second entry of 86,900, and the Agency Overall is 396,900 | 10                    |
| no_component   | Numbers that foia.gov does not link to any component                                                                                                                                               | 15                    |

In the master table, Component, Component Name and Row Type together
identify a row within an agency and year. The abbreviation alone is not
enough because USPS had two PS components in FY2019–2024. Some
components also appear under two abbreviations. For example, Interior's
OSM became OSMRE in FY2020, so check Component Name when you follow one
component over time.

**Adding up numbers**

Agency totals and component rows should never be added together. This
applies to the master table and the 06 table. For example, DHS's FY2024
backlog is 141,420 in the Agency Overall row, and its 15 components also
add up to 141,420. Adding all 16 rows would give 282,840, which is twice
the real number.

- For a government-wide total, add the Agency Overall rows.
- For an agency's components, add the component, second_entry and
  no_component rows, and leave out rows with Exclude From Component
  Sum = yes. Only Commerce FY2025 "DOC" has this flag, because it is a
  copy of a total.
- Counts, dollars and FTE can be added up. Medians, averages, days and
  dates cannot.

The 03/11 table does not have this problem. For each agency and year, it
has either Agency Overall rows or other rows, but not both.

**0, N/A, blank and \<1**

| **Value** | **Meaning**                                                                                                                                                                                                                                         |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0         | In count columns, the agency reported zero. In days and ten-oldest columns, it usually means the agency had no such cases.                                                                                                                          |
| N/A       | Not applicable or nothing to calculate. For example, an expedited median when no expedited requests were processed.                                                                                                                                 |
| Blank     | Usually the component is not in that data type's table. For example, DOJ reported all its FY2025 appeals under OIP, so the appeals tables are blank for its other 31 components. Data types 24 and 25 are also almost entirely blank before FY2017. |
| \<1       | Less than one day.                                                                                                                                                                                                                                  |

### Per-year summary

| **Fiscal Year** | **Data types** | **Agencies reporting** | **Agencies with components** | **Component rows** | **Agencies added vs prior year** | **Agencies removed vs prior year** |
|-----------------|----------------|------------------------|------------------------------|--------------------|----------------------------------|------------------------------------|
| 2008            | 32             | 71                     | 21                           | 307                | —                                | —                                  |
| 2009            | 32             | 73                     | 22                           | 314                | 2                                | 0                                  |
| 2010            | 32             | 97                     | 25                           | 360                | 24                               | 0                                  |
| 2011            | 32             | 99                     | 25                           | 360                | 2                                | 0                                  |
| 2012            | 32             | 99                     | 26                           | 361                | 0                                | 0                                  |
| 2013            | 32             | 99                     | 25                           | 357                | 1                                | 1                                  |
| 2014            | 32             | 100                    | 26                           | 352                | 1                                | 0                                  |
| 2015            | 32             | 100                    | 26                           | 350                | 1                                | 1                                  |
| 2016            | 32             | 115                    | 27                           | 349                | 15                               | 0                                  |
| 2017            | 32             | 116                    | 29                           | 356                | 1                                | 0                                  |
| 2018            | 32             | 118                    | 29                           | 360                | 2                                | 0                                  |
| 2019            | 32             | 118                    | 29                           | 350                | 0                                | 0                                  |
| 2020            | 32             | 119                    | 28                           | 348                | 3                                | 2                                  |
| 2021            | 32             | 118                    | 29                           | 350                | 0                                | 1                                  |
| 2022            | 32             | 120                    | 29                           | 349                | 2                                | 0                                  |
| 2023            | 32             | 121                    | 30                           | 352                | 1                                | 0                                  |
| 2024            | 32             | 122                    | 28                           | 310                | 1                                | 0                                  |
| 2025            | 32             | 118                    | 28                           | 306                | 1                                | 5                                  |
| **Total**       |                | **1,923** agency-years |                              | **6,191**          |                                  |                                    |

In the total row, 1,923 is the number of agency-years (one agency in one
year).

An agency is counted in a year if foia.gov has its report for that year,
so a change in the count does not necessarily mean an agency was created
or closed. The count jumps twice. The 24 agencies added in FY2010,
including USDA and EEOC, make up about 9% of that year's requests, so be
careful when comparing totals before and after FY2010. The 15 agencies
added in FY2016 are small, with 42 requests in total.

### ID columns

| **Column**                 | **Meaning**                                                                                                                         |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| Fiscal Year                | 2008–2025                                                                                                                           |
| Agency                     | Agency name, spelled as in the agency-level data                                                                                    |
| Agency Abbreviation        | As on foia.gov (e.g. DOJ, CSB)                                                                                                      |
| Component                  | Component abbreviation in foia.gov's **current** form, the same in every year (e.g. Army = DA). Agency Overall for the agency total |
| Component Name             | Full component name. Use Component + Component Name together as the key, because two components can share an abbreviation           |
| Row Type                   | agency_overall, component, second_entry, or no_component (below)                                                                    |
| Exclude From Component Sum | leave this row out when summing components                                                                                          |
| Exclude Reason             | Why the row is excluded                                                                                                             |

### Column info

8 ID columns + **244 data columns** covering 31 of the 32 data types
(all except 06). Data column names follow the pattern
\<NN\>\_\<ShortName\>\_\_\<Field\>, e.g.
26_Backlog\_\_BackloggedRequestQuantity,
01_Requests\_\_ProcessingStatisticsReceivedQuantity,
02_Disposition\_\_NonExemptionDenialQuantity\[NoRecords\].

| **No.** | **Column prefix**                 | **No.** | **Column prefix**                    |
|---------|-----------------------------------|---------|--------------------------------------|
| 01      | 01_Requests\_\_                   | 17      | 17_ComplexRequests\_\_               |
| 02      | 02_Disposition\_\_                | 18      | 18_ExpeditedRequests\_\_             |
| 03      | *Excluded in the master table*    | 19      | 19_PendingRequests\_\_               |
| 04      | 04_ExpeditedProcessing\_\_        | 20      | 20_TenOldestRequests\_\_             |
| 05      | 05_Exemptions\_\_                 | 21      | 21_FeeWaiver\_\_                     |
| 06      | *Excluded in the master table*    | 22      | 22_Personnel\_\_                     |
| 07      | 07_Appeals\_\_                    | 23      | 23_Costs\_\_                         |
| 08      | 08_AppealsDisposition\_\_         | 24      | 24_Exclusions\_\_                    |
| 09      | 09_AppealsExemptions\_\_          | 25      | 25_ProactiveDisclosures\_\_          |
| 10      | 10_AppealsOtherThanExemptions\_\_ | 26      | 26_Backlog\_\_                       |
| 11      | *Excluded in the master table*    | 27      | 27_Consultations\_\_                 |
| 12      | 12_AppealsResponseTime\_\_        | 28      | 28_ConsultationsTenOldest\_\_        |
| 13      | 13_AppealsTenOldest\_\_           | 29      | 29_Comparisons\_\_                   |
| 14      | 14_ProcessingTime\_\_             | 30      | 30_ComparisonsRequestsBacklogged\_\_ |
| 15      | 15_ProcessingTimeGranted\_\_      | 31      | 31_ComparisonsAppeals\_\_            |
| 16      | 16_SimpleRequests\_\_             | 32      | 32_ComparisonsAppealsBacklogged\_\_  |

The total number of times Exemption 3 was used is still in the master
table, in the Ex. 3 columns of 05 and 09.

### other_reasons_03_11.csv

ID columns + Data Type No. (03 or 11), Data Type (foia.gov name, e.g.
Requests - Dis. - "Other" Reasons), Reason (cleaned free text),
Quantity.

### exemption_statutes_06.csv

ID columns + Statute, Type of Information Withheld, Case Citation,
Number of Times Relied Upon.

- The same statute may appear more than once for an agency; all entries
  are kept.
- The same statute is written in many different ways (e.g. 30 variants
  of 26 U.S.C. § 6103), so group statute names before ranking them.

### Known issues

These come from foia.gov's own data, and we kept the numbers as
reported.

- Components do not add up to the agency total in 13 agency-years:
  Veterans Affairs FY2025 (47 columns), GSA FY2016 (20), EPA FY2011
  (8), Defense FY2025 (3), Commerce FY2025 (2), Agriculture, Labor and
  EEOC FY2025 (1 each), and USPS FY2010, 2013, 2014, 2016 and 2017
  (appeals pending at end of year).
- The Commerce FY2025 "DOC" row repeats the Agency Overall row in 239 of
  244 columns, so leave it out when adding up components. In the 06
  table it copies the other components, which doubles the Agency
  Overall statute count (276 instead of 138).
- In FY2025, data type 11, 8 agencies have component values but a blank
  Agency Overall cell: Justice 1,045, Veterans Affairs 192, EEOC 76,
  Labor 52, Energy 45, Defense 14, Agriculture 4, Commerce 1. Add up
  the components for these agencies.
- For Energy FY2025 HQ, data type 11, the reasons add up to 49 but the
  total column says 45.
- foia.gov's FY2022 CSV export leaves out USAGM, so its All agencies row
  shows 928,261 requests received. Adding the Agency Overall rows here
  gives 928,353, because the API includes USAGM's 92 requests.
- The same statute can be written many ways in the 06 table. For
  example, there are 30 versions of 26 U.S.C. § 6103, so group the
  names before ranking statutes.
- N/A has several spellings and a few values are written oddly. The
  README lists them.

### How the tables were checked

- We checked every cell against the API reports a second time with
  separate code and found no differences.
- We compared the Agency Overall rows with the agency-level table, which
  comes from foia.gov's CSV exports with a few gaps filled from the
  API. 469,204 cells match. The other 8 differ because the CSV export
  is blank (SBA FY2021 fee waiver days and CEQ FY2023 pending request
  days).
- We compared FY2024 components with foia.gov's component CSV export for
  23 data types. All 36,466 cells match.
- We compared the Exemption 3 Agency Overall rows with the agency-level
  statute table, which is built the same way. All 1,919 agency-years
  with statutes match.
