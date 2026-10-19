# MEA Density and Viscosity Extraction Targets

This folder retains source-resolved density and viscosity measurements extracted from literature Markdown or the identified source PDF.

Initial source:

- `docs/papers/md/Amundsen et al. - 2009 - Density and viscosity of monoethanolamine + water + carbon dioxide from (25 to 80) °C.md`

Required columns are defined in `data/reference/MEA/manifests/source_status_manifest.csv`.

Do not add estimated or fabricated rows.

## Hartono 2014 loaded densities (19 October 2026)

`Hartono_2014_loaded_density.csv` retains 40 own loaded density measurements
from Hartono, Mba and Svendsen, *J. Chem. Eng. Data* **59**, 1808–1816,
DOI `10.1021/je401081e`, Table 3 p.1810 (PDF p.3). The source is Zotero
parent `5VGPDVGB`, PDF `L7SKR73P`, SHA-256
`c085678a27172f0f9875d194cda6de18403753743fdf97a76b49384857bec196`.
The PDF hash was verified; its layout text and rendered p.1810 were checked.
The task worktree has no `literature/` shelf. The main checkout's shelf and
index were inspected; they contain Amundsen 2009, but no Hartono Markdown
entry. Hartono was therefore read directly from the identified Zotero PDF.

### Own measurements and comparison rows

At each of 20, 25, 30, 40, 50, 60, 70 and 80 °C, the first row has no
reference superscripts. Those eight rows supply five loaded values each,
at printed α = 0.11, 0.19, 0.29, 0.39 and 0.50 mol CO₂/mol MEA.
The additional cells have superscripts identifying references, rather than
additional Hartono experiments. The references on p.1815 identify:

- Superscript 2: Han, Jin, Eimer and Melaaen (2012), density of water–MEA–CO₂,
  *J. Chem. Eng. Data* **57**, 1095–1103.
- Superscript 3: Amundsen, Øi and Eimer (2009), *J. Chem. Eng. Data* **54**,
  3096–3100, DOI `10.1021/je900188m`.
- Superscript 5: Weiland, Dingman, Cronin and Browning (1998), *J. Chem.
  Eng. Data* **43**, 378–382.

Section 3.1 p.1809, first paragraph, identifies Tables 2, 3 and A1 as the
authors' measured density results. Table 5 p.1811 independently identifies
the 30 mass % campaign at 20–80 °C as this work and separates the literature
campaigns. Figure 2's caption on p.1811 distinguishes this work from
references 2, 3 and 5. Only the unsuperscripted Table 3 cells are adopted.
No comparison cell is copied into the new observations.

The own unloaded column is 1012.68, 1010.55, 1008.31, 1003.45, 998.07,
992.23, 985.96 and 979.27 kg/m³ in increasing temperature order. All six
Hartono records already in `../../physical_solubility/unloaded_solution_density.csv`
(25–70 °C) match exactly. The 20 and 80 °C unloaded cells are reported here
for the cross-check; they are not new rows in that file or the loaded CSV.

### Composition definitions and unresolved loading values

Section 2.1 p.1808, the paragraph beginning with aqueous-solution
preparation and continuing at the top of the right column, says that MEA
and deionized water were mixed on a mass basis, and that CO₂ was then bubbled
into the unloaded aqueous MEA. Loading was first estimated from weight
change; the BaCl₂ method (reference 15) and acid–base titration (reference 16)
then verified the CO₂ and MEA concentrations. This preparation sequence
supports interpreting the reported 30 mass % as MEA/(MEA + water) before
CO₂ addition. It does not provide individual prepared masses or unrounded
loading analyses for the Table 3 columns.

Table 3 footnote a p.1810 explicitly defines α = nCO₂/nMEA in mol CO₂/mol
MEA and calls the parenthesized values mole fraction x₃. Section 3.1's
heading p.1809 identifies MEA (1), water (2), CO₂ (3). Section 3.2 p.1812,
the paragraph following Eq.9, describes added CO₂ by its mole fraction in
solution. Thus x₃ is an apparent component mole fraction; no measured
free-molecular-CO₂ or species-fraction definition is supplied. The identical
loading/x₃ pairs recur in Table 7 p.1812, so that table does not independently
adjudicate them. Equation 4 p.1809 uses α and component mole fractions in
the added-CO₂ mass fraction, but supplies no unrounded compositions or
correction to Table 3.

