"""Shared helpers for the storyline walkthroughs (S0, S3, S4). Text check: every number written in a card must appear,
as written, in the final notebook's own text (11/12), where the notebook checks it with an assertion."""
import json, re
from pathlib import Path
NB_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NUM = re.compile(r"(?<![\w.])[−-]?\d(?:[\d,]*\d)?(?:\.\d+)?")

def notebook_numbers(name):
    nb = json.load(open(NB_DIR / f"{name}.ipynb"))
    text = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown")
    return {t.replace("−", "-").lstrip("-") for t in NUM.findall(text)}

def card_texts(walk):
    out = [walk["cover"]["title"], walk["cover"]["body"], walk["cover"].get("foot", "")]
    for s in walk["steps"]:
        out += [s["title"], s.get("method", "")] + [p for x in s["sections"] for p in x["p"]]
        for t in s.get("tables", []): out += [t["title"]]   # table cells come straight from asserted series, not from prose
    return out

def check_numbers(walk, name, allow=()):
    known = notebook_numbers(name) | {str(a) for a in allow}
    bad = sorted({t.replace("−", "-").lstrip("-") for txt in card_texts(walk) for t in NUM.findall(txt)} - known)
    assert not bad, f"{name}: numbers in the cards that are not in the notebook text: {bad}"
    return True
