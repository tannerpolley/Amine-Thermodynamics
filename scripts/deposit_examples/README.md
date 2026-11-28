# Reproduce the aqueous amine calculations

The staged repository contains the fixed-reference MEA, DEA, MDEA and AMP declarations, the selected endpoints and the numerical records used by the manuscript. `uv.lock` identifies the ePC-SAFT wheel. The package checks its hash and installed bytes before running a calculation.

From the deposit root, check the tables, figures and named manuscript values.

```sh
uv run --locked python -m analyses.amines.displays --check
```

Build the supplement and main paper in `docs/scientific/latex` with `latexmk -pdf`. Compile the supplement, then the main paper, and repeat this order to resolve their cross-references.

## Fits and replays

Set `AGENT_HEAVY_CORES=3` and set the BLAS and OpenMP thread counts to one. Run the sodium-salt `rows` and `fit` stages before `mea reported`. Then run `rows` and `fit` for `dea reported`, `mdea reported`, and `amp reported`. For example:

```sh
uv run --locked python -m analyses.amines.run salt sodium-salts rows
uv run --locked python -m analyses.amines.run salt sodium-salts fit
uv run --locked python -m analyses.amines.run mea reported rows
uv run --locked python -m analyses.amines.run mea reported fit
```

The amine `phase` and `properties` stages take the retained reported selection. The `replay` stage evaluates each retained fit set at its saved parameters, including the first AMP fit and the MEA and MDEA sides of the water–bicarbonate ablation. The `FIT_SETS` declarations in `analyses/amines` name the original campaign archive. The commands put fresh records under `build/amine-reproduction` for comparison with the retained inputs.

## Worked calculations

```sh
uv run --locked python scripts/deposit_examples/c1.py
uv run --locked python scripts/deposit_examples/dea_split.py
uv run --locked python scripts/deposit_examples/mea_heat.py
```

The C1 example checks the pressure and temperature derivatives of the Gibbs energy at a retained MEA bubble state against the volume and enthalpy readbacks. The DEA script searches the reported DEA model at the density state of Weiland et al. at 30 wt% DEA, 298.15 K and a loading of 0.50 mol CO₂/mol DEA, where an earlier DEA fit gives a liquid–liquid split. The MEA caloric example uses the retained 313.15 K, 1.734 MPa state at 30 wt% MEA, from zero to 0.31 mol CO₂/mol MEA. Each script checks the quantities it prints against the retained numerical results.

These tests reproduce calculations with the stated models and inputs. They do not establish that the models predict physical phase stability outside the tested states.
