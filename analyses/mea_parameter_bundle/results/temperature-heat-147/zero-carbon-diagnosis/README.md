# #147: exactly CO₂-free initial endpoint diagnosis

## Result and scope

The pinned wheel does **not expose an admitted exact-zero-carbon representation for this endpoint with all five reaction declarations unchanged**. The reported failure reproduces exactly. Full diagnostics establish why the returned residual is large: hydronium remains near the optimizer's composition box, while the coupled Newton correction leaves the permitted positive-composition chart at the zero-carbon boundary.

All six positive-carbon endpoints converge by the Engine's amount-weighted criterion. Their extensive enthalpies approach a smooth limit. However, every native finite-addition observation then fails independently at the pure-CO₂ feed: its density converges, but its Born contribution and residual enthalpy are NaN. An ε amendment alone therefore cannot make the current native observation usable.

These are bounded diagnosis results, not resumed §8 qualification, physical validation, a fit, parameter adoption, or permission to use ε in the study. Independent review remains pending. No Engine or study code, tolerance, reaction law, physical parameter, source target, or phase topology was changed.

## Inputs and reproduction

- One reacting liquid, 313.15 K, 1,734,000 Pa; initial feed MEA 1 mol, water 7.911062165006594 mol, added-carbon amount exactly 0 mol. The loaded comparison endpoint has 0.11 mol added CO₂.
- Physical parameters: `../../temperature-reanchor-140/restored-source-parameters.json`, SHA-256 `7e9e3f02723700f8b6577681173249c0e7bd2c8c2a098f38a4e0a7e4611852d5`. The five declarations are the unchanged `../campaign-reactions.json`; R2/R4/R5 laws and physical calorics remain frozen.
- Engine source `717a2990e443423e051fc0569f25209d04007543`; wheel SHA-256 `9e6a76cf59d4e2fef3347d895bf3a966ecced01f13dc6e0caec74c3c3d618dc4`. Engine source was inspected only in `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-build-717a2990`.
- Every numeric subprocess used `timeout -k 5s 175s`, uv's isolated non-editable wheel environment, and OMP/OpenBLAS/MKL threads = 1. Eight independent ladder/final/support probes ran concurrently within the 12-CPU affinity. Summed measured probe elapsed times, including trace serialization and feed comparisons, are 13.508 s; these are not whole-process startup times.
- Disposable producers remain ignored in `../../runs/temperature-heat-147/diagnose/`; exact hashes are in `results.json`. From the worktree root, the endpoint command was `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout -k 5s 175s uv run --no-project --python analyses/mea_parameter_bundle/results/runs/temperature-heat-147/.venv/bin/python analyses/mea_parameter_bundle/results/runs/temperature-heat-147/diagnose/probe.py <alpha>`.
- Returned rows, amounts, compositions, convergence records and unavailable native heat values are retained in `results.json`; full zero-carbon and changed-initial-guess traces are retained separately. Installed-wheel verification still matches all 14 RECORD hashes; installation metadata was not rewritten.

## Cause: carbon conservation and the positive chart

For the declared species order, the conserved added-carbon vector is `(1,0,0,0,1,1,1,0,0)`. It annihilates every reaction row. Nonnegative amounts therefore require

$$n_{CO_2}+n_{MEACOO^-}+n_{HCO_3^-}+n_{CO_3^{2-}}=0$$

at the exactly unloaded endpoint: all four amounts must be structurally zero, not merely small.

The compiler admits the feed but retains all nine reaction participants: `removed_species=[]`, balance rank 4, primal size 11, generic Jacobian rank 15. Those generic counts do not establish boundary regularity. `request_compile.cpp:891–931` removes a zero-feed species only if it is not a reaction participant; `:1098–1101` requires every supported exponential composition coordinate to be strictly positive. An explicit liquid support omitting the four carbon-containing species is rejected with **`ParameterError: species 0 has no support`**, with the five declarations preserved.

The reproduced default solve has Ipopt `SUCCESS`, but native `success=false`, no accepted state, 28 iterations/43 evaluations, classified residual **1.1966663563277393e-7**, requested criterion **1e-10**, and returned floor estimate **1.764126414087811e-10**. It matches the earlier retained residual bit-for-bit and uses exactly the same initial feed.

