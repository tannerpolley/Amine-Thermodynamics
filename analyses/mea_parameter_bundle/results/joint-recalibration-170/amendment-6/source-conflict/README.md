# Loaded 30 mass % MEA density: third-source comparison

Research evidence gathered 19 October 2026 for #170 amendment 6. These are
comparison values, not adopted observations. No Engine calculation, parameter
fit, source selection, observation edit, or GitHub write was made.

The two requested third sources give **split evidence at α = 0.4**. Han 2012
is closer to Hartono at every temperature shared with Amundsen: Han − Hartono
is +1.43 to +2.84 kg/m³, whereas Han − Amundsen is −7.53 to −6.23 kg/m³.
The reduction in absolute difference from choosing Hartono as the comparator
is 3.39–6.11 kg/m³. At 25 °C, Weiland 1998 instead gives 1095 kg/m³, only
0.70 kg/m³ below Amundsen and 8.37 kg/m³ above Hartono, so it is closer to
Amundsen by 7.67 kg/m³. Han is a separate reported measurement series from
the same Eimer research group as Amundsen; it shares the low-temperature
instrument type and closely related chemical analysis. Weiland supplies a
separate group and measurement method, but only at 25 °C, with incomplete
loaded-solution uncertainty information. These two sources do not establish
one unanimously supported density series.

At α = 0.3, Han is closer to Amundsen at all five shared temperatures,
although both comparators are much nearer than at α = 0.4. Thus the Han
comparison also identifies the larger separation specifically above α ≈ 0.3.
The meaning is a disagreement among reported experimental series, with
conditional interpolation between measurements. This is neither an ePC-SAFT
prediction nor physical validation of a parameter record.

## Source identities and reading checks

Zotero storage root: `/home/tnnrpolley21/Zotero/storage/`. Each PDF below was
read from its attachment directory and identified by SHA-256. The DOI and
journal locator identify the publication; the hash identifies the local copy.

| Source | Publication | Parent / PDF attachment | PDF SHA-256 |
|---|---|---|---|
| Han, Jin, Eimer & Melaaen 2012 | *J. Chem. Eng. Data* **57**, 1095–1103; DOI `10.1021/je2010038` | `X8GZTAGN` / `BEZB6G4U` | `14d8a6b065889dddd06a21c736df2dacee86201bd624b0bb5f6282a1af5f8a92` |
| Weiland, Dingman, Cronin & Browning 1998 | *J. Chem. Eng. Data* **43**, 378–382; DOI `10.1021/je9702044` | `CTSDNKZK` / `U4KFM6ST` | `c057c98684fba6cc13f8090eb357fc017745d61325af623bb99e1e0bc8dea03e` |
| Hartono, Mba & Svendsen 2014 | *J. Chem. Eng. Data* **59**, 1808–1816; DOI `10.1021/je401081e` | `5VGPDVGB` / `L7SKR73P` | `c085678a27172f0f9875d194cda6de18403753743fdf97a76b49384857bec196` |
| Amundsen, Øi & Eimer 2009 | *J. Chem. Eng. Data* **54**, 3096–3100; DOI `10.1021/je900188m` | `3QJR6RHH` / `NGQVTDX7` | `a6525dde4e8b0e74902ebbe1d8c6e3f246cee36be9ae5409e32669750f409d4e` |

The worktree has no `literature/` shelf. The main checkout's
`literature/README.md`, index, and relevant Amundsen reading copy were read.
The Amundsen Markdown attachment `6ZD3H493`, indexed copy, and current source
all have SHA-256
`4b585de0d9d73a1f7ac142882cdbafeaa37d780c36f795f40bac627b1d7ec1ce`.
The other three requested papers lack indexed Markdown reading copies, so
their original PDFs were used. Companion's read-only capability check worked;
the project density search added no exact evidence beyond these sources.

Actual reading relevant to this comparison:

