# Reactive ePC-SAFT Parameter Evidence

This directory retains the Issue #70 supported-negative decision, source and
readiness receipts, and bounded diagnostic evidence. There is no active MEA
parameter set.

New generic ePC-SAFT methods are built and debugged first in
`ePC-SAFT-project/analysis/` or `validation/`. This repository may then run the
pinned public Engine method directly against MEA-owned inputs and an accepted
immutable parameter packet. Engine Issue #80 owns the current campaign.

The following Born/permittivity scripts are retained as dormant parameter-evaluation methods:

- `run_ion_coefficient_blocks.py`
- `evaluate_calorimetry_consistency.py`
- `compare_independent_evidence.py`

They are not current entry points and will require the accepted packet and its
retained input tables before they can run. Candidate-specific renderers and
superseded result trees were removed.

The Kiepe CO2--water induced-association calculation remains a valid local
Engine reproduction with qualified source evidence. Render-only retained
figures with:

```bash
uv run python analyses/reactive_epcsaft_parameter_evidence/scripts/render_figures.py
```
