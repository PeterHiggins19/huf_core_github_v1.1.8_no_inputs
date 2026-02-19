\
# Start Here (Zero GitHub Knowledge)

This page is written for **Windows PowerShell** users who want copy/paste success.

> **Important:** HUF installs into a repo-local virtual environment at `.venv/`.
> To avoid Conda/PATH collisions, this guide uses **explicit venv paths**.

---

## Option 1: One-click starter (recommended)

From the repo root, run:

- **Windows:** `START_HERE_WINDOWS.bat`
- **Mac:** `START_HERE_MAC.command`
- **Linux:** `START_HERE_LINUX.sh`

These scripts bootstrap the environment and print the exact commands to run next.

---

## Option 2: Manual (copy/paste)

### 0) Open PowerShell in the repo root

If your folder is, for example, `D:\GitHub\HUF-Core\huf_core_github_v1.1.8_no_inputs`, then:

```powershell
cd D:\GitHub\HUF-Core\huf_core_github_v1.1.8_no_inputs
```

### 1) Create the repo venv + install dependencies

```powershell
python scripts/bootstrap.py
```

### 2) Fetch the small demo inputs (Markham + Toronto)

```powershell
.\.venv\Scripts\python scripts/fetch_data.py --markham --toronto --yes
```

### 3) Run the demos (always use the repo venv)

**Markham 2018 budget**

```powershell
.\.venv\Scripts\huf markham `
  --xlsx cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx `
  --out  out/markham2018 `
  --tau-global 0.005 `
  --tau-local  0.02
```

**Traffic Phase**

```powershell
.\.venv\Scripts\huf traffic `
  --csv cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv `
  --out out/traffic_phase `
  --tau-local 0.05
```

**Traffic Anomaly**

```powershell
.\.venv\Scripts\huf traffic-anomaly `
  --csv cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv `
  --out out/traffic_anomaly `
  --status "Green Termination" `
  --tau-global 0.0005
```

### 4) Planck (large file — guide only)

Print the Planck download guide:

```powershell
.\.venv\Scripts\python scripts/fetch_data.py --planck-guide
```

After you place the FITS at:

`cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits`

Run:

```powershell
.\.venv\Scripts\huf planck `
  --fits cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits `
  --out out/planck70 `
  --retained-target 0.97 `
  --nside-out 64
```

---

## Build / preview the docs locally

If you ever see:

> `mkdocs : The term 'mkdocs' is not recognized ...`

Use this (it bypasses PATH issues):

```powershell
.\.venv\Scripts\python -m mkdocs serve
```

Then open the local URL it prints.

---

## Mac/Linux convenience: `make` (optional)

If you have `make` installed, these are shortcuts:

```bash
make fetch-data
make planck-guide
```

Windows users should stick to the PowerShell blocks above.
