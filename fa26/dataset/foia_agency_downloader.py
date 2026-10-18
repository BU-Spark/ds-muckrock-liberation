"""Download FOIA.gov CSV reports for one agency and all its components/periods."""

import argparse
import csv
import hashlib
import re
import sys
import time
import zipfile
from pathlib import Path

from playwright.sync_api import Page, expect, sync_playwright


OUTPUT_ROOT = Path(__file__).resolve().parent / "foia_data" / "by_agency"
TIMEOUT_MS = 30_000
PAUSE_SECONDS = 1.0
MAX_ATTEMPTS = 3

PAGES = {
    "annual": {
        "url": "https://www.foia.gov/data.html",
        "years_group": "Select Fiscal Years",
    },
    "quarterly": {
        "url": "https://www.foia.gov/quarterly.html",
        "years_group": "Select Fiscal Years",
        "quarters_group": "Select Quarters",
    },
}

def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return slug[:80] or "agency"


def step_box(page: Page, heading_regex: str):
    heading = page.get_by_text(re.compile(heading_regex, re.I)).first
    heading.wait_for(state="visible", timeout=TIMEOUT_MS)
    return heading.locator("xpath=ancestor::*[.//input or .//select][1]")


def save_debug(page: Page, tag: str, output_root: Path) -> None:
    debug_dir = output_root / "_debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=str(debug_dir / f"{tag}.png"), full_page=True)
        (debug_dir / f"{tag}.html").write_text(page.content(), encoding="utf-8")
    except Exception as error:
        print(f"Warning: could not save debug capture for {tag}: {error}", file=sys.stderr)


def select_agency_and_components(page: Page, agency: str) -> None:
    agency_search = page.get_by_role("textbox", name="Agency or Component Name")
    expect(agency_search).to_be_enabled(timeout=TIMEOUT_MS)
    agency_search.fill(agency)

    exact_match = page.locator(
        ".tt-dataset-agencies .tt-suggestion"
    ).filter(has_text=re.compile(rf"^\s*{re.escape(agency)}\s*$")).first
    expect(exact_match).to_be_visible(timeout=TIMEOUT_MS)
    agency_search.press("Enter")
    expect(agency_search).to_have_value(agency, timeout=TIMEOUT_MS)
    expect(page.locator(".tt-menu").first).to_be_hidden(timeout=TIMEOUT_MS)

    select_components = page.get_by_role(
        "button", name=re.compile(r"^Select Agency Components$", re.I)
    )
    if select_components.count() == 0:
        print(f"  No additional components offered for {agency}; using agency overall.")
        return

    expect(select_components).to_be_visible(timeout=TIMEOUT_MS)
    select_components.click()

    dialog = page.get_by_role("dialog", name=re.compile(r"Filter agency components", re.I))
    expect(dialog).to_be_visible(timeout=TIMEOUT_MS)
    select_all = dialog.get_by_role("link", name=re.compile(r"^\s*Select All\s*$", re.I))
    expect(select_all).to_be_visible(timeout=TIMEOUT_MS)
    select_all.click()

    components = dialog.get_by_role("checkbox")
    if components.count() == 0:
        raise RuntimeError(f"No components were listed for agency {agency!r}.")
    unchecked = [
        index for index in range(components.count()) if not components.nth(index).is_checked()
    ]
    if unchecked:
        raise RuntimeError(
            f"Could not select all components for {agency!r}; "
            f"{len(unchecked)} component(s) remain unchecked."
        )

    dialog.get_by_role("button", name=re.compile(r"^Submit$", re.I)).click()


def get_data_types(page: Page) -> list[dict[str, object]]:
    box = step_box(page, r"Select Data Type")
    select = box.locator("select")
    if select.count():
        select.first.locator("option").nth(1).wait_for(
            state="attached", timeout=TIMEOUT_MS
        )
        options = select.first.locator("option")
        items: list[dict[str, object]] = []
        parent = ""
        for index in range(options.count()):
            label = (options.nth(index).inner_text() or "").replace("\xa0", " ").strip()
            if not label or re.fullmatch(r"-\s*none\s*-", label, re.I):
                continue
            if label.startswith("-"):
                name = f"{parent} - {label.lstrip('- ').strip()}"
            else:
                parent = label
                name = label
            items.append({"index": index, "label": label, "name": name})
        if not items:
            raise RuntimeError("No report data types were found on the FOIA.gov page.")
        return items

    data_type_labels = box.locator("label")
    data_type_labels.first.wait_for(state="visible", timeout=TIMEOUT_MS)
    labels = [label.strip() for label in data_type_labels.all_inner_texts()]
    items = [{"index": None, "label": label, "name": label} for label in labels if label]
    if not items:
        raise RuntimeError("No report data types were found on the FOIA.gov page.")
    return items


