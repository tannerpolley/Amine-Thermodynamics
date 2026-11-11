# Adoption of the #255 MEA record, issue #297

The owner selected the #255 wide-start primary on 2026-11-11. This change adopts its exact bytes (`f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97`) together with Engine `391dfe5d64ede5036bf160bc6ae037ad5e14af32`. No parameter fit, new start, retreat or selection was run. Implementation base: `e165b828624e7ddd41f3011142936fc524a51455`. Independent delivered review remains for the orchestrator; this package is not investigator promotion for manuscript use.

## Numerical evidence

| Gate | Result |
|---|---|
| F1 | Both 307-row replays available with exact observation declarations and frozen input bytes. Largest relative prediction differences: incumbent 6.273797117442816e-14; candidate 2.1015413489803645e-13. Costs 148.88326044022858 and 148.51054565397726. Relative cost differences 1.5271943586600474e-15 and 4.784459801364064e-15; limit 1e-10. |
| F2 | Both records: 1903/1903 enforced, 576/576 offset, 162/162 census available, zero resolved descents. All five originally excluded states are available with zero descent; four previously unavailable states became available. Exclusions were not enlarged. |
| F3 | Every inherited group rule passes; candidate cost 148.51054565397726 < 148.88311155696815. See scores below. |
| F4 | Normal 153 quantities: largest relative difference 8.379722527822233e-16. Normal solvent endpoint: 307/307 available and within tolerance; largest prediction difference 0, cost 148.51054565397726. Selected and endpoint bytes are identical. |
| F5 | 4820 overlapping physical quantities agree with #255; largest relative difference 2.1015413489803645e-13, on vle_obs_0193-pco2 (absolute 1.5963451005518436e-08 Pa); limit 1e-8. Row identities and declared availability agree. |

The four formerly excluded states at 25 wt% MEA and loading $10^{-5}$, at 313.15 and 323.15 K and each at pressure ratios 1.05 and 3, are now available with no descent: before, the 313.15 K pair reported “parent plane uncertainty unavailable” and the 323.15 K pair reported a failed bubble-pressure reference solve; the responsible Engine change was not isolated.

These results are numerical verification and calibration-quality comparison, with fixed-parameter predictions against previously accessed observations. They are not new independent physical validation. The 307-row declaration and #260 caloric record were unchanged during qualification. `input-identity.json` compares their byte identities against accepted #255 commit `e9009a8`; `wheel.json` records installed-wheel origin and native/package byte hashes.

## Every #255 group rule

| Group | Candidate score | Limit / incumbent |
|---|---|
| CO2-free density | within twice scale 5; AARD ratio 1.01460666787; RMSE ratio 1.01495145342 | count ≥ 5; both ratios ≤ 1.25 |
| Jakobsen ratio | AARD rise -0.478322508797 percentage points | ≤ 2 percentage points |
| Kiepe pressure | AARD rise 0 percentage points | ≤ 2 percentage points |
| fitted CO2 partial pressure | AARD rise -0.0745907931606 percentage points | ≤ 2 percentage points |
| fitted heat of absorption | within twice scale 8; AARD ratio 1.01135204868; RMSE ratio 1.00102621061 | count ≥ 8; both ratios ≤ 1.25 |
| fitted phase mole fraction | AARD rise 0.0115510176611 percentage points | ≤ 2 percentage points |
| heat capacity | within twice scale 3; AARD ratio 0.973799953365; RMSE ratio 0.978882643469 | count ≥ 3; both ratios ≤ 1.25 |
| loaded density | within twice scale 46; AARD ratio 0.915531009223; RMSE ratio 0.902139984108 | count ≥ 44; both ratios ≤ 1.25 |
| restored species | AARD rise -0.0386102964014 percentage points | ≤ 2 percentage points |

Cai is report-only: 50 available rows, 36 within twice row scale, AARD 1.480133268797904%. The 25 temperature rows have RMSE 1.7870860894407765 K; the 25 mole-fraction rows have RMSE 0.020383219381861897. Units are separated in `cai-units.json`. Observation cost is reported separately from stability: the signed native stability values are zero at every available enforced state, so the finite requirement contributes zero squared stability cost. These thresholds are repository choices, not published universal standards.

