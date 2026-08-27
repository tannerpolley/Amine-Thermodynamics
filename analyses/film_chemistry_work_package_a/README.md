# Film Chemistry Work Package A

This analysis validates the versioned Issue #72 Work Package A input contract.
It checks source hashes, ordering, exact reaction projections, elemental and
charge balances, directions, dimensions, domains, uncertainty states,
published-correlation anchors, and explicit exclusions.

The result is intentionally nonexecutable: the primary kinetic paper reports
dimensionally inconsistent rate-constant units, primary diffusivity
coefficients are unavailable, the retained density extraction disagrees with
the primary-source uncertainty by one decimal place, and no active MEA
parameter packet exists. Work Package B remains blocked by ePC-SAFT Issue #80.

Run the bounded analysis with:

```bash
uv run python -m MEA.common.film_chemistry_inputs \
  --write-report analyses/film_chemistry_work_package_a/results/validation_report.json
```
