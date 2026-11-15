"""从 foia.gov API（网站数据库）下载每份年报的全部 32 张表（含部门），用于和 XML 转换结果做外部对照。

密钥从 ~/.foia_api_key 读（api.data.gov 免费申请），不写进任何文件。
每份年报存一个 gzip JSON：<输出目录>/<年>/<机构缩写>_<年>_<id前8位>.json.gz；已下载的跳过，可断点续跑。

用法：
    python download_api_annual.py <report_data_map.json> <输出目录>
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
PAUSE = 3.7  # 两次请求"开始"之间至少隔 3.7 秒：每小时最多约 970 次，低于 1,000 次的限额
WORKERS = 3  # 单次请求要等几秒，几个并行才能用满限额
_lock = threading.Lock()
_next = [0.0]


def pace():
    """全局节流：所有线程共用一个"下一次可以发请求的时间"。"""
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
        except Exception as e:  # 网络抖动或限流：等一会儿重试
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

    # 1. 年报清单
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

    # 2. 逐份下载
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
