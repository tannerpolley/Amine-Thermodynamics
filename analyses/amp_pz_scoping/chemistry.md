# Chemistry to declare before AMP, PZ and blend fitting

This is a proposed chemical-equilibrium declaration for #227. AMP chemistry is supported by Ciftja 2011 §§3–6 (DOI [10.1016/j.egypro.2011.01.096](https://doi.org/10.1016/j.egypro.2011.01.096)) and Tong 2012 §3.1 (DOI [10.1016/j.ijggc.2011.11.005](https://doi.org/10.1016/j.ijggc.2011.11.005)). PZ carbamate constants remain a source gap: Ermatchkov 2003 is indexed but not in Zotero. No private fitted constant is a source for this design.

## Shared species and reactions

Freeze H2O, CO2, H3O+, OH−, HCO3− and CO3²− at the selected MEA record, with their shared interactions and the adopted R1–R3 laws. In the hydronium convention:

1. 2 H2O ⇌ H3O+ + OH−.
2. CO2 + 2 H2O ⇌ HCO3− + H3O+.
3. HCO3− + H2O ⇌ CO3²− + H3O+.

These equations are charge and element balanced. Ciftja 2011's extracted Eq.3 is garbled; it must not replace the repository-owned bicarbonate dissociation equation. Vapor supports only neutral volatile molecules, not ions. A neutral zwitterion needs a separate volatility decision; electrical neutrality alone does not make it volatile.

## AMP

Add neutral AMP, AMPH+ (charge +1), and AMPCOO− (charge −1). Together with the six shared species this gives nine liquid species. Proposed vapor support: H2O, CO2, AMP.

- AMPH+ + H2O ⇌ AMP + H3O+ (Ciftja Eq.4; Tong reaction V).
- AMPCOO− + H2O ⇌ AMP + HCO3− (carbamate hydrolysis; Tong reaction VI).

Ciftja Eq.6 writes the second reaction in reverse. Its formation constant must be inverted for hydrolysis. Do not also impose the dependent CO2-to-carbamate reaction: its log constant follows from the shared CO2 law and carbamate hydrolysis law.

**Carbamate assessment:** retain the species for the proposed pressure-and-speciation study. Ciftja 2011 §5.1 and Fig.2 identify a carbamate signal at low loading; §5.2/Table 2 report nonzero concentrations. That is evidence against an exactly zero-carbamate chemistry over the measured states. It does not establish the magnitude of its influence on pressure. A bicarbonate-only model could later be assessed as a reduction against measured NMR and pressure uncertainty; it cannot be assumed adequate now. The later Ciftja 2014 temperature-dependent study remains unread, so no quantitative high-temperature negligibility claim is made.

Ciftja 2011 §4 explicitly omits activity coefficients from its apparent constant. Its NMR measures AMP+AMPH+ and HCO3−+CO3²− sums because proton exchange prevents separation (§5.1). The split uses pH and literature constants (§5.2). Preserve each paper's reported observation basis. Either compare reported mole fractions directly or retain the explicit conversion to ratios per total analytical AMP, including AMPCOO− in the denominator and propagating normalization uncertainty. Do not fit the normalized AMP+AMPH+ sum and normalized carbamate as independent observations: they are complementary. Use a nonredundant observation set compatible with the driver's scalar residuals, and document remaining correlations and uncertainty assumptions. Do not score pH-derived protonation splits as independent NMR measurements.

## PZ

Proposed liquid additions: PZ (0), PZH+ (+1), PZH2²+ (+2), PZCOO− (−1), HPZCOO (0, zwitterion, also written H+PZCOO−), PZ(COO)2²− (−2). Six shared species plus these six give twelve liquid species. Proposed vapor: H2O, CO2, PZ. These names correspond to the chemistry indexed by Ermatchkov 2003 and the CESAR-1 species list, not an adopted numerical PZ parameter set.

An independent balanced basis is:

1. PZH+ + H2O ⇌ PZ + H3O+.
2. PZH2²+ + H2O ⇌ PZH+ + H3O+.
3. PZCOO− + H2O ⇌ PZ + HCO3−.
4. HPZCOO + H2O ⇌ PZCOO− + H3O+.
5. PZ(COO)2²− + H2O ⇌ PZCOO− + HCO3−.

