# Markham worked example (2018 budget)

[← Back to Cases](cases.md)

This page walks through a **full, reproducible** analysis using the bundled workbook:

`cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx`

Goal: show what HUF reveals that a normal “sum + chart” spreadsheet workflow usually hides:
**concentration**, **tail mass**, **stable regime structure**, and **cell-level provenance**.

---

## 1) Run it

Windows PowerShell (from repo root):
```powershell
huf markham --xlsx cases\markham2018\inputs\2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out\markham2018
```

You should see something like:
- `active_set=24`
- `coherence_rows=6`
- `discarded_global≈0.029`

---

## 2) What’s in the input

The adapter reads a simple **fund × account** block from the workbook (units: **k$**):
- accounts: rows 18–38
- funds: columns 1–6
- blanks / zeros are dropped

For the shipped workbook, HUF finds:
- **67** non-zero cells (elements)
- total value in the selected block: **456,172 k$** (≈ **$456.2M**)

---

## 3) The coherence map (fund-level regimes)

Open:
- `out/markham2018/artifact_1_coherence_map.csv`

This answers: **which funds dominate the retained budget**, and **how much tail mass got dropped**.

Totals (k$):

| Fund (regime)                                 |   Pre total (k$) |   Discarded (k$) |   Retained (k$) |   Share of retained |
|:----------------------------------------------|-----------------:|-----------------:|----------------:|--------------------:|
| Fund=Operating Fund                           |           218483 |            10874 |          207609 |              0.4687 |
| Fund=Waterworks/Stabilization Capital Reserve |           131634 |             1692 |          129942 |              0.2934 |
| Fund=Capital Development Fund                 |            77715 |                0 |           77715 |              0.1754 |
| Fund=Planning & Design                        |            10295 |              177 |           10118 |              0.0228 |
| Fund=Building Fee                             |             9957 |              200 |            9757 |              0.022  |
| Fund=Engineering                              |             8088 |              277 |            7811 |              0.0176 |

Interpretation:
- “Share of retained” sums to 1.0 (unity budget after compression).
- “Discarded (k$)” is what was below the global/local thresholds **inside that fund**.
- Here, the **Operating Fund** carries the biggest **within-fund tail** (≈ 5.0% of its pre-mass is discarded).

---

## 4) The active set (account-level winners)

Open:
- `out/markham2018/artifact_2_active_set.csv`

This answers: **which line-items explain most of the budget**, globally and within each fund.

Top items (k$):

|   Rank | Fund (regime)                            | Account                        |   Retained (k$) |   Share of retained |   Share within fund |
|-------:|:-----------------------------------------|:-------------------------------|----------------:|--------------------:|--------------------:|
|      1 | Operating Fund                           | Salaries & Benefits            |          131828 |              0.2976 |              0.635  |
|      2 | Waterworks/Stabilization Capital Reserve | Contracted Municipal Services  |          100989 |              0.228  |              0.7772 |
|      3 | Capital Development Fund                 | Capital Expenditures           |           77715 |              0.1754 |              1      |
|      4 | Operating Fund                           | Transfers to Reserves          |           28756 |              0.0649 |              0.1385 |
|      5 | Waterworks/Stabilization Capital Reserve | Transfers to Reserves          |           15281 |              0.0345 |              0.1176 |
|      6 | Operating Fund                           | Contracted Municipal Services  |           11167 |              0.0252 |              0.0538 |
|      7 | Operating Fund                           | Utilities                      |            9121 |              0.0206 |              0.0439 |
|      8 | Waterworks/Stabilization Capital Reserve | Salaries & Benefits            |            7729 |              0.0174 |              0.0595 |
|      9 | Planning & Design                        | Salaries & Benefits            |            6851 |              0.0155 |              0.6771 |
|     10 | Operating Fund                           | Maintenance & Repair           |            6848 |              0.0155 |              0.033  |
|     11 | Operating Fund                           | Contracts & Service Agreements |            6707 |              0.0151 |              0.0323 |
|     12 | Building Fee                             | Salaries & Benefits            |            6076 |              0.0137 |              0.6227 |

