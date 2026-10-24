# Pure-MEA association-volume conversion on Engine 3e83e19c

**Decision: stop under issue #210.** Both estimators converged. The original
absolute-error search supports the printed volume, but the native least-squares
optimum rounds to a different value. The owner must decide which estimator
defines the paper's conversion. No parameter, subsequent fit or manuscript was
changed. These results have not been independently reviewed or promoted for
manuscript use.

| Estimator | Optimum, dimensionless | Five significant figures | Numerical completion |
|---|---:|---:|---|
| SciPy bounded absolute error | 0.03628703079971812 | 0.036287 | success=True; 25 evaluations |
| Engine native least squares | 0.03630543900419865 | 0.036305 | usable=True; converged; 3 iterations |

The absolute-error optimum differs from the original `0.03628703079972324`
by `1.4088730182493236e-13` relative, within the required `1e-6`, and passes
the rounding criterion. Least squares stops by function tolerance:
`|cost_change|/cost: 2.929726e-13 <= 1.000000e-12`.

## Basis and numerical evidence

Pure MEA has one donor and one acceptor site (2B). The reported record supplies
the fixed values: segment count 3.0353, segment diameter 3.0435 Å, dispersion
energy divided by Boltzmann's constant 277.174 K and association energy divided
by Boltzmann's constant 2586.3 K. They match Baygi and Pahlavanzadeh (2015),
Table 2, p. 792. Equations (4)–(5), p. 791, give the exact isothermal reference
volume in the Engine convention:

$$\kappa_{\mathrm{equiv}}(T)=0.037470[1-0.12\exp(-3(277.174)/T)]^3.$$

Both fits use pressure and saturated-liquid molar density at 21 temperatures,
293.15–393.15 K at 5 K spacing. Each relative error has unit weight. The
absolute-error objective sums their absolute values; the native cost is half
the sum of their squares. Bounds are [0.033723, 0.037470]. SciPy uses the
original bounded search with `xatol=1e-8`. The native coordinate, start, all
42 observations in Pa and mol/m³, and the exact issue controls are retained in
[least-squares-declaration.json](least-squares-declaration.json).

All 722 retained saturation solves pass: success, finite positive pressure and
liquid density, and maximum absolute equation residual at most `1e-10`.
The observed maximum is `5.81756864903582e-14`. All 42 native final observations
are available and finite; there are no rejected native trials. Independent
saturation replay gives native cost `0.0003835770506949749`, within
`1.3465790982269965e-16` absolute of the fitter's `0.00038357705069510953`.

| Evaluated volume | Absolute-error objective J | Half sum of squared relative errors |
|---|---:|---:|
| Absolute-error optimum | 0.11081423588344319 | 0.0003857111510874517 |
| Least-squares optimum | 0.11088518051704765 | 0.0003835770506949749 |

## Reporting-grid average absolute deviations

Values below are percentages relative to Baygi's model. The first interval
contains 21 temperatures; the second contains 29 temperatures.

| Constant volume | Pressure, 293.15–393.15 K | Density, 293.15–393.15 K | Pressure, 303.15–443.15 K | Density, 303.15–443.15 K |
|---|---:|---:|---:|---:|
| Printed 0.036287 | 0.5251564863 | 0.002535959087 | 0.7932801701 | 0.008972621897 |
| Absolute-error optimum | 0.5251507532 | 0.002536084347 | 0.7933040064 | 0.008973047727 |
| Least-squares optimum | 0.5253983971 | 0.002626272048 | 0.8102036875 | 0.009238578799 |
| Unconverted 0.037470 | 2.795010456 | 0.01423429653 | 3.203611411 | 0.02955397285 |

[reporting-grid.csv](reporting-grid.csv) and [reporting-grid.json](reporting-grid.json)
retain all 31 temperatures, 293.15–443.15 K, for each of the four constants,
with signed relative pressure and density differences. The scalar rounding
decision is fully specified by the optimum table; a plot would not change
that decision. No model disagreement with measurements is assessed here.

## Retained files and reproduction

- [reference-curves.json](reference-curves.json): 31 exact-equivalent reference states.
- [solves.jsonl](solves.jsonl): all 722 saturation results and their equation residuals.
- [absolute-error-history.jsonl](absolute-error-history.jsonl): 25 search evaluations and two final cross-evaluations, each with its 21 states.
- [absolute-error-optimum.json](absolute-error-optimum.json): original SciPy result.
- [least-squares-fit.json](least-squares-fit.json): native values, residuals, exact derivative columns, stopping message and covariance.
- [cross-evaluation.json](cross-evaluation.json), [summary.json](summary.json), and [validation.json](validation.json): full precision objectives, deviations, decision and admission checks.
- [provenance.json](provenance.json): wheel, reported record, executed producer, command and package identities. SciPy is 1.17.1; the complete numerical run took 1.454 wall seconds including file writes.

Engine commit: `3e83e19ccc771b51d8ebc038931ab25192f4c5b5`.
Wheel SHA-256: `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`.
Reported record SHA-256: `e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e`.
Installed Engine files were checked byte for byte against the wheel before
execution. No Engine source checkout was imported.

The original source was read with `git -C upstream/ePC-SAFT show d0cb9b8c:analyses/2026-mea-association-diameter/scripts/mea_saturation.py`
in the main checkout. Its full commit is `d0cb9b8ceb8cf9fc6cfd83b807bd3e81db703341`.
The read-only clone was left unchanged, as instructed, at `a6a93b85c9027296a5103b50f841bca21a29c8fb`;
remote main was `f30863c71775f9c82e2eda67d7f413ab5ff96a33` when inspected.
The historical source read uses the specified commit and does not depend on
either main tip.

From this worktree, the calculation command was:

```bash
nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mea_parameter_bundle/scripts/mea_association_volume.py
```

The producer refuses an existing output directory. The initial pressure-return
mapping was corrected from the historical vector to the current scalar before
the complete run. After that run, summary serialization failed on a NumPy
Boolean; [producer-summary-error.json](producer-summary-error.json) retains
that exception. The final producer explicitly casts this comparison to Python
`bool` and preserves any nonfinite rejected-state values as explicit strings in
JSON. Neither change alters numerical evaluation. Only the summary was recovered from retained results with `python -I`;
neither estimator nor the reporting calculations were repeated.
`validation.json` identifies the final producer hash separately from the
executed producer hash in `provenance.json`. The final script is 147 gross
added executable-file lines, including comments and blanks, against `e4de95d`.

Baygi's Markdown reading copy was checked against Zotero attachment `ICDS2PAA`
(SHA-256 `f28ed7ca19317eb9f5e017f9a34d31cd35419117da2b012a7a750388f9a83cbe`).
Equations (4)–(5), Table 1, Table 2 and §3.1 were checked against PDF attachment
`JWH69DKG`, pp. 791–792; its SHA-256 is in `validation.json`.

## Claim limits and handoff

This is numerical reproduction against Baygi's pure-MEA model, not physical
validation against measurements. It concerns one constant association volume
with the other pure parameters fixed and isothermal properties only; it does
not establish caloric equivalence. The 293.15–303.15 K portion extends below
Baygi's published 303.15–443.15 K pure-parameter fitting interval (§3.1, p. 792).
The difference between optima and the native local covariance are numerical
diagnostics against deterministic model targets, not physical parameter
uncertainty. Issue #211 must await the owner's estimator decision and
independent delivered review; these results do not authorize an S1 edit.
