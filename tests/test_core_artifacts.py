from huf_core.io import validate_trace_line_min
import pandas as pd
from huf_core import HUFCore, HUFConfig, REQUIRED_TRACE_FIELDS

def test_cycle_emits_required_artifacts():
    elements = pd.DataFrame({
        "element_id": [f"R1/e{i}" for i in range(5)] + [f"R2/e{i}" for i in range(5)],
        "regime_id": ["R1"]*5 + ["R2"]*5,
        "value": [10, 5, 2, 1, 0.5, 8, 4, 2, 1, 0.5],
    })
    core = HUFCore(elements, dataset_id="unit_test")
    cfg = HUFConfig(budget_type="mass", exclusion="global", tau=0.03)
    art = core.cycle(cfg)

    assert "coherence_map" in art
    assert "active_set" in art
    assert "trace_report" in art
    assert "error_budget" in art
    assert "run_stamp" in art

    # global unity (post)
    post_sum = sum(r["rho_global_post"] for r in art["active_set"])
    assert abs(post_sum - 1.0) < 1e-9

    # trace schema
    for rec in art["trace_report"]:
        for f in REQUIRED_TRACE_FIELDS:
            assert f in rec


def test_trace_lines_have_min_fields(tmp_path):
    # Use core demo runner already in tests (if present); otherwise create a minimal run.
    from huf_core.core import HUFRun
    rho = {"a": 0.6, "b": 0.4}
    regimes = {"R": ["a", "b"]}
    run = HUFRun(rho=rho, regimes=regimes, budget_type="mass")
    artifacts = run.cycle(tau_global=0.0, tau_local=0.0)
    # Validate emitted trace lines
    for line in artifacts["trace_report"]:
        validate_trace_line_min(line)
