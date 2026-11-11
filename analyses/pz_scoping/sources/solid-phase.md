# PZ solid phases and the liquid window

Checked 2026-11-02 for #237. Aqueous PZ precipitates solids at absorber-relevant conditions. **This assessment declares no qualified solid model.** The pinned Engine has SolidSpec; this supersedes the historical PhaseKind-only inference at `217026ab`. Source-observed liquid measurements can support comparisons at those states, but do not establish an interpolated or global liquid window.

## Unloaded PZ–water

Hilliard 2008, §5.3, PDF pp.144–150, measured solid–liquid transitions by DSC. Samples were heated from −20 to 125 °C at 5 °C/min, and the transition was assigned to the peak maximum (p.145). The peaks were assigned as follows (p.148):

- A: ice;
- B: piperazine hexahydrate PZ·6H2O;
- C: eutectic of PZ·6H2O and anhydrous PZ, 10–20 m;
- D: anhydrous PZ, above 20 m.

Reactions 5-1 and 5-2 are PZ·6H2O ⇌ PZ + 6 H2O and PZ(anh) ⇌ PZ (p.144–145). App. I.1 (PDF pp.1008–1009) tabulates 45 solidus/liquidus pairs for w_PZ = 0–0.771. The liquidus rises from 4.1 °C (pure water, as recorded) to a maximum of 50.9 °C near w_PZ = 0.459. The PZ·6H2O composition is w_PZ = 86.14/(86.14 + 6·18.015) = 0.444, computed from molar masses. The liquidus then falls to about 38 °C near w_PZ ≈ 0.60–0.63 (the E2 eutectic in Fig.5.3-3), and rises again toward anhydrous PZ.

Freeman et al. 2010 (DOI 10.1016/j.ijggc.2009.10.008, §3.1, p.120; Fig.2, p.121) report a eutectic near 19 m (60 wt %). They also give the solubility of anhydrous PZ at 20 °C as 14 wt %, which is 1.9 m. Their Fig.2 combines Dow (2001), Bishnoi (2000) and Hilliard (2008) data. Freeman's "anhydrous PZ" phrase probably refers to the anhydrous reagent dissolved in water, since the solid in equilibrium below 50 °C is the hexahydrate. That reading is an interpretation, not a statement in the paper.

Hilliard fitted a hexahydrate solubility constant on a mole-fraction basis with his eNRTL activities: Table 9.4-1, PDF p.341, ln K = A + B/T + C ln T + D T. Its equation labels (9-15, 9-16) do not match the text's Eqs.9-14/9-15. It is tied to that activity model and is not transferable to ePC-SAFT.

## Loaded PZ–CO2–water

