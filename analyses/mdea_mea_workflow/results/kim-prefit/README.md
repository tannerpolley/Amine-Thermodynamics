# Kim-only binary pre-fit, issue 222 item (k)

Item (k) passes. This is calibration of ion-free MDEA–water bubble pressure and
numerical verification of liquid miscibility for the prescribed model. It is
not independent physical validation or an MDEA transfer verdict.

The primary endpoint is k(313.15 K) = −0.18178699467896325 and reciprocal slope
−75.5392333856162 K, in k(T) = k(313.15 K) + b(1/T − 1/313.15 K).
The second endpoint is −0.18178700296135544 and −75.53924198900174 K.
Both converge, agree within the owner's 1e−4 / 1 K limits, have rank two and
no active bounds. The primary scaled-Jacobian singular values are
0.21248131881714344 and 0.028869880181215713, for coordinate scales 0.01 and
10 K. The cost is 0.0012265413343831894 and pressure AARD is 0.4998312500%
for all 61 Table 8 rows, including pure-water rows. Each residual is the
bubble-pressure log ratio, weight one. No vapor-composition residual is fitted.

The initial zero-pair attempt was refused before any iteration for local
liquid instability; its eigenvalue and native refusal remain in
`zero-pair-refused.json`. The subsequent initializations (−0.184, 0 K) and
(−0.15, 0 K) were **orchestrator-chosen from the diagnosis probes, not source
values**. The primary endpoint is used for every amended start. Start 2 is
recorded as a duplicate of start 1 for each variant. Start 4 preserves the
Bülow ion dimensions and its zero ion–water interaction. Inputs and hashes
are under `../../inputs/amended-starts/`.

All four Gibbs-mixing lower convex hulls are miscible at 293.15, 313.15,
353.15 and 393.15 K. The diagnostic owner's composition grid covers
x(MDEA) = 1e−6 through 1−1e−6, supplemented with pure endpoints for the
phase searches. There are 277 interior grid compositions plus two pure endpoints per temperature,
and 61 Kim-state searches: 1,177 searches in total. All complete with zero
unresolved trials and no liquid descending split. Search summaries and native
trial quantities, compositions, split checks and coordinates are retained.
This finite grid and finite trial search do not prove global stability at
every continuous composition.

There are 170 vapor-witness searches, separately retained in
`vapor-witnesses.json`. The owner ruled these outside the liquid-miscibility
gate. Of these, 38 are Kim states; every one has the matching positive
bubble-pressure residual (model pressure above measured), with zero sign
mismatches. At 393.15 K and 101325 Pa, vapor formation near pure water is
expected. The binary grid uses the diagnosis pressure of 101325 Pa; Kim
states use their measured pressures. No vapor witness is called evidence
of liquid demixing.

All ten amended Carson searches (A1/A3/A4/B1/B3 at rows 1 and 10) complete
with zero unresolved trials and no descending split, at 298.15 K and the
owner's 101325 Pa convention. These results qualify starts only; endpoint
phase checks remain required.

The source PDF was read directly: Kim et al. 2008, Table 8, printed p.2524;
experimental uncertainties, pp.2526–2527; Results and Discussion and
Conclusions, pp.2527–2529. The existing retained transcription and source
`data/reference/MDEA/stage1-sources.json` own data provenance. The fit uses native regression coordinates,
pressure observations and bounded least squares as in MEA
`fit_observations.py`/`fit_neutral_co2_mea.py`; all equations and derivatives
remain in the pinned Engine wheel. Fit controls are retained in `compute.json`.
`bubble-pressure.png` uses only `bubble-pressure-residuals.csv`; points are
observations and cross markers are predictions at reported states, with no
interpolation. Source u(P) = 0.3 kPa is shown; it is not a fit weight.

The pinned Engine wheel and every installed package file were verified,
using the main checkout interpreter with `-I`. There was no Engine source
import, no worktree environment, and no write to the main checkout.
Independent delivered review and manuscript promotion have not occurred.
