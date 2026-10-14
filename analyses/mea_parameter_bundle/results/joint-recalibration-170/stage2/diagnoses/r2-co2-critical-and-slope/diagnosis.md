# Stage 2 CO₂–water: critical point and temperature-slope diagnosis

The tested constant-interaction fits seek a larger interaction to reduce the higher-temperature pressure underprediction, but rejected trials lose the anchored CO₂-rich vapor branch at the high-pressure 313.20 K rows. A reciprocal-temperature slope resolves this conflict in the bounded experiment: two starts converge in four iterations, all 39 rows remain available, and cost falls from 1.255881 to 0.02648176. This supports an owner-approved temperature-dependent interaction as the smallest remedy tested here.

The proposed explanation needs correction. With the current CO₂ dispersion energy of 169.21 K, the Engine pure-CO₂ critical temperature is **310.276799 K**, below 313.20 K. With the old energy of 173.44025 K it is **318.033719 K**, above 313.20 K. Both overshoot real CO₂, but only the old value makes pure CO₂ subcritical at the requested temperature. Water at mole fraction 0.017 produces a mechanical loop at 313.20 K even with the current energy. That fixed composition represents a diagnostic neighboring state, not the final slope-fit composition or a computed mixture critical point.

These are disposable numerical diagnosis and calibration comparisons. No parameter set is adopted, no notebook or frozen record is changed, and no independent review or physical validation is claimed.

## Basis and methods

Existing worktree `/home/tnnrpolley21/.t3/worktrees/Amine-Thermodynamics/t3-170-stage-2-build-and-run-mea-water-an-c331b494`, HEAD `173b75b`. Git tracked state was clean before and after the probes. Used installed CSE research/diagnosis instructions, repository instructions and scientific map, the actual issue #170 design and amendment, the frozen Stage 2 inputs, and the earlier scratch diagnosis. Neither journal memory file nor the literature shelf exists in this worktree; source reading used the main checkout's shelf/index and current Zotero originals.

Engine merged main `36485a88`, immutable wheel SHA-256 `da5a2b65668ab5647e51b917a659614bdcb4afbe7e5c3149aee2294b86a4c1bd`. All 11 installed Engine files match the wheel bytes (`wheel-check.json`). Used `tmp/stage2/venv`, `PYTHONPATH=src:analyses/mea_parameter_bundle/scripts`, `nice -n 10`, single-threaded numerical libraries, and one native fit worker. CoolProp 8.0.0 was installed inside this ignored scratch environment solely for the independent pure-CO₂ comparison.

CO₂ segment count 2.0729 and diameter 2.7852 Å; new water and refreshed reciprocal association remain fixed. The old-energy probe changes CO₂ dispersion only. Temperature, one-mole liquid composition/feed, zero incipient amount, two neutral phase supports, original liquid/vapor declarations, native observation weights and log-pressure residuals remain unchanged. The equilibrium row tolerance is 1e-10.

Pure saturation was traced with the native `Pure.saturation` and `solve_equilibrium` routines. The installed public interface has no callable critical-point solver. After tracing, solved the pure-fluid conditions

$$\left(\frac{\partial P}{\partial\rho}\right)_T=0,\qquad \left(\frac{\partial^2 P}{\partial\rho^2}\right)_T=0.$$

The first derivative is the Engine's analytical pressure-density derivative; the second is its centered finite difference with density steps 10, 1 and 0.1 mol/m³. All three solves converge for each energy. Between steps 1 and 0.1, critical density changes by less than 0.000029 mol/m³, temperature by less than 2e-11 K, and pressure by less than 3e-6 Pa. Conservatively report numerical precision 0.001 K, 0.001 MPa and 0.1 mol/m³; this is numerical repeatability, not parameter or physical uncertainty. Saturation trace and derivative residuals are retained in `critical.json` and `saturation-*.json`.

Direct fixed-composition density scans use 1–30,000 mol/m³, with 50 mol/m³ spacing, bracketed pressure roots and pressure-density turning points. Root counts refer to mechanical stability, not global thermodynamic stability. Final fitted-composition scans use 1,000–23,000 mol/m³ with the same spacing.

## Pure CO₂ critical points and independent densities