- Han: pp.1095–1099 and 1101–1102 (PDF pp.1–5, 7–8), including preparation,
  Table 4, comparison discussion, uncertainty assessment, Table 12, and
  conclusions. Tables 4 and 12 and the methods on p.1096 were also checked
  as rendered pages. The reported correlation errors were read as description
  of the authors' work; the correlation was not evaluated here.
- Weiland: pp.378–379 (PDF pp.1–2), the density method, preparation, Table 3,
  and density-correlation discussion on p.380; the later discussion and
  conclusions on pp.381–382 were inspected in text. The retained Table 3
  values and p.378 method were checked as rendered pages.
- Hartono: pp.1808–1811 (PDF pp.1–4), the loading representation on p.1812,
  and the conclusions/references on pp.1814–1815. Table 3 p.1810, Fig.2 and
  Table 5 p.1811 were checked as rendered pages; Table 3 was enlarged to
  distinguish superscripts from digits in `1010.63³`.
- Amundsen: methods pp.3096–3097, density discussion pp.3097–3098, combined
  uncertainty pp.3099–3100, and conclusions p.3100, using both the verified
  Markdown and PDF text. Methods and Tables 1/3 on pp.3096–3097 were checked
  as rendered pages. The combined-uncertainty passages on pp.3099–3100
  were also checked as rendered pages.

PDF text was extracted with `pdftotext -layout` into a newly created empty
scratch directory, `tmp/source-conflict-Kw6rmf/`. Rendering used `pdftoppm`.
All Python was run with `python3 -I`. Paper text was treated as data.
Scratch text/images are temporary and are not retained scientific inputs;
the exact PDF identities, checked values, and locators are retained here.

## Han 2012: values, preparation, and uncertainty

Table 4 p.1098 (PDF p.4) explicitly defines the nominal MEA mass fraction
as MEA/(water + MEA), excluding added CO₂. Loading is
α = nCO₂/nMEA. All requested temperatures are at printed p = 0.1 MPa.
The table prints temperature in K and density in kg·m⁻³. There are six
in-scope temperatures: 298.15, 313.15, 323.15, 333.15, 343.15, and 353.15 K
(25, 40, 50, 60, 70, and 80 °C). Within 0.25 ≤ α ≤ 0.55 the complete
set of columns is α = 0.32 and 0.44. The α = 0.21 column is also retained
because it brackets the α = 0.3 target. The table's α = 0.10 and 0.56
columns are outside the requested loading interval and are not needed for
the target interpolations.

| t (°C) | α = 0.21 | α = 0.32 | α = 0.44 |
|---:|---:|---:|---:|
| 25 | 1053.4 | 1075.6 | 1096.4 |
| 40 | 1046.4 | 1066.9 | 1089.1 |
| 50 | 1041.2 | 1061.3 | 1083.8 |
| 60 | 1035.6 | 1055.6 | 1078.2 |
| 70 | 1029.7 | 1049.6 | 1072.3 |
| 80 | 1023.4 | 1043.4 | 1066.0 |

All entries above are kg/m³ and were checked cell by cell against the rendered
Table 4. `third-source-values.csv` retains these 18 cells with printed units,
temperatures, pressure, source identity, and locators.

Han's Experimental Section pp.1095–1096 reports Merck MEA (initial mole
fraction purity 0.995), Milli-Q water, rotary-evaporator degassing of MEA
and water **before mixing**, approximately 0.5 kg samples, and balance
accuracy ±10⁻⁷ kg. CO₂ was bubbled at 0.150 NL/min into an unloaded
solution. The highly loaded stock was analyzed by BaCO₃ precipitation and
titration, then mixed with unloaded solution to obtain the loading series.
The analysis used 0.05–0.1 g samples, 41.7 mL of 0.3 M BaCl₂ and 50 mL
of 0.1 M NaOH, boiling for 4–5 min, filtration, redissolution in degassed
water, acid titration to pH 2, and back-titration to pH 5.27.

