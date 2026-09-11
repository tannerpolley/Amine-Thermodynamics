# Full Component Parameter Source Audit

Scope:
- Local source digests in `docs/papers/md/*.md`
- `docs/latex/source_log.md`
- `docs/latex/references.bib`
- Historical parameter evidence under `data/reference/MEA/` and retained analysis results

Rules used for this audit:
- Do not fabricate missing parameter values.
- If a markdown digest mentions a parameter set but does not print the table values, treat it as "check cited table/reference".
- Deleted local parameter CSV paths below are historical locators only; they are not active parameter authority.
- The selected JSON under `analyses/mea_parameter_bundle/results/` owns the
  exploratory incumbent mapping; its notebook interprets retained replay
  evidence. Engine issues own generic method work and retained cross-repository evidence.

## Summary

The retired MEA ionic calculation used mixed provenance. The exploratory
mapping and its evidence classes are now owned by
`analyses/mea_parameter_bundle/`; this audit preserves the source lineage below:

- CO2 and H2O still come from literature seed rows.
- Neutral MEA is a literature-backed molecular fit.
- MEAH+ and MEACOO- retain outputs from a May 2026 local-speciation fit. Git history preserves the fit inputs and results, but the fit was not pressure-coupled and is not adopted as an active parameter authority.
- HCO3-, CO3^2-, H3O+, and OH- were diagnostic/transfer ions whose historical sigma/dispersion values came from the Held/Uyan ePC-SAFT ion tables. H3O+ used an SSM+DS Born diameter from Figiel 2025, HCO3- and CO3^2- have a trace-carbonate Born diagnostic around `3.0/3.0` plus an unanchored bicarbonate-sensitive alternative, and OH- has a Born hydration-energy derivation record supporting the historical diagnostic `d_born=3.081076894`.

The historical calculation's retained binary interactions were sparse
(read the selected JSON for present exploratory values):

- `k_ij(MEA,H2O) = -0.052`
- `k_ij(MEAH+,MEACOO-) = -0.00201813457644`
- The historical calculation transferred Held/Uyan water-ion interactions for H3O+, OH-, HCO3-, and CO3^2-.
- Its remaining MEA-specific ionic binary terms were zero.

## Species Audit

