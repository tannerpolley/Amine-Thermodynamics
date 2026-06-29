# Full Component Parameter Source Audit

Scope:
- Local source digests in `docs/papers/md/*.md`
- `docs/latex/source_log.md`
- `docs/latex/references.bib`
- Current parameter CSVs under `data/reference/MEA/` and `data/reference/epcsaft_datasets/MEA_CO2_H2O_ionic_fit/`

Rules used for this audit:
- Do not fabricate missing parameter values.
- If a markdown digest mentions a parameter set but does not print the table values, treat it as "check cited table/reference".
- Treat `data/reference/epcsaft_datasets/MEA_CO2_H2O_ionic_fit/pure/any_solvent.csv` and the matching binary CSVs as the current promoted values.

## Summary

The current MEA ionic lane uses a mixed provenance:

- CO2 and H2O still come from literature seed rows.
- Neutral MEA is a literature-backed molecular fit.
- MEAH+ and MEACOO- are now fit against real MEA speciation data, with the MDEA ePC-SAFT lineage used only as the analog/transfer starting point.
- HCO3-, CO3^2-, H3O+, and OH- are diagnostic/transfer ions, but their promoted sigma/dispersion values now come from the Held/Uyan ePC-SAFT ion tables rather than generic placeholders. H3O+ also has a promoted SSM+DS Born diameter from Figiel 2025, HCO3- and CO3^2- have a trace-carbonate Born diagnostic showing that the regularized promoted values remain near `3.0/3.0` while an unanchored bicarbonate-sensitive alternative reduces the trace-only residual, and OH- has a Born hydration-energy derivation artifact supporting `d_born=3.081076894`.

The current promoted binary interactions are also sparse:

- `k_ij(MEA,H2O) = -0.052`
- `k_ij(MEAH+,MEACOO-) = -0.00201813457644`
- Held/Uyan water-ion interactions are promoted for H3O+, OH-, HCO3-, and CO3^2-.
- The remaining MEA-specific ionic binary terms in the promoted current CSV are zero unless fitted directly.

## Species Audit

