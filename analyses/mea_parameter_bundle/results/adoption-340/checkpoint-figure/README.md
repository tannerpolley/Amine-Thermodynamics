# Figure for issue #340: MEA pressure candidates

This read-only figure compares measured CO2 partial pressures with the seven selected candidate records in the #338 evidence. Curves are evaluations of the existing `analyses/mea_parameter_bundle/scripts/model_curves.py` pressure producer (`evaluated()`), which calls `shared_evaluation.evaluate_state()` with the Engine model from `probe._base_model()`. This uses the candidate record's declared reactions and parameter mapping; no local equation copy or Engine source checkout was used.

## Inputs and fingerprints

Repository checkout: `.`, commit `dbe0db0bf5b065a55d4a52bcd346dcb67182e530`.

| Record | Selected endpoint | Parameter document SHA-256 |
|---|---|---|
| F0 | Current record | `f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97` |
| F1 | `F1/previous` | `399c77c6a51df718c40c57e5c3f6b97610ba627823b960b37995ce8d97a5e6ff` |
| F2 | `F2/previous` | `ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed` |
| F3 | `F3/previous` | `d32d4fc44ceccad977f6a34878c5d6dda21bfc0732ff0e64950b682cf9a07c87` |
| F4 | `F4/previous` | `e13c4f7eab2822fd762b97d33e360b16854f82b3a1de0877c7de11087b8fea22` |
| F4-0 | `F4-0/current` | `21ffa2b48932c7ca72d20824251171dbbeda0841fa48aad6f935dcfbc27fec24` |
| F5 | `F5/previous` | `76778d08c0cbed1699420e1d6d24aec8ef190e0aead58113c1e275edaf2def37` |

The selected endpoint names are from `analyses/mea_parameter_bundle/results/reduced-refit/summary.json`; the SHA-256 values match the fingerprints table in `results/reduced-refit/README.md`.

Engine wheel pin: commit `391dfe5d64ede5036bf160bc6ae037ad5e14af32`, SHA-256 `0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b`. The run invoked `shared_evaluation.verify_wheel()` before calculation; its installed-wheel verification passed.

Measured rows and roles:

- 159 measurements from the six-source Part I assessment: Aronu 2011, Hilliard 2008, Idris 2014, Jou 1995, Mamun 2005, and Xu 2011.
- Observed pressures and measurement conditions are from the retained canonical pressure rows. F0 is read from `results/adoption-297/paper-evidence/canonical-pressure.csv`; F1–F5 and F4-0 use their `results/reduced-refit/evidence/<candidate>/canonical-pressure.csv` snapshots. Fitted pressure row identities are from F1's `fitted-rows.csv`, the Part I data-role table.
- Points are assigned to the nearest nominal isotherm (within 3 K) so all 159 rows appear. Actual source temperatures and concentration basis are retained in `measurements.csv`. The five nominal panels are 313.15, 333.15, 353.15, 373.15 and 393.15 K, with 59, 25, 21, 18 and 36 rows, respectively.
- Curves are at exactly 30 mass% MEA and each nominal panel temperature; their loading grids span the assigned data's loading range. Hilliard and Xu source rows retain their source molality-based declarations in the measurements file. Thus the measured points preserve their source conditions; the curves show the requested nominal 30 mass% condition.

Selected source fingerprints: F0 canonical-pressure CSV `1e198b93260d8bfdeb4d2f02e497ddea5f12fa7cd57da80e1cc82247b00d8353`; F1 canonical-pressure CSV `162172556be7b5be6182523b0630bc516a506d9721503c53e44884198337fe6b`; F1 fitted rows `c21350e6e052a7d4a512c147ea2d7a5f2d396f05965192244849e2f0c599c408`; canonical VLE source file `d5cd6ea0d5d75f9994f5ed354463776a09b8f3cd081eb72ddef98dd4a356c53a`; state packet `e9d3ea9903fec9b5239dddcfe5bb8449e9f1a1aff488f0900cc9a91479ba48ba`.

## Checks and outputs

The producer's predictions were checked at every one of the 159 exact retained measured states for each candidate against that candidate's retained #338 prediction rows: 1,113 comparisons total, largest relative difference **0** (below the required `1e-10`). Exact source feed declarations were used for this identity check. There were **0 failed grid points** for every candidate (205 curve evaluations each).

The PNG and SVG contain the same five panels. The curve CSV retains every grid point and its status; the measurement CSV retains source, pressure, exact temperature, loading, concentration basis, fitted role, and panel assignment. Open marks are not fitted; filled marks are fitted. Curve lines are model evaluations; measurements are not connected.

Commands run from the repository root (all numerical library threads set to one):

```bash
agent-heavy env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 .venv/bin/python -u <original-scratch>/generate_fig340.py
.venv/bin/python <original-scratch>/render_fig340.py
```

The first command evaluates candidate models and writes `curve-values.csv`, `measurements.csv`, `prediction-identity.csv`, and `summary.json`; the second renders the PNG and SVG from those retained values without rerunning the model.

Only retained values and the chosen figure are copied here; the original scratch producers are not retained executable entry points.
