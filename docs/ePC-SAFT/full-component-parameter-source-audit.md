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
- Engine Issue #80 owns the next direct calculation and validated immutable packet.

## Summary

The retired MEA ionic calculation used mixed provenance; none of the values below are active parameter authority:

- CO2 and H2O still come from literature seed rows.
- Neutral MEA is a literature-backed molecular fit.
- MEAH+ and MEACOO- had provisional fixed values from an exploratory historical calculation; the repository does not reproduce or adopt that fit.
- HCO3-, CO3^2-, H3O+, and OH- were diagnostic/transfer ions whose historical sigma/dispersion values came from the Held/Uyan ePC-SAFT ion tables. H3O+ used an SSM+DS Born diameter from Figiel 2025, HCO3- and CO3^2- have a trace-carbonate Born diagnostic around `3.0/3.0` plus an unanchored bicarbonate-sensitive alternative, and OH- has a Born hydration-energy derivation artifact supporting the historical diagnostic `d_born=3.081076894`.

The retained binary interactions are also sparse:

- `k_ij(MEA,H2O) = -0.052`
- `k_ij(MEAH+,MEACOO-) = -0.00201813457644`
- The historical calculation transferred Held/Uyan water-ion interactions for H3O+, OH-, HCO3-, and CO3^2-.
- Its remaining MEA-specific ionic binary terms were zero.

## Species Audit

