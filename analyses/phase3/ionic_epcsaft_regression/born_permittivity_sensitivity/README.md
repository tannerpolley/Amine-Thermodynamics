# Born-formulation and induced-association sensitivity

This fixed-parameter study separates CO2-water induced association from the
Born formulation while holding the neutral molecular parameters, ionic
parameters, and five reaction correlations constant. The four combinations
are:

1. original Born with solvent-only relative permittivity, induced association off;
2. original Born with solvent-only relative permittivity, induced association on;
3. shell-modified Born with ion-fraction-suppressed relative permittivity,
   induced association off;
4. shell-modified Born with ion-fraction-suppressed relative permittivity,
   induced association on.

Original-Born cases use `c_shell = c_dielectric = 0`. Shell-modified-Born
cases always use `c_shell = c_dielectric = 1` together with the ion-suppression
coefficient `7.01`.

The six states are the Jakobsen 30 wt% MEA observations at 313.15 K and CO2
loadings 0.11, 0.21, 0.40, 0.60, 0.78, and 0.99 mol CO2/mol MEA. The Amundsen
unloaded 30 wt% density at 313.15 K is shown only as a liquid-density scale;
it is not a loaded-solution validation point.

Generation and rendering are separate:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src \
  uv run python analyses/phase3/ionic_epcsaft_regression/born_permittivity_sensitivity/scripts/generate.py
PYTHONPATH=src uv run python \
  analyses/phase3/ionic_epcsaft_regression/born_permittivity_sensitivity/scripts/render.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src \
  uv run python analyses/phase3/ionic_epcsaft_regression/born_permittivity_sensitivity/scripts/fit_ion_diameters.py
PYTHONPATH=src uv run python \
  analyses/phase3/ionic_epcsaft_regression/born_permittivity_sensitivity/scripts/render_ion_diameter_fit.py