For these 25–80 °C comparisons Han used an Anton Paar DMA 4500, calibrated
with air and water. Its DMA HP at ≥373.15 K and 0.7 MPa is outside this
comparison; Han describes that high-pressure instrument as restraining
MEA evaporation and CO₂ desorption (p.1096). It would be incorrect to
attribute the present 25–80 °C differences to the DMA HP.

The experiments are reported as new measurements rather than copies of
Amundsen's values, but complete experimental independence is not established:
Eimer and the Telemark/Tel-Tek group are shared, as are the DMA 4500 instrument
type and the precipitation/titration approach. Distinct reported details
include Milli-Q water and pre-mixing degassing, a specified CO₂ flow, a
smaller analytical sample, and endpoint pH 5.27 rather than Amundsen's 5.3.
The papers do not identify a common stock batch or prove that the physical
instrument was different. These procedural differences alone do not diagnose
the density disagreement.

Table 12 p.1102 and its assessment on pp.1101–1102 give u(T) = 0.03 K
below 373.15 K, u(w₂) = 0.005, instrument accuracy 0.05 kg/m³ in that
range, and u(α) = 0.003 mol CO₂/mol MEA. The text gives combined density
uncertainty 1.3 kg/m³ and combined expanded uncertainty Uc(ρ) = 2.6 kg/m³
at 95% confidence for **loaded** solutions over the whole temperature range.
The 0.68 kg/m³ expanded uncertainty is for unloaded solution and is not
substituted for loaded uncertainty. Han says loading analysis dominates the
loaded uncertainty. No covariance or uncertainty for a linearly interpolated
value is supplied. Han's p.1098 comparison with Weiland reports a maximum
12 kg/m³ deviation and calls it acceptable; that is the authors' assessment,
not a new acceptance threshold for this comparison.

## Weiland 1998: values, preparation, and uncertainty

Table 3 p.379 (PDF p.2), block **30 mass % MEA**, prints:

| α (mol/mol) | ρ (g/mL as printed) | Converted ρ (kg/m³) |
|---:|---:|---:|
| 0.25 | 1.065 | 1065 |
| 0.30 | 1.073 | 1073 |
| 0.35 | 1.085 | 1085 |
| 0.40 | 1.095 | 1095 |
| 0.45 | 1.106 | 1106 |
| 0.50 | 1.117 | 1117 |

These are all the source's loaded-density cells in the requested loading
interval. All six were checked against the rendered page. The Experimental
Section p.378 states all measurements were at 25 °C; there are no 40–80 °C
measurements to compare and no temperature interpolation is made. The
α = 0.3 and 0.4 targets are exact tabulated nodes. The complete series runs
from α = 0 to 0.5, so α = 0.4 is inside its range; α > 0.5 would be
outside it.

Weiland describes a stock amine solution of known concentration, saturation
of part of it by CO₂ bubbling at 1 atm through a sintered-glass Dreschel
head, then mixing saturated and reserved unloaded portions at fixed
amine/water ratio (p.378). This preparation supports the CO₂-free solvent
mass basis, rather than an inclusive MEA/(MEA + water + CO₂) basis. Both
amine concentrations and loadings of single-amine solutions were checked
using the titrimetric method of Weiland & Trass 1969. Individual analytical
results and loading uncertainties are not printed in this paper. The 1 atm
value is the stock carbonation pressure, not an explicitly specified
measurement-cell pressure; the latter remains unreported here.

The density method is a hydrometer, calibrated against distilled water,
pure amines, and NaCl solutions at 25 °C (Experimental Section p.378).
The paper says unloaded densities were within ±0.1% of literature values;
this is a calibration comparison, **not a stated combined uncertainty for
loaded density**. The ±0.2% repeat-measurement precision in the neighbouring
paragraph applies to viscosity, not density. No density/loading coverage
factor or combined loaded uncertainty is supplied. The density table's
printing increment is 0.001 g/mL (1 kg/m³), not an uncertainty estimate.

