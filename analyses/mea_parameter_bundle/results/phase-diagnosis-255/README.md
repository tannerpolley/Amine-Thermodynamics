# MEA liquid-split diagnosis at fixed parameters

Stage 1 of [issue #255](https://tnnrpolley21-ms-7c95.taila72856.ts.net:3000/tannerpolley/Amine-Thermodynamics/issues/255). These are fixed-model predictions and numerical verification, not physical validation. No parameter fitting or parameter adoption is performed. Independent delivered review and investigator promotion for manuscript use remain open.

## Question and basis

Which parameter directions remove the water-poor, ion-rich second liquid, and what calibration cost do they incur? Does the final parameter set lie immediately next to a detected split?

The starting evidence is the complete [162-state census](../engine-3e83e19c-phase-search/run-2/README.md), the [earlier phase diagnosis](../joint-recalibration-170/amendment-6/selected-checks/phase-diagnosis/report.md), and the #170/#212 history in the [research notebook](../../joint-recalibration/index.qmd). The census found 54 states with resolved descent and 51 confirmed paths across 32 states for the wider-bound set. The final set had no resolved descent at 162 states. Earlier Born and ion-pair moves weakened particular descents but did not establish a replacement parameter set.

The Engine wheel is built from merged commit `3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, SHA-256 `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`. The wider-bound parameter file is `efb2a9abe3787410734394f5ee32e6eade42d7cb6f5ad23445a357423690b2f3`; the final file is `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`. Installed Engine files are checked against the wheel by the existing verification function. No Engine checkout is imported or edited.

Temperatures are 313.15, 318.15, 333.15, 353.15, 373.15 and 393.15 K; analytical loadings are $10^{-5}$, 0.05, 0.1, 0.2, 0.256, 0.3, 0.4, 0.5 and 0.6 mol CO₂/mol MEA. Pressures retain the census's 0.50, 0.80 and 0.95 fractions of the final set's bubble pressures. The feed basis is 9.7292821 mol MEA, 76.9751925 mol water and $9.7292821\alpha$ mol CO₂. Every probe uses these same physical pressures; bubble calculations under each mapping determine the admissible parent topology rather than redefining the pressure grid.

## Method and interpretation

Each fixed vector first re-solves and searches the 32 states with a retained confirmed split. A vector without resolved descent there is searched at the remaining 130 states. Consequently, a 32-state result with descent is a sufficient counterexample, not a fresh 162-state census. A 162-state result without descent is only finite-search evidence. The parent solve, bubble calculation and nine liquid/vapor trial starts use the existing `family_job` function and its numerical limits, with a classified-row tolerance of $10^{-10}$. Each point starts independently, without continuation between points. The unchanged controls recover the retained wider-bound cost and the final cost and density counts.

The MEAH⁺ size coordinate retains its original ties: Debye–Hückel diameter equals segment diameter and packing diameter equals 0.88 times segment diameter. Interaction constants change alone unless the probe name contains `water-law`, which interpolates both the constant and reciprocal-temperature slope toward the final values. Born probes change the MEAH⁺ and carbamate Born diameters together. Every other coefficient, including reaction laws, stays at the named starting set.

Each vector replays the exact 307 observation rows and their original weights, with no optimizer call. Cost is one half the sum of squared weighted residuals. Loaded-density counts use the 47 original rows and $|r_i|\leq2$ with their assigned scales. These are calibration diagnostics, not new independent measurements. The scales do not establish parameter uncertainty.

### Energy accounting

[contributions.csv](contributions.csv) retains all 51 confirmed paths. Two different differences are kept explicitly:

- `poor_minus_rich_*` is the residual molar Helmholtz contribution in the water-poor liquid minus that in the water-rich liquid, divided by $RT$. Different compositions make this unsuitable as a stability test on its own.
- The unsuffixed contribution columns are the extensive change between the entire confirmed split state and its parent, $\sum_{p,\mathrm{split}}n_p a_{p,c}^{res}/RT-\sum_{p,\mathrm{parent}}n_p a_{p,c}^{res}/RT$, including any vapor. `pv` is the corresponding $PV/RT$ change. `ideal_and_standard` is the remainder obtained by subtracting those terms from the native total $\Delta G/RT$; it is not an independently evaluated ideal-gas/chemical decomposition.

The full weighted comparison is required because the split changes phase amounts and reactive speciation. Contributions are not separately minimized, and the largest negative term does not by itself identify an erroneous equation. Cation-mixing and polar contributions are zero for these states. All five requested residual contributions are evaluated by the pinned wheel at the retained compositions and densities; their sum is checked against its residual Helmholtz value to $10^{-10}$.

## Diagnosis and fixed-parameter costs

Strengthening MEAH⁺–water attraction is sufficient to remove detected descent in this model. The least-cost complete removing vector **among the tested fixed vectors** is `wide-water--0.175`: cost **835.050161950**, with **40/47** loaded densities within twice their assigned scales. This is neither a continuous constrained optimum nor a fitted replacement. [probes.csv](probes.csv) retains every vector and result; each named folder contains its full parameter mapping, 307-row replay, state reduction and compressed raw phase calculations.

| Fixed vector | Searched states | Descent states | Incomplete states | 307-row cost | Densities within 2s / 47 |
|---|---:|---:|---:|---:|---:|
| wide | 32 | 32 | 0 | 148.211508 | 47 |
| wide-size-5.35 | 32 | 24 | 0 | 654.423073 | 0 |
| wide-pair--0.8 | 32 | 19 | 0 | 182.429824 | 47 |
| wide-pair--0.5 | 32 | 8 | 0 | 350.057836 | 47 |
| wide-born-4.5 | 32 | 23 | 0 | 148.755097 | 47 |
| wide-water--0.1 | 32 | 3 | 0 | 420.193873 | 46 |
| wide-water--0.125 | 162 | 7 | 1 | 537.890582 | 42 |
| wide-water--0.15 | 162 | 0 | 1 | 676.242101 | 41 |
| wide-water--0.175 | 162 | 0 | 0 | 835.050162 | 40 |
| wide-water--0.2 | 162 | 0 | 0 | 1014.112302 | 40 |
| wide-water-born-4.0 | 162 | 6 | 0 | 439.300228 | 40 |
| wide-water-born-4.5 | 162 | 9 | 0 | 428.391127 | 42 |
| wide-water-pair--0.8 | 162 | 5 | 0 | 618.934765 | 42 |
| wide-water-pair--0.5 | 162 | 0 | 0 | 1022.863181 | 39 |
| final | 162 | 0 | 0 | 148.878939 | 44 |
| final-size-5.34 | 162 | 0 | 1 | 148.904194 | 45 |
| final-size-5.2 | 162 | 0 | 0 | 158.499701 | 7 |
| final-size-wide | 162 | 0 | 0 | 677.891223 | 0 |
| final-water--0.499 | 162 | 0 | 1 | 148.915395 | 44 |
| final-water--0.49 | 162 | 0 | 0 | 152.355129 | 44 |
| final-water--0.35 | 162 | 0 | 0 | 954.156709 | 37 |
| final-water--0.3 | 32 | 5 | 0 | 1593.774837 | 33 |
| final-water--0.2 | 32 | 32 | 0 | 3456.522305 | 24 |
| final-pair | 162 | 0 | 1 | 149.014738 | 44 |
| final-born | 162 | 0 | 1 | 148.881147 | 44 |

The cation size alone, ion-pair relaxation alone and paired Born-diameter reductions alone leave counterexamples. The Born moves preserve all 47 density checks but do not remove splitting. Larger cation size severely worsens the fixed-vector density score. Water attraction and the cation dispersion-energy/size combination must be considered together: the final vector also has MEAH⁺ dispersion energy 177.8933 K rather than 300.3371 K and water-interaction slope −41.6196 K rather than +18.4207 K. This stage does not vary that dispersion energy, so it cannot identify a unique optimal partition between size, energy and interaction parameters.

At wider-bound water constant −0.125, no descent remains among the original 32 confirmed states, but seven of the other 130 states descend. A search limited to the original split witnesses would have missed them. At −0.15 no descent is found but one search is incomplete; at −0.175 all 162 searches complete with no resolved descent. This brackets the first **demonstrated complete removal** along this sampled direction between −0.125 and −0.175; it does not assert monotonicity between evaluations or certify every intermediate value.

![Fixed water-interaction changes and objective cost. Points are independent fixed-model evaluations; the logarithmic cost axis exposes the large range. No error bars are assigned because this is a deterministic parameter probe, not a parameter-confidence calculation.](water-interaction-cost.png)

### Coupled energy change

At the strongest confirmed path, state 133, trial 3, 333.15 K, loading 0.5 and pressure 21175.719 Pa, the split lowers Gibbs energy by 7569.9205 J on the stated feed basis. The following extensive changes are divided by RT; the unit is consequently mol on this extensive convention, not a per-mole free-energy difference:

| Contribution | Split minus parent, divided by RT |
|---|---:|
| hard_chain | 29.937183381 |
| dispersion | -57.868857636 |
| association | -18.231820259 |
| debye_huckel | -10.349016784 |
| born | -106.233887620 |
| pv | -5.696099288 |
| ideal_and_standard | 165.712944290 |
| delta_g_over_rt | -2.729553915 |

The corresponding poor-minus-rich *molar* residual Helmholtz differences, divided by RT, are dimensionless:

| Contribution | Poor minus rich |
|---|---:|
| hard_chain | -0.975069506 |
| dispersion | 2.603473503 |
| association | 1.523680564 |
| debye_huckel | -0.732102459 |
| born | -37.363121467 |

Water mole fractions are 0.590900152 and 0.973235253. The native full Gibbs decrease is small compared with opposing individual terms. Born, dispersion, association and Debye–Hückel changes favor this split; hard-chain and the ideal/standard remainder oppose it. Across all 51 paths the Born change can have either sign, so this is not evidence that the Born term alone causes every split.

### Distance of the final set from detected descent

Moving the final cation segment diameter from 5.35 Å all the way to the wider-bound value 4.15535743 Å still returns no resolved descent with all 162 searches complete. At 5.34 Å and 5.30 Å one search is incomplete, so those individual evaluations cannot certify absence of descent, even though larger tested inward moves complete. The observed behavior does not establish a monotone stability interval.

Changing final water interaction from −0.5 to −0.49 and −0.35 also gives complete searches without descent. The move to −0.2 gives resolved descent at all 32 original confirmed states. At −0.3, five of those 32 states descend, with minimum tangent-plane distance −0.00705527. The sampled onset is therefore between −0.35 and −0.3, an increase of 0.15–0.20 from the final constant, with every other coefficient fixed. Thus the tested final vector is not poised at an immediate split when its size or water bound is relaxed. This is a directional finite-search result, not the distance in the full 16-dimensional parameter space. Near-zero trial tangent-plane values around 1e−13 occur at coincident phases and do not measure proximity to an instability surface.

The 0.001 water-interaction move, the 0.01 ion-pair move and the paired 0.01 Å Born move have no detected descent but contain an incomplete search each. The Born case also has one parent that does not pass the local minimum checks. They remain unresolved numerical evidence. The larger water move of 0.01 completes. [validation.json](validation.json) identifies all parent states failing numerical admission; the raw calculations retain optimizer and curvature diagnostics. Resolved descents at other admitted states remain counterexamples even when a different state is unresolved.

### Falsifier and remaining decision

The issue's universal falsifier is **not met**: an allowed single water-interaction change and allowed small groups remove resolved descent on the complete finite grid. Therefore this diagnosis does not force a model-form change. It also does not prove that a low-cost stable fit exists inside physically justified bounds. The present cost increases and density losses are the reason to propose a constrained refit rather than adopt any fixed removing vector. All numerical search limits and unknown trials remain part of that proposal.

## Engine fitting capability

[engine-capability.json](engine-capability.json) records executable refusals and hashes of the installed wheel interfaces. `epcsaft.regression.observation(..., kind='stability', ...)` refuses the unknown quantity. An observation whose phases request `Discover()` is refused with `a regression observation needs declared phases`. The installed `ObservationKind` enumeration has no stability quantity; `fit` accepts observations, hydration holds, final error checks and guarded minimax, but no stability functional or callback. The check metrics compare existing observations to measured values; they cannot express a tangent-plane minimum. Declaring a second liquid and fitting its amount would not enforce absence of other lower-Gibbs states.

The required Engine capability is a native parameter-fitting stability constraint or separately weighted penalty evaluated at each candidate vector, for declared reactive feeds, temperatures, pressures and trial supports. It must:

1. Build the parent state and trial searches with the candidate EOS parameters **and** candidate reaction laws, retaining charge and material balance and liquid-only ionic supports.
2. Return signed tangent-plane/descent values with finite-split feasibility and numerical error estimates. A failed parent or incomplete trial search must remain unavailable, rather than contribute zero penalty.
3. Supply parameter derivatives for admitted trial branches, account for branch changes and ties, and expose failed derivative or feasibility evaluations to the fitting driver. A smooth local derivative cannot be assumed at a minimum's branch switch.
4. Support a no-resolved-descent constraint, or an explicitly scaled negative-descent penalty, with declared work limits and separate reporting of the original 307-row cost and stability penalty. Numerical tolerances must derive from the native error estimates, not an arbitrary thermodynamic offset.
5. Retain per-state evidence at the final vector and permit an independent, denser final search. The wider-bound census (54/162 descent states) and final census (0/162) supply reference cases; the present fixed probes supply parameter-direction cases.

This is a requested Engine-owner design, not an Engine implementation or an opened Engine issue. The orchestrator owns that issue and any wheel publication. A future capability must be qualified on a new immutable wheel built from merged Engine main before final use here.

## Proposed stable refit for owner and design review

Keep the current model form initially. Preserve the 307 observation roles, weights, reaction conventions and density scales. Fit with a native stability constraint rather than using the 5.35 Å size restriction as a substitute for searching stability. Use the final set and the wider-bound set as distinct proposed starts; a fixed removing vector is diagnostic evidence, not automatically a scientifically acceptable start or replacement.

The owner and design reviewer should approve the stability residual/constraint and its numerical handling before execution. Propose a training grid that retains all 162 physical states and adds intermediate temperatures and loadings, further pressures and additional CO₂-free MEA strengths. A concrete candidate for discussion is 313.15–393.15 K at 10 K increments, loading increments of 0.025 up to 0.6, 20/30/40 mass % MEA, the retained pressure fractions and fixed-pressure states represented in the observation set. This grid is a proposal; reference-pressure construction, applicability and final work budget still need design review. Retain a separate denser assessment grid that does not steer fitting.

Use the existing parameter-source and volumetric evidence to justify diameter, dispersion, ion-pair and Born bounds individually. Neither the historical box nor a stability-removing value becomes a physical bound merely because it works numerically. Report which coordinates remain on justified bounds and compare the original objective and all 47 density residuals. Do not reject a feasible stable fit solely for missing the historical cost. If no stable fit with acceptable calibrated properties exists inside source-supported bounds, return to model-form design, particularly the ion–solvent/ion-pair and dielectric–Born treatment, instead of tightening a new arbitrary bound.

## Literature basis and limits

The actual methods and results read here are Baygi and Pahlavanzadeh (2015), §§2, 3.2.1, 3.3 and 4, and Bülow, Ascani and Held, *ePC-SAFT advanced, Part I*, §§2.1–2.2 and 3.1–3.3, together with its corrigendum. [literature-hashes.json](literature-hashes.json) verifies the local reading copies against their indexed Zotero sources, including the corrigendum. Baygi fits neutral binary VLE, combines PC-SAFT with ideal chemical speciation, and assesses ternary pressures/speciation; it does not supply physical limits for these independently fitted ionic coordinates. Bülow treats concentration-dependent dielectric/Born effects, reuses ion parameters fitted in aqueous electrolytes and assesses solvation/transfer and activity properties of inorganic salts. Those systems are an analog, not physical validation of MEAH⁺ or carbamate. The corrigendum corrects activity-coefficient parameter results in its Figs. 6–7; those figures are not used numerically here.

The supported diagnosis is a property of the exact model, parameter vectors, finite search and feed domain. No liquid–liquid experimental observations are introduced. The issue's statement that the split is physically spurious remains its motivating premise, rather than a newly established exhaustive literature conclusion. Directional parameter brackets are not confidence intervals or a globally nearest instability surface. Unresolved searches cannot be relabelled stable. No stage-2 fit, manuscript edit or parameter promotion is authorized by this result.

## Reproduction and delivery checks

From the repository root, with the pinned wheel available at its locked path:

```bash
agent-heavy uv run python analyses/mea_parameter_bundle/scripts/phase_diagnosis_255.py
agent-heavy uv run python analyses/mea_parameter_bundle/scripts/check_phase_diagnosis_255.py
uv run python analyses/mea_parameter_bundle/scripts/plot_phase_diagnosis_255.py
```

The calculation command resumes completed fixed vectors only after checking their saved mappings equal the requested mappings. It does not call a fitter. Each vector retains raw phase calculations in `phase-results.json.gz` and all observations in `replay.json`. A first reduction assumed every trial supplied a tangent-plane value and stopped on a missing value; `interrupted-point.json` and `initial-run.log` preserve that numerical stopping point. The corrected reduction retains missing quantities as unknown and reruns affected vectors with unchanged solver settings. `provenance.json`, `provenance-resume.json` and `source-hashes.json` bind the wheel, parameter inputs, state list, objective declaration and source files; logs retain the separate calculation runs.

The 48-vector numerical check passes: all vectors have 307 available, tolerance-admitted observations; both unchanged objective and density controls reproduce; all 51 contribution sums close within $7.11\times10^{-15}$ in the native extensive $G/(RT)$ convention. The wheel's independent residual-term sum check passes at every decomposed phase. Parent minimum/feasibility checks are reported individually in `validation.json`, including unavailable cases rather than dropping them. The three new scripts pass the selected undefined/unused-name checks.

Quarto produced the updated joint-recalibration notebook HTML. The subsequent home-page refresh failed because the `snakemake` executable is unavailable in this worktree's rendering environment. No model was rerun by rendering. The normal `manuscript.py refresh` command was bypassed because its `sync()` rewrites the owner's `analyses/_cse-manuscript.json`; that file remains unchanged. No preview service was started or altered. This rendering limitation does not change the retained numbers or the completed notebook source.
