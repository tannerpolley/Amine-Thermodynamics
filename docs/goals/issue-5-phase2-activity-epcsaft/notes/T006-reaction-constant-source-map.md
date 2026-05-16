# T006 Reaction Constant Source Map

Superseded status note: T008 narrowed this blocker after the operator supplied local paper Markdown sources and Zotero lookup was performed. R1-R5 now have local Nasrifar/Austgen H3O+-basis candidate rows, but they remain unpromoted until the original reference-state convention is verified.

## Scope

Scout task T006 checked local sources only. No public web search was used. Zotero Desktop local API preferences were enabled, but the local API was not running on `127.0.0.1:23119`, so Zotero search could not be used.

## Local Sources Checked

- `data/reference/MEA/manifests/phase2_reaction_constant_manifest.csv`
- `data/reference/MEA/manifests/reaction_constant_manifest.csv`
- `docs/roadmaps/phase2_reaction_constant_basis.md`
- `docs/roadmaps/reaction_constant_convention_plan.md`
- `docs/papers/md/Baygi and Pahlavanzadeh - 2015 - Application of the PC-SAFT equation of state for modeling CO2 solub.md`
- `docs/papers/md/Uyan et al.md`
- `docs/papers/md/Wangler et al.md`
- `docs/papers/md/Wong et al. - 2015 - Chemical speciation of CO2 absorption in aqueous monoethanolamine investigated by in situ Raman spec.md`
- `docs/latex/references.bib`
- `data/reference/MEA/manifests/source_status_manifest.csv`
- `data/reference/MEA/pH/`
- `data/reference/MEA/ionic_activity/`
- `data/reference/MEA/dielectric/`

## Findings By Reaction

| Reaction | Status | Evidence | Safe next action |
|---|---|---|---|
| R1 water autoprotolysis | local activity-candidate found, not promoted | Uyan Table 1 and Wangler Table 2 give `K_a` forms with activity coefficients for the shared water reaction; Baygi Table 4 remains the Phase 1 apparent/mole-fraction basis. | Add a separate candidate manifest row and require a Worker convention check before changing the canonical Phase 2 manifest. |
| R2 CO2 hydration to bicarbonate | local activity-candidate found, not promoted | Uyan/Wangler give activity-based carbonate-system constants with ePC-SAFT activity coefficients; Baygi/Edwards values are apparent Phase 1 inputs. | Add candidate values, record source and standard-state caveat, and keep equilibrium solves blocked until all reactions are ready. |
| R3 bicarbonate dissociation | local activity-candidate found, not promoted | Uyan/Wangler give activity-based carbonate-system constants; carbonate activity remains sensitive to the selected ion parameters and standard state. | Add candidate values, then validate sign/stoichiometry before promotion. |
| R4 carbamate hydrolysis | blocked by original source/convention | Local Baygi text says the MEA carbamate-hydrolysis constant was reported on a molality basis and converted for the ideal Smith-Missen workflow. No local source proves a thermodynamic-activity constant for MEACOO- hydrolysis. | Requires original Tong/Austgen/source inspection or user-approved source search before activity solve. |
| R5 MEAH+ dissociation | needs original source lookup | Baygi/Bates supplies Phase 1 apparent/mole-fraction coefficients; Uyan/Wangler MDEA protonation constants are useful analogs but are not MEA constants. | Requires original Bates/Pinching or other MEA protonation source with reference-state convention before activity solve. |

## Conclusion

At the time of T006, the available local source set was enough to create a source-backed candidate artifact for R1-R3 and to document exact blockers for R4-R5. T008 later superseded that source map by finding local Nasrifar/Austgen H3O+-basis candidate rows for all R1-R5. The constants are still not enough to mark the canonical manifest as `converted` or `thermodynamic_activity`, so Phase 2 equilibrium, parity, and figure outputs must stay blocked until the reference-state convention is verified.
