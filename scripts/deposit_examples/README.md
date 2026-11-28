# Reproduce the aqueous amine calculations

The archive contains the fixed-reference MEA, DEA, MDEA and AMP declarations, processed observations, selected parameters and numerical results. The reported fit manifests and selections are under `analyses/amines/results/move/{mea,dea,mdea,amp}/reported/fit/`.

Use Python 3.13 and uv on x86-64 Linux with glibc 2.39 or later. `uv.lock` pins the development wheel used for the reported fits and the reproduction commands. The calculation code verifies its hash and installed bytes. The archive also contains the earlier 1.3.0 and 1.3.1 wheels used for the MEA comparison calibration and earlier transfer calculations. See `provenance/source.json` for wheel paths and hashes. The project code is under MIT. Third-party measurements remain under the terms of their sources.

From the deposit root, check the archived tables, figures and named manuscript values, then regenerate the display files from the retained results.

```sh
sha256sum -c SHA256SUMS
uv run --locked python -m analyses.amines.displays --check
uv run --locked python -m analyses.amines.displays
```

Build both PDFs with TeX Live and latexmk. The second pass resolves cross-references between the article and supplement.

```sh
cd docs/scientific/latex
for document in supplement main supplement main; do
    latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds "$document.tex"
done
cd ../../..
```

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
