"""读取部门级 FOIA 数据（component_v3）的共用工具。

所有表都以字符串读入（keep_default_na=False），避免 pandas 把 "N/A"、"<1" 这类
有含义的原文悄悄变成 NaN。需要算数时再用 to_num 显式转换。

    import foia_component as fc
    df = fc.load("ProcessedRequestSection", ROOT)           # 分析层
    df = fc.numeric(df)                                      # 数据列转成数字
    parts = fc.for_component_sum(df)                         # 可以加总的部门行
"""
import os
import re

import numpy as np
import pandas as pd

ID_COLS = ["Agency", "Agency Abbreviation", "Component", "Component Name", "Fiscal Year",
           "Source File", "Row Type", "Duplicate Of Overall", "Data Item ID", "Org Ref ID", "Assoc Index"]
# 分析层额外加的列
ANALYSIS_COLS = ["Agency Std", "FY", "Row Level", "Row Key", "Exclude From Component Sum", "Exclude Reason"]
META_COLS = ID_COLS + ANALYSIS_COLS

MISSING = {"", "N/A", "NA", "n/a", "N/a"}


def load(section, root, layer="analysis"):
    """读一张表。layer = "analysis"（默认）或 "raw"。"""
    return pd.read_csv(os.path.join(root, layer, f"{section}.csv"), dtype=str, keep_default_na=False)


def value_status(s):
    """把一列原文分成 blank / na / lt1 / zero / number / text 六类，用来区分"0"和"没填"。"""
    s = s.astype(str).str.strip()
    num = pd.to_numeric(s.str.replace(",", "", regex=False), errors="coerce")
    out = pd.Series("text", index=s.index)
    out[num.notna()] = "number"
    out[num == 0] = "zero"
    out[s == "<1"] = "lt1"
    out[s.isin(MISSING - {""})] = "na"
    out[s == ""] = "blank"
    return out


def to_num(s, lt1=np.nan):
    """原文 → 数字。空白、N/A、非数字文本 → NaN；"<1" → lt1（默认 NaN，算中位数时可以传 0.5）。"""
    s = s.astype(str).str.strip()
    out = pd.to_numeric(s.str.replace(",", "", regex=False), errors="coerce")
    out[s == "<1"] = lt1
    return out


def data_cols(df):
    return [c for c in df.columns if c not in META_COLS]


def numeric(df, cols=None, lt1=np.nan):
    """返回副本，数据列（或指定列）转成数字；日期、文本列原样保留。"""
    df = df.copy()
    for c in cols or data_cols(df):
        if column_kind(c) not in ("date", "text"):
            df[c] = to_num(df[c], lt1)
    return df


def column_kind(col):
    """按 XML 字段名判断列的类型。"""
    col = col.split("[")[0]  # 代码列（如 OtherDenialReasonQuantity[…]）只看方括号前面
    if col.endswith("Date"):
        return "date"
    if col.endswith("Text"):
        return "text"
    if col.endswith("DaysValue") or col.endswith("PendingDaysQuantity"):
        return "days"  # AdjudicationWithinTenDaysQuantity 是件数，不算
    if col.endswith("Percent"):
        return "percent"
    if col.endswith("Amount"):
        return "money"
    if "FullTime" in col:
        return "fte"
    if col.endswith("Quantity") or "Quantity[" in col:
        return "count"
    return "text"


def summable(col):
    """部门之间能不能直接相加：件数、金额、FTE 可以；天数（中位数/平均数/最长）、百分比不行。"""
    return column_kind(col) in ("count", "money", "fte")


def for_component_sum(df):
    """用于"部门加总"的行：具名部门 + 未归属，去掉已知的重复合计（如 DOC FY2025）。"""
    return df[df["Row Level"].isin(["component", "unattributed"]) & (df["Exclude From Component Sum"] != "yes")]


def overall(df):
    return df[df["Row Level"] == "agency_overall"]


def named(df):
    """具名部门（不含未归属、不含已知重复合计）。"""
    return df[(df["Row Level"] == "component") & (df["Exclude From Component Sum"] != "yes")]


def unique_key(df, key=("Agency Std", "FY", "Component")):
    """只保留键唯一的行，用于跨表一对一连接（Exemption 3 这类多行表不要用）。"""
    key = list(key)
    return df[~df.duplicated(key, keep=False)]