The experimental text calls the measured quantity more precisely specific
gravity, while Table 3 and the density equations label it g/mL. This comparison
uses the table's printed density convention, multiplying by 1000 exactly;
no water-reference correction is imposed. A fully specified specific-gravity
reference and conversion is not provided in the inspected method. That limits
precision of interpretation, particularly the apparent 0.70 kg/m³ agreement
with Amundsen. Weiland remains numerically closer to Amundsen under the
printed convention; no claim of sub-kg/m³ physical agreement is made.

## Same-temperature arithmetic

The comparison operation is linear interpolation within each source's own
loading series, identified here as C1:

$$
\rho_s(\alpha,T)=\rho_s(\alpha_i,T)
+\frac{\alpha-\alpha_i}{\alpha_{i+1}-\alpha_i}
 [\rho_s(\alpha_{i+1},T)-\rho_s(\alpha_i,T)]. \tag{C1}
$$

Here s denotes one source, density is kg/m³, T is fixed, and α is mol
CO₂/mol MEA. C1 is task-specified comparison arithmetic, not a published
property correlation. Exact tabulated targets return their printed value.
There is no temperature interpolation, extrapolation, correlation evaluation,
or use of another source's loading grid to relabel a measurement.

Han's α = 0.3 uses 0.21–0.32 with fraction 9/11; its α = 0.4 uses
0.32–0.44 with fraction 2/3. Hartono's own α = 0.3 uses 0.29–0.39
with fraction 0.1, and α = 0.4 uses 0.39–0.50 with fraction 1/11.
Weiland and Amundsen have exact α = 0.3 and 0.4 nodes. No requested
α = 0.4 is outside either third source's range. Amundsen has no 60 °C
series, so its differences at that temperature are unavailable. At 60 °C
Han can still be compared with Hartono.

For example, at 25 °C:

- Han(0.4) = 1075.6 + (2/3)(1096.4 − 1075.6) = 1089.466667 kg/m³.
- Hartono(0.4) = 1084.70 + (1/11)(1105.88 − 1084.70) = 1086.625455 kg/m³.
- Amundsen(0.4) = 1000 × 1.0957 = 1095.7 kg/m³.
- Weiland(0.4) = 1000 × 1.095 = 1095 kg/m³.

`compare.py.txt` prints the following table when run from the repository root:

```bash
python3 -I analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-6/source-conflict/compare.py.txt
```

All density and difference columns are kg/m³. “Distance advantage” is
|third − farther comparator| − |third − closer comparator|. Six decimals
retain arithmetic for reproduction; they are not experimental precision.

| Source | t (°C) | α | Third ρ | Amundsen ρ | Hartono ρ | Third − Amundsen | Third − Hartono | Closer | Distance advantage |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| Han2012 | 25 | 0.3 | 1071.563636 | 1070.000000 | 1068.554000 | 1.563636 | 3.009636 | Amundsen | 1.446000 |
| Han2012 | 25 | 0.4 | 1089.466667 | 1095.700000 | 1086.625455 | -6.233333 | 2.841212 | Hartono | 3.392121 |
| Han2012 | 40 | 0.3 | 1063.172727 | 1062.900000 | 1061.604000 | 0.272727 | 1.568727 | Amundsen | 1.296000 |
| Han2012 | 40 | 0.4 | 1081.700000 | 1088.500000 | 1079.650909 | -6.800000 | 2.049091 | Hartono | 4.750909 |
| Han2012 | 50 | 0.3 | 1057.645455 | 1058.000000 | 1056.436000 | -0.354545 | 1.209455 | Amundsen | 0.854909 |
| Han2012 | 50 | 0.4 | 1076.300000 | 1083.000000 | 1074.495455 | -6.700000 | 1.804545 | Hartono | 4.895455 |
| Han2012 | 60 | 0.3 | 1051.963636 | unavailable | 1050.919000 | unavailable | 1.044636 | unavailable | unavailable |
| Han2012 | 60 | 0.4 | 1070.666667 | unavailable | 1068.998182 | unavailable | 1.668485 | unavailable | unavailable |
| Han2012 | 70 | 0.3 | 1045.981818 | 1046.400000 | 1045.035000 | -0.418182 | 0.946818 | Amundsen | 0.528636 |
| Han2012 | 70 | 0.4 | 1064.733333 | 1071.900000 | 1063.163636 | -7.166667 | 1.569697 | Hartono | 5.596970 |
| Han2012 | 80 | 0.3 | 1039.763636 | 1040.200000 | 1038.852000 | -0.436364 | 0.911636 | Amundsen | 0.475273 |
| Han2012 | 80 | 0.4 | 1058.466667 | 1066.000000 | 1057.040909 | -7.533333 | 1.425758 | Hartono | 6.107576 |
| Weiland1998 | 25 | 0.3 | 1073.000000 | 1070.000000 | 1068.554000 | 3.000000 | 4.446000 | Amundsen | 1.446000 |
| Weiland1998 | 25 | 0.4 | 1095.000000 | 1095.700000 | 1086.625455 | -0.700000 | 8.374545 | Amundsen | 7.674545 |

