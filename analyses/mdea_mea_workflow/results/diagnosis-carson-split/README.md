# Diagnosis: start-1 liquid–liquid split for dilute loaded MDEA (Carson rows 1 and 10)

Diagnosis only (2026-10-28). Nothing was fitted. No frozen #222 choice, MEA record or manuscript file changed.
Each probe edits an in-memory copy of a retained start document.

## Case

- **States:** Carson 2000 Table 3, rows 10 (α = 0.247976) and 1 (α = 0.082434). Both are 10 wt% MDEA (59.5306 mol water per mol MDEA), at 298.15 K and 101325 Pa (the declared convention).
- **Model:** variant-A.json (sha256 c4c7b18a…) and variant-B.json (59a408b4…) at start 1. Start 4 is variant-A-start-4.json (db9d8574…). The shared MEA record is 00e77608….
- **Engine:** wheel 0d08dff9… (Engine 3e83e19c), run through the main checkout's `.venv/bin/python -I`.
- **Method:** the stage-2 path. It solves a single reactive liquid, then runs the MEA tangent-plane search, `final_evidence.py::stability` (sha256 823f7b76…), with an unchanged budget.
- **Phase compositions:** decoded from the search's `split_coordinates` (ln x per supported species, amount in mol, ln packing). For start 1, these seed a converged two-liquid solve, and the same search is then rerun on that result.
- **Command:** `nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/diagnose_carson_split.py`. It takes about 1 minute on 32 processes with one BLAS thread each.

## Files

| File | Content |
|---|---|
| `reactive-probes.json` | One record per probe × variant × row: the single liquid, search summary, best split with both phase compositions and, for start 1, the converged two-liquid check |
| `summary.csv` | One line per reactive probe |
| `binary-mdea-water.json` | Non-reactive MDEA–water stability search at the row ratio; Gibbs energy of mixing convex-hull scan over k(MDEA–water) at 298.15 and 313.15 K |
| `shared-species.json` | Frozen MEA record only: water + cation + bicarbonate, non-reactive, at the row ionic strengths and a molality scan |
| `compute.json` | Input hashes, workers, search owner |

## 1. Reproduction

The split ΔG/RT values, and the single-liquid mole fractions to the last bit, match `results/carson-phase-check.json`.
They are A: −2.78273 (row 10) and −3.09322 (row 1); B: −3.94744 (row 10) and −2.71154 (row 1).

**Converged two-liquid equilibrium** (start 1, seeded from the finite split). The search rerun on each result finds no further split.

| Case | Aqueous phase (mol) | MDEA-rich phase (mol) | MDEA-rich phase mole fractions | ΔG/RT vs single liquid |
|---|---:|---:|---|---:|
| A row 10 | 59.144 | 1.387 (2.3 %) | MDEA 0.542, MDEAH+ 0.178, HCO3− 0.178, H2O 0.102 | −7.02 |
| A row 1 | 59.294 | 1.237 | MDEA 0.742, MDEAH+ 0.0665, HCO3− 0.0665, H2O 0.125 | −6.58 |
| B row 10 | 59.140 | 1.391 | MDEA 0.541, MDEAH+ 0.178, HCO3− 0.178, H2O 0.103 | −8.48 |
| B row 1 | 59.297 | 1.234 | MDEA 0.744, MDEAH+ 0.0668, HCO3− 0.0668, H2O 0.123 | −7.03 |

In the coexisting aqueous phase, x(MDEA) ≈ 1–3 × 10⁻⁶ and x(MDEAH+), x(HCO3−) ≈ 10⁻⁵–10⁻⁷. In the model, essentially all of the MDEA and all of the absorbed CO2, as MDEAH+/HCO3− pairs, leave water for a small phase that is mostly MDEA. The finite split itself (reported in stage 2) has the same direction: in A row 10, a phase of 0.46 mol with MDEA 0.813, MDEAH+ = HCO3− = 0.094 and water 0.0003.

## 2. Unloaded MDEA–water (α = 0)