def choose_data_type(page: Page, item: dict[str, object]) -> None:
    box = step_box(page, r"Select Data Type")
    select = box.locator("select")
    if item["index"] is not None:
        select.first.select_option(index=int(item["index"]))
        selected_label = select.first.locator("option:checked").inner_text().strip()
        if selected_label != item["label"]:
            raise RuntimeError(
                f"Selected data type changed: expected {item['label']!r}, "
                f"got {selected_label!r}."
            )
        return

    exact_label = re.compile(rf"^\s*{re.escape(str(item['label']))}\s*$")
    box.locator("label").filter(has_text=exact_label).first.click()


def select_all_in_group(page: Page, group_name: str) -> list[str]:
    group = page.get_by_role("group", name=re.compile(re.escape(group_name), re.I)).first
    group.wait_for(state="visible", timeout=TIMEOUT_MS)
    checkboxes = group.get_by_role("checkbox")
    count = checkboxes.count()
    if count == 0:
        raise RuntimeError(f"No selectable periods were found in {group_name!r}.")

    select_all = group.get_by_role("link", name=re.compile(r"^\s*Select All\s*$", re.I))
    expect(select_all).to_be_visible(timeout=TIMEOUT_MS)
    select_all.click()

    unchecked = [
        index for index in range(checkboxes.count()) if not checkboxes.nth(index).is_checked()
    ]
    if unchecked:
        raise RuntimeError(
            f"Could not select every item in {group_name!r}; "
            f"{len(unchecked)} item(s) remain unchecked."
        )
    return [
        str(checkboxes.nth(index).get_attribute("value") or "")
        for index in range(count)
    ]


def select_all_periods(page: Page, report: str) -> dict[str, list[str]]:
    selected = {
        "years": select_all_in_group(page, PAGES[report]["years_group"]),
    }
    if report == "quarterly":
        selected["quarters"] = select_all_in_group(
            page, PAGES[report]["quarters_group"]
        )
    return selected


def wait_for_report(page: Page) -> None:
    page.get_by_role("button", name=re.compile(r"^View Report$", re.I)).click()
    page.wait_for_url(re.compile(r"/results(?:[?#].*)?$"), timeout=TIMEOUT_MS)
    download_button = page.get_by_role(
        "button", name=re.compile(r"^Download CSV$", re.I)
    )
    expect(download_button).to_be_enabled(timeout=TIMEOUT_MS)


def validate_csv(
    path: Path,
    expected_agency: str | None = None,
    expected_years: set[str] | None = None,
) -> tuple[int, list[str], str]:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("Downloaded file is missing or empty.")
    if zipfile.is_zipfile(path):
        raise ValueError("Downloaded file is a ZIP archive, not a CSV.")

    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        try:
            header = next(reader)
        except StopIteration as error:
            raise ValueError("Downloaded CSV has no header row.") from error

        if len(header) < 2 or not any(column.strip() for column in header):
            raise ValueError("Downloaded CSV has an invalid header row.")
        normalized_header = [column.strip().casefold() for column in header]
        if "agency" not in normalized_header:
            raise ValueError("Downloaded CSV does not contain the Agency column.")
        agency_index = normalized_header.index("agency")
        year_index = (
            normalized_header.index("fiscal year")
            if "fiscal year" in normalized_header
            else -1
        )
        if expected_years and year_index < 0:
            raise ValueError("Downloaded CSV does not contain the Fiscal Year column.")

        row_count = 0
        for row_number, row in enumerate(reader, start=2):
            if not row:
                continue
            if len(row) != len(header):
                raise ValueError(
                    f"CSV row {row_number} has {len(row)} fields; "
                    f"the header has {len(header)}."
                )
            if (
                expected_agency
                and row[agency_index].strip().casefold() != expected_agency.casefold()
            ):
                raise ValueError(
                    f"CSV row {row_number} has agency {row[agency_index]!r}; "
                    f"expected {expected_agency!r}."
                )
            if expected_years and row[year_index].strip() not in expected_years:
                raise ValueError(
                    f"CSV row {row_number} has fiscal year {row[year_index]!r}, "
                    "which was not selected."
                )
            row_count += 1

    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(chunk)
    digest = hasher.hexdigest()
    return row_count, header, digest