The source CSV inputs are the existing repository files, unchanged:

| File in `data/reference/MEA/observations/density_viscosity/` | SHA-256 |
|---|---|
| `Amundsen_2009_density_viscosity.csv` | `7322b7dc7f0c961d09dbfb356dccde00851c0de20ba589d150d9c3834900f70c` |
| `Hartono_2014_loaded_density.csv` | `be0daa47de963643c498af015b430ae785a3f0b0103a23f3d5f9f81102cee7b4` |

The script verifies those hashes and selects only density, nominal 30 mass %,
loaded rows. It checks a known linear reference case, exact-node evaluation,
and rejection of out-of-range targets. It imports only the Python standard
library and writes no output files. The retained third-source CSV contains
24 printed cells: 18 Han and 6 Weiland. The output is conditional on printed
loadings and local linearity; interpolated values have no propagated
uncertainty, and neighbouring points may share stock-composition errors.

## Hartono Table 3 comparison cells and discussion

Table 3 p.1810 (PDF p.3) mixes own unsuperscripted measurements with cells
from references 2 (Han), 3 (Amundsen), and 5 (Weiland), identified in the
references p.1815. Superscripts are source references, not trailing decimals.
These cells add no independent measurements. In particular, the common
column headings 0.11, 0.19, 0.29, 0.39, and 0.50 describe Hartono's own
series; they must not replace the literature sources' actual α values.

Hartono's Table 3 footnotes give u(t) = ±0.02 °C, u(ρ) = ±0.02 kg/m³,
u(α) = ±0.01 mol CO₂/mol MEA and u(w₁) = ±2 × 10⁻⁵ kg, as printed.
The same footnotes print expanded U(ρ) = ±0.02 kg/m³ at 95% confidence,
k = 2. The equal u(ρ) and U(ρ) and the kg unit attached to u(w₁) are
preserved, not repaired. These instrument/table figures do not remove the
separate composition ambiguity assessed in the existing density README.

All twelve superscript-2 cells shown are only the **unloaded and first
loaded** values at each listed temperature. Checked against Han's Tables 3
and 4, they are:

| t (°C) | Han unloaded, as copied (kg/m³) | Han α = 0.10, as copied (kg/m³) |
|---:|---:|---:|
| 25 | 1010.9 | 1033.3 |
| 40 | 1003.5 | 1025.3 |
| 50 | 998.1 | 1019.6 |
| 60 | 992.3 | 1013.8 |
| 70 | 986.1 | 1007.6 |
| 80 | 979.4 | 1000.2 |

They match Han's originals. Hartono Table 3 contains no superscript-2
cells near α = 0.3–0.5; the needed Han values therefore come directly from
Han Table 4, not a later comparison table.

