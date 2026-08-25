# CO2-water qualification with fixed induced association

This study evaluates the retained Pabsch parameterization against all 39
nonzero-composition rows in Kiepe et al. (2002), Table 1. The molecular
parameters, reciprocal CO2-water association edges, and

\[
k_{\mathrm{CO2,H2O}}(T)=0.0122+3.016\times10^{-4}(T-298.15\ \mathrm{K})
\]

come from Pabsch et al. (2020), Tables 2 and 6. No reactive MEA parameter is
estimated here. The calculation uses the declared liquid/vapor topology and
stores every evaluated row, phase density, vapor composition, residual, and
solver certificate.

## Result

All 39 rows evaluate. The natural-log pressure RMSE is `0.21228`, the median
multiplicative error is `1.1703`, the maximum pressure residual is
`2.36e-9`, and the maximum chemical-potential residual is `1.85e-8`. The
source temperature correlation is therefore frozen for the next MEA stage.

Exact values are in `results/predictions.csv`, the complete molecular and
interaction table is in `results/parameter_table.csv`, and the numerical
summary is in `results/summary.json`.

Run generation and rendering separately:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  .venv/bin/python analyses/phase3/ionic_epcsaft_regression/co2_water_induced_association/scripts/generate.py
.venv/bin/python analyses/phase3/ionic_epcsaft_regression/co2_water_induced_association/scripts/render.py
```
