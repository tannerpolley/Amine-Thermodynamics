# Bülow 2021 MDEA preparation

Preparation for [issue 223](https://github.com/tannerpolley/Amine-Thermodynamics/issues/223),
§7 steps 1–5, is complete for review on Engine `3e83e19c`. These are numerical
verification results for declared inputs. They provide no pressure reproduction,
experimental validation, parameter adoption, or process-use evidence.

The clean task worktree was created from `main` at
`4835dfd0362876582a216e38f0115daa62bda3bd`. The issue body and its 2026-10-28
readiness disposition were read before implementation. Owner decisions D1–D5
remain fixed. Independent review is the next gate.

## Frozen inputs

- `declaration.json` owns the printed Bülow Tables 1–3 parameters and corrected
  reaction constants. Its SHA-256 is
  `a491381972ddad9224f1b0833371b82479db7f4f0244dab99fbb9d9cffc2a657`.
  It binds the source and inventory files by their hashes.
- The declaration specifies D1's literal free-species mole-fraction sum and D3's
  Hsieh polynomials, with no density term. Its descriptive pending-896 choice
  must be mapped to the merged Engine's declaration spelling. The frozen file
  itself remains the scientific input identity. The current wheel cannot admit
  that permittivity choice.
- `placeholder-3e83e19c.json` is the Engine-admitted document used only for these
  checks. It removes the descriptive preparation metadata and substitutes the
  existing component-mixing `solvent-only` permittivity choice. It is not the
  pressure-run declaration. Both document hashes are in `numerical-checks.json`.
- Every component, including neutrals, has solvation factor 1. The ionic-region
  relative permittivity is 1; it has no effect when both Born coefficients are
  zero. Ion Born and Debye–Hückel diameters equal σ; packing diameters equal
  0.88σ. MDEAH+ is a single nonassociating sphere. Same-sign dispersion pairs,
  including self pairs, are excluded.
- `sources.json` records the six PDF identities and hashes, three existing CSV
  paths and hashes, corrected reaction assignments, and the SI's original row
  labels and reference numbers. Source tables are reused at their existing paths.
  No source table or PDF is copied into this directory.
- `inventory.json` freezes the 67 positive-loading source-row identities, eight
  published comparison values and ±3-percentage-point intervals. It preserves
  actual row temperatures and molalities through the hashed source CSV, on a
  basis of 1 kg initial water. Total pressure is primary; zero-loading rows 28
  and 69 and the product of vapor CO2 mole fraction and total pressure are
  diagnostics. The 413 K rows are excluded. No pressure deviations are computed.

## Numerical evidence

All completed checks passed. Exact inputs, comparison values, tolerances and
errors are retained in `numerical-checks.json`.

| Check | Result |
|---|---|
| Wheel identity | SHA-256 `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`; installed package files match wheel bytes |
| Classic Born reduction, Eq. 20 | Native and independent expression both −5.739844399715162; relative difference 0, tolerance 1e-9 |
| Water diameter and Table 3 temperature laws | At 298.15, 333.15 and 393.15 K, native residual Helmholtz energy agrees with independently evaluated constant inputs within 1e-12 absolute; observed difference 0 |
| Hsieh pure-solvent laws | Native water and MDEA permittivities agree with the printed polynomials within 1e-12 absolute at the same three temperatures |
| Association | CO2 site fractions 1 in MDEA–CO2 and 0.9869904051415042 in water–CO2 at 333.15 K and 1000 mol/m³; no ionic sites |
| Cross-association energy and volume | Water–CO2 energy 1212.8 K; explicit Eqs. 24–25 inputs reproduce native association energy with absolute difference 0, tolerance 1e-12 |
| Water pK on molality scale | 13.9983057944 versus 14.00; tolerance 0.005 |
| MDEAH+ pK on molality scale | 8.5509151552 versus 8.551; tolerance 0.0005 |
| Carbon hydration pK on molality scale | 6.3590659626 versus 6.359; tolerance 0.0005 |
| Bicarbonate pK on molality scale | 10.3327985981 versus 10.333; tolerance 0.0005 |
| Full document and reaction admission | Eight species with H+ bookkeeping, four reactions, raw mole-fraction infinite dilution in water and system-pressure reference compile; no equilibrium solve |
| Native derivatives, neutral state | Maximum relative difference 2.599e-9; required limit 1e-5 |
| Native derivatives, charged state | Maximum relative difference 2.627e-9; required limit 1e-5 |
| Dielectric values 58 and 72.5 | Pending merged #896 wheel; not evaluated with the placeholder |

The Born and derivative states use 333.15 K and 30000 mol/m³. Their compositions
are retained explicitly. Derivatives compare native pressure density slope,
residual Helmholtz temperature slope derived from native entropy, and residual
chemical potentials against centered finite differences of pressure and total
residual Helmholtz energy. Ionic composition directions conserve charge. These
are prescribed-density checks, with no claim of phase stability.

The scale conversion is
$\ln K_m=\ln K_x-\Delta\nu_{solute}\ln(M_w m^\circ)$, using
$M_w=0.01801528$ kg/mol and $m^\circ=1$ mol/kg. The solute stoichiometric sums
are 2 for water dissociation and 1 for the other reactions. The pK tolerances
reflect the displayed precision of the issue's reference values. Water uses a
pure-liquid reference; every other species, including MDEA and CO2, uses infinite
dilution in pure water. An unset native reference pressure means system pressure,
not a fixed 100 kPa standard state. The 100 kPa compilation input is only a
chosen system pressure.

## Source basis and limits

The preparation read the local PDFs directly: Bülow Eqs. 1–4, 12–26 and Tables
1–3 (pp. 6328–6331); SI Tables S1 and S3; Austgen Table V (p. 547); Hsieh
Eq. 3 and Table 3 (p. 621); and Kamps–Maurer Eqs. 8 and 12 (pp. 1508–1509).
The existing Kuranov Table 2 CSV supplies the row inventory. PDF hashes were
computed from the local Zotero attachments without writes to Zotero.

The corrected SI assignment follows the issue: SI Ka,5 supplies MDEAH+
dissociation, Ka,2 carbon hydration, Ka,3 bicarbonate dissociation, and Ka,4 is
excluded as H2S. Austgen writes the reactions in hydronium form; using Bülow's
H+ directions retains the issue's acknowledged water-activity difference.
The printed association volumes are used without the conversion from issue 222.
No issue 222 calculation or record was changed.

The Hsieh MDEA polynomial is measured over 303.15–328.15 K and the water law is
listed over 273.15–373.15 K. Values outside those ranges are extrapolations.
Kamps–Maurer's measured range ends at 368 K. Vahidi–Moshtari and Edwards were
not read. The authors' exact dielectric implementation, scored observable and
row selection remain unrecovered. The interval width is a working allowance,
not a measurement uncertainty.

## Repeat after Engine 896

Qualify an immutable wheel built from merged Engine main and record its full
commit and SHA-256. Check both native dielectric reference values, 58 and 72.5,
at solvent permittivities 80 and 20 and mole fractions (0.7, 0.1, 0.1, 0.1),
within 1e-12 absolute. Check density and molar-mass independence, pure-solvent
limits, and refusal at a zero solvent denominator. Repeat the neutral and
charged derivative checks with the new mole-fraction rule, within 1e-5 relative;
repeat the Born reduction with that rule as well. Recheck document and reference
admission when mapping the frozen declaration to the merged Engine grammar.
The pressure run remains blocked until that wheel is qualified and preparation
has received independent review.

## Replay preparation

From the task worktree, run:

```bash
nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_bulow_reproduction/prepare.py
```

`prepare.py` owns input serialization and these bounded numerical checks. It
imports only the installed pinned Engine and the Python standard library;
no local environment is created. This command never solves a reactive bubble
state or fits parameters. Source and inventory hashes, document admission,
analytic comparisons, and derivative checks protect distinct numerical risks.