```

Curated results retain one complete Engine JSON parameter document, compact
candidate receipts that reproduce fitted mappings by hash, exact row tables,
and PNG/SVG/PDF render bundles. Flat fitted coordinates and compilation
outcomes remain tabular; raw Engine fit requests, result objects, and start
caches regenerate under the ignored `results/runs/` tree.

The calculation does not fit any parameter. It can reject an incompatible
formulation or parameter combination, but it cannot identify a dielectric or
Born parameter without direct dielectric, activity, transfer, or solvation
observations.

## Result

| Formulation | Evaluated states | Density range (kg/m3) | Typical speciation factor |
|---|---:|---:|---:|
| Original Born, association off | 2/6 | 1.087--1.125 | 2.531 |
| Original Born, association on | 2/6 | 1.087--1.125 | 2.531 |
| Shell Born, ion-suppressed, association off | 6/6 | 1065.5--1445.3 | 1.3235 |
| Shell Born, ion-suppressed, association on | 6/6 | 1065.5--1447.6 | 1.3238 |

Both original-Born formulations fail four states and resolve vapor-scale roots
for the remaining two, so neither supplies a liquid starting branch. Both
ion-suppressed formulations resolve every state at liquid-scale density and
follow the measured carbamate and bicarbonate trends. Turning induced
association on changes the ion-suppressed density by at most 2.27 kg/m3, the
bulk relative permittivity by at most 0.056, and any directly compared species
mole fraction by at most 0.000956. Its speciation metric is therefore
effectively neutral in this six-state calculation.

Induced association remains retained because it was independently qualified
against physical CO2-water phase-equilibrium data. This result shows that ion
suppression, not induced association, selects the liquid reactive branch. It
does not identify the suppression coefficient or establish a universal
superiority claim; direct dielectric and ion-solvation evidence is still
missing.

Exact numerical outputs are in `results/`; the comparison figure is retained
in PNG, SVG, and PDF formats under `figures/`.

## Two-ion-diameter result

The fit compares the same four combinations while freeing only the `MEAH+` and
`MEACOO-` segment diameters. Every case uses the same observations, parameter
bounds, starts, stopping tolerance, and frozen neutral, reaction, Born, and
permittivity parameters. State coverage, branch density, speciation residuals,
fitted parameter movement, active bounds, and Jacobian
conditioning are compared before selecting a structure. Original-Born cases
that return vapor roots remain negative controls and are not treated as liquid
fits.

The two original-Born cases were not fitted because they had no admissible
liquid starting branch. The two shell-Born cases used 32 direct-positive
Jakobsen observations; aggregate rows were excluded to avoid double counting.

| Formulation | $\sigma_{MEAH^+}$ (Å) | $\sigma_{MEACOO^-}$ (Å) | log SSE | Typical factor | Status |
|---|---:|---:|---:|---:|---|
| Shell Born, ion-suppressed, association off | 2.00000 | 3.07165 | 22.811 | 1.477 | converged (`gtol`) |
| Shell Born, ion-suppressed, association on | 2.00000 | 3.06644 | 23.303 | 1.442 | evaluation limit; optimality $7.18\\times10^{-6}$ |

Both fits move the `MEAH+` diameter from 3.48509 Å to the exploratory lower
bound and move the `MEACOO-` diameter from 3.53544 Å to about 3.07 Å. The
well-conditioned two-column Jacobians (condition numbers 3.23 and 3.21) show
that this is a directional model/data result, not a numerical rank failure.
It is not a promoted parameter set because the optimum for `MEAH+` remains
outside the tested interior and the observations are unweighted speciation
rows at one temperature and solvent concentration.

## Ion-specific suppression sensitivity

The Zuber et al. (2014) form
`epsilon = epsilon_salt-free / (1 + sum(alpha_i x_i))` was evaluated with shell
Born and CO2-water induced association retained. Three assignments were compared
with the universal Figiel coefficient 7.01: source H+/OH- plus generic aqueous
charge classes for the unsupported MEA ions, generic charge classes for all six
ions, and source H+/OH- with 7.01 retained for the MEA ions.

| Assignment | States | Typical factor, common five states | Permittivity range |
|---|---:|---:|---:|
| Universal 7.01 | 6/6 | 1.25909 | 32.09--56.58 |
| Zuber known ions + generic organic classes | 5/6 | 1.23991 | 37.06--58.82 |
| Zuber generic charge classes | 5/6 | 1.23991 | 37.06--58.82 |
| Zuber H+/OH- + 7.01 organic fallback | 6/6 | 1.25909 | 32.09--56.58 |

The source H+/OH- substitutions alone are numerically negligible. Assigning
2.60 to MEAH+ and 7.89 to the three MEA-derived/carbonate anions raises the
permittivity, improves the common-state median speciation factor by only about
1.5%, and loses a certified state at loading 0.78. The two generic-class
variants are effectively identical, so the result is controlled by the
unsupported organic-ion transfer rather than the source H+/OH- values. The
useful next calculation is therefore a small MEAH+/MEACOO- coefficient sweep,
not a blanket replacement of 7.01.

## Independent ion-coefficient blocks

The follow-up holds shell Born, ion-suppressed relative permittivity,
CO2--water induced association, $\alpha_{H3O+}=9.55$, and
$\alpha_{OH-}=13.96$ fixed. All unsupported ions start at 7.01. The first
block changes MEAH+ to the generic-aqueous cation value 2.60 and MEACOO- to
the generic-aqueous anion value 7.89, independently and together. The second
block starts from the best full-coverage amine configuration and changes
HCO3- and CO3^2- to 7.89, independently and together. No parameter is fitted.

| Configuration | States | Typical factor, all six states | Permittivity range |
|---|---:|---:|---:|
| Remaining ions 7.01 | 6/6 | 1.32380 | 32.09--56.58 |
| MEAH+ = 2.60 | 6/6 | 1.28178 | 38.62--59.38 |
| MEACOO- = 7.89 | 6/6 | 1.32482 | 31.86--56.10 |
| MEAH+ = 2.60; MEACOO- = 7.89 | 6/6 | 1.29242 | 38.40--58.85 |
| MEAH+ = 2.60; HCO3- = 7.89 | 6/6 | 1.27083 | 37.31--59.37 |
| MEAH+ = 2.60; CO3^2- = 7.89 | 6/6 | 1.28067 | 38.62--59.36 |
| MEAH+ = 2.60; HCO3-/CO3^2- = 7.89 | 6/6 | 1.26912 | 37.31--59.35 |

The MEAH+ coefficient is the controlling amine-ion lever: it reduces the
six-state median factor by 3.2% and removes the prior blanket-transfer
evaluability loss. MEACOO- alone is effectively neutral. On the MEAH+ base,
HCO3- supplies most of the additional median improvement; CO3^2- alone is
nearly neutral. Changing both carbonate coefficients gives the lowest tested
median factor, 1.26912, but its worst individual factor is 7.85 versus 6.40
for MEAH+ alone. The aggregate gain therefore does not imply uniform species
improvement: MEAH+ mainly corrects molecular CO2 and carbonate discrepancies,
while slightly worsening the already closer MEAH+ and MEACOO- predictions.

All 42 state calculations satisfy the numerical checks. The maximum balance
infinity norm is $8.21\times10^{-16}$ and the maximum reaction-affinity
infinity norm is $2.84\times10^{-13}$. Exact state, observation, coefficient,
and plotted-value tables are under `results/ion_coefficient_blocks/`; the
comparison is retained as PNG, SVG, and PDF under `figures/`.

## Broader temperature and pressure comparison

The selected ion block was next evaluated without regression against 15
source-backed 30 wt% MEA pressure observations spanning 40--120 °C. Three
fixed structures were compared: the remaining-ion 7.01 baseline, the selected
ion-specific coefficients, and the selected coefficients with the existing
Archer--Wang water-permittivity temperature approximation. Every structure
retains shell Born, ion-suppressed permittivity, and CO2--water induced
association.

| Configuration | Pressure states | Pressure ln-RMSE | Typical pressure factor | Hajj states | Hajj permittivity RMSE |
|---|---:|---:|---:|---:|---:|
| Remaining ions 7.01; constant water permittivity | 7/15 | 6.802 | 4.398 | 27/28 | 32.80 |
| Selected ion-specific; constant water permittivity | 9/15 | 4.948 | 2.500 | 25/28 | 25.40 |
| Selected ion-specific; water permittivity $\epsilon(T)$ | 10/15 | 0.913 | 2.226 | 27/28 | 32.41 |

The pressure quantity is a diagnostic fixed-pressure neutral-CO2 liquid
fugacity, not a replacement for the final coupled bubble calculation. A
representative 40 °C coupled bubble solve gave 406.37 Pa versus 407.49 Pa from
the diagnostic calculation, supporting its use as the inexpensive structure
screen at that state. Above 323.15 K the reaction correlations are explicitly
extrapolated, and five of the 15 broad states remain non-evaluable.

Hajj et al. (2024), DOI `10.1016/j.molliq.2024.124819`, supplies 28 Cole--Cole
fitted static limits for loaded 30 wt% MEA from 20--80 °C. These microwave-fit
limits are aggregate mixture observations, not direct DC permittivities or
single-ion coefficients. They show that all three solvent-mixing predictions
remain too low in absolute magnitude. Adding water $\epsilon(T)$ supplies the
correct temperature direction but does not close that model-form discrepancy;
the ion coefficients therefore must not be fitted directly to the Hajj table.

Within the tested structures, the best fixed starting parameter document uses
$\alpha_{\mathrm{MEAH^+}}=2.60$,
$\alpha_{\mathrm{MEACOO^-}}=7.01$,
$\alpha_{\mathrm{HCO_3^-}}=\alpha_{\mathrm{CO_3^{2-}}}=7.89$,
$\alpha_{\mathrm{H_3O^+}}=9.55$, and
$\alpha_{\mathrm{OH^-}}=13.96$, together with the Archer--Wang water
$\epsilon(T)$ approximation. The exact full parameter document is
`results/broader_candidate/best_fixed_candidate_parameters.json`, with SHA-256
`28af5df2c37ef878d7e68e0b73faf332f4a3fdea27700c5ebeb5b0ef04cd7a4b`.
This is the best fixed structure from the sensitivity screen, not yet the
completed globally fitted MEA parameter set.

## Superseded fixed-TP shared refinement

The retired fixed-TP surrogate supplied the starting point for the full
reactive-bubble refinement. Its compact parameter receipt remains at
`results/final_shared_refinement/summary.json`; the obsolete runner,
diagnostics, confirmation, and figure bundle are no longer retained.

| Shared parameter | Start | Fitted | Bounds |
|---|---:|---:|---:|
| $k_{CO2,MEA}$ | 0 | -0.03182703 | [-1, 1] |
| $\sigma_{MEAH+}$ (A) | 3.48508557 | 2.68378739 | [1.5, 5.8] |
| $\sigma_{MEACOO-}$ (A) | 3.53543526 | 3.26931496 | [1.5, 5.8] |

## Complete numerical-coverage diagnostic

The fixed-TP cache above was replaced by independently certified problems at
every loading. Pressure residuals now come from the specified finite reactive
liquid plus incipient neutral vapor topology, with total pressure and vapor
composition solved by GREPE. No continuation certificate is transferred
between different conserved feeds.

All 59 pressure rows at 30 wt% MEA and 313.15, 333.15, and 353.15 K compiled
and evaluated, as did all 32 direct-positive targets across six Jakobsen
speciation states. This calculation mixed training, reserved, and
reaction-correlation challenge rows, so it is retained only as proof that the
equilibrium formulation evaluates every selected state. It is not a
predictive parameter fit. The fitted-result accounting is 91 input rows, 91
included, 91 evaluated, zero dropped, zero failed, and zero rejected.

| Shared parameter | Start | Fitted | Bounds |
|---|---:|---:|---:|
| $k_{CO2,MEA}$ | -0.03182703 | -0.55051900 | [-1, 1] |
| $\sigma_{MEAH+}$ (A) | 2.68378739 | 2.77802786 | [1.5, 5.8] |
| $\sigma_{MEACOO-}$ (A) | 3.26931496 | 3.00876798 | [1.5, 5.8] |

The complete pressure block has log-RMSE 0.80079, RMS factor 2.2273, median
factor 1.9161, and mean log bias -0.0101. The complete speciation block has
log-RMSE 0.73458, RMS factor 2.0846, median factor 1.5079, and mean log bias
0.0648. The exact Jacobian has singular values 2.1054, 1.8158, and 0.03779
(condition number 55.7). The second refinement step changed the objective by
only 0.056%, so further iterations with this three-parameter block were not
cost-effective.

The immutable Engine wheel SHA-256 is
`e14288867d4fb5bc1367dd0de490aeb1551f1613074aced0a8d28432ca762f23`.
Exact fit rows, parameters, state-compilation diagnostics, and plotted values
are under `results/full_predictive_refinement/`; the rendered PNG, SVG, and PDF
are `figures/full_predictive_pressure_speciation_refinement.*`.

The remaining scientific limitation is the source validity of reaction
correlations above 323.15 K, not numerical state coverage. The 353.15 K rows
are retained with explicit reaction-correlation extrapolation and remain
separate from a source-qualified high-temperature claim.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  PYTHONPATH=src:analyses/phase3/ionic_epcsaft_regression/born_permittivity_sensitivity/scripts \
  .venv/bin/python analyses/phase3/ionic_epcsaft_regression/born_permittivity_sensitivity/scripts/run_full_predictive_refinement.py --workers 2 --pressure-bounds-pa 10 3000000 --maximum-log-pressure-distance 2 --compile-only
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  PYTHONPATH=src:analyses/phase3/ionic_epcsaft_regression/born_permittivity_sensitivity/scripts \
  .venv/bin/python analyses/phase3/ionic_epcsaft_regression/born_permittivity_sensitivity/scripts/run_full_predictive_refinement.py --fit-existing --maximum-iterations 1
PYTHONPATH=src:analyses/phase3/ionic_epcsaft_regression/born_permittivity_sensitivity/scripts \
  .venv/bin/python analyses/phase3/ionic_epcsaft_regression/born_permittivity_sensitivity/scripts/render_full_predictive_refinement.py
```

