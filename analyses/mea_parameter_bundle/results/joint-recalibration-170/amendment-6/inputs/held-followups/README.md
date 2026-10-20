# Held follow-up declarations (#170 amendment 6)

Declarations only; no fit, release, derivative evaluation or Engine solve was run.
Authority: `tmp/joint-design/amendment-6-paper-candidate.md` §0b, “Matched F1 fits and selection”,
and owner comments 6278610430, 6278891898 and 6279085063 (2026-10-19).
The five Amundsen loading-0.4 rows stay excluded, the 50 Cai rows and all 16 coordinates stay
unchanged, and the CO₂-free assessment limit is 1.0 kg/m³ (2u).

## Frozen B identity and chemistry

B uses `analyses/mea_parameter_bundle/data/input/fit-campaigns/frozen-172/larger-dV/F1-B/start-parameters.json`; SHA-256 `be92bc06ff4b8681c56a0a5e2fb23f0f098c2eaecd9885879a8f30d1f7fd689d`.
Exact locator: `stage3/qualification/current/spec.json`, case `larger-dV/F1`, start `B`,
`source.commit = 32129e5`, `source.path = analyses/mea_parameter_bundle/results/permittivity-refit-172/larger-dV/F1-B/start-parameters.json`.
The source bytes at that commit equal the frozen file. Its historical `run.py`, function `fit`,
reads `heat-final-170/F1-B/start-parameters.json`, substitutes the measured dielectric branch and
sets B Born diameters to (4, 3) Å. This identifies the original B initialization, rather than an
optimizer endpoint, CO₂–MEA variant or another F-family. The historical README section
“Same-wheel replay and fitting” states: “All 24 original attempts retain the original starts”.
The earlier screen at `5ebcb37` contains fixed-parameter dielectric variants, not this measured-route B start.

Inherited totals are recovered from `c369705:analyses/mea_parameter_bundle/results/reaction-temperature-fit/candidate-receipt.json`,
SHA-256 `e01a4f75b4b7027a02c20f70b66ad47ce52f3df42676fab909c82667cc8a46f1`,
matching the hash in B’s R2/R5 provenance. Use `candidate_shifts_kj_mol`, multiplied by 1000.
The current file at the same path has been replaced by a later study and does not supply these totals.
The retained `amendment-2/diagnosis-refresh-swap/README.md`, “Basis and fixed-vector method”,
independently records R2 = −8201.884540544 J/mol and R5 = 8418.523404172 J/mol.
These inherited totals are needed by `fit_campaign.py` lines 620–625 when writing later chemistry totals.
Existing `stage6_coordinates` bounds enthalpy-shift increments about the supplied start, and the
stored R5 a_k directly. `rebase` therefore moves B's two increment boxes by −(inherited total) and
its a_k box by +(inherited R5)/(R ln 10) = +439.73 K, so the total shifts stay in ±10000 J/mol and
the unshifted a_k in [2400, 3000] K, the same physical box as start A (parent correction, 2026-10-19).
R4 and all undeclared neutral/trace-ion quantities remain those of the corrected Held start.

With the rebased box no start value is clipped (B stored a_k 3037.64 K, unshifted 2597.91 K).
One start modification (owner decision, 2026-10-19): carbamate–MEAH⁺ k_ij starts at −0.99 instead of the frozen
−1.0 (its lower bound). At −1.0 with B's other ion values the Engine refuses 25 CO₂ partial-pressure problems
before solving (`NOT_RUN: rank-deficient declared equations`); −1.0 × (1 − 1e-6) still refuses, −0.99 evaluates all
307 rows. Evidence: `../../held-followups/diagnosis/`.

| Clipped identity | Frozen B value | Start value |
|---|---:|---:|

## held-B