- Dominant **classified** row: hydronium stationarity. Its raw residual is **11.966574858838811**; its amount weight, reconstructed as classified/raw using the exact Engine classification, is **1.0000074126840494e-8**. That is near the `1e-8` composition box, not the neighboring solved hydronium fraction of about `6.35e-14`.
- Largest **raw** row: CO₂ stationarity, **14.982388473576336**, but its classified residual is only **5.847660814838519e-13**. Material-balance maximum is **7.728918795409451e-13** and normalization is **7.72937269744034e-13**. Carbon/material imbalance is not the dominant returned defect.
- The first full Newton step reduces raw maximum `14.9824 → 6.49360e-5`, while classified maximum rises to `1.36387e-7`. The next full step reduces raw maximum further to **7.88117e-9** and classified maximum to **2.11256e-11**, but is rejected. Both half and quarter steps also reduce the raw maximum and are rejected.
- This rejection mechanism is determined from the trace and `gibbs_minimizer.cpp:757–781`: after a recorded raw contraction, the remaining rejection condition is a nonzero composition below `STABILITY_COMPOSITION_FLOOR=1e-20`. The trace does not report which individual species coordinate crosses it. The driver consequently restores the best classified point visited, the optimizer point with unresolved hydronium.

A documented `composition_guess` control was also tested: noncarbon fractions from the `1e-8` neighbor, with all four carbon guess entries set exactly zero and the **feed still exactly zero-carbon**. It stalls at **1.5534812489122854e-8** (27 iterations/35 evaluations), without an accepted state. A better initial guess is not an exact boundary representation.

The floor estimate alone is not a demonstrated precision limit: positive-carbon neighbors attain classified residuals much smaller than it. Neither increasing iteration counts nor weakening the requested criterion was tested or justified.

### Absent species, phase pins, and manufactured checks

`Phase.amount=Free/Pinned` specifies an entire phase amount fraction, not individual species amounts. `Pinned(0)` is an incipient phase with intensive composition, not four absent species in a nonzero liquid. At fixed T/P a pinned phase requires a free intensive (`request_compile.cpp:939–950`); introducing such a phase would change the required specification. `FreeValue.absent` means an absent variable guess (`problem.hpp:47–63`), not absent species. `Reaction` exposes no inactive-reaction declaration.

Engine #210 requires identical endpoint reaction declarations and componentwise addition admission at `1e-12`; it explicitly excludes endpoint declarations with different reaction sets. Its manufactured Case N has feeds `(2,0.2)` and `(2+n_add,0.2)`, with positive conserved inventory and neutral species; Case I starts from `(1,1e-6,1e-6)`. The zero vapor amount in the bubble variant is a phase pin, not a zero conserved reacting component. Read: #210 F1–F8/O4/limits, `regression_checks.cpp:1751–1874,1906–1948`, `test_reference_calorics.py:246–290`, and retained `analyses/2026-addition-enthalpy-fitting/results/summary.json`. Existing manufactured evidence was not rerun or generalized to this boundary. Engine #211's direct source ln K observations do not solve equilibrium and provide no boundary support.

## ε ladder and enthalpy trend

All amounts are on the 1 mol MEA basis. Extensive H uses the unchanged neutral anchors. The final endpoint has **H(0.11) = −2364483.718759536 J**, classified maximum `3.69447e-15`, raw maximum `7.10543e-14`.

| ε, mol CO₂/mol MEA | Classified maximum | Raw maximum | H(ε), J | Independently assembled Δh(ε→0.11), kJ/mol CO₂ |
|---:|---:|---:|---:|---:|
| 1e-3 | 5.045e-14 | 7.105e-14 | −2314160.295303 | −68.108335 |
| 1e-4 | 3.135e-14 | 9.038e-12 | −2313738.859237 | −68.162216 |
| 1e-5 | 4.739e-11 | 2.018e-8 | −2313696.590614 | −68.168692 |
| 1e-6 | 7.738e-12 | 3.317e-9 | −2313692.362278 | −68.169353 |
| 1e-7 | 7.662e-13 | 3.335e-10 | −2313691.939425 | −68.169419 |
| 1e-8 | 5.495e-14 | 3.456e-11 | −2313691.897139 | −68.169425 |

All six native endpoint solves report convergence and meet their unchanged amount-weighted criterion. However, the raw maxima at `1e-5`, `1e-6`, and `1e-7` exceed #147 §8's `1e-10` maximum-stationarity requirement. This table does not qualify those endpoints for the study. There is no endpoint failure among the requested positive ε values; the tested failure is at exactly zero. No smaller positive ε was probed.