The six superscript-5 cells at 25 °C are 1013.0, 1033.0, 1054.0, 1073.0,
1095.0, and 1117.0 kg/m³. These match Weiland's original α = 0, 0.10,
0.20, 0.30, 0.40, and 0.50 nodes after unit conversion. Table 3 does not
copy Weiland's intermediate 0.25, 0.35, or 0.45 values.

The complete set of 23 superscript-3 cells is below. Column α here denotes
the **original Amundsen node** with which the position is being compared.
For the unloaded column the original is Amundsen Table 1; loaded nodes
are Table 3, both p.3097. A dash means no superscript-3 cell was printed.

| t (°C) | α = 0 | α = 0.1 | α = 0.2 | α = 0.3 | α = 0.4 | α = 0.5 |
|---:|---:|---:|---:|---:|---:|---:|
| 25 | 1010.63 | 1021.0 | 1041.0 | 1070.0 | 1095.7 | 1121.1 |
| 40 | 1003.4 | 1021.0 | 1041.0 | 1062.9 | 1088.5 | 1114.0 |
| 50 | 998.1 | 1016.0 | 1035.5 | 1058.0 | 1083.0 | 1108.0 |
| 70 | 985.8 | 1004.8 | 1024.0 | 1046.4 | 1071.9 | — |
| 80 | — | — | — | — | — | — |

Nineteen of the 23 cells match Amundsen's originals after unit conversion;
four do not:

| t (°C) | Original α | Hartono superscript-3 density | Amundsen original density | Hartono copy − original (kg/m³) |
|---:|---:|---:|---:|---:|
| 25 | 0 | 1010.63 | 1010.6 | +0.03 |
| 25 | 0.1 | 1021.0 | 1028.0 | −7.0 |
| 25 | 0.2 | 1041.0 | 1048.0 | −7.0 |
| 70 | 0.1 | 1004.8 | 1004.0 | +0.8 |

The two −7.0 cells happen to equal Amundsen's 40 °C values, but the cause
of copying them into the 25 °C block is unknown. The enlarged rendered
page and bounding-box text both confirm `1010.63` followed by superscript
3; its second trailing 3 is a source reference. Most importantly for this
question, **all four printed superscript-3 α ≈ 0.4 cells equal Amundsen's
own α = 0.4 values**: 1095.7, 1088.5, 1083.0, and 1071.9 kg/m³ at
25, 40, 50, and 70 °C. No 80 °C superscript-3 comparison row is printed.
The primary-source α = 0.4 disagreement therefore is not created by those
four comparison-cell transcriptions.

Hartono's discussion on p.1810 says its 30 mass % measurements agree well
with Amundsen and Weiland, while Han deviates at higher concentrations and
shows nonlinear loaded/unloaded density ratios. Figure 2 p.1811 distinguishes
own measurements, Han, Amundsen, and Weiland, and plots density against α.
The discussion reports a roughly 0.4% discrepancy measure; Table 5 gives
model average absolute relative deviations at 30 mass % of 0.13% (own),
0.09% (Weiland), 0.28% (Amundsen), and 0.43% (Han). These are aggregate
**correlation-to-data** deviations, not matched α = 0.4 pairwise differences.
The three correlation parameters were fitted using all reported loaded
solutions (p.1810, text following Eq.5). Thus those statements and model
curves do not independently resolve the source disagreement or establish
that the unsuperscripted measurements coincide at high loading. No Hartono
correlation was evaluated in this task.

## Composition basis, handling, and unresolved causes

Amundsen states the MEA mass fraction is on a basis without CO₂ (p.3097,
Experimental Section). Han Table 4 footnote a states the same basis
explicitly. Weiland's fixed amine-to-water preparation supports the same
basis. Hartono prepares aqueous MEA first and then adds CO₂ (Section 2.1,
p.1808); the repository has adopted its printed α and nominal 30 mass %
CO₂-free basis, while preserving an unresolved α/x₃ inconsistency. No
requested source explicitly describes these 30 mass % series as
MEA/(MEA + water + CO₂). A switch between inclusive and exclusive mass
percent is therefore not an established explanation for their disagreement.