Start SHA-256: `cb4096a62c8a73d5188cf00e129290a52dba2412e99821678f0d26c28e45baa2`.
Inherited totals (J/mol): R2 = -8201.88454054374; R5 = 8418.523404172149.
All differing identified parameter magnitudes against `inputs/revision-3/held-start.json`:

| Parameter identity | Held larger-A reference | Prepared start |
|---|---:|---:|
| `component/carbamate-anion/born_diameter` | 3.5605 | 3.0 |
| `component/carbamate-anion/debye_huckel_diameter` | 3.5605 | 3.53543525721 |
| `component/carbamate-anion/dispersion_energy_over_k` | 533.11 | 453.265244384 |
| `component/carbamate-anion/packing_diameter` | 3.1332400000000002 | 3.1111830263448 |
| `component/carbamate-anion/segment_diameter` | 3.5605 | 3.53543525721 |
| `component/protonated-monoethanolamine/born_diameter` | 3.563 | 4.0 |
| `component/protonated-monoethanolamine/debye_huckel_diameter` | 3.563 | 3.48508556586 |
| `component/protonated-monoethanolamine/dispersion_energy_over_k` | 228.71 | 232.687201645 |
| `component/protonated-monoethanolamine/packing_diameter` | 3.13544 | 3.0668752979568 |
| `component/protonated-monoethanolamine/segment_diameter` | 3.563 | 3.48508556586 |
| `pair/carbamate-anion/protonated-monoethanolamine/k_ij` | -0.7072858902151943 | -0.99 |
| `pair/carbamate-anion/water/k_ij` | 0.13408074131722733 | -0.05009622525689636 |
| `pair/protonated-monoethanolamine/water/k_ij` | -0.3795540800656849 | 0.11717335470882706 |
| `pair/protonated-monoethanolamine/water/k_ij/reciprocal_temperature_slope` | -112.56775058400221 | -119.03707287298563 |
| `reaction:R2:correlation:a` | 235.4815349923 | 232.33141533884407 |
| `reaction:R2:correlation:b_k` | -12092.1 | -11105.640030520277 |
| `reaction:R5:correlation:a_k` | 2677.91 | 3037.6399534696106 |
| `reaction:R5:correlation:b` | 0.3869 | -1.0173150837285996 |

Checks: both declarations pass `fit_campaign.verify`; both pass `stage6_ties`;
16 coordinate objects construct without solving; 12 installed Engine files match the wheel.
Information/fit binding is identical: `1deef32a73ae1fb212cdb7f11cc8529293e0da7f29dd6881535fe825e1fe3234`.
Only the declared start, its input-list hash, purpose, fit-case start ID and pending fresh-release
path/hash and the three chemistry bounds rebased by the inherited totals (unchanged when they are zero) differ from `inputs/joint-mea-water/held-*.json`. No rows, scales or weights change.

## held-smaller-A

Start SHA-256: `548d1a46425e420bbb414f931cb525161a8b10a7d299773fbf0e0e9513ab13a7`.
Inherited totals (J/mol): R2 = 0.0; R5 = 0.0.
All differing identified parameter magnitudes against `inputs/revision-3/held-start.json`:

| Parameter identity | Held larger-A reference | Prepared start |
|---|---:|---:|
| `component/monoethanolamine/dielectric_temperature` | 1019.0786110170793 | 2436.4423007273617 |
| `component/monoethanolamine/dielectric_volume` | 0.7309888238084122 | 0.2464540312088979 |

Checks: both declarations pass `fit_campaign.verify`; both pass `stage6_ties`;
16 coordinate objects construct without solving; 12 installed Engine files match the wheel.
Information/fit binding is identical: `7b65b3883ca654840b67134f054741e37ace7ef37740e4ecea77505ec4088c26`.
Only the declared start, its input-list hash, purpose, fit-case start ID and pending fresh-release
path/hash and the three chemistry bounds rebased by the inherited totals (unchanged when they are zero) differ from `inputs/joint-mea-water/held-*.json`. No rows, scales or weights change.

