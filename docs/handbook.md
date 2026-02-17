<!-- Auto-converted from HUF_Handbook_v1.1.docx. Figures/line-art images are omitted in this markdown export; see the DOCX/PDF or the artifacts pack for visuals. -->

# HUF Handbook

## Figures (from reference runs)

**Planck (70 GHz)**
- Coherence map by face (coarse nside=64):  
  ![Planck coherence map faces](assets/coherence_map_faces.png)
- Active count vs threshold (stability sweep):  
  ![Planck stability active count](assets/stability_active_count.png)

**Traffic**
- Phase activity top contributors:  
  ![Traffic top contributors](assets/active_top15.png)
- Anomaly locus top contributors:  
  ![Traffic anomaly top contributors](assets/anomaly_top15.png)

**Markham**
- Fund weights (global regime bars):  
  ![Markham fund weights](assets/markham_fund_weights.png)
- Stability: retained budget vs threshold:  
  ![Markham stability budget](assets/markham_stability_budget.png)
- Stability: active count vs threshold:  
  ![Markham stability count](assets/markham_stability_count.png)

---

Unity‑Budgeted Hierarchies for Auditable Reduction
Version 1.1 (February 2026)
Core + verified reference runs (Planck + Markham + Traffic)

**Data policy:** upstream inputs (Planck FITS / Markham workbook / Toronto traffic CSV) are **not bundled** to keep downloads small. Download them from public sources and place them under `cases/*/inputs/` as documented in `DATA_SOURCES.md`.

# Contents
1. HUF in One Page (The Contract)
2. Core Definitions
3. The Locked Cycle
4. Artifact Standards
5. Stability Packet
6. Hazards, Pitfalls, and Incompatible Systems
7. Reference Library
8. Case Study A — Planck LFI 70 GHz Sky Map (Energy Budget)
9. Case Study B — Markham 2018 City Budget (Mass Budget)
10. Case Study C — Traffic Signals (Phase Distribution + Anomaly Dominance)
11. How to Add a New Domain Adapter
12. Glossary and Index

# 1. HUF in One Page (The Contract)
HUF compresses a system while preserving a declared unity budget and emitting audit artifacts. If an artifact is missing, the run is invalid.
# 2. Core Definitions
Finite element: smallest verifiable unit that produces a contribution value.
Regime: named grouping of finite elements (or sub‑regimes) that share context; regimes can be nested.
Unity budget: conserved total influence; sums to 1.0 globally (and locally after normalization).
Traceability: every retained contribution must map back to finite elements and source data coordinates.
Budget types (choose exactly one per run):
# 3. The Locked Cycle
Locked cycle: Normalize → Propagate → Aggregate → Exclude → Renormalize. The only freedom is how you define elements, regimes, propagation maps, and thresholds.
[Normalize] → [Propagate] → [Aggregate] → [Exclude] → [Renormalize]
# 4. Artifact Standards
# 5. Stability Packet
Run ≥ 5 thresholds τ and record: retained budget, active set size, turnover (Jaccard), and rank stability (Spearman).
If stability fails, redesign elements/regimes before publishing results.
# 6. Hazards, Pitfalls, and Incompatible Systems
HUF preserves what you declare. Wrong budget ⇒ wrong answers, perfectly audited.
If you can’t audit finite elements, don’t run HUF.
Propagation must be explicit and conservation‑checked (no black boxes).
Signed cancellation needs an extension (not covered here).
Do not compare runs across different budgets or different element definitions.
# 7. Reference Library
A reference Python library (zip) accompanies this handbook. It includes CLI commands, adapters for these case studies, and tests.
CLI (inputs not bundled; see `DATA_SOURCES.md`):

  # fetch Markham + Toronto inputs (Planck is manual)
  make fetch-data
  # or: python scripts/fetch_data.py --markham --toronto

  huf planck --fits cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits --out out/planck70 --retained-target 0.97 --nside-out 64
  huf markham --xlsx cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out/markham2018 --tau-global 0.005 --tau-local 0.02
  huf traffic --csv cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv --out out/traffic_phase --tau-local 0.05
  huf traffic-anomaly --csv cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv --out out/traffic_anomaly --status "Green Termination" --tau-global 0.005

# 8. Case Study A — Planck LFI 70 GHz Sky Map (Energy Budget)
Real HEALPix Planck LFI 70 GHz map. Budget is energy in pixel basis; discarded budget equals reconstruction error (Parseval).
Coherence map:

Stability sweep:

## Top retained regimes:

# 9. Case Study B — Markham 2018 City Budget (Mass Budget)
Public city expenditures. Budget is spend share; discarded budget is the explicit loss ledger.
Fund weights:

Stability sweep:

## Top retained elements:

# 10. Case Study C — Traffic Signals (Phase Distribution + Anomaly Dominance)
Two runs: (1) phase activity distribution; (2) anomaly dominance. For anomaly dominance: finite element = TCS × PHASE × PHASE_STATUS_TEXT (± PHASE_CALL_TEXT). Budget = event share or severity‑weighted share (weights must be declared).
Phase distribution top-15 contributions:

Anomaly dominance top-15 contributions:


# 11. How to Add a New Domain Adapter
Declare budget type and units.
Define finite elements with audit coordinates.
Define regimes (explainable groupings).
Define propagation map(s) with conservation checks.
Choose thresholds and generate a stability packet.
Emit artifacts and treat them as deliverables.
# 12. Glossary and Index
## Glossary
## Index (term → section)
Active set — 4, 8–10
Budget type — 2, 8–10
Coherence map — 4, 8–10
Contract — 1
Discarded budget — 4, 8–10
Finite element — 2, 8–10
Hazards — 6
Markham — 9
Planck — 8
Propagation — 3
Regime — 2, 8–10
Stability packet — 5, 8–9
Trace report — 4, 8–10
Traffic signals — 10
Unity — 1–6

