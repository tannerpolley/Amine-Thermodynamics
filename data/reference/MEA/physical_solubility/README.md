# Physical gas solubility in unloaded aqueous MEA

These data support the neutral CO₂–MEA design for issue #170. They contain
23 measured N₂O Henry constants and 23 corresponding CO₂ physical Henry
constants inferred through the N₂O analogy. The CO₂ values are indirect
estimates, conditional on that analogy. No parameter fit, target admission,
or physical validation was performed. The later mole-fraction extension below
is accompanied by separately retained native calculation evidence.

## Source measurements and coverage

| File | Rows | Temperature / K | Gas-free MEA mass fraction | Primary locator |
|---|---:|---|---|---|
| `Hartono_2014_N2O_solubility.csv` | 7 | 298.35–360.25 | 0.30 | Hartono 2014 Table 11 p.1813; SI Table S2 PDF p.10, Loading=0.00 |
| `Xu_2018_N2O_solubility.csv` | 16 | 293.15–323.15 | 0.12208545, 0.24418628, 0.36619575, 0.48838927 | Xu and Wang 2018 Table 8 p.2715, x₂-only block |

Hartono has six distinct temperatures and a repeat at 312.65 K: 22 distinct
temperature/composition states in total. The 4.79 value with superscript 10 in
Hartono Table 11 belongs to Browning and Weiland; it is not included. Hartono
SI values are additional fields on the same seven observations, not seven
additional observations. Loaded rows, 6.2 mass% rows, and Xu ionic-liquid
mixtures are outside this extraction. Xu's N₂O table ends at 323.15 K even
though its title and density/viscosity measurements extend to 333.15 K.

The 16 October Hartono-only disposition makes the seven Hartono observations at gas-free MEA mass fraction 0.30 the sole primary neutral calibration candidates, subject to source-basis and numerical qualification. All 16 Xu rows remain conditional comparisons until Table S3 and its pressure/gas reference are checked. This supersedes the earlier proposal to fit eight Xu rows at 24.42 and 36.62 mass%. No reacting target membership changes. There are no extracted measurements above 360.25 K; extension toward 393 K remains extrapolation.

`sources.json` records obtained PDFs, parent and attachment keys, SHA-256
hashes, locators, reading scope, and the missing Hartono 2013 PDF. Hartono's
supplement was acquired as a distinct Figshare source item; its deposited-file
year says 2016, while its parent article is 2014. Both identities are preserved.
The four table/equation pages were rendered and checked against their PDF
text layers. The tables did not require Mathpix or figure digitization.

## Conversion and assumptions

Source convention: $H=p/c$, in Pa m³ mol⁻¹; concentration is dissolved gas
per liquid volume. Hartono reports kPa m³ mol⁻¹, converted by multiplying by
1000. Temperature uses $T=t+273.15$. MEA fractions exclude gas.

For Xu's gas-free solvent mole fraction $x$, the mass conversion is

$$
w=\frac{xM_{\rm MEA}}{xM_{\rm MEA}+(1-x)M_w}. \tag{N2O-1}
$$

The masses, 0.06108 and 0.01801528 kg mol⁻¹, are the existing stage-2
parameter document's component `molar_mass` values. They are conversion
constants, not newly estimated properties.

**Literature practice:** Xu 2018 Eq.1 p.2708 uses

$$
H_{\rm CO_2,s}=H_{\rm N_2O,s}
\frac{H_{\rm CO_2,w}}{H_{\rm N_2O,w}}. \tag{N2O-2}
$$

Its reference 18 is Versteeg and van Swaaij 1988. Their Eqs.4–5 p.30 give
the inverse Henry coefficients, $HE=c/p$, in mol m⁻³ Pa⁻¹:

$$
HE_{\rm CO_2,w}=3.54\,10^{-7}\exp(2044/T),\qquad
HE_{\rm N_2O,w}=1.17\,10^{-7}\exp(2284/T). \tag{N2O-3}
$$

The selected conversion is therefore

