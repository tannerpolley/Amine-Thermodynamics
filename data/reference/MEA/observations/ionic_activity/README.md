# Ionic-activity evidence

Direct MEAH+ salt and binary electrolyte evidence used by MEA #121 (model D binary fits). Sources, hashes and admission limits are in `ionic_activity_source_manifest.csv`.

| File | Rows | Content | Use |
|---|---:|---|---|
| `peiper_pitzer_1982_nahco3_osmotic.csv` | 60 | NaHCO3 water activity and osmotic coefficients, 278.15-318.15 K, 0.001-1.000 mol/kg; values evaluated from the source Pitzer-model fit | B1, water-HCO3- |
| `lee_lee_1998_mea_hcl_vapor_pressure.csv` | 110 | Vapor pressures of 2-hydroxyethylammonium (MEAH+) chloride solutions, 298.15-333.15 K, 0.097-10.014 mol/kg, and the source's pure-water rows | 94 rows at m >= 1.0 mol/kg: Route B fit B2 and Route A out-of-fit comparison; 5 pure-water rows: p_sat,obs reference; 11 rows below 1.0 mol/kg: unused (#121 decision 9) |

No direct carbamate-salt (MEACOO-) activity dataset is known. Analog salts must be labelled as analogs. Do not add estimated or fabricated rows.
