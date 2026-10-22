# MDEA–CO₂–H₂O: Kuranov constant ion–water fit (issue #126)

**The fitted endpoint fails the issue's ARD < 10.9% rule.** All 82 Kuranov 1996
Table 2 total pressures solve, but ARD is **19.5432%**: **16.5453%** for the
19 mass % half and **22.5410%** for the 32 mass % half (41 rows each).
The fitted constant is **k(MDEAH⁺–water) = −0.2297985443**, interior to
[−0.3, +0.3], 0.07020146 above the lower bound. HCO₃⁻–water stays fixed at
−0.0765. These are calibration and numerical verification results for reading
(A), not physical validation or a promoted parameter set. Independent review
and investigator promotion remain open.

The [research notebook](notebook.qmd) presents the pressure comparison.
[refit-summary.json](results/refit-summary.json) owns the fit and assessment
numbers; [fitted-kuranov.csv](results/fitted-kuranov.csv) retains every fitted
pressure, phase composition, experimental target, source row and solve message.

## Basis and Kuranov results

The issue requires

$$\mathrm{ARD}=\frac{100}{82}\sum_{i=1}^{82}\left|1-\frac{p_{i,\mathrm{calc}}}{p_{i,\mathrm{exp}}}\right|<10.9\%,$$

with every row solved. The optimizer instead minimizes
$\tfrac12\sum_i[\ln(p_{i,\mathrm{calc}}/p_{i,\mathrm{exp}})]^2$; convergence
of that objective does not establish the ARD condition.

| Model | Solved | Overall ARD / % | 19 mass % / % | 32 mass % / % |
|:--|--:|--:|--:|--:|
| Reading (A), Wangler temperature-dependent ion–water laws | 82/82 | 17.6485 | 14.6081 | 20.6890 |
| Constant start: −0.184, −0.0765 | 82/82 | 32.5553 | 23.7576 | 41.3529 |
| Constant fitted endpoint: −0.2297985443, −0.0765 | 82/82 | 19.5432 | 16.5453 | 22.5410 |
| Fitted endpoint, Hsieh quadratic permittivity; no refit | 82/82 | 19.5090 | 16.5186 | 22.4993 |

The unchanged reading-(A) gate is inside the issue's 16.7–22.7% reproduction
window around Wangler's 19.7% (2018, Table 11). This is numerical agreement
under the adopted reading, not identification of the authors' implementation.
The constant fit improves its own start but is worse than the temperature-law
gate model on this ARD metric.

The two-column start Jacobian has column norms 88.3184 and 10.1679. After
column normalization its singular values are 1.41404336 and **0.02194035**.
Because the smaller value is below 0.1, only MDEAH⁺–water is admitted as
identifiable by the issue's start-Jacobian rule and fitted. The 0.1 threshold
is the issue's decision rule, not a literature-derived uncertainty criterion.
The fit converged in three iterations, with cost 10.75645410 → 2.75756683,
zero failed trials and all 82 native observations `Available`. It is one local
fit from one start; uniqueness, parameter confidence intervals and a global
minimum of ARD have not been established.

Kuranov Table 2 covers 313.11–413.16 K, about 19 and 32 mass % MDEA, on a
stoichiometric molality basis per kg water. The printed `10(p) (MPa)` values
are multiplied by 10⁵ to obtain total pressure in Pa. All four CO₂-free rows
and **all five rows above loading 1.2** (rows 8–11 and 18, maximum 1.316) are
included. Wangler Table 11 counts 82 rows while its caption limits loading
to 1.2; that source ambiguity remains. Row 58's non-monotone pressure is kept.

## Held-out Ermatchkov comparison

All 101 Ermatchkov 2006 Tables 1–3 CO₂ partial-pressure observations are
reported, without fitting them or applying a pass condition.

| Model | Solved | CO₂ partial-pressure ARD / % | Retained rows |
|:--|--:|--:|:--|
| Reading (A), original Wangler temperature laws (gate model) | 101/101 | 47.6504 | [gate](results/ermatchkov-gate.csv) |
| Constant start | 101/101 | 60.2291 | [start](results/ermatchkov-start.csv) |
| Fitted endpoint | 101/101 | 62.4440 | [fit](results/ermatchkov-fitted.csv) |

The prediction compared with the measured partial pressure is $y_{\mathrm{CO_2}}P$,
not the bubble total pressure. Both quantities and vapor compositions are
retained. The source's kPa values are multiplied by 1000. This is an outside-fit
comparison; it shows no held-out improvement from the fitted constants.

