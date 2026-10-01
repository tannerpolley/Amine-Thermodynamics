# Born-form ranking after interaction refits

Preregistered 2026-10-01 under owner-authorized follow-up to [issue #141](https://github.com/tannerpolley/Amine-Thermodynamics/issues/141), before any follow-up fit. Starting tree: `83ab62be8c811f65eae0c6a6436f211fd949a82e`, branch `work/141-sensitivity-current`.

Question: does the baseline SSM+DS advantage on the 142-target objective persist when both Born forms can refit all five interaction coordinates at the two input sets that lowered the fixed-interaction Original Born cost?

## Frozen comparison

Four cases: {Original Born, SSM+DS} × {Born diameters multiplied by 0.8 for MEAH+, MEACOO− and HCO3− only; pure-MEA relative permittivity eps_MEA = 24}. Each has two deterministic starts: its own accepted coordinates and the matched other-form coordinates. This is exactly eight five-coordinate fits; no extra start, fitted Born input or new method. Both start vectors are the two records in #141, independent of input set.

Diameter perturbation leaves H3O+, OH− and CO3²− Born diameters, all packing and Debye–Hückel diameters, and eps_MEA = 32 fixed. Permittivity perturbation leaves every diameter fixed. Both retain f_water = 1.5, f_MEA = 1 and eps_ion = 8. Original Born has c_shell = c_dielectric = 0; SSM+DS has both 1; Born remains enabled.

Retain #141 chemistry (nine species, five reactions), aqueous-molality convention, source R4, association topology, solvent-only permittivity mixing, inherited neutral interactions and packet-v5 inputs. No adopted-record change or manuscript edit.

Objective: C = 1/2 sum(r²) = C_pressure + C_Böttinger + C_Matin on the frozen ordered 142 targets over 84 states (48/40/54). Pressure residual is ln(p_model/p_observed)/0.3; species residual is (x_model−x_observed)/(0.1 x_observed+0.001), with existing pooled-target construction. Matin's 18 carbonate/bicarbonate-pool targets remain report-only. Residual scales are fixed engineering choices, not measurement uncertainty estimates. Report pressure/species AARD = 100/n sum(abs(y_model/y_observed−1)), using only positive observations and reporting counts and source/species groups.

The four dimensionless k bounds remain [−0.5,0.5] for MEACOO−–water, MEAH+–water intercept and HCO3−–water; [−1,1] for MEAH+–MEACOO−. The MEAH+–water reciprocal-temperature slope b remains [−1000,1000] K. k(T) = k_ref + b(1/T−1/313.15 K); retain admissibility k(T)<1 at 293.15 and 353.15 K.

Inputs: SSM+DS record SHA-256 `9055458d8b7cd767a0d08e9f37e4fd28631e29c363364d7b842ebade645cb241`; Original Born record `ebb5f8f9df2aa4ff9bbaec72899dae33fba2233823bb7e389bef92b3d2981900`; immutable installed Engine wheel `28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2`. Reuse #141 frozen targets, source hashes, baseline replays and existing fit/evaluation owners, with `uv run --no-sync`. Confirm identities before execution. Baseline references are SSM+DS C = 32.991897261221126 and Original Born C = 34.584032061137975, replay absolute tolerance 1e−8.

## Numerical checks and stopping

Use the existing installed Engine fit and `p5conv-fit.py`: maximum 40 iterations, native elapsed limit 2250 s, relative function stopping tolerance 1e−12, external timeout 2400 s per fit. No revised bound, tolerance, retries or new optimizer. At most two concurrent single-thread numerical jobs host-wide; inspect exact other-fit PIDs before launch and wait on PIDs if needed. OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = 1, memory limit 2 GiB/job.

Every accepted final replay must provide all 142 fitted targets over 84 states, finite predictions, balances ≤1e−7 and maximum absolute stationarity ≤1e−10 with unchanged phase support/topology. Reload all eight saved final mappings; replay/native fitted cost difference ≤1e−8 absolute; use existing 600 s objective replay and 180 s individual-state limits.

Within each case, both starts must converge and agree within 1e−6 relative in cost (denominator max(1,abs(C))), within 1e−5 in each k and within 0.1 K in b. Report active bounds and effective temperature endpoints. A cap, timeout or unavailable solve remains incomplete; retain available values and the cause without reduced-subset costs or penalties. Other independent cases may continue; no third start is authorized. A failed pair cannot support a definitive comparison for that input set.

## Decision rule and delivery

Report every fit's total and pressure/Böttinger/Matin costs, pressure/species AARD and counts, coordinates, bounds, convergence, replay and start agreement, together with both baselines. At each input set the lower converged cost defines the ranking; use the lower accepted start cost per form while displaying both starts. “Robust ranking” means the same form wins at baseline and both altered inputs. Otherwise report “input-dependent”. Also report the minimum fitted cost of each form across the three input sets. Incomplete comparisons keep the verdict unresolved.

Retain compact CSV/JSON and final mappings here, add a section to the existing bundle notebook, render ordinary HTML without model execution, and commit locally without pushing. The supplied-mapping/all-five-coordinate binding in the existing fitter is expected to need three gross added lines; at most six further executable lines are allowed within #141's 80-line budget (74 already used), counted from `d730dc80bbe3b11385c43c2d8e7f3c90b60f52ab`. Stop rather than exceed it. Configuration files carry case inputs; no new calculation driver, equations, residuals or method.

Independent design readiness precedes execution; a separate GPT-6.1 Sol high reviewer checks delivered evidence and the notebook. This is bounded re-calibration and numerical verification under inherited chemistry, residual scales, observation roles and active bounds, not independent physical validation, global optimality, uniquely identified Born inputs, concentration/temperature transfer or absorber qualification. Manuscript use requires investigator promotion of the new notebook commit.

Source basis is inherited from #141. Reading copies were located in the attached checkout's ignored literature shelf and checked against indexed/current Zotero files: Böttinger 2008 §§3–8 (NMR pooling, chemical/interaction estimation); Matin 2012 Experimental Section, Method Description, Speciation Comparisons and Conclusions (ambient titration and carbon pooling); Figiel 2025 Born Term, Model Parameters and Conclusions (Born-input and interaction responsibilities). This study transcribes no thermodynamic equation from the uncorrected paper; the qualified Engine remains its numerical owner. Study tolerances and the ranking rule are owner conditions.