- **Reactive problem at α = 0:** unresolved. With no carbon in the feed, all nine trials collapse to pure CO2, a composition the feed cannot form ("no witness; unresolved trials 9"). This is not evidence of stability.
- **Reactive problem at α = 0.001:** split ΔG/RT = −3.087 (A) and −3.082 (B). The second phase is 99.9 % MDEA.
- **Non-reactive binary at the row ratio, k(MDEA–water) = 0:** split ΔG/RT = −3.092. Phases: x(MDEA) = 0.0083 (60.03 mol) and 0.9995 (0.50 mol).
- **Gibbs energy of mixing scan:**
  - At k = 0, the binary is immiscible from x(MDEA) ≈ 4 × 10⁻⁶ to 0.80 at 298.15 K, and from 1.3 × 10⁻⁵ to 0.765 at 313.15 K. The activity coefficient of dilute MDEA is ln γ = 12.35 at 298.15 K.
  - It first becomes fully miscible at k(MDEA–water) = −0.13, at both temperatures. The grid step is 0.01, so the threshold lies in (−0.13, −0.12].
  - At the start-2 value (−0.0899, slope −8.06 K), the binary still splits: phases x(MDEA) = 0.0084 and 0.763, ΔG/RT = −0.467.
  - At the start-4 projection (−0.1319 at 313.15 K, which is −0.115 at 298.15 K), it still splits: x(MDEA) = 0.0085 and 0.337, ΔG/RT = −0.0037.
- **Comparison with data:** Kim 2008 Table 8, a fitted #222 set, reports homogeneous MDEA–water liquids at x(MDEA) = 0.0076–0.357, 40–100 °C. With k = 0, the model places these inside its 313.15 K miscibility gap.

## 3–5. Declared starts and one-change probes

Values are the split ΔG/RT. "none" means no witness with 0 unresolved trials.

| Probe (one change from start 1 unless stated) | A row 10 | A row 1 | B row 10 | B row 1 |
|---|---:|---:|---:|---:|
| start 1 (reproduction) | −2.783 | −3.093 | −3.947 | −2.712 |
| start 2 | −0.252 | −0.392 | −0.244 | −0.388 |
| start 3 | −2.304 | −2.831 | −2.329 | −2.841 |
| start 4 (A only) | −0.394 | −0.059 | — | — |
| k(MDEA–water) = start-2 value | −1.164 | −0.362 | −1.517 | −0.428 |
| k(MDEAH+–water) = −0.2298 | −2.243 | −2.806 | −2.212 | −2.793 |
| k(MDEAH+–water) = −0.5 | −2.355 | −2.851 | −2.398 | −2.868 |
| σ(MDEAH+) = 3.563 Å (A; packing 0.88σ, Debye–Hückel σ) | −2.287 | −2.819 | — | — |
| Born diameter (MDEAH+) = 3.563 Å | −2.759 | −3.099 | −3.888 | −2.712 |
| Born diameter (MDEAH+) = 7 Å | −2.806 | −3.090 | −3.646 | −2.711 |
| u/k (MDEAH+) = 177.9 K | −3.425 | −2.750 | −3.543 | −2.690 |
| Born off (Debye–Hückel only; diagnostic) | −2.137 | −3.080 | −5.150 | −3.312 |
| Debye–Hückel off (diagnostic) | refused | refused | refused | refused |

- **Debye–Hückel off:** the Engine refuses `electrolyte = none` with charged species ("missing pair/bicarbonate-anion/carbonate-anion/k_ij"). Running it would require new ion–ion dispersion declarations, which is not a one-change probe.
- **Born off, Variant B:** the split phase is a water-free MDEAH+/CO3²⁻ salt. Without the Born term, a water-free ion phase carries no solvation penalty, so this result is not used here.

**Diagnostic k scans** below are bounded probes, not proposed values:

| Probe | A row 10 | A row 1 | B row 10 | B row 1 |
|---|---:|---:|---:|---:|
| k(MDEA–water) = −0.10 | −1.010 | −0.289 | −1.417 | −0.392 |
| k(MDEA–water) = −0.13 | −0.642 | −0.152 | −1.170 | −0.303 |
| k(MDEA–water) = −0.184 | −0.330 | −0.043 | −0.945 | −0.223 |
| k(MDEA–water) = −0.25 | −0.193 | −0.0006 | −0.821 | −0.178 |
| two changes: k(MDEA–water) = −0.10 and k(MDEAH+–water) = −0.2298 | −0.113 | −0.225 | −0.107 | −0.222 |
| two changes: k(MDEA–water) = −0.10 and k(MDEAH+–water) = −0.5 | −0.192 | −0.257 | −0.234 | −0.274 |
| two changes: k(MDEA–water) = −0.13, −0.15 or −0.184, with k(MDEAH+–water) = −0.2298 or −0.5 | none | none | none | none |

The single "none" case not clean is k(MDEA–water) = −0.15 with k(MDEAH+–water) = −0.5, A row 10, which has one unresolved trial. Values −0.12 and −0.15 for the one-change scan are in `summary.csv`.

