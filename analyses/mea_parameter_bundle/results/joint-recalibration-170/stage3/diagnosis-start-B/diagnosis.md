# B row 13: an existing vapor root missed by the cold solve

The unchanged B parameter set has an aqueous-liquid/CO₂-rich-vapor coexistence root for `kiepe-313.20-13`. The Engine reaches it by warming the original row-13 problem from the adjacent, already available B row 12. It converges in four iterations at **5.503809502954197 MPa**, with phase densities **54014.522623831755 / 3100.2957005057815 mol/m³** and maximum raw residual **4.3520742565306136×10⁻¹⁴**. Thus the original unavailable observation is a cold-start numerical failure, not evidence that its declared vapor branch is physically absent.

The parent authorized only a bounded diagnosis after the stopped stage-3 delivery, with 60 CPU-s / 60 s wall, unchanged B parameters, rows, bounds and tolerances, and no fits. This report returns that classification. No replacement calibration start or campaign amendment was selected; no fit ran from A alone or from either start.

## Pure CO₂ comparison

All calculations use the qualified Engine wheel `a974c0e0…`, the exact committed B starting record and the same source row. `inputs.json` verifies the wheel bytes and input hashes and records the B parameter-file hash. CO₂ dispersion is 173.44025 K. The pure calculation selects only CO₂ from that same full parameter document.

| Quantity | New-wheel result |
|---|---:|
| Critical temperature | 318.033719231655 K |
| Critical pressure | 8.265513906689 MPa |
| Critical molar density | 10023.6355 mol/m³ |
| Saturation pressure at 313.20 K | 7.494939038247918 MPa |
| Saturated liquid / vapor density at 313.20 K | 14024.9438285 / 6467.0652249 mol/m³ |
| Maximum raw saturation residual | 2.6645352591×10⁻¹⁵ |
| Row-13 observed pressure | 9.2319 MPa |
| Pure-CO₂ liquid density at the observed pressure | 16157.6318467 mol/m³ |

The observed pressure exceeds this model's pure saturation pressure by **1.736960961752 MPa**, or **23.17511794%**. Pure CO₂ at that temperature and pressure is on the compressed-liquid branch of this model. Its pressure-density derivative is positive, 1403.1079709 Pa/(mol/m³).

That pure-fluid comparison does **not** determine the binary bubble phase or its predicted pressure. In the declared binary problem, temperature and aqueous liquid composition are fixed and pressure is solved freely. The observed 9.2319 MPa is also the original pressure guess, not an imposed coexistence pressure. B's recovered binary pressure is below pure saturation, at 5.50381 MPa; its accepted CO₂-rich vapor root has density 3100.30 mol/m³. Assigning that root the pure-fluid compressed-liquid classification from the observed pressure would combine two different states.

The critical calculation repeats the retained stage-2 method: solve zero first and second pressure-density derivatives, using the Engine's first derivative and centered density differences of 1 and 0.1 mol/m³ for the second. The two critical temperatures differ by less than 3×10⁻¹⁴ K and densities by 2.76×10⁻⁵ mol/m³. This supports the previous 318.03 K numerical result; it supplies no physical parameter uncertainty. `pure-critical.json` and `pure-saturation.json` retain the returned values.

## Same binary case, different initial numerical state

The aqueous feed remains CO₂/water 0.02481/0.97519 on the original one-mole basis. The original phases remain liquid `L`, vapor `V`, with zero incipient vapor inventory. The equilibrium row tolerance remains 10⁻¹⁰. The diagnostic warm solve passes the converged Engine result for B row 12 as `start=` to the original B row-13 problem. No row-13 parameter, feed, phase declaration, bound, tolerance or observation changes.

| Call | Returned pressure, MPa | Aqueous / CO₂-rich density, mol/m³ | Result |
|---|---:|---:|---|
| Original B row 13, cold | Unavailable | Unavailable | Local infeasibility; residual 0.0050988359807841097 after 31 iterations |
| B row 12, original vapor declaration | 4.544316729321262 | 54165.9402057 / 2320.6141272 | Converged |
| Original B row 13, warm from row 12 | 5.503809502954197 | 54014.5226238 / 3100.2957005 | Converged in 4 iterations |

