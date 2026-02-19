# Traffic Phase worked example (Toronto signals)

[← Back to Cases](cases.md)

This page is a **guided artifact-reading flow** for the Traffic Phase case:

`cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv`

Goal: show what HUF reveals that a typical “count rows / pivot table” workflow usually hides:
**a ranked, auditable “where the mass is” map**, **per-intersection signatures**, and **stable compression knobs (tau)**.

---

## 1) Run it

Windows PowerShell (from repo root):
```powershell
huf traffic --csv cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv --out out\traffic_phase
```

You should see something like:
- `active_set≈1312`
- `coherence_rows≈851`
- `discarded_global≈0.001`

---

## 2) What’s in the input

HUF expects a **Toronto traffic phase status** CSV with at least:
- `TCS` (signal controller / intersection id)
- `PHASE` (phase number)

For the shipped snapshot, the input contains:
- **66,912** rows (observations)
- **851** distinct `TCS` values (intersections)

---

## 3) What the adapter does (finite elements)

The Traffic Phase adapter compresses raw rows into **finite elements**:

- **Regime (group):** `TCS=<id>` (one regime per intersection)
- **Element (inside a regime):** `PHASE_BAND=<band>`

Where `PHASE_BAND` is a deliberate, human-readable grouping:

- `MajorEven(2,4,6,8)`
- `MinorOdd(1,3,5,7)`
- `Other(9-12)`

So each intersection becomes a 2–3 element “signature vector”:

```
TCS=<id>  ->  [MajorEven share, MinorOdd share, Other share]
```

Why this is useful:
- You can compare **intersections** on the same basis (a 3-number signature)
- You can rank intersections by **global mass** (how much of the dataset they explain)
- You can filter tiny within-intersection tails with `--tau-local`

---

## 4) The outputs (what to open first)

A run writes to `out/traffic_phase/`:

1) `artifact_1_coherence_map.csv`  
   **Intersection ranking** (one row per `TCS`) + discard reporting.

2) `artifact_2_active_set.csv`  
   **Retained elements** (per `TCS`, which bands survived tau, with local + global shares).

3) `artifact_3_trace_report.jsonl`  
   **Provenance chain** (item id → regime path → input fingerprint → method).

4) `artifact_4_error_budget.json`  
   Single number summary: **how much budget was discarded**.

5) `stability_packet.csv`  
   A small sweep showing how stable the result is as you change `tau`.

---

## 5) Global view: what dominates this dataset?

### 5.1 Phase-band totals (simple, but important)

In the shipped snapshot, the raw rows split like this:

| Phase band | Rows | Share |
|:--|--:|--:|
| MajorEven(2,4,6,8) | 54,818 | 0.8193 |
| MinorOdd(1,3,5,7) | 11,298 | 0.1688 |
| Other(9-12) | 796 | 0.0119 |

This baseline matters because it tells you what “normal” looks like globally.

### 5.2 The coherence map = “where the mass is” (by intersection)

Open:
- `out/traffic_phase/artifact_1_coherence_map.csv`

Top intersections by global retained share (shipped snapshot):

| Rank | Intersection (regime) | Global share |
|--:|:--|--:|
| 1 | TCS=619 | 0.005535 |
| 2 | TCS=175 | 0.002513 |
| 3 | TCS=25 | 0.002498 |
| 4 | TCS=137 | 0.002424 |
| 5 | TCS=440 | 0.002424 |
| 6 | TCS=529 | 0.002349 |
| 7 | TCS=320 | 0.002304 |
| 8 | TCS=70 | 0.002304 |
| 9 | TCS=750 | 0.002214 |
| 10 | TCS=948 | 0.002184 |

Interpretation:
- Each `TCS=<id>` gets a slice of the **global unity budget**.
- With **851** regimes, even the top one is only ~0.55% of the full dataset.
- This ranking gives you a fast “audit list”: if you only have time to look at a few intersections, start at the top.

---

## 6) Local signatures: what’s unusual at an intersection?

Open:
- `out/traffic_phase/artifact_2_active_set.csv`

Each row has:
- `rho_global_post` = global share after compression
- `rho_local_pre` / `rho_local_post` = within-intersection shares (before/after tau filtering)
- `value` = the raw count in that element

### 6.1 Example: a MinorOdd-dominant intersection

For `TCS=619` (top-ranked by global mass), the retained elements are:

| Element | Count | Local share |
|:--|--:|--:|
| MinorOdd(1,3,5,7) | 314 | 0.8486 |
| MajorEven(2,4,6,8) | 56 | 0.1514 |

