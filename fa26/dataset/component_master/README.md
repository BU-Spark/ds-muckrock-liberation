# component_master

Component-level FOIA data, FY2008-2025, from the foia.gov XML annual reports, with data the XML is missing filled from the foia.gov API.

- `component_master_no_03_11.csv` (8,088 rows, 253 columns): one row per fiscal year x agency x component, plus one "Agency Overall" row per agency per year (1,923). 9 ID columns and 244 data columns covering 31 of the 32 data types. Column names start with the data type number (01-32). For 03 and 11 ("Other" reasons) only the total column is kept.
- `other_reasons_long.csv` (13,700 rows): the 03 and 11 "Other" reasons, one row per fiscal year x agency x component x reason. Only reported values are included.

Values are copied as reported: blank, 0 and N/A are not changed.

## Columns to know
- `Level`: `agency_overall`, `component`, or `duplicate_entry` (5 rows where the XML reports the same component twice with different numbers). Don't add Agency Overall rows to component rows.
- `Exclude From Component Sum`: `yes` for 1 row (Commerce FY2025 "DOC", which repeats the Agency Overall numbers). Leave it out when adding up components.

## Not included
- 06 Exemption 3 statutes (one row per statute, kept separately).
- Rows the XML does not link to any component.

## Known source issue
FY2025: for 8 agencies the 11 Agency Overall total is 0 while their components report values (e.g. Justice: components 1,045, Agency Overall 0).
