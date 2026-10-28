# Remaining joint-fit starts

Diagnostic calibration only, on Engine 3e83e19c, wheel SHA-256 0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804. Base commit 2623829. No endpoint is selected or adopted; no outside-fit observations are evaluated. Independent delivered review and Design remain open.

| Case | Cost | Active coordinate indices (1-based) | Carson row 1 ΔG/RT | Carson row 10 ΔG/RT |
|---|---:|---|---:|---:|
| A1 | 2478.055957 | 3, 6, 9 | no witness | -0.0413548 |
| A3 | 2478.055957 | 3, 6, 9 | no witness | -0.0413555 |
| A4 | 2478.055957 | 3, 6, 9 | no witness | -0.0413507 |
| B1 | 2685.766932 | 3, 6, 9 | no witness | unresolved |
| B3 | 2685.766932 | 3, 6, 9 | no witness | no witness |

Coordinate order: 1: k(MDEA-water); 2: slope(MDEA-water) K; 3: k(MDEAH+-CO2); 4: k(MDEAH+-water); 5: slope(MDEAH+-water) K; 6: k(MDEAH+-HCO3-); 7: sigma angstrom; 8: u/k K; 9: Born angstrom.

Cost is half the sum of weighted squared scaled residuals. Diagnostic omitted-group costs below are evaluated at the endpoint but excluded from its fitted objective. A missing phase witness is only a completed-search statement, not proof of global stability. Negative split Gibbs energy is a numerical model result, not physical validation.

The frozen 395 K reaction-domain amendment and Merkley fit temperatures 333.15 and 388.71 K are retained. Fits use the frozen 40-iteration/2100-second controls and tolerances; each compute.json records the memory-sized worker count and one BLAS thread per process. A2 and B2 remain duplicates.

Reproduce from this worktree using `nice -n 10 agent-heavy /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/remaining_starts_bounds.py`. Existing fit files are reused; phase/replay evidence is regenerated. The initial evaluation object access correction in fit_mdea.py changes no numerical declaration.

## A1

converged: Function tolerance reached. |cost_change|/cost: 2.559080e-11 <= 1.000000e-10 Iterations: 19.

| Group | Cost |
|---|---:|
| unloaded-density | 1273.52961 |
| Cp | 751.832429 |
| Kuranov | 231.610672 |
| Merkley | 78.5840331 |
| Carson | 70.4923515 |
| Jakobsen | 68.9892933 |
| loaded-density | 2.99999117 |
| Kim | 0.0175756581 |

| Coordinate | Endpoint | Active bound |
|---|---:|---|
| k(MDEA-water) | -0.179560673976 |  |
| slope(MDEA-water) K | -94.3749061493 |  |
| k(MDEAH+-CO2) | 0.5 | yes |
| k(MDEAH+-water) | 0.360212621128 |  |
| slope(MDEAH+-water) K | -143.775923608 |  |
| k(MDEAH+-HCO3-) | 1 | yes |
| sigma angstrom | 6.49720423753 |  |
| u/k K | 836.778940666 |  |
| Born angstrom | 2 | yes |

Scaled-Jacobian singular values: 20.9720881, 12.8666649, 6.84657896, 4.02081322, 2.60065851, 0.446013306, 0.229938154, 0.174518305, 0.0155412265. Full right singular vectors and active bounds are in fit.json. Full Carson searches, numerical error estimates, and equilibrium residuals are in carson-phase.json. Endpoint documents and fitted-row replay are retained alongside them.

## A3

converged: Function tolerance reached. |cost_change|/cost: 4.628886e-11 <= 1.000000e-10 Iterations: 24.

| Group | Cost |
|---|---:|
| unloaded-density | 1273.5309 |
| Cp | 751.832339 |
| Kuranov | 231.610806 |
| Merkley | 78.5835797 |
| Carson | 70.4917604 |
| Jakobsen | 68.9890452 |
| loaded-density | 2.99995047 |
| Kim | 0.0175756421 |

| Coordinate | Endpoint | Active bound |
|---|---:|---|
| k(MDEA-water) | -0.179560658265 |  |
| slope(MDEA-water) K | -94.3748533058 |  |
| k(MDEAH+-CO2) | 0.5 | yes |
| k(MDEAH+-water) | 0.360211435398 |  |
| slope(MDEAH+-water) K | -143.776051567 |  |
| k(MDEAH+-HCO3-) | 1 | yes |
| sigma angstrom | 6.49720273504 |  |
| u/k K | 836.77358448 |  |
| Born angstrom | 2 | yes |

