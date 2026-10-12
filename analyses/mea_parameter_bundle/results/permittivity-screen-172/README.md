All six Schreckenberg variants remove the retained falsifier composition's stable gas-density root, but none reaches 73/73 two-phase states at the original family pressures. With the selected SSM+DS record they reach 69/73 after bounded starts; the four remaining rows lie above each variant's computed bubble pressure and have converged single-liquid states. Row 66 is recovered in every current-record variant. The fixed 149-target cost rises from 32.056684909 to 56.350358–60.839193: pressure error worsens, species error improves modestly, Vinjarapu heat error worsens, and Arcis heat error improves. This is a numerical diagnosis and fixed-parameter comparison, with no fit or adoption.

The same-wheel baseline was replayed before the variants. All 149 objective targets and 14 additional Arcis heat comparisons returned available finite predictions. Against the supplied rounded summary, the differences are +0.000000909 in cost, −0.000003657 percentage points in pressure AARD, +0.000000571 percentage points in species AARD, −0.000027703 kJ/mol in Vinjarapu RMSE and +0.000020938 kJ/mol in Arcis RMSE. Exact replay values and differences are in [baseline-replay.csv](baseline-replay.csv); [baseline-targets.json](baseline-targets.json) retains the first replay. The native historical heat-fit cost, 32.0566836963, differs by +0.0000012124 from this wheel's replay; it was not substituted for the baseline.

The falsifier uses loading 0.25557798094241313 mol CO₂/mol MEA, 318.15 K and 3699.0803800848512 Pa. The family uses the retained 73 T/P/loading triples, including row 66 at loading 0.5, 313.15 K and 5061.649225730684 Pa. The feed is 9.7292821 mol MEA, 76.9751925 mol water, and loading × MEA mol CO₂. The current-record declaration preserves its source reaction correlations and neutral reference; it does not substitute the Engine test's fixed reaction constants.

The Engine's historical case-7 record is a separate control. It uses Original Born, with shell and dielectric-saturation coefficients zero, rather than the selected SSM+DS record's coefficients of one. Its fixed reaction logarithms are retained in [inputs/engine-case7-reactions.json](inputs/engine-case7-reactions.json). On this newer wheel its unchanged cold run is 69/73, rather than the historical 72/73 on `6bbaaf1e`; all four cold failures recover with nearby starts, giving 73/73, including row 66. Consequently the historical family count and failure location cannot be presumed for this wheel. Each test record is kept fixed within its own baseline-versus-permittivity comparison.

| Variant | Current cold two-phase | Current after starts | Engine case-7 cold | Engine case-7 after starts | Current row 66 after starts |
|---|---:|---:|---:|---:|---|
| baseline | 46/73 | 53/73 | 69/73 | 73/73 | False |
| MEA-900-CO2-near-zero | 69/73 | 69/73 | 63/73 | 72/73 | True |
| MEA-900-CO2-epsilon-1.55 | 69/73 | 69/73 | 65/73 | 72/73 | True |
| MEA-1403-CO2-near-zero | 66/73 | 69/73 | 68/73 | 72/73 | True |
| MEA-1403-CO2-epsilon-1.55 | 67/73 | 69/73 | 67/73 | 72/73 | True |
| MEA-2200-CO2-near-zero | 65/73 | 69/73 | 66/73 | 72/73 | True |
| MEA-2200-CO2-epsilon-1.55 | 68/73 | 69/73 | 67/73 | 72/73 | True |

The four remaining current-record rows are 63 and 70–72, all at 333.15 K. Row 63 has loading 0.4 and pressure 21787.826 Pa, above the variants' 19617.0–19710.1 Pa bubble pressures. Rows 70–72 have loading 0.5 and pressures 38286.784, 61258.855 and 72744.890 Pa, above their 33027.4–33761.8 Pa bubble pressures. The same declared two-phase problem is not counted as accepted when its vapor disappears. Converged single-liquid states and bubble calculations provide numerical evidence for the phase-boundary explanation; they are not a global phase-stability proof. The remaining Engine-control row for every variant is 69 (loading 0.5, 318.15 K, 7146.172 Pa), above its approximately 6940.5–6940.9 Pa bubble pressure.

