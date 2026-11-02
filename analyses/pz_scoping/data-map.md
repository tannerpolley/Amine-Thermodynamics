# PZ source and data map

Research snapshot for [#237](https://github.com/tannerpolley/Amine-Thermodynamics/issues/237), 2026-11-02. It replaces the PZ rows of [#227's inventory](../amp_pz_scoping/data-map.md). Those rows were CESAR-1 filename leads; these are paper-checked blocks. No measurement table is copied here. Counts are rows printed in the source table, counted from the PDF text. They are not independent experiments.

CESAR-1 (`~/Workspaces/External/CESAR-1`, commit `f24611b95a0fa62bd41b99c1bfd8d700fc6ddd2a`) was read only for filenames and column headers, to find these sources. Nothing from it was copied or run.

Stage key, as in #227: (a) pure PC-SAFT; (b) unloaded VLE; (d) reaction constants; (e) loaded pressure; (f) speciation; (g) absorption heat; (i) loaded heat capacity; (s) solid–liquid equilibrium (new for PZ).

## Paper-checked blocks

| Stage | Source and locator | Property and basis | Conditions | Rows | Independence and caveats |
|---|---|---|---|---:|---|
| b | Hilliard 2008 thesis, App. D.2, PDF pp.968–969 (printed pp.911–912) | P_PZ and P_H2O over unloaded PZ–H2O, hot-gas FTIR, kPa; molality | 0.89–5.00 m, 32.7–63.4 °C | 46 | UT Rochelle lab. Rows marked "a" are the zero-loading points of the D.5 runs. CESAR-1's 42-row file is a figure digitization of the same data; use the table. |
| s | Hilliard 2008, App. I.1, PDF pp.1008–1009 (printed 951–952); method §5.3, PDF pp.144–150 | DSC solidus and liquidus, °C, vs PZ weight fraction; unloaded | w_PZ 0–0.771 (≈ 0–40 m), A/B duplicates | 45 | Peak-maximum assignment (§5.3). Phases assigned from DSC peaks (Fig.5.3-1/2): ice, PZ·6H2O, PZ·6H2O + anhydrous eutectic, anhydrous PZ. |
| d | Hamborg & Versteeg 2009, Table 16 continued, p.1326 | ln K from emf; molality, infinite dilution | 293–353 K, two PZ steps | 24 + 24 | Independent of every loaded dataset. Mapping to P1/P2 is in [chemistry](chemistry.md#group-to-reaction-mapping-now-settled). |
| d | Hetzer, Robinson & Bates 1968, Table III p.2084 | pK1, pK2 from emf; molality, zero ionic strength | 0–50 °C, 11 temperatures | 11 + 11 | Independent second source for P1/P2; laws printed (abstract). |
| f | Ermatchkov, Pérez-Salado Kamps & Maurer 2003, Tables 1–4, pp.1282–1285 | ¹H-NMR mole numbers per kg D2O of three lumped groups: (PZ+PZH⁺+PZH2²⁺), (PZCOO⁻+HPZCOO), PZ(COO)2²⁻ | 283.15, 298.15, 313.15, 333.15 K; 0.10–1.48 mol PZ/kg; CO2/PZ ≤ ~1 | 33+33+33+22 = 121 | **D2O solvent.** 10 rows report no dicarbamate (blank). The three groups sum to the PZ total (Eq.6), so only two of the three are independent per row. The same rows define the carbamate laws (Table 5), so they are not an independent test of those laws. |
| f | Hilliard 2008, App. F.4–F.5, PDF pp.990–991 (printed 933–934) | NMR, mol/kg H2O: PZ/PZH⁺, PZCOO⁻/HPZCOO, PZ(COO)2²⁻, HCO3⁻/CO3²⁻ | 27 °C; 1 m and 2 m; loading 0.16–0.80 mol CO2/(2 mol PZ) | 3 + 5 | The method and solvent were not read. Row 1-3 (1 m) sums to 1.45 mol/kg of PZ species, above the nominal 1 m: check the basis before any use. |
| e | Ermatchkov, Pérez-Salado Kamps, Speyer & Maurer 2006, Tables 1–3, p.1789 | CO2 **partial** pressure by headspace GC, kPa; molalities of PZ and CO2 | 313.1 K (≈1, 2 m), 353.15 and 393.15 K (≈2, 4 m); 0.1–95 kPa; CO2/PZ 0.05–0.95 | 52 | Δp = Δp* + 0.02 p, each point repeated 3–8 times (p.1789). Kaiserslautern lab, separate from UT. 393 K lies outside the 283–333 K carbamate law domain. |
| e | Hilliard 2008, App. D.5, PDF pp.973–974 (printed 916–917) | P_CO2, P_PZ, P_H2O by hot-gas FTIR, kPa; loading mol CO2/(2 mol PZ) | 0.89–5.18 m; 40 and 60 °C | 62 | Hilliard's own fit used these 62 rows (Table 14.4-2, p.527). P_PZ in loaded solution is a separate volatility observable on the same rows. |
| e | Dugas & Rochelle 2011, Table 2, p.2190; correction DOI 10.1021/je400717h | Equilibrium P*CO2 from zero-flux interpolation in a wetted-wall column, Pa; loading mol CO2/mol alkalinity | 2, 5, 8, 12 m; 40–100 °C | 43 (12+12+12+7) | Not a static measurement: the value comes from bracketing absorption and desorption (p.2188, Eq.4). **The correction says the 40 and 60 °C rows were already published** in Dugas & Rochelle 2009 (Zotero B7T53U6N): do not count both. Same lab as Hilliard. 12 m at 40 °C was not run (viscosity) and 12 m near 0.40 was not tested (solid limit, p.2189). |
| e | Xu & Rochelle 2011, Table 1, pp.119–120 | **Measured total pressure** Pt, kPa; P_CO2 is calculated from Eq.1 by subtracting Raoult's-law water and PZ (DIPPR); loading mol CO2/mol alkalinity, corrected for vapor CO2 | 4.93–8.00 m; 81–191.8 °C; loading 0.224–0.451 | 159 | Score only Pt as an observation; the printed P_CO2 depends on a model. The whole block lies above the constant domains (≤ 353 K). It is a high-temperature extrapolation test. Same lab as Hilliard; autoclave method (§2). |
| e | Bishnoi & Rochelle 2000, Table 1, p.5535 | P_CO2 by wetted-wall bracketing, Pa; loading mol CO2/mol PZ (**per molecule**) | 0.6 M PZ; 313 and 343 K | 17 (per Ermatchkov 2006 Table 5) | Dilute. Its own constants were fitted to these rows. One 313 K row at loading 0.96 is predicted 6.5 times too high by the authors' model: a domain edge. |
| g | Hilliard 2008, App. H.1, PDF pp.997–999 (printed 940–942) | Differential −ΔH_abs, kJ/mol CO2; NTNU calorimeter (credited to Inna Kim in Table 14.4-2) | 2.4 m; 40, 80, 120 °C; loading 0.03–0.50 mol CO2/(2 mol PZ) | 47 | The primary publication by Kim was not identified here. Caloric comparison only after reaction calorics are admitted. |
| i | Hilliard 2008, App. G.3–G.4, PDF pp.994–995 (printed 937–938) | Mass Cp, kJ/(kg K), DSC | 2.0 m (4 loadings) and 3.6 m (3 loadings); 40–120 °C at 5 K steps | 68 + 51 | Includes 34 unloaded values. Smoothed 5 K grid: each column is one run, not 17 independent points. |

Pressure caveat (from Ermatchkov 2006 Table 5 note b, p.1793): Pérez-Salado Kamps et al. 2003 report total pressures and "solid-phase precipitation" rows. Ermatchkov 2006 scored only rows above 0.2 MPa that had no precipitation.

## Indexed, not read (PDF unavailable or identity unresolved)

| Stage | Source | What is known, and from where | Status |
|---|---|---|---|
| e | Pérez-Salado Kamps, Xia & Maurer 2003, AIChE J. 49, 2662, DOI 10.1002/aic.690491019 | 95 total-pressure rows, 314–395 K, 2.0–4.0 m PZ, 0–5.4 mol CO2/kg, 13–9 560 kPa; includes solid-precipitation rows (Ermatchkov 2006 Table 5). CESAR-1 lead: 94 rows. | Zotero metadata `79R7VKJW`; Wiley needs the user's login (hand-off link https://doi.org/10.1002/aic.690491019) |
| e | Derks, Dijkstra, Hogendoorn & Versteeg 2005, AIChE J. 51, 2311, DOI 10.1002/aic.10442 | 58 rows, 298–343 K, 0.2–0.63 m, 0.3–111 kPa (Ermatchkov 2006 Table 5 ref.7) | Zotero metadata `ESTCE9HW`; same Wiley hand-off |
| s | Bishnoi 2002 solid solubility (cited in Hilliard Fig.5.3-3 and Table 9.4-1) | Unloaded SLE used with Hilliard's DSC data | Not identified or read |
| s | Freeman 2011 dissertation; Ma et al. 2012 crystallization study (SINTEF/TCCS) | Loaded SLE; hemihydrate, hexahydrate and anhydrous phases by powder XRD (SINTEF abstract only) | Not acquired |
| b | Hartono et al. 2013 PZ–H2O T–x–y (CESAR-1 file `hartono_et_al_2013_PZ_T_x_y.csv`, 24 rows) | Unloaded VLE | Bibliographic identity not resolved |
| b | Nguyen 2013 dissertation, Tables 3.3.1 and 5.3.3 (CESAR-1 leads); Nguyen, Hilliard & Rochelle 2011, Energy Procedia, DOI 10.1016/j.egypro.2011.02.033 | PZ and H2O partial pressures | Not acquired |
| i (support) | Chen et al. 2010, J. Chem. Thermodyn. 42, 54–59, Table 2 (inferred from CESAR-1 filename `chen_et_al_2010_54_59_table_2.csv`, 44 rows) | Unloaded PZ–H2O Cp | Identity inferred from a filename; not read |
| g | Liu PZ ΔH_abs (58 rows), Hartono Table 15 (26 rows) (CESAR-1 leads) | Absorption heat | Identities not resolved |
| f | Bishnoi 2000 NMR (two points, §4) | Speciation | Read only as cited in Ermatchkov 2003 §4 |

Searching for an author surname alone does not establish that a paper is absent.

## Proposed roles (not frozen)

The owner must approve these before any fit. The principle, from #220/#227: no row informs the law that is then tested on it, and hold-outs are whole campaigns chosen before fitting.

| Role | Proposal | Why |
|---|---|---|
| Fixed input | P1/P2 from Hamborg Table 16, after transcription and a fit to Eq.21 with uncertainty; Hetzer laws as a cross-check over 293–323 K | Independent of all loaded data, and it covers 293–353 K |
| Calibration, neutral | Hilliard D.2 (46 rows, P_PZ and P_H2O) for PZ–water k(T) | Only paper-checked unloaded PZ volatility block |
| Calibration, speciation | Ermatchkov 2003, two nonredundant groups per row; preserve the D2O basis and record its uncertainty | Only quantitative speciation block; carbamate law offsets would be fitted here, not tested here |
| Calibration, loaded pressure | Hilliard D.5 P_CO2 (62 rows, 40/60 °C) | Absorber temperatures, broad concentration range |
| Primary hold-out | Ermatchkov 2006 (52 rows), whole campaign, partial pressure; 393 K reported separately as extrapolation | Different laboratory, method and solvent preparation from every calibration block except the NMR lab. Note that the NMR came from the same Kaiserslautern group, so it is not lab-independent of the NMR calibration. |
| Secondary comparisons | Dugas 2011 80/100 °C rows (the 40/60 °C rows duplicate 2009 data); Xu 2011 Pt (159 rows) as a temperature-extrapolation test; Bishnoi 2000 (dilute edge) | Same UT lab as Hilliard; different apparatus |
| Supporting, unscored until calorics are admitted | Hilliard H.1 heat (47), G.3–G.4 Cp (119), D.5 P_PZ (62) | Need ideal-gas Cp and h/s anchors for PZ and its species |
| Domain gate | Hilliard I.1 SLE (45) and Freeman 2010 Figs.1–2 | Limits states the liquid-only model may claim |

An alternative primary hold-out is Dugas 80/100 °C (11 rows at 2–12 m), but it shares the UT lab and TIC loading method with Hilliard. That is why Ermatchkov 2006 is recommended. Kamps 2003 could replace it once its PDF is read; it comes from the same lab as Ermatchkov 2006 and overlaps in 313–393 K.
