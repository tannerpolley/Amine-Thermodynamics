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

