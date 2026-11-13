"""
FOIA.gov CSV downloader  (Annual + Quarterly reports)
=====================================================

What one run does for ONE year:
  for every data type on the page:
      1. open the report page fresh
      2. select ALL agencies/components
      3. select that ONE data type
      4. select the fiscal year (annual) / quarters of that year (quarterly)
      5. click the CSV download and save it to  foia_data/<report>/<year>/

Usage examples
--------------
  python foia_downloader.py --year 2009
  python foia_downloader.py --year 2009 --report quarterly
  python foia_downloader.py --year 2008-2025            # a range, one year after another
  python foia_downloader.py --year 2015 --report both
  python foia_downloader.py --year 2015 --headless      # no browser window

Or just edit YEAR below and run:  python foia_downloader.py
"""

import argparse
import hashlib
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

# =====================================================================
# SETTINGS  (the only part you should normally need to change)
# =====================================================================
YEAR = "2009"                    # <-- change the year here (or use --year on the command line)
REPORT = "annual"                # "annual", "quarterly" or "both"
OUTPUT_ROOT = Path("foia_data")  # folder where everything is saved
HEADLESS = False                 # False = you can watch the browser work
TIMEOUT_MS = 30_000              # how long to wait for the page (milliseconds)
PAUSE_SECONDS = 1.0              # small pause between downloads (be polite to the site)
MAX_ATTEMPTS = 3                 # retries per file
LOAD_TIMEOUT_S = 300             # max seconds to wait for a report to finish loading
QUIET_SECONDS = 6                # report is "loaded" after this many seconds with no new data

# ---------------------------------------------------------------------
# PAGE DETAILS  (if the website changes its wording, fix it here)
# These are regular expressions that are matched against text on the page.
# ---------------------------------------------------------------------
PAGES = {
    "annual": {
        "url": "https://www.foia.gov/data.html",
        "period_heading": r"Select Fiscal Years?",
    },
    "quarterly": {
        "url": "https://www.foia.gov/quarterly.html",
        "period_heading": r"Select (Fiscal Years?|Quarters?)",
    },
}
AGENCY_HEADING = r"Select Agenc"          # step 1 heading
DATATYPE_HEADING = r"Select Data Type"    # step 2 heading
SELECT_ALL_TEXT = r"select all|all agencies|all components"
SUBMIT_BUTTON = r"^\s*(view|search|submit|generate|apply|go|show|run|create)\b"
DOWNLOAD_TEXT = r"download.*csv|csv|download"


# =====================================================================
# HELPERS
# =====================================================================
def slugify(text):
    """'Requests Received & Processed' -> 'requests_received_processed'"""
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return text[:80] or "dataset"


def step_box(page, heading_regex):
    """Find the block of the page that belongs to one step (by its heading)."""
    heading = page.get_by_text(re.compile(heading_regex, re.I)).first
    heading.wait_for(state="visible", timeout=TIMEOUT_MS)
    # closest parent that contains form controls
    return heading.locator("xpath=ancestor::*[.//input or .//select][1]")


def exact_text(name):
    return re.compile(rf"^\s*{re.escape(name)}\s*$")


def save_debug(page, tag):
    """On failure, save a screenshot + HTML so you can see what the page looked like."""
    debug_dir = OUTPUT_ROOT / "_debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=str(debug_dir / f"{tag}.png"), full_page=True)
        (debug_dir / f"{tag}.html").write_text(page.content(), encoding="utf-8")
    except Exception:
        pass


# =====================================================================
# THE THREE STEPS ON THE PAGE
# =====================================================================
def select_all_agencies(page):
    """Step 1: click the 'Select All Agencies' link."""
    main = page.locator("main, #main").first
    pattern = re.compile(r"select all agenc", re.I)
    target = main.get_by_role("link", name=pattern).or_(main.get_by_role("button", name=pattern))
    try:
        target.first.wait_for(state="visible", timeout=10_000)
        target.first.click()
    except Exception:
        select_all_agencies_fallback(page)


def select_all_agencies_fallback(page):
    """Step 1: tick 'select all' (or every agency checkbox as a fallback)."""
    box = step_box(page, AGENCY_HEADING)

    toggle = box.get_by_role("checkbox", name=re.compile(SELECT_ALL_TEXT, re.I))
    if toggle.count():
        if not toggle.first.is_checked():
            toggle.first.check(force=True)
        return

    # maybe it's a button/link instead of a checkbox
    button = box.locator("button, a, label").filter(
        has_text=re.compile(SELECT_ALL_TEXT, re.I)
    )
    if button.count():
        button.first.click()
        return

    # fallback: tick every checkbox in the agency box
    boxes = box.get_by_role("checkbox")
    for i in range(boxes.count()):
        if not boxes.nth(i).is_checked():
            boxes.nth(i).evaluate("e => e.click()")