Hamborg & Versteeg 2009 Tables 9, 10 and 16 supply the two protonation equilibria, with group numbering to be mapped explicitly to these directions. Ermatchkov 2003 is the candidate for monocarbamate, protonated monocarbamate and dicarbamate equilibria; original directions, coefficient forms, solvent isotope correction and activity standard state must be read before numerical adoption. This is a stoichiometric proposal, not a claim that those five numerical laws are ready.

## Constant bases and caloric references

For every independent reaction retain stoichiometric coefficients, direction, natural-log versus log10 convention, coefficient units and polynomial form, temperature domain, standard pressure, source activity basis, water activity and reference species. Use dimensionless activities with a stated standard molality of 1 mol/kg for a molality law; never insert a dimensional concentration product directly into a logarithm.

Hamborg 2009 theory Eqs.1–15 and Appendix B derive infinite-dilution molality constants from electromotive-force measurements with activity corrections. AMPH+ dissociation: use Hamborg & Versteeg 2009 Table 1 (p.1320), the correlation form ln K = A/T + B + C ln T in Eq.21 (p.1319), and the 24 AMP experimental runs in Table 16 (p.1325). Table 4 describes DMMEA; Eq.35/Table 15 do not provide the AMP dissociation law. The source uses hydronium, explicit water activity, and an infinite-dilution molality standard state. Transcribe the AMP measurements and establish the numerical correlation and its uncertainty before adoption. Document the mapping into the Engine reaction-reference convention, including water factors, standard pressure, direction, and temperature domain; verify source reference values and reciprocal constants for reversed reactions.

PZ Tables 9–10 and 16 supply reaction-equilibrium evidence; the group-to-reaction mapping remains unresolved until checked against named stoichiometry, rather than numbered first and second constants. Do not import a mole-fraction polynomial or an eNRTL fitted constant without the conversion. At infinite dilution, m_i/(1 mol/kg) = x_i/[M_water x_water (1 mol/kg)]. Apply the resulting stoichiometric powers and explicit water factors to the whole reaction; the MDEA additive conversion is not a universal constant for every PZ reaction. Check a reference-temperature value against the paper and verify reversed reactions give reciprocal constants.

Freeze shared R2 including its MEA enthalpy shift. New AMP/PZ thermodynamic constants need source-backed temperature derivatives before claiming reaction enthalpies. The driver permits a constant log-law shift and a pivot-preserving enthalpy shift; these are distinct fitted quantities. A law fitted to NMR cannot also validate that NMR. Missing ideal-gas Cp or incompatible h/s anchors block caloric comparisons even when pressure solves.

## Blend additions

Combine the two single-amine species sets with one copy of each shared species: fifteen liquid species, proposed vapor H2O/CO2/AMP/PZ. There is no new independent proton-transfer constant: it is derived from the single-amine dissociation laws. Analytical feed must retain separate AMP and PZ amounts. Report loading both per amine molecule and per nitrogen site when a source uses the latter: PZ contributes two sites; they are not interchangeable.

New cross-solvent pairs are the Cartesian product {AMP, AMPH+, AMPCOO−} × {PZ, PZH+, PZH2²+, PZCOO−, HPZCOO, PZ(COO)2²−}: **18 possible unlike-component pairs** before model exclusions. This count is a derived enumeration, not a claim of 18 adjustable parameters. It includes neutral–neutral, neutral–ion, opposite-sign ion pairs and same-sign pairs. Apply the declared same-sign dispersion exclusion in the sphere convention; the charged-molecule convention requires its own explicit rule. Cross-association between neutral amines and any associating charged molecules also needs a mixing-rule declaration. Single-amine fits determine none of these AMP/PZ cross pairs directly.

First blend prediction: freeze every single-amine and shared quantity, set unmeasured cross dispersion corrections to the declared zero convention, and use the declared association combining rule. Report this as a prediction conditional on those assumptions. Only after the untouched blend comparison may an owner approve fitting a small, identifiable subset, starting with AMP–PZ from unloaded VLE. Do not infer mixed carbamates or a new covalent species without source evidence.