$$
H_{\rm CO_2,s}=H_{\rm N_2O,s}
\frac{1.17}{3.54}\exp(240/T). \tag{N2O-4}
$$

**Explicit analogy assumption:** the physical concentration-solubility ratio
CO₂/N₂O in unloaded aqueous MEA equals the corresponding ratio in water.
This estimates nonreacting molecular CO₂ solubility; it does not measure
reactive total CO₂ capacity. Versteeg's cited direct analogy check in its
introduction p.29 concerns MDEA and the combined mass-transfer quantity;
it does not establish an MEA uncertainty distribution.

Versteeg Eq.6 instead prints the rounded solubility ratio
$C_1=3.04\exp(-240/T)$. Its inverse yields CO₂ H values 0.47233468% below
Eq.N2O-4. The alternative is retained as `H_CO2_using_Eq6_Pa_m3_per_mol`;
it is not a second observation. Using the exact printed Eqs.4–5 ratio is an
explicit engineering convention pending independent review. Do not silently
mix these alternatives. Tables I–II p.30 support water measurements over
roughly 291–360 K (N₂O maximum 359.4 K). Conversion of the highest Hartono
point at 360.25 K is a slight extrapolation; this source does not qualify
extension to 393 K.

## Uncertainty and data use

Hartono Table 11 gives expanded uncertainty 0.03 kPa m³ mol⁻¹, coverage
factor 2, confidence 0.95. Its printed composition uncertainty has unit kg
despite using the symbol w₁; retain this ambiguity and do not interpret it as
a dimensionless standard uncertainty. Xu Table 8 gives expanded uncertainty
51 Pa m³ mol⁻¹ at confidence 0.95, with no coverage factor stated. Its
composition standard uncertainty is 0.0002 in mole fraction. Temperature
and pressure uncertainties are retained per row.

Multiplying expanded H uncertainty by the analogy ratio propagates only the
N₂O measurement component. Analogy, water-correlation, preparation,
temperature and composition uncertainties are not thereby quantified.
Campaign and repeat groups remain explicit. Source disagreement must be
reported by source, without averaging independent campaigns into one value.
The derived CO₂ range is 2787.9155–8667.2022 Pa m³ mol⁻¹ across all 23 rows.

**Repository policy:** source extraction does not admit fitting targets.
Independent data and design review, frozen row roles and residual scales,
and immutable input binding precede calibration. Neither extraction nor
calibration residuals establish independent physical validation.

`CO2_physical_from_N2O.csv` retains the conversion of the two source CSVs using Eqs.N2O-1–N2O-4. Temperature, pressure units, source values and the Eq.6 alternative are retained explicitly. This delivery contains no executable conversion script. Versteeg Table I at 298 K provides a printed water reference for checking the Henry direction and units. Source PDFs remain in Zotero.

The derived CSV was verified against Eqs.N2O-1–N2O-4 in the [amendment-4 independent readiness review, r1, §1](/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/tmp/joint-design/amendment-4-readiness-r1.md), 16 October 2026. This delivery preserves those reviewed values.

## Mole-fraction Henry basis for the dilute neutral bubble

The 16 October addendum appends a mole-fraction basis to the same 23 derived
rows. Existing fields and row identities are preserved. The transformation
uses measured unloaded mass densities, rather than the stage-2 model density.
It does not change the N₂O analogy or admit new fitting observations.

`unloaded_solution_density.csv` contains 24 measured mass densities with
source keys, PDF hashes, locators, pressure statements and uncertainties:

- Hartono 2014 Table 3 p.1810, own unloaded 30 mass% values without reference
  superscripts: 1010.55, 1008.31, 1003.45, 998.07, 992.23 and 985.96 kg/m³ at
  25, 30, 40, 50, 60 and 70 °C. Section 2.2 p.1809 states atmospheric
  pressure. Its seven Henry observations require interpolation in temperature.
- Xu 2018 Table 4 p.2711, MEA-only block: the 16 densities at the exact
  Table 8 temperatures and compositions. These are 993.8–1025.7 kg/m³;
  the table states 101000 Pa. No composition or temperature interpolation
  is used for Xu.
