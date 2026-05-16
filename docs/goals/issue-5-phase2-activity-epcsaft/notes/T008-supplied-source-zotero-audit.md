# T008 Supplied Source And Zotero Audit

## Result

The operator supplied local paper Markdown sources for the R4/R5 blocker. The blocker has narrowed from `source missing` to `reference-state promotion pending`.

## Local Paper Findings

- `Nasrifar and Tafazzol - 2010 - Vapor-liquid equilibria of acid gas-aqueous ethanolamine solutions us.md` is the primary local candidate source for the current MEA H3O+ reaction basis.
- Nasrifar Table 1 lists R1-R10 mole-fraction equilibrium constants and traces them to Austgen et al. (1991). The table includes the current MEA reactions:
  - R1 water autoprotolysis: `2 H2O <-> OH- + H3O+`
  - R2 bicarbonate formation: `CO2 + 2 H2O <-> HCO3- + H3O+`
  - R3 carbonate formation: `HCO3- + H2O <-> CO3^2- + H3O+`
  - R4 MEA carbamate hydrolysis: `MEACOO- + H2O <-> MEA + HCO3-`
  - R5 MEAH+ dissociation: `MEAH+ + H2O <-> MEA + H3O+`
- Nasrifar Equation 11 uses `prod((x_j gamma_j) ** nu_j)` for the reaction constants, which makes it the closest local source to an activity-coefficient-compatible MEA reaction set.
- Nasrifar later sets `gamma_i = 1` for the predictive PC-SAFT calculation. That means the table is a candidate source, not an automatic promotion to the final Phase 2 activity solve.
- `Uyan et al.md`, `Wangler et al.md`, `Bülow et al.md`, and `Cleeton et al.md` are method evidence for ePC-SAFT activity coefficients and reference-state normalization, but they are MDEA/H+ convention sources and must not be directly substituted for MEA R4/R5.
- `Baygi and Pahlavanzadeh - 2015 ... MEA ... .md` remains the Phase 1 apparent-basis source path and documents the risk of the previous R4 molality-to-mole-fraction conversion.
- `Wong et al. - 2015 ... Raman spec.md` is validation/speciation evidence, not a reaction-constant source.
- `Amundsen ... Density and viscosity ... .md` and the Amundsen appendix are physical-property validation evidence, not reaction-constant sources.

## Zotero Findings

Zotero local API was running and searched successfully.

Found:

- Wong 2015: `CJ45LPAQ`
- Amundsen 2009 density/viscosity: `3QJR6RHH`
- Baygi 2015: `B8EJJPCJ`
- Najafloo/Zarei 2018: `7MICDGGJ`
- Nasrifar/Tafazzol 2010: `CBRPAXQG`
- Pahlavanzadeh/Fakouri Baygi 2013: `DUAIHQ7Y`
- Pakravesh/Zarei 2025: `ABY3LIRG`
- Schick et al. 2023: `V9MAIE7D`
- Cleeton et al. 2020: `MMI98GID`
- Uyan et al. 2015: `GSLTFVDM`
- Wangler et al. 2018: `ZILDPWWE`

Not found in Zotero by local search:

- Austgen et al. 1991, the primary source cited by Nasrifar Table 1
- Austgen et al. 1989
- Bates and Pinching 1951
- Tong et al. 2012
- Bülow et al. 2021
- The Amundsen/Dag appendix as a separate item

## Implementation Consequence

Update the machine-readable candidate manifest so R1-R5 all have local H3O+-basis candidate rows from Nasrifar/Austgen. Keep the canonical reaction manifest at `not_converted` until Austgen or another primary reference-state source is inspected. Do not generate `phase2_equilibrium_results.csv` yet.
