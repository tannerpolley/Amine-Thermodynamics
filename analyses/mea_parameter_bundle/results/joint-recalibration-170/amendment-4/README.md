# Amendment 4 (#170)

## Outcome (2026-10-18)

- **B1 passes after a vapor-side target correction** (Hartono 2008 Eq. 5
  basis; signed transfer ≤ 0.51 % for rows 1–6, 0.83 % at 360.25 K):
  [b1-vapor-bound](b1-vapor-bound/README.md).
- **Neutral CO₂–MEA pair:** k(313.15 K) = 0.098720, b = −50.989 K; Hartono
  errors −1.41 to +1.32 %: [neutral-fit](neutral-fit/README.md).
- **Matched reacting comparison: null on both d_V branches.** C166 is 0.06 %
  higher with the neutral pair (×1.00059), against the required 10 %
  reduction; same five active bounds in every arm; formally not decidable
  (endpoint free-block condition 3.7e4; fixed-step derivative truncation):
  [larger](matched-larger-dV/README.md), [smaller](matched-smaller-dV/README.md).
- **Defect fixed:** endpoint documents carried R2's ln K constant 211.4 too
  low (88ee4c8); this also caused the Route 2b replay stop.
- **Compute:** ledger 10,532 of 21,600 s and 93,620 of 144,000 CPU-s
  ([compute-ledger.json](compute-ledger.json)); campaign code 1,000 of 1,000
  lines.

The sections below record the earlier preflight stop (16 October), kept for
the record.

## Earlier record: incomplete native-observation preflight

**Stopped before any fit.** The mandatory pressure comparison in amendment 4,
correction R3, could not be specified and verified using an existing supported
Engine declaration for the same Henry quantity, H = p(CO₂)/c(CO₂), at the solvent
bubble reference and at 101325 Pa. No thermodynamic evaluation was launched.
This is an unresolved calculation declaration, not evidence against the neutral
formulation or the N₂O analogy.

Analyze is the starting stage because the accepted amendment authorizes a
bounded observation preflight before calibration. Build required no executable
change. This record preserves the inspection and stopping point; it contains
no fitted or predicted physical result.

## Authority, environment and retained inputs

The task entered the specified worktree and branch
`170-a2-part-1-requalify-84ca269d-shared` at clean commit
`2f37ab9620daa4069fff77b756c8e49e7123fcb8`. Commands ran from that worktree.
The [published amendment 4](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6212553416),
its corrected local design and readiness review r1 were read. The local design
and review hashes are retained in [inputs-check.json](inputs-check.json).
The issue body and complete amendment-4 comment were rechecked during this task.
No new source judgment or claim of rereading the underlying papers is made;
the supplied independent source/data review remains the source-read evidence.

The inspection used `tmp/amendment-2-84ca269d/venv/bin/python`, Engine merged
commit `84ca269dfa0c7068417a1c4c326acae276d4d965`, and wheel SHA-256
`98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`.
The existing `fit_campaign.verify` compared all 12 installed Engine files
byte-for-byte with the wheel and verified every input in the amendment-3
information declaration. The physical-solubility file hashes and the counts
23 retained rows, 15 primary rows and 14 primary states were also recorded.
No source checkout was imported.

The recorded machine check found 32 CPUs and 23336497152 available bytes,
above the inherited 32 × 268435456 = 8589934592-byte estimate. Inspection
commands used `nice -n 10` and single-thread BLAS/OpenMP settings. Thirty-two
workers were admitted by the existing sizing function, but no native numerical
worker calculation ran; an actual 32-worker execution is not claimed.

## Exact pressure-comparison stopping point

Paths below are relative to the verified installed `epcsaft/` directory under
`tmp/amendment-2-84ca269d/venv/lib/python3.13/site-packages/`.

- `equilibrium/problem.py:428`, `bubble_point`, fixes temperature and declares
  pressure free. `Problem` at line 149 supplies one shared pressure. With no
  reactions and zero vapor amount, the liquid composition follows the feed.
  The accepted fixed-temperature, fixed-feed bubble therefore determines its
  own pressure. It was not additionally pinned to 101325 Pa.
- `regression.py:183`, `observation`, supplies `partial_pressure` as solved
  pressure times the selected vapor mole fraction. This supports the proposed
  dilute-bubble pressure observation in principle. It does not by itself
  define the separate pressure comparison required by R3.
- `eos.py:79`, `Mixture.state`, accepts fixed pressure, liquid composition and
  branch. `State.log_fugacity_coefficient` and the native property/action
  exports supply fugacity quantities. A liquid fugacity/concentration quantity
  does not supply partial pressure/concentration without a specified gas
  reference and the corresponding fugacity-to-partial-pressure conversion.