## Tables (from DOCX)


### Table 1

| Non‑Negotiable | Pass/Fail Test | Why it exists |
| --- | --- | --- |
| Budget declaration | Budget type declared once (mass/weight OR energy/power). Non‑negative unless using a signed extension. | Prevents mixing incompatible meanings. |
| Unity preservation | Global unity holds after every operation. Regime unity holds after normalization/exclusion. | Prevents silent drift. |
| Locked cycle | Normalize → Propagate → Aggregate → Exclude → Renormalize. | Prevents ad‑hoc steps and post‑hoc fixes. |
| Artifact emission | Coherence map, active set, trace report, error/budget report emitted every cycle. | Turns reduction into an auditable product. |
| Repro stamp | Inputs hash + config + timestamp recorded. | Enables repeat runs and external review. |

### Table 2

| Budget Type | Unity Meaning | Typical Domains |
| --- | --- | --- |
| Mass/Weight | ∑ρ = 1 over non‑negative contributions. | Spending, counts, event shares, portfolio weights. |
| Energy/Power | ∑|c|² = 1 (orthonormal basis) or normalized energy. | Harmonics, spherical modes, HEALPix fields. |

### Table 3

| Normalize | Propagate | Aggregate | Exclude |
| --- | --- | --- | --- |
| Rescale ρ to satisfy unity. | Move budget through an explicit, conservation‑checked map. | Merge near‑duplicate contributors; preserve trace mapping. | Drop below threshold; ledger discarded budget; renormalize. |

### Table 4

| Artifact | Minimum | Use |
| --- | --- | --- |
| Coherence map | Unity bars + regime weights + drift checks. | Dominance summary. |
| Active set | Retained items with shares + thresholds. | Compressed system. |
| Trace report | Back‑mapping to finite elements + source coordinates. | Audit + root cause. |
| Error/Budget report | Discarded budget + error metric. | Loss ledger. |

### Table 5

| Item | Value |
| --- | --- |
| Input | 12,582,912 pixels (nside=1024, NESTED) |
| Coarse regime | 49,152 coarse pixels (nside=64) |
| Finite element | Group of 256 fine pixels → coarse pixel energy |
| Discarded budget | 0.030000 |
| RMSE | 7.6942e-05 |
| Effective τ (from sweep) | 1.663e-06 |
| Active set | 18,198 regimes retained |

### Table 6

| item_id | rho_global_pre | rho_global_post | trace_path (short) |
| --- | --- | --- | --- |
| face04/pix1636 | 0.104598 | 0.107833 | face04 / pix1636 / fine[4613120:4613375] |
| face10/pix3738 | 0.0585659 | 0.0603772 | face10 / pix3738 / fine[11442688:11442943] |
| face04/pix2407 | 0.0369717 | 0.0381151 | face04 / pix2407 / fine[4810496:4810751] |
| face06/pix0894 | 0.0350825 | 0.0361675 | face06 / pix0894 / fine[6520320:6520575] |
| face04/pix1706 | 0.0329661 | 0.0339856 | face04 / pix1706 / fine[4631040:4631295] |
| face04/pix2412 | 0.020599 | 0.021236 | face04 / pix2412 / fine[4811776:4812031] |
| face07/pix1620 | 0.0189408 | 0.0195266 | face07 / pix1620 / fine[7754752:7755007] |
| face07/pix1635 | 0.0186632 | 0.0192404 | face07 / pix1635 / fine[7758592:7758847] |

### Table 7

| Item | Value |
| --- | --- |
| Input | 2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx (EXPENDITURES) |
| Finite element | Fund × Account line item |
| Regime | Fund |
| Thresholds | global ≥ 0.005 OR within‑fund ≥ 0.02 |
| Elements | 67 total → 24 retained |
| Discarded budget | 0.028980 |
| Total spend | 456,172 k$ |

### Table 8

| Fund | Account | Amount (k$) | rho_global_raw | keep_reason |
| --- | --- | --- | --- | --- |
| Operating Fund | Salaries & Benefits | 131,828 | 0.2890 | global |
| Waterworks/Stabilization Capital Reserve | Contracted Municipal Services | 100,989 | 0.2214 | global |
| Capital Development Fund | Capital Expenditures | 77,715 | 0.1704 | global |
| Operating Fund | Transfers to Reserves | 28,756 | 0.0630 | global |
| Waterworks/Stabilization Capital Reserve | Transfers to Reserves | 15,281 | 0.0335 | global |
| Operating Fund | Contracted Municipal Services | 11,167 | 0.0245 | global |
| Operating Fund | Utilities | 9,121 | 0.0200 | global |
| Waterworks/Stabilization Capital Reserve | Salaries & Benefits | 7,729 | 0.0169 | global |
| Planning & Design | Salaries & Benefits | 6,851 | 0.0150 | global |
| Operating Fund | Maintenance & Repair | 6,848 | 0.0150 | global |

### Table 9

| Run | Budget | Discarded budget |
| --- | --- | --- |
| Phase activity distribution | Event share | 0.0010 |
| Anomaly dominance (Green Termination) | Event share on subset | 0.6741 |

### Table 10

| Term | Definition |
| --- | --- |
| Finite element | Smallest verifiable unit producing a contribution value. |
| Regime | Named grouping of elements sharing context. |
| Unity budget | Conserved influence total (equals 1). |
| Discarded budget | Pruned mass/energy before renormalization. |
| Coherence map | Unity bars + regime weights summary. |
| Active set | Retained elements after exclusion. |
| Trace report | Back‑mapping from retained items to sources. |
| Stability packet | Threshold sweep quantifying brittleness. |