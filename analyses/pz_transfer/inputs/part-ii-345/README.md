# Piperazine inputs for Part II

Phase 1 of #345, under the owner's 14 November 2026 decision in #337.
These are plain data for the shared calculation code being built in #343.
No driver, fit, search, parameter adoption or manuscript change is included.
Paths in the JSON files are relative to the repository root.

- `declaration.json` binds the F2 shared-value and parameter files by SHA-256,
  names the PZ-only inputs, declares the 12 fitted coordinates and two starts,
  and ties the Born diameter of all four charged PZ species to their segment
  diameters. The neutral protonated carbamate has no Born diameter.
- `data-roles.csv` identifies all 329 reactive states: 183 fitted states
  (294 observations), 52 not fitted states seen during development, and
  94 comparison only states. Measurement values remain in the hashed source
  CSV files. Each row carries a separate range mark for all eight reactions.
  One Kamps solid-precipitation row retains its existing exclusion from the
  fluid-only comparison; no row is excluded for temperature.
- `split-compositions.json` retains 102 distinct liquid trial compositions
  admitted by native resolved descent, with source hashes and JSON pointers.
  It includes the known Hilliard rows 55/56 neighbours whose supplied trials
  at A12s gave -0.030909497986794147 and -0.04372673268093612 RT.
  Its coverage table enumerates the tracked PZ JSON files inspected at the
  recorded base. Eight binary PZ-water descents have incompatible two-component
  order and are counted separately. Unresolved iterates and scalar-only
  negatives are not supplied trials. These are historical trial compositions,
  not 102 independent split states or evidence of F2 stability.

The common calculation interval for every reaction is 283.15–395.0 K.
PZ protonation range marks use 293.14–353.42 K (Hamborg 2009 Table 16);
carbamate marks use 283.15–333.15 K (Ermatchkov 2003 Tables 1–5).
273.15–498.15 K is the source-correlation range stated by Austgen 1991 Table V p.547 (citing Edwards 1978), not verified measured coverage.
The R1–R3 marks use that source-correlation range; the narrower historical
calculation declarations do not establish measured coverage.

Phase 2 must adapt these files to #343's reviewed, merged interface. That code
must bind F2 without using the frozen F0 readers as current inputs, apply the
coordinate ties and reaction interval, preserve the fitted observation weights
and covariance, and consume and extend only this PZ split record. It must then
perform the two-start fits and continuations, data/grid stability searches with
supplied trials, conditional penalty and retreat, conditional standard errors,
range-separated comparisons and curve generation. Run/report evidence, the
notebook and figures remain phase 2 work. Historical pure and binary deviations
and the exact F0 replay remain in the existing PZ results.
