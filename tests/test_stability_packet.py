import pandas as pd
from huf_core import HUFCore, HUFConfig

def test_stability_packet_shape():
    elements = pd.DataFrame({
        "element_id": [f"A{i}" for i in range(20)],
        "regime_id": ["R1"]*10 + ["R2"]*10,
        "value": list(range(20,0,-1)),
    })
    core = HUFCore(elements, dataset_id="unit_test2")
    base = HUFConfig(budget_type="mass", exclusion="global", tau=0.05)
    sp = core.stability_packet(base, [0.02,0.03,0.05,0.07,0.10])
    assert sp.shape[0] == 5
    assert set(["tau","active_count","discarded_budget_global","jaccard_vs_baseline","spearman_regime_rho_vs_baseline","near_threshold_count"]).issubset(sp.columns)
