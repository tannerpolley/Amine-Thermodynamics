# PZ dielectric inputs and measurement residuals for #308

Read 11 November 2026 for the design revision. Current Zotero PDF bytes for Razavi `4L3HXHTI`, Hilliard `LB7LUETY`, Hamborg `334KGLPV`, Ermatchkov 2003 `BBMLF2KZ`, Ermatchkov 2006 `R3UZX4UN`, Hartono 2013 `SEPZQIPE`, Kim 2008 `4SMCK4SC`, Freeman 2010 `EXYPAS6E`, Kamps `VSVC3FEB`, Derks `MTKZ5MEF`, Fosbøl `VVP244A8` and Yi `3YP4GUWT` match the hashes in `pdf-identities.json`. Text was extracted into temporary files for reading; no full paper was committed or attached. Exact numerical passages were checked in the PDF text layer. The main-checkout shelf README/index and current hash-matching Baygi 2015 and Wangler 2018 Markdown companions were read; this worktree has no literature shelf.

## Dielectric evidence and the adopted fallback

The existing project corpus and live library search were inspected before external searches for PZ dielectric data. Hilliard 2008 §6, printed pp.118–119, PDF pp.175–176, Eqs.6-2–6-5 is a concrete PZ estimate:

$$D_{PZ}=4.25+1532\,[1/T-1/(298.15\,K)].$$

Hilliard states that PZ was assumed equivalent to piperidine owing to limited data, using CRC (2004) and correcting to one PZ experimental point. This is an analog-derived pure permittivity slope, not a set of PZ mixture density/permittivity measurements that determines the adopted density-dependent Engine dielectric_volume/dielectric_temperature pair. The primary PZ point, its uncertainty and isotope/composition conditions were not recovered in this bounded search. Do not silently fit those Engine coefficients to the analog law. No HPZCOO permittivity measurement was found in the inspected corpus, source PDFs or search results. This is a bounded evidence gap, not proof that none exists anywhere.

Under the owner's explicit fallback, fix PZ and HPZCOO to adopted neutral MEA dielectric_volume 0.7309865858310542 L/mol and dielectric_temperature 1019.0802597119892 K. Values were read from the SHA-256 f8f64820…eef97 document. They are transferred coefficients; no scientific claim of equal permittivity is made. Low-temperature ionic activity, Born solvation and the zwitterion contribution remain conditional on this assumption. No dielectric fitting is authorized here.

## NMR observations

Ermatchkov 2003 §2 pp.1278–1281 reports D2O, 121 experiments at 283/298/313/333 K, about 0.1–1.5 mol/kg PZ. Peak 2 represents the three uncarbamated protonation states; peaks 1+4 the monocarbamate plus protonated monocarbamate; peak 3 the dicarbamate. Eqs.1–7 give A1=A4=4k n_mono, A2=8k n_free, A3=8k n_di, k=sum(A)/(8 n_PZtotal). All groups share the normalization; there are two independent fractions, not three independent observations.

The consistency of separate A1/A4 determinations with their sum is about (2±1.9)% (p.1281); repeated group determinations differed by no more than 1%. Neither statement supplies a measured covariance matrix or a species detection threshold. The design's peak-independence propagation is a declared assumption, with a 3.9% sensitivity calculation, not a source standard deviation. Ten blank dicarbamate cells in Tables 1–4 are not measured zeroes; no numeric upper bound is printed. Omit only that observation; retain the monocarbamate group, analytical total and original blank. Do not derive a third fraction from rounded cells and call it measured.

## Pressure uncertainty

Ermatchkov 2006 Results p.1789 distinguishes the total uncertainty beside each p2 from the repeatability column Delta p2,repr. The prose decomposes total uncertainty into propagated T/composition uncertainty plus 0.02p calibration. That decomposition must not be added to the total in parentheses. The review calls the adopted total Delta p*: operationally bind the source column and parentheses, not just a symbol. Use it exactly once; retain repeatability separately. Temperature/molarity sensitivity may be reported as diagnosis, not added again to this total scale. Source-scaled agreement is not a probabilistic confidence test unless the source error interpretation warrants it.

Hartono 2013 §2 pp.152–153 and Table 6 p.156: binary liquid/vapor samples are acid-titrated; 1H-NMR is used for resolving ternary amine mixtures. The less-than-2% NMR statement must not be relabeled binary titration uncertainty. Kim 2008 apparatus pp.2526/2528 supplies T ±0.05 K and controller P ±0.3 kPa. Its standard-solution titration repeatability is less than 1% for three parallel titrations (p.2528), which the design proposes as an analog method scale, not Hartono total PZ accuracy; applicability to dilute PZ vapor condensate remains a limitation. Four-decimal y imposes ±0.00005 rounding half-width, a relative half-width of 12.5% at y=0.0004. A uniform rounding model has standard scale 0.00005/sqrt(3). Multiplying y by P shares the same measured pressure; transformed pressure residuals need the covariance in the design. Independent P and y coordinates avoid that algebraic double-counting, but not unknown campaign-common calibration error.

## Assessment convention and limits

Baygi 2015 §3.1 Eqs.8–10 fits neutral MEA parameters to compiled saturation correlations and reports aggregate property deviations; its reactive comparisons are on a different model. Wangler 2018 §§3.1,6.1–6.2 distinguishes ion representations, fits binary/osmotic data, and predicts gas solubility without fitting ternary gas-solubility data. Neither establishes a universal PZ acceptance percentage or an uncertainty covariance for these measurements. The #308 owner instead requires source-uncertainty reporting and owner decisions on consequential continuation. The design implements that policy while identifying engineering search limits separately from measured uncertainty.