## Source-partitioned predictive fit

The same fixed structure was then tested without leakage. The retained
structure is shell Born, ion-suppressed permittivity, CO2--water induced
association, ion-specific suppression coefficients, Archer--Wang water
relative permittivity, and no explicit polar term. Only three shared
coordinates were varied: $k_{CO2,MEA}$, $\sigma_{MEAH+}$, and
$\sigma_{MEACOO-}$.

The training calculation contains 24 Hilliard pressure rows and 131
speciation targets from 44 Boettinger/Matin states. Every one of the 155
targets evaluated at the retained parameter point; none was dropped,
rejected, or replaced by a penalty. One bounded exact-Jacobian step changed
the objective from 0.391179 to 0.385128 and produced:

| Shared parameter | Fitted training value |
|---|---:|
| $k_{CO2,MEA}$ | -0.19572686 |
| $\sigma_{MEAH+}$ (A) | 2.75333285 |
| $\sigma_{MEACOO-}$ (A) | 3.01707929 |

The training pressure RMS factor is 2.0208 and the training speciation RMS
factor is 1.6900. The scaled Jacobian singular values are 2.0252, 0.92458,
and 0.00042673, giving condition number 4746. The weakest direction is not
identified well enough to justify more iterations of this three-parameter
fit.

The parameters were then frozen. All eight reserved Jou pressure rows and all
67 targets from 16 reserved Jakobsen states evaluated without failure. Their
RMS factors are 2.2814 for pressure and 2.3343 for speciation. All 27
333.15--353.15 K reaction-correlation challenge pressure rows also evaluated;
their combined RMS factor is 2.3926. The 353.15 K subset has RMS factor 2.9087
and mean log bias -0.7991, which isolates the high-temperature underprediction
that the next reaction-temperature study must address.

