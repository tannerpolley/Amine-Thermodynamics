# Issue 201: diagnosis of missing high-temperature phase evidence

The tested numerical failures can be corrected by changing their starts while
keeping the equations, wheel and tolerances fixed. The frozen reference needs
composition, packing and pressure continuation at the same loading from a
nearby lower temperature. The parent failures tested here arise because the
fit's bubble diagnostic fails from its initial pressure; a converged single
liquid already exists. Neighbouring bubble starts recover that diagnostic.
All three original A7 trial-optimizer failures remain unresolved after the
parent-continuation probes. Some converged reference roots also exceed the
declared pressure domain; start correction does not admit those roots.

These are disposable diagnosis results, not a replacement phase family or
physical validation. No original run, notebook, manuscript or solver was
changed. The original 155 files were checked byte for byte before and after
the probes. The inherited build remains unreviewed.

## Question, declarations and identities

This stage asks which missing values are caused by numerical initialization,
which returned roots fail the declared domain, and what correction can be
proposed without changing the Ready design. It follows design revision 2,
SHA-256 `fb771344530184e34fe80c884cbd552780472db9d8abab8c217adc9945992b49`,
especially sections 4 and 5, and the requested CSE failure-triage reference.
Readiness is inherited from the parent task's explicit instruction.

The original feed is 9.7292821 mol analytical MEA, 76.9751925 mol water and
`loading * 9.7292821` mol CO2. Loading is mol CO2/mol MEA; temperature is K;
pressure is Pa; densities are mol/m³; phase amounts are mol on that feed
basis. Liquid supports all nine declared species; vapor supports CO2, MEA
and water. No charged species enter the vapor. All ordinary probes preserve
this basis. The explicitly labelled scaling probe alone multiplies every
feed amount by 0.01 and is excluded from proposed retained calculations.

The reference uses the frozen Original-Born, solvent-only-permittivity
case-7 inputs, explicit absent CO2/MEA cross-association edge, liquid plus
pinned-zero vapor, free pressure initially 7398.16 Pa, and the five constant
EOS-standard-state reaction logarithms from the retained input. Their
declared temperature interval is 250–450 K; the parameter document's
candidate interval is 293.15–393.15 K and 1–10,000,000 Pa. These declarations
do not establish experimental validity. Reference input hashes are in
`../input-hashes.json` and the checked runtime mapping hash is in
`verification.json`.

Both fits retain the inherited chemistry and neutral-reference construction
from `heat_evidence_170.request` and `final_evidence.flash_problem`.
A6 parameter-byte SHA-256 is
`ceefc95cd051fb291e0c08675c4cb6f159bf10dca0116ef1251ba78c243f79c7`;
A7 is `e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e`.
Engine commit is `8298c6029ebb8b467929badc4a223c580ec591ab`; installed wheel
SHA-256 is `8897a0caab9f2508ed642f42c8b5226957fbe7035ed7bfdad71e4166798785b3`.
Every worker verifies the wheel bytes and records its installed path. The
environment is Python 3.13.14, NumPy 2.4.4 and SciPy 1.17.1. Only the installed
immutable wheel was imported, with current-worktree MEA modules.

Row tolerance remains `1e-10`. Default single solves retain their Engine
limits; the inherited parent recovery retains its two-start, 400-per-attempt,
800-total limits. No option, row scaling rule, finite-descent rule, trial
count or numerical acceptance threshold was changed. Later probe files also
record the returned effective solver settings and linear solver. Earlier
files predate that diagnostic-field addition, without a change in calculation.

The source commit is `86ee3bad6ab5521a010154e63d24eece4738c451`, fast-forwarded
onto this task branch. The retained `producer.py.txt` differs from the WIP
launcher in reporting, checkpoint writing and reductions. Its reference
calculation is unchanged. Both hashes, plus the unchanged state-calculation
owner, are recorded in `verification.json`; these diagnosis results do not
certify the WIP build or its reductions.

## Frozen-reference solve: reproduction and explanations

`ref-cold-393-low.json` reproduces the original 393.15 K, loading `1e-5`
failure exactly: `LOCAL_INFEASIBILITY`, stop `infeasible`, residual
0.09362552048968942 after 96 closure iterations. The returned solver iteration
count is separately 109. There is no admitted pressure, composition, density,
coordinate vector or phase amount. Row 9 is the liquid pressure equation,
residual 0.09362552048968942. Material-balance rows 15 and 16, in the native
conserved-quantity basis, are 0.08390179240929078 and 0.0839020424071192.
All other classified rows are below `1e-10`. The predicted numerical floor
is `1.35289606837796e-10`, far below the actual failed residual. This is an
infeasible solver iterate, not proof of infeasible physical equations.
The same row identities are explicitly retained by the subsequent probes.

Ranked explanations and falsifiers:

