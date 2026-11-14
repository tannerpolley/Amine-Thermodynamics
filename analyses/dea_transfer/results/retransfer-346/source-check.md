# DEA source check for issue 346

The fixed dissociation law is unchanged. The bounded search of the held Zotero
sources did not find a DEA dissociation measurement above approximately 323 K.
This is a statement about the inspected library, not an exhaustive literature
search or proof that no higher-temperature measurements exist.

Bower, Robinson and Bates (1962), *Journal of Research of the National Bureau
of Standards A* 66A, 71–75, reports measurements from 0 to 50 degrees Celsius.
The measurement temperatures are described in the experimental section on
p. 71; Eq. 7 on p. 73 is the law retained here. Zotero parent V67HZ6HX,
PDF HBS9XN4Q, DOI 10.6028/jres.066a.008. The present calculation interval is
broader than those measurements. The upper bound for range marks is 323.15 K
using the modern Celsius conversion, consistent with Part II's approximate
323 K limit.

Hamborg and Versteeg (2009), *Journal of Chemical & Engineering Data* 54,
1318–1328, DOI 10.1021/je800897v, was read at the introduction and methods
(pp. 1318–1319), results and discussion, Table 11 (p. 1322), Appendix B
Table 16 and reference 32 (p. 1328). Its measured-amine list excludes DEA.
Its Table 11 DEA thermodynamic values cite Bower as reference 32. It therefore
supplies no extended DEA measurement range or replacement DEA law.
Zotero parent D9KXSKLR, PDF 334KGLPV.

The live Zotero title searches `diethanolamine`, `diethanolammonium`,
`dissociation`, `Hamborg`, `Blauwhoff` and `Littel`, together with the project
Companion search, supplied navigation. The N-methyldiethanolamine source is
for MDEA and cannot extend DEA's range. No alternative DEA constant was
identified in those held sources. A numerical difference from an alternative
law and a count of states relieved of range marks are consequently unavailable;
no such law is substituted or assigned a zero difference.

## Published models on the same observations

- Lawson and Garst (1976), results and accuracy discussion, printed p. 25:
  Table II supplies the fitted DEA observations; the stated 9 percent scatter
  is against smoothed data curves, not a reported thermodynamic model error.
  No same-row published-model scalar deviation is reported there.
- Seo and Hong (1996), Table 1 and Results and Discussion, printed p. 259:
  the 30/0 DEA/AMP subset supplies the 16 not-fitted observations. The Li and
  Chang smoothed comparison in Figure 2 is for AMP, not this DEA subset.
  No scalar DEA model deviation is reported for these rows.
- Lal, Otto and Mather (1985), pp. 683–684, Eqs. 9–13 and Figure 3:
  Kent and Eisenberg's constants give a published CO2 comparison at 100 degrees
  Celsius. Lal states that those constants were fitted to earlier data, mostly
  at higher partial pressure. These later Lal observations are not fitted by
  that comparison. The paper reports the comparison graphically and
  qualitatively, with no scalar deviation on the present 44-row subset.
  Digitizing a graph is not treated here as a reported numerical scalar.
- Carson et al. (2000), Table 2, Table 5 and Table 6, pp. 1289–1295:
  the fitted integral heat observations and their uncertainties are reported.
  Table 6 compares infinite-dilution measurements and inferred heats, a different
  quantity from the 50 finite-loading observations. No same-row published
  thermodynamic-model scalar deviation is supplied for those 50 rows.

Published-model scalar deviations are therefore recorded as not reported in
these inspected source passages. Source uncertainties remain named comparisons,
not agreement thresholds: Lawson 9 percent scatter, Carson approximately
1–2 percent, Seo and Hong 2–3 percent loading uncertainty, and Lal approximately
15 percent partial-pressure accuracy above 0.05 kPa with much larger errors
below it. The data transformations and detailed source identities remain in
`data/reference/DEA/sources.json`.
