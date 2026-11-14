# Shared Part II route (#337, #343 Stage A)

`part_ii.py` takes one JSON declaration. Its `replay`, `fit`, and `report`
commands use the installed, immutable Engine wheel. Stage A is a capability
change: its numerical qualification is the frozen 278-observation MDEA B1
replay. No F2 amine fit or stability campaign is run until this route is
independently reviewed and merged. The replay fixture refuses `fit` and
`report`; it is not the Stage B MDEA declaration.

```bash
agent-heavy uv run --no-sync python analyses/part_ii.py \
  analyses/mdea_mea_workflow/inputs/part-ii-replay.json replay
PYTHONPATH=src agent-heavy uv run --no-sync pytest -q tests/test_part_ii.py
```

Run fits, searches, curve calculations and checks under `agent-heavy`, with
its background shell kept attached to its log until completion. Worker counts
use `AGENT_HEAVY_CORES` and the #255 free-memory rule; numerical libraries use
one thread per worker. A fit's Engine workers share this same count.

## Declaration interface

Paths are relative to the JSON declaration. Every input JSON reference has
`path` and `sha256`. The existing `SolventSpecification` TOML owns species,
reaction stoichiometry and reference states, calorics, templates, source CSVs,
observation constructors, residual scales and weights. Its existing input
hash checks remain active. It supplies the data rows; no solvent-specific
Python callbacks are required. The JSON adds:

| Field | Meaning |
|---|---|
| `amine` | Analytical amine component ID. |
| `species`, `vapor_species` | Full Engine component order and neutral vapor support, respectively. |
| `specification` | Existing solvent-specification TOML, including all fitted and comparison rows. |
| `coordinates` | Hashed JSON coordinate declarations accepted by `SolventSpecification.coordinates`: identity, targets or reaction coordinate, origin, scale, bounds. |
| `starts` | Exactly two hashed parameter documents. Each may supply hashed `reactions` (the complete grouped laws) and `coordinates`. EOS origins are transported; reaction origins must match the completed law. Reaction enthalpy coordinates describe increments about that law, with transported total-shift bounds, following `refit_306.py coordinates(H0)`. No completed law is reset. Every complete start is replayed before fitting; out-of-bound origins raise an error and are never clipped. |
| `born_ties` | Amine ion IDs whose Born diameter equals their segment diameter. The route removes independent Born coordinates and adds the Born target to a fitted segment coordinate. Fixed segment diameters remain fixed. |
| `calculation_interval_K` | One interval covering every problem in the specification. Every reaction law and observation uses it; states are never excluded for being outside a source range. |
| `reaction_ranges_K` | Known source limits for named reactions; `null` or an absent limit means source range unknown. A law absent from a problem is marked reaction not used. Inside/outside statistics use only applicable laws with known limits. |
| `covariance` | Optional hashed JSON with `identities` in the exact fitted-row order and the full `covariance` matrix. Use raw difference observations, scale 1, weight 1, as in PZ. |
| `roles` | Optional group-to-role map: `fitted`, `not fitted`, `comparison only`. Objective membership must agree with the specification. Earlier access to observations remains the amine notebook's responsibility. |
| `stocks` | List of analytical feed-amount dictionaries, in mol, for every fitted concentration (water and analytical amine components). |
| `loadings` | Explicit ordered loading nodes in mol CO2 per mol analytical amine, starting at `1e-5` and reaching the data maximum. |
| `split_record` | Hashed initial record with `amine`, `species`, and `trials`. Native split trials have `resolved_descent: true`, native phase `kind`, native index `support`, full-width `composition`, and `packing`. The amine owner must initialize it from its own prior native resolved descents with their provenance. Composition-only historical trials may be included with `resolved_descent: false` (or absent), their provenance, and null or recovered packing; the route preserves them separately as `supplied_trials`. That optional list may also be supplied directly. An empty record is appropriate only when none exists. |
| `curve_rows` | Hashed JSON list, described below. |
| `optimizer` | Existing Engine fit controls, unchanged between continuations. The route supplies the worker count. |
| `output` | Separate retained directory for this immutable declaration. Changing its hash requires a new output directory. |

The replay-only fixture additionally supplies `reference`,
`reference_predictions`, `reference_cost`, and `replay_only: true`.
Frozen replay keeps the historical laws and Born diameter. F2 binding is
exercised separately by the declaration test; replay does not relabel B1 as F2.

