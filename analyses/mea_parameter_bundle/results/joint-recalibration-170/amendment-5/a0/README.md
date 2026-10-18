# Amendment 5, screen A0 (#170): stopped at the start check, before the fit

Run 2026-10-18 from MEA `main` at `adecfb3`, following the reviewed design
`tmp/joint-design/amendment-5-ion-model-form.md` (#170 comment 6252925020).
Engine wheel `main-21e761c3` (SHA-256 `d2f61e3a…0357`) in a scratch environment
with exactly that wheel, numpy 2.5.4 and scipy 1.18.1; `fit_campaign.verify`
passed in every call (`*/inputs.json`). Abbreviations: DH = Debye–Hückel;
A4 = amendment 4; C205/C166/C149/C154 = half the sum of squared weighted
residuals over all rows / all but Kiepe / the common rows / C166 without the
12 caloric rows (design §7).

## Result

**A0 has no outcome category: the run stopped at check 1, before the fit.** At
the A0 start the identification (release) test fails. The 10 mandatory free
columns have condition 2.20e5 and all 12 free columns 2.24e5, against the
limit of 1e4; the A4 start passed at 3.45e3 and 6.39e3. Design §10 lists a
check-1 failure as a stop, so no fit was launched. There is therefore no
endpoint. The three decision coordinates (MEAH⁺ size, carbamate size,
carbamate–MEAH⁺ k), C166 and C149 against the A4 control (39.6902 and
24.5609), the active bounds and the endpoint gates (checks 3–10) do not exist
for A0. As design §10 states, a stop is not evidence that the
charged-molecule form cannot fit MEA.

**Why the start check fails.** The A0 start keeps the A4 start's ion k
values, which were set for the one-sphere ions, on the new chain form.

| A0 start against the A4 start | Value | Source |
|---|---|---|
| C205 | 13,843.7 against 195.70 (×70.7) | `check1-diagnosis/analysis.json` `start_costs` |
| CO₂ partial-pressure share of it | 13,653.4 (47 rows) | same |
| Worst eight rows, ln(p_calc/p_obs) | −10.0 to −11.0, so 10⁴–10⁵ times too low (A4 start at the same rows: −0.13 to +0.34) | `largest_weighted_rows` |
| Pair dispersion weight m_i m_j √(u_i u_j)(1−k)σ_ij³ at 313.15 K, A0/A4 | carbamate–water ×3.73; MEAH⁺–water ×2.59; carbamate–MEAH⁺ ×9.92 | `pair_dispersion_weights_313_15_K` |
| New self pairs (zero under the A4 rules) | MEAH⁺ 72,000 K Å³; carbamate 334,000 K Å³ | same |
| Weakest direction | cosine 0.986 with bicarbonate–water k (components −0.15 MEAH⁺–water k, +0.07 carbamate–water k); singular value 8.1e-5 against 17.8 | `release_test` |
| Column norms, A0/A4 | ion and pair columns ×4–10 (carbamate–water 9.98, carbamate size 5.45); bicarbonate–water ×0.54 | `weighted_column_norm_ratio_a0_over_a4_start` |
| Condition with one column dropped | any one of the three ion–water k columns: 5.4e3–5.9e3 (passes); any other column: ≥ 1.6e5 | `mandatory_condition_with_one_column_dropped` |
| All free columns without bicarbonate–water | 1.62e4 (still above 1e4) | `all_free_condition_without_bicarbonate_water` |

Reading (inference from these numbers and the declared parameters): the
inherited k values give the MEA ions 2.6–9.9 times their A4-start dispersion
attraction, plus self-attraction they did not have. This over-stabilizes the
ions and draws CO₂ into the liquid, so CO₂ pressures fall by 4–5 orders of
magnitude. Against those large ion and pair columns, the three ion–water k
columns are nearly collinear, mostly along bicarbonate–water k, which was
also the weakest direction at the A4 endpoints. The failure is not caused by
the suppression-factor change below: at the design's literal factor 1e-8 the
test gives 2.2023e5 and 2.2409e5, with Jacobian columns that agree to 2.3e-7
relative.

On the chain form, the k values that would keep the A4-start pair weights
are 0.768 (carbamate–water, outside its [−0.5, 0.5] box), 0.467 (MEAH⁺–water)
and 0.828 (carbamate–MEAH⁺). This is arithmetic for the next design decision,
not a tested start.

## Gates

| Check (design §8/§10) | Result | Limit | Verdict |
|---|---|---|---|
| Step 1, probe P: recomposed tied size gradient against the A4 column | 1.16e-10 (MEAH⁺), 1.52e-11 (carbamate), relative | 1e-8 | pass |
| Probe P cold replay against the A4 control weighted residuals | 6.9e-12 | — | consistent |
| Check 2, document X, suppression factor 1e-8 (as A5-4 states) | 6.64e-8 largest weighted row; 8.8e-9 relative cost | 1e-8 | **fail** |
| Check 2 at the corrected factor 1e-12 | 9.3e-11; 5.3e-12 relative cost | 1e-8 | pass |
| Check 1, A0 start release test (factor 1e-12) | mandatory 2.20e5; all 12 free 2.24e5; shift block after projection 533 | 1e4 each | **fail: stop** |
| Checks 3–10, the fit and the §9 decision | not run (no endpoint) | — | — |
| Check 11, densities (report only) | A4 control endpoint (probe P): −24.3 to −24.5 kg/m³ at loading 0.1, falling to −107.0 to −108.2 at 0.4, at 298, 323 and 343 K. A0 start: −21.7 to −97.8 kg/m³. The A0 endpoint was not reached | stage-7 reference ≤ 2 kg/m³ | report only |

All rows were available in every call: 217 rows in probe P and 205 objective
rows plus 12 densities in the others. No row solve failed. The stop list's
"spurious phase behavior" cannot be assessed beyond that: the release test
does not check phase stability.

## Probe P (step 1): what drives the A4 size bound

The gradient of C at the A4 control endpoint is split into the parts of the
tied size column, per optimizer unit of 0.1 Å. The size sits at the 5.8 Å
upper bound, so a negative value points outward:

| Ion | σ only (dispersion size) | 0.88 × packing (hard core) | 0.88 × DH | Tied sum (A4 column) |
|---|---:|---:|---:|---:|
| MEAH⁺ | +0.0959 | −0.1121 | +0.0093 | −0.0069 |
| Carbamate | +0.1173 | −0.2577 | +0.0250 | −0.1153 |

Only the hard-core part points outward; the dispersion size and the DH
distance point inward. By the design's rule (§4, option (ii)), untying the
0.88 ties is **kept as a fallback**, not dropped. Probe P also reproduces the
A4 u columns to 1.1e-9 and 9.6e-9 relative. All values are in
`probe-p-analysis.json`.

## Check 2: the leftover self-dispersion, and the correction made

The A5-4 workaround replaces an ion's u by SUPPRESS·u and rescales its k_ij,
which leaves a self-dispersion of SUPPRESS·u_i rather than zero. With the
#126 helper's SUPPRESS = 1e-8, document X misses its limit (6.64e-8 against
1e-8). A bounded diagnosis (`check2-diagnosis/`, one 18.5 s call) rebuilt X
at 1e-10 and 1e-12:

