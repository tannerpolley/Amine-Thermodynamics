# Stage-4 bubble-trial diagnosis for #308

Design evidence, 11 November 2026. No optimization, Engine edit, parameter adoption or hold-out evaluation. The source endpoints are the merged stage-4 evidence at `7885c7c`. The [owner decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/308#issuecomment-6810468221) requires redesign before refitting; consult #308 for the exact comment if its URL changes.

## Finding and limits

**The bubble trial unavailability is reproducibly associated with a liquid-labelled search converging to a gas-density boundary close to the existing vapor. It is not a failed parent bubble solve.** All 62 Hilliard bubble states for each variant contain a successful `near-pure-0` Liquid optimizer whose evidence is `indeterminate`. This is distinct from genuine resolved model splits, which also occur. The audit narrows a numerical phase-search limitation; it does not prove an Engine implementation defect or prove these models physically stable.

[The full 62-state audit](bubble-audit.json) reads existing evidence only, retaining row identities, source hashes, unresolved seeds and resolved split counts. [Bounded probes](probes.json) use frozen A/B parameters on the byte-verified merged Engine wheel `0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b` (Engine `391dfe5d64ede5036bf160bc6ae037ad5e14af32`). The source convention is analytical mol PZ/kg water and mol CO2/mol PZ. No private sources were consulted.

At Hilliard D.5 row 1 (313.127 K), A/B bubble pressures are 7293.797309/7290.949023 Pa. Maximum parent row residuals are 2.42e-13/5.54e-13, against the requested 1e-10. Both liquid-labelled near-pure trials converge in 21 iterations with residuals about 1.04e-14/5.22e-15, but remain indeterminate. Their volumes are 0.356609955/0.356749346 m³/mol, effectively the parent vapor volumes, versus parent liquid volumes about 1.93e-5 m³/mol. Their reduced tangent-plane distances (TPD) are −7.86819e-7/−8.10134e-7. These are not rounded zeros: the reported descent error estimates are about 2.13e-10/3.52e-10 RT. Nevertheless the Engine does not establish a resolved feasible descending split; negative TPD alone cannot override that result.

| Probe, both frozen variants | Observation | What it establishes |
|---|---|---|
| Original Full search, rows 1, 32, 62 | Same near-pure Liquid indeterminacy in all six searches | Reproduced across temperatures/loadings and both representations |
| Row 1 parent tolerance 1e-12 instead of 1e-10 | Indeterminacy persists; pressure changes below 4e-10 Pa | Parent-solve refinement does not explain it; the trial search retains its native tolerance |
| Row 1 liquid trial initialized at parent composition and packing 0.4, same Full search | Indeterminacy persists | This single improved liquid seed does not fix the search; not an exhaustive initialization study |
| Row 1 all-liquid parent at 1.05 and 3 times its own bubble pressure | Four completed searches, no unresolved trials and no descent witnesses | Native #255-style compressed-liquid searches are available at these tested states; not proof for the full PZ domain |
| B rows 32 and 62 at bubble pressure | Resolved dense witnesses, TPD −0.742993 and −0.981877 RT, alongside the indeterminate gas-like trial | Model instability coexists with numerical unavailability; solving the latter cannot qualify B |

The initialization probe leaves Full mode and all default starts enabled. An initial scratch attempt to use supplied-trial evaluation instead produced a missing-vapor-composition diagnostic; that was not a minimization or a test of Full search. The retained probe uses ordinary Full optimization with a supplied liquid guess. No trial is omitted or reclassified. A first script attempt also failed before probing because native reaction-law objects do not support deep copying; the retained script uses the existing shallow-copy convention. Neither setup error is scientific evidence.

The retained counts “62/63 unresolved” refer to source-family reporting in stage 4, not 62 failed bubble solvers. There are 62 pressure rows, each with an indeterminate trial for each variant. Preserve the original phase-family report alongside the row-level audit; categories overlap and some NMR rows repeat source-state conditions. The new probes cover three pressure rows per variant and the first-row interventions only, not a new 366-search campaign.

## Engine use case — draft only, owner files it

**Request:** resolve or explicitly diagnose gas-density boundary trials in Full stability searches of reactive bubble states. Preserve true dense instabilities and honest unavailability. This is a generic Equilibrium responsibility; no local EOS equations, phase-search replacement, tolerance weakening or seed suppression is proposed.

**Exact application declaration:** reproduce `reactive.pressure_problem` on Hilliard D.5 row 1 with `reactive-A-endpoint.json` and `laws_at(reactive-A-fit.json[optimizer])`, then B and rows 32/62. Inputs are committed in `analyses/pz_transfer/`; [probe.py](probe.py) is the bounded reproducer. Twelve liquid species and eight reactions; feed `{piperazine:1, water:1/(0.0180153*mPZ), carbon-dioxide:alpha_per_PZ}`; free positive pressure with original guess `10000+pCO2_kPa*1000`; liquid support all species; pinned-zero vapor support water/CO2/PZ with composition guess 0.5/0.4999/0.0001. Original reaction reference and molality ratios, row tolerance 1e-10. Solve the declared parent, compile it, then call `stability_test` with Full `StabilityOptions`, trial Liquid/all species and Vapor/water+CO2+PZ. Do not use phase discovery with free pressure: the installed interface explicitly refuses free-intensive discovery.

**Consumed quantities:** parent pressure (Pa), phase amounts (mol), compositions and densities (mol/m³), row residuals and tolerance admission; each trial's kind/support/seed, optimizer termination reason, evidence, TPD/RT, donor slope/capacity, reconstructed split and its Gibbs change/error, trial volume, uncertainty estimates and availability cause. The application needs a finite-search disposition usable by final bubble-state assessment; a successful termination is insufficient. #255 fitting additionally consumes the raw minimum descending TPD and its exact coordinate derivatives through `reg.stability`; unavailable searches must fail the evaluation.

**Acceptance:** replay the declared parents and their partial pressures within the existing stage-4 numerical refinement/replay tolerances (parent row criterion 1e-10; compare prediction differences separately from measurement scales). At rows 1/32/62 either resolve all requested searches or expose the precise remaining numerical cause; a still-indeterminate result is useful diagnosis but does not unblock PZ acceptance. Distinguish duplicate/vapor-boundary minima from feasible new phases using native numerical error and feasibility checks, not an application TPD cutoff. Preserve B's row-32/62 dense witnesses and the original first-NMR A/B dense witnesses (−0.133516/−0.846990 RT) within reported numerical uncertainty. Preserve first-row compressed-liquid available/no-witness behavior and charge/material balance. Retain all seeds and uncertainty meanings. Qualify any merged replacement wheel by SHA-256 before using it; no candidate wheel establishes final PZ evidence.

**Routing:** the owner may file this use case with the reproducer and frozen inputs. No Engine issue was filed in this task. Full bubble acceptance remains blocked until the Engine-owned disposition is adequate. Compressed-liquid penalties can be qualified independently, but they cannot stand in for bubble-state searches.

## Reproduction

Run from this checkout, using the verified installed wheel (the script checks every installed Engine file against its wheel):

```bash
agent-heavy /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python analyses/pz_transfer/diagnosis-308/probe.py
```

The absolute interpreter/wheel paths record this machine's diagnostic environment; the script imports no Engine source. The output is numerical verification of frozen model behavior, not physical validation, and gives no solid-phase assurance.
