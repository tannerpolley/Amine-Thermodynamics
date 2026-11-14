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
| `starts` | Exactly two hashed parameter documents. A start may also supply its own hashed `coordinates`; EOS origins are transported to that start. Reaction origins and total-shift bounds belong to the declaration. |
| `born_ties` | Amine ion IDs whose Born diameter equals their segment diameter. The route removes independent Born coordinates and adds the Born target to a fitted segment coordinate. Fixed segment diameters remain fixed. |
| `calculation_interval_K` | One interval covering every problem in the specification. Every reaction law and observation uses it; states are never excluded for being outside a source range. |
| `reaction_ranges_K` | A pair of limits for every named reaction, including each amine-specific law from the Part II range table. |
| `roles` | Optional group-to-role map: `fitted`, `not fitted`, `comparison only`. Objective membership must agree with the specification. Earlier access to observations remains the amine notebook's responsibility. |
| `stocks` | List of analytical feed-amount dictionaries, in mol, for every fitted concentration (water and analytical amine components). |
| `loadings` | Explicit ordered loading nodes in mol CO2 per mol analytical amine, starting at `1e-5` and reaching the data maximum. |
| `split_record` | Hashed initial record with `amine`, `species`, and `trials`. Each trial has `resolved_descent: true`, native phase `kind`, native index `support`, full-width `composition`, and `packing`. The amine owner must initialize it from its own prior native resolved descents with their provenance. An empty record is appropriate only when none exists. |
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
Its finite search admits only native resolved descents, evaluates supplied
trials, and reports unavailable searches separately. The route records those
trials per amine and supplies every recorded composition at every subsequent
state. A record with a different amine or component order is refused.

The #255 grid constructor accepts stocks and loading nodes, retaining its
313.15–393.15 K temperature grid in 10 K steps and pressure factors 1.05 and
3.0. Source bubble observations use a liquid parent at 1.05 times its bubble
pressure; prescribed-pressure liquid data keep their declared pressure. Heat
initial/final states and declared phase states are included. Saturation-capped
heat endpoints use the Engine's current `endpoint_loading`; a refused heat
becomes an unavailable search with the native message.

Each fit uses the existing #255 fit stage. A limit permits two continuations
with unchanged controls. Every returned, replayable endpoint is searched.
A discovered split invokes stages `1e-2` and `3e-3` and the existing #255
retreat, including its 0.01 steps and ten bisections. The selection file keeps
all starts, their convergence and stability counts, and chooses the lowest
fitted cost among converged, available starts; costs within the optimizer's
function tolerance are reported as ties. The retained fit attempts contain
cost histories when convergence is not reached. A finite search gives a
lower bound on split counts, never a proof of global stability.

`report` consumes the selected point. `data-rows.json` keeps native numerical
availability, temperatures, roles, units and every source-range mark.
`deviations.json` separates inside/outside counts for each law, including
available counts, without dropping unavailable rows from coverage counts.
It reuses the MDEA retained-statistics reduction, moved to its shared owner.
`conditional-uncertainty.json` reuses #307's conditional information calculation
with active-bound coordinates held fixed. Rank deficiency remains an explicit
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