Cold failures retain exact messages, residuals, iteration counts and returned coordinates. The first recovery uses at most two nearest same-temperature converged coordinates, with 400 iterations per attempt and the original row tolerance of 1e-10. Remaining rows are checked by single-liquid and bubble calculations. For rows below their bubble pressure only, two bubble-based starts are then tested. These change starts and work allowance, not thermodynamics or acceptance tolerance. The baseline current record still has 16 unavailable below-bubble two-phase rows after these bounded probes, plus the four above-bubble rows. Those 16 remain numerical/solver limitations of this bounded probe, not a physical rejection of the model. [flash-family-comparison.csv](flash-family-comparison.csv) joins accepted/failed rows across variants; [flash-family-summary.csv](flash-family-summary.csv) retains counts. The raw cold, start-sensitivity and phase-boundary results remain beside them.

| Variant | 149-target cost | Pressure AARD (%) | Species AARD (%) | Vinjarapu RMSE (kJ/mol) | Arcis RMSE (kJ/mol) |
|---|---:|---:|---:|---:|---:|
| baseline | 32.056685 | 13.814747 | 7.891435 | 2.126572 | 8.364421 |
| MEA-900-CO2-near-zero | 60.839193 | 40.422320 | 7.524698 | 2.310766 | 7.560472 |
| MEA-900-CO2-epsilon-1.55 | 60.827850 | 40.415464 | 7.524678 | 2.310767 | 7.560475 |
| MEA-1403-CO2-near-zero | 56.361317 | 37.667081 | 7.580354 | 2.309781 | 7.547927 |
| MEA-1403-CO2-epsilon-1.55 | 56.350358 | 37.660358 | 7.580356 | 2.309782 | 7.547930 |
| MEA-2200-CO2-near-zero | 57.741284 | 38.516099 | 7.558841 | 2.276475 | 7.617463 |
| MEA-2200-CO2-epsilon-1.55 | 57.730174 | 38.509319 | 7.558843 | 2.276477 | 7.617466 |

The objective remains 47 pressure, 94 species and 8 Vinjarapu heats, at identical retained states, source values and residual scales. Pressure residuals are logarithmic with scale 0.3; species use the existing 0.1 × observed + 0.001 scale; heat scales are the existing 3–6 kJ/mol values. Arcis's 14 rows are additional comparisons and excluded from the 149-target cost. No parameter optimizer was called. [target-summary.csv](target-summary.csv) includes changes from baseline and cost contributions; [target-source-temperature.csv](target-source-temperature.csv) gives every temperature/source cohort; [targets.csv](targets.csv) and [targets.json](targets.json) retain all predictions.

Switching CO₂ from near-zero to the nominal ε=1.55 construction changes cost by at most 0.011343 and pressure AARD by at most 0.006856 percentage points. Species AARD changes by at most 0.000021 percentage points; heat RMSE differences are below 0.000003 kJ/mol. These are small observable changes in this screen. Cold family counts are sensitive to this small perturbation and are not claimed to be insensitive; bounded starts resolve that count difference. See [co2-sensitivity.csv](co2-sensitivity.csv).

At the falsifier composition, both native vapor and liquid root requests return the same single stable dense root for every Schreckenberg variant. The current-record root density is approximately 58379.47 mol/m³. The native potential at the retained gas packing coordinates is 2872.77–2874.00 RT above the newly converged physical two-phase state under the same variant; those retained coordinates are not a mechanically equilibrated density root under the new form. The gas-density witness itself is mechanically off the imposed pressure under the new form. The fixed-coordinate potential comparison remains useful for identifying the term that moved, but it is not presented as a newly converged gas state.