The recovered vapor composition is CO₂/water **0.9973605954604049 / 0.002639404539595121**. The aqueous composition remains exactly the declared feed. Both returned phase pressure-density derivatives are positive: **102386.69137406675 / 1079.2500574127416 Pa/(mol/m³)**. The returned reduced-Hessian minimum is zero. Direct EOS pressure checks differ from the common solved pressure by **−3.3053×10⁻⁶ / +2.7940×10⁻⁹ Pa**. The CO₂-rich packing fraction is 0.0408183707102, compared with 0.4622629811900 for the aqueous phase. These are distinct phases, not a coalesced or identical-phase solution.

The recovered pressure underpredicts the observation by **40.3827001706%**. Availability is therefore established for this diagnostic solve; good calibration agreement is not. The original campaign's cold failure remains preserved and is not replaced by this value. No complete B family score, B objective or fitted endpoint was generated.

Dense-phase diagnostic declarations did not converge at the original pressure guess, or at 15, 30 and 50 MPa initial pressure guesses. These were changes to diagnostic numerical initialization and incipient-phase root selection only, never changes to calibration parameter starts or retained source rows. At 30 MPa initialization, the Engine specifically rejects the liquid declaration because its sole stable root, 3100.2957005 mol/m³, lies below a negative-slope sample at 11035.1979477 mol/m³. That is consistent with the independently recovered vapor root. The failed dense attempts do not prove the absence of every other coexistence state. Their complete messages remain in `coexistence-calls.json` and `dense-initialization-calls.json`.

## Comparison with retained stage-2 diagnoses

The [first stage-2 diagnosis](../../stage2/diagnoses/r1-kiepe-start/diagnosis.md) demonstrated a different failure: at dispersion 169.21 K, constant interaction −0.02424240226792941 and row-10 aqueous CO₂ fraction 0.01639, a dense coexistence root existed at 24.19308948 MPa with densities 54562.32 / 20147.93 mol/m³. Passing that identical dense solution back with the vapor declaration was rejected as an absent anchored vapor branch. Those parameters and that row differ from B row 13 here.

The [second stage-2 diagnosis](../../stage2/diagnoses/r2-co2-critical-and-slope/diagnosis.md) retained the same pure-CO₂ critical and saturation results at dispersion 173.44025 K. Its old-dispersion constant-interaction row-13 cold failure did not establish that every root at the present B parameters was absent. On the selected stage-2 slope record at dispersion 169.21 K, row 13 instead solved at about 9.000105 MPa with CO₂-rich density 14043.38 mol/m³ under the original vapor declaration. A dense returned phase and an unavailable declared branch are therefore different numerical observations.

Here an Engine warm solve directly reaches a locally admissible vapor root with the exact B equations. This falsifies the proposed physical-branch-absence explanation for this case. The cold pressure guess lies above the pure saturation pressure and the recovered root lies below it, which is consistent with initialization crossing a density-root region. The cold solver's complete internal trajectory is unavailable, so its precise path is not inferred from the termination message.

## Evidence, limits and timing

This is numerical verification of local coexistence and a bounded diagnosis of initialization. It is not a global phase-stability search, a mixture critical-locus calculation, proof of root uniqueness, physical validation or a completed calibration. No new external literature claim was needed; the source-row and physical-model definitions remain those of the accepted design. The findings use the existing Engine equilibrium and EOS owners; no local equilibrium optimizer or EOS equation was added.

The three sequential batches used **5.581665704 CPU-s / 5.768992230 wall-s** in total, including their measured import/setup work, within the parent's 60/60 allowance. Each ran at `nice -n 10` with single-threaded libraries and an outer timeout; no process was interrupted. Per-call and per-batch times are retained. The scripts are retained as inert `.py.txt` files for reproducibility and their 114 lines are separately charged in the conservative code accounting. No further numerical work follows this classification.
