All coefficients in this screen are screening inputs. None is adopted. Only the bulk permittivity declaration changes; SSM+DS Born diameters, shell constants, ionic-region permittivity (8), solvation factors, interactions, association topology, reaction correlations and the empirical density correction remain as serialized. The density correction is not applied to the equation of state.

The Engine evaluates Yang, Kontogeorgis and de Hemptinne (2024), §2.1, p. 4, Eqs. (1a), (2a), (2b):

$$\epsilon_r=1+\frac{n_S}{V}\overline{d_V}\left(\frac{\overline{d_T}}{T}-1\right),\qquad
\overline{d_V}=\frac{\sum_{i\in S}n_i d_{V,i}}{n_S},\qquad
\overline{d_T}=\frac{\sum_{i\in S}n_i d_{T,i}}{n_S}.$$

$S$ contains every neutral component: water, MEA and CO₂. Ions do not enter the coefficient averages. $V$ is the total phase volume and $n_S$ is the neutral amount. The Engine converts $d_V$ from L/mol to m³/mol. This is a product of two mole averages, not an average of pure-component permittivities. It retains the neutral mole fraction in $n_S/V$.

Water uses $d_V=0.3777$ L/mol and $d_T=1403$ K. Yang Table 6, p. 6 marks both as preset and attributes them to Schreckenberg et al. (2014), its Ref. 24. The source reader visually verified the Yang table. No other water equation-of-state parameters were taken from Yang.

Agieienko and Buchner (2024), main article §3.1 and SI Table S2, give neat MEA $\epsilon_s=30.45$ at 298.15 K. A pure-liquid Engine calculation using the current model gives $\rho_{\mathrm{MEA}}=16569.75035575249$ mol/m³ at 298.15 K and 101325 Pa. The SI reports 16.56 mol/L and density 1.01142 g/cm³; these are independent comparisons, not alternative density inputs used to tune coefficients. The one constraint determines:

$$d_{V,\mathrm{MEA}}=\frac{30.45-1}{(\rho_{\mathrm{MEA}}/1000)(d_{T,\mathrm{MEA}}/298.15-1)}\quad\mathrm{L/mol}.$$

| MEA $d_T$ (K) | MEA $d_V$ (L/mol) | Role |
|---:|---:|---|
| 900 | 0.8804726755150551 | Lower-temperature coefficient bracket |
| 1403 | 0.4796239125299687 | Same $d_T$ as water |
| 2200 | 0.2786300074972979 | Higher-temperature coefficient bracket |

The bracketing temperatures are analyst-selected sensitivity inputs, not measured MEA parameters. Both bracket water's 1403 K and exceed the current model's 393.15 K upper screening domain, so the factor $d_T/T-1$ remains positive. At fixed density and normalized to the 298.15 K anchor, the pure-MEA dielectric excess at 353.15 K is about 0.767, 0.802 and 0.820 of its anchor for 900, 1403 and 2200 K, respectively. This samples temperature curvature while satisfying the same single datum. These three choices do not identify two coefficients or estimate uncertainty.

CO₂ has $d_T=1403$ K in both alternatives. A nominal liquid-like reference density of 20 mol/L at 298.15 K, explicitly assumed rather than obtained from a CO₂ phase solve, gives:

$$d_{V,\mathrm{CO_2}}=\frac{1.55-1}{20(1403/298.15-1)}=0.007421030004072951\quad\mathrm{L/mol}.$$

The second alternative uses $d_V=10^{-8}$ L/mol, with the same $d_T$, giving a near-zero dielectric excess. The nominal CO₂ reference is only a screening construction. The six combinations are recorded, without rounding, in [coefficients.csv](coefficients.csv) and the six parameter JSON files. All constant `relative_permittivity` coefficients and all correlations of that family were removed. The Engine admitted all six declarations; no Engine declaration rule was bypassed.

The full unloaded MEA–water comparison uses [Agieienko SI Tables S1–S2](https://www.rsc.org/suppdata/d3/cp/d3cp05027k/d3cp05027k1.pdf), 14 compositions at 298.15 K, in [inputs/agieienko-298K.csv](inputs/agieienko-298K.csv). The closest tabulated composition to 30 wt% is 30.21 wt%, with density 1.01042 g/cm³ and $\epsilon_s=66.71$. Table S2 takes neat-water data from its Ref. 2. SI S1 and S2 print different concentrations, 13.47 and 13.50 mol/L, for the 80.48 wt% row; both are preserved. The numerical comparison uses printed mass fraction and density. The official RSC indexed text was readable, but the ESI PDF could not be downloaded and has no local hash; this source-access limit remains explicit.

The source-density calculation uses the measured mixture density, reported component molar masses and the unloaded neutral composition. The model-density calculation uses the same composition at 101325 Pa. They do not introduce an unloaded chemical fit. The SI reports generally less than 1% relative uncertainty in static permittivity; the main article §2.3, p. 2313 reports relative expanded density uncertainty 0.0005. These uncertainty statements are not propagated into screening coefficient intervals.

Hajj et al. (2024), Table 1, p. 9 supplies 28 loaded 30 wt% comparisons: 293.15–353.15 K, loadings 0.22, 0.33, 0.44 and 0.55 mol CO₂/mol MEA. Their §3.3.1, p. 8 warns that microwave measurements may misestimate the static limit, especially at low temperature and high loading, and that ionic polarization cannot be ruled out. We compute reacting single-liquid states at an assumed 101325 Pa, with the current reaction references; this pressure is a calculation assumption, not a measured pressure transcribed from Table 1. These rows are qualified comparisons, not calibration or physical-validation targets. Main-paper PDF identities and verified Zotero attachment identities are in [provenance.json](provenance.json).