The exact comparison is in
`results/predictive_partition_metrics.csv` and
`results/predictive_partition_summary.json`. The complete 257-row plotted
table is `figures/predictive_partition_plot_data.csv`; PNG, SVG, and PDF
figures are `figures/predictive_partition_evidence.*`. The immutable Engine
wheel SHA-256 is
`e14288867d4fb5bc1367dd0de490aeb1551f1613074aced0a8d28432ca762f23`.

This result resolves numerical row coverage but does not finish the physical
parameterization. The CO2--MEA dispersion coordinate is weakly identified,
and the systematic temperature trend remains after the best retained Born,
permittivity, and induced-association settings. The next calculation is a
small source-centered R4/R5 temperature-correlation sensitivity against the
training speciation temperatures, followed by frozen replay on the reserved
and pressure-challenge rows.

### R4/R5 temperature-correction result

The follow-up used corrections that are zero at 313.15 K and linear in
reciprocal temperature, with coordinates defined as $\Delta\ln K$ at 353.15 K.
Centered finite differences on the ten 333.15/353.15 K training speciation
states produced a locally identifiable two-column sensitivity matrix
(condition number 27.4). Its linear candidate was
$\Delta\ln K_{R4}=-0.5268$ and $\Delta\ln K_{R5}=-2.0$ at 353.15 K; R5 reached
the exploratory bound.

