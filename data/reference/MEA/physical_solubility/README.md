# Physical gas solubility in unloaded aqueous MEA

These data support the neutral CO₂–MEA design for issue #170. They contain
23 measured N₂O Henry constants and 23 corresponding CO₂ physical Henry
constants inferred through the N₂O analogy. The CO₂ values are indirect
estimates, conditional on that analogy. No parameter fit, Engine calculation,
target admission, or physical validation was performed.

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

An engineering choice for amendment 4 is to use Hartono's seven rows and Xu's
eight rows at 24.42 and 36.62 mass% as calibration candidates. This deliberately
widens the near-30% interval to 24–37%; the repository discovery interval is
25–35%. The other eight Xu rows remain concentration-transfer comparisons.
All roles are proposals; existing reactive target membership is unchanged.
There are no extracted measurements above 360.25 K or at exactly 393 K.

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

Reproduce the derived CSV from this directory's source CSVs:

```bash
uv run --no-project python data/reference/MEA/physical_solubility/convert_n2o_henry.py
```

The script's water reference comparison uses Versteeg Table I at 298 K to
check the Henry direction and units. Source PDF files remain in Zotero.
