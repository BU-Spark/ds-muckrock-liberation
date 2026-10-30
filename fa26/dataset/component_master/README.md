# component_master

Component-level FOIA data, FY2008-2025, from the foia.gov XML annual reports, with data the XML is missing filled from the foia.gov API.

- `component_master_no_03_11.csv` (8,088 rows, 253 columns): one row per fiscal year x agency x component, plus one "Agency Overall" row per agency per year (1,923). 9 ID columns and 244 data columns covering 31 of the 32 data types. Column names start with the data type number (01-32). For 03 and 11 ("Other" reasons) only the total column is kept.
- `other_reasons_long.csv` (13,700 rows): the 03 and 11 "Other" reasons, one row per fiscal year x agency x component x reason. Only reported values are included.
- `exemption_statutes_06.csv` (16,632 rows): 06 Exemption 3 statutes, one row per fiscal year x agency x component x statute, with the same 9 ID columns as the master table. Columns: Statute, Type of Information Withheld, Case Citation, Number of Times Relied Upon.
- `foia_text.py`: the text cleaning used for the 06 text columns (see below).

Values are copied as reported: blank, 0 and N/A are not changed.

## 06 Exemption 3 statutes
- Text columns are cleaned with `foia_text.clean_text()`, because the same text is written differently depending on the source (foia.gov API, XML annual reports, or the foia.gov CSV export): HTML codes such as `&quot;`, curly vs straight quotes, line breaks, and spellings of N/A. Only formatting changes; counts and ID columns are not touched.
- An agency sometimes lists the same statute more than once; every entry is kept (the foia.gov CSV export shows only one of them).
- Statute names are written in many ways (1,587 different texts; 30 for 26 U.S.C. § 6103). Group them before ranking statutes.
- Commerce FY2025: the "DOC" row equals the other components combined (138), and the Agency Overall counts it twice (276). It is flagged in `Exclude From Component Sum`.

## Columns to know
- `Level`: `agency_overall`, `component`, or `duplicate_entry` (5 rows where the XML reports the same component twice with different numbers). Don't add Agency Overall rows to component rows.
- `Exclude From Component Sum`: `yes` for 1 row (Commerce FY2025 "DOC", which repeats the Agency Overall numbers). Leave it out when adding up components.

## Not included
- Rows the XML does not link to any component.

## Known source issue
FY2025: for 8 agencies the 11 Agency Overall total is 0 while their components report values (e.g. Justice: components 1,045, Agency Overall 0).