Scaled-Jacobian singular values: 20.9720882, 12.8666508, 6.84656004, 4.02081353, 2.6006542, 0.446011738, 0.229939108, 0.174518533, 0.0155411354. Full right singular vectors and active bounds are in fit.json. Full Carson searches, numerical error estimates, and equilibrium residuals are in carson-phase.json. Endpoint documents and fitted-row replay are retained alongside them.

## A4

converged: Function tolerance reached. |cost_change|/cost: 2.509661e-11 <= 1.000000e-10 Iterations: 27.

| Group | Cost |
|---|---:|
| unloaded-density | 1273.5339 |
| Cp | 751.831717 |
| Kuranov | 231.60954 |
| Merkley | 78.5834674 |
| Carson | 70.4913957 |
| Jakobsen | 68.9883192 |
| loaded-density | 3.00004241 |
| Kim | 0.0175756333 |

| Coordinate | Endpoint | Active bound |
|---|---:|---|
| k(MDEA-water) | -0.179560613432 |  |
| slope(MDEA-water) K | -94.3747301712 |  |
| k(MDEAH+-CO2) | 0.5 | yes |
| k(MDEAH+-water) | 0.360210422748 |  |
| slope(MDEAH+-water) K | -143.775508918 |  |
| k(MDEAH+-HCO3-) | 1 | yes |
| sigma angstrom | 6.49720421802 |  |
| u/k K | 836.772744125 |  |
| Born angstrom | 2 | yes |

Scaled-Jacobian singular values: 20.9720878, 12.8666399, 6.84655317, 4.02080575, 2.60065749, 0.446011243, 0.22993861, 0.174518327, 0.0155409552. Full right singular vectors and active bounds are in fit.json. Full Carson searches, numerical error estimates, and equilibrium residuals are in carson-phase.json. Endpoint documents and fitted-row replay are retained alongside them.

## B1

converged: Function tolerance reached. |cost_change|/cost: 2.261015e-11 <= 1.000000e-10 Iterations: 20.

| Group | Cost |
|---|---:|
| unloaded-density | 1764.88857 |
| Cp | 777.119985 |
| Kuranov | 29.830305 |
| Merkley | 7.85062342 |
| Carson | 67.5164621 |
| Jakobsen | 22.2934544 |
| loaded-density | 16.2524469 |
| Kim | 0.0150889712 |

| Coordinate | Endpoint | Active bound |
|---|---:|---|
| k(MDEA-water) | -0.173759807744 |  |
| slope(MDEA-water) K | -76.2778061873 |  |
| k(MDEAH+-CO2) | 0.5 | yes |
| k(MDEAH+-water) | -0.205098164217 |  |
| slope(MDEAH+-water) K | -68.6621580441 |  |
| k(MDEAH+-HCO3-) | 1 | yes |
| sigma angstrom | 3.66199240117 |  |
| u/k K | 251.18119019 |  |
| Born angstrom | 2 | yes |

Scaled-Jacobian singular values: 21.0868249, 10.6578376, 8.52581024, 4.95923324, 3.41895865, 0.365606439, 0.253842974, 0.0707477998, 0.023421573. Full right singular vectors and active bounds are in fit.json. Full Carson searches, numerical error estimates, and equilibrium residuals are in carson-phase.json. Endpoint documents and fitted-row replay are retained alongside them.

## B3

converged: Function tolerance reached. |cost_change|/cost: 3.615978e-11 <= 1.000000e-10 Iterations: 25.

| Group | Cost |
|---|---:|
| unloaded-density | 1764.88867 |
| Cp | 777.119991 |
| Kuranov | 29.8302029 |
| Merkley | 7.85058954 |
| Carson | 67.5164938 |
| Jakobsen | 22.2934483 |
| loaded-density | 16.2524458 |
| Kim | 0.0150889708 |

| Coordinate | Endpoint | Active bound |
|---|---:|---|
| k(MDEA-water) | -0.173759806685 |  |
| slope(MDEA-water) K | -76.277802672 |  |
| k(MDEAH+-CO2) | 0.5 | yes |
| k(MDEAH+-water) | -0.20510041521 |  |
| slope(MDEAH+-water) K | -68.6623897546 |  |
| k(MDEAH+-HCO3-) | 1 | yes |
| sigma angstrom | 3.66199241834 |  |
| u/k K | 251.179622639 |  |
| Born angstrom | 2 | yes |

Scaled-Jacobian singular values: 21.086825, 10.6578358, 8.52582944, 4.9592375, 3.41894833, 0.365604892, 0.253842915, 0.0707484718, 0.0234210312. Full right singular vectors and active bounds are in fit.json. Full Carson searches, numerical error estimates, and equilibrium residuals are in carson-phase.json. Endpoint documents and fitted-row replay are retained alongside them.

