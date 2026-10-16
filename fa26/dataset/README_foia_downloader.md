# FOIA.gov CSV Downloader

Automatically downloads the **Annual** (and **Quarterly**) FOIA report data from
[foia.gov](https://www.foia.gov/data.html) as CSV files, one file per data type, organised in one folder per year.

It does what you would otherwise do by hand on the "Create an Annual Report" page, over and over:

1. Select **all agencies and components**
2. Select **one data type**
3. Select **one fiscal year**
4. Click **View Report**, wait for it to load, then click **Download CSV**

---

## Files in this project

| File | Purpose |
|---|---|
| `foia_downloader.py` | The main script. Downloads the CSV files. |
| `inspect_foia_page.py` | Optional helper. Opens the page, lists its buttons and controls, and records what the site does when you click through manually. Use it only if the website changes and the main script stops working. |
| `README_foia_downloader.md` | This guide. |

---

## Requirements

- Python 3.10 or newer
- The `playwright` package and its Chromium browser
- Internet access to `foia.gov` and `api.foia.gov`

### One-time setup

From your project folder (with your virtual environment active):

```bash
pip install playwright
playwright install chromium
```

---

## How to run it

Each run handles **one year** (or a range of years you ask for).

```bash
# Annual report, one year
python foia_downloader.py --year 2009

# Quarterly report, one year
python foia_downloader.py --year 2009 --report quarterly

# Both annual and quarterly
python foia_downloader.py --year 2015 --report both

# A range of years, one after another
python foia_downloader.py --year 2008-2025

# Hide the browser window (faster, runs in the background)
python foia_downloader.py --year 2009 --headless
```

If the script is inside a `scripts/` folder, use `python scripts/foia_downloader.py ...` instead.

### Changing the year without the command line

Open `foia_downloader.py` and edit this line near the top, then run `python foia_downloader.py`:

```python
YEAR = "2009"
```

### Command-line options

| Option | Values | Meaning |
|---|---|---|
| `--year` | `2009` or `2008-2025` | Which fiscal year(s) to download |
| `--report` | `annual`, `quarterly`, `both` | Which report to download (default: `annual`) |
| `--headless` | (flag) | Run without showing the browser window |

---

## What you get

Files are saved in a folder per report and per year:

```
foia_data/
  annual/
    2009/
      01_requests.csv
      02_requests_disposition_dis.csv
      03_requests_dis_other_reasons.csv
      04_requests_expedited_processing.csv
      05_exemptions.csv
      06_exemptions_exemption_3_statutes.csv
      07_appeals.csv
      ...
    2010/
      ...
  quarterly/
    2009/
      ...
  _debug/        (screenshots + HTML saved only when something fails)
```

- The **number** at the start of each file name is the data type's position in the website dropdown.
- Sub-items include their parent heading in the name, because some names repeat
  (for example "Disposition" appears under both Requests and Appeals).
- Each CSV contains **all agencies and components** for **one data type** and **one year**.

---

## What the script does, step by step

For every data type in the dropdown, in order:

1. **Opens the page fresh** so earlier selections never carry over.
2. **Selects all agencies** by clicking "Select All Agencies".
3. **Selects the data type** from the dropdown (by its position in the list, so repeated names are not confused).
4. **Selects the fiscal year**: ticks the chosen year and makes sure no other year is ticked.
5. **Clicks "View Report"**. The website loads the report data from its API in many small batches.
6. **Waits until loading has finished** (no new data arrives for 6 seconds). Clicking "Download CSV" too early would give an incomplete file.
7. **Clicks "Download CSV"** and saves the file into the year folder.
8. **Checks the file** (see below). If it is wrong, the file is deleted and the attempt is retried.

### Built-in safety features

- **Resume support:** a file that already exists is skipped, so you can stop the script and run it again to continue.
- **Retries:** each file is tried up to 3 times.
- **File validation:** a downloaded file is rejected and deleted if it
  - is a ZIP file instead of a CSV,
  - has no CSV header row, or
  - is identical to another file in the same folder (a sign that the data type did not change).
- **Debug snapshots:** when an attempt fails, a screenshot and the page HTML are saved to `foia_data/_debug/`.
- **Summary:** at the end of each year the script prints how many files succeeded and lists any that failed.

---

## Settings you can change

All settings are at the top of `foia_downloader.py`:

| Setting | Default | Meaning |
|---|---|---|
| `YEAR` | `"2009"` | Year used when `--year` is not given |
| `REPORT` | `"annual"` | `annual`, `quarterly` or `both` |
| `OUTPUT_ROOT` | `foia_data` | Folder where everything is saved |
| `HEADLESS` | `False` | `True` hides the browser window |
| `TIMEOUT_MS` | `30000` | How long to wait for a page action (milliseconds) |
| `PAUSE_SECONDS` | `1.0` | Pause between files, to be polite to the website |
| `MAX_ATTEMPTS` | `3` | Retries per file |
| `LOAD_TIMEOUT_S` | `300` | Longest wait for one report to finish loading (seconds) |
| `QUIET_SECONDS` | `6` | Report counts as "loaded" after this many seconds without new data |

---

## How long does it take?

Reports for all agencies load in many small batches, so each file takes roughly **1 to 3 minutes**.
With around 30 data types, one year takes roughly **45 to 90 minutes**. Your first run will show the real time per file.

Tips:

- Test with **one year** first before running a long range.
- Use `--headless` for long runs.
- You can stop with `Ctrl+C` at any time and run the same command again to resume.
- Do not run more than 2 or 3 copies at once, to avoid overloading the website.

---

## Checking your results

```bash
# Every file should say "CSV text" (not "Zip archive")
file foia_data/annual/2009/*.csv

# File sizes should differ between data types
ls -l foia_data/annual/2009/
```

Open one file in Excel or a text editor: it should have readable column headers, one row per agency or component, and data for the chosen year only.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| `can't open file ... No such file or directory` | You are in the wrong folder. Use the full path, for example `python scripts/foia_downloader.py --year 2009`. |
| `No module named playwright` | Run `pip install playwright` and `playwright install chromium` inside your active virtual environment. |
| Error ends with `Buttons/links seen: ...` | The website's wording changed. Check `foia_data/_debug/` for the screenshot, or run `inspect_foia_page.py`, and update the button names in the script. |
| A file is rejected as "a ZIP" or "identical to ..." | The wrong button was clicked or the selection did not apply. Delete the year folder and run again; if it repeats, send the error message and the debug screenshot. |
| `Year ... is not offered` | That year is not available for that report (quarterly data starts later than annual). The script reports this and moves on. |
| Everything times out | Check your internet connection. Try raising `LOAD_TIMEOUT_S`. |

### Re-downloading a year from scratch

The script skips files that already exist, so delete the folder first:

```bash
rm -rf foia_data/annual/2009
python foia_downloader.py --year 2009
```

---

## Using the helper script (`inspect_foia_page.py`)

If the website changes and the downloader stops working:

```bash
python inspect_foia_page.py
```

A browser opens. Select all agencies, one data type and a year, and click the buttons that produce the CSV. After about 90 seconds the script prints the page's headings, buttons and form controls, plus any network requests made. Use that output to update the button names in `foia_downloader.py`.

To inspect the quarterly page, change the `URL` line in the helper to `https://www.foia.gov/quarterly.html`.

---

## Quarterly data

The quarterly option uses the same steps against `https://www.foia.gov/quarterly.html` and picks the quarters that match the year you give.
The annual page has been checked against the live site; **the quarterly page has not been tested yet**, so run a single year first:

```bash
python foia_downloader.py --year 2024 --report quarterly
```

If it fails, use the helper script on the quarterly page and update the settings.

---

## Adding it to your Git branch

From inside your repository:

```bash
git checkout -b feature/foia-downloader
mkdir -p scripts
# copy foia_downloader.py, inspect_foia_page.py and README_foia_downloader.md into scripts/
echo "foia_data/" >> .gitignore          # keeps the large CSV files out of git
git add scripts/ .gitignore
git commit -m "Add FOIA.gov annual and quarterly CSV downloader"
git push -u origin feature/foia-downloader
```

To use an existing branch instead, replace the first line with `git checkout your-branch-name`.

---

## Notes

- This script drives a normal browser the way a person would. FOIA data is public, but keep the pause between files and avoid heavy parallel runs.
- The script depends on the website's current layout. If foia.gov redesigns the page, button names or the order of steps may need updating (see the helper script above).
- The bulk dataset page (`https://www.foia.gov/foia-dataset-download.html`) offers complete yearly archives in XML format. This script produces the per-data-type CSV files from the report page instead.