The candidate improved the complete training-speciation RMS factor from
1.6900 to 1.5339, while reserved speciation changed from 2.3343 to 2.3476.
It failed the pressure replay decisively: the 27-row temperature-challenge RMS
factor increased from 2.3926 to 9.6479. The 333.15 K and 353.15 K factors were
4.4397 and 21.3844, respectively, with strong negative bias. The candidate is
rejected, the source R4/R5 correlations remain unchanged, and reaction
temperature coefficients must not be estimated from speciation alone.

The compact rejection receipt is
`results/reaction_temperature_rejection.json`. The final retained and
calorimetry-balanced comparisons remain under
`results/candidate_speciation_comparison/` and
`results/calorimetry_balanced_reaction_validation/`.

## CO2--water binary transfer and retained predictive candidate

The independently qualified Pabsch et al. CO2--water model was transferred
next. Its reciprocal induced-association edges were already retained. The
remaining source correlation is

\[
k_{CO2,H2O}(T)=0.0122+3.016\times10^{-4}(T-298.15\ \mathrm{K}).
\]

The binary qualification evaluates all 39 nonzero-composition Kiepe et al.
rows with log-pressure RMSE 0.2123 and median factor 1.1703. Transferring the
complete correlation without refitting leaves speciation unchanged and
improves the 333.15--353.15 K pressure-challenge factor from 2.3926 to 2.1148,
but worsens training pressure from 2.0208 to 2.5499 and reserved pressure from
2.2814 to 2.4846. The fitted CO2--MEA dispersion coefficient cannot repair
that tradeoff: its pressure log-sensitivity RMS is only 0.00161, and a bounded
Gauss--Newton move changes the linearized log-RMSE by less than 0.001.

