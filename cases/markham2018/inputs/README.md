# Inputs (Markham 2018)

This case reads the Markham 2018 *fund × account* expenditure workbook.

In this repo snapshot, a small **sample** workbook is already present at:

- `cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx`

If you want the original City of Markham workbook instead, see `DATA_SOURCES.md` (repo root) for download links and replace the file at the same path.

## Run
From the repo root:

```bash
huf markham \
  --xlsx cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx \
  --out out/markham2018
```

Optional thresholds:

```bash
huf markham --xlsx cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out/markham2018 --tau-global 0.005 --tau-local 0.02
```