| Factor | Largest weighted-row difference | Relative cost difference |
|---|---:|---:|
| 1e-8 | 6.639e-8 | 8.8e-9 |
| 1e-10 | 6.636e-10 | 9.2e-11 |
| 1e-12 | 9.3e-11 (evaluation floor) | 5.3e-12 |

The difference falls 100.04× per 100× in the factor, so it is the leftover
self-dispersion, linear in SUPPRESS. It is not a construction defect: a missed
pair or slope rescale would not shrink this way. The MEAH⁺–water
reciprocal-temperature slope is rescaled with its constant term (b′ = s·b),
and every other rescaled pair was asserted to carry a single constant k_ij
(`construction.json`, `workaround`). **The A0 documents therefore use
SUPPRESS = 1e-12.** The bicarbonate–water coordinate is k′ = 1 − 10⁶(1 − k),
with bounds [−1,499,999, 1] and scale 10⁴. That is the same optimizer
coordinate as A4's k (scale 0.01); report values back-transform as
k = 1 − (1 − k′)/10⁶.

## Deviations from the design (all reversible)

1. **Suppression factor 1e-12 instead of A5-4's 1e-8**, for the reason above.
   The gate itself is unchanged. The 1e-8 X document, its run and the
   diagnosis are retained.
2. **Two diagnostic calls beyond the design's list:** the check-2 diagnosis
   and the check-1 rerun at 1e-8 (37.4 s together). They classify the two
   failures and show that the check-1 stop does not depend on deviation 1.
