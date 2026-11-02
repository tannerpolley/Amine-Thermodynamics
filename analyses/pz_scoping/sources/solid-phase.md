# PZ solid phases and the liquid window

Checked 2026-11-02 for #237. Aqueous PZ precipitates solids at absorber-relevant conditions. The Engine has no solid phase. Its equilibrium problem declares only `PhaseKind { Liquid, Vapor }` (`engine/native/equilibrium/problem.hpp:29`, read-only clone at Engine `217026ab`). A liquid-only model cannot predict or report precipitation. Its results are claims only inside a declared liquid window.

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
- Ermatchkov 2006 Table 5 note b, p.1793: some Pérez-Salado Kamps 2003 total-pressure rows (2–4 m, 314–395 K) showed solid precipitation and were excluded from scoring.

## What this means for a PZ assessment

1. Every scored state must lie inside a declared liquid window: above the unloaded hexahydrate liquidus (Hilliard I.1) for zero-loading rows; inside Freeman's 8/10 m envelope for loaded rows near those compositions. Rows a source flags as precipitating are excluded before fitting, not after.
2. Lean, cold, concentrated states fall outside the liquid window: for example, 8 m below about 0.25 mol/mol alkalinity at 20 °C. A model "prediction" there is not a prediction of a real liquid.
3. The rich-side limit (Dugas 12 m near 0.40) has no identified solid phase or tabulated boundary in the sources read. Freeman's 2011 dissertation and the SINTEF crystallization work (Ma et al. 2012; abstract only) are the leads to read before claiming a rich-side boundary.
4. A solid model (a hexahydrate solubility product evaluated with ePC-SAFT activities) is a separate capability. It belongs to the Engine and needs an Engine issue stating the MEA-repository use case. This scoping task does not open one.