- `eos.py:97`, `Mixture.reference`, takes an ion pair and stoichiometry;
  `reference.py:11` exposes that electrolyte reference. It does not declare
  the required neutral mixed-solvent p/c pressure comparison.
- Inspection of the full observation-kind, state-field, property-observable,
  solved-state-observable and related native export lists found no existing
  declaration completing that comparison. These lists are retained in
  `inputs-check.json`.

No supported declaration with the required liquid composition, gas reference
and conversion was established and verified. A fixed-pressure flash with
free phase amounts would change the prescribed liquid composition; a pure-CO₂
gas reference or an ideal-gas conversion would introduce an unsettled choice.
Neither was substituted. No local generic Henry calculation, Engine edit,
new carrier component, alternate physical model or source-pressure assumption
was introduced.

The exact R3 prerequisite therefore remains open: supply an Engine-owned
calculation declaration and demonstrate that its returned p/c has the same
meaning at both pressures. This inspection does not prove that no such
construction is mathematically possible. The pressure difference has no
computed value; it is not a measured failure of the 1% approximation limit.
Xu Table S3 acquisition was not triggered by an evaluated >1% difference.

The 120 CPU-s thermodynamic-probe allowance was not spent: zero thermodynamic
evaluations ran. The preparation and inspection are still charged separately
in [accounting.json](accounting.json). Dilution at the three epsilon values,
density change, closure, phase identity, centered derivatives, dielectric
invariance and serialized cold replay remain unrun. The explicit R3 stop
returns this declaration gap to the parent/design owner before any fit.

## Requested fit and comparison quantities

| Quantity or check | Amendment-4 outcome |
|---|---|
| Neutral starts A and B | Both unrun after the preflight stop |
| k(CO₂,MEA) at 313.15 K and slope b / K | No estimate; neither starting value is a fitted value |
| Conditional parameter uncertainty, correlation, rank and conditioning | Uncomputed |
| Mean and maximum H error on the 15 primary rows, including each source | Uncomputed; the error falsifier was not evaluated |
| Larger-dV zero control: C₁₆₆ and C₁₄₉ | Both unavailable; no fit endpoint |
| Larger-dV neutral-fixed arm: C₁₆₆ and C₁₄₉ | Both unavailable; no qualified neutral pair or fit endpoint |
| Larger-dV 10% improvement / at-most-1% increase decision | Inconclusive; neither arm ran |
| Larger-dV convergence, active bounds, endpoint conditioning, Kiepe invariance and Cp | All unrun or uncomputed |
| Smaller-dV pair and its decision/checks | Unrun and inconclusive because the prerequisite preflight is incomplete |

The earlier amendment-3 source/seed costs, Kiepe differences and Cp values
are not amendment-4 matched endpoints and were not reused as such. No reactive
call reached admission, so there is no budget-refused arm, elapsed-time fit
vector or partial endpoint. The next authorized reactive call would still
require 44160 CPU-s plus all remaining checks and 1380 active wall-s plus
all remaining checks before launch.

## Ledger, code and delivery limits

The supplied entry is 51427.608914 CPU-s and 11805.510576207005 active wall-s.
This task conservatively charges 100 CPU-s and 600 active wall-s for its
preparation, inspection, reporting, checks and commit. These are reservations
covering this task, not measured Engine computation. The tracked interval and
remaining finish allowance are recorded in `accounting.json`.

The resulting charge is **51527.608914 / 144000 CPU-s**, leaving
**92472.391086 CPU-s**, and **12405.510576207005 / 21600 active wall-s**,
leaving **9194.489423792995 active wall-s**. The unused mandatory-check reserve
remains **17950.44 CPU-s / 1950.38 wall-s**; it is reserved, not charged as
executed work. The historical idle exclusion remains unchanged. Earlier
source/design/review overhead not represented in the supplied entry ledger
was not retrospectively measured or asserted to be zero.

No executable file, test, solver option, fit declaration, source data or
parameter record changed. New executable additions and removals are both
zero; the gross campaign count remains **861 / 900**, and this task uses
**0 / 30** permitted new executable lines. Only this stopping-point report,
input inspection and accounting evidence are delivered. No notebook result
section or figure is created because no useful physical or numerical result
exists. Independent delivered inspection remains with the parent; this is
not a self-issued scientific acceptance or parameter adoption.

No push, merge, GitHub write, subagent, idle answer wait, server action or
Quarto preview-service action occurred. No numerical process remains running.
