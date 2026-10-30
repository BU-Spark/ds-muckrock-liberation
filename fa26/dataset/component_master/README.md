# component_master

Component-level FOIA data, FY2008-2025, from the foia.gov XML annual reports, with data the XML is missing filled from the foia.gov API.

- `component_master_no_03_11.csv` (8,088 rows, 253 columns): one row per fiscal year x agency x component, plus one "Agency Overall" row per agency per year (1,923). 9 ID columns and 244 data columns covering 31 of the 32 data types. Column names start with the data type number (01-32). For 03 and 11 ("Other" reasons) only the total column is kept.
- `other_reasons_03_11.csv` (13,700 rows, 13 columns): the 03 and 11 "Other" reasons, one row per fiscal year x agency x component x reason. The same 9 ID columns as the master table, plus Data Type No., Data Type, Reason, Quantity. Only reported values are included.
- `exemption_statutes_06.csv` (16,632 rows, 13 columns): 06 Exemption 3 statutes, one row per fiscal year x agency x component x statute. The same 9 ID columns as the master table, plus Statute, Type of Information Withheld, Case Citation, Number of Times Relied Upon.
- `clean_text_06.py`: the text cleaning used for the 06 text columns (see below).

Values are copied as reported: blank, 0 and N/A are not changed.

## 06 Exemption 3 statutes
- Text columns are cleaned with `clean_text_06.clean_text()`, because the same text is written differently depending on the source (foia.gov API, XML annual reports, or the foia.gov CSV export): HTML codes such as `&quot;`, curly vs straight quotes, line breaks, and spellings of N/A. Only formatting changes; counts and ID columns are not touched.
- An agency sometimes lists the same statute more than once; every entry is kept (the foia.gov CSV export shows only one of them).
- Statute names are written in many ways (1,587 different texts; 30 for 26 U.S.C. § 6103). Group them before ranking statutes.
- Commerce FY2025: the "DOC" (Departmental Offices) row is not a separate office. In this file it repeats the other components (same statutes, same counts, 138 in all), and the Agency Overall row adds both, so every count is doubled (276; the correct total is 138). The DOC row is flagged in `Exclude From Component Sum`; for Commerce FY2025, add up the components instead of using Agency Overall.

## Columns to know

### `Level`: what kind of row it is

| Level | Meaning |
|---|---|
| `agency_overall` | The whole agency's total (one row per agency per year). |
| `component` | One office inside the agency. |
| `duplicate_entry` | A second entry for an office that the agency reported twice (5 rows). |

**Use the Agency Overall row or the component rows, never both.** The components add up to the agency total. Example, DHS FY2024 backlog: the 15 components add up to 141,420, and the Agency Overall row is also 141,420. Adding all 16 rows would give 282,840, twice the real number.

**`duplicate_entry` rows:** in 5 cases the agency's report lists the same office twice in one table, with different numbers. Example: NARA FY2025, 03 "Other" reasons: one entry says 23, the other says 97. We can't tell which one is right, so the first entry is the normal `component` row and the second is kept as its own row (only that table's columns are filled). Leave these rows out of totals unless you have checked them.

### `Exclude From Component Sum`: skip this row when adding up components

Only one row has `yes`: Commerce FY2025 "DOC" (Departmental Offices). It looks like an office, but it is really a copy of a total:
- In the master table it copies the Agency Overall. Requests received: Agency Overall 5,368, DOC 5,368, the other components together 5,368.
- In the 06 table it copies the other components added together (see above).

If you add it to the other components, the Commerce numbers come out twice as large.

## Not included
- Rows the XML does not link to any component.

## Known source issue
FY2025: for 8 agencies the 11 Agency Overall total is 0 while their components report values (e.g. Justice: components 1,045, Agency Overall 0).