The source covers 313.15, 353.15 and 393.15 K, MDEA molalities 1.905–8.441,
loadings about 0.0028–0.784, and partial pressures 0.12–69.3 kPa. The explicitly
requested full 101-row report includes **13 rows above 49 mass % MDEA**, up to
50.146%; they lie outside the issue's nominal concentration limit and are
neither fitted nor silently excluded. Ermatchkov's cells contain nitrogen;
this calculation uses the declared water/MDEA/CO₂ vapor without nitrogen and
does not reconstruct the full experimental headspace. Its discrepancy is not
separated into experimental and model errors. Source caveats include 33 rows
below the 7 kPa calibration range and 18 whose reported reproducibility exceeds
the estimated pressure uncertainty (Ermatchkov pp. 6082–6083; see the
[source record](../../data/reference/MDEA/README.md)).

**Kamps 2001 and Jakobsen 2005 MDEA remain unscored:** their corrected pressure
and NMR speciation rows are not transcribed in this analysis. Ermatchkov's
Tables 1–3 are its own observations, not the corrected Kamps data in Table 6.

## Permittivity sensitivity, without refitting

The fitted constants were held fixed for one replacement of the pure-MDEA
straight line by Hsieh 2007 Eq. (3), Table 3 (printed pp. 620–621):

$$\varepsilon_{\mathrm{MDEA}}(T)=44.1399-0.046824(T/\mathrm{K})
-8.82158\times10^{-5}(T/\mathrm{K})^2.$$

All 82 rows solve and ARD decreases by **0.03419739 percentage points**,
19.54315195% → 19.50895456%. The failure against 10.9% remains.
[The sensitivity CSV](results/fitted-hsieh-quadratic-kuranov.csv) retains every
row. The Engine declaration re-expands this quadratic exactly about 298.15 K;
a direct check at 303.15, 328.15 and 413.15 K agrees within 10⁻¹².

Hsieh's validity range is **303.15–328.15 K**. Both the line and quadratic are
extrapolated for the 61 Kuranov rows above that range. At 413.15 K the pure-MDEA
values are 10.5754 (line) and 9.73675 (quadratic); the small pressure effect is
specific to this model and endpoint and does not validate either extrapolation.
Hsieh's six measured values (Table 2, p. 620) and Table 3 coefficients were
checked against Zotero PDF `8X653CVB`, SHA-256
`3a5f95471866b71d4e702061ac1c150d5ae1dc88fc0c669426634507c9cd8cf9`.

## Reading (A) and remaining physical limits