273.15–498.15 K is the source-correlation range stated by Austgen 1991 Table V
p.547 (citing Edwards 1978), not verified measured coverage. This is the range
used for shared R1–R3 flags. Amine-specific ranges retain their own source
meaning. Calculation intervals are distinct from both.

## Reused producers and retained outputs

The #255 producer now accepts an optional route in its grid, fit-stage,
admissibility and retreat functions. Existing MEA calls retain their defaults.
Its finite optimized search and penalty stay in `reg.stability`; supplied compositions go to native `eq.stability_test` at the same parent pressure. Both results and their separate availability are retained. Only native resolved descents enter the historical split record. Supplied evaluations use the existing #338 evaluated-negative-distance decision, shared with its census producer; distances and their error estimates remain in the evidence, without relabelling evaluation-only trials as native resolved descents. Unavailable optimized searches remain unavailable even when a supplied negative distance is found. The route records admitted historical
trials per amine and supplies every recorded composition at every subsequent
state. A record with a different amine or component order is refused.

The #255 grid constructor accepts stocks and loading nodes, retaining its
313.15–393.15 K temperature grid in 10 K steps and pressure factors 1.05 and
3.0. Source bubble observations use a liquid parent at 1.05 times its bubble
pressure; prescribed-pressure liquid data keep their declared pressure. Heat
initial/final states and declared phase states are included. Saturation-capped
heat endpoints use the Engine's current `endpoint_loading`; a refused heat
becomes an unavailable search with the native message.

The route calls #338 `candidate` and `fit`, which call the existing #255 fit stage; it has no second continuation or penalty loop. A limit permits two continuations
with unchanged controls. Every returned, replayable endpoint is searched.
A discovered split invokes stages `1e-2` and `3e-3` and the existing #255
retreat, including its 0.01 steps and ten bisections. Optimizer convergence and retreat disposition are separate: the retreat file keeps the fraction, optimizer cost, retreat cost, and whether the selected point itself terminated on an optimizer tolerance. An interpolated point never inherits that termination. Each start keeps all replayable optimizer endpoints in `endpoints.json`, including their optimizer reports and cost histories; stage files retain every continuation. After an unsuccessful penalty or retreat, the converged unpenalized endpoint remains reportable with lower-bound split counts. A nonconverged endpoint retains that disposition and never enters the converged-start choice. The selection file keeps
reportable candidates and chooses the lowest
fitted cost among converged, available starts; costs within the optimizer's
function tolerance are reported as ties. Stability accompanies the choice and never chooses between starts. Unavailable searches retain their state and native cause in `search.grid.unavailable_searches`; no interval is extended and no state is excluded. When there is no observed split, the disposition states “no split found in the available searches; N searches unavailable”. Such a candidate remains reportable without a stable claim. If neither start converges, `chosen` remains null and both endpoints and their cost histories remain in the selection and start records. A finite search gives a
lower bound on split counts, never a proof of global stability.

`report` consumes the selected point. `data-rows.json` keeps native numerical
availability, temperatures, roles, units and every source-range mark.
`deviations.json` separates inside/outside counts for each law, including
available counts, without dropping unavailable rows from coverage counts.
At an observed zero, relative error is undefined; absolute errors and counts retain the row. It reuses the MDEA retained-statistics reduction, moved to its shared owner. Declare dataset `unit` and `basis` for every quantity, including unavailable predictions. Historical declarations without these fields retain their constructor/arguments as basis and use the native unit when a prediction supplies it; absent unit declarations remain explicit rather than being inferred from another row.
`conditional-uncertainty.json` reuses #307's conditional information calculation
with active-bound coordinates held fixed. PZ uses its existing measurement-uncertainty constructor, now shared with `SolventSpecification`: full covariance is preserved in native fitting, replay, and differentiated residuals. Only output sigmas are extended for stability observations; the native covariance matrix spans data observations. Prediction availability and fitted-row ordering are checked before pairing replay residuals with derivative columns. Rank deficiency remains an explicit
numerical error; no finite standard error is invented.

`curve_rows` uses the same observation constructors as data rows. Each entry
has `curve` (series identity), `loading` (mol/mol), `observation` (the ordinary
record), and `problems`: a dictionary from the observation's problem keys to
`{"template": "...", "bindings": {...}}`. These call the specification's
existing template binder and prediction method. `curve-data.json` preserves
series identity, loading, temperature, units, availability and range marks.
Curve observations use a normalization value only to satisfy the Engine
observation constructor; their values are model curves, never measurements
and never part of a data-deviation reduction. Amine notebooks and figures
must consume these retained marks and distinguish curves from observations.