def get_data_types(page):
    """Step 2 (discovery): read EVERY data type from the dropdown, including the
    indented sub-items ("- Disposition (Dis.)"). Each item remembers its position
    in the list, because some sub-item names repeat under different parents."""
    box = step_box(page, DATATYPE_HEADING)

    select = box.locator("select")
    if select.count():
        options = select.first.locator("option")
        items, parent = [], ""
        for i in range(options.count()):
            label = (options.nth(i).inner_text() or "").replace("\xa0", " ").strip()
            if not label or re.fullmatch(r"-\s*none\s*-", label, re.I):
                continue                                   # skip the empty "- none -" choice
            if label.startswith("-"):                      # sub-item of the last heading
                child = label.lstrip("- ").strip()
                name = f"{parent} - {child}"
            else:                                          # top-level heading
                parent = label
                name = label
            items.append({"index": i, "label": label, "name": name})
        return "select", items

    labels = [t.strip() for t in box.locator("label").all_inner_texts()]
    items = []
    for n in labels:
        if n and n not in [x["label"] for x in items]:
            items.append({"index": None, "label": n, "name": n})
    return "choice", items


def choose_data_type(page, kind, item):
    """Step 2 (action): select exactly ONE data type (by its position in the list)."""
    box = step_box(page, DATATYPE_HEADING)
    if kind == "select":
        box.locator("select").first.select_option(index=item["index"])
    else:
        box.locator("label").filter(has_text=exact_text(item["label"])).first.click()


def choose_period(page, report, year):
    """Step 3: pick the fiscal year (annual) or the quarters of that year (quarterly)."""
    # Annual page: one checkbox per year (2008, 2009, ...). Tick only the wanted year.
    main = page.locator("main, #main").first
    year_boxes = main.get_by_role("checkbox", name=re.compile(r"^\s*\d{4}\s*$"))
    if report == "annual" and year_boxes.count():
        found = False
        for i in range(year_boxes.count()):
            box_i = year_boxes.nth(i)
            label = box_i.evaluate(
                "e => (e.labels && e.labels[0]) ? e.labels[0].innerText.trim() : ''"
            )
            wanted = label == str(year)
            found = found or wanted
            if box_i.is_checked() != wanted:
                cb_id = box_i.get_attribute("id")
                label_el = main.locator(f'label[for="{cb_id}"]')
                if cb_id and label_el.count():
                    label_el.first.scroll_into_view_if_needed()
                    label_el.first.click()          # click the visible label
                else:
                    box_i.evaluate("e => e.click()")  # fallback: click via JavaScript
        if not found:
            raise ValueError(f"Year {year} is not offered for the annual report.")
        return

    box = step_box(page, PAGES[report]["period_heading"])
    year_pattern = re.compile(rf"\b{year}\b")

    select = box.locator("select")
    if select.count():
        options = select.first.locator("option").all_inner_texts()
        matches = [o.strip() for o in options if year_pattern.search(o)]
        if not matches:
            raise ValueError(f"Year {year} is not offered for the {report} report.")
        select.first.select_option(label=matches[0])
        return

    labels = box.locator("label").filter(has_text=year_pattern)
    if labels.count() == 0:
        raise ValueError(f"Year {year} is not offered for the {report} report.")
    for i in range(labels.count()):
        labels.nth(i).click()


API_STATE = {"last": 0.0, "count": 0}


def watch_api(page):
    """Remember when the report data last arrived (the page loads it in many small batches)."""
    def on_response(resp):
        url = resp.url
        if "api.foia.gov/api/" in url and "report" in url and "fiscal_years" not in url:
            API_STATE["last"] = time.monotonic()
            API_STATE["count"] += 1
    page.on("response", on_response)


def validate_csv(path):
    """Reject files that are not real CSVs (e.g. a ZIP) or that duplicate another download."""
    data = path.read_bytes()
    if data[:2] == b"PK":
        path.unlink()
        raise RuntimeError("Got a ZIP file, not a CSV (wrong button was clicked)")
    first_line = data[:4096].decode("utf-8", errors="replace").splitlines()[:1]
    if not first_line or "," not in first_line[0]:
        path.unlink()
        raise RuntimeError("File does not look like a CSV (no header row with commas)")
    digest = hashlib.md5(data).hexdigest()
    for other in path.parent.glob("*.csv"):
        if other != path and hashlib.md5(other.read_bytes()).hexdigest() == digest:
            path.unlink()
            raise RuntimeError(f"File is identical to {other.name}; the data type may not have changed")


