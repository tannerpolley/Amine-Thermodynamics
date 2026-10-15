# Corrected initial ion starting records

Both declared ion starts are derived from the unchanged stage-2 CO₂–water B record. The bicarbonate–water interaction changes from +0.5 to zero; carbamate–water and protonated-MEA–water interaction and slope remain zero. Trace-ion interactions, source R2/R5, adopted water, pure neutral parameters, refreshed association and stage-2 neutral binaries are preserved. CO₂ dispersion is 169.21 K; unshifted R5 is 2677.91 K. The original file remains unchanged.

Start A retains the source ion seeds. Start B uses the seven values in design §4, with packing and Debye–Hückel diameters equal to 0.88 times each segment diameter. `derived-starts.json` records all input and starting-record hashes.

| State | T, K | Original density, kg/m³ | Corrected density, kg/m³ | Difference, kg/m³ |
|---|---:|---:|---:|---:|
| AMU-DENS-002 | 298.15 | 1009.907212360454 | 1009.907212360454 | 4.547e-13 |
| AMU-DENS-009 | 313.15 | 1003.287419110843 | 1003.287419110845 | 1.364e-12 |
| AMU-DENS-016 | 323.15 | 998.099992017500 | 998.099992017500 | -1.137e-13 |
| AMU-DENS-023 | 343.15 | 986.342794101139 | 986.342794101139 | 2.274e-13 |
| AMU-DENS-030 | 353.15 | 979.927109423929 | 979.927109423930 | 1.137e-12 |

The paired replay has relative objective difference 4.94711e-13, maximum weighted residual difference 5.25135e-13, and identical five row definitions. All five states solve at 30 wt% unloaded MEA and 0.1 MPa, with maximum raw equilibrium residual below 2.3×10⁻¹³ and positive pressure-density derivatives. These values numerically verify that the bicarbonate correction leaves the stage-2 neutral comparisons unchanged at the declared $10^{-8}$ limits. No neutral fit ran.

A reporting assertion initially required exact binary equality and stopped after the completed solves. The retained differences above satisfy the accepted tolerances; the assertion was corrected without repeating the model calls. This was not a failed declared replay, closure or serialization check.

Derivation and paired solves used 0.441394710 recorded command wall-s. CPU was not metered because the assertion preceded the timing write; a conservative 14.124630720 CPU-s charge uses 32 CPUs times the complete command duration. This charge counts against the initial ion-pair allowance. Earlier qualification startup remains unmetered as disclosed in its historical record.

Program boundary before the ion fits: 1187.728494 CPU-s / at least 432.145917 active wall-s; remaining at most 142812.271506 CPU-s / 21167.854083 wall-s. Initial ion-pair allowance after these checks is at most 2385.875369 CPU-s / 359.558605 wall-s. This is numerical verification and starting-record construction; no ion calibration result exists yet.
