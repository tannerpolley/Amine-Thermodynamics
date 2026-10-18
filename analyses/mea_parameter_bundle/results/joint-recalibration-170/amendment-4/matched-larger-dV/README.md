# Amendment 4 matched reacting comparison, larger-d_V branch (#170)

Run 2026-10-18 on Engine wheel `main-21e761c3` (sha256 `d2f61e3a…0357`).

## Result

**Fixing the CO₂–MEA pair at its neutral value does not improve the reacting
fit.** Both arms converge to nearly the same endpoint, with the same five
coordinates on bounds. The non-Kiepe cost C166 is 0.06 % *higher* with the
neutral pair, against the required 10 % reduction (rule A4-5). This null was
stated in advance on #170 (comment 6246616060): changing the pair from (0, 0)
to the neutral value changes the reacting start cost by only 8e-7 relative.
The decision is formally **not decidable** because three endpoint checks miss
their limits (below); none can turn a 0.06 % increase into a 10 %
reduction.

| | Zero control | Neutral-fixed variant |
|---|---|---|
| CO₂–MEA k(313.15 K), b | 0, 0 K | 0.098720, −50.989 K |
| Status | converged (function tolerance) | converged (function tolerance) |
| Iterations | 84 | 75 |
| Cost, start → end | 195.7043 → 39.6908 | 195.7041 → 39.7141 |
| C166 (non-Kiepe) | 39.6902 | 39.7134 (×1.000585) |
| C149 (common) | 24.5609 | 24.5606 (×0.999989) |
| Active bounds | carbamate–MEAH⁺ k = −1; both ion segment diameters 5.8 Å; both Born diameters 5.0 Å | the same |
| Wall / CPU | 225 s / 3,247 CPU-s | 208 s / 3,008 CPU-s |

Family costs differ by at most 0.015 (heat capacity 2.248 vs 2.263; Jakobsen
ratios 10.459 vs 10.469). The free coordinates agree closely; the largest
differences are the R2 and R5 enthalpy shifts (2,719 vs 2,621 and 2,951 vs
2,806 J/mol), which are weakly determined.

## Endpoint checks (`matched-checks.json`)

| Check | Control | Variant | Limit |
|---|---|---|---|
| Rows available | 205 | 205 | all 205 |
| Rank | 14 | 14 | 14 |
| Cold replay from the endpoint document, largest weighted row difference | 1.3e-12 | 1.4e-12 | ≤ 1e-8 |
| Cold replay, relative cost difference | 5.4e-14 | 3.7e-14 | ≤ 1e-8 |
| Kiepe rows against the same-wheel fixed-binary start | 3.2e-15 | 3.2e-15 | ≤ 1e-8 |
| Free-block condition (9 free columns; all 14: 6.25e4 / 6.28e4) | 37,393 | 37,489 | ≤ 1e4 |
| Projected gradient | 0.0081 | 0.0092 | ≤ 1e-8 |
| Centered derivatives, steps 0.01 / 0.005 | miss at the two ion dispersion energies | the same | 1e-8 absolute or 1e-5 relative |

- **Derivatives:** the misses are 1.6e-7 to 6.4e-7 absolute. Each halving of
  the step cuts the error by 4.0, the h² truncation of a centered
  difference, so the native derivative is verified by convergence. The
  fixed-step tolerance itself is still not met. All other columns pass,
  including the five held at bounds (checked in boxes widened by one
  optimizer unit).
- **Conditioning:** the weakest direction lies mostly on the bicarbonate–water
  k_ij (cosine 0.973, 94.7 % of its squared length; value 0.86, interior), with smaller carbamate–water and MEAH⁺–water parts. The
  reacting rows barely determine it at this endpoint.
- **Projected gradient:** both arms stopped on the 1e-6 function tolerance, so
  the 1e-8 gradient limit is not met. A Gauss–Newton step on the nine free
  columns predicts at most 2.4e-4 (control) and 3.5e-4 (variant) further cost
  decrease, under 1e-5 relative; a 10 % change would need about 3.97. The
  gradients on the five held coordinates all point outward.
- **Not run at these endpoints:** the 12 zero-weight loaded-density rows and
  the per-row heat-capacity and heat assessments the design keeps.
- **Endpoint replay history:** the first check attempt failed because the
  campaign wrote R2's fitted ln K constant in the Engine's c ln(T/T_ref) form
  into a document that uses c ln T (211.4 too low). The fit itself was right:
  replay in the fit's own coordinates agreed to 3.8e-13. After the fix
  (`fit_campaign.py`, 88ee4c8) both arms were rerun; they reproduced bit for
  bit, and the documents now replay cold. The superseded runs are not
  retained.

## Meaning and limits

The neutral CO₂–MEA interaction, determined independently from N₂O-analogy
physical solubility, leaves the reacting fit unchanged. The five active
bounds, the symptom amendments 3–4 attribute to model form, persist with or
without it, so the neutral pair does not remove them. This is numerical
evidence about this objective; it is not physical validation and does not
show that the neutral pair is wrong. Both endpoints stopped on the 1e-6
function tolerance (projected gradients 0.008 and 0.009; the control's last
three steps lowered the cost by 4e-4, 1.5e-4 and 4e-5).

Files: `control/`, `variant/` (native results, endpoint documents, chemistry
coordinates, timing), `matched-checks.json`, the information checks at the
starts (`information/`), start documents, specs and command times. Producer:
`scripts/fit_campaign.py` (stage-6 fit) and `scripts/check_matched_co2_mea.py`.
