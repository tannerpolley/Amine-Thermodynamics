This section uses the DEA #413 endpoint. R4 is carbamate + water ⇌ DEA +
bicarbonate on the infinite-dilution common-molality basis, with
$m^\circ=1$ mol/kg and water explicit. The reported law gives a lower
hydrolysis constant throughout the table, which favors carbamate. The
referee's estimate of about −1.3 agrees with the fitted pivot shift of
@pivot_shift. The enthalpy increment changes the shift at other temperatures. The
asymmetric enthalpy bounds were declared about the source law.

Aroua et al. (1997, Eq. 14 and Tables 3–4, p. 695) estimated the
infinite-dilution DEA formation constant from titration data at
303–331 K and extrapolation in ionic strength. The inverted law's
Table 4 entries at 291, 298, and 313 K carry absolute uncertainties
0.014, 0.019, and 0.038, respectively, or @source_relative.
The first two temperatures extrapolate below the measurements.
The fit shifts at 298.15 and 313.15 K are about @source_multiples times
those relative uncertainties on a first-order log scale. Eq. 14
has intercept and slope standard errors of 0.36 and 114 K on the
base-10 scale, with 3% mean and 6% maximum deviation. The slope
error corresponds to @source_enthalpy_se kJ/mol. The fitted enthalpy increment
is about @enthalpy_se_multiple slope standard errors below the starting law. The paper gives no coefficient
covariance or uncertainty for extrapolation above 331 K.
Table 4 also lists constants of 0.218–0.262 at 298 K (VLE-fitted
and finite-ionic-strength values) and 0.303–0.379 at 313 K (VLE-fitted),
compared with the fitted @hydrolysis at 298.15 and 313.15 K.
The fitted-law shifts are about @se_multiples conditional standard
errors at 298.15, 313.15 and 393.15 K.
[Aroua Eq. 14 and Tables 3–4](https://doi.org/10.1021/je970004s)

Restoring Aroua's law at the other #413 parameter values improves the three
Böttinger NMR mole-fraction comparisons and worsens the fitted Lawson pressure
comparisons in each temperature band. The grid gives liquid amounts per
total amine and vapor CO₂ partial pressure for the Lawson 25 mass % stock.
Above the measured NMR range the speciation comes from the model. The fit's
conditional errors hold shared and transferred values and the model form fixed. The fitted
R4 level and carbamate–water interaction have correlation @correlation, so
changes at fixed parameters describe sensitivity of the #413 endpoint.
[Retained conditional uncertainty](results/refit-413/conditional-uncertainty.json)

[Input hashes](results/r4-shift-426/identity.json) ·
[Reported-law deviations](results/r4-shift-426/reported-deviations.csv) ·
[Source-law deviations](results/r4-shift-426/source-deviations.csv) ·
[Reported-law grid](results/r4-shift-426/reported-grid.csv) ·
[Source-law grid](results/r4-shift-426/source-grid.csv) ·
[Reported NMR curves](results/r4-shift-426/reported-nmr-curves.json) ·
[Source NMR curves](results/r4-shift-426/source-nmr-curves.json) ·
[Manuscript handoff](results/r4-shift-426/manuscript-handoff.md)