The retained predictive candidate therefore transfers the source slope while
anchoring the interaction to zero at the 313.15 K MEA calibration temperature:

\[
k_{CO2,H2O}(T)=3.016\times10^{-4}(T-313.15\ \mathrm{K}).
\]

This candidate evaluates all 119 states and all 257 pressure/speciation
targets with zero failures. Training and reserved metrics remain unchanged to
numerical precision, while the pressure-challenge RMS factor improves from
2.3926 to 2.2103. At 333.15 K the factor changes from 2.0288 to 1.9935 and
mean log bias from -0.1665 to -0.0547. At 353.15 K the factor changes from
2.9087 to 2.5168 and bias from -0.7991 to -0.5925.

One exact-Jacobian two-ion update under the full Pabsch correlation was also
tested. Its locally well-conditioned direction proposed
$\sigma_{MEAH+}=1.6815$ A and $\sigma_{MEACOO-}=3.0926$ A. The nonlinear
replay improved training factors to 1.8276 pressure and 1.6646 speciation but
worsened reserved factors to 3.1472 and 3.0587 and the temperature challenge
to 2.7647. It is rejected as overfit; the source-partitioned ion diameters are
retained.

The exact retained settings are
`results/retained_predictive_parameter_settings.json`, and the four-way
comparison is `results/predictive_structure_comparison.csv`. The frozen
reference replay was also simplified: certified continuation references
provide the same pressure and speciation values as the second owner
evaluation (exact pressure parity and maximum mole-fraction difference
$1.7\times10^{-16}$). Twelve-core replay of 70 changed states fell from the
earlier roughly 25-minute double-solve workflow to about 4.5 minutes without
changing any physical or numerical tolerance.

The complete retained 119-state, 257-target pressure/speciation comparison is
rendered in PNG, SVG, and PDF as
`figures/retained_predictive_candidate_evidence.*`. Its exact plotted values
are `figures/retained_predictive_candidate_plot_data.csv`; the partition
metrics are `results/retained_predictive_candidate_metrics.csv`.

The pressure-aware R4/R5 temperature correction was then replayed on top of
the retained anchored CO2--water slope. It provided no incremental pressure
benefit: the challenge factor changed from 2.2103 to 2.2126, while training
and reserved speciation worsened from 1.6900 to 1.7397 and from 2.3353 to
2.5054. The combined correction is rejected and the source reaction
correlations remain unchanged.

The replay path now uses all requested logical CPUs, one BLAS thread per
worker, one certified solve per state, and a 2-start homogeneous search with
the original 10-start search retained as fallback. The complete 70-state
replay passed with zero failures in 264.9 s. Profiling a difficult 353.15 K
state showed that parameter parsing took only 0.027 s; native chemical
equilibrium, homogeneous reactive evaluation, and source-reference transfer
dominated the 27.5 s profile. Exact timing evidence is in
`results/solver_performance_diagnosis.json`. Further material acceleration
therefore requires a certified warm-start or prepared-state Engine path across
nearby parameter evaluations, not weaker physical or convergence criteria.

## Newly extracted source data and external challenge

The curated observation inventory now contains 12 source blocks and 585
structured rows. Wong et al. (2016) Table 4 supplies 27 explicit 30 wt% MEA
pressure/loading states. Because every solution also contained 0.517 mol/kg
NaClO4, which is absent from the nine-species model, these rows are an external
challenge rather than regression data. The retained parameter set evaluated 21
of 27 states on each reported loading basis. Its RMS factors are 2.270 on the
pressure-drop basis and 2.637 on the Raman basis; the six high-pressure states
per basis terminate as typed Provider-domain rejections rather than fabricated
penalties. Exact predictions and admission decisions are under
`results/new_source_replay/`; the complete observation/model display is
`figures/new_source_wong2016_replay.*`.

