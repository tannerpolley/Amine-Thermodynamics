# MDEA–CO₂–H₂O preparation for issue 222

Stage 1 is retained with unresolved completion criteria. Stage 2 has not started.
The useful results are the pure-MDEA association-volume conversion, the
30-point dielectric fit, eight-species admission for both ion conventions,
and the two-column pressure sensitivity probe. These are numerical preparation
and calibration evidence, not a physical validation or a transfer verdict.

The [notebook](notebook.qmd) records quantities, interpretation and limits.
[Input hashes](inputs/hashes.json) identify calculation inputs, source tables,
and the reused MEA methods. [Runtime identity](inputs/runtime.json) verifies
installed package files against the immutable wheel. [Source provenance](../../data/reference/MDEA/stage1-sources.json)
owns source keys, PDF keys/hashes, locators, units, bases, uncertainties,
transcription hashes and remaining source gaps. No source observations change role.

| Item | Disposition | Retained evidence and remaining criterion |
|---|---|---|
| (a) Ten transcriptions | Incomplete | Ten files, 338 observations in total: Hsieh 24; corrected Kamps 28; Jakobsen 8; Böttinger 58; Carson 40; Weiland Cp 39; Weiland density 44; Sobrino 24; Kim 61; Merkley 12. The loaded-density uncertainty is not established; no scale assigned. Merkley plateau values lack individual finite-loading/pressure coordinates. |
| (b) Association volume | Incomplete | [Summary](results/kappa/summary.json): κ = 0.11800686; pressure AARD 1.34914%, saturated-liquid density AARD 0.00525150%, against the source model, not experiments. The 21 source-model saturation solves meet 10⁻¹⁰ residual tolerance. S1 describes the method but supplies no explicit MDEA AARD threshold; numerical conversion is retained without inventing that threshold. |
| (c) Ideal gas | Incomplete | [PDF units check](results/ideal-gas-units-check.json): Eq. 26 in the PDF itself has the apparent missing-temperature factor. No dimensional interpretation or alternate cited polynomial has been adopted. No polynomial/anchor completion claimed. |
| (d) Dielectric coefficients | Complete | [Summary](results/dielectric/summary.json): 0.8630669729 L/mol and 1121.773473 K; 30 measurements, AARD 3.86106%; native replay error 1.42 × 10⁻¹⁴. Above 328.15 K this is an extrapolation assumption. |
| (e) Admission | Incomplete | [A](results/admission-A.json), [B](results/admission-B.json): both parameter documents admitted, both unloaded and loaded liquid states evaluated, all Helmholtz terms retained. Full caloric admission remains contingent on (c). No variant was refused. |
| (f) CO₂ coordinate | Complete | [Probe summary](results/probe-summary.json), [A columns](results/probe-A-columns.csv), [B columns](results/probe-B-columns.csv). Both raw sensitivity norms favor MDEAH+–CO₂. Unit-column normalization removes the magnitude ranking, so both raw norms and normalized columns are retained explicitly. No joint coordinate was fitted or changed. |
| (g) Original reaction basis | Blocked | [Interim comparison](results/reaction-basis-interim.json): Jakobsen Table 1 differs from Uyan Table 1 by −0.002679 ln K at 298.15 K; Uyan gives pKₘ = 8.54994. The unavailable Kamps–Maurer paper is still required. |

The ten transcriptions contain 338 observations (including twelve figure points),
not 338 admissible fitting targets. Figure-point uncertainty and source
uncertainty remain distinct. Repeated source rows and suspect values remain.
Derks Table 1 reports “room temperature,” without a numerical temperature;
it remains unscored. Its concentration basis is kmol/m³ in an initially
2 kmol/m³ MDEA solution (PDF 5467GXJK, p.5, printed p.603).

## Reproduction

Use `/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I`
with the worktree script path. Run numerical scripts with `nice -n 10`.
There is no worktree environment and no source-checkout runtime import.

Run, in order:

1. `scripts/transcribe.py`, then `scripts/digitize_merkley.py` for the ten source tables.
2. `scripts/prepare.py` for the association conversion and installed-wheel identity check.
3. `scripts/dielectric.py` to fit the two dielectric coefficients and finalize both start-1 documents.
4. `scripts/source_checks.py` for the ideal-gas units and interim reaction-basis checks.
5. `scripts/admission_probe.py`, then `scripts/probe_summary.py`.
6. `scripts/numerical_checks.py 0.001` for the centered derivative check, then `scripts/shared_reference_checks.py`.
7. `scripts/retain_inputs.py` to verify identities and retain the source-table snapshots and input hashes.

The digitizer uses the installed CSE XY helper, unchanged; its hash is in
`inputs/merkley-calibration.json`. OpenCV 5.0.0.93 was installed only under
`/tmp/mdea222-deps`, outside either environment; reproduce that disposable
helper dependency with `uv pip install --target /tmp/mdea222-deps --no-deps opencv-python-headless==5.0.0.93`.
The source page images were rendered by `pdftoppm` at the commands recorded
in the calibration and units records; they are retained, not regenerated by fitting.
`numerical-checks-1e-4.json` preserves the initial small-step derivative
check. At that step the small B neutral derivative had relative error
1.2774 × 10⁻⁵. At 10⁻³ it is 1.1071 × 10⁻⁶; the other three derivatives
also meet 10⁻⁵. This is consistent with cancellation in the smaller difference;
it does not establish a defect in the exact native derivative.

The saturation functions and native observation/coordinate declarations reuse
`mea_association_volume.py`. Pressure observations and exact coordinate
differentiation use the declarations in `fit_observations.py`; no optimizer
is invoked by the probe. The dielectric reduction follows
`fit_campaign.py::stage5_study`, extended from its single-temperature linear
reduction to least squares for two coefficients across the six Hsieh temperatures.
The density and permittivity equations are replayed by the installed library.

Before stage 2: resolve (a), (b), (c), (e), and (g), obtain delivered evidence
review, then obtain the owner's issue comment freezing roles, scales, weights,
bounds and starts. The nine-coordinate fits, three starts per variant,
outside-fit assessments, phase searches, identifiability profiles and
sensitivity/control refits are all stage-2 work. Neither the MEA record nor
the manuscript has been changed. No Zotero writes, push, or merge occurred.