| Variant | Current gas-composition stable root (mol/m³) | Current retained gas-coordinate G minus physical (RT) | Engine retained gas-coordinate G minus physical (RT) |
|---|---:|---:|---:|---:|
| baseline | 1.401147 | 30.740698 | -114.252199 |
| MEA-900-CO2-near-zero | 58379.473726 | 2874.001790 | 3653.309446 |
| MEA-900-CO2-epsilon-1.55 | 58379.473726 | 2874.001790 | 3653.309446 |
| MEA-1403-CO2-near-zero | 58379.473856 | 2872.770206 | 3651.301817 |
| MEA-1403-CO2-epsilon-1.55 | 58379.473856 | 2872.770206 | 3651.301817 |
| MEA-2200-CO2-near-zero | 58379.473812 | 2873.282399 | 3652.006892 |
| MEA-2200-CO2-epsilon-1.55 | 58379.473812 | 2873.282399 | 3652.006892 |

The old Engine falsifier is reproduced: its unchanged gas root is −114.252199 RT relative to its physical state. The same retained gas composition does not beat the current selected record's physical state even before switching permittivity: its retained gas-coordinate potential is already +30.740698 RT. Thus the new probe confirms removal of the old gas root and a larger positive gap for this selected record; it does not prove that the old Engine example was also a lower-Gibbs state under the selected SSM+DS record. No search over all possible gas-density ion compositions or global stability claim is made.

The most informative SSM+DS breakdown is at the retained source gas density of 1.402397 mol/m³, with the retained composition. Bulk ε changes from 71.489805 to 1.001452 for the 1403 K, near-zero CO₂ variant. The extensive residual Helmholtz contributions change as follows; each is in RT for the retained amount of 86.704475 mol:

| Term | Current baseline | Schreckenberg, MEA 1403 K, near-zero CO₂ | Change |
|---|---:|---:|---:|
| Debye–Hückel | -0.277105 | -157.258933 | -156.981828 |
| Born bulk | -3008.409782 | -4.422707 | +3003.987075 |
| Born shell | -821.422413 | -821.422413 | +0.000000 |

The shell stays finite as bulk ε approaches one because the ionic-region ε remains 8 and the shell geometry is unchanged. At density 1e-6 mol/m³, the Born bulk contribution approaches zero while the shell remains −821.422413 RT. It therefore supplies a finite residual stabilization, but it does not sustain the old gas root in these variants. The Engine computes every contribution; bulk Born is obtained with `c_dielectric=0` at identical T, density and composition, and shell Born is total minus that bulk value. This ablation is solely a decomposition diagnostic; the solved models retain `c_dielectric=1`. No Born equation was copied locally.

[falsifier.csv](falsifier.csv) retains native Gibbs comparisons, root counts and pressure values. [falsifier-contributions.csv](falsifier-contributions.csv) includes hard-chain, dispersion, association, Debye–Hückel, Born bulk and shell at both retained source densities and newly solved physical states. The fixed-density extensive residual terms are Helmholtz contributions, not species chemical-potential contributions. For the current record, the source-density split and the retained packing-coordinate Gibbs comparison are distinct evaluations because its geometry differs from the old test record; their values are not summed together. The native Gibbs evaluator owns the standard, ideal and pressure-volume contributions. No private Engine accessor or local coordinate-conversion equation is used. [falsifier-low-density.csv](falsifier-low-density.csv) tests 1e-6–100 mol/m³. The old witness's vanished vapor amount of approximately −1e-8 mol is set to zero for comparison; no negative amount is counted as physical. The retained old physical coordinates are not a new equilibrium solution under the current record or a changed form; their compiled row mismatches remain visible. The contribution table reports the EOS pressure at each source-density diagnostic state.

At unloaded 30.21 wt% and 298.15 K, the source-density dielectric predictions are 68.4273, 64.6683 and 65.8419 for MEA dT 900, 1403 and 2200 K, versus Agieienko's 66.71. At the model density they are 68.3488, 64.5941 and 65.7664. Across all 14 unloaded compositions, source-density dielectric RMSE is 1.7137, 1.6747 and 0.6688 respectively (baseline 1.7666). These comparisons constrain plausibility at one temperature; they do not identify temperature dependence. The six variants reproduce neat MEA 30.45 at the model anchor density. [dielectric-comparisons.csv](dielectric-comparisons.csv) retains both density bases and the qualified Hajj comparisons. Source access, uncertainty, coefficients and derivations are detailed in [coefficients-and-derivations.md](coefficients-and-derivations.md).