The newly tabulated Raman, NMR, and ATR-FTIR speciation blocks remain held out
until their missing pressure or feed-conversion inputs are source-resolved.
The 158 heat-of-absorption rows are direct data, but the Engine does not yet
expose a complete reference-state absorption-enthalpy observable.

## Calorimetry consistency and balanced reaction-temperature challenge

A no-fit Gibbs--Helmholtz diagnostic was evaluated from completed 313.15,
333.15, and 353.15 K bubble predictions over the common loading interval
0.0888--0.642 mol CO2/mol MEA. Sixty-nine of 86 eligible direct 30 wt%
calorimetry observations lie inside that interval. The retained model gives
RMSE 15.755 kJ/mol CO2 and mean bias -11.118 kJ/mol CO2; the earlier full R4/R5
temperature candidate gives RMSE 14.088 and bias +10.032 kJ/mol CO2.

Interpolating between those two candidates identified the smaller challenge
$\Delta\ln K_{R4}(353.15\,K)=0.02988$ and
$\Delta\ln K_{R5}(353.15\,K)=0.53503$, with both corrections zero at 313.15 K
and linear in reciprocal temperature. Exact nonlinear replay evaluated all 70
pressure/speciation states with zero failures. The pressure-challenge RMS
factor improves from 2.210 to 2.041, while training speciation changes from
1.690 to 1.715 and reserved speciation from 2.335 to 2.418. Its exact
calorimetry RMSE is 10.489 kJ/mol CO2, median absolute error 5.287 kJ/mol CO2,
and mean bias +0.734 kJ/mol CO2.

This is the strongest tested joint pressure/calorimetry correction, but it is
not a replacement for the retained predictive set because it trades away some
independent speciation accuracy. Exact metrics are in
`results/calorimetry_consistency/` and
`results/calorimetry_balanced_reaction_validation/`; the data and all three
model curves are rendered as `figures/calorimetry_consistency.*`.

## Independent pressure--speciation--calorimetry comparison

The retained and calorimetry-balanced sets were compared using three frozen,
non-overlapping evidence blocks: 27 temperature-challenge pressure rows, 67
reserved speciation targets, and 69 direct calorimetry observations. Each
domain error was divided by the retained-set error before aggregation. The
balanced-to-retained ratios are 0.899 for pressure, 1.041 for reserved
speciation, and 0.666 for calorimetry. Equal domain weighting gives a geometric
score ratio of 0.854, so the balanced set reduces the combined normalized error
by 14.6\%.

A 0.01-spaced sweep of all 5151 nonnegative domain-weight combinations prefers
the balanced set for 97.2\% of combinations. The retained set is preferred only
when reserved speciation receives more than 72.5--91.0\% of the total weight;
the exact threshold depends on how the remaining weight is divided between
pressure and calorimetry. Pressure-focused, speciation-focused, calorimetry-
focused, and equal-domain examples all prefer the balanced set.

This comparison ranks the calorimetry-balanced set lower when pressure,
speciation, and heat are all intended outputs; it does not support parameter
adoption or downstream transfer. The weights express engineering priorities
because complete measurement covariance is unavailable; they are not
uncertainty weights. Exact domain errors, priority profiles, the deterministic
grid definition and aggregate result, and the preference boundary are under
`results/independent_evidence_comparison/`. The retained figure and its exact
plotted values are `figures/independent_evidence_comparison.*` and
`figures/independent_evidence_comparison_plot_data.csv`.

### Candidate speciation profiles

The retained, full R4/R5, and calorimetry-balanced candidates were also
compared on the identical frozen speciation target set. Each candidate
evaluates all 131 training and 67 reserved targets with zero failures or
omissions.

| Candidate | $\Delta\ln K_{R4}(353.15\,K)$ | $\Delta\ln K_{R5}(353.15\,K)$ | Training RMS factor | Reserved RMS factor |
|---|---:|---:|---:|---:|
| Retained source correlations | 0 | 0 | 1.690 | 2.334 |
| Full R4/R5 candidate | 0.05385 | 0.96427 | 1.740 | 2.505 |
| Calorimetry-balanced candidate | 0.02988 | 0.53503 | 1.715 | 2.418 |

