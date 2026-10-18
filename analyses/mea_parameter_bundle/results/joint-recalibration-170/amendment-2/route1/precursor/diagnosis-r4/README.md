# R4 at precursor A: bounded diagnostic probe

**Classification: inconclusive** for the statement that fixed R4 is a principal driver of the bound stops. R4 has a large start-point cost gradient and strong overlap with the seven ion sensitivities. At iteration 40 its gradient is much smaller, both signs of the requested finite R4 changes increase total cost, and moving all five active coordinates inward together with R4 a −0.2 also increases cost. These results do not isolate a principal cause across the three fits. They argue against a simple finite R4 shift rescuing this stopped vector, while leaving coupled re-estimation unresolved.

This is numerical verification of exact local sensitivities and conditional evaluations against the same calibration targets. It is neither a new fit nor physical validation. No parameter is selected. The parent owns independent delivered review and any design amendment; no notebook promotion or manuscript use is claimed.

## Basis and numerical method

R4 is MEACOO⁻ + H₂O ⇌ MEA + HCO₃⁻, with source ln K = a + b_k/T, a = 2.151 and b_k = −1545.3 K. Cost C = ½ Σ w_i r_i² uses the unchanged 203 rows: 25 reacting pressures, 115 unshared logarithmic species targets, 39 Kiepe pressures and 24 stage-4 standardized differences. The 16 overlaps are scored once in stage 4. Difference residual z = (prediction − observation)/(0.1 observation + 0.001); reported pool residuals are z, before multiplying by 1/√24. Jakobsen pools are ratios to total analytical amine; Matin pools are liquid mole fractions.

Exact derivatives use `regression.reaction_coordinate` and `regression.differentiate` at both serialized points, without optimizer iterations. The original ten source-increasing columns retain their declared scales and ties; the R5 native sign is reversed to report increasing source a_k. Added reporting scales are s_a = 0.2 and s_b = 80 K, so a = a₀ + 0.2 q_a and b_k = b₀ + 80 q_b. These scales define diagnostic units only; no bounds or estimation policy are proposed. Rank uses 10⁻¹⁴ times the largest singular value. Conditions depend on these scales; span cosines do not.

The immutable merged-main Engine 84ca269d wheel SHA-256 is `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`. All 12 installed wheel files were byte-compared. The numerical process ran at nice 10 with single-thread BLAS/OpenMP, a 90 CPU-s limit and 90 s alarm. All 203 targets returned at both exact points and each of four finite evaluations.

## 1. Local influence

| Point | Column | Scaled cost gradient | Cost gradient per source unit | Cosine with 7-ion span | Signed cosine with R5 a_k |
|---|---|---:|---:|---:|---:|
| A-start | R4_a | 19.2576339849 | 96.2881699247 | 0.99979115874 | 0.994382652384 |
| A-start | R4_b_k | 26.1953106424 | 0.327441383029 | 0.999812850932 | 0.995181495579 |
| A-iteration-40 | R4_a | 0.00774727634295 | 0.0387363817148 | 0.998594886541 | 0.197559040281 |
| A-iteration-40 | R4_b_k | 0.00886886690661 | 0.000110860836333 | 0.999205236464 | 0.214432517595 |

A positive gradient favors decreasing the source coefficient for an infinitesimal step. At iteration 40 the a-gradient is +0.03873638 per unit a, but the −0.2 finite step overshoots any improvement that the first-order term suggests. A local gradient cannot predict a finite-step cost by itself. The unconstrained ion-span projection permits both signs of ion motion and does not prove a feasible bounded compensation.

| Point | Columns | Rank | Condition number |
|---|---|---:|---:|
| A-start | 10 | 10/10 | 12290.8523983 |
| A-start | 10+R4_a | 11/11 | 18512.4722621 |
| A-start | 10+R4_b_k | 11/11 | 13707.8858928 |
| A-start | 10+2 | 12/12 | 31148.4153972 |
| A-iteration-40 | 10 | 10/10 | 1078.53531598 |
| A-iteration-40 | 10+R4_a | 11/11 | 1284.2829953 |
| A-iteration-40 | 10+R4_b_k | 11/11 | 1495.15462396 |
| A-iteration-40 | 10+2 | 12/12 | 1829.02896372 |

