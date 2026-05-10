# Source Log

This source log records the manuscript's verified citation anchors and intended use. Bibliographic entries are stored in `references.bib`.

| Citation key | Status | Use in manuscript |
| --- | --- | --- |
| `Gross2001` | Peer-reviewed article | Original PC-SAFT hard-chain/dispersion foundation. |
| `Gross2002` | Peer-reviewed article | Associating PC-SAFT extension for hydrogen-bonding species. |
| `Cameretti2005` | Peer-reviewed article | Original ePC-SAFT aqueous electrolyte foundation. |
| `Bulow2020` | Peer-reviewed article | ePC-SAFT advanced concentration-dependent dielectric/Born formulation. |
| `Bulow2021` | Peer-reviewed article | ePC-SAFT advanced salt-solubility and ion-pairing extension. |
| `Schick2023` | Peer-reviewed article | ePC-SAFT advanced CO2 solubility in electrolyte solutions. |
| `Rueben2024` | Peer-reviewed article | Recent permittivity modeling in electrolyte PC-SAFT. |
| `Figiel2025` | Peer-reviewed article | Modified Born term for ion thermodynamic properties. |
| `Hajj2024` | Peer-reviewed article | Dielectric-dispersion evidence for loaded 30 wt% MEA; motivates MEA-specific relative-permittivity validation. |
| `Uyan2015` | Peer-reviewed article; markdown paper in `docs/papers/md` | ePC-SAFT amine-solubility precedent with explicit ionic species and predictive VLE framing. |
| `Wangler2018` | Peer-reviewed article; markdown paper in `docs/papers/md` | Amine ePC-SAFT parameter-table and fitted-vs-predictive structure; binary-interaction regression against independent data. |
| `Bulow2020`, `Bulow2021` | Peer-reviewed articles; markdown paper context in `docs/papers/md` | Advanced ePC-SAFT/Born-term framing and reduced binary-parameter philosophy. |
| `MacDowell2010` | Peer-reviewed article | SAFT-VR modeling of CO2 in aqueous MEA. |
| `Nasrifar2010` | Peer-reviewed article | PC-SAFT modeling of acid-gas aqueous ethanolamine systems. |
| `Baygi2015` | Peer-reviewed article | PC-SAFT CO2 solubility in aqueous MEA and neutral parity comparison. |
| `Pakravesh2025a` | Peer-reviewed article | Recent SAFT-family alkanolamine thermodynamic modeling context. |
| `Aronu2011`, `Hilliard2008`, `Jou1995`, `Mamun2005`, `Xu2011` | Literature data sources | VLE evidence basis. |
| `Bottinger2008`, `Jakobsen2005`, `Matin2012` | Literature data sources | NMR/speciation evidence basis. |

## Parameter Audit Notes

- Held/Uyan ion tables provide the promoted diagnostic sigma/dispersion values for `H3O+`, `OH-`, `HCO3-`, and `CO3^2-`; the promoted water-ion interaction values are `0.25`, `-0.25`, `0.0`, and `-0.25`, respectively.
- Figiel2025 provides the SSM+DS Born diameter for the proton carrier (`H+` represented in the runtime as `H3O+`) as `d_born=1.218`.
- No local ePC-SAFT table value was found for SSM+DS `d_born` of `OH-`. The promoted value is now `d_born=3.081076894`, derived by Born hydration-energy inversion from an absolute hydroxide hydration free energy of `106.4 kcal/mol`; the derivation artifact is `analyses/epcsaft_ionic_regression/results/oh_born_derivation/`.
- No local table value was found for SSM+DS `d_born` of `HCO3-` or `CO3^2-`, but a Tier A trace-carbonate Born fit returned `HCO3- d_born=2.9990` and `CO3^2- d_born=2.9998`, supporting retention of the promoted `3.0` values.
