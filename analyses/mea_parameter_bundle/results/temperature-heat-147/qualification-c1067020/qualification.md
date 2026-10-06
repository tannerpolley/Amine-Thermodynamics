# Engine c1067020 qualification stops at the first exact-Jacobian call

The new wheel returns native finite-addition heats of **−68169.42621173232
and −68286.33285346051 J/mol CO2** for 0→0.11 and 0→0.45. These values
are identical to the retained `b83c4250…` results. Historical replay, frozen-law
mapping, independent endpoint/feed assembly, neutral-anchor invariance and
conditioning pass. The ordered run stops at check 5 before returning any heat
Jacobian. **Qualification is incomplete.** No bubble calculation ran.

Evidence type: **numerical verification only**. Negative heat denotes an
exothermic increment in the frozen one-liquid calculation. This run does not
establish calorimetric physical validation, local liquid-vapor admission,
global phase stability, parameter adoption, temperature extrapolation or
absorber/stripper performance. Independent delivered review remains with the parent.

Basis: 313.15 K, 1734000 Pa, 1 mol feed MEA and 7.911062165006594 mol water;
unloaded MEA mass fraction 0.3; initial carbon exactly zero; pure-CO2 feed at
the same temperature and pressure with the prescribed `vapor` hint. The
Phase A chemistry, all five reaction declarations, references, source-law
representations, starts and physical inputs are unchanged. Physical parameter
SHA-256 is `7e9e3f02723700f8b6577681173249c0e7bd2c8c2a098f38a4e0a7e4611852d5`;
physical calorics SHA-256 is
`c94d504e68c6dc6e85d3d950cc51422499846729b1a06994b362040be991924a`.

| Check | Outcome and returned evidence |
|---|---|
| 1. Historical replay | Pass: 84 states and 142 targets, fresh numerical caches, all row prediction differences within their unchanged allowances. Costs and comparisons follow below. Maximum prediction/allowance ratio 0.00012402064066160403. |
| 2. Frozen-law mapping | Pass: 12 R2/R4/R5 values at 293.15/313.15/333.15/353.15 K. Maximum absolute ln K difference 7.815970093361102e−14 against 5e−13. Stored/native polynomial RT² derivative differences zero; R2 reference pressure 101325 Pa, R4/R5 100000 Pa. Identical to the preceding wheel. Frozen source-admission grids and continuation errors remain unchanged. No loaded high-temperature solve occurred. |
| 3. Native 0→0.11 and 0→0.45 values | Native values, exact-zero initial carbon, identical reactions/references, zero feed-balance differences, fixed-pressure endpoints and independent feed root pass. Complete check 3 remains pending because its required §6.1 bubble admission is unrun. |
| 4. Assembly, anchor shift, conditioning | Pass at both loadings; returned numbers follow below. |
| 5. Exact heat Jacobian | Execution failure at the first coordinate declaration, α=0.11. No exact action, finite-difference comparison, truncation estimate or fine/coarse maximum ratio was returned on this wheel. |
| 6. Convergence and conservation | Formal stage unrun after the check-5 stop. Available training and fixed-pressure endpoint diagnostics meet the numerical limits; their maxima follow below. No boundary-state diagnostics exist. |
| §6.1 pure-CO2 feed root | Pass at both observations during check 3: one stable root, density 723.5928742984386 mol/m³, positive dp/dρ 2196.5242889643346 Pa/(mol/m³), finite total enthalpy −393574.4494137983 J/mol. Returned branch `Unspecified`; requested hint `vapor`. All feed-root fields equal the prior wheel. |
| §6.1 bubbles α=0, 0.11, 0.45 | All unrun after the first failure. Pressure and separation factor 1734000/P_bubble are unavailable for all three; the guard 1734000 > P_bubble(1+1e−7) and raw-row limit 1e−10 were not assessed. |

