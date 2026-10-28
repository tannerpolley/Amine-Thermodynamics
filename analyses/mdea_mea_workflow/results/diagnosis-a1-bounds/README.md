# A1 bound-pressure diagnosis

Diagnostic calibration only, on Engine 3e83e19c, wheel SHA-256 0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804. Base commit 2623829. No endpoint is selected or adopted; no outside-fit observations are evaluated. Independent delivered review and Design remain open.

| Case | Cost | Active coordinate indices (1-based) | Carson row 1 ΔG/RT | Carson row 10 ΔG/RT |
|---|---:|---|---:|---:|
| without-unloaded-density | 61.484953 | 3, 4, 6, 9 | no witness | no witness |
| without-Cp | 337.636025 | 3, 4, 6, 9 | no witness | no witness |
| without-both | 95.828886 | 4 | no witness | no witness |
| widened-bounds | 2367.978298 | 6, 9 | -3.45906e-05 | -0.10857 |

Coordinate order: 1: k(MDEA-water); 2: slope(MDEA-water) K; 3: k(MDEAH+-CO2); 4: k(MDEAH+-water); 5: slope(MDEAH+-water) K; 6: k(MDEAH+-HCO3-); 7: sigma angstrom; 8: u/k K; 9: Born angstrom.

Cost is half the sum of weighted squared scaled residuals. Diagnostic omitted-group costs below are evaluated at the endpoint but excluded from its fitted objective. A missing phase witness is only a completed-search statement, not proof of global stability. Negative split Gibbs energy is a numerical model result, not physical validation.

The frozen 395 K reaction-domain amendment and Merkley fit temperatures 333.15 and 388.71 K are retained. Fits use the frozen 40-iteration/2100-second controls and tolerances; each compute.json records the memory-sized worker count and one BLAS thread per process. A2 and B2 remain duplicates.

Reproduce from this worktree using `nice -n 10 agent-heavy /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/remaining_starts_bounds.py`. Existing fit files are reused; phase/replay evidence is regenerated. The initial evaluation object access correction in fit_mdea.py changes no numerical declaration.

## without-unloaded-density

converged: Function tolerance reached. |cost_change|/cost: 1.378652e-11 <= 1.000000e-10 Iterations: 10.

| Group | Cost |
|---|---:|
| unloaded-density | 10363.85 |
| Cp | 8.24966895 |
| Kuranov | 7.49563941 |
| Merkley | 1.74217614 |
| Carson | 21.1096655 |
| Jakobsen | 21.3713948 |
| loaded-density | 0.964172711 |
| Kim | 0.552235554 |

| Coordinate | Endpoint | Active bound |
|---|---:|---|
| k(MDEA-water) | -0.213475962355 |  |
| slope(MDEA-water) K | -17.0813068463 |  |
| k(MDEAH+-CO2) | 0.5 | yes |
| k(MDEAH+-water) | -0.5 | yes |
| slope(MDEAH+-water) K | 33.4657747049 |  |
| k(MDEAH+-HCO3-) | -1 | yes |
| sigma angstrom | 6.35933344533 |  |
| u/k K | 181.90212126 |  |
| Born angstrom | 7 | yes |

Scaled-Jacobian singular values: 11.4599721, 9.51726042, 3.50039145, 2.05525341, 0.521334019, 0.213595948, 0.134904722, 0.0155205408, 0.0024039769. Full right singular vectors and active bounds are in fit.json. Full Carson searches, numerical error estimates, and equilibrium residuals are in carson-phase.json. Endpoint documents and fitted-row replay are retained alongside them.

## without-Cp

converged: Function tolerance reached. |cost_change|/cost: 3.097770e-14 <= 1.000000e-10 Iterations: 8.

| Group | Cost |
|---|---:|
| unloaded-density | 287.568816 |
| Cp | 8207.33961 |
| Kuranov | 7.5713004 |
| Merkley | 0.954225893 |
| Carson | 19.6423783 |
| Jakobsen | 21.3261425 |
| loaded-density | 0.509238202 |
| Kim | 0.0639230896 |

