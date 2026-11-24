The reported AMP endpoint is the #412 slope-150 fit. R4 is carbamate +
water ⇌ AMP + bicarbonate on the infinite-dilution common-molality basis,
with $m^\circ=1$ mol/kg and water explicit. The fitted law increases the
hydrolysis constant and favors the products. The referee's +1.7 estimate at
313.15 K used symmetric level bounds. The declared bounds span −3 to +2
about the source value and give the pivot shift shown below, about @se_pivot
conditional standard errors. The fit standard error holds the enthalpy
increment at its lower bound and the shared inputs and model form fixed.

The starting hydrolysis law inverts Silkenbäumer et al. (1998, Table 5,
reaction IV, p. 3138), which represents Xu et al.'s (1992, Table 2, p. 11)
three extended Debye–Hückel solubility-model estimates of the formation
constant. Xu gives 0.034, 0.024 and 0.0089 kg/mol at 40, 50 and 100 °C
with no stated uncertainty. The maximum log deviation of the starting
law from those estimates is given in C3. Xu's Table 3 gives apparent
carbon-13 NMR upper bounds of 0.1 L/mol at 40 °C (Sartori and Savage)
and 42 °C (Chakraborty et al.). Bosch et al. obtained 0.048 L/mol at
25 °C from absorption kinetics, with 20% stated inaccuracy (Bosch
Table 4, p. 1169). Those molarity values give order-of-magnitude
comparisons with the fitted infinite-dilution formation constants of
@formation kg/mol at 298.15 and 313.15 K.
[Silkenbäumer Table 5](https://doi.org/10.1021/ie970925w) ·
[Xu Tables 2–3](https://doi.org/10.1016/0255-2701(92)80002-K)

At about 298 K, the retained source comparison spans 0.0075 kg/mol
(Ciftja 2011, apparent ratio converted at finite composition) to about
0.76 kg/mol (Ciftja 2014 Eq. 19, expressed at finite composition).
Ciftja 2014 gives 0.82 kg/mol at infinite dilution. Published hydrolysis
enthalpies near 298 K are 17.1 (Mehdizadeh 2013), 20.8 (Ciftja 2014),
21.2 (Xu and Silkenbäumer) and 35.8 kJ/mol (Hartono 2020).
[AMP law sources](../amp_pz_scoping/sources/carbamate-law-sources.md) ·
[Ciftja basis and residual scale](../amp_pz_scoping/sources/ciftja-2014.md)

The source-enthalpy and released variants hold the fitted $\ln K_4$
at 313.15 K and set the source-relative enthalpy increment to zero and
−10 kJ/mol, respectively. The source variant restores both source
coefficients. The fitted cost gradient of +$@gradient\times10^{-5}$
per J/mol projected a @projected cost reduction on release. The evaluated
reduction is about @evaluated and comes from the carbamate fractions, while
the loaded-pressure cost rises. At fixed parameters, the release raises
grid carbamate above the calibration range. The calibration residual changes
sign across that range, with the endpoint mean errors exceeding
the 0.0025–0.003 absolute residual scale cited in the source assessment.
The temperature groups cover different loadings.

The grid uses 30 mass % AMP, species amounts per total amine, and vapor
CO₂ partial pressure. Tong and the supplemental Hartono 2021 rows use
total equilibrium pressure. The deviations preserve the declared
observable of every other row, including Hartono 2013 vapor AMP mole
fractions and Kundu CO₂ partial pressures. Speciation above the Ciftja
measurement range comes from the model.
The law variants quantify fixed-parameter sensitivity. The unbounded
optimum would require a refit.

[Input hashes](results/r4-shift-426/identity.json) ·
[Reported deviations](results/r4-shift-426/reported-deviations.csv) ·
[Source-enthalpy deviations](results/r4-shift-426/source-enthalpy-deviations.csv) ·
[Released deviations](results/r4-shift-426/released-deviations.csv) ·
[Source deviations](results/r4-shift-426/source-deviations.csv) ·
[Reported grid](results/r4-shift-426/reported-grid.csv) ·
[Source-enthalpy grid](results/r4-shift-426/source-enthalpy-grid.csv) ·
[Released grid](results/r4-shift-426/released-grid.csv) ·
[Source grid](results/r4-shift-426/source-grid.csv)