def download_csv(page, destination):
    """Click 'View Report', wait until the data has finished loading, click 'Download CSV'."""
    main = page.locator("main, #main").first
    API_STATE["last"], API_STATE["count"] = 0.0, 0

    try:
        main.get_by_role("button", name=re.compile(r"view report", re.I)).first.click()

        # wait until the data stops arriving
        started = time.monotonic()
        while True:
            now = time.monotonic()
            quiet = now - API_STATE["last"]
            if API_STATE["count"] > 0 and quiet > QUIET_SECONDS:
                break
            if API_STATE["count"] == 0 and now - started > 20:
                break  # nothing was requested; carry on and let the CSV button decide
            if now - started > LOAD_TIMEOUT_S:
                raise RuntimeError("Report did not finish loading in time")
            time.sleep(1)

        csv_button = main.get_by_role("button", name=re.compile(r"download csv", re.I)).first
        expect(csv_button).to_be_enabled(timeout=TIMEOUT_MS)
        with page.expect_download(timeout=TIMEOUT_MS) as info:
            csv_button.click()
        info.value.save_as(str(destination))
        validate_csv(destination)
    except Exception as error:
        names = main.locator("button, a")
        seen = []
        for i in range(min(names.count(), 30)):
            text = (names.nth(i).inner_text() or "").strip()
            if text and text not in seen:
                seen.append(text)
        raise RuntimeError(f"{error} | Buttons/links seen: {' | '.join(seen)}") from None


# =====================================================================
# MAIN LOOP
# =====================================================================
def run_one_year(page, report, year):
    url = PAGES[report]["url"]
    out_dir = OUTPUT_ROOT / report / str(year)
    out_dir.mkdir(parents=True, exist_ok=True)          # creates e.g. foia_data/annual/2009/

    page.goto(url, wait_until="networkidle")
    kind, data_types = get_data_types(page)
    print(f"\n[{report.upper()} {year}] found {len(data_types)} data types")

    done, failed = [], []
    for number, item in enumerate(data_types, start=1):
        name = item["name"]
        destination = out_dir / f"{number:02d}_{slugify(name)}.csv"

        if destination.exists():
            print(f"  [{number:02d}] already downloaded, skipping: {destination.name}")
            done.append(name)
            continue

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                page.goto(url, wait_until="networkidle")  # fresh page = clean selections
                select_all_agencies(page)                 # 1) all agencies
                choose_data_type(page, kind, item)        # 2) one data type
                choose_period(page, report, year)         # 3) the year
                download_csv(page, destination)           # download + save
                print(f"  [{number:02d}] saved: {destination}")
                done.append(name)
                break
            except Exception as error:
                print(f"  [{number:02d}] attempt {attempt}/{MAX_ATTEMPTS} failed: {error}")
                save_debug(page, f"{report}_{year}_{number:02d}_attempt{attempt}")
                if attempt == MAX_ATTEMPTS:
                    failed.append(name)
        time.sleep(PAUSE_SECONDS)

    print(f"[{report.upper()} {year}] finished: {len(done)} ok, {len(failed)} failed")
    for name in failed:
        print(f"    FAILED: {name}")


def parse_years(text):
    """'2009' -> [2009]     '2008-2025' -> [2008, ..., 2025]"""
    text = str(text).strip()
    if "-" in text:
        start, end = text.split("-")
        return list(range(int(start), int(end) + 1))
    return [int(text)]


def main():
    parser = argparse.ArgumentParser(description="Download FOIA.gov CSV files.")
    parser.add_argument("--year", default=YEAR, help="e.g. 2009 or 2008-2025")
    parser.add_argument("--report", default=REPORT, choices=["annual", "quarterly", "both"])
    parser.add_argument("--headless", action="store_true", help="hide the browser window")
    args = parser.parse_args()

    reports = ["annual", "quarterly"] if args.report == "both" else [args.report]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS or args.headless)
        context = browser.new_context(accept_downloads=True)
        context.set_default_timeout(TIMEOUT_MS)
        page = context.new_page()
        watch_api(page)

        for report in reports:
            for year in parse_years(args.year):
                try:
                    run_one_year(page, report, year)
                except Exception as error:
                    print(f"[{report.upper()} {year}] skipped: {error}")
                    save_debug(page, f"{report}_{year}_fatal")

        browser.close()


if __name__ == "__main__":
    main()