All augmented matrices retain full rank at the stated cutoff, with increased condition numbers. No covariance or parameter confidence interval is inferred from the unconverged point. The full spectra and matrices are retained in [local-influence.json](local-influence.json), [start matrix](A-start-weighted-matrix.json) and [iteration-40 matrix](A-iteration-40-weighted-matrix.json).

### Five largest signed target contributions by absolute magnitude

Each term is r_i J_ij for the weighted residual and scaled coordinate; all 203 terms sum to the gradient. `HCO3-` in a Matin ID denotes its bicarbonate-plus-carbonate pool.

| Point | Column | Target | Scaled contribution |
|---|---|---|---:|
| A-start | R4_a | `Jakobsen2005_state_011::HCO3- + CO3^2-` | 16.2269195071 |
| A-start | R4_a | `Jakobsen2005_state_022::HCO3- + CO3^2-` | 0.70392458886 |
| A-start | R4_a | `Matin2012_state_016::HCO3-` | 0.592541092447 |
| A-start | R4_a | `Matin2012_state_019::HCO3-` | 0.585210160838 |
| A-start | R4_a | `Matin2012_state_009::HCO3-` | 0.329175981305 |
| A-start | R4_b_k | `Jakobsen2005_state_011::HCO3- + CO3^2-` | 22.1414559197 |
| A-start | R4_b_k | `Jakobsen2005_state_022::HCO3- + CO3^2-` | 0.899153235012 |
| A-start | R4_b_k | `Matin2012_state_016::HCO3-` | 0.808515903049 |
| A-start | R4_b_k | `Matin2012_state_019::HCO3-` | 0.798512926267 |
| A-start | R4_b_k | `Matin2012_state_009::HCO3-` | 0.449157061306 |
| A-iteration-40 | R4_a | `Jakobsen2005_state_011::HCO3- + CO3^2-` | 0.0375455982823 |
| A-iteration-40 | R4_a | `Matin2012_state_016::HCO3-` | -0.0211803381955 |
| A-iteration-40 | R4_a | `Matin2012_state_016::MEA` | -0.00860084480202 |
| A-iteration-40 | R4_a | `Matin2012_state_009::HCO3-` | -0.00824297272276 |
| A-iteration-40 | R4_a | `Jakobsen2005_state_022::HCO3- + CO3^2-` | 0.00659000182215 |
| A-iteration-40 | R4_b_k | `Jakobsen2005_state_011::HCO3- + CO3^2-` | 0.0512305622135 |
| A-iteration-40 | R4_b_k | `Matin2012_state_016::HCO3-` | -0.0289003420713 |
| A-iteration-40 | R4_b_k | `Matin2012_state_016::MEA` | -0.0117357595798 |
| A-iteration-40 | R4_b_k | `Matin2012_state_009::HCO3-` | -0.0112474470036 |
| A-iteration-40 | R4_b_k | `Jakobsen2005_state_022::HCO3- + CO3^2-` | 0.0084176935298 |

[All signed row contributions](target-gradient-contributions.csv) include the full cancellation, including positive and negative terms.

## 2. Iteration-40 finite evaluations

| Change from iteration 40 | Total cost | Reacting pressures, 25 | Unshared species, 115 | Kiepe, 39 | Stage 4, 24 |
|---|---:|---:|---:|---:|---:|
| Unchanged | 0.587102914023 | 0.0644782745271 | 0.0348614530959 | 0.00122766160347 | 0.486535524796 |
| R4-a--0.4 | 0.66878044172 | 0.0597406866046 | 0.0494866026361 | 0.00122766160347 | 0.558325490876 |
| R4-a--0.2 | 0.606282543608 | 0.0603762392568 | 0.0416950093221 | 0.00122766160347 | 0.502983633426 |
| R4-a-+0.2 | 0.628269027379 | 0.0718785532783 | 0.0289474839628 | 0.00122766160347 | 0.526215328534 |
| R4-a--0.2-plus-all-five-interior | 0.609726684867 | 0.0570885427963 | 0.0348057731729 | 0.00122766160347 | 0.516604707295 |

