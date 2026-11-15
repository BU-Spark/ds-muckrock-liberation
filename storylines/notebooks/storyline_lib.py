import csv, re
from collections import defaultdict
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "component_master_no_03_06_11.csv")  # the repo's data/ folder
rows = list(csv.DictReader(open(P, encoding="utf-8-sig")))
H = list(rows[0].keys())
def col(no, part):
    h = [c for c in H if c.startswith(no + "_") and part in c]; assert len(h) == 1, (no, part, h); return h[0]
def num(s):
    s = (s or "").strip().replace("$", "")
    if s == "": return None
    if s == "<1": return 1.0
    if re.fullmatch(r"-?\d{1,3}(,\d{3})+(\.\d+)?", s): s = s.replace(",", "")
    elif re.fullmatch(r"\d*,\d+", s): s = s.replace(",", ".")
    try: return float(s)
    except ValueError: return None
has_comp = {(r["Fiscal Year"], r["Agency Abbreviation"]) for r in rows if r["Row Type"] in ("component", "no_component")}
def in_gov(r):  # 0.3 definition
    if r["Exclude From Component Sum"].strip().lower() == "yes" or r["Row Type"] == "second_entry": return False
    if r["Row Type"] in ("component", "no_component"): return True
    return r["Row Type"] == "agency_overall" and (r["Fiscal Year"], r["Agency Abbreviation"]) not in has_comp
G = [r for r in rows if in_gov(r)]
AO = [r for r in rows if r["Row Type"] == "agency_overall"]
def tot(rs, c, fy, cond=lambda r: True):
    return sum(num(r[c]) or 0 for r in rs if r["Fiscal Year"] == str(fy) and cond(r))
noDHS = lambda r: r["Agency Abbreviation"] != "DHS"; isDHS = lambda r: r["Agency Abbreviation"] == "DHS"
YRS = range(2008, 2026)
pct = lambda a, b: f"{a/b*100:.1f}%" if b else "NA"

YR = list(range(2008, 2026))
c02 = [c for c in H if c.startswith("02_") and "Total" not in c]; c05 = [c for c in H if c.startswith("05_")]
FG, PG, FD = col("02", "FullGrant"), col("02", "PartialGrant"), col("02", "FullExemptionDenial"); NR = col("02", "[NoRecords]")
E6, E7C = col("05", "[Ex. 6]"), col("05", "[Ex. 7(C)]")
T8, RV, PA, AR, PRO = col("08", "Total"), col("08", "Reversed"), col("08", "Partial"), col("07", "Received"), col("01", "Processed")
BLR, REC = col("26", "BackloggedRequest"), col("01", "Received")
AGK = lambda r: r["Agency Abbreviation"]; COK = lambda r: r["Agency Abbreviation"] + "/" + (r["Component"] or "AO")
def table(cols, base):
    """{(year, unit_key): sum}, for both agency and component keys"""
    out = {"ag": defaultdict(float), "co": defaultdict(float), "all": defaultdict(float)}
    for r in G:
        if not base(r): continue
        y = int(r["Fiscal Year"]); v = sum(num(r[c]) or 0 for c in cols)
        out["ag"][(y, AGK(r))] += v; out["co"][(y, COK(r))] += v; out["all"][y] += v
    return out
def loo(numc, denc, base, years=YR):
    """ratio per year: full, and min/max over leaving out any single agency or single component"""
    n, d = table(numc, base), table(denc, base); res = {}
    for y in years:
        full = n["all"][y] / d["all"][y] * 100; vals = [full]; worst = {}
        for lvl in ("ag", "co"):
            for (yy, k), dv in d[lvl].items():
                if yy != y: continue
                nv = n[lvl].get((yy, k), 0); D = d["all"][y] - dv
                if D > 0: vals.append((n["all"][y] - nv) / D * 100)
        res[y] = (full, min(vals), max(vals))
    return res
show = lambda name, res: print(name, " | ".join(f"{y}:{f:.1f}[{lo:.1f}–{hi:.1f}]" for y, (f, lo, hi) in res.items()))
noDN = lambda r: AGK(r) not in ("DHS", "NARA"); allr = lambda r: True; noD = lambda r: AGK(r) != "DHS"
IMM = {("DHS", "USCIS"), ("DHS", "CBP"), ("DHS", "ICE"), ("DOJ", "EOIR")}; ni = lambda r: (AGK(r), r["Component"]) not in IMM
def paired(numc, denc, base):
    """for each unit (agency or component), remove it in ALL years; return {unit: {year: ratio}} plus full"""
    n, d = table(numc, base), table(denc, base); out = {"Baseline": {y: n["all"][y] / d["all"][y] * 100 for y in YR}}
    for lvl in ("ag", "co"):
        units = {k for (_, k) in d[lvl]}
        for u in units:
            out[(lvl, u)] = {y: (n["all"][y] - n[lvl].get((y, u), 0)) / (d["all"][y] - d[lvl].get((y, u), 0)) * 100
                             for y in YR if d["all"][y] - d[lvl].get((y, u), 0) > 0}
    return out