3. The X-evaluation spec was written before probe P ran, so its program
   priors omit probe P's 21.1 s and 21.1 CPU-s. Every other spec carries all
   earlier calls. No guard was near its limit.
4. Scratch environment `tmp/a5-a0/venv`, not the repository `.venv`:
   `uv.lock` pins numpy 2.4.4 and scipy 1.17.1, not the specs' 2.5.4 and
   1.18.1.
5. The probe-P and evaluation specs widen coordinate bounds by one optimizer
   unit, as the A4 checker does, because their origins sit on A4 bounds. The
   extra probe columns (packing, DH, segment count, u) have wide bounds that
   contain the origin. Bounds do not enter an information call's values.
6. The MEAH⁺ parent is the repository's MEA record (m 3.0353, σ 3.0435 Å,
   u 277.174 K), as design §5.1 specifies. MEA stands to MEAH⁺ as MDEA does to
   MDEAH⁺.

## Owner or orchestrator decision needed before any A0 fit

Recorded in the design §14 sense, as options with a recommendation:

- **(a) Recommended: a start consistent with the chain form.** Map the three
  MEA-ion k values to keep the A4-start pair weights: carbamate–MEAH⁺ 0.828
  and MEAH⁺–water 0.467, both inside their boxes. Carbamate–water needs
  0.768, outside [−0.5, 0.5]; capping it at 0.5 puts it on a bound at the
  start, and widening the box is a design change. Decide this together with
  open decision 3 (carbamate parent and fixed u), because carbamate's
  inherited u = 533.11 K is what makes its water pair too strong. Cost: one
  information call (about 20 s) before the fit.
- (b) Fix bicarbonate–water k at its start value. The mandatory block then
  passes (5.4e3), but all 11 free columns give 1.62e4, which still fails the
  all-columns rule.
- (c) Waive check 1 for A0. Not recommended: this guard is what keeps a fit
  from starting where its directions are not identified.

## Claim limits

- No A0 endpoint exists, so H5 (§9) is neither supported nor contradicted.
  The stop concerns the inherited-k start, not the charged-molecule form.
- The pair-weight attribution is arithmetic on declared parameters at
  313.15 K. It is not an attribution measured by evaluation.
- Probe P is first-order information at one endpoint (the A4 larger-d_V
  control).
- A0 documents change the declared inorganic u/k values (workaround) and
  cannot be adopted. Nothing is adopted.

## Compute

| Call | Wall, s | CPU-s |
|---|---:|---:|
| Probe P | 21.09 | 21.08 |
| Check 2, X at 1e-8 | 9.00 | 9.00 |
| Check-2 diagnosis, X at 1e-10 and 1e-12 | 18.50 | 18.49 |
| Check 1, A0 start | 19.01 | 19.00 |
| Check-1 diagnosis, A0 start at 1e-8 | 18.94 | 18.93 |
| **Total** | **86.54** | **86.50** |

Charged as 87 s and 87 CPU-s, appended to the single program ledger
`../../amendment-4/compute-ledger.json`. It now stands at 10,619 of 21,600 s
(10,981 s remaining; the 1,950.38 s check reserve is still held) and
93,706.61 of 144,000 CPU-s. Of the A5 allowance (3,000 s, 30,000 CPU-s),
87 s and 87 CPU-s are used. Information calls took 19–21 s each, against the
36 s the design expected. No campaign code was added (design §11). The
construction and post-processing command is disclosed scratch; its exact
text, hash and invocation order are in `commands.json`.

## Files

- `start-parameters.json` (SHA-256 `01f3b7f0…3004`): A0 start, factor 1e-12;
  `construction.json`: diameter factors (f₊ = 0.9915670684375054,
  f₋ = 0.9992736630204387 at 313.15 K, stored as the spec's tie factors), ion
  values and the per-pair workaround record.
- `probe-p-spec.json`, `probe-p/`, `probe-p-analysis.json`: step 1 and the
  check-11 densities at the A4 control endpoint.
- `check2-x-parameters.json`, `evaluation-x-spec.json`, `check2-x/`,
  `check2-analysis.json`: check 2 at 1e-8. `check2-diagnosis/`: X at 1e-10
  and 1e-12, the run and `analysis.json`.
- `information-spec.json`, `information/` (`release-tests.json`,
  `failure.json`): check 1. `check1-diagnosis/`: the 1e-8 start, the run and
  `analysis.json`.
- `*-command-time.json`: measured whole-command times. `commands.json`: the
  command text and invocations.
