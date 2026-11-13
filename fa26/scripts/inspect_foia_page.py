"""
Helper: shows what is on the FOIA.gov page and records what happens when YOU
click the CSV download. Send the printed output back to me.

Run:  python inspect_foia_page.py
Then, in the browser window that opens:
  1. select all agencies   2. pick ONE data type   3. pick a year
  4. click whatever button gets you the CSV
Wait ~90 seconds; the script closes by itself and prints a summary.
"""
from playwright.sync_api import sync_playwright

URL = "https://www.foia.gov/data.html"
WAIT_SECONDS = 90

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    # record anything that looks like a file / API request
    def on_response(resp):
        headers = resp.headers
        ctype = headers.get("content-type", "")
        disp = headers.get("content-disposition", "")
        url = resp.url
        if "csv" in url.lower() or "csv" in ctype or "attachment" in disp or "api" in url.lower():
            print(f"[REQUEST] {resp.request.method} {url}\n          type={ctype} disposition={disp}")

    page.on("response", on_response)
    page.on("download", lambda d: print(f"[DOWNLOAD STARTED] {d.url} -> {d.suggested_filename}"))

    page.goto(URL, wait_until="networkidle")

    print("\n=== HEADINGS ===")
    for h in page.locator("h1, h2, h3, h4, legend").all_inner_texts():
        if h.strip():
            print(" -", h.strip().replace("\n", " "))

    print("\n=== BUTTONS ===")
    for t in page.locator("main button, #main button, main input[type=submit]").all_inner_texts():
        if t.strip():
            print(" -", t.strip().replace("\n", " "))

    print("\n=== LINKS IN MAIN ===")
    for t in page.locator("main a, #main a").all_inner_texts()[:40]:
        if t.strip():
            print(" -", t.strip().replace("\n", " "))

    print("\n=== FORM CONTROLS (type | label) ===")
    controls = page.locator("main input, main select, #main input, #main select")
    for i in range(min(controls.count(), 60)):
        c = controls.nth(i)
        ctype = c.get_attribute("type") or c.evaluate("e => e.tagName").lower()
        label = c.evaluate(
            "e => (e.labels && e.labels[0] ? e.labels[0].innerText : (e.getAttribute('aria-label')||e.id||''))"
        )
        print(f" - {ctype} | {label.strip()[:70]}")

    print(f"\n>>> Now click through the steps yourself. Waiting {WAIT_SECONDS}s ...\n")
    page.wait_for_timeout(WAIT_SECONDS * 1000)
    page.screenshot(path="foia_page_after_clicks.png", full_page=True)
    browser.close()
    print("\nDone. Send me everything printed above (and foia_page_after_clicks.png if you can).")
