# Film Chemistry Work Package A

This analysis validates the versioned Issue #72 Work Package A input bundle: its file hashes, declared fields and units, species and charge balances, correlation values and property-uncertainty inventory, each checked fail-closed.
It checks source hashes, ordering, exact reaction projections, elemental and
charge balances, directions, dimensions, domains, uncertainty states,
correlation evaluation/transcription anchors, and explicit exclusions. The
eight anchor calculations reuse the four published A/B pairs; they test
deterministic evaluation and transcription, not independent physical agreement.

Version 3 supersedes version 1 for Work Package A after the #152 Amundsen
correction; version 1 stays unchanged as the pre-#152 record, and version 2 is
reserved for the Work Package B film-input release (MEA-Absorption-Column
issue36 release guard). The retained density observations distinguish the 0.00005 g cm^-3
instrument uncertainty from the 0.0005 g cm^-3 combined uncertainty of the
unloaded rows; those rows and the unloaded viscosity rows (1 %) are admitted,
and no interpolation law is introduced. Amundsen 2009 (pp. 3099-3100) gives
loaded-solution estimates of 0.002 g cm^-3 and 3 % but excludes its unnamed
highest temperatures and loadings, so the 68 loaded density and 75 loaded
viscosity rows carry no row uncertainty, keep those estimates separately, and
are not admitted. Downstream admission is limited to 293.15--323.15 K, discrete 1 M
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
