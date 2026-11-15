"""Compare two downloads of the foia.gov API and the component tables built from them.

Step 1 compares the report lists and the raw JSON of each report (the links in the JSON are ignored).
Step 2 compares the master table, the 03/11 reasons and the 06 statutes cell by cell. Blank, 0, N/A and "<1" count
as different values, and each change is labeled so a change of writing can be told from a change of number.

Usage: python compare_api_snapshots.py <old api dir> <new api dir> <old component dir> <new component dir> <out dir>
"""
import csv
import glob
import gzip
import json
import os
import sys
from collections import Counter

csv.field_size_limit(10 ** 9)
KEY = ["Fiscal Year", "Agency", "Component", "Component Name", "Row Type"]
MASTER = "component_master_no_03_06_11.csv"
LONG = {"other_reasons_03_11.csv": ["Data Type No.", "Reason", "Quantity"],
        "exemption_statutes_06.csv": ["Statute", "Type of Information Withheld", "Case Citation",
                                      "Number of Times Relied Upon"]}


def strip_links(x):
    if isinstance(x, dict):
        return {k: strip_links(v) for k, v in x.items() if k != "links"}
    if isinstance(x, list):
        return [strip_links(v) for v in x]
    return x


def load_report(path):
    with gzip.open(path, "rt", encoding="utf-8") as h:
        return strip_links(json.load(h))


def report_files(api_dir):
    return {os.path.basename(p): p for p in glob.glob(os.path.join(api_dir, "*", "*.json.gz"))}


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as h:
        return list(csv.DictReader(h))


def label(old, new):
    def kind(v):
        v = v.strip()
        if v == "":
            return "blank"
        if v.lower().replace(".", "").replace("/", "").replace("\\", "") in ("na",):
            return "N/A"
        if v == "<1":
            return "<1"
        try:
            return "0" if float(v.replace(",", "")) == 0 else "number"
        except ValueError:
            return "text"
    a, b = kind(old), kind(new)
    return f"{a} -> {b}"


def compare_reports(old_dir, new_dir, out):
    old_index = {r["id"]: r for r in json.load(open(os.path.join(old_dir, "_index.json")))}
    new_index = {r["id"]: r for r in json.load(open(os.path.join(new_dir, "_index.json")))}
    added = [new_index[i] for i in new_index.keys() - old_index.keys()]
    removed = [old_index[i] for i in old_index.keys() - new_index.keys()]
    renamed = [(old_index[i], new_index[i]) for i in old_index.keys() & new_index.keys() if old_index[i] != new_index[i]]
    old_files, new_files = report_files(old_dir), report_files(new_dir)
    changed = []
    for name in sorted(old_files.keys() & new_files.keys()):
        if load_report(old_files[name]) != load_report(new_files[name]):
            changed.append(name)
    with open(os.path.join(out, "reports_changed.csv"), "w", newline="", encoding="utf-8") as h:
        w = csv.writer(h)
        w.writerow(["status", "report", "year", "agency"])
        for r in added:
            w.writerow(["added", r["title"], r["year"], r["agency"]])
        for r in removed:
            w.writerow(["removed", r["title"], r["year"], r["agency"]])
        for a, b in renamed:
            w.writerow(["index entry changed", f"{a['title']} -> {b['title']}", b["year"], b["agency"]])
        for name in changed:
            w.writerow(["json changed", name, name.split("_")[-2], name.split("_")[0]])
    return [f"reports old {len(old_index)}, new {len(new_index)}",
            f"added {len(added)}, removed {len(removed)}, index entries changed {len(renamed)}",
            f"reports compared {len(old_files.keys() & new_files.keys())}, raw JSON changed {len(changed)}"]


def compare_master(old_dir, new_dir, out):
    old = read_csv(os.path.join(old_dir, MASTER))
    new = read_csv(os.path.join(new_dir, MASTER))

    def index(rows):
        d = {}
        for r in rows:
            k = tuple(r[c] for c in KEY)
            n = 1
            while k + (n,) in d:  # second_entry rows can share a key
                n += 1
            d[k + (n,)] = r
        return d
    a, b = index(old), index(new)
    cols = [c for c in old[0] if c not in KEY]
    lines = [f"master rows old {len(old)}, new {len(new)}",
             f"rows added {len(b.keys() - a.keys())}, rows removed {len(a.keys() - b.keys())}"]
    if list(old[0]) != list(new[0]):
        lines.append(f"columns differ: added {set(new[0]) - set(old[0])}, removed {set(old[0]) - set(new[0])}")
    kinds = Counter()
    with open(os.path.join(out, "master_cells_changed.csv"), "w", newline="", encoding="utf-8") as h:
        w = csv.writer(h)
        w.writerow(KEY + ["column", "old", "new", "change"])
        for k in sorted(a.keys() & b.keys()):
            for c in cols:
                x, y = a[k].get(c, ""), b[k].get(c, "")
                if x != y:
                    t = label(x, y)
                    kinds[t] += 1
                    w.writerow(list(k[:5]) + [c, x, y, t])
    with open(os.path.join(out, "master_rows_changed.csv"), "w", newline="", encoding="utf-8") as h:
        w = csv.writer(h)
        w.writerow(["status"] + KEY)
        for k in sorted(b.keys() - a.keys()):
            w.writerow(["added"] + list(k[:5]))
        for k in sorted(a.keys() - b.keys()):
            w.writerow(["removed"] + list(k[:5]))
    lines.append(f"cells changed {sum(kinds.values())}: {dict(kinds.most_common())}")
    return lines


def compare_long(old_dir, new_dir, name, fields, out):
    def bag(path):
        return Counter(tuple(r[c] for c in KEY + fields) for r in read_csv(path))
    a, b = bag(os.path.join(old_dir, name)), bag(os.path.join(new_dir, name))
    only_old, only_new = a - b, b - a
    stem = name.split(".")[0]
    with open(os.path.join(out, f"{stem}_rows_changed.csv"), "w", newline="", encoding="utf-8") as h:
        w = csv.writer(h)
        w.writerow(["status"] + KEY + fields)
        for k in sorted(only_new.elements()):
            w.writerow(["new"] + list(k))
        for k in sorted(only_old.elements()):
            w.writerow(["old"] + list(k))
    return [f"{name}: rows old {sum(a.values())}, new {sum(b.values())}, "
            f"only old {sum(only_old.values())}, only new {sum(only_new.values())}"]


def main(old_api, new_api, old_comp, new_comp, out):
    os.makedirs(out, exist_ok=True)
    lines = compare_reports(old_api, new_api, out)
    lines += compare_master(old_comp, new_comp, out)
    for name, fields in LONG.items():
        lines += compare_long(old_comp, new_comp, name, fields, out)
    text = "\n".join(lines)
    open(os.path.join(out, "summary.txt"), "w", encoding="utf-8").write(text + "\n")
    print(text)


if __name__ == "__main__":
    main(*sys.argv[1:6])
