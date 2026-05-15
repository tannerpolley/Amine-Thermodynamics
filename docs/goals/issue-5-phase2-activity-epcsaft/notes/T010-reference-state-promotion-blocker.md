# T010 Reference-State Promotion Blocker

## Current Gate

Superseded by `T010-austgen-reference-state-evidence.md`. R1-R5 now have source-verified Austgen Table V constants and the canonical manifest marks them as `thermodynamic_activity` fixed inputs.

## Local Search Result

Local repo search found references to Austgen, Bates/Pinching, Tong, and Bülow in existing markdown papers and analysis inputs, but did not find local Austgen 1991, Austgen 1989, Bates/Pinching 1951, or Tong 2012 source markdown/PDF files suitable for reference-state promotion.

Zotero local API search found the supplied Nasrifar, Uyan, Wangler, Cleeton, Wong, Amundsen, Baygi, Najafloo, Pahlavanzadeh, Pakravesh, and Schick items. It did not find Austgen 1991, Austgen 1989, Bates/Pinching 1951, Tong 2012, or Bülow 2021 as local library items.

## Safe Next Step

The old reference-state gate is closed. The remaining safe next step is upstream package work:

- wait for or verify upstream ePC-SAFT issue #115,
- repin `epcsaft` after the activity-coupled backend lands,
- rerun final integration,
- then generate Phase 2 equilibrium rows and figures.

Until then, do not generate `phase2_equilibrium_results.csv` or Phase 2 figures through a MEA-owned nonlinear solver workaround.
