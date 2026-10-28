# Diagnostic transfer comparison

Every calculated number here is **diagnostic: phase assumption violated at fitted Merkley saturation states**. The notebook owns interpretation. These calculations do not give a qualified transfer verdict.

A1 and B1 were selected by fitted objective before this outside-fit access. Their Ermatchkov 88-row CO2 partial-pressure AARDs are 26.0571053742% and 18.7677551175%. Removing exactly the unstable fitted Merkley rows listed for each candidate in `../stage2/liquid-witnesses.csv` gives 277-row A and 278-row B sensitivity objectives, costs 395.374637991 and 371.795416342, and diagnostic AARDs 27.2939018646% and 19.7791194828%. Both converge but fail the phase gate.

Each directory owns its endpoint, fit, declaration, row-level comparisons, subset summaries, Wangler heat/Cp predictions, model-saturation/156 kPa calculations, and pressure-bracket speciation spread. The removal directories also retain the full fitted/comparison phase searches. `liquid-witnesses.csv` indexes every resolved liquid trial, including the native split and error estimates. Native JSON preserves vapor witnesses and unresolved searches separately.

Böttinger uses all 58 rows at both 500000 and 2500000 Pa. The source gives a 5–25 bar range but no per-row pressure (Methods, p.7919); the owner approved this bracket in the native question tool. Its carbonate signal is the combined bicarbonate/carbonate signal (Results and Discussion, p.7921). All rows remain; DMDEA and byproduct contributions relative to the reported amine sum are flagged above 3%. The full carbonate relative AARD is undefined because one reported signal is zero; the complete 58-row mean absolute mole-fraction error is retained. Files marked `101325Pa` are withdrawn and supply no source-pressure comparison evidence.

All six Zheng model saturation loadings and the three 333.15 K Merkley alternatives resolve for each vector. The owner-approved scan is 0.05–1.50 mol CO2/mol MDEA in 0.05 steps; every native admission failure is retained, then the first adjacent admitted pressure-sign bracket is inverted by Brent at loading tolerance 1e-12. No multiple admitted sign changes occur on these scans. Earlier fixed-bracket failures and their bounded diagnosis are retained under explicit filenames; they do not replace the resolved results. The three 288.71 K alternatives, the 422.04 K Merkley states and Kuranov 413 K remain outside the frozen reaction domain. Derks, Xiao and Zhang retain their frozen unscored dispositions.

Reproduce from a fresh checkout of ed58166 using the isolated interpreter command in the narrowed-results README, with operation `diagnostic`; operation `present` renders the retained AARD values without model calculations. The source notebook reports the parameter vectors, every declared subset, the caloric sensitivity and the pressure spread. `summary.json` aggregates nonzero-observation relative errors; the NMR summary also reports a full-row absolute error so its zero observation is retained. Neither statistic creates another pass bar.

No MEA record, manuscript, source data or Zotero record is changed. No Engine source is imported. Independent review and manuscript promotion remain open.

The Merkley omission is confined to the sensitivity objective. Its phase query includes all 280 original fitted observations (324 fitted-state records), plus comparisons, for 754 records per vector. Final liquid-witness/unresolved counts are A 32/102 and B 32/108. Earlier objective-row-only queries are archived under that explicit filename.

## Stored evidence

Phase-search JSON files larger than 5 MB are stored as `.json.gz` (gzip level 9). `../compressed-evidence.json` lists each raw SHA-256; restore with `gunzip -k <file>.json.gz` before rerunning the summary scripts.
