# AMP carbamate law: unresolved thermodynamic input

Source preparation for #229, 2026-10-29. Neither a transferable thermodynamic
hydrolysis law with verified temperature dependence nor an AMPCOO− PC-SAFT
representation was established. This blocks numerical Build; it is not evidence
that such a law cannot exist.

Ciftja et al. (2011), DOI [10.1016/j.egypro.2011.01.096](https://doi.org/10.1016/j.egypro.2011.01.096),
was read in the [author's full text](https://www.researchgate.net/publication/251711690_Study_on_carbamate_stability_in_the_AMPCO2H2O_system_from_13C-NMR_spectroscopy).
§3 Eqs.5–6, p.616, supplies carbamate formation and the alternative
AMP + HCO3− ⇌ AMPCOO− + H2O. §4 Eq.7 explicitly omits activity coefficients
from its evaluated apparent constant. §5.2/Fig.3 and §6 report an average
mole-fraction apparent stability constant near 0.47 at 25 °C, with loading
dependence. This is not an infinite-dilution thermodynamic constant or a
measured enthalpy. Relevant cited leads are Chakraborty et al. (1986), ref.1;
Jakobsen et al. (2005), ref.7; Wang's 2001 NMR thesis, ref.10; and the
Deshmukh–Mather model, ref.13. These are leads, not newly verified AMP laws;
no unapproved Zotero additions were made.

For hydrolysis in the reverse direction, the required thermodynamic definition
is, by reaction stoichiometry,

$$\mathrm{AMPCOO^-+H_2O\rightleftharpoons AMP+HCO_3^-},\qquad
K_h(T)=\frac{a_{\rm AMP}a_{\rm HCO_3^-}}{a_{\rm AMPCOO^-}a_w}.$$

On a common mole-fraction standard convention, the apparent formation ratio
omitting water is q=x(AMPCOO−)/[x(AMP)x(HCO3−)]. Thus

$$K_h=\frac{1}{q}\frac{\gamma_{\rm AMP}\gamma_{\rm HCO_3^-}}
{\gamma_{\rm AMPCOO^-}a_w}.$$

This identity explains why simply using 1/0.47 as K_h loses both activity and
water factors. A molality law additionally needs its standard-state conversion.
Even a constant apparent q would not establish zero thermodynamic reaction
enthalpy. The temperature derivative belongs to ln K_h, with all standard
states specified; no slope is inferred from a single-temperature measurement.

Ciftja et al. (2014), DOI [10.1016/j.ces.2013.12.028](https://doi.org/10.1016/j.ces.2013.12.028),
CES 107, 317–327, remains **unavailable as full text/PDF** in this attempt.
The public publisher abstract/highlights describe 30 wt% AMP at 25,35,45 °C,
an apparent stability calculation, and pH/literature-assisted splitting of
protonation and carbonate signals. They cannot establish its exact tables,
equations, uncertainty or temperature coefficients. The acquisition command
created metadata parent `HBBD5J2B` but obtained no PDF: the Elsevier Article Retrieval service
returned only one page for an eleven-page paper and the publisher check did
not clear. No retry or Mathpix conversion was performed. Handoff: the DOI link
above. A metadata item is not completion of the requested PDF acquisition.

The NMR evidence supports retaining AMPCOO− as a species. It does not determine
its segment number, association sites, dispersion parameters or Born diameter.
These remain modeling decisions requiring sources or a separately approved
identification design. Do not infer the anion's sites from neutral AMP's 2B set,
or count a law estimated from NMR rows as independent evidence beside those rows.