The numerical verification is limited to this falsifier, its retained composition and the declared flash family. The 149-target results are fixed-parameter comparisons on previously used observations, not calibration, predictive assessment or independent physical validation. MEA has one measured coefficient constraint; its dT sensitivity is analyst-chosen. CO₂ coefficients are assumed. Hajj's static-limit values are qualified because of the source's extrapolation warning, and the calculation assumes 101325 Pa. The ESI numerical tables were read from official indexed text, without a downloadable PDF hash. No selected record, notebook, manuscript or worktree `.venv` pin was changed.

The owner decisions raised are whether a family requirement should admit one-liquid states when the original pressure lies above the changed model's bubble pressure; which dielectric temperature and composition evidence should constrain MEA before coefficient selection; whether the finite low-density shell stabilization needs an additional model study; and whether a separately designed fixed-form parameter fit is warranted by the pressure-error increase. This screen authorizes none of those changes. The 900 K choice is not selected merely because it gives the largest cold two-phase count, and the 2200 K choice is not adopted merely because its unloaded one-temperature comparison is closest.

Independent delivered review found this bounded screen Supported, with no material findings or required corrections; see [review.md](review.md).

The result check passed: unchanged non-dielectric inputs, six imposed dielectric anchors, 1141 available target predictions, 1022 accounted cold flash rows and the retained Engine Gibbs reference. The explicit check is [check_results.py](check_results.py).

The immutable installed wheel is `main-81d1e38a`, from a commit on `origin/main`, SHA-256 `3fd8140211aac1fb1e82807f066cdf507be733b36c6c27bf41377e7bb939aa86`. The read-only clone was synchronized to `df48223fa19f5e4585a866328812976e7023bdff`. Installation is in the ignored `tmp/permittivity-screen-172-venv`, with package bytes verified against the wheel. [provenance.json](provenance.json) records full commit, source/parameter/input hashes and environment identity. At most 16 processes run at a time, with OMP, OpenBLAS and MKL threads set to one.

To reproduce through the existing MEA owners, run from the repository root with the private interpreter:

```bash
uv run --no-project --python tmp/permittivity-screen-172-venv/bin/python analyses/mea_parameter_bundle/results/permittivity-screen-172/permittivity_probe.py targets
uv run --no-project --python tmp/permittivity-screen-172-venv/bin/python analyses/mea_parameter_bundle/results/permittivity-screen-172/permittivity_probe.py falsifier
uv run --no-project --python tmp/permittivity-screen-172-venv/bin/python analyses/mea_parameter_bundle/results/permittivity-screen-172/permittivity_probe.py family
uv run --no-project --python tmp/permittivity-screen-172-venv/bin/python analyses/mea_parameter_bundle/results/permittivity-screen-172/recover_family.py
uv run --no-project --python tmp/permittivity-screen-172-venv/bin/python analyses/mea_parameter_bundle/results/permittivity-screen-172/diagnose_family.py
uv run --no-project --python tmp/permittivity-screen-172-venv/bin/python analyses/mea_parameter_bundle/results/permittivity-screen-172/bubble_starts.py
uv run --no-project --python tmp/permittivity-screen-172-venv/bin/python analyses/mea_parameter_bundle/results/permittivity-screen-172/compare_dielectric.py
uv run --no-project --python tmp/permittivity-screen-172-venv/bin/python analyses/mea_parameter_bundle/results/permittivity-screen-172/summarize_results.py
```

```bash
uv run --no-project --python tmp/permittivity-screen-172-venv/bin/python analyses/mea_parameter_bundle/results/permittivity-screen-172/check_results.py
```