The existing density-folder README owns Hartono's unresolved composition
assessment: a loading shift consistent with printed x₃ is worth about
1.2–2.5 kg/m³, or a CO₂-free solvent of about 30.54–30.86 mass % is worth
about 0.9–2.3 kg/m³ relative to 30 mass %. These are alternative readings,
not additive error bars. Their scale is comparable to much of Han − Hartono
at α = 0.4 (+1.43 to +2.84 kg/m³); it is smaller than the Amundsen −
Hartono gap (+8.50 to +9.07 kg/m³), the Han − Amundsen gap (6.23–7.53
kg/m³ in magnitude), or the Weiland − Hartono gap at 25 °C (+8.37 kg/m³).
Hartono's ambiguity alone therefore cannot account for the full separation.
The particular alternatives described in that README would both lower
Hartono's density at a specified true loading and true 30 mass % composition:
using larger x₃-derived loadings shifts its curve to the right, and correcting
a richer solvent to 30 mass % lowers density. They would consequently
increase the positive Han − Hartono and Weiland − Hartono differences,
rather than reconcile them. Even a 2.5 kg/m³ downward change would leave
Han numerically closer to Hartono at each shared temperature at α = 0.4,
because the smallest printed-basis distance advantage is 3.39 kg/m³. This
is a bound using the existing ambiguity estimates, not an uncertainty test.
Han and Weiland raw preparation masses and unrounded loading analyses are
unavailable in the inspected papers, so a different unreported composition
error cannot be excluded or quantified as the cause.

Amundsen's method (pp.3096–3097) uses Merck MEA ≥99.5%, deionized water,
CO₂ bubbling, analysis of saturated stock, dilution with unloaded solvent,
approximately 500 g samples, and balance accuracy ±0.1 mg. Some diluted
samples were checked by BaCO₃ precipitation and acid/base titration, with
0.5 g analytical samples and endpoint pH 5.3. Amundsen gives no individual
stock or diluted-sample loading analyses with the density table.

Amundsen explicitly reports degassing difficulties as temperature rises
(p.3096) and gas-bubble formation preventing highest-loading density
measurements (p.3097). At α = 0.5 the omitted cases are 20 mass % at
80 °C, 30 mass % at 70 and 80 °C, and 40 mass % above 25 °C. That
statement does **not** say that the 30 mass % α = 0.4 measurements were
omitted, corrected for CO₂ loss, or known to be erroneous. A degassing
warning cannot be used as proof of the cause or as a numeric correction.

Amundsen's apparatus density uncertainty is ±0.00005 g/cm³ (0.05 kg/m³),
with estimated temperature uncertainty ±0.03 K, MEA mass-fraction
uncertainty 0.5% and loading uncertainty 2% (p.3096, as printed). The
later combined uncertainty is ±0.2% or ±0.002 g/cm³ (2 kg/m³) for loaded
solutions, except the highest temperatures and loadings (p.3099 continuing
on p.3100). There the authors say uncertainty is greater, chiefly because
of liquid-composition analysis, obtaining homogeneous samples, and avoiding
evaporation. No numerical upper bound or exact temperature/loading boundary
for that exception is supplied. The 0.05 kg/m³ instrument figure must not
replace the 2 kg/m³ combined estimate, nor the unbounded high-end exception.
These limitations prevent a formal uncertainty-based source ranking here.

## Other relevant items already in the Zotero library

The search remained inside Zotero. The supplied immutable SQLite URI was
queried read-only, excluding deleted items. A title query for density,
physical properties, or thermophysical properties together with amine/MEA
terms was followed by title/abstract searches for density and
monoethanolamine, and inspection of relevant parent/attachment metadata.
This is a bounded library inventory, not an exhaustive publication search.
Other physical-property papers were not added as comparison rows.

