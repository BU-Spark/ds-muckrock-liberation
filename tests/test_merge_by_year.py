import importlib.util
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "fa26" / "dataset" / "raw_agency_level"
API_FILLS = ROOT / "fa26" / "dataset" / "agency_level" / "api_fills"

spec = importlib.util.spec_from_file_location("merge_by_year", ROOT / "fa26" / "scripts" / "merge_by_year.py")
merge_by_year = importlib.util.module_from_spec(spec)
spec.loader.exec_module(merge_by_year)


def test_gap_fills_are_the_13_documented_tables():
    assert sum(len(v) for v in merge_by_year.GAP_FILLS.values()) == 13


@pytest.mark.parametrize("year", sorted(merge_by_year.GAP_FILLS))
def test_gap_fill_files_exist_for_their_year(year):
    files = merge_by_year.gap_fill_files(RAW, year)
    assert [f.name[:2] for f in files] == merge_by_year.GAP_FILLS[year]
    for f in files:
        fy = pd.read_csv(f, dtype=str, keep_default_na=False)["Fiscal Year"]
        assert (pd.to_numeric(fy, errors="coerce") == year).all(), f.name


def test_no_gap_fills_for_other_years():
    assert merge_by_year.gap_fill_files(RAW, 2024) == []


def test_missing_gap_fill_file_raises(tmp_path):
    (tmp_path / "2013").mkdir()
    with pytest.raises(FileNotFoundError):
        merge_by_year.gap_fill_files(tmp_path, 2013)


def test_api_fill_files_exist():
    assert (API_FILLS / "agency_years_from_api.csv").is_file()
    assert (API_FILLS / "exemption_statutes_from_api.csv").is_file()