1. **Starting state outside the convergent region: supported.** A complete
   physical start from the successful 353.15 K reference at the same loading
   gives 173333.00198051374 Pa at 393.15 K, with maximum raw residual
   `5.684341886080802e-14`, in 12 closure iterations. Liquid amount is
   86.70457188869062 mol, vapor amount is exactly zero, reduced-Hessian minimum
   is zero, and both pressure-density derivatives are positive
   (64786.3521 and 3139.7271 Pa m³/mol). It passes the unchanged reference
   admission checks. At 373.15 K the same start gives 87806.81207878212 Pa,
   residual `5.684341886080802e-14`, in 11 iterations.
2. **Inadequate pressure guess alone: insufficient for this reference.**
   Setting only the initial pressure to the recovered 173333.002 Pa still
   fails: residual 0.4937962565, with material-balance rows 16 and 17 failing.
   Direct continuation from the 313.15 K anchor to 393.15 K also fails
   (0.0936443478). Continuing loading from `1e-5` to 0.05 at 393.15 K fails
   (1.0000001814). Merely using any previous solution is insufficient.
3. **Extensive-feed scaling: not supported as the correction tested.**
   The cold solve with every feed amount divided by 100 still fails at
   residual 0.0936255126 after 114 iterations, in the same pressure and
   material-balance rows. This excludes that particular scaling fix; it
   does not test all possible equation conditioning or precision changes.
4. **No liquid–vapor bubble root or temperature outside declaration:**
   contradicted for the recovered cases. The requested temperatures lie in
   the recorded temperature declarations, and admitted roots were returned.
   Experimental accuracy and uniqueness of those roots remain unknown.

Same-loading continuation from the retained 373.15 K roots also gives
393.15 K pressures 1386128.2740195496, 2613492.5300919665 and
5137766.2253514845 Pa at loadings 0.05, 0.1 and 0.2. Their maximum raw
residuals are at most `1.1368683772161603e-13`; each needs three closure
iterations, has positive liquid and zero vapor amounts, nonnegative
reduced-Hessian minimum and positive pressure-density derivatives. These
are useful numerical results from the fixed reference equations.

**Domain admission is a separate issue.** In the original run, the two
353.15 K references at loadings 0.5 and 0.6 converge to 10.72218449 and
15.49186181 MPa. The corresponding 373.15 K references converge to
13.07149288 and 17.84320026 MPa. These four cases account for six unavailable
states at each temperature per fit; they are pressure exclusions rather than
nonconverged solves. The additional three unavailable 373.15 K states arise
from the low-loading nonconvergence.

As a correction attempt for the first domain-excluded reference, continuing
353.15 K/loading 0.5 from the qualified 333.15 K/loading 0.5 anchor gives
10722184.49030041 Pa, agreeing with the original root to relative
`8.0e-15`; raw residual is `1.1368683772161603e-13`. The root remains excluded.
Likewise, correcting 393.15 K/loading 0.4 gives 10775510.966802668 Pa with
raw residual `5.684341886080802e-14`, but admission remains false. These
mathematical roots are not admitted physical results within the chosen
pressure domain. This does not prove that an exhaustive root search would
find no other root. No reference root was substituted or pressure clamped.

The 393.15 K reference cases at loadings 0.25557798094241313, 0.3, 0.5 and
0.6 were not re-solved during diagnosis. Their original non-results remain
non-results; success of the tested continuation is not extrapolated to them.

## Parent flash: reproduction and correction

All 18 original parent failures per fit have a successful single-liquid
diagnosis and an unsuccessful bubble diagnosis. The exact 36 cases are in
`failure-cases.csv`. They cover loadings 0.2, 0.25557798094241313 and 0.3 at
fractions 0.8 and 0.95, and loading 0.4 at all three fractions, at both
353.15 and 373.15 K. They are distinct from the reference exclusions.

At A7 state 28, loading 0.2, 353.15 K and 2855660.9360872805 Pa, the original
liquid converges with residual `7.394922169312439e-14`. The bubble diagnostic
starts at that imposed pressure and fails with residual 0.7399819144835588
after 83 closure iterations. The failing classified row is vapor
normalization, row 19, at -0.7399819144835588. `bubble-cold-a7-28.json`
reproduces this exactly; `parent-cold-a7-28.json` also reproduces the missing
final parent through the unchanged `family_job` with empty recovery history.
The original record retains two nearest two-phase recovery attempts as well.

Ranked explanations and falsifiers:

1. **Bubble initialization: supported.** Reusing state 27's same-temperature,
   same-loading bubble composition, packing and pressure converges in one
   closure iteration to 41767.47872334231 Pa, maximum raw residual
   `2.8421709430404007e-13`. Keeping the target liquid composition/packing
   and changing only the pressure guess also converges in two iterations to
   41767.478723341446 Pa. The imposed pressure is about 68 times this bubble
   pressure. The declared single-liquid branch is therefore selected by the
   inherited procedure. It passes the raw residual, amount, derivative and
   Hessian checks and returns nine successful trials with zero resolved
   descents (`passed-single-liquid`).