- Freeman 2010 §3.1, p.120, Fig.1 p.121: transition temperature on slow cooling (1 °C per 5 min) for 8 and 10 m PZ versus loading. "For 8 m PZ, a CO2 loading of approximately 0.25 mole CO2 per mole of alkalinity is required to maintain a liquid solution without precipitation at room temperature (20 °C)." Rich-loading dashed lines mark solutions that stayed liquid. Values exist only in the figure: digitizing them would be a separate task.
- Hilliard did not measure loaded SLE (§5.3, p.150). §14.6 (PDF pp.644–646, Figs.14.6-1 to 14.6-3) **predicts** a hexahydrate boundary for 1–5 m with his eNRTL model. It suggests an operating range of 0.25–0.45 mol CO2/(2 mol PZ) for concentrated PZ. That is a model prediction, not data.
- Dugas & Rochelle 2011, p.2189: "PZ samples (12 m) with approximately 0.40 CO2 loading were not tested due to solubility limitations." A rich-side solid exists at 12 m. Its phase identity was not established in any source read here.
- Pérez-Salado Kamps 2003, p.2665 and Table 3 footnote, p.2666 (read in #239): one row precipitated. It is at 2 m PZ, 313 K (corrected 313.75 K), m̄_CO2 = 3.366 mol/kg (1.69 mol CO2/mol PZ, 0.84 mol/mol alkalinity), p = 4.446 MPa. The authors call the salt "probably piperazine bicarbonate", seen "only ... in a single experiment"; "the precipitate could not be analyzed". No 4 m row and no row at 333 K or above precipitated, up to 5.37 mol/kg CO2 and 9.6 MPa. Their model curve above about 4 MPa at 313 K is an extrapolation into the vapor–liquid–solid region (p.2667, Fig. 2a).

## Row admission for #308

Freeze decisions before inspecting fitted residuals. Record the exact source/table/row, analytical PZ molality, loading per mole PZ, temperature, solvent isotope, reported phase and boundary comparison. Missing evidence is quarantine, not exclusion based on model error. A fluid stability calculation cannot replace solid admission.

| Source/cohort | Concentration, loading and temperature | Admission evidence and action |
|---|---|---|
| Hartono 2013 Table 6 | 1.35–7.41 m, alpha=0, 333–373 K | Above the unloaded low-concentration liquidus maximum (Hilliard I.1 about 324 K); retain source liquid ebulliometer rows. The named outlier is separate for measurement reasons, not a solid exclusion. |
| Hilliard D.2 | 0.89–5 m, alpha=0, 306–337 K | Compare each row with the bracketing I.1 liquidus points in unloaded mass fraction w=86.13m/(1000+86.13m). Use the larger adjacent liquidus value, including duplicate maximum, as a conservative interpolation bound; admit only T above it. Equality, missing bracket or conflict with observed phase is quarantine for owner decision. Do not extrapolate I.1. |
| Hilliard D.5 | 0.89–5.18 m, loaded, 313/333 K | Source-observed liquid FTIR samples; admit those exact loaded states only where no precipitate is reported, label observational phase support. Zero-loading supports use I.1 as for D.2. No boundary interpolated from Freeman. |
| Ermatchkov 2003 Tables 1–4 | 0.10–1.48 m, CO2/PZ up to about 1, 283/298/313/333 K | Liquid NMR samples in D2O (§2 pp.1278–1281). Admit exact observed loaded states with isotope/phase limitation. Do not impose an H2O unloaded liquidus on loaded D2O or treat 8/10 m Freeman as an exclusion envelope. |
| Ermatchkov 2006 Tables 1–3 | about 1/2 m at 313 K, 2/4 m at 353/393 K, alpha 0.05–0.95 | Source liquid sampling/headspace GC (pp.1788–1789); admit exact unflagged states, no interpolation into unmeasured cold/rich region. |
| Kamps 2003 Table 3 | 2/4 m, alpha 0–1.69, corrected 313.75–395 K | Exclude 2 m, alpha=1.69, corrected 313.75 K, 4.446 MPa precipitation row (p.2665 and Table 3 footnote). Admit other observed fluid-equilibrium rows with no reported solid, flag proximity to the excluded state and no solid-free envelope claim. Unloaded endpoints require I.1. |
| Derks 2005 | about 0.2035/0.633 m from nominal molarity, source loading and T | Admit source observed dilute liquid rows; retain molarity-to-molality assumption. Below 313 K and alpha>1 rows each reported separately. Freeman concentrated data impose no dilute boundary. |
| Dugas/Xu/Bishnoi secondary observations | Use each printed concentration, loading and T | Admit only actual measured liquid observations without precipitation reports; unresolved preparation or phase status stays unscored. Dugas 12 m, about 0.40 per alkalinity was not measured owing to solubility: no invented row there. |
| Unmeasured 8/10 m loaded states | Freeman 2010 Fig.1, loadings per alkalinity | Do not manufacture numeric boundaries from the figure. No digitization authorized here. Exact observed rows can be reported, but new states remain unadmitted until a sourced boundary is bound. |
| Any other extrapolated composition/T | outside source observed states or I.1 brackets | Quarantine for owner decision; no Freeman-to-dilute extrapolation. |

This admits observed liquid measurements as conditional evidence rather than claiming that absence of a precipitation note proves global stability. Hilliard §5.3 measured unloaded SLE only; his §14.6 loaded boundary is an eNRTL prediction, not a measurement. Fosbøl 2011 abstract, introduction and Tables 1–3 concern PZ–water/AMP–water/AMP–PZ–water without CO2 and cannot supply a loaded boundary. Freeman 2011 and loaded SINTEF work remain necessary before a rich-side envelope claim, but no such claim is used in this design. Sources and locators above were checked in the current hash-matching PDFs. No solid-model fitting or figure digitization was performed.
