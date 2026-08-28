# Film Chemistry Work Package A

This analysis validates the versioned Issue #72 Work Package A input contract.
It checks source hashes, ordering, exact reaction projections, elemental and
charge balances, directions, dimensions, domains, uncertainty states,
correlation evaluation/transcription anchors, and explicit exclusions. The
eight anchor calculations reuse the four published A/B pairs; they test
deterministic evaluation and transcription, not independent physical agreement.

The retained density observations distinguish the 0.00005 g cm^-3 instrument
uncertainty from applicable combined uncertainties of 0.0005 g cm^-3 for
unloaded rows and 0.002 g cm^-3 for loaded rows; no interpolation law is
introduced. Downstream admission is limited to 293.15--323.15 K, discrete 1 M
or 5 M MEA cases, and loading below 0.5 mol CO2/mol MEA. The finite-reaction
records separately retain their local source domains; F3 records unavailable
local bounds because its cited coefficient source is not retained. The primary
kinetic paper reports dimensionally inconsistent rate-constant units, primary
diffusivity coefficients are unavailable, and no active MEA parameter packet
exists. Work Package B remains blocked by ePC-SAFT Issue #80.

Run the bounded analysis with:

```bash
uv run python -m MEA.common.film_chemistry_inputs \
  --write-report analyses/film_chemistry_work_package_a/results/validation_report.json
```