Stage B supplies the two starts, all source rows (including any absent from
an older specification), stocks, loading nodes, historical split record and
curve rows. It also supplies published-model comparisons, measurement
uncertainties, the compact parameter table and summary row, then renders the
requested figures. None of those new MDEA results is claimed by Stage A.


## Data-only adaptation checked at the delegated amine commits

These declarations were inspected, not run as new amine campaigns. Each needs
ordinary JSON/TOML/CSV materialization into the interface above; no new amine
callback is required by the inspected observation constructors.

- **AMP, `c65b2ba`:** turn its dataset and template declarations into the
  solvent-specification file; materialize each hashed complete hydrolysis law
  and its own `coordinates(H0)` chart (retained endpoint H0 = -5000 J/mol,
  second start H0 = 0). Supply identities, units/bases, roles, stocks, loading
  nodes, curve rows, and the amine/species envelope around its own split
  record. Both retained carbamate segment diameters, 5.31999516340193 and
  5.3 Å, are below the F2-moved 5.34799141560911 Å floor. The #344 decision
  projects both starts onto that floor, records the projection, and replays
  each moved start before fitting, preserving other coordinates and each
  completed law. This projection belongs in AMP's declaration; the shared
  calculation raises on out-of-bound origins and never clips them.
- **PZ, `460d00e`:** materialize its two optimizer starts as complete parameter
  and reaction-law documents, preserving the declared total P3–P5 offsets.
  Create the solvent specification for 232 normalized-area NMR observations,
  62 pressure observations and all other role-table rows. Export the full
  normalized-area covariance from `fit_speciation.declarations`, append the
  existing pressure variances, and supply the exact fitted identity order,
  raw difference form, scale 1 and weight 1. Supply chart identities,
  units/bases, source ranges, the 283.15–395 K calculation interval, stocks,
  loading nodes and curve rows. Convert the PZ split compositions to native
  support/composition/packing entries with resolved-descent provenance and
  a PZ/species envelope. The reviewer reproduced the two composition-only
  neighbour compositions exactly, recovering packing fractions
  0.4128283021108707 and 0.41196189417630624. The native supplied evaluator
  also accepts `packing: null`. Preserve the composition-only historical
  provenance: recovered packing values are a reproduction, not invented
  historical fields. Never borrow a MEA composition or relabel a supplied
  evaluation as a native resolved descent.
- **DEA, `294bebc`:** materialize its datasets/templates and role table in the
  solvent specification; export the two complete hydrolysis laws and their
  transported charts, including the second start's declared pair overrides.
  Supply coordinate identities, units/bases, stocks, loading nodes, curve
  rows and the DEA split record. Use its 293.15–458.64 K calculation interval;
  keep the hydrolysis source range unknown, the 273.15–323.15 K dissociation
  range separate, and binary Cai/Horstmann rows marked reaction not used.

Born-target insertion is idempotent, so an amine declaration can already
contain each Born/segment tie without duplicating its native active target.
No Engine capability request is needed for the inspected paths.

## #359 correction evidence

The [verification record](mdea_mea_workflow/results/part-ii-route-replay/issue-359/verification.json)
compares this correction with `a561ab7`: 12 Part II tests pass; the full
`tests analyses` suite retains precisely main's 11 failing test identities
(107 passes versus 103). MDEA B1 reproduces all 278 predictions exactly, with
relative fitted-cost difference 2.7622348852673895e-13. Twelve fitted rows each
from #338 F0 and #341 F2 replay exactly. These are numerical regression checks,
not new fits or physical validation. The PZ test fixture retains the 100
native records' source hashes and JSON pointers and the two composition-only
records separately; both Hilliard reference distances pass within the native
numerical error estimate. The unavailable capped-heat check uses the pinned
Engine and preserves its interval refusal without changing its temperature.

The #359 correction uses 67 gross added executable lines (28 production,
39 test), under the owner’s revised 67-line ceiling. Penalty construction
refusals are retained in `penalized-N/unavailable.json`; they do not prevent
cost-based selection of an already reportable endpoint. Stability never
prioritizes an endpoint over one with a lower fitted cost.