For a CO₂-free solvent containing W = 7.911062165 mol water per mol MEA
(the task's declared 30 mass % arithmetic basis), component mole balance gives

$$
x_3=\frac{\alpha}{1+W+\alpha},\qquad
\alpha_{x_3}=\frac{x_3(1+W)}{1-x_3}.
$$

| Printed α (mol/mol) | Printed x₃ | Derived α from x₃ (mol/mol) | Derived minus printed α |
|---:|---:|---:|---:|
| 0.11 | 0.0130 | 0.117369613116 | 0.007369613116 |
| 0.19 | 0.0215 | 0.195797482420 | 0.005797482420 |
| 0.29 | 0.0328 | 0.302194829417 | 0.012194829417 |
| 0.39 | 0.0431 | 0.401365638323 | 0.011365638323 |
| 0.50 | 0.0544 | 0.512649938426 | 0.012649938426 |

The source supports the definition and printed values of α, but does not
establish which numerical representation describes the actual compositions.
Rounding, a different prepared composition or a transcription error cannot
be selected as the cause from these passages. Preserve both representations;
the derived values are conditional arithmetic, not corrected measurements.
The common `co2_loading_mol_per_mol_mea` column retains printed α.
`co2_loading_source_supported_mol_per_mol_mea` is empty because no unique
resolution is source-supported. Every row has
`loading_basis_status=printed_alpha_and_x3_inconsistent_unresolved` and
`lifecycle_status=blocked_pending_source_review`. Independent source/data
review and an explicit loading/uncertainty decision are required before
fitting. No fit target, split, weight or parameter has been added.

### Uncertainties and units

Table 3 p.1810 footnote b prints:

> Uncertainty: u(t) = ± 0.02 °C, u(ρ) = ± 0.02 kg·m⁻³, u(α) = ± 0.01 mol CO₂/mol MEA, and u(w₁) = ± 2·10⁻⁵ kg.

Footnote c prints:

> Expanded uncertainty: U(ρ) = ± 0.02 kg·m⁻³ (level of confidence = 0.95 where k = 2).

Both u(ρ) and U(ρ) are retained exactly, including their equal numerical
values. No factor-of-two repair or choice of a standard density uncertainty
has been made. The source prints kg for u(w₁); it is not silently converted
to a mass-fraction or relative uncertainty. Section 2.2 p.1808, the density
apparatus paragraph, separately reports repeatability ±0.01 °C and
±0.01 kg·m⁻³, no vapor phase and atmospheric pressure. These repeatabilities
do not replace the Table 3 uncertainties. No numeric atmospheric pressure,
x₃ uncertainty, covariance or propagated uncertainty for derived α is given
by the cited table and passages.

The CSV keeps the Amundsen columns, with additional fields for source
identity, reported x₃, alternative loading, composition basis and explicit
uncertainties. `value` and `uncertainty_value` retain kg/m³;
`uncertainty_type=as_printed_u_absolute`. `density_g_cm3` and
`density_uncertainty_g_cm3` divide those values by 1000 to give the g/cm³
units used in the Amundsen file. Thus 0.02 kg/m³ becomes 0.00002 g/cm³.
`temperature_K=temperature_C+273.15`; the temperature uncertainty is 0.02 K.
The `density_expanded_uncertainty_*` fields retain U(ρ), its unit, k = 2 and
confidence 0.95. `co2_loading_absolute_uncertainty_mol_per_mol_mea=0.01`
applies to the reported α, not automatically to α derived from x₃.
`mea_mass_fraction_uncertainty_reported` and its unit retain 0.00002 kg.
Relative-uncertainty fields and Markdown line-number fields are empty where
they do not apply. Each row has its own temperature/loading locator, the
PDF identity and the Table 3 uncertainty locator.

### Arithmetic comparison with Amundsen 2009

Linear interpolation at each temperature uses Hartono's own unloaded point
at α = 0 and the five own loaded points. This is required at α = 0.1,
which lies below the first loaded point. No temperature interpolation or
extrapolation is used. For adjacent loadings αᵢ and αᵢ₊₁,

$$
\rho_H(\alpha)=\rho_i+
\frac{\alpha-\alpha_i}{\alpha_{i+1}-\alpha_i}(\rho_{i+1}-\rho_i).
$$

Amundsen's original 30 mass % density observations are used, converting
g/cm³ to kg/m³ by multiplication by 1000. Their source is Table 3 p.3097,
with the CO₂-free solvent basis stated in the experimental section p.3097.
The reading-shelf Markdown matches its indexed and current Zotero companion
SHA-256 `4b585de0d9d73a1f7ac142882cdbafeaa37d780c36f795f40bac627b1d7ec1ce`.
No Amundsen observation or uncertainty has changed. These differences are
arithmetic comparisons, without uncertainty propagation or physical
validation. The alternative-x₃ column is a sensitivity calculation using
the conditional loadings above; it is not a second set of observations.

| t (°C) | α target (mol/mol) | Amundsen − Hartono, printed α (kg/m³) | Amundsen − Hartono, α from x₃ (kg/m³) |
|---:|---:|---:|---:|
| 25 | 0.1 | 0.795455 | 1.841190 |
| 25 | 0.2 | 1.004000 | 2.332617 |
| 25 | 0.3 | 1.446000 | 3.693004 |
| 25 | 0.4 | 9.074545 | 11.247044 |
| 40 | 0.1 | 0.795455 | 1.847469 |
| 40 | 0.2 | 0.963000 | 2.292222 |
| 40 | 0.3 | 1.296000 | 3.543211 |
| 40 | 0.4 | 8.849091 | 10.997044 |
| 50 | 0.1 | 1.084545 | 2.142268 |
| 50 | 0.2 | 0.678000 | 2.010247 |
| 50 | 0.3 | 1.564000 | 3.814242 |
| 50 | 0.4 | 8.504545 | 10.647319 |
| 70 | 0.1 | 0.912727 | 1.988145 |
| 70 | 0.2 | 0.768000 | 2.112347 |
| 70 | 0.3 | 1.365000 | 3.628368 |
| 70 | 0.4 | 8.736364 | 10.868559 |
| 80 | 0.1 | 0.420909 | 1.507743 |
| 80 | 0.2 | 0.702000 | 2.056027 |
| 80 | 0.3 | 1.348000 | 3.621668 |
| 80 | 0.4 | 8.959091 | 11.089523 |

The printed-α comparison confirms +0.420909 to +1.564000 kg/m³ at
α = 0.1–0.3 and +8.504545 to +9.074545 kg/m³ at α = 0.4. Using the
x₃-derived alternative changes those ranges to +1.507743 to +3.814242
and +10.647319 to +11.247044 kg/m³, respectively. The choice of loading
representation therefore affects the comparison and remains a review gate.

### Adopted fitting basis (owner decision, 2026-10-19)

Independent source review (GPT-6.1 Sol, 2026-10-19) of commit `f2d6f82` found the 40-row transcription, the own-row identification and the library changes correct. It also found that the source cannot decide between the two loading readings:

- **(H1) The x₃-derived loadings are the real ones.** The printed α would then be low by 0.0058–0.0127, which is 0.6–1.3 times the stated u(α) = 0.01. A common loading offset of about 0.00715–0.01126 reconciles all five columns within printing precision.
- **(H2) The printed α is right,** and the solvent was not exactly 30 mass %. Allowing both printed quantities their rounding, one common solvent composition W′ = 7.5959–7.7126 mol water/mol MEA, i.e. **30.54–30.86 mass % MEA** on a CO₂-free basis, reproduces all five x₃ values. Without that rounding, the five columns imply different compositions, 30.6–31.6 mass %. Calling it the titrated concentration would be an inference; the paper reports no titration numbers.
- **Density consequence:**
  - *H1:* at the observed slopes of 179–224 kg/m³ per unit α, the loading shift is worth about 1.2–2.5 kg/m³.
  - *H2:* compared with a true 30 mass % solution, about +0.9 to +2.3 kg/m³, using finite differences of ∂ρ/∂w between Amundsen's 30 and 40 mass % tables.
  - Both effects far exceed the printed u(ρ) = 0.02 kg/m³.
- **Correlation check:** the paper's density correlation (Eqs. 3–5) does not reproduce Table 3 closely enough to adjudicate (0.74 % average absolute relative deviation in a literal check, against the reported 0.13 %).

**Adopted for fitting** (owner, #170):
- **Basis:** the printed α with the nominal 30 mass % CO₂-free solvent (W = 7.911062165). This is the authors' reporting convention and an **adopted assumption**, not a uniquely resolved composition.
- **Residual scale:** each row combines u(ρ) = 0.02 kg/m³ with u(α) = 0.01 propagated through ∂ρ/∂α, s² = u(ρ)² + (∂ρ/∂α · u(α))², about 1.8–2.2 kg/m³.
- **Sensitivity:** the H1/H2 ambiguity is a separate, possibly systematic effect shared across each temperature series. It is assessed by rerunning the selected candidate on the x₃-derived loadings, which stay in `co2_loading_from_mole_fraction_mol_per_mol_mea`.

**Row status.**
- Loadings 0.11–0.39 (32 rows): `property_target_candidate`.
- Loading 0.50 (8 rows): `validation_only`.
- `co2_loading_source_supported_mol_per_mol_mea` stays empty, because no unique source-supported loading exists.

## Han 2012 (assessment-only)

`Han_2012_loaded_density.csv` retains 67 measured densities at 30 mass %
MEA on a CO₂-free basis: 50 loaded cells from Table 4 p.1098 (PDF p.4)
and 17 unloaded cells from Table 3 p.1097 (PDF p.3). The source is
Jingyi Han, Jing Jin, Dag A. Eimer and Morten C. Melaaen (2012),
“Density of Water (1) + Monoethanolamine (2) + CO₂ (3) from (298.15 to
413.15) K and Surface Tension of Water (1) + Monoethanolamine (2) from
(303.15 to 333.15) K”, *J. Chem. Eng. Data* **57**, 1095–1103,
DOI `10.1021/je2010038`. Zotero parent `X8GZTAGN`, PDF attachment
`BEZB6G4U`, PDF SHA-256
`14d8a6b065889dddd06a21c736df2dacee86201bd624b0bb5f6282a1af5f8a92`.
The task worktree has no literature shelf; the main checkout's reading
index has no Han entry. The identified Zotero PDF was read directly.

### Transcription and checks (19 October 2026)

The selected temperature interval is the model's 293.15–393.15 K domain.
Han prints no 30 mass % density at 293.15 K. Table 4 contributes every
cell at 298.15, 313.15, 323.15, 333.15, 343.15, 353.15, 363.15,
373.15, 383.15 and 393.15 K, with five printed loadings at each
temperature: α = 0.10, 0.21, 0.32, 0.44 and 0.56 mol CO₂/mol MEA.
Each loading therefore has ten rows. Table 3 contributes one unloaded
cell at each of those ten temperatures and at 303.15, 308.15, 318.15,
328.15, 338.15, 348.15 and 358.15 K. Thus the first set of temperatures
has six rows each and the latter set has one each. Values above 393.15 K,
other MEA concentrations, excess volumes and surface tensions are outside
this extraction.

The PDF was extracted with `pdftotext -layout` and pages were rendered
with `pdftoppm` into a new empty directory under `tmp/`. All 50 Table 4
density cells, their temperature/loading headers and pressure column, and
all 17 selected Table 3 density cells and headers were checked visually
against the rendered pages. The methods on p.1096 and uncertainty table
and prose on p.1102 were also visually checked. Every row records
`checked_against_rendered_page=yes` and `visual_check_date=2026-10-19`.
All 67 CSV density values also agree with the layout-text extraction;
no selected cell was unreadable or ambiguous.

The 18 Han cells in commit `128b299`,
`analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-6/source-conflict/third-source-values.csv`,
were cross-checked by temperature and printed loading. All 18 densities,
temperatures, loadings, pressures and PDF identities match exactly;
there are zero disagreements. That earlier comparison file is not a
second set of measurements.

### Composition, loading and pressure

Table 4 footnote a p.1098 explicitly defines w₂ as the mass fraction of
MEA in the water + MEA solution. Its title defines α = nCO₂/nMEA.
The Experimental Section pp.1095–1096 describes degassing MEA and water,
preparing solutions by weighing, bubbling CO₂ into unloaded solution,
and analyzing the highly loaded solution by BaCO₃ precipitation and
titration. The precipitate was dissolved with HCl to pH 2, then excess
HCl was determined by NaOH titration to pH 5.27. Unloaded and highly
loaded solutions were mixed to obtain the loading series (p.1096,
left column). The CSV preserves the printed loadings; it does not
reconstruct individual sample analyses or infer unrounded loadings.
The unloaded Table 3 row prints w₂ = 0.3 and x₂ = 0.1122; it has no
printed α. Its loading field is blank, with `system=binary` and an
explicit unloaded note (zero CO₂).

Table 4's pressure column and Table 3 footnote a report 0.1 MPa through
363.15 K and 0.7 MPa from 373.15 K upward. The CSV converts these to
100 and 700 kPa. The Experimental Section p.1096 identifies the
oscillating U-tube instruments as Anton Paar DMA 4500 through 363.15 K
and DMA HP at higher temperatures, the latter operated under pressure
to restrain evaporation and CO₂ desorption.

### Reported uncertainties and CSV conventions

The “Assessment of the Experimental Uncertainties” pp.1101–1102 and
Table 12 p.1102 report:

- Combined density uncertainty of 1.3 kg/m³ for loaded solutions over
  the whole temperature range, with expanded uncertainty 2.6 kg/m³ at
  confidence 0.95 (p.1102, paragraph beginning “Similar to the previous
  calculations”).
- Combined density uncertainty of 0.34 kg/m³ below 373.15 K and
  0.35 kg/m³ at or above 373.15 K for unloaded solutions, with expanded
  uncertainties 0.68 and 0.70 kg/m³, respectively, at confidence 0.95
  (p.1102, first paragraph). Table 12 places 0.70 kg/m³ beside the
  loaded-solution label; the prose explicitly assigns it to unloaded
  solutions at or above 373.15 K. This extraction follows that prose.
- Temperature uncertainty 0.03 K below 373.15 K and 0.05 K at or above
  373.15 K; MEA mass-fraction uncertainty 0.005; loading uncertainty
  0.003 mol CO₂/mol MEA; instrument density accuracy 0.05 kg/m³ below
  373.15 K and 0.1 kg/m³ at or above 373.15 K (Table 12).

The paper's prose says the combined density uncertainty includes
temperature, mass fraction, instrument error and, for loaded solutions,
loading. These contributions are retained separately as source metadata;
they are not added to the combined uncertainty again. The source states
confidence 0.95 but does not explicitly state a coverage factor in these
passages; the coverage-factor column is blank. No covariance, new
residual scale or fitting weight is assigned.

The file follows the Hartono CSV's column names where applicable.
`value` and `value_unit` preserve the printed density and kg/m³ unit;
`density_kg_m3` repeats the density in the requested normalized unit,
and `density_g_cm3` divides by 1000. `uncertainty_value` retains the
combined density uncertainty with `uncertainty_type=combined_absolute`;
the expanded uncertainty and confidence have separate columns.
`temperature_printed` and `temperature_unit_printed` retain kelvin;
`temperature_C=temperature_K−273.15`. Mass-fraction uncertainty is
dimensionless and absolute. The loading uncertainty is populated for
loaded rows only. Unreported x₃, alternative loadings, relative
uncertainties, coverage factors and Markdown line numbers remain blank.
Each row retains its source table/page, temperature/loading locator,
Zotero keys and PDF hash. The Amundsen-specific column definitions describe
their own source; they are not extended to imply identical units or uncertainty
definitions for Han.

### Relation to Amundsen 2009 and adopted use

Han and Amundsen share Dag A. Eimer and the Porsgrunn/Telemark research
group (Han p.1095 author affiliations; Amundsen p.3096 author
affiliations). Both describe CO₂ saturation, mixing with unloaded
solution, BaCO₃ precipitation/titration and DMA 4500 density
measurements (Han p.1096; Amundsen Experimental Section pp.3096–3097).
They should not be described as independent laboratories. Amundsen's
30 mass % Table 3 p.3097 uses α = 0.1–0.5 and 298.15–353.15 K,
with the highest-loading high-temperature cells absent. Han's Table 4
uses α = 0.10–0.56 and 298.15–413.15 K, and adds DMA HP measurements
at 0.7 MPa. Their reported loading uncertainties also differ:
Amundsen estimates 2 % (p.3096), while Han gives an absolute
0.003 mol/mol (Table 12 p.1102). The Amundsen reading copy used here
matches both its shelf index and current Zotero Markdown attachment
`6ZD3H493`, SHA-256
`4b585de0d9d73a1f7ac142882cdbafeaa37d780c36f795f40bac627b1d7ec1ce`.
These passages do not establish the cause of the density disagreement.

The owner decision of 19 October 2026 in
[#170 comment 6278610430](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6278610430)
adds Han as assessment-only comparison evidence and removes the five
Amundsen loading-0.4 rows from the fitted objective and gate because
Hartono and Han contradict them there. This records the supplied owner
decision; it does not change Amundsen observations or implement objective
changes. Every Han row, including unloaded rows, has
`lifecycle_status=validation_only`: no row is a fit target or gate.
The status is an assessment role, not a claim of physical validation.
No Engine calculation, fit, interpolation or new density comparison was
performed for this adoption.

