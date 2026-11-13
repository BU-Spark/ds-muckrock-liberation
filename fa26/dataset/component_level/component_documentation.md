## 2. Component-level tables

This section covers the component-level data for FY2008–FY2025. A component is an office inside an agency, like the FBI inside DOJ. Each agency with a report on foia.gov has one total row per year, and agencies with components also have a row for each component.

The data comes from the foia.gov API and was downloaded on October 18–19, 2026. We kept the values as foia.gov reports them. The only changes were removing extra spaces around values and cleaning up the formatting of text in data types 03, 06 and 11.

### The three files

| File | What it holds | Rows |
|---|---|---:|
| `component_master_no_03_06_11.csv` | All data types in one wide table. Data types 03 and 11 only have their total column here, and 06 is not included | 8,139 |
| `other_reasons_03_11.csv` | The "Other" reasons for requests (03) and appeals (11), one row per reason | 13,903 |
| `exemption_statutes_06.csv` | The Exemption 3 statutes (06), one row per statute cited | 16,532 |

The master table has 8 ID columns and 244 data columns. Data column names start with the data type number, for example `26_Backlog__BackloggedRequestQuantity`. The [README](https://github.com/BU-Spark/ds-muckrock-liberation/blob/fa26-dev/fa26/dataset/component_level/README.md) lists the prefix for each data type.

### Row types

| Row Type | Meaning | Rows in the master table |
|---|---|---:|
| `agency_overall` | The agency's total for the year. Agencies that report as one organization only have this row | 1,923 |
| `component` | One component of the agency | 6,191 |
| `second_entry` | A second entry in the same table. foia.gov counts both in the agency total. For example, Peace Corps FY2022 costs are OIG 310,000 plus a second entry of 86,900, and the Agency Overall is 396,900 | 10 |
| `no_component` | Numbers that foia.gov does not link to any component | 15 |

In the master table, `Component`, `Component Name` and `Row Type` together identify a row within an agency and year. The abbreviation alone is not enough because USPS had two `PS` components in FY2019–2024. Some components also appear under two abbreviations. For example, Interior's `OSM` became `OSMRE` in FY2020, so check `Component Name` when you follow one component over time.

### Adding up numbers

Agency totals and component rows should never be added together. This applies to the master table and the 06 table. For example, DHS's FY2024 backlog is 141,420 in the Agency Overall row, and its 15 components also add up to 141,420. Adding all 16 rows would give 282,840, which is twice the real number.

- For a government-wide total, add the Agency Overall rows.
- For an agency's components, add the `component`, `second_entry` and `no_component` rows, and leave out rows with `Exclude From Component Sum = yes`. Only Commerce FY2025 "DOC" has this flag, because it is a copy of a total.
- Counts, dollars and FTE can be added up. Medians, averages, days and dates cannot.

The 03/11 table does not have this problem. For each agency and year, it has either Agency Overall rows or other rows, but not both.

### 0, N/A, blank and <1

| Value | Meaning |
|---|---|
| `0` | In count columns, the agency reported zero. In days and ten-oldest columns, it usually means the agency had no such cases. |
| `N/A` | Not applicable or nothing to calculate. For example, an expedited median when no expedited requests were processed. |
| Blank | Usually the component is not in that data type's table. For example, DOJ reported all its FY2025 appeals under OIP, so the appeals tables are blank for its other 31 components. Data types 24 and 25 are also almost entirely blank before FY2017. |
| `<1` | Less than one day. |

### Coverage by year

| Fiscal Year | Agencies reporting | Agencies with components | Component rows |
|---|---:|---:|---:|
| 2008 | 71 | 21 | 307 |
| 2009 | 73 | 22 | 314 |
| 2010 | 97 | 25 | 360 |
| 2011 | 99 | 25 | 360 |
| 2012 | 99 | 26 | 361 |
| 2013 | 99 | 25 | 357 |
| 2014 | 100 | 26 | 352 |
| 2015 | 100 | 26 | 350 |
| 2016 | 115 | 27 | 349 |
| 2017 | 116 | 29 | 356 |
| 2018 | 118 | 29 | 360 |
| 2019 | 118 | 29 | 350 |
| 2020 | 119 | 28 | 348 |
| 2021 | 118 | 29 | 350 |
| 2022 | 120 | 29 | 349 |
| 2023 | 121 | 30 | 352 |
| 2024 | 122 | 28 | 310 |
| 2025 | 118 | 28 | 306 |
| **Total** | **1,923** | **482** | **6,191** |

In the total row, 1,923 is the number of agency-years (one agency in one year).

An agency is counted in a year if foia.gov has its report for that year, so a change in the count does not necessarily mean an agency was created or closed. The count jumps twice. The 24 agencies added in FY2010, including USDA and EEOC, make up about 9% of that year's requests, so be careful when comparing totals before and after FY2010. The 15 agencies added in FY2016 are small, with 42 requests in total.

### Known issues

These come from foia.gov's own data, and we kept the numbers as reported.

- Components do not add up to the agency total in 13 agency-years: Veterans Affairs FY2025 (47 columns), GSA FY2016 (20), EPA FY2011 (8), Defense FY2025 (3), Commerce FY2025 (2), Agriculture, Labor and EEOC FY2025 (1 each), and USPS FY2010, 2013, 2014, 2016 and 2017 (appeals pending at end of year).
- The Commerce FY2025 "DOC" row repeats the Agency Overall row in 239 of 244 columns, so leave it out when adding up components. In the 06 table it copies the other components, which doubles the Agency Overall statute count (276 instead of 138).
- In FY2025, data type 11, 8 agencies have component values but a blank Agency Overall cell: Justice 1,045, Veterans Affairs 192, EEOC 76, Labor 52, Energy 45, Defense 14, Agriculture 4, Commerce 1. Add up the components for these agencies.
- For Energy FY2025 HQ, data type 11, the reasons add up to 49 but the total column says 45.
- foia.gov's FY2022 CSV export leaves out USAGM, so its All agencies row shows 928,261 requests received. Adding the Agency Overall rows here gives 928,353, because the API includes USAGM's 92 requests.
- The same statute can be written many ways in the 06 table. For example, there are 30 versions of 26 U.S.C. § 6103, so group the names before ranking statutes.
- N/A has several spellings and a few values are written oddly. The README lists them.

### How we checked the tables

- We checked every cell against the API reports a second time with separate code and found no differences.
- We compared the Agency Overall rows with the agency-level table, which comes from foia.gov's CSV exports with a few gaps filled from the API. 469,204 cells match. The other 8 differ because the CSV export is blank (SBA FY2021 fee waiver days and CEQ FY2023 pending request days).
- We compared FY2024 components with foia.gov's component CSV export for 23 data types. All 36,466 cells match.
- We compared the Exemption 3 Agency Overall rows with the agency-level statute table, which is built the same way. All 1,919 agency-years with statutes match.