**Every native `addition_enthalpy` value is null**, with `feed:nonfinite: the predicted value is not finite`. The last table column instead uses accepted standalone Engine endpoint H values and the separate documented pure-support feed property:

$$\Delta h_\epsilon=\frac{H(0.11)-H(\epsilon)}{0.11-\epsilon}-h_{feed}.$$

This arithmetic is diagnosis-only and is not a replacement implementation of the study observation.

## Second cause: pure-CO₂ Born evaluation

The nine-species pure-CO₂ feed has exactly one stable density root, **723.5928742984386 mol/m³**, zero density residual, and positive pressure-density derivative **2196.5242889643346**. It is not a root failure. The returned bulk permittivity is 0; Born, residual Helmholtz energy, and residual enthalpy are NaN.

At zero ion inventory and zero dielectric-solvent mass, `electrolyte.hpp:239–241` returns zero bulk permittivity. `born.hpp:47–76` still evaluates each declared charged term as its zero fraction times an expression containing `1/bulk_permittivity`, producing an undefined `0 × infinity`. This identifies the observed NaN without modifying the equations or dielectric parameters.

Using `Parameters.from_mapping(..., components=...)` to select either the three unchanged neutral records or only CO₂ gives **the identical density and hard-chain/dispersion values**, Born = 0, finite residual enthalpy **−623.740071356366 J/mol**, and total feed enthalpy **−393574.4494137983 J/mol**. The two selections agree exactly. Full-mixture state thermochemistry also reports missing ion records; the native observation already restricts its ideal thermal record to feed support, so that is not its missing-record failure. Its NaN EOS residual remains.

## Remaining decisions and recommendation

1. **Existing exact declaration:** none found under the specified one-liquid, fixed-T/P, unchanged-reaction inputs. Zero-carbon support removal is rejected; phase pins mean a different specification; the documented initial-guess probe still fails. Deleting carbon reactions or declaring artificial carbon is not an exact representation.
2. **Explicit ε-limit amendment:** numerically plausible at this one condition, but not authorized adoption. Two-point extrapolation of the two smallest neighbors gives **H(0) ≈ −2313691.892440736 J** and **Δh(0→0.11) ≈ −68.169426211656 kJ/mol**. The `1e-8` estimate differs by **0.000735875 J/mol = 7.35875e-7 kJ/mol**, or **2.453e-7** of the smallest frozen 3000 J/mol source scale. At `1e-3` the difference is 61.092 J/mol. Successive extrapolated heat limits differ by about `1.44e-6 J/mol` for the last two pairs. These are observed trend estimates, not rigorous error bounds or an exact-zero solved heat. Intermediate raw stationarity failures remain disclosed. Source scales are Vinjarapu Table 4 rows 1–8 (3–6 kJ/mol), not assumed known 1σ values. Source §1.1.1 defines the integral measurement from a zero-loading solvent, so ε would be an explicit numerical-limit amendment, not a reinterpretation of the measured initial loading. Current Zotero PDF `CE8AP5BM` was rechecked read-only: SHA-256 `fcb05a98b686aa981b4253868fc6b9e5d110bfd61cf3fec419e58356ad776186`; its text matches the earlier phase-A reading. The worktree has no literature shelf; the confirmed PDF was used directly.
3. **Specific upstream changes, recommended:** compile zero attainable conserved inventories onto their exact nonnegative support face, removing absent species from the solved chart and deriving the active reaction span from the conserved balances restricted to that face **while preserving the complete declared reaction/reference set for identity and caloric completion**. Do not form partial reactions by simply deleting zero-species stoichiometric columns. For this endpoint the surviving reaction span is R1/R5; R2/R3/R4 require absent carbon species. Qualify central H and fixed-support parameter actions, exact component zeros, charge/material balance, anchor cancellation, and finite-addition assembly. Separately make the feed EOS/thermal evaluation respect exact feed support (or establish a zero-ion value/thermal branch that never evaluates absent Born terms). A finite neutral feed value does not imply that inserting ions or changing support has a differentiable action.

Prefer the exact support-face and feed correction, followed by a newly authorized source pin and wheel qualification. If the investigator instead chooses an ε-limit study amendment, the displayed ladder supports a small numerical perturbation at this particular condition, but feed handling and all remaining §8/§6.1 checks still need approval and qualification. No upstream issue, patch, wheel change, study amendment, commit, push, or publication was performed here. The earlier phase-B stop and source freeze remain unchanged; persistent executable additions remain 331/450 lines.