| Basis | ε/k, K | Tc, K | Pc, MPa | ρc, mol/m³ |
|---|---:|---:|---:|---:|
| Current Engine record | 169.21 | 310.276799 | 8.063916 | 10023.6355 |
| Old dispersion only | 173.44025 | 318.033719 | 8.265514 | 10023.6355 |
| Real CO₂: CoolProp HEOS / Span–Wagner | — | 304.128200 | 7.377298 | 10624.9056 |

Current Tc exceeds the reference by 6.1486 K; old Tc exceeds it by 13.9055 K. Native saturation at 313.20 K is unavailable for the current pure model because it is above Tc. At the old energy, native saturation at that temperature gives 7.494939 MPa, liquid density 14024.94 and vapor density 6467.07 mol/m³, with maximum equilibrium residual 1.78e-15.

At **313.20 K**, using the requested rounded pressures:

| EOS and composition | ρ at 6.64 MPa, mol/m³ | ρ at 9.23 MPa, mol/m³ |
|---|---:|---:|
| Real pure CO₂, Span–Wagner | 4050.21 | 12176.47 |
| Engine pure CO₂, ε/k = 169.21 K | 4109.67 | 13336.76 |
| Engine pure CO₂, ε/k = 173.44025 K | 4405.46 | 16156.28 |
| Engine xwater = 0.017, k = −0.04560, ε/k = 169.21 K | 4228.42 | 15336.90 |
| Engine xwater = 0.017, k = −0.04560, ε/k = 173.44025 K | 4580.11 and 15229.82 | 17386.87 |

The two old-energy mixture densities at 6.64 MPa are mechanically stable roots; an unstable root at 11066.64 mol/m³ lies between them. Other entries have one stable pressure root in the scanned interval. At the exact Kiepe pressures 6.6438 and 9.2319 MPa, real pure-CO₂ densities are 4054.59 and 12184.79 mol/m³. Thus the supplied approximate 11,000 mol/m³ high-pressure reference is low relative to this evaluation. At 6.64 MPa real CO₂ is above Tc but below Pc; it is gas-like. At 9.23 MPa it is above both and is a dense supercritical fluid.

Current pure CO₂ has no pressure-density turning point at 313.20 K. At fixed xwater = 0.017, the current mixture has a local pressure maximum **8.014280 MPa at 8807.41 mol/m³** and minimum **7.924547 MPa at 11579.15 mol/m³**. Consequently 6.64 MPa has the low-density root and 9.23 MPa has only the dense, liquid-like root; two stable roots occur between the turning pressures. This is a subcritical-shaped mechanical isotherm, not evidence of the actual binary critical locus. The old-energy mixture has a wider loop, 6.222312–7.326526 MPa, explaining its two stable roots at 6.64 MPa.

A direct unanchored `state(P=..., phase='vapor')` can return the sole dense root. That is not equivalent to the anchored vapor-branch check used by equilibrium. The retained constant-fit errors explicitly reject dense roots relative to a negative-slope witness; the direct-state result does not establish that changing pressure initialization recovers those equilibrium trials.

## Full 39-row reciprocal-temperature fits

$$k_{ij}(T)=k_{ij}(313.15)+b\left(\frac{1}{T}-\frac{1}{313.15}\right).$$

Used native family `k_ij_reciprocal_temperature_slope`, b in K, bounds −1000 to 1000 K, scale 10 K. Base interaction uses the original scale 0.01 and bounds −0.5 to 0.5. Controls: at most 40 iterations, function/parameter tolerances 1e-10, gradient tolerance 1e-8, maximum native elapsed time 50 seconds. No phase declaration or weight changes.

| Start (k, b) | Endpoint k(313.15) | Endpoint b, K | Cost | Iterations | Failed trials | Available rows |
|---|---:|---:|---:|---:|---:|---:|
| (−0.04560, 0) | −0.0464169013241 | −35.6650526525 | 0.0264817604505401 | 4 | 0 | 39/39 |
| (−0.04690, 0) | −0.0464169011206 | −35.6650522065 | 0.0264817604505423 | 4 | 0 | 39/39 |

Both terminate by **function tolerance**, with relative last cost changes 2.58e-13 and 1.98e-13. Their projected gradient norms are 1.52e-7 and 2.15e-7; these are above the separate 1e-8 gradient tolerance, so do not describe gradient tolerance as met. Native convergence permits function tolerance termination. Both have rank two and no active bounds. Endpoint relative cost difference is 8.24e-14. Their initial costs are 1.25619165897 and 1.43852289509. The fitted cost is 97.8914% below the retained constant endpoint's 1.25588118323, which had not converged.

