"""Build docs/data/walk_s0|s1|s3|s4.json: the four storyline cards and their steps.
usage: MPLBACKEND=Agg python storylines/build/build_walks.py docs/data"""
import json, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "notebooks")); sys.path.insert(0, str(HERE))
import walk_s0, walk_s3, walk_s4
out = Path(sys.argv[1])
EXPLORE = {"s0": {"q": 1, "label": "Requests received & processed"}, "s1": {"q": 4, "label": "Outcomes & exemptions"},
           "s3": {"q": 5, "label": "Appeals"}, "s4": {"q": 6, "label": "Backlog vs intake"}}
# S1: the existing build (steps 1-10, all asserted), wrapped in the same shape as the others
with tempfile.TemporaryDirectory() as td:
    subprocess.run([sys.executable, str(HERE / "build_s1_walk.py"), f"{td}/s1.json"], check=True, capture_output=True)
    s1 = json.load(open(f"{td}/s1.json"))
s1_cover_series = s1["cover"]["series"]
assert s1_cover_series["Released in full"][0] == 50.0 and s1_cover_series["Released in full"][-1] == 21.4
walks = {"s1": {"id": "s1", "name": "Outcomes", "years": s1["years"], "steps": s1["steps"],
    "cover": {"kicker": "Outcomes", "title": "A shrinking share of requests is released in full",
      "body": "Outside DHS and NARA, the share of processed requests released in full fell from 50.0% in FY2008 to 21.4% in FY2025. The fall holds with any single agency or component left out, and it comes mostly from agencies' own shares falling.",
      "foot": "Share of all processed requests. Why DHS and NARA are left out, and what lies behind the fall, is in the steps.",
      "chart": {"title": "Share of closed requests, outside DHS and NARA", "series": s1_cover_series}}}}
for mod in (walk_s0, walk_s3, walk_s4):
    w = mod.build(); w["years"] = s1["years"]; walks[w["id"]] = w
# renamed agencies: current name first, former name in brackets (applied once, so no double brackets)
import re
RENAME = [(re.compile(r"\bDepartment of Defense\b(?! *\))"), "Department of War (Department of Defense)"), (re.compile(r"(?<!\()\bDoD\b(?!\))"), "DoW (DoD)")]
def renamed(x):
    if isinstance(x, str):
        for pat, rep in RENAME: x = pat.sub(rep, x)
        return x
    if isinstance(x, list): return [renamed(v) for v in x]
    if isinstance(x, dict): return {renamed(k): renamed(v) for k, v in x.items()}
    return x
for k, w in walks.items():
    w["explore"] = EXPLORE[k]
    w = renamed(w)
    (out / f"walk_{k}.json").write_text(json.dumps(w, ensure_ascii=False))
    print(f"walk_{k}.json: {len(w['steps'])} steps, {sum(len(s['charts']) for s in w['steps'])} charts")