Two quick “hidden” facts this makes obvious:
- **top 2** line-items cover **52.6%** of the retained budget  
- **top 3** cover **70.1%**
- it takes only **11** line-items to cover **90%** of retained spend

That’s a *concentration story* you don’t get from a typical workbook view unless you go hunting.

---

## 5) Provenance: the trace report (the “why” chain)

Open:
- `out/markham2018/artifact_3_trace_report.jsonl`

Each retained item includes the workbook pointer it came from (sheet + cell), so you can audit
the pipeline end-to-end.

Example (top 5):

|   Rank | Fund (regime)                            | Account                       |   Retained (k$) |   Share of retained | Workbook cell   |
|-------:|:-----------------------------------------|:------------------------------|----------------:|--------------------:|:----------------|
|      1 | Operating Fund                           | Salaries & Benefits           |          131828 |              0.2976 | B19             |
|      2 | Waterworks/Stabilization Capital Reserve | Contracted Municipal Services |          100989 |              0.228  | G34             |
|      3 | Capital Development Fund                 | Capital Expenditures          |           77715 |              0.1754 | C37             |
|      4 | Operating Fund                           | Transfers to Reserves         |           28756 |              0.0649 | B38             |
|      5 | Waterworks/Stabilization Capital Reserve | Transfers to Reserves         |           15281 |              0.0345 | G38             |

If something looks wrong, you can jump straight to those cells in Excel.

---

## 6) Stability: how sensitive is the result?

Open:
- `out/markham2018/stability_packet.csv`

This runs the same case across a few tau values and reports how much the answer changes.

|   tau_global |   active_count |   discarded_frac |   near_tau_count |   spearman_vs_base |   jaccard_vs_base |
|-------------:|---------------:|-----------------:|-----------------:|-------------------:|------------------:|
|       0.0025 |             30 |           0.01   |                2 |                  1 |             1     |
|       0.005  |             24 |           0.029  |                4 |                  1 |             0.8   |
|       0.0075 |             20 |           0.0522 |                1 |                  1 |             0.667 |
|       0.01   |             20 |           0.0522 |                0 |                  1 |             0.667 |
|       0.015  |             20 |           0.0522 |                3 |                  1 |             0.667 |

How to read it:
- `discarded_frac` ↑ means more aggressive pruning.
- `jaccard_vs_base` close to 1.0 means “mostly the same active set”.
- `near_tau_count` high means lots of elements hover around the cutoff (more sensitivity).

---

## 7) “So what did HUF reveal?”

Here’s the story for this workbook:

1) **Budget mass is extremely concentrated.**  
   A small number of accounts explain most of the retained spend.

2) **Different funds have different tail behavior.**  
   The Operating Fund sheds the most tail (small accounts below thresholds) while the Capital Development Fund is essentially a single dominant line item.

3) **Everything is auditable.**  
   The trace report points back to the original spreadsheet cells, so the compression is inspectable, not a black box.

---

## 8) Explore further (copy/paste)

```python
import pandas as pd

coh = pd.read_csv("out/markham2018/artifact_1_coherence_map.csv")
active = pd.read_csv("out/markham2018/artifact_2_active_set.csv").sort_values("rank")

# Which funds dominate?
print(coh[["regime_id","rho_global_post","rho_discarded_pre"]].sort_values("rho_global_post", ascending=False))

# How many items cover 90%?
active["cum"] = active["rho_global_post"].cumsum()
print(active.loc[active["cum"] >= 0.90, ["rank","item_id","cum"]].head(1))

# Top 10 line-items (global + within-fund shares)
print(active.head(10)[["rank","regime_id","item_id","value","rho_global_post","rho_local_post"]])
```

---

## Links

- Input workbook: `cases/markham2018/inputs/...xlsx` (bundled)
- Case folder (GitHub): https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs/tree/main/cases/markham2018
