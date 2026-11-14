# DEA inputs for Part II, issue 346

Phase 1 supplies plain data for the shared Part II route owned by issue 343.
No new fit, phase search, model curve or F2 result is claimed. The shared route
must be reviewed and merged before phase 2 runs. Paths in the declaration
resolve from the repository root. This is input data, not a new driver interface.

- `parameters.json` starts from the retained B-2 endpoint and replaces the six
  shared components, all shared pairs and the water correlation with F2.
  DEA ion Born diameters equal their fixed segment diameters: DEAH+ 2.9477
  angstrom and DEACOO- 6.167209298821595 angstrom. The declaration retains
  explicit ties for the route to apply. No cation–bicarbonate fit is introduced.
- `declaration.json` binds the adopted shared-values file and F2 parameter
  document by SHA-256, supplies chemistry, observations, four fitted coordinates,
  original bounds, weights and scales, and the two requested starts.
  The endpoint's native optimizer values refer to the original B-2 coordinate
  chart and carbamate-law anchor. The route must preserve those physical bounds
  when representing the endpoint; it must not recenter the enthalpy bounds.
- `data-roles.csv` enumerates 299 observations: 80 fitted, 67 not fitted and
  152 comparison only. These include all seven Lawson observations at
  394.26111111111106 K as not fitted. All were seen during development.
  Each row carries the applicable reaction-range marks. No temperature
  exclusion is applied; existing source row identities define the fitted set.

All reaction constants have one calculation interval, 293.15–458.64 K.
The upper limit includes the Cai binary comparison, although that calculation
uses no reactions. The Bower dissociation measurements cover 0–50 degrees
Celsius (273.15–323.15 K with the modern conversion). Of 30 fitted Lawson
pressures, 23 lie outside that range; all seven additional Lawson pressures
also lie outside it.

273.15–498.15 K is the source-correlation range stated by Austgen 1991 Table V p.547 (citing Edwards 1978), not verified measured coverage.

The R1–R3 coefficients, reference temperatures and standard states follow the
adopted file. Their calculation limits are changed explicitly to the common
interval; source-range marks are independent of those calculation limits.
The Part II reaction-range table does not establish separate measured coverage
for the fitted DEA hydrolysis law; its range is recorded as unknown. Binary
Cai and Horstmann comparisons use no reactions, so reaction-range marks are
not applicable to them.

Phase 2 needs the merged issue-343 route to consume these inputs, preserve the
original coordinate chart, perform fit continuation and per-amine stability
searches with supplied splits and conditional penalty/retreat, and produce
conditional standard errors, range-separated comparisons and curve data.
The DEA protonation-source check, numerical endpoint checks, notebook, figures
and independent delivered review remain phase-2 work. Historical F0 files and
manuscript files are unchanged.
