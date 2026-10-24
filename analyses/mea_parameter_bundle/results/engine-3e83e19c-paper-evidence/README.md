# Engine 3e83e19c paper evidence: stopped at the code preflight

**No new calculation was dispatched and no record was adopted.** The draft
implementation measures 122 gross added executable lines against
`74bb89a45987e0f1062edbcc32c723b8d20fcfde`, exceeding issue #215's ceiling of
100. The stop occurs before the first assessment mode. These files retain
the upstream gate checks and the unfinished implementation; they are not a
complete paper-evidence package.

## Upstream gates

[Gate verification](gate-verification.json) retains 880 input/output hash
checks: 284 for #212, 54 for #213 and 542 for #214. The checks use the exact
recorded producer revisions where appropriate. All three issues are merged in
the base commit. The pinned wheel's SHA-256 is
`0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`;
all 12 installed Engine files equal that wheel's bytes. No Engine source
checkout was imported.

- #212: 44 of 47 loaded densities lie within twice the assigned scale. The
  miss IDs are exactly the three permitted IDs, so the required subset check
  passes. The largest absolute CO₂-free density error is
  0.557484452458425 kg/m³, below 1 kg/m³.
- #213: all six unrounded limits pass for this candidate. Their values,
  margins and exact input hashes remain in the upstream `limits.json`.
- #214: the reported record has zero descending trials at all 162 states,
  with complete state evidence. The comparison has 54 descent states and
  143 descending trials. Both fits return all 1458 trials each.

These are retained calibration statistics and finite-search numerical
verification results. They do not establish physical validation, global
stability, predictive transfer or process-use qualification. This preflight
adds file-identity verification, not another thermodynamic evaluation.

## Inventory at the stop

No displayed data file has been produced or imported into this directory.
The complete displayed-input inventory therefore remains unverified. No
non-3e83e19c Engine-computed display input has been accepted here; this is
not a claim that the current paper's inputs are free of older Engine results.
The existing paper generators still retain their historical bindings, owned
by #211.

The following upstream inputs have verified hashes in
`gate-verification.json`; every Engine calculation listed here used
`3e83e19ccc771b51d8ebc038931ab25192f4c5b5` and the pinned wheel above:

| Upstream directory under `results/` | Verified files needed by the issue | Producing Engine |
|---|---|---|
| `engine-3e83e19c-refit-chain/` | Reported and comparison endpoints, declarations, native results, replays, scores, permittivity rows/summary, Arcis and Cai results, conditional uncertainty | 3e83e19c |
| `engine-3e83e19c-density-free/` | `limits.json`, `parameters.csv`, their input and output hashes | 3e83e19c; limits are arithmetic reductions |
| `engine-3e83e19c-phase-search/run-2/` | `phase-family.csv`, `reference-pressures.csv`, `states.csv`, `trials.csv`, `split-confirmations.csv`, numerical checks and provenance | 3e83e19c |

**Earlier selected-record dependency:** #212's and #213's retained calculations
read the selected record through the old helper default, but their provenance
does not list that input. The emitted Engine calculation inputs were proven
identical with each supplied record. See
[the #214 dependency account](../engine-3e83e19c-phase-search/run-2/README.md)
and its `earlier-dependency.json`. The #213 hashes for `shared_evaluation.py`
and `heat_evidence_170.py` were verified at its merged commit
`4e5e5f599c0a14253cae00fbbc7e87a34eee0de9`; #214 subsequently changed those
files. Neither issue was rerun.

Source-only density scales, source-density interpolation, literature values,
source caloric coefficients and nomenclature have not been changed. Their
complete displayed-input inventory has not been assembled.

## Execution and adoption

[Execution](execution.json) has no calculation calls and no transient units.
No preview service was controlled and no notebook was rendered. There is no
new useful numerical calculation to add to the research notebook; its adopted
record and reported values remain unchanged.

| Required step, in order | Result at the stop |
|---|---|
| Assessments | 0 of 6 modes; 0 newly evaluated rows |
| Assessment reduction | Not run |
| Package point-data reduction | Not run |
| Comparison density export | 0 of 47 rows exported |
| Water display | 0 of 42 states evaluated |
| #212 display imports | Not run |
| Model curves | 0 of 5 families; no curve states evaluated |
| Package inventory | Upstream hashes checked; displayed-input inventory incomplete |
| Adoption | Not performed |
| Consumer updates | Not performed |

The new 307-row replay identity comparison has not run. Assessment and curve
completeness are unestablished. The upstream 307-row replay was inspected only
for density-gate reduction and input identity; it is not the required new
replay. No completeness or identity check has been weakened.

The selected record remains byte SHA-256
`e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e`.
The unadopted candidate is
`engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json`,
SHA-256 `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`.
Active consumers and the three historical commands have not been changed or
pinned. Manuscript sources and generators are unchanged. Independent delivered
review has not run; the implementation has not been accepted.

## Measured code and remaining issue requirements

[Change accounting](change-accounting.json) measures the final tree against
the base. Its filename classifier calls the two executable `.py.txt`
producers documents; they are explicitly included in the issue's code count:

| Changed executable responsibility | Gross additions |
|---|---:|
| Explicit mappings in `shared_evaluation.py` | 15 |
| Explicit mappings in `calibration-misfit/probe.py` | 2 |
| Explicit mappings in `fit_observations.py` | 4 |
| Assessment producer, including paths and worker sizing (`assess.py.txt`) | 11 |
| Assessment reducer, including limits and Cp availability (`reduce.py.txt`) | 12 |
| Package point-data bindings (`reduce_a7_evidence.py`) | 22 |
| Curve bindings, repeated-grid comparison and complete availability (`model_curves.py`) | 12 |
| Comparison-density export and water display (`paper_displays_215.py`) | 44 |
| **Total** | **122** |

This is already 22 lines over the ceiling before the remaining replay-identity
check, display imports, complete inventory, consumer changes, historical
command pins and notebook update. Deletions do not offset gross additions.
No copied driver is excluded, and no persistent test was added.

The draft code was not executed or numerically verified. It does not yet
implement every requirement. In addition to the unexecuted steps above, the
remaining issue work includes complete timing/input bindings, strict checking
of all assessment identities, the independent 307-row replay, separate old/new
curve availability comparison, bubble-pressure completeness, and all required
water summary/display imports. A continuation needs an owner decision on the
code ceiling or an implementation reduced within it before calculations.