| Species | Candidate parameter sources | Exact MEA or analog / transfer | Parameter types covered | Historical diagnostic source / value status | Gap or fitting need | Evidence anchors |
| --- | --- | --- | --- | --- | --- | --- |
| CO2 | `Gross2001`; `Gross2002`; `Schick2023` Table 2; carried forward in `Uyan et al.` Table 3 and `Wangler et al.` Table 4 | Exact molecular PC-SAFT seed plus temperature-dependent ePC-SAFT permittivity correlation | `m,s,e,dielc(T),MW` | Deleted historical CSV row used `m=2.079`, `s=2.7852`, `e=169.21`, `dielc=1.4122`, and `MW=0.04401`; `1.4122` is exactly Schick's `dielc(T)=-0.0036 T+2.467` evaluated at 293 K, not a source-supported constant | The full 123-state comparison selects Uyan solvent-only mixing, so CO2 permittivity is not an active coordinate; Schick remains retained comparison evidence | Zotero item `V9MAIE7D`, main PDF `WVKUKNLW`, Table 2 on PDF page 4; `analyses/mea_parameter_bundle/results/permittivity-formulation-comparison.json`; `literature/Uyan2015--9C7EACSK.md`; `literature/Wangler2018--RIUUBS2B.md`; `docs/latex/source_log.md`; `docs/latex/references.bib` |
| H2O | `Fuchs2006` in `Uyan et al.`; `Diamantonis2012` in `Wangler et al.`; `Held2008` / `Figiel2025` in the source log chain | Exact solvent seed, plus dielectric / Born transfer support | `m,s(T),e,e_assoc,association,vol_a,dielc,f_solv,MW` | Deleted historical CSV row used `m=1.2047`, `s(T)=sigma=2.7927+(10.11*exp(-0.01775*T)-1.417*exp(-0.01146*T))`, `e=353.95`, `e_assoc=2425.7`, `vol_a=0.04509`, `assoc_scheme=2B`, `dielc=78.09`, `f_solv=1.5`, `MW=0.01801528` | The exploratory incumbent’s solvent-only mixing uses the retained water correlation; loaded-MEA dielectric validation remains unresolved | `literature/Uyan2015--9C7EACSK.md`; `literature/Wangler2018--RIUUBS2B.md`; `docs/latex/source_log.md`; `docs/latex/references.bib` |
| MEA | `Najafloo and Zarei 2018`; `Nasrifar and Tafazzol 2010`; deleted historical MEA parameter row | Exact MEA molecular fit | `m,s,e,e_assoc,vol_a,assoc_scheme,MW` | Historical row used `m=3.0353`, `s=3.0435`, `e=277.174`, `e_assoc=2586.3`, `vol_a=0.03747`, `assoc_scheme=2B`, `MW=0.06108` | The exploratory incumbent’s solvent-only mixing uses $\epsilon_r=32$; temperature dependence and loaded-mixture validation remain unresolved | `docs/papers/md/Najafloo and Zarei - 2018 - Modeling solubility of CO2 in aqueous monoethanolamine (MEA) solution us.md`; `docs/papers/md/Nasrifar and Tafazzol - 2010 - Vapor-liquid equilibria of acid gas-aqueous ethanolamine solutions us.md`; `docs/latex/source_log.md` |
| MEAH+ | `Uyan et al.` and `Wangler et al.` provide the MDEAH+ analog lineage; MEA NMR data provide fit/evaluation targets | Analog starting context plus retained local-speciation fit | `s,e,d_born,dielc,f_solv,z,MW` | The May 2026 fit started from `s=3.563`, `e=228.71`, and `d_born=3.563` and returned `s=3.48508556586`, `e=232.687201645`, and `d_born=3.53322927146`; the historical calculation used `dielc=8`, `f_solv=1`, `z=+1`, and `MW=0.06209` | The fit used 8 states / 22 residuals, improved log-RMSE only from `0.2714` to `0.2677`, had two final failures, and was not pressure-coupled; retain as provisional local-fit evidence, not an accepted pure-ion row | Git commit `897bb6e`; `literature/Uyan2015--9C7EACSK.md`; `literature/Wangler2018--RIUUBS2B.md`; `docs/latex/source_log.md` |
| MEACOO- | `Matin2012`; `Jakobsen2005`; `Bottinger2008`; MDEA-lineage analog context in `Uyan et al.` and `Wangler et al.` | Direct MEA fit/evaluation evidence plus retained local-speciation fit | `s,e,d_born,kij,dielc,f_solv,z,MW` | The May 2026 fit started from `s=3.5605`, `e=533.11`, `d_born=3.5605`, and `k_ij=0` and returned `s=3.53543525721`, `e=453.265244384`, `d_born=3.54107030822`, and `k_ij(MEAH+,MEACOO-)=-0.00201813457644`; the historical calculation used `dielc=8`, `f_solv=1`, `z=-1`, and `MW=0.10408` | Exact literature pure-ion values are not printed in the digests; the retained local fit is limited by the same 8-state / 22-residual, two-failure, non-pressure-coupled boundary | Git commit `897bb6e`; `literature/Uyan2015--9C7EACSK.md`; `literature/Wangler2018--RIUUBS2B.md`; `docs/latex/source_log.md` |
| HCO3- | `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.`; trace-carbonate Born full-data diagnostic | Analog / diagnostic set with direct trace check | `s,e,d_born,dielc,f_solv,z,MW,kij` | Historical calculation used `m=1`, `s=2.9296`, `e=70`, `d_born=3`, `dielc=8`, `f_solv=1`, `z=-1`, `MW=0.0610168`, and `water-HCO3- k_ij=0.0` | The unanchored multistart diagnostic found a lower trace-only residual at `HCO3- d_born=6.80294` and `CO3^2- d_born=2.99744`; this is an identifiability warning, not an active value | `literature/Uyan2015--9C7EACSK.md` Tables 4-5; Held 2014 Table 2 through the ePC-SAFT source digest; `analyses/reactive_epcsaft_parameter_evidence/results/trace_carbonate_born_regression` |
| CO3^2- | `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.`; trace-carbonate Born full-data diagnostic | Analog / diagnostic set with direct trace check | `s,e,d_born,dielc,f_solv,z,MW,kij` | Historical calculation used `m=1`, `s=2.4422`, `e=249.26`, `d_born=3`, `dielc=8`, `f_solv=1`, `z=-2`, `MW=0.06001`, and `water-CO3^2- k_ij=-0.25` | The unanchored multistart diagnostic left CO3^2- near `d_born=3.0` while moving HCO3-; this does not prove independent carbonate identifiability | `literature/Uyan2015--9C7EACSK.md` Tables 4-5; Held 2014 Table 2 through the ePC-SAFT source digest; `analyses/reactive_epcsaft_parameter_evidence/results/trace_carbonate_born_regression` |
| H3O+ | `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.` | Analog / diagnostic set with direct SSM+DS Born value | `s,e,d_born,dielc,f_solv,z,MW,kij` | Historical calculation used `m=1`, `s=3.4654`, `e=500`, `d_born=1.218`, `dielc=8`, `f_solv=1`, `z=+1`, `MW=0.01902`, and `water-H3O+ k_ij=0.25` | No direct MEA-system hydronium fit is identifiable from the MEA speciation targets | `literature/Uyan2015--9C7EACSK.md` Tables 4-5; Figiel 2025 Table 3; `docs/latex/source_log.md` |
| OH- | `Held2008`; `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.`; `Jacobs1985`; hydroxide hydration-energy literature lead | Analog / diagnostic set with hydration Born derivation | `s,e,d_born,dielc,f_solv,z,MW,kij` | Historical calculation used `m=1`, `s=2.0177`, `e=650`, `d_born=3.081076894`, `dielc=8`, `f_solv=1`, `z=-1`, `MW=0.01701`, and `water-OH- k_ij=-0.25`; `d_born` came from Born hydration-energy inversion | The local MEA speciation targets do not directly identify OH- | `literature/Uyan2015--9C7EACSK.md` Tables 4-5; Held 2014 Table 2 through the ePC-SAFT source digest; `analyses/reactive_epcsaft_parameter_evidence/results/oh_born_derivation` |

## Binary Interaction Notes

The retired calculation used this sparse binary-interaction mapping:

- `MEA-H2O = -0.052`
- `MEAH+-MEACOO- = -0.00201813457644`
- `H2O-H3O+ = 0.25`
- `H2O-OH- = -0.25`
- `H2O-HCO3- = 0.0`
- `H2O-CO3^2- = -0.25`
- All other retained ionic `k_ij` entries are zero

This documents the retired calculation:

- MEA and water are the only retained neutral-pair interaction that is already explicit.
- The ion-pair interaction is a provisional fixed input rather than a current fit result.
- The bicarbonate / carbonate / hydronium / hydroxide water-ion terms followed Held/Uyan ePC-SAFT values; none is active MEA authority.

## Evidence Quality Caveat

Some markdown digests only state that a parameter set was taken from literature or transferred from a prior paper, but do not print the numerical table. For those cases, the audit treats the markdown as provenance only and leaves the exact numbers to the cited table or historical Git record. That applies most strongly to the transfer-heavy ion rows.
