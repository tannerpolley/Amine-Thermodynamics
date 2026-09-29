# Model D (#121): checks N1 and N2, stopped before any binary fit

Design: MEA-Thermodynamics #121 (owner decisions 1–13). Base: the packet v5 record
`../calibration-misfit/pre-refit-packet-v5-parameters.json` (`562b5976…`) on Engine wheel `f66d972c…`
(commit `1303c119`), read through `shared_evaluation.parameter_mapping`, as refit C and C_src were.

**Outcome: the work stopped at N1, before B1, B2 or any ternary fit.** #121 routes the N1 result to the
owner, and no parameter was fitted.

## N1: NaCl counter-ions (`n1-nacl.csv`)

NaCl osmotic coefficient at 298.15 K and 0.101325 MPa, against Hamer & Wu 1972 Table 16 at 0.1–5 mol/kg (21 rows).
Na⁺ and Cl⁻ come from Held 2014 Tables 2–3 in Held's convention: packing 0.88σ, Debye–Hückel and Born σ.

| Born form of the electrolyte family | NaCl φ ARD (limit 3.5 %) | max \|φ(Born) − φ(no Born)\| (limit 1e-10) |
|---|---:|---:|
| as loaded, c_shell = c_dielectric = 1 (the form refit C and C_src used) | **25.42 %** | **0.720** at 5 mol/kg |
| c_shell = c_dielectric = 0 (the form #121's model section states; diagnostic) | 1.242 % | 4.9e-13 |
| Born off (Debye–Hückel only) | 1.242 % | — |

- **Finding.** #121 states the base uses "original Born, with c_shell = c_dielectric = 0". The record omits
  both coefficients, and `shared_evaluation.MODEL_RUNTIME_DEFAULTS` fills (1, 1). This matches the Engine's own
  resolution rule for documents without them: water declares f_solv = 1.5 (Engine `docs/science/full-eos.md` §7).
- **Why E3 fails for (1, 1).** In the Engine's Born term (`born.hpp`), the outer-shell diameter
  D_i = d_i^Born[1 + c_shell(f_mix − 1)/|z_i|] uses f_mix = Σ x_k f_k / Σ x_k over every component with
  f_k > 0, ions included (f = 1). D_i therefore changes with the salt fraction, so the Born energy is not linear
  in the ion amounts. It then contributes to ln a_w: φ falls from 0.940 to 0.768 at 1 mol/kg.
- **Outcome under #121.** The N1 Born invariant is a shared step (outcome 1), and the 25.4 % ARD is a
  counter-ion agreement failure (outcome 2). Both stop all work and go to the owner.
- **Locator defect.** #121 names Engine packet `hamer-wu-1972-aqueous-alkali-halides/1` for the φ values, but
  that packet holds only γ±. `hamer-wu-1972-nacl-osmotic.csv` carries Hamer & Wu Table 16's φ and γ± columns
  from the reading copy `literature/Hamer1972--VYE43TLN.md`.
  - All 21 γ± values equal the packet's NaCl rows.
  - All 21 φ values are reproduced by Hamer & Wu Eq. (3.11) with the printed NaCl constants
    (B* = 1.4495, β = 2.0442e-2, C = 5.7927e-3, D = −2.8860e-4, A = 0.5108) within 5e-4, the printed rounding.
  - The Zotero PDF is not in local storage.

## N2: the E4 transformation (`n2-nacl.csv`; base record as loaded, NaCl)

| Check | Limit | Result |
|---|---|---|
| (i) ln a_w: `Reference.activity` vs ln φ_w^V,pure − ln φ_w^L,pure at p_b | 1e-8 | 1.2e-9, 8.2e-11, 1.4e-10; **2.25e-8 at 298.15 K, 1 mol/kg** |
| (ii) \|ln a_w(p_b) − ln a_w(0.101325 MPa)\| | 1e-5 | ≤ 6.6e-7 (estimate: 7e-7 at 1 and 4e-6 at 3 mol/kg) |
| (iii) Approximation B correction terms at the NaCl p_b | report | 5.9e-5 to 1.37e-4 per mol/kg (estimate: 5e-5 to 1.6e-4) |
| (iii) gate: \|B_w,model − B_ref\| ≤ 0.3·\|B_ref − v_w^L\| | ratio ≤ 0.3 | **0.746, 0.491, 0.346** at 298.15, 318.15, 333.15 K |
| (iv) `pressure` Jacobian in k(Cl⁻–water) and its 1/T slope vs central differences, 318.15 K | 1e-5 relative | ≤ 6.8e-8; solve residuals 3.8e-15 and 2.8e-14 |

- **(i) diagnosis.** ln a_w from the mixture's own fugacity coefficient on polished liquid roots equals the E4
  identity within 9.5e-10 at every state (`identity_minus_mixture_fugacity`). The 2.25e-8 difference is in the
  `Reference.activity` value.
  - The Engine's liquid root at a few kPa meets its density criterion (DENSITY_ROOT_RESIDUAL 1e-12), yet leaves
    P(ρ) about 1.1e-8 (relative) off the requested pressure, which moves ln φ_L by about 1.1e-8.
  - `binary.polished_state` polishes the density by Newton steps on P(ρ). The pure-water ln φ difference then
    varies by about 1e-9, against 2e-8 unpolished.
  - #121 uses `Reference.activity` only in checks, but it names (i) a stop condition.
- **(iii) B_w.** The model's water B_w is −2.180, −1.344 and −0.980 L/mol at 298.15, 318.15 and 333.15 K, from
  RT ln φ_w^V/p at 1 Pa; the values at 10 and 100 Pa agree within 3.1e-5 relative. IAPWS G11-15 Eq. (5) gives
  −1.241, −0.895 and −0.723 L/mol.
  - It reproduces the guideline's Table 7 at 200, 300 and 400 K within 7e-10.
  - Document SHA-256 `00fbe4df…dec8f`, as decision 10 records.
  - v_w^L uses standard liquid densities 997.05, 990.21 and 983.20 kg/m³.
  - Under #121, an N2(iii) failure stops Route B and goes to the owner.
- **The Engine accepts the ionic bubble point** (the capability #121 lists as not established) when the
  document holds only the solution's species. A record with absent species (zero feed) is refused as
  "rank-deficient declared equations", even for pure water, so `binary.document` reduces the record to water
  and one salt.

## Files and commands

- `binary.py`: the reduced salt–water document (base record + Held Na⁺/Cl⁻), E2 compositions, the E4 identity
  and target pressure, `Reference.activity`, and the bubble point with the vapor limited to water.
- `checks.py`: N1 and N2, writing `n1-nacl.csv` and `n2-nacl.csv`.

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python checks.py n1
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python checks.py n2
```

The pinned wheel must be installed; `probe.py` checks it. The IAPWS document is fetched to the ignored
`../results/runs/model-d/` only to read it; Eq. (5) is transcribed in `checks.b_ww_iapws`.
