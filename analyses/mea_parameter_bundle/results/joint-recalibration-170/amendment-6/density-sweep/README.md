# Amendment 6, step 1: density-weighted F1 screen (#170)

Run 2026-10-18 on Engine wheel `main-21e761c3` (sha256 `d2f61e3a…0357`), on the
A4 larger-d_V control declaration. The only change is `fit_case.density_weight`:
each of the 12 Amundsen 2009 loaded densities (30 wt %, 298/323/343 K, loading
0.1–0.4) gets weight λ/12 at scale 2 kg/m³. Design:
`tmp/joint-design/amendment-6-paper-candidate.md` §0, readiness reviews r1–r3.
The screen covers the larger d_V branch from start A only. The smaller branch
and the second starts remain outstanding.

## Result

**The λ = 0.01 fit stopped at the 100-iteration limit, without converging.** The
runner then refused further fits, as its stop rule requires
(`fit_campaign.py:598`, "return to owner before another fit"). The λ = 0.1 and
λ = 1 fits were therefore not run.

Its endpoint is a numerical result of an unfinished fit, not a candidate.

| | λ = 0 (A4 control) | λ = 0.01 (iteration 100) |
|---|---:|---:|
| Status | converged (function tolerance) | iteration limit |
| C149, common rows | 24.5609 | 24.5850 (+0.10 %) |
| C166, non-density reacting rows | 39.6902 | 40.7433 (+2.65 %) |
| C178, reacting rows with density | 39.6902 | 41.0084 |
| C217, all rows | 39.6908 | 41.0091 |
| Pressure AARD, 47 rows | 12.76 % | 12.36 % |
| Species AARD, 94 rows | 7.17 % | 7.12 % |
| Vinjarapu heat RMSE, 8 rows | 1.515 kJ/mol | 1.789 kJ/mol |
| 12 loaded densities, kg/m³ | −24.3 to −108.2 | −2.9 to −24.4 |
| MEAH⁺ segment diameter | 5.8 Å (bound) | 4.467 Å (interior) |
| Carbamate segment diameter | 5.8 Å (bound) | 5.8 Å (bound) |
| Born diameters | 5.0 / 5.0 Å (bound) | 5.0 / 5.0 Å (bound) |
| Active bounds | 5 | 6: bicarbonate–water k = 1, carbamate–MEAH⁺ k = −1, carbamate σ, both Born diameters, R5 reference |
| Hilliard Cp, %: 318.15 K 0.0 / 0.358; 353.15 K 0.0 / 0.358 | +3.31 / +1.55 / −0.64 / −2.05 | +3.32 / +1.91 / −0.64 / −2.01 |

Here AARD is the average absolute relative deviation, RMSE the root-mean-square
error, and Cp the isobaric heat capacity.

**Densities at λ = 0.01, kg/m³**, in row order 060–063, 070–073 and 075–078:
- 298 K: −2.85, −7.45, −14.06, −23.78
- 323 K: −2.98, −7.30, −14.51, −23.29
- 343 K: −3.02, −8.05, −15.26, −24.41

None is within the 2 kg/m³ gate.

**Where the cost moved** (λ = 0.01 minus λ = 0):
- Jakobsen ratios: +0.859.
- Vinjarapu heats: +0.465.
- Cp: +0.137.
- Restored species: +0.033.
- Böttinger species: +0.004.
- Matin species: −0.171.
- Pressures: −0.275.
- Density term: 0.265.

**Reading.**
- **Density can be weighted at almost no cost to the paper's common rows.** A small weight already cuts the loaded-density errors 4–5× while leaving C149 essentially unchanged and slightly improving the pressure and species deviations.
- **The trade-off falls on the corrected Jakobsen ratios and the Vinjarapu heats.**
- **Only the MEAH⁺ size moved.** Carbamate and both Born diameters stay on their bounds.
- **The remaining density errors still grow with loading,** which points to the carbamate size held at its 5.8 Å bound.
- **These are hypotheses about an unconverged endpoint.** A converged fit, or higher λ, may move differently.

## Checks

- **Start release tests** (`release-l*/release-tests.json`) pass at every λ:
  - augmented condition 4,887 / 4,521 / 4,031 (mandatory 3,318 / 3,210 / 2,784);
  - projected ion dispersions 11.5 / 11.8 / 9.3.
- **Endpoint cold replay** (`endpoint-l0p01/`): 217 rows at λ/12 weights against `fit-l0p01/native.json`, largest weighted-row difference 1.8e-12, relative cost difference 1.4e-13.
- **Fit progress:** rank 14 of 14, projected gradient 0.0051. The final iteration lowered the cost by 6.4e-5 relative against the 1e-6 function tolerance, and the last 10 iterations by 0.20 %.
- **λ = 0 reference values:** taken from the A4 control endpoint as evaluated by amendment-5 probe P (`amendment-5/a0/probe-p/information/a4-control-endpoint/native.json`) on the same wheel.
- **Not run:** endpoint derivatives, and the 8 loaded plus 5 unloaded assessment densities.

## Compute

| Call | Wall s | CPU-s |
|---|---:|---:|
| Three release tests | 55.45 | 55.37 |
| Fit, λ = 0.01 | 282.95 | 3,778.54 |
| Endpoint evaluation | 18.40 | 18.30 |

- **Program ledger:** charged together with the smaller-d_V density call as one rounded-up entry of 377 s / 3,872 CPU-s (`amendment-4/compute-ledger.json`). The program now stands at 10,996 of 21,600 compute-wall s and 97,578.61 of 144,000 CPU-s.
- **Ledger file:** `step-ledger.json` holds this step's calls.
- **Fit charge:** GNU time prefixed its record with "Command exited with non-zero status 1"; the fit's charge was transcribed from that file.

## Owner decision

Before another fit, the owner decides among:
- a continuation of λ = 0.01 from this endpoint to convergence;
- the λ = 0.1 and λ = 1 fits, which may need a higher iteration limit;
- stopping here.