2. **A forced two-phase parent above the fit's own bubble: supported as the
   explanation of the failed liquid/vapor attempts.** The original attempts
   report vanished vapor phases. `family_job` chooses the single-liquid
   result only after a successful bubble diagnostic. Its failed bubble
   solve prevents that choice despite the available converged liquid.
   This is not evidence of an invalid single-liquid model state.
3. **Too few nearest-history starts or recovery iterations: lower priority.**
   The original states already try the permitted nearest starts. Continuing
   a two-phase history cannot make a positive vapor amount the expected
   parent at these tested pressures. Bubble initialization fixes the missing
   parent without extra two-phase starts or iteration increases.
4. **Checks too strict: unsupported.** The corrected states meet the original
   checks, so weakening them is unnecessary and prohibited.

The same-temperature bubble correction also recovers A7 state 54
(353.15 K, loading 0.4, 3934866.0148269394 Pa; bubble 47361.83363528192 Pa)
and state 58 (373.15 K, loading 0.4, 7770488.787037492 Pa; bubble
119369.5060989532 Pa). Both return complete nine-trial searches, no resolved
descent and `passed-single-liquid`. Unprobed parent cases are not counted
as recovered.

A6 state 58 also recovers its bubble at 125782.94358403931 Pa, maximum raw
residual `3.126388037344441e-13`; its converged parent has maximum raw
residual `1.1368683772161603e-13`. Its subsequent search has four resolved
liquid-trial descents. The most negative finite split has
`delta_G/RT = -0.1831170218756597`, error estimate `6.437308475199757e-8`,
and transfer amount 8.370794125942691 mol. This remains an A6 descent despite
recovering the numerical parent. It is a new disposable probe observation,
not a change to the original counts, and no seeded confirmation was attempted
in this diagnosis stage.

## Three unresolved A7 trial optimizers

The original cases are states 10 and 11 at 353.15 K/loading 0.05, pressures
653529.8105062192 and 776066.6499761352 Pa, and state 22 at
373.15 K/loading 0.1, 1827110.123551797 Pa. Each has all nine returned
trials, with the liquid `near-pure-0` optimizer unsuccessful. Their parents
are converged and admitted; these are not missing-parent cases.

`trials-cold-a7-10.json` reproduces native trial index 1 exactly:
`stalled`, residual `3.700114059031003e-6`, 21 closure iterations,
310 closure evaluations, numerical floor `1.0114526119935869e-14`.
Classified chemical rows 3–8 fail, the largest at row 6. Their raw chemical
residuals include 370.0113999775557 at row 6. Pressure, normalization and
balance rows remain small. The raw ionic log fractions cluster near
`log(1e-8)`; the returned trial tangent-plane distance is positive,
2.702046965356402. That positive evaluated value does not repair the failed
stationarity solve or complete the declared search.

Continuing the parent from the lower-pressure single liquid at the same
temperature/loading changes state 10's trial residual to
`1.0813986295784726e-9`, still stalled above `1e-10`. In this probe the
maximum failure moves to pressure row 9; chemical row 2 also exceeds
tolerance. Rows 10–12 remain below tolerance. This demonstrates sensitivity to parent/initial numerical values,
not successful correction. The same parent-continuation attempt leaves
state 11 at `3.538167385133682e-6` and state 22 at
`2.5008523223328345e-6`, both stalled.

The remaining explanations are, in order: a trial optimizer's starting
composition/density and trace-species conditioning; its numerical refinement
or stopping behavior; then other precision effects. The source at the
pinned Engine commit puts the ionic trial through the shared driver and
generates the near-pure starts internally (`phase_stability.cpp:530–563,
599–620`; `request_compile.cpp:1368–1410`). MEA's supplied composition is
not a replacement optimized start in the default nine-start search.
`evaluate_supplied_trials` evaluates supplied points without that optimization;
using it would change the method. No altered Engine trial solver or optimizer
start was tested. A correction of those internal mechanics requires an
Engine-owned issue and a design decision before retained use. The narrower
launcher correction was tried and did not resolve these cases; this report
does not close them as final physical limitations.

## Proposed re-run and scientific limits

A new attempt is justified for numerical recovery, within the Ready design's
initialization boundary: reuse admitted same-loading reference solutions at
nearby lower temperature, and initialize each fit's bubble diagnostic from a
successful neighbouring same-temperature bubble. Preserve all original
attempts, pressure construction, finite trials, row checks and iteration
limits. Keep the original loading/pressure order for the parent history.
The tested reference correction needs actual lower-temperature solutions;
the long anchor jump and low-to-0.05 loading jump are not supported substitutes.
The parent may arrange those dependencies in the launcher or reuse the
unchanged first-attempt reference files. No retained correction or campaign
re-run was performed here; later attempts need a distinct output directory
and must fit the existing allocation, without an automatic increase.