- The Hartono 87.1 °C row lies above its own density table. Use Karunarathne
  et al. 2020, DOI 10.3390/fluids5010013, Table 3 PDF p.5, own values at
  30 mass% with no reference superscript: 979.4 and 972.3 kg/m³ at 80 and
  90 °C. Linear interpolation gives 974.359 kg/m³ at 87.1 °C. Sections 2.2
  and 3 describe the vibrating-tube method and uncertainty. This is a
  measured-density source from a different campaign, with measurement
  pressure unreported; the 4 bar statement in §2.3 concerns viscosity.

The three density-table pages were visually checked against the Zotero PDFs;
their current hashes match `sources.json`. No density correlation or
extrapolation supplies these values. For bracketing measurements at fixed w,
the explicit interpolation is

$$
f=(T-T_0)/(T_1-T_0),\qquad
\rho_m(T,w)=(1-f)\rho_m(T_0,w)+f\rho_m(T_1,w). \tag{N2O-5}
$$

Here $\rho_m$ is mass density in kg/m³. The molar density of the gas-free
solution and the limiting Henry constant on a mole-fraction basis are

$$
c_{\mathrm{total},0}=\rho_m
\left(\frac{w}{M_{\mathrm{MEA}}}+\frac{1-w}{M_w}\right)
\quad [\mathrm{mol/m^3}], \tag{N2O-6}
$$

$$
H_x=H_c c_{\mathrm{total},0}\quad [\mathrm{Pa}],\qquad
U_{H_x,\mathrm{N_2O\ only}}=
c_{\mathrm{total},0}U_{H_c,\mathrm{N_2O\ only}}. \tag{N2O-7}
$$

These are MEA-owned basis identities: $c_{\mathrm{CO_2}}=x_{\mathrm{CO_2}}
c_{\mathrm{total}}$ and $H_c=p/c_{\mathrm{CO_2}}$, with the gas concentration
tending to zero. The molar masses remain those of Eq.N2O-1. The derived
columns retain both density bracket identities and f. Across all 23 rows,
$c_{\mathrm{total},0}=36660.2868$–50999.3137 mol/m³ and
$H_x=120998548.9$–369615034.3 Pa. The 360.25 K Hartono row has
$c_{\mathrm{total},0}=42645.2535$ mol/m³. These are converted source estimates,
not new CO₂ measurements.

The source density uncertainties remain separate: Hartono reports expanded 0.02 kg/m³, k=2; Xu reports standard 1 kg/m³. Karunarathne's rendered Table 3, PDF p.5, reports expanded 7.10 kg/m³, k=2, at 95% confidence for its aqueous-MEA density table. Section 3, PDF p.3, separately reports 7.80 kg/m³ for CO₂-loaded solutions. Record 7.10 kg/m³ with the Table 3 density rows and retain the distinct loaded-solution statement in the source notes. The table value is about 0.73% of the interpolated 974.359 kg/m³; it is not a quantified uncertainty for the interpolation or the difference between campaigns. The appended Hx uncertainty column propagates only the original N₂O H uncertainty and excludes density, composition, interpolation, water-ratio and analogy uncertainty. No combined uncertainty or statistical independence is asserted.

The conversion does not establish the Henry measurement's reference pressure.
Xu Table S3 remains unread. The Companion supplement request returned the
existing main article; the exact supplement URL in its Zotero snapshot
returned HTTP 403. The atmospheric density measurement must not be called
the Henry measurement pressure. The addendum's pressure estimate to 101325 Pa
is conditional on that declared reference and its stated gas reference.

## Hartono source representations and selected primary basis