def test(name, res, cond, desc):
    fails = [(u, {y: round(v, 1) for y, v in s.items() if y in (2008, 2017, 2019, 2020, 2023, 2024, 2025)}) for u, s in res.items() if not cond(s)]
    print(f"{name}：{desc} —— 去掉任一单位（{len(res)-1} 种）后{'全部成立' if not fails else f'有 {len(fails)} 种不成立'}")
    for f in fails[:5]: print("     不成立：", f)
    return fails

import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.figsize': (10,4.6), 'axes.spines.top':False,'axes.spines.right':False,'font.size':11})
def series(n,d,base=allr):
    a,b=table(n,base),table(d,base)
    return pd.Series({y:100*a['all'][y]/b['all'][y] for y in YR})
def chart(data,title,ylabel='Percent',ylim=None,vline=None,note=None):
    ax=pd.DataFrame(data).plot(marker='o',markersize=3)
    ax.set(title=title,xlabel='Fiscal year',ylabel=ylabel)
    if ylim is not None: ax.set_ylim(*ylim)
    if vline is not None: ax.axvline(vline,color='grey',lw=1,ls='--',alpha=.6)
    if note: ax.text(0,-0.2,note,transform=ax.transAxes,fontsize=8,color='dimgray')
    ax.set_xticks([2008,2011,2014,2017,2020,2023,2025])
    ax.tick_params(axis='x', labelrotation=0)
    ax.grid(alpha=.2)
    ax.legend(bbox_to_anchor=(1.02,1),loc='upper left',frameon=False)
    plt.tight_layout(); plt.show()
def check(s,expected,digits=1):
    assert list(s.round(digits))==expected,(list(s.round(digits)),expected)
def sensitivity(n,d,base):
    r=paired(n,d,base)
    df=pd.DataFrame({str(k):v for k,v in r.items()})
    print('Removal scenarios:',len(r)-1)
    return df
vba=lambda r:r['Agency Abbreviation']=='VA' and r['Component']=='VBA'
isD=lambda r:r['Agency Abbreviation']=='DHS'
OT=col('08','Other')

# Agency-weight decomposition used by the S1 walkthrough.
UN=COK
def bykey(y, c, cond=lambda r: True, key=UN):
    d = defaultdict(float)
    for r in G:
        if r["Fiscal Year"] == str(y) and cond(r): d[key(r)] += num(r[c]) or 0
    return d
FGc=FG
def ss(y0, y1):
    cond = noDN; n0, d0 = bykey(y0, FGc, cond, AGK), defaultdict(float); n1, d1 = bykey(y1, FGc, cond, AGK), defaultdict(float)
    for c in c02:
        for k, v in bykey(y0, c, cond, AGK).items(): d0[k] += v
        for k, v in bykey(y1, c, cond, AGK).items(): d1[k] += v
    D0, D1 = sum(d0.values()), sum(d1.values()); ks = [k for k in set(d0) & set(d1) if d0[k] and d1[k]]
    dr = {k: n1[k] / d1[k] - n0[k] / d0[k] for k in ks}
    w0 = sum(d0[k] / D0 * dr[k] for k in ks) * 100; w1 = sum(d1[k] / D1 * dr[k] for k in ks) * 100
    return round((sum(n1.values()) / D1 - sum(n0.values()) / D0) * 100, 1), round(w0, 1), round(w1, 1), round((w0 + w1) / 2, 1)



def backlog_revisions():
    """Outside the four specified units; numeric-only following-year replacement."""
    def totals(year,column):
        result=defaultdict(float)
        for row in G:
            if int(row['Fiscal Year'])==year and ni(row):
                value=num(row[column])
                if value is not None: result[COK(row)]+=value
        return result
    prior_backlog,prior_receipts=col('30','LastYear'),col('29','ItemsReceivedLastYear')
    changes=[]; records={}
    for year in YR:
        b,r=totals(year,BLR),totals(year,REC)
        nb=totals(year+1,prior_backlog) if year<2025 else {}
        nr=totals(year+1,prior_receipts) if year<2025 else {}
        changes.extend((year,k,b[k],nb[k]) for k in b.keys() & nb.keys() if abs(nb[k]-b[k])>=500)
        revised_b=sum(nb.get(k,v) for k,v in b.items())
        revised_r=sum(nr.get(k,v) for k,v in r.items())
        records[year]={'Original':100*sum(b.values())/sum(r.values()),'Revised backlog':100*revised_b/sum(r.values()),'Revised backlog and receipts':100*revised_b/revised_r}
    return pd.DataFrame(sorted(changes),columns=['Fiscal year','Unit','Original backlog','Following-year report']),pd.DataFrame.from_dict(records,orient='index')