Six active bounds are listed in `conditional-uncertainty.json`. MEAH+ segment diameter is 4.904548117641809 Å, outside the outgoing restricted interval [5.35, 5.8] Å; `restricted-bound-departures.json` lists this departure. The other disclosed bounds are MEAH+–water −0.5, bicarbonate–water +1, carbamate–MEAH+ −1, both Born diameters 5 Å, and R5 total enthalpy shift +10000 J/mol.

## Wheel and execution

Wheel SHA-256: `0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b`. The existing Engine `tools/build-engine.sh --wheel` built the checked-out merged commit after synchronizing its main to origin/main. No Engine source was edited. Build and numerical commands ran under `agent-heavy`; process pools used its three-core allowance with single-threaded numerical libraries. `logs/wheel-build.log` retains the build.

Identical wheel copies are at `build/engine-wheels/main-391dfe5d64ede5036bf160bc6ae037ad5e14af32/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl` under this worktree and `/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/`. The latter survives worktree removal. The rebuilt wheel has the same SHA-256 as the wheel used by #284: the build reproduced the same bytes. Qualification checked the rebuilt bytes rather than assuming equality.

Qualification commands: `adoption_297.py f1`, `f2`, `f3`, `evidence`, `extras`, `phase-export`, `f5`. The producer contains no fitting call. F2 saves each completed state separately and resumes only missing states. It uses the exact #255 native Full liquid-parent requirement and original census producer; candidate-dependent bubble pressures are recomputed. Census pressures retain the outgoing reference. State-level numerical results are in `incumbent/` and `candidate/`; native census trial diagnostics are retained in each census JSON. The phase export contains 162 fresh candidate rows and the 162 unchanged historical comparison rows, each labeled by its own wheel and parameter hash.

Defaults were replaced together after F1–F3 and the numerical package completed. Fresh normal commands were environment validation, `check_a7_selected.py`, `analyses/solvent_specification_mea/run.py`, `generate_figure_data.py`, the retained replay reduction and both notebook renderers. There was no numerical command between partial pin/record edits. Corrected stale consumer assertions and bindings are retained in the execution logs. The initial terminal assertion in the normal endpoint command still held the old cost even though all 307 rows matched; it now derives its reference cost from the qualified rows.

The default replay declaration previously pinned pre-#260 physical ideal-gas calorics. Its new binding names the current qualified bytes; `default-spec-binding-changes.json` records the change. The figure command also had a pre-#152 canonical-speciation hash and selected 30 wt% at 80 °C. The current source records that series at 31 wt%, as in #255. All four grid loading endpoints are unchanged (`canonical-speciation-source-comparison.json`). These are source/input-binding changes, not measured Engine effects. Three canonical pressure states outside the declared reaction domain remain excluded; figure outputs retain every attempted state and diagnostic.

## Conditional information

The exact native #255 coordinate chart was differentiated at the fixed candidate. Its predictions agree with the direct replay within 4.206226655888516e-13 relative. The free-coordinate Jacobian has rank 10. Six active coordinates are held fixed; the remaining errors and correlations are conditional on inputs, row weights and local linearization, with 297 degrees of freedom. They do not quantify prediction intervals or the uncertainty of the stability boundary. R5 below is the completed native b coordinate (K), retaining #255’s identity label; it is not the unshifted source A.

| Free coordinate | Conditional standard error |
|---|---|
| `component/carbamate-anion/dispersion_energy_over_k` | 36.1519257559088 |
| `component/carbamate-anion/segment_diameter` | 0.978333810283774 |
| `component/protonated-monoethanolamine/dispersion_energy_over_k` | 51.3084747357223 |
| `component/protonated-monoethanolamine/segment_diameter` | 1.08023503337279 |
| `pair/carbamate-anion/water/k_ij` | 0.144399109777138 |
| `pair/monoethanolamine/water/k_ij` | 0.00128763177457311 |
| `pair/monoethanolamine/water/k_ij/reciprocal_temperature_slope` | 2.04289718377521 |
| `pair/protonated-monoethanolamine/water/k_ij/reciprocal_temperature_slope` | 65.397459943683 |
| `reaction:R2:enthalpy_shift` | 5227.76651574866 |
| `reaction:R5:correlation:a_k` | 265.195066418746 |

Full coordinate values, units and bounds are in `paper-evidence/fit-summary.json`; standard errors, correlations and the weighted native Jacobian are retained separately. No #212 uncertainty was reused.

## Handoff to #298 and limits

