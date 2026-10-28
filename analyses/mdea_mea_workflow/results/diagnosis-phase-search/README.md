# Diagnosis of the stage-2 phase-search results (issue 222)

Diagnosis only. Nothing was fitted or adopted, no frozen choice changed, and the MEA record and manuscript are untouched. Engine 3e83e19c, wheel SHA-256 0d08dff9…6804 (`runtime.json`). The notebook owns interpretation; this file indexes the evidence.

## Results

1. **No stage-2 "liquid witness" is a liquid–liquid split.** All 552 liquid-witness records in the 18 retained or reproduced searches (A1, B1, both sensitivity refits, all 12 narrowed steps) come from the near-pure-CO2 seed of the liquid trial. In every one:
   - the new phase has packing fraction ≤ 0.025 (the present liquid is about 0.43);
   - an identical vapor-trial descent exists, agreeing to within 1.8e-12 in ΔG/RT (`unresolved/summary.json` → `liquid_witnesses`).

   Converged at the Merkley states, the second "liquid" has the following properties (`splits/compositions.csv`):
   - CO2 mole fraction 0.84–0.98 and water 0.016–0.156;
   - MDEA ≤ 1.4e-4 and ions ≤ 4e-20;
   - molar density 358–423 mol/m³, close to the ideal-gas value P/RT;
   - phase fraction 0.2–1.0 mol%.

   A liquid–vapor solve with the vapor on the neutral species gives the same phase, to within 9.4e-15 in mole fraction. The fixed-pressure liquid is therefore supersaturated: the model evolves CO2 gas. The confirmed MEA splits, by contrast, are two dense liquids (22.6–51.6 kmol/m³, CO2 ≤ 0.017 in the new phase).
2. **Cause of the Merkley descents.** At Merkley's loading point, the model bubble pressure exceeds the declared 1121 kPa:

   | Vector | 333.15 K, 40 wt% | 388.71 K, 20 wt% | 388.71 K, 40 wt% | 333.15 K, 20 wt% (no descent) |
   |---|---:|---:|---:|---:|
   | A1 | 1450 kPa | 1798 kPa | 1625 kPa | 1100 kPa |
   | B1 | 1336 kPa | 1795 kPa | 1827 kPa | 1051 kPa |

   The model saturation loading at 1121 kPa lies below α_LP: 0.900 against 0.941 (A1, 333.15 K/40 wt%), and 0.456 against 0.587 and 0.288 against 0.360 at 388.71 K. The Jakobsen row 8 trace is the same effect at 1 atm: bubble pressure 102 kPa, α_sat 0.7886 against 0.790.

   Across 210 baseline, pressure, loading and probe cells without a dense split, a gas-density descent occurs exactly when the model bubble pressure exceeds the declared pressure (210 of 210, `summary.json`).
3. **The unresolved trials have two numerical causes. Neither is an iteration or recovery limit.** The largest trial iteration count is 53, below the fixed limit of 200; no message names the recovery budget.
   - **Carbon-free reference states (68 records per 754-record search, identical in every vector).**
     - *Where:* zero-loading initial states of the heat observations, and the α = 0 Cp, density and Kuranov rows.
     - *What fails:* every trial reports `negative_plane_without_positive_donor`. The tangent plane is built from balance multipliers (`plane_over_rt = Bᵀλ`). With no carbon in the feed, the carbon multiplier is not determined; it equals +211 at Kuranov 393 K. Carbon trials therefore show spurious negative distances (−279), and no present phase can donate carbon.
     - *Admitted resolution:* declaring carbon-free trial supports (liquid: water, MDEA, MDEAH+, H3O+, OH−; vapor: water, MDEA) resolves all 68 per vector, with 0 unresolved trials (`unresolved/repair.json`).
   - **Charge reconstruction (22–48 records per search, scattered).**
     - *What fails:* only the near-pure-CO2 seed of the full-support liquid trial, which ends with `converged …; reconstruction destroys support`. The Engine's two-pivot correction (`phase_stability.cpp:390-405`) adds the normalization residual to the largest cation and anion. Here the charge-balanced ion fractions are at most 1.7e-19, while |Σx − 1| reaches 2.2e-16, so a positive rounding residual drives them negative. A float64 replay reproduces 595 of 595 failures.
     - *Where:* the states differ between vectors, because the outcome depends on the rounding sign. 343 states fail in at least one search and none fails in all of them, at about 5% in every temperature bin from 293 to 395 K, at loadings 0.03–1.29, and at both fixed and bubble pressures.
     - *Within admitted controls:* adding an ion-free liquid face (CO2, water, MDEA) reaches the same stationary point. It shows descents only where the vapor trial already did (A1 Böttinger 5 bar, α = 1.285; B1 Merkley 333.15 K/40 wt%). The failed full-support trial still counts as unresolved, and no seed selector or limit override exists (`../item-l/A4-retry-capability.json`).
   - **One further non-result:** B narrowed step 3, corrected-Kamps row 13 (`state not searched: ParameterError: stability test requires this model's accepted declared result`).
