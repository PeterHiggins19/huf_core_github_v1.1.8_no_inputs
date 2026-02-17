import pandas as pd
from pathlib import Path

from huf_core.adapters import markham_2018_fund_expenditure_elements
from huf_core import HUFCore, HUFConfig


def test_markham_adapter_smoke(tmp_path: Path):
    """Create a tiny Markham-like workbook and ensure the adapter + cycle runs."""

    # Build a sheet that matches the adapter's expectations:
    # row 0 has fund names in columns 1..6, EXPENDITURES block starts at row 18.
    raw = pd.DataFrame([[None]*8 for _ in range(45)])
    funds = ["Operating", "Waterworks", "Wastewater", "Planning", "Engineering", "Building Fee"]
    for i, name in enumerate(funds, start=1):
        raw.iat[0, i] = name

    # Put two expenditure lines at rows 18 and 19.
    raw.iat[18, 0] = "Salaries"
    raw.iat[19, 0] = "Contracted"
    # Values in k$ across a couple funds
    raw.iat[18, 1] = 100
    raw.iat[18, 2] = 50
    raw.iat[19, 1] = 80
    raw.iat[19, 2] = 20

    xlsx = tmp_path / "markham_like.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
        raw.to_excel(w, index=False, header=False)

    elements, meta = markham_2018_fund_expenditure_elements(xlsx)
    assert meta["elements"] > 0
    assert elements["regime_id"].nunique() >= 1

    core = HUFCore(elements, dataset_id=meta["dataset_id"])
    art = core.cycle(HUFConfig(budget_type="mass", exclusion="global", tau=0.0))
    assert "active_set" in art
    assert len(art["active_set"]) == len(elements)
