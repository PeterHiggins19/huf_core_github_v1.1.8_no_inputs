# HUF Reference (Skeptic Appendix) — v1.3.0

> Build date: 2026-02-21  
> Canonical public reference (Markdown). This supersedes prior skeptic/reference variants.

!!! note "Ethics disclosure (short)"
    Drafted with AI assistance as an editing tool and reviewed/curated by the author. Formal claims are stated conservatively and should be reproducible via repository code where applicable. See **[Ethics](ethics.md)**.

## Key intuition: why 'loss' can make retained stronger
If you keep only a retained subset and then re-normalize, every retained weight is scaled by the same factor `1 / retained_mass`.

Example:

- start: `[0.60, 0.30, 0.10]` (sums to 1)
- discard the last `0.10` tail → retained mass is `0.90`
- re-normalize retained → `[0.60/0.90, 0.30/0.90] = [0.667, 0.333]`

Nothing “mystical” happened: you’re now looking at the mix **conditional on retention**. HUF makes this explicit and auditable (trace report + error budget).

Purpose: help technically skeptical readers quickly locate what is proved, what is measured, and what is presented as analogy.
## 1) What is the core claim?
Core claim: HUF provides normalization‑invariant diagnostics of regime dominance and concentration for any scored mixture output, and packages the results as auditable artifacts.
## 2) Is this just ‘normalize weights on the simplex’?
At the base layer, yes: HUF explicitly constructs p on the simplex. The contribution is (a) a consistent artifact protocol, (b) dominance/coherence statistics and concentration summaries that are easy to operationalize, and (c) a stability workflow (τ sweeps, deltas, trace reports) that turns ‘mixture drift’ into something you can track and regress-test.
## 3) What is actually proved vs. suggested?
Proved/derivable (within the handbook’s scope):
- scale invariance under s→αs (α>0) at the regime distribution level.
- functorial behavior of regime merging as pushforward on distributions.
- geometric embedding φ(p) on the sphere, connecting to standard statistical geometry.
Presented as interpretations (not equivalences unless formalized): sheaf/topos/simplicial analogies; QEC analogies; Langlands/arithmetic geometry claims. These should be treated as research directions until fully constructed.
## 4) Where is the universal property?
If a universal property is claimed, it must be stated in category language: e.g., “(R,p) is initial among objects receiving a regime-merging map from a given mixture log under pushforward constraints.” In v1.3.0, we do not claim a strong universal property beyond the standard pushforward construction.
## 5) Does the sphere mapping add anything beyond visualization?
It can, when used as a geometry for stability/contraction analysis or for defining distances between mixtures. Without those steps, it is indeed mostly a convenient coordinate transform. The handbook therefore frames it as ‘geometry support’ for stability workflows.
## 6) What is the computational advantage?
Operational advantage: you can monitor regime dominance and concentration as first-class metrics, and attach traceable artifacts to PRs, incident reports, or eval dashboards. This is valuable precisely when scalar retrieval metrics (NDCG/MRR) hide distributional collapse across sources/tenants.
## 7) What should I verify if I’m reviewing this?
- Reproduce the vector_db example end-to-end; confirm the coherence map reflects your namespaces.
- Run a τ sweep; confirm concentration and active_set size change sensibly.
- Inspect artifact_3_trace_report.jsonl; confirm discards are explainable and consistent.
- Confirm invariance: multiply all input scores by 10 and verify regime-level outputs are unchanged.
## 8) Common failure modes
- Mixing shell syntaxes (Bash heredoc in PowerShell) → parse errors.
- Including generated outputs in git (site/, out/) → repo looks like HTML, slows clones, confuses reviewers.
- Unpinned doc dependencies → MkDocs/Material warnings or build failures.
## 9) Limits and non-goals
HUF does not claim to improve retrieval quality directly; it diagnoses composition and stability. It does not claim that analogies (topos, Langlands, QEC) are theorems. Those belong in separate, peer-reviewable technical notes.
## 10) How to cite or discuss responsibly
Recommended phrasing:
- “HUF is a normalization-invariant audit layer for regime dominance and concentration.”
- “We use sphere embedding of simplex distributions to visualize and analyze mixture stability.”
- “We discuss sheaf/topos analogies as interpretive correspondences, not equivalences.”

