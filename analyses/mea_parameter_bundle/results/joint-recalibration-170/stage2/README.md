# Stage 2 joint recalibration, 13 October 2026

MEA–water passes the declared numerical and cost gates at both starts. CO₂–water is incomplete: start A stopped at `kiepe-313.20-10`, 313.20 K, liquid CO₂ mole fraction 0.01639 and initial total pressure 4.6671 MPa. Engine returned `CentralSolveUnavailable` / `LOCAL_INFEASIBILITY`, residual 0.0021452086689242953 after 26 iterations against its 1e-10 row tolerance. No CO₂–water fit ran. No rows were dropped, tolerances relaxed, or historical binary values restored. No parameter adoption or Stage 3 readiness is established.

The MEA–water comparison endpoint is start A: constant k_ij = **−0.0843938800264992**, against the old #160 value −0.08031722618968729 and earlier all-Cai value −0.07352749874985018. Start B gives −0.08439384952694257. Cost falls from 102.57716039244268 (A) or 788.2827447533418 (B) to 91.84540850646788; A/B relative cost difference is 4.92724e-12. Both are interior to −0.5…0.5 with no active bound. The CO₂–water old/start-A value −0.02424240226792941 has no new fitted replacement; B = 0.013262879176919628 was not evaluated.

Cai errors for selected A, all 25 rows and both quantities:

| Pressure, Pa | Rows | T mean absolute error, K | T maximum error, K | T RMSE, K | Vapor-water fraction mean absolute error | Maximum fraction error | Fraction RMSE |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 101330 | 12 | 1.514611 | 3.234746 | 1.721445 | 0.01407445 | 0.02820476 | 0.01728448 |
| 66660 | 13 | 1.432137 | 3.726595 | 1.820914 | 0.01514660 | 0.06352112 | 0.02289486 |

The pressure-level costs are 35.70545157 and 55.62357017 respectively. These are boiling-temperature and vapor-composition observations at fixed experimental pressures, not fitted total-pressure errors. All residuals for both endpoints are in `residuals.csv` and each endpoint's `predictions.json`; no accuracy cutoff beyond the design was imposed.

Unloaded 30 wt% density at exact zero carbon and assumed 100000 Pa:

| Row | Temperature, K | Observed, kg/m³ | Predicted, kg/m³ | Signed error, kg/m³ | Role | Within 0.5 kg/m³ |
|---|---:|---:|---:|---:|---|---|
| AMU-DENS-002 | 298.15 | 1010.6 | 1009.907212 | −0.692788 | Fit | No |
| AMU-DENS-009 | 313.15 | 1003.4 | 1003.287419 | −0.112581 | Assessment | Yes |
| AMU-DENS-016 | 323.15 | 998.1 | 998.099992 | −0.000008 | Fit | Yes |
| AMU-DENS-023 | 343.15 | 985.8 | 986.342794 | +0.542794 | Fit | No |
| AMU-DENS-030 | 353.15 | 979.4 | 979.927109 | +0.527109 | Assessment | No |

Finite density misses are reported; the all-five hard density pass belongs to the later completed joint candidate. The current ion quantities are provisional literature/analog seeds.

Kiepe start-A qualification covered eight of twelve 313.20 K rows before the unavailable ninth attempted row. The eight-row partial starting-pressure AARD is 70.223684% (maximum 78.380998%); it is not a complete isotherm or calibration score. At 353.11/373.26/393.17 K, 0/9, 0/12 and 0/6 rows were evaluated. `co2-water/qualification-by-isotherm.json` preserves these denominators, with unavailable full-isotherm scores. `co2-water/A/qualification.json` and the CSV distinguish unavailable from unattempted observations. Cold initialization was used; no continuation or further native call was launched after the unavailable observation, as instructed. The failure does not establish physical model invalidity.

Numerical verification for the completed MEA–water endpoints: relative replay cost difference ≤1.13e-13, weighted residual difference ≤2.76e-11, identical observation IDs, positive phase pressure-density derivatives, and native local-minimum and equilibrium evidence retained for every row. Centered parameter re-solves at optimizer steps 0.01 and 0.005 verify boiling T, vapor-water fraction and reacting density within the declared 1e-5 relative / 1e-8 absolute limits. Maximum material and charge errors are 1.15e-15 and 1.08e-15 mol; maximum source-mass error is 7.80e-17 kg. Unloaded carbon stays exactly zero. Rounded EOS species masses give a separately retained maximum mass difference of 8.50e-9 kg. Native rank is one; both Jacobians, singular spectra, gradients, covariance and its conditional assumptions are retained. Engine does not return its numerical rank cutoff or actual worker count.

Calculation and numerical checks used 56.673325 CPU-s and 35.795568 active wall-s. The existing declaration/hash/memory check also passed across 48 historical starts, using 100.80 CPU-s and 101.23 wall-s. Aggregate execution and checks used **157.473325 CPU-s and 137.025568 active wall-s**, including the earlier rejected declaration, interrupted bookkeeping, and conservatively charged first retained-balance check. Limits remain 900 CPU-s / 300 wall-s. There were two fits, each within 40 iterations and its 60 s wall ceiling. Native row workers requested: 32, from 32 CPUs and 23.25 GB available memory; libraries were single-threaded and calls sequential. Non-fit calls were bounded by 60 s. `timing.json`, `summary.json` and `checks.json` retain measured call costs, host load and charging details.

These results provide conditional MEA–water calibration, same-source density assessment at the two withheld temperatures, and numerical verification. They provide no complete CO₂–water calibration, unique ion properties, independent physical validation, absorber qualification, or adopted parameter set. Notebook, manuscript and selected-current record were not edited. Independent delivered review remains with the parent task.

The accepted design is [#170 §2](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6158000594), with [§8 controls and §9–10 ownership/output rules](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6158000919). `spec.json` freezes the stage-only declaration and all source hashes. Water input: `59acacc310a6dbea73b33599e9fdca3a474e4eccf12ccd139c27816cbef75a7f`. Engine main `36485a88`, wheel `da5a2b65668ab5647e51b917a659614bdcb4afbe7e5c3149aee2294b86a4c1bd`; installed bytes verified, Python 3.13.14, NumPy 2.5.4, SciPy 1.18.1, separate `tmp/stage2/venv`.

`reference-parameters.json` retains adopted water, refreshed CO₂–water induced association (878.3248982254499 K; volume 0.0376197279502706), the Engine-owned Wolbach–Sandler MEA–water combining declaration, source chemistry and provisional starting assumptions. Its hash and the selected MEA–water path/hash are in `frozen-inputs.json`; no CO₂–water endpoint was created. Selected A SHA-256: `36c827bdb5e8b27997f3bc82439ef22d70f7fe8648526e0aa2ac1b6079e6d237`.

The declaration is `data/input/fit-campaigns/joint-recalibration-170.json`, with generated target rows beside it. Responsibilities remain in `fit_campaign.py` (bounded calls, fits, replay and selection), `fit_observations.py` (observations, retained values and balances), and `shared_evaluation.py` (association/seed refresh and exact carbon-free feed). No local optimizer or EOS equations were added. `declaration-check.json` preserves the two programming interruptions; the numerical stopping point is in `failure.json`. Implementation base: `6c8d20073fd0e5fda8dd323a51f55551d12b7486`. Change accounting reports 285 gross added executable lines and 3 removed, below the 350-line slice ceiling. Its classifier places the 2,033 declaration/target lines and 62,359 retained-result lines in “other”; these are JSON/CSV inputs and numerical evidence, not hidden executable code. The accounting report itself was copied in after the final-tree measurement. No tests were added; result-level checks protect the declared numerical invariants.
