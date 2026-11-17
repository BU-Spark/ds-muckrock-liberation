"""Read or change the dashboard code that runs inside docs/index.html.

The page was rendered once with Quarto. Its code is kept in one <script type="ojs-module-contents"> block, as
base64-encoded JSON with one entry per cell. This script writes the cells out as files and puts them back.

    python tools/page_code.py unpack <folder>     # one file per cell: c01.js, c02.js, ...
    python tools/page_code.py pack <folder>       # write the edited cells back into docs/index.html

Keep the number of cells the same: the page has one output slot per cell.
"""
import base64
import json
import re
import sys
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "docs" / "index.html"
BLOCK = re.compile(r'(<script type="ojs-module-contents">\s*)(.*?)(\s*</script>)', re.S)


def cells(page):
    m = BLOCK.search(page)
    return m, json.loads(base64.b64decode(m.group(2)).decode("utf-8"))


def unpack(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    _, blob = cells(PAGE.read_text(encoding="utf-8"))
    for i, c in enumerate(blob["contents"], 1):
        (folder / f"c{i:02d}.js").write_text(c["source"], encoding="utf-8")
    print(f"{len(blob['contents'])} cells -> {folder}")


def pack(folder):
    folder = Path(folder)
    page = PAGE.read_text(encoding="utf-8")
    m, blob = cells(page)
    files = sorted(folder.glob("c[0-9][0-9].js"))
    if len(files) != len(blob["contents"]):
        sys.exit(f"{len(files)} files for {len(blob['contents'])} cells: the number of cells must stay the same")
    changed = 0
    for c, f in zip(blob["contents"], files):
        source = f.read_text(encoding="utf-8")
        changed += source != c["source"]
        c["source"] = source
    coded = base64.b64encode(json.dumps(blob, ensure_ascii=False).encode("utf-8")).decode()
    PAGE.write_text(page[:m.start(2)] + coded + page[m.end(2):], encoding="utf-8")
    print(f"{changed} cells changed -> {PAGE}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("unpack", "pack"):
        sys.exit(__doc__)
    {"unpack": unpack, "pack": pack}[sys.argv[1]](sys.argv[2])
