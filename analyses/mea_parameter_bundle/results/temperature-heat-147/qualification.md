# Issue 147 phase B — qualification stopped at the exact-zero-carbon endpoint

The OLD replay and frozen-law mapping pass. The first Vinjarapu finite-addition
observation returns no heat: its initial endpoint is numerically unavailable.
Phase B is **incomplete**, not a negative calorimetric finding. No later check,
retry, fitted parameter, changed tolerance or positive-carbon substitute was used.
Source admission remains the independently Supported phase-A result at `845e98a`.

## Checks in the authorized order

1. **OLD replay: pass.** All 84 states and 142 targets were recalculated with
   independent empty numerical caches. Every prediction matches its retained
   reference exactly, so the maximum prediction/allowance ratio is zero.
   Costs are pressure **8.14345313051485**, species **24.848444130706277** and
   total **32.991897261221126**; all three cost differences are zero.
   `old-replay-states.json` retains every state, returned row, attempted solve,
   convergence/reference diagnostic and failure field. `old-replay-targets.csv`
   retains all predictions, differences, allowances and row costs.
2. **R2/R4/R5 mapping: pass.** The 12 direct native ln K values at
   293.15/313.15/333.15/353.15 K agree with their frozen four-term document laws;
   maximum absolute difference is **7.815970093361102e-14**, below 5e-13.
   Native a versus A+C ln(313.15) was checked. R2 reference pressure is
   **101325 Pa**; R4/R5 use **100000 Pa**, all common-molality references.
   `native-law-mapping.csv` retains both ln K values and both RT² derivative
   expressions. The derivative comparison checks stored versus native polynomial
   coefficients, with the native expression independently inspected in
   `engine/native/properties/thermochemistry.cpp:221–229`; it is not a newly
   qualified solved-state temperature action. Phase-A source-representation
   grids, maxima and continuation errors remain unchanged and admitted only
   within their previously frozen intervals. `campaign-reactions.json` fixes all
   five reaction declarations; R1/R3 retain their inherited raw-mole-fraction
   source conversions, with no added 55.51 factor.
3. **Vinjarapu 0→0.11: fail at the initial endpoint.** T=313.15 K,
   P=1734000 Pa, 30 wt% unloaded solvent, exactly 1 mol MEA and
   **7.911062165006594 mol water**. Initial CO2 feed is **exactly 0 mol**;
   final CO2 feed is **0.11 mol**. All other component feeds are zero.
   Componentwise final−initial−0.11·pure-CO2 feed is zero. Both endpoint
   problems carry the identical five reactions, source pressures and neutral
   reference, and declare one reacting liquid; the CO2 feed hint is `vapor`.
   The accepted physical default-start inputs are reused from #140's source
   reset, not an adopted fitted interaction vector. Its obsolete reaction
   metadata is not consumed: the endpoint Problems own the frozen new chemistry.
   The native observation compiles but its first prediction returns
   `CentralSolveUnavailable`, with this exact diagnostic:

   ```text
   initial:central_solve_unavailable: SUCCESS: stalled: residual 1.1966663563277393e-07 against EQUILIBRIUM_ROW_RESIDUAL 1e-10 after 28 iterations, contraction absent, floor 1.7641264140878111e-10, amplification 0
   ```

   Native requested tolerance is not met. There were 28 iterations and 43
   evaluations; reported floor is 1.764126414087811e-10, amplification zero,
   contraction unavailable. The heat value and residual are null. Ipopt's
   `SUCCESS` label does not override the Engine's recomputed failed convergence.
   No admitted initial state, caloric value or exothermic-sign result exists.
   **0→0.45 was not run.**
4. **Independent endpoint/feed enthalpies, +10 kJ/mol anchor invariance and
   conditioning: not reached.** No replacement total H or conditioning ratio
   is invented after the initial endpoint failure.
5. **Exact heat Jacobian against h/2h centered re-solves: not reached.** Q2 was
   not started; none of the five directions has new MEA qualification evidence.
6. **Convergence/material/charge: training passes, initial calorimetric endpoint
   fails.** Across the OLD replay, maximum material error is
   **2.0605739337042905e-13 mol**, charge error
   **3.7951851945411784e-14 mol**, and raw stationarity
   **3.979039320256561e-13**. All requested tolerances were met. These material
   and charge maxima were calculated from retained phase amounts/compositions
   and the unchanged packet balances, without another Engine calculation.
   Initial calorimetric material/charge/stationarity values are unavailable:
   the Engine rejects and clears that state.
7. **§6.1 bubble separation, feed-root regularity and declared-phase admission:
   not reached.** The native observation stops before its feed calculation.
   No bubble pressure, Pobs/Pbubble separation, root count, pressure-density
   derivative, enthalpy, or stability conclusion is asserted. No topology switch
   or ideal-gas feed was substituted. Global LLE/solid stability remains outside
   the specified local boundary check.