| Coordinate | Endpoint | Active bound |
|---|---:|---|
| k(MDEA-water) | -0.206276759636 |  |
| slope(MDEA-water) K | -175.649762228 |  |
| k(MDEAH+-CO2) | 0.5 | yes |
| k(MDEAH+-water) | -0.5 | yes |
| slope(MDEAH+-water) K | -151.897402803 |  |
| k(MDEAH+-HCO3-) | -1 | yes |
| sigma angstrom | 6.38518598013 |  |
| u/k K | 180.234446673 |  |
| Born angstrom | 7 | yes |

Scaled-Jacobian singular values: 20.8425435, 10.9238099, 6.02508955, 3.77628082, 1.81924561, 0.228314126, 0.202691137, 0.0113731355, 0.00151596455. Full right singular vectors and active bounds are in fit.json. Full Carson searches, numerical error estimates, and equilibrium residuals are in carson-phase.json. Endpoint documents and fitted-row replay are retained alongside them.

## without-both

limit_reached: Maximum number of iterations reached. Number of iterations: 38. Iterations: 40.

| Group | Cost |
|---|---:|
| unloaded-density | 1158.30822 |
| Cp | 15994.8681 |
| Kuranov | 23.3604658 |
| Merkley | 1.30178932 |
| Carson | 26.9057153 |
| Jakobsen | 21.6401041 |
| loaded-density | 22.4150241 |
| Kim | 0.205787646 |

| Coordinate | Endpoint | Active bound |
|---|---:|---|
| k(MDEA-water) | -0.217343222451 |  |
| slope(MDEA-water) K | -240.855265596 |  |
| k(MDEAH+-CO2) | 0.488869576354 |  |
| k(MDEAH+-water) | -0.5 | yes |
| slope(MDEAH+-water) K | -285.284377366 |  |
| k(MDEAH+-HCO3-) | -0.971174433832 |  |
| sigma angstrom | 6.22637479715 |  |
| u/k K | 178.071349304 |  |
| Born angstrom | 3.4359671052 |  |

Scaled-Jacobian singular values: 10.5303675, 5.65345654, 2.11335151, 0.527068428, 0.20258641, 0.122073966, 0.0887332813, 0.0383875415, 0.00155277961. Full right singular vectors and active bounds are in fit.json. Full Carson searches, numerical error estimates, and equilibrium residuals are in carson-phase.json. Endpoint documents and fitted-row replay are retained alongside them.

## widened-bounds

converged: Function tolerance reached. |cost_change|/cost: 3.698236e-11 <= 1.000000e-10 Iterations: 30.

| Group | Cost |
|---|---:|
| unloaded-density | 1150.54543 |
| Cp | 764.880822 |
| Kuranov | 235.894802 |
| Merkley | 65.7560686 |
| Carson | 53.1370473 |
| Jakobsen | 95.6990839 |
| loaded-density | 2.04619714 |
| Kim | 0.0188510233 |

| Coordinate | Endpoint | Active bound |
|---|---:|---|
| k(MDEA-water) | -0.181232967878 |  |
| slope(MDEA-water) K | -99.5853191584 |  |
| k(MDEAH+-CO2) | 0.850830077434 |  |
| k(MDEAH+-water) | 0.301906666715 |  |
| slope(MDEAH+-water) K | -199.043111386 |  |
| k(MDEAH+-HCO3-) | 2 | yes |
| sigma angstrom | 6.43632122076 |  |
| u/k K | 501.2797303 |  |
| Born angstrom | 1 | yes |

Scaled-Jacobian singular values: 21.0770933, 12.3615383, 6.25427368, 4.5140132, 2.56709522, 0.915334768, 0.483078547, 0.29239247, 0.0169120376. Full right singular vectors and active bounds are in fit.json. Full Carson searches, numerical error estimates, and equilibrium residuals are in carson-phase.json. Endpoint documents and fitted-row replay are retained alongside them.


[The research notebook](../../notebook.qmd) owns the cause, inference limits, residual figure and Design options. `a1-density-cp-residuals.csv` owns the per-row residuals; `ion-free-density.json`, `ion-free-density-only-fit.json` and `a1-group-gradients.json` retain the attribution checks. Reproduce the neutral calculations with `scripts/a1_density_cp.py`, the figure with `scripts/plot_a1_residuals.py`, and this presentation with `scripts/summarize_bounds.py`, using the same isolated interpreter.

HTML refresh: `python3 analyses/manuscript.py refresh analyses analyses/mdea_mea_workflow/notebook.qmd` failed because `snakemake` is unavailable. The notebook source is complete; no service was started or restarted.