Decision D1 (issue #126, 2026-10-20) selects MDEAH⁺ as charged MDEA. It keeps
self-dispersion and the neutral temperature-dependent diameter while retaining
its declared Debye–Hückel diameter. `model.charged_molecule_ions` uses the
Engine's per-component declaration:

```json
"fixed": {"charged_molecule_ion": {"value": {"magnitude": 1, "unit": "dimensionless"}}}
```

No `packing_diameter` is declared on MDEAH⁺. This single document replaces
the former local construction and is used for both evaluation and fitting.

- **Numerical support only for reading (A).** Uyan 2015 p. 93 and Eq. (10),
  Wangler 2018 Eqs. (6)–(7), and Bülow 2021a's model description state the
  opposite like-ion dispersion/fixed-diameter convention. Agreement with the
  reproduction window does not resolve that textual conflict.
- **The high-CO₂ pressure gap is open.** Earlier retained reading-(A) diagnostics
  fall about 0.9 in ln P below Uyan Fig. 5 and down to 0.6 below Wangler Fig. 11
  where dissolved CO₂ dominates. This fit does not establish its cause or
  resolve it. Wangler's osmotic coefficients and §6.2 proton mole fractions
  also remain unreproduced in the earlier diagnosis.
- **Wangler Table 10 and Fig. 14 are untested with reading (A).** No inference
  about their 60 mass % case is made here.
- **The fitted model replaces both ion–water temperature laws by constants.**
  Water–MDEA, water–CO₂ and cross-association temperature laws remain fixed.
  Reaction constants are Uyan Table 1 on the mole-fraction basis, water relative
  to pure water and every solute at infinite dilution in water. No Born term,
  fitted reaction constant, slope, or additional fitted coordinate was added.
- **Permittivity uses free water/free MDEA mass weighting.** The distinction
  from weighting the initial CO₂-free solvent is unresolved; the present fit
  uses the Engine's speciated solvent basis throughout.
- No parameter adoption, absorber-use qualification, multistart assessment,
  uncertainty propagation, or physical validation is claimed. The 10.9% value
  remains this issue's numerical rule; the 2020 benchmark uses different fitted
  pairs and electrolyte physics (issue literature check, 2026-10-02).

## Numerical verification and retained history

[numerical-checks.json](results/numerical-checks.json) recomputes all seven
pressure tables from retained rows. Charge neutrality, phase normalization,
carbon/MDEA loading and water/MDEA feed conservation differ from their exact
relations by at most 6.67 × 10⁻¹⁶. The Ermatchkov partial-pressure conversion
is checked separately. The independently replayed fitted pressures differ
from the native fit predictions by at most 8.91 × 10⁻¹³ relative; the replayed
log-pressure cost is 2.757566830526, consistent with the native final cost.
These checks verify numerical bookkeeping, not experimental accuracy or
phase stability. No new stability study was performed.

Earlier readings and their evidence remain in `results/reproduction-*`,
`results/diagnosis.json`, `results/conventions.json` and
`results/wangler-figures-11-12.*`. They retain their original Engine and
parameter identities; they were not rerun or relabeled as current results.
The newer `reading-a-reproduction-*` files own the current reproduction gate.

Sources actually read for this continuation were Wangler 2018 §§3–4 and
§§6.1–6.2, Uyan 2015 §2 and §§4.1–4.3, Ermatchkov 2006 experimental methods,
Tables 1–3 and the discussion of corrected Kamps data, Bülow 2021a
Eq. (18) and its following model description, and Hsieh 2007 experimental/results
text, Eq. (3) and Tables 2–3. The indexed Wangler, Uyan
and Ermatchkov Markdown copies in the main checkout's ignored `literature/`
were verified against their current Zotero source hashes. Baygi 2015 §§3.1–3.3
was read for the MEA comparison of fitted versus predicted quantities; no
new fitting standard is inferred from it. The original sources behind Uyan
Table 1 were not reverified.

## Reproduce

Use the repository's immutable Engine wheel built from merged commit
`8298c6029ebb8b467929badc4a223c580ec591ab`. Its SHA-256 must be
`8897a0caab9f2508ed642f42c8b5226957fbe7035ed7bfdad71e4166798785b3`.
It is installed through the root `pyproject.toml` and `uv.lock`; no Engine
source checkout is imported. Linear solver: **MA57**.

From the repository root, after placing the wheel at the pinned ignored path:

```bash
sha256sum build/engine-wheels/main-8298c6029ebb8b467929badc4a223c580ec591ab/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl
nice -n 10 uv sync --locked
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
# Reproduction gate only:
nice -n 10 agent-heavy uv run --locked python analyses/mdea_kuranov_refit/score.py
# Re-evaluate the retained fitted endpoint, all held-out models, and sensitivity; no optimization:
nice -n 10 agent-heavy uv run --locked python analyses/mdea_kuranov_refit/fit.py --score-only
# Optional full re-estimation from the issue's prescribed start (up to eight workers):
nice -n 10 agent-heavy uv run --locked python analyses/mdea_kuranov_refit/fit.py
# Verify and present retained numbers without running the Engine:
nice -n 10 uv run --locked python analyses/mdea_kuranov_refit/check_results.py
nice -n 10 uv run --locked python analyses/mdea_kuranov_refit/plot.py
python3 analyses/manuscript.py refresh analyses analyses/mdea_kuranov_refit/notebook.qmd
```

The continuation scored the saved endpoint without re-estimating it.
`refit-summary.json` preserves the original fit script hashes and adds separate
scoring hashes; the original fit source is retained in commit `0567d9a`.
`model.py` owns declarations and `score.py` owns bubble evaluation and metrics;
`fit.py` owns the constant fit and endpoint assessment. `diagnose.py` and
`conventions.py` retain the earlier scientific probes, with reading (A) now
using the charged-molecule declaration. No diagnostic campaign is needed to
reproduce the endpoint results above.

The presentation-profile refresh stopped with `manuscript failed: [Errno 2] No such file or directory: 'snakemake'`. No Snakemake installation or service change was made. The ordinary HTML view was instead rendered with execution disabled:

```bash
nice -n 10 agent-heavy quarto render analyses/mdea_kuranov_refit/notebook.qmd --to html --no-execute
nice -n 10 agent-heavy quarto render analyses/index.qmd --to html --no-execute
```