## Smaller-A correction boundary

Starting from A4 smaller-dV control, copy the corrected larger-A MEA–water pair (k and the
single b coefficient with its metadata), set all six Debye–Hückel diameters to σ and retain
packing = 0.88σ. The complete magnitude comparison above leaves exactly the two MEA dielectric
coefficients different. The A4 smaller-branch topology provenance locator remains branch-specific.
Purpose text describes the prepared start. No additional physical parameter correction is present
in the revision-3 / without-Amundsen / joint-MEA–water declaration chain.

## Hartono x₃ sensitivity function

`x3(endpoint_path, output=OUT)` copies the selected Held endpoint without changing any parameter,
and reads its sibling `chemistry-coordinates.json` for inherited totals. It writes
`held-x3-start.json`, `held-x3-density-source-rows.json`, `held-x3-information.json` and `held-x3-fit.json`.
Exactly 32 Hartono carbon-dioxide feeds and source-row alpha values are replaced by the CSV’s
`co2_loading_from_mole_fraction_mol_per_mol_mea`; nominal 30 mass % solvent and all other observations,
IDs, coordinates, scales and weights remain unchanged. Source values and temperatures are checked
against the CSV; endpoint and chemistry files enter the hashed input list.

`fit_campaign.verify` line 47 asserts equality of the entire frozen scale document with
`density_scales(updated_source_rows)`. This fails after the alpha replacement: the returned rows
contain changed alpha, secants, loading contributions and scales. Even numerically unchanged scales
would not preserve equality of the complete documents. Regenerating scales would violate §0b.

Minimal declaration-only arrangement: rename `density_scale_path` to `frozen_density_scale_path`,
retain the original frozen file/hash in `inputs`, and bind the renamed reference path through
`stage6_binding`. No consumer except `verify` reads the old field. The function explicitly checks
every fitted loaded-row scale against the frozen file before calling `verify`. This preserves
scale verification against the adopted file without falsely requiring composition-based recomputation.
The function also exercises the incompatible declaration and requires its exact AssertionError.

No x₃ declarations are selected or generated in this directory by `build()`. Its scratch dry run
writes only under `tmp/held-followups-x3/`, using the existing Held endpoint to check construction.
Checked endpoint SHA-256: `ceefc95cd051fb291e0c08675c4cb6f159bf10dca0116ef1251ba78c243f79c7`. Exactly 32 Hartono feeds/alpha values change;
both declarations pass `verify`, all six ion ties and construction of 16 coordinate objects.
Information/fit binding: `6021369ff084283ec4d24875a39b94769bf1e4a5d6e1e27de661d18bab4ce04d`.
Frozen scale-file SHA-256: `ee61922f62b40e8a3f947e85bb9d0e1247ff5dd97e567e554f7b90e589dc95ce`.
All 32 Hartono scales would change if recomputed; for
`Hartono2014_density_20C_alpha0.11` the frozen scale is 1.9913504368895074
and the recomputed value is 2.0312641880450997 kg/m³.
The incompatible declaration reproduces `AssertionError` at `fit_campaign.py:47`.
The dry run selects no fit. To generate the later selected-endpoint declarations, use:

```bash
PYTHONPATH=src:analyses/mea_parameter_bundle/scripts /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/tmp/a6/venv/bin/python analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-6/inputs/held-followups/build.py.txt x3 <selected-endpoint-path>
```

## Reproduction and limits

From the checkout root:

```bash
PYTHONPATH=src:analyses/mea_parameter_bundle/scripts /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/tmp/a6/venv/bin/python analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-6/inputs/held-followups/build.py.txt
```

The parent must generate fresh information releases and fill their hashes before fitting.
These checks establish declaration consistency, not density predictions, convergence, physical validation
or permission to adopt a parameter record. Campaign scripts are unchanged. The disclosed generator
owns only the requested start/declaration preparation; it introduces no numerical method.
