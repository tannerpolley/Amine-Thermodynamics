# Direct MEAH+/MEACOO- Volumetric Measurement Request

## Decision this experiment should resolve

Measure whether an acetate-informed `MEACOO-` size prior is compatible with the
aqueous exact salt. The requested observable belongs to the electroneutral
2-hydroxyethylammonium (2-hydroxyethyl)carbamate solution, not to either
isolated ion.

## Primary series

Prepare one independently characterized salt batch and measure vibrating-tube
density at 298.15 K and laboratory pressure for 6 aqueous compositions,
including a dilute point, four interior points, and the highest stable
concentration. Report the composition as both salt mole fraction and molality;
retain the measured quantities used for each conversion. Replicate at least
the dilute, middle, and concentrated points from separately prepared samples.
Include matched water and unloaded aqueous-MEA controls.

The requested uncertainty target is a combined standard density uncertainty no
larger than 0.001 g/cm³. Report the densimeter model, calibration standards,
calibration residuals, temperature and pressure uncertainty, replicate values,
sample order, equilibration time, and any rejected measurement with its reason.
Do not report only a fitted density correlation.

## Chemical identity required at every density point

For the isolated batch and every prepared solution, retain:

- synthesis route, purification history, salt stoichiometry, batch identifier,
  and storage history;
- Karl Fischer water content;
- quantitative NMR, or an equivalently calibrated assay, resolving free MEA,
  carbamate, bicarbonate/carbonate where present, and a stated detection limit;
- total carbon or another independently calibrated CO2-inventory measurement;
- composition masses with balance resolution and calibration;
- pH only as contextual data unless its scale, calibration, junction, and
  equilibrium interpretation are documented.

If dissolution or handling changes the carbamate/MEA/CO2 inventory, preserve
the measured species distribution. A nominal preparation recipe is not a
substitute for the state that entered the densimeter.

## Data package requested

Provide one raw table with sample and replicate identifiers, masses, reported
and converted composition bases, temperature, pressure, density, uncertainty
components, assay results, detection/censoring flags, and timestamps. Provide
instrument exports and calibration files without overwriting them with
processed values. A separate derivation table may contain apparent molar
volumes, with the equation, molar masses, pure-component densities, covariance
assumptions, and propagated uncertainty.

The experiment is discriminating only if the measured density and simultaneous
speciation can reject at least one preregistered parameter candidate relative
to experimental uncertainty. Otherwise the disposition remains
`additional-data-required`.

## Secondary solid evidence

Helium-pycnometer density or an X-ray crystal structure is useful for material
identity and crystal packing. Record polymorph, hydration, temperature, and
uncertainty. These results remain structural priors and may not replace the
aqueous density/speciation series because a crystal is not a hydrated reactive
solution.
