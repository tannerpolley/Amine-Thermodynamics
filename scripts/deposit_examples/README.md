# Reproducibility package for referee round 10

This package contains the fixed 100 kPa reaction-reference calculations for
aqueous MEA, DEA, MDEA and AMP adopted in #440. The examples replay three
states at the retained endpoints. They perform numerical verification on the
study wheel. The comparisons with measurements and the finite phase searches
have the limits stated in the #440 notebook and the manuscript.
The round-9 evidence includes the four DEA certificates in Table S48,
the shared-interaction comparisons in Tables S49–S50, and the pressure
and search accounting.

## Verify and install

From the package directory, on Linux x86-64 with glibc 2.39 or newer and CPython
3.13, run the following. Keep the environment outside the deposit so the
package can be checked and archived as received.

```sh
sha256sum --check --quiet SHA256SUMS
env_dir=$(mktemp -d)
uv venv --python 3.13 "$env_dir"
uv pip sync --python "$env_dir/bin/python" --require-hashes requirements.txt
uv pip install --python "$env_dir/bin/python" --no-deps \
  build/engine-wheels/main-05e94210*/epcsaft-1.3.1-*.whl
export PYTHONPATH="$PWD/analyses:$PWD/src"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for example in mea_heat dea_split c1; do
    "$env_dir/bin/python" "scripts/deposit_examples/$example.py"
done
"$env_dir/bin/python" analyses/round_9/handoff.py --check
```

On an affinity-restricted Linux host, allow at least one of CPUs 0–11 for
the archived #440 code. Each example runs one calculation at a time. The
scripts abort if a checked quantity misses its replay tolerance. See
[sample output](scripts/deposit_examples/expected.txt).
The handoff check recomputes six quantity groups from 49 retained records.
The [round-9 notebook](analyses/round_9/notebook.qmd) presents the results,
and the [handoff](analyses/round_9/manuscript-handoff.json) lists each
contributor and its SHA-256 hash.

The #440 calculations use Engine commit
`05e94210fa64cf69725e45babc0411d32139df5a` (wheel SHA-256
`c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb`).
The public `v1.3.1` tag points to `1b46e57ce8`, a different commit.
The earlier MEA calculations on 1.3.0 use the 391dfe5d wheel in the same
directory tree. [Build commits and wheel hashes](provenance.json)

## Worked states

- **MEA heat.** At 313.15 K and 1.734 MPa, add pure vapor-phase CO₂ to
  30 wt% MEA from zero to 0.31 mol CO₂/mol MEA. The script replays the heat
  of addition and the equilibrium heat capacity at the loaded state. The
  replay tolerance is half the last displayed digit (0.0005 in each
  printed unit). The producer also checks heat from the independent
  enthalpy readbacks, Cp against a centered temperature derivative, and
  the reaction reference and pressure closures.
- **DEA split.** A 30 wt% DEA feed at 298.15 K, loading 0.50 mol/mol and
  101.325 kPa (the pressure assigned to the density calculation) gives a
  confirmed split in the selected model. The script reads the #440
  declared-screen record for `weiland-1998:32:problem` (zero-based deposit
  ID 32, processed Weiland Table 2 source row 33) and starts the two-liquid
  calculation from the confirmed pair at deposit ID 42 (processed source
  row 43). The adjacent unresolved feed at loading 0.45 has deposit ID 31
  and processed source row 32. In ascending
  molar density, the daughters are 31,971.88 mol/m³ at 1.422586 mol and
  44,593.61 mol/m³ at 13.196994 mol. The decrease in $G^*/(RT)$ is
  0.001406466 mol. The density and amount tolerances are half the last
  displayed digit. The comparison of Gibbs decreases uses the sum of
  both calculations' numerical Gibbs errors. The experiment treated
  the sample as one liquid.
- **C1.** At the selected MEA bubble state `vle_obs_0131-pco2`
  (313.02 K, approximately 6.675 kPa), continue the liquid branch at
  fixed feed. The middle centered step uses ±0.3338 Pa and ±0.02 K.
  Compare the pressure derivative of extensive Gibbs energy with liquid
  volume and the fixed-reference enthalpy with the Gibbs–Helmholtz
  derivative. The comparison uses the numerical error estimates stored
  with the admitted steps. The volume resolution at this step is about
  5.25% of the volume. The absolute enthalpy is on the neutral caloric
  anchor basis and refers to the entire feed of one mole of apparent MEA
  plus water and CO₂.

## Rows, vectors and searches

- `analyses/fixed_reaction_reference/results/<design>/manifest.json.gz`
  contains the processed IDs, source rows, observable constructors,
  transformations, scales, roles and weights for the model declarations.
  The `fitted` list supplies the objective. Rows in `comparisons` have
  zero objective contribution, even where a prediction weight is
  recorded. There are 307, 140, 281, 214 and 214 fitted rows for MEA, DEA,
  MDEA, AMP free slope and AMP fixed slope. MEA's outside-objective rows
  are in the property and off-window replays. The source tables and
  conversion code keep their repository-relative paths under `data/`
  and `analyses/`.
- `manifest.json.gz` and `replacement-starts.json.gz` (where used) give
  the coordinate order, full-precision start vectors, bounds, ties and
  complete declarations from which fixed inputs are inherited. Each
  attempt's file records the optimizer start, its report, and any
  returned complete endpoint. An initial evaluation failure has no
  final vector. `selection.json` identifies the selected endpoint and
  `stationarity/` retains diagnostics and continuation attempts.
- `provenance.json` maps the Table 8 names to the full model vectors
  by file and JSON field. For the convention comparison at unchanged
  parameters, `prior_declaration` in each manifest gives the fixed-at-old
  declaration and `reference-control.json.gz` gives both replays.
  `manuscript-handoff.json` maps comparison quantities to retained
  files and hashes. The corresponding comparison vectors, row-level
  predictions and refused evaluations are included.
- Read `screen/`, `controls/` and the MEA `results/E/MEA/measured/`
  records for the per-state phase-search results. Use the recorded
  absolute or bubble-scaled pressure and follow aliases where the
  search reused a calculation. Unavailable rows, requests that were
  refused, unresolved descents, and attempted split confirmations are
  preserved with their messages and diagnostic values. The salt
  cascade and its refused rows are in the #440 results and the #435
  `salt/` and #282 records.

## Caloric inputs

- **MEA.** Use the adopted declaration's hash-addressed
  `analyses/solvent_specification_mea/inputs/caloric.json` and the
  historical specification in `results/adoption-297/historical-spec/`.
  The worked heat reads
  `data/reference/MEA/thermal/physical-ideal-gas-calorics.json`.
- **DEA.** The active declaration and the caloric coefficients it
  references are under `analyses/dea_transfer/inputs/`.
- **MDEA.** The active `stage-b.toml` links the caloric coefficients
  under `analyses/solvent_specification_mdea/inputs/`. The #440
  `R1-R3-R5` results record the historical and current-water heat-capacity
  calculations and their difference.
- **AMP.** Its declaration points to the shared MEA caloric input.
  The AMP C1 check records the explicit zero-Cp, zero-enthalpy,
  zero-entropy neutral reference gauge used because a physical AMP
  caloric anchor was unavailable. The gauge and the reaction laws are
  retained. Interpret that check on the declared gauge.

Source reaction correlations, neutral references, fixed pressure readbacks,
and the source files for measured heat and heat capacity are included with
the declarations and processed rows.