The combined inward move sets both segment diameters to 5.7 Å, both Born diameters to 1.1 Å, and R5 a_k to 2480 K. Packing and Debye–Hückel diameters remain tied to 0.88 times the segment diameter, hence 5.016 Å. R4 a becomes 1.951, and b_k remains −1545.3 K. All other coordinates stay at iteration 40. This is one combined evaluation, not five separate inward evaluations.

| Change | Jakobsen 011 pool z | Jakobsen 022 pool z | Matin 009 pool z | Matin 019 pool z | Matin 016 pool z |
|---|---:|---:|---:|---:|---:|
| Unchanged | 0.98365400429 | 0.396270769652 | −1.61917587897 | −0.190706177165 | −1.69409831303 |
| R4-a--0.4 | -0.58528388237 | -0.381403617265 | -1.82804754088 | -0.667839436112 | -2.25506988441 |
| R4-a--0.2 | 0.136024730758 | 0.00238508299111 | -1.73211737344 | -0.435652830065 | -1.98440197152 |
| R4-a-+0.2 | 1.97350008484 | 0.800817865419 | -1.48700977246 | 0.0672939163367 | -1.38437718727 |
| R4-a--0.2-plus-all-five-interior | 0.590010386614 | 0.883909693431 | -1.66655351471 | -0.20071496291 | -1.86561094135 |

R4 a −0.2 reduces the Jakobsen pool residuals to +0.1360 and +0.002385 but makes all three Matin pools more negative. The remaining costs therefore prevent interpreting the two Jakobsen improvements as a joint-objective rescue. [Finite evaluations](finite-evaluations.json) retain predictions, scales and residuals for every pool; [all target values](finite-targets.csv) retain all four complete evaluations.

## 3. Source law and retired adjustment