| Historical replay quantity | This wheel | Difference from historical reference | Difference from b83c4250… |
|---|---:|---:|---:|
| Pressure cost | 8.143453130517166 | +2.3163693185779266e−12 | +2.6894042548519792e−12 |
| Species cost | 24.84844413070364 | −2.6361135496699717e−12 | −2.6361135496699717e−12 |
| Total cost | 32.99189726122081 | −3.197442310920451e−13 | +5.684341886080802e−14 |

The historical references remain 8.14345313051485, 24.848444130706277 and
32.991897261221126. Each absolute cost difference is below 1e−8; the
benchmark was not reset. The costs changed slightly from the preceding wheel.

| Heat verification quantity | 0→0.11 | 0→0.45 |
|---|---:|---:|
| Native heat (J/mol CO2) | −68169.42621173232 | −68286.33285346051 |
| Initial H (J) | −2313691.8924407274 | −2313691.8924407274 |
| Final H (J) | −2364483.718759536 | −2521529.244460994 |
| Independent assembled heat (J/mol CO2) | −68169.42621173232 | −68286.33285346051 |
| Assembly minus native (J/mol CO2) | 0 | 0 |
| Unchanged allowance (J/mol CO2) | 0.0425980386189414 | 0.010814222192635062 |
| Heat change after +10000 J/mol neutral CO2 anchor shift | 0 | +2.0372681319713593e−9 |
| Conditioning | 623.8701358675985 | 157.35119182398864 |

Conditioning is (abs(Hi)+abs(Hf))/(nadd abs(heat)), below 1e4 at both loadings.
The allowance is 1e−9 abs(heat)+1e−9(abs(Hi)+abs(Hf))/nadd+1e−6 J/mol.
Native heats, endpoint totals, feed enthalpy, independent assembly, allowance
and conditioning are identical to the prior wheel. The anchor-shift changes
were +4.249159246683121e−9 and +1.0477378964424133e−9 J/mol on that wheel;
they changed here by −4.249159246683121e−9 and +9.89530235528946e−10 J/mol,
remaining far below the unchanged allowances. Feed ideal/residual contributions
remain −392950.7093424419/−623.740071356366 J/mol.

For the four returned fixed-pressure records (three distinct states), maximum
raw row/residual is **2.8421709430404007e−13**, classified residual
**7.567628033932771e−14**, material error **9.959481156451844e−16 mol**,
and charge error **7.770991991234328e−16 mol**. All returned endpoints meet
their requested tolerance. The prior maxima were respectively
1.9895196601282805e−13, 5.045085355955182e−14, 3.0531133177191805e−16 mol
and 4.96507676858133e−16 mol. Thus these small numerical diagnostics changed;
the endpoint enthalpies did not.

Training maxima are raw stationarity **5.968558980384842e−13**, material
**6.066258606551855e−13 mol** and charge **2.0431756812929434e−13 mol**.
Their preceding-wheel maxima were 3.979039320256561e−13,
2.0605739337042905e−13 mol and 3.7951851945411784e−14 mol. All are below
1e−10 for raw stationarity and 1e−7 mol for material/charge. Conservation
sums use only the new retained phase amounts/compositions and unchanged
packet balances; they require no further Engine solve.

The first failure is exactly:

```text
TypeError: coordinate() takes 2 positional arguments but 3 positional arguments (and 2 keyword-only arguments) were given
```

It occurs in the wrapper at line 82 in the call to `reg.coordinate`, before
`reg.differentiate`. The failed child is `gradient 0.11`, exit 1; the parent
stops at stage 5 with an `AssertionError` preserving that child output.
`gradient-0.11.json`, `qualification-failure.json`, `remaining-qualification.json`
and `remaining-qualification.log.gz` preserve the diagnostic and complete
child/parent tracebacks. This is a Python call failure, not numerical
nonconvergence, physical-model failure, or an infrastructure exit.
No correction, retry or later numerical call ran.

No new Jacobian ratios exist. The preceding-wheel fine/coarse maxima were
0.03434805942801085/0.03253644283281535 at α=0.11 and
0.005455402229353226/0.005611162721701841 at α=0.45. Those remain history;
they do not qualify this wheel. Likewise the Engine handoff α=0 pressure
6289.083617367117 Pa and rank 14/14 are diagnostic history, not a downstream
bubble result from this run.

