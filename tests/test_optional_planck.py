import pytest
healpy = pytest.importorskip('healpy')
astropy = pytest.importorskip('astropy')
import os
import numpy as np
from pathlib import Path
from huf_core.adapters import planck_lfi70_pixel_energy_elements

def test_optional_planck_adapter():
    fits_path = os.environ.get("PLANCK70_FITS")
    if not fits_path:
        return  # optional
    elements, meta = planck_lfi70_pixel_energy_elements(Path(fits_path))
    assert meta["nside_out"] == 64
    assert meta["coarse_npix"] == 49152
    # sanity: total energy positive
    assert meta["total_energy"] > 0
    # sort rho and ensure 0.97 target gives about 18k elements
    rho = elements["value"] / elements["value"].sum()
    sorted_rho = np.sort(rho.to_numpy())[::-1]
    cum = np.cumsum(sorted_rho)
    k = int(np.searchsorted(cum, 0.97) + 1)
    assert 17000 < k < 20000