The selected source is Tong et al. (2012), *Solubility of carbon dioxide in aqueous solution of monoethanolamine or 2-amino-2-methyl-1-propanol: Experimental measurements and modelling*, DOI [10.1016/j.ijggc.2011.11.005](https://doi.org/10.1016/j.ijggc.2011.11.005), §3.1 p.43 reaction VI, Eq. (9), Eq. (12), and Table 5 p.44 K5,MEA. Equation (9) is K5 = (m_MEA m_HCO3 / m_MEACOO) (γ_MEA γ_HCO3 / γ_MEACOO), with solvent water omitted. Table 5 gives a_i = −1545.3, b_i = c_i = 0 and d_i = 2.151 in Eq. (12): ln K = a_i/(T/K) + b_i ln(T/K) + c_i(T/K) + d_i. It states a mol/kg basis and validity 293–323 K, and footnote b identifies conversion from Aroua’s original correlation. The repository adopts an aqueous molality standard of 1 mol/kg at infinite dilution in water, source reference pressure 100 kPa, and the explicit 293.15–323.15 K interval; it does not convert Tong R4 from a mole-fraction standard.

The primary source is Aroua, Benamor and Haji-Sulaiman (1999), *Equilibrium Constant for Carbamate Formation from Monoethanolamine and Its Relationship with Temperature*, DOI [10.1021/je980290n](https://doi.org/10.1021/je980290n). Its p.888 reaction (i), Eqs. (1)–(2), define the reverse, carbamate-formation constant from concentration quotients and activity coefficients, using mol/dm³. Its p.890 Eq. (14) is log₁₀ K1 = −0.934 + 671 K/T, for formation. Inversion and multiplication by ln 10 give the hydrolysis form approximately 2.15061448 − 1545.03460 K/T, consistent with Tong’s rounded coefficients but not a new basis conversion. Aroua’s methods p.887 and Table 3 p.890 cover 298, 308, 318 and 328 K; the paper is not itself a 293.15–323.15 K measurement declaration. Reported coefficient standard errors are 0.272 and 85 K in its base-10 formation form; covariance is not supplied here. These cannot be converted into an independent uncertainty for the present dense MEA model without further assumptions. Tong’s adopted molality presentation and Aroua’s original concentration presentation remain distinguished.

Source checks: the worktree has no ignored `literature/` shelf. The main-checkout `literature/README.md`, `index.csv` and `missing-markdown.csv` were read; Tong and Aroua have no full-paper Markdown listed in the latter. The existing Zotero PDFs were read directly through Poppler, and Tong pp.43–44 and Aroua p.890 were visually checked. Live `wiki-source` identifies parents/attachments Tong `5FB2UHQZ`/`2SVMJQ58` and Aroua `L8GDWZEW`/`93Y7NVMH`, with no Markdown companions; PDF hashes are retained in [source-identities.json](source-identities.json). The Tong PDF hash matches the repository evidence map. No conversion service or library write was used. The actual source passages, rather than the metadata abstracts, support the statements above.

On main at `5082ba4f03850c2bdeed2f3e0e2e8c1c0718b221`, neither `results/co2-r4-calibration/` nor `analyses/mea_parameter_bundle/results/co2-r4-calibration/` exists or has path history on main. The historical page is `analyses/mea_parameter_bundle/co2-r4-calibration/index.qmd`, and its retained numerical owner is `results/best-in-slot-campaign/local-best-grid-summary.csv`. Git history traces the retained grid to `97e9c15ca6b6ed78a0e9453ae80c5c3fd0ab8411`. The selected row `local-p0.15-db-350-eps+0.025` has a = 3.3515778177997895 and b_k = −1895.3 K. Relative to the current source law this is Δa = +1.2005778177997895 and Δb_k = −350 K; Δln K(333.15 K) = +0.15. The implementation uses Δa = 0.15 − (−350)/333.15. Its 2.5% CO₂ dispersion increase was coupled to that chemistry change, so historical scores cannot identify an R4 effect alone. Later reaction-temperature changes are a separate historical adjustment, not this grid move.

**Yes: the selected 293.15–323.15 K source interval is narrower than the design’s 293.15–393.15 K reactive use.** The upper 70 K extends beyond that adopted source interval. The current design explicitly keeps R4 source-fixed in §3 and in both alternatives. This diagnosis does not qualify that extrapolation or infer that extrapolation caused the 20 °C discrepancies, which occur at the lower edge of the adopted interval.

## 4. Options for the parent, without selection

- Free one R4 reference-level coordinate in both Route 1 and Route 2, written ln K(T) = L_p + b_k(1/T − 1/T_p) with a declared pivot T_p and source b_k fixed. This adds one degree of freedom and permits a coherent level change; it retains the source temperature dependence and may trade strongly with ion activities. It requires an amended declaration, scales/bounds and matched assessment; a pivot alone does not remove ion overlap.
- Free both L_p and b_k in both alternatives. This permits level and temperature-dependence changes and adds two degrees of freedom. Both local augmented matrices are full rank, but their condition numbers rise; this is not proof of estimability, uncertainty or temperature transfer. New coefficients would be empirical calibrations rather than the unchanged source law.
- Keep R4 fixed. This preserves the declared source law and its limited domain, leaves the observed cost trade-offs and five bound-active coordinates unresolved, and requires the parent to address the existing stop before any continuation. These probes do not prove another fit will fail or identify which other hypothesis is correct.

No option is selected. Changing a shared fixed reaction changes the scientific question and requires the parent’s design/owner decision.

## Numerical checks, timing and limits

The ten existing exact columns replay within 3.433e-14 absolute, and weighted residuals within 2.346e-13. The added columns satisfy J_b = J_a (80/0.2)/T to 4.441e-16 absolute. Saved family memberships, cost sums, row counts and availability are checked in [verification.json](verification.json). R4 centered-difference verification, fits, confidence intervals and new physical observations are outside this probe; no such evidence is claimed.

Measured numerical work uses 38.490062000 CPU-s / 38.481418740 active wall-s. A conservative 25 CPU-s / 25 s covers all source work, inspection, report algebra, checks and commit. **Total charge: 63.490062000 CPU-s / 63.481418740 active wall-s**, within 120/120. Cumulative program charge is **2267.535137720 CPU-s / at least 702.764352127 active wall-s**. Remaining program allowance is at most 141732.464862280 CPU-s / 20897.235647873 s, less unknown earlier overhead. Remaining precursor accounting is 6932.479424000 CPU-s / 365.760287605 s; this does not authorize continuation. [Accounting](timing-and-program-accounting.json) adds the preceding diagnosis once.

Only this evidence directory is changed. `probe.py.txt` and `report.py.txt` are inert retained calculation text; zero production or executable files are added. No fit, design choice, subagent, service action, push, merge or GitHub write occurred. Independent review remains with the parent.