- **Jayarathna et al. 2013**, *J. Chem. Eng. Data* **58**, 986–992,
  DOI `10.1021/je301279x`; parent `9Q8ZZDKV`, PDF `YB6FNMXQ`.
  The PDF's Table 2 p.988 contains r = 0.3, α = 0–0.5 densities at
  303.15, 313.15, 323.15, and 333.15 K, printed pressure 0.8 MPa.
  The preparation defines r as MEA/(MEA + water) (p.987). Title,
  preparation, and the table were inspected in layout text to confirm scope;
  values were not visually transcribed or compared. Eimer and Melaaen
  are coauthors. PDF SHA-256
  `8ed775573f7e717034dda17a2d8a89cd5e211d67ab318ef3fe775ccf7d8aa53e`.
- **Karunarathne, Eimer & Øi 2020**, *Fluids* **5**, 13,
  DOI `10.3390/fluids5010013`; parent `JVANK8KM`, PDF `Y82ITJ68`.
  Table 4 p.6 contains w₁ = 0.3 loaded densities over 293.15–353.15 K,
  including α = 0.328, 0.445 and 0.543 (the highest-loading series has
  missing high-temperature cells). Title, abstract and Table 4 were inspected
  in layout text only; its methods and comparison values were not evaluated.
  This is another Eimer/Øi-group source. PDF SHA-256
  `d7980c47030f3753ffa339c42f4bc7914908ff24e1cd12e2acd52512daf8d48d`.
- **Ramezani et al. 2021**, *J. Mol. Liq.*, 115569,
  DOI `10.1016/j.molliq.2021.115569`; parent `VMZKH34U`.
  The local attachment `NCLG54A3` is linked to
  `/home/tnnrpolley21/Downloads/Zotero-Supplements/Ramezani_2021_Supporting_Information.pdf`.
  Its Table S2 p.2 includes zero-sugar, 30 mass % MEA loaded densities at
  298.15–343.15 K alongside the sugar-added series. The title and first
  tables were inspected in layout text to confirm that the zero-sugar
  comparison exists; the main paper, method and numerical comparisons were
  not read. Supplement SHA-256
  `06c2ca3388440f78aca2d4e8fc34416938ea04d391554d1329d72a782e5e2385`.
- **Perumal et al. 2021**, “Experimental investigation on CO₂ absorption
  and physicochemical characteristics of different carbon-loaded aqueous
  solvents,” DOI `10.1007/s11356-020-10562-0`; parent `J5IGJX7Y`,
  PDF `JIUQTMT3`. The library abstract explicitly lists 30 wt% MEA and
  loaded-solution density measurements. This is an abstract/metadata lead
  only: its numerical table, temperatures, method and uncertainties were
  not inspected, so it contributes no evidence to the numerical conclusion.
- Hartono's separately catalogued `MTGKTMAL` / `582BLNR4`, DOI
  `10.1021/je401081e.s001`, is **supporting information to Hartono 2014**,
  not a new 2016 experimental campaign. Its title page and Figure S1
  caption (PDF p.1) were inspected in layout text. It contains density parity
  plots; no new density table was identified in the inspected contents.
  PDF SHA-256
  `8a46e75b131f7b2e296956add89e65548392af0ba027d3db626707574dc38ce0`.
- Hartono also cites **Aronu et al. 2011**, DOI
  `10.1016/j.ces.2011.08.042`, parent `AYEZBMRS`, PDF `W2NNU9H6`,
  as containing some loaded physical-property data (Hartono p.1808,
  ref.11 p.1815). This paper is present in the library, but its abstract
  concerns vapor–liquid equilibrium. Its density contents were not checked
  here; it remains an unverified lead, not another confirmed density series.

The two fully transcribed third sources answer the requested comparison but
disagree. Remaining unknowns are the raw stock analyses, correlated systematic
errors, the cause of Hartono's copying discrepancies and loading/composition
inconsistency, Weiland's full loaded-density uncertainty and specific-gravity
convention, and the result of a separate primary-source comparison using the
additional library papers. No recommendation about what to fit follows from
this evidence record.
