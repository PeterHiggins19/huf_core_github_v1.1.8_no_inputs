# Higgins Unity Framework (HUF)

Normalization-invariant audit layer for hierarchical mixtures (regimes/tenants/sources).

PROOF (fast intuition): items_to_cover_90pct 37 -> 12 when switching baseline -> exception view on the same dataset (see the 2-minute demo below).

Docs: https://peterhiggins19.github.io/huf_core/

## What it outputs (artifact-first)
- Coherence map (artifact_1_coherence_map.csv) - where the mass is (ranked regimes)
- Active set (artifact_2_active_set.csv) - retained items + global/local shares
- Trace report (artifact_3_trace_report.jsonl) - provenance + "why it stayed"
- Error budget (artifact_4_error_budget.json) - accounting of discards

Why "loss can make retained stronger": if you discard tail mass and then renormalize, the retained portion is scaled up.