The shared bicarbonate–water interaction is exactly **+1.0** (dimensionless), with the full pair declaration in `shared-bicarbonate-water.json`. The completed R2 law is in `shared-R2.json`, its full reaction declaration in `shared-R2-declaration.json`, and their hashes in `shared-hashes.json`. The law has a=23.87092013089665, b=−12017.430996556475 K, c=−36.7816, d=e=f=0, reference temperature 313.15 K and domain 293.15–393.15 K, in `aqueous-molality-infinite-dilution-water-v1`. In the native convention, ln K = a + b/T + c ln(T/313.15 K). MDEA files and its frozen reaction reference were not changed.

Concentration transfer remains uneven (15 wt% AARD 29.49→33.89%; 45 wt% 56.04→44.53%). The unloaded 318.15 K Cp deviation remains +5.43%; the temperature slope, 353 K carbamate excess and carbonate share are unresolved. #284’s decomposition remains evidence about the outgoing record. #282’s salt-anchored alternative and #283’s temperature-dependent ion study do not identify unique transferable ion parameters. Their campaigns were not repeated. The original #255 fit’s iteration/evaluation counts remain those returned in its retained fit file; adoption ran no optimizer and asserts no global or local constrained optimality.

Fixed substitution into the old MDEA-specific parameters gives Xiao pressure deviations 52.9%/58.6% and Ermatchkov 52.5%/42.0%. These are the retained #255 transfer comparisons, not new MDEA fits. #298 owns its replacement evidence and heat availability. Finite stability searches are not a global stability certificate, and this record is not qualified for absorber/process use. Manuscript work remains #259 and requires investigator promotion after review.

## Retained inputs and consumers

`inventory.json` identifies current candidate calculations, source-only inputs and explicitly historical comparisons by file hash. `historical-display-inputs.json` retains the older comparison calculations without rerunning or relabeling them. `historical-spec/` freezes the outgoing solvent endpoint, reaction declaration and baseline reference for historical studies. All binding-file changes are accounted for in `changed-files.json`, the authority for final changed-file hashes. Current-output inventory entries must differ from implementation base `e165b828624e7ddd41f3011142936fc524a51455` and lie in the explicit output paths of the #297 figure, table or normal-endpoint commands; `adoption_297.py inventory` applies that rule and records the producing command, rather than classifying any file whose path contains a figure-output directory.

Historical #255 final, #261, #268, #284, #285 and AMP references now point to the immutable outgoing endpoint. The permittivity study also uses the frozen solvent specification and reference. Historical fit-check declarations retain the outgoing endpoint. No historical study was rerun or rescored.

Additional readers found: `analyses/permittivity_temperature_loading/present.py` reads only component identifiers (unchanged) and needs no numerical rebinding; `analyses/solvent_specification_mea/prepare.py` is the historical materialization producer and refuses the new selected bytes at its existing assertion before producing the old declaration; it was not run. `compare_engines.py` is an unpinned comparison command and follows the selected record by design. The shared-evaluation test reads a record explicitly from Git history and remains historical. Retained scripts under old results directories are archived evidence and were not edited. Generic default readers follow the new selected record. MDEA readers remain for #298, and manuscript/deposit readers remain outside this task.

The package excludes regenerable solve caches and execution-staging duplicates from Git, while retaining their producer snapshots and the canonical numerical outputs. Logs include unsuccessful stale-binding attempts as well as successful commands.

## Change accounting

The fixed-base accounting is `change-accounting.json`. It counts 454 gross executable additions and 193 removals, plus one changed existing test line. Retained executable producer snapshots are counted conservatively as executable below rather than hidden in the generic file classification. The 300-line design figure was an estimate, not a ceiling. Additional responsibilities are the exact input-identity inventory, resumable state output, native conditional information and coordinated default/historical bindings; no fitting or solver implementation was added. The superseded reduction of historical fit outputs was replaced by reduction of the qualified fixed-parameter replay.

Retained executable snapshots add 1115 gross lines; the conservative executable total is 1569. Generated numerical rows, notebook prose and plots are separate.

The historical binding check verifies 1052 referenced file hashes. The original #261 study still pinned the pre-#260 caloric bytes through a mutable path. Those exact bytes are now frozen as `historical-spec/pre-260-caloric.json` (SHA-256 `71c0f65204de5f10a22099db8ee6a939895bf280c725292e2cc46c0b1ebe9ef1`), recovered from `0e216fe^`. Its hash is preserved; the study was not rerun. All 1052 bindings now resolve to their declared bytes.