def download_one_type(
    page: Page,
    report: str,
    agency: str,
    item: dict[str, object],
    output_dir: Path,
) -> tuple[Path, int]:
    number = int(item["file_number"])
    prefix = f"{number:02d}_"
    destination = output_dir / f"{prefix}{slugify(str(item['name']))}.csv"
    if destination.exists():
        try:
            row_count, _, _ = validate_csv(destination)
        except (OSError, ValueError) as error:
            print(
                f"  Existing output is invalid and will be replaced after a valid "
                f"download: {destination.name} ({error})",
                file=sys.stderr,
            )
        else:
            print(f"  Already present and valid: {destination.name} ({row_count} rows)")
            return destination, row_count

    page.goto(PAGES[report]["url"], wait_until="domcontentloaded")
    page.get_by_role("textbox", name="Agency or Component Name").wait_for(
        state="visible", timeout=TIMEOUT_MS
    )
    select_agency_and_components(page, agency)
    choose_data_type(page, item)
    periods = select_all_periods(page, report)
    wait_for_report(page)

    partial = destination.with_name(destination.name + ".part")
    try:
        with page.expect_download(timeout=TIMEOUT_MS) as download_info:
            page.get_by_role(
                "button", name=re.compile(r"^Download CSV$", re.I)
            ).click()
        download_info.value.save_as(str(partial))
        row_count, header, digest = validate_csv(
            partial,
            expected_agency=agency,
            expected_years=set(periods["years"]),
        )
        partial.replace(destination)
    except Exception:
        partial.unlink(missing_ok=True)
        raise

    print(
        f"  Saved {destination.name}: {row_count} rows, "
        f"{len(header)} columns, SHA-256 {digest[:12]}, periods={periods}"
    )
    return destination, row_count


def run_report(
    page: Page, report: str, agency: str, output_root: Path
) -> list[str]:
    output_dir = output_root / slugify(agency) / report
    output_dir.mkdir(parents=True, exist_ok=True)

    page.goto(PAGES[report]["url"], wait_until="domcontentloaded")
    page.get_by_role("textbox", name="Agency or Component Name").wait_for(
        state="visible", timeout=TIMEOUT_MS
    )
    items = get_data_types(page)
    print(f"\n[{report.upper()}] {len(items)} data type(s) found for {agency!r}")

    failures: list[str] = []
    for number, item in enumerate(items, start=1):
        item["file_number"] = number
        name = str(item["name"])
        print(f"  [{number:02d}/{len(items):02d}] {name}")
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                destination, _ = download_one_type(
                    page, report, agency, item, output_dir
                )
                print(f"  Complete: {destination}")
                break
            except Exception as error:
                print(f"  Attempt {attempt}/{MAX_ATTEMPTS} failed: {error}", file=sys.stderr)
                save_debug(
                    page,
                    f"{slugify(agency)}_{report}_{number:02d}_attempt{attempt}",
                    output_root,
                )
                if attempt == MAX_ATTEMPTS:
                    failures.append(name)
        time.sleep(PAUSE_SECONDS)

    if failures:
        print(f"[{report.upper()}] Failed data types: {', '.join(failures)}", file=sys.stderr)
    else:
        print(f"[{report.upper()}] All {len(items)} data types downloaded or validated.")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download FOIA.gov CSV reports for one agency, all components, and all available periods."
    )
    parser.add_argument("--agency", required=True, help="Exact agency name shown on FOIA.gov")
    parser.add_argument(
        "--report", choices=["annual", "quarterly", "both"], default="annual"
    )
    parser.add_argument("--output", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    reports = ["annual", "quarterly"] if args.report == "both" else [args.report]
    failures: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.headless)
        try:
            context = browser.new_context(accept_downloads=True)
            context.set_default_timeout(TIMEOUT_MS)
            page = context.new_page()
            for report in reports:
                try:
                    failures.extend(
                        f"{report}: {name}"
                        for name in run_report(page, report, args.agency, args.output)
                    )
                except Exception as error:
                    failures.append(f"{report}: {error}")
                    print(f"[{report.upper()}] Fatal error: {error}", file=sys.stderr)
                    save_debug(page, f"{slugify(args.agency)}_{report}_fatal", args.output)
            context.close()
        finally:
            browser.close()

    if failures:
        print("\nRun completed with failures:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