Hartono Table 11 Hc multiplied by the measured gas-free molar density exceeds the matching SI Table S2 pN₂O/xN₂O by 0.85368–3.09128% across the seven unloaded observations. The discrepancy occurs within Hartono's own density campaign as well as at 360.25 K. The conversion arithmetic is verified, but equivalence of the two source representations is unresolved. Keep the Table 11-derived values and SI fields unchanged as candidate evidence; do not silently replace one with the other or treat them as separate observations. Before fitting, establish the source concentration/volume convention or resolve the source inconsistency and document which representation supports the intended limiting Henry target. The 5% residual scale and the pressure-only 1% check do not resolve this discrepancy. Until that source-basis check is complete, retain the existing stop on unresolved source basis.

Orchestrator decision, 2026-10-16 (owner away): select Hartono SI Table S2 direct pN₂O/xN₂O as the primary Hartono Hx basis for this conditional design. It already uses mole fraction, so no density conversion is needed. Apply the unchanged N₂O-to-CO₂ water ratio of Eq.N2O-4 to that direct ratio. Retain the Table 11 Hc-derived values and SI fields unchanged as candidate evidence on the same seven observations. Report their 0.85368–3.09128% difference as a source-representation difference; the source's concentration/volume convention remains unresolved. This explicitly adjudicates the representation used for the proposed calibration without asserting equivalence of the source tables. The selected SI basis does not transfer Table 11's Hc uncertainty: its uncertainty is unquantified here, and 0.05 remains an engineering residual scale. Source pressure/gas-reference qualification and the outstanding numerical checks still block fitting.

For the same Hartono observation, the selected transformation is

$$
H_{x,\mathrm{N_2O},\mathrm{SI}}=\frac{1000P_{\mathrm{N_2O},\mathrm{kPa}}}{x_{\mathrm{N_2O}}},\qquad
H_{x,\mathrm{CO_2},\mathrm{SI}}=H_{x,\mathrm{N_2O},\mathrm{SI}}
\frac{1.17}{3.54}\exp(240/T)\quad[\mathrm{Pa}]. \tag{N2O-8}
$$

Hartono SI Table S2 PDF p.10 supplies the pressure in kPa and the mole
fraction (its printed column is $10^4 x_{\mathrm{N_2O}}$); the water ratio
is Eq.N2O-4, from Xu Eq.1 and Versteeg Eqs.4–5. This is an analogy-derived,
finite-source-pressure candidate target. Selecting this representation does
not establish its limiting or source gas-reference equivalence.

The derived CSV appends `H_N2O_SI_mole_fraction_Pa`,
`H_CO2_SI_mole_fraction_Pa`, `Table11_over_SI_relative_excess`,
`H_CO2_primary_mole_fraction_Pa`, `primary_Hx_basis`,
`primary_Hx_uncertainty` and `neutral_log_ratio_weight`. The first two
and the relative difference are populated only for Hartono. The existing
`H_CO2_physical_mole_fraction_Pa` and `U_Hx_from_N2O_only_Pa` remain the
Table 11 Hc-times-density representation for Hartono; neither is the selected
primary SI target or its uncertainty. The direct-SI primary CO₂ range is
151298904.50–358676232.10 Pa. The seven Hartono rows have six temperature
groups; each group has total weight $1/[6(0.05)^2]$, split equally between
the two 312.65 K repeats. All 16 Xu primary-target fields are empty and their
fitting weights are zero; their existing density-derived values remain
conditional comparisons. These weights describe the proposed objective,
not admission to fitting. No new observations are created.

The retained dilute-bubble preflight's numerical values, target replays and
`primary` labels describe the earlier Table 11 density-based, two-source
proposal. Preserve those results as historical evidence; use the corrected
row roles and explicitly selected basis for any later qualified inputs.

The retained 0.416577% liquid and 0.695049% combined pressure estimates
change the model bubble pressure to 101325 Pa under the assumed volume
envelope and fixed bubble-vapor composition. They do not establish transfer
from Hartono's N₂O gas reference. Its SI pressures are partial pressures;
total pressure and gas-fugacity transfer remain unqualified. All seven
Hartono source mappings and the nonzero pair require the original ≤1%
combined source-transfer check within the remaining preflight allowance.
Otherwise the no-fit stop remains. All 16 Xu rows remain conditional
comparisons with zero fitting weight until Table S3 is verified.
