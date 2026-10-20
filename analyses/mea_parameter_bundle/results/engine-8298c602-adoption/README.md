# Engine 8298c602 adoption (#170 strict gate)

The selected record's 152 retained Engine 21e761c3 predictions are reproduced on
Engine 8298c602 to **at most 2.9 × 10⁻¹² relative difference**; 13 are bitwise
equal. Every difference is far below the 10⁻¹⁰ equilibrium row tolerance.
[comparison.json](comparison.json) retains every old/new value and the comparison
definition.

| Quantity | Count | Bitwise equal | Worst relative difference | Worst absolute difference | Unit |
|---|---:|---:|---:|---:|---|
| CO2 partial pressure | 47 | 0 | 1.40 × 10⁻¹³ | 6.32 × 10⁻⁹ | Pa |
| Species mole fractions | 94 | 13 | 2.89 × 10⁻¹² | 6.38 × 10⁻¹⁴ | mol/mol |
| Vinjarapu integral heat of absorption | 8 | 0 | 1.03 × 10⁻¹³ | 8.44 × 10⁻⁹ | J/mol CO2 |
| Equilibrium solution heat capacity | 3 | 0 | 5.72 × 10⁻¹⁵ | 1.95 × 10⁻¹⁴ | kJ/(kg K) |

The largest relative difference is the MEAH⁺ mole fraction of Matin 2012 state 5.
The quantities, evaluators (`fit_observations.py:rows_for/replay` on the `base` set
of `results/fit-campaign-179-baseline-complete/spec.json`; `heat_evidence_170.py:cp_check`
at the three Hilliard states), record and declaration are those of the
[21e761c3 adoption](../engine-21e761c3-adoption/README.md); its retained new-wheel values
are the old values here, so the old wheel was not rerun. The old wheel's IPOPT used
MUMPS 5.6. The new wheel selects MA57 when the HSL library loads (Engine #643), and it
reports `ma57` here. Results that agree to roundoff without being bitwise equal are
consistent with that change, but no single cause was isolated. This is numerical verification of
fixed-state predictions for this record. It does not test stability classification,
phase families or fitting. Those are requalified on the A7 branch (A4-control and
A6 families, 307-row replay) before any A7 fit. It adds no physical validation.

## Why the interface changed

The A7 strict gate ([#170 comment 6283064075](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6283064075))
needs a merged-main wheel with Engine #660. Every such wheel also contains
Engine #609 leg 2 (`b11d69d6`, "Return equilibrium T and P as plain numbers").
`EquilibriumResult.temperature` and `.pressure` are now numbers, `None` without a state,
instead of one-element lists. On this wheel, the unchanged MEA code failed both A7 qualification families at all 73 points
with `TypeError` before any stability test. The 307-row replay stopped at
`fit_observations.py:261`. Those failures are retained and charged on the A7 branch.
The owner chose repo-wide adoption
([#170 comment 6297147461](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6297147461)).

## Code and record changes

- **Engine reads:** the T/P reads change from `x[0]`/`list(x)` to `x`. There are
  22 one-line replacements in 10 files, with no algorithm change:
  - `shared_evaluation.py` 3, `fit_observations.py` 5, `final_evidence.py` 4;
  - `verify_temperature_reference.py` 4, `verify_reference_calorics.py` 1;
  - `validate_thermal_references.py` 1, `verify_pressure_reference.py` 1;
  - `check_neutral_co2_mea.py` 1;
  - `model-d/checks.py` 1;
  - `analyses/reactive_epcsaft_parameter_evidence/.../generate.py` 1.

  The shared evaluator's success-only pressure-bounds check now tests the one
  system pressure. Newly written equilibrium evidence holds `temperature` and `pressure` as numbers.
  Earlier retained records keep their one-element lists unchanged; no reader
  indexes those fields.
- **Pin:** `ENGINE_WHEEL_SHA256` and `ENGINE_COMMIT` in `shared_evaluation.py`
  (two lines), the relative wheel path in `pyproject.toml` and `uv.lock`, and
  `analysis.yaml`.
- **Campaign-code ceiling:** 10 of those lines are in the counted
  campaign files (`fit_observations.py` 5, `final_evidence.py` 4,
  `check_neutral_co2_mea.py` 1). The gross total is now 1,331 against the
  owner-raised ceiling of 1,331 (`../joint-recalibration-170/amendment-4/compute-ledger.json`).
- **Not changed:** `analyses/mdea_kuranov_refit` (#126) pins wheel 21e761c3 in
  its own scripts and refuses any other wheel. Its six list reads and its results
  stay on that wheel; re-pinning belongs to #126. `fit_neutral_co2_mea.py`
  declares the amendment-4 21e761c3 wheel and package versions in its own
  `campaign.verify` guard, so it keeps its list reads and runs only on that wheel. Retained numerical outputs,
  parameter documents and figure locks are byte-unchanged.
- **Other Engine changes since 21e761c3:**
  - Charged-molecule ions (#641) and cation mixing are declaration opt-ins that
    no MEA document uses.
  - The removed `InfiniteDilutionReference.value_difference` has no MEA reader.
  - The stability changes (#666, #672, #673, #677), the discovery and start
    changes (#647, #648, #652) and the rank-test scaling (#661) are outside the
    fixed-state comparison above. The A7 requalification is where they are tested.

## Wheel and installation

- Tag `main-8298c6029ebb8b467929badc4a223c580ec591ab` targets commit
  `8298c6029ebb8b467929badc4a223c580ec591ab`, which contains Engine #660
  (delivered on main `655871fc`).
- Relative path:
  `build/engine-wheels/main-8298c6029ebb8b467929badc4a223c580ec591ab/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl`.
- SHA-256 `8897a0caab9f2508ed642f42c8b5226957fbe7035ed7bfdad71e4166798785b3`.
  The download passed `sha256sum --check --strict`. The release asset digest, the
  tag target and `release.json` (commit, filename, checksum) match.
- `uv lock` changed only the `epcsaft` source and hash. `uv sync --locked` exits 0;
  the locked environment has numpy 2.4.4 and scipy 1.17.1.

Fresh checkout: replace the tag in the
[21e761c3 instructions](../engine-21e761c3-adoption/README.md#wheel-and-installation)
with this one.

## Checks

[checks.json](checks.json) records the commands and exits.

- Pytest: **76 passed, 0 failed** (11.3 s). The seven failures recorded at the
  21e761c3 adoption no longer occur; that change predates this adoption, and
  `main` was not rerun to attribute it.
- The source snapshot `data/input/parameters.json` (version 2) is still refused
  after the existing `c_shell`/`c_dielectric` defaults, with exactly
  `ParameterError: missing model/electrolyte/ionic_dispersion`
  ([source-construction.json](source-construction.json)).
- Ruff and manuscript freshness were not run.
- Compute: comparison run 1, 3.38 wall-s / 17.28 CPU-s; run 2, 3.45 / 17.33; source
  construction 0.19 / 2.25. Total 8 wall-s (rounded up) / 36.86 CPU-s, charged against
  the A7 qualification allocation. Run 2 replaced run 1's relative difference
  |new − old|/|old| with the 21e761c3 adoption's declared definition,
  |new − old|/max(|old|, |new|, 10⁻³⁰⁰). The 152 predictions are bitwise
  identical between the runs, and 64 relative differences change. Run 1's output and
  timing are `evaluate-r1-*`.
