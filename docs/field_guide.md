# HUF Field Guide — Architecture, Artifacts, and Domain Map

> **Higgins Unity Framework (HUF)** is a normalization-invariant **audit layer** for hierarchical mixtures (regimes/tenants/sources).  
> It grew out of wavefront-control work in multi-driver acoustic systems and later proved useful as a general-purpose way to **track where the mass went** across hierarchies.
>
> **Scope note:** This page is *field-guide level*. It emphasizes intuition, reproducible artifacts, and safe claims.  
> Mathematical analogies (entropy, wavefronts, sheaves, etc.) are presented as **interpretive** unless explicitly proven in a dedicated proof note.

!!! note "Ethics disclosure (short)"
    This page was AI-assisted for drafting/editing and then reviewed/curated by the author. Formal claims are stated conservatively and should be reproducible via code and artifacts in the repository.

---

## Contents

1. [What HUF does in one paragraph](#1-what-huf-does-in-one-paragraph)  
2. [Origin story: wavefront control → audit layers](#2-origin-story-wavefront-control--audit-layers)  
3. [Core architecture (conceptual pipeline)](#3-core-architecture-conceptual-pipeline)  
4. [Artifacts (what every run emits)](#4-artifacts-what-every-run-emits)  
5. [Mathematical core (minimal, safe)](#5-mathematical-core-minimal-safe)  
6. [The PROOF line](#6-the-proof-line)  
7. [Domain map (where HUF applies)](#7-domain-map-where-huf-applies)  
8. [Stability and convergence (practical)](#8-stability-and-convergence-practical)  
9. [HUF vs other approaches](#9-huf-vs-other-approaches)  
10. [Quick start](#10-quick-start)  
11. [Glossary](#11-glossary)

---

## 1. What HUF does in one paragraph

HUF takes any **hierarchical mixture** — budgets, logs, retrieval outputs, channel mixes, multi-tenant pipelines — and turns it into a **coherence-audited, mass-accounted, provenance-tracked view**. Items (records, documents, events) are grouped into **regimes** (categories/tenants/channels/sources). HUF computes how much normalized **mass** each regime carries, applies retention policies (if requested), and emits review-ready artifacts so you can answer:

- *Which regimes dominate?*  
- *How concentrated is the mix?*  
- *What changed between baseline and exception views?*  
- *Why did each item stay or get discarded?*  

The “counter‑intuitive” part is intentional: **discarding tail mass and then re-normalizing makes the retained portion look stronger**. HUF makes that effect explicit (and auditable), so humans don’t misread it as “magic.”

---

## 2. Origin story: wavefront control → audit layers

HUF wasn’t invented as “a library feature.” It emerged from experimental work in **multi-driver wavefront control**, where many drivers must combine into a coherent field without any one driver silently dominating the energy budget.

The transferable pattern was:

- normalize contributions across many components
- detect drift (components leaving their expected role)
- damp coupling so corrections don’t oscillate or amplify
- keep a trace so every adjustment is explainable after the fact

!!! tip "Interpretive bridge (safe framing)"
    “Embedding drift” in AI pipelines *resembles* phase decoherence in wave systems as a **control pattern**: both are multi-component systems where small misalignment can dominate outcomes.  
    This is an analogy that motivates the architecture; it is not a claim that the underlying physics or domains are mathematically identical.

---

## 3. Core architecture (conceptual pipeline)

```
Input data (any scored items + regime labels)
         │
         ▼
┌─────────────────────────────────────────────┐
│                 REGIMES                     │
│  Each tenant/source/category/channel = r    │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│              MASS ACCOUNTING                │
│  w_r = Σ scores in regime r                 │
│  p_r = w_r / Σ w_r                          │
│  (p is a simplex distribution over regimes) │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│        RETENTION / THRESHOLDING (optional)  │
│  keep most-mass items; log discards         │
│  re-normalize retained mass (explicitly)    │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│          COHERENCE + CONCENTRATION          │
│  dominance, items_to_cover_90pct, drift     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│               ARTIFACTS OUT                 │
│  coherence map, active set, trace, budget   │
└─────────────────────────────────────────────┘
```

**Key properties HUF enforces (as an audit layer):**
- unity accounting on the chosen distribution (regime mass sums to 1 after normalization)
- no silent mass loss (discards are logged, not hidden)
- per-item traceability (“why it stayed” / “why it was removed”)

---

## 4. Artifacts (what every run emits)

HUF is *artifact-first*: the point is to create reviewable outputs you can diff in PRs, attach to emails, or hand to auditors.

### `artifact_1_coherence_map.csv` — where the mass is
Ranked regimes by normalized mass share (e.g., `rho_global_post`). Primary signal for dominance and concentration.

Typical fields (names may vary slightly by run):
- `regime`
- `rho_global_pre`, `rho_global_post`
- `rank`
- optional stability/coherence fields if enabled (e.g., `C_r`, `alpha_star`)

### `artifact_2_active_set.csv` — what was retained
All retained items and their shares (global + local) plus regime labels. This is the “what you kept” ledger.

Typical fields:
- `item_id`
- `regime`
- `rho_local`, `rho_global`
- `retained`
- optional provenance columns (source path, query id, rank, etc.)

### `artifact_3_trace_report.jsonl` — why it stayed
Append-only trace: one JSON record per item (and sometimes per step). This is what makes HUF “audit-friendly.”

Example shape:
```json
{
  "item_id": "proj_roads_phase2",
  "regime": "Roads",
  "rho_normalized": 0.038,
  "retained": true,
  "reason": "above_threshold",
  "drift_flag": false
}
```

### `artifact_4_error_budget.json` — what was discarded (accounting)
A compact summary of discarded mass by reason and by regime, so “loss” is visible and explainable.

!!! note "Why 4 artifacts?"
    Early writeups sometimes said “three artifacts.” In practice, the **error budget** is the piece that keeps the story honest: it prevents “discarded mass” from disappearing silently.

---

## 5. Mathematical core (minimal, safe)

This section gives a stable, conservative core that matches what HUF is actually doing conceptually.

### Regimes and mass
Each item \(i\) has:
- regime label \(r(i)\)
- nonnegative score \(s(i)\) (after any preprocessing)

Regime mass:
\[
w_r = \sum_{i: r(i)=r} s(i)
\]

Normalized regime distribution (simplex point):
\[
p_r = \frac{w_r}{\sum_{r'} w_{r'}}
\]

Everything “audit-grade” comes from being explicit about \(p\) and how it changes under retention.

### Retention and renormalization (the counter-intuitive part)
If you keep a subset \(K\) of items and discard the rest, retained mass is:
\[
m_K = \sum_{i \in K} s(i)
\]
and the retained distribution is re-normalized by dividing by \(m_K\).

So retained shares increase by a factor \(1/m_K\) (if \(m_K < 1\) after normalization), which is why “loss makes retained stronger” appears.

### Optional geometry (interpretive, but useful)
Many workflows embed \(p\) into a geometry for stability plots. A common embedding is:
\[
\phi(p) = (\sqrt{p_1}, \dots, \sqrt{p_n})
\]
This can be used to define distances between mixtures, but the geometry is a **tool**, not the core claim.

---

## 6. The PROOF line

The quickest “does this do anything?” signal is:

```
PROOF: items_to_cover_90pct 37 -> 12
```

**Meaning:** sort items by mass share; count the minimum number needed to cover 90% of total mass.  
Lower count → more concentrated mix (fewer items dominate).

!!! tip "How to explain it to a human"
    Baseline view: “Where is the mass across everything?”  
    Exception view: “Where is the mass given only the exceptions?”  
    Re-normalization makes the exception story *sharper*, so concentration becomes visible instead of blurred.

---

## 7. Domain map (where HUF applies)

HUF is domain-agnostic in the core. Domain specifics show up in:
- what a “regime” means
- what scores represent
- what retention/penalty policies you choose
- what thresholds you consider “drift”

### Civic: budgets / allocation tables
- regimes: categories, departments, programs
- items: projects/line items
- audits: dominance, “approved vs actual” drift, missing categories

### Civic: traffic signal telemetry
- regimes: corridors, zones, controller types
- items: intersections/events
- audits: exception-only concentration, drift flags, explainable discard reasons

### Science: instrument channels / data products (template)
- regimes: channels, sensors, bands, pipelines
- items: bins/pixels/records
- audits: stability under resampling, dominance shift under filtering

!!! caution "Scientific claims"
    HUF can be used as a *template* for scientific audits. Any claim about a specific dataset’s results should be backed by a reproducible run and cited measurements.

### RAG / vector databases / multi-tenant retrieval
- regimes: namespaces, sources, tenants, collections
- items: retrieved docs/chunks
- audits: “one source dominates”, “exception-only becomes brittle”, “eval scores are misleading under collapse”

---

## 8. Stability and convergence (practical)

Instead of claiming universal convergence theorems, treat stability as an **engineering contract**:

- run the same evaluation under small perturbations (τ sweeps, score rescaling, small data shifts)
- check whether regime dominance and concentration metrics remain consistent
- inspect the error budget to ensure “improvements” aren’t just aggressive discarding

If you do implement an explicit objective (coherence + variance + penalty), document it as an **implementation choice** and keep any “convexity / proof” claims in a dedicated proof note that reviewers can check.

---

## 9. HUF vs other approaches

| Approach | Mass accounting | Traceability | Concentration metrics | Multi-regime first-class |
|---|---:|---:|---:|---:|
| **HUF (audit layer)** | ✓ | ✓ | ✓ | ✓ |
| Plain normalization | ✓ | ✗ | partial | partial |
| Ad-hoc monitoring dashboards | partial | varies | varies | varies |
| Domain-specific reconciliation tools | varies | partial | partial | ✗ |

Key distinction: many systems ensure “sums to 1.” HUF ensures:
- **what sums to 1 is explicit**
- **what was discarded is logged**
- **dominance/concentration is surfaced**
- **every retained item is explainable**

---

## 10. Quick start

Windows (PowerShell):
```powershell
python scripts/bootstrap.py
.\.venv\Scripts\python scripts/fetch_data.py --toronto --yes
.\.venv\Scripts\python scripts/run_long_tail_demo.py --status "Green Termination"
```

macOS / Linux:
```bash
python scripts/bootstrap.py
.venv/bin/python scripts/fetch_data.py --toronto --yes
.venv/bin/python scripts/run_long_tail_demo.py --status "Green Termination"
```

Inspect any output folder:
```powershell
.\.venv\Scripts\python scripts/inspect_huf_artifacts.py --out out/traffic_anomaly_demo
```

Docs (local):
```powershell
.\.venv\Scripts\python -m mkdocs serve
```

---

## 11. Glossary

| Term | Meaning |
|---|---|
| **Regime** | Category/tenant/namespace/channel/source grouping |
| **Mass / ρ** | Normalized share assigned to an item or regime |
| **Coherence map** | Ranked regimes by mass (dominance view) |
| **Active set** | Retained items above policy threshold |
| **Trace report** | JSONL “why it stayed” provenance log |
| **Error budget** | Accounting of discarded mass by reason/regime |
| **items_to_cover_90pct** | Concentration proxy (lower = more concentrated) |
| **Drift** | A regime or item shifting beyond your declared threshold |

---

*Docs: https://peterhiggins19.github.io/huf_core/ · Repo: https://github.com/PeterHiggins19/huf_core*