Errors are mean/maximum absolute relative **total-pressure** errors against the same calibration rows; these are not the solubility errors used in Pabsch's assessment.

| T, K | Rows | Constant A mean / maximum, % | Slope A mean / maximum, % | Slope B mean / maximum, % |
|---|---:|---:|---:|---:|
| 313.20 | 12 | 3.1909 / 11.3068 | 1.5012 / 2.6591 | 1.5012 / 2.6591 |
| 353.11 | 9 | 19.2082 / 24.9227 | 3.8261 / 5.5775 | 3.8261 / 5.5775 |
| 373.26 | 12 | 26.3691 / 32.8308 | 0.9726 / 2.7998 | 0.9726 / 2.7998 |
| 393.17 | 6 | 27.7912 / 41.4272 | 6.6456 / 11.3361 | 6.6456 / 11.3361 |

No rows lose the vapor branch at either start, any recorded trial, or either fitted endpoint. Endpoint effective k values at the four isotherms are −0.04639872, −0.03352830, −0.02807579 and −0.02323716. The slope lets the low-temperature rows retain their smaller interaction while correcting the hotter rows.

A separate cold replay of slope A solves every row with maximum raw equilibrium residual **1.0747e-13**, minimum returned phase pressure-density derivative **563.84 Pa/(mol/m³)**, and maximum difference from native fit predictions **5.34e-7 Pa**. In particular:

| Row | Observed P, MPa | Fitted P, MPa | CO₂-rich xwater | CO₂-rich ρ, mol/m³ |
|---|---:|---:|---:|---:|
| kiepe-313.20-12 | 6.6438 | 6.467135 | 0.00263709 | 3925.71 |
| kiepe-313.20-13 | 9.2319 | 9.000105 | 0.00843643 | 14043.38 |

Both fitted-composition isotherms have no detected turning point in 1,000–23,000 mol/m³; minimum sampled derivatives are 58.62 and 16.18 Pa/(mol/m³). Row 13 is dense but available with the original vapor declaration. Its composition is appreciably drier than the 0.017 diagnostic state. Therefore a dense phase is not categorically refused; the anchored branch geometry and solved composition matter.

## Optional old-dispersion comparison

At ε/k = 173.44025 K, the current constant endpoint −0.04560 cannot initialize the full fit: row 13 ends at local infeasibility, residual 0.0044384 after 32 equilibrium iterations. Its reported zero costs contain no fitted result. This attempt is retained separately in `constant-old-eps-first-available-copy.json`.

A second, feasible constant start **−0.05000** runs all 40 allowed iterations. It stops without convergence at **k = −0.03880739645**, cost **1.86819290794** from 5.08593838519, projected gradient **2.06796**, with 27 failed trials. All 39 rows are available at its returned endpoint. Failed trial observations are rows **kiepe-313.20-11 and -13**; messages include an absent anchored vapor branch and local infeasibility. Native failure records do not retain the trial parameter vectors, so the exact rejected k values cannot be recovered from this fit. This endpoint is not an accurately determined branch boundary.

| T, K | Old-dispersion constant mean / maximum pressure error, % |
|---|---:|
| 313.20 | 8.1158 / 18.0804 |
| 353.11 | 25.0063 / 31.4964 |
| 373.26 | 30.8034 / 37.9849 |
| 393.17 | 30.5214 / 45.1394 |

Changing dispersion shifts the critical point and feasible fit region, but restoring the old value does not cure the constant-interaction fit in this probe.

## Remedy, ownership and limits

Recommend an **owner-approved model amendment to retain the reciprocal-temperature interaction**, followed by the normal independent qualification and delivery. It has a converged all-row solution from two starts and keeps all 39 observations, the original phase declarations, weights and numerical tolerances. This is a **model-form change**, not a numerical repair; the earlier amendment authorized diagnosis only, not adoption. Its numerical evidence is the two converged fits and independent cold replay.