4. **One-change probes at the witnesses** (`probes/table.csv`):
   - **k(MDEA–water) c₁ = 0** removes every Merkley descent for both vectors, with bubble pressures 412–923 kPa.
   - **B1, k(MDEAH+–HCO3−) from +1 to 0** removes them all; at −0.5 and −1 it creates dense splits.
   - **A1, k(MDEAH+–HCO3−)** moved away from −1 raises the bubble pressure and deepens the descents.
   - **Born diameter** over 3–7 Å changes the bubble pressure by up to about 50% (largest at 333.15 K/40 wt%) and never removes the 388.71 K gas descents.
   - **k(MDEAH+–water)** behaves differently in the two vectors:
     - *A1:* any value from −0.25 to +0.25 creates genuine dense liquid–liquid splits (packing fraction 0.40–0.46, e.g. an ion-rich second liquid with water 0.51, MDEAH+ 0.24 and HCO3− 0.24).
     - *B1:* moving it to −0.25 or −0.5 raises the bubble pressure to 5–17 MPa; 0 lowers it to 0.05–1.4 MPa; +0.25 creates dense splits.
   - **Born off** gives dense splits at all five states for both vectors.
   - **Debye–Hückel off** is refused by the Engine for a model with ions: `ParameterError: invalid ionic_dispersion` (`helmholtz_model.cpp:887`); without the same-sign ion pairs, `missing pair/bicarbonate-anion/carbonate-anion/k_ij`.

Claim limits: numerical verification against the declared model. These results say nothing about whether MDEA solutions physically split. The Merkley loading points are digitized to ±0.02 mol/mol; the 333.15 K excess of 0.024–0.041 lies within about two such uncertainties, the 388.71 K excess of 0.07–0.13 does not.

## Files

- `reproduce/{A1,B1}/` — full stage-2 search (fitted, comparison and saturation states) at the A1 and B1 endpoints, by the stage-2 runner with 16 processes. The 324 fitted-state records reproduce the retained stage-2 classes and ΔG/RT exactly.
- `unresolved/` — classification of every record in the 18 searches:
  - `records.*` — per state;
  - `trials.json.gz` — per unresolved trial, with native messages and the reconstruction replay;
  - `liquid-witnesses.*` — new-phase density, composition and matching vapor descent;
  - `repair.json` — searches with the admitted trial supports.
- `splits/` — two-liquid solves as in stage 2, plus liquid–vapor solves, with all eight species, phase fractions and molar densities.
- `probes/` — one-change probes; the pressure (156–5000 kPa) and loading (0.25–1.1 α_LP) grid; model saturation loading at the declared pressure.
- `summary.json` — every count quoted above.

Files larger than 5 MB are stored as level-9 gzip and registered in `../compressed-evidence.json`.

## Reproduce

Run from the worktree root, in order:

```bash
PY="nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/diagnose_phase_search.py"
for op in reproduce classify repair splits probes summarize; do $PY $op; done
```

Process pool: at most 16 workers, with one BLAS thread each. Wall time is about 3 minutes.
