# HUF Handbook (Clean Edition) — v1.3.0

> Build date: 2026-02-21  
> Canonical public handbook (Markdown). This supersedes prior handbook variants.

!!! note "Ethics disclosure (short)"
    Drafted with AI assistance as an editing tool and reviewed/curated by the author. Formal claims are stated conservatively and should be reproducible via repository code where applicable. See **[Ethics](ethics.md)**.

!!! tip "Conceptual trigger: why 'loss' can make retained look stronger"
    If you discard some mass and then **re-normalize**, the retained portion is re-scaled to sum to 1. That can make the retained shares appear larger even though nothing “grew” — you are looking at the conditional mix **given what was kept**.

This handbook is organized for readers coming from multiple fields (software, data engineering, ML, physics, pure math). It prioritizes (1) reproducible computation, (2) explicit definitions, and (3) clear separation between formal results and interpretive analogies.
If you only read one section first: Start Here → Worked Example (Vector DB) → Artifact Reference → Nomenclature.
## Start Here
HUF is a normalization‑invariant formalism for analyzing and stabilizing hierarchical mixtures. Given any system that produces weighted contributions across regimes (sources, namespaces, components, experts, tenants), HUF asks: which regimes dominate, how concentrated is dominance, and how stable is the mix under small perturbations?
In practice, HUF consumes a simple JSONL log of retrieval results (or any scored items with a regime label) and emits a small set of artifacts: (1) a coherence map, (2) an active set, (3) a trace report, and (4) an error budget.
Core promise: results are meaningful even when upstream scores are rescaled, normalized differently, or mixed across sources—because the analysis is designed to be invariant to normalization choices.
## What HUF Is (and Is Not)
HUF is NOT a vector database, not a reranker, and not a replacement for your retrieval or modeling stack. It is an audit and stability layer that evaluates the *composition* of outputs across regimes.
HUF IS useful when you suspect: a tenant dominates a multi‑tenant system, one data source overwhelms others, a pipeline is brittle under small score shifts, or overall metrics look good while a subset silently collapses.
## Formal Core
### Objects, Regimes, and Weights
An *item* is a returned unit (document, record, event, sample). Each item i has:
- a regime label r(i) (e.g., namespace, tenant, source, modality)
- a non‑negative score s(i) (e.g., similarity, relevance, likelihood)
- optional metadata (rank, query id, timestamp, etc.)
Let R be the set of regimes. Define regime mass:
- w_r = Σ_{i: r(i)=r} s(i)
Define the normalized regime distribution (a point on the probability simplex):
- p_r = w_r / Σ_{r∈R} w_r
HUF computations are designed to depend on p (and derived geometric quantities), not on the absolute scale of scores.
### Category-Theoretic Spine
A minimal formalization treats HUF instances as objects in a category where morphisms preserve the structure relevant to normalization‑invariant analysis.
- Definition (HUF object). A HUF object is a pair (R, p) where R is a finite set of regimes and p is a distribution on R (p_r ≥ 0, Σ p_r = 1).
- Definition (structure-preserving morphism). A morphism f: (R, p) → (R', p') is a regime map f: R → R' such that p' is the pushforward of p under f (i.e., p'_{r'} = Σ_{r: f(r)=r'} p_r).
Intuition: merging regimes (kb + manual → docs) is a morphism; splitting regimes is not (unless you introduce additional structure).
This captures “sum-preserving” behavior: total mass is conserved under the regime mapping, and composition behaves as expected.
### Normalization Invariance
Most pipelines rescale scores: cosine similarity, distances, logits, calibrated probabilities, min‑max scaling, temperature scaling, etc. HUF is designed so that its regime-level conclusions are stable under monotone rescalings that do not change the relative ordering within a query, and under global multiplicative scaling.
- Claim (informal). If scores are scaled by a positive constant α>0 (s(i)→α s(i)), then p is unchanged and all regime-level statistics derived from p are unchanged.
- Note. For more general rescalings, invariance holds for the parts of the pipeline that depend only on normalized regime mass p (not on raw s).
### Sphere Embedding and Geometry
The normalized distribution p lives on the simplex. A useful embedding maps p to the unit sphere via elementwise square root:
- φ(p) = (√p_1, …, √p_|R|) ∈ S^{|R|-1}
This embedding connects to well-known statistical geometry (Hellinger distance / Fisher–Rao metric). In HUF, it provides a convenient geometry for defining contraction/stability measures and for visualizing regime mixtures.
### Stability and Lyapunov View
HUF tracks whether the regime mixture is stable under small perturbations (e.g., small score changes, small dataset shifts). A practical stability packet reports how the active set and dominance metrics change under controlled noise or parameter sweeps (τ variants).
- Lyapunov-style heuristic. If an update rule on φ(p) is contractive (reduces a suitable distance on the sphere), the mixture converges to a stable regime composition.
## Interpretive Extensions (Explicitly Non-Equivalence)
The following sections are *structural correspondences* and *embedding interpretations*. They are included because they help experts connect HUF to familiar frameworks, but they are not claimed as formal equivalences unless a full construction is given.
- Sheaf analogy: regimes as open covers; local consistency vs global coherence.
- Simplicial analogy: mixtures across regimes form simplices; refinement corresponds to regime partitioning.
- Topos analogy: internal logic of a regime-indexed system; useful as metaphor unless axiomatized.
- QEC / trace-preserving analogy: error budgets and discard tracking resemble conserved quantities; again, analogy unless formalized.
- GNN analogy: aggregation over a regime graph; helpful for implementation mapping.
## Worked Examples
### Vector DB Coherence (multi-namespace retrieval)
Goal: detect whether one namespace dominates retrieval results even when overall ranking metrics appear fine.
Expected outcome (example run): top regimes by rho_global_post show dominance split across two regimes. In a sample run, 'kb' and 'tickets' appeared with rho ≈ 0.62 and 0.38 respectively (your console output).
What you get:
- artifact_1_coherence_map.csv — regime-level dominance/coherence
- artifact_2_active_set.csv — retained items after thresholding
- artifact_3_trace_report.jsonl — explainability trace
- artifact_4_error_budget.json — discards and accounting
### Planck 70 GHz (scientific data)
Goal: demonstrate that the same audit/stability machinery works on scientific maps by treating map contributions as regime mixtures after binning/resolution changes.
Expected outcome (example run): a compact coherence map across regimes, an active set of retained items, and generated plots (concentration curve, coherence by regime) when plotting is enabled.
Example run metadata from a successful invocation:
- active_set ≈ 18198, coherence_rows ≈ 12
- retained_target = 0.97, nside_out = 64
- discarded_global ≈ 0.03
## Artifact Reference
HUF writes a directory of artifacts under --out. The artifact numbering is stable so downstream tools and documentation can rely on it.

| Artifact | File | What it answers |
| --- | --- | --- |
| 1 | artifact_1_coherence_map.csv | Which regimes dominate, and by how much (global/local coherence). |
| 2 | artifact_2_active_set.csv | Which items are retained after τ/retention policy; ranks and regime labels. |
| 3 | artifact_3_trace_report.jsonl | Per-item trace: why retained/discarded; attribution fields. |
| 4 | artifact_4_error_budget.json | Accounting of discards: global/local/declared; summary stats. |

## Nomenclature (Symbols, Variables, and Definitions)
This section is intended to make the math readable and the code searchable.

| Symbol / term | Meaning | Where you see it |
| --- | --- | --- |
| R | Set of regimes (namespaces/tenants/sources). | Coherence map; regime-field. |
| i | Item index. | Active set, trace report. |
| s(i) | Raw score for item i (non-negative after any transform). | Input JSONL. |
| w_r | Regime mass Σ s(i) within regime r. | Internal; coherence. |
| p_r | Normalized regime mass w_r / Σ w. | Core object distribution. |
| τ (tau) | Global retention / threshold parameter controlling how much tail mass is discarded. | CLI flags; meta.json. |
| ρ_global_post | Post-normalization global coherence/dominance statistic over regimes. | artifact_1_coherence_map.csv |
| ρ_local_post | Local coherence statistic within a regime (item-level concentration). | active set/coherence map |
| items_to_cover_90pct | Smallest number of items whose cumulative mass reaches 90% (concentration proxy). | inspect scripts; tail summary. |
| discarded_global | Fraction of mass removed by global policy. | meta.json; error_budget. |

## Cross-Platform Execution Notes
HUF examples are runnable on Windows PowerShell, macOS, and Linux. Be careful: shell syntax differs. In particular, PowerShell does not support Bash heredocs (<<'PY'). Use either (a) a Python script file, (b) python -c "...", or (c) PowerShell here-strings (@' ... '@).
If you see errors like “The '<' operator is reserved for future use”, you pasted Bash syntax into PowerShell.
Recommendation: use the provided scripts in scripts/ and examples/ rather than pasting multi-line Python into a shell.
## Troubleshooting
MkDocs warning about “MkDocs 2.0 incompatible with Material” means your MkDocs major version and the theme version are mismatched. If you use Material, prefer the pinned versions in this repo’s docs requirements. If you upgrade MkDocs, upgrade the theme accordingly (or switch generators).
If documentation pages exist but are “not included in nav”, run scripts/docs_hygiene.py (it normalizes nav and updates the catalog).