The balanced candidate is therefore the intermediate reaction-temperature
correction, not the full correction. It sacrifices some speciation accuracy
relative to the retained set, but substantially less than the full R4/R5
candidate. The per-species observations and model trajectories are rendered
as `figures/speciation_fit_retained.*`,
`figures/speciation_fit_full_r4_r5.*`, and
`figures/speciation_fit_calorimetry_balanced.*`. Their exact shared plotted
table is `figures/candidate_speciation_comparison_plot_data.csv`; aggregate and
per-species metrics are under `results/candidate_speciation_comparison/`.

## Direct molecular-CO2 external challenge and interaction falsification

Wong et al. (2016), DOI `10.1016/j.jngse.2016.10.029`, Table 3 supplies 29
direct Raman free-molecular-CO2 observations for 30 wt% MEA at 303.15,
313.15, and 323.15 K and 1--60.8 bar. Every source solution contains
0.517 mol/kg NaClO4, which is absent from the current nine-species model, so
these rows are an external challenge rather than regression targets.

The retained and calorimetry-balanced candidates give free-CO2 RMS factors
3.785 and 3.738. An absolute R4 correction of -1.85 improves that factor to
1.740 but worsens the complete training/reserved speciation factors to 3.004
and 2.635. Setting the anchored CO2--water interaction intercept to 0.45 gives
an apparently excellent free-CO2 factor of 1.191 and 12.21% AARD while leaving
complete speciation at factors 1.714 training and 2.477 reserved.

That intercept fails the independent transfer tests. On the 59-row reactive
pressure packet, only 40 rows evaluate even with a declared 1 Pa--100 MPa
pressure interval and multiple pressure starts. The evaluated rows have RMS
factor 8283 and mean log bias 8.96; 19 rows still reach the bubble Newton
iteration limit. On the independent 39-row Kiepe CO2--water binary, the source
Pabsch correlation evaluates 39/39 rows with log-RMSE 0.212, whereas the
reactive-fit intercept evaluates only 11/39 with log-RMSE 0.608 on survivors.

| Additive offset to Pabsch $k_{CO2,H2O}(T)$ | Evaluated binary rows | Failed rows | Log-RMSE on survivors |
|---:|---:|---:|---:|
| 0 | 39 | 0 | 0.212 |
| 0.05 | 38 | 1 | 2.009 |
| 0.10 | 28 | 11 | 3.102 |
| 0.20 | 7 | 32 | 3.611 |
| 0.30 | 9 | 30 | 2.098 |
| 0.433276 | 11 | 28 | 0.608 |

The positive CO2--water intercept is therefore rejected as compensation for
physics absent from this comparison, principally the source salt and possibly
reactive standard-state/model error. The source-compatible induced-association
and anchored temperature slope remain retained. The compact intercept rejection
receipt is `results/co2_water_activity_rejection.json`. The retained and
calorimetry-balanced Wong predictions remain under
`results/wong_free_co2_external_challenge/`; their verified figure is
`figures/wong_free_co2_external_challenge.*`, with 58 exact plotted rows in
`figures/wong_free_co2_external_challenge_plot_data.csv`. Binary evidence is
under `../co2_water_induced_association/results/`.

## Generic pressure-domain handling

Parameter-document source ranges remain provenance. Calculation batches now
expand a copied execution domain to the union of the requested temperatures
and pressures without mutating the source mapping. Reactive-bubble pressure
bounds, optional extra pressure starts, and the continuation radius are
explicit run inputs; no regression dataset supplies a hidden universal
pressure ceiling. Typed failures can be resumed without recomputing completed
states, and partial campaigns always write diagnostics and metrics before
returning failure status.

## Final Issue 70 decision

The assembled evidence supports a negative predictive decision. The retained
candidate is diagnostic only: its optimizer terminated `NO_CONVERGENCE`, its
active scaled Jacobian is weakly identified, the former reserved rows were
opened during model selection, and its Engine wheel does not match the frozen
lock. No untouched replacement validation partition exists. The authoritative
record, generated tables, downstream-property coverage, and explicit transfer
refusal are under `../results/issue_70/`. Predictive export and absorber-column
mapping are prohibited.
