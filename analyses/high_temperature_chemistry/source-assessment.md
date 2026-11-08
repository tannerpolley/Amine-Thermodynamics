# High-temperature MEA reaction constants

Issue #263 source assessment, 6 November 2026. Intended use: reaction-law
attribution with the selected EOS parameters held fixed, not parameter adoption.
The source question is whether R4 carbamate hydrolysis or R5 MEAH+ dissociation
has measurements above 323 K that are independent of fitting the concentrated
MEA activity model. Activity corrections in a dilute experiment do not imply
that a law was fitted jointly with a concentrated-solution model.

## Sources read and applicability

| Source and exact locator | Temperature and convention | Assessment |
| --- | --- | --- |
| Hamborg and Versteeg (2009), DOI 10.1021/je800897v, Theory and Experimental Procedure pp. 1318–1319, Eq. (18), Eq. (21), Table 16 pp. 1326–1327 | MEA measurements approximately 293–353 K; molality, infinite dilution extrapolation; Pitzer HCl/KCl corrections and approximate solution corrections before dilution extrapolation | Independent dilute R5 evidence exists above 323 K. MEA Table 5 prints correlated values only through 323 K; Table 16 contains the higher-temperature observations. Any new polynomial fitted to Table 16 must be identified as a derived law, rather than coefficients published by these authors. |
| Kim et al. (2011), DOI 10.1016/j.jct.2011.06.004, §2.2 pp. 1755–1756, §3.2 p. 1758, Eq. (6), Tables 5 and 7 | MEA potentiometric titration 298.15–363.15 K; protonation calorimetry 298.15–393.15 K. Dilute molal solutions; pKa from pH at half equivalence, with activity coefficients assumed constant | Independent of fitting the MEA EOS, but not an exact infinite-dilution molality determination. Table 5 law is deferred: its printed coefficients fail to reproduce its own Table 7 by about 13 natural-log units; activity assumptions and rounding do not explain that discrepancy. Table 7 reports ln Ka = −18.55 at 353.15 K and −18.18 at 363.15 K. The 393 K support is calorimetric, not a direct Ka measurement. |
| Aroua et al. (1999), DOI 10.1021/je980290n, Theory p. 888, Table 3 and Eq. (14) p. 890 | Molarity-based carbamate formation constant; measurements at 298, 308, 318, 328 K; extrapolation to zero ionic strength after calculated species and Guggenheim activity correction | Extends above 323 K to 328 K. Does not measure R4 at 353 or 393 K. Equation (14), log10 Kformation = −0.934 + 671/T, reverses to approximately Tong's ln Khydrolysis = 2.151 − 1545.3/T, before the molarity/molality distinction. The paragraph next to Table 3 contains a conflicting temperature list; the experimental table and Table 3 identify 298–328 K. |
| Böttinger et al. (2008), DOI 10.1016/j.fluid.2007.09.017, §§2–3, §5 and Table 5, §§6–7 | NMR species to 353 K; asymmetric molality activities. Carbamate formation law fitted jointly with extended Pitzer parameters and with an oxazolidone reaction | Model-bound R4 law, not an independent thermodynamic replacement. Experimental amine quantity is MEA + MEAH+, not separately resolved species. Omitting oxazolidone changes the interpretation of high-loading amine balance. |
| Wada et al. (2021), DOI 10.1016/j.ijggc.2020.103175, §2 pp. 2–3, §3 p. 3, §4.3.1 pp. 5–6, Tables 2 and 4 | MEA carbamate NMR at 25, 30, 35, 40, 45 °C, approximately 30 wt% in D2O; molarity constants and activity coefficients unity in modified Kent–Eisenberg analysis | Does not supply an above-323 K R4 law; concentration constants are not interchangeable with thermodynamic molality constants. Newly acquired Zotero parent KG36XZ5V, PDF DVCEZP5V. |
| Kim and Svendsen (2007), DOI 10.1021/ie0616489, Experimental, Uncertainties, Tables 1–3, Conclusions | Semi-differential finite-dose heats, 30 wt% MEA, 313.15/353.15/393.15 K; variable reactor pressure and gas inventory corrections | Preserve the existing #245 finite-dose comparison, anomalous-row exclusions, and pressure limitations. Remaining heat discrepancy cannot be uniquely assigned to oxazolidone or unavailable pressure/dose histories. |

The Kim (2011) DOI above is verified against its PDF first page; Zotero parent
89KKLDUF is the source identity. No Mathpix conversion was used. Existing
Böttinger, Kim (2007), and Nasrifar reading copies were checked against current
indexed Zotero source hashes. Nasrifar and Tafazzol (2010), Chemistry and
Table 1, provide a model comparison and inherited source laws, not a new
independent high-temperature R4/R5 measurement.

## Kim (2011) printed correlation inconsistency

Independent readiness review checked the original PDF p. 1758. Equation (6)
and Table 5 give ln Ka = −184.66 + 33.24 ln T − 0.0452 T. At 298.15 K
this gives −8.748265, whereas Table 7 prints a correlated value of −21.80;
at 353.15 K it gives −5.606860, whereas Table 7 prints −18.69. This law
is excluded from the numerical comparisons pending resolution by source
evidence. The experimental values in Table 7 remain source evidence.
No coefficient repair, new correlation, or enlarged check tolerance is inferred.
Hamborg Table 16 remains the independent source for the derived R5 law.

## PDF identities

| Zotero parent | PDF attachment | SHA-256 |
| --- | --- | --- |
| D9KXSKLR | 334KGLPV | 21c8cd7aa8f6547eb8579c90958aac4e8f97f6bc43b2af5cfdf3294cc846ac37 |
| 89KKLDUF | 7R3LYF7R | 8e2fe3d0f4c1294ad74d1ea10b987dbb11c2d89a739386dd0f09198f6a1efbce |
| L8GDWZEW | 93Y7NVMH | 8ff86fb4dc598900c7540bb8ce0b08abd3b2b17121fb027048949bd0fa51eb6a |
| KG36XZ5V | DVCEZP5V | 1d3ebee8dcc33e02aaa6b2d0caf10ad8fefd881c64e74952b968b862d22fc627 |

## Limits of the source search

This bounded search inspected the project source map, retained reaction-source
audit, Companion project search, live Zotero searches and children, and primary
sources identified by searches for high-temperature MEA dissociation and
carbamate hydrolysis. It establishes the existence of independent R5 evidence.
It does not establish that every published R4 measurement has been found.
No source law tested outside its measurement interval becomes validated by
that extrapolation.
