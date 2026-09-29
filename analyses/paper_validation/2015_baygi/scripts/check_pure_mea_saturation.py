"""Pure-MEA saturation pressure of the Table 2 parameter rows against the DIPPR correlation of Baygi Eq. 9 / Table 1
(15 temperatures, 303.15-443.15 K), as an association-scheme convention check for the pcsaft calculation.

    uv run python analyses/paper_validation/2015_baygi/scripts/check_pure_mea_saturation.py
"""
import numpy as np
import pandas as pd
from pcsaft import flashTQ

from baygi_model import ANALYSIS_DIR, pcsaft_params

A, B, C, D, E = 92.624, -10367.0, -9.4699, 1.9e-18, 6.0  # Table 1 (Avlund 2008 DIPPR)
rows = []
for scheme, published in (("2B", 0.62), ("3B", 1.75), ("4C", 0.24)):
    p = pcsaft_params(scheme, "4C")
    mea = {k: (v[[1]] if isinstance(v, np.ndarray) and v.ndim == 1 else v) for k, v in p.items()}
    mea.update(k_ij=np.zeros((1, 1)), assoc_scheme=[scheme.lower()])
    for T in np.linspace(303.15, 443.15, 15):
        ps = np.exp(A + B / T + C * np.log(T) + D * T**E)
        rows.append({"scheme": scheme, "temperature_K": T, "dippr_psat_Pa": ps,
                     "pcsaft_psat_Pa": flashTQ(T, 0, np.array([1.0]), params=mea)[0], "baygi_table2_aad_percent": published})
d = pd.DataFrame(rows)
d["abs_rel_error"] = (d.pcsaft_psat_Pa / d.dippr_psat_Pa - 1).abs()
d.to_csv(ANALYSIS_DIR / "data" / "processed" / "baygi_pure_mea_psat_check.csv", index=False, float_format="%.6g")
print(d.groupby("scheme").agg(aad_percent=("abs_rel_error", lambda s: 100 * s.mean()), published=("baygi_table2_aad_percent", "first")))