| Species | Candidate parameter sources | Exact MEA or analog / transfer | Parameter types covered | Current selected source / value status | Gap or fitting need | Evidence anchors |
| --- | --- | --- | --- | --- | --- | --- |
| CO2 | `Gross2001`; `Gross2002`; carried forward in `Uyan et al.` Table 3 and `Wangler et al.` Table 4 | Exact molecular PC-SAFT seed | `m,s,e,dielc,MW` | Current promoted row in `data/reference/epcsaft_datasets/MEA_CO2_H2O_ionic_fit/pure/any_solvent.csv` is `m=2.079`, `s=2.7852`, `e=169.21`, `dielc=1.4122`, `MW=0.04401`; no CO2-specific binary fit in the promoted current CSV | No pure-component gap; binary mixing terms are handled separately | `docs/papers/md/Uyan et al.md`; `docs/papers/md/Wangler et al.md`; `docs/latex/source_log.md`; `docs/latex/references.bib` |
| H2O | `Fuchs2006` in `Uyan et al.`; `Diamantonis2012` in `Wangler et al.`; `Held2008` / `Figiel2025` in the current source log chain | Exact solvent seed, plus dielectric / Born transfer support | `m,s(T),e,e_assoc,association,vol_a,dielc,f_solv,MW` | Current promoted row in `any_solvent.csv` is `m=1.2047`, `s(T)=sigma=2.7927+(10.11*exp(-0.01775*T)-1.417*exp(-0.01146*T))`, `e=353.95`, `e_assoc=2425.7`, `vol_a=0.04509`, `assoc_scheme=2B`, `dielc=78.09`, `f_solv=1.5`, `MW=0.01801528` | Water is selected, but the MEA-mixture dielectric behavior is still not directly regressed from MEA data | `docs/papers/md/Uyan et al.md`; `docs/papers/md/Wangler et al.md`; `docs/latex/source_log.md`; `docs/latex/references.bib` |
| MEA | `Najafloo and Zarei 2018`; `Nasrifar and Tafazzol 2010`; the promoted current MEA row in `data/reference/epcsaft_datasets/MEA_CO2_H2O_ionic_fit/pure/any_solvent.csv` | Exact MEA molecular fit | `m,s,e,e_assoc,vol_a,assoc_scheme,MW` | Current promoted row is `m=3.0353`, `s=3.0435`, `e=277.174`, `e_assoc=2586.3`, `vol_a=0.03747`, `assoc_scheme=2B`, `MW=0.06108` | No direct dielectric or Born value is attached to the neutral MEA row; those belong to the ionic lane | `docs/papers/md/Najafloo and Zarei - 2018 - Modeling solubility of CO2 in aqueous monoethanolamine (MEA) solution us.md`; `docs/papers/md/Nasrifar and Tafazzol - 2010 - Vapor-liquid equilibria of acid gas-aqueous ethanolamine solutions us.md`; `docs/latex/source_log.md`; current `any_solvent.csv` |
| MEAH+ | `Uyan et al.` and `Wangler et al.` transfer MDEAH+ from the MDEA lineage; the current ionic regression fit is the MEA-specific source of truth | Analog / transfer starting point, then MEA-specific fit | `s,e,d_born,dielc,f_solv,z,MW` | Current promoted row is `m=1`, `s=3.48508556586`, `e=232.687201645`, `d_born=3.53322927146`, `dielc=8`, `f_solv=1`, `z=+1`, `MW=0.06209` | The literature digest does not give an exact MEA MEAH+ pure table; the promoted values are fit-derived and should stay tied to the ionic regression artifact | `docs/papers/md/Uyan et al.md`; `docs/papers/md/Wangler et al.md`; `docs/latex/source_log.md`; current `any_solvent.csv`; current `k_ij.csv` |
| MEACOO- | `Matin2012`; `Jakobsen2005`; `Bottinger2008`; analog MDEA-lineage transfer in `Uyan et al.` and `Wangler et al.` | Real MEA fit, built from analog / transfer seed behavior | `s,e,d_born,kij,dielc,f_solv,z,MW` | Current promoted row is `m=1`, `s=3.53543525721`, `e=453.265244384`, `d_born=3.54107030822`, `dielc=8`, `f_solv=1`, `z=-1`, `MW=0.10408`; current `k_ij(MEAH+,MEACOO-)=-0.00201813457644` | Exact literature pure-ion values are not printed in the markdown digests; the fit is the evidence-backed value source | `docs/papers/md/Uyan et al.md`; `docs/papers/md/Wangler et al.md`; `docs/latex/source_log.md`; `data/reference/MEA/ion_parameter_regression_sources.csv`; current `any_solvent.csv`; current `k_ij.csv` |
| HCO3- | `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.`; trace-carbonate Born full-data diagnostic | Analog / diagnostic set with direct trace check | `s,e,d_born,dielc,f_solv,z,MW,kij` | Promoted row is `m=1`, `s=2.9296`, `e=70`, `d_born=3`, `dielc=8`, `f_solv=1`, `z=-1`, `MW=0.0610168`; promoted `water-HCO3- k_ij=0.0` from Held/Uyan; regularized full-data fit retained `d_born=3.0` | The unanchored multistart diagnostic found a lower trace-only residual at `HCO3- d_born=6.80294` and `CO3^2- d_born=2.99744` with norm `0.68287` versus `0.70211` for the regularized promoted pair; this is an identifiability warning, not a promoted value, until pressure-weighted global optimization is feasible | `docs/papers/md/Uyan et al.md` Tables 4-5; Held 2014 Table 2 through the ePC-SAFT source digest; `analyses/phase3/ionic_epcsaft_regression/results/trace_carbonate_born_regression`; current `any_solvent.csv`; current `k_ij.csv` |
| CO3^2- | `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.`; trace-carbonate Born full-data diagnostic | Analog / diagnostic set with direct trace check | `s,e,d_born,dielc,f_solv,z,MW,kij` | Promoted row is `m=1`, `s=2.4422`, `e=249.26`, `d_born=3`, `dielc=8`, `f_solv=1`, `z=-2`, `MW=0.06001`; promoted `water-CO3^2- k_ij=-0.25` from Held/Uyan; regularized full-data fit retained `d_born=3.0` | The unanchored multistart diagnostic left CO3^2- near `d_born=3.0` while moving HCO3-; this supports keeping carbonate at the promoted Held/Uyan-compatible value but does not prove independent carbonate identifiability | `docs/papers/md/Uyan et al.md` Tables 4-5; Held 2014 Table 2 through the ePC-SAFT source digest; `analyses/phase3/ionic_epcsaft_regression/results/trace_carbonate_born_regression`; current `any_solvent.csv`; current `k_ij.csv` |
| H3O+ | `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.` | Analog / diagnostic set with direct SSM+DS Born value | `s,e,d_born,dielc,f_solv,z,MW,kij` | Promoted row is `m=1`, `s=3.4654`, `e=500`, `d_born=1.218`, `dielc=8`, `f_solv=1`, `z=+1`, `MW=0.01902`; promoted `water-H3O+ k_ij=0.25` using H+/H3O+ literature values | No direct MEA-system hydronium fit is identifiable from the MEA speciation targets; the proton carrier now uses exact literature s/e/k_ij and Figiel 2025 SSM+DS d_born rather than a placeholder | `docs/papers/md/Uyan et al.md` Tables 4-5; Figiel 2025 Table 3; `docs/latex/source_log.md`; current `any_solvent.csv`; current `k_ij.csv` |
| OH- | `Held2008`; `Held2014`; `Figiel2025`; `Uyan et al.`; `Wangler et al.`; `Jacobs1985`; hydroxide hydration-energy literature lead | Analog / diagnostic set with hydration Born derivation | `s,e,d_born,dielc,f_solv,z,MW,kij` | Promoted row is `m=1`, `s=2.0177`, `e=650`, `d_born=3.081076894`, `dielc=8`, `f_solv=1`, `z=-1`, `MW=0.01701`; promoted `water-OH- k_ij=-0.25` from Held/Uyan; `d_born` comes from Born hydration-energy inversion | The local MEA speciation targets do not directly identify OH-; a direct OH-sensitive dataset would be needed for a true MEA-system OH- fit | `docs/papers/md/Uyan et al.md` Tables 4-5; Held 2014 Table 2 through the ePC-SAFT source digest; `analyses/phase3/ionic_epcsaft_regression/results/oh_born_derivation`; current `any_solvent.csv`; current `k_ij.csv` |

## Binary Interaction Notes

The current promoted binary interaction CSV keeps the MEA ionic lane deliberately small:

- `MEA-H2O = -0.052`
- `MEAH+-MEACOO- = -0.00201813457644`
- `H2O-H3O+ = 0.25`
- `H2O-OH- = -0.25`
- `H2O-HCO3- = 0.0`
- `H2O-CO3^2- = -0.25`
- All other promoted ionic `k_ij` entries are zero

This matches the current workflow intent:

- MEA and water are the only promoted neutral-pair interaction that is already explicit.
- The ion-pair interaction is fit to the real MEA regression lane.
- The bicarbonate / carbonate / hydronium / hydroxide water-ion terms follow Held/Uyan ePC-SAFT values, while the MEA-specific trace-ion interactions remain unpromoted.

## Evidence Quality Caveat

Some markdown digests only state that a parameter set was taken from literature or transferred from a prior paper, but do not print the numerical table. For those cases, the audit treats the markdown as provenance only and leaves the exact numbers to the cited table or the current CSV. That applies most strongly to the transfer-heavy ion rows.
