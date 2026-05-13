# Goal: Implement MEA-Thermodynamics Issue #3 Native Regression Delegation

## GitHub Issue

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/3

## Objective

Implement issue #3 in MEA-Thermodynamics strictly: MEA becomes the data, target-construction, artifact, validation, approval, and manuscript evidence repository. MEA must stop owning production ePC-SAFT parameter optimization loops and must delegate production fitting to the ePC-SAFT native regression API, then consume structured package fit results for artifacts and manuscript claims.

## Carbonate Context

Current promoted carbonate values remain regularized at:

- `HCO3- d_born = 3.0`
- `CO3^2- d_born = 3.0`

Current unanchored trace-only diagnostic found a lower residual near:

- `HCO3- d_born = 6.80294`
- `CO3^2- d_born = 2.99744`

MEA must not promote that alternative from trace-only evidence. Promotion requires coupled pressure/speciation native regression evidence and approval gates.

## Non-Goals

- Do not implement production optimization algorithms in MEA.
- Do not use SciPy optimizers for production ePC-SAFT fitting.
- Do not vendor, clone, or hide an ePC-SAFT package copy inside MEA.
- Do not reopen ePC-SAFT issue #52 unless Scout/Judge evidence proves package API work is actually required.
- Do not promote carbonate Born values from trace-only evidence.
- Do not manually edit `docs/latex/references.bib`.

## Source Anchors

- MEA repo: `C:\Users\Tanner\Documents\git\MEA-Thermodynamics`
- Correct issue: `https://github.com/tannerpolley/MEA-Thermodynamics/issues/3`
- Plan: `docs/ePC-SAFT/carbonate-global-regression-resolution-plan.md`
- Trace diagnostic: `analyses/epcsaft_ionic_regression/results/trace_carbonate_born_regression/trace_carbonate_born_fit_summary.json`
- Current package dependency: sibling `C:\Users\Tanner\Documents\git\ePC-SAFT`

## Completion Proof

A final PM/Judge audit must show:

- Issue #3 requirements were inspected and mapped to concrete MEA changes.
- MEA production regression path no longer imports or calls SciPy optimizers.
- MEA builds and serializes native regression target problems with stable row/source/split/species metadata.
- MEA calls the ePC-SAFT native regression API when available and consumes package result status/metrics/bounds/residuals as the source of truth.
- Approval gates prevent promotion on nonconverged package status, bound artifacts, incomplete rows, or trace-only carbonate improvements.
- Tests and quick validation pass.
- Manuscript language no longer uses vague `package_fit_not_completed` / other package-specific nonconverged statuses claims once native fit results exist; nonconverged results use specific package statuses.

## Starter Command

```powershell
cd C:\Users\Tanner\Documents\git\MEA-Thermodynamics
/goal Follow docs/goals/issue-3-native-regression-carbonate/goal.md.
```