| Species | Candidate parameter sources | Exact MEA or analog / transfer | Parameter types covered | Historical diagnostic source / value status | Gap or fitting need | Evidence anchors |
| --- | --- | --- | --- | --- | --- | --- |
| CO2 | `Gross2001`; `Gross2002`; carried forward in `Uyan et al.` Table 3 and `Wangler et al.` Table 4 | Exact molecular PC-SAFT seed | `m,s,e,dielc,MW` | Deleted historical CSV row used `m=2.079`, `s=2.7852`, `e=169.21`, `dielc=1.4122`, `MW=0.04401`; no CO2-specific binary fit was retained | No active packet; a future packet must state its selected source and mixing terms | `docs/papers/md/Uyan et al.md`; `docs/papers/md/Wangler et al.md`; `docs/latex/source_log.md`; `docs/latex/references.bib` |
| H2O | `Fuchs2006` in `Uyan et al.`; `Diamantonis2012` in `Wangler et al.`; `Held2008` / `Figiel2025` in the source log chain | Exact solvent seed, plus dielectric / Born transfer support | `m,s(T),e,e_assoc,association,vol_a,dielc,f_solv,MW` | Deleted historical CSV row used `m=1.2047`, `s(T)=sigma=2.7927+(10.11*exp(-0.01775*T)-1.417*exp(-0.01146*T))`, `e=353.95`, `e_assoc=2425.7`, `vol_a=0.04509`, `assoc_scheme=2B`, `dielc=78.09`, `f_solv=1.5`, `MW=0.01801528` | No active packet; MEA-mixture dielectric behavior was not directly regressed from MEA data | `docs/papers/md/Uyan et al.md`; `docs/papers/md/Wangler et al.md`; `docs/latex/source_log.md`; `docs/latex/references.bib` |
| MEA | `Najafloo and Zarei 2018`; `Nasrifar and Tafazzol 2010`; deleted historical MEA parameter row | Exact MEA molecular fit | `m,s,e,e_assoc,vol_a,assoc_scheme,MW` | Historical row used `m=3.0353`, `s=3.0435`, `e=277.174`, `e_assoc=2586.3`, `vol_a=0.03747`, `assoc_scheme=2B`, `MW=0.06108` | No active packet; no direct dielectric or Born value was attached to the neutral MEA row | `docs/papers/md/Najafloo and Zarei - 2018 - Modeling solubility of CO2 in aqueous monoethanolamine (MEA) solution us.md`; `docs/papers/md/Nasrifar and Tafazzol - 2010 - Vapor-liquid equilibria of acid gas-aqueous ethanolamine solutions us.md`; `docs/latex/source_log.md` |
| MEAH+ | `Uyan et al.` and `Wangler et al.` transfer MDEAH+ from the MDEA lineage; MEA NMR data provide evaluation targets | Analog / transfer context plus provisional historical value | `s,e,d_born,dielc,f_solv,z,MW` | Historical calculation used `m=1`, `s=3.48508556586`, `e=232.687201645`, `d_born=3.53322927146`, `dielc=8`, `f_solv=1`, `z=+1`, `MW=0.06209` | The literature digest does not give an exact MEA MEAH+ pure table, and the repository does not reproduce a fit; retain only as historical evidence | `docs/papers/md/Uyan et al.md`; `docs/papers/md/Wangler et al.md`; `docs/latex/source_log.md` |
| MEACOO- | `Matin2012`; `Jakobsen2005`; `Bottinger2008`; analog MDEA-lineage transfer in `Uyan et al.` and `Wangler et al.` | Direct MEA evaluation evidence plus provisional historical value | `s,e,d_born,kij,dielc,f_solv,z,MW` | Historical calculation used `m=1`, `s=3.53543525721`, `e=453.265244384`, `d_born=3.54107030822`, `dielc=8`, `f_solv=1`, `z=-1`, `MW=0.10408`, and `k_ij(MEAH+,MEACOO-)=-0.00201813457644` | Exact literature pure-ion values are not printed in the digests, and the repository does not reproduce a fit; the NMR data evaluate rather than establish these values | `docs/papers/md/Uyan et al.md`; `docs/papers/md/Wangler et al.md`; `docs/latex/source_log.md` |
| HCO3- | `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.`; trace-carbonate Born full-data diagnostic | Analog / diagnostic set with direct trace check | `s,e,d_born,dielc,f_solv,z,MW,kij` | Historical calculation used `m=1`, `s=2.9296`, `e=70`, `d_born=3`, `dielc=8`, `f_solv=1`, `z=-1`, `MW=0.0610168`, and `water-HCO3- k_ij=0.0` | The unanchored multistart diagnostic found a lower trace-only residual at `HCO3- d_born=6.80294` and `CO3^2- d_born=2.99744`; this is an identifiability warning, not an active value | `docs/papers/md/Uyan et al.md` Tables 4-5; Held 2014 Table 2 through the ePC-SAFT source digest; `analyses/reactive_epcsaft_parameter_evidence/results/trace_carbonate_born_regression` |
| CO3^2- | `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.`; trace-carbonate Born full-data diagnostic | Analog / diagnostic set with direct trace check | `s,e,d_born,dielc,f_solv,z,MW,kij` | Historical calculation used `m=1`, `s=2.4422`, `e=249.26`, `d_born=3`, `dielc=8`, `f_solv=1`, `z=-2`, `MW=0.06001`, and `water-CO3^2- k_ij=-0.25` | The unanchored multistart diagnostic left CO3^2- near `d_born=3.0` while moving HCO3-; this does not prove independent carbonate identifiability | `docs/papers/md/Uyan et al.md` Tables 4-5; Held 2014 Table 2 through the ePC-SAFT source digest; `analyses/reactive_epcsaft_parameter_evidence/results/trace_carbonate_born_regression` |
| H3O+ | `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.` | Analog / diagnostic set with direct SSM+DS Born value | `s,e,d_born,dielc,f_solv,z,MW,kij` | Historical calculation used `m=1`, `s=3.4654`, `e=500`, `d_born=1.218`, `dielc=8`, `f_solv=1`, `z=+1`, `MW=0.01902`, and `water-H3O+ k_ij=0.25` | No direct MEA-system hydronium fit is identifiable from the MEA speciation targets | `docs/papers/md/Uyan et al.md` Tables 4-5; Figiel 2025 Table 3; `docs/latex/source_log.md` |
| OH- | `Held2008`; `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.`; `Jacobs1985`; hydroxide hydration-energy literature lead | Analog / diagnostic set with hydration Born derivation | `s,e,d_born,dielc,f_solv,z,MW,kij` | Historical calculation used `m=1`, `s=2.0177`, `e=650`, `d_born=3.081076894`, `dielc=8`, `f_solv=1`, `z=-1`, `MW=0.01701`, and `water-OH- k_ij=-0.25`; `d_born` came from Born hydration-energy inversion | The local MEA speciation targets do not directly identify OH- | `docs/papers/md/Uyan et al.md` Tables 4-5; Held 2014 Table 2 through the ePC-SAFT source digest; `analyses/reactive_epcsaft_parameter_evidence/results/oh_born_derivation` |

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
