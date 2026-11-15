"""Download every annual report (all 32 tables, with components) from the foia.gov API.

The key is read from ~/.foia_api_key (free from api.data.gov) and never written to a file.
One gzip JSON per report: <out dir>/<year>/<agency>_<year>_<first 8 characters of the id>.json.gz.
Reports already downloaded are skipped, so the script can be stopped and run again.

Usage: python download_api_annual.py <report_data_map.json> <out dir>
"""
import gzip
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import urllib.parse
import urllib.request

BASE = "https://api.foia.gov/api"
KEY = open(os.path.expanduser("~/.foia_api_key")).read().strip()
PAUSE = 3.7  # seconds between request starts: about 970 an hour, under the limit of 1,000
WORKERS = 3  # a request takes a few seconds, so a few run at once to use the limit
_lock = threading.Lock()
_next = [0.0]


def pace():
    """One rate limit for all threads: wait for the shared next start time."""
    with _lock:
        now = time.time()
        wait = max(0.0, _next[0] - now)
        _next[0] = max(now, _next[0]) + PAUSE
    time.sleep(wait)


def get(url):
    for attempt in range(5):
        pace()
        try:
            req = urllib.request.Request(url, headers={"X-API-Key": KEY})
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read())
        except Exception as e:  # network error or rate limit: wait and try again
            print("  retry", attempt + 1, type(e).__name__, e, flush=True)
            time.sleep(60 * (attempt + 1))
    raise RuntimeError(f"failed: {url}")


def main(map_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    inc = []
    for g in json.load(open(map_path)):
        for x in g.get("includes", []):
            if x not in inc:
                inc.append(x)
    include = ",".join(["field_agency"] + inc)

    # 1. list of reports
    index_path = os.path.join(outdir, "_index.json")
    if os.path.exists(index_path):
        index = json.load(open(index_path))
    else:
        index = []
        url = BASE + "/annual_foia_report?" + urllib.parse.urlencode({
            "include": "field_agency", "fields[annual_foia_report_data]": "title,field_foia_annual_report_yr,field_agency",
            "fields[agency]": "name,abbreviation", "page[limit]": 50})
        while url:
            d = get(url)
            ag = {x["id"]: x["attributes"] for x in d.get("included", []) if x["type"] == "agency"}
            for r in d["data"]:
                a = (r["relationships"].get("field_agency") or {}).get("data") or {}
                info = ag.get(a.get("id"), {})
                index.append({"id": r["id"], "title": r["attributes"].get("title"),
                              "year": str(r["attributes"].get("field_foia_annual_report_yr")),
                              "agency": info.get("name"), "abbr": info.get("abbreviation")})
            url = (d.get("links", {}).get("next") or {}).get("href")
            print("index", len(index), flush=True)
        json.dump(index, open(index_path, "w"), indent=1)

    # 2. download each report
    todo = [r for r in index if 2008 <= int(r["year"] or 0) <= 2025]

    def fetch(item):
        i, r = item
        safe = "".join(ch if ch.isalnum() else "-" for ch in (r["abbr"] or "NA"))
        path = os.path.join(outdir, r["year"], f"{safe}_{r['year']}_{r['id'][:8]}.json.gz")
        if os.path.exists(path):
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        d = get(f"{BASE}/annual_foia_report/{r['id']}?include={include}")
        with gzip.open(path + ".part", "wt", encoding="utf-8") as h:
            json.dump(d, h)
        os.replace(path + ".part", path)
        print(f"{i}/{len(todo)} {r['abbr']} {r['year']}", flush=True)

    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(fetch, enumerate(todo, 1)))
    print("done", len(todo))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