Retain the exact 1–10,000,000 Pa candidate interval; returned reference
pressures above its upper boundary remain excluded. Admitting the recovered 10.776 MPa reference,
changing the reference model or pressure fractions, changing the finite
trial optimizer, or raising any allocation requires Design and appropriate
authority. Removing the reference-pressure gate merely because a pressure
fraction lies below 10 MPa also changes the Ready admission rule. The current
root evidence does not permit a complete zero-descent claim on all 81 states.

The original A7 evidence is zero detected descents in 189 returned trials
across 21 of 81 states: 18 pass and three remain unresolved. Forty-two states
are unavailable from reference admission and 18 more have missing parents.
This is not a completed 729-trial zero-descent result. The original A6 has
five descending states and six resolved trials; the extra state-58 probe
descents are recorded separately. These are finite-search numerical findings
and model predictions. They establish neither global stability, physical
liquid separation, high-temperature physical validation, uncertainty in
fitted parameters, nor absorber/stripper performance.

Issue 197 may eventually use reviewed results with these denominators and
limits after investigator promotion. It cannot claim the 81-state extension
is complete from the WIP outputs or these probes. No manuscript or notebook
changes were made. The source distinction between finding a negative trial
and proving a global solution is consistent with Pereira et al. (2012),
sections 3.1 and 3.4; section 3.3.3 discusses trace-component numerical
refinement. Its HELD algorithm is not the Engine's solver and supplies no
MEA validation data. Those actual sections were read from the main-checkout
literature shelf; the current Zotero Markdown matched the shelf index at
SHA-256 `f5cb0f043b6e9b9f19ac25f07a9694e7cd3eb985146fafaf7a0599619152c543`.
No new literature-backed validity threshold is asserted.

## Commands, retained evidence and budget

Every original failure's exact state, units by the conventions above,
termination and source is in `failure-cases.csv` (14 reference cases,
36 parent cases, three trial cases). `probe-summary.csv` contains all 23
probe outcomes. Full compositions, phase amounts, densities, coordinates,
raw/classified residuals, feasibility quantities, solver messages and finite
trial reports are in the individual JSON files. No missing quantity is
represented as zero. `budget.json` contains each exact command, captured
process ID, host load, elapsed wall and consumed CPU time, exit and kill
information, and maximum resident memory. `.log` files retain command output.

All commands used this prefix from the task worktree:

```bash
nice -n 10 agent-heavy uv run --frozen --no-sync python \
  analyses/mea_parameter_bundle/results/phase-extension-201/diagnosis/probes.py
```

The narrowest reference reproduction appends
`reference ref-cold-393-low --temperature 393.15 --loading 0.00001`.
Its successful correction appends
`reference ref-warm-393-low --temperature 393.15 --loading 0.00001 --seed analyses/mea_parameter_bundle/results/phase-extension-201/reference-pressure/reference-353.15-0.json`.
The narrowest parent diagnostic reproduction appends
`bubble bubble-cold-a7-28 --index 28`; its successful correction appends
`bubble bubble-warm-a7-28 --index 28 --seed analyses/mea_parameter_bundle/results/phase-extension-201/A7/point-27.json`.
The trial reproduction appends `trials trials-cold-a7-10 --index 10`.
These are the actual executed commands; the script rejects existing output
names, so a later authorized repetition must use a fresh name. The supervisor
charges every process, including solver failures and unsuccessful correction
attempts, and enforces the cumulative compute ceilings with a captured
process group and a maximum 150-second command allowance. Only its own
launched group can be terminated. No process was killed in this run.

All workers ran at niceness 10 with OMP, OpenBLAS, MKL, BLIS and NumExpr
thread variables set to one before numerical imports. The 23 whole worker
commands used **131.926757 wall-s and 130.974927 CPU-s**, including imports,
failed solves and all correction attempts, against **900 wall-s / 2700 CPU-s**.
The largest measured worker memory was **97144 KiB**. Budget totals are sums
of command elapsed time, not time spent reading or writing this diagnosis.
The separate `uv sync --frozen` setup took 0.67 wall-s and ran no scientific
calculation. No additional numerical work is running.

The assertions summarized in `verification.json` check corrected reference
admission/residuals, three complete A7 parent searches, preservation of the
inadmissible recovered reference, failure-case accounting, budget limits,
and unchanged original outputs. The old phase CSV, old point declaration
and both parameter-byte hashes also match the Ready design. There was no
Engine edit, notebook edit, manuscript edit, system-browser operation,
Quarto-service action, agent-memory write or remote GitHub mutation.
Independent review and any re-run remain with the parent.