The bubble problem on this wheel accepts only explicit `liquid` or `vapor` kinds. Compilation rejects `None`, `fluid` and `supercritical`; `phase-kinds.json` retains the actual errors. A dense incipient phase can be declared liquid, as the earlier diagnosis demonstrated, but that changes the physical phase/root selection and requires an owner decision plus stability assessment. There is no currently supported generic fluid declaration to substitute mechanically.

Do not drop rows 12/13 on the proposed pure-CO₂ subcritical justification: current pure Tc is below 313.20 K, and the tested slope solves both with the declared vapor phase. A row-domain restriction would be an owner-approved change to the calibration population, not a numerical adjustment. The present evidence supplies no need for that exclusion. If the owner retains a constant interaction, defer the joint choice to accepted Stage 3a with CO₂ dispersion free and all Kiepe rows retained; this remains a separate model/parameter decision, and its outcome is unknown.

The cause is bounded to the tested constant-fit trajectories. These probes do not prove that no constant-interaction optimum exists. They do not calculate the binary critical locus, global tangent-plane stability, parameter uncertainty, held-out predictive performance, or full Stage 3a optimum. The 393.17 K maximum calibration error remains 11.34%; successful fitting is not a claim of absorber/stripper qualification. Full planned derivative qualification and independent delivered review were not performed by this bounded diagnosis.

## Sources actually read

- **Kiepe et al. (2002)**, [DOI 10.1021/ie020154i](https://doi.org/10.1021/ie020154i): original Zotero PDF `P9HDI8CX/WYBWWKE8`, SHA-256 `8e93b3922f4a0b5cb1001efb9b5d97e07fc5cd9b80d0c1e57a967fea21898f51`; read Experimental §2.2, Table 1 on printed p.4394, data reduction pp.4394–4395 and Results §3. Measured total-pressure/liquid-composition rows are used here. The authors' coexisting-fluid data reduction is not a justification for excluding a row solely because pure CO₂ is above its real Tc.
- **Pabsch et al. (2020)**, [DOI 10.1021/acs.jced.0c00704](https://doi.org/10.1021/acs.jced.0c00704): current Zotero `92X6B228/TBPJLBZT`; indexed Markdown and current source are byte-identical, SHA-256 `21f91300e2a7de10a295667cabe521d2b729b283a20a9b48021d04c2c710d190`; original PDF SHA-256 `9e34bcca55d6c2c473b84169914279587af8b07d0972e6c9049c46e59884a98a`. Read EOS/parameter methods, Table 2, temperature-dependent interaction discussion, binary-system data comparison, fitting and assessment in Tables 5–7. Checked Table 2 and the critical-point sentence against the actual PDF. Results, “Modeling the CO₂ Solubility in Water,” printed p.5772, reports 310.227 K and 80.69 bar, consistent in physical conclusion with this wheel's 310.2768 K and 80.6392 bar; the small numerical difference was not diagnosed. Their linear-in-temperature fitted interaction differs from the requested reciprocal-temperature form. No claim that their particular coefficients or assessment thresholds transfer to new water is made.
- **Real pure CO₂ reference:** [CoolProp CarbonDioxide documentation](https://coolprop.org/fluid_properties/fluids/CarbonDioxide.html), “Equation of State” and critical-point data, identifies Span–Wagner (1996). Densities above were computed directly with CoolProp 8.0.0 `PropsSI('Dmolar','T',313.2,'P',P,'HEOS::CO2')`; no water-mixture density was inferred from this pure reference. These are reference-EOS comparisons, not new measurements.

## Budget and retained files

Final measured probe CPU totals **73.2393 CPU-s**; longest batch **46.8188 s wall**. The failed first critical batch, two short reporting attempts for the optional initial failure, interpreter/import work and source extraction add unmetered overhead; conservatively charge **100 CPU-s**, below 400. Every numerical shell uses a 60-second outer timeout, and both fits use a native 50-second limit. No timeout or CPU allowance was extended.

`probe.py`, `critical.py`, `replay.py` and `density-composition.py` reproduce the calculations. `slope-A.json`, `slope-B.json`, `slope-replay.json`, `fitted-composition-density.json`, `critical.json`, `saturation-*.json`, `constant-old-eps*.json`, `phase-kinds.json`, `wheel-check.json` and `*-timing.json` retain returned values and diagnostics. All outputs remain under `tmp/stage2-diagnose-r2/`; no tracked edits, commits, GitHub writes, subagents or parent-thread messages were made.
