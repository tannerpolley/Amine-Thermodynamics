# Published comparison and exploratory coefficient range

Hajj, Pré and Curet (2024), *Dielectric dispersion of 30% aqueous
monoethanolamine solution loaded with CO2 at microwave frequencies*,
[DOI 10.1016/j.molliq.2024.124819](https://doi.org/10.1016/j.molliq.2024.124819),
Table 1, p. 9, supplies the four 353.15 K values in
[inputs/hajj-353K.csv](inputs/hajj-353K.csv). The stock is 30 mass% MEA before
loading. The values are Cole–Cole static-limit estimates inferred from
**915–2450 MHz spectra**, not independently established static-permittivity
measurements. Section 3.3.1, p. 8, and the conclusion, p. 11, warn that the
band does not extend sufficiently low to determine the static limit accurately,
especially at lower temperatures and higher loading. No uncertainty interval
for that inferred limit is supplied. Spectral repeatability below 1% in
section 2.2 cannot be used as the uncertainty of the extrapolated static value.

Live Zotero parent `6EGFRED5`, PDF attachment `DEU5G2C5`, PDF SHA-256
`ffbaa92067f598d8b808a5becc934e62d76748918be57c2de28d59f9af86e30f`.
An independent source investigator verified Table 1 in extracted text and the
rendered PDF page. These are table values; figure digitization is unnecessary.
The original PDF is not redistributed in this public repository.

Figiel et al. (2025), *Predicting Thermodynamic Properties of Ions in Single
Solvents and in Mixed Solvents Using a Modified Born Term within the ePC-SAFT
Framework*, [DOI 10.1021/acs.iecr.5c00475](https://doi.org/10.1021/acs.iecr.5c00475),
section “Dielectric Constant,” equation (11) and Figures 2–3, uses
$\varepsilon=\varepsilon_{solvent}/(1+7.01 x_{ion})$.
The common, dimensionless 7.01 coefficient was correlated for alkali halides
in water and methanol, with ethanol as a comparison solvent, at 298.15 K.
The paper reports neither ion-specific nor solvent-specific parameters,
correlates through ion mole fraction about 0.38, and does not test temperature
transfer. This is an analogy, not a measured MEAH+, carbamate or bicarbonate
coefficient and not validation in loaded MEA at 353.15 K.

The main-checkout reading shelf and its indexed live Markdown hash were
checked. Zotero parent `YEENX35P`, Markdown `2M74BKJG`, supplies the formulation
and limitations read here. The source investigator additionally searched the
Companion corpus, the shelf and live Zotero records, then external literature
for protonated amines, carbamate and bicarbonate dielectric decrement.
No transferable ion-specific coefficient for the composed mole-fraction law
was found. This is bounded search coverage, not proof of absence.
Rueben (2024), Table 1, uses effective ionic permittivities fitted to activity
coefficients; these are different quantities and were not converted into
suppression coefficients. Hasted-type salt concentration slopes use another
basis and likewise were not adopted.

The probe therefore uses the explicitly exploratory symmetric interval
**−10 to +10**, dimensionless, independently for MEAH+, carbamate and
bicarbonate. It brackets the published common value +7.01 with a rounded
outer bound; the negative half has no literature calibration. The initial
trend sweep follows the equal-coefficient diagonal of that interval, with
additional resolution at −2 and +2. The fit frees all three independently;
other ionic coefficients are fixed at zero. No conclusion about every point
in the three-dimensional interval follows from the diagonal sweep. Engine
positivity checks remain active: some negative-coefficient declarations
cannot be evaluated at the solver's intermediate compositions.

Only the 307 adopted Part I observations enter the objective. Hajj's
915–2450 MHz-derived values are comparison-only and carry no fit weight.