That’s a strong signature: this intersection is **minor-phase heavy** compared to the global baseline (where MinorOdd is ~16.9%).

### 6.2 Example: an Other-heavy intersection

For `TCS=175`, the signature is split evenly between MajorEven and Other:

| Element | Count | Local share |
|:--|--:|--:|
| MajorEven(2,4,6,8) | 84 | 0.5000 |
| Other(9-12) | 84 | 0.5000 |

“Other(9-12)” is only ~1.2% globally, so 50% is a major outlier worth inspecting.

### 6.3 Outlier list (use this as a reading guide)

**Most MinorOdd-heavy intersections (top 10, shipped snapshot):**

| TCS | Total rows | MajorEven | MinorOdd | Other | MinorOdd share |
|--:|--:|--:|--:|--:|--:|
| 619 | 370 | 56 | 314 | 0 | 0.8486 |
| 142 | 68 | 20 | 48 | 0 | 0.7059 |
| 747 | 70 | 21 | 49 | 0 | 0.7000 |
| 318 | 64 | 20 | 44 | 0 | 0.6875 |
| 868 | 105 | 34 | 71 | 0 | 0.6762 |
| 875 | 78 | 26 | 52 | 0 | 0.6667 |
| 694 | 80 | 27 | 53 | 0 | 0.6625 |
| 746 | 40 | 14 | 26 | 0 | 0.6500 |
| 912 | 93 | 33 | 60 | 0 | 0.6452 |
| 751 | 111 | 40 | 71 | 0 | 0.6396 |

**Most Other-heavy intersections (top 10, shipped snapshot):**

| TCS | Total rows | MajorEven | MinorOdd | Other | Other share |
|--:|--:|--:|--:|--:|--:|
| 175 | 168 | 84 | 0 | 84 | 0.5000 |
| 841 | 126 | 71 | 10 | 45 | 0.3571 |
| 284 | 71 | 46 | 0 | 25 | 0.3521 |
| 282 | 92 | 51 | 12 | 29 | 0.3152 |
| 931 | 132 | 78 | 16 | 38 | 0.2879 |
| 303 | 115 | 66 | 16 | 33 | 0.2870 |
| 137 | 162 | 85 | 31 | 46 | 0.2840 |
| 896 | 67 | 43 | 5 | 19 | 0.2836 |
| 25 | 167 | 90 | 33 | 44 | 0.2635 |
| 948 | 146 | 74 | 34 | 38 | 0.2603 |

This is the kind of “needle list” most dashboards don’t give you for free.

---

## 7) What tau did here (and why it’s safe)

This case uses **local tau** (default `--tau-local 0.05`):
- inside each `TCS`, drop bands below 5% of that intersection’s mass
- renormalize the remainder to unity

For the shipped snapshot:
- input elements (TCS × band): **1338**
- retained elements: **1312**
- dropped elements: **26**
- global dropped budget: **0.0010013** (≈ **0.10%**) = **67 rows**

So tau is doing **surgical cleanup** (tiny tails), not rewriting the story.

If you want the stability proof, open:
- `out/traffic_phase/stability_packet.csv`

Example (shipped snapshot):

| tau | active_count | discarded_budget_global | jaccard_vs_baseline |
|--:|--:|--:|--:|
| 0.02 | 1335 | 0.000045 | 1.0000 |
| 0.03 | 1327 | 0.000269 | 0.9940 |
| 0.05 | 1312 | 0.001001 | 0.9828 |
| 0.07 | 1298 | 0.002077 | 0.9723 |
| 0.10 | 1268 | 0.005305 | 0.9498 |

Takeaway: you can raise/lower tau, and the **ordering stays stable**, while you trade off a little more discard for a cleaner signature.

---

## 8) Provenance: “show me the chain”

Open:
- `out/traffic_phase/artifact_3_trace_report.jsonl`

Each retained item includes:
- `item_id` (e.g., `TCS=619/band=MinorOdd(1,3,5,7)`) 
- `regime_path` (Global → TCS → band)
- `inputs_ref` (file fingerprint)
- `method_ref` (finite-element mapping statement)

This is how you keep the analysis auditable when you change thresholds.

---

## 9) Next steps

- Want a *diagnostic lens* on a specific status? Use the next case:
  👉 `huf traffic-anomaly ... --status "Green Termination"`

- Want to see more / less structure?
  - lower tau: `--tau-local 0.03`
  - raise tau: `--tau-local 0.07`

- Want to build your own “outlier report”?
  Use `artifact_2_active_set.csv` as the authoritative retained set, and join to your own intersection metadata.