Wheel SHA-256 (the `.whl` archive bytes):
`e8ad39e0c5d7da471a6d3ace6ff62d60518c57bc1c96fe5198d8bf18747ba8b5`.
Source commit: `c106702048e87d0c583a3a5516cb5746e7a6ac07`, the merged PR #276
commit, verified as an ancestor of fetched `origin/main`. The separate detached
build worktree is `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-build-c1067020`.
The Engine's own setup script restored a fingerprint-matched shared-cache
wheel in 11.82 s (user/system CPU 5.63/3.50 s), under
`agent-heavy --timeout 30m --max 6G`, with one build job. Wheel fingerprint:
`f5932d5ba6d63f5665ded5314bc95b9e932ab442c7ca29245dde27b1fd7822b0`;
toolchain fingerprint:
`f6db693e21e289603ae71c78242a17b102f1e324061021d5dca361f47a0bfef7`.
`wheel-identity.json` and `build-toolchain.json` retain full source/build,
compiler/dependency, input and installed-file identities.

Installation is noneditable in a newly created private uv environment
`results/runs/temperature-heat-147/.venv-c1067020`, CPython 3.13.14,
epcsaft 0.2.0.dev0, numpy 2.5.1, scipy 1.18.0 and pandas 3.0.5.
The Engine verifier matched all 14 wheel RECORD hashes; the retained wrapper
verified all 18 hashed installed RECORD entries and their sizes. State and
summary records identify the actual `site-packages` module origin. `direct_url.json` and
`RECORD` were not rewritten. No Engine source was imported. The packet input
identity is its decompressed JSON hash, as in the retained evaluator; the
wheel archive hash is always over archive bytes.

Compute for this attempt: replay 8.05 s enclosing wall, **71.94193797600019 s
summed worker wall** over the affinity-sized pool of 12; mapping 0.37 s;
remaining sequence 6.59 s enclosing wall. Its 11 serial children took
6.22890521500176 s, with ten successes and the final TypeError; Q1/Q2 child
time 5.865348822001579/0.36355639300018083 s. Conservative new numerical
charge is **78.9019379760002 s**, without parent/child double counting.
Using the retained prior charge 201.11 s, cumulative conservative numerical
time is **about 280.01 of 50400 s**, leaving about 50119.99 s. Build preparation
is reported separately. Replay used `agent-heavy --wait 180 --timeout 1800s
--max 3G`; mapping/remaining used 1G and 1770/3540 s outer caps. Individual
observations retained `timeout -k 5s 175s`; OMP/OpenBLAS/MKL threads were one.
No 137, 124 or 75 exit occurred. Peak RSS reported by `/usr/bin/time` is per
process, not aggregate pool memory; the 3G parent cap controlled the replay job.

Wheel identity commit: **aa3d1a9**. Driver commit: **ebb24a6**; producer SHA-256
`c5b535bb00898d23b38b6f39bf30030093d815be290735565d5c1b7a3e556fa5`.
The wrapper remains at its existing path; wheel tag selects the build path,
fresh replay directory, private environment and result directory. No wrapper
copy or numerical-method change was made. The driver change adds six gross
lines and removes five. From base `76ea465fe1ede72257a809d04fc986489c5267f3`,
the charged total is **484 of 491**, seven remaining, with no removal credit:
120 source-law + 213 original-driver + 151 wrapper additions. The CSE final-tree
accounting and Git numstat cross-check are retained in `change-accounting.json`
and `gross-line-history.txt`; 473 surviving executable additions are separate
from 484 gross historical additions. No test or executable helper was added.

All pre-existing result files were checked byte-for-byte against their initial
hashes; only the explicitly authorized wrapper changed. The protected
`zero-carbon-diagnosis/` files remain untouched and untracked. `SHA256SUMS`
verifies every new retained file. Fits, loaded solves above 333.15 K,
#152/#160 substitution, epsilon, notebook/manuscript changes, push, PR and
issue edits are outside this delivery and did not run.