## Source inspection and required decision

No numerical probe or fix was attempted after the failed check, as instructed.
Read-only Engine inspection identifies a structural boundary mechanism needing
upstream diagnosis. At `717a2990`, `request_compile.cpp:838–915` constructs the
full reaction balance basis and only removes a zero-feed species when it is
**not a reaction participant**. All nine declared species participate in the
five MEA reactions, so the four added-carbon species remain in the declared
support. `gibbs_minimizer.cpp:863–878` represents supported species through
positive exponentials. The conserved added-carbon quantity is

$$n_{\mathrm{CO_2}}+n_{\mathrm{MEACOO^-}}+n_{\mathrm{HCO_3^-}}+n_{\mathrm{CO_3^{2-}}}=\alpha.$$

Its coefficient vector annihilates each of the five frozen reaction rows.
At α=0 all four amounts must be structurally zero, not strictly positive
coordinates. This explains why inactive reacting supports are a consequential
Engine requirement; the returned diagnostic does not identify which individual
residual dominates the stalled solve. A bounded upstream trace diagnosis is
needed to establish the complete numerical cause and correction. No local
solver, reaction deletion, seed-carbon regularization or tolerance change is
permitted here. A corrected wheel would require an owner amendment of the
717a2990 pin and renewed qualification. No upstream issue was opened or changed.

## Wheel, computation and retained identities

The Engine's own `.codex/environments/setup.sh` and
`tools/ensure-engine-wheel.sh` ran in the separate local clone
`/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-build-717a2990`, detached at
**717a2990e443423e051fc0569f25209d04007543**. No command built, installed or
checked out code in the active Engine checkout. The build script restored its
fingerprint-matched shared cache; **no fresh C++ compilation was claimed**.
The clone remains clean.

- Wheel SHA-256: `9e6a76cf59d4e2fef3347d895bf3a966ecced01f13dc6e0caec74c3c3d618dc4`.
- Wheel fingerprint: `95b2495a5b66332f49f4609e0dd3d57fa1e010c63794c9d3a2d627d689a8bbaf`.
- Build fingerprint: `18483e74957c5a9e6bb6e1b64f610e0c9da32fb8bd18b51357206e5d29786a6d`.
- Toolchain fingerprint: `f6db693e21e289603ae71c78242a17b102f1e324061021d5dca361f47a0bfef7`.

`wheel-identity.json` retains the source commit, actual module origin, installed
file hashes including installation metadata, direct URL and input hashes.
`build-toolchain.json` and the byte-preserving `engine-build.log.gz` retain
compiler/build/dependency versions and build controls. The isolated uv
installation is non-editable; all 14 wheel RECORD hashes match. Neither
`direct_url.json` nor `RECORD` was rewritten. Runtime imports use the isolated
site-packages, never the Engine source. Generic #210 F1–F8 evidence is cited
unmodified by path, wheel identity and hashes in `qualification.json`; its
manufactured systems are not MEA boundary qualification and were not rerun.

CPU affinity is **12 CPUs**, not the issue's earlier machine example of ten.
`EPCSAFT_BUILD_JOBS=12`; the R1 pool has 12 single-threaded workers, with
OMP/OPENBLAS/MKL thread limits all one. R1 wall time is **4.663484371 s**;
summed worker elapsed time is **43.138958198 s**. The failed native heat
prediction took **0.183327334 s**, single-threaded and serial because the
required initial observation precedes the second state. The twelve direct ln K
calls were not separately timed. Engine preparation, R1 and Q1 mapping used
external total limits of 1800, 1800 and 1770 s; the individual heat observation
used `timeout -k 5s 175s` (180 s including kill grace). Q1 stopped at this failure;
there were no retries, Q2, fits, or other numerical batches.

The exact executed producer versions are retained in local Git history:
R1 at `c277710`, mapping at `0bc35b7`, and the failed heat producer in the final
qualification commit. No numerical job was rerun while retaining these versions.
`qualification.json` reads retained numbers; `SHA256SUMS` binds written files.
Phase-A frozen inputs and scientific results remain unchanged.

The sole phase-B executable addition is `qualify.py`: **211 gross lines**,
including comments/blanks; no executable tests or fixtures were added.
Accounting from **76ea465** is **120 phase-A + 211 phase-B = 331 gross lines**,
leaving **119** of the 450-line ceiling. No pressure/species/training,
qualification-adoption, parameter-record or manuscript input was edited, and no
#152-corrected target was used. Independent review of this stopped phase-B
execution remains for the parent; nothing was pushed or published remotely.