With the binary made miscible but k(MDEAH+–water) still 0, the remaining split phase is ion-pair-rich. At k(MDEA–water) = −0.184, A row 10, it has MDEAH+ = HCO3− = 0.274, water 0.293 and MDEA 0.16.

## 6. Shared species only (frozen MEA record, non-reactive)

The checks use water + cation + HCO3− at the start-1 single-liquid ionic strength: 0.2398 mol/kg (row 10) and 0.0833 mol/kg (row 1). A scan covers 0.001–1 mol/kg.

- **Cation H3O+ (k with water +0.25):** splits at 0.24 mol/kg (ΔG/RT = −0.079), 0.3 and 1 mol/kg. It does not split at ≤ 0.1 mol/kg, including row 1's 0.083. The split phase is ion-rich: water 0.43, H3O+ = HCO3− = 0.28.
- **Cation MEAH+, the MEA record's own counter-ion (k with water −0.5):** no split anywhere from 0.001 to 1 mol/kg.

## Cause

1. **The main cause is established: k(MDEA–water) = 0 makes the MDEA–water binary itself immiscible.**
   - With the MEA record's water (u/k = 432.4 K) and the Uyan MDEA parameters, the binary has ln γ∞(MDEA) ≈ 12 and a miscibility gap from x(MDEA) ≈ 10⁻⁵ to 0.8. Real MDEA–water is miscible over the measured fitted range.
   - The split is unchanged at α → 0 (ΔG/RT −3.09 for the binary and −3.087 at α = 0.001). Its second phase is 99.9 % MDEA. Every probe that changes only MDEAH+ quantities leaves ΔG/RT between −2.1 and −3.9.
   - Making k(MDEA–water) more negative is the only one-change probe that shrinks the split by an order of magnitude. Miscibility needs k ≤ −0.13, and both the start-2 and start-4 values are above that at 298.15 K.
   - Inference, not tested: the published Uyan/Wangler model pairs this MDEA with k(MDEA–water) = −0.184 at 298.15 K (Wangler Table 6, as transcribed in `analyses/mdea_kuranov_refit/model.py`). That suggests start 1's zero lies outside the region this MDEA parameter set needs.
2. **A secondary cause appears once the binary is miscible:** k(MDEAH+–water) = 0 leaves an ion-pair-rich liquid lower in Gibbs energy.
   - The frozen bicarbonate–water value (+0.727) disfavours HCO3− in water. Without an attractive counter-cation–water interaction, MDEAH+/HCO3− pairs form their own phase.
   - The shared-species check shows the same mechanism in the MEA record alone. With H3O+ (+0.25) as the counter-ion it splits at the row-10 ionic strength; with MEAH+ (−0.5), its own counter-ion, it does not.
   - This parallels the MEA paper, where narrowing k(MEAH+–water) to [−0.5, −0.161], together with the MEAH+ σ bound, removed the detected instabilities (supplement §S9; conclusion).

## Which probes remove the split

- **No declared start** (A1–A4, B1–B3) and **no one-change probe** removes it at either row in either variant.
- **The split is removed** at all four row/variant cases when both of these hold:
  - k(MDEA–water) ≤ −0.13, tested at −0.13, −0.15 and −0.184; **and**
  - k(MDEAH+–water) ≤ −0.2298, tested at −0.2298 and −0.5.
- With k(MDEA–water) = −0.10 it persists even with k(MDEAH+–water) = −0.5.
- The k(MDEAH+–water) threshold between 0 and −0.2298 was not bracketed.

## Does the split come from the start vector or from the frozen shared record?

**It comes from the start vector**: specifically the zero MDEA-specific interactions at start 1 (and, more weakly, at starts 2–4). Every frozen shared value stays inside a vector that removes the split.

The shared record is **conditionally** stable:
- It is stable with its own counter-ion (MEAH+, k = −0.5) up to 1 mol/kg.
- It is unstable at ≥ 0.24 mol/kg when the counter-cation has a repulsive water interaction (H3O+, +0.25).
- An MDEA fit therefore inherits a requirement that k(MDEAH+–water) be sufficiently negative. This requirement comes from the frozen bicarbonate–water value.

## Limits

- **Search scope:** the finite trial-set search is not a global-stability certificate.
- **Scan resolution:** the k grid steps are 0.01 (binary) and the listed values (loaded), so thresholds are bracketed, not located.
- **States covered:** only 298.15 K and 101325 Pa at 10 wt% were searched for the loaded system, plus 313.15 K for the binary.
- **No physical claim:** none of these values is proposed or fitted. They are numerical properties of the model at the stated vectors and make no claim of experimental phase behaviour.
